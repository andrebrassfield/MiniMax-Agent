---
description: "The 6-step procedure ea-5-mistakes-audit runs — pick work surface, walk 11 dimensions, aggregate findings, prioritize fixes, decide action, report. Load when the skill is invoked. Moved from SKILL.md inline content 2026-06-22 as part of Upgrade 1 aggressive refactor."
---

# ea-5-mistakes-audit — The 6-step Procedure

1. **Pick a work surface to audit.** One sentence: "I'm auditing [this skill / this loop / this workflow]."
2. **Walk the 11 dimensions.** For each, answer Present? / Evidence? / Minimum fix? Full dimension content at `[[02 Notes/patterns/ea-5-mistakes-dimensions]]`.
3. **Aggregate findings.** Count dimensions where answer was "yes." That count = audit severity.
4. **Prioritize fixes.** Additions 6-11 are higher leverage in 2026 than originals 1-5. For regulated domains, dimension 11 is FIRST priority.
5. **Decide action.** 3+ present → redesign, not patch. 1-2 → fix inline. 0 → ship.
6. **Report.** "[N]/11 dimensions present. Top fix: [dimension]. Proceeding to fix / halting for Andre's call."

The 11 dimensions: architecture obsession, data as commodity, skipping scaling math, stopping at SFT, trusting surface metrics, skipping RLVR (Karpathy 2025), saturated benchmarks (MMLU-Pro), inference cost, no eval pipeline, no observability, regulatory layer (EU AI Act / FDA / HIPAA / UPL). Source table in `[[02 Notes/patterns/ea-5-mistakes-dimensions]]`. Regulatory specifics in `[[02 Notes/patterns/ea-5-mistakes-regulatory-regimes]]`.

The audit is read-only. Disk wins over recap. Modern additions are 2025-2026 specific. For peer-agent audits (Hermes, OpenClaw): state findings, don't fix.
