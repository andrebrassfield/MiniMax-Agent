# Schema Discipline — ea-commitment-tracker

The 6-field + 5 metadata field presence check + append-only
verification. The eval suite verifies each commitment line
has the right shape.

## S1. 6 load-bearing fields are present

```bash
# Each commitment line in the JSONL must have the 6 fields
required_fields='commitment|beneficiary|due_by|surface|dependencies|status'

while IFS= read -r line; do
  missing=$(echo "$line" | jq -r 'keys[]' | sort | comm -23 \
    <(echo "$required_fields" | tr '|' '\n' | sort))
  if [ -n "$missing" ]; then
    echo "FAIL: line missing fields: $missing"
    echo "  line: $line"
  fi
done < ~/.mavis/agents/mavis/commitments.jsonl
```

**Failure mode this catches:** a commitment line is missing
one of the 6 load-bearing fields. The format forces rigor;
missing fields mean the commitment is incomplete.

## S2. 5 metadata fields are present

```bash
required_metadata='ts|session_pointer|delivered_at|reversed_at|reversal_reason'

while IFS= read -r line; do
  missing=$(echo "$line" | jq -r 'keys[]' | sort | comm -23 \
    <(echo "$required_metadata" | tr '|' '\n' | sort))
  if [ -n "$missing" ]; then
    echo "FAIL: line missing metadata: $missing"
  fi
done < ~/.mavis/agents/mavis/commitments.jsonl
```

**Failure mode this catches:** a commitment line is missing
metadata. The `ts` + `session_pointer` are required at
creation; the lifecycle fields (`delivered_at`, `reversed_at`,
`reversal_reason`) are required when applicable.

## S3. Append-only (no edits to prior lines)

```bash
# Compare current line count to the sum of: original commitments
# + status changes. If the count matches, append-only is intact.

# Approximate: count the number of "DELIVERED:" / "REVERSED:" /
# "DROPPED:" prefixes (these are status changes, not originals)
status_changes=$(grep -cE "DELIVERED:|REVERSED:|DROPPED:" \
  ~/.mavis/agents/mavis/commitments.jsonl)
total_lines=$(wc -l < ~/.mavis/agents/mavis/commitments.jsonl)
originals=$((total_lines - status_changes))

# If git tracks the file, check the diff for any lines that
# disappeared or were modified
git -C ~/MiniMax-Agent log -p --follow -- \
  ~/.mavis/agents/mavis/commitments.jsonl | grep -E "^-" | head -5
```

**Failure mode this catches:** a prior line was edited (not
appended). The audit trail is broken.

**Note:** the JSONL is in `~/.mavis/agents/mavis/`, NOT in
the vault. Git tracking is on the mirror file at
`02 Notes/commitments/YYYY-MM.md` (the vault side).

## S4. Status lifecycle is valid

```bash
valid_statuses='open|in-progress|delivered|dropped|reversed'

while IFS= read -r line; do
  status=$(echo "$line" | jq -r '.status // ""')
  if ! echo "$status" | grep -qE "^($valid_statuses)$"; then
    echo "FAIL: invalid status: $status"
  fi
done < ~/.mavis/agents/mavis/commitments.jsonl
```

**Failure mode this catches:** an invalid status string
(typo, non-lifecycle state).

## S5. Reversed lines have a reason

```bash
# Any line with status=reversed must have a non-empty
# reversal_reason
while IFS= read -r line; do
  if echo "$line" | jq -e '.status == "reversed"' > /dev/null; then
    reason=$(echo "$line" | jq -r '.reversal_reason // ""')
    if [ -z "$reason" ]; then
      echo "FAIL: reversed line without reason: $line"
    fi
  fi
done < ~/.mavis/agents/mavis/commitments.jsonl
```

**Failure mode this catches:** a `reversed` line without a
reason. Per hard constraint #10, this is a discipline
violation.

## S6. Delivered lines have delivered_at

```bash
while IFS= read -r line; do
  if echo "$line" | jq -e '.status == "delivered"' > /dev/null; then
    delivered_at=$(echo "$line" | jq -r '.delivered_at // ""')
    if [ -z "$delivered_at" ] || [ "$delivered_at" = "null" ]; then
      echo "FAIL: delivered line without delivered_at: $line"
    fi
  fi
done < ~/.mavis/agents/mavis/commitments.jsonl
```

**Failure mode this catches:** a `delivered` line without
the delivery timestamp.

## S7. Surface is non-empty

```bash
# The surface can be "TBD" but not empty
while IFS= read -r line; do
  surface=$(echo "$line" | jq -r '.surface // ""')
  if [ -z "$surface" ]; then
    echo "FAIL: commitment without surface: $line"
  fi
done < ~/.mavis/agents/mavis/commitments.jsonl
```

**Failure mode this catches:** a commitment without a
surface. The surface can be `"TBD"` if unclear, but never
empty.

## S8. Beneficiary is named

```bash
# beneficiary must be "andre" or "third-party:<name>"
while IFS= read -r line; do
  beneficiary=$(echo "$line" | jq -r '.beneficiary // ""')
  if [ -z "$beneficiary" ]; then
    echo "FAIL: commitment without beneficiary: $line"
  fi
  if ! echo "$beneficiary" | grep -qE "^(andre|third-party:)"; then
    echo "WARN: non-default beneficiary: $beneficiary"
  fi
done < ~/.mavis/agents/mavis/commitments.jsonl
```

**Failure mode this catches:** a commitment without a
beneficiary, or a beneficiary that's not in the expected
format.
