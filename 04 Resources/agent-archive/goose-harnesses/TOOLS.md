# TOOLS.md — Goose Tool Stack

## Kanban (via openclaw-bridge MCP)
- `poll_mavis_tasks` — claim coding tasks
- `claim_task` — atomic task lock
- `emit_completion` — report results
- `list_openclaw_tasks` — current task state

## Playwright MCP
Browser automation for:
- UI testing, DOM validation
- Web scraping, procurement
- Screenshot comparisons

## Computer Use (cu)
Desktop control for local app automation

## Matrix
Web search, image generation, video, audio

## Reference Stacks (read-only)
```
~/.gbrain/repos/oh-my-pi.git/AGENTS.md
~/.gbrain/repos/goose.git/AGENTS.md
~/.gbrain/repos/agency-agents.git/engineering/
~/.gbrain/repos/Archon.git/.archon/
~/.gbrain/repos/mattpocock-skills.git/
~/.gbrain/repos/llama.cpp.git/
~/.gbrain/repos/anthropics-skills.git/
~/.gbrain/repos/karpathy-skills.git/
~/.gbrain/repos/goose.git/
~/.gbrain/repos/agency-agents.git/
```

## Prohibited
- Modifying main branch directly
- Executing unclaimed tasks
- Skipping test runs before reporting success
- Long conversational responses to Andre