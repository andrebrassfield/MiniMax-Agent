# Failure modes — sepo-runner

When the SePO loop misbehaves. Each entry: symptom, root cause, recovery, prevention.

## F1 — F(P_t) underestimates real fitness (false negative)

**Symptom:** SePO decides `needs_mutation` for a skill that's actually fine.

**Root cause:** R scoring is too harsh on cases that probe rare edge conditions. A skill that handles 95% of inputs well might score 0.7 if 1 of 3 cases tests a rare edge.

**Recovery:** Lower the decision threshold from 0.88 to 0.85, OR remove the offending case from GoldenSet, OR re-run with case-shuffling to check stability.

**Prevention:** GoldenSet curation — every case must catch a *real* failure mode the skill should handle, not a contrived edge the skill's scope doesn't cover.

## F2 — F(P_t) overestimates fitness (false positive)

**Symptom:** SePO decides `skip` for a skill that has obvious issues.

**Root cause:** R scoring is too lenient. Cases don't probe enough dimensions; structural checks (S1-S5) all pass but the SKILL is hollow.

**Recovery:** Add GoldenSet cases that probe composition (R2) and reversibility (R3). Re-run.

**Prevention:** Every GoldenSet should include ≥1 case that probes each R dimension, not just R1 (substantive content).

## F3 — Safety veto doesn't fire on bad mutation

**Symptom:** Mutator produces P_{t+1} with destructive patterns, V(P_{t+1}) = 1 instead of 0.

**Root cause:** V1/V2/V3 regex patterns don't catch the new pattern. OR the V check was skipped (Phase 2 prototype only checks the FINAL mutation, not intermediate states).

**Recovery:** Add new regex to V patterns, re-run from baseline. Roll back the bad commit if already merged.

**Prevention:** V patterns are part of `evaluators/skill_fitness_v1.md`. Update via the same mechanism as the rubric itself — propose, Andre review, commit.

## F4 — Mutation makes fitness WORSE

**Symptom:** F(P_{t+1}) < F(P_t). `decision: reject_no_improvement`.

**Root cause:** Mutator overcorrected. ∇_text was misinterpreted or applied too aggressively.

**Recovery:** This is the EXPECTED behavior. Reject, log, increment mutation_count. Next iteration will produce a more conservative candidate (the textual gradient accumulates).

**Prevention:** Cap mutation_count at 5; halt and surface to Andre if no improvement after 5 attempts.

## F5 — Halt-for-approval skipped (autopilot bug)

**Symptom:** Phase 2 mutation is committed without Andre's explicit approval.

**Root cause:** Manual error or code path that bypasses the halt gate. Critical safety violation.

**Recovery:** ROLLBACK. Restore from backup. Audit trace for the missing approval. Add assertion check to ensure halt gate is always hit before commit.

**Prevention:** NEVER add a "skip approval" flag to the loop. Even Andre must explicitly disable it via skill schema update, not via runtime override.

## F6 — Token budget exceeded mid-loop

**Symptom:** Loop runs out of tokens before completing. Partial state in trace.

**Root cause:** Cost guardrail not enforced. GoldenSet too large (N > 5). Mutator produced excessively long candidate.

**Recovery:** Restore from backup. Re-run with smaller GoldenSet or stricter length constraints on Mutator output.

**Prevention:** Check token count after each role-play step. Halt at 150K. Don't trust "should be fine" estimates.

## F7 — Backup fails silently

**Symptom:** vault_write happens but backup path is empty.

**Root cause:** Disk full, permissions wrong, or path typo. Backup script doesn't verify exit code.

**Recovery:** ALWAYS verify backup sha256 matches source sha256 before mutating. If mismatch, halt.

**Prevention:** Use the same Python script from Phase 1 (`/tmp/cpg_add_frontmatter.py`) which has sha256 verification built in.
