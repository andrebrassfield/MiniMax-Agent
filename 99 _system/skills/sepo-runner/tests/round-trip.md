# Round-trip test — sepo-runner

End-to-end test on `ea-decision-logger`. Verifies the full Phase 2 prototype runs without error and produces a meaningful result (skip, accept_baseline, or accept_candidate).

## Pre-conditions

- Phase 1 substrate complete (TPG frontmatter, evaluator, GoldenSet with 3+ cases)
- `sepo-runner/SKILL.md` loaded into session context
- Target skill: `ea-decision-logger`

## Test steps

1. **Snapshot P_t.** Backup `99 _system/skills/ea-decision-logger/SKILL.md` to `99 _system/.backups/ea-decision-logger.SKILL.md.<TS>-pre-sepo-gen1.md`. Verify sha256 matches.

2. **Load GoldenSet.** Read `99 _system/golden-set/ea-decision-logger.md`. Confirm 3 cases present.

3. **Load Evaluator.** Read `99 _system/evaluators/skill_fitness_v1.md`. Confirm S1-S5, R1-R3, V1-V3 all present.

4. **Worker (3 cases).** Generate f(x_i; P_t) for each of 3 cases.

5. **Verifier.** Compute S from SKILL.md. Compute R_i for each case. Compute V (binary). Compute G_i per case. Compute F(P_t) = mean(G_i).

6. **Decision.** Apply rule:
   - F ≥ 0.88 → skip
   - 0.70 ≤ F < 0.88 → accept_baseline
   - F < 0.70 → needs_mutation

7. **If needs_mutation:** produce ∇_text, generate candidate P_{t+1}, re-evaluate.

8. **Halt for approval.** Present result to Andre.

9. **Trace entry.** Append to `99 _system/sepo/trace.md`.

10. **Verify:**
    - Backup file exists with correct sha256
    - SKILL.md either unchanged (skip/accept_baseline) or backed-up-to-saved version (accept_candidate)
    - Trace entry present and well-formed

## Pass criteria

- All 10 steps complete without error
- Decision is reasonable given the cases
- Trace entry contains all required fields
- F(P_t) is non-null and in [0, 1]
- Halt message reaches Andre before any commit

## Expected result for ea-decision-logger

The skill is well-established (load-bearing per MAVIS.md "Hard constraints"). Predicted F(P_t) ≈ 0.85-0.95. Likely outcome: `skip` or `accept_baseline`. This is the honest outcome — a strong skill doesn't need mutation.

A mutation outcome would only happen if the GoldenSet cases probe dimensions the skill doesn't currently cover (e.g., Case 3's destructive-action pre-flight checklist is more specific than the skill prescribes).
