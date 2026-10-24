# Blind Occupation Reader (web app)

A web version of the `character-occupation-inference` skill. A visitor pastes scene text; the server runs
5 independent "blind" readings (behavior only, stated jobs ignored), groups the answers into a vote count,
shows the quotes behind the winning answer, and checks it against an optional list of occupations already considered.

The prompts in [prompts.py](prompts.py) are adapted from `.claude/agents/blind-inferrer.md` and `matcher.md`.

## Run locally

```bash
cd webapp
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # or `ant auth login`
./.venv/bin/python app.py           # http://127.0.0.1:5000
```

No key yet? `MOCK_LLM=1 ./.venv/bin/python app.py` returns a canned result so you can try the page.
Tests: `./.venv/bin/pip install pytest && ./.venv/bin/python -m pytest` (they run in mock mode and call no API).

## Limits (the point of the scaffold)

| Limit | Default | Setting | Enforced |
|---|---|---|---|
| Scene text length | 8,000 characters | `MAX_SCENE_CHARS` | Raw request body rejected with 413 before parsing; then 400 with the exact count. The page shows a live counter and disables submit when over. |
| Requests per visitor | 3 per hour | `RATE_LIMIT` | Per IP, returns 429. Each request makes `VOTES` + 1 model calls (4 by default). |
| Total requests per day | 100 | `DAILY_REQUEST_CAP` | Global counter (UTC day), returns 503. This is the spend backstop. |
| Other input | name 60 chars; 20 candidates of 200 chars | constants in app.py | 400 |

Worst-case spend per day is roughly `DAILY_REQUEST_CAP` x (`VOTES` + 1) calls x the scene text's token count, plus output, at your chosen model's price. Also set a monthly spend limit in the Anthropic Console as a backstop; the app can't do that for you.

## Model and cost

Defaults: `claude-sonnet-5-5`, `EFFORT=low`, `VOTES=3`. Sonnet lists at $2 / $10 per million input / output tokens: about half
of Opus 5.5 ($4 / $20) and 20x Haiku 5.5 ($0.10 / $0.50). My estimate, not measured, is roughly 5 cents per request, so the
daily cap of 100 is about $5 a day at worst.

**Check done on the invented sample (live API, one pipeline run per setting, 3 votes each):**

| Model, effort | Answer | Notes |
|---|---|---|
| Haiku 5.5, low | "EMT or paramedic" 3/3, in 3 of 3 runs | Quoted "I work nights" in 2 of 3 runs despite the rule |
| Haiku 5.5, medium | "Paramedic" 3/3 | No stated-job quotes |
| Haiku 5.5, high | "Paramedic" 2/3, "emergency nurse" 1/3 | |
| **Sonnet 5.5, low (the default)** | "Emergency room nurse" 3/3 | No stated-job quotes |
| Opus (from the Claude Code runs) | "Emergency department nurse" 5/5, twice | The intended answer |

Haiku does **not** reproduce the Opus answer on this sample: it lands on paramedic, a neighbouring job, where the scenes
(scrubs, clogs, hospital handoff) point to nurse. Sonnet 5.5 at `EFFORT=low` matched Opus, so it is the default. This is one
sample and a handful of runs. For the cheapest option, set `MODEL=claude-haiku-5-5` and treat its answers as approximate.

The sample scenes are read from `../sample/scenes/marek_scenes.md` (override with `SAMPLE_PATH`), so deploy the repo, not just this folder, or set `SAMPLE_PATH`.

## Deploy on Render (free)

[render.yaml](../render.yaml) at the repo root sets it up: free plan, `gunicorn` with one worker, `TRUST_PROXY_HOPS=1`.

1. Push the repo to GitHub (check no key or private text is in it first).
2. On render.com: **New > Blueprint**, pick the repo. Render asks for `ANTHROPIC_API_KEY`; paste the key there. It is stored on Render, not in the repo.
3. Open the `https://...onrender.com` address it gives you; check the padlock, load the sample, run it.
4. In the Anthropic Console, set a monthly spend limit at platform.claude.com/settings/billing.

Free-tier behavior to expect: the service sleeps after 15 idle minutes and takes about a minute to wake, and it may restart at any time.
**Each restart resets the in-memory rate limits and daily cap**, so the Console spend limit is the real backstop.

## Other things to know

- **Rate limits are in memory.** Run one worker, or point Flask-Limiter at Redis (`storage_uri`) if you scale out.
- **Proxy IPs.** `TRUST_PROXY_HOPS` is the number of reverse proxies in front of the app (1 on Render). Too low and all visitors share one rate-limit bucket; too high and visitors can fake their address. Leave 0 with no proxy.
- **Privacy.** Pasted text goes to the Anthropic API. Say so on the page, and don't log request bodies.
- **Keep the key server-side.** Put `ANTHROPIC_API_KEY` in your host's environment-variable settings (the "Environment" or "Variables" page of the hosting dashboard), never in the code, the repo or the page. The app does **not** read `.env` files; locally, `export ANTHROPIC_API_KEY=...` in your shell. The key is read from the environment and never sent to the browser. If you ever paste it into a file that gets committed, revoke it in the Anthropic Console and make a new one.
- **Do not ship your real manuscript.** The sample is the invented Marek scenes in `../sample/`.

## How it differs from the Claude Code skill

- No log file or candidates file: the visitor supplies the candidate list per request, and nothing is stored.
- A sixth call groups differently worded answers ("ER nurse" / "emergency room nurse") into one tally. In Claude Code, the orchestrating session does this.
- Each quote is checked against the pasted text. A quote the readers invented is flagged "Not found verbatim".
- The prompt tells readers not to quote lines that state the job. This is a prompt-level fix only; whether it fully stops the stated-job leak seen in earlier runs has not been measured.
