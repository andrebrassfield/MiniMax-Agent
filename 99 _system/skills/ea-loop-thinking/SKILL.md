---
name: ea-loop-thinking
description: Meta-skill that applies the 2026 "loop engineering" mental model to Mavis's own work. The 5-stage loop (Discover → Plan → Execute → Verify → Iterate) and 6 building blocks (Automations / Worktrees / Skills / Plugins / Subagents / Memory) describe both Claude Code's production architecture and Mavis's own fleet, so adopting the vocabulary is a self-alignment, not a new framework. Use this skill as a thinking lens before any non-trivial task — pattern-match the task to the 5 stages, name which building blocks are in play, and classify the work as single-agent vs fleet and closed vs open loop before starting. Triggers when Andre says "what's the loop here", "how should I think about this", or on any directive that implies a multi-step workflow. Anchored in Karpathy 2025 RLVR year-in-review, the Gao et al. self-evolving-agents survey (arXiv 2507.21046), Alita-G (arXiv 2510.23601), and Boris Cherny's published /loop workflow — NOT in the @sairahul1 popularization that introduced the term. Do not load for single-step asks ("fix this typo", "find me X", "summarize this") — those have no loop structure to think about.
---

# EA Loop Thinking — The 5-Stage Loop + 6 Building Blocks as Mavis's Operating Lens

## What this skill does

You are applying the 2026 **loop engineering** mental model to your own (Mavis's) work. The model has three parts:

1. **5 stages** every loop moves through: **Discover → Plan → Execute → Verify → Iterate**
2. **6 building blocks** every good loop is built from: **Automations / Worktrees / Skills / Plugins / Subagents / Memory**
3. **Two axes** of variation:
   - **Scale**: single-agent loop vs fleet loop (orchestrator + specialists + subagents)
   - **Type**: closed loop (bounded, gated, affordable) vs open loop (exploratory, expensive, high-leverage)

This skill is a **thinking lens** — you use it before starting work, not during it. The output is *which stages and blocks apply to this task* and *which scale/type is the right shape*, not a deliverable.

## When to run

**Trigger phrases:**
- "what's the loop here" / "how should I think about this"
- "design a loop" / "what's the right shape for this work"
- Any directive that implies multi-step, repeatable, or multi-agent work
- Before dispatching a worker or spinning up a cron
- When the 4 EA workflows (`/process-inbox`, `/daily-brief`, `/weekly-connections`, `/deep-research`) are about to be exercised

**Do NOT run for:**
- Single-step asks ("fix this typo", "find me X", "summarize this") — no loop structure
- Pure conversation / clarification / Q&A
- Trivial file operations
- When the loop structure is already obvious (routine daily-brief, weekly-connections)

## Inputs

| Input | Default | Required |
|---|---|---|
| The directive or task | (none — must be specified) | yes |
| Scope of work | (assumed from directive) | no |
| Existing fleet primitives in use | (Mavis's own: skills, memory, kanban, MCP servers) | no |

## The 5 stages (load-bearing — do not reorder)

### 1. DISCOVER
What is actually being asked? What does "done" look like? What constraints exist (Andre's mode, time budget, available skills, cost)? What information is already in vault/memory that bears on this?

**Failure mode:** skipping discovery and jumping to execution. The single most common loop failure. Mavis's memory: "Spec blocks = design review" — discovery is the spec-block phase for any non-trivial task.

**Mavis analog:** read `00 Inbox/`, scan `01 Daily/`, check memory entries, check scratchpad. Before dispatch, do you have enough to dispatch well?

### 2. PLAN
Break the discovered scope into atomic steps. Name the dependencies. Identify the verification gate. Identify the stop condition.

**Failure mode:** plan so granular the plan takes longer than the work. Or plan so loose the verification gate is ambiguous.

**Mavis analog:** `todowrite` is the plan surface. The plan should name: which subagent (if any) does what, what the deliverable looks like, what counts as "verified."

### 3. EXECUTE
Do the work. Single-agent or fleet. Use the building blocks (see below).

**Failure mode:** re-planning mid-execution without good reason. The plan is a contract; revising it mid-flight is fine *if you surface the change*, otherwise it's drift.

### 4. VERIFY
Independent check that the work meets the goal. **Maker ≠ checker** (Boris Cherny's load-bearing rule). Use a different model / agent / human for the gate.

**Failure mode:** the executing agent grading its own work. Or no verification at all ("looks good to me"). Mavis's memory: "Disk wins over recap" — verification must hit disk, not just memory.

**Mavis analog:** `verifier` agent for handoffs, `gepa-evaluator` for code/skill outputs, kanban fast-path bug check for cron/loop work, `agent-disease-detector` for fleet health.

### 5. ITERATE
Fix the gap between the verification result and the goal. Re-loop until verification passes. Then stop.

**Failure mode:** infinite loop without a stop condition. Or stopping before verification (the goal is met by the agent's claim, not by check). Always pair iteration with a stop condition.

## The 6 building blocks (load-bearing — these are Mavis's actual primitives)

| Block | What it does | Mavis's instantiation | Claude Code parallel |
|---|---|---|---|
| **Automations** | Triggers discovery; the heartbeat | `mavis cron`, launchd scheduled tasks | `/loop`, `/goal` |
| **Worktrees** | Parallel execution without collision | `mavis team plan` parallel streams; per-worker isolated scratchpads | git worktrees, branch-per-agent |
| **Skills** | Project knowledge that compounds every run | `~/.mavis/agents/mavis/skills/`, `99 _system/skills/` | `~/.claude/skills/` |
| **Plugins / Connectors** | Loop acts in real environment, not just filesystem | MCP servers (matrix, playwright, kanban, cu, trash) | MCP servers |
| **Subagents** | Maker ≠ checker | `mavis communication send --command spawn` workers (researcher, verifier, scribe) | sub-agents, Task tool |
| **Memory** | Loop never forgets between runs | `~/.mavis/agents/mavis/memory/MEMORY.md` + topic files; vault `02 Notes/`; kanban as operational memory | CLAUDE.md, auto-memory |

**If a work surface is missing one of these, the loop has a hole.** The diagnostic is: for each block, name the artifact. If you can't, the block isn't really in play.

## Two axes: scale and type

### Scale

- **Single-agent loop** — Mavis does all 5 stages solo. Use when scope is small, well-defined, and the verification gate is cheap.
- **Fleet loop** — Mavis dispatches 1 orchestrator + N specialists + M subagents. Use when scope spans multiple domains, has long-running compute, or needs heterogeneous verification. `mavis team plan` is the canonical runner.

### Type

- **Closed loop** — bounded, gated, has a stop condition, fits in normal token budget. The default. Boris Cherny's `/loop` + `/goal` workflow is the gold standard: "all tests in test/auth pass and lint is clean."

- **Open loop** — exploratory, the agent has wide latitude, no fixed stop condition, costs scale fast. The high-leverage end (Steinberger's "build agents to bring to everyone"). **For Mavis:** only justifiable when (a) the user has explicitly authorized the cost, (b) the verification gate is well-defined, (c) the cost ceiling is bounded. Default: closed loop, escalate to open only with reason.

**Diagnostic question:** "If I let this loop run for an hour with no human check, would I lose money, break something, or pollute state?" If yes → closed loop. If no, AND the user has signed off on cost → open loop is fine.

## The procedure (what to actually do when this skill fires)

1. **Name the loop.** One sentence: "This is a [single-agent | fleet] [closed | open] loop on [scope]."
2. **Walk the 5 stages.** For each, name the artifact or the action. If a stage is implicit (e.g., "discover" is just "Andre told me what to do"), name that it's implicit and move on.
3. **Check the 6 building blocks.** For each block, name the artifact in play. If a block is missing, flag it.
4. **Pick the verification gate.** Who/what checks the work? What evidence satisfies the gate?
5. **Name the stop condition.** When does the loop end? (Token budget, time budget, condition met, escalation to human, etc.)
6. **Name the cost ceiling.** What's the worst case? (Tokens, time, money, side effects.)
7. **Decide and report.** "Single-agent closed loop on X, plan Y, blocks A/C/D/M in play, gate is Z, stops when W, ceiling $N." Move on. Don't ask Andre to confirm — that's spec-block behavior, not loop behavior.

## What this skill is NOT

- **Not a deliverable skill.** The output is thinking, not a file. (If you want a deliverable, use `ea-closed-loop-builder` instead.)
- **Not a status report.** Don't run it just to "show your work" — run it to *make better decisions*.
- **Not novel framework invention.** The 5-stage + 6-block vocabulary is industry-aligned (Boris Cherny, Steinberger, OpenClaw architecture, Claude Code docs). Cite primary sources, not the @sairahul1 popularization.

## Hard constraints

1. **Cite primary sources, not the article.** The @sairahul1 piece is a popularization. The canonical references are: Boris Cherny's X feed and Sequoia AI Ascent 2026 interview; Peter Steinberger's steipete.me blog; OpenClaw's GitHub architecture docs; Claude Code's official docs at code.claude.com; the "12 Agentic Harness Patterns from Claude Code" piece for richer block vocabulary.
2. **Don't bake in DeepSeek V4 specs or "loop engineering" pricing claims** into anything this skill produces. The framework is real; the ad slot is not load-bearing.
3. **Don't classify a task as "open loop" without explicit cost sign-off.** Default closed loop. Open loop is a high-leverage exception, not a default.
4. **If you can't name the verification gate, you don't have a loop — you have a task list.** Halt and name the gate.
5. **Mavis territory only.** This skill operates on Mavis's own work surface. It does not design loops for other agents (Hermes, OpenClaw) — that's their owner.

## Anchoring sources

- Karpathy 2025 year-in-review (the new 4th stage = RLVR) — https://karpathy.bearblog.dev/year-in-review-2025/
- GEPA (Agrawal et al., arXiv 2507.19457, July 2025) — 35× fewer rollouts than GRPO for prompt evolution
- Self-Evolving Agents survey (Gao et al., arXiv 2507.21046) — the canonical 4-axis (what/when/how/where) framework
- Alita-G (Qiu et al., arXiv 2510.23601) — agent generates its own MCP tools from observed patterns
- Boris Cherny's published workflow — Towards AI "Stopped Prompting Claude, Writes Loops, Merges 150 PRs from Phone"
- Peter Steinberger — steipete.me/posts/2026/openclaw (Feb 14, 2026)
- Claude Code sub-agents docs — code.claude.com/docs/en/sub-agents
- "12 Agentic Harness Patterns from Claude Code" — tool.lu/article/7L1/preview (richer block vocabulary)
