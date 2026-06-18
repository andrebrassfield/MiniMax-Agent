---
name: x-value-bomb-dropper
description: Hunt for high-intent operational questions from SMB owners or knowledge workers on X ("how do I automate lead intake", "best way to sync Shopify inventory", "how to build an AI phone agent"), extract one specific question, dispatch the Scribe to draft a pure-value 3-step technical reply that solves the exact problem. Zero sales pitch. Architecture given away for free. Output to drafts/value-bombs-YYYY-MM-DD.md. Uses mavis browser tool against the user's real Chrome. Triggers when the user says "value bomb", "free architecture", "answer a question", "free technical reply", "drop a value bomb", or specifies an operational question query. HARD CONSTRAINT: Read-only. Never click reply/post. Manual publish only. No CTAs. No "DM me." No "book a call." The answer IS the value.
---

# X Value Bomb Dropper

## What this skill does

Searches X for **high-intent operational questions** from real SMB owners and knowledge workers — the people who are actively trying to solve a problem in their business or their job. Examples of target queries:

- "how do I automate lead intake"
- "best way to sync Shopify inventory"
- "how to build an AI phone agent"
- "how to stop missing calls after hours"
- "anyone using AI for customer support"
- "how to integrate my CRM with QuickBooks"
- "best AI tool for drafting proposals"

Extracts the strongest single question from the search results, then dispatches the Content Scribe to draft a **pure-value, 3-step technical reply** in @DreTheSalesGuy's voice that **solves the exact problem the person asked** — architecture, tools, and the step-by-step, given away for free.

This is the supply pipeline for **Pillar 4 (Build Logs / Behind-the-Scenes)** + **Pillar 2 (The Trades)** — the inbound channel where Andre demonstrates technical depth to operators who are actively searching for it. The audience is the person with the question, not the broader X audience. The reply's job is to **make the person say "this just saved me a $5k consultant fee"** — without ever pitching anything.

**Hard constraint: NEVER click the reply button on x.com.** The skill is read-only against the X UI. Drafts go to a file. The user copy/pastes manually. This is non-negotiable — same constraint as `x-empowerment-hunter` and `x-engagement-hunter`.

## The Difference From Sibling Skills

| Skill | Audience | Angle | Reply shape | Sales posture |
|-------|----------|-------|-------------|---------------|
| `x-empowerment-hunter` | Anxious employee | Empathy + tactical AI play | Short, emotional, 1-2 sentences pivoting | Zero sales. Tactical advice. |
| `x-engagement-hunter` | AI influencers / large accounts | Value-add on their thread | Concise tactical add-on | Zero sales. Thought leadership. |
| `x-hype-translator` | Broad X audience | "What this new tool actually does" | Practical breakdown for SMBs | Zero sales. Filter. |
| **`x-value-bomb-dropper`** | **SMB owner / operator with a specific question** | **Solve the question in 3 steps** | **3-step technical, names tools, gives away the architecture** | **Zero sales. Pure technical answer. The answer IS the value.** |

The value-bomb-dropper is the **highest-trust reply in the engine** — it's where Andre pays forward the technical knowledge that makes him the authority. The whole reply IS the value proposition. If there's even a hint of a sales CTA, the reply fails.

## When to run

**Trigger phrases:**
- "value bomb" / "drop a value bomb" / "free architecture"
- "answer a question" / "answer an operational question"
- "free technical reply" / "give away the architecture"
- "draft a value-bomb reply" / "Pillar 4 reply" / "Pillar 2 reply"

**Do NOT run for:**
- Replies to AI influencers / pundits (those are the engagement-hunter's domain)
- Replies to anxious employees (those are the empowerment-hunter's domain)
- The user's own posts (no reply needed)
- Mass-reply workflows (this skill is single-target by design; one source post → one draft reply per run)
- Posts that are not actually asking an operational question (skip the rhetorical "what do you think about AI" / "is anyone else worried" posts — those belong to the engagement-hunter)
- Non-X platforms

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Operational question query | (none — must be specified) | **yes** |
| Search tab | `Latest` | no — `Top` for established questions |
| Capture depth | top 5 posts | no — 1, 5, 10 |
| Engagement floor | 5 likes (low — question posts often have low reach) | no |
| Destination dir | `03 Projects/X-Content-Engine/drafts/` | no |
| File naming | `value-bombs-YYYY-MM-DD.md` (one rolling file per day) | no |

**Operational question query patterns:**
- "how do I automate X"
- "best way to X"
- "how to build an AI X"
- "anyone using X for Y"
- "how to integrate X with Y"
- "recommend a tool for X"
- "how do you handle X"

Operator can supply any custom query. The skill does NOT auto-rotate queries — the operator picks the angle.

**Anti-pattern queries** (do NOT use these — they surface the wrong audience):
- "AI taking my job" (→ empowerment-hunter)
- "worried about AI" (→ empowerment-hunter)
- "is AI overhyped" (→ engagement-hunter)
- "best AI tool" (too generic, surfaces AI influencers)

## Outputs

A markdown file at `03 Projects/X-Content-Engine/drafts/value-bombs-YYYY-MM-DD.md` (one rolling file per day, all targets in that day aggregated). Each reply section contains:

- A header with the source author's handle + post URL + a quoted excerpt of their post
- The full text of the source question (verbatim)
- The 3-step technical reply text (raw, ready to copy/paste into x.com)
- A character count
- A "Why this reply" rationale explaining the 3 steps + why this stack is the right play for the specific question
- A "Notes for Andre" section flagging any specifics to verify (e.g., "this assumes the person has a Shopify Plus plan; if they're on basic Shopify, the API rate limits change the math" or "step 2 references Vapi specifically; you may want to soften to 'any low-latency voice engine' depending on your brand voice that week")
- An unchecked approval box

The skill returns a one-paragraph summary to the operator with: file path, target count, and a one-line note about which reply is the strongest candidate to publish first.

## The Hard Constraint (READ THIS)

**DO NOT click the reply button on x.com. EVER.** The skill is read-only against the X UI. The draft is written to a file. The user copy/pastes the draft into x.com manually after approval.

This is the same constraint as `x-empowerment-hunter` and `x-engagement-hunter`. The skill explicitly forbids:
- Clicking the reply button
- Clicking the quote-reply button
- Typing into any reply textarea
- Submitting a reply
- Following the source author
- Liking the source post (would change the account state)
- DMing the source author

The skill is "draft a reply" — it is NOT "post a reply."

## The Zero-Sales-Pitch Constraint (READ THIS TOO)

**The reply contains the answer. The reply contains ONLY the answer.** No sales CTA. No "DM me." No "book a call." No "link in bio." No "I run an agency that does this." No "happy to chat offline." The architecture is given away for free, in public, on the timeline. The trust is the moat.

This is the **most-load-bearing constraint in the entire skill.** A value-bomb reply that ends with "DM me to set this up for you" is a pitch, not a value bomb. The whole engine collapses if the Scribe pads the reply with a CTA.

The Scribe's hard verification step is: re-grep the reply for `DM me`, `book a call`, `link in bio`, `my agency`, `I help companies`, `let's chat offline`, `reach out`, `consulting`, `services`. If any of those phrases appear, the reply fails verification and the Scribe must retry.

## The 3-Step Format (the load-bearing pattern)

Every value-bomb reply should follow this 3-beat structure:

1. **Beat 1 — Name the stack** (1 sentence, 40-70 chars). "Use Vapi + Google Calendar + Zapier." / "Shopify Admin API + a small Node.js middleware + a Postgres ledger." Name the tools. Don't be vague.

2. **Beat 2 — The first concrete step** (1-2 sentences, 80-130 chars). A specific action the person can take this week. "Sign up for Vapi. Connect your Google Calendar. Build a 5-minute voice agent that books a 30-min slot when the caller says 'schedule me in.'" Specific = high-trust.

3. **Beat 3 — The second concrete step + the outcome** (1-2 sentences, 80-130 chars). The follow-on action + the unit-economics payoff. "Wire the calendar slot to ServiceTitan via Zapier. Cost: ~$0.40/call. Replaces a $22/hr CSR. Payback in 3 weeks."

Total: 200-330 chars. **Hard cap 280 for a single tweet, OR ~840 chars if using a 🧵 thread (3 tweets of 280 each).** The Scribe decides based on the source question's complexity.

**Format options (Scribe picks):**
- **Single-tweet format** (target 200-280 chars): dense 3-step. Use only when the question is narrow.
- **Thread format** (🧵 marker on tweet 1, 3 tweets total): use when the question needs the breathing room. Each tweet is a step. Total ~600-840 chars across the 3 tweets.

**Example skeleton (NOT a real draft, just a template):**

> Single-tweet: "Use Vapi + Google Calendar + Zapier. Step 1: sign up for Vapi, connect your Google Calendar, build a 5-min voice agent that books a 30-min slot when the caller says 'schedule me in.' Step 2: wire the slot to ServiceTitan via Zapier. Cost ~$0.40/call. Replaces a $22/hr CSR. Payback in 3 weeks."

> Thread: "Use Vapi + Google Calendar + Zapier. 🧵 1/ Sign up for Vapi. Connect your Google Calendar. Build a 5-min voice agent that books a 30-min slot when the caller says 'schedule me in.' 2/ Wire the calendar slot to ServiceTitan via Zapier. Map the customer's name, address, and slot to the existing job fields. Test with a fake call. 3/ Cost: ~$0.40/call all-in. Replaces a $22/hr CSR. Payback in 3 weeks on volume as low as 8 calls/day."

**The Scribe's job** is to fill in this template with the source-question-specific stack and steps, not to copy the template verbatim. Different questions need different stacks.

## Procedure

### Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected`, **HALT** and tell the operator to load the Chrome extension. Do not proceed with auto-spawned Chromium fallbacks for x.com.

### Step 2: Open the search URL

```bash
mavis browser tool open_tab '{"url":"https://x.com/search?q=<URL-encoded operational question query>&f=live"}'
```

Use `f=live` (Latest) by default — operational question posts are time-sensitive and a real human's "how do I X" post is freshest in Latest. Use `f=top` if the operator wants the most-engaged version of the conversation.

Note the returned `tabId`.

### Step 3: Authentication + load wait + result check

Wait 3-5 seconds. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":3}'
```

**Halt conditions:**
- Snapshot shows "Sign in to X" / "Log in" — operator needs to log in manually
- Snapshot shows a rate-limit warning — HALT, recommend waiting
- URL is not `x.com/search` after navigation
- Zero results — HALT, report "no posts matching this operational question query — try a different angle"

**Proceed conditions:**
- Search results visible, with author handles + post timestamps
- The query is producing real operational question posts (not just AI hype, not just engagement bait)

**Filter heuristic:** the chief should also mentally check that the results contain **actual operational question posts** — a tweet ending in "?" or starting with "how do I" / "anyone using" / "best way to" / "recommend a tool for." Skip the rhetorical "what do you think about AI" posts. Skip the AI influencer threads. The value-bomb is for the operator with the concrete problem.

### Step 4: Extract the top source posts

Parse the snapshot's `text` field. For each post, extract:
- Author handle (real SMB owner or knowledge worker, not an AI influencer — filter out accounts with "AI", "ML", "GPT" in the handle if possible)
- Full post text
- Timestamp (preferring recent)
- Engagement metrics
- The source URL
- The specific operational question being asked (paraphrase in 1 sentence — keep the tools and the verb, drop the noise)

**Do NOT scroll via `press_key`** — same Focus Rule as the other X skills.

**Pick the strongest target** — one post only. Ranking heuristic:
1. Is the question specific enough that a 3-step answer can actually solve it? (Skip vague questions like "what's the best AI tool.")
2. Is the author a real SMB owner / operator / knowledge worker? (Skip AI influencers, founders pitching their own products, anonymous accounts.)
3. Is the engagement floor met (5+ likes, or 0 if it's a brand-new post)?
4. Recency — prefer last 24h.

If no post meets all four, HALT and report "no operational question matching the query — try a different angle."

### Step 5: Dispatch the Scribe

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
You are drafting a "Value Bomb" reply to a target X post in @DreTheSalesGuy's voice. The voice file is at `03 Projects/X-Content-Engine/agents/persona.md`. Read it before drafting. Pillar 2 (The Trades) + Pillar 4 (Build Logs) are the load-bearing references.

**The target post:**
- Author: @<handle>
- URL: <source-url>
- The operational question being asked: <one-sentence paraphrase with the verb and the tool/domain>
- Full text: <full post text>
- Timestamp: <timestamp>
- Engagement: <likes, reposts, replies>

**The Value Bomb reply rules (HARD):**

1. **Solve the exact problem the person asked.** Not a related problem. Not a more interesting problem. The exact problem. If the person asked "how do I sync Shopify inventory with my 3PL?", the answer must address the Shopify → 3PL sync, not "here's how to think about inventory."

2. **Name the stack in the first sentence.** Vapi, ServiceTitan, Shopify Admin API, Zapier, Airtable, Make, n8n, Postgres, Cloudflare Workers — whatever the right stack is for the question. Be specific. "Use a tool" is not a stack. "Use Vapi + Google Calendar + Zapier" is a stack.

3. **Three concrete steps.** Each step is a specific action the person can take this week. The 3-step pattern is load-bearing — see "The 3-Step Format" section in the skill. If a step is "learn the tool" or "figure out the right approach," the step is too vague. Replace it.

4. **Give away the architecture for free.** This is the highest-trust reply in the engine. The architecture IS the value. The trust is the moat. Do NOT hold back details in hopes of converting the reader into a customer — the conversion is the trust itself.

5. **End with the unit economics.** Cost per call, hours saved per week, payback period, dollar number. "~$0.40/call all-in. Replaces a $22/hr CSR." / "Saves 6 hours/week. Pays back in 2 weeks." Anchor the answer in a real number.

6. **ZERO SALES PITCH.** The reply must NOT contain:
   - "DM me"
   - "book a call"
   - "link in bio"
   - "my agency"
   - "I help companies"
   - "let's chat offline"
   - "reach out"
   - "consulting"
   - "services"
   - "if you need help"
   - "happy to walk you through"
   - Any other CTA
   
   The reply ends at the unit-economics line. Period. The answer is the value. There is no follow-on.

7. **Match the voice per persona.md.** Pillar 2 + 4 voice: staccato periods, lead with the punch (the stack), follow with the steps, end with the unit economics. No banned phrases. No "dive into" / "in today's fast-paced world" / "harness the power of." No emoji except 🧵 for thread markers.

8. **No "I will" / "we will" / "let's" openers.** Speak as a peer sharing what worked, not as a consultant pitching what they could do.

9. **Single-tweet vs 🧵 thread — pick the right format.** Use single-tweet (200-280 chars) when the question is narrow. Use 🧵 thread (3 tweets, ~840 chars total) when the question needs the breathing room. The thread format MUST start with the 🧵 emoji on tweet 1.

10. **Banned phrases list is in your Scribe spec.** Re-grep before returning. Also re-grep the **zero-sales-pitch list** above. If any of those phrases appears, the reply fails verification — retry.

**Output format (append to 03 Projects/X-Content-Engine/drafts/value-bombs-YYYY-MM-DD.md, create the file if it doesn't exist; the day-rolling filename is the standard):**

## Value Bomb for @<handle> · <source post timestamp>

**Source:** <source-url>
**Quoted post (excerpt):** "<first 200 chars of source post>..."
**Operational question being answered:** <one-sentence paraphrase with the verb and the tool/domain>
**Format chosen:** <single-tweet | 🧵 3-tweet thread>
**Status:** pending_review

### Reply draft

<the actual reply text here, raw, ready to copy-paste into x.com. If thread, label tweets 1/, 2/, 3/.>

### Character count

<XX / 280 single | XXX / ~840 thread>

### Why this reply

[2-3 sentences: what stack you named, why it's the right stack for THIS question, and how the 3 steps take the person from zero to working solution in a week. If you chose thread format, explain why single-tweet would have lost the breathing room.]

### Notes for Andre

[Any specifics to verify — e.g., "step 2 references Vapi specifically; you may want to soften to 'a low-latency voice engine' if you're not ready to commit to one vendor publicly" or "the unit-economics line assumes the person is missing 8+ calls/day; you may want to scale the math up or down depending on the post's signal" or "this stack assumes a Shopify Plus plan; if the person is on basic Shopify, the API rate limits change the math — flag if the post doesn't reveal their plan tier."]

### Approval

- [ ] approved → copy/paste
- [ ] rejected (reason: ________)
- [ ] needs revision (notes: ________)
```

The chief should spawn the Scribe **once per source post** (not in batch). If 5 source posts are in the capture, the chief picks the strongest one and spawns the Scribe once. Single-target by design — the value-bomb format loses its punch in batch.

### Step 6: Update the value-bombs ledger

Append a one-line entry per reply to `03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — value-bomb to @<handle> (source: <source-url>, Scribe draft, pending)
```

### Step 7: Return summary

Send a one-paragraph summary to the operator:
- File path
- Number of value-bombs drafted (1 by default; single-target by design)
- The strongest reply candidate (one line)
- Any concerns (e.g., "the Scribe flagged 2 of the 5 candidate posts as too vague to answer with a 3-step — those were skipped; one strong target was identified and drafted")

## The Safety Halts (inherited, plus the value-bomb-dropper specifics)

1. **No interaction.** Read-only. Never click reply, quote-reply, like, follow, or DM.
2. **No credential entry.** Login prompts → halt.
3. **Sensitive content skip.** Some question posts mention specific employers, financial situations, or proprietary workflows. Skip those — don't draft a reply that could leak the employer's stack or financials.
4. **Unfamiliar UI.** Halt if the search results page layout changes.
5. **Rate limit.** Halt and surface.
6. **Source post is too vague for a 3-step.** "What's the best AI tool?" / "Should I be using AI?" — these can't be answered with 3 specific steps. Skip the source post; the Scribe can't draft a useful reply without a concrete problem.
7. **Source post is from an AI influencer pitching their own product.** Skip — the value-bomb is for the operator with the problem, not the founder with the pitch.
8. **Scribe violates the zero-sales-pitch rule.** Re-grep for `DM me` / `book a call` / `link in bio` / `my agency` / `I help companies` / `let's chat offline` / `consulting` / `services`. If any of those phrases appears, the reply fails — surface to the operator, do not file.
9. **Scribe returns a generic 3-step.** "Step 1: research the tool. Step 2: try it. Step 3: measure the results." — that's filler. The 3 steps must be specific actions with named tools.
10. **Scribe returns a draft > 280 chars (single-tweet) or > ~840 chars (thread).** File output. Halt; surface the over-limit draft for operator review.
11. **Banned phrases re-grep.** Before returning, the Scribe must re-grep the draft for both the banned-phrases list AND the zero-sales-pitch list.
12. **Scribe pads the answer with "happy to walk you through" / "DM me if you want more detail"** — this is a soft CTA, the same violation. Re-grep for "happy to" / "reach out" / "if you need help" / "let me know if you want."

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Bridge offline | `mavis browser status` shows `not connected` | Halt; tell operator to load Chrome extension |
| Login prompt | snapshot shows Sign in / Log in | Halt; tell operator to log in |
| Rate limit | snapshot shows rate limit OR `mavis browser` returns 429 | Halt; surface; recommend waiting 10+ minutes |
| Zero results | snapshot has no author blocks | Halt; report "no posts matching this query — try a different angle" |
| Source post is too vague | source text is general (e.g., "what's the best AI tool?") | Skip; Scribe can't draft a useful 3-step without specifics |
| Source post is from an AI influencer | handle contains "AI"/"GPT"/"ML" or bio signals "founder" | Skip; this is a pitch, not a question |
| Scribe violates the zero-sales-pitch rule | draft contains any CTA phrase | Halt; surface for Scribe to retry |
| Scribe returns a generic 3-step | draft is vague on the specific tool/task | Halt; surface for Scribe to retry with specific steps |
| Scribe returns a draft > 280 chars (single) or > ~840 chars (thread) | file output | Halt; surface the over-limit draft for operator review |
| Scribe spawn fails | dispatch error | Halt; surface the spawn error |
| All candidate posts fail the filters | none meet the "specific question + real operator + low engagement" bar | Halt; report "no operational question matching the query — try a different angle" |

## Verification

After each Scribe value-bomb section is written:
1. `ls -la` confirms the file exists and contains the new section
2. The reply's character count is 200-280 (single-tweet) or ~600-840 (thread)
3. The reply names a specific stack in the first sentence — no "use a tool" / "find the right platform" filler
4. The reply has 3 concrete steps — each is a specific action with named tools
5. The reply ends with unit economics — a dollar number, a time-saved number, or a payback period
6. The reply contains **zero** sales CTAs (re-grep for `DM me` / `book a call` / `link in bio` / `my agency` / `I help companies` / `let's chat offline` / `consulting` / `services` / `reach out` / `happy to`)
7. The reply contains no banned phrases (re-grep the standard banned-phrases list)
8. The ledger is appended

## Cross-reference

- `x-empowerment-hunter` — sibling for anxiety posts (Pillar 5). Different audience, different angle. Empathy + tactical play, not 3-step architecture.
- `x-engagement-hunter` — sibling for value-add replies to large accounts (Pillar 6 default). Different audience, different angle. One-liner tactical add-on, not 3-step architecture.
- `x-hype-translator` — sibling for "what does this new tool actually do for an SMB" broadcast posts (Pillar 6). Different rhythm — broadcast, not inbound.
- `x-niche-scraper` — for the wider market scan (top 10 by query)
- `x-bookmark-parser` — for the user's own curated saves
- `mavis browser` CLI — the underlying tool surface
- The Content Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — consumes the source question + the Value Bomb task spec
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`) — the load-bearing voice source (Pillar 2 + 4)
- `team-config.md` — the dispatch protocol for spawning the Scribe
