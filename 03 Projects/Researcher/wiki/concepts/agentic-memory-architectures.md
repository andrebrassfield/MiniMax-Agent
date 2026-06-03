# Concept — Agentic Memory Architectures

**Type:** design pattern family
**First seen in vault:** 2026-06-02
**Dossier:** ai_agents
**Status:** active research frontier, no canonical winner

## Definition

A family of architectural patterns for giving LLM agents persistent, queryable memory that survives across sessions. Spans context-resident compression, retrieval-augmented stores, reflective self-improvement, hierarchical virtual context, and policy-learned management (per Du 2026 survey).

## Why it matters

LLMs are stateless by default. The difference between an agent that forgets and an agent that compounds is the difference between an experiment and a product. Andre's stack runs gbrain, Honcho, and OpenClaw — all of which sit in this design space. The architecture that wins this race will reshape how every agent stack is built, including Andre's.

## The four production-grade approaches (as of June 2, 2026)

| System | Architectural approach | Best for | Source |
|--------|------------------------|----------|--------|
| **Letta** (MemGPT-derived) | OS-inspired; memory blocks in context, archival on disk, agent-managed via tool calls | Long-running autonomous agents that operate independently | letta.com (primary) |
| **Mem0** | Extract atomic facts from conversation → vector DB; query at read time | Quick setup, chatbots, personal assistants | mem0.ai (secondary corroboration) |
| **Zep** | Temporal knowledge graph with fact validity periods | Production scale + enterprise users + long-term user modeling | getzep.com (secondary) |
| **Cognee** | Knowledge graph over heterogeneous sources (documents, code, conversations) | Complex multi-document reasoning, enterprise knowledge bases | topoteretes/cognee (secondary) |

## Cross-cutting findings

- **MemoryArena (He 2026)** exposes a deep gap: models near-perfect on LoCoMo plummet to 40-60% on multi-session decision tasks. Passive recall is not the same as active decision-relevant memory. (arXiv 2603.07670)
- **Agentic Memory / AgeMem (Yu 2026)** trains memory ops (store, retrieve, update, summarize, discard) as policy via 3-stage RL with step-wise GRPO. Outperforms strong baselines across 5 long-horizon benchmarks. (arXiv 2603.07670)
- **Security class is novel:** InjecMEM (Tian 2026), eTAMP (Zou 2026), SpAIware (Herrador & Rehberger 2026) show persistent memory introduces contamination that survives prompt-injection defenses. (arXiv 2604.16548)

## Open questions

- Does any of the four approaches generalize to Andre's stack, or does gbrain have a different shape entirely?
- Is the answer "use a subquadratic-attention model with huge context" instead of a memory system at all? (See [[Subquadratic Attention]].)
- Will policy-learned memory management (AgeMem-style) replace the current extract-store-retrieve paradigm?

## Source trail

- src-2026-06-02-004 (Letta Code blog, primary, 0.9)
- src-2026-06-02-017 (arXiv Du 2026 memory survey, primary, 0.85)
- src-2026-06-02-018 (arXiv Mnemonic Sovereignty, primary, 0.85)
- (pending) dev.to/agdex_ai Mem0 vs Zep vs Letta vs Cognee comparison (secondary, 0.6)

## Related concepts

- [[Subquadratic Attention]] — competes with memory systems on the long-context axis
- [[Agent Runtime Primitives]] — memory is one of several agent runtime primitives (alongside subagents, sandboxes, tool use)
