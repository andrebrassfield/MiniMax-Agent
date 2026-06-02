# weekly_connections — starting skill
# This is the hand-written baseline. SkillOpt will optimize this.
# Source of truth for current behavior: 07 Vellum/workflows/weekly-connections.md

You are synthesizing the week's captures into 3-5 connection notes in `06 Connections/`. Single-day synthesis misses the slow-burn patterns; the week-at-once view catches them.

## Inputs

- All notes added to `02 Notes/` (all subfolders) in the last 7 days
- Existing notes in `02 Notes/` from prior weeks (for cross-week connections)

## Connection types (use exactly these four)

- **TYPE A** — same underlying principle in two completely different domains (e.g., a `patterns/` note matches an `ideas/` note)
- **TYPE B** — contradiction between two notes that creates interesting tension (both sides are right; the tension is the insight)
- **TYPE C** — pattern connecting 3+ notes into one unnamed insight (the whole is greater than the sum)
- **TYPE D** — a question from one note that another note accidentally answers (without the author knowing they were answering)

## For each strong connection, produce

1. **Type** (A, B, C, or D)
2. **One-sentence bridge** between the ideas
3. **New note in `06 Connections/`** named `YYYY-MM-DD - <slug>.md` (use today's date)

## Output format per connection note

```markdown
# {Slug} — {Type}: {One-sentence bridge}

**Type**: A | B | C | D
**Date**: YYYY-MM-DD
**Sources**: [[source note 1]], [[source note 2]] (+ more for Type C)

## Why this connection matters
[2-3 sentences explaining the insight, not just restating the sources]

## The bridge
[The one-sentence connection, expanded with evidence from both sources]
```

## Rules

- **Minimum 3, maximum 5 connections.** Quality over quantity.
- **Only surface connections that would genuinely surprise Andre.** A connection between two notes that already wikilink each other is not a connection; it's redundancy.
- **If you cannot find 3 strong connections, say so explicitly.** That is a signal about whether the week's inputs were diverse enough.
- **Every source must be a real note** in Andre's vault, reachable by `[[wikilink]]`.
