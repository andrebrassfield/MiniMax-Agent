# Dossier — Harness Engineering

> Living topic file. Built 2026-06-04 for the vault knowledge base buildout. The canonical reference for the agent harness pattern — the orchestration loop, tools, memory, context management, prompt construction, output parsing, state, errors, guardrails, verification, subagent orchestration, and lifecycle. Maps directly onto [`02 Notes/patterns/agent-harness.md`](../../02%20Notes/patterns/agent-harness.md) (Andre's internal pattern capture) and serves as the *external source trail* that justifies it.
>
> **Cross-references:** [`dossiers/ai-landscape.md`](ai-landscape.md) for the model layer the harness wraps · [`dossiers/ai_agents.md`](ai_agents.md) for production-tested framework ranking · [`dossiers/agent-engineering.md`](agent-engineering.md) for production memory/state/tool patterns · [`dossiers/mcps.md`](mcps.md) for the MCP server surface · [`dossiers/skills.md`](skills.md) for the Mavis/Anthropic/OpenAI skill catalogs.

## Why this topic matters to Andre

Andre runs a 6-agent fleet. Every agent — Mavis, Researcher, Verifier, Builder, Scribe, Designer — is a harness wrapping a model. The harness is the OS the model runs on. When a subagent fails, when a dossier is wrong, when a context window overflows, when a tool call hangs, when verification gets bypassed — the failure lives in the *harness*, not the model. Understanding the harness pattern at the canonical level (Anthropic, OpenAI, LangChain, LangGraph, deepagents, Codex) is the prerequisite for understanding, debugging, and improving the fleet.

## Current signal (as of 2026-06-04 02:25 CT)

### 1. The canonical definition

**"If you're not the model, you're the harness."** — Vivek Trivedy, LangChain. (src-2026-06-04-035)

The harness is the complete software infrastructure wrapping an LLM: orchestration loop, tools, memory, context management, prompt construction, output parsing, state persistence, error handling, guardrails, verification loops, subagent orchestration, and lifecycle/scaffolding management. Twelve components. One shape. The Anthropic Claude Code harness, the OpenAI Codex harness, the LangChain/LangGraph harness, the LangChain deepagents harness — all converge on the same pattern.

### 2. The 12 components (the canonical checklist)

From Akshay Pachaar's "The Anatomy of an Agent Harness" (Aug 2025, X long-form article) — which became the canonical reference and the basis for Andre's internal pattern capture. Cross-referenced against LangChain 1.0 docs, Claude Agent SDK docs, and Addy Osmani's "Agent Harness Engineering" (Jun 2025, addyosmani.com). (src-2026-06-04-035, src-2026-06-04-036, src-2026-06-04-037, src-2026-06-04-038)

1. **Orchestration Loop** — the ReAct / Thought-Action-Observation heartbeat. The model sees context → produces reasoning + tool call → harness executes → observation returned → loop. Per-turn in Claude Code, per-graph-step in LangGraph, per-async-task in deepagents.
2. **Tools** — schemas injected into context. JSON Schema function definitions. OpenAI function calling, Anthropic tool use, MCP servers (Model Context Protocol). The tool surface is the agent's "hands."
3. **Memory** — short-term (conversation history, in-context) + long-term (vault, MEMORY.md, topic files, vector DB). The 3-tier hierarchy: index (~150 chars, always loaded) → topic files (on demand) → raw transcripts (search only).
4. **Context Management** — context rot, Lost in the Middle, compaction, observation masking, JIT retrieval, subagent delegation. The discipline: as context grows, the model's effective intelligence decays. Subagent isolation is the canonical answer.
5. **Prompt Construction** — hierarchical, priority-stacked. Codex: server-controlled system message > tool definitions > developer instructions > user instructions > conversation history. Each layer can override the layer below, in order.
6. **Output Parsing** — native tool calling (OpenAI function_calls, Anthropic tool_use blocks, MCP JSON-RPC). Structured outputs eliminate the parse-failure mode of regex on raw text.
7. **State Management** — typed dicts (LangGraph State), checkpointing (LangGraph checkpointer, deepagents file-system state), git commits as checkpoints, durable storage. The state is the single source of truth; the LLM is stateless.
8. **Error Handling** — 99% per-step × 10 steps = 90.4% end-to-end. Four error types: transient (retry with backoff), LLM-recoverable (return as ToolMessage), user-fixable (interrupt), unexpected (bubble up). Stripe pattern: cap retries at 2 before escalation.
9. **Guardrails and Safety** — three levels: input (prompt injection defense), output (PII redaction, content moderation), tool (path sandbox, network egress control). Tripwires vs soft warnings. Permission/decision split.
10. **Verification Loops** — rules-based (tests, linters, type checkers), visual (Playwright screenshots, browser-based checks), LLM-as-judge (subagent evaluates). Boris Cherny (Anthropic): 2-3x quality improvement. Verifier-as-separate-vantage is canonical.
11. **Subagent Orchestration** — Fork (byte-identical context copy), Teammate (file-based mailbox, queue.md), Worktree (own git branch, isolated state). Agents-as-tools vs handoffs vs parallel sub-agents.
12. **Lifecycle / Scaffolding Management** — when to remove complexity. The discipline: scaffolding is *temporary infrastructure* that should be *retired* as the model improves. Manus was rewritten 5 times in 6 months, each version removing harness complexity. Anthropic *deletes planning steps* from Claude Code's harness as new model versions internalize that capability.

### 3. The Von Neumann frame (Beren Millidge, 2023)

Millidge's "Scaffolded LLMs as natural language computers" (Apr 2023, beren.io) re-frames the harness as a von Neumann architecture: (src-2026-06-04-039, src-2026-06-04-040)

| Component | Computing analogy | Mavis's instantiation |
|---|---|---|
| The LLM | CPU | M3 (MiniMax-M3) — the only intelligence in the system |
| Context window | RAM | the active turn's working context (system prompt + tools + memory + history + current message) |
| External storage | Disk | Obsidian vault + git + MEMORY.md + topic files + scratchpad |
| Tools | Device drivers | OpenCode tools + MCP servers + 6 hard-constraint-gated capabilities |
| Harness | Operating system | OpenCode runtime + Mavis EA protocol + team delegation pattern |

The "OS metaphor" is durable. The harness is what the model *runs on*. We are OS-builders, not feature-builders. The arXiv paper "Building LLM Agents by Incorporating Insights from Computer Systems" (Apr 2025, arXiv:2504.04485) proposes the same structured framework — modular design, universal abstractions, separation of concerns.

### 4. The seven decisions (the architecture choices every harness must make)

From Pachaar's checklist, cross-referenced against LangChain 1.0, deepagents v0.4-v0.5, and Claude Agent SDK:

1. **Single-agent vs multi-agent.** Default: single. Multi only when tool overload > ~10 overlapping tools OR clearly separate task domains. Mavis's fleet: task-domain split (EA + 5 specialists), not tool-overload split.
2. **ReAct vs plan-and-execute.** ReAct interleaves reasoning and action. Plan-and-execute separates them. LLMCompiler achieves 3.6x speedup over sequential ReAct by parallelizing independent tool calls. Mavis's split: plan-and-execute at the EA level, ReAct at the per-turn level.
3. **Context window management.** Five production approaches: time-based clearing, conversation summarization, observation masking, structured note-taking, sub-agent delegation. ACON (Agent Context Optimization): 26-54% token reduction with 95%+ accuracy. Mavis's split: sub-agent delegation + topic files.
4. **Verification loop design.** Computational (deterministic — tests, linters, type checkers) vs inferential (semantic — LLM-as-judge). Hybrid wins. Boris Cherny's 2-3x quality improvement comes from the inferential layer. Mavis's split: Verifier (LLM-as-judge) + 6 hard constraints (rules-based).
5. **Error handling strategy.** Retry caps (Stripe: 2), escalation paths, LLM-recoverable vs user-fixable classification. Mavis's split: escalation + spawn-and-await. The retry cap (2) is the open gap.
6. **Guardrail placement.** Input vs output vs tool. Tripwires vs soft warnings. Permission/decision split. Mavis's split: hard constraints (deterministic) + Verifier veto (semantic).
7. **Subagent orchestration model.** Fork (byte-identical, full context copy, expensive) vs Teammate (file-based mailbox, queue.md, cheap) vs Worktree (own git branch, isolated state, complex). Mavis's split: Teammate with file-based mailboxes (`mavis communication send --command spawn` + `queue/*.md`).

### 5. The harness is the product (the TerminalBench evidence)

LangChain jumped from outside top 30 to rank 5 on TerminalBench 2.0 by changing *only* the infrastructure wrapping their LLM. A separate research project (auto-harness optimization) hit 76.4% pass rate by having an LLM optimize the infrastructure itself, surpassing hand-designed systems. (src-2026-06-04-016, src-2026-06-04-035)

> "Two products using identical models can have wildly different performance based solely on harness design."

The harness is not a solved problem or a commodity layer. It's where the hard engineering lives: managing context as a scarce resource, designing verification loops that catch failures before they compound, building memory systems that provide continuity without hallucination, making architectural bets about how much scaffolding to build versus how much to leave to the model.

### 6. The canonical frameworks (June 2026)

| Framework | Type | Open source | Key feature | Adoption |
|---|---|---|---|---|
| **LangChain 1.0** (Oct 22, 2025 GA) | High-level abstractions | Yes (MIT) | `create_agent`, middleware hooks (HITL, summarization, PII redaction), langchain-core 1.0 with standardized content blocks | 90M monthly downloads, used by Uber/LinkedIn/Klarna/Rippling/JPMorgan/Blackrock/Cisco |
| **LangGraph 1.0** (Oct 22, 2025 GA) | Stateful graph runtime | Yes (MIT) | Built on LangGraph runtime, durable state, built-in persistence, first-class HITL, InMemorySaver, Postgres checkpointer | Powers create_agent; production at LinkedIn/Uber/Klarna/GitLab |
| **deepagents v0.4-v0.5** (Feb-Apr 2026, v0.6.1 current) | Battery-included harness | Yes (MIT) | Pluggable sandbox, async subagents (v0.5), Anthropic prompt caching, ContextHubBackend, AsyncSubAgent for non-blocking delegation | 8.8K stars, 1.4K forks (v0.5) |
| **Claude Agent SDK** (May 12, 2026 release, Anthropic) | Anthropic-native harness | Yes (MIT) | Powers Claude Code; in-process MCP servers, custom tools with input schemas, configurable permissions; Python and TypeScript | Powers Claude Code (production at Anthropic, hundreds of thousands of devs) |
| **Anthropic Managed Agents** (May 12, 2026) | Managed runtime | No (Anthropic-hosted) | Dreaming (memory curation), Multiagent Orchestration, Outcomes (rubric-graded, +10pt task success), Webhooks, Self-hosted Sandboxes (Cloudflare/Daytona/Modal/Vercel), MCP tunnels | Production at Anthropic, beta to enterprise |
| **Google Antigravity 2.0** (May 19, 2026, I/O) | Managed agent platform | No (Google-hosted) | Projects, scheduled tasks, subagents, slash commands, agent-first development platform; Antigravity CLI; built-in cross-platform terminal sandbox, credential masking, hardened Git policy | Free public preview for individuals on macOS/Windows/Linux |
| **OpenAI Codex + OpenAI on AWS** (Jun 1, 2026) | Hosted runtime | No (OpenAI) | GPT-5.5 in Codex; Responses API; 1M context; Bedrock preview for GPT-5.5/GPT-5.4; dynamic workflows in ChatGPT | Powers ChatGPT, Codex; 85% of OpenAI internal usage weekly |
| **Letta Code** (Dec 16, 2025) | Memory-first OSS harness | Yes (Apache 2.0) | #1 model-agnostic on TerminalBench; /init for memory, /remember for skill learning; .md files in git; Conversations API; Context Repositories (git-based memory) | Comparable to Claude Code/Gemini CLI on TerminalBench |
| **CrewAI** (v0.x, 2026) | Role-based multi-agent | Yes (MIT) | Native MCP + A2A; 45.9K stars; 12M+ daily agent executions | Production at multiple Fortune 500 |
| **AutoGen / AG2** (v0.4, 2026) | Microsoft Research multi-agent | Yes (MIT/Apache) | Conversable agents, group chat manager; v0.4 unifies AutoGen + AG2 | Production at Microsoft, multiple enterprises |
| **Smolagents** (Hugging Face, 2025) | Minimal agent | Yes (Apache 2.0) | Code-based tool calling, ~1000 LoC; minimal harness | Production at Hugging Face |
| **Semantic Kernel** (Microsoft, .NET) | Enterprise SDK | Yes (MIT) | Native .NET, function calling, planner, RAG; v1.x 2026 | Enterprise .NET shops |
| **AutoGPT** (Significant Gravitas, 2024-2026) | Autonomous loop | Yes (MIT) | Original autonomous agent; ~170K stars; less production-used but iconic | Reference for autonomous loops |

(src-2026-06-04-041, src-2026-06-04-042, src-2026-06-04-043, src-2026-06-04-044, src-2026-06-04-045, src-2026-06-04-046, src-2026-06-04-047, src-2026-06-04-048)

### 7. The Anthropic "Dynamic Workflows" and the Managed Agents shift (May 2026)

Anthropic shipped two production-grade agent runtimes within one month, marking a structural shift in how frontier labs approach the harness:

- **Dynamic Workflows in Claude Code (May 28, 2026).** Runs hundreds of parallel subagents in a single session. The harness's subagent orchestration component (component 11) becomes the primary surface, not the orchestration loop.
- **Claude Managed Agents (May 12, 2026).** Dreaming (memory curation — the model writes its own memory blocks based on user feedback), Multiagent Orchestration, Outcomes (rubric-graded task success, +10pt on hardest problems), Webhooks, Self-hosted Sandboxes (Cloudflare/Daytona/Modal/Vercel), MCP tunnels. The harness moves from "developer-written" to "Anthropic-hosted."

This is the harness-as-a-service shift. Andre's fleet (self-hosted via Mavis + OpenCode) sits orthogonal to this — we're building our own harness for sovereignty, verification, and the EA model. But the patterns Anthropic surfaces (Dreaming, Outcomes) are worth studying for adoption.

### 8. The Mavis-specific position (the seven decisions applied)

From [`02 Notes/patterns/agent-harness.md`](../../02%20Notes/patterns/agent-harness.md) § "Mavis's position on the seven decisions" — already captured, this dossier just verifies against the canonical external sources:

| Decision | Our choice | Canonical parallel |
|---|---|---|
| 1. Single vs multi | Multi-agent (6 specialists) | Task-domain split (Pachaar, deepagents) — NOT tool-overload split |
| 2. ReAct vs plan-and-execute | Hybrid | Plan-and-execute at EA level, ReAct at per-turn level (LLMCompiler pattern) |
| 3. Context management | Sub-agent delegation + topic files | The 3-tier hierarchy (index/topic files/raw) is canonical; ACON's 26-54% token reduction is the ceiling |
| 4. Verification | Hybrid | LLM-as-judge (inferential) + hard constraints (computational). Boris Cherny's 2-3x is the case for the Verifier |
| 5. Error handling | Escalation + spawn-and-await | Stripe pattern (cap retries at 2) — **gap, not yet codified** |
| 6. Guardrails | Hard constraints + Verifier veto | 6 hard constraints (no deploy, no push, no other-vault touch, no external sends, no destructive ops without approval, no spec-block execution) |
| 7. Subagent orchestration | Teammate model with file-based mailboxes | `mavis communication send --command spawn` + `queue/*.md` = Teammate. Not Fork (no full context copy), not Worktree (no per-agent git branch) |

### 9. The Scaffolding Metaphor (the meta-principle)

> Construction scaffolding is temporary infrastructure that enables workers to build a structure they couldn't reach otherwise. Doesn't do the construction. But without it, workers can't reach the upper floors. *Scaffolding is removed when the building is complete.*

Manus was rebuilt 5 times in 6 months. Each rewrite removed complexity. "Complex tool definitions became general shell execution. Management agents became simple structured handoffs." (src-2026-06-04-035)

**Implications for the fleet:**

- Every specialist agent is *scaffolding for a stage of construction*. The Researcher is scaffolding for the capture phase. The Designer (proposed) is scaffolding for the rendering phase. The Runtime-Ops (proposed) is scaffolding for the loop-audit phase.
- Scaffolding should be *removable*. As the model improves, scaffolding should *retire*, not accumulate.
- The future-proofing test: *will this role still be necessary in M5, M6, M7?* If not, appropriate scaffolding. If yes, permanent organ.

**The future-proofing test (applied to each fleet member):**

- **Verifier** — will LLM-as-judge stay necessary, or will better models self-verify? **Probably stays** (verification has 2-3x ROI even on frontier models). Real organ.
- **Researcher** — will research need a separate context window in M5? **Probably yes** (research involves external sources the chief context shouldn't carry). Real organ.
- **Scribe** — will content generation internalize as the model improves? **Possibly no**. Real organ, but the form may change.
- **Designer (proposed)** — will visual decisions stay necessary as a separate vantage? **Possibly no**. May be removable scaffolding.
- **Builder** — will code generation internalize? **Probably stays** (code has 99% × 10 = 90.4% compounding floor; verification is non-negotiable). Real organ.

### 10. The co-evolution warning

> Models are post-trained with specific harnesses in the loop. Claude Code's model learned to use the specific harness it was trained with. Changing tool implementations can degrade performance because of this tight coupling.

When we change the harness (add an agent, change a tool, restructure the queues), the model may need to re-learn the new shape. Practical implications:

- **Version the harness and the model together.** Don't make harness changes without a corresponding model-context update.
- **When adding an agent, update the EA system prompt with the new role.** The model will pick it up implicitly.
- **Document the harness as a load-bearing surface** for the model's expected behavior.

### 11. Tool Scoping Strategy (the counterintuitive finding)

> More tools often means *worse* performance.

- **Vercel removed 80% of tools from v0 and got better results.**
- **Claude Code achieves 95% context reduction via lazy loading.**
- *The principle:* expose the minimum tool set needed for the current step.

The Mavis tool audit: the 6 hard-constrained native tools (Read, Write, Edit, Bash, Grep, Glob) plus MCP servers (matrix, obsidian, codegraph, kanban, supabase, playwright, cu, hf-vision, etc.) are all loaded into context. Lazy-load candidates: matrix MCP (only for media work), kanban MCP (only when explicitly interfacing), cu MCP (only for desktop automation), supabase (only when querying). The obsidian MCP should always be available. **This is an audit, not a removal — measure first.**

### 12. Harness Thickness

> How much logic lives in the harness versus the model.

- **Anthropic bets on thin harnesses + model improvement.** They regularly *delete planning steps* from Claude Code's harness as new model versions internalize that capability.
- **Graph-based frameworks** (LangGraph, CrewAI Flows) bet on *explicit control* — keep the logic in the graph, even if the model could do it.

The bias: **when in doubt, build thinner**. The model's capability grows; the harness's complexity should *not*.

**Mavis's thickness check:** the team delegation pattern (EA + 5 specialists) is a *thicker* harness than a single-agent approach. The bet is that vantage separation earns its place. Apply the future-proofing test to each specialist on every eval cycle.

### 13. Guides vs Sensors (Martin Fowler, Thoughtworks)

Production harnesses use *both*:

- **Guides** — feedforward, steer *before* action. The model reasons about what to do, then acts. Lives in the prompt and the planning step.
- **Sensors** — feedback, observe *after* action. The harness measures what happened, then routes. Lives in the verification loops and the error handling.

**Mavis's split:** the system prompt is mostly guides (the four workflows, the hard constraints, the EA tone). The Verifier is mostly a sensor. The cron self-reminders and the daily-note handoffs are sensors too.

### 14. Permission and Safety Architecture

- **Permissive** — fast but risky, auto-approve most actions
- **Restrictive** — safe but slow, require approval for each action

Mavis is *restrictive* on the 6 hard constraints and *permissive* within those constraints. The Verifier adds an inferential sensor layer on top of the deterministic rules.

## Source trail

See `knowledge/sources.jsonl`. Key primary sources for this dossier (all fetched 2026-06-04 02:00-02:25 CT):

- `src-2026-06-04-035` Akshay Pachaar: "The Anatomy of an Agent Harness" (x.com long-form) — weight 0.95
- `src-2026-06-04-036` Addy Osmani: "Agent Harness Engineering" (addyosmani.com) — weight 0.9
- `src-2026-06-04-037` Aakash Gupta: "2025 Was Agents. 2026 Is Agent Harnesses." (medium) — weight 0.8 (secondary)
- `src-2026-06-04-038` Beren Millidge: "Scaffolded LLMs as natural language computers" (beren.io, 2023) — weight 0.9
- `src-2026-06-04-039` arXiv:2504.04485 "Building LLM Agents by Incorporating Insights from Computer Systems" — weight 0.85
- `src-2026-06-04-040` arXiv:2507.11633 "General Modular Harness for LLM Agents in Multi-Turn Gaming Environments" — weight 0.85
- `src-2026-06-04-041` LangChain: "LangChain and LangGraph 1.0" (langchain.com/blog) — weight 0.9
- `src-2026-06-04-042` LangChain: Middleware overview (docs.langchain.com) — weight 0.95
- `src-2026-06-04-043` LangChain: Deep Agents v0.4 changelog — weight 0.9
- `src-2026-06-04-044` LangChain: Deep Agents v0.5 (async subagents) — weight 0.9
- `src-2026-06-04-045` GitHub: langchain-ai/deepagents (batteries-included harness) — weight 0.9
- `src-2026-06-04-046` GitHub: langchain-ai/langgraph README (stateful multi-actor) — weight 0.9
- `src-2026-06-04-047` GitHub: anthropics/claude-agent-sdk-python (in-process MCP servers) — weight 0.9
- `src-2026-06-04-048` Claude Code Docs: Agent SDK overview (code.claude.com) — weight 0.9
- `src-2026-06-04-049` Anthropic: "Introducing Claude Managed Agents" (Code w/ Claude SF, May 12) — weight 0.9
- `src-2026-06-04-050` Google: I/O 2026 developer highlights (blog.google) — weight 0.9
- `src-2026-06-04-051` Promptfoo: Claude Agent SDK provider docs (promptfoo.dev) — weight 0.85
- `src-2026-06-04-052` MongoDB: "The Agent Harness: Why the LLM Is the Smallest Part" (medium) — weight 0.8
- `src-2026-06-04-053` Reddit: "I built an OS kernel for LLM agents in 500 lines of Python" (r/AI_Agents) — weight 0.7 (community)
- `src-2026-06-04-054` Microsoft: Semantic Kernel docs — weight 0.85
- `src-2026-06-04-055` Hugging Face: smolagents docs (huggingface.co/docs/smolagents) — weight 0.9
- `src-2026-06-04-056` LangChain Forum: How to use LangChain v1.x middleware in LangGraph — weight 0.8
- `src-2026-06-04-057` CSDN: LangChain Deep Agents v0.5 async subagents deep-dive — weight 0.75
- `src-2026-06-04-058` Tencent News: Deep Agents v0.4 + v0.5 release summary (news.qq.com) — weight 0.8
- `src-2026-06-04-059` hidekazu-konishi.com: MCP Server Ecosystem Reference 2026 — weight 0.8
- `src-2026-06-04-060` LocalLLaMA: MiniMax M2.7 announcement (r/LocalLLaMA) — weight 0.7 (community, no primary)
- `src-2026-06-04-061` X: Akshay Pachaar thread on harness anatomy (x.com) — weight 0.9
- `src-2026-06-04-062` Reddit: Anyone seen a deep agent architecture actually running in production — weight 0.7
- `src-2026-06-04-063` LinkedIn: Akshay Pachaar — Agent Harness Explained — weight 0.7
- `src-2026-06-04-064` LangChain blog: Building LangChain and LangGraph 1.0 (YouTube transcript) — weight 0.8
- `src-2026-06-04-065` LangChain Reddit: Agent Middleware in 1.0 alpha (r/LangChain) — weight 0.7
- `src-2026-06-04-066` arXiv:2508.20148 "The Anatomy of a Personal Health Agent" (Apple/Google/UW) — weight 0.85

## Contradictions and open questions

- **Anthropic Managed Agents vs self-hosted harness:** Anthropic's May 12 release pushes the harness-as-managed-service model (Dreaming, Outcomes, MCP tunnels). The open-source / self-hosted story (LangChain, deepagents, Letta, Smolagents) continues to grow. **Open question for Andre's fleet:** does the fleet adopt Managed Agents for production workloads (outcomes rubric, dreaming memory) or stay self-hosted for sovereignty/audit/verification? Likely hybrid: Managed Agents for non-frontier workers, self-hosted for the Verifier and the EA.
- **LangGraph vs deepagents vs raw LangChain:** The community is split. LangGraph users want explicit control (the graph is the source of truth). deepagents users want opinionated defaults (batteries included). raw LangChain users want neither (DIY). **Mavis's position:** deepagents-shaped (batteries-included for the worker pool) with the EA pattern overlaying it. Worth re-validating against the v0.5 async subagent story.
- **deepagents v0.6.1 middleware bug:** Per community report (CSDN, May 18, 2026), `SummarizationMiddleware` throws "duplicate middleware instances" error in v0.6.1. Workaround: pin to v0.5.1. **Watch for fix in next release.**
- **The "more tools = worse performance" principle is counterintuitive.** Vercel removed 80% of tools from v0; Claude Code achieves 95% context reduction via lazy loading. This argues for a *small, focused* tool surface per specialist. **Mavis's tool audit is overdue.** The current 6 native + 8 MCP servers is *wide*, not *focused*. The next eval cycle should measure: (a) which tools are actually used, (b) what the token cost of loading them all is, (c) whether lazy-loading the rarely-used ones improves performance.
- **Open question — the retry cap (Stripe pattern, gap 8 in agent-harness.md):** The Verifier + escalation + spawn-and-await pattern is the *spirit* of the Stripe retry cap, but the explicit "max 2 retries" cap is not codified. Worth a follow-up: define a 3-strikes rule (2 retries + 1 escalation) at the next agent.md revision.
- **Re-verification watch — subagent orchestration in production (Pachaar + deepagents claim):** The "hundreds of parallel subagents in a single session" claim (Anthropic Dynamic Workflows, May 28) and the AsyncSubAgent pattern (deepagents v0.5) are both new in May 2026. **No independent production case study yet** of these at scale beyond the lab demos. Marked for a 90-day re-verification on 2026-09-04.

## Implications

- **Build:** the Mavis tool audit (lazy-load matrix, kanban, cu, supabase) is overdue. The token cost of loading 8 MCP servers + 6 native tools is non-trivial. Recommend the Builder run the audit (per-worker tool usage, per-MCP token cost) in the next 2 weeks. Mid-priority for Hermes.
- **Build:** adopt the Stripe retry cap (2 retries + 1 escalation) as a Mavis-wide convention. Codify in `agent.md` on next revision. Low-effort, structural improvement.
- **Build:** evaluate Managed Agents (Anthropic, May 12) for the Scribe or Builder (the workers where rubric-graded Outcomes and Dreaming memory are highest-leverage). Not for the Verifier (must be self-hosted for audit reasons). Low-priority.
- **Content:** the "harness is the product" thesis (TerminalBench evidence) is the strongest available frame for the daily brief. The dossier above is the canonical reference.
- **Watch:** deepagents v0.6+ (the v0.6.1 middleware bug fix), LangGraph 1.1+, Letta Code app (Apr 6, 2026), Codex Runtime upgrades, LangSmith Fleet (renamed from Agent Builder, Mar 2026).
- **Verify:** the "Dynamic Workflows runs hundreds of parallel subagents" claim is single-source (Anthropic blog, May 28). Cross-check on 90-day cadence against production case studies.

## Routing history

| Date | Routed to | Item | Outcome |
|------|-----------|------|---------|
| 2026-06-04 | queue/mavis-handoff.md | dossier ready | Pending |
| 2026-06-04 | knowledge/sources.jsonl | src-2026-06-04-035 through src-2026-06-04-066 | Appended |
| 2026-06-04 | Cross-ref: 02 Notes/patterns/agent-harness.md | dossier is the external source trail for the internal pattern | Internal pattern capture already exists |

---

*This dossier is the external source trail for the internal pattern capture. When the Verifier audits a subagent's failure, this is the file to consult first: which of the 12 components is broken? When the Builder implements a new specialist, this is the file to consult: which of the 7 decisions need to be made?*
