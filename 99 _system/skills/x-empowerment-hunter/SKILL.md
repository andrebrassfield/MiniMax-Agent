---
name: x-empowerment-hunter
description: |
  Hunt for real humans expressing AI anxiety on X, extract their posts,
  dispatch the Scribe to draft an "Aggressive Empathy" reply
  (acknowledge the fear, pivot to a tactical AI play). Output to
  `03 Projects/X-Content-Engine/drafts/empowerment-replies-YYYY-MM-DD.md`
  (one rolling file per day, all targets aggregated). Uses mavis browser
  tool against the user's real Chrome. Triggers: "empowerment hunt",
  "find people worried about AI", "draft Pillar 5 replies", "find AI
  anxiety posts", or specifies a pain-point query. HARD CONSTRAINT:
  read-only. Never click reply/post. Manual publish only. Auto-invoke
  when Andre says "empowerment hunt" or names an AI-anxiety pain
  point. Do NOT use for AI influencer replies (use x-engagement-hunter),
  the user's own posts, mass-reply workflows (single-target by design),
  or non-X platforms.
---

# x-empowerment-hunter

The supply pipeline for Pillar 5 (The Leverage Play / Job Defense).
The audience for the reply is the anxious employee, not the broader
X audience. The reply's job is to convert a "I'm scared" post into
a "I have a tactical move" mindset — without being preachy or
condescending.

## Intent

- Take a pain-point query from Andre ("worried about AI", "AI
  taking jobs", "replaced by ChatGPT", etc.)
- Search X for real humans expressing that anxiety
- Filter out counter-messaging and AI-hype accounts
- Dispatch the Scribe once per source post with a complete task spec
- The Scribe drafts a 180-280 char reply in Pillar 5 voice with the
  3-beat empathy-pivot structure (acknowledge → reframe → tactical
  play)
- Append to the rolling replies file

The model decides *which* source posts to target, *which* tactical
play to map the fear to, and *how* to thread the empathy beat. The
Scribe's task spec (the load-bearing contract) lives in
`references/scribe-task-spec.md`. The 3-beat empathy-pivot template
lives in `references/empathy-pivot-template.md`. Safety halts and
Scribe discipline live in `tests/`.

## When to run

**Triggers:**
- "empowerment hunt" / "find people worried about AI"
- "draft Pillar 5 replies" / "leverage play replies"
- "find posts about AI taking jobs" / "find AI anxiety posts"
- "reply to people worried about replacement"

**Do NOT run for:**
- AI influencer / pundit replies (use `x-engagement-hunter`)
- The user's own posts
- Mass-reply workflows (single-target by design)
- Non-X platforms

## Inputs

| Input | Default | Required |
|---|---|---|
| Pain-point query | — | **yes** |
| Search tab | `Latest` (f=live) | no — `Top` for established conversations |
| Capture depth | top 5 posts | no — 1, 5, 10 |
| Engagement floor | 100 likes (low — anxiety posts often have low reach) | no |
| Destination | `03 Projects/X-Content-Engine/drafts/` | no |
| File naming | `empowerment-replies-YYYY-MM-DD.md` (rolling per day) | no |

**Pain-point query patterns** (operator can override):
"worried about AI", "AI taking jobs", "replaced by ChatGPT",
"AI will take my job", "company replaced with AI", "my job AI",
"AI made me redundant", etc.

## Output contract

A markdown file at the destination path with one section per source
post containing:
- Source author + URL + quoted post excerpt
- The draft reply (raw, copy-pasteable)
- Character count
- "Why this reply" rationale (the empathy + tactical pivot)
- "Notes for Andre" (any specifics to verify)
- Unchecked approval box

The chief spawns the Scribe **once per source post** (not in
batch) so each reply's task spec is tight. Report back: file
path, target count, strongest reply candidate, any halts.

## Resolver

Auto-invoke when:
- Andre names an AI-anxiety pain point
- "empowerment hunt" or "draft Pillar 5 replies"
- The Scribe is mid-draft on a Pillar 5 post and needs fresh source material

Do NOT auto-invoke for:
- AI influencer replies (different skill)
- The user's own posts
- Mass-reply workflows

## The load-bearing constraint

**NEVER click the reply button on x.com. EVER.** The skill is
read-only. Drafts go to a file. The operator copy/pastes the draft
into x.com manually after approval.

This is non-negotiable. The skill explicitly forbids: clicking
reply, clicking quote-reply, typing into any reply textarea,
submitting a reply, following the source author.

## The 3-beat empathy pivot (the load-bearing pattern)

Every Aggressive Empathy reply follows this 3-beat structure (full
template in `references/empathy-pivot-template.md`):

1. **Beat 1 — Acknowledge the fear** (1 sentence, 30-50 chars). Mirror the person's actual concern. "I hear you on this."
2. **Beat 2 — Reframe the threat** (1 sentence, 50-90 chars). The threat isn't the AI; it's the coworker who's already using it. Or: the threat isn't the tool; it's the workflow that hasn't been touched.
3. **Beat 3 — Tactical play** (2-3 sentences, 100-150 chars). Specific tool + specific task + specific time window. "Open X. Do Y. Walk into Z."

Total: 180-290 chars. Hard cap 280.

The Scribe fills in this template with source-post-specific details,
not a copy of the template. Different anxieties need different
reframes and different tactical plays.

## Hard rules (the discipline)

1. **Acknowledge the fear first.** The first sentence mirrors the person's actual concern. Don't skip it.
2. **NEVER argue with the fear.** Don't say "you shouldn't worry" or "AI isn't actually going to take your job."
3. **NEVER preach.** No "you should learn AI" / "you need to adapt" / "the future belongs to those who..." The reader knows.
4. **Specific tactical play (the load-bearing element).** Not "learn AI tools." Not "stay ahead." Specific: "Open ChatGPT. Paste in your last 4 weekly status reports. Ask it to write the 5th one. Walk into Monday with 90 minutes pre-done."
5. **No "I will" / "we will" / "let's" openers.** The reply is peer-to-peer, not a corporate call-to-action.
6. **No "follow for more" / "DM me" / "link in bio" CTAs.** The value is in the tactical play, not audience growth.
7. **Banned phrases re-grep before returning.** Scribe's persona spec.
8. **No follow, no like, no repost on the source post.** Read-only.

## Cross-reference

- `references/scribe-task-spec.md` — the load-bearing contract to the Scribe
- `references/empathy-pivot-template.md` — the 3-beat structure with examples
- `references/output-format.md` — the markdown file template
- `tests/safety-halts.md` — login, rate limit, zero results, Scribe failure
- `tests/scribe-discipline.md` — empathy floor, preachy floor, banned-phrase re-grep
- `x-engagement-hunter` — sibling skill for AI influencer replies (Pillar 6 / Pillar 2)
- `x-hype-translator` — sibling skill for outbound AI-tool posts (Pillar 5 + 6 broadcast)
- `x-niche-scraper` — for the wider market scan
- The Content Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — consumer of the task spec
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`) — voice source (Pillar 5)
- `team-config.md` — the dispatch protocol
