---
name: character-occupation-inference
description: Use this when the user wants to infer a character's job or role from a scene, based on his behavior and psychology. Ignore anything a character states outright about his job, including when the character claims a different occupation than his actions support.
---

You will be given the text of one or more scenes for a specific character. Always use the character's complete scene manuscript as scene text, regardless of what excerpt is named in the invocation. The manuscript path is the "Manuscript:" line in the character's candidates file; if there is no candidates file or no such line, ask the user for the manuscript path and do not guess one. If the user points to a smaller file or scene subset, read the full manuscript instead and note that you did so.

A character may appear under more than one name (e.g. Marek is also "Mac", a nickname). Check the character's candidates file for aliases, and include every scene for any alias — never select scenes by one name only.

Each blind-inferrer or matcher call must be a single isolated
invocation with only the scene text (or verdict + candidates file)
in the prompt. Never let a delegated call spawn further agents, write
or edit files, or run shell/git commands — those agents have no tools
for that by design; do not work around it by doing it on their behalf
either.

1. Run the blind-inferrer agent 5 separate times, each with only the
   scene text — no other context, no memory of the other runs.
2. Collect all 5 results (Answer + Why).
3. Count how many runs gave each Answer. Report the plain count, no
   added label.
4. Take the Answer with the most votes. Use the Why quotes from the
   runs that picked it.
5. Check for an existing log file for this character; if one exists,
   read its most recent entry.
6. If a previous entry exists, state what's different in the text and
   whether the Answer changed.
7. Append a new entry to the character's log file:
   ## [date]
   - Answer: [occupation] ([vote count])
   - Why: [quotes]
   - Scene text: [exact text used]
8. Run the matcher agent with today's verdict and the character's
   candidates file; report match / new / contradicts, citing the entry.
9. Report the Answer, vote count, quotes, what changed since last time,
   and the matcher's finding.