# Scribe Discipline — x-engagement-hunter

The 6-floor quality check the Scribe's draft must pass. The eval
suite verifies each floor.

## D1. Never-argue floor

**Verification:** the draft does NOT open with disagreement.

```bash
# Anti-arguer openers (must NOT contain any)
anti_arguer="I disagree|actually,|you're wrong|the real story is|that's not right|on the contrary|however,|but actually|wait,"
echo "$draft_text" | grep -qiE "^($anti_arguer)" && echo "FAIL: never-argue floor violated"
```

**Failure mode this catches:** the Scribe picks a fight with the
target's premise. The reply loses the agree-and-extend voice.

## D2. Value-add floor (the load-bearing element)

**Verification:** the draft adds a number, a tool/vendor name, a
tactical use case, or a Pillar 2/4 connection that the target
didn't already say.

```bash
# Must contain at least one value-add marker
value_add="\\\$[0-9]+|\\$[0-9]+\\.|Pillar [246]|Zapier|ChatGPT|Claude|GPT|API|n8n|Make|Notion|Fathom|Otter|Elicit|Perplexity|CRM|SDR|deal|call|invoice|missed call|trade|plumber|HVAC|Shopify|automation|workflow"
echo "$draft_text" | grep -qiE "$value_add" || echo "FAIL: no value-add detected"
```

**Failure mode this catches:** the Scribe restates the target's
point without adding anything new. The reply is a restate, not a
value-add.

## D3. Character count discipline

**Verification:** the draft is 80-280 chars (or shorter for
value-adds).

```bash
char_count=${#draft_text}
test "$char_count" -le 280 || echo "FAIL: draft is $char_count chars (>280)"
test "$char_count" -ge 20 || echo "WARN: draft is $char_count chars (very short — may be insufficient value-add)"
```

**Failure mode this catches:** the Scribe's draft is over the
280-char limit (would be truncated) or so short it's a one-liner
without substance.

## D4. No-AI-fluff floor (per Scribe's persona spec)

**Verification:** the draft contains no AI fluff openers or
banned phrases.

```bash
# AI fluff openers (must NOT start with)
ai_fluff="Great point|love this|well said|absolutely!|this is gold|so true|spot on|exactly!|nailed it"
echo "$draft_text" | grep -qiE "^($ai_fluff)" && echo "FAIL: AI fluff opener"

# Banned phrases (re-grep per Scribe's persona spec)
banned="dive into|delve into|game.changer|paradigm shift|seamlessly|effortlessly|unleash the power|unlock the potential|excited to announce|thrilled to share|here's the thing|at the end of the day|in today's fast.paced|in conclusion"
echo "$draft_text" | grep -qiE "$banned" && echo "FAIL: banned phrase detected"
```

**Failure mode this catches:** the Scribe opened with a corporate-
fluff opener that violates Dre's voice, or used a banned phrase.

## D5. No-CTAs floor

**Verification:** the draft contains no growth CTAs ("follow for
more", "DM me", "link in bio").

```bash
ctas="follow for more|DM me|link in bio|check out my|sign up for|join my"
echo "$draft_text" | grep -qiE "$ctas" && echo "FAIL: growth CTA detected"
```

**Failure mode this catches:** the Scribe turned the reply into
a personal-marketing pitch. The reply is for the target's
audience, not for Andre's follower growth.

## D6. Peer-voice floor (no "I will" / "we will" / "let's" openers)

**Verification:** the draft's first sentence does not start with
"I will", "we will", "let's", or other coach-voice openers.

```bash
coach="^(I will|we will|let's|Let me|Here's what I would do|You should[^.]+\\.|You need to[^.]+\\.)"
echo "$first_sentence" | grep -qiE "$coach" && echo "FAIL: peer voice violated"
```

**Failure mode this catches:** the Scribe writes in corporate
coach voice ("I'll show you...", "Let's talk about..."). The
reply loses the peer-to-peer tone.

## D7. Target post is in a draftable state

**Verification:** the source post is still online, not a
soft-deleted post, not from a suspended account.

```bash
# Source URL must be reachable
curl -sI "$source_url" | head -1 | grep -qE "200|303" || echo "FAIL: source URL not reachable"
```

**Failure mode this catches:** the Scribe drafts against a
target that no longer exists. The reply is wasted.
