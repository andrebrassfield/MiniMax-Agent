---
type: workflow
name: process-inbox
trigger:
  - "process my inbox"
  - "clear the inbox"
  - "morning processing"
cadence: daily (on-demand)
created: 2026-06-01
---

# Process Inbox

## Purpose

Move raw captures from `00 Inbox/` into the right typed subfolder inside `02 Notes/`, sharpening them along the way. The capture layer has one job: collect without friction. This workflow is where raw becomes useful.

## When to use

- Every morning, first thing (replaces the open-the-inbox habit)
- Whenever `00 Inbox/` has 3+ items piling up
- After a heavy capture session (article digests, voice transcripts, telegram bot dumps)

## Prompt

> Read every note in my `00 Inbox/` folder from the last 24 hours. For each note:
>
> 1. **Determine the type.** Pick one: `articles/` (external content digest), `ideas/` (my own observation or thesis), `patterns/` (same principle in different domains), `questions/` (something I genuinely don't know), `numbers/` (specific data point), or `_MOCs/` (hub note — only if it's a synthesis).
> 2. **Sharpen the raw capture into one specific punchy sentence.** A stranger should understand exactly what was observed without any additional context. If it still needs explanation, it is not sharp enough.
> 3. **Move it to the correct subfolder** using `git mv` (preserves history).
>
> After processing all notes, tell me:
> - Total notes processed and where each went
> - Any patterns you noticed across today's captures
> - One connection worth exploring from today's batch
>
> Do not skip a note. Do not re-categorize a note that already has a clear type. Do not invent content — sharpen what is there.

## What "sharp enough" means

A note like:
> "looked at the apple thing — they're using gemini now for siri"
becomes:
> "Apple rebuilt Siri on Gemini for WWDC 2026 — they don't care whose model runs underneath, only that the UX, distribution, and trust layer stays theirs."

The first is a reminder. The second is a note that will still make sense in 18 months.

## Related

- `daily-brief.md` — runs after process-inbox, surfaces cross-day patterns
- `weekly-connections.md` — runs Sunday, processes the whole week
