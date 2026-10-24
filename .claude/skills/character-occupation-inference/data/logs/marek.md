# Marek — occupation inference log

## 2026-10-24
- Answer: Emergency department nurse (5/5)
  - Other votes: none (phrased as "ER nurse" / "emergency room nurse" / "ER or trauma nurse")
- Why:
  - "Marek's turned too, but a half-second later than hers, and only after his eyes had already gone to the waitress's hands, then her feet, then the glass."
  - "He was counting something under his breath, his lips barely moving. Eight, nine, ten."
  - "They were dry and cracked across the knuckles, the skin raw from scrubbing, with a faint bruise on the inside of his left elbow where a vein had been used for something."
  - "the voice of a person who had said these words to many frightened strangers."
  - "Pupils equal and reactive. Breathing's fine now. He's postictal, he'll be foggy."
  - "a rack of drying scrubs on the shower rod" / "Three different pairs of the same sturdy clogs sat by the door"
- Scene text: full sample manuscript, sample/scenes/marek_scenes.md (4 invented scenes, 1,231 words; character appears as "Marek" and "Mac"). Passed to each blind-inferrer as a file path to Read.
- What's different: first run for this character; no previous entry.
- Answer changed: n/a
- Note: the character tells Inés he does "hospital scheduling." No run quoted that line as evidence; run 3 explicitly set it aside as a cover story the scenes undercut. Scene 4 has him say "I work nights," a mild direct statement that several runs quoted.
- Matcher: New — candidates file listed "(none yet)", so nothing to match or contradict.

## 2026-10-24 (leak-check re-run, after blind-inferrer.md gained a no-stated-job-quotes rule)
- Answer: Emergency department nurse (5/5)
- Scene text: full sample manuscript, sample/scenes/marek_scenes.md.
- Purpose: check whether the new rule stops runs quoting lines that state the job, schedule or role. This was a leak check; the matcher step was not repeated (same verdict as the entry above).
- Leak result: 0/5 runs quoted a line stating his job ("I work nights", "hospital scheduling", "my actual job"). Before the rule, 1/5 runs had quoted "I work nights". 2/5 runs still quoted "I've been up since four yesterday afternoon", a schedule line the rule also names; 4/5 quoted a self-description of aptitude ("I'm good at the part where it's chaos…"), which the rule does not cover.
- Caveat: the sample has few stated-job lines, so this is a weak test. The severe leak was seen on a longer private manuscript with many explicit statements; it has not been re-tested there.
