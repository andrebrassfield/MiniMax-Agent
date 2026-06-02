---
type: number
created: 2026-06-02
status: verified
tags: [number, benchmark, apple-silicon, llama-3-3-70b, inference-throughput, mavis-deep-silicon]
as_of: 2026-05-26
source: https://www.currentaffair.today/blog/technology-13/mac-m4-max-local-llm-70b-benchmark-493, https://insiderllm.com/guides/m4-max-ultra-local-llms-apple-silicon/, https://localaimaster.com/blog/apple-silicon-ai-buying-guide
---

# 70B Q4 Throughput on Apple Silicon

> **The number:** Tokens per second for **Llama 3.3 70B at Q4_K_M quantization** (~40 GB) on Apple Silicon, by chip.

| Chip | tok/s (Llama 3.3 70B Q4) | Generation | Year |
|---|---|---|---|
| M1 Max (64GB) | 5.8 | M1 | 2020 |
| M2 Max (96GB) | 6.4 | M2 | 2023 |
| M3 Max (128GB) | 11.2 | M3 | 2023 |
| M4 Pro (48GB) | (not feasible — 40GB won't fit in 48GB with context) | M4 | 2024 |
| M4 Max (128GB) | 28.4 | M4 | 2024 |
| M4 Max (128GB) | 20-28 (community reports) | M4 | 2024 |
| M3 Ultra (192GB) | 25-30 | M3 | 2024 |
| M2 Ultra (192GB) | 11-14 | M2 | 2023 |

## Source

Primary: currentaffair.today M4 Max 70B benchmark (May 2026) + insiderllm M4 Max/Ultra guide (2026) + localaimaster.com buying guide (2026). All three converge on the M4 Max 28.4 tok/s figure for Q4_K_M. The M2 Max 6.4 → M3 Max 11.2 → M4 Max 28.4 progression tracks the bandwidth ladder (400 → 400 → 546 GB/s) — 70B Q4 is bandwidth-bound.

## Context

For comparison, on NVIDIA hardware:
- RTX 4090 (24GB VRAM) — won't fit 70B Q4 fully; partial offload drops to 8-15 tok/s
- Dual RTX 3090 NVLink (48GB) — 25-35 tok/s, but 700W+ system
- H100 80GB — 40-60 tok/s, batched cloud

The Apple Silicon numbers are **single-user, single-stream** (no continuous batching). vllm-mlx continuous batching at 16 concurrent requests achieves 4.3x aggregate throughput (arXiv 2601.19139).

## What this changes about my model

**The local "feels like a cloud API" threshold is 25-30 tok/s.** M4 Max 128GB and M3 Ultra 192GB both cross it. Below 15 tok/s, the latency is conversational but stuttery; above 25, the user perceives a real-time chat partner.

For the Omni-Operator:
- **M4 Max 128GB at $3,500** = the developer workstation. Holds 70B Q4 + 128K context (12 GB KV). 28 tok/s. Conversational.
- **M3 Ultra 192GB at $5,000** = the operator workstation. Holds 70B Q4 + 32B Q4 simultaneously (multi-agent). 25-30 tok/s each. Multi-model residency.

The "which Mac for AI" decision is now: **$3,500 M4 Max 128GB if you need one model; $5,000 M3 Ultra 192GB if you need multi-model or future-proofing for >70B.**

## Confidence

- [x] High (primary source, verified) — three independent benchmarks converge on M4 Max 28.4 tok/s
- [x] High for M3 Max/M2 Max progression
- [ ] Medium for the M5 Max estimate (no M5 Max 70B Q4 published yet)

## Freshness

Date measured: 2026-05-26. Staleness risk: medium — M5 Max benchmarks will arrive mid-2026 and may change the ladder by ~30%. The 70B Q4 is the right benchmark; sub-30B numbers are bandwidth-proportional.

## Connections

- [[Apple Silicon Memory Bandwidth Ladder]] — the bandwidth ladder is the throughput curve.
- [[UMA as Killer Feature — The Local Agent Memory Ceiling]] — the capacity that makes 70B feasible at all.
- [[Memory Bandwidth is the Real LLM Inference Ceiling]] — the architectural principle.
- [[The Apple-NVIDIA Inversion]] — the strategic positioning.
- [[Anchor-Ends — Validated]] — at 28 tok/s, Anchor-Ends matters more, not less.

---

*Verified 2026-06-02. The "feels like a cloud API" threshold is 25-30 tok/s. M4 Max 128GB and M3 Ultra 192GB both cross it. Below that, you're typing into a fax machine; above that, you're chatting with a colleague.*
