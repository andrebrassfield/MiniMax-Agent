---
name: ea-draft-approval
description: |
  Codifies the **half-loop bridge** between the Scribe's draft queue and
  the post-N publish chain. The Scribe (per `agents/scribe.md` Hard Rule
  #10) writes drafts to `03 Projects/X-Content-Engine/drafts/` but never
  publishes. The post-N cron chain reads from `approved/` and publishes. The
  gap: drafts must move from `drafts/` to `approved/` only after Andre
  approves. This skill codifies Mavis's role as the bridge — propose drafts
  to Andre via Telegram, capture his approval, move approved drafts to
  `approved/`, archive denied drafts, and apply edits when given. The
  procedure: (1) on a daily trigger (default 18:00 CT, after the Scribe's
  daily work, before the 19:00 x-analytics-tracker), scan `drafts/` for
  files modified since the last scan; (2) for each new draft file, parse the
  individual posts (the Scribe's batch files contain 2-4 posts each, separated
  by `## Draft N` headers); (3) post each draft to Telegram as a separate
  proposal with: the post text verbatim, a 1-2 line rationale (which pillar,
  which audience), and the explicit "Reply: approve / deny / edit"
  instruction; (4) record the proposal in the state file at
  `~/.mavis/agents/mavis/crons/ea-draft-approval.state.json` with a stable
  draft_id, the post text, the proposal timestamp, and the response status
  (open / approved / denied / edited); (5) on Andre's reply, match the reply
  to a draft_id, update the state, and act: approved → move to `approved/`
  (preserve the batch file structure for the post-N chain); denied → move
  to `archive/denied/`; edited → apply the edit, then move to `approved/`.
  Use this skill when the Scribe writes new drafts, when the daily cron
  fires, and on Andre's Telegram reply about a draft. Do NOT load for the
  post-N publish chain (that's the post-N cron), for the Scribe's drafting
  work (Scribe is its own agent), for the Analytics feedback loop (that's
  a different cron), or for any draft that's already in `approved/` (the
  bridge is between `drafts/` and `approved/`, not after).
---

# ea-draft-approval

The Scribe → Andre → post-N bridge. The Scribe writes
drafts but never publishes (Hard Rule #10). The post-N
chain publishes from `approved/`. Mavis closes the gap:
propose drafts to Andre, capture approval, route approved
drafts to the post-N chain.

**The discipline:** the Scribe does the writing, Andre
does the approving, Mavis does the routing, the post-N
chain does the publishing. Four roles, three handoffs,
zero ambiguity. This skill codifies the second and third
handoffs (Mavis ↔ Andre, Mavis → post-N).

## The 5-part closed loop (per `ea-closed-loop-builder`)

| # | Part | What it does |
|---|---|---|
| 1 | **Trigger** | Daily at 18:00 CT (after the Scribe's daily work, before the 19:00 x-analytics-tracker); OR on-demand when a new draft is detected in `drafts/` |
| 2 | **Signal + context** | Read the Scribe's batch file, parse the individual posts, check the persona for pillar alignment, check the content_brain for the source idea |
| 3 | **Action** | Post each draft to Telegram with: verbatim text, 1-2 line rationale, "Reply: approve / deny / edit" |
| 4 | **Eval gate** | Andre's reply (text-based, one of: approve / deny / edit + new text). Mavis matches the reply to a draft_id in the state file |
| 5 | **Stop condition** | Reply captured → action taken (move / archive / edit) → state updated → next draft proposed → cron ends |

## When to run

**Auto-trigger conditions (load the skill when):**
- The daily cron fires at 18:00 CT
- Andre replies to a draft proposal with: "approve",
  "deny", "edit", "ship it", "kill it", or any of:
  "approved", "yes", "no", "denied", or a draft text that
  starts with "Draft N:" (indicates an edit)
- Mavis detects a new file in `drafts/` during a normal
  session

**Do NOT load for:**
- The post-N cron chain (publishes from `approved/`,
  doesn't propose)
- The Scribe's drafting work (Scribe is its own agent,
  separate from Mavis)
- The Analytics feedback loop (reads `performance_log`
  after posts land)
- Drafts already in `approved/` (the bridge ends at
  `approved/`, not after)
- The X.com compose flow (handled by the post-N cron's
  `mavis browser tool` procedure)
- Cross-agent territory (this is Mavis's surface; do
  not propose drafts on behalf of Hermes or OpenClaw)

## Inputs

| Input | Default | Required |
|---|---|---|
| Cron schedule | `0 18 * * *` (daily 18:00 CT) | yes (configured at create time) |
| Scribe queue | `03 Projects/X-Content-Engine/drafts/` | yes |
| Approve queue | `03 Projects/X-Content-Engine/approved/` | yes |
| Deny archive | `03 Projects/X-Content-Engine/archive/denied/` | yes (create if missing) |
| Persona | `03 Projects/X-Content-Engine/agents/persona.md` | yes (read for pillar check) |
| State file | `~/.mavis/agents/mavis/crons/ea-draft-approval.state.json` | yes (auto-managed) |

## The 5-step procedure (overview)

The full 5-step procedure with bash commands lives in
`references/procedure.md`. The high-level flow:

1. **SCAN** — find drafts modified since the last run
   (uses `state.last_scan_at` as the boundary)
2. **PROPOSE** — post each draft to Telegram with
   verbatim text + 1-2 line rationale + explicit
   "approve / deny / edit" instruction; record in state
   file with stable `draft_id`
3. **CAPTURE** — match Andre's reply to a draft_id
   (approve / deny / edit patterns in
   `references/reply-patterns.md`)
4. **ACT** — move to `approved/`, archive to
   `archive/denied/`, or apply the edit (full bash
   patterns in `references/procedure.md`)
5. **UPDATE** — the post-N chain picks up `approved/`;
   update state with `acted_at` + action

The state file schema in `references/state-schema.md`.
The Scribe dispatch contract in
`references/state-schema.md` (the state is auto-managed,
not dispatched).

## Hard constraints

1. **Verbatim post text.** The Telegram proposal shows
   the post text EXACTLY as the Scribe wrote it. No
   reformatting, no shortening, no commentary. Andre
   needs to see what the Scribe wrote, not Mavis's
   interpretation.
2. **One Telegram message per draft.** If the draft is
   too long, split into N/N with the approval instruction
   only in the last message. Do NOT collapse multiple
   drafts into one message.
3. **Stable draft_id.** The draft_id is
   `<file>:<draft-N>:<sha256-of-post-text>`. Mavis matches
   Andre's reply to this ID. If the Scribe rewrites the
   file between the proposal and the reply, the sha256
   changes; treat as a new draft (re-propose, don't act
   on the stale reply).
4. **The Scribe's Hard Rule #10 binds Mavis too.** Mavis
   does not auto-approve. Mavis does not auto-publish.
   Mavis proposes, Andre decides. The bridge is
   propose → decide → route.
5. **State is append-only.** New proposals append; status
   changes are updates, not edits. The audit trail is the
   value.
6. **Multi-draft batch files stay together until
   approved.** If a batch has 3 drafts and Andre approves
   1, the source file remains in `drafts/` until all 3
   are decided. Splitting a batch mid-decision is not
   allowed.
7. **Mavis territory only.** Do not propose drafts on
   behalf of other agents' queues. This skill is for the
   X-Content-Engine drafts, not for any other agent's
   pipeline.
8. **Mirror discipline.** The state file is at
   `~/.mavis/agents/mavis/crons/ea-draft-approval.state.json`
   (agent home). Mirror to
   `~/MiniMax-Agent/99 _system/crons/ea-draft-approval.state.json`
   per `ea-skill-evolution` Hard Constraint #6.
9. **No silent-failure.** If the Telegram post fails
   (auth, network), HALT and surface. Do not assume the
   proposal was sent. Same discipline as the post-N
   chain's silent-failure patch.

## When the skill HALTs

Halt and escalate to Andre when:
- Telegram post fails (auth, network) (H1) — surface,
  don't assume the proposal was sent
- State file write fails (H2) — surface
- The Scribe's file is missing or unreadable (H3) —
  surface; the bridge can't propose drafts it can't read
- Andre's reply is ambiguous (not approve/deny/edit) (H4)
  — ask for clarification (one short message:
  "approve / deny / edit?")
- The reply is for a stale draft_id (sha256 mismatch) (H5)
  — re-propose the new draft
- The post-N chain is down (H6) — surface; the bridge
  can route to `approved/` but the post-N chain is the
  publisher

The skill is a diagnostic, not an authorization. The
operator decides the action.

## The closed loop, end-to-end

```
Scribe drafts → Mavis proposes → Andre approves → 
Mavis moves to approved/ → post-N publishes → 
Analytics learns → Scribe's next batch uses the analytics
```

The 4 roles, 3 handoffs, zero ambiguity:
- **Scribe** = writes drafts
- **Mavis** = proposes + routes (this skill)
- **Andre** = approves / denies / edits
- **post-N cron** = publishes from `approved/`

## What this skill is NOT

- **Not the Scribe.** Drafting is the Scribe's job. Mavis
  doesn't write drafts; Mavis proposes them.
- **Not the post-N publish chain.** The post-N cron
  reads `approved/` and publishes. This skill writes to
  `approved/`. The two skills are different handoffs in
  the same loop.
- **Not the Analytics feedback loop.** Analytics reads
  `performance_log` after posts land and writes the
  feedback to the Scribe's backlog. This skill is
  upstream of post-N, not downstream.
- **Not autonomous.** The Scribe's Hard Rule #10 binds.
  Mavis does not auto-approve. Andre decides.
- **Not a memory write.** State is in the cron state
  file, not in Mavis's memory. The skill's behavior is
  fixed; only the data changes per run.

## Anchoring sources

- **EA contract — 4 workflows, 5 behaviors** —
  `ea-contract.md` — quote verbatim, sharpen to one
  sentence, end with question
- **Closed-loop builder — 5-section spec** —
  `ea-closed-loop-builder` (Mavis skill) — Goal / Context
  / Action / Feedback / Stop condition
- **Three-hard-stops discipline** —
  `~/.mavis/agents/mavis/memory/loop-engineering-framework.md`
  — the cron fleet's discipline
- **Scribe's Hard Rule #10** —
  `03 Projects/X-Content-Engine/agents/scribe.md` —
  "Never publish to x.com"
- **Persona load-bearing** —
  `03 Projects/X-Content-Engine/agents/persona.md` — the
  6 pillars + 6 voice examples
- **Mirror-sync.sh gate** —
  `ea-skill-evolution/scripts/mirror-sync.sh` — for the
  state file mirror

## Cross-reference

- `references/procedure.md` — the 5-step procedure with
  bash commands
- `references/state-schema.md` — state file schema +
  Scribe dispatch contract
- `references/reply-patterns.md` — Andre's reply patterns
  (approve / deny / edit) + how Mavis matches them to
  draft_ids
- `references/scribe-batch-format.md` — how the Scribe's
  batch files are parsed (the `## Draft N` headers, the
  multi-draft file structure)
- `tests/safety-halts.md` — 6 halt conditions + eval cases
- `tests/state-discipline.md` — append-only, stable-
  draft_id, no-silent-failure checks
- `tests/multi-draft-discipline.md` — multi-draft batch
  handling (split, archive, edit)
- `ea-closed-loop-builder` — the 5-section spec framework
- `ea-skill-evolution` — Hard Constraint #6 (mirror
  discipline)
- The Scribe's Hard Rule #10 — the load-bearing rule
