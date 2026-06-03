# Dossier — AI Agents

> Living topic file. Updated on every REFRESH. Cross-references the evidence trail in `knowledge/`.
>
> **Canonical synthesis pointer:** [`wiki/articles/2026-agentic-frontier.md`](../wiki/articles/2026-agentic-frontier.md) — cross-vendor long-form synthesis. Update that article on deltas that span both this dossier and `frontier_ai.md`.

## Why this topic matters to Andre

Andre runs a 6-agent stack. Agent architecture is the spine — orchestration, tool use, multi-agent patterns, memory, eval, safety. Every release, RFC, and postmortem in this lane directly shapes how his agents should be built, audited, and evolved.

## Current signal (last refresh: 2026-06-02 21:50 CT)

**The 2026 frontier has moved from "smarter models" to "agentic capability on top of the model."** Every major lab shipped agent-runtime primitives in May–June 2026:

1. **LangChain 1.0 + LangGraph 1.0 GA** (Oct 22, 2025) is now the de facto standard. `create_agent` is the new entry point, `AgentExecutor` is deprecated, middleware (HITL, summarization, PII redaction) is the customization surface, and LangGraph is the durable-execution runtime. 90M monthly downloads; used in production at Uber, LinkedIn, Klarna, Rippling, JP Morgan, Blackrock, Cisco. (clm-2026-06-02-004)

2. **Anthropic shipped two production-grade agent runtimes in one month:** Dynamic Workflows in Claude Code (May 28) — runs hundreds of parallel subagents in a single session — and Claude Managed Agents (May 12) — Dreaming (memory curation), Multiagent Orchestration, Outcomes (rubric-graded, +10pt task success on hardest problems), Webhooks, Self-hosted Sandboxes (Cloudflare/Daytona/Modal/Vercel), MCP tunnels. (clm-2026-06-02-003)

3. **Letta Code** (Dec 16, 2025) is the #1 model-agnostic OSS harness on Terminal-Bench, comparable to provider-specific harnesses. Memory-first architecture: `/init` for memory, `/remember` for skill learning, skills as .md files in git, Conversations API for shared agent memory, Context Repositories (git-based memory) and Context Constitution (Apr 2, 2026). (fnd-2026-06-02-007, fnd-2026-06-02-008)

4. **Google Antigravity 2.0** (I/O 2026, May 19) is the third major entry into the agent-runtime space — projects, scheduled tasks, subagents, slash commands, agent-first development platform for Gemini 3.5. (fnd-2026-06-02-020)

5. **deepagents v0.4 → v0.5** (Feb → Apr 2026): pluggable sandbox, async subagents, multi-modal support, Anthropic prompt caching improvements, ContextHubBackend (LangSmith Hub). (fnd-2026-06-02-006)

6. **LangSmith Fleet** (renamed from Agent Builder, Mar 2026) — agent identity, sharing, permissions. Polly GA. LangSmith Sandboxes (Private Preview). (fnd-2026-06-02-005)

7. **Production maturity:** 57% of orgs have agents in production. Quality is the top production killer (32%); cost concerns dropped YoY. 89% have observability; 62% detailed tracing. 75%+ use multiple models — model diversity is the norm. (fnd-2026-06-02-009)

8. **Persistent memory is the active research frontier** with no clear winner: Letta/MemGPT, Mem0, Zep, Cognee. arXiv surveys (Du 2026; 47-author Hu 2025) confirm no canonical solution. MemoryArena exposes a deep gap — models near-perfect on LoCoMo plummet to 40-60% on multi-session decision tasks. (clm-2026-06-02-005)

9. **Persistent memory introduces a novel security class** that prompt-injection defenses do not cover. InjecMEM (Tian 2026) achieves 61.4% retrieval success + 76.6% conditional attack success. eTAMP (Zou 2026) shows environmental-observation poisoning across sessions. (clm-2026-06-02-006; *single-source verification at the rubric boundary — see re-verification watch*)

10. **Production-tested framework ranking** (Alice Labs + nxcode): LangGraph #1 for stateful workflows; Claude Agent SDK #2 (Anthropic-native, powers Claude Code); CrewAI #3 (45.9K stars, native MCP+A2A, 12M+ daily agent executions); AutoGen/AG2 #4; Semantic Kernel #5 (.NET). (fnd-2026-06-02-029)

## Source trail

See `knowledge/sources.jsonl`. Key primary sources for this dossier:
- `src-2026-06-02-003` LangChain 1.0 GA blog (langchain.com) — weight 0.9
- `src-2026-06-02-004` Letta Code blog (letta.com) — weight 0.9
- `src-2026-06-02-006` LangChain changelog — weight 0.9
- `src-2026-06-02-007` LangChain March 2026 newsletter — weight 0.9
- `src-2026-06-02-009` Anthropic Managed Agents (Code w/ Claude SF recap) — weight 0.9
- `src-2026-06-02-013` Releasebot Anthropic release log — weight 0.7 (secondary corroboration)
- `src-2026-06-02-015` LangChain State of Agent Engineering — weight 0.85
- `src-2026-06-02-017` arXiv Du 2026 memory survey — weight 0.85
- `src-2026-06-02-018` arXiv Mnemonic Sovereignty survey — weight 0.85

## Contradictions and open questions

- **GPT-6 rumor (fnd-2026-06-02-026)**: SEO source geo.fkw.com claims OpenAI released GPT-6 on Apr 14, 2026 with 2M context. Contradicted by OpenAI's own research index (src-2026-06-02-002) which shows GPT-5.5 as current frontier. Routed to verification queue. **Do not act on.**
- **Anthropic "Mythos"** mentioned in sources.news Substack but not corroborated in any Anthropic primary source as of June 2, 2026. Watch item.
- **Anthropic acquired "Versept"** mentioned in a YouTube transcript (per Linas Substack coverage of Claude 5 preview). Not corroborated. Watch item.
- **Open question — workload-shaped vs framework-shaped:** AI SDK 6 vs LangChain 1.0 — the 2026 decision is workload-shaped, not framework-shaped. (src-2026-06-02-014) Andre's stack runs on the Hermes orchestrator + worker pool. Does Hermes currently sit closer to AI SDK (chat surface) or LangGraph (graph surface) or Managed Agents (autonomous long-running)? Worth a follow-up question.
- **Open question — Andre's interest profile on persistent memory:** Andre's stack runs gbrain, Honcho, OpenClaw. Letta is the academic-grade option, Mem0 is the fastest path, Zep is the temporal KG, Cognee is the knowledge graph. Which one (if any) is closest to what gbrain actually is? This is exactly the question Mavis would ask — but she has not yet.
- **Re-verification watch — clm-2026-06-02-006 (persistent memory security):** promoted to `verified=true` on 2026-06-03 via a single primary source (src-2026-06-02-018, arXiv 2604.16548) at the rubric boundary. The dossier prose asserted this as fact on 2026-06-02 before the verification was recorded; vrf-handoff-2026-06-03-001 closed the gap. Flagged for a second-source cross-check on the next REFRESH — do not silently down-weight, the underlying claim is correct, but a second primary (e.g. InjecMEM/eTAMP/SpAIware/Nasr 2025 paper trail) would lift `cross_source_agreement` and remove the boundary flag.

## Implications

- **Build:** clm-2026-06-02-003 (Anthropic Managed Agents) is buildable, verified, ready to route to Hermes. Concrete implications: Andre's workers can be retrofitted to use Outcomes (rubric-graded task success) without rewriting the agent loop. Mid-priority for Hermes handoff.
- **Build:** [clm-2026-06-02-001 (GPT-5.5 frontier)](../dossiers/frontier_ai.md) — workers should default to `gpt-5.5` for high-stakes Codex tasks where Terminal-Bench / GDPval gains matter. Migration path: gpt-5.5 API ships "very soon" per OpenAI's Apr 24 update; Andre should hold Codex defaults at 5.4 until 5.5 API is live, then flip.
- **Content:** Content framing is unblocked. Five claims now cross the `weight ≥ 0.7` AND `verified: true` bar (as of 2026-06-03). Pre-existing: clm-2026-06-02-002 (0.8, agentic frontier shift) and clm-2026-06-02-003 (0.85, Anthropic Managed Agents) — verified 2026-06-02. Promoted by vrf-handoff-2026-06-03-001: clm-2026-06-02-004 (0.75, LangChain/LangGraph 1.0 standard), clm-2026-06-02-005 (0.7, persistent memory frontier), clm-2026-06-02-006 (0.7, memory security — single-source at boundary, draft with the re-verification watch caveat). Strongest single-claim framing candidate: clm-2026-06-02-003 (Anthropic Managed Agents, +10pt task success claim). Replaces the 2026-06-02 framing that no claim had crossed the bar.
- **Watch:** Anthropic Mythos, Anthropic Versept acquisition, GPT-5.6 canary, Daybreak (OpenAI cyber). All routed to watch-handoff.
- **Verify:** fnd-2026-06-02-026 (GPT-6 rumor) routed to verification-review.

## Routing history

| Date | Routed to | Item | Outcome |
|------|-----------|------|---------|
| 2026-06-02 | queue/hermes-handoff.md | hms-handoff-2026-06-02-001 (Anthropic Managed Agents adoption) | Awaiting Hermes consumption |
| 2026-06-02 | queue/hermes-handoff.md | hms-handoff-2026-06-02-002 (GPT-5.5 default flip on Codex) | Awaiting Hermes consumption |
| 2026-06-02 | queue/verification-review.md | clm-2026-06-02-026 (GPT-6 rumor) | Awaiting Mavis triage |
| 2026-06-02 | queue/watch-handoff.md | wch-handoff-2026-06-02-001 (Mythos, Versept, GPT-5.6 canary, Daybreak) | Awaiting Andre consumption |
| 2026-06-02 | queue/mavis-handoff.md | priority_alert (run receipt as source trail) | Awaiting Mavis consumption |

---

*This dossier is durable. It accumulates. It is the difference between "the agent said something" and "the system can inspect what it believes."*
