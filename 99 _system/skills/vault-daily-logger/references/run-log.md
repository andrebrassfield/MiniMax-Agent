# Run Log — vault-daily-logger

The JSONL audit trail. Append-only. One line per cron run. Lives
at `99 _system/logs/daily-logger-runs.jsonl`.

## Schema

```jsonl
{"date": "2026-06-17", "run_at": "18:00:00 CT", "files_scanned": 23, "top_projects": ["X-Content-Engine: 7", "Mavis EA Design: 5", "Builder: 4", "Researcher: 3", "Verifier: 2"], "daily_path": "01 Daily/2026-06-17.md", "halt": null, "outcome": "generated"}
```

## Fields

| Field | Type | Description |
|---|---|---|
| `date` | string (YYYY-MM-DD) | The date the daily was for |
| `run_at` | string (HH:MM:SS TZ) | When the cron ran |
| `files_scanned` | int | Total files modified in `03 Projects/` on that date |
| `top_projects` | array of strings | Top 5 projects with counts (project: count) |
| `daily_path` | string | The file path (generated or skipped) |
| `halt` | string or null | If the run halted, the halt reason; null if generated |
| `outcome` | enum | `generated` \| `skipped-manual-entry` \| `skipped-clock-skew` \| `skipped-too-old` \| `error` |

## Outcomes

- `generated` — the daily was missing or empty, the skill generated it
- `skipped-manual-entry` — the daily had manual entries, the skill halted (per hard constraint #1)
- `skipped-clock-skew` — the date is in the future, the skill halted
- `skipped-too-old` — the date is >7 days in the past, the skill halted
- `error` — the atomic write failed or another disk error; surface to the chief

## Why the run log matters

The cron-driven skill runs unattended. The run log is the audit
trail that lets Mavis (or Andre) reconstruct what happened when a
daily is missing or stale.

Example audit queries:
- "When was the last time vault-daily-logger generated a daily?"
  → `tail -1 99 _system/logs/daily-logger-runs.jsonl`
- "Why is there no daily for 2026-06-15?" → `grep "2026-06-15" ...`
  (the entry should show `skipped-manual-entry` if the operator
  wrote one, or `error` if the cron failed)
- "How many dailies were generated vs. skipped in the last 30 days?"
  → `jq -r .outcome ... | sort | uniq -c`

## File growth pattern

The log grows linearly with each cron run (one line per day). At
365 lines/year, it's manageable. If the log becomes unwieldy
(>10K lines), consider rolling it: `daily-logger-runs-YYYY.jsonl`
per year, with the active year being the un-suffixed file.
