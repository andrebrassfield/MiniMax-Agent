---
type: pattern
created: 2026-06-01
status: developing
tags: [pattern, memory, memgpt, virtual-context]
domains: [llm-agents, memory-systems]
---

# Paged Memory for Long-Running Agents

> Treat the LLM's context window like RAM, external storage like disk, and let the agent page between them via explicit function calls. The agent manages its own memory hierarchy.

## Where this pattern appears

### Domain 1: MemGPT / Letta (Packer et al., 2023)
arXiv 2310.08560. Three tiers: **main context** (in-window, like RAM), **archival memory** (vector store, like disk), **recall memory** (searchable conversation log). The LLM itself decides when to page in/out, when to search recall, when to rewrite its own core memory — all via function calls. The "LLM OS" framing.

### Domain 2: vLLM PagedAttention (Kwon et al., SOSP 2023)
Different scale, same pattern. PagedAttention divides the KV cache into fixed-size **blocks** (typically 16 tokens) and allocates them on demand. Logical-to-physical block tables, like OS page tables. Cut KV cache waste from 60–80% to under 4%. 2–4× throughput. Production standard for any LLM serving at scale.

### Domain 3: PagedEviction (2025)
arXiv 2509.04377. Block-wise eviction algorithm tailored to PagedAttention — drops the lowest-importance blocks (by `||V||/||K||` ratio) when memory pressure hits. 10–12% lower latency, 15–20% better accuracy than StreamingLLM. The pattern: import OS-style virtual memory into the agent's *own* memory management, not just the inference engine's.

## Why this pattern matters

- **Separates "what's in my head" from "what's on disk."** The agent can reason about its own memory state — "I should page this out, I don't need it for the next 5 steps." That's a load-bearing distinction for long-horizon work.
- **Unifies the serving stack and the agent stack.** vLLM uses paging for KV cache. MemGPT uses paging for agent memory. The pattern is the same: small fixed-size blocks, indirection tables, on-demand allocation. Once you internalize it, you see it everywhere.
- **M3 + MemGPT = a different category of agent.** With [[M3 Capabilities|1M context]], the "main context" tier gets dramatically larger — you page in whole documents, code repos, vault sections — and the "archival" tier can stay cheap because page-out is rarer. The whole OS metaphor scales.

## Anti-patterns (when this DOESN'T apply)

- **Short single-turn tasks.** The overhead of explicit memory management costs more than the context you save. Just keep it all in the window.
- **M3 with 1M context, low task complexity.** If your task fits comfortably in 200k tokens, MemGPT's tier indirection is pure overhead.
- **When the agent can't reason about memory.** MemGPT requires a model that's good at function calling *and* good at knowing what it doesn't need. Weaker models page in the wrong things or fail to page at all.
- **Latency-critical paths.** Each paging call is a tool invocation. Add enough and you've blown the latency budget.

## Evidence strength

- [ ] Single observation (anecdote)
- [x] Multiple observations, same domain — MemGPT/Letta family has multiple follow-ups (Context Repos 2025, etc.)
- [x] Multiple observations, multiple domains (strong) — agent memory (MemGPT) + inference serving (vLLM) + KV cache research (PagedEviction, IceCache, vAttention)
- [ ] Tested and confirmed (strongest)

## Connections

- [[Context Engineering 1M]] — M3's 1M context changes the economics of when to page
- [[M3 Edge]] — large main context = fewer pages = simpler memory strategy
- [[Mavis EA Workflow]] — my vault is the archival tier; the active session is main context
- [[Linking Principle]] — backlinks are the recall-memory equivalent for a knowledge graph
- [[Vault Conventions]] — the 1M-token window turns vault chunks into main-context candidates

---
*Sources: arXiv 2310.08560 (Packer et al., MemGPT); arXiv 2309.06180 (Kwon et al., vLLM/PagedAttention, SOSP 2023); arXiv 2509.04377 (PagedEviction); research.memgpt.ai; letta.com/blog/context-repositories; the deeplearning.ai "LLMs as Operating Systems" course on MemGPT/Letta.*
