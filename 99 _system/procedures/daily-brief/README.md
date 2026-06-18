# daily-brief procedure.json

> First `procedure.json` in the vault. The article's playbook, applied to the Mavis-procedural engine — the compiled half of the two-engine chief role.

## Status

**v0.1.0-draft** — seeded from the Scribe's mavis-as-companion.md synthesis (2026-06-04 01:50 CT) + chief contract (adopted 2026-06-02) + the Coder-loop lesson (2026-06-04 08:36 CT). Not yet compiled.

## What's in the file

- **system_prompt** — who Mavis-procedural is, and what is NOT its scope (companion mode, design review, spawn-prompt writing)
- **9 nodes** — the workflow steps, with single-question-per-turn discipline
- **terminals** — 4 outcomes: success, user_clarification, escalation, external_handoff (routed_to_judgment)
- **9 warnings** — the bugs found in testing, with `learned_from` citations and severity
- **scenario_variables** — the variables that change per brief (window, count thresholds, sleep state)
- **eval_set_planned** — the 7 held-out criteria for the v0.1 evaluation pass

## Scope boundary

This procedure is for the **operator-mode daily brief**. It is NOT:
- The companion-mode daily check-in (that's the Coder's prototype at `03 Projects/Mavis Daily Check-in/`, a separate procedure)
- Design review (Mavis-judgment handles spec blocks and contradictions)
- Spawn-prompt writing (Mavis-judgment handles producer spawns)

The boundary is enforced by the `routed_to_judgment` terminal — if a spec block or design-review request comes in, this engine routes it to the frontier engine rather than attempting to handle it.

## Warnings (the under-specified discipline)

The 9 warnings are the load-bearing content. They are the bugs found in testing during the 2026-06-04 cascade recovery + the 2026-05-26 feedback correction + the 2026-06-03 orchestrator discipline lesson. They translate the chief contract's prose into flowchart rules the compiled model can follow.

The highest-severity warnings (severity: high):
- `6-hour-window-rule` — recap-vs-status distinction
- `sharpen-to-one-sentence` — recommendation discipline
- `end-with-sharper-question` — closer discipline
- `lead-with-wins-then-fix-then-dont-change` — feedback structure
- `spec-block-is-design-review` — execution-vs-review boundary
- `delegate-producer-work` — orchestrator discipline

## Next steps

1. **Live with v0.1 for 5 runs** (per the Coder's "live with it a week" discipline). Surface edge cases the v0.1 doesn't handle. v0.2 will absorb them.
2. **Run a v0.1 eval set** (200 conversations) once 5 live runs have produced edge cases. Use the 7 held-out criteria above. Hold-out score above 80% → ready for compile.
3. **Compile to Qwen 2.5-3B** (per the article's spec). Self-host on a rented GPU. Cost: ~$50-80 + ~30-50 min recompile cycle.
4. **Replace the daily-brief in the cron with the compiled engine.** The frontier Mavis-judgment engine takes over design review, contradiction surfacing, and the "is this spec block or execution" call. The compiled engine handles the morning brief.

## Related

- `02 Notes/ideas/mavis-as-companion.md` — the Scribe synthesis that seeded the warnings
- `06 Connections/2026-06-04 - AI-as-companion landing.md` — the synthesis-of-syntheses that ties this to the cascade + article
- `02 Notes/patterns/agent-harness.md` — the operator-mode view; this procedure is the procedural half
- `/tmp/builder-prompt-fleet-ui.md` — the Builder's first procedure.json candidate (in flight)

---
*Staged 2026-06-04 09:21 CT, while Builder is mid-build on the Fleet-Status Surface renderer. Not yet compiled; awaiting 5 live runs to surface edge cases.*
