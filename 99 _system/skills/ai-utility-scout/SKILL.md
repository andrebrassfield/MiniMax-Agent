---
name: ai-utility-scout
description: |
  Scan top AI launch directories (There's An AI For That, Rundown AI, Product
  Hunt, etc.) for newly released AI tools, pick ONE specific (non-generic-
  chatbot) tool, dispatch the Researcher for a discovery brief, then
  dispatch the Scribe for a Pillar 6 X post mapping that tool to an SMB
  (HVAC/plumber/Shopify) bottleneck. Output to
  `drafts/utility-scout-YYYY-MM-DD.md`. Uses mavis browser tool against the
  user's real Chrome. Triggers: "scout for new AI tools", "find a new tool
  today", "what dropped this week in AI", "ai utility scout", or specifies a
  launch directory. Halt on login, rate-limit, or unfamiliar UI. Read-only
  extraction.
---

# ai-utility-scout

The supply pipeline for **Pillar 6** (The Hype Translator).
Daily scan of AI launch directories, picks ONE specific
(non-generic) newly released AI tool, dispatches the
Researcher for a discovery brief, then the Scribe for a
Pillar 6 X post that maps the tool to a boring, money-
making SMB use case.

This pairs with `x-hype-translator` (broadcast-side, single-
tool-by-name) the same way `x-niche-scraper` pairs with
`x-bookmark-parser`. The scout finds the tool; the hype-
translator narrates a specific announcement.

## When to run

**Triggers:**
- "ai utility scout" / "scout for new AI tools" / "what
  dropped today in AI"
- "find a new tool" / "scan the launch directories"
- "what's new in AI" (daily-cadence variant)
- "Rundown AI today" / "Product Hunt AI" / "There's An AI
  For That" (operator can name the source)

**Do NOT run for:**
- The user's own posts (no translation needed)
- Tools older than 14 days (use `x-niche-scraper` for
  settled tools; the scout is for fresh drops)
- Generic chatbot launches (filtered out — the persona
  translates specific-tool capability, not "ChatGPT
  alternative #4,317")
- Mass translations of multiple tools in one run (this
  skill picks ONE per run)
- The user's own X bookmarks (use `x-bookmark-parser`)

## Inputs

| Input | Default | Required |
|---|---|---|
| Launch directory | pick from approved list | **yes** (or operator-supplied URL) |
| Filter (banned categories) | "AI Chatbot" / "AI Assistant" / "General AI" / "GPT Wrapper" | no — operator can override |
| Capture depth | top 5 tools listed today | no — 1, 5, 10, or "all visible in first snapshot" |
| Engagement floor | 100 saves (or 50 upvotes) | no |
| Destination dir | `03 Projects/X-Content-Engine/drafts/` | no |
| File naming | `utility-scout-YYYY-MM-DD.md` (rolling per day) | no |

The 4 approved launch directories + their strengths in
`references/launch-directories.md`. The reject/accept
filter rules in `references/filter-rules.md`.

## Outputs

A markdown file at
`03 Projects/X-Content-Engine/drafts/utility-scout-YYYY-MM-DD.md`
(one rolling file per day, all scouts aggregated). Each
scout section contains:

- A header with the tool name, source directory, capture
  timestamp, the source URL
- The Researcher's discovery brief (what the tool actually
  does, who uses it, what category)
- The Scribe's Pillar 6 X post draft (raw, copy-pasteable,
  180-260 chars)
- The 4-step implementation for the boring SMB audience
- The $/month cost + hours/week time-saved
- A "Why this angle" rationale
- An unchecked approval box

Full template in `references/output-format.md`.

## The 10-step procedure (overview)

The full 10-step procedure with bash commands lives in
`references/procedure.md`. The high-level flow:

1. Verify bridge is live (`mavis browser status`)
2. Pick the launch directory (rotate across 4 approved)
3. Open the directory
4. Auth + load wait + result check
5. Filter the listings (reject generic chatbots, accept
   specific tools)
6. Extract the tool info (name, URL, one-liner, pricing,
   engagement)
7. Dispatch the Researcher for a discovery brief (task
   spec in `references/researcher-task-spec.md`)
8. Dispatch the Scribe for the Pillar 6 draft (task spec
   in `references/scribe-task-spec.md`)
9. Update the drafts ledger
10. Return summary

## Hard constraints

1. **No interaction.** Read-only against the launch
   directory and the tool's page.
2. **No credential entry.** If the launch directory is
   paywalled (e.g., Product Hunt's full archive), halt and
   surface.
3. **Rate limit.** Some launch directories have aggressive
   bot detection. If the snapshot returns a "verify you
   are human" page, halt.
4. **No fabrication.** The Scribe may not invent a feature
   the tool doesn't have. If the tool's capability is
   unclear from the directory, halt and ask the operator.
5. **No daily spam.** The skill picks ONE tool per run.
   Mass translations are a different skill.
6. **Filter bypass.** The Scribe's draft must include the
   specific tool name. If the draft writes a generic "AI
   tool X" without naming the actual tool, the Scribe's
   contract is violated and the draft is rejected.
7. **One tool per run.** The skill does NOT do
   roundups. ONE per run.
8. **Specific tool, not category.** Don't translate
   "AI voice agents" — translate a specific tool.

## When the skill HALTs

Halt and escalate to Andre when:
- Bridge offline (H1) — load Chrome extension
- Login prompt / paywall (H2) — operator logs in
- Rate limit (H3) — wait 10+ minutes
- Zero listings (H4) — try a different directory
- All listings are generic chatbots (H5) — try a
  different directory
- Tool already in `_ledger.mdl` (H6) — pick the next
- Scribe returns a draft > 280 chars (H7) — surface
- Scribe invents a feature not in the brief (H8) —
  surface for retry
- Scribe's draft doesn't name the specific tool (H9) —
  surface for retry
- Tool pricing is unclear (H10) — Scribe marks `unclear`,
  operator provides

The skill is a diagnostic, not an authorization. The
operator decides the action.

## Verification (post-write)

After the Scribe writes the file:

1. `ls -la` confirms the file exists and contains both
   the Researcher's brief and the Scribe's draft
2. The post draft is 180-280 chars (target 180-260)
3. The post names the SPECIFIC tool (not "an AI tool" or
   "a new platform")
4. The post includes a specific $/month cost or `unclear`
5. The 4-step implementation is concrete (specific tools,
   specific order) — not generic
6. The banned-phrase re-grep ran
7. The ledger is appended
8. The Researcher's brief is present in the file before
   the Scribe's draft (chronological order)

## Cross-reference

- `references/launch-directories.md` — 4 approved launch
  directories + their strengths
- `references/filter-rules.md` — reject/accept categories
  (no generic chatbots, prefer video/voice/image tools)
- `references/researcher-task-spec.md` — the verbatim
  Researcher task spec (the discovery brief contract)
- `references/scribe-task-spec.md` — the verbatim Scribe
  task spec (the Pillar 6 post contract)
- `references/output-format.md` — the markdown file
  template
- `references/procedure.md` — the 10-step procedure with
  bash
- `tests/safety-halts.md` — 10 halt conditions + eval cases
- `tests/discipline.md` — 5 quality floors (specific tool,
  $/month anchor, 4-step concrete, no fabrication, banned
  phrases re-grep)
- `x-hype-translator` — broadcast-side sibling. Single-
  tool-by-name. Scout finds; hype-translator narrates a
  specific announcement.
- `x-niche-scraper` — search-side. For settled tools,
  broader queries.
- `local-competitor-auditor` — sibling for Pillar 1/2
  raw intelligence. Scout finds AI tools; auditor finds
  local businesses with friction.
- The Content Researcher
  (`03 Projects/X-Content-Engine/agents/researcher.md`) —
  produces the discovery brief
- The Content Scribe
  (`03 Projects/X-Content-Engine/agents/scribe.md`) —
  produces the Pillar 6 draft
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`)
  — the load-bearing voice source
- `team-config.md` — dispatch protocol for spawning
  Researcher + Scribe
