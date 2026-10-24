# Case study: a blind-reader test for "show, don't tell"

**Problem.** A writer wants to know if a character's job comes through in behavior alone. Doing it by hand needs fresh
readers after every edit. **Built:** agents that read only the scenes, vote on the job, quote their evidence, and log how
the answer changes, plus a web version. **Outcome:** it works on an invented sample, and it taught me three things about
agent behavior.

## How it works
Five (web app: three) independent readers see only the scene text and guess the job, ignoring stated jobs. The winning
answer's quotes are reported. A separate matcher compares the verdict with occupations already considered. Each run is
logged with the exact text used.

## Decisions
| Decision | Why |
|---|---|
| Readers never see the candidate list | Otherwise they anchor on what the writer already thought of. |
| Several votes, exact quotes | A count shows consistency; quotes can be checked (the web app flags any not in the text). |
| Agents limited to the Read tool | They never need to write or run anything (see incident 1). |
| Always use the full manuscript | Answers changed with scene scope (incident 3). |
| Web limits enforced on the server | Body size, text length, per-IP rate and a daily cap; the page's counter is only a convenience. |
| Default model: Sonnet 5.5, low effort | Matched Opus on the sample at about half the price; Haiku was 20x cheaper but missed. |

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

## Model check
On the sample (live API, few runs): Opus "ER nurse" 5/5 twice; Sonnet 5.5 "ER nurse" 3/3; Haiku 5.5 "paramedic" at low and
medium effort, split at high. Haiku also quoted a stated-job line in 2 of 3 runs at low effort. The cheapest model was
the one that missed the evidence (scrubs, clogs, hospital handoff).

## Not measured
Agreement with human readers; subtle or ambiguous writing (the sample is clear on purpose); real cost per request (token
prices only); behavior at scale.

## Next
Measure cost from API usage, re-test the quote rule on long text, add an ambiguous sample, compare with human readers,
move the rate-limit store to Redis for more than one server process.
