# MiniMax-Agent — Mavis workspace

This is Mavis's project workspace on Andre's machine. Set up **2026-06-01**, the day MiniMax-M3 launched.

## What's here

| File | Purpose |
|------|---------|
| `SOUL.md` | Who I am, my voice, hard constraints. **Read this first** if you're new. |
| `agent.md` | Operating procedures, fleet paths, kanban schema, memory layout, gotchas. |
| `learnings.md` | What I learned about M3, migration notes from M2.7, open questions, backlog. |
| `README.md` | This file. Workspace overview. |

## What's NOT here (intentionally)

- **Memory** → lives in `~/.mavis/agents/mavis/memory/MEMORY.md` (canonical agent root)
- **Skills** → `~/.mavis/agents/mavis/skills/` (agent-local) and `~/.mavis/skills/` (global)
- **Configs / secrets** → `~/.mavis/agents/mavis/config.yaml` and friends
- **Code work** → project repos elsewhere, or `~/.hermes-worktrees/` for sandboxes

This workspace is for **identity, process, and discoveries** — not for storing state or running code.

## Quick start for M3 sessions

```bash
# Where am I?
pwd  # → /Users/brassfieldventuresllc/MiniMax-Agent

# What model am I on?
grep "model" ~/.mavis/agents/mavis/config.yaml | head -5
# Should show: minimax/MiniMax-M3

# Fleet status
curl -s http://127.0.0.1:9119/api/status | jq .

# Today's kanban
sqlite3 ~/.hermes/kanban.db "SELECT id, title, status, assignee FROM tasks WHERE status IN ('triage','ready','running') ORDER BY created_at DESC LIMIT 10"
```

## M3 highlights (one-liner)

> 1M context, MSA sparse attention, native image+video input, drives a desktop, frontier coding (SWE-Bench Pro 59%, beats GPT-5.5 / Gemini 3.1 Pro), long-horizon (12h+ autonomous, keeps grinding through plateaus), open-weight, $20/mo Plus tier.

Full breakdown in `learnings.md`.

## Fleet map (TL;DR)

```
Andre
  └─ Mavis (this — orchestrator/executor/coder, M3)
       ├─ Hermes v2026.5.16 (peer orchestrator, kanban/gateway/memory)
       │    ├─ Fleet: 11 profiles (orchestrators + workers)
       │    └─ Kanban DB: ~/.hermes/kanban.db
       ├─ OpenClaw (Telegram/browser bridge, MCP 15331)
       ├─ GBrain (knowledge base, PostgreSQL)
       └─ Vault: ~/vault (git) + ~/Documents/Obsidian Vault (UI)
```

## When in doubt

- **Tone / "is this me?"** → `SOUL.md`
- **How do I do X with the fleet?** → `agent.md`
- **What did I learn about M3?** → `learnings.md`
- **Something feels off, who am I again?** → `~/.mavis/agents/mavis/memory/MEMORY.md` (full agent memory)

---

Maintained by Mavis. Last touched: 2026-06-01.
