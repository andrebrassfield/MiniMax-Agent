# 5-Field Schema — ea-decision-logger

The 5 required fields + 4 optional fields. None of the 5
required fields are optional — the format forces rigor.

## The 5 required fields

| Field | What it captures | Format |
|---|---|---|
| **Decision** | The choice that was made | One sentence, past tense, definitive. "We are using X for Y." Not "we should consider X." |
| **Rationale** | Why this choice over the alternatives | 2-4 sentences. The synthesis + the why, in EA voice. Cite the brief / research / evidence that informed the decision. |
| **Alternatives considered** | The other options that were on the table | Bulleted list, 2-5 options. Each option: name + 1-line why it was rejected. |
| **Expected impact** | What this decision enables / prevents / changes | 2-4 sentences. Concrete effects: which skills / crons / memory / workflows change, what the new failure modes are, what gets easier. |
| **What would change my mind** | The conditions under which this decision should be revisited | 2-3 sentences. Specific triggers: a measurement, a benchmark, a regulatory change, a scale threshold, a new tool. NOT "if I learn more" — that's not a trigger. |

## The 4 optional fields (capture when available)

| Field | What it captures | Format |
|---|---|---|
| **Date** | When the decision was made | ISO 8601 (auto: today's date) |
| **Conversation pointer** | Where the decision was said | Session ID or chat reference |
| **Decider** | Who made the decision | "Andre" / "Mavis-with-approval" / "Mavis-autonomous" — be honest about the autonomy level |
| **Reversibility** | How hard to reverse | "fully reversible" / "partially reversible" / "hard to reverse" |

## Per-field capture rules

### Decision

- One sentence, past tense, definitive
- "We are using X for Y" (statement) not "we should
  consider X" (suggestion)
- "The architecture is now X" (state) not "let's try X"
  (proposal)

### Rationale

- 2-4 sentences in EA voice (synthesis + why)
- Cite the brief / research / evidence that informed
  the decision
- "We picked X over Y because [evidence]" (decision-
  shaped reasoning) not "X has the following properties"
  (feature description)

### Alternatives considered

- 2-5 options, each with 1-line why-rejected
- The "why rejected" must be substantive (a real reason,
  not "we just picked X instead")
- Skip options that weren't actually considered (don't
  pad the list)

### Expected impact

- 2-4 sentences, concrete effects
- Name the skills / crons / memory / workflows that
  change
- Identify the new failure modes (what can break now
  that couldn't before)
- Note what gets easier (the unlock)

### What would change my mind

- 2-3 sentences, specific triggers
- A trigger is observable: a measurement, a benchmark,
  a regulatory change, a scale threshold, a new tool
- NOT "if I learn more" (vague), NOT "if Andre changes
  his mind" (circular)
- Examples of good triggers: "if MMLU-Pro scores drop
  below 0.7", "if the corpus exceeds 30KB", "if the EU
  AI Act is enforced before 2027", "if a new voice
  engine with <100ms latency ships"

## What the 5-field schema is NOT

- **Not a chat-log dump.** The decision file is
  structured, not a transcript. The chat is the trigger;
  the file is the artifact.
- **Not a project journal.** Project journals are in
  `03 Projects/<project>/`; decisions are cross-project
  and architectural.
- **Not a one-line note in the daily.** Daily notes are
  operational. Decisions are architectural. The
  threshold is reversibility + scope.
- **Not a substitute for the daily brief.** The daily
  brief surfaces the decision; the `decisions/` file is
  the source of truth. The two are different artifacts.
- **Not retroactive.** This skill is for *current* and
  *forward* decisions. Backfilling old decisions is a
  different task (and requires more rigor).
