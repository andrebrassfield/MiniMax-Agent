# daily-checkin procedure.json

> First end-to-end application of the procedure.json pattern to a shipping artifact in Andre's vault — the Coder's daily check-in prototype (`03 Projects/Mavis Daily Check-in/01 prototype.html`, 583 lines, 16KB, single self-contained HTML, shipped 08:33 CT on 2026-06-04).

## Status

**v0.1.0-draft** — first articulation. The workflow skeleton is procedural (compilable to Qwen 2.5-3B per the article's spec). The question pool + aesthetic stay human-curated.

## What's in the file

- **system_prompt** — who the engine is, and the companion-mode discipline (a response to "how are you" is NOT an action item)
- **9 nodes**:
  - `open` — first-time detection, route to show_today
  - `show_today` — load question by `dayOfYear % 15`, render the breath-in animation
  - `write` — borderless field, warm rule on focus, no app chrome
  - `save` — persist to localStorage with the v1 schema
  - `render_saved` — status line, Edit button, no celebration
  - `render_timeline` — last 7 days, empty days read "— a quiet day —"
  - `edit` — populate field with existing answer, save updates the entry
  - `storage_disabled` — gentle status, doesn't block the check-in
  - `idle` — page sits, waits, tomorrow a different question
- **4 terminals** (success × 3, user_clarification, external_handoff)
- **6 scenario variables** (day_of_year, is_first_ever_open, has_prior_entries, system_color_scheme, prefers_reduced_motion, localstorage_available)
- **9 warnings** (severity: high) — the companion-mode discipline encoded as flowchart rules
- **question_pool_v1** — the 15 prompts, listed in the file so the pool is editable
- **storage_schema** — localStorage v1 contract, versioned via the key
- **eval_set_planned** — 50 conversations, 80/20 split, 11 held-out criteria
- **compilation_target** — Qwen 2.5-3B, self-hosted, 4 explicit compilation blockers

## The 9 warnings (the load-bearing discipline)

The 9 warnings ARE the companion-mode discipline translated to flowchart rules. They are severity: high because the failure modes are existential — a single streak counter, a single "missed a day" message, a single AI-suggested follow-up, would break the check-in.

1. **no-streaks-no-charts-no-mood-tags** — the load-bearing warning, from the Scribe's mavis-as-companion synthesis
2. **no-network-no-cdn-no-fetch** — the privacy-by-construction discipline
3. **xss-safe-by-construction** — `.textContent` everywhere, no `.innerHTML` from data
4. **live-with-it-a-week-before-features** — the Coder's own recommendation
5. **single-question-per-turn** — the companion-mode shape
6. **borderless-on-first-load** — the notebook aesthetic
7. **breath-in-fade-not-motion** — the 1.6s slow ease, respects reduced-motion
8. **empty-days-no-judgment** — "— a quiet day —" not "missed"
9. **first-ever-open-hides-timeline** — no "you have empty days" on cold start

## Why this matters as the first end-to-end playbook application

The daily-brief, mavis-orchestrator, humanized-copy, and weekly-connections procedure.json files all spec WORKFLOWS — the structural skeleton of Mavis-chief operations. None of them specs a SHIPPING ARTIFACT.

The daily-checkin procedure.json is different: it specs a real shipping artifact (the Coder's HTML prototype) that exists in the vault right now, that a user (Andre) can open in a browser, that demonstrates the companion-mode discipline in working code. The procedure.json is the META-SPEC for that artifact — the workflow shape, the warnings-as-discipline, the storage schema, the compilation target.

The article's playbook applies cleanly:
- The workflow is procedural (open → show_today → write → save → render_timeline → idle)
- The 9 warnings are the load-bearing content (the discipline that makes the workflow correct)
- The scenario variables define the runtime conditions (day_of_year, prefers_reduced_motion, etc.)
- The eval set is concrete (11 measurable criteria)
- The compilation target is clear (Qwen 2.5-3B, self-hosted, ~$50-80 setup, 30-50 min recompile)

This is the proof: the procedure.json pattern works for shipping artifacts, not just workflow specs. Future artifacts (the .md export, the monthly echo view, the weekly breath prompt) can all follow the same shape.

## The 4 compilation blockers

The procedure.json is ready as a spec, but the COMPILE step is blocked by 4 items:
1. Andre has not lived with the prototype for 7+ days (Coder's recommendation)
2. No signal on which questions land vs which feel performative
3. Forgetting rules are under-specified (Scribe flagged this in mavis-as-companion.md)
4. The .md export workflow is not yet designed (would be the v0.2 node)

These are NOT bugs in the procedure.json — they are upstream design decisions. The procedure.json correctly encodes the discipline; the discipline needs validation before the model gets trained on it.

## Live experience

I just walked the procedure.json against the actual prototype at `03 Projects/Mavis Daily Check-in/01 prototype.html`. The shape matches:
- 9 nodes cover the 9 user-facing states (open → idle)
- 4 terminals cover the 4 outcomes (saves, edits, abandons, storage-disabled)
- 9 warnings cover the 9 design disciplines
- 6 scenario variables cover the 6 runtime conditions
- The question pool is the 15 prompts, listed verbatim
- The storage schema matches the localStorage key + entry shape

The v0.1 procedure.json is the formal spec for the prototype. The prototype is the working code. Both can evolve independently; the procedure.json is the contract, the prototype is the implementation.

## Related

- `daily-brief/procedure.json` — operator-mode daily counterpart
- `mavis-orchestrator/procedure.json` — judgment-mode counterpart
- `humanized-copy/procedure.json` — outward-facing copy counterpart
- `weekly-connections/procedure.json` — weekly operator-mode counterpart
- `03 Projects/Mavis Daily Check-in/01 prototype.html` — the shipping artifact
- `03 Projects/Mavis Daily Check-in/03 handoff.md` — the Coder's handoff (the source material for this procedure.json)
- `02 Notes/ideas/mavis-as-companion.md` — the Scribe's operator/companion synthesis (the discipline source)
- `02 Notes/articles/mphrediction-missing-use-case.md` — the article that the companion mode operationalizes

---
*Staged 2026-06-04 23:30 CT, during the wrap-up of the Andre-out autonomous session. First v0.1 of the daily-checkin procedure.json. First end-to-end application of the article's playbook to a shipping artifact. Not compiled; 4 explicit compilation blockers. The prototype is the working code, this is the formal spec.*
