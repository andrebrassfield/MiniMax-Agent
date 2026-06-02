# MiniMax-Agent — Mavis Vault

This is **Mavis's home** — Andre's executive assistant, running on MiniMax-M3, working out of this Obsidian vault. CHIEF + Vellum-pattern architecture, live since 2026-06-01.

## What's here

| File / Folder | Purpose |
|---------------|---------|
| `SOUL.md` | **Read first.** Who Mavis is, voice, hard constraints. |
| `agent.md` | Operating procedures, vault structure, M3 cheat sheet. |
| `learnings.md` | Discoveries, M3 capabilities, role pivot history, backlog. |
| `README.md` | This file. Vault overview + quick navigation. |
| `INDEX.md` | Dataview dashboards + Mermaid architecture diagram. |
| `MAVIS.md` | **Intelligence layer context file** (VELLUM.md equivalent). Weekly-updated. |
| `00 Inbox/` | Raw captures. Empty regularly. |
| `01 Daily/` | Daily notes (`yyyy-mm-dd.md`). The capture hub. |
| `02 Notes/_MOCs/` | Hub notes (sort to top via underscore prefix). |
| `02 Notes/articles/` | External content digests. |
| `02 Notes/ideas/` | My own observations and theses. |
| `02 Notes/patterns/` | Same principle appearing in different domains. |
| `02 Notes/questions/` | Open questions worth sitting with. |
| `02 Notes/numbers/` | Specific data points. |
| `03 Projects/` | Active projects, one subfolder each (`00 Overview.md`). |
| `04 Resources/` | Reference material, organized by topic. |
| `05 Archive/` | Completed / obsolete (nothing deleted). |
| `06 Connections/` | **Synthesized insights** from 2+ notes. Populated by `weekly-connections` workflow. |
| `07 Vellum/` | **Intelligence layer**: `workflows/`, `eval-logs/`, `weekly-context/`. |
| `99 _system/` | Templates, dashboards, scripts, meta. |

## Vault at a glance

```
Mavis's vault = /Users/brassfieldventuresllc/MiniMax-Agent
  ├─ Identity:  SOUL.md, agent.md, learnings.md, README.md, INDEX.md, MAVIS.md
  ├─ Capture:   00 Inbox → 01 Daily
  ├─ Knowledge: 02 Notes (_MOCs/ + articles/ + ideas/ + patterns/ + questions/ + numbers/)
  ├─ Action:    03 Projects, 06 Connections
  ├─ Long-term: 04 Resources, 05 Archive
  ├─ AI:        07 Vellum (workflows/, eval-logs/, weekly-context/)
  └─ Meta:      99 _system (templates/, dashboards/, scripts/)
  └─ Backup:    git@github.com:andrebrassfield/MiniMax-Agent.git
```

## Intelligence layer (CHIEF + Vellum pattern)

The 2026-06-01 refactor adopted the CHIEF + Vellum pattern from the source articles by @cyrilXBT. Three pieces:

### 1. `MAVIS.md` (vault root, weekly-updated)

The most important file in the system. It is the **VELLUM.md equivalent**: the context file Mavis reads first on every session. It contains: who I am, what I'm working on, what Andre is reading/thinking, what Andre wants from me, open questions, hard constraints, and the live vault structure. **Update cadence: Monday morning, 5 minutes.** Stale context = stale output.

### 2. `07 Vellum/workflows/` — 4 saved prompts, called by trigger phrase

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `process-inbox` | "process my inbox" / "morning processing" | Moves raw captures from `00 Inbox/` to the right typed subfolder in `02 Notes/`, sharpening them. |
| `daily-brief` | "give me my daily brief" | Surfaces 3 connections + 1 pattern + 1 question from the last 7 days. On-demand (6am cron held per hard constraint). |
| `weekly-connections` | "run weekly connections" | Synthesizes the week into 3-5 new notes in `06 Connections/`. Sunday cadence. |
| `deep-research [topic]` | "deep research on X" | Reads the whole vault on a topic, surfaces beliefs, contradictions, gaps, unasked questions. |

### 3. Type-based sub-organization in `02 Notes/`

Captures are organized by **type** (articles, ideas, patterns, questions, numbers) rather than by topic. The reason: a crypto pattern and a psychological principle both go in `patterns/`, and the AI finds the connection automatically. Topic-foldering keeps them apart forever. Each subfolder has a purpose-built template that auto-applies on note creation (Templater folder→template mapping in `data.json`).

### 4. `06 Connections/` — synthesized insights, separate from raw captures

Not a raw capture folder. New ideas that emerge from the relationship between two or more notes live here. Populated by the `weekly-connections` workflow, not manually. This is where the best thinking compounds.

## Plugins in use

- **Dataview** — query the vault like a database
- **Templater** — auto-fill templates; folder→template routing for 8 folders
- **Calendar** — click a date → daily note
- **Tasks** — todo tracking, due dates, recurring
- **obsidian-git** — auto-commit + push to GitHub every 5min
- **Smart Connections** — semantic search across notes
- **Local REST API** — external automation (when needed)
- **Homepage** — opens INDEX on launch
- **QuickAdd** — fast capture from anywhere

## Quick start

```bash
# Where am I?
pwd  # → /Users/brassfieldventuresllc/MiniMax-Agent

# Vault status
cd /Users/brassfieldventuresllc/MiniMax-Agent
git status           # what changed since last commit
git log --oneline    # recent commits

# Today's daily note
# (in Obsidian) Calendar → click today, or Cmd+N → "Today's Daily Note"

# Run a workflow
# (in chat) "process my inbox" or "give me my daily brief" or "run weekly connections"
```

## Working with Mavis

- **Anything you want captured**: just tell me. I'll put it in `00 Inbox/` and process it via `process-inbox`.
- **Anything you want researched**: ask, I'll search the vault + web and summarize with sources.
- **Anything you want drafted**: emails, briefs, agendas, posts — say the audience and tone, I'll write.
- **Anything you want reviewed**: I'll surface what changed, what's stale, what needs attention.
- **Anything irreversible** (delete, push, send, deploy): I'll ask first.

## M3 in one line

> 1M context via MSA sparse attention, native image+video/audio input, drives a desktop, frontier coding, open-weight. **Built to hold an entire second brain in working memory.**

Full capability breakdown in `learnings.md`. The chief-of-staff pattern requires M3 + MAVIS.md together — see the first `06 Connections/` note for why.

---

*Maintained by Mavis. Last touched: 2026-06-01 (CHIEF + Vellum refactor).*
