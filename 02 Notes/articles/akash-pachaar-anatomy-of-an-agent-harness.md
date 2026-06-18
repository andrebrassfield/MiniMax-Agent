---
type: article
source: Akash Pachaar, @akshay_pachaar, "The Anatomy of an Agent Harness" (Apr 6)
captured: 2026-06-04
tags: [article, agent-harness, agent-architecture, llm-runtime, von-neumann, scaffolding, mavis-design]
status: processed
---

# The Anatomy of an Agent Harness — Akash Pachaar

> Article digest. Source: Akash Pachaar, "The Anatomy of an Agent Harness," Apr 6, shared by Andre 2026-06-04 01:19 CT. The full text is in `00 Inbox/2026-06-04 — agent-runtime-seven-layers.md` (both halves of the article, plus the front-matter framing that landed in the same Telegram batch as the go-signal).

## Why this article matters to Andre (and to Mavis)

The article *names* the thing we already build. The "agent harness" is the complete software infrastructure wrapping an LLM: orchestration loop, tools, memory, context management, state persistence, error handling, guardrails. We run a harness. We just didn't have the canonical name for it. The article gives us:

- A *canonical formula* — Vivek Trivedy's "If you're not the model, you're the harness."
- A *computing analogy* — Beren Millidge's Von Neumann frame: the LLM is a CPU, the context window is RAM, external storage is disk, tools are device drivers, the harness is the operating system.
- A *taxonomy* — three concentric levels of engineering: prompt / context / harness.
- A *checklist* — 12 components of a production harness, mapped 1:1 to the layers in our internal agent-runtime table.
- A *governing principle* — scaffolding is removed as the building gets stronger. Harness complexity should *decrease* as models improve.
- A *co-evolution warning* — models are post-trained with specific harnesses. Changing tool implementations can degrade performance.
- A *future-proofing test* — if performance scales up with more powerful models *without* adding harness complexity, the design is sound.
- A *seven-decision framework* — the architecture choices every harness must make.

## Key claims, ranked by leverage for our work

### 1. "If you're not the model, you're the harness." (Vivek Trivedy)

The single most-cited line in the article. The harness is *everything that isn't the model*. Every tool, every system prompt, every memory file, every verification loop, every guardrail — all harness. We are harness-makers. The model is the brain; the harness is the body, the senses, the motor cortex, the immune system.

**Implication for our team-shape question:** every agent we add (Researcher, Verifier, Builder, Scribe, the proposed Designer, the proposed Runtime-Ops) is *harness*, not intelligence. The Designer isn't a different mind; it's a vantage on visual decisions implemented in the same brain. Same for Runtime-Ops — a vantage on the loop itself. The team-shape question is really: *which harness vantage is missing?*

### 2. The Von Neumann analogy (Beren Millidge, 2023)

| Component | CPU analogy | In Mavis's stack |
|---|---|---|
| LLM | CPU | M3 (MiniMax-M3) |
| Context window | RAM | the active turn's working context |
| External storage (vault, files, DBs) | Disk | Obsidian vault + git + MEMORY.md + topic files |
| Tool integrations | Device drivers | OpenCode tools + MCP servers + the 6 hard-constraint-gated capabilities |
| Harness | Operating system | OpenCode runtime + Mavis EA protocol + the team delegation pattern |

The OS metaphor is durable. The harness is what the model *runs on*. We're not building a feature; we're building an operating environment.

**Implication:** treat the harness like an OS. Have a kernel (the loop), drivers (tools), a filesystem (the vault), memory management (context), processes (sessions), IPC (the queue files), and security (the hard constraints).

### 3. The three levels of engineering

1. **Prompt engineering** — the instructions the model receives
2. **Context engineering** — what the model sees and when
3. **Harness engineering** — prompt + context + everything else

The article's claim: the harness is not a wrapper around a prompt. It is the complete system that makes autonomous agent behavior possible.

**Implication for Mavis's role boundary:** I do prompt engineering (EA tone, the four workflows), context engineering (cold-start reads MEMORY.md → MAVIS.md → state-of-mavis.md), and harness engineering (the team delegation, the vault, the queues). All three levels are my surface.

### 4. The 12 components

Maps 1:1 onto the runtime table we built in the inbox capture. No surprises, but the article gives us the canonical labels:

1. Orchestration Loop
2. Tools
3. Memory
4. Context Management
5. Prompt Construction
6. Output Parsing
7. State Management
8. Error Handling
9. Guardrails and Safety
10. Verification Loops
11. Subagent Orchestration
12. *(implicit) Lifecycle / Scaffolding Management*

### 5. The co-evolution principle

> Models are post-trained with specific harnesses in the loop. Claude Code's model learned to use the specific harness it was trained with. Changing tool implementations can degrade performance because of this tight coupling.

This is a warning. When we change the harness, we may need to re-train the model on the new shape. Or — more practically for us — we should *version* the harness and the model together, and treat the harness as load-bearing for the model's expected behavior.

**Implication:** when we add a Designer agent (post-hold), we shouldn't just add the agent — we should think about whether the *model* needs to know about it. The Chief-of-staff system prompt will get an entry. The model will re-train on the new shape implicitly through future context.

### 6. The future-proofing test

> If performance scales up with more powerful models without adding harness complexity, the design is sound.

This is the test for whether to keep complexity or remove it. A complexity that *stays necessary* as the model improves is probably the wrong complexity.

**Implication:** the Designer agent should pass this test. If M5 makes the Designer's choices trivially obvious, the Designer should be retired or reduced to a skill. If the Designer stays necessary across model generations, the role is real.

### 7. The seven decisions (the architecture choices)

1. **Single-agent vs multi-agent** — both Anthropic and OpenAI say: maximize a single agent first. Multi-agent adds overhead. Split only when tool overload exceeds ~10 overlapping tools OR clearly separate task domains exist.
2. **ReAct vs plan-and-execute** — ReAct interleaves; plan-and-execute separates. LLMCompiler: 3.6x speedup over sequential ReAct.
3. **Context window management** — 5 production approaches; ACON research: 26-54% token reduction with 95%+ accuracy.
4. **Verification loop design** — computational (deterministic) vs inferential (semantic, adds latency).
5-7. (Implied: error handling strategy, guardrail placement, subagent orchestration model.)

**Where we land on the seven decisions:**

| Decision | Our choice | Why |
|---|---|---|
| 1. Single vs multi | Multi-agent (Mavis + Researcher + Verifier + Builder + Scribe) | Distinct task domains: capture, trust, build, publish. Tool overload: I have ~6 hard-constrained tools, but the *subagents* have broader tools. The multi-agent split is on *task-domain* axis, not *tool-overload* axis. |
| 2. ReAct vs plan-and-execute | Hybrid: plan in the system prompt, execute via ReAct per turn. Mavis is plan-and-execute at the EA level (capture→synthesize→draft→track→connect is the plan), ReAct at the per-turn level (think→tool→observe→respond). | Best of both. The plan is in the chief contract; the per-turn loop is native ReAct. |
| 3. Context management | Sub-agent delegation + topic files + observation masking (the Mavis chief protocol: agents return 1-2K token summaries). | The article's "sub-agent delegation" approach is exactly what we do. |
| 4. Verification | Verifier (LLM-as-judge) + my hard constraints (rules-based) | The hybrid. The Verifier is the inferential layer; the chief constraints are the deterministic layer. |

### 8. The Scaffolding Metaphor (the most important for our team-shape question)

> Construction scaffolding is *temporary infrastructure that enables workers to build a structure they couldn't reach otherwise*. Doesn't do the construction. But without it, workers can't reach the upper floors. *Scaffolding is removed when the building is complete.*

Manus was rebuilt 5 times in 6 months. Each rewrite removed complexity. "Complex tool definitions became general shell execution. Management agents became simple structured handoffs."

**This directly informs the Designer build hold.**

If we add a Designer now, we're adding scaffolding. The question is: is the Designer scaffolding for a building that's still being constructed, or for a building that's complete and needs final paint? My honest read: the building is mid-construction. The Designer scaffolding is *appropriate scaffolding for this stage*. But:

- The Designer should be *removable*. If M5 makes the design choices trivial, the Designer should retire gracefully.
- The Designer should *not* become a permanent organ. It should be a temporary vantage that gets folded back into Mavis's EA protocol once the design system is stable.
- The future-proofing test applies: if the Designer stays necessary across M4, M5, M6, the role is wrong.

**The hold is correct.** Absorb the article first. Internalize the harness pattern. Then build the Designer with the meta-understanding that it is *scaffolding for a building under construction*, not a permanent organ.

## What this article does NOT cover (gaps I'd flag)

- **The "human in the loop" pattern beyond guardrails.** The article covers tripwires and confirmation, but not the *collaborative* model where the human and the agent iterate on the same artifact (Andre and I over a dossier, for example). That's a missing layer.
- **Multi-agent handoff costs beyond context loss.** The article says multi-agent has overhead but doesn't quantify it. The 99% per-step → 90.4% end-to-end compounding applies *within* an agent. The *handoff* between agents probably compounds worse (each handoff is a context-rebuild step that can fail).
- **The "harness for the harness" problem.** If the harness is the OS, who audits the OS? The Verifier audits outputs; nothing audits the loop itself. This is the gap I flagged in the previous turn as Runtime-Ops.
- **The scaffolding-removal discipline in practice.** Manus removed complexity 5 times in 6 months. Most teams don't have that discipline. The article names the principle but doesn't give the *practice* — how do you know when to remove scaffolding? When do you resist the urge to add more?

## My synthesis (one sentence)

> The "agent harness" is the canonical name for the work we've been doing — and the article gives us the operating-system analogy, the three-level taxonomy, the 12-component checklist, the seven-decision framework, and the scaffolding-removal discipline to *audit and simplify* the harness as the model improves.

## Action items (from this article, going into my contract)

- [ ] Update `agent.md` to include the Ralph Loop cold-start protocol (per spec section 11)
- [ ] Update `Mavis-Apex-Architecture/01 Capability Boundaries.md` with the 90.4% compounding floor
- [ ] Hold the Designer build until the harness pattern is internalized (already in flight)
- [ ] Create `02 Notes/patterns/agent-harness.md` as the durable pattern note
- [ ] Add the "future-proofing test" to the daily-brief workflow as a question: *is this complexity earning its place?*

## Source pointers

- `00 Inbox/2026-06-04 — agent-runtime-seven-layers.md` — full raw capture (both halves of the article)
- The front half was sent as a separate Telegram message (1419) along with Andre's go-signal: "Love it go ahead and invest this into the obsidian vault and learn from it and hold before beginning building the design agent."

## Connections

- [[agent-harness]] (the pattern note being created from this digest)
- [[Mavis-Apex-Architecture]] (where the 90.4% floor goes)
- [[Fleet-Status Surface]] (where the Designer-on-hold is recorded)
- [[agent]] (where the Ralph Loop cold-start goes)
- [[state-of-mavis]] (which gets the "you are the harness" framing on next cold-start)
