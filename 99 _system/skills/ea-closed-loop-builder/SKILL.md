---
name: ea-closed-loop-builder
description: |
  Operational skill that produces a closed-loop spec for a recurring workflow.
  A closed loop is bounded, gated, affordable, and stoppable — the right
  default for any recurring Mavis work. The output is a markdown spec with
  5 sections: **Goal** (precise done condition) / **Context** (VISION /
  ARCHITECTURE / RULES references) / **Action** (atomic steps) / **Feedback**
  (verification gate — tests, type checks, linters, structured errors, human
  reviews) / **Stop condition** (what tells the loop it's done). Triggers:
  Andre says "automate this", "build a loop for X", "set up a recurring check
  on Y", "make this run weekly", "I keep doing this by hand", OR when a
  pattern shows up 3+ times in `01 Daily/`. Anchored in Boris Cherny's /loop
  + /goal pattern: "all tests in test/auth pass and lint is clean" is the
  gold standard for a tight, testable stop condition. Do NOT load for
  one-off tasks, human-only workflows, or open-ended exploration (use
  `ea-loop-thinking` for those). Mavis territory only.
---

# ea-closed-loop-builder

The 5-section spec writer for recurring Mavis workflows. The
section names match what Claude Code's `/loop` and `/goal`
consume, and what OpenClaw's loop detector expects. The format
is load-bearing — the spec becomes the basis for a cron, a
recurring dispatch, or a one-shot-but-idempotent script.

## When to run

**Triggers:**
- "automate this" / "make this run on a schedule"
- "build a loop for X" / "set up a recurring check on Y"
- "I keep doing this by hand" / "this should be a cron"
- "weekly audit of Z" / "daily check on W"
- When a pattern shows up 3+ times in `01 Daily/` (per
  `ea-data-quality-audit` / `vault-30day-auditor`)

**Do NOT run for:**
- One-off tasks (use `ea-loop-thinking` to think, then execute)
- Human-only workflows (closed loop requires an agent executor)
- Open-ended exploration (closed loop is bounded; open loops use
  `ea-loop-thinking` to design)
- When the verification gate can't be defined — HALT and
  surface, don't ship a loop without a gate
- Other agents' loops (cross-team discipline: state the
  pattern, let the owner build the spec)

## The 5-section spec format (load-bearing)

The output file is a markdown document with these five sections,
in this order, with these exact names. Each section has a
defined purpose and a defined minimum content. Full per-section
spec (purpose, minimum content, anti-patterns, strong patterns)
in `references/section-spec.md`.

### 1. GOAL
**Purpose:** name what "done" looks like, precisely. Most
important section. If you can't write a precise goal, the
loop isn't ready — HALT and ask.

### 2. CONTEXT
**Purpose:** name the persistent knowledge the loop reads on
every run. The agent should not re-derive this from scratch.

**Required:** VISION / ARCHITECTURE / RULES references. Disk
is ground truth; missing context files are a HALT condition.

### 3. ACTION
**Purpose:** the atomic steps the executor takes on every
run. Idempotent, named, with clear input + output per step.

### 4. FEEDBACK (the verification gate)
**Purpose:** the independent check that the action's output
meets the goal. The maker is not the checker. This is the
**load-bearing section**.

**Required:** who verifies, what evidence counts, frequency,
on-FAIL path. Anti-pattern: the executor self-verifying.

### 5. STOP CONDITION
**Purpose:** name the explicit end-of-loop trigger. Without
this, the loop runs until someone gets tired of it.

**Required:** trigger + cleanup + escalation. Every loop has
a budget; name what happens at the budget.

## Output format

The spec is a single markdown file, written to
`03 Projects/Mavis EA Design/loops/<loop-name>-spec.md` (or to
a project-specific path if Andre specifies). Template in
`references/spec-template.md`. File frontmatter:

```markdown
# Closed-Loop Spec: [loop name]

**Owner:** Mavis (EA) | [or: worker name]
**Created:** [date]
**Cadence:** [cron / one-shot / on-demand]
**Cost ceiling:** [tokens, time, money per run]
**Verdict on first run:** [PASS / WARN / FAIL with one-line reason]
```

## The procedure

1. **Name the recurring pattern.** One sentence: "This loop
   exists because [recurring work] happens [cadence] and the
   cost of doing it by hand is [cost]."
2. **Write the goal.** Most important section. If you can't
   write a precise goal → HALT and ask.
3. **Write the context.** The three V/A/R files. If they
   don't exist, either point at the closest existing file OR
   write them first (a loop without V/A/R is fragile).
4. **Write the action.** Atomic, idempotent, named. No "and
   then we'll see" steps.
5. **Write the feedback.** The gate. This is the section that
   prevents the loop from shipping slop. Boris Cherny's
   pattern: a different model decides if the loop is done.
6. **Write the stop condition.** Plus cleanup plus escalation.
   Every loop has a budget; name what happens at the budget.
7. **Sanity-check the 5 sections.** For each, can the
   executor run this without asking Andre a clarifying
   question? If any section requires a follow-up question, the
   spec is incomplete.
8. **Decide and report.** File goes to the right path. Andre
   gets a 3-line summary (goal, cadence, verifier). Move on.

## Hard constraints

1. **No spec ships without a feedback section.** A loop
   without a verification gate is a task list, not a loop.
   HALT and surface.
2. **The verifier is never the executor.** Same model with a
   different prompt is not a verifier. Use a different agent,
   a different model, or a script. Boris Cherny's load-bearing
   rule: "the maker is too nice grading its own homework."
3. **Cost ceiling is named upfront.** If you can't estimate
   a ceiling, the loop is open-ended — use `ea-loop-thinking`
   to think, don't ship as closed loop.
4. **Disk is ground truth.** All VISION/ARCHITECTURE/RULES
   references must resolve to actual files. If they don't,
   HALT and surface.
5. **Mavis territory only.** Closed-loop specs are for
   Mavis-side work. For other agents' loops (Hermes,
   OpenClaw), the right move is to surface the pattern and
   let the owner build the spec. Per cross-team-discipline:
   don't write other teams' specs.

## When the spec HALTs

Halt and escalate to Andre when:
- The recurring work is too rare to justify a loop
  (cost-of-automation > cost-of-manual)
- The verification gate can't be defined (no auto-check
  available, no different model/agent to be the verifier)
- The cost ceiling can't be estimated (the loop is open-ended)
- The V/A/R references don't resolve to disk files
- The spec would require Andre to clarify a fundamental
  decision (what to optimize, who owns the loop, what
  triggers the loop)

The spec is a design artifact, not an authorization to
deploy. The operator decides whether to build the loop.

## Anchoring sources

- Boris Cherny's /loop + /goal workflow (Towards AI, Sequoia
  AI Ascent 2026)
- Claude Code `/loop` and `/goal` slash commands (code.claude.com)
- "12 Agentic Harness Patterns from Claude Code" (tool.lu/article/7L1)
  — for the architecture the loop sits in
- Garry Tan's "if I have to ask you twice, you failed" rule —
  the discipline that justifies writing a loop in the first
  place (Andre's user memory)
- `ea-loop-thinking` — run this first to think through the
  loop's shape
- `ea-loop-audit` — run this on the first 1-2 executions to
  verify the loop runs correctly

## Cross-reference

- `references/section-spec.md` — per-section purpose, minimum
  content, anti-patterns
- `references/spec-template.md` — the full markdown template
- `references/strong-patterns.md` — rank-ordered verifier
  patterns (auto → cross-model → cross-agent → sampled human →
  pre-commit)
- `tests/spec-completeness.md` — 5-section sanity check
- `tests/verifier-discipline.md` — verifier ≠ executor check
- `ea-loop-thinking` — design before building
- `ea-loop-audit` — verify the loop runs correctly
- `ea-data-quality-audit` — find the recurring patterns
