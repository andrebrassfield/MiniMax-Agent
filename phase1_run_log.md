# Run Log — Phase 1 Daily Briefing Agent

> Experiment tracking for the Phase 1 daily briefing cron job.
> Log entry format: `ts=YYYY-MM-DD HH:MM dur=<seconds> status=<ok|fail|skip> files=<count> tokens=<estimate>`

## 2026-06-06

- **First run (manual test)**: Phase 1 artifacts created successfully.
  - raw_agent_loop.py (45 lines, Anthropic SDK, 3 tools) — runnable, tools are stubs
  - claude_sdk_briefing_agent.py — SDK version with hooks, skills, sub-agent
  - phase1_comparison.md — 200-word harness-vs-raw analysis
  - Cron job registered: `0 8 * * *` — first briefing tomorrow at 08:00

## Observations

- The raw loop is fragile. No retry on tool failure, no session persistence, no caching.
- The SDK version would handle all of those, but requires the Claude Agent SDK to be installed.
- For Hermes, the kanban-worker loop IS the "raw loop" equivalent — it's battle-hardened.

## Known Failure Modes (to watch for)

1. **File not found**: If `~/vault/daily-notes/` doesn't have today's file, the agent should create a briefing from whatever it finds.
2. **RSS feed unavailable**: Web search may fail. Agent should degrade gracefully (produce a local-only briefing).
3. **Empty briefing**: If no content to summarize, agent should explain why rather than produce a blank document.
4. **Token budget**: With web_search + file reads, a full briefing could run 50+ tool calls. Budget explicitly.
5. **Scratch workspace**: The kanban worker writes to a scratch dir. Output must be copied to `~/briefings/` for persistence.