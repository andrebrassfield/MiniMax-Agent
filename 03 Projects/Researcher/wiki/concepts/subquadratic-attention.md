# Concept — Subquadratic Attention

**Type:** architectural primitive
**First seen in vault:** 2026-06-02
**Dossier:** frontier_ai
**Status:** emerging — first commercial release May 5, 2026 (SubQ 1M-Preview)

## Definition

A transformer attention pattern whose compute scales sub-linearly in context length — typically O(n log n) or better — instead of the standard O(n²) dense attention that dominates current production LLMs. The "subquadratic" family includes sparse attention, linear attention, and hierarchical/segmented patterns.

## Why it matters

Standard transformer attention has a quadratic cost in context length. As context windows grow past 1M tokens, the attention compute begins to dominate inference cost and latency. If subquadratic patterns hold up under independent benchmarks, they change the unit economics of long-context inference — a 12M context model at 1/5 frontier cost would invert how Andre's stack (which depends heavily on long context via MSA sparse attention on M3) thinks about retrieval vs. context-window tradeoffs.

## Known instances

- **SubQ 1M-Preview** (Subquadratic, May 5, 2026) — first commercial LLM with fully subquadratic sparse attention, 12M token context window, claimed 52x faster attention at scale and ~1/5 cost of frontier models. Source: whatllm.org (secondary, weight 0.7). Verification pending — claims have not been independently benchmarked in the open as of 2026-06-02.
- **M3 MSA sparse attention** (the Researcher's own runtime) — 1M context via MiniMax MSA. This is the closest "production" instance Andre already has running.

## Open questions

- Does SubQ hold up on independent benchmarks, or is the 52x figure marketing?
- What is the actual quality degradation curve at 1M+ tokens vs. standard attention?
- Is subquadratic a temporary bridge to better architectures (state-space models, etc.) or a permanent shift?

## Source trail

- src-2026-06-02-011 (whatllm.org May 2026 roundup) — weight 0.7 (secondary)
- Related: src-2026-06-02-024 (HF Trending Models) — no direct subquadratic instance trending
- Related: src-2026-06-02-021 (geo.fkw.com) — uncorroborated GPT-6 architecture claim mentions "Symphony" but no subquadratic attribute, weight 0.2

## Related concepts

- [[Agentic Memory Architectures]]
- [[Context Window Economics]]
