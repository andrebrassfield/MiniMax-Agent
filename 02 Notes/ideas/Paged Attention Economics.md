---
type: idea
created: 2026-06-01
status: seed
tags: [idea, kv-cache, inference, paged-attention]
---

# Paged Attention Economics

> KV cache used to be the silent tax on long-context inference. vLLM's PagedAttention turned it into a 2-4× throughput win. The next layer — block-aware eviction and semantic clustering — is what makes million-token context affordable for agents that actually run all day.

## Why this matters

Standard KV cache allocation wastes 60-80% of reserved memory to fragmentation — you reserve for the worst case, most sequences use 20-30% of what they reserved. vLLM (Kwon et al., SOSP 2023) borrowed OS virtual memory: divide cache into fixed-size **blocks** (16 tokens typical), allocate on demand, map logical-to-physical via block tables. Result: under 4% waste, 2-4× throughput, prefix sharing via hash table. Production default in 2024-2026.

Then the second wave:
- **PagedEviction** (arXiv 2509.04377) — block-wise eviction by `||V||/||K||` ratio, no CUDA kernel changes, 10-12% lower latency than StreamingLLM.
- **IceCache** — semantic token clustering + paged memory, keeps 99% of full-cache accuracy at 256-token budget. 25% of the tokens, same quality.
- **vAttention** — keeps contiguous virtual memory, lets the OS do demand paging. 1.97× faster than vLLM at token gen, 3.92× faster at prompt processing.
- **Pensieve** — multi-tier cache (GPU + CPU) for multi-turn conversations. 1.51-1.95× throughput vs vLLM, 60-75% latency reduction.

**The pattern:** the field keeps finding more efficiency by treating KV cache as a paged, evictable, tier-able resource — exactly the OS virtual memory metaphor.

## Where this came from

The original vLLM paper (SOSP 2023) plus the 2025 follow-ups (PagedEviction, IceCache, vAttention, Pensieve). Plus Introl's December 2025 production update: KV cache is now often larger than the model weights themselves in production — a 70B model serving 8K context needs ~20GB cache per request, ~640GB for a batch of 32.

## What would have to be true for this to be right

- The next bottleneck after compute + memory is **attention selection** — which KV blocks actually matter for this query. MSA's "KV outer gather Q" approach (M3's pattern) is one answer; learned eviction policies are another.
- **Prefix caching becomes a first-class feature**, not an optimization. If 80% of your requests share a 50K-token system prompt, hash-based prefix sharing saves 80% of prefill cost. Default-on in vLLM today.
- **Tiered cache is normal.** Hot in GPU HBM, warm in CPU RAM, cold in NVMe. LMCache, IceCache, vAttention all enable this.
- **MSA + paged eviction compose well.** M3's block-level attention selection is a natural match for PagedAttention's block-level eviction — you can prioritize caching the blocks MSA would attend to.

## What would falsify this

- If M3's MSA can replace KV cache entirely with compressed latent states (a la DeepSeek MLA), the whole paged-KV story becomes a transitional artifact. (M3 chose *not* to compress KVs — MSA uses real, uncompressed KVs per the launch blog. So paged KV stays relevant for at least this generation.)
- If context windows stop growing because "long context doesn't actually help agents" — see [[Context Engineering 1M]] — then paged eviction is solving a problem that stops mattering. (No signs of this. Frontier labs are still pushing.)
- If a fully new attention mechanism (state-space models, etc.) replaces transformer attention, KV cache is gone and paged attention goes with it. (Speculative; no production-grade replacement yet.)

## Connections

- [[M3 Capabilities]] — MSA is the M3-side counterpart; paged KV is the inference-side counterpart
- [[Paged Memory Pattern]] — the same OS metaphor at the agent level
- [[Context Engineering 1M]] — the user-side design that paged KV enables
- [[Long-Horizon Patterns]] — long-running agents stress the cache in production ways

## See also

- vLLM docs on automatic prefix caching
- The PagedEviction, IceCache, vAttention, Pensieve papers (all 2024-2025)
- LMCache for tiered KV offload
- Introl's December 2025 KV cache production guide

---
*Seed from Operation Apex Phase 1 (2026-06-01). The economic argument is solid; the open question is how much further compression can go before paged KV becomes legacy.*
