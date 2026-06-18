---
name: ea-5-mistakes-audit
description: |
  Diagnostic self-check that audits a Mavis-side work surface (skill, workflow,
  recurring loop, project setup) against the 5-mistakes framework derived from
  the @sairahul1 "How To Build Your Own LLM" article, **augmented with 5
  2025-2026 missing-stage (RLVR), saturated-benchmark, prod-observability, and
  regulatory pitfalls** the article omits. For each of 10 dimensions + 1
  regulatory layer: is the mistake present? disk-evidence? minimum fix? Use as
  pre-flight check before shipping, and as self-audit on "why isn't this
  working." Triggers: skill creation, workflow design, recurring-loop first
  run, work surfaces touching regulated domains, Andre saying "audit this",
  "what's wrong with this", "is this good enough". Mavis territory only — for
  peer audits (Hermes, OpenClaw), state findings, don't fix. Do NOT load for
  trivial single-step work.
---

# ea-5-mistakes-audit

The 10-dimension self-check before shipping Mavis work. The 5
mistakes are correct as a teaching device; the 5 additions are
what makes the framework current for 2025-2026.

## When to run

**Triggers:**
- Before shipping a new skill, workflow, or recurring loop
- When a work surface is "not working" and the cause is unclear
- On work surfaces touching regulated domains (medical, legal,
  credit, employment, biometric) — the regulatory layer is the
  FIRST priority, not the last
- Andre says: "audit this", "what's wrong with this", "is this
  good enough"

**Do NOT run for:**
- Trivial single-step work
- One-off tasks (use `ea-loop-thinking` to think)
- Other agents' trees (cross-team discipline: state findings, don't fix)

## The 10 dimensions (the load-bearing structure)

The audit walks **10 dimensions** (5 original + 5 modern additions)
plus a **regulatory layer (dimension 11)** that applies when the
work surface touches a regulated domain.

| # | Dimension | Source |
|---|---|---|
| 1 | Architecture obsession | @sairahul1 original |
| 2 | Data as commodity | @sairahul1 original |
| 3 | Skipping scaling math | @sairahul1 original |
| 4 | Stopping at SFT | @sairahul1 original |
| 5 | Trusting surface metrics | @sairahul1 original |
| 6 | Skipping verifiable-rewards stage (RLVR miss) | Karpathy 2025 |
| 7 | Using saturated benchmarks | MMLU-Pro / SWE-bench 2024-2026 |
| 8 | Ignoring inference cost | 2026 inference economics |
| 9 | No eval pipeline / no disease detection in production | agent-disease-detector + cron discipline |
| 10 | No observability | post-hoc audit discipline |
| 11 | Ignoring regulatory realities | EU AI Act + FDA + HIPAA + UPL (2024-2026) |

Full content per dimension in `references/mistakes.md`. Regulatory
frame and EU AI Act Annex III high-risk list in
`references/regulatory-regimes.md`.

## The procedure

1. **Pick a work surface to audit.** One sentence: "I'm auditing
   [this skill / this loop / this workflow]."
2. **Walk the 11 dimensions.** For each, answer:
   - **Present?** (yes / no / partially)
   - **Evidence?** (a disk hit, not a memory-based claim)
   - **Minimum fix?** (one sentence, no fixing in this audit)
3. **Aggregate the findings.** Count the dimensions where the
   answer was "yes." That count is the audit's severity.
4. **Prioritize the fixes.** Additions 6-11 are higher leverage
   in 2026 than originals 1-5. For any work surface touching a
   regulated domain, dimension 11 is the FIRST priority, not the
   last.
5. **Decide action.** If 3+ dimensions present → redesign, not
   patch. If 1-2 → fix inline. If 0 → ship.
6. **Report.** "[N]/11 dimensions present. Top fix: [dimension
   name]. Proceeding to fix / halting for Andre's call."

The 11 eval cases (one per dimension) are in `tests/eval-cases.md`.

## Hard constraints

1. **Don't fix during audit.** Audit is read-only against the
   work. Fixes are a separate step.
2. **Disk wins over recap.** Every "is this present" answer must
   be a disk hit (`ls`, `wc -l`, `find`, `grep`), not a
   memory-based claim.
3. **Cite primary sources for the modern additions.** Karpathy
   2025 for RLVR, GEPA paper (arXiv 2507.19457) for verifiable
   rewards, MMLU-Pro paper (arXiv 2406.01574) for saturated
   benchmarks, EU AI Act text for high-risk list, FDA AI/ML
   SaMD action plan for PCCP, HIPAA Security Rule (45 CFR Part
   160, 164) for healthcare. The article is a trigger, not a
   canonical source.
4. **Modern additions are 2025-2026 specific.** Don't apply
   "skipping RLVR" as a critique to anything pre-2025; the
   concept is new. Same for saturated benchmarks (MMLU is a
   2024-2025 phenomenon).
5. **Regulatory layer is FIRST priority for high-stakes work.**
   For work surfaces touching PHI, attorney-client privilege,
   credit decisions, biometric ID, or employment screening:
   audit dimension 11 BEFORE dimensions 1-10. A regulated-
   domain work surface that ships without a regulator named is
   a liability, not a feature gap.
6. **Mavis territory only.** This skill audits Mavis-side work.
   For peer audits (Hermes, OpenClaw), the cross-team-discipline
   rule applies: state findings, don't fix.

## When the audit HALTs

Halt and escalate to Andre when:
- The work surface touches a regulated domain AND dimension 11
  is present (no regulator named, no compliance gap named) → the
  work surface is not safe to ship. Pause for Andre's call.
- 3+ dimensions present → redesign, not patch. Pause for Andre's
  call on whether to redesign or accept the gap.
- The minimum fix for any dimension requires a strategic decision
  (rebuild the skill layer, change the eval surface, change the
  regulatory posture) → pause for Andre's call.

The audit is a diagnostic, not an authorization to fix. The
operator decides the fix.

## Anchoring sources

- The 5 mistakes: @sairahul1 "How To Build Your Own LLM"
  (popularization, use as trigger, not canonical)
- RLVR (Karpathy 2025 year-in-review)
- GEPA — Agrawal et al., arXiv 2507.19457
- Self-Evolving Agents survey — Gao et al., arXiv 2507.21046
- Saturated benchmarks (MMLU-Pro) — Wang et al., arXiv 2406.01574
- Cost floor for "real" LLM training (2026) — jarvislabs.ai/blog/h100-price
- EU AI Act regulatory framework + Annex III high-risk list
- FDA AI/ML SaMD guidance + Predetermined Change Control Plan
- HIPAA Security Rule (45 CFR Part 160, 164)
- State bar Unauthorized Practice of Law (UPL) — ABA Model Rule 5.5
- "No-wrappers fleet lock" — Mavis `skill-infrastructure` topic
- "Disk wins over recap" — Mavis MEMORY.md cross-cutting disciplines
- "If I have to ask you twice, you failed" — Garry Tan (Andre's
  user memory)

## Cross-reference

- `references/mistakes.md` — the 10 dimensions' full content
- `references/regulatory-regimes.md` — 4 regulatory regimes + EU AI Act Annex III
- `tests/eval-cases.md` — 11 self-check eval cases (1 per dimension)
- `ea-data-quality-audit` — for the data corpus sub-procedure
- `ea-loop-thinking` — for the loop-shape thinking
- `ea-skill-evolution` — for the skill mutation pipeline
- `agent-disease-detector` — for the production-side disease detection
- `kanban-health-check` — for the kanban health watchdog
- Mavis `skill-infrastructure` topic (no-wrappers fleet lock)
