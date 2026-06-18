# Discipline — x-value-bomb-dropper

The 8-floor quality check the Scribe's draft must pass. The
eval suite verifies each floor.

## D1. Zero-sales-pitch floor (the load-bearing element)

**Verification:** the draft contains NONE of the 11 banned
CTA phrases.

```bash
zero_sales="DM me|book a call|link in bio|my agency|I help companies|let's chat offline|reach out|consulting|services|if you need help|happy to walk you through|happy to chat|reach out|let me know if you want"

if echo "$draft_text" | grep -qiE "$zero_sales"; then
  echo "FAIL: zero-sales-pitch floor violated"
  # Print which phrase matched
  echo "$draft_text" | grep -oiE "($zero_sales)" | head -3
fi
```

**Failure mode this catches:** the Scribe pads the reply with
a sales CTA. The reply becomes a pitch, not a value bomb. The
whole engine collapses.

## D2. Banned-phrases floor (per Scribe's persona spec)

**Verification:** the draft contains no banned phrases.

```bash
banned="dive into|delve into|game.changer|paradigm shift|seamlessly|effortlessly|unleash the power|unlock the potential|excited to announce|thrilled to share|here's the thing|at the end of the day|in today's fast.paced|in conclusion|harness the power of"
echo "$draft_text" | grep -qiE "$banned" && echo "FAIL: banned phrase detected"
```

**Failure mode this catches:** the Scribe used a corporate
fluff phrase that violates Dre's voice.

## D3. Specific 3-step floor

**Verification:** all 3 steps name specific tools, specific
actions, and specific outcomes.

```bash
# Extract the 3 steps (after the stack naming sentence)
# For single-tweet: split on periods, look for 3 sentences
# For thread: tweet 1/, 2/, 3/

# Each step must mention a tool name
tools="Vapi|ServiceTitan|Shopify|Zapier|Airtable|Make|n8n|Postgres|Cloudflare|Resend|GPT|Claude|Notion|Slack|Linear|Fathom|Otter|Calendar|Gmail|Twilio|HubSpot|Salesforce|Stripe|QuickBooks|Sheets|Excel|Trello|Asana"

# Count tool mentions
tool_count=$(echo "$draft_text" | grep -oiE "$tools" | wc -l)
test "$tool_count" -ge 3 || echo "FAIL: less than 3 tool mentions across the steps"

# No "vague step" patterns
vague_step="Step [0-9]+:[ ]+(learn|try|figure|set up|integrate|find|explore)"
echo "$draft_text" | grep -qiE "$vague_step" && echo "FAIL: vague step detected"
```

**Failure mode this catches:** the Scribe's 3 steps are
vague filler instead of specific actions.

## D4. Unit-economics floor

**Verification:** the reply ends with a concrete number
(cost, time, payback period).

```bash
# Must contain a dollar amount, percentage, or time number
unit_econ="\\\$[0-9]+|[0-9]+%|payback in [0-9]+|saves? [0-9]+|per call|per week|per month|per hour|cost:|replaces? .* \\\$[0-9]+|[0-9]+x cheaper|[0-9]+ hours"
echo "$draft_text" | grep -qiE "$unit_econ" || echo "FAIL: no unit-economics line"
```

**Failure mode this catches:** the reply ends with a generic
"this will help" instead of a concrete number.

## D5. Stack-naming floor (the load-bearing opener)

**Verification:** the first sentence names a specific stack
(multiple named tools, not "use a tool").

```bash
first_sentence=$(echo "$draft_text" | head -1 | cut -d. -f1)
tool_count=$(echo "$first_sentence" | grep -oiE "$tools" | wc -l)
test "$tool_count" -ge 1 || echo "FAIL: first sentence doesn't name a tool"
```

**Failure mode this catches:** the reply opens with "Use a
tool" / "Find the right platform" / "AI can help" — vague
filler instead of a specific stack.

## D6. Character count discipline

**Verification:** the draft is 200-280 chars (single-tweet)
or 600-840 chars (thread, 3 tweets).

```bash
char_count=${#draft_text}
if echo "$draft_text" | grep -qE "🧵"; then
  # Thread format
  test "$char_count" -gt 840 && echo "FAIL: thread is $char_count chars (>840)"
  test "$char_count" -lt 600 && echo "WARN: thread is $char_count chars (<600, may be too short)"
else
  # Single-tweet format
  test "$char_count" -gt 280 && echo "FAIL: single-tweet is $char_count chars (>280)"
  test "$char_count" -lt 200 && echo "WARN: single-tweet is $char_count chars (<200, may be too short)"
fi
```

**Failure mode this catches:** the Scribe's draft is over the
format cap (would be truncated on x.com) or so short it
loses substance.

## D7. Format-choice floor

**Verification:** the Scribe picked the right format
(single-tweet for narrow Q, 🧵 for Q needing breathing room).

```bash
# Heuristic: if the source Q is < 100 chars, single-tweet
# is usually enough. If > 200 chars, thread is usually right.
source_q_len=${#source_post_text}

if [ "$source_q_len" -lt 100 ] && echo "$draft_text" | grep -qE "🧵"; then
  echo "WARN: narrow source Q drafted as thread (may be over-formatting)"
fi
```

**Failure mode this catches:** the Scribe over-formats a
narrow Q as a thread, or under-formats a complex Q as a
single-tweet.

## D8. Peer-voice floor (no "I will" / "we will" / "let's" openers)

**Verification:** the draft's first sentence does not start
with "I will", "we will", "let's", or other coach-voice
openers.

```bash
coach="^(I will|we will|let's|Let me|Here's what I would do|You should[^.]+\\.|You need to[^.]+\\.)"
echo "$first_sentence" | grep -qiE "$coach" && echo "FAIL: peer voice violated"
```

**Failure mode this catches:** the Scribe writes in consultant
voice ("I'll show you...", "Let me walk you through...").
The reply loses the peer-to-peer tone.
