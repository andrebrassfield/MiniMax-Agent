#!/usr/bin/env bash
# deploy_cron.sh — register the Mavis scaffolding-review LaunchAgent with macOS.
#
# Source: 03 Projects/Builder/drafts/com.mavis.cron.plist (committed artifact)
# Target: ~/Library/LaunchAgents/com.mavis.cron.plist (runtime registration)
# Idempotent: safe to re-run. Re-running unloads the old version, copies the
# new one, and reloads it. A 2xx `launchctl print` confirms registration.
#
# Usage:  ./deploy_cron.sh
# Verify: launchctl print gui/$UID/com.mavis.cron

set -euo pipefail

readonly DRAFTS="/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Builder/drafts"
readonly SRC="${DRAFTS}/com.mavis.cron.plist"
readonly DEST_DIR="$HOME/Library/LaunchAgents"
readonly DEST="${DEST_DIR}/com.mavis.cron.plist"
readonly LABEL="com.mavis.cron"
readonly LOG_DIR="/Users/brassfieldventuresllc/MiniMax-Agent/99 _system/logs"
readonly RUNTIME_BIN="$HOME/.mavis/bin"
readonly RUNNER_SRC="${DRAFTS}/scaffolding_review_cron_runner.py"
readonly RUNNER_DST="${RUNTIME_BIN}/scaffolding_review_cron_runner.py"

log() { printf '[deploy_cron] %s\n' "$*"; }

# --- preflight ---------------------------------------------------------------

[ -f "$SRC" ] || { log "FATAL: source plist not found at $SRC"; exit 1; }
[ -f "$RUNNER_SRC" ] || { log "FATAL: source runner not found at $RUNNER_SRC"; exit 1; }
command -v launchctl >/dev/null 2>&1 || { log "FATAL: launchctl not on PATH"; exit 1; }

# Ensure log dir exists (the harness plist uses the same logs/ dir; mirror it).
mkdir -p "$LOG_DIR" "$RUNTIME_BIN"

# --- unload (if previously loaded) -------------------------------------------

UID_NUM="$(id -u)"
DOMAIN="gui/${UID_NUM}"

if launchctl print "${DOMAIN}/${LABEL}" >/dev/null 2>&1; then
  log "unloading previous registration of ${LABEL}"
  launchctl bootout "${DOMAIN}/${LABEL}" 2>/dev/null || true
fi

# --- copy runner to runtime --------------------------------------------------

cp "$RUNNER_SRC" "$RUNNER_DST"
chmod 755 "$RUNNER_DST"
log "runner copied: $RUNNER_DST"

# --- copy + plistlint --------------------------------------------------------

mkdir -p "$DEST_DIR"
cp "$SRC" "$DEST"
chmod 644 "$DEST"

if ! plutil -lint "$DEST" >/dev/null 2>&1; then
  log "FATAL: plutil -lint rejected the plist:"
  plutil -lint "$DEST" || true
  exit 1
fi
log "plist copied and lints clean: $DEST"

# --- load --------------------------------------------------------------------

# `launchctl bootstrap` is the modern (macOS Big Sur+) replacement for
# `launchctl load -w`. Both register the agent; bootstrap does not require
# the `-w` flag because StartCalendarInterval jobs are inherently
# "wait for the schedule".
log "loading ${LABEL} into ${DOMAIN}"
launchctl bootstrap "${DOMAIN}" "$DEST"

# --- verify ------------------------------------------------------------------

if launchctl print "${DOMAIN}/${LABEL}" >/dev/null 2>&1; then
  log "OK: ${LABEL} is registered with launchd"
  log "verify with: launchctl print ${DOMAIN}/${LABEL}"
  log "next run:    launchctl start ${DOMAIN}/${LABEL}  (manual trigger for smoke test)"
  log "unload:      launchctl bootout ${DOMAIN}/${LABEL}"
else
  log "FATAL: ${LABEL} did not register. See: log show --predicate 'subsystem == \"com.apple.launchd\"' --last 1m"
  exit 1
fi
