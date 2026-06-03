# Operator Action Ledger

> Follow-through surface. Rebuilt by MIDDAY_FOCUS. Tracks what Mavis and Hermes actually consumed from handoff queues, and what is still sitting there.

*Last built: 2026-06-02 21:50 CT (manual REFRESH; not a MIDDAY_FOCUS rebuild). Will be rebuilt by next MIDDAY_FOCUS run.*

## Current lane status

| Lane | Pending | Oldest pending | Status |
|------|---------|----------------|--------|
| mavis | 1 | 2026-06-02 21:50 CT | healthy (pending < 3, oldest < 12h) |
| hermes | 2 | 2026-06-02 21:50 CT | healthy (pending < 3, oldest < 12h) |
| build | 0 | — | healthy |
| content | 0 | — | healthy |
| watch | 4 | 2026-06-02 21:50 CT | healthy (well under 20 cap) |
| verify | 0 | — | healthy (separate from verification-review, which has 1 item) |

## Format

```yaml
- lane: mavis | hermes | build | content | watch | verify
  consumed_last_24h: N
  consumed_last_7d: N
  pending_now: N
  oldest_pending: YYYY-MM-DD
  stale_threshold_hours: 24
  status: healthy | aging | stale
```

## Status rules

- `healthy` — pending < 3, oldest < 12h
- `aging` — pending ≥ 3 or oldest ≥ 12h
- `stale` — pending ≥ 6 or oldest ≥ 24h

## Action

When any lane is `stale`, the Researcher surfaces it in the operator brief and asks Mavis to confirm consumption. If Mavis confirms the items are intentionally queued, the action moves to `decisions/`.

---

*This file is a feedback loop. If handoffs are written but never read, the system is broken. The action ledger is what catches it.*
