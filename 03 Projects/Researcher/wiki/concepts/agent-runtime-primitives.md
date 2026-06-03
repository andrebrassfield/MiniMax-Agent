# Concept — Agent Runtime Primitives

**Type:** design pattern family
**First seen in vault:** 2026-06-02
**Dossier:** ai_agents
**Status:** converging on a shared vocabulary across vendors

## Definition

The set of platform-level capabilities that turn a model into a production-grade agent runtime. As of June 2, 2026, the vendor landscape has converged on a recognizable vocabulary: subagent orchestration, durable execution, sandboxed tool execution, memory curation, rubric-graded outcomes, and webhooks for async completion.

## The vocabulary (cross-vendor)

| Primitive | What it is | Where it shipped |
|-----------|-----------|-----------------|
| **Subagent orchestration** | Lead agent delegates to specialist subagents in parallel; traceable | Anthropic Managed Agents (May 12, 2026); LangGraph Send API; Google Antigravity 2.0 |
| **Dynamic / parallel workflows** | Model plans and runs tens to hundreds of subagents in a single session | Anthropic Dynamic Workflows (May 28, 2026) in Claude Code |
| **Durable execution** | State persists across restarts; resumable from any checkpoint | LangGraph 1.0 (Oct 22, 2025); Managed Agents (built-in) |
| **Sandboxed tool execution** | Code runs in customer's perimeter, not vendor's | Anthropic Self-hosted Sandboxes (May 26, 2026) — Cloudflare/Daytona/Modal/Vercel |
| **Memory curation ("dreaming")** | Scheduled process reviews past sessions, extracts patterns, curates memory | Anthropic Dreaming (May 12, 2026); Letta Context Constitution (Apr 2, 2026) |
| **Rubric-graded outcomes** | Developer-defined rubric; separate grader context; agent revises until bar met | Anthropic Outcomes (May 12, 2026) — +10pt task success on hardest problems per Anthropic |
| **Async completion webhooks** | Notify when an outcome is met, without polling | Anthropic Webhooks (May 12, 2026) |
| **Fast mode** | Higher output tokens/sec at higher $/token | Anthropic Opus 4.8 Fast Mode (May 28, 2026): 2.5x tokens/sec at 3x cost |
| **Mid-conversation system messages** | Inject role: system messages mid-conversation, preserving prompt cache | Anthropic Opus 4.8 (May 28, 2026) |

## Why it matters

Andre's Hermes orchestrator + worker pool pattern maps onto this vocabulary. Specifically: Hermes workers already do subagent orchestration, durable execution, and webhook notification. Where Andre's stack currently lags the frontier is in rubric-graded outcomes, memory curation, and self-hosted sandboxing. clm-2026-06-02-003 in `dossiers/ai_agents.md` is the buildable claim — the Managed Agents primitives are ready to retrofit onto Hermes workers.

## Source trail

- src-2026-06-02-008 (Anthropic Dynamic Workflows)
- src-2026-06-02-009 (Anthropic Managed Agents)
- src-2026-06-02-003 (LangChain 1.0 + LangGraph 1.0)
- src-2026-06-02-020 (Google Antigravity 2.0)

## Related concepts

- [[Agentic Memory Architectures]] — memory is one primitive in this vocabulary
- [[Subquadratic Attention]] — the model-layer primitive that competes with the runtime-layer primitives on long-context workloads
