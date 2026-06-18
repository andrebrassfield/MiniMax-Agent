---
name: x-hype-translator
description: Hunt for newly released AI tools, models, or features, extract the raw capability, dispatch the Scribe to draft a "Hype Translation" post that maps the tool to a boring practical SMB or employee use case. Output to drafts/hype-translations-YYYY-MM-DD.md. Uses mavis browser tool against the user's real Chrome. Triggers when the user says "hype translate", "what's new in AI", "translate this tool", "new tool breakdown", or specifies a tool/model to scout. Halt on login, rate-limit, or unfamiliar UI. Read-only extraction.
---

# X Hype Translator

## What this skill does

Searches X for the most recent high-engagement posts about newly released AI tools, models, repos, or features. Extracts the raw capability announcement, then dispatches the Content Scribe to draft a **"Hype Translation"** post in @DreTheSalesGuy's voice — one that ignores the general-purpose hype and maps the new tool to a specific, boring, money-making practical use case for an SMB owner or everyday employee.

This is the supply pipeline for Pillar 6 (The Hype Translator). Speed is the brand: if a tool drops at 9am, the user has a tactical breakdown posted by noon.

## When to run

**Trigger phrases:**
- "hype translate" / "hype-translate" / "translate this drop"
- "what's new in AI" / "what dropped this week" / "new AI tool"
- "translate this tool" / "break down this launch" / "practical breakdown of [tool name]"
- "[tool name] hype translation"

**Do NOT run for:**
- The user's own posts (no translation needed)
- Tools older than 7 days (use the niche-scraper for settled tools, this skill is for fresh drops)
- Non-AI tooling (the persona only translates AI capability)
- Mass translations of multiple tools in one run (this skill is single-tool by design)

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Tool / model name | (none — must be specified) | **yes** |
| Optional: launch date | today | no — useful for filtering "just released" |
| Search queries | auto-generated from tool name + "just released" / "just dropped" / "launch" | no — operator can override |
| Search tab | `Latest` | no — `Top` for established tools, `Media` for screenshots |
| Capture depth | top 5 posts | no — 1, 5, 10, or "all visible in first snapshot" |
| Engagement floor | 500 views (low — fresh drops may not have rolled up yet) | no |
| Destination dir | `03 Projects/X-Content-Engine/drafts/` | no |
| File naming | `hype-translations-<tool-slug>-YYYY-MM-DD-HHMM.md` | no — operator can override the per-tool slug to a single rolling file `hype-translations-YYYY-MM-DD.md` |

**Query generation:** the skill auto-generates 2-3 search queries from the tool name:
- `<tool name> just released`
- `<tool name> launch` (or `dropped`, `shipped`, `announcing`)
- `<tool name> benchmark` (for technical posts)

Operator can override with a specific query if they already have one in mind.

## Outputs

A markdown file at `03 Projects/X-Content-Engine/drafts/hype-translations-<tool-slug>-YYYY-MM-DD-HHMM.md` (or the rolling per-day variant) with:

- A header with the tool name, the search queries used, the freshness filter, and the timestamp
- The raw capability extraction from the top posts (per-post summary with author + handle + post URL + engagement metrics)
- A "Practical use case" section: the boring, money-making SMB or employee application Andre would post about
- The Scribe's hype-translation draft (per the dispatch contract below)
- An unchecked approval box

The skill returns a one-paragraph summary to the operator with: file path, top post found, and the Scribe's draft headline.

## Procedure

### Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected`, **HALT** and tell the operator to load the Chrome extension per `mavis browser install` output. Do not proceed with auto-spawned Chromium fallbacks for x.com.

### Step 2: Generate search queries

Build 2-3 search queries from the tool name. Default patterns:

- `<tool name> just released` → `https://x.com/search?q=<tool>+just+released&f=live`
- `<tool name> launch` → `https://x.com/search?q=<tool>+launch&f=live`
- `<tool name> dropped` or `shipped` → `https://x.com/search?q=<tool>+shipped&f=live`

If the operator provided a specific query, use that instead.

### Step 3: Open the search URL

```bash
mavis browser tool open_tab '{"url":"<first-search-url>"}'
```

Note the returned `tabId`. If the first query returns no results, try the next query in sequence.

### Step 4: Authentication + load wait + result check

Wait 3-5 seconds. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":2}'
```

**Halt conditions:**
- Snapshot shows "Sign in to X" / "Log in" — operator needs to log in manually
- Snapshot shows a rate-limit warning — HALT, recommend waiting
- URL is not `x.com/search` after navigation
- Zero results across all generated queries — HALT, report "no posts about [tool] yet — too fresh, try again in 24h"

**Proceed conditions:**
- Search results visible with author handles + post timestamps
- At least one post within the engagement floor

### Step 5: Extract the raw capability

From the snapshot, identify the top 1-3 posts that are announcing or describing the tool. For each:

- Author handle + post URL
- Full post text
- Engagement metrics
- The capability being announced: "what is it, what does it do, what's the new thing"
- The launch context: "just released" / "preview" / "available now" / etc.

**Do NOT scroll via `press_key`** — same Focus Rule as the other X skills. If more posts are needed, the operator scrolls manually and re-runs.

### Step 6: Dispatch the Scribe

The Scribe is registered as `x-scribe`. Per the team-config dispatch protocol, the chief (Mavis) sends:

```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{"agent":"x-scribe","model":"MiniMax-M2.7","prompt":"<task spec>"}'
```

**The task spec to pass (verbatim — copy this block):**

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

### Step 7: Update the drafts ledger

Append a one-line entry to `03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — hype-translation-<tool-slug> from <source-url> (Scribe draft, pending)
```

### Step 8: Return summary

Send a one-paragraph summary to the operator:
- Tool name
- File path
- Top source post found
- Scribe's draft headline (one line)
- "Speed-to-tactical" verdict (is the draft ready to post now, or does it need a human pass first?)

## The Data Schema (the source extraction, before dispatching to Scribe)

The chief (Mavis) extracts the raw capability from the top 1-3 source posts before dispatching. The Scribe doesn't see x.com directly — it gets the chief's extraction as task-spec input. Per the source post:

| Field | Type | Required |
|-------|------|----------|
| `tool_name` | string | yes |
| `tool_slug` | string (kebab-case) | yes — used in filename |
| `capability_one_liner` | string | yes — what the tool does, in one sentence |
| `source_url` | string | yes |
| `source_handle` | string | yes |
| `source_post_text` | string | yes — full post text |
| `source_engagement` | object | yes — `{replies, reposts, likes, views}` |
| `launch_context` | string | yes — "just released" / "preview" / "available now" |
| `captured_at` | ISO timestamp | yes |

## The Scribe's Hype Translation contract (recap)

The Scribe receives the source extraction AND the task spec (above). The Scribe's job:

1. Read `03 Projects/X-Content-Engine/agents/persona.md` for voice + pillars
2. Pick the specific boring audience (one of: roofer, plumber, HVAC tech, sales rep, marketing manager at 12-person co, small e-com store, $40K/mo Shopify)
3. Show the 4-step implementation (specific tools, specific order, specific time window)
4. Show the cost ($/month) + time saved (hours/week)
5. Draft a 180-260 char post in Pillar 6 voice
6. Re-grep for banned phrases before returning

The Scribe may not invent a feature the tool doesn't have. The capability comes from the source post. The translation is a reframe, not an addition.

## The Safety Halts (inherited, plus the hype-translation specifics)

1. **No interaction.** Strictly read-only against X UI.
2. **No credential entry.** Login prompts → halt and alert.
3. **Rate limit.** X is aggressive about scraping. If `mavis browser` returns 429, halt.
4. **Source accuracy.** The Scribe may not invent a feature the tool doesn't have. If the source post is vague about capability, the Scribe drafts a "vague hype → narrow use case" pattern, not an invented use case.
5. **Audience specificity.** If the Scribe's draft is generic ("any business can use this") instead of specific ("a roofer in Ohio with 3 trucks"), halt and surface.
6. **Dollar + time math grounded.** If the Scribe can't ground the $/month cost or the hours/week time-saved in a real number, it marks `unclear` and the operator provides the number — the Scribe may not invent.
7. **Banned phrases re-grep.** Before returning, the Scribe must re-grep the draft for the banned-phrases list.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Bridge offline | `mavis browser status` shows `not connected` | Halt; tell operator to load Chrome extension |
| Login prompt | snapshot shows Sign in / Log in | Halt; tell operator to log in |
| Rate limit | snapshot shows rate limit OR `mavis browser` returns 429 | Halt; surface; recommend waiting 10+ minutes |
| Zero results across all queries | snapshot has no author blocks | Halt; report "tool too fresh, try again in 24h" |
| Scribe returns a draft > 280 chars | file output | Halt; surface the over-limit draft for operator review |
| Scribe returns a generic audience | file output ("any business can use this") | Halt; surface for Scribe to retry with specific audience |
| Scribe invents a feature the source post didn't announce | file output vs source extraction | Halt; surface the fabricated feature for the Scribe to correct |
| Tool has no $/month pricing (e.g., open-source) | Scribe marks `unclear` for cost | Surface to operator; Scribe may draft with "free" as the cost |
| Scribe spawn fails | dispatch error | Halt; surface the spawn error |

## Verification

After the Scribe writes the file:
1. `ls -la` confirms the file exists and contains the new translation section
2. The post draft is 180-260 chars (target), never over 280
3. The 4-step implementation is concrete (specific tools, specific order) — not generic
4. The cost is grounded in a real $/month figure (or marked `unclear`)
5. The time saved is grounded in a real hours/week figure (or marked `unclear`)
6. The audience is specific (one of the persona-anchored audiences) — not "any business"
7. The banned-phrase re-grep ran (no "dive into" / "game-changer" / etc.)
8. The ledger is appended

## Cross-reference

- `x-niche-scraper` — for the wider market scan (top 10 by query, settled tools)
- `x-bookmark-parser` — for the user's own curated saves
- `x-engagement-hunter` — for replying to specific large accounts
- `x-empowerment-hunter` — for finding people expressing AI anxiety (Pillar 5 reply pipeline)
- `mavis browser` CLI — the underlying tool surface
- The Content Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — consumes the source extraction + the Hype Translation task spec
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`) — the load-bearing voice source (Pillar 6)
- `team-config.md` — the dispatch protocol for spawning the Scribe
