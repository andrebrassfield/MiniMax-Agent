# Runs

> Per-audit-run receipts. Replayable. Append-only.

## Convention

```
runs/RUN-<YYYYMMDD-HHMMSS>.md
```

Each run receipt records:
- Mode (BOOTSTRAP, AUDIT, ADJUDICATE, DAILY_BRIEF)
- Started at, ended at, duration
- Targets audited
- Verdicts issued (count + per-verdict summary)
- Findings surfaced
- Anomalies
- Handoff lanes written
- Vault health summary

## Pending

*Empty. First AUDIT will populate.*

---

**Discipline:** Run receipts are the audit log of the audit log. They are how Andre replays a Verifier decision.
