---
name: ea-daily-brief
description: |
  Codifies the named EA `/daily-brief` workflow — a once-per-day synthesis
  that reads 24h of `00 Inbox/` + 7d of `02 Notes/` + today's
  `01 Daily/` (if it exists) and produces a brief with exactly 3
  connections + 1 pattern + 1 question, written to
  `00 Inbox/brief-YYYY-MM-DD.md`. The 4 connection types (A: same
  principle two domains / B: contradiction / C: 3+ notes forming one
  insight / D: question from one note answered by another) come from
  `ea-contract.md`. The brief ends with a question (per EA contract
  behavior #3) — never a task list. Triggers: "what's the brief",
  "morning brief", "what's open", "what did I miss", and the EA
  `/daily-brief` workflow. Auto-invoke at first-Mavis-interaction-of-
  the-day if today's `01 Daily/<date>.md` exists and the brief has
  not yet been written. Do NOT load for weekly synthesis
  (ea-weekly-connections), for single-project status, for inbox
  filing (/process-inbox), or on days with <24h of new inbox
  activity (halt — no fabrication).
# === TPG (Cognitive Parameter Graph) layer - added 2026-06-17 ===
# Phase 1 codification: schema-only, no SePO loop running yet.
# Phase 2 will populate fitness_score, last_evaluated, etc. via sepo-runner.
node_type: agent_parameter
parameter_id: ea-daily-brief
generation: 1
fitness_score: null
last_optimized: null
last_evaluated: null
mutation_count: 0
schema_version: 1
# purpose: writes a 3-connection brief ending with a question, never a task list
---

# ea-daily-brief

The single most-used EA output. Every day, Mavis reads the most
recent 24h of captures and 7d of filed notes, then produces a
structured brief that ends in a QUESTION. The brief keeps Andre
oriented without requiring him to re-read the inbox or the daily
notes himself.

**The discipline:** the brief is **bounded** (3 connections + 1
pattern + 1 question — never more), **current** (24h inbox + 7d
notes), and **question-ended** (the deliverable forces a decision or
a follow-up, not a status report).

## Intent

- Pull 24h of `00 Inbox/` items
- Pull 7d of `02 Notes/` items
- Cross-reference today's `01 Daily/YYYY-MM-DD.md` if it exists
- Apply the 4 connection types and pick 3
- Extract 1 cross-domain pattern
- End with exactly 1 question
- Write the brief to `00 Inbox/brief-YYYY-MM-DD.md` (atomic)
- Surface to Andre on next interaction (the brief IS the message)

The model decides *which* 3 connections are the strongest, *what* the
pattern is, and *what* the question is. The deterministic layer
(connection types, atomic write command, question-form examples)
lives in `references/`. The output-shape discipline lives in `tests/`.

## When to run

**Triggers:**
- "what's the brief" / "morning brief" / "what's open today" / "what did I miss"
- "give me the daily" / "ea-daily-brief" / "run the daily"
- At first-Mavis-interaction-of-the-day if today's `01 Daily/<date>.md` exists
- The EA `/daily-brief` workflow
- `00 Inbox/` has >0 items added in the last 24h

**Do NOT load for:**
- Inbox filing / capture-sharpening (`/process-inbox`)
- Weekly synthesis (`ea-weekly-connections`)
- Single-project status (cross-project by design)
- Days with <24h of new `00 Inbox/` activity (halt — no fabrication)
- When today's `01 Daily/<date>.md` already has a `daily_brief:` link (already written)

## Inputs

| Input | Default | Required |
|---|---|---|
| Date | today (America/Chicago) | yes (the date IS the output filename) |
| Inbox window | 24h | no (overridable for catch-up) |
| Notes window | 7d | no |
| Daily note check | `01 Daily/YYYY-MM-DD.md` if exists | no (auto) |
| Output path | `00 Inbox/brief-YYYY-MM-DD.md` | no |

## Output contract

A single markdown file at `00 Inbox/brief-YYYY-MM-DD.md` with:

```markdown
---
date: YYYY-MM-DD
generator: ea-daily-brief
inbox_window: 24h
notes_window: 7d
connection_count: 3
---

# Daily Brief — YYYY-MM-DD

## 1. <Title A>
- **Surfaces:** <paths>
- **Pattern:** <2-3 sentences, EA voice — direct, not academic>
- **Evidence:** <file:line refs>

## 2. <Title B>
...

## 3. <Title C>
...

## Cross-domain pattern
<one sentence, or omit section>

## Question
<one question, one sentence>
```

The full template and the bash atomic-write command are in
`references/output-template.md`.

## Resolver

Auto-invoke when:
- First Mavis interaction of the day, AND
- Today's `01 Daily/<date>.md` exists, AND
- `00 Inbox/brief-<date>.md` does NOT exist yet

Do NOT auto-invoke when:
- Brief already written (the `daily_brief:` link check)
- <24h of new inbox activity (halt — no fabrication)
- Weekly synthesis is the right cadence (different skill)

## Hard constraints (the spec)

1. **3 connections + 1 pattern + 1 question. Never more, never fewer.** Padding dilutes; truncating wastes the input corpus.
2. **Quote notes verbatim.** Per EA contract behavior #1. Never paraphrase. If you can't find a verbatim quote, the connection is weak — pick a different one.
3. **End with a question, not a task.** Per EA contract behavior #3. The question forces a decision.
4. **No fabrication on empty corpus.** If `00 Inbox/` is empty for 24h, halt. Do not write a brief from prior days' material.
5. **One brief per day.** If `00 Inbox/brief-YYYY-MM-DD.md` already exists, halt. To update, append a `## Update — <HH:MM CT>` section, never replace.
6. **Verbatim quotes only.** Truncate at clause boundaries with `[truncated at <marker>]` if needed.
7. **Surface contradictions, don't resolve them.** Type B connections are for surfacing tensions. The brief flags; Andre resolves.
8. **Cross-domain by default.** A single-domain "connection" is a project status, not a connection. Reject those.
9. **The question is the deliverable.** The 3 connections + 1 pattern are scaffolding for the question. If the question is weak, the brief failed.

## Good question forms (load-bearing)

- "Ship X as-is, or hold for the GEPA review?"
- "Is X a working surface or a hard boundary?"
- "Which of these 3 connections is the one you want me to chase?"

**Bad question forms (halt and rewrite):**
- "What do you want me to do?" (too open)
- "Should I keep going?" (status, not decision)
- "Want me to file these?" (task, not question)

The full good/bad question examples are in `references/question-forms.md`.

## Cross-reference

- `references/connection-types.md` — the 4 connection types (A/B/C/D) with their question + when-to-use
- `references/output-template.md` — the markdown file template + atomic-write bash
- `references/question-forms.md` — good vs. bad question forms
- `tests/safety-halts.md` — empty corpus, already-written, no daily note
- `tests/output-shape-discipline.md` — exactly 3 connections, exactly 1 question, etc.
- `ea-contract.md` (Mavis memory) — the 4 workflows + 5 behaviors + 4 connection types
- `ea-weekly-connections` — the weekly counterpart (different cadence, different scope)
- `/process-inbox` — inbox filing workflow (different from brief synthesis)
