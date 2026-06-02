---
type: idea
created: 2026-06-02
status: seed
tags: [idea, inference, memory-bandwidth, hardware-bound, llm-systems, mavis-deep-silicon]
related: [[UMA as Killer Feature — The Local Agent Memory Ceiling]], [[Apple-NVIDIA Inversion]], [[Apple Silicon Memory Bandwidth Ladder]]
domains: [llm-inference, systems-thinking, hardware-architecture]
source: https://www.sitepoint.com/local-llms-apple-silicon-mac-2026/, https://insiderllm.com/guides/m4-max-ultra-local-llms-apple-silicon/, https://codersera.com/blog/apple-silicon-llms-complete-guide-2026/
---

# Memory Bandwidth is the Real LLM Inference Ceiling

> For batch-size-1 local LLM inference (the Omni-Operator regime), the *memory bandwidth between model weights and the compute units* is the dominant throughput constraint — not raw FLOPs, not cache size, not NUMA topology. Apple Silicon's UMA bandwidth ladder (100-800 GB/s) is the real performance curve. The same model on the same architecture at 2x bandwidth = ~2x tok/s. Everything else is noise.

## What this idea is

Every token requires reading the model weights through the memory hierarchy. For a 70B Q4 model, the weights are ~40 GB. To generate 1 token, you must read 40 GB of weights at the bandwidth of your memory system.

The math is unforgiving:
- M3 Ultra 800 GB/s, 40 GB weights → 50 ms per token = 20 tok/s
- M4 Max 546 GB/s, 40 GB weights → 73 ms per token = 13.7 tok/s
- RTX 4090 1008 GB/s, but model offloaded across PCIe (64 GB/s) → ~600 ms per token = 1.6 tok/s
- H100 3350 GB/s, model in HBM3 (80 GB) → 24 ms per token = 41 tok/s

The 70B Q4 case is a "capacity-bounded" workload: only the M3 Ultra can hold the entire model in fast memory. The RTX 4090 can't, the H100 can. Once the model fits in fast memory, the bandwidth ladder is the throughput curve.

For sub-7B models that fit on any device, the equation inverts — peak compute matters more, NVIDIA wins. But the Omni-Operator is operating at 30B-70B class for parity with cloud APIs. The local agent is bandwidth-bound.

## Why this matters

Three architectural decisions follow:

1. **Don't add more cores; add more bandwidth.** On Apple Silicon, this means Max/Ultra tiers, not Pro. The M4 Pro (273 GB/s) is bandwidth-limited for 30B+; the M4 Max (546 GB/s) and M3 Ultra (800 GB/s) are the right shape.
2. **MoE > dense for local agents.** Qwen3-30B-A3B activates only 3B parameters per token. Effective bandwidth requirement is 3B × bits-per-param, not 30B. Same memory pool, much faster. Local LLMCheck benchmarks show Qwen3-30B-A3B at ~100 tok/s on 32GB M-class, vs ~13 tok/s for dense 30B.
3. **Quantization is a bandwidth play, not a quality play.** Q4 vs Q8 is roughly 2x bandwidth. Same hardware, ~2x throughput. The Q8 quality advantage is real for reasoning-heavy tasks; the Q4 throughput advantage is real for interactive agents. Choose by use case.
4. **Paging is expensive.** Blockwise Paging for Long Context ([[Blockwise Paging for Long Context]]) tells you the in-memory regime is the right one; page-out to NVMe is 10x slower than UMA. Keep the working set in UMA.

## What would falsify this

- Speculative decoding changes the math — if you accept 2-3 draft tokens per step, effective bandwidth improves. MLX has speculative decoding; vllm-mlx has it. The bandwidth ceiling is breakable with algorithmic tricks.
- MoE expert routing variance — if a few "hot" experts absorb 50% of tokens, the effective bandwidth requirement is back to dense for those experts. NPUMoE (arXiv 2604.18788) addresses this with energy-aware scheduling.
- If the user is doing batch inference (multiple parallel requests), the math changes. Continuous batching amortizes weight reads across requests; H100 with vLLM continuous batching hits 1000+ tok/s aggregate. The local agent at batch=1 is not the batched regime.

## Connections

- [[UMA as Killer Feature — The Local Agent Memory Ceiling]] — the bandwidth ladder as the architectural lever.
- [[Apple Silicon Memory Bandwidth Ladder]] — the hard numbers (100-800 GB/s).
- [[Apple-NVIDIA Inversion]] — bandwidth advantage vs capacity advantage; the local regime wants capacity.
- [[Blockwise Paging for Long Context]] — the in-memory regime is bandwidth-optimal; page-out is the 10x penalty.
- [[70B Q4 Throughput on Apple Silicon]] — concrete benchmarks validating the math.

## See also

- [[M3 Edge]] — M3's 1M context is also bandwidth-bound; the architecture has to manage the budget.
- [[Esalen, Not Foxconn]] — the model is the engine; the engine runs at bandwidth speed, not FLOP speed.

---

*Seed 2026-06-02. To validate: a benchmark script that sweeps batch size, quant, and bandwidth ceiling on M3 Ultra 192GB vs M4 Max 128GB vs M5 Max, all on the same model. The predicted pattern: throughput scales linearly with bandwidth, sub-linearly with compute.*
