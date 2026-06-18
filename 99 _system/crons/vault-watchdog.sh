#!/usr/bin/env bash
# vault-watchdog.sh — three-hard-stops vault integrity watchdog.
# Implements the Matt Van Horn (2026-06-08) discipline codified in
# ~/.mavis/agents/mavis/memory/loop-engineering-framework.md:
#   1. Max iteration count (finite tick budget)
#   2. No-progress detection (output-hash convergence)
#   3. Token / dollar ceiling (rough byte proxy)
# Plus a wallclock TTL backstop baked into the cron prompt.
#
# State persists in vault-watchdog.state.json so the loop survives restart.
# State is the only persistent feedback channel between ticks; without it,
# the cron cannot tell whether it is making progress or stuck.
#
# Exit codes:
#   0 = all integrity checks passed (cron prompt: <mavis-progress>, exit)
#   1 = integrity check failed (cron prompt: page Andre with failure)
#   2 = halted by a hard stop (cron prompt: suggest `mavis cron delete`)

set -uo pipefail

STATE_DIR="$HOME/.mavis/agents/mavis/crons"
STATE_FILE="$STATE_DIR/vault-watchdog.state.json"
VAULT="/Users/brassfieldventuresllc/MiniMax-Agent"
BASELINE_SIZE_MB=50

# Hard-stop thresholds (tuneable)
# MAX_TICKS is a long-horizon backstop, not a per-shift budget. At 5-min intervals,
# 10000 ticks = ~35 days. The signal-based stops (no-progress, consecutive failures,
# dollar ceiling) are the actual feedback mechanism. MAX_TICKS only trips if those
# signals are missed or if the loop is otherwise stuck.
MAX_TICKS=10000
MAX_NO_PROGRESS_DUPLICATES=3
MAX_TOKENS_ESTIMATE_BYTES=100000
MAX_CONSECUTIVE_FAILURES=5

mkdir -p "$STATE_DIR"

# Initialize state on first run
if [ ! -f "$STATE_FILE" ]; then
  cat > "$STATE_FILE" <<'EOF'
{
  "tick_count": 0,
  "last_outputs": [],
  "consecutive_failures": 0,
  "total_bytes_estimate": 0,
  "last_tick_at": null,
  "halted": false,
  "halt_reason": null,
  "last_outcome": null
}
EOF
fi

# Helper: read a field from state
state_get() {
  python3 -c "import json,sys; print(json.load(open('$STATE_FILE')).get('$1', ''))"
}

# Helper: set fields in state
state_set() {
  python3 -c "
import json
with open('$STATE_FILE', 'r') as f: s = json.load(f)
$1
with open('$STATE_FILE', 'w') as f: json.dump(s, f, indent=2)
"
}

# === HARD STOP 0: already halted ===
HALTED=$(state_get halted)
if [ "$HALTED" = "True" ]; then
  REASON=$(state_get halt_reason)
  echo "vault-watchdog: already halted (reason: $REASON). To restart: delete state file."
  exit 2
fi

# === HARD STOP 1: max iteration count ===
TICK_COUNT=$(state_get tick_count)
if [ -n "$TICK_COUNT" ] && [ "$TICK_COUNT" -ge "$MAX_TICKS" ]; then
  state_set "s['halted'] = True; s['halt_reason'] = 'max_iter'"
  echo "vault-watchdog: HALTED — max iterations ($MAX_TICKS) reached."
  exit 2
fi

# === HARD STOP 2: no-progress detection (FAIL-output convergence only) ===
# A watchdog's healthy state IS stable. Three identical PASS outputs mean the vault
# is fine, not that the cron is stuck. Only trip on three identical FAIL outputs
# — that means the cron is reporting the same failure repeatedly without recovery,
# which is the @cv_usk failure mode in action.
NO_PROGRESS=$(python3 -c "
import json
s = json.load(open('$STATE_FILE'))
out = s.get('last_outputs', [])
fail = s.get('last_failure_hash', None)
fcount = s.get('consecutive_failures', 0)
if fcount >= $MAX_NO_PROGRESS_DUPLICATES and fail is not None:
  print('STUCK')
else:
  print('OK')
")
if [ "$NO_PROGRESS" = "STUCK" ]; then
  state_set "s['halted'] = True; s['halt_reason'] = 'no_progress'"
  echo "vault-watchdog: HALTED — last $MAX_NO_PROGRESS_DUPLICATES ticks reported the same FAILURE without recovery. The cron is stuck yelling."
  exit 2
fi

# === HARD STOP 3: token / dollar ceiling (rough byte proxy) ===
BYTES=$(state_get total_bytes_estimate)
if [ -n "$BYTES" ] && [ "$BYTES" -ge "$MAX_TOKENS_ESTIMATE_BYTES" ]; then
  state_set "s['halted'] = True; s['halt_reason'] = 'dollar_ceiling'"
  echo "vault-watchdog: HALTED — total byte estimate ($BYTES) >= $MAX_TOKENS_ESTIMATE_BYTES. Spend cap reached."
  exit 2
fi

# === HARD STOP 4: consecutive failures ===
FAILURES=$(state_get consecutive_failures)
if [ -n "$FAILURES" ] && [ "$FAILURES" -ge "$MAX_CONSECUTIVE_FAILURES" ]; then
  state_set "s['halted'] = True; s['halt_reason'] = 'consecutive_failures'"
  echo "vault-watchdog: HALTED — $MAX_CONSECUTIVE_FAILURES consecutive failures."
  exit 2
fi

# === INTEGRITY CHECKS ===
FAIL_DETAIL=""
OVERALL=0

check() {
  local name="$1"
  local cmd="$2"
  if eval "$cmd" >/dev/null 2>&1; then
    echo "OK    $name"
  else
    echo "FAIL  $name"
    FAIL_DETAIL="${FAIL_DETAIL}${name}; "
    OVERALL=1
  fi
}

check "vault-git-dir"      "test -d '$VAULT/.git'"
check "vault-inbox"        "test -d '$VAULT/00 Inbox'"
check "vault-projects"     "test -d '$VAULT/03 Projects'"
check "vault-memory-file"  "test -f '$VAULT/99 _system/memory/MEMORY.md'"

if git -C "$VAULT" log --oneline -1 >/dev/null 2>&1; then
  echo "OK    vault-git-log"
else
  echo "FAIL  vault-git-log (git history corrupted)"
  FAIL_DETAIL="${FAIL_DETAIL}vault-git-log; "
  OVERALL=1
fi

# Trash check (best-effort; macOS-specific)
TRASH_NAMES=$(osascript -e 'tell application Finder to return name of every item of trash' 2>/dev/null || echo "")
if echo "$TRASH_NAMES" | grep -q "MiniMax-Agent"; then
  echo "FAIL  vault-in-trash (Put Back required, do NOT auto-recover)"
  FAIL_DETAIL="${FAIL_DETAIL}vault-in-trash; "
  OVERALL=1
else
  echo "OK    vault-trash-check"
fi

# Size check
SIZE_MB=$(du -sm "$VAULT" 2>/dev/null | awk '{print $1}' || echo "0")
if [ "$SIZE_MB" -lt $((BASELINE_SIZE_MB / 2)) ]; then
  echo "FAIL  vault-size ($SIZE_MB MB < 25 MB threshold)"
  FAIL_DETAIL="${FAIL_DETAIL}vault-size; "
  OVERALL=1
else
  echo "OK    vault-size ($SIZE_MB MB)"
fi

# === COMPUTE OUTPUT HASH AND UPDATE STATE ===
OUTPUT_HASH=$(echo "$OVERALL $FAIL_DETAIL" | shasum -a 256 | awk '{print $1}')
NOW_ISO=$(date -u +%Y-%m-%dT%H:%M:%SZ)
ESTIMATED_BYTES=$(echo "$OVERALL $FAIL_DETAIL $OUTPUT_HASH" | wc -c)

state_set "
s['tick_count'] = s.get('tick_count', 0) + 1
s['last_outputs'] = (s.get('last_outputs', []) + ['$OUTPUT_HASH'])[-5:]
s['total_bytes_estimate'] = s.get('total_bytes_estimate', 0) + $ESTIMATED_BYTES
s['last_tick_at'] = '$NOW_ISO'
s['last_outcome'] = 'pass' if $OVERALL == 0 else 'fail'
if $OVERALL == 0:
  s['consecutive_failures'] = 0
  s['last_failure_hash'] = None
else:
  s['consecutive_failures'] = s.get('consecutive_failures', 0) + 1
  s['last_failure_hash'] = '$OUTPUT_HASH'
"

# === EXIT ===
if [ "$OVERALL" -eq 0 ]; then
  echo "vault-watchdog: tick $((TICK_COUNT + 1)) — all checks pass (output_hash=$OUTPUT_HASH)"
  exit 0
else
  echo "vault-watchdog: tick $((TICK_COUNT + 1)) — FAILURE: $FAIL_DETAIL"
  exit 1
fi
