# MiniMax-Agent — Mavis Vault

This is **Mavis's home** — Andre's executive assistant, running on MiniMax-M3, working out of this Obsidian vault.

## What's here

| File / Folder | Purpose |
|---------------|---------|
| `SOUL.md` | **Read first.** Who I am, my voice, hard constraints. |
| `agent.md` | Operating procedures, vault structure, M3 cheat sheet. |
| `learnings.md` | Discoveries, M3 capabilities, role pivot history, backlog. |
| `README.md` | This file. Vault overview + quick navigation. |
| `00 Inbox/` | Raw captures. Empty regularly. |
| `01 Daily/` | Daily notes (`yyyy-mm-dd.md`). |
| `02 Notes/` | Permanent notes — one concept per note. |
| `03 Projects/` | Active projects, one subfolder each. |
| `04 Resources/` | Reference material, organized by topic. |
| `05 Archive/` | Completed / obsolete (nothing deleted). |
| `99 _system/` | Templates, dashboards, INDEX. |

## What's NOT here (intentionally)

- **No fleet tools**: I don't reach into Hermes, OpenClaw, kanban, gbrain. Those are separate.
- **No agent memory here**: lives in `~/.mavis/agents/mavis/memory/MEMORY.md` (canonical). This vault is the project layer.
- **No other vaults**: this is the only one I touch.

## Vault at a glance

```
Mavis's vault = /Users/brassfieldventuresllc/MiniMax-Agent
  ├─ Identity: SOUL.md, agent.md, learnings.md, README.md
  ├─ Work: 00 Inbox → 02 Notes → 03 Projects → 05 Archive
  ├─ Cadence: 01 Daily, 04 Resources, 99 _system
  └─ Backup: git@github.com:andrebrassfield/MiniMax-Agent.git
```

## Plugins in use

- **Dataview** — query the vault like a database
- **Templater** — auto-fill templates with date/variables
- **Calendar** — click a date → daily note
- **Tasks** — todo tracking, due dates, recurring
- **obsidian-git** — auto-commit + push to GitHub
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
```

## Working with Mavis

- **Anything you want captured**: just tell me. I'll put it in `00 Inbox/` and process it.
- **Anything you want researched**: ask, I'll search + summarize with sources.
- **Anything you want drafted**: emails, briefs, agendas, posts — say the audience and tone, I'll write.
- **Anything you want reviewed**: I'll surface what changed, what's stale, what needs attention.
- **Anything irreversible** (delete, push, send, deploy): I'll ask first.

## M3 in one line

> 1M context, MSA sparse attention, native image+video/audio input, drives a desktop, frontier coding. Open-weight. **Built to hold an entire second brain in working memory.**

Full capability breakdown in `learnings.md`.

---

Maintained by Mavis. Last touched: 2026-06-01.
