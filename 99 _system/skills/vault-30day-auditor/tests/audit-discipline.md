# Audit Discipline — vault-30day-auditor

The 5-floor quality check the audit itself must pass. The
audit is a verifier — it must not become the thing it's
auditing (introducing recap-vs-disk mismatch into the
footprint report).

## A1. No-invented-context floor (the load-bearing element)

**Verification:** every claim in the report has file
evidence in the appendix.

```bash
report="03 Projects/Mavis EA Design/reports/30-day-footprint-2026-06-17.md"

# Extract section content
active_pipelines=$(awk '/^## 4\. Active project pipelines/,/^## 5\./' "$report")
core_topics=$(awk '/^## 5\. Core topics/,/^## 6\./' "$report")
repetitive_tasks=$(awk '/^## 6\. Repetitive manual tasks/,/^## 7\./' "$report")

# For each project mentioned in section 4, verify it has a
# file in the appendix
for project in $(echo "$active_pipelines" | grep -E "^\d+\. \*\*" | awk -F'\\*\\*' '{print $2}'); do
  # Project must have ≥1 file in the appendix
  appendix_files=$(awk '/^## 9\. Appendix/,/^$/' "$report" | grep -c "$project")
  if [ "$appendix_files" -lt 1 ]; then
    echo "FAIL: project '$project' has no file in appendix"
  fi
done

# For each topic in section 5, verify it has ≥2 file references
for topic in $(echo "$core_topics" | grep -E "^\d+\. \*\*" | awk -F'\\*\\*' '{print $2}'); do
  # Topic should have a "files:" line with ≥2 entries
  topic_files=$(echo "$core_topics" | grep -A2 "^\d\+\. \*\*$topic\*\*" | grep "files:" | wc -l)
  if [ "$topic_files" -lt 1 ]; then
    echo "FAIL: topic '$topic' has no files: line"
  fi
done
```

**Failure mode this catches:** the report mentions a
project or topic that has no file evidence. The report is
a recap, not a footprint.

## A2. Disk-wins-over-recap floor

**Verification:** every "active project" line references a
real project dir in `03 Projects/`.

```bash
# Each project mentioned must exist on disk
for project in $(awk '/^## 4\. Active project pipelines/,/^## 5\./' "$report" \
  | grep -E "^\d+\. \*\*" | awk -F'\\*\\*' '{print $2}'); do
  if [ ! -d "$VAULT/03 Projects/$project" ]; then
    echo "FAIL: project '$project' does not exist on disk"
  fi
done
```

**Failure mode this catches:** the report names a project
that doesn't exist. Recap contamination.

## A3. Mavis-synthesizes floor (no x-researcher dispatch)

**Verification:** the audit was done in-session by Mavis,
not dispatched to a sub-agent.

```bash
# Check the generator field in the YAML frontmatter
generator=$(grep "^generator:" "$report" | awk '{print $2}')
echo "$generator" | grep -qiE "(mavis|chief-of-staff|in-session)" \
  || echo "FAIL: generator field does not indicate in-session synthesis"

# Check for any spawn commands in the audit log
grep -c "spawn.*x-researcher\|spawn.*x-scribe" audit.log 2>/dev/null
# Should be 0 — no dispatch for this work
```

**Failure mode this catches:** the audit dispatched to
x-researcher (wrong agent for this work — domain mismatch).

## A4. Quantified-claims-verified floor

**Verification:** every count in the report matches a
disk-hittable command.

```bash
# files_in_window must match `find | wc -l`
claimed=$(grep "^files_in_window:" "$report" | awk '{print $2}')
actual_daily=$(find "$VAULT/01 Daily" -type f -mtime -30 | wc -l)
actual_projects=$(find "$VAULT/03 Projects" -type f -mtime -30 | wc -l)
actual=$((actual_daily + actual_projects))
if [ "$claimed" != "$actual" ]; then
  echo "FAIL: files_in_window mismatch (claimed=$claimed, actual=$actual)"
fi

# daily notes count must match `ls 01 Daily/`
claimed_notes=$(echo "$report" | grep -c "days with notes")
# (heuristic — actually verify the dates against `ls`)
```

**Failure mode this catches:** the report's counts
disagree with the disk. The audit's claims must be
verifiable.

## A5. Mavis-territory floor (no cross-team activity)

**Verification:** the report does NOT include activity
from `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, or
`~/.hermes-evolution/`.

```bash
# Check for forbidden paths in the report
forbidden='~/\.hermes|~/\.openclaw|~/\.gbrain|~/\.hermes-evolution'
grep -qE "$forbidden" "$report" && echo "FAIL: report references other agent's tree"

# Check that the report's vault_root is Mavis's vault
vault_root=$(grep "^vault_root:" "$report" | awk '{print $2}')
echo "$vault_root" | grep -q "MiniMax-Agent" \
  || echo "FAIL: vault_root is not Mavis's vault"
```

**Failure mode this catches:** the audit crossed into
another agent's tree. Mavis territory rule violation.
