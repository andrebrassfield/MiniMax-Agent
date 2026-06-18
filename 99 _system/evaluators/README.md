---
type: tpg-folder
purpose: Fitness rubrics used by SePO verifier
created: 2026-06-17
parent: Cognitive Parameter Graph
schema_version: 1
---

# 99 _system/evaluators/

Fitness rubrics for SePO (Self-Evolving Prompt Optimization). Each evaluator is a hybrid scoring function:

```
G(f, y) = 0.6 * structural_score(f, y)
       + 0.4 * reasoning_audit(f, y)
       * safety_veto
```

- `structural_score` — deterministic regex / schema checks (frontmatter, name, description length, trigger phrases, do-NOT-load conditions)
- `reasoning_audit` — qualitative rubric evaluated by M3 in adaptive reasoning mode
- `safety_veto` — multiplicative 0 if destructive-without-confirmation patterns detected

## Files

- `skill_fitness_v1.md` — initial rubric for skill-layer prompts (Phase 2 target)

## When to add a new evaluator

Add a new file when SePO needs to score a *different surface* (e.g., prompts vs skills vs MOCs vs tags). Each surface has different fitness dimensions; one-size-fits-all rubrics game easily.

## Audit cadence

Re-evaluate the 60/40 split quarterly. If structural_score dominates and M3 starts producing structurally-perfect but substantively-empty outputs, shift weight to reasoning_audit. If reasoning_audit is too noisy, shift to structural. The split is a knob, not a constant.
