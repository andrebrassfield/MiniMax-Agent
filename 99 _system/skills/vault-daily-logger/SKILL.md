---
name: vault-daily-logger
description: |
  Daily cron (18:00 CT) that auto-generates a 5-bullet technical-
  footprint daily note at `01 Daily/YYYY-MM-DD.md` when the day's file
  is missing or empty. Detects manual entries (≥100 bytes of body
  content after frontmatter) and halts to preserve them. Tags the
  generated file with `tags: [auto-generated]` so the operator can
  tell the chief wrote it. Source material: `find 03 Projects/ -type
  f -mtime 0` grouped by top-level project, top 5 by modification
  count. Triggers: cron at 18:00 CT daily. Manual invocation:
  "run vault-daily-logger", "auto-generate today's daily", "daily
  note cron", "fallback daily brief", "backfill the daily note gap".
  Hard constraint: NEVER overwrite a daily that has manual entries —
  that is the load-bearing rule. Read-only against `01 Daily/` for
  the detection step; writes only to today's file.
---

# vault-daily-logger

The daily-note habit gap closer. The 2026-06-16 vault audit found
a 6-day gap where no daily notes were written, with the prior gap
having been caught by the chief ("Mavis's memory was lagging
reality, citing 3-day-old state as if current"). This skill is the
automated fallback that ensures a daily note always exists at
18:00 CT, so the chief never operates on stale context.

## Intent

- Cron at 18:00 CT daily
- Check `01 Daily/YYYY-MM-DD.md` for today's date
- If the file is missing or empty, auto-generate a 5-bullet summary of the day's actual technical footprint
- If the daily already exists with manual entries (≥100 bytes of body content after frontmatter), halt — the operator's manual work is sacred
- Append to a run log at `99 _system/logs/daily-logger-runs.jsonl`

The model decides *what* the 5 bullets say (the 1-line project
summary per project). The deterministic layer (find/awk/sort for
scanning, Python for the atomic write, the 100-byte manual
detection logic) lives in `references/`. Safety halts and edge cases
live in `tests/`.

## When to run

**Primary trigger:** cron at 18:00 CT daily. Wire to the chief's cron
schedule (`mavis cron`).

**Manual triggers:**
- "run vault-daily-logger"
- "auto-generate today's daily"
- "daily note cron"
- "fallback daily brief"
- "backfill the daily note gap"

**Do NOT run for:**
- Future dates (system clock may be off)
- Dates more than 7 days in the past (older gaps should be flagged, not silently backfilled)
- The `02 Notes/` or `00 Inbox/` directories (this skill writes only to `01 Daily/`)
- A daily that has manual entries (the load-bearing halt)

## Inputs

| Input | Default | Required |
|---|---|---|
| Date to log | today (CT) | no |
| Vault root | `/Users/brassfieldventuresllc/MiniMax-Agent` | no |
| Daily dir | `01 Daily/` | no |
| Projects dir | `03 Projects/` | no |
| Top-N bullets | 5 | no |
| Manual-detection threshold | 100 bytes of body content | no — adjust if operator's dailies are consistently shorter/longer |

## Output contract

A markdown file at `01 Daily/YYYY-MM-DD.md` (only on the
"missing-or-empty" path) with:
- Frontmatter (date, day, type, tags `[auto-generated]`, generator
  metadata)
- An `> **AUTO-GENERATED**` callout (explicit marker for future-Mavis)
- The 5-bullet technical footprint (top 5 projects by file-mod
  count, each with: project name + count + 1-line summary + key
  files)
- Optional stubs (🎯 / 📥 / ✅ / 🚧 / 🧹) for manual follow-up
- "Notes for the chief" section with the run metadata

Plus an append to the run log at
`99 _system/logs/daily-logger-runs.jsonl` (one line per run with
timestamp, files scanned, top projects).

The full file template is in `references/output-template.md`.

## Resolver

Auto-invoke when:
- 18:00 CT cron fires (the primary trigger)
- Operator says "run vault-daily-logger" / "backfill the daily note gap"

Do NOT auto-invoke for:
- Future dates (clock-skew check)
- Manual dailies present (the load-bearing halt)
- Dates >7 days old (surface the gap, don't silently backfill)

## Hard constraints (the load-bearing rule + supporting halts)

1. **NEVER overwrite a daily that has manual entries.** This is the load-bearing rule. If the file has ≥100 bytes of body content (excluding frontmatter), halt immediately. The operator's manual work is sacred.
2. **Future date → halt.** System clock may be off.
3. **Date >7 days in the past → halt.** The audit is weekly-cadence; older gaps should be flagged, not silently backfilled.
4. **Atomic write mandatory.** Use temp-write-fsync-rename to prevent partial writes on cron interruption.
5. **0 files modified today → still generate a stub daily.** "0 files modified today" is a valid daily, even if sparse.
6. **Top project with 50+ files modified → cap the bullet's key files at 3.** The bullet's summary is the load-bearing element, not the file list.

## Cross-reference

- `references/output-template.md` — the file structure + the auto-generated frontmatter
- `references/scan-protocol.md` — the find/awk/sort pipeline for `03 Projects/`
- `references/atomic-write.md` — the Python atomic write pattern
- `references/run-log.md` — the JSONL log entry shape
- `tests/safety-halts.md` — manual-daily, future-date, body-size, atomic-write failure
- `tests/manual-detection.md` — the 100-byte threshold accuracy
- `tests/edge-cases.md` — 0 files modified, single project, sparse days
- The `99 _system/templates/daily.md` template — the canonical daily-note structure this skill mirrors
- The `vault-30day-auditor` skill — the audit skill that flagged the 6-day gap this skill is fixing
- The chief's `MEMORY.md` "Daily notes cadence" — the discipline this skill operationalizes
