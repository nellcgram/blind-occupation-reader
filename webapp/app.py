"""Web version of the character-occupation-inference skill.

POST /api/infer runs N independent blind readings of the scene text, groups the
answers into a vote count, and checks the winner against an optional candidates list.
"""
import json
import os
import re
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import anthropic
from flask import Flask, jsonify, request, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

from prompts import AGGREGATOR_SCHEMA, AGGREGATOR_SYSTEM, INFERRER_SCHEMA, INFERRER_SYSTEM

# --- Limits (all overridable by environment) -------------------------------
MAX_SCENE_CHARS = int(os.environ.get("MAX_SCENE_CHARS", 8000))
MAX_NAME_CHARS = 60
MAX_CANDIDATES = 20
MAX_CANDIDATE_CHARS = 200
RATE_LIMIT = os.environ.get("RATE_LIMIT", "3 per hour")  # per IP, per request (each = N+1 model calls)
DAILY_REQUEST_CAP = int(os.environ.get("DAILY_REQUEST_CAP", 100))  # global spend backstop
VOTES = int(os.environ.get("VOTES", 3))
MIN_VOTES = 3  # fewer successful readings than this and the request fails

MODEL = os.environ.get("MODEL", "claude-sonnet-5-5")
EFFORT = os.environ.get("EFFORT", "low")
MOCK_LLM = os.environ.get("MOCK_LLM") == "1"
# The sample scenes live outside webapp/ so the repo keeps one copy.
SAMPLE_PATH = Path(os.environ.get("SAMPLE_PATH", Path(__file__).resolve().parent.parent / "sample" / "scenes" / "marek_scenes.md"))

app = Flask(__name__, static_folder="static", static_url_path="/static")
# Reject oversized bodies before parsing: scene cap in bytes (4 per char worst case) plus headroom.
app.config["MAX_CONTENT_LENGTH"] = MAX_SCENE_CHARS * 4 + 16 * 1024

hops = int(os.environ.get("TRUST_PROXY_HOPS", 0))
if hops:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=hops)  # only set behind a proxy you control

limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

_daily = {"day": None, "count": 0}
_daily_lock = threading.Lock()


def take_daily_slot() -> bool:
    today = datetime.now(timezone.utc).date()
    with _daily_lock:
        if _daily["day"] != today:
            _daily["day"], _daily["count"] = today, 0
        if _daily["count"] >= DAILY_REQUEST_CAP:
            return False
        _daily["count"] += 1
        return True


# --- Validation --------------------------------------------------------------
class BadRequest(Exception):
    pass


def parse_input(data):
    if not isinstance(data, dict):
        raise BadRequest("Send a JSON object.")
    scenes = data.get("scenes")
    if not isinstance(scenes, str) or not scenes.strip():
        raise BadRequest("scenes is required.")
    if len(scenes) > MAX_SCENE_CHARS:
        raise BadRequest(f"scenes is {len(scenes):,} characters; the limit is {MAX_SCENE_CHARS:,}.")
    name = data.get("character", "")
    if not isinstance(name, str) or len(name) > MAX_NAME_CHARS:
        raise BadRequest(f"character must be text of at most {MAX_NAME_CHARS} characters.")
    name = " ".join(name.split()) or "the character"
    cands = data.get("candidates", [])
    if not isinstance(cands, list) or len(cands) > MAX_CANDIDATES:
        raise BadRequest(f"candidates must be a list of at most {MAX_CANDIDATES} items.")
    cleaned = []
    for c in cands:
        if not isinstance(c, str) or len(c) > MAX_CANDIDATE_CHARS:
            raise BadRequest(f"each candidate must be text of at most {MAX_CANDIDATE_CHARS} characters.")
        c = " ".join(c.split())
        if c:
            cleaned.append(c)
    return scenes, name, cleaned


# --- Model calls -------------------------------------------------------------
_client = None


def client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(timeout=90.0, max_retries=2)
    return _client


def call_json(system, user, schema):
    response = client().messages.create(
        model=MODEL,
        max_tokens=4000,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": schema}},
    )
    if response.stop_reason in ("refusal", "max_tokens"):
        raise RuntimeError(f"model stopped: {response.stop_reason}")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


def infer_once(name, scenes, _i):
    if MOCK_LLM:
        return {"answer": "Emergency department nurse",
                "why": ["He was counting something under his breath, his lips barely moving."]}
    user = f"Character: {name}\n\n<scenes>\n{scenes}\n</scenes>\n\nWhat job does this character seem like they have?"
    return call_json(INFERRER_SYSTEM, user, INFERRER_SCHEMA)


def aggregate(answers, candidates):
    if MOCK_LLM:
        return {"groups": [{"label": "Emergency department nurse", "indexes": list(range(len(answers)))}],
                "status": "new", "entry": "", "reason": "Mock result."}
    listing = "\n".join(f"{i}: {a}" for i, a in enumerate(answers))
    considered = "\n".join(f"- {c}" for c in candidates) or "(none)"
    user = f"Answers:\n{listing}\n\nConsidered occupations:\n{considered}"
    return call_json(AGGREGATOR_SYSTEM, user, AGGREGATOR_SCHEMA)


_SMART = {ord("‘"): "'", ord("’"): "'", ord("“"): '"', ord("”"): '"'}


def _norm(s):
    return " ".join(s.translate(_SMART).lower().split())


def quote_is_verbatim(quote, scenes_norm):
    """True if every ellipsis-separated piece of the quote appears in the scene text."""
    pieces = [p for p in re.split(r"\.\.\.|…", quote) if len(p.strip()) >= 6]
    return bool(pieces) and all(_norm(p).strip(" \"'") in scenes_norm for p in pieces)


def run_pipeline(name, scenes, candidates):
    with ThreadPoolExecutor(max_workers=VOTES) as pool:
        futures = [pool.submit(infer_once, name, scenes, i) for i in range(VOTES)]
        runs = []
        for f in futures:
            try:
                r = f.result()
                if isinstance(r.get("answer"), str) and isinstance(r.get("why"), list):
                    runs.append(r)
            except anthropic.APIStatusError as e:
                if e.status_code in (401, 403):
                    raise
            except (anthropic.APIConnectionError, RuntimeError, ValueError, StopIteration):
                pass
    if len(runs) < MIN_VOTES:
        raise RuntimeError("too few readings completed")

    agg = aggregate([r["answer"] for r in runs], candidates)
    seen, groups = set(), []
    for g in agg["groups"]:
        idx = [i for i in g["indexes"] if isinstance(i, int) and 0 <= i < len(runs) and i not in seen]
        seen.update(idx)
        if idx:
            groups.append({"label": g["label"], "indexes": idx})
    for i in range(len(runs)):  # any answer the grouper dropped keeps its own wording
        if i not in seen:
            groups.append({"label": runs[i]["answer"], "indexes": [i]})
    groups.sort(key=lambda g: -len(g["indexes"]))
    top = groups[0]

    scenes_norm = _norm(scenes)
    quotes = []
    for i in top["indexes"]:
        for q in runs[i]["why"]:
            if isinstance(q, str) and q.strip() and q not in [x["text"] for x in quotes]:
                quotes.append({"text": q, "verified": quote_is_verbatim(q, scenes_norm)})

    entry = agg.get("entry")
    return {
        "character": name,
        "total": len(runs),
        "votes": [{"label": g["label"], "count": len(g["indexes"])} for g in groups],
        "answer": {"label": top["label"], "count": len(top["indexes"])},
        "quotes": quotes,
        "match": {
            "status": agg["status"] if candidates else "new",
            "entry": entry if entry in candidates else None,
            "reason": agg["reason"],
        },
    }


# --- Routes ------------------------------------------------------------------
@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/sample.txt")
def sample():
    if not SAMPLE_PATH.is_file():
        return jsonify(error="No sample available."), 404
    return SAMPLE_PATH.read_text(encoding="utf-8"), 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.get("/api/limits")
def limits():
    return jsonify(maxSceneChars=MAX_SCENE_CHARS, maxCandidates=MAX_CANDIDATES, rateLimit=RATE_LIMIT)


@app.post("/api/infer")
@limiter.limit(RATE_LIMIT)
def infer():
    try:
        scenes, name, candidates = parse_input(request.get_json(silent=True))
    except BadRequest as e:
        return jsonify(error=str(e)), 400
    if not take_daily_slot():
        return jsonify(error="The daily limit for this demo has been reached. Try again tomorrow."), 503
    try:
        return jsonify(run_pipeline(name, scenes, candidates))
    except anthropic.RateLimitError:
        return jsonify(error="The model is busy. Try again in a minute."), 503
    except anthropic.APIError:
        app.logger.exception("Anthropic API error")
        return jsonify(error="The model call failed. Try again."), 502
    except RuntimeError:
        return jsonify(error="Too few readings completed. Try again."), 502


@app.errorhandler(413)
def too_large(_):
    return jsonify(error=f"Request too large. Scene text is limited to {MAX_SCENE_CHARS:,} characters."), 413


@app.errorhandler(429)
def rate_limited(e):
    return jsonify(error=f"Rate limit reached ({RATE_LIMIT} per visitor). Try again later."), 429


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
