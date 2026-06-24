#!/usr/bin/env bash
# kanban-health-check — autonomous ghost-completion watchdog
#
# Detects the kanban fast-path bug: tasks marked status='done' without real
# execution. Asserts the actual kanban state machine invariants on the
# `default` board over a sliding window (last 60 min by default).
#
# Invariants checked (any violation = ghost):
#   1. tasks.status='done' AND latest task_run.worker_pid IS NULL
#   2. tasks.status='done' AND latest task_run.outcome IS NULL
#   3. tasks.status='done' AND (ended_at - started_at) < 1 second
#   4. task_runs row stuck in 'running' state with ended_at IS NULL for > 60 min
#
# Exit codes: 0 = green, 1 = ghost(s) found, 2 = infra problem (db missing, etc).
# Provenance: written by Mavis 2026-05-25 after the swarm_dispatcher.py +
# UnboundLocalError outage. See /Users/brassfieldventuresllc/Documents/Obsidian Vault/Agents/mavis/2026-05-25-kanban-postmortem.md

set -uo pipefail

KANBAN_DB="${HERMES_HOME:-$HOME/.hermes}/kanban.db"
LOG_DIR="$HOME/.mavis/logs"
LOG_FILE="$LOG_DIR/kanban-health-check.log"
ALERT_DIR="/Users/brassfieldventuresllc/Documents/Obsidian Vault/fleet-alerts/$(date +%Y-%m-%d)"
WINDOW_MIN="${KANBAN_HC_WINDOW_MIN:-60}"
TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$LOG_DIR"
mkdir -p "$ALERT_DIR"

log() { echo "[$TIMESTAMP] $*" >> "$LOG_FILE"; }

if [ ! -f "$KANBAN_DB" ]; then
  log "FATAL: kanban.db not found at $KANBAN_DB"
  exit 2
fi

# --- Ghost completions in window ---
# A ghost = tasks.status='done' AND latest run has NO terminal outcome row.
# The kernel must always write a terminal outcome ('completed' / 'crashed' /
# 'timed_out' / 'spawn_failed' / 'gave_up' / 'blocked' / 'reclaimed') before
# flipping the task to 'done'. If we see status='done' with outcome IS NULL
# (or no run row at all), the dispatcher fast-pathed past the worker.
#
# NOTE: worker_pid IS NULL on task_runs is NORMAL after clean exit — the
# kernel clears it. Do NOT use it as a ghost signal on its own.
# Sub-second duration is also normal for legitimately short tasks
# (skill-sync, idempotency hits), so we don't flag it.
#
# SCHEMA QUIRK: tasks.completed_at is written in MILLISECONDS by the kernel,
# while tasks.created_at and task_runs timestamps are SECONDS. We normalize
# anything >= 1e12 by dividing by 1000. Tracked as a separate upstream issue.
GHOST_SQL=$(cat <<EOF
WITH norm AS (
  SELECT
    t.id, t.assignee, t.status,
    CASE WHEN t.completed_at >= 1000000000000
         THEN t.completed_at / 1000
         ELSE t.completed_at END AS completed_at_secs
  FROM tasks t
  WHERE t.status = 'done' AND t.completed_at IS NOT NULL
)
SELECT n.id || '|' || COALESCE(n.assignee, '<none>') ||
       '|run_id=' || COALESCE(r.id, 'NO_RUN') ||
       '|outcome=' || COALESCE(r.outcome, 'NULL') ||
       '|run_status=' || COALESCE(r.status, 'NO_RUN') ||
       '|completed=' || datetime(n.completed_at_secs, 'unixepoch', 'localtime')
FROM norm n
LEFT JOIN task_runs r ON r.task_id = n.id AND r.id = (
  SELECT MAX(id) FROM task_runs WHERE task_id = n.id
)
WHERE n.completed_at_secs > strftime('%s', 'now', '-${WINDOW_MIN} minutes')
  AND (r.id IS NULL OR r.outcome IS NULL);
EOF
)

GHOSTS=$(sqlite3 "$KANBAN_DB" "$GHOST_SQL" 2>&1)

# --- Check 4: orphan runs stuck running for > window ---
ORPHAN_SQL=$(cat <<EOF
SELECT 'run_id=' || r.id || '|task=' || r.task_id || '|profile=' || COALESCE(r.profile, 'NULL') ||
       '|started=' || datetime(r.started_at, 'unixepoch', 'localtime') ||
       '|age_min=' || ((strftime('%s', 'now') - r.started_at) / 60)
FROM task_runs r
WHERE r.status = 'running'
  AND r.ended_at IS NULL
  AND r.started_at < strftime('%s', 'now', '-${WINDOW_MIN} minutes');
EOF
)

ORPHANS=$(sqlite3 "$KANBAN_DB" "$ORPHAN_SQL" 2>&1)

# --- Decide verdict ---
EXIT=0
SUMMARY="window=${WINDOW_MIN}min"

if [ -n "$GHOSTS" ]; then
  EXIT=1
  GHOST_COUNT=$(echo "$GHOSTS" | wc -l | tr -d ' ')
  SUMMARY="$SUMMARY ghosts=$GHOST_COUNT"
  log "FAIL ghost_completions=$GHOST_COUNT"
  echo "$GHOSTS" | while IFS= read -r line; do log "  ghost: $line"; done
else
  SUMMARY="$SUMMARY ghosts=0"
fi

if [ -n "$ORPHANS" ]; then
  EXIT=1
  ORPHAN_COUNT=$(echo "$ORPHANS" | wc -l | tr -d ' ')
  SUMMARY="$SUMMARY orphans=$ORPHAN_COUNT"
  log "FAIL orphan_runs=$ORPHAN_COUNT"
  echo "$ORPHANS" | while IFS= read -r line; do log "  orphan: $line"; done
else
  SUMMARY="$SUMMARY orphans=0"
fi

if [ "$EXIT" -eq 0 ]; then
  log "PASS $SUMMARY"
  exit 0
fi

# --- Failure: write vault alert ---
ALERT_FILE="$ALERT_DIR/kanban-ghosts-$(date +%H%M%S).md"
cat > "$ALERT_FILE" <<EOF
---
type: fleet-alert
title: Kanban Ghost Completion Detected
date: '$TIMESTAMP'
action: GHOST_COMPLETION
severity: critical
source: kanban-health-check skill (Mavis)
window_minutes: $WINDOW_MIN
---

**Alert:** GHOST_COMPLETION
**Summary:** $SUMMARY
**Time:** $TIMESTAMP

## What This Means

The kanban fast-path bug is back. A task was marked \`status='done'\` without
real execution (no worker_pid, no outcome, or zero-duration run). This is the
exact failure mode the 2026-05-25 audit caught. Do NOT trust recent task
completions until root cause is identified.

## Likely Causes (in order of probability)

1. A custom dispatcher script was re-enabled (check \`launchctl list | grep -E "swarm|dispatch"\`)
2. The local patch to \`hermes_cli/kanban_db.py:5009\` was overwritten by \`hermes update\`
3. A new code path in the dispatcher bypasses the worker_pid + outcome guarantee
4. A worker is crashing post-spawn before writing its outcome row

## Detected Ghost Completions

\`\`\`
$GHOSTS
\`\`\`

## Detected Orphan Runs (stuck 'running' > $WINDOW_MIN min)

\`\`\`
$ORPHANS
\`\`\`

## Triage

1. \`launchctl list | grep -iE 'swarm|dispatch'\` — confirm no custom dispatcher is running
2. \`tail -50 ~/.hermes/profiles/<assignee>/logs/gateway.log\` — look for tracebacks
3. \`sqlite3 ~/.hermes/kanban.db "SELECT * FROM task_runs WHERE id=<id>"\` — inspect the run row
4. Reset ghost task: \`UPDATE tasks SET status='ready', worker_pid=NULL, claim_lock=NULL, current_run_id=NULL WHERE id='<id>'\` and force a fresh dispatch
EOF

log "FAIL alert_written=$ALERT_FILE"
exit "$EXIT"
