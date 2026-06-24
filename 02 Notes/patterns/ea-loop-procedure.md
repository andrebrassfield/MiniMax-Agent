---
description: "The 7-step procedure ea-loop-thinking applies — name the loop, walk 5 stages, check 6 blocks, pick gate, name stop condition, name cost ceiling, decide-and-report. Load when the skill is invoked. Moved from SKILL.md inline content 2026-06-22 as part of Upgrade 1 aggressive refactor."
---

# ea-loop-thinking — The 7-step Procedure

When the meta-skill loads, walk these 7 steps and emit a one-sentence
loop classification. Then proceed to Execute.

1. **Name the loop.** One sentence: "This is a [single-agent | fleet] [closed | open] loop on [scope]."
2. **Walk the 5 stages.** For each, name the artifact or the action. If a stage is implicit (e.g., "discover" is just "Andre told me what to do"), name that it's implicit and move on. See `[[02 Notes/patterns/ea-loop-vocabulary]]` for the 5 stages + failure modes.
3. **Check the 6 building blocks.** For each block, name the artifact in play. If a block is missing, flag it. See `[[02 Notes/patterns/ea-loop-vocabulary]]` for the 6 blocks table.
4. **Pick the verification gate.** Who/what checks the work? What evidence satisfies the gate? If you can't name it → halt.
5. **Name the stop condition.** When does the loop end? (Token budget, time budget, condition met, escalation to human.) If you can't name it → halt.
6. **Name the cost ceiling.** Worst case? Tokens, time, money, side effects. If unbounded → default to closed loop.
7. **Decide and report.** "Single-agent closed loop on X, plan Y, blocks A/C/D/M in play, gate is Z, stops when W, ceiling $N." Move on. Don't ask Andre to confirm — that's spec-block behavior, not loop behavior.

The output of the skill is a one-sentence loop classification in the
response preamble, then proceed.
