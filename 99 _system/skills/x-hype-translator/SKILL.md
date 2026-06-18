---
name: x-hype-translator
description: |
  Hunt for newly released AI tools/models/features on X, extract the raw
  capability from the top source posts, then dispatch the Content Scribe
  to draft a "Hype Translation" post in @DreTheSalesGuy's voice — one
  that ignores the generic hype and maps the new tool to a specific
  boring practical SMB or employee use case. Output to
  `03 Projects/X-Content-Engine/drafts/hype-translations-<tool-slug>-YYYY-MM-DD-HHMM.md`.
  Speed is the brand: tool drops at 9am, tactical breakdown posted by
  noon. Triggers: "hype translate", "what's new in AI", "translate this
  tool", "break down this launch", "practical breakdown of [tool]".
  Auto-invoke when the operator says a tool name + "hype translate."
  Do NOT use for tools older than 7 days (settled — use x-niche-scraper),
  non-AI tooling, the user's own posts, or multi-tool batches (single-
  tool by design).
---

# x-hype-translator

The supply pipeline for Pillar 6 (Hype Translator). The chief (Mavis)
extracts the raw capability from X; the Scribe drafts the post. Speed
matters: a tool drops at 9am, the tactical breakdown should be in
the drafts folder by noon.

## Intent

- Take a tool/model name from Andre
- Search X for the most recent high-engagement posts about the launch
- Extract the raw capability (what it does, in one sentence) from the top 1-3 posts
- Dispatch the Scribe with a complete task spec (source + audience + rules)
- The Scribe produces a 180-260 char post in Pillar 6 voice + 4-step implementation + $/month cost + hours/week saved
- Append to the drafts ledger

The model decides *which* source posts to anchor on, *which* boring
audience to pick, and *how* to translate the capability without
inventing features. The Scribe's task spec (the load-bearing contract)
lives in `references/scribe-task-spec.md`. The data schema and
query-generation rules live in `references/`. Safety halts and Scribe
discipline live in `tests/`.

## When to run

**Triggers:**
- "hype translate [tool name]" / "hype-translate [tool]"
- "what's new in AI" / "what dropped this week"
- "break down this launch" / "practical breakdown of [tool name]"
- "translate this drop" / "translate this tool"

**Do NOT run for:**
- Tools older than 7 days (use `x-niche-scraper` — settled tools)
- Non-AI tooling (the persona only translates AI capability)
- Andre's own posts (no translation needed)
- Multi-tool batches (single-tool by design — call once per tool)

## Inputs

| Input | Default | Required |
|---|---|---|
| Tool / model name | — | **yes** |
| Launch date filter | today | no |
| Search queries | auto-generated from tool name | no — operator can override |
| Search tab | `Latest` | no — `Top` for established tools |
| Capture depth | top 5 posts | no |
| Engagement floor | 500 views (low — fresh drops may not have rolled up) | no |
| Destination | `03 Projects/X-Content-Engine/drafts/` | no |
| File naming | `hype-translations-<tool-slug>-YYYY-MM-DD-HHMM.md` | no |

Auto-generated queries (in order): `<tool> just released`, `<tool>
launch`, `<tool> shipped/dropped`. If the first returns no results,
try the next. Full rules in `references/query-generation.md`.

## Output contract

A markdown file at the destination path with:
- Header (tool name, queries used, freshness filter, timestamp)
- The raw capability extraction (per-post summary with author + URL + engagement)
- The Scribe's draft (per `references/output-format.md`)
- A "Practical use case" section (the boring use case mapped)
- An unchecked approval box (Andre reviews before posting)

Report back: file path, top source post found, Scribe's draft
headline, speed-to-tactical verdict (ready to post now, or needs
human pass?).

## Resolver

Auto-invoke when:
- Andre names a tool + says "hype translate" / "translate" / "break down"
- A "what dropped this week" / "what's new in AI" request needs a specific tool's tactical breakdown
- The Scribe is mid-draft and needs fresh source material

Do NOT auto-invoke for:
- Settled tools (older than 7 days — use `x-niche-scraper`)
- The user's own posts
- Non-AI tooling (wrong pillar)
- Multi-tool batches

## Hard rules

1. **Source accuracy is the load-bearing constraint.** The Scribe may not invent a feature the source post didn't announce. The capability is a reframe, not an addition. If the source is vague, the draft flags the gap.
2. **Audience specificity required.** The Scribe's draft must name a specific boring audience (a roofer, a plumber, a sales rep, a marketing manager at a 12-person co, a small e-com store). NOT "any business can use this" — that's a halt.
3. **Dollar + time math grounded.** The Scribe's $/month cost and hours/week saved must be grounded in a real number, or marked `unclear` for Andre to fill. No invented numbers.
4. **Speed to tactical.** If the tool dropped today, the brief should be in the drafts folder within 60 minutes. The Scribe's draft should be ready to post (after Andre's approval) without further iteration.
5. **No auto-publish.** The draft is a proposal. Andre reviews the Scribe's output, decides approve/reject/revise.
6. **No credential entry.** X login prompt → halt.

## Cross-reference

- `references/scribe-task-spec.md` — the load-bearing contract passed to the Scribe
- `references/data-schema.md` — the raw capability extraction fields
- `references/query-generation.md` — auto-generated query patterns
- `references/output-format.md` — the markdown file template
- `tests/safety-halts.md` — login, rate limit, zero results, Scribe spawn failure
- `tests/scribe-discipline.md` — source accuracy, audience specificity, dollar/time math
- `x-niche-scraper` — for settled tools (older than 7 days)
- `x-bookmark-parser` — for Andre's personal saves
- The Content Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — consumer of the task spec
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`) — voice source (Pillar 6)
- `team-config.md` — the dispatch protocol for spawning the Scribe
