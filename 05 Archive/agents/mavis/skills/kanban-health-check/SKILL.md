---
name: kanban-health-check
description: >
  Autonomous watchdog for the kanban fast-path bug. Asserts kanban state
  machine invariants on the `default` board over a sliding window. Writes a
  vault fleet-alert on violation. Runs as launchd cron every 30 min.

  Triggers: "run kanban health", "kanban eval", "check fleet health",
  "dispatcher health", "task false positive", "fast-path bug",
  "ghost completion", "kanban watchdog".

  Implements Garry Tan's principle: evals and integration tests, repeat.
  Disease coverage: Anosognosia (wrong and unaware) + Disinhibition.
triggers:
  - run kanban health
  - kanban eval
  - check fleet health
  - dispatcher health
  - task false positive
  - fast-path bug
  - ghost completion
  - kanban watchdog
  - kanban health check
---

# Kanban Health Check — Ghost Completion Watchdog

Detects the kanban fast-path bug that silently marks tasks `done` without real
execution. Built after the 2026-05-25 outage where `swarm_dispatcher.py`
overrode explicit assignees and the native `kanban_db.py:5089` raised
`UnboundLocalError` on every tick.

## Invariants Asserted (in window, default 60 min)

A task is a **ghost** if `tasks.status='done'` AND its latest `task_run`
has `outcome IS NULL` (or there is no run row at all). The kanban kernel
must always write a terminal outcome — `completed` / `crashed` / `timed_out`
/ `spawn_failed` / `gave_up` / `blocked` / `reclaimed` — before flipping the
task to `done`. If `status='done'` exists without that outcome, the
dispatcher fast-pathed past the worker.

A run is an **orphan** if `task_runs.status='running'` AND `ended_at IS NULL`
AND `started_at > window_min ago` — claim was made but no worker ever
reported back.

Either condition = FAIL.

### Why NOT to use these as ghost signals

- **`worker_pid IS NULL`** on `task_runs` is NORMAL after clean exit — the
  kernel clears it. Using it as a ghost signal produces false positives on
  every successful run.
- **Sub-second duration** is legitimate for skill-sync ticks, idempotency
  hits, and other trivially-short tasks. Don't flag.

### Schema quirk

`tasks.completed_at` is written in **milliseconds** by the kernel while
`tasks.created_at` and all `task_runs` timestamps are **seconds**. The
script normalizes anything `>= 1e12` by dividing by 1000. This inconsistency
is tracked as a separate upstream issue — fix the kernel writer, not
downstream consumers.

## Run Manually

```bash
~/.mavis/skills/kanban-health-check/scripts/check.sh
```

Exit codes: `0` = green, `1` = ghost(s)/orphan(s) found, `2` = infra problem.

## Cron Cadence

Wired via `~/Library/LaunchAgents/ai.mavis.kanban-health-check.plist`,
`StartInterval=1800` (30 min). Logs to `~/.mavis/logs/kanban-health-check.log`.

## What Happens On FAIL

1. Writes a structured fleet-alert to
   `~/Documents/Obsidian Vault/fleet-alerts/<YYYY-MM-DD>/kanban-ghosts-<HHMMSS>.md`
   with the offending rows + triage steps.
2. Exits non-zero (launchd will record in `.err` log).
3. Does **not** auto-remediate. A ghost completion implies a regression we
   need to diagnose by hand, not paper over.

## Tunables

| Env var | Default | Meaning |
|---|---|---|
| `KANBAN_HC_WINDOW_MIN` | `60` | Sliding window for completed-task and orphan-run inspection |
| `HERMES_HOME` | `~/.hermes` | Kanban DB location |

## Triage Playbook (when an alert fires)

1. `launchctl list \| grep -iE 'swarm\|dispatch'` — make sure no custom
   dispatcher script has been re-enabled
2. `tail -50 ~/.hermes/profiles/<assignee>/logs/gateway.log` — look for the
   actual exception
3. `sqlite3 ~/.hermes/kanban.db "SELECT * FROM task_runs WHERE id=<id>"` —
   inspect the orphan/ghost row
4. Reset the task: `UPDATE tasks SET status='ready', worker_pid=NULL,
   claim_lock=NULL, current_run_id=NULL WHERE id='<id>'`

## Provenance

- 2026-05-25 08:00 — Original skill drafted (claim-TTL hypothesis)
- 2026-05-25 08:31 — Rewritten by Mavis after the audit proved the disease
  was routing override + UnboundLocalError, not TTL exhaustion. SQL
  assertion now mirrors the actual state-machine invariants.
- 2026-05-25 08:33 — First armed run flagged the freshly-passed probe as a
  false positive. Removed `worker_pid IS NULL` and `duration < 1s` clauses
  (both produce noise on healthy runs). Discovered `completed_at` is in ms
  while every other timestamp is in seconds; added unit-normalization in
  SQL. PASS confirmed at 08:34.
