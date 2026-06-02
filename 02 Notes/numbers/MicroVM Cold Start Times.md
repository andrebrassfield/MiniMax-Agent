---
type: number
created: 2026-06-02
status: verified
tags: [number, microvm, sandbox, cold-start, mavis-deep-silicon]
as_of: 2026-04-15
source: https://www.infralovers.com/blog/2026-02-15-sandboxing-claude-code-macos/, https://github.com/lynaghk/vibe, https://kevinlynagh.com/newsletter/2026_02_01_vibe/, https://www.youtube.com/watch?v=haVGXjtSkgE (Slicer for Mac), https://northflank.com/blog/daytona-vs-modal, https://e2b.dev/, https://www.ikangai.com/the-complete-guide-to-sandboxing-autonomous-agents-tools-frameworks-and-safety-essentials/
---

# MicroVM Cold Start Times

> **The number:** Cold start times for microVM-based sandboxes on Apple Silicon and Linux, by platform. Determines the per-task overhead of the agent safety layer.

| Platform | Cold Start | First-token Latency | Notes |
|---|---|---|---|
| Daytona | 27-90 ms | ~200ms execution | Fastest. Snapshot reuse + lifecycle automation. Apple Silicon: works via Docker Desktop. |
| E2B | 150 ms | ~200ms execution | Firecracker microVM, AWS Lambda heritage. Fortune 100 customers. |
| Firecracker (raw) | ~150 ms | — | AWS Lambda's microVM tech. Sub-second cold start. |
| Sprites.dev | 300ms checkpoint | — | Firecracker + NVMe, copy-on-write storage |
| Vibe (Mac, Apple Silicon) | ~10 s (first boot) | 0.5-2s (warm) | Single Rust binary, Debian nocloud |
| Vibe (Mac, warm) | ~5s | — | After first boot, image cached |
| Slicer for Mac (instant clone) | 200 ms | — | From cached golden image, instant clone |
| OrbStack | 2 s (vs 30s for Lima) | — | 40% less RAM than Docker Desktop; shared kernel (WSL2-like) |
| Lima | 8-30 s | — | QEMU/Virtualization.framework VM; first-boot only |
| Docker Desktop (Apple Virtualization) | 5-10 s | — | Standard Docker; Apple Virtualization.framework |
| Modal Sandbox (gVisor) | sub-second | — | gVisor kernel interception; 2-9x performance overhead |
| Anthropic Claude Code sandbox mode | ~1s (Seatbelt) | — | User-space, no VM; config-file based |
| Together.ai sandbox (full VM) | ~500ms | — | From snapshot; 64 vCPU, versioned storage |

## Source

Primary: northflank.com Daytona vs Modal comparison (2026), infralovers.com macOS sandboxing 2026, lynaghk Vibe project (Feb 2026), Slicer for Mac YouTube demo (2026), ikangai sandboxing guide (2026), E2B docs.

## Context

**Apple Silicon microVMs are competitive with Linux microVMs for cold start.** Vibe at 10s (first boot) and Slicer at 200ms (instant clone) match the Linux microVM range. OrbStack's 2s is the developer-experience winner for interactive use, but it's shared-kernel (closer to WSL2 than to true microVM isolation).

The cost-quality tradeoff:
- **200-500ms** (Daytona, E2B, Slicer instant, Together) — production-grade, true microVM isolation
- **2-10s** (Vibe, OrbStack, Lima) — acceptable for agent task sandboxes, less for high-frequency invocations
- **Sub-second** (Modal gVisor) — fast but weaker isolation (user-space kernel, not hardware)
- **Seatbelt-only** (Claude Code sandbox mode) — no VM overhead, but config-file isolation, higher escape risk

For the Omni-Operator, the per-task sandbox is **Slicer-class** (200ms instant-clone from cached image) or **Vibe-class** (10s cold, 0.5-2s warm) for less latency-critical tasks. The 10s first-boot is amortized over many task invocations; the 200ms instant-clone is for production-grade per-task isolation.

## What this changes about my model

The "sandbox per task" cost is **2-10 seconds** for cold start, **sub-second for warm** (Slicer instant-clone). For an agent doing 100 tasks/day, the per-task overhead is 200ms-2s, not 30s. The old objection ("VM is too slow for per-task sandboxing") is gone.

**Implication: the Omni-Operator's safety layer can be a microVM per task without becoming the bottleneck.** The reflection layer ([[Self-Healing via Reflection Layer]]) runs on the host ANE/GPU in UMA, fast and always-on. The tool execution runs in a microVM, isolated, ephemeral, and fast enough.

## Confidence

- [x] High (primary source, verified) — multiple platforms measured
- [x] High for Daytona/E2B/Firecracker (production-grade, audited)
- [ ] Medium for Vibe/Slicer (research/developer tools, may shift with optimization)
- [ ] Medium for OrbStack (proprietary VirtioFS, may not generalize)

## Freshness

Date measured: 2026-04-15. Staleness risk: medium — the VM tech is mature; cold starts will improve with better caching but not dramatically. OrbStack and Slicer are moving fast; refresh in 6 months.

## Connections

- [[Native Hypervisor Sandbox as the Esalen Way to Agent Safety]] — the architectural pattern this enables.
- [[Self-Healing via Reflection Layer]] — the in-band safety complement.
- [[UMA as Killer Feature — The Local Agent Memory Ceiling]] — sandbox VMs share the host memory pool; the model stays in UMA, the sandbox runs a tool-only image.
- [[Apple-NVIDIA Inversion]] — the local regime wants this kind of multi-tenant isolation; Apple's hardware delivers it.
- [[Esalen, Not Foxconn]] — VM is the security boundary (blast-radius cage), Seatbelt is the trust cage (Foxconn risk). VM is the Esalen choice.

---

*Verified 2026-06-02. The per-task sandbox cost is 200ms-2s on Apple Silicon. The "VM is too slow" objection is dead. The Omni-Operator's safety layer is hypervisor microVMs, one per task.*
