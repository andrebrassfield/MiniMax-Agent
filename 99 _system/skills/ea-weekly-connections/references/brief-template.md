# Brief Template — ea-weekly-connections

The connection brief template. The chief writes the
brief to `02 Notes/connections/YYYY-WNN-synthesis.md`
after running the 4-step procedure.

## Full template

```markdown
# Weekly Connections — Week NN, YYYY (MM-DD to MM-DD)

> Generated: <YYYY-MM-DD HH:MM CT> | Author: Mavis (EA) | Window: last 7 days
> Connections surfaced: <N> | Surfaces scanned: 5 (daily, kanban, workers, memory, skills)

## Connection 1: <title>

**Surfaces:** <surface 1>, <surface 2>, ...
**Pattern:** <1-2 sentences>
**Evidence:** <file paths / dates>
**What this means for Andre:** <synthesis>
**What to do:** <action or "no action — informational">

## Connection 2: ...

## What's not on this list (deliberate omissions)

<1-2 sentences on what Mavis considered and rejected, so
Andre can audit the selection.>

## Open threads

<Any patterns that almost-connected but didn't quite —
keep for next week.>
```

## Per-connection fields

- **Title** — 5-10 words, descriptive. Names the
  pattern, not the surface.
- **Surfaces** — which ≥2 surfaces the connection spans
  (daily, kanban, workers, memory, skills).
- **Pattern** — 1-2 sentences naming the underlying
  pattern (the type from `4-connection-types.md`).
- **Evidence** — file paths, line numbers, dates. The
  evidence must be a real disk hit.
- **What this means for Andre** — 1-2 sentences in EA
  voice (synthesis + why, not "the data shows X").
- **What to do** — 1-2 sentences, concrete. "Schedule
  a 30-min review of X" is concrete. "Consider" /
  "monitor" are not.

## Per-section content discipline

- **Header:** generated timestamp, author, window (last 7
  days), connections surfaced (3-5), surfaces scanned (5).
- **Connection blocks:** each block is 1 paragraph
  (Surfaces, Pattern, Evidence, What this means, What to
  do). Use the bolded field names as anchors.
- **What's not on this list:** 1-2 sentences naming the
  things Mavis considered and rejected. The audit trail
  for the selection.
- **Open threads:** 1-3 patterns that almost-connected.
  These stay for next week (don't force-fit them into
  this week's brief).

## What this template is NOT

- **Not a project summary.** Project summaries live in
  `03 Projects/<project>/` directories. The weekly is
  for cross-project connections.
- **Not a kanban review.** Kanban state is one of the 5
  surfaces, not the output.
- **Not a memory audit.** Memory appends are one of the
  5 surfaces. The output is the cross-domain connection.
- **Not exhaustive.** 3-5 connections is the spec. 7+
  is signal-diluted. <3 is insufficient material.
- **Not the daily brief.** That's `ea-daily-brief`
  (different cadence, different scope).

## Filename convention

`02 Notes/connections/YYYY-WNN-synthesis.md`

- `YYYY` = 4-digit year
- `W` = "W" prefix
- `NN` = ISO week number (01-53)
- `-synthesis.md` = suffix

Examples:
- `2026-W25-synthesis.md` (week 25 of 2026)
- `2026-W26-synthesis.md` (week 26 of 2026)

The ISO week number can be computed:
```bash
date "+%Y-W%V"
```
