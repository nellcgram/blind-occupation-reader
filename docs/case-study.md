# Case study: a blind-reader test for "show, don't tell"

**Problem.** A writer wants to know if a character's job comes through in behavior alone. Doing it by hand needs fresh
readers after every edit. **Built:** agents that read only the scenes, vote on the job, quote their evidence, and log how
the answer changes. **Outcome:** it works on an invented sample, and it taught me three things about agent behavior.

## How it works
Five independent readers see only the scene text and guess the job, ignoring stated jobs. The winning answer's quotes are
reported. A separate matcher compares the verdict with occupations already considered. Each run is logged with the exact
text used.

## Decisions
| Decision | Why |
|---|---|
| Readers never see the candidate list | Otherwise they anchor on what the writer already thought of. |
| Five votes, exact quotes | A count shows consistency; quotes can be checked against the text. |
| Agents limited to the Read tool | They never need to write or run anything (see incident 1). |
| Always use the full manuscript | Answers changed with scene scope (incident 3). |
| One candidates file per character, with a `Manuscript:` path and aliases | A hard-coded path and name-based scene selection both caused errors (incident 3). |

## What went wrong
1. **Runaway agents.** Parallel readers re-ran the whole workflow and, in one case, pushed a deletion to an unrelated
   repo. The agents had full shell access they never needed. Fix: Read-only tools, plus a permission prompt before any push.
   Lesson: ask what an agent *can* do, not only what it was told.
2. **Stated-job quotes.** Readers kept quoting lines that name the job. An explicit rule cut this on the sample (1 of 5
   runs before, 0 of 5 after), but two still quoted a schedule line, and the original leak was on a longer text I
   haven't re-tested. Treated as reduced, not solved.
3. **The answer moved.** Three runs gave narrow, broad, then narrow again. The cause was scene selection, not the model:
   one run picked scenes by one of the character's two names. Fix: per-character manuscript path and alias rules. A log
   of the exact text used is what made this visible.

## Not measured
Agreement with human readers; subtle or ambiguous writing (the sample is clear on purpose); behavior on other models.

## Next
Re-test the quote rule on long text, add an ambiguous sample, compare with human readers, try a cheaper model and see
whether the answer holds.
