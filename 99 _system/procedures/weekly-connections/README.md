# weekly-connections procedure.json

> Mavis-procedural (compiled, planned) for the weekly synthesis. Parallels the daily-brief procedure structurally — same 4-terminal pattern, same warnings array, same scenario-variables shape.

## Status

**v0.1.0-draft** — first articulation. The connection-selection is compilable (3B territory). The synthesis body is judgment (frontier). The procedural engine handles the routing and the structural skeleton; Mavis-judgment handles the bridge text and the implications.

## What's in the file

- **system_prompt** — who Mavis-weekly-connections is, and the load-bearing distinction: the structure is procedural, the synthesis is judgment
- **8 nodes**:
  - `scan_weekly_corpus` — tagged inventory of the last 7 days
  - `theme_surface` — identify the dominant thread (1-3 themes)
  - `connection_selection` — apply the 4 connection types, pick 3-5 strong ones
  - `synthesis_write` — write the synthesis with the lead-with-wins-then-fix-then-dont-change structure
  - 4 routing/terminal nodes (routed_to_judgment, routed_to_procedural, blocked_on_source, synthesis_shipped)
- **4 terminals** (success, user clarification, two external handoffs)
- **4 scenario variables** — notes_in_window, themes_count, open_questions_count, user_state
- **6 warnings** (severity: high) — 4-connection-types-required, lead-with-wins-then-fix-then-dont-change, end-with-sharper-question, 3-to-5-connections-not-10, synthesis-is-judgment, no-handshake-loops
- **eval_set_planned** — 200 conversations, 90/10 train/eval, 7 held-out criteria

## The 4 connection types encoded

The chief contract names 4 connection types. The procedure.json encodes each as a typed template:

| Type | Bridge | Example |
|---|---|---|
| **A** | Same principle, two different domains | "X and Y are doing the same thing under different names" |
| **B** | Contradiction between two notes | "Note X says A, Note Y says not-A. Both have source weight. The disagreement is the data" |
| **C** | 3+ notes forming one unnamed insight | "These three notes are pointing at the same unnamed thing. Naming it is the deliverable" |
| **D** | Question from one note accidentally answered by another | "Note X asked Q. Note Y, written without reference to X, contains the answer" |

Type C is the highest-synthesis-value type. The connection_selection node prefers it when the corpus supports it.

## Why this is partially compilable

The connection_selection step is flowchart-able: scan the corpus, apply the 4 types, pick 3-5. This is a 3B-territory compile target.

The synthesis_write step is judgment: which 3-5 of the 10 candidates to highlight, how to frame each bridge, what implications to surface for next week, what sharper question to close with. That's Mavis-judgment on frontier.

The procedural engine handles the routing, the inventory, the connection-selection. Mavis-judgment handles the body. Same architecture as the article's compiled-procedural + frontier-judgment split.

## Live experience

I just ran this week's worth of content through the mental model:
- 2026-06-04 has 1 daily note + 7 Night Flight artifacts (Scribe 3 + Researcher 4) + 1 connections note (the AI-as-companion landing I wrote this morning) + 4 procedure.json files + several agent.md updates
- Dominant thread: the operator/companion split + the procedural/judgment architecture
- 3-5 strong connections:
  - Type A: the article's procedure.json pattern (compiled-procedural) and the two-engine chief architecture (Mavis-judgment + Mavis-procedural) are doing the same thing under different names — the procedural layer is the compiled, the judgment layer is the frontier
  - Type B: the operator mode (scaffolding-removable, retires as the model improves) and the companion mode (an organ that doesn't retire) are in productive tension per the Scribe's mavis-as-companion synthesis
  - Type C: the Scribe's mavis-as-companion synthesis + the mavis-orchestrator procedure.json + the daily-brief procedure.json all point at the same unnamed thing — the two-engine chief role is the architecture, the operator/companion split is the application
  - Type D: the mphrediction article's "we are not building a better tool, we are becoming a presence" is the unanswered question that the operator/companion split (Scribe's synthesis) accidentally answers

That's a real 4-type week. The procedure.json could surface this as the v0.1 weekly synthesis.

## Related

- `daily-brief/procedure.json` — daily operator-mode counterpart
- `mavis-orchestrator/procedure.json` — judgment-mode counterpart
- `02 Notes/ideas/mavis-as-companion.md` — the Scribe's operator/companion synthesis
- `06 Connections/2026-06-04 - AI-as-companion landing.md` — this week's strategic synthesis
- `06 Connections/2026-W22 - AI-Agent-Landscape.md`, `06 Connections/2026-W23 - Operation-Horizon-Synthesis.md` — prior weekly syntheses (format reference)

---
*Staged 2026-06-04 13:00 CT, during an Andre-out autonomous session. First v0.1 of the weekly-connections procedure. Not compiled. The connection-selection is the compilable target; the synthesis body is Mavis-judgment.*
