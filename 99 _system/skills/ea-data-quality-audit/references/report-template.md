# Report Template — ea-data-quality-audit

The audit report template. The chief writes the report to
`03 Projects/Mavis EA Design/reports/data-quality-audit-YYYY-MM-DD.md`
after running the 5 sub-steps.

## Full template

```markdown
# Data Quality Audit: Mavis Corpus

**Audit time:** [timestamp]
**Auditor:** Mavis (EA)
**Scope:** [memory + skills + vault + kanban — which surfaces in scope]
**Window:** [the period the corpus covers]

## 1. Inventory

[table from sub-step 1 — file path, size, last modified, 1-line "what's in it" tag]

## 2. Filter list

[entries to remove/rewrite, with reasons from sub-step 2]

## 3. Dedup map

[canonical file + links to update, from sub-step 3]

## 4. Quality scores

[per-entry score table, from sub-step 4]

## 5. Balance report

[mix dimensions, current vs target, from sub-step 5]

## 6. Recommended actions (in priority order)

1. [highest-leverage fix]
2. [next fix]
3. ...
```

## Per-section content discipline

- **Header:** audit time (ISO 8601), auditor (Mavis EA),
  scope (which surfaces in scope), window (the period
  the corpus covers).
- **Inventory:** real file paths, sizes from `wc -c`, mtimes
  from `ls -la`, 1-line "what's in it" tag from `head -3`.
- **Filter list:** file:line references for every flagged
  entry, with the specific filter criterion that fired.
- **Dedup map:** canonical file per claim, with the links
  to update.
- **Quality scores:** per-entry table. Be honest — if it's
  LOW, say so. Don't pad scores.
- **Balance report:** for each dimension, current
  distribution + target. Targets are operator's call
  (Mavis proposes; Andre decides).
- **Recommended actions:** priority-ordered. Top 3 should
  be doable in one session. Don't list 20 items; pick the
  highest-leverage 3-5.

## What this report is NOT

- **Not the fix.** The report is descriptive. Fixes are a
  separate step (`ea-skill-evolution` for skill
  mutations, manual edit for memory entries).
- **Not a re-architecture.** The audit is about the
  corpus, not the structure. Architecture changes go
  elsewhere.
- **Not exhaustive.** The report surfaces the most-
  leverage items. If the corpus has 100 LOW items, the
  report names 3-5, not all 100.
- **Not a recurring document.** Each run produces a new
  file with the date. The previous run's report is
  history; don't append.
