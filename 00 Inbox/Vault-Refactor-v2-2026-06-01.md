---
type: design-proposal
date: 2026-06-01
author: Mavis
status: DRAFT — awaiting Andre's go
tags: [vault, refactor, design, chief-pattern, vellum-pattern]
---

# Vault Refactor v2 — CHIEF + Vellum Pattern Adoption

> Proposal only. No file moves until you say "go."

## What the two articles actually add to my current vault

| Article | Core claim | What I currently have | Gap |
|---------|-----------|------------------------|-----|
| **CHIEF + Vellum** | Organize captures **by type** (articles/ideas/patterns/questions/numbers), not by topic. Synthesized insights need their **own folder** (02-CONNECTIONS). The AI's context file is the **most important file** in the system. | `02 Notes/` is a flat folder mixing article-digests (Apple/Siri, SoftBank, Sysdig) with concept notes (M3 Edge, Capture Over Polish) | No type-based sub-organization; insights get mixed back into Notes |
| **CHIEF + Vellum** | 4 saved workflows (process-inbox, daily-brief, weekly-connections, deep-research) + VELLUM.md (the context file) | No AI context file. No saved workflows. I run ad-hoc. | I re-discover the system on every session |
| **30-min Obsidian** | Daily note IS the capture hub; linking system is the superpower; minimalism (5 folders beats 20); 3 habits (capture / process / review) | I already have `01 Daily/`, links, INDEX, templates, dashboards | Mostly aligned — the 3-habit loop is what makes the system compound |

**The high-leverage delta** is two things:
1. **Type-based sub-organization inside `02 Notes/`** — this is the CHIEF insight that makes connection-finding automatic
2. **An AI context file (MAVIS.md) + a saved-workflows folder** — this is what makes *me* (the AI in the loop) consistent across sessions

## Proposed structure (drop-in diff against current)

```
MiniMax-Agent/                         (no root files moved)
├── SOUL.md                            [unchanged]
├── agent.md                           [unchanged]
├── learnings.md                       [unchanged]
├── README.md                          [REFRESH — new structure, MAVIS.md mentioned]
├── INDEX.md                           [REFRESH — new mermaid, Connections dashboard]
├── MAVIS.md                           [NEW — VELLUM.md equivalent; root, weekly-updated]
│
├── 00 Inbox/                          [unchanged — raw, processed daily]
│
├── 01 Daily/                          [unchanged — daily IS the capture hub]
│
├── 02 Notes/                          [REFACTOR — add type-based subfolders]
│   ├── _MOCs/                         [NEW — hub notes sort to top via _]
│   │   ├── AI Landscape 2026.md       [MOVED from 02 Notes/ root]
│   │   └── Mavis Operating System.md  [NEW — hub for SOUL/agent/M3 stack]
│   ├── articles/                      [NEW — external content digests]
│   │   ├── 2026-06-01 - Apple WWDC 2026 Siri Rebuilt on Gemini.md  [MOVED]
│   │   ├── 2026-06-01 - First LLM-Agent-Driven Cyberattack (Sysdig).md  [MOVED]
│   │   └── 2026-06-01 - SoftBank €75B French AI Data Centers.md  [MOVED]
│   ├── ideas/                         [NEW — my own observations / theses]
│   │   ├── M3 Edge.md                 [MOVED]
│   │   ├── M3 Capabilities.md         [MOVED]
│   │   └── Long-Horizon Patterns.md   [MOVED]
│   ├── patterns/                      [NEW — same principle across domains]
│   │   ├── Capture Over Polish.md     [MOVED]
│   │   ├── Linking Principle.md       [MOVED]
│   │   ├── Vault Conventions.md       [MOVED]
│   │   └── Mavis EA Workflow.md       [MOVED]
│   ├── questions/                     [NEW — open questions]
│   │   └── (TBD — populated as I encounter them)
│   └── numbers/                       [NEW — specific data points]
│       └── (TBD — populated as I encounter them)
│
├── 03 Projects/                       [unchanged — M3 Eval Lab, Mavis EA Design, Vault Refinement]
│
├── 04 Resources/                      [unchanged — currently empty, will use]
│
├── 05 Archive/                        [unchanged — currently empty]
│
├── 06 Connections/                    [NEW — synthesized insights from 2+ notes]
│   └── (populated by weekly workflow, not manually)
│
├── 07 Vellum/                         [NEW — intelligence layer's working dir]
│   ├── workflows/                     [NEW — 4 saved prompts, called by trigger phrase]
│   │   ├── process-inbox.md
│   │   ├── daily-brief.md
│   │   ├── weekly-connections.md
│   │   └── deep-research.md
│   ├── eval-logs/                     [NEW — task outcomes for the feedback loop]
│   │   └── 2026-06-01 - first-M3-eval.md
│   └── weekly-context/                [NEW — dated context snapshots, kept forever]
│       └── 2026-W22.md
│
└── 99 _system/                        [unchanged]
    ├── templates/                     [+ add: mavis-context.md, connection.md, pattern.md, idea.md, question.md, number.md]
    ├── dashboards/                    [+ add: Connections Dashboard, Weekly Patterns]
    └── scripts/                       [unchanged]
```

## Why the 06 / 07 numbering

I deliberately kept 00-05 + 99 unchanged. Adding `06 Connections/` (between Notes and the long-term layer) and `07 Vellum/` (the AI's working dir, just before meta) avoids renumbering any existing project folders, links, or dataview queries. **No break to existing wikilinks.**

## Why MAVIS.md at root, not inside 07 Vellum/

Article 1 puts VELLUM.md at the top of `04-VELLUM/` because it's the **single most important file in the system**. Burying it one level deep is symbolic of "the AI is an afterthought." Putting it at root says "this is the file the AI reads first." My SOUL.md is also at root for the same reason. MAVIS.md joins them.

`07 Vellum/` is the AI's *working* dir (workflows, eval logs, weekly context snapshots). Different concept: outputs, not inputs.

## Migration map (11 file moves, 5 new top-level things)

| # | From | To | Action |
|---|------|------|--------|
| 1 | `02 Notes/AI Landscape 2026.md` | `02 Notes/_MOCs/AI Landscape 2026.md` | move |
| 2 | `02 Notes/2026-06-01 - Apple WWDC...` | `02 Notes/articles/` | move |
| 3 | `02 Notes/2026-06-01 - First LLM-Agent...` | `02 Notes/articles/` | move |
| 4 | `02 Notes/2026-06-01 - SoftBank €75B...` | `02 Notes/articles/` | move |
| 5 | `02 Notes/M3 Edge.md` | `02 Notes/ideas/` | move |
| 6 | `02 Notes/M3 Capabilities.md` | `02 Notes/ideas/` | move |
| 7 | `02 Notes/Long-Horizon Patterns.md` | `02 Notes/ideas/` | move |
| 8 | `02 Notes/Capture Over Polish.md` | `02 Notes/patterns/` | move |
| 9 | `02 Notes/Linking Principle.md` | `02 Notes/patterns/` | move |
| 10 | `02 Notes/Vault Conventions.md` | `02 Notes/patterns/` | move |
| 11 | `02 Notes/Mavis EA Workflow.md` | `02 Notes/patterns/` | move |
| 12 | — | `MAVIS.md` | **create** |
| 13 | — | `06 Connections/` | **create folder** |
| 14 | — | `07 Vellum/` + subdirs | **create folder** |
| 15 | — | `02 Notes/_MOCs/Mavis Operating System.md` | **create** |
| 16 | — | `07 Vellum/workflows/` (4 files) | **create** |
| 17 | — | `99 _system/templates/` (6 new) | **create** |
| 18 | — | `99 _system/dashboards/Connections Dashboard.md` | **create** |
| 19 | `README.md` | `README.md` | **update** (1 section refresh) |
| 20 | `INDEX.md` | `INDEX.md` | **update** (mermaid + new dataview blocks) |

**Net effect:** 11 file moves + ~15 new files/folders. All atomic, all reversible (git history captures every step). No links break (filenames unchanged).

## MAVIS.md — what it actually contains (draft)

```markdown
# MAVIS — Andre's context for Mavis

> Updated weekly. Stale context = stale output. Article 1's #1 lesson.

## Who Mavis is (one line)
EA on MiniMax-M3, working out of this vault. Capture / surface / draft / track.

## What I'm working on this week
[Linked from `03 Projects/` — currently active: M3 Eval Lab, Mavis EA Design, Vault Refinement]

## What Andre is reading / thinking about
[Update Monday — current obsessions, puzzles, threads I should be alert to]

## What I want from Mavis this week
[5 specific things, not a generic job description]

## Open questions I'm sitting with
[3-5 things I don't have an answer to yet — surfaces them to Mavis so she doesn't gloss over them]

## Hard constraints (always)
- No deploys / pushes (except this vault) / external sends without explicit go
- No fleet (Hermes, OpenClaw, kanban, gbrain) — vault is the boundary
- Reconfirm before destructive ops

## Vault structure (so Mavis re-orients on cold start)
[Pointer to README.md — never duplicate, link]
```

The **update cadence** is the whole point. Article 1 says: "5 minutes every Monday. This single habit is what keeps the AI's context accurate as your thinking evolves."

## The 4 saved workflows (in `07 Vellum/workflows/`)

1. **`process-inbox.md`** — "Read my 00 Inbox from the last 24h. For each note: pick the right 01-CAPTURES subfolder, sharpen the raw capture into one punchy sentence, move it. Then report total processed, patterns noticed, one connection worth exploring."
2. **`daily-brief.md`** — Runs 6am (cron). "Read 00 Inbox (24h) + 02 Notes (7d). Three outputs: CONNECTIONS (3 most interesting, quote actual passages), PATTERN (one pattern across the week — what is my brain working on?), QUESTION (one question worth sitting with). Save as `00 Inbox/brief-{{date}}.md`."
3. **`weekly-connections.md`** — Run Sunday. "Search 02 Notes (all subfolders) for connections. 4 types: same principle across domains / contradiction / pattern connecting 3+ notes / question accidentally answered. Output: 3-5 new notes in `06 Connections/` linking the source notes."
4. **`deep-research.md`** — On-demand. "Read everything in vault related to [topic]. Four things: what I believe, what contradicts that, what's missing, the most important unasked question."

The `process-inbox` and `daily-brief` are the two I'd wire to run automatically. The other two are called by trigger phrase.

## What I will NOT change

- `00 Inbox/`, `01 Daily/`, `03 Projects/`, `04 Resources/`, `05 Archive/`, `99 _system/` — all unchanged
- `SOUL.md`, `agent.md`, `learnings.md` — unchanged (different layer, different cadence)
- obsidian-git auto-commit cadence — unchanged
- Plugin set — unchanged (already have Dataview, Templater, Calendar, Tasks, Smart Connections, Local REST API, Homepage, QuickAdd — covers everything the articles need)
- Daily-note capture habit — unchanged (already aligned with Article 2's #1 habit)

## What this gets me (Article 1's 30/90/180-day curve)

- **30 days:** Daily briefs start surfacing forgotten notes. Type-based organization makes weekly-connections a 30-second Dataview query instead of a manual scan.
- **90 days:** MAVIS.md weekly updates + connections folder = the AI stops needing to re-discover the system every session. The vault starts feeling like working with a chief of staff who has history.
- **180 days:** The eval-logs folder + the 4 workflows = a real feedback loop. I can see which of my outputs Andre acted on, which he archived, and adjust. This is what makes the system compound past 6 months.

## Open decisions (need your call before I execute)

1. **Numbering**: 06/07 vs renaming everything 00-09? I chose 06/07 to avoid breaking existing links. Alternative: full renumber `03→04 / 04→05 / 05→06 / Connections→03 / Vellum→04`. Cleaner numbers, but breaks ~10 existing wikilinks.
2. **MAVIS.md at root vs inside 07 Vellum/**: I chose root. Either works.
3. **Daily-brief cron**: should it actually fire 6am via a script in `99 _system/scripts/`, or stay as a workflow I run manually? Article 1 implies automatic. My hard constraints say I don't deploy/schedule without explicit go.
4. **`_MOCs/` prefix vs no prefix**: I chose `_MOCs/` so they sort to top in the file panel. Alternative: no underscore, accept that they sit mixed with the typed subfolders.
5. **Templater auto-apply**: Article 1 implies templates apply by folder. I have Templater installed. Should I configure the folder→template mapping? (Easy, but irreversible-feeling config change.)

## Rollback plan

Every move goes through `git mv` so history is clean. To rollback: `git revert` the migration commit. Worst case (if something weird happens): restore from the obsidian-git auto-backup at `git@github.com:andrebrassfield/MiniMax-Agent.git`. **Nothing in this refactor can cause data loss.**

## TL;DR

- Add 2 new top-level folders: `06 Connections/`, `07 Vellum/`
- Add 1 new root file: `MAVIS.md` (the VELLUM.md equivalent)
- Sub-organize `02 Notes/` by type: `_MOCs/`, `articles/`, `ideas/`, `patterns/`, `questions/`, `numbers/`
- Move 11 existing notes into the right type-folder
- Create 4 workflow files, 6 new templates, 1 new dashboard
- Update `README.md` and `INDEX.md` to reflect the new structure
- 0 root files moved, 0 wikilinks broken, 0 plugins added, 0 hard constraints crossed

**Say "go" and I execute the migration in one git commit. Say "tweak X" and I revise the design.**
