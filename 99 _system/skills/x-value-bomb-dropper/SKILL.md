---
name: x-value-bomb-dropper
description: |
  Search X for high-intent operational questions from SMB owners / knowledge
  workers ("how do I automate lead intake", "best way to sync Shopify
  inventory"), extract one specific question, dispatch the Scribe to draft a
  pure-value 3-step technical reply that solves the exact problem. Zero sales
  pitch. Architecture given away for free. Output to
  `03 Projects/X-Content-Engine/drafts/value-bombs-YYYY-MM-DD.md`. Pillar 2
  (The Trades) + Pillar 4 (Build Logs) source pipeline. HARD CONSTRAINT:
  Read-only. Never click reply/post. Manual publish only. No CTAs. No "DM me."
  No "book a call." The answer IS the value. Triggers: "value bomb", "drop a
  value bomb", "free architecture", "answer a question", "free technical reply",
  "Pillar 4 reply", "Pillar 2 reply". Sibling to x-empowerment-hunter
  (anxiety) + x-engagement-hunter (large accounts). Single-target by design.
---

# x-value-bomb-dropper

The highest-trust reply in the engine. The reply's value is
the answer itself — a 3-step technical solution to the
operator's exact problem, given away for free, in public,
on the timeline. The trust is the moat.

## When to run

**Triggers:**
- "value bomb" / "drop a value bomb" / "free architecture"
- "answer a question" / "answer an operational question"
- "free technical reply" / "give away the architecture"
- "draft a value-bomb reply" / "Pillar 4 reply" / "Pillar 2 reply"

**Do NOT run for:**
- AI influencer / pundit replies (→ `x-engagement-hunter`)
- Anxious employee posts (→ `x-empowerment-hunter`)
- The user's own posts
- Mass-reply workflows (single-target by design; 1 source post →
  1 draft per run)
- Posts that are not actually asking an operational question
  (rhetorical "what do you think about AI" → `x-engagement-hunter`)
- Non-X platforms

Full trigger phrases + anti-pattern query list in
`references/triggers.md`.

## Inputs

| Input | Default | Required |
|---|---|---|
| Operational question query | — | **yes** |
| Search tab | `Latest` (f=live) | no — `Top` for established Qs |
| Capture depth | top 5 posts | no — 1, 5, 10 |
| Engagement floor | 5 likes (low — Q posts have low reach) | no |
| Destination | `03 Projects/X-Content-Engine/drafts/` | no |
| File naming | `value-bombs-YYYY-MM-DD.md` (rolling per day) | no |

## The 3-step format (the load-bearing pattern)

| Beat | Purpose | Length |
|---|---|---|
| 1. Name the stack | "Use Vapi + Google Calendar + Zapier." | 1 sentence, 40-70 chars |
| 2. First concrete step | Specific action this week. | 1-2 sentences, 80-130 chars |
| 3. Second step + unit economics | Follow-on action + cost/payback number. | 1-2 sentences, 80-130 chars |

**Total:** 200-330 chars. **Hard cap 280 single-tweet, ~840
char 🧵 thread (3 × 280).** Scribe picks format based on
question complexity. Full template + example skeletons +
what-makes-a-strong-stack in `references/3-step-format.md`.

## The zero-sales-pitch constraint (the load-bearing rule)

**The reply contains the answer. The reply contains ONLY
the answer.** No sales CTA. No "DM me." No "book a call."
No "link in bio." No "I run an agency that does this." No
"happy to chat offline."

The architecture is given away for free, in public, on the
timeline. The trust is the moat. A value-bomb reply that
ends with "DM me to set this up for you" is a pitch, not
a value bomb. The whole engine collapses if the Scribe
pads with a CTA.

The Scribe's hard verification step: re-grep the reply for
`DM me`, `book a call`, `link in bio`, `my agency`, `I help
companies`, `let's chat offline`, `reach out`, `consulting`,
`services`, `if you need help`, `happy to walk you through`.
If any of those phrases appear → reply fails verification →
Scribe retries.

## The procedure (overview)

The 7-step procedure (bridge check → search URL → auth check
→ source extraction → Scribe dispatch → ledger update →
summary) lives in `references/procedure.md`. The high-level
shape:

1. Verify bridge is live (`mavis browser status`)
2. Open search URL with `f=live` (Latest)
3. Auth check + load wait + result check
4. Extract + rank source posts (pick the strongest target)
5. Dispatch Scribe (one spawn per target)
6. Update value-bombs ledger
7. Return summary

## Hard rules (the discipline)

1. **Solve the exact problem the person asked.** Not a
   related problem. Not a more interesting problem. The
   exact problem.
2. **Name the stack in the first sentence.** "Use Vapi +
   Google Calendar + Zapier." Not "use a tool."
3. **Three concrete steps.** Each is a specific action the
   person can take this week. "Learn the tool" / "figure
   out the right approach" = too vague. Replace.
4. **Give away the architecture for free.** The trust is
   the moat. Do NOT hold back details hoping to convert
   the reader into a customer.
5. **End with unit economics.** Cost per call, hours saved
   per week, payback period, dollar number.
6. **ZERO SALES PITCH** (the load-bearing rule). Re-grep
   for the 11 banned CTA phrases.
7. **Match persona voice** (Pillar 2 + 4). Staccato periods,
   lead with the punch, follow with steps, end with
   economics. No banned phrases. No emoji except 🧵 for
   thread markers.
8. **No "I will" / "we will" / "let's" openers.** Peer voice,
   not consultant voice.
9. **Single-tweet vs 🧵 thread — pick the right format.**
   Single-tweet (200-280 chars) for narrow Q. 🧵 thread
   (3 tweets, ~840 chars total) when Q needs breathing room.
10. **Banned phrases re-grep** + **zero-sales-pitch re-grep**
    before returning.
11. **Mavis territory only.** This skill dispatches the
    Scribe — both Mavis-side. No cross-team handoff.

## Hard constraint (READ THIS)

**DO NOT click the reply button on x.com. EVER.** Read-only
against the X UI. Drafts go to a file. Operator copy/pastes
manually. Same constraint as `x-empowerment-hunter` and
`x-engagement-hunter`. The skill explicitly forbids:
reply, quote-reply, typing into reply textarea, submitting
reply, following source author, liking source post, DMing
source author.

The skill is "draft a reply" — it is NOT "post a reply."

## Cross-reference

- `references/3-step-format.md` — single-tweet vs 🧵 thread,
  char targets, example skeletons
- `references/scribe-task-spec.md` — the load-bearing contract
  to the Scribe
- `references/procedure.md` — the 7-step procedure with bash
- `references/output-format.md` — the per-reply markdown
  schema
- `references/triggers.md` — trigger phrases + anti-pattern
  queries
- `tests/safety-halts.md` — 12 halt conditions + eval cases
- `tests/discipline.md` — 8 quality floors (zero-sales-pitch,
  banned phrases, char count, specific 3-step, unit economics,
  format choice, peer voice, source targeted)
- `x-empowerment-hunter` — anxiety-targeted replies (Pillar 5)
- `x-engagement-hunter` — value-add replies to large accounts
- `x-hype-translator` — outbound AI-tool posts
- `x-niche-scraper` — for the wider market scan
- `x-bookmark-parser` — for the user's own curated saves
- The Content Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`)
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`) — voice source (Pillar 2 + 4)
- `team-config.md` — dispatch protocol
