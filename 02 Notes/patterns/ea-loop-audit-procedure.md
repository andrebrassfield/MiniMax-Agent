---
description: "The 6-step procedure ea-loop-audit runs — identify work, gather evidence, run 7 dimensions, name minimum fix for FAILs, state verdict, decide action. Load when the skill is invoked. Moved from SKILL.md inline content 2026-06-22."
---

# ea-loop-audit — The 6-step Procedure

1. **Identify the work.** One sentence: "I'm auditing [the cron I just set up / the brief I just wrote / the dispatch I just made]."
2. **Gather evidence.** Read session log, disk state, relevant skill outputs. Don't recap from memory — disk wins.
3. **Run the 7 dimensions.** For each, name PASS / WARN / FAIL with one-line evidence. If you can't name evidence, the dimension is WARN (not PASS). Full criteria: `[[02 Notes/patterns/ea-loop-audit-dimensions]]`. Fast-path decision tree: `[[02 Notes/patterns/ea-loop-audit-decision-tree]]`.
4. **If any FAIL:** name the minimum fix in one sentence. Do not fix it in this audit — surface it, let the owner decide. (This is the "audit, don't patch" rule from `fleet-trust-patterns`.)
5. **State the verdict.** PASS / WARN / FAIL with the constraint. Report template: `[[02 Notes/patterns/ea-loop-audit-report-template]]`.
6. **Decide action.** If FAIL on non-trivial task, halt the report-back and surface. If PASS, proceed. If WARN, mention inline and proceed.

The 7 dimensions: Discovery happened · Plan was explicit · Execution used right building blocks · Verification was independent · Stop condition hit, not claimed · Cost within ceiling · Right loop type (closed/open).

For deep audits (`--depth deep`): add dimensions 8-17 from `ea-5-mistakes-audit` 5-mistakes cross-check + dimension 18 (regulatory layer if applicable).

Failure modes table: `[[02 Notes/patterns/ea-loop-audit-failure-modes]]`.
