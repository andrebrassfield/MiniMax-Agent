# Marker Detection — ea-commitment-tracker

The marker phrases + regex + detection logic for catching
commitments in chat. The detection rule is conservative:
only flag statements that are first-person + future-tense +
have a deliverable or a due date.

## Marker phrases (the load-bearing list)

**Strong markers (high confidence — auto-capture):**
- "I'll do X" / "I'll have X ready"
- "I will X"
- "let me X" / "let me look into that"
- "I owe you X"
- "I'll handle that" / "I'll take care of that"
- "I'll have it by <time>" / "I'll deliver by <time>"
- "I'll come back to that"
- "I should have X"
- "I need to X"
- "I'll follow up"
- "I'll check on that"

**Time markers (combine with strong markers):**
- "by EOD" / "by end of day"
- "by <day>" (Monday, Tuesday, etc.)
- "by tomorrow" / "tomorrow morning"
- "in an hour" / "in 30 minutes"
- "next session" / "next Mavis-touch"
- "this afternoon" / "this morning"
- "next week" / "next month"

**Weak markers (low confidence — review before capture):**
- "yeah I'll get to that" (vague, sharpen first)
- "at some point" (no due-by)
- "soon" (no due-by)
- "later" (no due-by)
- "I might X" (not first-person future-tense commitment)

## Marker regex (illustrative, not exhaustive)

```
\b(I('ll| will)|let me|i owe|i should|i need to|by (eod|monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|next (week|month|quarter))|in the morning|in an hour|next session|come back to|follow up|check on)\b
```

The regex is a starting point, not a complete solution. Some
phrases don't fit the regex pattern ("I promise", "I'm going
to", "I'm on it"). Manual review catches what the regex
misses.

## Detection rule (the conservative form)

The detection rule has 3 conditions, ALL must be met:

1. **First-person** — the subject is "I" (not "he", "she",
   "we", "they", "the team")
2. **Future-tense** — the verb is in the future (will, 'll,
   going to, plan to, should have)
3. **Has a deliverable or due date** — there's either a
   specific action the speaker will take OR a specific time
   they're committing to

**Pure acknowledgments are NOT commitments:**
- "I see" — not future-tense
- "Got it" — not future-tense
- "Noted" — not future-tense
- "Acknowledged" — not future-tense
- "Thanks" — not future-tense
- "Will do" (without context) — borderline; the surrounding
  message usually supplies the deliverable

**Third-party commitments are NOT Mavis commitments:**
- "Andre said he'd send the report" — Andre's commitment,
  goes in `02 Notes/commitments/andre-to-others.md`
- "He'll handle the billing" — third-party, not tracked

**One-shot operational promises are excluded:**
- "I'll run that command now" — completes in the same turn,
  no ledger entry
- "Let me check that" — if check completes in same turn,
  no ledger entry

## The detection procedure

1. **Scan the current session** for the marker phrases.
2. **Apply the 3-condition rule** (first-person + future-tense
   + deliverable/due date).
3. **For each match:** load this skill, extract the 6 fields,
   append to the JSONL ledger.
4. **Do not ask Andre to confirm** — the verbatim quote is
   the evidence. If the wording is loose, sharpen to one
   specific sentence (per EA contract behavior #2) and
   capture.

## Edge cases

**The "I'll think about it" case:** not a commitment. No
deliverable, no due date. The 3-condition rule excludes it.

**The "I'll try" case:** weak commitment. Sharpen to "I'll
do X by Y" or "I'll attempt X" with explicit deliverable
and due date. If Andre just said "I'll try", ask for the
specific deliverable and due date before capturing.

**The "let me know" case:** "let me know" is a request from
Mavis to Andre, not a commitment. "Let me look into it" IS
a commitment. The verb after "let me" is the test.

**The "by next session" case:** if Andre says "next session"
implicitly (e.g., Mavis says "I'll come back to that
tomorrow"), the due_by is `next-session` (the literal
string). The next Mavis-touch is the implicit deadline.

**The "by Friday" case:** if the chat said "by Friday", the
chief computes the next Friday 23:59:59 CT as an ISO 8601
timestamp. The chief does NOT ask Andre "which Friday?" — the
default is the next one.

## Eval cases

```bash
# Strong marker should auto-capture
input="I'll have the regulatory anchors by EOD"
echo "$input" | grep -qiE "^I('ll| will) " && echo "CAPTURE"

# Time marker should be parsed
input="I'll have it by Friday"
echo "$input" | grep -qiE "by (monday|...)" && echo "PARSE-DUE-BY"

# Pure acknowledgment should NOT capture
input="Got it"
echo "$input" | grep -qiE "^(got it|noted|i see|acknowledged|thanks)$" && echo "NOT-CAPTURE"

# Third-party commitment should NOT capture as Mavis commitment
input="Andre said he'd send the report"
echo "$input" | grep -qiE "(he|she|they) said" && echo "NOT-MAVIS-COMMITMENT"
```
