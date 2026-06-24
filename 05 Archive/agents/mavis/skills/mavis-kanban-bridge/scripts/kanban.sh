#!/usr/bin/env bash
# kanban.sh — thin wrapper around kanban.py for the mavis-kanban-bridge skill.
# All actual logic lives in scripts/kanban.py.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/kanban.py" "$@"
