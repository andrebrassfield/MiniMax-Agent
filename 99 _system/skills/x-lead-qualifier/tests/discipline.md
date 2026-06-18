# Discipline — x-lead-qualifier

The 5-floor quality check the skill itself must pass.
The lead-qualifier is a verifier — it must not become
the thing it's auditing (a hype-cycle echo chamber that
drafts hard-sell DMs).

## D1. Intent classification floor

**Verification:** the Scribe's draft addresses the
detected intent type (not a different type).

```bash
# Extract the intent type from the queue entry
intent=$(awk '/intent:/{print $NF; exit}' "$queue_entry" | tr -d ' ')

# Extract the draft content
draft=$(awk '/^  - Draft/,/^  - Status/' "$queue_entry" | tail -n +2 | head -1)

# The draft should address the intent (heuristic:
# contains a technical insight for ai_automation_question,
# contains empathy for pain_point_statement, etc.)
case "$intent" in
  ai_automation_question|pain_point_statement|integration_inquiry)
    # Should contain a number or technical insight
    echo "$draft" | grep -qE "[0-9]+|\\\$[0-9]+|specific" \
      || echo "WARN: draft for $intent may lack technical insight" ;;
  job_defense_question)
    # Should contain learning/upskilling language
    echo "$draft" | grep -qiE "(learn|skill|start|where)" \
      || echo "WARN: draft for job_defense may lack learning language" ;;
  operational_distress)
    # Should contain scaling/automation language
    echo "$draft" | grep -qiE "(scale|automate|operational|efficiency)" \
      || echo "WARN: draft for operational_distress may lack scaling language" ;;
esac
```

**Failure mode this catches:** the Scribe drafted for
the wrong intent type (e.g., a `pain_point_statement`
draft for an `ai_automation_question` lead). The
audience mismatch is the failure.

## D2. No-hard-sell floor (the load-bearing element)

**Verification:** the draft contains NONE of the
hard-sell language. This is the most-load-bearing check.

```bash
hard_sell="\\bbuy\\b|\\bsign up\\b|\\bbook a call\\b|this week only|scarcity|spots? left|can't afford|10x|guaranteed|free trial|discount|coupon|promo code|limited time|act now"

if echo "$draft" | grep -qiE "$hard_sell"; then
  echo "FAIL: no-hard-sell floor violated"
  # Print which phrase matched
  echo "$draft" | grep -oiE "($hard_sell)" | head -3
fi
```

**Failure mode this catches:** the Scribe pads the DM
with a sales CTA. The lead gets a pitch, not a
qualification. The whole funnel collapses.

## D3. Voice match floor

**Verification:** the draft matches the DM-specific
voice (staccato, lead with punch, specific numbers,
conversational, no emoji default).

```bash
# Staccato check: ≥3 sentences
sentence_count=$(echo "$draft" | grep -oE "\\." | wc -l | tr -d ' ')
[ "$sentence_count" -lt 3 ] && echo "WARN: draft has $sentence_count sentences (<3)"

# Specific numbers check: ≥1 real number
echo "$draft" | grep -qE "[0-9]+|\\\$[0-9]+" \
  || echo "WARN: draft has no specific numbers"

# No emoji default (≤1 emoji)
emoji_count=$(echo "$draft" | grep -oE "[😀-🙏🎀-🎯🔥-🔟]" | wc -l | tr -d ' ')
[ "$emoji_count" -gt 1 ] && echo "WARN: draft has $emoji_count emoji (>1 is excessive)"
```

**Failure mode this catches:** the Scribe wrote in
the wrong voice (long run-on, no numbers, excessive
emoji).

## D4. 3-section structure floor

**Verification:** the draft has the 3 sections
(Acknowledge / Tip / CTA) in order.

```bash
# Heuristic: the draft should have the 3 sections
# separated by sentence boundaries
section_check=$(echo "$draft" | wc -w | tr -d ' ')
# Acknowledge (1-2 sentences) + Tip (2-3 sentences) + CTA (1 sentence)
# = 4-6 sentences, ~80-200 words
[ "$section_check" -lt 60 ] && echo "WARN: draft is $section_check words (too short for 3 sections)"
[ "$section_check" -gt 350 ] && echo "WARN: draft is $section_check words (too long for a DM)"
```

**Failure mode this catches:** the draft is missing
one of the 3 sections, or the sections are out of
order, or the draft is too long/short for a DM.

## D5. Queue-file-writable floor

**Verification:** the queue file is writable and the
Scribe's write succeeded.

```bash
queue="03 Projects/X-Content-Engine/queue/qualification-dms-$(date +%Y-%m-%d).mdl"

# Queue dir must exist
[ -d "$(dirname "$queue")" ] || { mkdir -p "$(dirname "$queue")" 2>/dev/null || echo "FAIL: queue dir not writable"; }

# Queue file must be writable
touch "$queue" 2>/dev/null || echo "FAIL: queue file not writable"
```

**Failure mode this catches:** the Scribe tried to
write to a non-existent dir or a read-only file. The
draft is lost.

## Cross-reference

- `references/filter-rules.md` — the 5 intent types
- `references/procedure.md` — the 7-step procedure
- `references/scribe-task-spec.md` — the Scribe contract
- `references/voice-discipline.md` — DM-specific voice
- `references/output-format.md` — the queue file format
- `tests/safety-halts.md` — 8 halt conditions
