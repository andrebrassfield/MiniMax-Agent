# Report Template — ea-loop-audit

The output report template. The audit produces this report
unless `--write <path>` is passed (which writes to a file
instead of returning in-session).

## Standard report (7 dimensions)

```markdown
# Loop Audit: [work being audited]

**Audit time:** [timestamp]
**Auditor:** Mavis (EA) | [or: verifier agent]
**Audit depth:** standard | deep

## Dimensions

1. Discovery:  PASS | WARN | FAIL — [one-line evidence]
2. Plan:       PASS | WARN | FAIL — [one-line evidence]
3. Blocks:     PASS | WARN | FAIL — [one-line evidence; list which blocks were in play, which absent]
4. Verify:     PASS | WARN | FAIL — [one-line evidence; name the verifier]
5. Stop:       PASS | WARN | FAIL — [one-line evidence; state the stop condition]
6. Cost:       PASS | WARN | FAIL — [one-line evidence; state the ceiling + actual]
7. Type:       PASS | WARN | FAIL — [one-line evidence; closed or open, justified]

## Critical failures (if any)

- [Dimension name]: [minimum fix in one sentence]

## Verdict

- **PASS:** loop ran correctly, work is accepted
- **WARN:** minor gaps, acceptable with the named mitigations
- **FAIL:** loop did not run correctly, do not accept the work; surface the gaps to the owner
```

## Deep report (17 dimensions, with --depth deep)

For deep audits, add dimensions 8-17 (5-mistakes cross-check)
+ dimension 18 (regulatory layer if applicable):

```markdown
## 5-Mistakes Cross-Check (deep audit only)

8.  Architecture obsession:  PASS | WARN | FAIL — [evidence]
9.  Data as commodity:       PASS | WARN | FAIL — [evidence]
10. Skipping scaling math:   PASS | WARN | FAIL — [evidence]
11. Stopping at SFT:         PASS | WARN | FAIL — [evidence]
12. Surface metrics:         PASS | WARN | FAIL — [evidence]
13. Skipping RLVR:           PASS | WARN | FAIL — [evidence]
14. Saturated benchmarks:    PASS | WARN | FAIL — [evidence]
15. Inference cost:          PASS | WARN | FAIL — [evidence]
16. No eval pipeline:        PASS | WARN | FAIL — [evidence]
17. No observability:        PASS | WARN | FAIL — [evidence]
18. Regulatory layer:        PASS | WARN | FAIL | N/A — [evidence; if regulated domain, name the regulator]
```

## Persisting the report

When `--write <path>` is passed:

```bash
# Path convention
report_path="03 Projects/Mavis EA Design/audits/loop-audit-YYYY-MM-DD-HHMM.md"
mkdir -p "$(dirname "$report_path")"
# Write the report (in-session, use the Write tool)
```

The audit directory is at
`03 Projects/Mavis EA Design/audits/`. Audits persist for
quarterly review and for the 5-mistakes cross-check trend
analysis.

## How to fill "one-line evidence"

The evidence line is a disk hit, not a recap. Examples:

- D1: "Directive read from session log mvs_abc...; loaded
  Mavis MEMORY.md; scope named in first todowrite."
- D2: "todowrite created with 4 steps + 1 verification gate."
- D3: "Skills: x-researcher (brief), x-scribe (draft).
  Subagent: x-scribe spawned via spawn command. Memory:
  Mavis MEMORY.md consulted."
- D4: "Verifier: M3 (different model from M2.7 executor).
  Evidence: <file path> PASS, <test name> exit code 0."
- D5: "Stop condition: 'all 5 eval cases PASS'. Met because:
  tests/eval-cases.md shows 5/5 PASS."
- D6: "Ceiling: 5 minutes, ~$0.50. Actual: 3.2 min, $0.31.
  Within ceiling."
- D7: "Closed loop (bounded: 5 eval cases, gated by D4,
  affordable per D6)."

If the auditor can't produce a disk hit for evidence, the
dimension is WARN (not PASS).
