# 4-Field Presence — agent-deployment-monitor

The eval suite verifies each `deployment-status.md` has
all 4 fields populated (or marked "unclear" with a reason).

## F1. Agent-Type is populated

```bash
# Extract the Agent-Type value from the status board
agent_type=$(awk '/\*\*Agent-Type\*\*/,/^---/' "$status_file" \
  | grep -oE "Voice|SMS|Scraper|Other|unclear" | head -1)
[ -z "$agent_type" ] && echo "FAIL: Agent-Type not populated"
echo "$agent_type" | grep -qE "^(Voice|SMS|Scraper|Other|unclear)$" \
  || echo "FAIL: Agent-Type is invalid: $agent_type"
```

**Failure mode this catches:** Agent-Type is missing or
has an invalid value.

## F2. Last-Sync-Date is populated (or "unclear")

```bash
# Extract the Last-Sync-Date value
last_sync=$(awk '/\*\*Last-Sync-Date\*\*/,/^---/' "$status_file" \
  | grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}|unclear" | head -1)
[ -z "$last_sync" ] && echo "FAIL: Last-Sync-Date not populated"
echo "$last_sync" | grep -qE "^([0-9]{4}-[0-9]{2}-[0-9]{2}|unclear)$" \
  || echo "FAIL: Last-Sync-Date is invalid: $last_sync"
```

**Failure mode this catches:** Last-Sync-Date is missing
or has an invalid value (not a date, not "unclear").

## F3. Lead-Volume-Today is populated (or "unclear")

```bash
lead_volume=$(awk '/\*\*Lead-Volume-Today\*\*/,/^---/' "$status_file" \
  | grep -oE "[0-9]+|unclear" | head -1)
[ -z "$lead_volume" ] && echo "FAIL: Lead-Volume-Today not populated"
echo "$lead_volume" | grep -qE "^([0-9]+|unclear)$" \
  || echo "FAIL: Lead-Volume-Today is invalid: $lead_volume"
```

**Failure mode this catches:** Lead-Volume-Today is missing
or has an invalid value.

## F4. Error-Log-Alerts is populated (or "unclear")

```bash
error_alerts=$(awk '/\*\*Error-Log-Alerts\*\*/,/^---/' "$status_file" \
  | grep -oE "[0-9]+|unclear" | head -1)
[ -z "$error_alerts" ] && echo "FAIL: Error-Log-Alerts not populated"
echo "$error_alerts" | grep -qE "^([0-9]+|unclear)$" \
  || echo "FAIL: Error-Log-Alerts is invalid: $error_alerts"
```

**Failure mode this catches:** Error-Log-Alerts is missing
or has an invalid value.

## F5. Inference notes are documented for non-Other types

```bash
# If Agent-Type is not "Other" or "unclear", the inference notes
# section should explain the heuristic used
if [ "$agent_type" != "Other" ] && [ "$agent_type" != "unclear" ]; then
  notes=$(awk '/## Inference notes/,/^## /' "$status_file" | grep -v "^##" | wc -l | tr -d ' ')
  [ "$notes" -lt 1 ] && echo "FAIL: Inference notes empty for Agent-Type $agent_type"
fi
```

**Failure mode this catches:** the inference heuristic is
not documented. The operator can't verify or override.

## F6. Data source section explains "unclear" fields

```bash
# For each "unclear" field, the data source section should
# explain why
unclear_fields=$(grep -oE "\*\*[A-Z][a-z-]+\*\*: unclear" "$status_file" | wc -l | tr -d ' ')
data_source_section=$(awk '/## Data source/,/^## /' "$status_file" | wc -l | tr -d ' ')

if [ "$unclear_fields" -gt 0 ] && [ "$data_source_section" -lt 2 ]; then
  echo "FAIL: $unclear_fields 'unclear' fields but Data source section is empty"
fi
```

**Failure mode this catches:** the operator sees "unclear"
without knowing why. The data source section must explain.

## F7. Quick links section is present

```bash
grep -qF "## Quick links" "$status_file" \
  || echo "FAIL: Quick links section missing"
```

**Failure mode this catches:** the operator can't navigate
from the per-client file to the God View (or vice versa).

## F8. Generator is identified

```bash
grep -qE "^generator: agent-deployment-monitor" "$status_file" \
  || echo "FAIL: generator not identified in frontmatter"
```

**Failure mode this catches:** the file's provenance is
unknown. The operator can't tell whether the file is the
skill's output or a manual edit.
