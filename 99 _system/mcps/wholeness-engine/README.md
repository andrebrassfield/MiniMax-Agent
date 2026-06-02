# Wholeness-Engine

> **The Alexandrian QA layer.** M3-powered LLM-as-judge for Christopher Alexander's 15 structural properties of "living structure" (from *The Nature of Order* Book 1, 2002). Score any CHIEF note 0-30. Below 18 = structure surgery required. Esalen posture: M3 does the qualitative grading. Python handles files, JSON parsing, and surgery validation.

## The 15 properties (canonical)

From Alexander's *Nature of Order*, Book 1, pp. 141-242. Each is a *relationship* between centers, not a property of an object. Empirical regularities in every structure with high "Quality Without a Name."

| # | Property | Question to ask the note |
|---|---|---|
| 1 | Levels of Scale | Does the note nest smaller ideas inside larger ones at consistent ratios? |
| 2 | Strong Centers | Is there one clear central claim, even with many sections? |
| 3 | Thick Boundaries | Are section transitions zones, not walls? |
| 4 | Alternating Repetition | Do examples and principles alternate in a way that reinforces both? |
| 5 | Positive Space | Is the structure doing real work, or is it decoration? |
| 6 | Good Shape | Can you recognize the note by its section headers? |
| 7 | Local Symmetries | Are parallel sections mirror each other? |
| 8 | Deep Interlock and Ambiguity | Does each section both serve the note and contribute to a MOC? |
| 9 | Contrast | Are sections genuinely different in voice, length, or stance? |
| 10 | Gradients | Does the energy change smoothly? |
| 11 | Roughness | Does the note admit the occasional quirk? |
| 12 | Echoes | Does a key term appear 2-3+ times with variations? |
| 13 | The Void | Does the note have a moment of breathing room? |
| 14 | Simplicity and Inner Calm | Could you cut 20% without losing the message? |
| 15 | Not Separateness | Does the note end with a connection to a larger structure? |

## Verdict scale

- **30 (exemplary)** — rare and suspicious; double-check
- **24-29 (alive)** — well-formed, the rubric passes
- **18-23 (working)** — acceptable, room to improve
- **12-17 (rough)** — needs repair on multiple properties
- **0-11 (weak)** — structure surgery required

**Threshold: 18.** Below this, the engine emits a `structure_surgery` plan with 2-6 specific, actionable repairs.

## Quick start

```bash
# Use the Glass Server's venv (shared Python)
99 _system/mcps/glass-server/.venv/bin/python 99 _system/mcps/wholeness-engine/wholeness_engine.py score \
  --path "02 Notes/patterns/Mycelial Routing.md" \
  --vault /Users/brassfieldventuresllc/MiniMax-Agent
```

Or via the `mavis-vault` CLI (wired-in integration):

```bash
mavis-vault wholeness "02 Notes/patterns/Mycelial Routing.md"
mavis-vault wholeness-report
```

## Subcommands

| Subcommand | Purpose | LLM? |
|---|---|---|
| `score` | Score a single note | Yes (cached by mtime) |
| `report` | Run across all atomic notes in `02 Notes/`, `06 Connections/`, `00 Inbox/` | Yes |
| `cache` | Show or clear the cache | No |

## Architecture

```
wholeness-engine/
  wholeness_engine.py    # main module — LLM-as-judge orchestrator
  rubric.py              # the 15 properties + scoring rubric + system prompt
  surgery.py             # structure surgery validation + generation
  README.md              # this file
  __init__.py
  cache.jsonl            # per-file mtime-keyed cache (gitignored)
```

The flow:
1. **Read** the note (body, stripped of frontmatter)
2. **Truncate** to 12KB if needed
3. **Call M3** at temperature 0.0 (deterministic) with the strict rubric system prompt
4. **Parse** the JSON response (robust to code fences, preamble)
5. **Validate** — ensure all 15 properties have scores 0-2 with rationales
6. **Compute total** — sum of 15 property scores
7. **Surgery** — if total < 18, emit structure_surgery (validate LLM's, fall back to template)
8. **Cache** — keyed by `rel_path + mtime`, so unchanged notes don't re-grade

## Why temperature 0.0

Per the discipline in agent memory: **LLM-as-judge temperature is 0.0 for graders, 0.2 for optimizers.** The Wholeness-Engine is a grader, so temperature 0.0. This makes the scores bit-deterministic — a re-run on an unchanged file returns the same result. The bit-determinism matters for:
- The canary rule (red-line properties need stable scores)
- Diffing scores over time
- Trusting the result as a gate, not as a sample

## The surgery plan

When a note scores below 18, the engine emits 2-6 specific repairs, like:

```
⚠️  STRUCTURE SURGERY REQUIRED (score: 8/30, below 18 threshold)
============================================================
  1. Strip the navigation menu, footer, 'On this page' TOC, and 'Was this page helpful?' widget — keep only the article body and the one core diagram description.
  2. Add a 'Why I saved this' framing paragraph at the top (2-3 sentences) that locates MCP within a personal MOC on protocol standards or agent infrastructure, plus 3-5 outbound links to sibling atomic notes.
  3. Convert the flat 'What can MCP enable?' bullet list into a graded sequence (small examples → large enterprise examples) so a Levels-of-Scale gradient emerges.
  4. Add a closing 'Open questions' or 'What this page doesn't tell me' section to introduce a void and create room for a future note on MCP's limits.
```

Each repair names a *specific property* and a *specific action*. Not "make it better" — "convert the flat list to a graded sequence (small → large) so a Levels-of-Scale gradient emerges."

The surgery is **per-property, not generic.** The engine looks at which properties scored 0 or 1, and proposes repairs for those exact properties.

## Verified test results (2026-06-02)

Tested on 4 notes at temperature 0.0:

| Note | Score | Verdict | Surgery? |
|---|---|---|---|
| `02 Notes/patterns/Mycelial Routing.md` | 26/30 | alive | No |
| `02 Notes/patterns/Topological Skill Composition (Braiding).md` | 28/30 | alive | No |
| `02 Notes/ideas/Agent-Anyon Duality.md` | 28/30 | alive | No |
| `04 Resources/MCP-Ouroboros/01-mcp-intro-raw.md` | 8/30 | weak | Yes (4 repairs) |

The first three are my own atomic notes (well-formed, expected high scores). The fourth is a raw scrape (expected low score, surgery correctly emitted).

## Tying into the Horizon pitches

Wholeness-Engine is **Pitch 2 of Operation Horizon** — the QA layer. It operationalizes the principle from `02 Notes/patterns/15-Properties Quality Rubric for Atomic Notes.md`. The engine:

- Replaces the heuristic `mavis-vault wholeness` command (which used regex + section count)
- Caches results, so re-running on an unchanged note is free
- Emits surgery for low-scoring notes, so the EA can act on the diagnosis
- Is wired into the Glass Server for Phase 3 (wholeness score appears in the HTML)

## Future work

- [ ] Add `--compare` mode to diff two notes' wholeness
- [ ] Add a "trajectory" view — show how a note's score changed over edits
- [ ] Add per-property Pareto analysis — which properties are vault-wide weakest?
- [ ] Add a "prerequisite map" — which properties are most-leveraged in well-formed notes?
- [ ] Wire the rubric into the Glass Server's HTML output (Phase 3 of this operation)

## See also

- `02 Notes/patterns/15-Properties Quality Rubric for Atomic Notes.md` — the underlying rubric
- `02 Notes/ideas/Workflows as Generative Codes.md` — the generative-code sister idea
- `99 _system/mcps/pattern-forge/` — the sister workshop (Phase 1 of this operation)
- `00 Inbox/Horizon-Pitches-2026.md` — the pitch this implements
- Christopher Alexander, *The Nature of Order* Book 1, pp. 141-242

---

*Seeded 2026-06-02 from Operation Architect's Forge Phase 2. The Alexandrian QA layer. M3 is the judge; Python is the file system.*
