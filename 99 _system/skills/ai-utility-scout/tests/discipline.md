# Discipline — ai-utility-scout

The 5-floor quality check the audit itself must pass. The
scout is a verifier — it must not become the thing it's
auditing (a hype-cycle echo chamber instead of a specific
boring SMB tool).

## D1. Specific-tool-named floor (the load-bearing element)

**Verification:** the Scribe's draft includes the specific
tool name, not a generic placeholder.

```bash
# Extract the tool name from the brief
tool_name=$(awk '/^## Tool:/,/^### What it does/' "$draft_file" | head -1 | awk -F'—' '{print $2}' | xargs)

# Extract the post draft
post=$(awk '/^### Post draft/,/^### Character count/' "$draft_file" | tail -n +2 | head -1)

# The post must contain the specific tool name (case-insensitive)
echo "$post" | grep -qiF "$tool_name" \
  || echo "FAIL: post doesn't name the specific tool ($tool_name)"

# The post must NOT use generic placeholders
echo "$post" | grep -qiE "(an AI tool|a new platform|this AI|some AI|the AI)" \
  && echo "FAIL: post uses generic placeholder instead of specific tool name"
```

**Failure mode this catches:** the Scribe wrote "an AI
tool" instead of naming the actual tool. The audience
can't act on a generic reference.

## D2. $/month anchor floor

**Verification:** the post includes a specific dollar
amount OR explicitly marks `unclear`.

```bash
# The "Cost" section must have a value or "unclear"
cost=$(awk '/^### Cost/,/^### Time saved/' "$draft_file" | tail -n +2 | head -1)
echo "$cost" | grep -qE "(\\\$[0-9]+|unclear|free)" \
  || echo "FAIL: Cost section missing $/month or 'unclear'"

# The post itself should reference the cost (not always required,
# but if the post has no cost, the operator should know)
echo "$post" | grep -qiE "(\\\$|free|costs?|\\\$/month|month)" \
  || echo "WARN: post doesn't reference cost at all"
```

**Failure mode this catches:** the post has no cost
anchor. The audience can't evaluate the tool.

## D3. 4-step-concrete floor

**Verification:** the 4-step implementation is concrete
(named tools, specific actions) — not generic.

```bash
# Extract the 4 steps
steps=$(awk '/^### 4-step implementation/,/^### Cost/' "$draft_file" | tail -n +2)

# Must have 4 numbered steps
step_count=$(echo "$steps" | grep -cE "^[0-9]+\\. ")
[ "$step_count" -ne 4 ] && echo "FAIL: 4-step has $step_count steps (should be 4)"

# Each step must mention a tool or specific action
for step in 1 2 3 4; do
  step_text=$(echo "$steps" | grep "^$step\\.")
  vague_step="^(learn|try|figure|set up|integrate|find|explore|use AI)"
  echo "$step_text" | grep -qiE "$vague_step" \
    && echo "FAIL: step $step is vague"
done
```

**Failure mode this catches:** the 4 steps are vague
filler ("learn the tool" / "try it" / "see if it works").
The audience can't act on vague steps.

## D4. No-fabrication floor

**Verification:** the Scribe's draft doesn't include
features not in the Researcher's brief.

```bash
# Extract the Researcher's brief (features mentioned)
brief_features=$(awk '/^### What it does/,/^### What makes it hype/' "$draft_file" \
  | grep -oE "[A-Z][a-z]+" | sort -u)

# Extract the Scribe's draft (features mentioned)
draft_features=$(awk '/^### Post draft/,/^### Character count/' "$draft_file" \
  | grep -oE "[A-Z][a-z]+" | sort -u)

# (heuristic — full implementation would use embeddings or
# explicit feature lists)
echo "WARNING: feature extraction is heuristic, not exhaustive"
```

**Failure mode this catches:** the Scribe invented a
feature the tool doesn't have. The "no fabrication"
constraint is violated.

**Manual review is the discipline** — the chief reads the
brief + the draft and verifies alignment.

## D5. Banned-phrase re-grep ran

**Verification:** the Scribe's draft contains no banned
phrases per the Scribe's persona spec.

```bash
banned="dive into|delve into|game.changer|paradigm shift|seamlessly|effortlessly|unleash the power|unlock the potential|excited to announce|thrilled to share|here's the thing|at the end of the day|in today's fast.paced|in conclusion|harness the power of|revolutionary|game changing|going to change everything|the future is here|this is revolutionary"

echo "$post" | grep -qiE "$banned" \
  && echo "FAIL: banned phrase detected in Scribe draft"
```

**Failure mode this catches:** the Scribe opened with a
corporate-fluff phrase that violates Dre's voice.

## D6. Chronological order floor

**Verification:** the Researcher's brief appears in the
file BEFORE the Scribe's draft.

```bash
brief_line=$(grep -n "^## Tool:" "$draft_file" | head -1 | cut -d: -f1)
scribe_line=$(grep -n "^### Post draft" "$draft_file" | head -1 | cut -d: -f1)

[ "$brief_line" -gt "$scribe_line" ] \
  && echo "FAIL: Scribe's draft is BEFORE the Researcher's brief (wrong order)"
```

**Failure mode this catches:** the Scribe wrote before
the Researcher's brief. The audit trail is broken.
