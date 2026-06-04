#!/usr/bin/env bash
# start.sh — The Obsidian Glass Server launcher.
#
# Esalen posture: thin, local, deterministic. No auth, no DB, no caching,
# no production hardening. Local viewing room, not a production server.
#
# Behavior:
#   1. Resolve the vault root to this script's parent-of-parent-of-parent.
#   2. Check for the local venv at <script_dir>/.venv. If missing, create
#      it and install requirements (markdown + Pygments for the renderer).
#   3. Launch the server on the requested port (default 8765).
#
# Usage:
#   ./start.sh                # default port 8765
#   ./start.sh --port 8766    # alternate port
#   PORT=9000 ./start.sh      # via env
#
# Requirements file (optional):
#   99 _system/mcps/glass-server/requirements.txt
#   One package per line. Currently: markdown, Pygments.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
PORT="${PORT:-8765}"

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --port) PORT="$2"; shift 2 ;;
        --help|-h)
            sed -n '2,20p' "$0"
            exit 0
            ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

# Ensure the venv exists; create + install if missing
if [[ ! -x "$VENV_DIR/bin/python3" ]]; then
    echo "[start.sh] venv missing at $VENV_DIR; bootstrapping..." >&2
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip >/dev/null
    if [[ -f "$REQUIREMENTS_FILE" ]]; then
        echo "[start.sh] installing requirements from $REQUIREMENTS_FILE" >&2
        "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS_FILE"
    else
        echo "[start.sh] no requirements.txt; installing markdown + Pygments" >&2
        "$VENV_DIR/bin/pip" install markdown Pygments
    fi
fi

# Ensure deps are present (idempotent check; cheap)
"$VENV_DIR/bin/python3" -c "import markdown, pygments" 2>/dev/null || {
    echo "[start.sh] deps missing in venv; reinstalling..." >&2
    "$VENV_DIR/bin/pip" install markdown Pygments
}

# Launch the server with PYTHONPATH so the renderer/wikilinks modules resolve
cd "$VAULT_ROOT"
exec env PYTHONPATH="$SCRIPT_DIR" "$VENV_DIR/bin/python3" \
    "$SCRIPT_DIR/glass_server.py" --port "$PORT"
