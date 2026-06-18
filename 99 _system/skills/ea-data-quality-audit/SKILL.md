---
name: ea-data-quality-audit
description: |
  Operational skill that audits Mavis's own "training data" (memory entries,
  skill files, vault files, kanban state) using the LLM data-cleaning
  framework: (1) extract clean content from raw state, (2) filter noise /
  harmful / off-topic, (3) deduplicate by entry / topic / line, (4) quality-
  score entries (is this still load-bearing, or stale?), (5) balance the mix
  (memory vs topic files vs skills vs kanban). The "data quality > architec-
  ture" insight from the LLM-training article applies directly to Mavis: the
  agent's memory + skill corpus IS the data, and the ceiling on output
  quality is the ceiling on the corpus. Triggers: "audit my data", "clean
  the memory", "is the vault fresh", "what's in the skill library", or as a
  recurring monthly check. Pairs with `ea-5-mistakes-audit` (Mistake 2:
  treating data as commodity) and `vault-30day-auditor` (the modification-
  frequency surface). Do NOT load for ad-hoc memory entries, for other
  agents' trees (Mavis territory only), or for less than 7 days of vault
  history (the window is too narrow to surface patterns).
---

# ea-data-quality-audit

The corpus-as-data audit. Adapts the LLM data-cleaning
framework ("data quality > architecture") to Mavis's
surfaces — memory, skills, vault, kanban. The skill
library + memory + vault IS the data; the corpus's
quality is the ceiling on output quality.

## When to run

**Triggers:**
- "audit my data" / "clean the memory" / "is the vault fresh"
- "what's in the skill library" / "are the skills still load-bearing"
- "I think the corpus has gone stale"
- Monthly cadence (recommended: first Sunday of the month,
  after `vault-30day-auditor`)

**Pairing triggers:**
- After `ea-5-mistakes-audit` flags Mistake 2 (treating data
  as commodity)
- After `vault-30day-auditor` surfaces a stale or saturated
  work surface
- After a major project transition (clean the old
  project's residue)

**Do NOT run for:**
- Ad-hoc memory entries (single entry, not corpus)
- Other agents' trees (Mavis territory only —
  `~/.mavis/agents/mavis/` and `~/MiniMax-Agent/`)
- Less than 7 days of vault history
- Active in-flight work (the audit is read-only against the
  corpus, but the corpus should be quiet)

## The 5 sub-steps (the load-bearing structure)

The LLM data-cleaning pipeline applied to Mavis surfaces.
Full per-sub-step detail (purpose, what to inventory,
filter criteria, dedup levels, quality-score rubric,
balance dimensions) in `references/5-sub-steps.md`. Output
report template in `references/report-template.md`.

| # | Sub-step | What it does | Source in references |
|---|---|---|---|
| 1 | **Extract** | Inventory the corpus in canonical form (paths, sizes, mtimes, 1-line "what's in it" tag) | §1 — 6 surfaces × per-surface extraction |
| 2 | **Filter** | Remove noise / harmful / off-topic (course-corrections vs memory, PII, stale claims, duplicates with drift) | §2 — 5 filter criteria |
| 3 | **Dedupe** | Remove redundant copies so the canonical version is the only version (by file / topic / line) | §3 — 3 dedup levels + tools |
| 4 | **Quality-score** | Score every entry 4-point: HIGH (load-bearing) / MEDIUM (overhead) / LOW (rewrite) / DEAD (remove) | §4 — score rubric + quality signals |
| 5 | **Balance** | Ensure the corpus is well-distributed across Mavis's actual work surfaces (memory vs skills vs vault vs kanban; domain; temporal; rule vs example vs context) | §5 — 4 balance dimensions + target distribution |

**The article's analog:** "data quality beats data quantity"
→ the Mavis version: the corpus's quality is the ceiling
on output quality. Architecture is one paragraph; the
corpus is the load-bearing layer.

## The procedure (overview)

The full procedure in `references/procedure.md`. The
high-level flow:

1. **Pick the scope.** All surfaces by default; a specific
   surface if Andre says so.
2. **Run sub-step 1 (inventory).** Use `find`, `wc -l`,
   `ls -la`. Disk hits only.
3. **Run sub-step 2 (filter).** Read the entries, don't
   recap. Apply the filter criteria.
4. **Run sub-step 3 (dedupe).** Use `grep` + `diff`. Read
   with intent before merging.
5. **Run sub-step 4 (quality-score).** Score every entry.
   Be honest — if it's LOW, say so.
6. **Run sub-step 5 (balance).** Compare to Andre's actual
   work mix (use `vault-30day-auditor` for the baseline).
7. **Aggregate to the report.** Prioritize recommended
   actions. Top 3 should be doable in one session.
8. **Decide action.** If on cron, write the report and
   notify. If on demand, present the report and ask for
   go-ahead on actions.

## The output (the audit report)

A single markdown file at
`03 Projects/Mavis EA Design/reports/data-quality-audit-YYYY-MM-DD.md`.
Full template in `references/report-template.md`. Structure:

1. Header (audit time, scope, window)
2. Inventory (from sub-step 1)
3. Filter list (from sub-step 2)
4. Dedup map (from sub-step 3)
5. Quality scores (from sub-step 4)
6. Balance report (from sub-step 5)
7. Recommended actions (priority-ordered; top 3 doable
   in one session)

The report is **descriptive, not prescriptive** — it
surfaces what the corpus contains and where the gaps are.
The "recommended actions" are the operator's decisions.

## Hard constraints

1. **Disk is ground truth.** Every inventory, filter, dedup,
   and score must reference a real file path. Show the
   file:line, not a recap.
2. **Read-only during audit.** The audit doesn't delete or
   rewrite anything. It produces a recommended-actions
   list. Fixes are a separate step, owned by the chief.
3. **Mavis territory only.** Inventory is
   `~/.mavis/agents/mavis/` and `~/MiniMax-Agent/`. Do not
   cross into `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`,
   `~/.hermes-evolution/`, or any other agent's tree. (Per
   ABSOLUTE SEPARATION rule.)
4. **The article is a trigger, not a source.** The
   5-sub-step framework is from the LLM data-cleaning
   pipeline; the Mavis mapping is local. Cite the article
   for the framework, but the specific filter criteria,
   score rubric, and balance dimensions are Mavis-
   specific.
5. **No fixing during audit.** If the audit finds a
   critical entry that is actively harmful, surface it
   inline and stop — don't fix in this skill.
6. **Read with intent during dedup.** Two entries that
   look the same may be two facets of the same claim.
   Don't auto-merge; check first.

## When the skill HALTs

Halt and escalate to Andre when:
- Corpus inventory can't be enumerated (filesystem error)
  — HALT (H1)
- An actively harmful entry is found (memory says one
  thing, Andre's later notes say another) — surface
  inline, HALT for the rest of the audit, don't fix in
  this skill (H2)
- The recommended-actions list has 5+ HIGH-priority items
  — the corpus needs a multi-session cleanup, not a
  one-shot fix (H3)
- The audit itself has insufficient data (corpus is too
  small or too new) — HALT, note the data limitation
  (H4)

The audit is a diagnostic, not an authorization. The
operator decides the action.

## Anchoring sources

- The 5-sub-step framework: @sairahul1 "How To Build Your
  Own LLM" Stage 1 (popularization, use as trigger)
- Mavis `MEMORY.md` cross-cutting disciplines: "Disk
  wins over recap", "quantified claims need verification"
- `vault-30day-auditor` — for the work-mix baseline
- `ea-5-mistakes-audit` — for the Mistake 2 cross-check
- X-Content-Engine rule: skill agent home + vault mirror
  must be in sync

## Cross-reference

- `references/5-sub-steps.md` — full per-sub-step detail
  (purpose, criteria, dedup levels, score rubric, balance
  dimensions)
- `references/procedure.md` — the 8-step procedure
- `references/report-template.md` — the audit report
  template
- `tests/5-sub-step-checks.md` — 5 sub-step disk-verifiable
  probes
- `tests/audit-discipline.md` — disk-wins, no-fixing,
  Mavis-territory checks
- `vault-30day-auditor` — provides the work-mix baseline
- `ea-5-mistakes-audit` — Mistake 2 cross-check
- `ea-skill-evolution` — consumes the recommended-actions
  list for skill mutations
