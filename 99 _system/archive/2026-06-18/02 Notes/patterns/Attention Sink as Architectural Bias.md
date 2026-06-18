---
type: pattern
created: 2026-06-02
status: validated
tags: [pattern, attention, transformer-architecture, decoder-only, foundational, mavis-deep-silicon]
domains: [transformer-architecture, attention, decoder-only-models]
source: https://arxiv.org/abs/2307.03172 (Liu et al. 2023, lost in the middle), https://techxplore.com/news/2025-06-lost-middle-llm-architecture-ai.html (MIT 2025), https://arxiv.org/abs/2510.10276 (Salvatore et al. 2025), https://arxiv.org/abs/2502.01951 (Wu et al. 2025, MIT theoretical)
---

# Attention Sink as Architectural Bias

> The U-shaped attention curve in long-context LLMs is not a bug. It is a **structural property** of decoder-only transformers: causal masking gives early tokens structural visibility, RoPE introduces distance decay, and specific attention heads act as "sinks" that concentrate mass on the first token. The bias is intrinsic to the architecture, not the training data. Mitigations must either modify the model or work around the U-curve at the prompt layer.

## The pattern

The phenomenon is empirically established (Liu et al. 2023, Chroma 2025, MIT 2025) and the mechanism is now theoretically explained (Wu et al. 2025, Salvatore et al. 2025).

Three causes stack:

1. **Causal masking visibility asymmetry** — In a decoder-only transformer, token #1 is visible to token #2, #3, #4, …, #N. Token #500 is visible to tokens #501-#N only. Early tokens get a structural *visibility* advantage: they can accumulate attention from many later tokens; later tokens cannot retroactively attend. As the model grows deeper, this bias *amplifies* because earlier parts of the input are used more frequently in the model's reasoning (MIT 2025).

2. **RoPE distance decay** — Rotary Position Embedding makes the dot product between query and key vectors naturally decay with position distance. Fast-rotating dimensions encode short-range; slow-rotating dimensions encode long-range. Middle tokens have neither — they are too far for the fast dims to help, too close to be rescued by the slow dims. The U-shape is geometric.

3. **Attention sinks** — Specific attention heads (especially in early layers) concentrate disproportionate mass on the first token. Dropout interventions on these heads *flatten primacy* (and degrade overall performance) — proving the sinks are causally responsible. (Salvatore et al. 2025) This is *not* a learned bug; it is a stable attention pattern in decoder-only transformers. Bidirectional models (T5, encoder-decoder) show much less positional bias.

Salvatore's framing: the U-shape is an *adaptation* to a mixture of retrieval demands during pretraining — some pretraining tasks require uniform recall across the entire input (long-term memory demand), others prioritize most-recent tokens (short-term memory demand). Under cross-entropy, the model converges to a U-shape: primacy from uniform recall, recency from end-weighted recall. The middle gets sacrificed.

## Why this matters (the leverage)

The leverage is **architectural awareness**. If you build on top of decoder-only transformers, you cannot eliminate the U-curve. You can:

1. **Anchor-Ends at the prompt layer** — place high-signal at prefix + suffix. (See [[Anchor-Ends — Validated]].)
2. **Modify the model** — Found in the Middle (UW/MIT/Google 2024) calibrates attention bias and improves middle retrieval by 15pp. Ms-PoE rescales position indices for specific attention heads, gaining 20-40% middle accuracy with no fine-tuning.
3. **Compress the middle away** — Microsoft LongLLMLingua: 4x compression, 21.4pp accuracy gain. The middle becomes too small to lose information in.
4. **Re-segment the context** — break long contexts into multiple shorter inference calls; each call is fresh, no decay.

For a 1M-context M3 Omni-Operator, option (1) is the instruction-layer (Esalen) play; option (3) is the deterministic-layer (I/O) play. Both are correct; use both.

The pattern also explains why some mitigation strategies *don't* work: prompt engineering "put the important info first" only hits the *primacy* half. You also need to hit the *recency* half. The Anchor-Ends strategy is the only mitigation that explicitly targets both ends of the U-curve.

## Anti-patterns (when this DOESN'T apply)

- **Encoder-only or encoder-decoder models** — less positional bias; the U-curve is decoder-only.
- **Models with non-RoPE positional encodings (ALiBi, NoPE)** — these can have different bias profiles.
- **Sub-2K contexts** — the U-curve is too shallow to matter.
- **Streaming/agentic generation** where the suffix is overwritten by new tokens — the recency bias shifts but the sink/primacy pattern persists.

## Evidence strength

- [ ] Single observation (anecdote)
- [x] Multiple observations, same domain — Liu 2023, Chroma 2025, MIT 2025, Salvatore 2025
- [x] Multiple observations, multiple domains (strong) — decoder-only transformers (Llama, Mistral, Qwen, Claude, Gemini), all show U-curve
- [x] Tested and confirmed (strongest) — attention sink ablation experiments (Salvatore 2025) directly prove the causal mechanism by removing the heads and watching primacy flatten

## Connections

- [[Anchor-Ends — Validated]] — the prompt-layer mitigation that exploits the U-curve.
- [[Blockwise Paging for Long Context]] — infrastructure layer; the bias is in the model, paging is in the system.
- [[Esalen, Not Foxconn]] — the U-curve is a *property of the engine*, not a *cage* you build around it. Anchor-Ends is an instruction-layer exploit, not a code-layer workaround.

---

*Pattern locked 2026-06-02. This is the foundational architectural fact that Anchor-Ends and the entire context-engineering layer of the Omni-Operator is built on top of. It is not a flaw to fix; it is a property to design around.*
