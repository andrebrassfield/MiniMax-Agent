---
type: pattern
created: 2026-06-02
status: active
tags: [pattern, context-engineering, ring-attention, paging, kimi, mavis-deep-silicon]
domains: [distributed-systems, attention, long-context]
source: https://arxiv.org/abs/2411.01783 (Context Parallelism for Million-Token Inference), https://arxiv.org/abs/2402.08268 (Blockwise RingAttention / LWM), https://arxiv.org/html/2412.20501v1 (TokenRing), https://introl.com/blog/kv-cache-optimization-memory-efficiency-production-llms-guide, https://www.exxactcorp.com/blog/deep-learning/how-llms-reach-large-token-context-windows
---

# Blockwise Paging for Long Context

> Chunk the sequence. Page the KV cache. Ring the compute. Long-context inference (1M+ tokens) is now a **distributed-systems problem**, not a model problem. Blockwise RingAttention + PagedAttention + TokenRing + Context Parallelism turn an O(N²) impossible task into an O(N/k) parallel one with 93% parallelization efficiency at 128 H100s.

## The pattern

The 1M-token context window is now an operating regime, not a research artifact. The 2024-2026 stack that made it tractable:

1. **Blockwise RingAttention (Liu et al. 2024)** — partition the sequence across devices, each device computes attention against its local block, then KV blocks ring around the topology. The Pallas + FlashAttention fusion overlaps comm with compute, so the ring cost is hidden as long as tokens-per-device is large enough. The LWM (Large World Model) paper demonstrates 1M-token training across TPU v4-128 with 32-way tensor + 4-way sequence parallelism.

2. **Context Parallelism (arXiv 2411.01783, Nov 2024; v3 Apr 2025)** — the production form. Two lossless ring variants: pass-KV and pass-Q. **77 seconds for 1M-context prefill on Llama 3 405B across 128 H100s** (93% parallelization efficiency, 63% FLOPS utilization). 128K-context prefill in 3.8s. RDMA and TCP both work — the bandwidth threshold is moderate.

3. **TokenRing (arXiv 2412.20501, Dec 2024)** — bidirectional ring with concurrent Q and block_out + block_lse transmission. Reduces comm overhead from 7.6ms to ~3.5ms per ring step on 4xA10. The point: comm can be a 2-3x bottleneck, and bidirectional routing kills it.

4. **PagedAttention (vLLM, SOSP 2023)** — the OS-virtual-memory cousin at the inference layer. KV cache is divided into 16-token blocks; logical-to-physical page tables eliminate 60-80% KV cache waste. Cut to <4% waste. 2-4x throughput. Now the default for any LLM serving at scale.

5. **PagedEviction (arXiv 2509.04377, 2025)** — block-wise eviction tailored for PagedAttention. Drops the lowest-importance blocks by `||V||/||K||` ratio. 10-12% lower latency, 15-20% better accuracy than StreamingLLM. The pattern: OS-style virtual memory is the right metaphor for the agent's *own* memory management too (MemGPT/Letta).

6. **Cake, LayerKV, InfiniGen, Oneiros, CLO** (2025) — the offload-based extensions. When KV exceeds GPU memory, page to CPU/NVMe. 44-82% latency reduction at 8B-70B scale. The Hybrid compute-load systems (Cake) schedule GPU and I/O cache generation in parallel, cutting TTFT by 2.6x.

7. **Zig-Zag Ring Attention** — load balance for causal masking. In autoregressive ring attention, GPU 0 only attends to its own block first; later GPUs idle. The zig-zag pattern interleaves positions so each GPU gets a mix of early + late tokens, equalizing the causal-mask compute.

## Why this matters (the leverage)

For an Omni-Operator with 1M context (M3-class), the question is not "can the model attend" but "can the *system* page." The answers above show:
- **The cost is hardware-comparable, not software-intractable.** 77s for 1M prefill on 128 H100s = $0.40-$1.00 on H100 cloud pricing. Single H100 with PagedAttention + PagedEviction handles 200K-token contexts at 30+ tok/s.
- **The communication is the bottleneck, not the math.** TokenRing's 2x comm reduction is the same order of magnitude as the model improvement.
- **The same primitive (page tables) works at three layers:** vLLM PagedAttention (inference KV), MemGPT/Letta (agent memory), and OS virtual memory (the hardware). The pattern generalizes.

For a *single-Mac* Omni-Operator, Blockwise Paging is the *paging for off-device context*. The M3 Ultra 192GB can hold ~120B model + large context in UMA; beyond that, page to NVMe SSD or to a second Mac over Thunderbolt 5. Multi-Mac JACCL clusters now run 120B+ models at 10-20 tok/s.

## Anti-patterns (when this DOESN'T apply)

- **Short contexts (<32K)** — the overhead of paging exceeds the cost of just holding the KV.
- **Single-user, single-GPU with no NVMe offload** — PagedAttention is in-memory; if you don't have page-out, the benefit is just the page-table reduction (still real, just smaller).
- **Strict latency budgets** — ring comm adds 10-50ms per hop. For interactive sub-200ms responses, stay single-device.
- **Causal-mask workloads without zig-zag** — load imbalance wastes 30-50% of compute on the first/last device in the ring.

## Evidence strength

- [ ] Single observation (anecdote)
- [x] Multiple observations, same domain — Blockwise + Context Parallel + TokenRing + PagedAttention are all from 2023-2025, multiple production deployments
- [x] Multiple observations, multiple domains (strong) — vLLM (inference serving), MemGPT (agent memory), LWM (training), LoongTrain (head-context parallelism), RingX (HPC)
- [x] Tested and confirmed (strongest) — vLLM PagedAttention is the production default; LWM trained end-to-end; Context Parallelism 77s benchmark reproducible

## Connections

- [[Paged Memory Pattern]] — MemGPT/Letta + vLLM share the OS-virtual-memory lineage.
- [[Anchor-Ends — Validated]] — paging protects the context infrastructure; Anchor-Ends exploits the attention biases of the model.
- [[Memory Bandwidth is the Real LLM Inference Ceiling]] — page-out to NVMe is bandwidth-bound; UMA is ~10x faster than NVMe, so page-out is a 10x latency hit.
- [[Native Hypervisor Sandbox as the Esalen Way to Agent Safety]] — sandbox VM can hold a paged context window across long-running tasks without escaping to host.
- [[Apple Silicon Memory Bandwidth Ladder]] — UMA bandwidth is the floor for in-memory paging; NVMe page-out is the ceiling.

---

*Pattern locked 2026-06-02. The 1M-context M3 Omni-Operator runs on this stack — PagedAttention in-process, PagedEviction for compression, Ring Attention for multi-Mac, Anchor-Ends for prompt architecture.*
