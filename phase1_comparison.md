---
# Phase 1 Comparison: Raw Loop vs Claude Agent SDK
# What Did the Harness Give Me for Free?
---

I wrote an agent twice. Same basic capability — read notes, search web, write briefing. Two different harnesses. The gap is not subtle.

## What I Wrote Myself in Build #1 (45 lines)

A while-loop calling `client.messages.create()`, parsing `tool_use` blocks, routing to three Python functions, appending `tool_result`, and looping. It worked. The loop is ~15 lines. The tool stubs are ~20 lines. The system prompt is a single string. No caching. No retries. No isolation.

**What breaks at line 46:** no sessions (lose all state on crash), no prompt caching (pay for system prompt every turn), no tool retry logic (one bad search = dead agent), no sub-agent isolation, no context window management (blow past limit on long sessions).

## What the Claude Agent SDK Gave Me for Free

**1. CLAUDE.md as persistent system prompt.** One file read at startup. The agent has project conventions without hardcoding them. My raw loop had a string literal.

**2. Skill progressive disclosure.** `research-summary/SKILL.md` loads only when the `--skill` flag is set. Not in every session. My raw loop has one prompt fits all.

**3. PostToolUse hooks.** The `autoformat_hook.py` fires after every file write — no agent code needed. My raw loop would need explicit format calls after every write.

**4. Sub-agent Task tool.** Built-in isolation. The research sub-agent gets a clean context, works independently, returns a compressed summary. My raw loop would need to implement this from scratch (spawn a subprocess, pipe results, merge contexts).

**5. Built-in tool definitions.** `text_editor_20241022`, `bash_20241022` — SDK-typed, cached, tested. My raw loop had raw JSON schemas I wrote by hand.

**6. Prompt caching.** SDK caches system prompt + tools. Saves ~90% on repeated calls in a session. My raw loop re-sends everything every time.

**7. Session persistence.** SDK snapshots and resumes across crashes. My raw loop dies with an unhandled exception and loses all state.

**8. Token counting + budgeting.** Built-in. My raw loop would burn to $0 without noticing.

**The harness is 86% of the value.** The model is just the CPU. The harness is the OS.