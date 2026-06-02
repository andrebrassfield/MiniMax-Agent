# weekly-connections — Skill Pack

> Esalen Skill Pack (skill.md + action.py + test_action.py). The instruction
> for M3; the deterministic I/O layer that consumes M3's JSON.

## Purpose

Synthesize the week's captures into 3-5 connection notes in `06 Connections/`.
Single-day synthesis misses the slow-burn patterns; the week-at-once view
catches them. This is the same shape as daily-brief but produces multiple
files (one per connection).

## Input

- **Query week** (default: current week, ISO 8601 YYYY-Www or start date)
- **M3's context**: M3 reads `02 Notes/` (last 7d), the existing
  `02 Notes/` from prior weeks, and queries vault-brain for cross-week
  candidates.

## Output (M3 produces this JSON)

```json
{
  "week_label": "2026-W22",
  "connections": [
    {
      "type": "A",
      "bridge": "1-sentence connection between two ideas",
      "slug": "descriptive-slug-no-spaces",
      "sources": ["[[source-note-1]]", "[[source-note-2]]"],
      "body": "## Why this connection matters\n\n[2-3 sentences explaining the insight, not just restating the sources]\n\n## The bridge\n\n[The one-sentence connection, expanded with evidence from both sources]"
    }
  ]
}
```

Field reference:
- `week_label` — required, ISO week label (YYYY-Www) or "YYYY-MM-DD to YYYY-MM-DD"
- `connections` — required, list of 3-5 items (or fewer if you say so explicitly)
  - `type` — required, one of `"A"`, `"B"`, `"C"`, `"D"`
  - `bridge` — required, 1-sentence connection
  - `slug` — required, kebab-case, will become the filename
  - `sources` — required, list of 2+ wikilinks (Type C needs 3+)
  - `body` — required, markdown body for the connection note

## Connection types (use exactly these four)

- **TYPE A** — same underlying principle in two completely different domains
  (e.g., a `patterns/` note matches an `ideas/` note)
- **TYPE B** — contradiction between two notes that creates interesting
  tension (both sides are right; the tension is the insight)
- **TYPE C** — pattern connecting 3+ notes into one unnamed insight
  (the whole is greater than the sum)
- **TYPE D** — a question from one note that another note accidentally
  answers (without the author knowing they were answering)

## Procedure

1. **Read** the inputs: `02 Notes/` (last 7d), the existing `02 Notes/` from
   prior weeks (for cross-week connections)
2. **Query vault-brain** for cross-week candidates
3. **Find 3-5 strong connections** of types A, B, C, or D
4. **For each**, write the type, bridge, slug, sources, and body
5. **Write the JSON** in the format above. Do NOT touch any files yourself —
   `action.py` will create the connection note files.

## Rules

- **Minimum 3, maximum 5 connections.** Quality over quantity.
- **Only surface connections that would genuinely surprise Andre.** A
  connection between two notes that already wikilink each other is not a
  connection; it's redundancy.
- **If you cannot find 3 strong connections, say so explicitly** (return
  fewer than 3 in the `connections` list with the bridge field starting
  with `"[insufficient diversity this week — only N connections]"`).
  That is a signal about whether the week's inputs were diverse enough.
- **Every source must be a real note** in Andre's vault, reachable by `[[wikilink]]`.
- **Body must contain both `## Why this connection matters` and `## The bridge`**
  sections (the deterministic layer checks for these).

## Output location

`action.py` creates one file per connection in `06 Connections/`:
`YYYY-MM-DD - <slug>.md` (using today's date).

## Worked example (truncated)

```json
{
  "week_label": "2026-W22",
  "connections": [
    {
      "type": "A",
      "bridge": "Anchor-ends packing and MSA both put the highest-signal content where attention is sharpest",
      "slug": "anchor-ends-msa",
      "sources": ["[[Mavis-Apex-Architecture]]", "[[MSA-Sparse-Attention]]"],
      "body": "## Why this connection matters\n\nBoth patterns solve the same problem: making the most of limited attention. Anchor-ends is the deterministic version (place at positions 0 and N-1); MSA is the learned version (skip computation where attention would be diffuse).\n\n## The bridge\n\nThe principle is identical: don't spread compute evenly; concentrate it where the value is."
    }
  ]
}
```

## Integration: vault-brain

Query vault-brain with the most recent capture's keywords to find
cross-week candidates. The top results usually match the strongest
connection candidates.

## Edge cases

- **Fewer than 3 strong connections** — return as many as you found
  (1, 2, or "none"). The action.py will still write the files.
- **Slug collision** — `action.py` will refuse to overwrite; the script
  reports the conflict so M3 can pick a different slug.
- **Empty inputs** — return a single connection with bridge starting with
  `"[insufficient diversity this week — no notes]"` and sources = [].

## Related

- `action.py` — the deterministic I/O layer (creates one file per connection)
- `test_action.py` — pytest tests
- `99 _system/mcps/vault-brain/` — semantic retrieval
- The trailblazer: `process-inbox/` (single-file output, same shape)
- The simpler sibling: `daily-brief/` (single connection file)

---

*Skill Pack authored 2026-06-02 as part of Operation Chimera — refactor
of the 4 raw workflow skills into Esalen-compliant Skill Packs.*
