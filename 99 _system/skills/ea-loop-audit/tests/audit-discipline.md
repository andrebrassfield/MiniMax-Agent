# Audit Discipline — ea-loop-audit

The 5-floor quality check the audit itself must pass. The
audit is a verifier — it must not become the thing it's
auditing.

## A1. No-false-PASS floor

**Verification:** the auditor produces a disk hit for every
PASS verdict.

```bash
# For each dimension with PASS, evidence must be a disk hit
for dim in d1 d2 d3 d4 d5 d6 d7; do
  verdict=$(grep -A1 "^$dim:" report.md | tail -1 | awk '{print $2}')
  evidence=$(grep -A1 "^$dim:" report.md | tail -1 | sed 's/^[^—]*— //')
  if [ "$verdict" = "PASS" ]; then
    # Evidence must contain a disk path, log line, or file reference
    echo "$evidence" | grep -qE "(/Users/|\.md|\.log|\.json|exit code|test|todowrite)" \
      || echo "FAIL: $dim has PASS without disk evidence"
  fi
done
```

**Failure mode this catches:** the auditor gave a PASS
without producing disk evidence. PASS without evidence is
a recap, not an audit.

## A2. Disk-wins-over-recap floor

**Verification:** every FAIL or WARN verdict has a disk hit
referenced in the evidence, not a memory-based claim.

```bash
# For each dimension, evidence should be traceable to a file
for dim in d1 d2 d3 d4 d5 d6 d7; do
  evidence=$(grep -A1 "^$dim:" report.md | tail -1 | sed 's/^[^—]*— //')
  # Check for memory-based claims ("I remember", "I think",
  # "based on context", "from prior session")
  if echo "$evidence" | grep -qiE "(I remember|I think|based on context|from prior|presumably|probably|likely)"; then
    echo "FAIL: $dim has recap evidence (memory-based, not disk)"
  fi
done
```

**Failure mode this catches:** the auditor used a
memory-based claim as evidence. Disk wins.

## A3. Audit-not-fix floor

**Verification:** the report does NOT contain fix actions,
only minimum-fix recommendations.

```bash
# Check for action verbs that imply fixing
fix_actions="apply|patch|edit|modify|fix|change|update|replace|delete|remove"
grep -qiE "^($fix_actions)\\b" report.md && echo "WARN: report contains action verbs (fix actions)"

# The report should say "minimum fix" (a recommendation) not
# "fixing" (an action)
```

**Failure mode this catches:** the audit crossed the line
into fixing. The audit is read-only; the worker fixes, not
the auditor.

## A4. Mavis-territory floor (for cross-team audits)

**Verification:** if the work is cross-team (Hermes,
OpenClaw, Socratic, etc.), the report follows the
cross-team-discipline rule: (1) what they got right, (2)
what they got wrong (recap-vs-disk), (3) stop. NOT a fix-it
list.

```bash
# Check the cross-team marker
is_cross_team=$(grep -qE "hermes|openclaw|socratic|hermes-evolution" report.md && echo "yes")
if [ "$is_cross_team" = "yes" ]; then
  # Report should have these 3 sections
  for section in "what they got right" "what they got wrong" "stop"; do
    grep -qi "$section" report.md || echo "FAIL: cross-team report missing '$section' section"
  done
  # Report should NOT have a "Recommended fixes" or "TODO" section
  if grep -qiE "(recommended fixes|TODO|action items|build proposal)" report.md; then
    echo "FAIL: cross-team report has fix-it list (Mavis is not the PM for other teams)"
  fi
fi
```

**Failure mode this catches:** the audit crossed into
cross-team territory and produced a fix-it list. Mavis
audits Mavis-side work only.

## A5. Verdict-honesty floor

**Verification:** the final verdict matches the worst
dimension.

```bash
# Extract final verdict
verdict=$(grep "^\\- \\*\\*Verdict:\\*\\*" report.md | awk '{print $NF}')

# Count FAILs
fails=$(grep -c "FAIL" report.md)
warns=$(grep -c "WARN" report.md)

if [ "$fails" -gt 0 ] && [ "$verdict" = "PASS" ]; then
  echo "FAIL: final verdict is PASS but dimensions have FAILs"
fi
if [ "$fails" -eq 0 ] && [ "$warns" -gt 0 ] && [ "$verdict" = "PASS" ]; then
  echo "WARN: final verdict is PASS but dimensions have WARNs"
fi
```

**Failure mode this catches:** the auditor glossed over
FAILs to give a clean PASS. The verdict must reflect the
worst dimension.
