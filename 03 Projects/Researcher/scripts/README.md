# Scripts (placeholders)

> Operational scripts. Each mode has a driver. Fill as Andre enables each mode.

## To build

| Script | Mode | Purpose |
|--------|------|---------|
| `research_agent_loop.py` | REFRESH | Main refresh driver — collects, scores, writes, updates |
| `research_agent_bootstrap.py` | BOOTSTRAP | Initial vault scaffold |
| `research_agent_daily_summary.py` | DAILY_SUMMARY | Render human-facing digest |
| `research_agent_midday_focus.py` | MIDDAY_FOCUS | Rebuild operator cockpit from existing artifacts |
| `backup_research_agent.py` | BACKUP | Snapshot vault to `runs/backup-*.tar.gz` (excludes `raw/`) |
| `restore_research_agent.py` | RESTORE | Preview or apply a backup |
| `recover_research_agent.py` | RECOVER | RESTORE + REFRESH (or BOOTSTRAP if no backup) |
| `compile_refresh_to_wiki.py` | REFRESH (sub-step) | Convert dossier deltas to wiki pages |
| `evaluate_research_agent_run.py` | REFRESH (sub-step) | Dry-run evaluator of a refresh |
| `validate_research_agent_release.py` | REFRESH (sub-step) | Release validator |
| `validate_research_agent_regressions.py` | REFRESH (sub-step) | Regression validator |
| `print_research_digest.py` | delivery | Digest printer (DAILY_SUMMARY, MIDDAY_FOCUS) |
| `research_agent_health_check.py` | HEALTH | Structural integrity check |

## Order to build

1. `research_agent_bootstrap.py` — needed to seed the first run.
2. `research_agent_loop.py` — main loop, the heart of the system.
3. `research_agent_daily_summary.py` — gives Andre visible output.
4. `research_agent_health_check.py` — gates everything else.
5. `compile_refresh_to_wiki.py` — gives the vault searchable memory.
6. `backup_research_agent.py` — keeps the system survivable.
7. The rest as needed.

## Conventions

- All scripts read `config.yaml` for runtime parameters.
- All scripts write run receipts to `runs/RUN-<timestamp>.md`.
- All scripts are idempotent — re-running them does not corrupt state.
- All scripts log anomalies to `ops/` and surface them in the operator brief.
