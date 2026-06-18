---
type: tpg-folder
purpose: Human-curated test inputs (x_i) + expected outputs (y_i) for SePO fitness evaluation
created: 2026-06-17
parent: Cognitive Parameter Graph
schema_version: 1
curator: Andre
curation_cadence: monthly
---

# 99 _system/golden-set/

Curated test inputs and expected outputs. **Andre curates**; Mavis proposes. SePO optimizes against this — the GoldenSet IS the definition of "good" for each skill.

## Format per skill

One file per skill (e.g., `ea-decision-logger.md`). Inside:

```markdown
---
parameter_id: ea-decision-logger
curated_by: Andre
last_review: 2026-06-17
case_count: 3
---

## Case 1: <name>

**Input (x_i):**
> Verbatim chat snippet or scenario description.

**Expected output (y_i):**
> What the right output looks like. Schema-valid + reasonable example.

**Reasoning for inclusion:**
> Why this case matters. What failure mode it catches.

## Case 2: ...
```

## Curation cadence

**Monthly review.** Drift detection: if GoldenSet was last reviewed >30 days ago, SePO halts and alerts. Drift = stale "good output" definition = local optimum lock-in.

## Anti-patterns

- Letting Mavis curate independently (alignment failure mode — Mavis optimizes for what Mavis can already produce)
- Adding cases without expected outputs (incomplete test, can't compute fitness)
- Skipping cases that already pass (the failing cases drive improvement)
