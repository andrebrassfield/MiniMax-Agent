---
type: number
created: 2026-06-02
status: verified
tags: [number, hardware, apple-neural-engine, ANE, mavis-deep-silicon]
as_of: 2026-04-22
source: https://arxiv.org/abs/2603.06728 (Orion 2026), https://insiderllm.com/guides/apple-neural-engine-llm-inference/, https://arxiv.org/html/2604.18788 (NPUMoE)
---

# ANE Actual Throughput — The 19 TFLOPS Reality

> **The number:** Apple markets the M4 Neural Engine (ANE) at **38 TOPS INT8**. The actual measured FP16 throughput is **~19 TFLOPS** — about half the marketed number, because the ANE dequantizes INT8 to FP16 before computing. INT8 saves only memory bandwidth, not compute cycles. The 32 MB on-chip SRAM creates a performance cliff (30% throughput drop when exceeded). The 119-compile-per-process limit caps program count.

## The hardware specs (M4 Max generation)

| Spec | Value | Notes |
|---|---|---|
| Generation | H16 | |
| ANE cores | 16 | per M4 Max |
| Peak INT8 (Apple spec) | 38 TOPS | marketing number |
| **Peak FP16 (measured)** | **~19 TFLOPS** | maderix 2026 + Orion independent |
| On-chip SRAM | 32 MB | per cluster |
| Evaluation queue depth | 127 | |
| Dispatch overhead (XPC+IOKit) | ~0.095 ms | per dispatch |
| Idle power | 0 W (hard power-gated) | |
| Peak power | ~2.8 W | |
| Efficiency | ~6.6 TFLOPS/W | 80x more efficient per op than A100 |
| Compilation limit per process | ~119 | |

## Source

Primary: maderix 2026 (reverse-engineered private ANE API) + Orion (arXiv 2603.06728, Mar 2026) which independently confirmed all measurements + extended to 14 previously undocumented constraints.

## Context

The marketed "38 TOPS" is real *if* you count INT8 operations at double rate (since each takes half the bits). But the ANE dequantizes INT8 to FP16 before doing the math. So the *compute* throughput is the FP16 number: ~19 TFLOPS. INT8 only saves memory bandwidth, not compute cycles.

For comparison:
- M5 GPU Neural Accelerators (per core) — embedded in M5 GPU, accessed via Metal 4 TensorOps
- M5 GPU total compute — 4x speedup over M4 on TTFT for compute-bound workloads
- M5 GPU memory bandwidth — 153 GB/s (28% over M4's 120 GB/s) on the base model

The ANE's killer feature is **power efficiency** (~6.6 TFLOPS/W vs A100's ~0.08 TFLOPS/W), not raw throughput. It's the right shape for *always-on background inference* (Hey Siri, on-device classification, small-model serving), not for primary LLM inference.

## Performance comparison (ANE vs GPU vs CPU, on the same model)

From Orion 2026 (M4 Max, GPT-2 124M):

| Config | Throughput | Latency | Power |
|---|---|---|---|
| CPU decode | 283 tok/s | 3.48 ms/tok | ~15W |
| ANE full forward (decode) | 170 tok/s | 5.76 ms/tok | ~2W |
| ANE prefill (first call) | 12 tok/s | — | (compile overhead) |
| ANE prefill (cached) | 165 tok/s | — | ~2W |

And on operation-specific acceleration:

| Operation | CPU | ANE | Speedup |
|---|---|---|---|
| Classifier fwd (embed × x) | 10.77 ms | 1.06 ms | **10.2x** |
| Softmax (vocab=32000) | 81.11 ms | 2.40 ms | **33.8x** |
| RMSNorm backward | 0.18 ms | 0.21 ms | ~1x |

The ANE is **slow at autoregressive decode** (~170 tok/s for a 124M model — M3 Ultra GPU does 525+ tok/s for 7B), but **massively fast at batched operations** (33.8x on softmax). The right use case: parallelizable batch operations, always-on background tasks, on-device classification. Not the primary LLM inference path.

## The 32 MB SRAM cliff

LLM weight matrices regularly exceed 32 MB. When the working set spills out of on-chip SRAM, throughput drops 30%. The fix: chunk the model across multiple ANE programs (Orion's "deep operation graphs" reach 94% ANE utilization vs ~30% for single operations). The constraint: 119 compilations per process.

## What this changes about my model

The ANE is a *secondary* accelerator for the Omni-Operator, not the primary:
- **Primary LLM inference** — M-series GPU via MLX on Metal. ~525 tok/s for 7B, ~28 tok/s for 70B Q4.
- **ANE for always-on side tasks** — classification, on-device signal detection, agent reflection log appraisal, intent classification. Power efficiency is the value.
- **ANE for MoE expert dispatch** — NPUMoE shows 1.81-3.19x energy reduction vs CoreML, 1.19-1.32x speedup. The right shape for sparse expert routing.
- **ANE for memory-anchored operations** — softmax over a 32K vocabulary is 33.8x faster on ANE. Worth using for output projection.

The ANE *is* useful, just not as a primary LLM engine. It's the right shape for the **reflection layer** ([[Self-Healing via Reflection Layer]]): low-power, always-on, fast for the operation-specific tasks (softmax, classification, signal detection) that the reflection layer needs.

## Confidence

- [x] High (primary source, verified) — maderix 2026 + Orion 2026 + insiderllm all converge
- [x] High (multiple independent measurements)
- [x] High (cross-verified by operation-level benchmarks)

## Freshness

Date measured: 2026-03-06 (Orion paper). Staleness risk: medium — M5 ANE specs not yet reverse-engineered. Will refresh when M5 ANE analysis appears.

## Connections

- [[UMA as Killer Feature — The Local Agent Memory Ceiling]] — ANE shares the UMA pool.
- [[Memory Bandwidth is the Real LLM Inference Ceiling]] — ANE's 32 MB SRAM is its own bandwidth ceiling.
- [[Self-Healing via Reflection Layer]] — VIGIL's reflection layer is the right shape for ANE's always-on, low-power profile.
- [[Native Hypervisor Sandbox as the Esalen Way to Agent Safety]] — sandboxed VMs don't have ANE access; reflection layer on host ANE is the way.
- [[The Apple-NVIDIA Inversion]] — Apple wins on power efficiency per operation; ANE is the extreme example.

---

*Verified 2026-06-02. The ANE is not the primary LLM engine. It's the right shape for the *secondary*, *always-on*, *power-efficient* operations — which is exactly the reflection layer's workload. Allocate the ANE to the in-band safety subsystem, not the inference engine.*
