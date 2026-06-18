# Spec Completeness — ea-closed-loop-builder

The 5-section sanity check. Each section has a defined purpose
and a defined minimum content. The eval cases verify each
section is filled out and the spec is executable.

## S1. GOAL section is precise

```bash
# Extract the GOAL section
goal=$(awk '/^## 1\. GOAL/,/^## 2\. CONTEXT/' spec.md | head -n -2)

# Must contain an outcome (one sentence)
echo "$goal" | grep -qE "^The outcome|This loop produces|This spec produces" \
  || echo "FAIL: GOAL section has no outcome statement"

# Must contain a deliverable (where it lands)
echo "$goal" | grep -qE "(user.visible deliverable|written to|lands at|output:|\.md|\.json)" \
  || echo "FAIL: GOAL section has no deliverable"

# Must contain a success criterion (what evidence = done)
echo "$goal" | grep -qE "(success criterion|evidence = done|complete when|done when|done if)" \
  || echo "FAIL: GOAL section has no success criterion"
```

**Failure mode this catches:** vague goals that don't
distinguish "done" from "still running."

## S2. CONTEXT section has all 3 V/A/R files

```bash
context=$(awk '/^## 2\. CONTEXT/,/^## 3\. ACTION/' spec.md | head -n -2)

# VISION
echo "$context" | grep -qE "^\*\*VISION:\*\*" || echo "FAIL: no VISION"
# ARCHITECTURE
echo "$context" | grep -qE "^\*\*ARCHITECTURE:\*\*" || echo "FAIL: no ARCHITECTURE"
# RULES
echo "$context" | grep -qE "^\*\*RULES:\*\*" || echo "FAIL: no RULES"
```

**Failure mode this catches:** loops that re-derive context
from scratch instead of reading persistent V/A/R files.

## S3. ACTION section is atomic + idempotent

```bash
action=$(awk '/^## 3\. ACTION/,/^## 4\. FEEDBACK/' spec.md | head -n -2)

# Count numbered steps
step_count=$(echo "$action" | grep -cE "^[0-9]+\\. ")

# Must have at least 1 step
[ "$step_count" -lt 1 ] && echo "FAIL: no ACTION steps"

# Must not have unstated globals ("use the latest data")
echo "$action" | grep -qiE "(use the latest|use current|read the data)" \
  && echo "WARN: ACTION has unstated global references"
```

**Failure mode this catches:** action sections that are
"vibes" rather than discrete steps the executor can run.

## S4. FEEDBACK section is non-empty (the load-bearing section)

```bash
feedback=$(awk '/^## 4\. FEEDBACK/,/^## 5\. STOP/' spec.md | head -n -2)

# Must name a verifier
echo "$feedback" | grep -qE "^\- \\*\\*Verifier:\\*\\*" || echo "FAIL: no Verifier"
# Must name evidence
echo "$feedback" | grep -qE "^\- \\*\\*Evidence:\\*\\*" || echo "FAIL: no Evidence"
# Must name frequency
echo "$feedback" | grep -qE "^\- \\*\\*Frequency:\\*\\*" || echo "FAIL: no Frequency"
# Must name on-FAIL path
echo "$feedback" | grep -qE "^\- \\*\\*On FAIL:\\*\\*" || echo "FAIL: no On-FAIL path"
```

**Failure mode this catches:** loops without a verification
gate (the load-bearing section). A loop without a gate is a
task list, not a loop.

## S5. STOP CONDITION has trigger + cleanup + escalation

```bash
stop=$(awk '/^## 5\. STOP CONDITION/,/^$/' spec.md | head -n -2)

# Trigger
echo "$stop" | grep -qE "^\- \\*\\*Trigger:\\*\\*" || echo "FAIL: no Trigger"
# Cleanup
echo "$stop" | grep -qE "^\- \\*\\*Cleanup:\\*\\*" || echo "FAIL: no Cleanup"
# Escalation
echo "$stop" | grep -qE "^\- \\*\\*Escalation:\\*\\*" || echo "FAIL: no Escalation"
```

**Failure mode this catches:** loops with no end condition
that run until someone gets tired of them.

## S6. Cost ceiling is in the frontmatter

```bash
# Frontmatter line
grep -qE "^\\*\\*Cost ceiling:\\*\\* " spec.md || echo "FAIL: no cost ceiling in frontmatter"
# Must have a value
cost=$(grep "^\\*\\*Cost ceiling:\\*\\* " spec.md | sed 's/.*: //')
[ -z "$cost" ] && echo "FAIL: cost ceiling is empty"
```

**Failure mode this catches:** loops with no cost ceiling
(the loop is open-ended; use `ea-loop-thinking` instead).

## S7. Disk references resolve

```bash
# Extract all file references in CONTEXT
context_files=$(awk '/^## 2\. CONTEXT/,/^## 3\. ACTION/' spec.md \
  | grep -oE '[A-Za-z0-9_./-]+\.md' | sort -u)

# Each must exist
for f in $context_files; do
  # Resolve relative to spec directory
  spec_dir=$(dirname "$spec_path")
  resolved="$spec_dir/$f"
  [ ! -f "$resolved" ] && [ ! -f "$f" ] && echo "FAIL: missing context file: $f"
done
```

**Failure mode this catches:** specs that link to V/A/R
files that don't exist on disk. Disk is ground truth.
