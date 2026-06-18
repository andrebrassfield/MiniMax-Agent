#!/usr/bin/env bash
# mirror-sync.sh — atomic home + vault mirror write with cmp-based byte-identity gate.
# Implements the ea-skill-evolution sync gate (hard constraint #6).
#
# Usage: mirror-sync.sh <skill-name> [content-via-stdin]
#   - If content is piped via stdin, the script writes the piped content to both paths.
#   - If no content is piped, the script reads from the canonical home and copies it to the vault mirror.
#   - The vault mirror write is the precondition for status=shipped. If cmp fails, the script exits non-zero
#     and the caller MUST mark the proposal `status: mirror-pending`, not `shipped`.
#
# Exit codes:
#   0 = mirror is byte-identical to home (gate passed)
#   1 = missing arguments or missing source file
#   2 = mirror write failed (filesystem / permissions)
#   3 = cmp failed — home and mirror are not byte-identical (gate held)

set -euo pipefail

SKILL_NAME="${1:-}"
if [ -z "$SKILL_NAME" ]; then
  echo "usage: $0 <skill-name> [content-via-stdin]" >&2
  exit 1
fi

HOME_PATH="$HOME/.mavis/agents/mavis/skills/${SKILL_NAME}/SKILL.md"
VAULT_PATH="$HOME/MiniMax-Agent/99 _system/skills/${SKILL_NAME}/SKILL.md"
VAULT_DIR="$(dirname "$VAULT_PATH")"

mkdir -p "$VAULT_DIR"

if [ -p /dev/stdin ]; then
  # Content piped via stdin — write to both paths atomically.
  TMP_HOME="$(mktemp -t mirror-sync-home-XXXXXX)"
  TMP_VAULT="$(mktemp -t mirror-sync-vault-XXXXXX)"
  cat > "$TMP_HOME"
  cp "$TMP_HOME" "$TMP_VAULT"
  sync "$TMP_HOME" "$TMP_VAULT"
  mv -f "$TMP_HOME" "$HOME_PATH" || { rm -f "$TMP_HOME" "$TMP_VAULT"; exit 2; }
  mv -f "$TMP_VAULT" "$VAULT_PATH" || { rm -f "$TMP_VAULT"; exit 2; }
elif [ -f "$HOME_PATH" ]; then
  # No stdin — copy the existing home to the vault mirror.
  cp -f "$HOME_PATH" "$VAULT_PATH" || exit 2
else
  echo "mirror-sync: no source content (stdin empty and home missing at $HOME_PATH)" >&2
  exit 1
fi

# Gate check: byte-identity via cmp. Exit code 0 = pass; non-zero = gate held.
if cmp -s "$HOME_PATH" "$VAULT_PATH"; then
  HASH=$(shasum -a 256 "$HOME_PATH" | awk '{print $1}')
  printf '{"ts":"%s","skill":"%s","mode":"mirror-sync","status":"ok","sha256":"%s","verified_at":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$SKILL_NAME" \
    "$HASH" \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  exit 0
else
  echo "mirror-sync: cmp FAILED for ${SKILL_NAME} — home and vault are not byte-identical" >&2
  echo "  home:   $HOME_PATH ($(wc -c < "$HOME_PATH") bytes)" >&2
  echo "  vault:  $VAULT_PATH ($(wc -c < "$VAULT_PATH") bytes)" >&2
  exit 3
fi
