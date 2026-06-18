---
type: tpg-folder
purpose: TPG principle nodes — load-bearing distilled truths that supersede redundant source notes
created: 2026-06-18
parent: Cognitive Parameter Graph
schema_version: 1
related: [99 _system/skills (agent_parameters), 99 _system/evaluators (fitness rubrics), 99 _system/golden-set (test inputs), 99 _system/sepo (loop trace)]
---

# 99 _system/principles/

TPG **principle** nodes. Distilled, load-bearing truths that supersede clusters of overlapping source notes. Principles are the "structured" leg of the article's three-property test (neutral / horizontal / structured) — they encode provenance, supersession, and dependency relationships, not just similarity.

## What is a principle?

A principle is **one idea + one body of evidence + one supersession chain + one provenance trail**. Six pieces:

- **Body** — 2-4 sentence statement of the principle
- **Evidence** — where the principle came from (an article, an observation, a session, a research synthesis)
- **Supersedes** — which prior notes this principle consolidates
- **Superseded by** — (in the prior notes' stubs) which principle supersedes them
- **Provenance** — who/when/why created the principle; what triggered the consolidation
- **Related nodes** — other principles, skills, and memories that connect

Principles are NOT evolved via SePO (yet). `fitness_score: null`, `mutation_count: 0`, `last_evaluated` records when the principle was last reviewed, not when it was scored.

## Schema (TPG principle node)

```yaml
---
node_type: principle                  # distinguishes from agent_parameter, stub
parameter_id: <slug>                  # stable identifier (kebab-case)
generation: 1                         # incremented on supersession (principle X is replaced by principle Y)
fitness_score: null                   # principles aren't evolved via SePO (yet)
last_optimized: null                  # ditto
last_evaluated: <ISO>                 # when the principle was last reviewed
mutation_count: 0
schema_version: 1
supersedes:                           # list of file paths (relative to vault root) this principle consolidates
  - "02 Notes/ideas/<old-file>.md"
  - "02 Notes/patterns/<old-file>.md"
  - "99 _system/instincts/<old-file>.md"
provenance:                           # multi-line string
  <YYYY-MM-DD> — <who>, <what>, <why>
created: <ISO date>
created_by: <operator and session id>
status: active | superseded | deprecated
related_skills:                       # skills that operationalize this principle
  - <skill-id>
related_nodes:                        # other principles / nodes this connects to
  - <principle-id>
---

# <Principle Title>

<The principle itself, in 1-3 sentences>

## The principle
...

## <Supporting sections — failure modes, properties, operational implications>
...

## What this principle supersedes
<table mapping each superseded source to where its argument now lives>

## See also
<wikilinks to related skills, principles, source articles>

## Provenance
<who/when/why>
```

## The supersession discipline (the eviction layer)

When a principle is written, the source notes it consolidates **must be evicted from the active retrieval pool**. Procedure:

1. **Copy** the original note to `99 _system/archive/<YYYY-MM-DD>/<original-path>`. Preserve path structure for traceability.
2. **Replace** the original note with a stub. The stub is the same filename, the same title, but:
   - `node_type: stub` in the frontmatter
   - `archived: true`
   - `superseded_by: "[[<principle-id>]]"`
   - A one-paragraph body noting the supersession and pointing to the archive
3. **The chooser MUST skip stubs.** This is a hard rule. A file with `node_type: stub` or `archived: true` is out of the active retrieval pool. Future agents and skill lookups should never load it as primary content.
4. **Wikilinks to the stub still work.** The stub has the original title, so `[[<original-title>]]` resolves to the stub. The stub points to the principle. The principle is the new canonical source.
5. **The original content lives in the archive.** The historical record is preserved. Andre (or future-Mavis) can read the archive to understand the lineage, but the archive is NOT in the active retrieval pool.

## Why principles are not in MEMORY.md

Principles are NOT injected into Mavis's always-on memory. They live here, in the TPG substrate, and are loaded on demand via the `ea-context-chooser` skill. The principle surface is the "structured" leg of the selection layer; it's how Mavis makes the relational query (`which principles connect to this task?`) rather than the similarity query (`which notes look like this task?`).

The MEMORY.md target ceiling (≤10KB) and the principles layer (currently growing) are intentionally decoupled. The chooser bridges them.

## Current principles

| ID | Title | Created | Status |
|---|---|---|---|
| `context-budget-is-finite` | Context Budget is Finite — Selection is the Binding Constraint | 2026-06-18 | active |

## Future

- **Cross-cluster principles.** A second principle, `selection-over-similarity` (or similar), will consolidate notes on retrieval mechanisms, embedding-vs-graph tradeoffs, and the `Adaptive Selectors for Web Scraping` pattern. TBD on subsequent Night Shift passes.
- **Principle evolution.** When new evidence contradicts a principle, the principle gets a successor (generation + 1) and the old version is marked `superseded`. The successor's `supersedes` list points to the prior version's `parameter_id`.
- **Principle fitness scoring.** When SePO is extended beyond the skill layer, principles become the next target. The fitness function would score: (a) how many active notes the principle supersedes (consolidation power), (b) how many skills operationalize it (operational reach), (c) how often the chooser surfaces it (use frequency).
