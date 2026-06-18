# Decision rule test — sepo-runner

Verify decision rules fire at correct F(P_t) thresholds.

## Cases

| F(P_t) | Expected decision |
|---|---|
| 0.95 | skip |
| 0.88 | skip (boundary, included) |
| 0.87 | accept_baseline |
| 0.70 | accept_baseline (boundary, included) |
| 0.69 | needs_mutation |
| 0.50 | needs_mutation |

## Pass criteria

- 0.95, 0.88 → skip (no mutation)
- 0.87, 0.70 → accept_baseline (record baseline, no mutation)
- 0.69, 0.50 → needs_mutation (continue to textual gradient + mutator)
- Halt fires correctly at each decision point

## Special cases

- mutation_count > 5 AND decision = needs_mutation → halt and alert Andre
- F(P_{t+1}) > F(P_t) AND V(P_{t+1}) = 0 → reject_safety (override accept logic)
- F(P_{t+1}) ≤ F(P_t) → reject_no_improvement
