# Audit Discipline — ea-decision-logger

The 4-floor quality check the audit itself must pass. The
decision logger is the source of architectural truth; it
must not become the thing it's auditing (a chat-log dump
or a partial file).

## A1. All-5-fields-required floor (the load-bearing discipline)

**Verification:** if any field is missing, the file is
not a valid decision.

```bash
# Reuse the 5-field presence checks
decision_file="$1"
for section in \
  "^## Decision$" \
  "^## Rationale$" \
  "^## Alternatives considered$" \
  "^## Expected impact$" \
  "^## What would change my mind$"; do
  if ! grep -qE "$section" "$decision_file"; then
    echo "FAIL: $section missing — this is a partial decision, not a valid file"
  fi
done
```

**Failure mode this catches:** a partial decision file
in the `decisions/` folder. Per hard constraint #1, a
partial file is worse than no file (creates a false
record of rigor).

## A2. Append-only floor

**Verification:** the file was not edited after creation.
A reverse creates a NEW file; it does not edit the
original.

```bash
# Check the git log for the decision file
git -C ~/MiniMax-Agent log --follow --oneline -- \
  "02 Notes/decisions/$decision_filename"

# If the file has been modified after creation, the
# "modification" should be a NEW file (a reversal), not
# an edit to the original
```

**Failure mode this catches:** the file was edited, not
appended. The audit trail is broken.

## A3. Mavis-territory floor

**Verification:** the decision does not belong to another
agent's tree.

```bash
# Check the related surfaces — none should be in
# other agents' trees
yaml=$(awk '/^---$/,/^---$/' "$decision_file")
related=$(echo "$yaml" | grep -A20 "related:" | grep -E "^  - " | head -10)

for surface in $related; do
  if echo "$surface" | grep -qE "(~/.hermes|~/.openclaw|~/.gbrain|~/.hermes-evolution)"; then
    echo "FAIL: decision references other agent's tree: $surface"
  fi
done
```

**Failure mode this catches:** the decision is about
another agent's work. Mavis territory rule violation.

## A4. Stable-filename floor

**Verification:** the filename slug is 2-4 words,
lowercase, hyphenated, captures the essence.

```bash
# Extract the slug from the filename
filename=$(basename "$decision_file")
slug=$(echo "$filename" | sed 's/^[0-9-]*//' | sed 's/\\.md$//')

# Count words
word_count=$(echo "$slug" | tr '-' ' ' | wc -w | tr -d ' ')

[ "$word_count" -lt 2 ] && echo "FAIL: slug has $word_count words (need 2-4)"
[ "$word_count" -gt 4 ] && echo "WARN: slug has $word_count words (5+ is too long)"

# Must be lowercase + hyphenated
echo "$slug" | grep -qE "^[a-z][a-z0-9-]+$" \
  || echo "FAIL: slug is not lowercase + hyphenated: $slug"
```

**Failure mode this catches:** the filename is not
stable (e.g., `decision-1.md` is not stable; `gepa-pivot.md`
is stable).
