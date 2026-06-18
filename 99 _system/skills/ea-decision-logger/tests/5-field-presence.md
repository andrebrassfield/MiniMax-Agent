# 5-Field Presence — ea-decision-logger

The 5-field sanity check. The eval suite verifies each
decision file has all 5 required fields.

## F1. All 5 required sections are present

```bash
decision_file="02 Notes/decisions/2026-06-16-gepa-pivot.md"

for section in \
  "^## Decision$" \
  "^## Rationale$" \
  "^## Alternatives considered$" \
  "^## Expected impact$" \
  "^## What would change my mind$"; do
  grep -qE "$section" "$decision_file" || echo "FAIL: section missing: $section"
done
```

**Failure mode this catches:** a section is missing
entirely. The decision is structurally incomplete.

## F2. Decision is one sentence, past tense, definitive

```bash
# Extract the Decision section
decision=$(awk '/^## Decision$/,/^## /' "$decision_file" | tail -n +2 | head -1)

# Must be one sentence (count periods)
period_count=$(echo "$decision" | grep -oE "\\." | wc -l | tr -d ' ')
[ "$period_count" -ne 1 ] && echo "WARN: Decision has $period_count periods (should be 1 sentence)"

# Must be past tense / definitive (no "should", "could",
# "consider", "let's try")
if echo "$decision" | grep -qiE "(should|could|consider|let's try|might|may)"; then
  echo "FAIL: Decision is not definitive (contains modal verbs)"
fi
```

**Failure mode this catches:** the Decision section is
vague ("we should consider X") instead of definitive
("we are using X for Y").

## F3. Rationale cites evidence

```bash
rationale=$(awk '/^## Rationale$/,/^## /' "$decision_file" | tail -n +2)

# Must reference at least one evidence source (a path, a
# brief, a research citation)
if ! echo "$rationale" | grep -qE "(03 Projects/|00 Inbox/|04 Resources/|report|brief|article)"; then
  echo "FAIL: Rationale has no evidence citation"
fi
```

**Failure mode this catches:** the Rationale is a
feature description, not a decision-shaped reasoning
("X has the following properties" not "we picked X
because [evidence]").

## F4. Alternatives are 2-5 with why-rejected

```bash
alt_section=$(awk '/^## Alternatives considered$/,/^## /' "$decision_file")

# Count alternatives
alt_count=$(echo "$alt_section" | grep -cE "^\\- \\*\\*")
[ "$alt_count" -lt 2 ] && echo "FAIL: only $alt_count alternatives (need ≥2)"
[ "$alt_count" -gt 5 ] && echo "WARN: $alt_count alternatives (5+ is padding)"

# Each alternative should have a why-rejected (text after the dash)
echo "$alt_section" | grep -E "^\\- \\*\\*" | while read line; do
  echo "$line" | grep -qE " — " || echo "WARN: alternative without why-rejected: $line"
done
```

**Failure mode this catches:** the alternatives list is
under-populated (<2) or over-padded (5+).

## F5. Expected impact is concrete

```bash
impact=$(awk '/^## Expected impact$/,/^## /' "$decision_file" | tail -n +2)

# Must name a concrete effect (a skill, cron, memory,
# workflow, failure mode)
if ! echo "$impact" | grep -qiE "(skill|cron|memory|workflow|failure|enable|prevent|change)"; then
  echo "WARN: Expected impact is vague (no concrete effect named)"
fi
```

**Failure mode this catches:** the Expected impact is
abstract ("this will help us") instead of concrete
("`ea-skill-evolution` will now consume the decision log
on every mutation proposal").

## F6. What-would-change-my-mind has specific triggers

```bash
trigger=$(awk '/^## What would change my mind$/,/^## /' "$decision_file" | tail -n +2)

# Must have at least one specific trigger (a number, a
# benchmark, a scale threshold, a regulatory reference)
if ! echo "$trigger" | grep -qE "[0-9]+|benchmark|threshold|regulation|EU AI Act|measure|score|metric"; then
  echo "FAIL: What-would-change-my-mind has no specific trigger (must be a measurement, benchmark, or scale threshold)"
fi

# Must NOT be vague ("if I learn more", "if Andre changes
# his mind")
if echo "$trigger" | grep -qiE "(if I learn more|if I learn|if Andre changes|if we change)"; then
  echo "FAIL: What-would-change-my-mind is vague (circular or non-specific)"
fi
```

**Failure mode this catches:** the trigger is vague or
circular. "If I learn more" is not a trigger; a specific
measurement is.

## F7. Optional fields present in YAML frontmatter

```bash
yaml=$(awk '/^---$/,/^---$/' "$decision_file" | head -n -1)

for field in "date:" "type:" "status:" "decider:" "reversibility:" "conversation:"; do
  echo "$yaml" | grep -qE "^$field" || echo "WARN: optional field missing: $field"
done
```

**Failure mode this catches:** the optional fields
(date, type, status, decider, reversibility,
conversation) are missing. The decision is metadata-
poor.

## Cross-reference

- `references/5-field-schema.md` — full field definitions
- `references/procedure.md` — the 5-step procedure
- `references/file-template.md` — the file template
- `references/cross-link-patterns.md` — how to link to
  related surfaces
- `tests/audit-discipline.md` — no-partial, append-
  only, Mavis-territory checks
