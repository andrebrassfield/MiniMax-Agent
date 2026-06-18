---
name: x-lead-qualifier
description: |
  Monitor @DreTheSalesGuy's X mentions, replies, and DMs for intent signals
  (specific questions about AI automation, pain points like "I need help with
  this" or "How does that integration work?"), and dispatch the Scribe to
  draft a "Qualification DM" — a tiny, high-value technical tip ending with
  a "Low-Friction CTA" (e.g., "DM me 'AUDIT' if you want me to look at your
  current stack for free"). Hard constraint: NO SELLING. Only qualification.
  The technical tip must be genuinely useful, not bait-and-switch. Read-only
  against x.com; writes only to a draft queue at `03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl`.
  Drafts are reviewed and sent manually. Triggers: "run x-lead-qualifier",
  "scan for DMs", "lead qualifier", "check mentions for leads", "qualification
  DM".
---

# x-lead-qualifier

The inbound lead-qualification funnel. Turns
@DreTheSalesGuy's X engagement (mentions, replies, DMs)
into qualified leads. Detects intent signals, dispatches
the Scribe to draft a "Qualification DM" (no selling, just
qualification), writes the draft to a queue for manual
review.

**Lead qualification is NOT selling.** The DM's job is
to figure out if a lead is a good fit *before* pitching.
The DM provides genuine value (a tiny technical tip) and
ends with a low-friction CTA (the lead types a keyword
to self-qualify).

## When to run

**Primary trigger:** cron at scheduled cadence (every
2-4 hours during business hours, or daily at 09:00 /
14:00 / 18:00 CT).

**Manual triggers:**
- "run x-lead-qualifier"
- "scan mentions for leads"
- "qualification DM check"
- "any new leads today?"
- "process the DMs"

**Do NOT run for:**
- Outbound prospecting (this skill is inbound-only —
  it processes engagement that came to @DreTheSalesGuy,
  not cold outreach)
- DM responses to drafts already in the queue (the
  queue is the user's review surface; the skill doesn't
  re-process pending drafts)
- Spam / bot accounts (filter by follower count,
  account age — see `references/filter-rules.md`)
- Posts that are pure praise ("Great post!") with no
  intent signal
- Slander / harassment / negative sentiment (handled
  by `x-engagement-hunter` differently or escalated,
  not qualified)

## Inputs

| Input | Default | Required |
|---|---|---|
| Engagement surface | mentions + replies + DMs | no |
| Lookback window | 24 hours | no |
| Min follower count (spam filter) | 50 | no |
| Min account age (spam filter) | 30 days | no |
| CTA keyword (default) | `AUDIT` | no — operator can override per run |
| Output queue | `03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl` | no |

## The 5 intent signal types

The skill classifies incoming engagement into 5 intent
types. Full filter rules + classification in
`references/filter-rules.md`. The skill only drafts
DMs for engagement that matches one of these types
*and* has a confidence score ≥ 0.6.

| Type | Pattern | Why qualifies |
|---|---|---|
| **`ai_automation_question`** | "How does that integration work?", "What stack are you using?" | Specific question about AI tools |
| **`pain_point_statement`** | "I need help with this", "We're losing $X to Y", "I tried Z and it didn't work" | Expressed pain |
| **`integration_inquiry`** | "How does X integrate with Y?" | Specific integration question |
| **`job_defense_question`** | "How do I learn this?", "Where do I start?" | Skill/learning gap |
| **`operational_distress`** | "My VAs are burning out", "We're scaling and breaking" | Operational scaling pain |

Below 0.6 confidence → skip (too ambiguous for a
qualification DM).

## The 7-step procedure (the load-bearing structure)

The SKILL.md only carries the 7-step list. Full bash
commands in `references/procedure.md`. The Scribe
dispatch contract in `references/scribe-task-spec.md`.
The voice discipline in `references/voice-discipline.md`.

| # | Step | What it does |
|---|---|---|
| 1 | **Verify bridge** | `mavis browser status` — HALT if not connected |
| 2 | **Open X notifications** | `mavis browser tool open_tab` with `https://x.com/notifications` |
| 3 | **Extract + filter engagement** | Wait 5-7s, snapshot, extract mentions + replies + DM notifications, filter by follower count / account age / spam signals / sentiment, classify into 5 intent types with confidence score |
| 4 | **Dispatch Scribe** | For each intent-qualified candidate (confidence ≥ 0.6), `mavis communication send --command spawn` with the Scribe's task spec |
| 5 | **Write the draft to the queue** | Scribe appends to `03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl` |
| 6 | **Update the leads ledger** | Append a one-line entry to the rolling `qualification-dms.mdl` |
| 7 | **Return summary to operator** | Count of candidates → qualified → drafted, queue file path, halt conditions, suggested next action |

## The "no selling" rule (the load-bearing discipline)

**NO SELLING. ONLY QUALIFICATION.** The DM is the first
step of a sales funnel, not a sales pitch. The lead is
asking a question; the DM answers it with genuine value.
The CTA at the end is a low-friction offer, not a hard
sell.

**The DM must:**
1. **Acknowledge** the lead's specific question/pain
2. **Provide value** — a tiny, genuine technical tip
   that helps the lead even if they never reply
3. **Offer a low-friction next step** — a "DM me
   'AUDIT' for a free stack review" or similar

**The "low-friction CTA" is acceptable because:**
- It's free (no cost barrier)
- It's self-qualifying (lead types "AUDIT" → they're
  warm)
- The technical tip is genuine value (the lead gets
  something even if they don't engage)

**What the DM must NOT do:**
- Hard-sell a service ("Buy my $5k/month retainer")
- Pressure a timeline ("Sign up this week for 50% off")
- Make claims that aren't true ("This will 10x your
  revenue")
- Promise outcomes the operator can't deliver
- Use scarcity tactics ("Only 3 spots left this month")
- Use manipulative copy ("You can't afford to miss
  this")

**The Scribe's task spec** (the load-bearing contract)
in `references/scribe-task-spec.md` enforces this as a
hard rule, with explicit examples of forbidden phrases.

## The DM structure (3 sections, the Scribe's output)

1. **Acknowledge the specific question/pain** (1-2
   sentences) — "Saw your post about [specific topic].
   The [specific thing they asked about] is exactly where
   most teams [common failure]."
2. **Tiny high-value technical tip** (2-3 sentences
   with a real number or insight) — "Quick tip: [specific
   technical insight]. The [specific metric/result] is
   the test. If your [current state] is below
   [threshold], you have a [specific problem]."
3. **Low-friction CTA** (1 sentence) — "If you want me
   to look at your current stack for free, DM me 'AUDIT'
   and I'll spend 15 minutes on it."

The Scribe self-checks against the verification checklist
in `references/scribe-task-spec.md` before returning. If
any check fails, the Scribe halts.

## Output (the queue file)

The Scribe appends to
`03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl`.
One entry per detected intent signal + draft:

```markdown
- 2026-06-16 14:23 CT — @<handle> · <post-URL-or-DM-source> · intent: <signal-type>
  - Source: "<verbatim quote of the source text, ≤200 chars>"
  - Draft (from Scribe):
    > <the drafted DM, with technical tip + low-friction CTA>
  - Status: pending_review
  - Confidence: <0.0-1.0>
```

The queue is the operator's review surface. The
operator opens the queue, reads each draft, decides:
send / edit / skip / hold.

The skill never sends. The operator does.

## Hard constraints

1. **Read-only against x.com.** The skill only navigates
   and snapshots. No clicking on Reply, Repost, Like,
   Follow, DM, Block, Mute, or any other interactive
   affordance.
2. **No credential entry.** If the snapshot shows "Sign
   in to X" / "Log in", halt and surface.
3. **No DM button clicks.** DMs are a sensitive surface.
   The skill does not open the DM composer, type into
   any DM textarea, or send a DM. Drafts go to a file;
   the user copy-pastes manually.
4. **No outbound actions.** The skill is INBOUND ONLY.
   It processes engagement that came to @DreTheSalesGuy.
5. **Per-account scope.** Scoped to @DreTheSalesGuy only.
   The skill does not navigate to other accounts'
   notifications.
6. **Mass-scrape guard.** If the lookback window has >
   100 candidate notifications, halt and ask the
   operator to narrow. 100 is the upper bound for a
   single run.
7. **Rate-limit halt.** If `mavis browser` returns 429
   or the snapshot shows a rate-limit warning, halt and
   surface. Do not retry-loop.
8. **Unfamiliar UI halt.** If the snapshot shows a
   layout the skill does not recognize, halt and
   surface. Do not guess at field names.
9. **The Scribe's hard-sell check is a HALT.** If the
   Scribe returns a DM that fails the no-hard-sell check
   (CTA check), HALT and surface prominently. The hard
   constraint was violated.

## When the skill HALTs

Halt and escalate to Andre when:
- Bridge offline (H1) — load Chrome extension
- Login prompt (H2) — operator logs in
- > 100 candidates in window (H3) — operator narrows
  the window
- Rate limit (H4) — wait 10+ minutes
- Notifications page is unfamiliar UI (H5) — surface
  for skill update
- Scribe returns off-voice DM (H6) — surface the draft
  for chief review
- **Scribe returns a hard-sell DM** (H7) — HALT and
  surface prominently, the hard constraint was violated
- Queue file is not writable (H8) — fix permissions

The skill is a diagnostic, not an authorization. The
operator decides the action.

## What this skill is NOT

- **Not the Scribe.** The Scribe is the agent that
  drafts. This skill is the inbound detector + Scribe
  dispatcher.
- **Not outbound.** Inbound only. Cold outreach is a
  different skill (not yet built).
- **Not the analytics feedback loop.** That's
  `x-analytics-tracker` (Layer 5 feedback).
- **Not auto-sending.** The operator sends manually. The
  queue is the review surface.
- **Not autonomous.** No selling, no auto-approval.

## Anchoring sources

- **EA contract — 4 workflows, 5 behaviors** —
  `ea-contract.md` — quote verbatim, sharpen to one
  sentence, end with question
- **`x-engagement-hunter`** — sibling for value-add
  replies to large accounts (different scope; this
  skill handles DMs, not replies)
- **Scribe's Hard Rule #10** —
  `03 Projects/X-Content-Engine/agents/scribe.md` —
  "Never publish to x.com" (the lead-qualifier
  respects this — drafts go to a file, not to x.com)
- **Persona load-bearing** —
  `03 Projects/X-Content-Engine/agents/persona.md` —
  voice source for the Scribe's DM drafts

## Cross-reference

- `references/filter-rules.md` — 5 intent types + spam
  filter + classification
- `references/procedure.md` — the 7-step procedure with
  bash commands
- `references/scribe-task-spec.md` — the verbatim Scribe
  task spec (the load-bearing contract)
- `references/voice-discipline.md` — DM-specific voice
  discipline (staccato, no AI fluff, etc.)
- `references/output-format.md` — the queue file format
- `tests/safety-halts.md` — 8 halt conditions + eval
  cases
- `tests/discipline.md` — 5 quality floors (intent
  classification, no-hard-sell, voice match, 3-section
  structure, queue-file-writable)
- `x-engagement-hunter` — sibling for reply pipelines
- `x-bookmark-parser` — for the user's own bookmarks
- `x-niche-scraper` — search-side AI tool scan
- `x-analytics-tracker` — Layer 5 feedback
- The Content Scribe — produces the DM drafts
- The Persona — voice source
- `team-config.md` — dispatch protocol
