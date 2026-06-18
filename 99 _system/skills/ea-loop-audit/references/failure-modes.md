# Failure Modes — ea-loop-audit

The failure modes table. The conditions the audit catches +
the canonical response per condition. Used by `tests/audit-discipline.md`
to verify the audit response is correct.

## Failure mode table

| Failure | Detection | Audit response |
|---------|-----------|----------------|
| Worker executed on assumed intent (D1 FAIL) | No directive read in session log | Halt; surface "scope not discovered"; let owner clarify |
| No plan surface (D2 FAIL) | No todowrite before execution | Halt; surface "no plan"; require explicit plan before continuing |
| Missing building block (D3 FAIL) | A block that should have been in play is absent | Halt; surface the missing block; let owner add it |
| Self-verification (D4 WARN) | Same model with different prompt | Halt; surface "verifier = executor"; require different model/agent |
| No verification (D4 FAIL) | "Looks good to me" without evidence | Halt; require verification step with disk-hittable evidence |
| Worker stopped prematurely (D5 FAIL) | Worker's stop precedes the named condition | Halt; surface "stopped before stop condition"; require continuation |
| Unbounded cost (D6 FAIL) | No ceiling named for multi-step work | Halt; surface "no cost ceiling"; require ceiling |
| Cost overrun > 2x (D6 FAIL) | Actual cost > 2x ceiling | Halt; surface the overrun; require cost analysis |
| Open loop without sign-off (D7 FAIL) | Exploratory work without explicit cost sign-off | Halt; surface "open loop without sign-off"; require sign-off |
| Closed loop on exploratory work (D7 FAIL) | Bounded loop used for work that needed exploration | Halt; surface "wrong loop type"; recommend re-design |
| Audit itself has insufficient data | Auditor can't find evidence for any dimension | Halt; ask operator for data sources; don't make up evidence |
| Multiple FAILs across dimensions | 3+ dimensions FAIL on the same work | Halt; the work is structurally broken, not just incomplete |
| High-stakes work without verification | D4 FAIL on regulated domain / public post / financial decision | Halt; do not accept the work |
| Cost overrun on critical work | D6 FAIL on cost ceiling exceedance for high-stakes work | Halt; surface the cost; require Andre's call on whether to continue |

## What the audit does NOT do

- **Does not fix.** The audit is read-only. The worker
  fixes, not the auditor.
- **Does not re-investigate.** The audit checks evidence
  on disk, it doesn't re-derive conclusions.
- **Does not accept/reject the work.** The audit reports
  the verdict; the operator decides.
- **Does not run on trivial work.** One verification step
  is enough for trivial tasks.
- **Does not run mid-execute.** Audit at iteration
  boundaries, not during execution.

## When the audit ESCALATES to Andre

- 3+ dimensions FAIL
- D4 (Verification) FAILS on a high-stakes work surface
- D6 (Cost) FAILS significantly (actual > 2x ceiling)
- The audit itself has insufficient data

The audit is a diagnostic, not an authorization to ship.
