---
name: x-empowerment-hunter
description: Hunt for real humans expressing AI anxiety on X, extract their posts, dispatch the Scribe to draft a "Aggressive Empathy" reply (acknowledge the fear, pivot to a tactical AI play). Output to drafts/empowerment-replies-YYYY-MM-DD.md. Uses mavis browser tool against the user's real Chrome. Triggers when the user says "empowerment hunt", "find people worried about AI", "draft Pillar 5 replies", or specifies a pain-point query. HARD CONSTRAINT: Read-only. Never click reply/post. Manual publish only.
---

# X Empowerment Hunter

## What this skill does

Searches X for posts where real humans are expressing anxiety about their careers in the AI era. Extracts the source posts, then dispatches the Content Scribe to draft a **"Aggressive Empathy"** reply in @DreTheSalesGuy's voice — one that acknowledges the fear directly, then immediately pivots to a tactical piece of advice on how the person can use an AI tool to protect their position.

This is the supply pipeline for Pillar 5 (The Leverage Play / Job Defense). The audience for the reply is the anxious employee, not the broader X audience. The reply's job is to convert a "I'm scared" post into a "I have a tactical move" mindset — without being preachy or condescending.

**Hard constraint: NEVER click the reply button on x.com.** The skill is read-only against the X UI. Drafts go to a file. The user copy/pastes manually. This is non-negotiable — same constraint as `x-engagement-hunter`.

## When to run

**Trigger phrases:**
- "empowerment hunt" / "find people worried about AI"
- "draft Pillar 5 replies" / "leverage play replies"
- "find posts about AI taking jobs" / "find AI anxiety posts"
- "reply to people worried about replacement"

**Do NOT run for:**
- Replies to AI influencers / pundits (those are the engagement-hunter's domain)
- The user's own posts (no reply needed)
- Mass-reply workflows (this skill is single-target by design; one source post → one draft reply per run)
- Non-X platforms

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Pain-point query | (none — must be specified) | **yes** |
| Search tab | `Latest` | no — `Top` for established conversations |
| Capture depth | top 5 posts | no — 1, 5, 10 |
| Engagement floor | 100 likes (low — anxiety posts often have low reach) | no |
| Destination dir | `03 Projects/X-Content-Engine/drafts/` | no |
| File naming | `empowerment-replies-YYYY-MM-DD.md` (one rolling file per day) | no |

**Pain-point query patterns:**
- "worried about AI"
- "AI taking jobs"
- "replaced by ChatGPT"
- "AI will take my job"
- "company replaced with AI"
- "my job AI"
- "AI made me redundant"

Operator can supply any custom query. The skill does NOT auto-rotate queries — the operator picks the angle.

## Outputs

A markdown file at `03 Projects/X-Content-Engine/drafts/empowerment-replies-YYYY-MM-DD.md` (one rolling file per day, all targets in that day aggregated). Each reply section contains:

- A header with the source author's handle + post URL + a quoted excerpt of their post
- The draft reply text (raw, ready to copy/paste into x.com)
- A character count
- A "Why this reply" rationale explaining the empathy + tactical pivot
- A "Notes for Andre" section flagging any specifics to verify
- An unchecked approval box

The skill returns a one-paragraph summary to the operator with: file path, target count, and a one-line note about which reply is the strongest candidate to publish first.

## The Hard Constraint (READ THIS)

**DO NOT click the reply button on x.com. EVER.** The skill is read-only against the X UI. The draft is written to a file. The user copy/pastes the draft into x.com manually after approval.

This is the same constraint as `x-engagement-hunter`. The skill explicitly forbids:
- Clicking the reply button
- Clicking the quote-reply button
- Typing into any reply textarea
- Submitting a reply
- Following the source author (would change the account state)

The skill is "draft a reply" — it is NOT "post a reply."

## Procedure

### Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected`, **HALT** and tell the operator to load the Chrome extension. Do not proceed with auto-spawned Chromium fallbacks for x.com.

### Step 2: Open the search URL

```bash
mavis browser tool open_tab '{"url":"https://x.com/search?q=<URL-encoded pain-point query>&f=live"}'
```

Use `f=live` (Latest) by default — anxiety posts are time-sensitive and a real human's "I'm scared" post is freshest in Latest. Use `f=top` if the operator wants the most-engaged version of the conversation.

Note the returned `tabId`.

### Step 3: Authentication + load wait + result check

Wait 3-5 seconds. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":2}'
```

**Halt conditions:**
- Snapshot shows "Sign in to X" / "Log in" — operator needs to log in manually
- Snapshot shows a rate-limit warning — HALT, recommend waiting
- URL is not `x.com/search` after navigation
- Zero results — HALT, report "no posts matching this pain-point query — try a different angle"

**Proceed conditions:**
- Search results visible, with author handles + post timestamps
- The query is producing real posts (not just noise / engagement bait)

**Filter heuristic:** the chief should also mentally check that the results contain actual human anxiety posts, not just AI-hype posts. A query like "worried about AI" can return both "I'm scared of losing my job" (target) and "Don't worry about AI" (counter-messaging). Skip the counter-messaging — only target the actual anxiety posts.

### Step 4: Extract the top source posts

Parse the snapshot's `text` field. For each post, extract:

- Author handle (real human, not an AI influencer — filter out accounts with "AI", "ML", "GPT" in the handle if possible)
- Full post text
- Timestamp (preferring recent)
- Engagement metrics
- The source URL
- The actual fear or anxiety being expressed (paraphrase in 1 sentence)

**Do NOT scroll via `press_key`** — same Focus Rule as the other X skills.

### Step 5: Dispatch the Scribe for each post

The Scribe is registered as `x-scribe`. Per the team-config dispatch protocol, the chief (Mavis) sends:

```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{"agent":"x-scribe","model":"MiniMax-M2.7","prompt":"<task spec for one post>"}'
```

**The task spec to pass (verbatim — copy this block, one spawn per source post):**

```
You are drafting an "Aggressive Empathy" reply to a target X post in @DreTheSalesGuy's voice. The voice file is at `03 Projects/X-Content-Engine/agents/persona.md`. Read it before drafting.

**The target post:**
- Author: @<handle>
- URL: <source-url>
- The fear being expressed: <one-sentence paraphrase>
- Full text: <full post text>
- Timestamp: <timestamp>

**The Aggressive Empathy reply rules (HARD):**

1. **Acknowledge the fear directly. Don't skip it.** The first sentence should mirror the person's actual concern. "I hear you on this." / "This is a real fear." / "You're not wrong to be worried." Acknowledge before pivoting.

2. **NEVER argue with the fear.** Don't say "you shouldn't worry" or "AI isn't actually going to take your job." The fear is real. Treat the person as a rational actor responding to a real threat.

3. **NEVER preach.** No "you should learn AI" / "you need to adapt" / "the future belongs to those who..." Those are condescending. The reader knows they need to adapt. They don't need a lecture.

4. **Immediately pivot to a specific tactical play.** The pivot is the load-bearing element. The reply should bring something the source post didn't already say: a specific tool, a specific 30-minute task the person can do this weekend, a specific workflow the person can automate in their current role.

5. **The tactical play must be boringly specific.** Not "learn AI tools." Not "stay ahead of the curve." Specific: "Open ChatGPT this weekend. Paste in your last 4 weekly status reports. Ask it to write the 5th one in your voice. Walk into Monday with 90 minutes of busywork pre-done."

6. **Match the voice per persona.md.** Pillar 5 voice: staccato periods, lead with a punch, follow with unit economics. 180-260 chars target, 280 hard cap. No emoji except 🧵 for thread markers.

7. **No "I will" / "we will" / "let's" openers.** The reply is not a corporate call-to-action. The reply is a peer-to-peer note. Speak as a peer, not as a coach.

8. **No "follow for more" / "DM me" / "link in bio" CTAs.** The reply's value is in the tactical play itself, not in growing Andre's audience.

9. **Banned phrases list is in your Scribe spec.** Re-grep before returning.

**Output format (append to 03 Projects/X-Content-Engine/drafts/empowerment-replies-YYYY-MM-DD.md, create the file if it doesn't exist):**

## Reply to @<handle> · <source post timestamp>

**Source:** <source-url>
**Quoted post (excerpt):** "<first 200 chars of source post>..."
**Fear being addressed:** <one-sentence paraphrase>
**Status:** pending_review

### Reply draft

<the actual reply text here, raw, ready to copy-paste into x.com>

### Character count

XX / 280

### Why this reply

[2-3 sentences: what the empathy opener does, what the tactical pivot is, why this specific tool/workflow is the right play for THIS person's specific anxiety. If the reply generalizes, flag that — the post is too specific for a generic play.]

### Notes for Andre

[Any specifics to verify — e.g., "the tactical play assumes the person has ChatGPT Plus; if they're on free, the time-saved math is different" or "this reference to 'last 4 weekly reports' is a guess; you may want to substitute 'last 4 status emails' or 'last 4 sprint retros' depending on the person's role."]

### Approval

- [ ] approved → copy/paste
- [ ] rejected (reason: ________)
- [ ] needs revision (notes: ________)
```

The chief should spawn the Scribe **once per source post** (not in batch). If 5 source posts are in the capture, the chief spawns the Scribe 5 times. This keeps each reply's task spec tight and prevents the Scribe from confusing source posts.

### Step 6: Update the replies ledger

Append a one-line entry per reply to `03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — empowerment-reply to @<handle> (source: <source-url>, Scribe draft, pending)
```

### Step 7: Return summary

Send a one-paragraph summary to the operator:
- File path
- Number of replies drafted
- The strongest reply candidate (one line)
- Any concerns (e.g., "the Scribe flagged 2 of the 5 source posts as too generic; those are surface-level anxieties, the operator should review whether to publish")

## The Empathy Pivot Template (the load-bearing pattern)

Every Aggressive Empathy reply should follow this 3-beat structure:

1. **Beat 1 — Acknowledge the fear** (1 sentence, 30-50 chars). Mirror the person's actual concern.
2. **Beat 2 — Reframe the threat** (1 sentence, 50-90 chars). The threat isn't the AI; it's the coworker who's already using it. Or: the threat isn't the tool; it's the workflow that hasn't been touched.
3. **Beat 3 — Tactical play** (2-3 sentences, 100-150 chars). Specific tool + specific task + specific time window. "Open X. Do Y. Walk into Z."

Total: 180-290 chars. Hard cap 280.

**Example skeleton (NOT a real draft, just a template):**

> "I hear you on this. The threat isn't the AI, it's the coworker who's already using it. Open ChatGPT this weekend. Paste in your last 4 weekly status reports. Ask it to write the 5th one in your voice. Walk into Monday with 90 minutes pre-done."

**The Scribe's job** is to fill in this template with the source-post-specific details, not to copy the template verbatim. Different anxieties need different reframes and different tactical plays.

## The Safety Halts (inherited, plus the empowerment-hunter specifics)

1. **No interaction.** Read-only. Never click reply, quote-reply, follow, or DM.
2. **No credential entry.** Login prompts → halt.
3. **Sensitive content skip.** Some anxiety posts mention specific employers, financial situations, or personal details. Skip those — don't draft a reply that could be traced back to the employer.
4. **Unfamiliar UI.** Halt if the search results page layout changes.
5. **Rate limit.** Halt and surface.
6. **Empathy floor.** If the Scribe's draft opens with "Don't worry" / "AI won't take your job" / "Just learn AI" — the empathy floor is violated. Halt and surface for the Scribe to retry.
7. **Banned phrases re-grep.** Before returning, the Scribe must re-grep the draft for the banned-phrases list.
8. **Preachy floor.** If the Scribe's draft reads like a corporate coach or a LinkedIn influencer ("you need to upskill", "the future is bright"), the preachy floor is violated. Halt and surface.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Bridge offline | `mavis browser status` shows `not connected` | Halt; tell operator to load Chrome extension |
| Login prompt | snapshot shows Sign in / Log in | Halt; tell operator to log in |
| Rate limit | snapshot shows rate limit OR `mavis browser` returns 429 | Halt; surface; recommend waiting 10+ minutes |
| Zero results | snapshot has no author blocks | Halt; report "no posts matching this query — try a different angle" |
| Scribe violates the empathy floor | draft opens with "Don't worry" / "AI won't take your job" | Halt; surface for Scribe to retry |
| Scribe violates the preachy floor | draft reads like a corporate coach | Halt; surface for Scribe to retry |
| Scribe returns a generic tactical play ("learn AI tools") | draft is vague on the specific tool/task/time | Halt; surface for Scribe to retry with a specific play |
| Scribe returns a draft > 280 chars | file output | Halt; surface the over-limit draft for operator review |
| Scribe spawn fails | dispatch error | Halt; surface the spawn error |
| Source post is too vague for a tactical play | source text is general (e.g., "AI scares me") without specifics | Skip the source post; the Scribe can't draft a useful reply without specifics |

## Verification

After each Scribe reply section is written:
1. `ls -la` confirms the file exists and contains the new reply section
2. The reply's character count is 180-280 (target 180-260)
3. The reply opens with empathy (Beat 1), pivots to tactical (Beat 3) — no "Don't worry" / "you need to" / "follow for more" openers
4. The tactical play is specific (named tool, named task, named time window) — not generic
5. The banned-phrase re-grep ran
6. The ledger is appended

## Cross-reference

- `x-engagement-hunter` — sibling skill for value-add replies to large accounts. Different audience, different angle. Pillar 6 (hype) vs Pillar 2 (trades) by default. Empowerment-hunter targets Pillar 5 (job defense).
- `x-hype-translator` — sibling skill for "what does this new tool actually do for an SMB" posts. Empowerment-hunter is the inbound-pipeline; hype-translator is the broadcast-pipeline. Both serve Pillar 5 + 6 with different rhythms.
- `x-niche-scraper` — for the wider market scan (top 10 by query)
- `x-bookmark-parser` — for the user's own curated saves
- `mavis browser` CLI — the underlying tool surface
- The Content Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — consumes the source post + the Aggressive Empathy task spec
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`) — the load-bearing voice source (Pillar 5)
- `team-config.md` — the dispatch protocol for spawning the Scribe
