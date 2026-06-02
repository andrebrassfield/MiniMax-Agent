---
type: pattern
created: 2026-06-01
status: developing
tags: [pattern, orchestration, moa, agent-architecture]
domains: [llm-systems, multi-agent]
---

# Mixture of Agents

> Layered LLM aggregation where each layer's agents see all prior-layer outputs as auxiliary context, then synthesize a higher-quality response. The whole beats any single member — even when members are weaker.

## Where this pattern appears

### Domain 1: Together MoA (2024)
Wang et al. (Together AI + Duke + Stanford + U-Chicago), arXiv 2406.04692, ICLR 2025. Three-layer MoA using only open-source models — Qwen1.5-110B-Chat, WizardLM-8x22B, LLaMA-3-70B-Instruct, Mixtral-8x22B, dbrx-instruct — scored **65.1% on AlpacaEval 2.0**, beating GPT-4 Omni's 57.5% by 7.6 points. Code at github.com/togethercomputer/moa.

### Domain 2: Self-MoA (2025)
arXiv 2502.00674. The followup surprised everyone: aggregating multiple outputs from the *same* model (temperature sampling) beat mixing different LLMs by **6.6% on AlpacaEval 2.0** and 3.8% on average across MMLU/CRUX/MATH. The "collaborativeness" effect isn't about model diversity — it's about giving the model a panel of drafts to react to.

### Domain 3: M3 1M-context aggregation
When [[M3 Edge]] gives you 1M tokens of context, the cost curve for "run 6 models in parallel, aggregate the outputs" flattens. Sparse attention makes proposer calls cheap; same window accepts all 6 outputs. MoA becomes a routine option instead of a luxury.

## Why this pattern matters

- **Quality lift without retraining.** Together MoA hit SOTA on three benchmarks with zero fine-tuning — pure orchestration of off-the-shelf models.
- **Composability.** MoA stacks with anything: prefix caching, tool use, retrieval, [[Reflexion Loop|self-critique]]. Each layer can apply its own transformation.
- **Cost shift, not cost reduction.** MoA's per-query token cost is higher than a single call, but per-quality-unit cost can be lower. The right metric is "tokens per winning answer," not "tokens per call."
- **The collaborator phenomenon.** Wang et al. observed that LLMs reliably do better when shown other models' outputs — even when those outputs are *worse* than what the model would produce cold. This is counter-intuitive and worth a permanent note.

## Anti-patterns (when this DOESN'T apply)

- **Latency-sensitive paths.** Together MoA explicitly notes high TTFT — the aggregator can't start until all proposers finish. Sequential Self-MoA helps but doesn't eliminate this. Sub-200ms interactive UIs don't get MoA.
- **Single-ground-truth tasks.** Math, deterministic code, fact lookup. Aggregation can't synthesize a better answer when there's one right answer; it can only vote.
- **Privacy-isolated contexts.** MoA leaks every prompt to every proposer. If the input contains secrets you can't route to N providers, you can't MoA.
- **Same-model Self-MoA on small models.** The paper shows 12% gains at ≤9B parameters, but the quality floor is still the base model. Self-MoA on a 7B is still a 7B.

## Evidence strength

- [ ] Single observation (anecdote)
- [ ] Multiple observations, same domain
- [x] Multiple observations, multiple domains (strong) — ICLR 2025 + 4 follow-ups + 3.9K+ citations on Reflexion companion work
- [ ] Tested and confirmed (strongest)

## Connections

- [[Reflexion Loop]] — another single-context self-improvement pattern; can run as one of the MoA layers
- [[Context Engineering 1M]] — M3's 1M context removes the "stitch 6 outputs" cost barrier
- [[M3 Capabilities]] — MSA makes parallel proposer calls cheap enough to make this routine
- [[Mavis EA Workflow]] — when I see a synthesis task, this is the default mental model

---
*Sources: arXiv 2406.04692 (Wang et al., Together MoA, 2024); arXiv 2502.00674 (Li et al., Rethinking MoA, 2025); together.ai/blog/together-moa; github.com/togethercomputer/MoA.*
