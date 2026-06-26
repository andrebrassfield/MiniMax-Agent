---
date: 2026-06-25
type: connection
trigger: nightly-finder
strength: strong
thesis-relevant: true
thesis-link: Thesis 1 (the bottleneck is spec throughput, not implementation) + Thesis 3 (skills beat agents when the harness is mature) + Thesis 5 (Mavis is structurally isomorphic to an LLM)
domains-crossed: [verification-substrate, loop-engineering, akash-harness, dose-of-proof-operations]
---

# Connection: codegraph-on-vault closes part of the Anosognosia gap from the 06-24 "ships that aren't load-bearing" connection — DISCOVER stage is now the first Mavis loop stage with a structural (deterministic) verifier

**Why this connection matters:** The 2026-06-24 `ships-that-arent-load-bearing` connection ended with a sharp finding: "Mavis has rules without mechanisms. A skill that exists on disk and a skill that runs in production look identical in the catalog. The loop-engineering plan's 6 blocks include Memory (block #6) but not *verification of which block is currently firing* — that's the missing 7th block, or the missing audit layer for the existing 6." This morning's synthesis (2026-06-25) reports: "the 5-stage loop's DISCOVER stage got a 10x speedup because `codegraph_explore` is now a different process from the chief session... Before codegraph-on-vault, DISCOVER was chief-greps-and-reads the same loop. After: the chief queries, codegraph answers — they are not the same process. The '10x speedup' IS the architectural payoff of the maker-≠-checker rule applied to a single stage." Reading the 06-24 gap-finding and the 06-25 morning-synthesis together reveals that **codegraph-on-vault is the first partial closure of the Anosognosia gap.** Not the full closure (skills, crons, substrates still need verification) — but a structural, deterministic verifier is now live for the DISCOVER stage of every Mavis loop, and the verifier is a *different process* from the chief (Boris Cherny's maker-≠-checker rule operationalized at one stage). This is the architectural payoff the 06-24 connection named. It's also Thesis 5 (Mavis-as-LLM) in operational form: Stage 5 (Evaluation) is no longer aspirational — it's instrumented for DISCOVER. The 10x speedup is the visible benefit; the structural benefit is that DISCOVER now has a verifiable outcome metric, just like an SFT'd model needs held-out eval.

**Note A:**
- Title: Morning Synthesis — 2026-06-25 (Connections #2)
- Path: `~/MiniMax-Agent/02 Notes/_MOCs/2026-06-25-morning-synthesis.md`
- Claim: The synthesis explicitly identifies codegraph-on-vault as the first structural verifier at the DISCOVER stage. The "10x speedup" is the visible payoff; the structural payoff is the maker-≠-checker rule applied to a single stage. Before: DISCOVER was "chief greps + reads the same loop." After: "chief queries, codegraph answers — they are not the same process." The synthesis cites `02 Notes/patterns/ea-loop-vocabulary.md` (Maker ≠ Checker, Boris Cherny's load-bearing rule) and `01 Daily/2026-06-22.md` (codegraph v1.0.1 = first structural verifier) as the source pair.

**Note B:**
- Title: Connection — Three "ships" that aren't load-bearing — `ea-skill-evolution` dormant + `ea-correction-capture` Phase A possibly unfired + `reply-sweep-daily` HALTs as `success`
- Path: `~/MiniMax-Agent/08-COMPOUND/2026-06-24-connection-ships-that-arent-load-bearing.md`
- Claim: Three artifacts Mavis treats as load-bearing (a skill, a feedback-loop phase, a cron) all turn out, on close inspection, to be *shells that don't run*. The unifying discipline gap: "Mavis currently has no registry of which artifacts (skills, crons, loops) are stated-live vs revealed-live. A skill that exists on disk and a skill that runs in production look identical in the catalog." The connection proposed adding a verification step to the `ea-correction-capture` plan, plus a one-shot audit cron that diffs the skill catalog against the crons that reference those skills. The gap named: the loop-engineering plan's 6 blocks don't include "verification of which block is currently firing."

**Note C:**
- Title: Akash Pachaar — The Anatomy of an Agent Harness (harness components #10: Verification Loops)
- Path: `~/MiniMax-Agent/02 Notes/articles/_pending_reaction/2026-06-04 - akash-pachaar-anatomy-of-an-agent-harness.md`
- Claim: Akash's 12-component harness checklist includes "Verification Loops" as component #10 — "computational (deterministic) vs inferential (semantic, adds latency)." The article frames the verification layer as a first-class component of the harness, not an optional add-on. The Von Neumann analogy frames the LLM as CPU and verification loops as the operating system's process supervision — every productive process has a verifiable state.

**What reading all three reveals:** Codegraph-on-vault is the first Mavis-side artifact that satisfies Akash's component #10 (Verification Loops) at the loop-stage level (DISCOVER), not just the output level (the chief's response). It's a *deterministic* verifier (computational, not inferential — adds no LLM latency, just queries the dependency graph). It's a *different process* from the chief (maker-≠-checker). It runs on a *different substrate* than the LLM (codegraph is filesystem + database, not transformer inference). All three properties — deterministic, different-process, different-substrate — are the criteria Akash's component #10 implicitly demands.

The 06-24 connection said Mavis has rules without mechanisms. Today's evidence: at least one rule (the DISCOVER stage must find canonical sources) now has a mechanism (codegraph). The 10x speedup is the visible payoff; the structural payoff is that DISCOVER now has a verifiable outcome metric — for the first time, Mavis can answer "did DISCOVER actually find what it claimed to find?" without re-doing DISCOVER. That's the Anosognosia disease being treated (not cured) at one stage.

The non-obvious finding: **the 10x speedup is the wrong metric to celebrate.** The 10x is a performance number (DISCOVER now runs faster). The architectural number is: "DISCOVER now has a different process from the chief." When a single agent does DISCOVER with the same brain that does PLAN/EXECUTE/VERIFY/ITERATE, the agent is reasoning about its own reasoning — a known failure mode (the LLM can rationalize its own outputs because it generated them). When a different process (codegraph) does DISCOVER, the chief can't rationalize codegraph's output because it didn't generate it. The 10x is a symptom; the architectural payoff is *epistemic independence* between the loop stages.

This is Thesis 3 (skills beat agents when the harness is mature) in operational form: codegraph IS the verification skill. It's not a new agent — it's a deterministic skill that the chief loop calls at the DISCOVER stage. The article's claim ("skills beat agents when the work is non-trivial and the harness is mature") is now visibly true at one specific stage. The pattern is repeatable: at PLAN stage, the verifier could be a plan-validation skill (checks the plan against the goal); at EXECUTE stage, the verifier could be a state-diff skill (checks the diff against the plan); at VERIFY stage, the verifier could be an evaluator-skill (checks the output against the spec). Each is a deterministic skill that the chief calls, not a new agent that the chief coordinates.

This is also Thesis 5 (Mavis-as-LLM) in operational form: Stage 5 (Evaluation) is the LLM-side analog of the harness-side verification loops. The 06-24 connection said Stage 5 was missing for Mavis. Today's evidence: Stage 5 is partially instrumented (DISCOVER stage only). The full Mavis Stage 5 would have:
- (a) DISCOVER verifier: codegraph-on-vault (LIVED)
- (b) PLAN verifier: plan-validation skill (NOT YET)
- (c) EXECUTE verifier: state-diff skill (NOT YET)
- (d) VERIFY verifier: evaluator-skill (PARTIALLY — Verifier agent exists but is inferential, not deterministic)
- (e) ITERATE verifier: feedback-aggregation skill (PARTIALLY — `ea-correction-capture` is a candidate)

This is a buildable roadmap. Each is a skill (not an agent), deterministic (mostly), and lives at a different loop stage.

**Suggested next step:**
- For the 2026-06-26 morning synthesis: cross-reference this connection explicitly. Frame codegraph as the *first* Stage-5 verifier, not the only one. The roadmap above is the candidate next steps.
- For `mavis-loop-engineering-plan-2026-06-22.md`: add Stage-5 verifier roadmap as Item 4 (after Items 1-3 already on the plan). The roadmap above is the candidate list. Each verifier is a skill, not an agent — consistent with Thesis 3.
- For `agent-harness-principles.md` (the topic file): add codegraph-on-vault as the canonical worked example of Akash's component #10 at the loop-stage level. Update the topic-file description to note this is the first instrumented verifier in the Mavis harness.
- For Thesis 5: this connection is the first hard evidence that the Mavis-as-LLM framing produces concrete architectural decisions (the Stage-5 roadmap). Update `mavis-as-llm.md` with the Stage-5 instrumentation status (DISCOVER: live; PLAN/EXECUTE/VERIFY/ITERATE: not yet) as the working state of the 5-stage audit.
- For the Anosognosia disease (per `agent-disease-detector`): amend the disease description with a "treatment in progress" status for the DISCOVER stage. The disease is not cured, but one stage now has a treatment.
