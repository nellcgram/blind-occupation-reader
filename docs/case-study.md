# Case study: a blind-reader test for "show, don't tell"

## Decisions

- Readers don't see the list of possible jobs
- Agents should reference the whole manuscript, not only some scenes
- One candidates file per character, with a `Manuscript:` path and aliases (a hard-coded path and name-based scene selection both caused errors)

## Problems fixed

**Stated-job quotes.** Subagents kept quoting lines that named the job (dialogue, not behavior). I added a rule to cut this.
