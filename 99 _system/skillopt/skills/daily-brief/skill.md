# daily-brief — Skill Pack

> Esalen Skill Pack (skill.md + action.py + test_action.py). The instruction
> for M3; the deterministic I/O layer that consumes M3's JSON.

## Purpose

Produce the daily brief: 3 specific connections, 1 weekly pattern, 1
question worth sitting with. The brief is the moment the system earns
its place — read this before opening any app, every morning.

## Input

- **Query date** (default: today, ISO 8601 YYYY-MM-DD)
- **M3's context**: M3 reads `00 Inbox/` (last 24h), `02 Notes/` (last 7d),
  `01 Daily/YYYY-MM-DD.md` (if it exists), and queries vault-brain for
  the most relevant context.

## Output (M3 produces this JSON)

```json
{
  "brief_date": "2026-06-02",
  "connections": [
    {
      "headline": "1-sentence framing of the connection",
      "source_note_1": "[[Note Name 1]]",
      "source_quote_1": "exact quoted text from source_note_1 (15+ chars)",
      "source_note_2": "[[Note Name 2]]",
      "source_quote_2": "exact quoted text from source_note_2 (15+ chars)"
    }
  ],
  "pattern": {
    "name": "1-sentence pattern name (no generic advice)",
    "evidence_notes": ["[[Note A]]", "[[Note B]]", "[[Note C]]"]
  },
  "question": "1 question worth sitting with today (not a task; the kind that changes how Andre thinks)"
}
```

Field reference:
- `brief_date` — required, ISO 8601 YYYY-MM-DD
- `connections` — required, list of exactly 3 connection objects
  - `headline` — 1-sentence framing, NOT a generic rephrase
  - `source_note_1`, `source_note_2` — required, `[[Note Name]]` form
  - `source_quote_1`, `source_quote_2` — required, EXACT quoted text (15+ chars each)
- `pattern` — required, exactly 1
  - `name` — 1-sentence, specific to Andre's recent work
  - `evidence_notes` — list, 3+ items
- `question` — required, 1 question

## Procedure

1. **Read** the inputs: `00 Inbox/` (24h), `02 Notes/` (7d), today's daily note
2. **Query vault-brain** with the most relevant terms from the recent captures
3. **Find 3 specific connections** between recent captures and older notes
   Andre has not noticed. A connection is "specific" if it links named notes,
   not themes. **Quote the exact text** from the source files.
4. **Identify 1 pattern** across everything Andre has been reading this week
5. **Formulate 1 question** worth sitting with today
6. **Write the JSON** in the format above. Do NOT touch any files yourself —
   `action.py` will render the markdown and save it.

## Rules

- **Every claim must be grounded** in a specific note (use `[[wikilinks]]`)
- **No generic advice** that could apply to anyone
- **No re-summarization** of what Andre already knows
- **Quote the exact text** in `source_quote_*` — paraphrase is failure
- **If a section has nothing to surface, say so explicitly** — that's a signal
  (use a single sentence in the `headline` / `name` / `question` field that
  starts with "[nothing to surface this morning —]")

## Output location

`action.py` saves the rendered brief to `00 Inbox/brief-YYYY-MM-DD.md`
(so the brief itself gets re-processed by `process-inbox` the next day).

## Worked example

M3's JSON output (truncated for brevity):
```json
{
  "brief_date": "2026-06-02",
  "connections": [
    {
      "headline": "The vault-brain anchor-ends pattern shows up in M3 MSA",
      "source_note_1": "[[Mavis-Apex-Architecture]]",
      "source_quote_1": "Anchor-ends packing puts the highest-signal notes where attention is sharpest",
      "source_note_2": "[[MSA-Sparse-Attention]]",
      "source_quote_2": "Sparse attention concentrates compute on the most informative positions"
    }
  ],
  "pattern": {
    "name": "Compression as a first-class architectural layer is paying off across all three MCPs",
    "evidence_notes": ["[[direct-intake]]", "[[vault-brain]]", "[[M3-Summary-Mode]]"]
  },
  "question": "If regex compression caps at ~50% on prose, where else is the deterministic layer hitting its ceiling?"
}
```

## Integration: vault-brain

Always query vault-brain with a search term derived from the most recent
capture before generating the brief. The top results are the candidate
older notes for the connections section.

## Edge cases

- **Empty inputs** — if `00 Inbox/` and `02 Notes/` are both empty, return
  the "[nothing to surface]" pattern in every field. `action.py` will still
  write the file.
- **Today's brief already exists** — `action.py` will refuse to overwrite
  by default. Use `--overwrite` to force.
- **Fewer than 3 connections** — return as many as you found; if 0, return
  the explicit empty pattern.

## Related

- `action.py` — the deterministic I/O layer (renders markdown, saves file)
- `test_action.py` — pytest tests for `action.py`
- `99 _system/mcps/vault-brain/` — the semantic retrieval MCP
- `99 _system/skillopt/PIPELINE.md` — how SkillOpt optimizes this skill
- The trailblazer pack: `process-inbox/` (same shape)

---

*Skill Pack authored 2026-06-02 as part of Operation Chimera — refactor
of the 4 raw workflow skills into Esalen-compliant Skill Packs.*
