#!/usr/bin/env bash
# deploy_mavis.sh — Stage the Mavis Harness as a persistent background daemon.
#
# Source: 03 Projects/Mavis/phase_next_architecture.md §4.0
#         (Local-Compute Pivot, 2026-06-07 14:18 CT)
# Sprint: 5 (deployment bridge)
# Author: Mavis (chief-of-staff)
#
# What this script does (in order):
#   1. Preflight: verify Ollama is reachable on localhost:11434.
#      Without Ollama, the dispatch lane's Local-Compute Pivot
#      cannot fire; we abort with a clear error rather than deploy
#      a daemon that will silently degrade.
#   2. Stage the harness: copy the six Sprint 1-5 Python modules to
#      ~/.mavis/bin/. The harness imports the four primitives
#      relatively — they must all live in the same directory.
#   3. Stage the plist: copy com.mavis.harness.plist to
#      ~/Library/LaunchAgents/. launchd reads plists from this
#      directory at user login and at explicit bootstrap.
#   4. (Re)load the launchd job: bootout any existing instance
#      (silent if none), then bootstrap the new plist. The harness
#      starts as a persistent background process.
#   5. Smoke-check: confirm the harness is in launchd's job list
#      and that the log file is being written.
#
# What this script does NOT do:
#   - It does NOT start Ollama (you do that with `ollama serve`).
#   - It does NOT pull the models (you do that with `ollama pull`).
#   - It does NOT migrate the chief-of-staff session or change
#     any user-level state beyond ~/.mavis/bin/ and the LaunchAgent.
#
# Idempotency: re-running the script is safe. It overwrites the
# destination files with `cp -f`, and uses bootout+bootstrap to
# reload the launchd job. The harness itself, if already running,
# is replaced with the new copy.
#
# Reversibility: `deploy_mavis.sh --uninstall` removes the
# launchd job, plist, and installed files. See the bottom of the
# script for the uninstall path.
#
# Usage:
#   ./deploy_mavis.sh                  # full deploy
#   ./deploy_mavis.sh --preflight      # just check Ollama, no changes
#   ./deploy_mavis.sh --uninstall      # tear down the deployment

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Source location: the Builder drafts dir. Override with MAVIS_SRC if you
# have a different copy of the harness (e.g. a CI build).
MAVIS_SRC="${MAVIS_SRC:-/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Builder/drafts}"

# Destination locations.
MAVIS_BIN="${HOME}/.mavis/bin"
LAUNCH_AGENTS_DIR="${HOME}/Library/LaunchAgents"
PLIST_NAME="com.mavis.harness.plist"
PLIST_DEST="${LAUNCH_AGENTS_DIR}/${PLIST_NAME}"
PLIST_LABEL="com.mavis.harness"

# Workspace (for the log dir referenced by the plist).
WORKSPACE_DIR="/Users/brassfieldventuresllc/MiniMax-Agent"
LOG_DIR="${WORKSPACE_DIR}/99 _system/logs"
LOG_OUT="${LOG_DIR}/harness.log"
LOG_ERR="${LOG_DIR}/harness.err"

# Ollama endpoint (must match DEFAULT_OLLAMA_BASE_URL in mavis_harness_main.py).
OLLAMA_URL="http://localhost:11434"
OLLAMA_TAGS_ENDPOINT="${OLLAMA_URL}/api/tags"

# Required models for the Local-Compute Pivot. Names match the
# DEFAULT_OLLAMA_CHAT_MODEL and DEFAULT_OLLAMA_FAST_MODEL constants
# in mavis_harness_main.py. The script warns if these are missing;
# the harness will degrade gracefully but slowly (model loads on
# first use).
REQUIRED_CHAT_MODEL="gemma4:12b-it-qat"
REQUIRED_FAST_MODEL="gemma4:e4b-it-qat"

# The seven files the harness needs to function. Order doesn't matter;
# they're a flat directory of siblings. mavis_harness_daemon.py is
# the HTTP server that the launchd job runs (--daemon mode).
HARNESS_FILES=(
    "mavis_harness_main.py"
    "mavis_harness_daemon.py"
    "command_router.py"
    "context_loader.py"
    "filesystem_bridge.py"
    "token_multiplier_config.py"
    "scaffolding_review_cron.py"
)

# Test files are optional in production but kept in the staging dir
# so the scaffolding_review cron can invoke the golden-test suite.
TEST_FILES=(
    "test_mavis_harness_main.py"
    "test_scaffolding_review_cron.py"
    "test_command_router.py"
    "test_token_multiplier_config.py"
    "test_filesystem_bridge.py"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log()  { printf "[deploy] %s\n" "$*"; }
warn() { printf "[deploy] WARN: %s\n" "$*" >&2; }
die()  { printf "[deploy] ERROR: %s\n" "$*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Preflight: Ollama reachable? Models pulled?
# ---------------------------------------------------------------------------

preflight() {
    log "Preflight: checking Ollama on ${OLLAMA_URL} ..."

    # Try a simple HEAD against /api/tags. `curl --max-time` bounds
    # the wait so we don't hang on a dead port. We don't need the
    # response body for the reachability check.
    if ! curl --silent --show-error --max-time 5 --output /dev/null \
         "${OLLAMA_TAGS_ENDPOINT}"; then
        die "Ollama is NOT reachable at ${OLLAMA_URL}.

To fix:
    1. Start Ollama:  open the Ollama app, or run 'ollama serve' in another terminal.
    2. Verify:        curl ${OLLAMA_TAGS_ENDPOINT}    # should return a JSON list.
    3. Re-run:        $0

The harness will NOT start without Ollama. The dispatch lane's
Local-Compute Pivot depends on local inference; without it, every
dispatch falls back to the API path and the cost discipline breaks."
    fi
    log "  Ollama is reachable."

    # Soft check: are the required models pulled? We use Ollama's
    # /api/tags response and grep for the model names. Missing models
    # are a WARNING, not a fatal error — the harness will still
    # start, but the first dispatch to a missing model will fail and
    # the worker will fall back to the API path.
    local tags_json
    if tags_json=$(curl --silent --max-time 5 "${OLLAMA_TAGS_ENDPOINT}"); then
        if ! echo "${tags_json}" | grep -q "${REQUIRED_CHAT_MODEL}"; then
            warn "Required model not pulled: ${REQUIRED_CHAT_MODEL}"
            warn "  Run: ollama pull ${REQUIRED_CHAT_MODEL}"
        else
            log "  Found model: ${REQUIRED_CHAT_MODEL}"
        fi
        if ! echo "${tags_json}" | grep -q "${REQUIRED_FAST_MODEL}"; then
            warn "Required model not pulled: ${REQUIRED_FAST_MODEL}"
            warn "  Run: ollama pull ${REQUIRED_FAST_MODEL}"
        else
            log "  Found model: ${REQUIRED_FAST_MODEL}"
        fi
    else
        warn "Could not read /api/tags response; skipping model-presence check."
    fi
}

# ---------------------------------------------------------------------------
# Stage files
# ---------------------------------------------------------------------------

stage_files() {
    log "Staging harness files to ${MAVIS_BIN}/ ..."

    # Verify all source files exist before doing any copies. A
    # partial copy is worse than no copy (the harness would fail
    # at import time with a confusing ModuleNotFoundError).
    for f in "${HARNESS_FILES[@]}" "${TEST_FILES[@]}"; do
        if [[ ! -f "${MAVIS_SRC}/${f}" ]]; then
            die "Source file missing: ${MAVIS_SRC}/${f}"
        fi
    done

    # Create the bin dir if needed. -p means "no error if exists".
    mkdir -p "${MAVIS_BIN}"

    # Copy the harness files. -f overwrites; -p preserves mtime
    # (the atomic_write pattern depends on file mtimes for
    # conflict detection, and the test suite uses mtime assertions
    # in a few places).
    for f in "${HARNESS_FILES[@]}"; do
        cp -fp "${MAVIS_SRC}/${f}" "${MAVIS_BIN}/${f}"
    done
    log "  Copied ${#HARNESS_FILES[@]} harness files."

    # Test files. Useful for `python3 -m unittest` from the cron,
    # and for manual regression checks. Same dest so they're all
    # importable as a unit.
    for f in "${TEST_FILES[@]}"; do
        cp -fp "${MAVIS_SRC}/${f}" "${MAVIS_BIN}/${f}"
    done
    log "  Copied ${#TEST_FILES[@]} test files."

    # Ensure the log dir exists. The plist's StandardOutPath will
    # fail silently if the dir doesn't exist at launchd load time.
    mkdir -p "${LOG_DIR}"
    log "  Ensured log dir: ${LOG_DIR}/"

    # Stage the plist.
    log "Staging plist to ${PLIST_DEST} ..."
    mkdir -p "${LAUNCH_AGENTS_DIR}"
    cp -fp "${MAVIS_SRC}/${PLIST_NAME}" "${PLIST_DEST}"
    log "  Plist staged."
}

# ---------------------------------------------------------------------------
# (Re)load the launchd job
# ---------------------------------------------------------------------------

load_launchd() {
    log "Loading launchd job (label: ${PLIST_LABEL}) ..."

    # On modern macOS (10.11+), the right way to load a user-level
    # LaunchAgent is `launchctl bootstrap gui/$UID <path>`. The
    # `gui/$UID` domain is the user's Aqua session — same as
    # `~/Library/LaunchAgents/`.

    # First, if a previous instance is loaded, boot it out. The
    # `|| true` makes this a no-op if nothing is loaded (the script
    # stays idempotent).
    launchctl bootout "gui/${UID}/${PLIST_LABEL}" 2>/dev/null || true

    # Bootstrap the new plist.
    if ! launchctl bootstrap "gui/${UID}" "${PLIST_DEST}"; then
        die "launchctl bootstrap failed for ${PLIST_DEST}.
Check the plist syntax with:  plutil -lint ${PLIST_DEST}
And the system log with:       log show --predicate 'process == \"launchd\"' --last 1m"
    fi
    log "  launchd job bootstrapped."
}

# ---------------------------------------------------------------------------
# Post-load smoke check
# ---------------------------------------------------------------------------

smoke_check() {
    log "Post-load smoke check ..."

    # Give launchd a moment to start the process.
    sleep 1

    # Confirm the label is in launchd's job list.
    if launchctl list | grep -q "${PLIST_LABEL}"; then
        log "  ${PLIST_LABEL} is in launchctl's job list."
    else
        warn "${PLIST_LABEL} is NOT in launchctl's job list."
        warn "Check the plist with: launchctl print gui/${UID}/${PLIST_LABEL}"
    fi

    # Confirm the log file is being written (or will be, on first
    # event). The harness writes to it via Python's print(), so
    # it's empty until the first handle_turn call.
    if [[ -f "${LOG_OUT}" ]]; then
        log "  Log file exists: ${LOG_OUT}"
    else
        log "  Log file will be created on first event: ${LOG_OUT}"
    fi
}

# ---------------------------------------------------------------------------
# Uninstall path
# ---------------------------------------------------------------------------

uninstall() {
    log "Uninstalling ${PLIST_LABEL} ..."

    # Boot out the launchd job (silent if not loaded).
    launchctl bootout "gui/${UID}/${PLIST_LABEL}" 2>/dev/null || true
    log "  launchd job booted out."

    # Remove the plist.
    if [[ -f "${PLIST_DEST}" ]]; then
        rm -f "${PLIST_DEST}"
        log "  Plist removed: ${PLIST_DEST}"
    fi

    # Don't remove ~/.mavis/bin/ — the user may have other Mavis
    # artifacts there. Just log what's left.
    if [[ -d "${MAVIS_BIN}" ]]; then
        log "  Staged files left in place at ${MAVIS_BIN}/"
        log "  (remove manually if you want a full teardown)"
    fi

    log "Uninstall complete."
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
    # Argument parsing: just enough for the three documented modes.
    case "${1:-}" in
        --preflight)
            preflight
            ;;
        --uninstall)
            uninstall
            ;;
        --help|-h)
            sed -n '2,40p' "$0"  # print the header doc
            ;;
        "")
            # Full deploy: preflight → stage → load → smoke.
            log "Mavis Harness deployment starting ..."
            log "  source: ${MAVIS_SRC}"
            log "  dest:   ${MAVIS_BIN}/ + ${PLIST_DEST}"
            log ""

            preflight
            echo ""
            stage_files
            echo ""
            load_launchd
            echo ""
            smoke_check
            echo ""

            log "Deploy complete."
            log ""
            log "Next steps:"
            log "  - Tail the log:    tail -f '${LOG_OUT}'"
            log "  - Status:          launchctl list | grep ${PLIST_LABEL}"
            log "  - Stop:            launchctl bootout gui/\${UID}/${PLIST_LABEL}"
            log "  - Uninstall:       $0 --uninstall"
            ;;
        *)
            die "Unknown argument: $1. Try --help."
            ;;
    esac
}

main "$@"
