# deep-research — Skill Pack

> Esalen Skill Pack (skill.md + action.py + test_action.py). The instruction
> for M3; the deterministic I/O layer that consumes M3's JSON.

## Purpose

Run deep research on a specific topic in Andre's vault. The workflow before
a major decision, when picking up a dormant project, or when Andre suspects
he is missing something obvious. This produces ONE structured research file
(4 sections in a fixed order) — the load-bearing output is section 4
(the unasked question).

## Input

- **Topic** (passed in by Andre): the question or subject being researched
- **M3's context**: M3 reads `02 Notes/` (all subfolders including `_MOCs/`),
  `03 Projects/`, `06 Connections/`, `04 Resources/`, `01 Daily/` (last 90d),
  and queries vault-brain for topic-relevant notes.

## Output (M3 produces this JSON)

```json
{
  "topic": "the topic Andre asked about",
  "research_date": "2026-06-02",
  "what_andre_believes": "2-4 paragraphs. Quote Andre's own words (with [[wikilinks]]). If 3+ notes on the topic, there is a position — name it.",
  "what_contradicts": "2-4 paragraphs. Show both sides from Andre's own notes. A good belief is load-bearing; if there is no tension, Andre has not been honest with himself. Name the contradiction explicitly.",
  "what_is_missing": "2-4 paragraphs. Look at the gaps in note coverage. If Andre has 5 notes on X and 0 on Y, and Y is a major counter-position to X, that is the gap. State it.",
  "unasked_question": "1 question. Not a question Andre has asked before (check 02 Notes/questions/ to verify). The kind of question that, if sat with for a week, would change the position.",
  "grounded_notes": ["[[Note 1]]", "[[Note 2]]", "[[Note 3]]"]
}
```

Field reference:
- `topic` — required, the topic string
- `research_date` — required, ISO 8601 YYYY-MM-DD
- `what_andre_believes` — required, 2+ paragraphs, quotes from real notes
- `what_contradicts` — required, 2+ paragraphs, both sides shown
- `what_is_missing` — required, 2+ paragraphs, gap identified
- `unasked_question` — required, 1 question (the load-bearing output)
- `grounded_notes` — required, list of 3+ wikilinks backing the claims

## Procedure

1. **Read** the inputs: `02 Notes/` (all), `03 Projects/`, `06 Connections/`,
   `04 Resources/`, `01 Daily/` (last 90d)
2. **Query vault-brain** with the topic
3. **Read the existing `02 Notes/questions/`** to verify the unasked question
   hasn't been asked before
4. **Write the 4 sections** per the structure above
5. **Write the JSON** in the format above. Do NOT touch any files yourself —
   `action.py` will render the markdown and save it.

## Rules

- **Be direct.** Challenge Andre. Do not summarize what he already knows.
  Do not give generic advice.
- **Every claim must be grounded** in a specific note. If you cannot ground
  it, flag the gap.
- **Quote Andre's words** when stating what he believes. Paraphrase is failure.
- **The unasked question is the load-bearing output.** If you can only
  deliver one section well, deliver that one.
- **No generic rephrases of common knowledge** — every paragraph should
  reference a real note in the vault.

## Output location

`action.py` saves the rendered research file to
`04 Resources/research-YYYY-MM-DD-<topic-slug>.md`.

## Worked example (truncated)

```json
{
  "topic": "agent memory architectures",
  "research_date": "2026-06-02",
  "what_andre_believes": "Andre's position (from 3 notes) is that agent memory should be **layered**: working memory (the context window) → episodic memory (recent sessions) → semantic memory (the vault). The 02 Notes/patterns/Mavis-Apex-Architecture.md note names this explicitly: 'Memory is a hint, not live state.' The SOUL.md hard constraints embody this: no implicit memory across sessions without a write step.",
  "what_contradicts": "The instinct 2026-06-01-021 'Memory is a hint, not live state' (0.90) supports layered memory. But the Friction Log shows repeated cases where the Mavis write step was skipped (Friction 10 — state regen used Write tool, not the script's --apply), which collapses the layered model. The contradiction: Andre believes in layered memory but executes linear write-then-forget.",
  "what_is_missing": "No notes on **memory decay policies** (when does an instinct decay? when does a note get archived?). The instinct README mentions 'confidence decay' as a future feature, but no actual implementation. This is a load-bearing gap if memory is supposed to be more than a write-once log.",
  "unasked_question": "If memory is layered and decay is a thing, what is the read path? Does Mavis always re-read the full vault, or does it trust the layered model to surface the right context?",
  "grounded_notes": ["[[Mavis-Apex-Architecture]]", "[[2026-06-01-021-memory-is-a-hint-not-live-state]]", "[[state-of-mavis]]", "[[Friction 10]]"]
}
```

## Integration: vault-brain

Query vault-brain with the topic (not a question, the topic noun-phrase).
The top results are the candidate notes for the "what Andre believes"
section. The bottom results (after excluding the top) are the candidates
for "what is missing."

## Edge cases

- **Topic with no existing notes** — return the explicit empty pattern
  in every field. `action.py` will still write the file with a
  "[no prior notes on this topic]" marker.
- **Topic already researched** — `action.py` will refuse to overwrite an
  existing research file with the same date + topic-slug.
- **Fewer than 3 grounded notes** — the validator requires 3+. If you
  truly have fewer, pad with notes from the broader category.

## Related

- `action.py` — the deterministic I/O layer
- `test_action.py` — pytest tests
- The simpler siblings: `daily-brief/` (single file, 3 sections),
  `weekly-connections/` (multi-file, type-coded)

---

*Skill Pack authored 2026-06-02 as part of Operation Chimera — refactor
of the 4 raw workflow skills into Esalen-compliant Skill Packs.*
