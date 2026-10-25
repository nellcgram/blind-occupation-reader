# Case study: a blind-reader test for "show, don't tell"

This is my earliest project where Claude did the most work (creating agents with few instructions) to teach me the overall structure of system instructions. I’m including it to show my thought process.

## Introduction
I built this to solve a characterization problem. I wanted to submit all manuscript scenes to Claude, then have Claude figure out what job made the most sense for the character across scenes.

## Problems
1. I wanted the answer to come from the character’s psychology and behavior, not how he or other characters described him in dialogue, in case he was saying he was a soldier but was actually a spy.
2. I wanted a solution that allowed me to avoid adding the same scenes to each fresh Claude chat.
3. I was tired of constant prompt engineering, asking variations on the same questions: "From his behavior here, has his likely job changed? Are both operator and intelligence viable options? Which is more viable? Ignore all dialogue from any character and focus on his behavior.”
4. I wanted to learn from Claude what system instructions worked best for this problem.

## Solutions
I asked Claude to build what it needed, then I rewrote the agent descriptions and prompts and used Claude Code to test results, and rewrote again. Each test I ran resulted in a new log of results and a new occupation considered.

My final problem was that this was not a project others could use because it used my own manuscript. I had Claude write sample scenes and rerun the tests so it made a new log and candidate file.

## Conclusion
I ultimately decided that this was more work with Claude than it was worth. Testing the agents and skill and adjusting the writing took more time than my original prompt engineering and re-submitting scenes had.

The answer I settled on was to use less Claude in the writing process. I interrogated why I had been using Claude in the first place: to get a general sense of the character’s psychology from “someone else’s” perspective. I decided to write many more scenes, let the writing process determine what occupation seemed to fit best over time (possibly many months of writing and revising), and then take distance from the work before I assessed whether the occupation seemed accurate. This felt like a case of outsourcing my judgment to AI too much.

------

## Technical specs during the creation process
The 2 agents created read all manuscript scenes, vote on the job, quote their evidence, and log how the answer changes. Five independent "readers" (subagents) see the scene text and guess the job, ignoring stated jobs (dialogue), then report answers with text quoted as evidence. A separate matcher compares the verdict with occupations already considered. Each run is logged with the text used.

### Decisions I made during the process
- Readers don't see the list of possible jobs
- Answers need to include text quotes so the user knows this is evidence-based, not guesswork
- Agents can use only the Read tool, do not write or run anything
- Agents should reference the whole manuscript, not only some scenes
- One candidates file per character, with a `Manuscript:` path and aliases (a hard-coded path and name-based scene selection both caused errors)

### What went wrong
1. **Runaway agents.** Parallel subagents re-ran the whole workflow and, in one case, pushed a deletion to an unrelated
   repo. The agents had full shell access they never needed. Fix: Read-only tools, plus a permission prompt before any push.
2. **Stated-job quotes.** Subagents kept quoting lines that named the job (dialogue, not behavior). I added a rule to cut this.
3. **The character had 2 names.** One run picked scenes by one of the character's two names. Fix: per-character manuscript path and alias rules.

### Not measured
Agreement with human readers; subtle or ambiguous writing (the sample is clear on purpose); behavior of other models.

