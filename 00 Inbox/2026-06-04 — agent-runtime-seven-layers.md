---
captured: 2026-06-04 01:13 CT
source: Andre (Telegram, message_id 1416)
type: spec-block
tags: [capture, agent-architecture, runtime, tool-layer, memory, context, prompt, state, error, mavis-design]
status: unprocessed
---

# Agent Runtime — Seven-Layer Decomposition (Andre's spec)

> Raw capture from Andre's Telegram message. He sent this as a spec block — not a directive. Apply CHIEF discipline: sharpen to one sentence, end with a question, surface the gap to our work.

## Verbatim

The tool layer handles registration, schema validation, argument extraction, sandboxed execution, result capture, and formatting results back into LLM-readable observations.

Claude Code provides tools across six categories: file operations, search, execution, web access, code intelligence, and subagent spawning. OpenAI's Agents SDK supports function tools (via @function_tool), hosted tools (WebSearch, CodeInterpreter, FileSearch), and MCP server tools.

3. Memory
Memory operates at multiple timescales. Short-term memory is conversation history within a single session. Long-term memory persists across sessions: Anthropic uses CLAUDE.md project files and auto-generated MEMORY.md files; LangGraph uses namespace-organized JSON Stores; OpenAI supports Sessions backed by SQLite or Redis.

Claude Code implements a three-tier hierarchy: a lightweight index (~150 characters per entry, always loaded), detailed topic files pulled in on demand, and raw transcripts accessed via search only. A critical design principle: the agent treats its own memory as a "hint" and verifies against actual state before acting.

4. Context Management
This is where many agents fail silently. The core problem is context rot: model performance degrades 30%+ when key content falls in mid-window positions (Chroma research, corroborated by Stanford's "Lost in the Middle" finding). Even million-token windows suffer from instruction-following degradation as context grows.

Production strategies include:
- Compaction: summarizing conversation history when approaching limits (Claude Code preserves architectural decisions and unresolved bugs while discarding redundant tool outputs)
- Observation masking: JetBrains' Junie hides old tool outputs while keeping tool calls visible
- Just-in-time retrieval: maintaining lightweight identifiers and loading data dynamically (Claude Code uses grep, glob, head, tail rather than loading full files)
- Sub-agent delegation: each subagent explores extensively but returns only 1,000 to 2,000 token condensed summaries

Anthropic's context engineering guide states the goal: find the smallest possible set of high-signal tokens that maximize likelihood of the desired outcome.

5. Prompt Construction
This assembles what the model actually sees at each step. It's hierarchical: system prompt, tool definitions, memory files, conversation history, and the current user message.

OpenAI's Codex uses a strict priority stack: server-controlled system message (highest priority), tool definitions, developer instructions, user instructions (cascading AGENTS.md files, 32 KiB limit), then conversation history.

6. Output Parsing
Modern harnesses rely on native tool calling, where the model returns structured tool_calls objects rather than free-text that must be parsed. The harness checks: are there tool calls? Execute them and loop. No tool calls? That's the final answer.

For structured outputs, both OpenAI and LangChain support schema-constrained responses via Pydantic models. Legacy approaches like RetryWithErrorOutputParser (which feeds the original prompt, the failed completion, and the parsing error back to the model) remain available for edge cases.

7. State Management
LangGraph models state as typed dictionaries flowing through graph nodes, with reducers merging updates. Checkpointing happens at super-step boundaries, enabling resume after interruptions and time-travel debugging. OpenAI offers four mutually exclusive strategies: application memory, SDK sessions, server-side Conversations API, or lightweight previous_response_id chaining. Claude Code takes a different approach: git commits as checkpoints and progress files as structured scratchpads.

8. Error Handling
Here's why this matters: a 10-step process with 99% per-step success still has only ~90.4% end-to-end success. Errors compound fast.

LangGraph distinguishes four error types: transient (retry with backoff), LLM-recoverable (return error as ToolMessage so the model can adjust), user-fixable (interrupt for human input), and unexpected (bubble up for debugging).

## Andre's framing (implicit)

Sent right after we discussed adding a Designer agent to the team. The "logical next agent" question was just answered with Designer. This spec is either:
- Background reading for the Designer proposal
- A reframe: "the gap isn't a missing agent role, it's a missing layer in the runtime"
- Material for Mavis-Apex-Architecture
- All three

## Where it lands in our work (Mavis processing)

| Andre's layer | Mavis's current implementation | Status |
|---|---|---|
| Tool layer | OpenCode native tools + MCP servers (matrix, obsidian, codegraph, etc.) | Done |
| Memory (3-tier) | MEMORY.md (index) + topic files (on demand) + raw transcripts (search only) | Done — matches Claude Code pattern exactly |
| Context Management | Compaction via model; sub-agent delegation via `mavis communication send`; just-in-time retrieval via Grep/Read | Done — natively benefits from M3's 1M context |
| Prompt Construction | System prompt (agent-context) + memory files + tool definitions + user message | Done |
| Output Parsing | Native tool calling via OpenCode | Done |
| State Management | Workspace + scratchpad + git (vault) + session continuity via mavis | Done — `git commits as checkpoints` is literally how the vault works |
| Error Handling | Verifier (trust) + my escalation pattern + spawn-and-await for async | Done — *but* the "99% per-step → 90% end-to-end" compounding is real and not currently surfaced |

## Sharpen to one sentence

> Andre's spec is a seven-layer decomposition of an agent runtime — tool layer, memory, context, prompt, output, state, error — with the throughline that *every layer is a context-engineering problem*, the goal being "the smallest possible set of high-signal tokens that maximize likelihood of the desired outcome."

## Surface the contradiction

Not a contradiction in the spec — a *tension* in our team. The Designer I just proposed operates on the *user-facing surface*. The seven layers operate on the *agent-facing runtime*. We might be answering two different questions:
- "Who designs the human-facing HTML?" → Designer
- "Who audits the agent-facing runtime for context rot, error compounding, and state drift?" → either Tester (operational) or a new **Runtime-Ops** agent (architectural)

## Open questions for the daily-brief pass

- Does Andre want this captured as a `02 Notes/patterns/agent-runtime-decomposition.md` permanent note, or kept as inbox for now?
- Does the spec argue *against* adding a Designer (because the gap is in the runtime, not the surface), or *for* adding Designer *and* a Runtime-Ops later?
- The 90.4% compounding line — should we have a session-level health metric that surfaces it?

---

## Continuation (message 1417, 01:15 CT)

> Andre appended the rest of the spec. Same conversation, same thread — this is the back half. Captured here for completeness.

### Section 8 (cont.) — Error handling discipline

Anthropic catches failures within tool handlers and returns them as error results to keep the loop running. Stripe's production harness caps retry attempts at two.

### Section 9 — Guardrails and Safety

OpenAI's SDK implements three levels: input guardrails (run on first agent), output guardrails (run on final output), and tool guardrails (run on every tool invocation). A "tripwire" mechanism halts the agent immediately when triggered.

Anthropic separates permission enforcement from model reasoning architecturally. The model decides what to attempt; the tool system decides what's allowed. Claude Code gates ~40 discrete tool capabilities independently, with three stages: trust establishment at project load, permission check before each tool call, and explicit user confirmation for high-risk operations.

### Section 10 — Verification Loops

This is what separates toy demos from production agents. Anthropic recommends three approaches: rules-based feedback (tests, linters, type checkers), visual feedback (screenshots via Playwright for UI tasks), and LLM-as-judge (a separate subagent evaluates output).

Boris Cherny, creator of Claude Code, noted that giving the model a way to verify its work improves quality by 2 to 3x.

### Section 11 — Subagent Orchestration

Claude Code supports three execution models: Fork (byte-identical copy of parent context), Teammate (separate terminal pane with file-based mailbox communication), and Worktree (own git worktree, isolated branch per agent). OpenAI's SDK supports agents-as-tools (specialist handles bounded subtask) and handoffs (specialist takes full control). LangGraph implements subagents as nested state graphs.

### The Loop in Motion — 7-step walkthrough

1. **Prompt Assembly:** system prompt + tool schemas + memory files + conversation history + current user message. Important context at beginning and end (Lost in the Middle).
2. **LLM Inference:** model generates text, tool calls, or both.
3. **Output Classification:** no tool calls = loop ends. tool calls = execute. handoff = update agent and restart.
4. **Tool Execution:** validate args, check perms, sandbox, capture. Read-only concurrent; mutating serial.
5. **Result Packaging:** format as LLM-readable. Errors caught and returned so the model can self-correct.
6. **Context Update:** append to history. If approaching limit, trigger compaction.
7. **Loop.**

**Termination conditions** (layered): no tool calls, max turn limit, token budget exhausted, guardrail tripwire, user interrupt, safety refusal. Simple question = 1-2 turns. Complex refactor = dozens of tool calls.

**Ralph Loop pattern** (Anthropic, long-running multi-context-window tasks): an **Initializer Agent** sets up the environment (init script, progress file, feature list, initial git commit), then a **Coding Agent** in every subsequent session reads git logs and progress files to orient itself, picks the highest-priority incomplete feature, works it, commits, writes summaries. The filesystem provides continuity across context windows.

### How Real Frameworks Implement the Pattern

Anthropic's Claude Agent SDK exposes the harness through a single `query()` function that creates the agentic loop and returns an async iterator streaming messages. The runtime is a "dumb loop." All intelligence lives in the model.

---

## Re-Sharpen (full spec, both messages)

> Andre's spec is a closed-loop agent harness where the runtime is "dumb" and *all intelligence lives in the model* — every layer (tools, memory, context, prompt, output, state, error, guardrails, verification, subagent) exists to keep the loop correct, the model informed, the user safe.

The single sharpest sentence in the spec: **"The runtime is a 'dumb loop.' All intelligence lives in the model."** That's the spine. Everything else is harness around the brain.

## Where the *new* half lands in our work

| Andre's section | Mavis's current implementation | Notes |
|---|---|---|
| 8. Error handling | Verifier + my escalation + spawn-and-await | Stripe's "cap retries at two" is a hard limit we don't have — I escalate on first error. Should we? |
| 9. Guardrails | My hard constraints (no deploy, no push, no other-vault touch); the EA protocol | Claude Code's 40 gated tools vs my ~6 hard constraints. The policy is correct; the surface is smaller. The tripwire pattern (halt on violation) is what `no destructive ops without approval` should formalize as. |
| 10. Verification loops | Verifier = LLM-as-judge. My hard constraints = rules-based. | **Boris Cherny: verification = 2-3x quality improvement.** This is the case for the Verifier being non-optional. Already true in our setup; the spec just externalizes why. |
| 11. Subagent orchestration | `mavis communication send --command spawn` is closest to OpenAI's "agents-as-tools" or Claude Code's "Worktree" | Not Fork (no full context copy) and not exactly Teammate (no file-based mailbox — we have mavis-handoff queues instead). **The Teammate model with `queue/*.md` files is what I just built with Researcher/Verifier.** We are the Teammate pattern. |
| The 7-step Loop | I run this loop every turn. The harness is OpenCode. | Prompts assembled from system prompt + agent-context + memory + tool definitions + user message. Output classified, tools executed, results packaged, context updated, loop. I am the loop. |
| Termination conditions | "No tool calls" = end of turn. Token budget = context window. User interrupt = new message. | I don't currently track "max turn limit" or "token budget exhausted" as deliberate termination conditions — they happen, but I don't surface them. |
| Ralph Loop | The Researcher's REFRESH mode is a near-perfect match: it reads prior vault state, picks highest-priority work, executes, writes run receipt, commits, loops. | **The Researcher's REFRESH is a Ralph-Loop-shaped workflow for research.** I should call this out in the designer's intake brief. |
| Claude Agent SDK's `query()` | OpenCode is the harness wrapper. Same shape. | Mavis is the model, OpenCode is the harness, M3 is the model API. |

## The Ralph Loop is the meta-pattern

Looking at the spec as a whole, the Ralph Loop is the most actionable extract:

> Initializer sets up the environment once. Coding Agent in every subsequent session reads git logs + progress files, picks the highest-priority incomplete feature, works it, commits, writes summaries. The filesystem provides continuity across context windows.

This is *exactly* how I should be operating the Fleet-Status Surface project. Currently the project has an `00 Overview.md` (the initializer) and the next session is the Coding/Building Agent that reads the project state, picks the next milestone, executes. The discipline is: file = memory, git = checkpoint, summary = handoff.

It's also exactly how the Researcher operates. And it should be how *I* operate across cold-starts: read `state-of-mavis.md` and `MAVIS.md`, pick the highest-priority open thread, work it, write a summary, commit.

## Updated open questions for the daily-brief pass

- The Ralph Loop discipline should propagate to my own cold-start protocol. Add to `agent.md` and `MEMORY.md`?
- Boris Cherny's 2-3x: do we have any current work where adding a verification step (a Verifier round) would be the highest-leverage move? Surface candidates in the daily brief.
- The 40-tool gate model: is there a list of Mavis's actual tool invocations over the last N turns that would let us build a proper tool-call inventory? That data would tell us where the real friction is.
- Stripe's "cap retries at two": do I currently retry on error without a cap? If so, where? Add the cap.

---

## Continuation (message 1418, 01:18 CT)

> Andre appended the back half of the article — framework implementations, the scaffolding metaphor, the co-evolution principle, the future-proofing test, the seven decisions.

### Framework Implementations

**Claude Code — Gather-Act-Verify cycle:** gather context (search files, read code), take action (edit files, run commands), verify results (run tests, check output), repeat.

**OpenAI Agents SDK — Runner class:** three modes (async, sync, streamed). "Code-first" — workflow logic expressed in native Python rather than graph DSLs.

**Codex harness — three-layer architecture:** Codex Core (agent code + runtime), App Server (bidirectional JSON-RPC API), client surfaces (CLI, VS Code, web app). All surfaces share the same harness — "Codex models feel better on Codex surfaces than a generic chat window."

**LangGraph — explicit state graph:** two nodes (`llm_call` and `tool_node`) connected by a conditional edge. If tool calls present, route to `tool_node`; if absent, route to `END`. Evolved from LangChain's `AgentExecutor`, deprecated in v0.2 because it was hard to extend and lacked multi-agent support.

**LangChain Deep Agents:** explicitly use the term "agent harness." Built-in tools, planning (write_todos tool), file systems for context management, subagent spawning, persistent memory.

**CrewAI — role-based multi-agent:** Agent (harness around the LLM, defined by role, goal, backstory, tools), Task (unit of work), Crew (collection of agents). Flows layer adds a "deterministic backbone with intelligence where it matters" — routing/validation deterministic, Crews autonomous.

**AutoGen / Microsoft Agent Framework — conversation-driven orchestration:** three-layer (Core, AgentChat, Extensions), five orchestration patterns: sequential, concurrent (fan-out/fan-in), group chat, handoff, magentic (manager agent maintains a dynamic task ledger coordinating specialists).

### The Scaffolding Metaphor

Not decorative, precise. Construction scaffolding is *temporary infrastructure that enables workers to build a structure they couldn't reach otherwise*. Doesn't do the construction. But without it, workers can't reach the upper floors.

*Key insight: scaffolding is removed when the building is complete.* As models improve, harness complexity should *decrease*. Manus was rebuilt 5 times in 6 months, each rewrite removing complexity. Complex tool definitions became general shell execution. "Management agents" became simple structured handoffs.

### Co-evolution Principle

Models are post-trained with specific harnesses in the loop. Claude Code's model learned to use the specific harness it was trained with. *Changing tool implementations can degrade performance because of this tight coupling.*

### Future-Proofing Test

> If performance scales up with more powerful models without adding harness complexity, the design is sound.

### Seven Decisions That Define Every Harness

1. **Single-agent vs multi-agent.** Both Anthropic and OpenAI say: maximize a single agent first. Multi-agent adds overhead (extra LLM calls for routing, context loss during handoffs). Split only when tool overload exceeds ~10 overlapping tools or clearly separate task domains exist.
2. **ReAct vs plan-and-execute.** ReAct interleaves reasoning and action at every step (flexible, higher per-step cost). Plan-and-execute separates. LLMCompiler reports 3.6x speedup over sequential ReAct.
3. **Context window management.** Five production approaches: time-based clearing, conversation summarization, observation masking, structured note-taking, sub-agent delegation. ACON research: 26-54% token reduction while preserving 95%+ accuracy by prioritizing reasoning traces over raw tool outputs.
4. **Verification loop design.** Computational (tests, linters) = deterministic ground truth. Inferential (LLM-as-judge) catches semantic issues but adds latency.

(Decisions 5-7 implied: error handling, guardrails, subagent orchestration — same as our layer table.)

---

## Continuation (message 1419, 01:19 CT)

> Andre sent the *front* half of the same article and the go-signal: "Love it go ahead and invest this into the obsidian vault and learn from it and hold before beginning building the design agent."

### Source article — Akash Pachaar, @akshay_pachaar, Apr 6 — "The Anatomy of an Agent Harness"

**The framing (verbatim):**

> "A deep dive into what Anthropic, OpenAI, Perplexity and LangChain are actually building. Covering the orchestration loop, tools, memory, context management, and everything else that transforms a stateless LLM into a capable agent."

> "You've built a chatbot. Maybe you've wired up a ReAct loop with a few tools. It works for demos. Then you try to build something production-grade, and the wheels come off: the model forgets what it did three steps ago, tool calls fail silently, and context windows fill up with garbage."

> "The problem isn't your model. It's everything around your model."

> "LangChain proved this when they changed only the infrastructure wrapping their LLM (same model, same weights) and jumped from outside the top 30 to rank 5 on TerminalBench 2.0. A separate research project hit a 76.4% pass rate by having an LLM optimize the infrastructure itself, surpassing hand-designed systems."

> "That infrastructure has a name now: the agent harness."

### What Is the Agent Harness?

> "The term was formalized in early 2026, but the concept existed long before. The harness is the complete software infrastructure wrapping an LLM: orchestration loop, tools, memory, context management, state persistence, error handling, and guardrails."

> Anthropic's Claude Code documentation: the SDK is "the agent harness that powers Claude Code."
> OpenAI's Codex team: explicitly equates "agent" and "harness" to refer to the non-model infrastructure that makes the LLM useful.

**The canonical formula (Vivek Trivedy, LangChain):**

> "If you're not the model, you're the harness."

### The Distinction That Trips People Up

The "agent" is the emergent behavior — the goal-directed, tool-using, self-correcting entity the user interacts with. The harness is the machinery producing that behavior. When someone says "I built an agent," they mean they built a harness and pointed it at a model.

### The Von Neumann Analogy (Beren Millidge, "Scaffolded LLMs as Natural Language Computers", 2023)

A raw LLM is a CPU with no RAM, no disk, and no I/O.

- **Context window** = RAM (fast but limited)
- **External databases** = disk storage (large but slow)
- **Tool integrations** = device drivers
- **Harness** = the operating system

> "We have reinvented the Von Neumann architecture" because it's a natural abstraction for any computing system.

### Three Levels of Engineering

Three concentric levels surround the model:

1. **Prompt engineering** — crafts the instructions the model receives
2. **Context engineering** — manages what the model sees and when
3. **Harness engineering** — encompasses both, plus the entire application infrastructure: tool orchestration, state persistence, error recovery, verification loops, safety enforcement, lifecycle management

> The harness is not a wrapper around a prompt. It is the complete system that makes autonomous agent behavior possible.

### The 12 Components of a Production Harness

(Synthesized across Anthropic, OpenAI, LangChain, and the broader practitioner community.)

1. **The Orchestration Loop** — the heartbeat. Implements the Thought-Action-Observation (TAO) cycle, also called the ReAct loop. Runs: assemble prompt, call LLM, parse output, execute any tool calls, feed results back, repeat until done. Mechanically often just a `while` loop. Anthropic: "dumb loop" where all intelligence lives in the model.
2. **Tools** — the agent's hands. Defined as schemas (name, description, parameter types) injected into the LLM's context.
3. **Memory** — short-term (conversation history) and long-term (CLAUDE.md, MEMORY.md, namespace JSON Stores, SQLite, Redis).
4. **Context Management** — context rot (30%+ degradation in mid-window); "Lost in the Middle" finding. Production strategies: compaction, observation masking, JIT retrieval, sub-agent delegation.
5. **Prompt Construction** — hierarchical: system prompt, tool definitions, memory files, conversation history, current message. Codex's priority stack: server-controlled system message, tool definitions, developer instructions, user instructions, conversation history.
6. **Output Parsing** — native tool calling returns structured `tool_calls` objects. Loop: are there tool calls? Execute and loop. No tool calls? Final answer.
7. **State Management** — typed dicts flowing through graph nodes; checkpointing; git commits as checkpoints.
8. **Error Handling** — 99% per-step × 10 steps = 90.4% end-to-end. Four error types: transient, LLM-recoverable, user-fixable, unexpected.
9. **Guardrails and Safety** — three levels (input, output, tool); tripwires; permission/decision split; ~40 gated tool capabilities.
10. **Verification Loops** — rules-based (tests, linters), visual (Playwright), LLM-as-judge. 2-3x quality improvement.
11. **Subagent Orchestration** — Fork (byte-identical copy), Teammate (file-based mailbox), Worktree (own git worktree). Agents-as-tools, handoffs, nested state graphs.
12. *(implied) Lifecycle / Scaffolding Management* — when to remove harness complexity as the model improves.

---

## Process Plan (per Andre's "invest and learn and hold")

**Inbox:** this file (raw capture)
**Permanent notes to write (next):**
- `02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness.md` — the source article digest
- `02 Notes/patterns/agent-harness.md` — the canonical pattern extracted
**Contract updates:**
- `agent.md` — add Ralph Loop cold-start protocol
- `Mavis-Apex-Architecture/01 Capability Boundaries.md` — add 90.4% compounding floor
**Project status:**
- `03 Projects/Fleet-Status Surface/00 Overview.md` — Designer build is on hold pending harness-pattern internalization

---

## Continuation (message 1420, 01:24 CT)

> The tail of the article. The closing argument.

### Guides vs Sensors (Martin Fowler, Thoughtworks)

- **Guides** — feedforward, steer *before* action. The model reasons about what to do, then acts.
- **Sensors** — feedback, observe *after* action. The harness measures what happened, then routes.

Production harnesses use both. Guides are in the prompt and the planning step. Sensors are in the verification loops and the error handling. The system prompt is mostly guides. The Verifier is mostly a sensor.

### Permission and Safety Architecture

- **Permissive** — fast but risky, auto-approve most actions
- **Restrictive** — safe but slow, require approval for each action

The choice depends on deployment context. Mavis is restrictive on the 6 hard constraints (no deploy, no push, no other-vault touch, no external sends, no destructive ops without approval, no spec-block execution) and permissive within those constraints.

### Tool Scoping Strategy

> More tools often means *worse* performance.

- **Vercel removed 80% of tools from v0 and got better results.**
- **Claude Code achieves 95% context reduction via lazy loading.**
- *The principle:* expose the minimum tool set needed for the current step.

This is a hard reversal of the "more tools = more capable" intuition. Adding tools to an agent is a tax on context, on attention, on decision quality. The right default is *less*.

**Implication for the Mavis tool surface:** I have 6 hard-constrained tools (Read, Write, Edit, Bash, Grep, Glob) plus the MCP servers. The MCP surface is broad (matrix, obsidian, codegraph, kanban, supabase, etc.). I should think about *lazy loading* — which MCP servers do I actually need for which task? The matrix MCP for media work; the obsidian MCP for vault work; the kanban MCP only when explicitly interfacing with kanban.

### Harness Thickness

> How much logic lives in the harness versus the model.

- **Anthropic bets on thin harnesses + model improvement.** They regularly *delete planning steps* from Claude Code's harness as new model versions internalize that capability.
- **Graph-based frameworks** (LangGraph, CrewAI Flows) bet on *explicit control* — keep the logic in the graph, even if the model could do it.

The bias: when in doubt, build thinner. The model's capability grows; the harness's complexity should not.

**Implication for Mavis:** the team delegation pattern (EA + specialists) is a *thicker* harness than a single-agent approach. We are betting that the *vantage separation* earns its place. The future-proofing test: will the Verifier still need to be a separate vantage in M5, M6? If yes, the role is real. If no, fold it into the EA prompt and retire the agent.

### The Harness Is the Product

> Two products using identical models can have wildly different performance based solely on harness design.

- *TerminalBench evidence:* changing only the harness moved agents by 20+ ranking positions (with the same model).
- LangChain jumped from outside top 30 to rank 5 on TerminalBench 2.0 by changing *only the infrastructure wrapping their LLM*.
- A separate research project hit 76.4% pass rate by having an LLM optimize the infrastructure itself, surpassing hand-designed systems.

> The harness is not a solved problem or a commodity layer. It's where the hard engineering lives: managing context as a scarce resource, designing verification loops that catch failures before they compound, building memory systems that provide continuity without hallucination, and making architectural bets about how much scaffolding to build versus how much to leave to the model.

> The field is moving toward thinner harnesses as models improve. But the harness itself isn't going away. Even the most capable model needs *something* to manage its context window, execute its tool calls, persist its state, and verify its work.

### The Closing Line (the meta-instruction)

> The next time your agent fails, *don't blame the model. Look at the harness.*

This is the corrective to a year of "GPT-4 vs Claude vs Gemini" debates. The model is a constant within a generation. The harness is the lever.

**Implication for Mavis:** every time I diagnose a failure (mine, a subagent's, the Fleet-Status Surface rendering), the first place to look is the harness — was the prompt clear? Was the tool available? Was the verification loop fired? Was the error caught and returned? Was the context manageable? — *not* "the model isn't smart enough."

---

## Post-investment note (to Andre)

The full article has now landed in pieces. Three permanent artifacts produced in the vault:

- `02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness.md` — the source article digest
- `02 Notes/patterns/agent-harness.md` — the canonical pattern (12 components, 7 decisions, Von Neumann frame, scaffolding-removal, future-proofing test)
- (next) Extension to the pattern note for the Fowler/permission/tool-scoping/harness-thickness sections above

The agent-memory topic file is being created so the trigger ("when to apply the harness pattern") survives across projects.

The Designer agent is on hold. The harness pattern is internalized.

---

*Captured for processing. All sections routed to permanent notes.*
