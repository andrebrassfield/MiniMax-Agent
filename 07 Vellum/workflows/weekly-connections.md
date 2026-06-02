---
type: workflow
name: weekly-connections
trigger:
  - "run weekly connections"
  - "find this week's connections"
cadence: weekly (Sunday)
created: 2026-06-01
---

# Weekly Connections

## Purpose

Synthesize the week's captures into 3-5 new connection notes in `06 Connections/`. The strongest cross-domain insights emerge when an entire week is processed at once — single-day synthesis misses the slow-burn patterns.

## When to use

- Sunday morning or evening, as the closing ritual of the week
- Whenever `02 Notes/` has 7+ new notes across multiple subfolders

## Prompt

> Read all notes added to my `02 Notes/` folder (all subfolders: `articles/`, `ideas/`, `patterns/`, `questions/`, `numbers/`, `_MOCs/`) in the last 7 days. Search for connections across all subfolders simultaneously.
>
> A strong connection is one of these four types:
>
> - **TYPE A** — the same underlying principle appearing in two completely different domains (e.g., a pattern from `patterns/` matches an observation in `ideas/`)
> - **TYPE B** — a contradiction between two notes that creates interesting tension (both sides are right, and the tension is the insight)
> - **TYPE C** — a pattern connecting three or more notes into one unnamed insight (the whole is greater than the sum)
> - **TYPE D** — a question from one note that another note accidentally answers (without the author knowing they were answering)
>
> For each strong connection:
> 1. **Name the connection type** (A, B, C, or D)
> 2. **Write a one-sentence bridge** between the ideas
> 3. **Create a new note in `06 Connections/`** linking the source notes (use `[[wikilinks]]` to both sources, name the connection file with the date and a short slug, e.g. `2026-06-08 - capture-as-edge.md`)
>
> Only surface connections that would genuinely surprise me. **Minimum three. Maximum five. Quality over quantity.**
>
> If you can't find at least 3 strong connections, say so explicitly — that itself is a signal about whether the week's inputs were diverse enough.

## Output format

Each connection note should follow this structure:

```markdown
# {Slug} — {Type letter}: {One-sentence bridge}

**Type**: A | B | C | D
**Date**: {YYYY-MM-DD}
**Sources**: [[source note 1]], [[source note 2]] (+ more for Type C)

## Why this connection matters
[2-3 sentences explaining the insight, not just restating the sources]

## The bridge
[The one-sentence connection, expanded with evidence from both sources]
```

## Related

- `process-inbox.md` — daily prep
- `daily-brief.md` — daily synthesis (lighter weight, runs every day)
