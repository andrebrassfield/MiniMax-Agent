# Audit Discipline — ea-data-quality-audit

The 4-floor quality check the audit itself must pass. The
audit is a verifier — it must not become the thing it's
auditing (a recap of the corpus instead of a disk-hit
inventory).

## A1. Disk-wins floor (the load-bearing discipline)

**Verification:** every inventory entry, filter, dedup, and
score references a real file path.

```bash
# Extract every file:line reference in the report
report_refs=$(grep -oE "MEMORY\\.md:[0-9]+|memory/[^:]+\\.md:[0-9]+|skills/[^:]+\\.md:[0-9]+|99 _system/skills/[^:]+\\.md:[0-9]+" "$report" | sort -u)

# Each reference must resolve to a real file
for ref in $report_refs; do
  file=$(echo "$ref" | cut -d: -f1)
  if [ ! -f "$HOME/.mavis/agents/mavis/$file" ] && [ ! -f "$HOME/MiniMax-Agent/$file" ]; then
    echo "FAIL: reference to non-existent file: $ref"
  fi
done
```

**Failure mode this catches:** the audit references a
file that doesn't exist on disk. Recap contamination.

## A2. No-fixing-during-audit floor

**Verification:** the report does NOT contain fix actions,
only minimum-fix recommendations.

```bash
# Check for action verbs that imply fixing (vs recommending)
fix_actions="apply|patch|edit|modify|fix|change|update|replace|delete|remove|merge"
grep -qiE "^($fix_actions)\\b" "$report" && echo "WARN: report contains action verbs (fix actions)"

# The report should say "recommend" (a recommendation) not
# "fixing" (an action)
```

**Failure mode this catches:** the audit crossed the line
into fixing. The audit is read-only; the chief fixes
separately, not the auditor.

## A3. Mavis-territory floor

**Verification:** the audit's inventory does NOT include
files from other agents' trees.

```bash
# Check for forbidden paths in the report
forbidden='~/\.hermes|~/\.openclaw|~/\.gbrain|~/\.hermes-evolution'
grep -qE "$forbidden" "$report" && echo "FAIL: report references other agent's tree"

# Verify the report's scope is Mavis-only
scope=$(grep "^Scope:" "$report" | head -1)
echo "$scope" | grep -qiE "Mavis|~/.mavis" \
  || echo "WARN: scope doesn't explicitly state Mavis-only"
```

**Failure mode this catches:** the audit crossed into
another agent's tree. Mavis territory rule violation.

## A4. Recommended-actions priority floor

**Verification:** the recommended-actions list is
priority-ordered and the top 3 are doable in one session.

```bash
# Extract recommended actions
actions=$(awk '/## 6\. Recommended actions/,EOF' "$report")

# Count numbered items
action_count=$(echo "$actions" | grep -cE "^[0-9]+\\. ")

# Top 3 should be doable in one session (heuristic: <2 hours each)
# Manual review: the chief reads the top 3 and verifies each is <2 hours
[ "$action_count" -gt 10 ] && echo "WARN: $action_count actions (top 3 should be doable in one session; rest are 'for later')"
```

**Failure mode this catches:** the recommended-actions list
is too long (loses focus) or not priority-ordered (no
clear "do this first" signal).
