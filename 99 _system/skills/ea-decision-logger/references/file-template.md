# File Template — ea-decision-logger

The decision file template. The chief writes the file to
`02 Notes/decisions/YYYY-MM-DD-<slug>.md` after extracting
the 5 fields from the conversation.

## Full template

```markdown
---
date: YYYY-MM-DD
type: architectural-decision
status: active | superseded | reversed
decider: Andre | Mavis-with-approval | Mavis-autonomous
reversibility: full | partial | hard
conversation: <session-id or chat pointer>
related:
  - <path to the brief / research that informed it>
  - <path to the skill / cron / memory that depends on it>
  - <path to any prior decision this reverses or supersedes>
---

# Decision: <one-sentence decision>

> Captured <YYYY-MM-DD HH:MM CT> by Mavis (EA) from <conversation pointer>.

## Decision

<one sentence, past tense, definitive>

## Rationale

<2-4 sentences, EA voice>

## Alternatives considered

- **<option name>** — <1-line why rejected>
- **<option name>** — <1-line why rejected>
- **<option name>** — <1-line why rejected>

## Expected impact

<2-4 sentences>

## What would change my mind

<2-3 sentences, specific triggers>

## Reversal log

<if this decision is later reversed, append the reversal
here with date + new decision link. The prior file is not
edited — the audit trail is the value.>
```

## Per-section content discipline

- **YAML frontmatter:** date (ISO 8601), type
  ("architectural-decision"), status (active /
  superseded / reversed), decider (Andre / Mavis-
  with-approval / Mavis-autonomous), reversibility
  (full / partial / hard), conversation pointer,
  related surfaces.
- **Decision:** one sentence, past tense, definitive.
  State the choice, not the consideration.
- **Rationale:** 2-4 sentences, EA voice. Cite the
  brief/research/evidence.
- **Alternatives considered:** 2-5 options, each with
  1-line why-rejected. Don't pad.
- **Expected impact:** 2-4 sentences, concrete effects
  on skills / crons / memory / workflows. Identify the
  new failure modes.
- **What would change my mind:** 2-3 sentences, specific
  triggers (measurement, benchmark, scale threshold).
  NOT "if I learn more."
- **Reversal log:** if later reversed, append the
  reversal here with date + new decision link. The
  prior file is not edited.

## What this template is NOT

- **Not a chat-log dump.** The decision file is
  structured, not a transcript.
- **Not a project journal.** Project journals are in
  `03 Projects/<project>/`; decisions are cross-project
  and architectural.
- **Not a one-line note in the daily.** Daily notes are
  operational. Decisions are architectural.
- **Not retroactive.** This skill is for *current* and
  *forward* decisions.
