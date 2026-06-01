# agent.md — Mavis Operating Procedures

This is the procedural companion to `SOUL.md`. Read it when I need to do real work — write code, manage the fleet, run commands, edit configs, dispatch tasks.

## Current state (2026-06-01)
- **Model**: `MiniMax-M3` (replaces M2.7-highspeed)
- **Workspace**: `/Users/brassfieldventuresllc/MiniMax-Agent/` (this dir, fresh)
- **Agent home**: `~/.mavis/agents/mavis/` (canonical agent root)
- **Active session**: `mvs_d566bc5ad049499cb7412761237b9463`

---

## Fleet — the lay of the land

### Core paths
| What | Path |
|------|------|
| Hermes agent | `~/.hermes/hermes-agent/` (v2026.5.16) |
| Kanban DB | `~/.hermes/kanban.db` (1.5MB, ~73 tasks) |
| GBrain | `~/.gbrain/` (PostgreSQL-backed knowledge base) |
| OpenClaw | MCP at port 15331 (Telegram/browser bridge) |
| Obsidian Vault | `/Users/brassfieldventuresllc/Documents/Obsidian Vault` |
| Git Vault | `/Users/brassfieldventuresllc/vault` |
| Hermes profiles | `~/.hermes/profiles/<name>/config.yaml` (24 total) |
| Hermes worktrees (sandbox) | `~/.hermes-worktrees/` |
| SSH deploy key | `~/.ssh/id_ed25519` |
| Supabase project | `xfqlxujtaticrsbcasai` (Postgres, IPv6 only) |

### Active fleet (restructured 2026-05-18, 11 profiles)
**Orchestrators** (kanban/gateway/memory only): `macro-orchestrator`, `eng-orchestrator`, `content-orchestrator`
**Landscape & Macro**: `stock-monitor`, `landscape-monitor`
**Code & Engineering**: `lead-architect`, `backend-engineer`, `qa-auditor`
**Content & Research**: `content-researcher`, `text-producer`, `visual-producer`

### Model providers (full stack in `memory/fleet-model-routing.md`)
- **Default**: `minimax/MiniMax-M3` (was M2.7-highspeed)
- Workers: minimax, fireworks, nvidia NIM, Gemini, Nous, CodeX
- GBrain embeddings: `zeroentropyai:zembed-1` @ 2560d
- MLX ModernBERT: 768d (agent-side only, can't hot-swap with zembed)

---

## Kanban — schema and gotchas

### Schema invariants (read these before any kanban write)
- `body` NOT `description` | `kind` NOT `event_type`
- `created_at` is INTEGER seconds (normalize: `CASE WHEN x >= 1e12 THEN x/1000 ELSE x END`)
- `completed_at` is in **milliseconds** — convert on read
- Default status on create: `triage` (Hermes has no `pending` status)
- Dispatch requires `status='ready'` (lowercase) + valid assignee
- Ghost task = `tasks.status='done'` + latest `task_run.outcome IS NULL`

### Status ownership
- Workers own: `RUNNING → COMPLETE/ERROR`
- Dispatcher owns: `TODO → READY`, `READY → RUNNING`, `BLOCKED → READY`
- **Always use `apply_status_change()`** for bridge writes — never raw `UPDATE SET status=?`

### Task creation (raw SQLite, since `KanbanDB` Python import can fail)
```sql
INSERT INTO tasks (id, title, body, status, kind, assignee, created_by, created_at)
VALUES (?, ?, ?, 'triage', ?, ?, ?, ?)
-- created_at = INTEGER milliseconds (epoch * 1000)
```

### Profile must exist before assignment
Check `~/.hermes/profiles/<name>/auth.json` exists. Non-existent profile = silent dispatch failure.

### Dispatcher location
Embedded in gateway since v2026.5.x. Never run `hermes kanban daemon` as a standalone command.

---

## GBrain — write path and embeddings

### Always use `gbrain put <slug>` (source_id=vault)
Direct Supabase REST POST/PATCH sets `source_id=default` and breaks graph traversal + FTS indexing.

### Edge cases
- gbrain CLI is broken by PgBouncer — use OpenClaw bridge `query_gbrain` via Supabase REST API as fallback
- Supabase `search_vector` trigger requires tsvector NOT raw text (INSERT violation otherwise)

---

## Git — always SSH, never HTTPS

```bash
export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519"
```

Fine-grained PATs fail with HTTPS. Deploy key is the only way.

---

## Hard rules for editing configs

When editing `~/.hermes/config.yaml` (or any critical YAML):
1. **BACKUP FIRST**: `cp config.yaml config.yaml.bak`
2. **Verify diff after edit**: `git diff config.yaml`
3. YAML indentation is critical — one wrong indent silently corrupts the gateway
4. If startup fails: `git checkout HEAD -- config.yaml` to restore
5. Never paste multi-line blocks without verifying exact insertion point

---

## Memory — three layers (narrowest first)

1. **Project memory** (`AGENTS.md` in the repo, or topic file referenced from it) — only true in this project
2. **Agent memory** (`~/.mavis/agents/mavis/memory/MEMORY.md` + topic files) — true on a different project
3. **User memory** (`~/.mavis/memory/user.md`) — would the conclusion change for a different user? (requires `--reason`)

**Append** = new entry. **Edit/Write** = update, merge, remove. Don't mix.
**Language**: write in the user's natural language (English here).
**Memory is a hint, not live state** — verify before acting on it.

---

## Routing decisions

| Situation | Action |
|-----------|--------|
| Conversation, Q&A, recommendation, simple lookup | Handle myself |
| 3+ independent parallel tracks, needs verifier, high error cost | `mavis-team` plan |
| Review/test/audit on existing deliverable | Spawn single-shot verifier worker |
| Multi-message spec block from Andre | Acknowledge → audit → report gaps → wait for "go" |
| Major irreversible action pending | Reconfirm before pulling the trigger |

### Single-shot worker rules
- **Verifier-only**: review, test, audit on existing deliverable
- **Producer work** (code, refactor, feature, bug fix): do it myself or route through `mavis-team`
- Never use `--command prompt` to a random existing session as a shortcut

---

## Async monitoring

After kicking off async work (CI, MR auto-merge, external API, human reply): set a cron self-reminder before ending the turn. The system reminder will nudge me — listen to it.

`mavis team plan` is the exception — it has its own heartbeat, don't cron it.

---

## Night mode (after-hours autonomous work)
**Allowed**: local research, code in `~/.hermes-worktrees/`, tests, docs, gbrain sync
**Not allowed**: deploys, pushes, migrations, external sends, credential changes, destructive ops
`~/.hermes-worktrees/` is outside any git working tree — true sandbox isolation.

---

## Self-check before ending a turn

- [ ] Did I learn anything reusable? → write to memory now
- [ ] Did I start async work without a cron reminder? → set one
- [ ] Did I just commit something destructive without approval? → reverse it
- [ ] Did I take a spec block as an order? → back up, audit, wait for "go"
