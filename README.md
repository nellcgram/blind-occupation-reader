# Blind Occupation Reader

Can readers tell what a character does for a living from behavior alone? Give the skill a manuscript, and several
independent "blind" readers guess the job from the scene text, ignoring any line that states it. The skill reports the
vote count and the quotes behind the winner, and checks the verdict against occupations you've already considered.

It's a Claude Code skill with two agents (`blind-inferrer` and `matcher`), plus a log per character. It runs on an
invented sample character.

**[Case study](docs/case-study.md)** has what went wrong and what I learned. Short version: restricting agent tools
fixed a runaway-agent incident, and answers changed because of which scenes were used.

## Try it

Open this folder in Claude Code and ask it to run the `character-occupation-inference` skill on Marek. The skill reads
the manuscript path from the `Manuscript:` line in
[marek_candidates.md](.claude/skills/character-occupation-inference/data/marek_candidates.md), runs `blind-inferrer`
five times, appends to [marek.md](.claude/skills/character-occupation-inference/data/logs/marek.md), then runs `matcher`.

To use it on your own character, add `data/<name>_candidates.md` with a `Manuscript:` line and any aliases.

## Layout

`.claude/` agents, skill, per-character candidates and logs · `sample/` invented manuscript · `docs/` case study

## Limits

- A prompt-based experiment, not a validated measure. Votes from one model are correlated.
- The sample is easy on purpose: every run gave the same answer (ER nurse, 5/5). It shows the pipeline works, not how it handles subtle writing.
- Small tests: one invented sample, a few runs.

## Important note
This section was written by Claude, carefully edited by Nell.

MIT license.


