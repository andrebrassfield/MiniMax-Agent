---
name: x-engagement-hunter
description: Open a target X account (e.g., @NickHuber), read their most recent post, dispatch the Scribe to draft a value-add reply in @DreTheSalesGuy voice, and save the draft to drafts/replies-YYYY-MM-DD.md for manual review. Hard constraint: NEVER click the reply button. Read-only extraction. The user copy/pastes and publishes manually. Triggers when the user says "reply to @handle", "engage with @handle's latest post", "draft a reply to X", or "engagement hunt on @handle".
---

# X Engagement Hunter

## What this skill does

Opens a target X account's profile or latest post URL, reads their most recent post, dispatches the Content Scribe to draft a **value-add reply** in @DreTheSalesGuy's voice (per `agents/persona.md`), and saves the draft to `03 Projects/X-Content-Engine/drafts/replies-YYYY-MM-DD.md` for manual review. The user then copies the draft reply and pastes it into x.com manually.

This is a top-of-funnel growth tool: by replying to large accounts with high-quality, non-arguing, technical/agentic insights, the user gets visibility in front of those accounts' followers without being spammy.

**Hard constraint: NEVER click the reply button on x.com.** The skill is read-only against the X UI. Drafts are written to a file, not posted. This is non-negotiable.

## When to run

**Trigger phrases:**
- "reply to @handle" / "draft a reply to @handle's latest post"
- "engage with @handle" / "engagement hunt on @handle"
- "what should I reply to @handle with"
- "build a reply to this X post: <url>"

**Do NOT run for:**
- The user's own posts (no reply needed)
- A post the user is already drafting a reply to (use the existing draft)
- Mass-reply workflows (this skill is single-target by design)
- Non-X platforms

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Target handle or URL | (none — must be specified) | **yes** |
| Capture source | most recent post on the profile | no — alternate: a specific post URL |
| Engagement floor | any (read whatever's there) | no |
| Reply angle hint | (none — Scribe picks from persona) | no — operator can hint "agree + add technical depth" or "tactical extension" to bias the draft |
| Destination dir | `03 Projects/X-Content-Engine/drafts/` | no |
| File naming | `replies-YYYY-MM-DD.md` (one file per day, all targets in one file) | no |

**Target URL formats accepted:**
- `https://x.com/<handle>` — opens profile, reads the topmost post
- `https://x.com/<handle>/status/<id>` — opens a specific post, replies to that
- `@<handle>` shorthand — auto-converted to `https://x.com/<handle>`

## Outputs

A markdown file at `03 Projects/X-Content-Engine/drafts/replies-YYYY-MM-DD.md` (one file per day, all targets in that day aggregated). Each reply section contains:

- A header with the target's handle + the source post URL + a quoted excerpt of their post
- The draft reply text (raw, ready to copy/paste into x.com)
- A character count
- A "Why this reply" rationale explaining the value-add angle
- A "Notes for Andre" section flagging any specifics to verify before posting
- An unchecked approval box

The skill returns a one-paragraph summary to the operator with: file path, target count, and a one-line note about which reply is the strongest candidate to publish first.

## The Hard Constraint (READ THIS)

**DO NOT click the reply button on x.com. EVER.** The skill is read-only against the X UI. The draft is written to a file in the vault. The user copy/pastes the draft into x.com manually after approval.

If at any point during the procedure a tool call would click a reply button, type into the reply textarea, or submit a reply, the skill halts and surfaces to the operator. The skill is "draft a reply" — it is NOT "post a reply."

The reason this is hard: X's UI has reply buttons, quote-reply buttons, and the post detail page has a reply textarea. The `click` tool could be tempted to use any of these. The skill explicitly forbids ALL of them.

## Procedure

### Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected`, **HALT** and tell the operator to load the Chrome extension per `mavis browser install` output. Do not proceed with auto-spawned Chromium fallbacks for x.com.

### Step 2: Open or navigate to the target URL

```bash
mavis browser tool open_tab '{"url":"<target-url>"}'
```

Note the returned `tabId`. The tool is documented to auto-claim the tab for the calling session.

**URL normalization:**
- `@NickHuber` → `https://x.com/NickHuber`
- `https://twitter.com/NickHuber` → `https://x.com/NickHuber`
- `https://x.com/NickHuber/status/1234567890` → leave as-is (specific post)

### Step 3: Authentication check + load wait

Wait 3-5 seconds for the page to render. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":2}'
```

**Halt conditions (operator-alert only, never type credentials):**
- Snapshot shows "Sign in to X" / "Log in" / "Sign up"
- Snapshot shows a rate-limit warning
- URL is not `x.com/<handle>` (or `x.com/<handle>/status/...`) after navigation

**Proceed conditions:**
- Profile page visible with the target handle in the header
- OR specific post page visible with the post text + author handle

### Step 4: Extract the source post

For a profile page: take the topmost post (the most recent).
For a specific post page: take the post in the main content area.

Extract:
- Author handle
- Full post text
- Timestamp
- Engagement metrics (for the operator's reference — not required for the reply draft)
- The source URL

**Do NOT scroll via `press_key`** — same Focus Rule as `x-bookmark-parser` and `x-niche-scraper`. If the topmost post is "Pinned" instead of "Latest," note that in the output (the operator can decide whether to draft against a pinned post or scroll to find the most recent non-pinned).

### Step 5: Dispatch the Scribe to draft the reply

The Scribe is registered as `x-scribe`. Per the team-config dispatch protocol, the chief (Mavis) sends:

```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{"agent":"x-scribe","model":"MiniMax-M2.7","prompt":"<task spec>"}'
```

**The task spec to pass:**

```
You are drafting a value-add reply to a target X post in @DreTheSalesGuy's voice.

**Target post:**
- Author: @<handle>
- URL: <source-url>
- Text: <full post text>
- Timestamp: <timestamp>

**The reply rules (HARD):**
1. **Never argue.** If the target's premise is correct, agree. If the target's premise is debatable, do not pick the fight. Just add a technical or agentic insight that extends or operationalizes their point.
2. **Add value, don't restate.** The reply should bring something the target didn't say — a number, a tactical implication, a connection to Andre's Pillar 2 (Trades / Missed Call) or Pillar 4 (Build Logs) work, a vendor/tool name, a use case the target didn't surface.
3. **Match Andre's voice per persona.md.** Staccato periods, lead with a punch, follow with unit economics. No AI fluff. No "great point" / "I love this" / "well said" openers.
4. **Hard character limit: 280.** Replies should be 80-260 chars. Shorter is fine for value-adds; longer is fine for tactical extensions.
5. **No emoji, no hashtags, no "follow for more" CTAs.**
6. **The reply is for the target's audience to see**, not just the target. Frame the insight so a third-party reader benefits too.

**Output format (write to 03 Projects/X-Content-Engine/drafts/replies-YYYY-MM-DD.md, append to the existing file or create if not present):**

For each reply draft:

## Reply to @<handle> · <source post timestamp>

**Source:** <source-url>
**Quoted post (excerpt):** "<first 200 chars of source post>..."
**Status:** pending_review

### Reply draft

<the actual reply text here, raw, ready to copy-paste into x.com>

### Character count

XX / 280

### Why this reply

[2-3 sentences: what value-add angle, what technical/agentic insight is being added, why this specific angle vs. the alternatives. Link to the persona pillar if relevant.]

### Notes for Andre

[Any specifics to verify — e.g., "this references a $0.40/call figure; confirm the latest number before posting" or "the @-mention is to a real account; double-check the handle."]

### Approval

- [ ] approved → copy/paste
- [ ] rejected (reason: ________)
- [ ] needs revision (notes: ________)
```

**Important:** the Scribe is dispatching with the system prompt at `agents/scribe.md`. The Scribe's own constraints (banned phrases, char limits, etc.) apply automatically. The chief does NOT need to repeat those in the task spec — the Scribe's system prompt enforces them.

### Step 6: Update the replies ledger

Append a one-line entry to `03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — reply to @<handle> (source: <source-url>, Scribe draft, pending)
```

### Step 7: Return summary to operator

Send a one-paragraph summary:
- File path
- Target handled
- One-line note about the strongest reply candidate (if multiple)
- Halt if the dispatch failed

## The Data Schema (the Scribe's reply section)

Per the Scribe spec, the reply draft section in the file must include:
- The source post (URL + quoted excerpt)
- The reply draft (raw, copy-pasteable)
- Character count
- "Why this reply" rationale linking back to the persona's content pillars
- "Notes for Andre" if any specifics to verify
- An unchecked approval box

The chief does NOT need to enforce this schema in the dispatch prompt — the Scribe's system prompt handles it. The chief just dispatches and waits for the Scribe to return with the file path.

## The Safety Halts (inherited, plus the hard constraint)

1. **No interaction.** Strictly read-only. Do not like, repost, follow, or **reply**. The reply constraint is the load-bearing rule.
2. **No credential entry.** If login is required, halt and alert.
3. **No DM, profile, or follow-tab navigation.** If the target's latest post is in a thread, the operator should manually navigate; the skill halts if it would click into a thread or open a DM.
4. **No quote-reply or repost buttons.** The skill extracts the source post text; it does not interact with any reply affordance.
5. **Sensitive content skip.** If the target's post contains DM screenshots, personal info, or content the operator hasn't opted to engage with, halt and surface.
6. **Unfamiliar UI.** If the snapshot shows a layout you don't recognize, halt and surface.
7. **Rate limit.** If `mavis browser` returns 429, halt and surface.
8. **Reply content boundary.** If the Scribe returns a draft that exceeds 280 chars, the skill halts and surfaces the over-limit draft rather than truncating. Truncation is the user's call.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Bridge offline | `mavis browser status` shows `not connected` | Halt; tell operator to load Chrome extension |
| Login prompt | snapshot shows Sign in / Log in | Halt; tell operator to log in |
| Target post is in a thread, can't isolate the topmost | snapshot shows "Show this thread" / nested replies | Halt; ask operator to provide the specific post URL instead |
| Pinned post at top instead of latest | snapshot shows "Pinned" badge | Note the pin; proceed with the pinned post OR ask the operator which they want |
| Scribe returns a draft > 280 chars | file output | Halt; surface the over-limit draft for operator review |
| Scribe returns a draft with AI fluff | file output (re-grep for banned phrases) | Halt; surface the offending draft for the Scribe to retry |
| Scribe spawn fails | dispatch error | Halt; surface the spawn error; suggest retry |
| Operator tries to use the skill for mass-replies | operator asks "draft replies to these 20 accounts" | Halt; this skill is single-target by design. For mass-reply, the operator should run it 20 times with one target each. |

## Verification

After the Scribe writes the file:
1. `ls -la` confirms the file exists and contains the new reply section
2. The reply section's character count is <= 280
3. The reply is NOT an arguer's reply (it agrees or extends, never contradicts the target's premise)
4. The reply adds something the target didn't already say (a number, a vendor, a tactical implication, a connection to Andre's Pillar 2 / 4 work)
5. The ledger is appended (not overwritten)
6. The approval box is unchecked

## Cross-reference

- `x-bookmark-parser` — for the user's own bookmarks (subjective curation)
- `x-niche-scraper` — for searching X by query (wider market, top-N)
- `x-link-reader` — for reading a single X URL without writing to the vault
- `mavis browser` CLI — the underlying tool surface
- The Content Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — consumes the source post + persona and returns the value-add reply
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`) — the load-bearing voice source for the Scribe's reply
- `team-config.md` — the dispatch protocol for spawning the Scribe
