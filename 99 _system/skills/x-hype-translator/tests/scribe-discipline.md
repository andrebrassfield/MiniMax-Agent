# Scribe Discipline — x-hype-translator

The Scribe's hype-translation output is the load-bearing deliverable.
The eval suite verifies the 7 hard rules are honored.

## D1. Source accuracy (no fabricated features)

**Verification:** cross-reference the Scribe's draft against the
source post. The draft may not reference a capability the source
post did not announce.

```bash
# Extract capability claims from the draft
draft_claims=$(grep -oE '(can|does|will|lets you) [a-z][a-z ]+(AI|tool|feature|model)' draft.md)
# Extract capability claims from the source post
source_claims=$(grep -oE '(can|does|will|lets you) [a-z][a-z ]+(AI|tool|feature|model)' source-url-fetched.txt)
# Every draft claim should appear in the source claims (or be a paraphrase of one)
echo "$draft_claims" | while read claim; do
  echo "$source_claims" | grep -qF "$claim" || echo "WARN: $claim may be fabricated"
done
```

**Failure mode this catches:** the Scribe invented a feature
(capacity hallucination) instead of translating the actual
capability.

## D2. Audience specificity (not "any business")

**Verification:** the draft must name a specific audience.

```bash
# Generic audiences to flag
generic_patterns="any business|developers|AI researchers|everyone|businesses in general"
if grep -qiE "$generic_patterns" draft.md; then
  echo "FAIL: draft uses a generic audience"
fi
# The audience should match one of the persona-anchored list
persona_anchors="roofer|plumber|HVAC tech|sales rep|marketing manager|small e-com|Shopify store"
grep -qiE "$persona_anchors" draft.md || echo "WARN: audience may not be persona-anchored"
```

**Failure mode this catches:** the Scribe wrote for "developers" or
"any business" — the persona's hard ban.

## D3. Dollar math grounded

**Verification:** the draft's `Cost` field has a real number or
`unclear`.

```bash
# Extract the Cost line
cost_line=$(grep -A1 "^### Cost" draft.md | tail -1)
# Should match a dollar figure or the literal "unclear"
echo "$cost_line" | grep -qE '^\$[0-9]+/month' && echo "PASS" || \
  echo "$cost_line" | grep -qE 'unclear' && echo "PASS (unclear flagged)" || \
  echo "FAIL: cost is not a real number or unclear"
```

**Failure mode this catches:** the Scribe invented a $/month cost
or left the field blank.

## D4. Time math grounded

**Verification:** the draft's `Time saved` field has a real number
or `unclear`.

```bash
time_line=$(grep -A1 "^### Time saved" draft.md | tail -1)
echo "$time_line" | grep -qE '[0-9]+ hours?/week' && echo "PASS" || \
  echo "$time_line" | grep -qE 'unclear' && echo "PASS (unclear flagged)" || \
  echo "FAIL: time saved is not a real number or unclear"
```

**Failure mode this catches:** the Scribe invented an hours/week
saving or left the field blank.

## D5. 4-step implementation is concrete

**Verification:** the 4-step implementation has specific tools,
specific order, and a time window.

```bash
# Count the 4 steps
step_count=$(grep -cE "^[0-9]+\\. " draft.md | head -1)
test "$step_count" -ge 4 || echo "FAIL: <4 steps"
# Each step should mention a tool name or specific action
for n in 1 2 3 4; do
  step=$(grep -E "^$n\\. " draft.md)
  # Each step should have ≥5 words and a verb
  words=$(echo "$step" | wc -w)
  test "$words" -ge 5 || echo "WARN: step $n is too short"
done
```

**Failure mode this catches:** the Scribe wrote "use AI" instead of
"install Zapier, connect to Shopify, set up the 3-line Zap, test
with one product."

## D6. Voice match (Pillar 6)

**Verification:** the draft starts with the Pillar 6 voice pattern
(contrarian "Who cares" or similar) and uses staccato periods.

```bash
draft=$(grep -A20 "^### Post draft" draft.md | head -10)
# First 50 chars
first_50=$(echo "$draft" | head -1 | cut -c1-50)
# Should NOT start with "I'm excited" or "Dive into" (banned)
echo "$first_50" | grep -qiE "(dive into|excited to|game-changer|revolutionary)" && echo "FAIL: banned opener"
# Staccato: multiple sentences ending in period
period_count=$(echo "$draft" | grep -oE "\\." | wc -l)
test "$period_count" -ge 3 || echo "WARN: draft may not be staccato"
```

**Failure mode this catches:** the Scribe's draft is too academic
or doesn't match the Pillar 6 voice.

## D7. Banned-phrase re-grep ran

**Verification:** the draft contains no banned phrases (per the
Scribe's persona spec).

```bash
banned_patterns="dive into|delve into|game.changer|paradigm shift|seamlessly|effortlessly|unleash the power|unlock the potential"
if grep -qiE "$banned_patterns" draft.md; then
  echo "FAIL: banned phrase detected"
fi
```

**Failure mode this catches:** the Scribe didn't re-grep before
returning. Per the Scribe's persona spec, the re-grep is mandatory.
