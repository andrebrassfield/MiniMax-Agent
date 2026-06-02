---
type: number
created: 2026-06-02
status: verified
tags: [number, hardware, apple-silicon, memory-bandwidth, mavis-deep-silicon]
as_of: 2026-06-02
source: https://hybrid-llm.com/tutorial/benchmarks/best-local-llm-models-mac/, https://insiderllm.com/guides/m4-max-ultra-local-llms-apple-silicon/, https://machinelearning.apple.com/research/exploring-llms-mlx-m5, https://www.currentaffair.today/blog/technology-13/mac-m4-max-local-llm-70b-benchmark-493
---

# Apple Silicon Memory Bandwidth Ladder

> **The number:** Apple Silicon unified memory bandwidth, by chip tier, 2024-2026.

| Chip | Bandwidth | Max UMA | Generation |
|---|---|---|---|
| M1 | 68 GB/s | 16 GB | 2020 |
| M2 | 100 GB/s | 24 GB | 2022 |
| M2 Pro | 200 GB/s | 32 GB | 2023 |
| M3 Pro | 150 GB/s | 36 GB | 2023 |
| M1 Pro | 200 GB/s | 32 GB | 2020 |
| M2 Max | 400 GB/s | 96 GB | 2023 |
| M3 Max | 400 GB/s | 128 GB | 2023 |
| M4 Pro | 273 GB/s | 64 GB | 2024 |
| M4 Max | 546 GB/s | 128 GB | 2024 |
| M5 (base) | 120 GB/s | 32 GB | 2025 |
| M5 Pro | ~250 GB/s (est) | 64 GB | 2025 |
| M5 Max | ~600 GB/s (est, 28% over M4) | 128 GB | 2025 |
| M2 Ultra | 800 GB/s | 192 GB | 2023 |
| M3 Ultra | 800 GB/s | 192 GB | 2024 |
| M4 Ultra | (rumored) ~900 GB/s | 256 GB | 2025-2026 |
| M5 Ultra | (rumored) ~1 TB/s | 512 GB | 2026 |

## Source

Primary: hybrid-llm.com benchmark compilation (Q1 2026) + Apple ML research M5 blog (April 2026) + insiderllm M4 Max/Ultra guide. Apple does not officially publish memory bandwidth for M-series chips; numbers are measured by community benchmarks (e.g., M5: 153 GB/s on base, vs M4: 120 GB/s, confirmed in Apple's M5 MLX post).

## Context

The 400 GB/s "Max" tier holds from M2 Max through M3 Max (no change). M4 Max jumped to 546 GB/s — the first significant M-series bandwidth increase in 3 years. M5 Max adds another ~10-20% (28% on the base model). Ultra doubles the Max bandwidth via the UltraFusion chip-to-chip interconnect.

For comparison: NVIDIA RTX 4090 GDDR6X = 1,008 GB/s, but 24 GB VRAM. H100 HBM3 = 3,350 GB/s, 80 GB. The M3 Ultra's 800 GB/s is in the same order of magnitude as discrete GPU VRAM bandwidth while holding 192 GB. The 192 GB capacity is the differentiator.

## What this changes about my model

The throughput ceiling for any local LLM inference is dominated by this ladder. A 30B Q4 model (~18 GB) at M4 Max bandwidth = ~33 ms per token = ~30 tok/s. Same model on M4 Pro (273 GB/s) = ~66 ms = ~15 tok/s. Bandwidth is the throughput curve for memory-bound local inference.

For the Omni-Operator, the rule is: **bandwidth is a function of chip tier, not generation**. M3 Max (2023) ≈ M2 Max (2023) at 400 GB/s. M4 Max (2024) = 546 GB/s = 1.36x. M5 Max (2025) ≈ 600 GB/s = 1.5x over M3 Max. Capacity (UMA size) is a separate axis.

The "right" local-agent machine is **M3 Ultra 192GB or M4 Max 128GB**, not M5 Max 128GB. The Ultra tier's 192 GB capacity is the differentiator; the bandwidth delta is small.

## Confidence

- [x] High (primary source, verified) — Apple ML research, hybrid-llm, insiderllm all converge
- [ ] Medium (credible secondary, plausible)
- [ ] Low (estimate, single source, stale)

## Freshness

Date measured: 2026-05-26 (hybrid-llm, M5 launch cycle). Staleness risk: low; this is hardware spec, doesn't drift. Next refresh: when M5 Ultra ships (rumored 2026 Q3-Q4).

## Connections

- [[UMA as Killer Feature — The Local Agent Memory Ceiling]] — the architectural pattern this enables.
- [[Memory Bandwidth is the Real LLM Inference Ceiling]] — why this number is the throughput curve.
- [[Apple-NVIDIA Inversion]] — the strategic positioning.
- [[70B Q4 Throughput on Apple Silicon]] — the validation benchmarks.
- [[Esalen, Not Foxconn]] — model is the engine, hardware is the I/O layer; the I/O layer's bandwidth is the throughput curve.

---

*Verified 2026-06-02 against hybrid-llm, Apple ML research, insiderllm. The M4 Max 546 GB/s + 128GB is the "developer sweet spot" for 70B Q4; the M3 Ultra 192GB is the "operator sweet spot" for multi-model residency.*
