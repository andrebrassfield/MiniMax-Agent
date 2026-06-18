---
name: x-lead-qualifier
description: Monitor @DreTheSalesGuy's X mentions, replies, and DMs for intent signals (specific questions about AI automation, pain points like "I need help with this" or "How does that integration work?"), and dispatch the Scribe to draft a "Qualification DM" — a tiny, high-value technical tip ending with a "Low-Friction CTA" (e.g., "DM me 'AUDIT' if you want me to look at your current stack for free"). Hard constraint: NO SELLING. Only qualification. The technical tip must be genuinely useful, not bait-and-switch. Read-only against x.com; writes only to a draft queue at `03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl`. Drafts are reviewed and sent manually. Triggers: "run x-lead-qualifier", "scan for DMs", "lead qualifier", "check mentions for leads", "qualification DM".
---

# X Lead Qualifier

## What this skill does

Turns @DreTheSalesGuy's X engagement surface (mentions, replies, DMs) into a lead-generation funnel. The skill:

1. **Monitors** the incoming engagement surface for **intent signals** — specific questions about AI automation, expressed pain points, or integration inquiries.
2. **Detects** the signal via pattern matching on the incoming text. Intent signals include:
   - Specific questions about AI automation ("How does that integration work?", "What stack are you using?")
   - Pain-point statements ("I need help with this", "We're losing $X to Y", "I tried Z and it didn't work")
   - Job-defense / leverage signals ("How do I learn this?", "Where do I start?")
   - Operational distress ("My VAs are burning out", "We're scaling and breaking")
3. **Dispatches the Scribe** to draft a Qualification DM. The Scribe's task spec includes:
   - The source mention/reply/DM text (verbatim)
   - The detected intent signal type
   - A "no selling, only qualification" hard constraint
   - The DM format requirements (longer than 280 chars, conversational, technical tip + low-friction CTA)
4. **Writes the draft** to a queue file for the operator's manual review. The skill never sends DMs. Never publishes. Never interacts with x.com beyond read-only extraction.

The CTA is a **self-qualifying action** — the lead types "AUDIT" (or whatever keyword) → they're warm → the operator can then decide whether to do a real sales conversation. This is **lead qualification**, not selling. The distinction is load-bearing.

## When to run

**Primary trigger:** cron at scheduled cadence (suggested: every 2-4 hours during business hours, or daily at 09:00 / 14:00 / 18:00 CT).

**Manual triggers:**
- "run x-lead-qualifier"
- "scan mentions for leads"
- "qualification DM check"
- "any new leads today?"
- "process the DMs"

**Do NOT run for:**
- Outbound prospecting (this skill is inbound-only — it processes engagement that came to @DreTheSalesGuy, not cold outreach)
- DM responses to drafts already in the queue (the queue is the user's review surface; the skill doesn't re-process pending drafts)
- Spam / bot accounts (filter by follower count, account age, verified status — see Step 3)
- Posts that are pure praise ("Great post!") with no intent signal (no question, no pain point, no action interest)
- Slander / harassment / negative sentiment (these are handled by `x-engagement-hunter` differently or escalated, not qualified)

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Engagement surface | mentions + replies + DMs | no |
| Lookback window | 24 hours | no |
| Min follower count (spam filter) | 50 | no |
| Min account age (spam filter) | 30 days | no |
| CTA keyword (default) | `AUDIT` | no — operator can override per run |
| Output queue | `03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl` | no |

## Outputs

Append-only markdown ledger (`.mdl` format, one entry per detected intent signal + draft):

```markdown
- 2026-06-16 14:23 CT — @<handle> · <post-URL-or-DM-source> · intent: <signal-type>
  - Source: "<verbatim quote of the source text, ≤200 chars>"
  - Draft (from Scribe):
    > <the drafted DM, with technical tip + low-friction CTA>
  - Status: pending_review
  - Confidence: <0.0-1.0, how confident the intent detection was>
```

The queue is the operator's review surface. The operator opens the queue, reads each draft, decides:
- Send as-is
- Edit then send
- Skip (no fit)
- Hold (warm up the lead first)

The skill never sends. The operator does.

## The Hard Constraint (READ THIS)

**NO SELLING. ONLY QUALIFICATION.** This is the load-bearing rule. The Scribe's task spec enforces it.

A "Qualification DM" is the **first step** of a sales funnel — figuring out if a lead is a good fit *before* pitching. It is NOT a sales pitch. The DM's job is to:
1. **Acknowledge** the lead's specific question/pain
2. **Provide value** — a tiny, genuine technical tip that helps the lead even if they never reply
3. **Offer a low-friction next step** — a "DM me 'AUDIT' for a free stack review" or similar

The "low-friction CTA" is acceptable because:
- It's free (no cost barrier)
- It's self-qualifying (lead types "AUDIT" → they're warm)
- The technical tip is genuine value (the lead gets something even if they don't engage)

**What the DM must NOT do:**
- Hard-sell a service ("Buy my $5k/month retainer")
- Pressure a timeline ("Sign up this week for 50% off")
- Make claims that aren't true ("This will 10x your revenue")
- Promise outcomes the operator can't deliver
- Use scarcity tactics ("Only 3 spots left this month")
- Use manipulative copy ("You can't afford to miss this")

**The Scribe's task spec includes this constraint as a hard rule** (re-stated in the dispatch prompt), with explicit examples of forbidden phrases.

## The Scribe Dispatch (the load-bearing step)

The x-lead-qualifier dispatches the Scribe with a task spec tailored to DMs (not posts). The Scribe's system prompt is post-focused, so the dispatch prompt overrides the post format and adds DM-specific constraints.

### Dispatch command

```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{
    "agent": "x-scribe",
    "model": "MiniMax-M2.7",
    "prompt": "<task spec below>"
  }'
```

### Task spec template (passed to the Scribe)

```
You are drafting a **Qualification DM** for @DreTheSalesGuy. This is NOT a post. This is a direct message response.

**Source (the inbound engagement that triggered this):**
- Author: @<handle>
- Source URL: <post-URL or DM-source>
- Source text (verbatim): "<the verbatim quote, ≤500 chars>"
- Detected intent: <"ai_automation_question" | "pain_point_statement" | "integration_inquiry" | "job_defense_question" | "operational_distress">

**The voice (loaded from `03 Projects/X-Content-Engine/agents/persona.md`):**
- @DreTheSalesGuy's voice: staccato periods, lead with a punch, follow with unit economics, no AI fluff
- For DMs: more conversational than posts, longer (300-500 words is fine), no 280-char limit, no banned-phrase list from the post context (the banned phrases are for posts; DMs are direct conversation)
- Banned in DMs: "dive into", "delve into", "unlock", "game-changer", "harness the power of", "in today's fast-paced world", "at the end of the day", "let's unpack this"

**The hard constraint (READ THIS):**
- **NO SELLING. ONLY QUALIFICATION.** The DM is the first step of a sales funnel, not a sales pitch. The lead is asking a question; you answer it with genuine value. The CTA at the end is a low-friction offer ("DM me 'AUDIT' for a free stack review"), not a hard sell.
- The technical tip in the body must be GENUINELY useful — not a teaser, not bait-and-switch. The lead gets value even if they never reply.
- The CTA must be:
  - Free (no cost barrier)
  - Self-qualifying (lead types the keyword → they're warm)
  - Single-step (one action, not a "schedule a call" funnel)

**The DM structure (3 sections):**

1. **Acknowledge the specific question/pain** (1-2 sentences)
   > "Saw your post about [specific topic]. The [specific thing they asked about] is exactly where most teams [common failure]."

2. **Tiny high-value technical tip** (2-3 sentences with a real number or insight)
   > "Quick tip: [specific technical insight]. The [specific metric/result] is the test. If your [current state] is below [threshold], you have a [specific problem]."

3. **Low-friction CTA** (1 sentence)
   > "If you want me to look at your current stack for free, DM me 'AUDIT' and I'll spend 15 minutes on it."

**The output format:**

Write to: `03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl` (append, do not overwrite). Use the queue entry format from the Outputs section.

**The verification checklist (the Scribe self-checks before returning):**
1. The DM has the 3 sections (Acknowledge / Tip / CTA) in order
2. The technical tip is genuinely useful (a real number, a real insight, not "you should consider X")
3. The CTA is free + self-qualifying + single-step
4. No hard-sell language (no "buy", no "sign up", no "this week only", no "scarcity")
5. The voice matches the persona (staccato, no AI fluff, no "dive into" / "delve into")
6. The DM is conversational (talks TO the lead, not AT them)

**Halt conditions (the Scribe halts on any of these):**
- The source text is < 10 chars (too thin to qualify against)
- The detected intent is below confidence threshold (default 0.6)
- The persona file is missing
- The technical tip would require making up facts (halt and surface the gap)

**The return summary (the Scribe returns to the chief):**
- File path written
- Source handle + intent type + confidence
- 1-line preview of the drafted DM
- Any halt conditions / blockers
```

## The Procedure

### Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected`, **HALT** and tell the operator to load the Chrome extension per `mavis browser install` output. Do not proceed with auto-spawned Chromium fallbacks for x.com.

### Step 2: Open the X notifications tab

```bash
mavis browser tool open_tab '{"url":"https://x.com/notifications"}'
```

Note the returned `tabId`.

### Step 3: Wait for the page to render, then extract engagement

Wait 5-7 seconds for the page to render. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":3}'
```

Extract from the snapshot:
- Mentions: post handle + post text
- Replies: same
- DM notifications (X shows a count + a few recent senders)

Filter by:
- **Min follower count** (default 50) — skip bot accounts
- **Min account age** (default 30 days) — skip burner accounts
- **Verified status** — optional, default to include all
- **Sentiment** — skip pure praise ("Great post!") with no question or pain point
- **Spam signals** — skip accounts with "crypto giveaway" / "follow back" / etc. in profile

For each filtered candidate, classify the intent signal:
- `ai_automation_question` — specific question about AI tools, integrations, stacks
- `pain_point_statement` — expressed pain ("we're losing X", "I need help with Y")
- `integration_inquiry` — "How does X integrate with Y?"
- `job_defense_question` — "How do I learn this?" / "Where do I start?"
- `operational_distress` — "My VAs are burning out" / "We're scaling and breaking"

Each candidate gets a confidence score (0.0-1.0). Below 0.6 → skip (too ambiguous for a qualification DM).

### Step 4: For each candidate, dispatch the Scribe

For each intent-qualified candidate (confidence ≥ 0.6), call the Scribe with the task spec template. Each dispatch is a separate `mavis communication send` call.

**Halt conditions for the dispatch:**
- Scribe system prompt returns "persona file missing" → halt, surface to operator
- Scribe returns a DM that fails the verification checklist → halt, surface the draft for review
- Dispatch error (timeout, spawn failure) → halt, surface

### Step 5: Write the draft to the queue

The Scribe writes to `03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl`. The skill's job is to verify the file was written and the entry has the required sections.

### Step 6: Update the leads ledger

Append a one-line entry to `03 Projects/X-Content-Engine/queue/qualification-dms.mdl` (the rolling ledger; the daily file is the per-day snapshot):

```markdown
- 2026-06-16 14:23 CT — @<handle> · intent: <type> · confidence: <0.0-1.0> · drafted by Scribe · status: pending_review
```

### Step 7: Return summary to operator

Send a one-paragraph summary:
- Number of candidates scanned
- Number of intent-qualified (confidence ≥ 0.6)
- Number of drafts written to the queue
- Queue file path
- Halt conditions, if any
- Suggested next action (operator reviews the queue, sends the drafts that fit)

## The Hard Safety Constraints (READ THIS)

1. **Read-only against x.com.** The skill only navigates and snapshots. No clicking on Reply, Repost, Like, Follow, DM, Block, Mute, or any other interactive affordance. The skill extracts text + URLs from the snapshot only.
2. **No credential entry.** If the snapshot shows "Sign in to X" / "Log in", halt and surface. The user logs in manually; the skill does not type credentials.
3. **No DM button clicks.** DMs are a sensitive surface on x.com. The skill does not open the DM composer, type into any DM textarea, or send a DM. The drafts go to a file; the user copy-pastes manually.
4. **No outbound actions.** The skill is INBOUND ONLY. It processes engagement that came to @DreTheSalesGuy. It does not cold-DM prospects, follow accounts, or post content.
5. **Per-account scope.** Scoped to @DreTheSalesGuy only. The skill does not navigate to other accounts' notifications.
6. **Mass-scrape guard.** If the lookback window has > 100 candidate notifications, halt and ask the operator to narrow. 100 is the upper bound for a single run.
7. **Rate-limit halt.** If `mavis browser` returns 429 or the snapshot shows a rate-limit warning, halt and surface. Do not retry-loop.
8. **Unfamiliar UI halt.** If the snapshot shows a layout the skill does not recognize (X has changed the notifications UI), halt and surface. Do not guess at field names.

## The Voice Discipline (the Scribe's hard rules, re-stated)

The Scribe's task spec enforces the persona voice. For DMs specifically:
- Staccato periods
- Lead with a punch (the first sentence lands the hardest fact)
- Specific numbers / unit economics
- No AI fluff
- No "dive into" / "delve into" / "unlock" / "game-changer"
- No emoji in body (DMs can use 1-2 emoji if the lead used them, mirroring tone — but defaults to no emoji)
- No "follow for more" / "DM me" (except the specific qualification CTA, which IS allowed)

The Scribe self-checks the draft against the verification checklist before returning. If any check fails, the Scribe halts and surfaces the draft for the chief to review (the chief can override the Scribe's self-check and submit the draft anyway, but the Scribe's default is to halt on a failed check).

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Bridge offline | `mavis browser status` | Halt; tell operator to load Chrome extension |
| Login prompt | snapshot | Halt; tell operator to log in |
| Notifications page is unfamiliar UI | snapshot | Halt; surface the snapshot for skill update |
| Spam / bot candidate | follower count < 50 OR account age < 30d | Skip silently; do not dispatch Scribe |
| Pure-praise candidate (no intent) | sentiment analysis | Skip silently |
| Low confidence intent | confidence < 0.6 | Skip silently; log to "skipped" in the return summary |
| Scribe dispatch fails | dispatch error | Halt; surface the dispatch error |
| Scribe returns off-voice DM | verification check fails | Halt; surface the draft for chief review |
| Scribe returns a hard-sell DM | CTA check fails | **HALT and surface prominently** — the hard constraint was violated |
| Queue file is not writable | `Write` fails | Halt; tell operator to fix permissions |
| > 100 candidates in window | count | Halt; ask operator to narrow the window |
| Rate limit | `mavis browser` 429 or snapshot warning | Halt; do not retry |
| X account suspended or restricted | notifications page shows restriction banner | Halt; surface; do not proceed |

## Verification

After each run:
1. The queue file exists and is non-zero
2. Each entry has the 3 sections (Source / Draft / Status)
3. The drafts match the persona voice (spot-check)
4. **No hard-sell language in any draft** (re-grep before returning) — this is the load-bearing check
5. The leads ledger was appended
6. The Scribe's self-check was applied to each draft (the verification checklist above)
7. The return summary correctly reports the count of candidates → qualified → drafted

## Cross-reference

- `x-engagement-hunter` — drafts replies to other accounts' posts (different scope; this skill handles DMs, not replies)
- `x-bookmark-parser` — parses the operator's own bookmarks (subjective, not engagement)
- `x-niche-scraper` — searches X for top-N posts by query (wider market, not own-account)
- `x-analytics-tracker` — pulls X metrics for our own posts (Layer 5 feedback)
- `03 Projects/X-Content-Engine/agents/persona.md` — voice source for the Scribe's DM drafts
- `03 Projects/X-Content-Engine/agents/scribe.md` — the Scribe's system prompt (post-focused; the lead-qualifier's task spec overrides for DM format)
- `03 Projects/X-Content-Engine/agents/team-config.md` — dispatch protocol for spawning the Scribe
- `mavis browser` CLI — the underlying tool surface

## Notes for the operator (the qualification funnel)

- The "AUDIT" CTA is the default. Operators can override per-run (e.g., "DEMO" for a specific product demo offer, "STACK" for a tech-stack review, "PRICING" for a pricing inquiry).
- The lead qualification funnel has 3 stages: (1) inbound signal detected, (2) DM sent (operator action), (3) lead types the keyword (operator receives the inbound DM). The skill handles stage 1 + draft for stage 2.
- For best results, send the drafted DMs within 24 hours of the original engagement. The lead's interest decays with time.
- A "qualification DM" is not a "pitch DM." The technical tip is the value. The CTA is a low-friction offer. The lead gets value whether or not they engage further.
