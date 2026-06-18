# Scribe Task Spec — x-hype-translator

The contract passed to the Content Scribe. This is the load-bearing
artifact — the Scribe's draft quality depends on the spec being
complete. The skill copies this block verbatim into the dispatch.

## The task spec (verbatim, copy this block)

```
You are drafting a Hype Translation post in @DreTheSalesGuy's voice. The voice file is at `03 Projects/X-Content-Engine/agents/persona.md`. Read it before drafting.

**The new tool / capability:**
<tool name>: <one-sentence description from the top source post>
Source post: <source-url> by <@handle>

**The Hype Translation brief:**

Take the tool announcement above. Your job is NOT to hype it. Your job is to map it to a boring, practical, money-making use case for an SMB owner or everyday employee.

**The Hype Translation rules (HARD):**

1. **Ignore the generic hype.** No "this is going to change everything" / "the future is here" / "this is revolutionary." Those phrases are banned by your Scribe spec already.
2. **Pick a specific boring audience.** A roofer, a plumber, a sales rep, a marketing manager at a 12-person company, a small e-com store doing $40K/month on Shopify. NOT "developers" or "AI researchers" — those are not Andre's audience.
3. **Show the exact 4-step implementation.** What does the SMB owner do, in what order, with what tools, in what time window? Concrete steps. Not "use AI to be more productive."
4. **Show the cost in $/month.** If the tool is free, say so. If it's $20/month, say so. The dollar figure is the load-bearing element.
5. **Show the time-saved in hours/week.** This is the second load-bearing element. "Saves 5 hours/week" or "saves 30 minutes per customer interaction" — pick a specific number.
6. **Match the voice per persona.md.** Pillar 6 voice: lead with a contrarian "Who cares. Here's what a [boring audience] can do with it." Staccato periods. No emoji except 🧵 for thread markers. 180-260 chars target, 280 hard cap.
7. **No AI fluff phrases.** Banned list is in your Scribe spec.

**Output format (write to 03 Projects/X-Content-Engine/drafts/hype-translations-<tool-slug>-YYYY-MM-DD-HHMM.md):**

## Hype Translation: <tool name> — YYYY-MM-DD HH:MM CT

**Source announcement:** <source-url>
**Tool capability (one line):** <what it does>
**Target audience (one line):** <the boring audience you're mapping to>

### Post draft

<the actual post text, 180-260 chars, voice-matched>

### Character count

XX / 280

### 4-step implementation

1. <step 1>
2. <step 2>
3. <step 3>
4. <step 4>

### Cost

$<X>/month

### Time saved

X hours/week

### Why this angle

[2-3 sentences: why this specific boring audience was the right pick, what tactical detail makes the 4-step implementation actionable, how the dollar + time math is grounded]

### Notes for Andre

[Any specifics to verify — e.g., "this assumes the tool is free during preview; check pricing before posting" or "the audience (roofer) is a guess based on a 2026 trend; adjust if you have a different one in mind."]

### Approval

- [ ] approved → post
- [ ] rejected (reason: ________)
- [ ] needs revision (notes: ________)
```

## The Scribe's contract (recap)

The Scribe receives the source extraction + the task spec. The Scribe's job:
1. Read `03 Projects/X-Content-Engine/agents/persona.md` for voice + pillars
2. Pick the specific boring audience (one of the persona-anchored audiences)
3. Show the 4-step implementation (specific tools, specific order, specific time window)
4. Show the cost ($/month) + time saved (hours/week)
5. Draft a 180-260 char post in Pillar 6 voice
6. Re-grep for banned phrases before returning

The Scribe may not invent a feature the tool doesn't have. The
capability comes from the source post. The translation is a reframe,
not an addition.
