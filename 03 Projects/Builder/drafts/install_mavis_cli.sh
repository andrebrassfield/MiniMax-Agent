#!/usr/bin/env bash
# install_mavis_cli.sh — install the Mavis Harness CLI bridge.
#
# Source: 03 Projects/Builder/drafts/mavis_cli.py (committed artifact)
# Target: ~/.mavis/bin/mavis-cli (runtime)
#         + symlink to /opt/homebrew/bin/mavis-cli (and /usr/local/bin)
#         + `alias mh="mavis-cli"` in ~/.zshrc (and ~/.bashrc if present)
#
# Idempotent: safe to re-run. Re-running detects the existing install,
# updates the file, refreshes the symlink, and skips the alias if it's
# already there.
#
# Usage:    ./install_mavis_cli.sh
# Verify:   which mavis-cli && mavis-cli --health
#           type mh   # should resolve to mavis-cli
# Uninstall: rm ~/.mavis/bin/mavis-cli
#            (and remove the symlinks + alias lines from rc files)

set -euo pipefail

readonly DRAFTS="/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Builder/drafts"
readonly SRC="${DRAFTS}/mavis_cli.py"
readonly RUNTIME_BIN="$HOME/.mavis/bin"
readonly DEST="${RUNTIME_BIN}/mavis-cli"
readonly SYMLINK_DIRS=("/opt/homebrew/bin" "/usr/local/bin")
readonly ALIAS_LINE='alias mh="mavis-cli"'
readonly ALIAS_MARKER="# mavis-cli alias (added by install_mavis_cli.sh)"

log() { printf '[install_mavis_cli] %s\n' "$*"; }

# --- preflight ---------------------------------------------------------------

[ -f "$SRC" ] || { log "FATAL: source not found at $SRC"; exit 1; }
command -v python3 >/dev/null 2>&1 || { log "FATAL: python3 not on PATH"; exit 1; }

mkdir -p "$RUNTIME_BIN"

# --- copy + chmod ------------------------------------------------------------

cp "$SRC" "$DEST"
chmod 755 "$DEST"
log "installed: $DEST"

# --- symlink to a PATH dir ---------------------------------------------------

# Try /opt/homebrew/bin first (Apple Silicon default), then /usr/local/bin
# (Intel Macs / brew on Intel). Skip if neither is writable. The symlink
# being absent is non-fatal — the user can still invoke via the full path.
for dir in "${SYMLINK_DIRS[@]}"; do
  if [ -d "$dir" ] && [ -w "$dir" ]; then
    if [ -L "$dir/mavis-cli" ] || [ -f "$dir/mavis-cli" ]; then
      rm -f "$dir/mavis-cli"
    fi
    ln -s "$DEST" "$dir/mavis-cli"
    log "symlinked: $dir/mavis-cli -> $DEST"
  fi
done

# --- add the `mh` alias ------------------------------------------------------

# Idempotent alias injection: check for the marker, then for the alias line
# (in case the user manually wrote `alias mh=...` without the marker). If
# either is present, skip. Otherwise append the marker + alias line.

add_alias() {
  local rcfile="$1"
  [ -f "$rcfile" ] || return 0
  if grep -qF "$ALIAS_MARKER" "$rcfile" 2>/dev/null; then
    log "alias already present in $rcfile (skipped)"
    return 0
  fi
  if grep -qE '^[[:space:]]*alias[[:space:]]+mh=' "$rcfile" 2>/dev/null; then
    log "alias mh already defined in $rcfile without marker (skipped to avoid clobber)"
    return 0
  fi
  printf '\n%s\n%s\n' "$ALIAS_MARKER" "$ALIAS_LINE" >> "$rcfile"
  log "appended alias to $rcfile"
}

add_alias "$HOME/.zshrc"
if [ -f "$HOME/.bashrc" ]; then
  add_alias "$HOME/.bashrc"
fi

# --- verify ------------------------------------------------------------------

log "verify:  which mavis-cli"
if command -v mavis-cli >/dev/null 2>&1; then
  log "  -> $(command -v mavis-cli)"
else
  log "  -> not on PATH; use full path: $DEST"
fi

log "verify:  mavis-cli --version (smoke: just confirm the shebang runs)"
if "$DEST" --help >/dev/null 2>&1; then
  log "  -> --help exits 0"
else
  log "  -> --help failed; check the file"
  exit 1
fi

log "DONE. Next shell will have the mh alias. Re-source with: source ~/.zshrc"
