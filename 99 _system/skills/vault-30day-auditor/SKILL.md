---
name: vault-30day-auditor
description: |
  Run a 30-day operational footprint audit on Andre's vault — scan
  `01 Daily/` and `03 Projects/` for files modified in the last 30 days,
  extract core topics, repetitive manual tasks, and active project pipelines
  strictly from file contents and modification frequency, then synthesize a
  Factual Index report to `03 Projects/Mavis EA Design/reports/30-day-footprint-YYYY-MM-DD.md`.
  Triggers: "vault 30-day audit", "what am I working on", "footprint report",
  "30-day audit", "map my activity", "what did I do this month". Hard
  constraint: do not invent context, do not include projects/topics that
  are not evidenced by on-disk files. Synthesis is done in-session by Mavis
  (chief-of-staff work) — do NOT dispatch the X-Content-Engine
  `x-researcher` for this; that agent is scoped to X content research, not
  vault activity audits. Mavis territory only — does not cross into
  `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/`.
---

# vault-30day-auditor

The "what am I actually working on" audit. Generates a
**Factual Index** of Andre's operational footprint over the
last 30 days — purely from on-disk files, no recap. The
audit is read-only against the vault filesystem and produces
one report per run.

## When to run

**Triggers:**
- "vault 30-day audit" / "run a 30-day audit"
- "what am I working on" / "footprint report"
- "what did I do this month" / "monthly activity"
- "map my activity" / "operational footprint"

**Do NOT run for:**
- A specific single project (just `ls` the project dir)
- Less than 7 days of vault history (window too narrow)
- Vault files Andre hasn't touched (the audit measures
  *modification* frequency, not existence)
- Non-vault data (calendar, email, browser history are out
  of scope)

## Inputs

| Input | Default | Required |
|---|---|---|
| Vault root | `/Users/brassfieldventuresllc/MiniMax-Agent` | no |
| Target dirs | `01 Daily/` and `03 Projects/` (recursive) | no |
| Window | last 30 days (T-30 → T, where T = today) | no |
| Report path | `03 Projects/Mavis EA Design/reports/30-day-footprint-YYYY-MM-DD.md` | no |
| Top-N projects to read in full | 5 (by modification count) | no |

## The 9-section report (the load-bearing shape)

The report has 9 sections, in this order. Full template +
field shapes in `references/report-template.md`. The 9-step
procedure with bash commands in
`references/audit-procedure.md`. Safety halts + failure
modes in `references/safety-halts.md`.

| # | Section | Source |
|---|---|---|
| 1 | Header | date, vault root, window, file counts, generation timestamp |
| 2 | Decision log | any non-obvious choices made during the audit |
| 3 | Daily notes cadence | which days have notes, mtime gaps |
| 4 | Active project pipelines (top 5) | projects with file activity, ranked by modification count |
| 5 | Core topics | subjects in 2+ files |
| 6 | Repetitive manual tasks | workflows in 3+ files |
| 7 | Inbox / hot files | `00 Inbox/` modified in window |
| 8 | Automation candidates | derived from repetitive tasks |
| 9 | Appendix: full file inventory | path + mtime + size for traceability |

The report is **descriptive, not prescriptive** — it
surfaces what Andre is doing, not what he should do. The
"automation candidate" section flags the single most
obvious next target but does not draft the skill.

## The 9-step procedure (overview)

The full 9-step procedure with bash commands lives in
`references/audit-procedure.md`. The high-level flow:

1. **Verify ground truth** — vault root + target dirs exist
2. **Establish the 30-day window** — T-30 to T (today)
3. **Inventory files** in window — `find -mtime -30`
4. **Rank projects** by modification count
5. **Read the top files** in each top-N project (full reads)
6. **Daily notes cadence** — which days have notes
7. **Synthesize** in-session (NOT dispatched to x-researcher)
8. **Write the report** to `reports/30-day-footprint-YYYY-MM-DD.md`
9. **Return summary** — report path, totals, top 3, candidate

## The hard constraints (READ THIS)

1. **No invented context.** Every claim must be traceable to
   a specific file in the report's appendix. If a project
   is mentioned in the report, it must appear in the file
   inventory. If a topic is mentioned, it must come from
   reading at least one file that contains it.
2. **Disk is ground truth.** Do not pull topics from memory
   or prior context. Re-read the files in this session.
3. **Mavis synthesizes, not x-researcher.** The audit is
   chief-of-staff synthesis work. Dispatching the
   X-Content-Engine `x-researcher` for this would be a
   domain mismatch — that agent is scoped to X content
   research. Do the synthesis in-session.
4. **Mavis territory only.** The audit does not cross into
   `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`,
   `~/.hermes-evolution/`, or any other agent's tree.
5. **Quantified claims need verification.** "X projects
   active" requires `find | wc -l` against the actual
   files, not an `ls` count.
6. **Window edge cases.** If the vault has no files in the
   30-day window, halt and surface. If the window is
   partial, note the actual coverage in the header.
7. **Read budget.** Read at most ~20 files in full during
   the synthesis. Sample from large projects.

## Hard rules

1. **Topics from content, not filenames.** A file called
   "research-brief.md" with content about "M3 eval lab"
   gets categorized under M3 eval lab, not research.
2. **Daily notes are primary cadence input.** The cadence
   section is a Mavis EA contract behavior, not an audit
   footnote. A 6-day gap at the end of the window is a
   finding.
3. **Top-5 ranking is by modification count, not size.**
   A project with 50 small files is more active than one
   with 5 large files.
4. **The report is single-file, single-session.** One
   `30-day-footprint-YYYY-MM-DD.md` per audit run. Do NOT
   append to a prior report.
5. **Synthesis happens in this session.** Per hard
   constraint #3, the EA does the synthesis work. The
   x-researcher would surface different artifacts (X
   content, not vault activity).
6. **Path corrections go in the Decision Log.** If the
   actual path differs from the convention (e.g.,
   `Mavis-EA-Design` vs `Mavis EA Design`), note the
   correction in the Decision Log. Do not silently invent.

## When the audit HALTs

Halt and escalate to Andre when:
- Vault root not found → HALT (H1)
- Target dirs missing → HALT (H2)
- Zero files in window → HALT (H3)
- Domain mismatch detected (synthesis needs cross-team
  context) → HALT (H4)
- Path correction required (operator specified wrong
  path) → note in Decision Log, proceed with actual path
- Mass file read budget exceeded (top-N has too many large
  files) → sample, don't read everything

The audit is a diagnostic, not an authorization. Andre
decides what to do with the findings.

## Verification (post-write)

After writing the report, verify:

1. `ls -la` confirms the report file exists
2. The report's `files_in_window` matches the `find | wc -l`
   output from Step 3
3. Every project in "Active project pipelines" has ≥1 file
   in the appendix
4. Every topic in "Core topics" has ≥2 file references
5. The Decision Log captures path corrections and the
   domain-mismatch decision
6. The Appendix is complete (every file in the inventory
   is listed)
7. The report is at the correct path with the date in the
   filename

## Cross-reference

- `references/audit-procedure.md` — 9-step procedure with
  bash commands
- `references/report-template.md` — full report template
  with field shapes
- `references/safety-halts.md` — 6 halts + 6 failure modes
- `tests/audit-discipline.md` — no-invented-context,
  disk-wins, Mavis-synthesizes checks
- `tests/file-inventory-verification.md` — count consistency
  + appendix completeness
- `00 Inbox/` — raw capture surface; audit cross-references
- `01 Daily/` — primary cadence input
- `03 Projects/` — primary pipeline ranking input
- `99 _system/dashboards/` — system-wide dashboards;
  reports/ is project-local convention
- Garry Tan's "audit and integration tests, repeat"
  principle — the audit is an integration test for the
  vault
- Mavis MEMORY.md — `cross-team-discipline` rule
