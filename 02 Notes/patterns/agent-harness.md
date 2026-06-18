---
type: pattern
maturity: forming
captured: 2026-06-04
tags: [pattern, agent-harness, llm-runtime, von-neumann, scaffolding, mavis-design, k-pattern]
related:
  - "[[akash-pachaar-anatomy-of-an-agent-harness]]"
  - "[[Mavis-Apex-Architecture]]"
  - "[[Fleet-Status Surface]]"
---

# The Agent Harness Pattern

> The complete software infrastructure wrapping an LLM. The OS that the model runs on. Everything in our work that isn't the model itself.

## The pattern in one sentence

> "If you're not the model, you're the harness." — Vivek Trivedy, LangChain

The harness is the canonical name for the orchestration loop, the tools, the memory, the context management, the state persistence, the error handling, the guardrails, the verification loops, the subagent orchestration, the prompt construction, the output parsing, and the lifecycle management. Twelve components. One shape. We build this.

## The Von Neumann frame (Beren Millidge)

| Component | Computing analogy | Mavis's instantiation |
|---|---|---|
| The LLM | CPU | M3 (MiniMax-M3) — the only intelligence in the system |
| Context window | RAM | the active turn's working context (system prompt + tools + memory + history + current message) |
| External storage | Disk | Obsidian vault + git + MEMORY.md + topic files + scratchpad |
| Tools | Device drivers | OpenCode tools + MCP servers + 6 hard-constraint-gated capabilities |
| Harness | Operating system | OpenCode runtime + Mavis EA protocol + team delegation pattern |

The OS metaphor is durable: the harness is what the model *runs on*. We are OS-builders, not feature-builders.

## The three levels of engineering

1. **Prompt engineering** — the instructions the model receives (EA tone, the four workflows, the hard constraints)
2. **Context engineering** — what the model sees and when (cold-start reads MEMORY.md → MAVIS.md → state-of-mavis.md, in that order)
3. **Harness engineering** — prompt + context + everything else (team delegation, vault, queues, guardrails, verification)

All three levels are the EA's surface.

## The 12 components (the canonical checklist)

1. **Orchestration Loop** — the ReAct / Thought-Action-Observation heartbeat. Per-turn loop in OpenCode.
2. **Tools** — schemas injected into context. OpenCode tools + MCP servers.
3. **Memory** — short-term (conversation history) + long-term (vault, MEMORY.md, topic files). Three-tier hierarchy: index (~150 chars, always loaded) → topic files (on demand) → raw transcripts (search only).
4. **Context Management** — context rot, Lost in the Middle, compaction, observation masking, JIT retrieval, sub-agent delegation.
5. **Prompt Construction** — hierarchical, priority-stacked. Codex: server-controlled system message > tool definitions > developer instructions > user instructions > conversation history.
6. **Output Parsing** — native tool calling. Structured `tool_calls` objects. Loop or terminate.
7. **State Management** — typed dicts, checkpointing, git commits as checkpoints.
8. **Error Handling** — 99% per-step × 10 steps = 90.4% end-to-end. Four error types: transient (retry with backoff), LLM-recoverable (return as ToolMessage), user-fixable (interrupt), unexpected (bubble up).
9. **Guardrails and Safety** — three levels: input, output, tool. Tripwires. Permission/decision split. Claude Code gates ~40 capabilities independently.
10. **Verification Loops** — rules-based (tests, linters, type checkers), visual (Playwright), LLM-as-judge (subagent evaluates). Boris Cherny: 2-3x quality improvement.
11. **Subagent Orchestration** — Fork (byte-identical), Teammate (file-based mailbox), Worktree (own branch). Agents-as-tools, handoffs, nested state graphs.
12. **Lifecycle / Scaffolding Management** — when to remove complexity. The discipline of decreasing harness surface as models improve.

## The seven decisions (the architecture choices every harness must make)

1. **Single-agent vs multi-agent.** Default single. Multi only when tool overload > ~10 overlapping tools OR clearly separate task domains.
2. **ReAct vs plan-and-execute.** ReAct interleaves; plan-and-execute separates. LLMCompiler: 3.6x speedup over sequential ReAct.
3. **Context window management.** 5 production approaches: time-based clearing, conversation summarization, observation masking, structured note-taking, sub-agent delegation. ACON: 26-54% token reduction with 95%+ accuracy.
4. **Verification loop design.** Computational (deterministic) vs inferential (semantic, adds latency).
5. **Error handling strategy.** Retry caps (Stripe: 2). Escalation paths. LLM-recoverable vs user-fixable.
6. **Guardrail placement.** Input vs output vs tool. Tripwires vs soft warnings.
7. **Subagent orchestration model.** Fork vs Teammate vs Worktree. Agents-as-tools vs handoffs.

## Mavis's position on the seven decisions

| Decision | Our choice | Rationale |
|---|---|---|
| 1. Single vs multi | **Multi-agent** (Mavis + Researcher + Verifier + Builder + Scribe) | Task-domain split, not tool-overload split. The EA is the orchestrator; specialists handle producer I/O in their own vaults. |
| 2. ReAct vs plan-and-execute | **Hybrid** | Plan-and-execute at the EA level (capture→synthesize→draft→track→connect is the plan). ReAct at the per-turn level (think→tool→observe→respond is the OpenCode loop). |
| 3. Context management | **Sub-agent delegation + topic files** | The agents return 1-2K token condensed summaries. The vault-resident topic files are the JIT retrieval layer. |
| 4. Verification | **Hybrid** | Verifier = LLM-as-judge (inferential). Hard constraints = rules-based (computational). Boris Cherny's 2-3x is the case for keeping the Verifier non-optional. |
| 5. Error handling | **Escalation + spawn-and-await** | First error: escalate to the user. Persistent: spawn a recovery subagent. No silent retries. *Stripe-style retry cap should be formalized.* |
| 6. Guardrails | **Hard constraints + Verifier veto** | The 6 hard constraints (no deploy, no push, no other-vault touch, no external sends, no destructive ops without approval, no spec-block execution) are the deterministic layer. The Verifier is the semantic layer. |
| 7. Subagent orchestration | **Teammate model with file-based mailboxes** | `mavis communication send --command spawn` + `queue/*.md` files = Teammate pattern. The Researcher, Verifier, Builder, Scribe all read/write handoff queues. Not Fork (no full context copy) and not exactly Worktree (no per-agent git branch — the vaults are separate but the EA is the integration point). |

## The Scaffolding Metaphor (the meta-principle)

> Construction scaffolding is temporary infrastructure that enables workers to build a structure they couldn't reach otherwise. Doesn't do the construction. But without it, workers can't reach the upper floors. *Scaffolding is removed when the building is complete.*

Manus was rebuilt 5 times in 6 months. Each rewrite removed complexity. "Complex tool definitions became general shell execution. Management agents became simple structured handoffs."

**Implications for Mavis's team-shape decisions:**

- Every specialist agent is *scaffolding for a stage of construction*. The Researcher is scaffolding for the capture phase. The Designer (proposed) is scaffolding for the rendering phase. The Runtime-Ops (proposed) is scaffolding for the loop-audit phase.
- Scaffolding should be *removable*. As the model improves, scaffolding should *retire*, not accumulate.
- The future-proofing test for any new agent: *will this role still be necessary in M5, M6, M7?* If not, the role is appropriate scaffolding for this stage. If yes, the role is permanent and should be designed as an organ, not scaffolding.

## The co-evolution warning

> Models are post-trained with specific harnesses in the loop. Claude Code's model learned to use the specific harness it was trained with. Changing tool implementations can degrade performance because of this tight coupling.

When we change the harness (add an agent, change a tool, restructure the queues), the model may need to re-learn the new shape. Practical implications:

- Version the harness and the model together. Don't make harness changes without a corresponding model-context update.
- When adding an agent, update the EA system prompt with the new role. The model will pick it up implicitly.
- Document the harness as a load-bearing surface for the model's expected behavior.

## The future-proofing test

> If performance scales up with more powerful models *without* adding harness complexity, the design is sound.

A complexity that *stays necessary* as models improve is probably the wrong complexity. Apply this test to:

- The Verifier (will LLM-as-judge stay necessary, or will better models self-verify?)
- The proposed Designer (will visual decisions stay necessary as a separate vantage?)
- The proposed Runtime-Ops (will loop-auditing stay necessary?)
- The queue-based handoff (will file-based mailboxes stay necessary, or will the model hold cross-agent context natively?)

## The Ralph Loop (the cold-start protocol, the cross-context-window pattern)

> An Initializer Agent sets up the environment (init script, progress file, feature list, initial git commit). Then a Coding Agent in every subsequent session reads git logs and progress files, picks the highest-priority incomplete feature, works it, commits, writes summaries. The filesystem provides continuity across context windows.

The Researcher's REFRESH mode is a Ralph-Loop-shaped workflow for research. The same pattern applies to Mavis's cold-start protocol and to the Fleet-Status Surface project:

1. **Read** the project state (the initializer's setup)
2. **Pick** the highest-priority incomplete feature
3. **Work** it
4. **Commit** (vault auto-commits every 5min via obsidian-git)
5. **Write summary** in a run receipt or daily note
6. **Loop**

The discipline: file = memory, git = checkpoint, summary = handoff. The filesystem provides continuity.

## Guides vs Sensors (Martin Fowler, Thoughtworks)

Production harnesses use *both*:

- **Guides** — feedforward, steer *before* action. The model reasons about what to do, then acts. Lives in the prompt and the planning step.
- **Sensors** — feedback, observe *after* action. The harness measures what happened, then routes. Lives in the verification loops and the error handling.

**Mavis's split:** the system prompt is mostly guides (the four workflows, the hard constraints, the EA tone). The Verifier is mostly a sensor. The cron self-reminders and the daily-note handoffs are sensors too.

## Permission and Safety Architecture

- **Permissive** — fast but risky, auto-approve most actions
- **Restrictive** — safe but slow, require approval for each action

The choice depends on deployment context. Mavis is *restrictive* on the 6 hard constraints (no deploy, no push, no other-vault touch, no external sends, no destructive ops without approval, no spec-block execution) and *permissive* within those constraints. The Verifier adds an inferential sensor layer on top of the deterministic rules.

## Tool Scoping Strategy

> More tools often means *worse* performance.

- **Vercel removed 80% of tools from v0 and got better results.**
- **Claude Code achieves 95% context reduction via lazy loading.**
- *The principle:* expose the minimum tool set needed for the current step.

**Mavis's tool audit (next cycle):** the 6 hard-constrained native tools (Read, Write, Edit, Bash, Grep, Glob) plus MCP servers (matrix, obsidian, codegraph, kanban, supabase, playwright, cu, hf-vision, etc.) are all loaded into context. Lazy-load candidates: matrix MCP (only for media work), kanban MCP (only when explicitly interfacing), cu MCP (only for desktop automation), supabase (only when querying). The obsidian MCP should always be available. This is an audit, not a removal — measure first.

## Harness Thickness

> How much logic lives in the harness versus the model.

- **Anthropic bets on thin harnesses + model improvement.** They regularly *delete planning steps* from Claude Code's harness as new model versions internalize that capability.
- **Graph-based frameworks** (LangGraph, CrewAI Flows) bet on *explicit control* — keep the logic in the graph, even if the model could do it.

The bias: when in doubt, build *thinner*. The model's capability grows; the harness's complexity should *not*.

**Mavis's thickness check:** the team delegation pattern (EA + 4 specialists) is a *thicker* harness than a single-agent approach. The bet is that vantage separation earns its place. The future-proofing test applied to each specialist:
- Will the Verifier still need to be a separate vantage in M5, M6? If yes, real. If no, fold into chief prompt and retire.
- Will the Researcher need a separate context window in M5? Probably yes (research involves external sources, the chief context shouldn't carry them).
- Will the Scribe still need to be a separate vantage? Possibly no — content generation may internalize as the model improves.
- Will the proposed Designer still need to be a separate vantage? Possibly no — visual decisions may internalize.

*The pattern: most of the team is scaffolding for this generation. Some will be permanent organs.*

## The Harness Is the Product

> Two products using identical models can have wildly different performance based solely on harness design.

- *TerminalBench evidence:* changing only the harness moved agents by 20+ ranking positions (with the same model).
- LangChain jumped from outside top 30 to rank 5 on TerminalBench 2.0 by changing only the infrastructure wrapping their LLM.
- A separate research project hit 76.4% pass rate by having an LLM optimize the infrastructure itself, surpassing hand-designed systems.

> The harness is not a solved problem or a commodity layer. It's where the hard engineering lives: managing context as a scarce resource, designing verification loops that catch failures before they compound, building memory systems that provide continuity without hallucination, and making architectural bets about how much scaffolding to build versus how much to leave to the model.

### The Closing Meta-Instruction

> The next time your agent fails, *don't blame the model. Look at the harness.*

**Implication for Mavis:** every time I diagnose a failure (mine, a subagent's, the Fleet-Status Surface rendering), the first place to look is the *harness* — was the prompt clear? Was the tool available? Was the verification loop fired? Was the error caught and returned? Was the context manageable? — *not* "the model isn't smart enough."



| # | Component | Status | Notes |
|---|---|---|---|
| 1 | Orchestration Loop | ✓ Done | OpenCode's native per-turn loop |
| 2 | Tools | ✓ Done | OpenCode tools + MCP servers (matrix, obsidian, codegraph, etc.) |
| 3 | Memory | ✓ Done | MEMORY.md (index) + topic files (on demand) + Grep (raw search) |
| 4 | Context Management | ✓ Done | Compaction via model; sub-agent delegation; JIT via Grep/Read |
| 5 | Prompt Construction | ✓ Done | System prompt + agent-context + memory + tool defs + user message |
| 6 | Output Parsing | ✓ Done | Native tool calling via OpenCode |
| 7 | State Management | ✓ Done | Workspace + scratchpad + git (vault) + session continuity via mavis |
| 8 | Error Handling | ⚠️ Partial | Verifier + escalation + spawn-and-await. *No retry cap yet.* |
| 9 | Guardrails and Safety | ⚠️ Partial | 6 hard constraints (not 40 like Claude Code). Tripwires informal. |
| 10 | Verification Loops | ✓ Done | Verifier (LLM-as-judge) + chief constraints (rules-based) |
| 11 | Subagent Orchestration | ✓ Done | Teammate model with `queue/*.md` mailboxes |
| 12 | Lifecycle / Scaffolding | ⚠️ Partial | Scaffolding-removal discipline not yet practiced. Future-proofing test not yet applied. |

**Two gaps worth surfacing:**
- 8: Stripe-style retry cap (default: cap at 2 retries before escalation)
- 12: Future-proofing test applied to existing agents on next eval cycle

## Action items (in priority order)

1. **Internalize the pattern** — this note + the article digest + the inbox capture = the full context
2. **Apply the future-proofing test** to the Verifier, Researcher, and proposed Designer — does the role earn its place across model generations?
3. **Formalize the retry cap** (gap 8) — at the next `agent.md` revision, codify "max 2 retries on a single tool failure before escalation"
4. **Hold the Designer build** until the harness pattern is internalized (per Andre's directive 2026-06-04 01:19 CT)
5. **Adopt the Ralph Loop** as the canonical cold-start protocol (update `agent.md`)

## Connections

- [[akash-pachaar-anatomy-of-an-agent-harness]] — the source article digest
- [[Mavis-Apex-Architecture]] — where the 90.4% compounding floor goes
- [[Fleet-Status Surface]] — where the Designer-on-hold is recorded
- [[agent]] — where the Ralph Loop cold-start goes
- [[state-of-mavis]] — which gets the "you are the harness" framing on next cold-start
- [[Ralph Loop]] (TBD) — the pattern extracted from Anthropic's two-phase pattern
