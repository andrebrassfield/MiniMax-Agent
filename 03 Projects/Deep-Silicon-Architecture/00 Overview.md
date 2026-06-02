---
type: project
created: 2026-06-02
status: master
tags: [project, master-thesis, omni-operator, apple-silicon, mavis-deep-silicon]
related: [[SOUL]], [[agent]], [[Mavis-Apex-Architecture]], [[Esalen, Not Foxconn]], [[state-of-mavis]]
source: 13 CHIEF notes in 02 Notes/{patterns,ideas,numbers}/, Operation Deep Silicon 2026-06-02
---

# Deep Silicon Architecture — The Omni-Operator Thesis

> **How to run an Omni-Operator natively on Apple Silicon with zero latency and infinite context.** The hardware ceiling is not the limit; the limit is the *coordination* of three layers — context, agent, and sandbox — that the software layer imposes on the hardware. The thesis: Apple's M-series Unified Memory Architecture is the only consumer hardware that solves the local agent's *capacity* problem without surrendering *bandwidth*. The Omni-Operator is a Mac. The cluster is Macs. The cloud is for training and for >120B models. Local is for the agent.

## 1. The thesis in one paragraph

Today's frontier reasoning models run at 30-100 tok/s on a single Mac Studio M3 Ultra 192GB at 70B Q4. That's the conversational latency threshold — the point at which the user stops perceiving a delay. Above this, the Omni-Operator can plausibly replace a cloud API for the local agent's regime (single-user, batch=1, 30-70B Q4, 30-100K effective context). The M3 Ultra's Unified Memory Architecture is the only consumer hardware that holds a 70B model + 128K context in fast memory; NVIDIA's discrete GPUs at the same price (RTX 4090 $1,600, 24GB VRAM) cannot. The Omni-Operator's "infinite context" is achieved through PagedEviction + Ring Attention + Anchor-Ends — not by stuffing 1M tokens into a single prompt. Its "zero latency" is achieved by the model living in the same memory pool as the agent's working state (no PCIe copy tax). Its "safety" is achieved by hypervisor microVMs (Vibe, Slicer, Lume) — one per task, 200ms-2s cold start, near-native performance, blast-radius isolated. The Esalen operating posture (model is the engine, code is the thin I/O layer) maps cleanly to this: MLX is the thin deterministic layer, the model is the engine, UMA is the I/O bus.

## 2. The hardware substrate

**Apple Silicon's killer feature is Unified Memory Architecture (UMA).** The 64-bit memory controller and silicon interposer let CPU, GPU, and ANE share one memory pool at full bandwidth — no PCIe copy tax. The bandwidth ladder (M2 100 → M3 Ultra 800 GB/s) is the throughput curve for memory-bound local inference. Capacity (24-192 GB) is the differentiator from NVIDIA's discrete GPUs. A 70B Q4 model at 40 GB won't run on a 24 GB RTX 4090 without severe offloading (drops to 8-15 tok/s); on M3 Ultra 192 GB, it runs at 25-30 tok/s with 152 GB to spare. This is the [[UMA as Killer Feature — The Local Agent Memory Ceiling]] pattern, validated against 6 independent 2026 benchmark sources.

The M5 generation adds **GPU Neural Accelerators** — dedicated matrix-multiplication units in every GPU core, accessible via MLX on Metal 4 TensorOps. Up to 4x TTFT speedup over M4 for compute-bound workloads; 19-27% on token generation (memory-bandwidth bound). The Apple-NVIDIA inversion is the strategic frame: **Apple trades raw FLOPs for memory capacity, NVIDIA trades memory capacity for raw FLOPs, the local agent regime is capacity-bounded, Apple wins.**

**ANE is not the primary LLM engine.** It markets 38 TOPS INT8; actual FP16 throughput is ~19 TFLOPS. The 32 MB on-chip SRAM creates a 30% performance cliff when exceeded. ANE's right shape is *always-on, low-power, operation-specific* — the reflection layer's workload (classification, softmax, signal detection) and MoE expert dispatch. Not the primary inference path. The 33.8x softmax speedup over CPU is real and useful for the *secondary* workloads.

## 3. The software architecture

Mavis's existing software layer is the [[Mavis-Apex-Architecture]] (Esalen posture, Resolver, Skill Packs, custom MCPs). The Esalen Posture — model is engine, code is thin I/O, markdown is intent — is the *correct* posture for this regime. The 3 audit questions (is the test Foxconn? is the code a model-judging-itself loop? does the system trust the model?) all resolve to the same answer for Apple Silicon: the model lives in MLX on Metal, the deterministic layer is the driver (Metal shader compilation, page-table management, microVM lifecycle), the instruction layer is the Skill Pack.

What changes when we run on Apple Silicon natively:

- **MLX replaces llama.cpp as the inference engine.** The Ollama-on-MLX switch (March 2026) made this the default for the most popular local-LLM runtime. vllm-mlx adds continuous batching (21-87% throughput gain over llama.cpp; 4.3x aggregate at 16 concurrent requests).
- **ANE replaces CPU for the reflection layer's appraisal functions.** The 33.8x softmax speedup and 6.6 TFLOPS/W power efficiency make ANE the right shape for VIGIL-style appraisal. Zero watts at idle; the reflection layer can be always-on without burning battery.
- **UMA replaces CUDA's VRAM tier.** The "model fits" question becomes "do we have enough UMA." M3 Ultra 192 GB holds 70B Q4 + 32B Q4 simultaneously (multi-agent, multi-model residency).
- **Virtualization.framework replaces Docker for tool-execution sandboxes.** The microVM cold start (200ms-2s) is fast enough for per-task isolation. The 75-95% native filesystem performance via VirtioFS kills the "VM is too slow" objection. The host can snapshot, replay, and destroy per task.

What does NOT change:

- **The Resolver's routing logic.** Mavis-Apex's functional-area dispatcher is model-agnostic; it routes to whatever the substrate is.
- **The Skill Pack authoring pattern.** Markdown instructions, capability-based skills, Esalen-composed.
- **The vault as the archival memory.** Same Obsidian vault, same 02 Notes/{patterns,ideas,numbers}/ routing, same daily brief, same weekly connections.

## 4. The context layer

**The 1M context window is a marketing claim, not an operating regime.** A 1M-token prompt is gated by (1) the U-curve attention bias ([[Attention Sink as Architectural Bias]]), (2) KV-cache memory pressure (70-90% of VRAM at 1M), and (3) the cost of prefill (O(N²) in context length). For the Omni-Operator, the *effective* context is 30-100K tokens. The 1M figure is a ceiling, not a target.

**Anchor-Ends is the prompt-layer mitigation.** Place high-signal at prefix (operating contract) and suffix (current task). The U-curve's structural property is well-documented across 5 independent papers (Liu 2023, Chroma 2025, MIT 2025, Salvatore 2025, MSR 2024 LongLLMLingua). For 30-100K context with an 8-15% middle-position accuracy gap, Anchor-Ends + Microsoft LongLLMLingua compression (21.4% gain at 4x) is the right combination. No model modification required — works at the API/instruction layer.

**Blockwise Paging is the infrastructure layer.** Ring Attention + PagedAttention + PagedEviction + TokenRing + Context Parallelism together make 1M+ context tractable. 77s for 1M prefill on 128 H100s. Single Mac with PagedAttention + PagedEviction handles 200K at 30+ tok/s. Multi-Mac JACCL cluster over Thunderbolt 5 scales to 120B+ at 10-20 tok/s. The pattern is *page tables everywhere*: vLLM PagedAttention for KV cache, MemGPT/Letta for agent memory, OS virtual memory for the hardware. The same primitive, three layers.

**The "infinite context" promise is PagedEviction + Ring Attention + Anchor-Ends, not raw 1M.** Effective infinite = (active working set in UMA) + (overflow paginated to NVMe with PagedEviction) + (overflow-of-overflow spread across multi-Mac Ring Attention) + (the U-curve mitigated by Anchor-Ends). The user perceives "infinite" because the *effective* context is always in the high-signal region.

## 5. The agent layer

**The 2026 stack for agent engineering has matured.** Multi-agent in single context ([[Mixture of Agents]], [[Reflexion Loop]]), self-healing via reflection ([[Self-Healing via Reflection Layer]] — VIGIL/SEMAF/Azure LLMOps), LLM-as-judge (Sage, TrustJudge, IF-RewardBench, Prometheus 2), and tool-execution sandboxes (E2B, Daytona, Modal, Firecracker, gVisor) are all production-grade. The Omni-Operator's agent layer adopts these.

**The self-healing pattern is the load-bearing one.** VIGIL's stage-gated pipeline (`start → eb_updated → diagnosed → prompt_done → diff_done`) prevents the agent from improvising illegal transitions. SEMAF's multi-source feedback + Evolution Engine drives policy optimization. The reflection layer runs on host ANE (zero idle power, 33.8x softmax speedup), always-on, observes the agent's behavioral JSONL log. When it detects a failure, it proposes a guarded prompt update (only the adaptive section; core identity immutable) or a read-only code diff. The agent loop never sees the reflection. The operator approves the patch. The agent continues.

**This is the Esalen shape.** Watchdog for state (catches real failure modes), not cage for trust (cages are Foxconn). The reflection layer is a sibling runtime, not a parent watchdog. Model-judges-itself loops are explicitly the wrong shape.

**Tool execution sandboxes:** For untrusted LLM-generated code, the production-grade sandboxes (E2B, Daytona, Modal) are Linux-side. On Apple Silicon, the macOS-native equivalent is a microVM (Vibe, Slicer, Lume) using Virtualization.framework. The architectural primitives are the same: ephemeral execution, hardware isolation, network policy. The difference: Apple Silicon microVMs share the host's memory pool (UMA), so the *model* can stay in host MLX while the *tool execution* runs in a microVM. The agent reasons on the host, executes in the sandbox, returns string outputs. Blast radius contained.

## 6. The sandbox layer

**The Omni-Operator's safety story is hypervisor microVMs, not Seatbelt profiles.** Seatbelt (Claude Code's default) is config-file isolation — fast (1s) but typo-prone. Docker on macOS is a Linux VM under the hood anyway, so the "lighter than VM" argument is wrong. Virtualization.framework + Vibe/Slicer/Lume gives:
- **200ms-2s cold start** (Vibe ~10s first, Slicer 200ms instant-clone from cached image, OrbStack 2s)
- **75-95% native filesystem performance** via VirtioFS
- **Near-native CPU performance**
- **Per-task ephemeral isolation** — snapshot, replay, destroy
- **UMA-shared memory pool** — the model stays in host, the tool execution in the sandbox

The cost-quality tradeoff is closed. The "VM is too slow for per-task sandboxing" objection is dead. The Omni-Operator's safety layer is a microVM per task, with the reflection layer providing in-band monitoring and the microVM providing out-of-band blast-radius containment.

## 7. The numbers

The benchmarks that anchor the thesis:

| Metric | Value | Source |
|---|---|---|
| M4 Max memory bandwidth | 546 GB/s | Apple ML research, hybrid-llm |
| M3 Ultra memory bandwidth | 800 GB/s | hybrid-llm |
| M5 base memory bandwidth | 120 GB/s (28% over M4's 120) | Apple ML research |
| M5 GPU Neural Accelerator speedup on TTFT | 4x over M4 | Apple ML research |
| 70B Q4 throughput on M4 Max 128GB | 28.4 tok/s | currentaffair, insiderllm, localaimaster (all converge) |
| 70B Q4 throughput on M3 Ultra 192GB | 25-30 tok/s | insiderllm |
| 70B Q4 throughput on M3 Max 128GB | 11.2 tok/s | currentaffair |
| 70B Q4 throughput on M2 Max 96GB | 6.4 tok/s | currentaffair |
| ANE actual FP16 throughput | ~19 TFLOPS (Apple markets 38 TOPS INT8) | maderix + Orion |
| ANE on-chip SRAM | 32 MB (30% throughput drop when exceeded) | Orion |
| ANE softmax speedup over CPU | 33.8x | Orion |
| ANE idle power | 0 W (hard power-gated) | Orion |
| microVM cold start (Slicer) | 200ms instant-clone | Slicer demo |
| microVM cold start (Vibe) | ~10s first, 0.5-2s warm | Vibe project |
| microVM cold start (E2B) | 150ms | E2B docs |
| 1M prefill on 128 H100s | 77s (93% parallelization efficiency) | arXiv 2411.01783 |
| KV cache memory pressure at 1M | 70-90% of VRAM | digitalapplied 2026 |
| Context length alone hurts (perfect retrieval) | 13.9% to 85% degradation | Du et al. EMNLP 2025 |
| Middle-position accuracy drop | 20-50% at 100K | Chroma Research 2025 |
| LongLLMLingua 4x compression | +21.4% accuracy gain | MSR 2024 |
| Multi-Mac JACCL throughput at 120B | 10-20 tok/s | petronellatech |

The "feels like a cloud API" threshold is 25-30 tok/s. M4 Max 128GB and M3 Ultra 192GB both cross it. Below 15, the latency is conversational but stuttery; above 25, the user perceives a real-time chat partner.

## 8. The Top 3 Most Dangerous Architectural Discoveries

**Discovery 1: The 1M context window is a marketing claim, not an operating regime.**

The literature is consistent: 20-50% middle-position accuracy drop at 100K, 13.9-85% degradation from context length alone, KV cache eating 70-90% of VRAM at 1M, 1M prefill at 77s on 128 H100s. The 1M figure is the *upper bound* of what the model can ingest; the *useful* context is 30-100K after the U-curve, KV-cache, and prefill-cost gates. **Implication for the Omni-Operator:** design for 30-100K effective context, not 1M. Use PagedEviction + Ring Attention + Anchor-Ends + LongLLMLingua to extend *effective* range. The "infinite context" promise is achieved through paging, not through stuffing. This is dangerous because it inverts the intuitive design (more context = better) and demands a real architectural commitment to compression and routing.

**Discovery 2: The Apple Neural Engine is a 19-TFLOPS secondary accelerator, not a 38-TOPS primary engine.**

Apple markets 38 TOPS INT8. Actual measured FP16 throughput is ~19 TFLOPS — about half. INT8 only saves memory bandwidth, not compute cycles. The 32 MB on-chip SRAM creates a 30% performance cliff. The 119-compile-per-process limit caps program count. **Implication for the Omni-Operator:** the primary LLM inference engine is M-series GPU via MLX on Metal (525+ tok/s for 7B, ~28 tok/s for 70B Q4). The ANE is the right shape for *secondary*, *always-on*, *power-efficient* operations — exactly the reflection layer's workload. The 33.8x softmax speedup over CPU is real and worth using for output projection. This is dangerous because the marketing number is 2x the reality, and the wrong allocation of ANE to primary inference will silently tank performance.

**Discovery 3: The local agent's safety story is hypervisor microVMs, one per task — not Seatbelt, not Docker, not gVisor.**

Apple Silicon microVMs (Vibe, Slicer, Lume) cold-start in 200ms-2s, share the host's UMA memory pool, run agents as root with --yolo inside the VM, and are isolated at the hardware level via Virtualization.framework. The cost-quality tradeoff is closed. Seatbelt is config-file isolation (fast but typo-prone, 1 escape = game over). Docker on macOS is a Linux VM under the hood anyway. **Implication for the Omni-Operator:** the safety layer is a microVM per task, with the reflection layer providing in-band monitoring and the microVM providing out-of-band blast-radius containment. The agent's *reasoning* runs on host MLX in UMA; the agent's *tool execution* runs in the microVM. The two-layer pattern is the Esalen shape: watchdog for state (in-band), cage for blast radius (out-of-band). This is dangerous because the developer community has not yet consolidated on this pattern; the easy default is Docker, which on macOS is a worse version of the same primitive.

## 9. The build order

This is the concrete next-sprint plan, ordered by leverage and risk:

1. **Validate the Anchor-Ends strategy on M3 Omni-Operator** (1-2 days). Run a controlled experiment: 30K context, 100K context, 1M context; high-signal at prefix only vs at prefix+suffix; measure middle-position retrieval accuracy. Confirm the literature.
2. **Stand up MLX on the local M-series Mac** (1 day). Install mlx-lm 0.19.2+, run Llama 3.1 8B Q4 at conversational speed, profile TTFT and generation tok/s. Confirm the 7B/30B/70B ladder against [[70B Q4 Throughput on Apple Silicon]].
3. **Build the Vibe/Slicer microVM template for agent tasks** (2-3 days). Debian nocloud image with Claude Code, Ollama, MLX, and the basic dev tools. Snapshot as the golden image. Validate 200ms instant-clone and VirtioFS performance.
4. **Implement the Reflection Layer on ANE** (1-2 days). Port VIGIL's appraisal functions to ANE via private API (maderix) or CoreML. Validate the 33.8x softmax speedup on real workloads. The 0W idle power matters for always-on.
5. **Wire PagedEviction into the context layer** (2-3 days). Integrate IndexMem or take-the-best-eviction-policy (Sage-KV, H2O, SnapKV, NACL, RocketKV) and benchmark on the Omni-Operator's 30-100K effective context.
6. **Build the JSON Canvas for the full architecture map** — done as part of this operation ([[Deep-Silicon-Map.canvas]]).
7. **Run the budget audit at month-end** — confirm we're within the $100/month M3 inference budget and that the Apple Silicon runtime reduces cloud spend (zero cloud bills for 70B inference) to make room for training and >120B.

## 10. What's in this project hub

- `00 Overview.md` (this file) — the master thesis
- `Deep-Silicon-Map.canvas` — the visual architecture map
- `01 Apple Silicon Ladder.md` (planned) — the hardware decision tree
- `02 Context Layer.md` (planned) — Anchor-Ends + Blockwise Paging + PagedEviction details
- `03 Agent Layer.md` (planned) — Multi-agent + Self-Healing + LLM-as-Judge details
- `04 Sandbox Layer.md` (planned) — microVM + Reflection Layer + blast-radius containment

And the 13 CHIEF notes in `02 Notes/{patterns,ideas,numbers}/`:

**Patterns (5):**
- [[Anchor-Ends — Validated]]
- [[Self-Healing via Reflection Layer]]
- [[Blockwise Paging for Long Context]]
- [[UMA as Killer Feature — The Local Agent Memory Ceiling]]
- [[Attention Sink as Architectural Bias]]

**Ideas (4):**
- [[Native Hypervisor Sandbox as the Esalen Way to Agent Safety]]
- [[Memory Bandwidth is the Real LLM Inference Ceiling]]
- [[The Apple-NVIDIA Inversion]]
- [[1M Context is a Marketing Claim, Not an Operating Regime]]

**Numbers (4):**
- [[Apple Silicon Memory Bandwidth Ladder]]
- [[70B Q4 Throughput on Apple Silicon]]
- [[ANE Actual Throughput — The 19 TFLOPS Reality]]
- [[MicroVM Cold Start Times]]

## Connections

- [[SOUL]] — the operating contract; Deep Silicon is the build plan under it.
- [[Esalen, Not Foxconn]] — the posture; Deep Silicon is the Esalen compliance audit for Apple Silicon.
- [[Mavis-Apex-Architecture]] — the existing software layer; Deep Silicon is the Apple Silicon-native port.
- [[M3 Edge]] — M3's 1M context is the capability; Deep Silicon is the *operating regime* that exploits it without falling into the marketing trap.
- [[Long-Horizon Patterns]] — 12h+ autonomy needs the safety layer (Reflection + microVM) and the context layer (Anchor-Ends + PagedEviction) to not break.
- [[Mixture of Agents]] — multi-agent is the right shape for >70B tasks; Apple Silicon's multi-model residency makes it cheap.
- [[Reflexion Loop]] — predecessor of the Self-Healing pattern.

---

*Operation Deep Silicon complete 2026-06-02. The Omni-Operator is a Mac. The architecture is the Mavis-Apex-Architecture ported to Apple Silicon native, with three layers added: ANE for the reflection layer, microVM per task for the safety layer, PagedEviction + Anchor-Ends for the context layer. The 1M context is a ceiling, not a target. The build order is locked. Awaiting GO for vault push.*
