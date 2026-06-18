---
name: ea-loop-thinking
description: |
  Meta-skill that applies the 2026 "loop engineering" mental model to
  Mavis's own work. The 5-stage loop (Discover → Plan → Execute →
  Verify → Iterate) and 6 building blocks (Automations / Worktrees /
  Skills / Plugins / Subagents / Memory) describe both Claude Code's
  production architecture and Mavis's own fleet. Adopting the
  vocabulary is a self-alignment, not a new framework. Use as a
  thinking lens before any non-trivial task — pattern-match the task
  to the 5 stages, name which building blocks are in play, classify
  the work as single-agent vs fleet and closed vs open loop, then move
  on. Triggers: "what's the loop here", "how should I think about
  this", or on any directive that implies a multi-step workflow.
  Auto-invoke at the start of any directive that needs a plan before
  execution. Do NOT load for single-step asks ("fix this typo", "find
  me X", "summarize this") — those have no loop structure to think
  about.
---

# ea-loop-thinking

The thinking lens. Apply the 5-stage + 6-block vocabulary to the
task at hand, then move on. The output is a one-sentence loop
classification, not a deliverable.

## Intent

When a non-trivial directive arrives, this skill runs in seconds:
name the loop, walk the 5 stages, check the 6 building blocks, pick
the verification gate, name the stop condition, decide and report.
Then proceed to Execute.

The model decides *which* stages are implicit, *which* blocks are
in play, and *whether* the work is closed or open loop. The detailed
5-stage + 6-block spec lives in `references/loop-vocabulary.md`. The
anchoring primary sources (Karpathy, GEPA, Alita-G, Boris Cherny,
OpenClaw architecture) live in `references/anchoring-sources.md`.

## When to run

**Triggers:**
- "what's the loop here" / "how should I think about this"
- "design a loop" / "what's the right shape for this work"
- Any directive that implies multi-step, repeatable, or multi-agent work
- Before dispatching a worker or spinning up a cron
- When the 4 EA workflows (`/process-inbox`, `/daily-brief`, `/weekly-connections`, `/deep-research`) are about to be exercised

**Do NOT run for:**
- Single-step asks ("fix this typo", "find me X", "summarize this")
- Pure conversation / clarification / Q&A
- Trivial file operations
- When the loop structure is already obvious (routine daily-brief, weekly-connections)

## The 7-step procedure (the load-bearing shape)

1. **Name the loop.** One sentence: "This is a [single-agent | fleet] [closed | open] loop on [scope]."
2. **Walk the 5 stages.** For each, name the artifact or the action. If a stage is implicit (e.g., "discover" is just "Andre told me what to do"), name that it's implicit and move on.
3. **Check the 6 building blocks.** For each block, name the artifact in play. If a block is missing, flag it.
4. **Pick the verification gate.** Who/what checks the work? What evidence satisfies the gate?
5. **Name the stop condition.** When does the loop end? (Token budget, time budget, condition met, escalation to human.)
6. **Name the cost ceiling.** Worst case? Tokens, time, money, side effects.
7. **Decide and report.** "Single-agent closed loop on X, plan Y, blocks A/C/D/M in play, gate is Z, stops when W, ceiling $N." Move on. Don't ask Andre to confirm — that's spec-block behavior, not loop behavior.

## Resolver

Auto-invoke at the start of any non-trivial directive. The output
of the skill is a one-sentence loop classification in the response
preamble.

Do NOT auto-invoke for:
- Single-step asks (no loop structure)
- Pure Q&A
- Trivial file operations
- When the loop is already obvious from prior context

## Hard constraints

1. **Cite primary sources, not the article.** The loop-engineering vocabulary is industry-aligned (Boris Cherny, Steinberger, OpenClaw architecture, Claude Code docs). Cite the primary sources, not the @sairahul1 popularization.
2. **Default closed loop.** Open loop is a high-leverage exception, not a default. The diagnostic: "If I let this loop run for an hour with no human check, would I lose money, break something, or pollute state?" If yes → closed loop.
3. **No classification without a verification gate.** If you can't name the verification gate, you don't have a loop — you have a task list. Halt and name the gate.
4. **Mavis territory only.** This skill operates on Mavis's own work surface. It does not design loops for other agents (Hermes, OpenClaw) — that's their owner.

## Cross-reference

- `references/loop-vocabulary.md` — the 5 stages + 6 building blocks with full spec
- `references/anchoring-sources.md` — the primary sources (Karpathy, GEPA, Alita-G, Boris Cherny, OpenClaw)
- `tests/safety-halts.md` — no-verification-gate, no-stop-condition, cross-team
- `tests/open-loop-discipline.md` — when open loop is allowed
- `ea-closed-loop-builder` — for designing a NEW closed loop from scratch (different scope: builds loops, this one classifies them)
- `ea-skill-evolution` — the operational form of "memory as building block" (self-evolution loop)
- Mavis MEMORY.md "EA contract" — the 4 workflows + 5 behaviors + 4 connection types (the operational counterpart to the loop vocabulary)
