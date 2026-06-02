# daily_brief — starting skill
# This is the hand-written baseline. SkillOpt will optimize this.
# Source of truth for current behavior: 07 Vellum/workflows/daily-brief.md

You are producing the daily brief. The brief is the moment the system earns its place — read this before opening any app, every morning.

## Inputs

- `00 Inbox/` from the last 24 hours
- `02 Notes/` (all subfolders) from the last 7 days
- Today's daily note (`01 Daily/YYYY-MM-DD.md`) if it exists

## Output structure (exactly these three sections, in this order)

### CONNECTIONS — 3 specific connections
Find 3 connections between recent captures and older notes Andre probably has not noticed. Be specific. **Quote the relevant passages from Andre's actual notes** (use the exact text from the source files, with `[[wikilinks]]` back to the source). A connection is "specific" if it links named notes, not themes.

### PATTERN — 1 pattern across the week
Identify one pattern across everything Andre has been reading this week. What is Andre's brain clearly working on, even if not stated explicitly? Name the pattern in one sentence, then show the evidence (3+ notes that demonstrate it).

### QUESTION — 1 question worth sitting with
One question worth sitting with today based on the pattern. Not a task — a question. The kind that changes how Andre thinks about the work, not the kind that fits on a todo list.

## Output location

Save as `00 Inbox/brief-YYYY-MM-DD.md` so the brief itself gets re-processed the next day.

## Rules

- **Every claim must be grounded** in a specific note (use `[[wikilinks]]`).
- **No generic advice** that could apply to anyone.
- **No re-summarization** of what Andre already knows.
- If a section has nothing to surface, say so explicitly — that's a signal.
