---
name: ea-daily-brief
description: Codifies the named EA `/daily-brief` workflow — a once-per-day synthesis that reads 24h of `00 Inbox/` + 7d of `02 Notes/` + today's `01 Daily/` (if it exists) and produces a brief with exactly 3 connections + 1 pattern + 1 question, written to `00 Inbox/brief-YYYY-MM-DD.md`. The procedure: (1) pull 24h of `00 Inbox/` items (raw captures from Telegram, browser bookmarks, web reads); (2) pull 7d of `02 Notes/` (decisions, references, drafts — anything that was filed as a thought); (3) cross-reference today's `01 Daily/YYYY-MM-DD.md` if it exists (skip if missing or <100 bytes body — the daily-logger cron owns that file); (4) apply the 4 connection types from `ea-contract.md` (A: same principle two domains / B: contradiction / C: 3+ notes forming one insight / D: question from one note answered by another) and pick 3; (5) extract 1 cross-domain pattern that doesn't fit any of the 3 connections; (6) end with exactly 1 question — never a task list, per behavior #3 of the EA contract; (7) write the brief, surface to Andre on next interaction. Use this skill at the start of any day when there's >24h of inbox activity, when Andre says "what's the brief", "morning brief", "what's open", or on the EA `/daily-brief` workflow. Do NOT load for weekly synthesis (that's `ea-weekly-connections`), for single-project status checks, for inbox filing (that's `/process-inbox`), or on days with <24h of new inbox activity (halt — no fabrication).
---

# EA Daily Brief — The 24h / 7d / Today Synthesis Workflow

## What this skill does

You are codifying the **daily brief** workflow — the single most-used EA output. Every day, Mavis reads the most recent 24h of captures and 7d of filed notes, then produces a structured brief that ends in a **question** (per EA contract behavior #3). The brief is the load-bearing artifact that keeps Andre oriented without requiring him to re-read the inbox or the daily notes himself.

**The discipline:** the brief is **bounded** (3 connections + 1 pattern + 1 question — never more), **current** (24h inbox + 7d notes, not 30d), and **question-ended** (the deliverable forces a decision or a follow-up, not a status report). A daily brief that becomes a status report is a failure mode — that's the weekly synthesis's job.

## When to run

**Trigger phrases:**
- "what's the brief" / "morning brief" / "what's open today" / "what did I miss"
- "give me the daily" / "ea-daily-brief" / "run the daily"
- At the start of any day when `00 Inbox/` has >0 items added in the last 24h
- On the EA `/daily-brief` workflow
- As a self-trigger at first-Mavis-interaction-of-the-day, paired with a check on `01 Daily/<today>.md`

**Do NOT load for:**
- Inbox filing or capture-sharpening (that's `/process-inbox`)
- Weekly synthesis (that's `ea-weekly-connections` — different cadence, different scope)
- Single-project status (the brief is cross-project by design)
- Days with <24h of new `00 Inbox/` activity (halt — no fabrication, the daily-logger cron owns the empty case)
- When today's `01 Daily/<date>.md` already has a `daily_brief:` link (the brief has been written — don't duplicate)

## Inputs

| Input | Default | Required |
|---|---|---|
| Date | today (America/Chicago) | yes (the date IS the output filename) |
| Inbox window | last 24h | no (overridable for catch-up briefs) |
| Notes window | last 7d | no |
| Daily note check | `01 Daily/YYYY-MM-DD.md` if exists | no (auto) |
| Output path | `00 Inbox/brief-YYYY-MM-DD.md` | no |

## The 7-step procedure

### 1. PULL — 24h of `00 Inbox/`

```bash
find ~/MiniMax-Agent/00\ Inbox/ -maxdepth 2 -type f -mtime -1 -not -name "brief-*" 2>/dev/null
```

Read each file. Note the **verbatim** content (per EA contract behavior #1: quote notes verbatim, never paraphrase). If the inbox is empty (no files in 24h), halt — there is no brief to write. Do not synthesize from prior days.

### 2. PULL — 7d of `02 Notes/`

```bash
find ~/MiniMax-Agent/02\ Notes/ -maxdepth 3 -type f -mtime -7 -not -path "*/Archive/*" 2>/dev/null
```

Read each. Focus on: `decisions/`, `connections/`, `references/`, `patterns/`, `drafts/`. Skip `Archive/` — those are settled. The 7d window is wide enough to catch patterns that took 2-3 days to surface, narrow enough that notes older than a week belong in the weekly synthesis, not the daily.

### 3. CHECK — today's `01 Daily/`

```bash
ls ~/MiniMax-Agent/01\ Daily/$(date +%Y-%m-%d).md 2>/dev/null
```

If the file exists and has ≥100 bytes of body content, read it. The daily is the **context** for the brief, not the brief itself. If the file is missing or <100 bytes, proceed without — the `vault-daily-logger` cron will fill it later in the day, but the brief should not wait.

### 4. CONNECT — pick 3 from the 4 connection types

Apply the 4 connection types from `ea-contract.md` §"4 Connection Types":

| Type | Question to ask the corpus | When to use |
|---|---|---|
| **A** | Is the same principle showing up in 2 different domains? | Most common — start here |
| **B** | Are 2 notes in tension with each other? | Rare but high-leverage — flag the contradiction, don't resolve it |
| **C** | Are 3+ notes converging on a single unnamed insight? | Use when the corpus is dense — protects against "3 separate things" framing |
| **D** | Did a question in one note get accidentally answered by another? | Use when surfacing a buried answer |

**Pick exactly 3.** Spread across types if possible (e.g., 1A + 1B + 1C) — but never all 3 of the same type (that's signal-diluted). If the corpus supports only 1 strong connection, write 1 and note the gap ("inbox was thin, brief is 1-connection-only today") — do NOT pad.

**Each connection gets:**
- **Title** (1 line, evocative, not generic)
- **Surfaces involved** (the file paths that surfaced it)
- **The pattern** (2-3 sentences, in EA voice — direct, not academic)
- **Evidence links** (`file:line` format, per the disk-wins-over-recap discipline)

### 5. EXTRACT — 1 cross-domain pattern

The pattern is the **non-connection** — the meta-observation that doesn't fit cleanly into any of the 3 connections. It should be:
- **Cross-domain** (spans ≥2 unrelated surfaces)
- **Underlying** (a discipline or a recurring correction, not an event)
- **One sentence** (per EA contract behavior #2: sharpen captures to one specific sentence)

If the corpus has no cross-domain pattern, omit the section entirely. Do not invent one. The brief is allowed to be 3 connections + 1 question, no pattern, on quiet days.

### 6. QUESTION — end with exactly 1

The closing question is the **load-bearing element** of the brief. Per EA contract behavior #3, the brief ends with a QUESTION, not a task. The question must:
- **Be answerable in 1-2 sentences** by Andre (not "what should we do about X" — that's a task)
- **Force a decision or a prioritization** (not a status check — Andre knows the status)
- **Reference a specific surface** from the brief (so Andre can drill in)

**Good question forms:**
- "Ship the ea-research-brief regulatory anchors as-is, or hold for the GEPA review?"
- "Is the Mavis ↔ Hermes mirror a working surface or a hard boundary?"
- "Which of these 3 connections is the one you want me to chase?"

**Bad question forms (halt and rewrite):**
- "What do you want me to do?" (too open)
- "Should I keep going?" (status, not decision)
- "Want me to file these?" (task, not question)

### 7. WRITE — atomic write to `00 Inbox/brief-YYYY-MM-DD.md`

```bash
# Atomic write: temp → fsync → rename
TMP=~/MiniMax-Agent/00\ Inbox/.brief-$(date +%Y-%m-%d).md.tmp
cp /dev/null "$TMP"
cat >> "$TMP" <<'BRIEF_EOF'
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
- **Pattern:** <2-3 sentences>
- **Evidence:** <file:line refs>

## 2. <Title B>
- ...

## 3. <Title C>
- ...

## Cross-domain pattern
<one sentence, or omit section>

## Question
<one question, one sentence>
BRIEF_EOF
sync "$TMP"
mv "$TMP" ~/MiniMax-Agent/00\ Inbox/brief-YYYY-MM-DD.md
```

After write, **surface the brief to Andre** at the next interaction (the brief itself, not a "I wrote a brief" notification). The brief is the message.

## Hard constraints

1. **3 connections + 1 pattern + 1 question. Never more, never fewer.** This is the spec. Padding dilutes; truncating wastes the input corpus.
2. **Quote notes verbatim.** Per EA contract behavior #1, never paraphrase. If you can't find a verbatim quote, the connection is weak — pick a different one.
3. **End with a question, not a task.** Per EA contract behavior #3, the brief is not a to-do list. The question forces a decision.
4. **No fabrication on empty corpus.** If `00 Inbox/` is empty for 24h, halt. Do not write a brief from prior days' material. The daily-logger cron handles empty days; the brief does not.
5. **One brief per day.** If `00 Inbox/brief-YYYY-MM-DD.md` already exists, halt — do not overwrite. To update, append a "## Update — <HH:MM CT>" section, never replace.
6. **Verbatim quotes only.** Never paraphrase. Never generic-ify. If a quote is too long, truncate at a clause boundary and note `[truncated at <marker>]`.
7. **Surface contradictions, don't resolve them.** Type B connections are for surfacing tensions. The brief flags the contradiction; Andre resolves it. Mavis does not editorialize.
8. **Cross-domain by default.** A connection that lives in 1 project is a project status, not a connection. Reject single-domain "connections" — they belong in `03 Projects/<project>/status.md`, not the daily brief.
9. **The question is the deliverable.** The 3 connections + 1 pattern are scaffolding for the question. If the connections are strong but the question is weak, the brief failed. Rewrite the question.

## What this skill is NOT

- **Not the weekly synthesis.** That's `ea-weekly-connections` (3-5 strong patterns over 7d, different cadence, different output).
- **Not the inbox filing workflow.** That's `/process-inbox` (read 00 Inbox, file by type to 02 Notes, sharpen each capture to one sentence).
- **Not a project status report.** A project status lives in `03 Projects/<project>/status.md`. The brief is cross-project by design.
- **Not autonomous.** The brief requires EA judgment (connection selection, pattern extraction, question framing). The cron writes a draft at 18:00 CT (via `vault-daily-logger-daily`); the EA finalizes on next interaction.
- **Not a memory write.** The brief is ephemeral (24h window). Patterns that survive the brief get promoted to `02 Notes/patterns/` or to `MEMORY.md` via the standard `mavis memory append` flow.
- **Not a single-source summary.** The brief is synthesis across ≥3 surfaces. A single-note summary is a link, not a brief.

## Anchoring sources

- **EA contract — 4 workflows, 5 behaviors, 4 connection types** — `ea-contract.md` (Mavis memory)
- **Dispatch taxonomy (5 modes)** — `ea-contract.md` §"Dispatch taxonomy" — this skill runs in `pattern_match` mode
- **Synthesis-doc audit pattern** — Mavis MEMORY.md cross-cutting discipline (citations are ground truth, prose is synthesis)
- **Disk wins over recap** — Mavis MEMORY.md cross-cutting discipline
- **Sharpen captures to one specific sentence** — `ea-contract.md` behavior #2
- **End briefs with a QUESTION, not a task** — `ea-contract.md` behavior #3
- **Surface contradictions between current beliefs and earlier saves** — `ea-contract.md` behavior #4
- **Challenge assumptions before agreeing** — `ea-contract.md` behavior #5
- **Mavis Daily Check-in cron** — `03 Projects/Mavis Daily Check-in/` — the source project for this workflow
- **Boris Cherny's /loop + /goal pattern** — `ea-closed-loop-builder` (Mavis skill) — bounded output with named stop condition
- **Garry Tan's "if I have to ask you twice, you failed"** — Andre's user memory — the discipline that justifies codifying the daily brief
