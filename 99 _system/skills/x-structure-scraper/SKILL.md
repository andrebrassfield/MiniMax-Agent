---
name: x-structure-scraper
description: |
  Reverse-engineer a "source-of-truth" X account's most viral long-form
  threads into a Structural Blueprint. The blueprint captures the
  SKELETON (hook bait vs. switch, argument architecture, pacing,
  human markers) — not the content. Output to
  `03 Projects/X-Content-Engine/briefs/blueprints-YYYY-MM-DD.md`
  (multi-account) or `blueprint-[handle]-YYYY-MM-DD.md` (single). The
  Scribe reads the blueprint as a style-anatomy reference; the
  Humanizer uses the pacing + human-marker analysis as its
  "what does authentic look like" reference. Triggers: "scrape the
  structure of [@account]", "study [@account]'s threads", "analyze
  the rhythm of [account]", "structural blueprint of [handle]", "how
  does [account] write". Auto-invoke when Andre pins a new account
  to the source-of-truth list. Do NOT use for the user's own posts,
  bookmarks, single-tweet links, topic scouting, or live engagement.
---

# x-structure-scraper

The style-anatomy skill. Captures how a high-quality long-form X
account builds their threads — the rhythm, the hook mechanics, the
pacing, the human markers — not what they argue. The Scribe reads
the blueprint to study the moves; the Humanizer reads the pacing +
human-marker analysis to calibrate "what does authentic look like."

## Intent

- Pick a target handle (from the pinned source-of-truth list or a new one Andre approves)
- Scrape the handle's most viral long-form threads (≥3 tweets or >500 chars)
- Apply the 4 structural dimensions to each thread
- Write a blueprint file with the per-thread analysis + cross-thread synthesis
- Surface the single most-copyable move (the load-bearing answer for the Scribe)

The model decides *how* to read the thread, *what* the bait/switch is,
and *which* move is the most copyable. The deterministic layer (the
4-dimension spec, the blueprint template, the source-of-truth account
list) lives in `references/`. The discipline checks (skeleton-not-
substance, hard rules) live in `tests/`.

## When to run

**Triggers:**
- "scrape the structure of [@account]" / "study [@account]'s threads"
- "analyze the rhythm of [account]" / "how does [account] write"
- "structural blueprint of [handle]" / "build a blueprint"
- "reverse-engineer [@account]'s voice" / "anatomy of [handle]'s threads"
- "who else is good at long-form X" / "give me a model to study"

**Do NOT run for:**
- Andre's own posts or drafts (Scribe territory)
- Bookmark dumps (use `x-bookmark-parser`)
- Single-tweet links (use `x-link-reader`)
- A specific topic/niche (use `x-niche-scraper`)
- Live engagement / reply-writing (use `x-engagement-hunter`)
- Low-engagement threads (<1K views) or accounts without clear long-form style

## Inputs

| Input | Default | Required |
|---|---|---|
| Target handle | — | **yes** (or from the pinned list) |
| Thread count | top 5 | no — 3, 10, or "all in first snapshot" |
| Engagement floor | 50,000 views | no — set higher for proven-winners-only |
| Output dir | `03 Projects/X-Content-Engine/briefs/` | no |
| File naming | `blueprints-YYYY-MM-DD.md` (multi) / `blueprint-[handle]-...` (single) | no |

## Output contract

A blueprint file with:
- Header (target handles, thread count, floor, timestamp, source URLs)
- **The Single Most-Copyable Move** (1-2 sentences, at the top — the load-bearing answer)
- Per-thread analysis (4 dimensions applied to each)
- Cross-thread synthesis (what unifies, what varies)
- Notes for the Scribe (moves to try, moves to avoid)

The full template is in `references/blueprint-template.md`.

## Resolver

Auto-invoke when:
- Andre pins a new account to the source-of-truth list (e.g., "scrape
  the structure of @new_account")
- The Scribe is starting a new voice experimentation cycle and needs
  fresh style-anatomy data
- The persona is being updated and the source-of-truth list is being
  refreshed

Do NOT auto-invoke for:
- Topic-based searches (use `x-niche-scraper`)
- Single URL analysis (use `x-link-reader`)
- "How is @account doing" performance questions (use `x-analytics-tracker`)

## The "Skeleton, Not Substance" discipline (load-bearing)

This skill is NOT a content-summarization skill. The most common
failure mode is the analyst drifting into "this thread argues that
X is the future of Y" — that's a content summary, not a structural
blueprint. The output should make a writer go "ah, I see how they
built the rhythm" — not "ah, I learned something new about the topic."

Discipline checks (all must be YES before returning):
- Does the file contain a paraphrased CONTENT line from the threads? If yes, delete it.
- Does the file contain ≥2 verbatim HOOK examples? If no, add them.
- Does the file contain a "Single Most-Copyable Move"? If no, add it.
- Does the file name correctly reflect single vs. multi-account?

The eval suite in `tests/discipline-checks.md` enforces these on
every run.

## Hard rules

1. **Read-only.** No likes, no reposts, no follows, no replies. Structural analysis, not engagement.
2. **No credential entry.** If login prompt, halt.
3. **No fabrication.** If a thread is missing a structural dimension (e.g., no human marker), say "0 human markers" — don't invent one.
4. **Structure-only output.** Don't summarize the thread's argument. The blueprint is how the thread is BUILT, not what it ARGUES.
5. **Verbatim over paraphrase.** Hooks, switches, transition phrasing, human markers — capture verbatim.
6. **No auto-publish.** The blueprint is a reference file. The Scribe reads it; doesn't copy the account's content.

## Cross-reference

- `references/structural-dimensions.md` — the 4 dimensions with full spec
- `references/blueprint-template.md` — the markdown file template
- `references/account-list.md` — the pinned source-of-truth accounts
- `tests/discipline-checks.md` — the 4 Skeleton-Not-Substance questions
- `tests/safety-halts.md` — login, rate limit, account suspended
- `tests/edge-cases.md` — threads below floor, all-lecture-mode, etc.
- `x-niche-scraper` — topic-based search
- `x-bookmark-parser` — Andre's personal saves
- `x-link-reader` — single URL
- The Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — primary consumer
- The Humanizer (`99 _system/skills/scribe-humanizer/SKILL.md`) — secondary consumer
