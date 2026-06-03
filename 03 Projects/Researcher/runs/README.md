# Runs

> Each refresh leaves a receipt here. If you cannot replay a run, you cannot trust its output later.

## Format

```markdown
# RUN-YYYYMMDD-HHMM

- mode: <BOOTSTRAP | REFRESH | DAILY_SUMMARY | ...>
- started_at: YYYY-MM-DD HH:MM CT
- finished_at: null              # REQUIRED: write null at receipt creation. Fill on the LAST actual write to disk during the run. Never estimate.
- duration_min: <number>          # Optional. Filled at the end.
- collector_lanes_active: [...]
- collector_lanes_degraded: [...]
- findings_appended: <N>
- sources_appended: <N>
- claims_appended: <N>
- claims_updated: <N>
- dossiers_updated: [ai_agents, frontier_ai, ...]
- handoffs_written: {mavis: N, hermes: N, build: N, content: N, watch: N, verify: N}
- verification_queue_size_after: <N>
- source_balance_social_pct: <N>
- vault_health: PASS | DEGRADED | FAIL
- notes: "<any anomalies>"
```

## Discipline

- **`finished_at: null` is the starting state.** Fill on the last actual write to disk during the run — not when you finish reasoning, not when you finish the brief, but the last file mtime you actually touched.
- **The integrity check is the gate, not the verifier.** See `health/latest-health-check.md` for the cross-check that rejects receipts where `finished_at` is after any source file's mtime in the run.
- **Don't backfill.** If a receipt was written with a wrong `finished_at`, the fix is a new receipt entry (or `decisions/`) that explains the correction, not a silent edit.

## Receipts

*Empty. Append on each run.*
