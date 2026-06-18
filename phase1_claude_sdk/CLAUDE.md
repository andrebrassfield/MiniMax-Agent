# CLAUDE.md — Daily Briefing Agent Project Conventions

## Project Overview
Daily briefing agent that reads Markdown notes + RSS feeds, writes summarized briefing to disk every morning.

## Architecture
- **Agent**: Single Claude Agent SDK agent with sub-agent delegation
- **Tools**: web_search, read_file, write_file (via SDK tool definitions)
- **Skills**: research-summary (loaded via skill system)
- **Hooks**: AutoFormat PostToolUse hook — runs black/isort/ruff on Python files after write

## Code Conventions
- **File locations**: Agents in `agents/`, skills in `skills/`, hooks in `hooks/`
- **Testing**: pytest, run with `python -m pytest tests/` from project root
- **Linting**: ruff format + ruff check on every file write (via AutoFormat hook)
- **Type hints**: Optional in agent code; required in shared modules

## Skill System
- Skills live in `.claude/skills/<skill-name>/`
- Each skill has `SKILL.md` + optional `scripts/` + `templates/`
- Load via `--skill` flag or `SKILLS` env var

## Sub-Agent Pattern
- Research sub-agent spawned via Task tool with isolated context
- Returns compressed summary to parent
- Parent writes final briefing

## Scheduling
- Runs daily at 08:00 via cron
- Logs to `run_log.md` with timestamp, duration, status, token count

## Output Format
- Briefings written to `~/briefings/YYYY-MM-DD.md`
- Format: `# Daily Briefing - YYYY-MM-DD` + sections per topic
- Each claim inline-cited with source: `[source: filename.md#section]`