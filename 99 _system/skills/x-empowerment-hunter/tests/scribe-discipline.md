# Scribe Discipline — x-empowerment-hunter

The 3-floor quality check the Scribe's draft must pass. The eval
suite verifies each floor.

## D1. Empathy floor (Beat 1 is acknowledgment)

**Verification:** the draft's first sentence acknowledges the
source post's fear (mirrors the concern, validates the feeling).

```bash
# Extract the first sentence
first_sentence=$(grep -A10 "^### Reply draft" draft.md | tail -n +2 | head -1 | cut -d. -f1)

# Empathy openers (must contain one of these)
empathy_patterns="I hear you|This is a real|You're not wrong|valid concern|makes sense|that'?s a real|legit fear|fair"
echo "$first_sentence" | grep -qiE "$empathy_patterns" || echo "FAIL: empathy floor violated"

# Anti-empathy openers (must NOT contain any of these)
anti_patterns="Don't worry|AI won't|Just learn|You need to adapt|Here's why you're wrong|I disagree|You're overreacting|It's not that bad"
echo "$first_sentence" | grep -qiE "$anti_patterns" && echo "FAIL: empathy floor violated (argues with fear)"
```

**Failure mode this catches:** the Scribe opens with a
"reassurance" or "argument" that invalidates the fear. The reply
loses the peer-to-peer tone.

## D2. Preachy floor (peer voice, not coach)

**Verification:** the draft does not read like a corporate coach
or LinkedIn influencer.

```bash
# Preachy patterns (must NOT contain any of these)
preachy="You should [^.]+\\.|You need to [^.]+\\.|The future is [^.]+\\.|Let me teach you|Here's what I would do[^.]*\\.|The key is to [^.]+\\."
grep -qE "$preachy" draft.md && echo "FAIL: preachy floor violated"
```

**Failure mode this catches:** the Scribe writes in advisory
("you should...") or coach ("the key is to...") tone. The reply
loses the peer voice.

## D3. Tactical play is specific (the load-bearing element)

**Verification:** the tactical play (Beat 3) names a specific
tool, task, and time window.

```bash
# Extract the tactical play section (the part after "reframe the threat")
tactical=$(grep -A5 "reframe\|threat isn't" draft.md | tail -3)

# Must mention a specific tool (any of: ChatGPT, GPT, Zapier, Make, n8n, Claude, Gemini, Notion AI, Fathom, Otter, etc.)
echo "$tactical" | grep -qiE "(chatgpt|gpt|zapier|make|n8n|claude|gemini|notion|fathom|otter|elicit|perplexity|consensus)" || echo "FAIL: tactical play doesn't name a specific tool"

# Must mention a specific time window (any of: today, this weekend, Friday, Monday, 30 minutes, an hour, etc.)
echo "$tactical" | grep -qiE "(today|this weekend|Friday|Monday|30 minutes|an hour|next week|this week|by end of)" || echo "FAIL: tactical play doesn't name a time window"

# Must NOT be vague ("learn AI tools", "stay ahead")
echo "$tactical" | grep -qiE "(learn AI tools|stay ahead|use AI|upskill)" && echo "FAIL: tactical play is vague"
```

**Failure mode this catches:** the Scribe's tactical play is
generic — the person reading the reply can't act on it. The reply
loses the load-bearing element.

## D4. Character count discipline

**Verification:** the draft is ≤280 chars.

```bash
draft_text=$(grep -A20 "^### Reply draft" draft.md | tail -n +2 | head -1)
char_count=${#draft_text}
test "$char_count" -le 280 || echo "FAIL: draft is $char_count chars (>280)"
```

**Failure mode this catches:** the Scribe's draft is over the
280-char limit. The post would be truncated on x.com.

## D5. Banned-phrase re-grep ran

**Verification:** the draft contains no banned phrases (per the
Scribe's persona spec).

```bash
banned="dive into|delve into|game.changer|paradigm shift|seamlessly|effortlessly|unleash the power|unlock the potential|excited to announce|thrilled to share"
grep -qiE "$banned" draft.md && echo "FAIL: banned phrase detected"
```

**Failure mode this catches:** the Scribe didn't re-grep before
returning. Per the Scribe's persona spec, the re-grep is mandatory.

## D6. Source post is targeted (not counter-messaging)

**Verification:** the source post expresses actual anxiety, not
counter-messaging ("Don't worry about AI") or AI hype.

```bash
# The source post should contain anxiety markers
anxiety_markers="worried|scared|afraid|anxious|losing my job|replaced|redundant|obsolete|lose my|fired|laid off"
echo "$source_post_text" | grep -qiE "$anxiety_markers" || echo "WARN: source post may not be actual anxiety"

# Should NOT be counter-messaging
counter="Don't worry|not as bad|overhyped|no need to panic|you'll be fine|don't be afraid"
echo "$source_post_text" | grep -qiE "$counter" && echo "WARN: source post may be counter-messaging"
```

**Failure mode this catches:** the chief dispatches the Scribe to
a counter-messaging post. The empathy pivot doesn't work on
"Don't worry about AI" — the source isn't anxious. Skip and find
a real target.

## D7. No "I will" / "we will" / "let's" openers (peer voice)

**Verification:** the draft's first sentence does not start with
"I will", "we will", or "let's".

```bash
first_sentence=$(grep -A10 "^### Reply draft" draft.md | tail -n +2 | head -1)
echo "$first_sentence" | grep -qiE "^(I will|we will|let's|Let me)" && echo "FAIL: peer voice violated"
```

**Failure mode this catches:** the Scribe writes in corporate
call-to-action voice ("I'll show you...", "Let's talk about..."). The
reply loses the peer-to-peer tone.
