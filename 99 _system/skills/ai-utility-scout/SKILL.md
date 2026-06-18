---
name: ai-utility-scout
description: Scan top AI launch directories (There's An AI For That, Rundown AI, Product Hunt, etc.) for newly released AI tools, pick ONE specific (non-generic-chatbot) tool, dispatch the Researcher for a discovery brief, then dispatch the Scribe for a Pillar 6 X post mapping that tool to an SMB (HVAC/plumber/Shopify) bottleneck. Output to drafts/utility-scout-YYYY-MM-DD.md. Uses mavis browser tool against the user's real Chrome. Triggers when the user says "scout for new AI tools", "find a new tool today", "what dropped this week in AI", "ai utility scout", or specifies a launch directory. Halt on login, rate-limit, or unfamiliar UI. Read-only extraction.
---

# AI Utility Scout

## What this skill does

Scans top AI launch directories daily, picks ONE specific (non-generic) newly released AI tool, and produces a Pillar 6 (Hype Translator) X post that maps that tool to a boring, money-making use case for an HVAC shop, plumber, Shopify store, or 9-to-5 knowledge worker.

This is the **supply pipeline for Pillar 6** (The Hype Translator). It pairs with `x-hype-translator` (broadcast-side, single-tool-by-name) the same way `x-niche-scraper` pairs with `x-bookmark-parser`. The scout finds the tool; the hype-translator narrates a specific announcement. Same data, different cadence.

## When to run

**Trigger phrases:**
- "ai utility scout" / "scout for new AI tools" / "what dropped today in AI"
- "find a new tool" / "scan the launch directories"
- "what's new in AI" (a daily-cadence variant of the same intent)
- "Rundown AI today" / "Product Hunt AI" / "There's An AI For That" (operator can name the source)

**Do NOT run for:**
- The user's own posts (no translation needed)
- Tools older than 14 days (use `x-niche-scraper` for settled tools; the scout is for fresh drops)
- Generic chatbot launches (filtered out — the persona translates specific-tool capability, not "ChatGPT alternative #4,317")
- Mass translations of multiple tools in one run (this skill picks ONE per run)

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Launch directory | (none — pick from approved list below) | **yes** (or operator-supplied URL) |
| Filter (banned categories) | "AI Chatbot" / "AI Assistant" / "General AI" / "GPT Wrapper" | no — operator can override |
| Capture depth | top 5 tools listed today | no — 1, 5, 10, or "all visible in first snapshot" |
| Engagement floor | 100 saves (or 50 upvotes, if source exposes them) | no |
| Destination dir | `03 Projects/X-Content-Engine/drafts/` | no |
| File naming | `utility-scout-YYYY-MM-DD.md` (one rolling file per day; multiple scouts aggregated) | no |

**Approved launch directories (use as the default rotation):**

1. **There's An AI For That** — `https://theresanaiforthat.com` — daily curated list, "Today" tab. Strong for SMB-flavored tools (inventory, voice, video). Weak for dev-only infrastructure.
2. **Product Hunt — AI category** — `https://www.producthunt.com/topics/artificial-intelligence` — daily launches, upvote-based ranking. Strong for new products with consumer/SMB angles. Watch for launch-pad noise.
3. **Rundown AI** — `https://www.rundown.ai` — daily AI news post + weekly tool roundup. Strong for "what dropped this week" framing. More curated than PH.
4. **Hacker News — Show HN** — `https://news.ycombinator.com/show` — dev-flavored. Use as a fallback for technical AI tools (open-source repos, dev infra).

Operator can supply any custom URL.

## Outputs

A markdown file at `03 Projects/X-Content-Engine/drafts/utility-scout-YYYY-MM-DD.md` (one rolling file per day, all scouts aggregated). Each scout section contains:

- A header with the tool name, source directory, capture timestamp, the source URL
- The Researcher's discovery brief (what the tool actually does, who uses it, what category)
- The Scribe's Pillar 6 X post draft (raw, copy-pasteable, 180-260 chars)
- The 4-step implementation for the boring SMB audience
- The $/month cost + hours/week time-saved
- A "Why this angle" rationale
- An unchecked approval box

The skill returns a one-paragraph summary to the operator with: file path, tool name, source, the Scribe's draft headline, and the strongest SMB use case identified.

## Procedure

### Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected`, **HALT** and tell the operator to load the Chrome extension. Do not proceed with auto-spawned Chromium fallbacks — the security memory locks auto-spawn patterns.

### Step 2: Pick the launch directory

Default rotation: alternate across the 4 approved directories across days to get a diverse feed. If the operator specified a directory, use that.

### Step 3: Open the directory

```bash
mavis browser tool open_tab '{"url":"<directory-url>"}'
```

Note the returned `tabId`.

### Step 4: Authentication + load wait + result check

Wait 3-5 seconds. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":2}'
```

**Halt conditions:**
- Snapshot shows "Sign in" / "Log up" / "Subscribe" paywall — operator decides whether to log in
- Snapshot shows a rate-limit warning — HALT
- URL is not the expected directory after navigation
- Zero results — HALT, report "no tools today — try a different directory"

**Proceed conditions:**
- Listings visible with tool names + 1-line descriptions
- At least one tool within the engagement floor (100 saves / 50 upvotes)

### Step 5: Filter the listings

**Reject (do not draft on these):**
- Generic AI chatbots / "ChatGPT alternative" wrappers
- Pure infrastructure with no SMB-flavored application (e.g., a new vector database with no consumer angle)
- Tools that have already been translated (check `drafts/_ledger.mdl` first — if the tool name is already on file, skip it)
- Tools with vague capability ("an AI that does X" with no specific use case)

**Prefer (in priority order):**
1. AI video / voice / image generation tools (Pillar 6's bread and butter — the "everyone is hyping it, here's what a roofer can do with it" angle)
2. AI voice agents / voice cloning (ties to Pillar 2's Missed Call thesis)
3. AI inventory / e-commerce / Shopify tools (Pillar 1)
4. AI productivity / automation tools (Pillar 5)
5. AI local services / dispatching / CRM tools (Pillar 2)
6. Other (novelty)

Pick the top ONE from the preferred categories. If the top of the directory is a generic chatbot, skip to the next non-generic tool.

### Step 6: Extract the tool info

For the picked tool, extract:
- Tool name
- Source URL (the tool's own page if available, or the directory entry URL)
- One-line capability description (verbatim from the directory)
- Launch date (if visible)
- Pricing tier (free / freemium / paid — from the tool's page if linked, or "unclear" if not)
- Engagement metrics (saves, upvotes, comments — for the Researcher's analysis)

**Do NOT click into the tool's full marketing page** unless necessary — the directory's one-liner is enough for the discovery brief. If the one-liner is too vague, click into the tool's page for one screenshot-equivalent (a snapshot, not a full crawl) and extract the headline + a bullet list.

**Do NOT scroll via `press_key`** — same Focus Rule as the other X skills. If the top of the directory is all generic chatbots, the operator scrolls manually and re-runs.

### Step 7: Dispatch the Researcher for a discovery brief

The Researcher is registered as `x-researcher`. Per the team-config dispatch protocol:

```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{"agent":"x-researcher","model":"MiniMax-M2.7","prompt":"<task spec>"}'
```

**The task spec to pass (verbatim — copy this block):**

```
You are drafting a **tool discovery brief** for a newly released AI tool that was just spotted in a launch-directory scan. Your job is NOT to analyze viral X posts (that's your other job) — this is a tool scout, focused on "what does this tool actually do and why should @DreTheSalesGuy translate it for SMBs?"

The voice file is at `03 Projects/X-Content-Engine/agents/persona.md`. Read it before drafting.

**The tool:**
- Name: <tool name>
- Source directory: <directory name>
- Directory entry URL: <directory-url>
- One-line capability (verbatim from directory): "<directory's one-liner>"
- Launch date (if visible): <date or "unclear">
- Pricing tier: <free / freemium / paid / unclear>
- Engagement (saves/upvotes): <number>

**The discovery brief format (write to 03 Projects/X-Content-Engine/drafts/utility-scout-YYYY-MM-DD.md, append to existing file or create new):**

## Tool: <tool name> — <source directory> — YYYY-MM-DD HH:MM CT

**Source:** <directory entry URL>
**Pricing:** <free / freemium / paid / unclear>
**Launched:** <date or "unclear">

### What it does (one sentence)

<the tool's actual capability, in plain English>

### Category

<video / voice / image / productivity / e-commerce / local services / dev infra / other>

### Who uses it (3 candidate audiences)

1. <audience 1>
2. <audience 2>
3. <audience 3>

### The boring SMB use case (the Dre Builds angle)

<one paragraph: which of the 3 audiences is the "boring practical money-making" audience, and what the 4-step implementation would look like. Reference the persona's content pillars (Pillar 1 E-Com, Pillar 2 Trades, Pillar 5 Job Defense, Pillar 6 Hype Translation) if relevant.>

### What makes it hype-able vs. practical

<2-3 sentences: what's the "cool" angle the X conversation will hype, vs. the boring application Dre Builds would post.>

### Open questions for the Scribe

- Should the post use a specific persona pillar (Pillar 1/2/5/6)?
- What's the specific tool pricing anchor (if visible)?
- Is there a 4-step implementation path that fits in 280 chars?
```

### Step 8: Dispatch the Scribe for the Pillar 6 draft

After the Researcher's brief is written, dispatch the Scribe:

```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{"agent":"x-scribe","model":"MiniMax-M2.7","prompt":"<task spec>"}'
```

**The Scribe's task spec to pass (verbatim):**

```
You are drafting a Hype Translator post in @DreTheSalesGuy's voice. The voice file is at `03 Projects/X-Content-Engine/agents/persona.md`. Read it before drafting. The Pillar 6 voice discipline is the lead.

**The new tool:**
- Name: <tool name>
- One-line capability: <from Researcher's brief>
- Source: <directory-url>
- The boring SMB use case: <from Researcher's brief>
- The 4-step implementation: <from Researcher's brief>
- Cost in $/month: <from Researcher's brief or "unclear">
- Time saved in hours/week: <from Researcher's brief or "unclear">

**The Hype Translation rules (HARD):**

1. **Ignore the generic hype.** No "this is going to change everything" / "the future is here" / "this is revolutionary."
2. **Pick a specific boring audience from the persona's content pillars** — roofer, plumber, HVAC tech, sales rep, marketing manager at 12-person co, small e-com store, $40K/mo Shopify, 9-to-5 knowledge worker. Not "developers" or "AI researchers."
3. **Show the exact 4-step implementation.** What does the SMB owner do, in what order, with what tools, in what time window?
4. **Show the cost in $/month.** If the tool is free, say so. If pricing is unclear, mark `unclear`.
5. **Show the time-saved in hours/week.** If unclear, mark `unclear`.
6. **Match the voice per persona.md.** Pillar 6: lead with a contrarian "Who cares. Here's what a [boring audience] can do with it." Staccato periods. 180-260 chars target, 280 hard cap.
7. **No AI fluff phrases.** Banned list is in your Scribe spec.
8. **Banned emoji except 🧵 for thread markers.**

**Output format (append to 03 Projects/X-Content-Engine/drafts/utility-scout-YYYY-MM-DD.md, under the Researcher's discovery brief):**

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

[Any specifics to verify — e.g., "the 4-step implementation assumes the tool stays free during preview; check pricing before posting"]

### Approval

- [ ] approved → post
- [ ] rejected (reason: ________)
- [ ] needs revision (notes: ________)
```

### Step 9: Update the drafts ledger

Append a one-line entry to `03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — utility-scout from <directory> (tool: <tool name>, Scribe draft, pending)
```

### Step 10: Return summary

Send a one-paragraph summary to the operator with: file path, tool name, source, draft headline, the strongest SMB use case identified.

## The Scribe's contract (recap)

The Scribe receives the Researcher's discovery brief + the Hype Translation task spec. The Scribe's job:

1. Read `persona.md` for voice + pillars
2. Pick the specific boring audience (one of the persona-anchored options)
3. Show the 4-step implementation (specific tools, specific order, specific time window)
4. Show the cost ($/month) + time saved (hours/week)
5. Draft a 180-260 char post in Pillar 6 voice
6. Re-grep for banned phrases before returning
7. **No fabrication.** If the cost or time-saved is unclear from the tool's pricing page, mark `unclear`. The operator provides the number; the Scribe may not invent.

## The Safety Halts (inherited, plus the scout specifics)

1. **No interaction.** Read-only against the launch directory and the tool's page.
2. **No credential entry.** If the launch directory is paywalled (e.g., Product Hunt's full archive), halt and surface.
3. **Rate limit.** Some launch directories have aggressive bot detection. If the snapshot returns a "verify you are human" page, halt.
4. **No fabrication.** The Scribe may not invent a feature the tool doesn't have. If the tool's capability is unclear from the directory, halt and ask the operator.
5. **No daily spam.** The skill picks ONE tool per run. If the operator wants a 5-tool roundup, that's a different skill (e.g., `ai-weekly-roundup` — not yet built).
6. **Filter bypass.** The Scribe's draft must include the specific tool name. If the draft somehow writes a generic "AI tool X" without naming the actual tool, the Scribe's contract is violated and the draft is rejected.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Bridge offline | `mavis browser status` shows `not connected` | Halt; tell operator to load Chrome extension |
| Login prompt / paywall | snapshot shows Sign in / Subscribe | Halt; tell operator to log in or choose a different directory |
| Rate limit | snapshot shows rate limit OR `mavis browser` returns 429 | Halt; recommend waiting 10+ minutes |
| Zero listings | snapshot has no tool entries | Halt; report "no tools today" and try a different directory |
| All listings are generic chatbots | filter rejects all of them | Halt; report "no specific tools today" and try a different directory |
| Tool already in `_ledger.mdl` | chief's pre-check | Skip; pick the next specific tool |
| Scribe returns a draft > 280 chars | file output | Halt; surface the over-limit draft for operator review |
| Scribe invents a feature the directory entry didn't describe | file output vs Researcher's brief | Halt; surface the fabricated feature for the Scribe to correct |
| Scribe's draft doesn't name the specific tool | file output | Halt; Scribe's contract violation; surface for retry |
| Tool pricing is unclear | Researcher's brief | Scribe marks `unclear`; operator provides the number |

## Verification

After the Scribe writes the file:
1. `ls -la` confirms the file exists and contains both the Researcher's brief and the Scribe's draft
2. The post draft is 180-280 chars (target 180-260)
3. The post names the SPECIFIC tool (not "an AI tool" or "a new platform")
4. The post includes a specific $/month cost or `unclear`
5. The 4-step implementation is concrete (specific tools, specific order) — not generic
6. The banned-phrase re-grep ran
7. The ledger is appended
8. The Researcher's brief is present in the file before the Scribe's draft (chronological order)

## Cross-reference

- `x-hype-translator` — broadcast-side sibling. Single-tool-by-name. The scout finds; the hype-translator narrates a specific announcement.
- `x-niche-scraper` — search-side. For settled tools, broader queries.
- `x-bookmark-parser` — for the user's own curated saves
- `x-engagement-hunter` — for replying to specific large accounts (Pillar 2/3 reply pipeline)
- `x-empowerment-hunter` — for finding AI-anxiety posts (Pillar 5 reply pipeline)
- `local-competitor-auditor` — sibling for Pillar 1/2 raw intelligence. The scout finds AI tools; the competitor-auditor finds local businesses with friction. Same data, different angle.
- `mavis browser` CLI — the underlying tool surface
- The Content Researcher (`03 Projects/X-Content-Engine/agents/researcher.md`) — produces the discovery brief (different output shape from the viral-format brief)
- The Content Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — produces the Pillar 6 draft
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`) — the load-bearing voice source
- `team-config.md` — the dispatch protocol for spawning Researcher + Scribe
