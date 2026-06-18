# mavis-orchestrator procedure.json

> Mavis-judgment (frontier) procedure. NOT compilable as a small model — judgment-required workflows stay on frontier. The procedure.json is a META-procedure: it routes to the right judgment workflow and applies the right structure. The actual content of each judgment is Mavis-judgment on the model itself.

## Status

**v0.1.0-draft** — first articulation. Not compiled. The Mavis-judgment engine is the frontier model itself; the procedure.json encodes the dispatch logic and the structural discipline, not the content.

## What's in the file

- **system_prompt** — who Mavis-judgment is, and what is NOT its scope (operator-mode goes to Mavis-procedural, companion-mode is a separate layer, spawn prompts are authored here but execution is delegated to workers)
- **4 judgment workflows** (the load-bearing content):
  - `design_review` — the 4-step protocol (summarize, surface contradiction, challenge assumption, sharper question). The signature workflow.
  - `contradiction_surface` — the 3-step protocol (name both, cite both, state weight without resolving)
  - `assumption_challenge` — the 2-step protocol (name the premise, state the alternative)
  - `build_order_question` — the hierarchy (external deliverable → chief infrastructure → internal synthesis → exploration) + the lean + the override question
- **3 routing-out workflows**:
  - `routed_to_procedural` — operator-mode goes to Mavis-procedural (daily-brief, weekly-connections, queue-triage)
  - `spawned_worker` — producer I/O goes to a specialist (Researcher, Builder, Designer, Coder, Verifier)
  - `judgment_not_appropriate` — explicit directive for execution, but no 'go' signal yet; surface the design-review framing
- **5 terminals** (success, two external handoffs, user clarification, judgment-not-appropriate)
- **10 warnings** (severity: high) — the 5 non-negotiables from the chief contract, plus 5 cross-cutting lessons from the 2026-06-04 morning: spec-block-is-design-review, lead-with-wins-then-fix-then-dont-change, no-handshake-loops, delegate-producer-work, read-queue-before-dispatch
- **eval_set_planned** — qualitative criteria, not pass/fail rates (judgment work doesn't score like procedural work)

## Why this isn't compilable (the structural insight)

Procedural workflows (daily-brief, weekly-connections) have a single-question-per-turn shape. The compiled Mavis-procedural engine can handle them by walking the flowchart with a small model.

Judgment workflows (design review, contradiction surfacing) require contextual reasoning that doesn't flowchart cleanly. The MODEL itself is the engine. A compiled 3B model could in principle be trained on design-review examples, but the quality would degrade sharply — the load-bearing insights depend on Andre's specific context (the dossier references, the prior conversations, the article canon). The frontier model is the right tool.

What the procedure.json CAN do for Mavis-judgment: encode the dispatch logic (which of the 4 workflows applies) and the structural discipline (the warnings array, the node definitions). This is the META-procedure — it makes Mavis-judgment more reliable, not cheaper.

## Compilable layer (future v0.2)

If we wanted to compile this, the compilable subset would be:
- The classification of inputs into 4 workflows (could be a small classifier)
- The routing decisions (operator-mode → Mavis-procedural, producer I/O → specialist spawn)
- The structural templates (the 4-step design review protocol, the 3-step contradiction protocol)

The non-compilable layer (stays on frontier):
- The actual content of the contradiction or the assumption challenge
- The recommendation in the build-order question
- The sharper question at the end

The future workflow: Mavis-judgment handles the body, Mavis-procedural handles the routing and the structural skeleton.

## Scope boundary

This procedure is for **Mavis-judgment workflows**. It is NOT:
- The operator-mode daily brief (see `daily-brief/procedure.json`)
- The operator-mode weekly connections (see `weekly-connections/procedure.json`)
- The companion-mode check-in (the Coder's prototype at `03 Projects/Mavis Daily Check-in/`, a separate artifact)
- The Scribe's prose work (the Scribe is a separate agent with its own contract)

The boundary is enforced by the `routed_to_procedural` and `judgment_not_appropriate` terminals — they route misclassified inputs to the right engine.

## Warnings (the load-bearing content)

The 10 warnings are the discipline that makes Mavis-judgment reliable. The 5 chief-contract non-negotiables (quote-verbatim, sharpen-to-one-sentence, end-with-sharper-question, surface-contradictions, challenge-assumptions) are the load-bearing bones. The 5 cross-cutting lessons (spec-block-is-design-review, lead-with-wins-then-fix-then-dont-change, no-handshake-loops, delegate-producer-work, read-queue-before-dispatch) encode the morning's hard corrections — the failure modes that almost shipped.

The 5 chief-contract non-negotiables are mandatory; the 5 cross-cutting lessons are learned-from-evidence. Both are severity: high.

## Next steps

1. **Live with v0.1 for 5 design reviews.** Surface edge cases the v0.1 doesn't handle. v0.2 will absorb them.
2. **Test the workflow classification.** When Andre sends a long input, do I correctly route to design-review vs spec-execute? When two beliefs disagree, do I correctly route to contradiction-surface? When Andre asks "what next?", do I correctly route to build-order-question? The classification is the load-bearing decision.
3. **Refine the structural templates.** The 4-step design review protocol is v0.1; the Scribe's mavis-as-companion synthesis had 7 contradictions worth attention — could those be a structured template for contradiction-surface?
4. **Future compilation candidate:** the classification layer (input → workflow) and the routing decisions could be compiled as a small classifier (3B territory). The body of each judgment stays on frontier.

## Related

- `daily-brief/procedure.json` — the operator-mode counterpart
- `weekly-connections/procedure.json` — the weekly operator-mode counterpart
- `02 Notes/ideas/mavis-as-companion.md` — the Scribe's operator/companion synthesis
- `06 Connections/2026-06-04 - AI-as-companion landing.md` — the strategic synthesis that grounds the two-engine chief role

---
*Staged 2026-06-04 13:00 CT, during an Andre-out autonomous session. First v0.1 of the Mavis-judgment meta-procedure. Not compiled. The Mavis-judgment scope stays on frontier; this is the structural discipline, not the content.*
