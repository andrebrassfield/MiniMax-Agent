#!/usr/bin/env python3
"""
Phase 1 Build #2: Daily Briefing Agent on Claude Agent SDK

Demonstrates:
- CLAUDE.md project conventions
- research-summary Skill loaded via SDK
- AutoFormat PostToolUse hook
- Research sub-agent via Task tool

Run: python3 phase1_claude_sdk/claude_sdk_briefing_agent.py
"""

import anthropic
import os
from datetime import date

CLAUDE_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
try:
    from anthropic.types import ToolParam
    SDK_TOOLS: list[ToolParam] = [
        {"type": "text_editor_20241022", "name": "write"},
        {"type": "bash_20241022", "name": "bash"},
        {"type": "text_editor_20241022", "name": "edit"},
    ]
except Exception:
    # Fallback to raw list if SDK version mismatch
    SDK_TOOLS = []

DAILY_BRIEFING_PROMPT = """
You are a daily briefing agent with CLAUDE.md conventions and the research-summary skill loaded.

TASK:
1. Read today's Markdown notes from ~/vault/daily-notes/{today}.md (if exists)
2. Read recent RSS content from any cached feed file
3. Spawn a RESEARCH SUB-AGENT via the Task tool for any topic needing deeper investigation
4. Write a briefing to {output_path} using the research-summary output format

FORMAT:
# Daily Briefing - {date}
## TL;DR
[one-paragraph summary of the most important things]

## [Topic 1]
[Using research-summary format: claims with citations]

## [Topic 2]
...

CRITICAL: Run black, isort, and ruff format on any Python files you write (the AutoFormat hook does this automatically).
CRITICAL: Every claim must have an inline source citation.
CRITICAL: The research-summary skill's output format is loaded — use it.
"""

def main():
    today = date.today()
    output_path = os.path.expanduser(f"~/briefings/{today.isoformat()}.md")
    prompt = DAILY_BRIEFING_PROMPT.format(
        date=today.isoformat(),
        today=today.isoformat(),
        output_path=output_path,
    )

    # This is a sketch of the SDK harness call.
    # In real usage with claude-code or Claude Agent SDK CLI:
    # $ claude -p "$prompt" --skill research-summary --hook ./hooks/autoformat_hook.py

    print(f"Phase 1 Build #2: Daily Briefing Agent (SDK version)")
    print(f"Today: {today.isoformat()}")
    print(f"Output: {output_path}")
    print()
    print("To run this with Claude Agent SDK:")
    print()
    print(f"  claude --skill research-summary --hook hooks/autoformat_hook.py \\")
    print(f'    -p "{prompt[:80]}..."')
    print()
    print("The SDK harness gives you:")
    print("  - CLAUDE.md auto-loaded as system prompt")
    print("  - Skill SKILL.md loaded at startup")
    print("  - Hooks fire after every tool call")
    print("  - Task tool for sub-agent spawning")
    print("  - Built-in tool definitions (text_editor, bash, etc)")
    print("  - Prompt caching on system prompt + tools")
    print("  - Token counting and budgeting")
    print("  - Session persistence across crashes")

if __name__ == "__main__":
    main()