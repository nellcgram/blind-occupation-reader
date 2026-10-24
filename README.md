# Blind Occupation Reader

Can readers tell what a character does for a living from behavior alone? Paste scenes, and several independent
"blind" model readers guess the job, ignoring any line that states it. The app shows the vote count and the quotes
behind the winner, and checks it against occupations you've already considered.

Two versions: a **Claude Code skill with two agents** (`.claude/`) and a **Flask web app** (`webapp/`) with a
per-visitor rate limit, a daily cap and a text-length cap. Both run on an invented sample character.

**[Case study](docs/case-study.md)** has what went wrong and what I learned. Short version: restricting agent tools
fixed a runaway-agent incident, and answers changed because of which scenes were used, not randomness.

## Try it

```bash
cd webapp
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
./.venv/bin/python app.py      # http://127.0.0.1:5000, click "Load sample scenes"
```

No key: `MOCK_LLM=1 ./.venv/bin/python app.py`. Settings, limits and deployment notes: [webapp/README.md](webapp/README.md).
Claude Code version: ask Claude Code to run the `character-occupation-inference` skill on Marek.

## Layout

`.claude/` agents, skill, per-character candidates and logs · `sample/` invented manuscript · `webapp/` app and tests · `docs/` case study

## Honest limits

- A prompt-based experiment, not a validated measure. Votes from one model are correlated.
- The sample is easy on purpose. Model check: Sonnet 5.5 matched Opus ("ER nurse"); Haiku 5.5 said "paramedic".
- Small tests: one sample, a few runs per setting, and 13 tests that use a fake model.

MIT license.
