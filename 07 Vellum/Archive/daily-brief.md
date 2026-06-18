---
type: workflow
name: daily-brief
trigger: "give me my daily brief"
cadence: on-demand (Article 1 says 6am auto; we run on-demand per hard constraint)
created: 2026-06-01
---

# Daily Brief

## Purpose

Surface 3 connections, 1 pattern, and 1 question across the last week of captures. This is the moment the system earns its place — read this **before** opening any app, every morning without exception.

## When to use

- First thing each morning
- When you need a fast re-orient to "what have I been working on"
- Before any major decision (forces the vault to surface relevant context)

## Prompt

> Read everything in my `00 Inbox/` from the last 24 hours and everything in `02 Notes/` (all subfolders) from the last 7 days.
>
> Then do three things:
>
> **CONNECTIONS** — find the 3 most interesting connections between recent captures and older notes I probably have not noticed. Be specific. **Quote the relevant passages from my actual notes** (use the exact text from the source files, with `[[wikilinks]]` back to the source).
>
> **PATTERN** — identify one pattern across everything I have been reading this week. What is my brain clearly working on even if I have not stated it explicitly? Name the pattern in one sentence, then show the evidence (3+ notes that demonstrate it).
>
> **QUESTION** — give me one question worth sitting with today based on the pattern you identified. Not a task. A question. The kind that changes how you think about the work, not the kind that fits on a todo list.
>
> Save this as a markdown file in `00 Inbox/` named `brief-{{date}}.md`.

## Why on-demand, not cron

The 6am auto-fire pattern from Article 1 is appealing but crosses Mavis's hard constraint: **no schedule changes without explicit in-session approval**. Build the habit first (use the trigger phrase every morning for 2 weeks). If it sticks and the value is real, then we add the cron.

## Related

- `process-inbox.md` — run this BEFORE the brief so the inbox is clean
- `weekly-connections.md` — Sunday's deeper sweep across the whole week
