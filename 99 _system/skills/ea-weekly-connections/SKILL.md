---
name: ea-weekly-connections
description: Codifies the named EA `/weekly-connections` Sunday workflow — the 3-5 strong cross-domain patterns that emerge from the last 7 days of vault activity, kanban moves, worker dispatches, and memory edits. The procedure: (1) surface pull from 01 Daily/ (last 7 entries), kanban cards (last 7 days), recent worker outputs (03 Projects/*/dossiers/ + queue/), recent memory appends (`mavis memory tail`), and the skill-build-monitor tick; (2) cross-domain pattern detection — look for the 3-5 connections that span ≥2 unrelated surfaces (e.g., "the X-Content-Engine persona leak and the Hermes config drift both stem from the same procedural-gap pattern" — that's one connection, not two); (3) connection brief drafting — 1 page, structured, each connection with: title, surfaces involved, the underlying pattern, evidence links, "what this means for Andre," "what to do about it"; (4) output to `02 Notes/connections/YYYY-WNN-synthesis.md` and surface as a Sunday digest. Use this skill on Sunday (or the next session if Sunday was missed), when Andre says "what patterns am I missing", "give me the weekly synthesis", "what changed this week", and on the EA `/weekly-connections` workflow. Do NOT load for daily briefs (that's `ea-daily-brief` — a different cadence), for ad-hoc questions about a single project, or when the vault has <7 days of activity.
---

# EA Weekly Connections — Sunday Synthesis Workflow

## What this skill does

You are codifying the named EA workflow `/weekly-connections` — the 3-5 strong cross-domain patterns that surface from the last 7 days of work. The discipline: most weeks produce a flood of activity (daily notes, kanban moves, worker dispatches, memory edits, skill builds). The signal is *not* in any individual item; it's in the **patterns that span surfaces**. This skill encodes the surface pull, the cross-domain detection, the brief structure, and the output discipline.

The deliverable is one file per week. Not a 50-page report. Not a 5-bullet summary. One page, 3-5 connections, each with evidence.

## When to run

**Trigger phrases:**
- "what patterns am I missing" / "what changed this week" / "give me the weekly synthesis"
- "weekly connections" / "Sunday synthesis" / "weekly review"
- "what should I be paying attention to"
- The EA `/weekly-connections` workflow (per `ea-contract.md`)
- Cron tick: Sunday 18:00 CT (auto-fired, see "Cron integration" below)

**Do NOT load for:**
- Daily briefs (use `ea-daily-brief` — different cadence, different scope)
- Ad-hoc questions about a single project ("how's X going")
- Weeks with <7 days of activity (the cross-domain detection needs material to work with)
- The first week of a new vault (no history to compare against)

## The 4-step procedure

### Step 1: Surface pull (the 5 surfaces, in order)

Pull from these 5 surfaces, in this order. Each surface is a deterministic read, not a synthesis. Read what's there, don't editorialize.

| # | Surface | Path / command | What to extract |
|---|---|---|---|
| 1 | **Daily notes** | `01 Daily/` (last 7 entries, sorted by mtime) | Top 3-5 non-routine entries per day, the date stamp, any links to other surfaces |
| 2 | **Kanban moves** | `~/.hermes/kanban/` (last 7 days) — read-only mirror, Mavis↔Hermes separation in effect | Cards that moved from `pending` → `in_progress` or `done`, any cards with cross-team tags, any escalations |
| 3 | **Worker outputs** | `03 Projects/*/dossiers/`, `03 Projects/*/queue/`, `03 Projects/*/reports/` (last 7 days, mtime) | Completed dispatches, briefs produced, verification verdicts, audit outputs |
| 4 | **Memory appends** | `mavis memory tail --limit 30` (last 30 memory entries) | New rules, corrections, lessons that haven't yet been codified into a topic file |
| 5 | **Skill activity** | `ls -lt 99 _system/skills/ ~/.mavis/agents/mavis/skills/` (last 7 days) | New skills, edits to existing skills, the skill-build-monitor's most recent tick report |

**Discipline:** the surface pull is **read-only** and **deterministic**. No summarizing, no "the gist is..." — list the items with their dates and source paths. The cross-domain detection happens in Step 2, not here.

**Output of Step 1:** a 5-section raw list, ~30-60 items total. Each item: date, surface, 1-line description, source path.

### Step 2: Cross-domain pattern detection

For each item in the surface pull, ask: **does this connect to anything from another surface?** A "connection" requires ≥2 unrelated surfaces sharing an underlying pattern. Examples of strong connections:

- **Same procedural gap, different surfaces.** "The X-Content-Engine persona leak and the Hermes config drift both stem from the same gap: the worker is reading a stale cached file, not the live config." Two surfaces, one root cause.
- **Cascading effect.** "The ea-5-mistakes-audit Addition 11 triggered the ea-research-brief regulatory frame, which then flagged the EU AI Act in three downstream briefs." One upstream change, multiple downstream effects.
- **Convergent timing.** "Three different surfaces (memory entry, kanban card, daily note) all touched the Mavis↔Hermes separation in the same week — that's a signal the rule is being stress-tested, not just referenced."
- **Contradictory surfaces.** "The 30-day footprint report said 'no orphan spawns this week' but the kanban-health-check tick on Wednesday found 2. The contradiction is the connection — one of them is wrong, and the audit ladder resolves it."

**Anti-patterns (NOT connections):**

- Multiple items on the same surface that don't relate to other surfaces (that's a project summary, not a connection)
- Forced connections (if you have to stretch to make the link, it's not a connection)
- Items that are obvious from any single surface (a connection should reveal something not visible in isolation)

**Output of Step 2:** 3-5 connections, each with:
- **Title** — 5-10 words, descriptive
- **Surfaces** — which ≥2 surfaces the connection spans
- **Underlying pattern** — 1-2 sentences
- **Evidence** — file paths / line numbers / dates
- **What this means for Andre** — 1-2 sentences, in EA-voice (synthesis + why)
- **What to do about it** — 1-2 sentences, or "no action — informational"

### Step 3: Connection brief drafting

Format the 3-5 connections into a 1-page brief. The brief is **dense**, not exhaustive. Andre should be able to read it in 5 minutes and get the signal.

**Structure:**

```markdown
# Weekly Connections — Week NN, YYYY (MM-DD to MM-DD)

> Generated: <YYYY-MM-DD HH:MM CT> | Author: Mavis (EA) | Window: last 7 days
> Connections surfaced: <N> | Surfaces scanned: 5 (daily, kanban, workers, memory, skills)

## Connection 1: <title>

**Surfaces:** <surface 1>, <surface 2>, ...
**Pattern:** <1-2 sentences>
**Evidence:** <file paths / dates>
**What this means for Andre:** <synthesis>
**What to do:** <action or "no action — informational">

## Connection 2: ...
...

## What's not on this list (deliberate omissions)

<1-2 sentences on what Mavis considered and rejected, so Andre can audit the selection.>

## Open threads

<Any patterns that almost-connected but didn't quite — keep for next week.>
```

**Discipline:**
- 3-5 connections. Not 2 (insufficient), not 7+ (loses signal-to-noise).
- Each connection must span ≥2 surfaces. If you find yourself with single-surface items, those go in the project summaries, not here.
- "What this means for Andre" is in **EA voice** — synthesis + why, not "the data shows X." (This is the EA role discipline per `chief-of-staff voice vs operator voice` in MEMORY.md.)
- "What to do" must be concrete. "Consider" / "monitor" / "think about" are not actions. "Schedule a 30-min review of X" is.

### Step 4: Output + handoff

**Write to:** `02 Notes/connections/YYYY-WNN-synthesis.md` (WNN = ISO week number, e.g., `2026-W25-synthesis.md`).

**Cron integration:** the cron `ea-weekly-connections` is scheduled Sunday 18:00 CT. On tick:
1. Run the surface pull (Step 1)
2. Run the cross-domain detection (Step 2)
3. Draft the brief (Step 3)
4. Write the file (Step 4)
5. Surface to Andre via `<mavis-progress>` tag with the file path

**Manual handoff:** if Andre asks for the weekly synthesis mid-week, run the same 4 steps with a 7-day window ending at the request time, not Sunday.

**Halt conditions:**
- <3 items in the surface pull → too little activity, skip the brief, log "weekly skipped: <3 items in pull"
- All items are from a single surface → no cross-domain patterns possible, skip the brief, log the reason
- The vault has been heavily edited (git pull, obsidian sync) in the last 24h → run the brief anyway, but flag the recency caveat in the header

## Output schema

```markdown
# Weekly Connections — Week NN, YYYY (MM-DD to MM-DD)

> Generated: <ISO timestamp> | Author: Mavis (EA) | Window: last 7 days
> Connections surfaced: 3-5 | Surfaces scanned: 5 (daily, kanban, workers, memory, skills)

## Connection 1: <title>
<structured fields>

## Connection 2: <title>
<structured fields>

(3-5 total)

## What's not on this list
<deliberate omissions + reason>

## Open threads
<patterns that almost-connected>
```

## Anchoring sources

- **`ea-contract.md`** — the named workflow `/weekly-connections` (Sunday) — 3-5 strong connections to `02 Notes/connections/`
- **`ea-loop-thinking`** — the 5-stage loop; this skill is a specialization of the Plan + Verify stages
- **`ea-data-quality-audit`** — the disk-evidence discipline; the "evidence" field in each connection must be a real path/date, not a recap
- **MEMORY.md "Cross-domain synthesis"** (if it exists) — or the `06 Connections/` vault convention
- **The `04 Resources/articles/2026-06-15 - Tony Simons SOUL.md Operator Contract`** — the operator contract framework (synthesis + why, not step-by-step)

## What this skill is NOT

- **Not the daily brief.** That's `ea-daily-brief` (different cadence, different scope, different output). The weekly is for cross-domain patterns over 7 days; the daily is for "what's open today."
- **Not a project summary.** Project summaries live in `03 Projects/<project>/` directories, not in the weekly connections. The weekly is for connections *across* projects.
- **Not a kanban review.** Kanban state is one of the 5 surfaces, not the output. The output is the connection, not the kanban snapshot.
- **Not a memory audit.** Memory appends are one of the 5 surfaces. The output is the cross-domain connection, not the memory diff.
- **Not exhaustive.** 3-5 connections is the discipline. 7+ is signal-diluted. <3 is insufficient material. The 3-5 range is the spec.
- **Not automated end-to-end.** The cron fires the surface pull automatically, but the cross-domain detection requires EA judgment. The cron writes a draft; the EA finalizes.
