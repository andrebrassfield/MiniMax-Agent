---
name: ea-weekly-connections
description: |
  Codifies the named EA `/weekly-connections` Sunday workflow — the 3-5
  strong cross-domain patterns that emerge from the last 7 days of vault
  activity, kanban moves, worker dispatches, and memory edits. The
  procedure: (1) surface pull from 01 Daily/ (last 7 entries), kanban cards
  (last 7 days), recent worker outputs (03 Projects/*/dossiers/ + queue/),
  recent memory appends (`mavis memory tail`), and the skill-build-monitor
  tick; (2) cross-domain pattern detection — look for the 3-5 connections
  that span ≥2 unrelated surfaces (e.g., "the X-Content-Engine persona leak
  and the Hermes config drift both stem from the same procedural-gap pattern"
  — that's one connection, not two); (3) connection brief drafting — 1
  page, structured, each connection with: title, surfaces involved, the
  underlying pattern, evidence links, "what this means for Andre," "what to
  do about it"; (4) output to `02 Notes/connections/YYYY-WNN-synthesis.md`
  and surface as a Sunday digest. Use this skill on Sunday (or the next
  session if Sunday was missed), when Andre says "what patterns am I
  missing", "give me the weekly synthesis", "what changed this week", and
  on the EA `/weekly-connections` workflow. Do NOT load for daily briefs
  (that's `ea-daily-brief` — a different cadence), for ad-hoc questions
  about a single project, or when the vault has <7 days of activity.
---

# ea-weekly-connections

The Sunday synthesis workflow. The 3-5 strong cross-domain
patterns that surface from the last 7 days of work. The
discipline: most weeks produce a flood of activity. The
signal is *not* in any individual item; it's in the
**patterns that span surfaces**.

The deliverable is one file per week. Not a 50-page
report. Not a 5-bullet summary. One page, 3-5
connections, each with evidence.

## When to run

**Triggers:**
- "what patterns am I missing" / "what changed this week"
  / "give me the weekly synthesis"
- "weekly connections" / "Sunday synthesis" / "weekly
  review"
- "what should I be paying attention to"
- The EA `/weekly-connections` workflow (per
  `ea-contract.md`)
- Cron tick: Sunday 18:00 CT (auto-fired)

**Do NOT load for:**
- Daily briefs (use `ea-daily-brief` — different cadence,
  different scope)
- Ad-hoc questions about a single project ("how's X
  going")
- Weeks with <7 days of activity (the cross-domain
  detection needs material to work with)
- The first week of a new vault (no history to compare
  against)

## The 4-step procedure (the load-bearing structure)

The SKILL.md only carries the 4-step list. Full
per-step detail in `references/4-step-procedure.md`.

| # | Step | What it does | Source in references |
|---|---|---|---|
| 1 | **Surface pull** | Read-only + deterministic read of 5 surfaces (daily notes, kanban, worker outputs, memory, skills). ~30-60 items total. No summarizing, no editorialize. | §1 — 5 surfaces × per-surface extraction |
| 2 | **Cross-domain detection** | For each item, ask: "does this connect to anything from another surface?" A connection requires ≥2 unrelated surfaces sharing an underlying pattern. 3-5 connections, not 2 (insufficient) and not 7+ (signal-diluted). | §2 — 4 connection types + 3 anti-patterns |
| 3 | **Brief drafting** | 1-page brief, dense, 3-5 connections. Each: title, surfaces, pattern, evidence, "what this means for Andre," "what to do." Plus "what's not on this list" + "open threads." | §3 — per-connection fields + structure |
| 4 | **Output + handoff** | Write to `02 Notes/connections/YYYY-WNN-synthesis.md`. Surface via `<mavis-progress>` tag. Cron integration: Sunday 18:00 CT. | §4 — file path + cron integration |

## The 5 surfaces (the load-bearing structure)

| # | Surface | Path / command | What to extract |
|---|---|---|---|
| 1 | **Daily notes** | `01 Daily/` (last 7 entries, sorted by mtime) | Top 3-5 non-routine entries per day, the date stamp, links to other surfaces |
| 2 | **Kanban moves** | `~/.hermes/kanban/` (last 7 days) — read-only mirror, Mavis↔Hermes separation in effect | Cards that moved pending → in_progress or done, cross-team tags, escalations |
| 3 | **Worker outputs** | `03 Projects/*/dossiers/`, `03 Projects/*/queue/`, `03 Projects/*/reports/` (last 7 days) | Completed dispatches, briefs, verification verdicts, audit outputs |
| 4 | **Memory appends** | `mavis memory tail --limit 30` | New rules, corrections, lessons not yet codified into a topic file |
| 5 | **Skill activity** | `ls -lt 99 _system/skills/ ~/.mavis/agents/mavis/skills/` (last 7 days) | New skills, edits, the skill-build-monitor's most recent tick |

**Discipline:** the surface pull is **read-only** and
**deterministic**. No summarizing. List the items with
their dates and source paths. Cross-domain detection
happens in Step 2.

**Output of Step 1:** a 5-section raw list, ~30-60
items total. Each item: date, surface, 1-line
description, source path.

## Cross-domain detection (the load-bearing element)

For each item in the surface pull, ask: **does this
connect to anything from another surface?** A
"connection" requires ≥2 unrelated surfaces sharing an
underlying pattern. Full 4 connection types + 3
anti-patterns in `references/4-step-procedure.md` §2.

The 4 connection types:
- **Same procedural gap, different surfaces**
- **Cascading effect** (one upstream change → multiple
  downstream)
- **Convergent timing** (multiple surfaces touching the
  same theme in the same week)
- **Contradictory surfaces** (one says X, another says ¬X)

**Anti-patterns (NOT connections):**
- Multiple items on the same surface that don't relate
- Forced connections (if you have to stretch, it's not
  a connection)
- Items obvious from any single surface (a connection
  should reveal something not visible in isolation)

**Output of Step 2:** 3-5 connections, each with:
- Title (5-10 words, descriptive)
- Surfaces (which ≥2 surfaces the connection spans)
- Underlying pattern (1-2 sentences)
- Evidence (file paths / line numbers / dates)
- What this means for Andre (1-2 sentences, EA voice)
- What to do about it (1-2 sentences, or "no action —
  informational")

## Hard constraints

1. **Read-only surface pull.** Step 1 is deterministic +
   read-only. No summarizing, no "the gist is...". List
   the items.
2. **3-5 connections. Not 2, not 7+.** The 3-5 range is
   the spec.
3. **Each connection spans ≥2 surfaces.** Single-surface
   items go in project summaries, not in the weekly
   connections.
4. **"What this means for Andre" in EA voice.** Synthesis
   + why, not "the data shows X." (Per chief-of-staff vs
   operator voice in MEMORY.md.)
5. **"What to do" must be concrete.** "Consider" /
   "monitor" / "think about" are not actions. "Schedule
   a 30-min review of X" is.
6. **Mavis territory only for fixes.** The cross-domain
   detection may surface work for other agents (Hermes,
   OpenClaw), but the brief's "what to do" is Mavis's
   call. For peer-team work, surface the connection
   (informational) without proposing a fix.
7. **The article is a trigger, not a source.** The
   cross-domain detection framework is from the EA
   workflow + the chief-of-staff role; the specific
   3-5 range is Mavis-specific.

## When the skill HALTs

Halt and escalate to Andre when:
- <3 items in the surface pull (H1) — too little
  activity, skip the brief, log "weekly skipped: <3
  items in pull"
- All items are from a single surface (H2) — no cross-
  domain patterns possible, skip the brief
- The vault has been heavily edited (git pull, obsidian
  sync) in the last 24h (H3) — run the brief anyway, but
  flag the recency caveat in the header
- The cron fails to write the file (H4) — surface
- The surface pull detects 7+ candidate connections (H5)
  — pick the strongest 3-5, document the rest in "open
  threads" rather than diluting the brief

## Output schema

A single file at
`02 Notes/connections/YYYY-WNN-synthesis.md`. Full
template in `references/brief-template.md`. Structure:

1. Header (Generated, Author, Window, Connections
   surfaced, Surfaces scanned)
2. 3-5 connections (per-connection fields)
3. "What's not on this list" (deliberate omissions)
4. "Open threads" (patterns that almost-connected)

## Anchoring sources

- **`ea-contract.md`** — the named workflow
  `/weekly-connections` (Sunday) — 3-5 strong
  connections to `02 Notes/connections/`
- **`ea-loop-thinking`** — the 5-stage loop; this skill
  is a specialization of the Plan + Verify stages
- **`ea-data-quality-audit`** — the disk-evidence
  discipline; the "evidence" field in each connection
  must be a real path/date, not a recap
- **MEMORY.md "Cross-domain synthesis"** (if it exists) —
  or the `06 Connections/` vault convention

## What this skill is NOT

- **Not the daily brief.** That's `ea-daily-brief`
  (different cadence, different scope, different
  output).
- **Not a project summary.** Project summaries live in
  `03 Projects/<project>/` directories.
- **Not a kanban review.** Kanban state is one of the 5
  surfaces, not the output.
- **Not a memory audit.** Memory appends are one of the
  5 surfaces. The output is the cross-domain connection.
- **Not exhaustive.** 3-5 connections is the discipline.
  7+ is signal-diluted. <3 is insufficient material.
- **Not automated end-to-end.** The cron fires the
  surface pull automatically, but the cross-domain
  detection requires EA judgment. The cron writes a
  draft; the EA finalizes.

## Cross-reference

- `references/4-step-procedure.md` — full per-step
  detail
- `references/brief-template.md` — the connection brief
  template
- `references/4-connection-types.md` — the 4 connection
  types + 3 anti-patterns
- `tests/safety-halts.md` — 5 halt conditions + eval cases
- `tests/discipline.md` — 3-5 range, cross-domain,
  EA-voice checks
- `ea-daily-brief` — different cadence, different scope
- `vault-30day-auditor` — provides the 30-day baseline
- `ea-data-quality-audit` — disk-evidence discipline
