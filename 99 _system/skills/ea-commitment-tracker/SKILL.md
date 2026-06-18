---
name: ea-commitment-tracker
description: Codifies the capture and tracking of **commitments Mavis makes in chat** — promises like "I'll do X", "let me Y", "I owe you Z", "I'll have it by Friday", "I'll check on that". The procedure: (1) detect commitment phrases in the current session or in `00 Inbox/` captures (the markers are first-person future-tense with Andre as the implied or explicit beneficiary: "I'll", "I will", "let me", "I owe you", "give me a day", "by EOD", "by Friday", "in the morning", "I should have", "I'll come back to", "I need to", "I'll follow up"); (2) extract the 6 fields — commitment, beneficiary, due-by, surface (where it lands), dependencies, status (open / in-progress / delivered / dropped / reversed); (3) write to an append-only ledger at `~/.mavis/agents/mavis/commitments.jsonl` (one JSON object per line) AND mirror a human-readable view to `02 Notes/commitments/YYYY-MM.md`; (4) surface open commitments on the next `ea-daily-brief` (under the "open commitments" callout — never bury); (5) on delivery, append a status-change line (do NOT edit the original line — the audit trail is the value, same discipline as `ea-decision-logger`). The discipline: chat-promises evaporate. Mavis said she'd do something, the session moved on, the promise is forgotten, Andre waits. The ledger survives the EA's context window and surfaces the backlog. Use this skill when Mavis makes a commitment in the current session, when a `00 Inbox/` capture contains a commitment marker, when the daily brief is about to run (auto-pull open commitments), and on the EA `/commitments` workflow. Do NOT load for Andre's commitments to other people (those go in `02 Notes/commitments/andre-to-others.md` — separate ledger, same shape), for third-party commitments mentioned in passing, or for one-shot operational promises that complete within the same session (those don't need a ledger entry).
---

# EA Commitment Tracker — The Append-Only Ledger of Mavis-Said-I'd-Do

## What this skill does

You are codifying the capture and tracking of **commitments Mavis makes in chat** to Andre. The failure mode this skill prevents: Mavis says "I'll have the regulatory anchors by end of day," the session moves on, the context window is gone, the next session has no idea the promise was made, and Andre is left waiting. The ledger is the load-bearing artifact that turns a chat promise into a tracked deliverable with a due date and a status.

**The discipline:** every "I'll do X" or "let me Y" gets a ledger line **in the same session it's said**, with a status field that gets updated (not edited — appended) on delivery. The ledger is append-only; reversals are status changes, not deletions. This is the same discipline as `ea-decision-logger`: the audit trail is the value, not the cleanliness of the file.

## When to run

**Trigger phrases (auto-load on detection):**
- Mavis says "I'll do X" / "let me Y" / "I owe you Z" / "I'll handle that"
- Mavis says "by EOD" / "by Friday" / "tomorrow morning" / "in an hour" / "next session"
- Mavis says "I'll come back to that" / "let me look into it" / "I should have that"
- Mavis says "I'll have it ready" / "I'll follow up" / "I'll check on that"
- A `00 Inbox/` capture contains a future-tense first-person commitment marker

**Auto-trigger conditions (load the skill when):**
- The current session contains ≥1 first-person future-tense statement with Andre as the implied beneficiary
- A daily brief is about to be written (pull open commitments for the brief)
- Andre asks "what did you say you'd do" / "what's on your plate" / "what's pending"
- A weekly synthesis is being drafted (cross-reference open commitments against the 7d window)

**Do NOT load for:**
- Andre's commitments to other people (separate ledger at `02 Notes/commitments/andre-to-others.md`)
- Third-party commitments mentioned in passing ("he said he'd send the report")
- One-shot operational promises that complete within the same session (e.g., "I'll run that command now" — delivered in the same turn, no ledger needed)
- Decisions that are already documented in `ea-decision-logger` (decisions and commitments are different — a decision is a choice; a commitment is a promise to act)
- Skill work in other agents' trees (Mavis territory only)

## Inputs

| Input | Default | Required |
|---|---|---|
| Commitment text | (the verbatim quote from chat) | yes |
| Beneficiary | Andre (default for EA-scope commitments) | no |
| Due-by | (parse from chat, default: next session) | no |
| Surface | (where the deliverable lands — file path, project, or "TBD") | no |
| Dependencies | (what blocks this — other commitments, Andre's input, external events) | no |
| Session pointer | (the session ID or chat reference) | yes |

## The 6-field schema

Every commitment line is a JSON object with these 6 fields. None are optional — the format forces rigor.

```json
{
  "ts": "2026-06-16T23:24:37-05:00",
  "commitment": "Have the regulatory anchors codified in ea-research-brief by EOD",
  "beneficiary": "andre",
  "due_by": "2026-06-16T23:59:59-05:00",
  "surface": "~/.mavis/agents/mavis/skills/ea-research-brief/SKILL.md",
  "dependencies": [],
  "status": "open",
  "session_pointer": "mvs_697b3c19c91b4910bfa4bc09914b60d7",
  "delivered_at": null,
  "reversed_at": null,
  "reversal_reason": null
}
```

| Field | What it captures | Format |
|---|---|---|
| **`ts`** | When the commitment was made | ISO 8601 with timezone |
| **`commitment`** | The verbatim or sharpened quote | First-person, future-tense, ≤2 sentences |
| **`beneficiary`** | Who the commitment is to | `andre` (default) or named |
| **`due_by`** | When the deliverable is due | ISO 8601 with timezone, or `next-session` / `next-Mavis-touch` |
| **`surface`** | Where the deliverable lands | File path, project path, or "TBD" |
| **`dependencies`** | What blocks this | Array of strings (other commitments, Andre-input, external) |
| **`status`** | Lifecycle state | `open` → `in-progress` → `delivered` / `dropped` / `reversed` |
| **`session_pointer`** | Where it was said | Session ID or chat reference |
| **`delivered_at`** | When the deliverable landed | ISO 8601, or `null` until delivered |
| **`reversed_at`** | When the commitment was reversed | ISO 8601, or `null` |
| **`reversal_reason`** | Why it was reversed (if applicable) | Short string |

## The 5-step procedure

### 1. DETECT — pull commitment markers from the current session

Scan the current session for the marker phrases. The detection rule is conservative: only flag statements that are **first-person + future-tense + have a deliverable or a due date** (explicit or implied). Pure acknowledgments ("I see," "got it," "noted") are not commitments.

**Marker regex (illustrative, not exhaustive):**
```
\b(I('ll| will)|let me|give me|i owe|i should|i need to|by (eod|monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|next (week|month|quarter))|in the morning|in an hour|next session|come back to|follow up|check on)\b
```

If the regex fires on a statement, load this skill and extract the 6 fields. Do not ask Andre to confirm — the verbatim quote is the evidence.

### 2. EXTRACT — fill the 6 fields

Apply the schema discipline. The hard parts:
- **`commitment`** — quote verbatim if the wording is precise ("I'll have the regulatory anchors codified by EOD"). If the chat is loose ("yeah I'll get to that"), sharpen to one specific sentence per EA contract behavior #2. Never lose the due-by in the sharpening.
- **`due_by`** — if the chat said "by EOD," compute today's 23:59:59 CT. If the chat said "Friday," compute the next Friday 23:59:59 CT. If no due-by is given, default to `next-session` (the next Mavis-touch is the implicit deadline).
- **`surface`** — if the deliverable is a file, the surface is the file path. If it's a brief or a decision, the surface is the project or the doc. If the deliverable is unclear, surface = `TBD` and flag in `dependencies` ("deliverable shape not yet specified").
- **`dependencies`** — if Andre needs to do something first ("I'll do X once you send me Y"), `dependencies: ["andre-to-send-Y"]`. If another commitment blocks this one, cross-reference the other commitment's timestamp.

### 3. WRITE — append to `commitments.jsonl`

```bash
LEDGER=~/.mavis/agents/mavis/commitments.jsonl
echo '{"ts":"<ISO>","commitment":"<verbatim>","beneficiary":"andre","due_by":"<ISO or next-session>","surface":"<path>","dependencies":[],"status":"open","session_pointer":"<sid>","delivered_at":null,"reversed_at":null,"reversal_reason":null}' >> "$LEDGER"
```

**Append-only.** Never edit a prior line. Status changes are new lines that reference the original timestamp.

**Also write a human-readable mirror** to `02 Notes/commitments/YYYY-MM.md` (the current month) — one line per commitment, with a `[STATUS]` tag, due date, and a link to the surface. This is what Andre sees on the daily brief; the JSONL is what Mavis reads at session start.

### 4. SURFACE — include in the next daily brief

The daily brief gets a callout: **"Open commitments: N"** with the top 3 (by due-date proximity, soonest first). If any commitment is overdue (due_by < now and status = open), the callout becomes a **red flag** — Andre should see this before any other brief content.

The brief does NOT enumerate all open commitments (that's `/commitments` workflow territory). It surfaces the 3 most time-sensitive and the overdue count.

### 5. UPDATE — append on delivery or reversal

When the deliverable lands:
```bash
LEDGER=~/.mavis/agents/mavis/commitments.jsonl
echo '{"ts":"<delivery-ISO>","commitment":"DELIVERED: <original-commitment-text>","original_ts":"<original-ts>","status":"delivered","delivered_at":"<ISO>","surface":"<path-where-it-landed>","session_pointer":"<sid>"}' >> "$LEDGER"
```

When the commitment is reversed (Andre says "drop that" or "never mind" or the deliverable becomes unnecessary):
```bash
echo '{"ts":"<reversal-ISO>","commitment":"REVERSED: <original-commitment-text>","original_ts":"<original-ts>","status":"reversed","reversed_at":"<ISO>","reversal_reason":"<why>","session_pointer":"<sid>"}' >> "$LEDGER"
```

**Never edit the original line.** The audit trail is the value. Reversals are new lines that reference the original.

## Hard constraints

1. **Append-only.** Never edit a prior line. Status changes are new lines that reference the original timestamp. The audit trail is the load-bearing value.
2. **Verbatim or sharpened-to-one-sentence.** Per EA contract behavior #1 + #2, never paraphrase loosely. Either quote the chat exactly or sharpen to a single specific sentence.
3. **Default beneficiary = Andre.** If the commitment is to a third party (rare for Mavis), name them explicitly. Defaulting to Andre keeps the daily brief's "open commitments" callout clean.
4. **Surface open commitments in the daily brief.** Per `ea-daily-brief` constraint #4, the brief surfaces the 3 most time-sensitive commitments. This is not optional — it's how Andre knows what's on Mavis's plate.
5. **Overdue = red flag.** Any commitment with `due_by < now` and `status = open` is overdue. The next Mavis interaction surfaces overdue commitments before any other work.
6. **No fabricated due dates.** If the chat doesn't specify, default to `next-session` — the next Mavis-touch is the implicit deadline. Do not invent "by tomorrow" or "by EOD" that wasn't said.
7. **One-shot operational promises are excluded.** "I'll run that command now" or "let me check that" — if it completes in the same turn, no ledger entry. The ledger is for cross-session promises.
8. **Mirror to `02 Notes/commitments/YYYY-MM.md`.** The JSONL is machine-readable; the markdown is human-readable. Both must stay in sync. The human-readable mirror is what Andre sees on the daily brief.
9. **Mavis territory only.** Do not track commitments for other agents (Hermes, OpenClaw, etc.). Cross-team commitment tracking is the other agent's job, not Mavis's.
10. **Reversals require a reason.** A `status: reversed` line without a `reversal_reason` is a discipline violation. The reason doesn't have to be long ("Andre said drop it" is enough), but it has to be there.

## What this skill is NOT

- **Not a decision log.** Decisions and commitments are different artifacts. A decision is a choice ("we're using X for Y"). A commitment is a promise to act ("I'll have X done by Friday"). Use `ea-decision-logger` for decisions, this skill for commitments.
- **Not a project tracker.** Project-level work lives in `03 Projects/<project>/`. The commitment ledger is cross-project, for cross-session promises.
- **Not autonomous.** The skill captures Mavis-said commitments (Mavis is the beneficiary's agent, not the promiser's agent). Andre's commitments to other people go in a separate file.
- **Not exhaustive.** One-shot operational promises are excluded. The ledger is for cross-session promises with a deliverable and (usually) a due date.
- **Not the kanban.** The kanban (`mavis team plan` / `mavis kanban`) is for dispatched tasks with workers. The ledger is for chat promises that don't have a worker yet.

## Anchoring sources

- **EA contract — 4 workflows, 5 behaviors** — `ea-contract.md` (Mavis memory) — sharpen to one sentence, quote verbatim, end with question
- **Append-only audit trail** — `ea-decision-logger` (Mavis skill) — same discipline, different artifact
- **Surface open commitments in the daily brief** — `ea-daily-brief` (Mavis skill) constraint #4
- **Disk wins over recap** — Mavis MEMORY.md cross-cutting discipline
- **Decision rule (reversible + I have authority → decide)** — `ea-contract.md` §"Post-decision execution mode" — when a commitment is in flight and unblocked, the default is to deliver, not to ask
- **If I have to ask you twice, you failed** — Garry Tan (Andre's user memory) — the discipline that justifies codifying the commitment ledger
- **Asana / Linear commitment pattern** — operational pattern: chat promise → ledger entry → due date → status change on delivery
- **Atomic write discipline** — `ea-skill-evolution` hard constraint #6 (mirror discipline) — the JSONL is the canonical, the markdown is the mirror
