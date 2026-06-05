---
description: LLM-as-judge temperature rules, fold-in principle for handoffs, M3 long-horizon patterns. Load when running evals, coordinating agent handoffs, planning long research tasks, or debugging eval flakiness.
---

# LLM Judgment Patterns

## LLM-as-judge temperature: 0.0 for graders, 0.2 for optimizers (2026-06-02)
These are different use cases. Don't conflate them.

- **Grader (LLM-as-judge for safety/correctness evals)**: temperature=0.0. The eval is the gate; bit-deterministic results are required so a regression is real and not sampling noise. Even at 0.2, M3 occasionally flips borderline scoring dimensions (0.5/0.67/0.83) between runs on identical input. The canary rule (100% pass required for red-line categories) is especially vulnerable — one flipped dimension on a red-line item would falsely trigger the canary.

- **Optimizer (SkillOpt target, model improvement loops)**: temperature=0.2 (or whatever lower-but-not-zero). Some noise is OK here because the optimizer aggregates over many samples. Bit-determinism is wrong — you'd bias the optimization toward a single output that may not generalize.

**Hardcode the grader temperature in the script** (don't expose as a flag). If a future use case needs a different temperature for non-grading work, add a separate flag — don't make the grader flag multi-purpose.

**Verified**: SOUL compliance eval set at temp=0.2 produced 2/25 PASS one run, 1/25 PASS on identical input the next run. Same eval at temp=0.0 will (in expectation) be bit-deterministic. (Not yet verified empirically — needs a 3x rerun at temp=0.0 to confirm.)

## Mavis fold-in principle — same handoff fixes its own staleness (2026-06-03)
When a handoff causes a side-finding that is bounded by the handoff itself (e.g., a Verifier verdict promotes claims that make a dossier Implication stale), fold the fix into the same handoff instead of queueing for the next cycle. Reason: deferring creates a 6h+ audit gap where the ledger says verified but the dossier still says the pre-handoff state. The audit trail is dishonest during the gap.

When the side-finding's blast radius is NOT bounded by the handoff (e.g., a new primary source needs to be captured, a dossier coverage gap unrelated to the handoff, a cross-dossier link to an untracked file), queue for the next REFRESH. The Researcher's signal: 'do not silently fix; flag, adjudicate, then fold-in or defer with explicit reasoning.'

Captured from the vrf-handoff-2026-06-03-001 two-pass pattern (initial consumption → Research flags 4 anomalies → Mavis adjudicates → fold-in pass). The fold-in principle is documented in `03 Projects/Researcher/decisions/research-questions-resolved.md#rqr-2026-06-03-001` as a precedent for future Mavis-coordinated handoffs. Use this entry as the rule, the decisions/ file as the worked example.

## M3 long-horizon patterns (learned from M3 launch demos)
- Don't bail at first plateau — keep exploring different optimization directions
- 1,959 tool calls in a 24h CUDA optimization; best result on submission 145 (most models gave up by 30)
- 12h autonomous paper reproduction with 18 commits, 23 figures
- Implication for EA work: when running a long research/synthesis task, let it grind. Don't quit early because an early result looked good
- 128k+ output tokens (40k cap from M2.7 is gone)
