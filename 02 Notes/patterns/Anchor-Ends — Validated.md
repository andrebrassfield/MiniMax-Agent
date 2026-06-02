---
type: pattern
created: 2026-06-02
status: validated
tags: [pattern, context-engineering, attention, prompt-architecture, anchor-ends, mavis-deep-silicon]
domains: [llm-attention, prompt-engineering, long-context]
source: https://arxiv.org/abs/2307.03172 (Liu et al. 2023), https://arxiv.org/abs/2510.10276 (Salvatore et al. 2025), https://www.getmaxim.ai/articles/solving-the-lost-in-the-middle-problem-advanced-rag-techniques-for-long-context-llms/ (Maxim AI 2025), https://techxplore.com/news/2025-06-lost-middle-llm-architecture-ai.html (MIT 2025)
---

# Anchor-Ends — A Validated Architectural Strategy

> Place the highest-signal content at **Position 0 (Prefix)** AND **Position N-1 (Suffix)** of any prompt or context payload. This is a structural exploit of two well-documented attention biases: primacy (early-token over-attention) and recency (end-of-context). It is not a heuristic — it is a workaround for an architectural property of decoder-only transformers.

## The pattern

The "lost in the middle" effect was named in Liu et al. 2023 (TACL): when relevant information sits at position 10/20 in a long context, performance drops 30%+ vs. position 1 or 20. Chroma Research (2025) confirmed the effect across 18 frontier models — Claude decays slowest but is not immune. Du et al. (EMNLP 2025) proved the effect persists *even with perfect retrieval and no distractor tokens* — the length itself damages performance (13.9% to 85% degradation as input length grows).

The mechanism is now well-understood. Three causes stack:
1. **Causal masking** — early tokens get attended to by every subsequent token; later tokens do not get attended to by early ones. This gives early tokens a structural visibility head-start (MIT 2025 theoretical analysis).
2. **RoPE distance decay** — dot products between queries and keys naturally decay with position distance, so middle tokens have lower attention scores than equivalent end tokens.
3. **Attention sinks** — specific attention heads concentrate disproportionate mass on the first token; ablating these heads flattens primacy (Salvatore et al. 2025).

Salvatore's framing is the cleanest: the U-shape is not a bug, it is an *adaptation* to the mixture of retrieval demands during pretraining — long-term uniform recall (early tokens) and short-term recency (last tokens). Under cross-entropy, this mixture collapses to primacy + recency at the cost of mid-context.

## Why this matters (the leverage)

For any EA or agent system building long contexts, Anchor-Ends is the single highest-leverage prompt-architecture pattern. Mitigations validated in 2025:
- **Strategic ordering** (anchor at prefix + suffix) — works at the API level, no model modification
- **Attention calibration** (Found in the Middle, UW/MIT/Google ACL 2024) — improves middle retrieval by 15pp but requires model modification
- **Context compression** (Microsoft LongLLMLingua) — 21.4pp gain at 4x compression; eliminates the middle
- **Multi-scale Positional Encoding (Ms-PoE)** — rescaling position indices for specific attention heads, 20-40% middle-position accuracy gain, no fine-tuning
- **HiLight (Meta + Stony Brook, 2026)** — input-side intervention that inserts `<start_important>` / `<end_important>` tags around high-signal tokens via a lightweight Emphasis Actor; no model retraining

For a 1M-context M3 Omni-Operator, Anchor-Ends is the only mitigation that works at the instruction layer (Esalen-style: "code is just a thin deterministic layer for I/O; the model is the engine"). The trick is the *position* of the system instructions and the *recency* of the active task. Suffix-anchoring the current task, prefix-anchoring the operating contract, leaves the middle as a free retrieval zone — but it is the U-curve's *blind spot*, not its strength.

## Anti-patterns (when this DOESN'T apply)

- **Pure RAG with >5 documents** — the middle is unavoidable. Use LongLLMLingua or rerank-then-anchor, not raw long context.
- **Short contexts (<2K tokens)** — the U-curve is too shallow to matter.
- **Streaming output** where the suffix is overwritten with each token — Anchor-Ends only works on the *input* side; for streaming, use attention-sink-aware output placement.
- **Encoder-only or encoder-decoder models** — they have less positional bias; the U-curve is decoder-only (T5, encoder-decoders show less degradation).

## Evidence strength

- [ ] Single observation (anecdote)
- [ ] Multiple observations, same domain
- [x] Multiple observations, multiple domains (strong) — Stanford TACL 2023, Chroma 2025, MIT 2025, Rutgers 2025, MSR 2024 (LongLLMLingua)
- [x] Tested and confirmed (strongest) — Liu et al. and Chroma both have controlled position-perturbation experiments

## Connections

- [[Blockwise Paging for Long Context]] — Ring Attention + PagedAttention is the *infrastructure* Anchor-Ends protects; the prompt architecture assumes you can keep high-signal content at the ends even when the middle is paginated.
- [[Paged Memory Pattern]] — MemGPT/Letta + vLLM PagedAttention share the OS-virtual-memory lineage.
- [[Self-Healing via Reflection Layer]] — VIGIL pattern; reflection log anchored at suffix of every turn.
- [[M3 Edge]] — M3's 1M context makes Anchor-Ends economically viable for the first time; before M3, you didn't have enough context to lose.
- [[Memory Bandwidth is the Real LLM Inference Ceiling]] — local-agent regime, every token counts; Anchor-Ends compounds with routing efficiency.
- [[Esalen, Not Foxconn]] — operating posture; Anchor-Ends is instruction-layer (markdown), not code-layer.

---

*Validated 2026-06-02 against 5 independent papers across 2023-2026. The pattern is *real* and *load-bearing* for any long-context system. It is not a hack; it is the model's nature.*
