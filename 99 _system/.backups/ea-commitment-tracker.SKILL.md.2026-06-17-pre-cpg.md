---
name: ea-commitment-tracker
description: |
  Codifies the capture and tracking of **commitments Mavis makes in chat** —
  promises like "I'll do X", "let me Y", "I owe you Z", "I'll have it by
  Friday". The procedure: (1) detect commitment phrases in the current
  session or in `00 Inbox/` captures; (2) extract the 6 fields —
  commitment, beneficiary, due-by, surface, dependencies, status; (3) write
  to an append-only ledger at `~/.mavis/agents/mavis/commitments.jsonl` (one
  JSON object per line) AND mirror a human-readable view to
  `02 Notes/commitments/YYYY-MM.md`; (4) surface open commitments on the
  next `ea-daily-brief` (under the "open commitments" callout — never bury);
  (5) on delivery, append a status-change line (do NOT edit the original
  line — the audit trail is the value, same discipline as
  `ea-decision-logger`). The discipline: chat-promises evaporate. Mavis said
  she'd do something, the session moved on, the promise is forgotten, Andre
  waits. The ledger survives the EA's context window and surfaces the
  backlog. Auto-trigger when Mavis makes a commitment in the current
  session, when a `00 Inbox/` capture contains a commitment marker, when the
  daily brief is about to run (auto-pull open commitments), and on the EA
  `/commitments` workflow. Do NOT load for Andre's commitments to other
  people (separate ledger at `02 Notes/commitments/andre-to-others.md`),
  for third-party commitments mentioned in passing, for one-shot operational
  promises that complete within the same session, or for skill work in
  other agents' trees (Mavis territory only).
---

# ea-commitment-tracker

The append-only ledger of "Mavis said I'd do." The failure
mode this skill prevents: Mavis says "I'll have the
regulatory anchors by end of day," the session moves on, the
context window is gone, the next session has no idea the
promise was made, and Andre is left waiting. The ledger is
the load-bearing artifact that turns a chat promise into a
tracked deliverable with a due date and a status.

## When to run

**Auto-trigger conditions (load the skill when):**
- The current session contains ≥1 first-person future-tense
  statement with Andre as the implied beneficiary
- A daily brief is about to be written (pull open
  commitments for the brief)
- Andre asks "what did you say you'd do" / "what's on your
  plate" / "what's pending"
- A weekly synthesis is being drafted (cross-reference open
  commitments against the 7d window)
- A `00 Inbox/` capture contains a future-tense first-person
  commitment marker

**Marker phrases:**
"I'll do X" / "let me Y" / "I owe you Z" / "I'll handle that"
/ "by EOD" / "by Friday" / "tomorrow morning" / "in an hour" /
"next session" / "I'll come back to that" / "let me look
into it" / "I should have that" / "I'll have it ready" / "I'll
follow up" / "I'll check on that"

**Do NOT load for:**
- Andre's commitments to other people (separate ledger at
  `02 Notes/commitments/andre-to-others.md`)
- Third-party commitments mentioned in passing ("he said
  he'd send the report")
- One-shot operational promises that complete within the
  same session (e.g., "I'll run that command now")
- Decisions that are already documented in `ea-decision-logger`
  (decisions and commitments are different artifacts)
- Skill work in other agents' trees (Mavis territory only)

## Inputs

| Input | Default | Required |
|---|---|---|
| Commitment text | the verbatim quote from chat | yes |
| Beneficiary | Andre (default for EA-scope commitments) | no |
| Due-by | parse from chat, default: next-session | no |
| Surface | where the deliverable lands | no |
| Dependencies | what blocks this | no |
| Session pointer | the session ID or chat reference | yes |

## The 6-field schema (the load-bearing structure)

Every commitment line is a JSON object with these 6 fields.
**None are optional — the format forces rigor.**

| Field | What it captures | Format |
|---|---|---|
| `commitment` | The verbatim or sharpened quote | First-person, future-tense, ≤2 sentences |
| `beneficiary` | Who the commitment is to | `andre` (default) or named |
| `due_by` | When the deliverable is due | ISO 8601, or `next-session` |
| `surface` | Where the deliverable lands | File path, project, or "TBD" |
| `dependencies` | What blocks this | Array of strings |
| `status` | Lifecycle state | `open` → `in-progress` → `delivered` / `dropped` / `reversed` |

Plus 5 metadata fields: `ts`, `session_pointer`,
`delivered_at`, `reversed_at`, `reversal_reason`. Full
schema + JSON template + field parsing rules in
`references/commitment-schema.md`.

## The 5-step procedure (overview)

1. **DETECT** — pull commitment markers from the current
   session. Marker regex + 3-condition rule (first-person +
   future-tense + deliverable/due date) in
   `references/marker-detection.md`.
2. **EXTRACT** — fill the 6 fields. Sharpen loose wording
   to one specific sentence. Compute `due_by` from chat
   ("by EOD" → today 23:59:59 CT; "by Friday" → next Friday
   23:59:59 CT; "next session" → literal string).
3. **WRITE** — append to `commitments.jsonl` (JSONL) AND
   mirror to `02 Notes/commitments/YYYY-MM.md` (markdown).
   Atomic write + mirror discipline in
   `references/mirror-discipline.md`.
4. **SURFACE** — include in the next daily brief. The callout
   format in `references/daily-brief-callout.md`.
5. **UPDATE** — append on delivery or reversal. **Never edit
   the original line.** The audit trail is the value.

Full procedure details + bash commands in
`references/procedure.md`.

## Hard constraints

1. **Append-only.** Never edit a prior line. Status changes
   are new lines that reference the original timestamp. The
   audit trail is the load-bearing value.
2. **Verbatim or sharpened-to-one-sentence.** Per EA
   contract behavior #1 + #2, never paraphrase loosely. Either
   quote the chat exactly or sharpen to a single specific
   sentence.
3. **Default beneficiary = Andre.** If the commitment is to a
   third party (rare for Mavis), name them explicitly.
4. **Surface open commitments in the daily brief.** Per
   `ea-daily-brief` constraint #4, the brief surfaces the 3
   most time-sensitive commitments. This is not optional.
5. **Overdue = red flag.** Any commitment with `due_by < now`
   and `status = open` is overdue. The next Mavis interaction
   surfaces overdue commitments before any other work.
6. **No fabricated due dates.** If the chat doesn't specify,
   default to `next-session` — the next Mavis-touch is the
   implicit deadline. Do not invent "by tomorrow" or "by EOD"
   that wasn't said.
7. **One-shot operational promises are excluded.** "I'll run
   that command now" — if it completes in the same turn, no
   ledger entry. The ledger is for cross-session promises.
8. **Mirror to `02 Notes/commitments/YYYY-MM.md`.** The JSONL
   is machine-readable; the markdown is human-readable. Both
   must stay in sync.
9. **Mavis territory only.** Do not track commitments for
   other agents (Hermes, OpenClaw, etc.). Cross-team
   commitment tracking is the other agent's job, not Mavis's.
10. **Reversals require a reason.** A `status: reversed` line
    without a `reversal_reason` is a discipline violation.

## What this skill is NOT

The full "what this skill is NOT" list (decisions vs
commitments, project tracker vs ledger, autonomous vs
promiser, exhaustive vs sampled, kanban vs ledger) lives
in `references/what-this-is-not.md`. The short version:
commitments are promises to act, not decisions; the ledger
is for cross-session promises, not single-shot operational
promises; Mavis is the promiser (Mavis→Andre), not the
beneficiary's agent.

## Anchoring sources

- **EA contract — 4 workflows, 5 behaviors** — `ea-contract.md`
  (Mavis memory) — sharpen to one sentence, quote verbatim
- **Append-only audit trail** — `ea-decision-logger` (Mavis
  skill) — same discipline, different artifact
- **Surface open commitments in the daily brief** —
  `ea-daily-brief` (Mavis skill) constraint #4
- **Disk wins over recap** — Mavis MEMORY.md cross-cutting
  discipline
- **Decision rule (reversible + I have authority →
  decide)** — `ea-contract.md` §"Post-decision execution mode"
- **If I have to ask you twice, you failed** — Garry Tan
  (Andre's user memory)
- **Asana / Linear commitment pattern** — operational pattern:
  chat promise → ledger entry → due date → status change on
  delivery
- **Atomic write discipline** — `ea-skill-evolution` hard
  constraint #6 (mirror discipline)

## Cross-reference

- `references/commitment-schema.md` — full 6-field + 5
  metadata field schema, JSON template
- `references/marker-detection.md` — marker regex + 3-condition
  detection rule
- `references/mirror-discipline.md` — JSONL + markdown mirror
  sync (atomic write)
- `references/daily-brief-callout.md` — the daily brief
  "open commitments" callout format
- `references/procedure.md` — the 5-step procedure with bash
  commands
- `references/what-this-is-not.md` — full "what this skill
  is NOT" list
- `tests/schema-discipline.md` — 6-field presence + append-
  only verification
- `tests/marker-detection-accuracy.md` — regex recall +
  precision
- `ea-decision-logger` — sibling for decisions
- `ea-daily-brief` — consumes the ledger for the callout
- `ea-contract` — the 5 EA behaviors
- `cross-team-discipline` — Mavis territory rule
