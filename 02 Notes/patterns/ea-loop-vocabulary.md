---
description: "The 5-stage loop + 6 building blocks + 2 axes (scale/type) spec — the load-bearing vocabulary ea-loop-thinking applies as a thinking lens. Read when classifying a non-trivial Mavis task, designing a closed/open loop, or auditing whether a work surface has all 6 blocks. Moved from skill-local references 2026-06-22 as part of Upgrade 1 skill-scaling-law refactor."
source: ~/.mavis/agents/mavis/skills/ea-loop-thinking/references/loop-vocabulary.md
---

# Loop Vocabulary — ea-loop-thinking

The 5 stages + 6 building blocks + 2 axes (scale/type) that describe
every loop. This is the spec; the model applies it as a thinking lens.

## The 5 stages (load-bearing — do not reorder)

### 1. DISCOVER
What is actually being asked? What does "done" look like? What
constraints exist (Andre's mode, time budget, available skills,
cost)? What information is already in vault/memory that bears on this?

**Failure mode:** skipping discovery and jumping to execution. The
single most common loop failure. Mavis's memory: "Spec blocks = design
review" — discovery is the spec-block phase for any non-trivial task.

**Mavis analog:** read `00 Inbox/`, scan `01 Daily/`, check memory
entries, check scratchpad. Before dispatch, do you have enough to
dispatch well?

### 2. PLAN
Break the discovered scope into atomic steps. Name the dependencies.
Identify the verification gate. Identify the stop condition.

**Failure mode:** plan so granular the plan takes longer than the
work. Or plan so loose the verification gate is ambiguous.

**Mavis analog:** `todowrite` is the plan surface. The plan should
name: which subagent (if any) does what, what the deliverable looks
like, what counts as "verified."

### 3. EXECUTE
Do the work. Single-agent or fleet. Use the building blocks (see below).

**Failure mode:** re-planning mid-execution without good reason. The
plan is a contract; revising it mid-flight is fine *if you surface
the change*, otherwise it's drift.

### 4. VERIFY
Independent check that the work meets the goal. **Maker ≠ checker**
(Boris Cherny's load-bearing rule). Use a different model / agent /
human for the gate.

**Failure mode:** the executing agent grading its own work. Or no
verification at all ("looks good to me"). Mavis's memory: "Disk
wins over recap" — verification must hit disk, not just memory.

**Mavis analog:** `verifier` agent for handoffs, `gepa-evaluator` for
code/skill outputs, kanban fast-path bug check for cron/loop work,
`agent-disease-detector` for fleet health.

### 5. ITERATE
Fix the gap between the verification result and the goal. Re-loop
until verification passes. Then stop.

**Failure mode:** infinite loop without a stop condition. Or stopping
before verification (the goal is met by the agent's claim, not by
check). Always pair iteration with a stop condition.

## The 6 building blocks (load-bearing — these are Mavis's actual primitives)

| Block | What it does | Mavis's instantiation | Claude Code parallel |
|---|---|---|---|
| **Automations** | Triggers discovery; the heartbeat | `mavis cron`, launchd scheduled tasks | `/loop`, `/goal` |
| **Worktrees** | Parallel execution without collision | `mavis team plan` parallel streams; per-worker isolated scratchpads | git worktrees, branch-per-agent |
| **Skills** | Project knowledge that compounds every run | `~/.mavis/agents/mavis/skills/`, `99 _system/skills/` | `~/.claude/skills/` |
| **Plugins / Connectors** | Loop acts in real environment, not just filesystem | MCP servers (matrix, playwright, kanban, cu, trash) | MCP servers |
| **Subagents** | Maker ≠ checker | `mavis communication send --command spawn` workers (researcher, verifier, scribe) | sub-agents, Task tool |
| **Memory** | Loop never forgets between runs | `~/.mavis/agents/mavis/memory/MEMORY.md` + topic files; vault `02 Notes/`; kanban as operational memory | CLAUDE.md, auto-memory |

**If a work surface is missing one of these, the loop has a hole.**
The diagnostic: for each block, name the artifact. If you can't, the
block isn't really in play.

## The 2 axes: scale and type

### Scale

- **Single-agent loop** — Mavis does all 5 stages solo. Use when
  scope is small, well-defined, and the verification gate is cheap.
- **Fleet loop** — Mavis dispatches 1 orchestrator + N specialists +
  M subagents. Use when scope spans multiple domains, has long-running
  compute, or needs heterogeneous verification. `mavis team plan` is
  the canonical runner.

### Type

- **Closed loop** — bounded, gated, has a stop condition, fits in
  normal token budget. The default. Boris Cherny's `/loop` + `/goal`
  workflow is the gold standard: "all tests in test/auth pass and
  lint is clean."
- **Open loop** — exploratory, the agent has wide latitude, no fixed
  stop condition, costs scale fast. The high-leverage end
  (Steinberger's "build agents to bring to everyone"). **For Mavis:**
  only justifiable when (a) the user has explicitly authorized the
  cost, (b) the verification gate is well-defined, (c) the cost
  ceiling is bounded. Default: closed loop, escalate to open only
  with reason.

**Diagnostic question:** "If I let this loop run for an hour with no
human check, would I lose money, break something, or pollute state?"
If yes → closed loop. If no, AND the user has signed off on cost →
open loop is fine.

## The diagnostic checklist (run when classifying a new task)

- [ ] What stage is the work entering at? (Usually Discover.)
- [ ] Which blocks are in play? (Usually Memory + Skills at minimum.)
- [ ] What's the verification gate? (If can't name it → halt.)
- [ ] What's the stop condition? (If can't name it → halt.)
- [ ] What's the cost ceiling? (If unbounded → closed loop by default.)
- [ ] Is this single-agent or fleet? (Hint: if it spans >2 domains or
      has long-running compute, fleet.)
