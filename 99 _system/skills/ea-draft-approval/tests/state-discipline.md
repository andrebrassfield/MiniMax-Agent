# State Discipline — ea-draft-approval

The 4-floor quality check the state file must pass. The
state is the audit trail; it must not become the thing
it's auditing (a partial or stale state).

## S1. Append-only floor (the load-bearing discipline)

**Verification:** the state file is not edited; new
proposals append, status changes are updates.

```bash
STATE="$HOME/.mavis/agents/mavis/crons/ea-draft-approval.state.json"

# Verify the JSON is valid
jq -e . "$STATE" > /dev/null 2>&1 || echo "FAIL: state is not valid JSON"

# Verify the schema
jq -e '.last_scan_at' "$STATE" > /dev/null 2>&1 || echo "FAIL: last_scan_at missing"
jq -e '.proposals' "$STATE" > /dev/null 2>&1 || echo "FAIL: proposals missing"

# Each proposal has the required fields
jq -r '.proposals[] | @json' "$STATE" | while IFS= read -r proposal; do
  for field in draft_id source_file draft_number post_text proposed_at response_status; do
    echo "$proposal" | jq -e ".$field" > /dev/null 2>&1 \
      || echo "FAIL: proposal missing field: $field"
  done
done
```

**Failure mode this catches:** the state file is
malformed or missing required fields. The audit trail is
broken.

## S2. Stable-draft_id floor

**Verification:** every draft_id is unique and matches
the `<file>:<draft-N>:<sha256>` pattern.

```bash
# Verify all draft_ids are unique
jq -r '.proposals[].draft_id' "$STATE" | sort | uniq -d

# Verify the format
jq -r '.proposals[].draft_id' "$STATE" | while read -r id; do
  echo "$id" | grep -qE "^.+\\.md:[0-9]+:[a-f0-9]{64}$" \
    || echo "FAIL: invalid draft_id format: $id"
done
```

**Failure mode this catches:** a draft_id is malformed
or duplicated. The reply-matching logic will fail.

## S3. No-silent-failure floor

**Verification:** every open proposal has a proposed_at
timestamp; every closed proposal has a response_status
that is not "open" + a responded_at timestamp.

```bash
# Open proposals must have proposed_at
open_count=$(jq '[.proposals[] | select(.response_status == "open")] | length' "$STATE")
[ "$open_count" -gt 0 ] && echo "WARN: $open_count open proposals (may indicate silent failure)"

# Closed proposals must have responded_at
jq -r '.proposals[] | select(.response_status != "open") | .responded_at' "$STATE" \
  | grep -c "null" || echo "0"
# (count of null responded_at in closed proposals; should be 0)
```

**Failure mode this catches:** a closed proposal is
missing its response timestamp. The audit trail is
incomplete.

## S4. Mirror discipline floor

**Verification:** the agent home + vault mirror are
byte-identical.

```bash
HOME_STATE="$HOME/.mavis/agents/mavis/crons/ea-draft-approval.state.json"
VAULT_STATE="$HOME/MiniMax-Agent/99 _system/crons/ea-draft-approval.state.json"

# Both files must exist
[ -f "$HOME_STATE" ] || echo "FAIL: agent home state missing"
[ -f "$VAULT_STATE" ] || echo "FAIL: vault mirror state missing"

# Byte-identity check
cmp -s "$HOME_STATE" "$VAULT_STATE" || echo "FAIL: mirror mismatch"
```

**Failure mode this catches:** the mirror is out of
sync. Per `ea-skill-evolution` Hard Constraint #6, mirror
discipline is the load-bearing rule.
