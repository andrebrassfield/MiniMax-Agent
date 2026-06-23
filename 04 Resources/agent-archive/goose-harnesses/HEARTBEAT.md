# HEARTBEAT.md — Goose

## Heartbeat: every 15 minutes
```
1. poll_mavis_tasks(limit=3) — check for waiting work
2. If tasks exist → execute immediately, skip wait
3. If empty → log idle, wait 60s
```

## Health Checks (hourly)
- Verify openclaw-bridge MCP connection
- Check worktree inventory (cleanup stale worktrees)
- Verify kanban.db write access

## Alert Rules
- MCP bridge down → flag Mavis via emit_completion
- Worktree limit reached → flag OpenClaw for cleanup
- 0 tasks for 2h+ → log idle state