---
name: telegram-kanban-bridge
description: >
  Telegram C2 bridge for Hermes Kanban — slash commands /board /spawn /health /brain.
  Direct aiogram bot, standalone from OpenClaw MCP bridge. Includes 30s error-task
  polling loop with inline keyboard [Retry] [Archive] [View Logs] buttons.
  Trigger keywords: telegram bridge, kanban from telegram, telegram C2, slash commands bot,
  error task alerts, task management from telegram.
version: 1.2.0

triggers: [telegram kanban bridge]
---

# Telegram Kanban Bridge v1.2

## Overview

Standalone aiogram 3.x Telegram bot exposing Hermes Kanban and G-Brain as slash
commands. Does NOT use the OpenClaw MCP bridge — direct Telegram polling for
mobile-first C2.

**Owner-only** — only `6598264778` can trigger commands (hardcoded).

## Commands

| Command | Description |
|---------|-------------|
| `/board` | List all tasks (up to 10 shown) |
| `/board <status>` | Filter: running, ready, blocked, done, todo, error, triage |
| `/spawn <title>` | Create task: assignee=`backend-engineer`, priority=5, status=`ready` |
| `/health` | Gateway health + kanban stats + 24h stall counts |
| `/brain <query>` | Query G-Brain, return top 3 results |
| `/start` | Welcome + command reference |

## Error Polling Loop

Every 30 seconds the bot queries for `status='error'` tasks. For each new
errored task, sends a Telegram alert with inline keyboard:

- **[Retry]** — sets status=`ready`, resets `consecutive_failures=0`
- **[Archive]** — sets status=`done`
- **[View Logs]** — tells user to run `hermes kanban show <id>`

Alerts go to `TELEGRAM_ALERT_CHAT_ID` if set (env var).

## Architecture

```
Telegram → aiogram bot (polling, port-free)
         → kanban SQLite at ~/.hermes/kanban.db
         → G-Brain MCP at localhost:15332 (JSON-RPC HTTP)
         → Hermes gateway at localhost:8644 (health only)
         → verdicts.db at ~/.hermes/evolver/verdicts.db (stall counts)
```

## Setup

**Install (one-time):**
```bash
pip install aiogram==3.22.0 aiosqlite==0.22.1
```

**Token** — from `~/.openclaw/openclaw.json` → `channels.telegram.botToken`:
```bash
export TELEGRAM_BOT_TOKEN="your:bot_token_here"
export TELEGRAM_ALERT_CHAT_ID="-1001234567890"   # optional
```

**Run:**
```bash
python3 ~/.mavis/skills/telegram-kanban-bridge/scripts/tg_bridge.py
```

**Daemonize:**
```bash
nohup python3 ~/.mavis/skills/telegram-kanban-bridge/scripts/tg_bridge.py \
  >> ~/.hermes/logs/tg-bridge.log 2>&1 &
echo $! > ~/.hermes/pids/tg-bridge.pid
```

## Kanban Schema (Critical)

The kanban `tasks` table columns:

```sql
-- ALWAYS query these (safe subset):
id, title, body, status, assignee, priority,
created_at, started_at, completed_at,
tags, consecutive_failures, last_failure_error

-- Optional (may not exist on all installs):
workspace_kind, workspace_path, parent_id, kind, result, tenant
```

**Rules:**
- `created_at` is Unix **seconds** (not milliseconds)
- `status` values: `todo`, `triage`, `ready`, `in_progress`, `running`,
  `blocked`, `error`, `done`, `rejected`
- Do NOT query `*` — always specify explicit columns
- `body` is the task description (NOT called `description`)
- `kind` is NOT `event_type`

## /spawn Task Insert

```python
# Correct field names:
task_id   = f"tg-{int(time.time())}-{abs(hash(title)) % 0xFFFFFF:06x}"
body      = json.dumps({"source": "telegram", "title": title})  # title goes in body
status    = "ready"
kind      = "triage"        # task kind (not status)
priority  = 5
assignee  = "backend-engineer"
created_by = "telegram"
created_at = int(time.time())  # Unix seconds
```

## G-Brain Query

1. Try G-Brain MCP at `localhost:15332/rpc` (JSON-RPC HTTP POST)
2. Fallback: grep in `~/vault/` if MCP unreachable
3. Timeout: 10s per attempt

## Safety Rules

1. Owner-only (`6598264778`) — unauthorized users get `Unauthorized` reply
2. `/spawn` title sanitized: 5-200 chars, no shell metacharacters `;&|$>`"'
3. Output truncated at 4000 chars (Telegram limit)
4. DB writes go to kanban SQLite only
5. 30-second command timeout with busy error

## Error Handling

| Condition | Behavior |
|-----------|----------|
| Kanban DB locked | Reply `Database busy, retry in 30s` |
| G-Brain MCP down | Fall back to vault grep |
| Invalid `/spawn` title | Reply with validation error |
| Gateway health check fails | Reply with local DB stats only |
| Error poll loop exception | Logged, never crashes the bot |

## Files

- Skill definition: `~/.mavis/skills/telegram-kanban-bridge/SKILL.md`
- Bot script: `~/.mavis/skills/telegram-kanban-bridge/scripts/tg_bridge.py`
- PID file: `~/.hermes/pids/tg-bridge.pid`
- Log file: `~/.hermes/logs/tg-bridge.log`
