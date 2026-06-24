---
description: "The 5-stage procedure ea-research-brief runs — scope, regime check, primary-source dispatch, noise filter, runtime cross-reference. Load when the skill is invoked. Moved from SKILL.md inline content 2026-06-22 as part of Upgrade 1 aggressive refactor."
---

# ea-research-brief — The 5-stage Procedure

1. **Scope** (Stage 1) — lock the question in one sentence, the deliverable shape, and the disk anchors (vault paths the worker should cross-reference). If scope is more than 1 line per element, scope is not tight enough.
2. **Regime check** (Stage 2) — pre-flight the 4 regulatory regimes (EU AI Act, FDA AI/ML + PCCP, HIPAA Security Rule, State-bar UPL). **HALT on any hit + no human-in-the-loop.** See `[[02 Notes/patterns/ea-research-brief-regulatory-regimes]]`.
3. **Primary-source dispatch** (Stage 3) — send the worker prompt per `[[02 Notes/patterns/ea-research-brief-dispatch-template]]`. Anchoring requirements: quote verbatim, fetch cited sources directly, end with "what I don't know," cross-reference runtime.
4. **Noise filter** (Stage 4) — separate signal from editorial / stale / saturated. See `[[02 Notes/patterns/ea-research-brief-noise-patterns]]` for the 5 categories (stale scaling laws, op-eds, vendor marketing copy, retracted pre-prints, saturated benchmarks).
5. **Runtime cross-reference** (Stage 5) — verify the brief against live MEMORY.md, skill state, cron state, last 30 days of relevant dispatches. Surface any contradictions before publishing.

The output schema is 6 sections: Scope → Primary sources → Findings → Runtime cross-reference → What I don't know → Verification checklist. Full template at `[[02 Notes/patterns/ea-research-brief-output-schema]]`.
