# Scripts (placeholders)

> Operational scripts. Each mode has a driver. Fill as Andre enables each mode.

## To build

| Script | Mode | Purpose |
|--------|------|---------|
| `verifier_bootstrap.py` | BOOTSTRAP | Initial vault scaffold |
| `verifier_loop.py` | AUDIT | Main audit driver — runs CROSS_CHECK → AUDIT_RUN → AUDIT_AGENT → ADJUDICATE → REPORT |
| `verifier_cross_check.py` | AUDIT (sub-step) | Capture source trail, score source quality |
| `verifier_audit_run.py` | AUDIT (sub-step) | Verify a single REFRESH/MIDDAY_FOCUS run followed stage discipline |
| `verifier_audit_agent.py` | AUDIT (sub-step) | Sample-check an agent's recent outputs against its own AGENTS.md |
| `verifier_report.py` | AUDIT (sub-step) | Verdict writer — applies rubric, appends to verdicts.jsonl |
| `verifier_adjudicate.py` | ADJUDICATE | Standalone dispute/appeal resolver |
| `verifier_daily_brief.py` | DAILY_BRIEF | Render human-facing audit digest |
| `verifier_health_check.py` | HEALTH | Structural integrity check (verdicts have trails, temperature is 0, etc.) |
| `compile_audit_to_wiki.py` | AUDIT (sub-step) | Convert audit deltas to wiki pages |
| `validate_verifier_release.py` | AUDIT (sub-step) | Release validator |
| `backup_verifier.py` | BACKUP | Snapshot vault to `runs/backup-*.tar.gz` (excludes `raw/`) |
| `restore_verifier.py` | RESTORE | Preview or apply a backup |
| `recover_verifier.py` | RECOVER | RESTORE + AUDIT (or BOOTSTRAP if no backup) |

## Order to build

1. `verifier_bootstrap.py` — needed to seed the first run.
2. `verifier_loop.py` — main loop, the heart of the system.
3. `verifier_cross_check.py` and `verifier_report.py` — the minimum viable audit pass.
4. `verifier_daily_brief.py` — gives Andre visible output.
5. `verifier_health_check.py` — gates everything else.
6. `verifier_adjudicate.py` — handles appeals without manual intervention.
7. `compile_audit_to_wiki.py` — gives the vault searchable memory.
8. `backup_verifier.py` — keeps the system survivable.
9. The rest as needed.

## Conventions

- All scripts read `config.yaml` for runtime parameters.
- All scripts write run receipts to `runs/RUN-<timestamp>.md`.
- All scripts are idempotent — re-running them does not corrupt state.
- All scripts log anomalies to `ops/` and surface them in the operator brief.
- All audit scripts verify `temperature.eval == 0.0` at start; non-zero aborts the run.
