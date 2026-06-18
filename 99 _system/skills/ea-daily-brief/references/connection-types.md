# Connection Types — ea-daily-brief

The 4 connection types from `ea-contract.md` §"4 Connection Types."
Each is a question to ask the corpus.

## The 4 types

| Type | Question to ask the corpus | When to use |
|---|---|---|
| **A** | Is the same principle showing up in 2 different domains? | Most common — start here |
| **B** | Are 2 notes in tension with each other? | Rare but high-leverage — flag the contradiction, don't resolve it |
| **C** | Are 3+ notes converging on a single unnamed insight? | Use when the corpus is dense — protects against "3 separate things" framing |
| **D** | Did a question in one note get accidentally answered by another? | Use when surfacing a buried answer |

## Pick exactly 3

Spread across types if possible (e.g., 1A + 1B + 1C). Never all 3 of
the same type (signal-diluted). If the corpus supports only 1 strong
connection, write 1 and note the gap ("inbox was thin, brief is
1-connection-only today") — do NOT pad.

## Each connection gets

- **Title** — 1 line, evocative, not generic
- **Surfaces involved** — the file paths that surfaced it
- **The pattern** — 2-3 sentences, in EA voice (direct, not academic)
- **Evidence links** — `file:line` format (per the disk-wins-over-recap discipline)

## The 1 cross-domain pattern

The pattern is the **non-connection** — the meta-observation that
doesn't fit cleanly into any of the 3 connections. It should be:
- Cross-domain (spans ≥2 unrelated surfaces)
- Underlying (a discipline or a recurring correction, not an event)
- One sentence (per EA contract behavior #2: sharpen to one specific sentence)

If the corpus has no cross-domain pattern, omit the section
entirely. Do not invent one. The brief is allowed to be 3
connections + 1 question, no pattern, on quiet days.

## Examples (good connections)

- **Type A:** "The same 'verify on disk before quoting' discipline
  showed up in the Mavis memory update AND the Hermes refactor
  discussion. The team is internalizing the disk-wins-over-recap
  rule."
- **Type B:** "Andre said the X-Content-Engine Scribe 'should not
  publish to x.com' (Hard Rule #10) but the Scribe's spec is being
  revised to allow cron-driven post dispatches. Tension: who's the
  publisher of record?"
- **Type C:** "The memory append on tool-quirks + the cron-prompt
  memory + the skill-infrastructure topic file all converge on:
  Mavis is over-engineering some skills. The unnamed insight is
  'a skill with 8 halt conditions is a foxconn factory, not a
  skill pack.'"

## Examples (bad connections)

- **Single-domain:** "The Scribe is making progress on Pillar 5
  drafts." → This is a project status, not a cross-domain connection.
  Belongs in `03 Projects/X-Content-Engine/status.md`, not the brief.
- **Generic:** "Things are busy." → No pattern, no surfaces, no
  evidence. Pad.
