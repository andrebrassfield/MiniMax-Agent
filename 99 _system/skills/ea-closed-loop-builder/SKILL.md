---
name: ea-closed-loop-builder
description: Operational skill that produces a closed-loop spec for a recurring workflow. A closed loop is a bounded, gated, affordable loop with a named stop condition — the right default for any recurring Mavis work (daily checks, weekly audits, fleet health, content publishing, etc.). The output is a markdown spec with five sections: **Goal** (precise done condition) / **Context** (VISION.md, ARCHITECTURE.md, RULES.md references) / **Action** (atomic steps the agent actually takes) / **Feedback** (verification gate — tests, type checks, linters, structured errors, human reviews) / **Stop condition** (what tells the loop it's done). Triggers when Andre says "automate this", "build a loop for X", "set up a recurring check on Y", "make this run weekly", "I keep doing this by hand", or when a pattern is identified in `ea-data-quality-audit` as recurring manual work. Anchored in Boris Cherny's /loop + /goal pattern: "all tests in test/auth pass and lint is clean" is the gold standard for a tight, testable stop condition. Do NOT load for one-off tasks, for human-only workflows, or for loops that need open-ended exploration (use `ea-loop-thinking` for those).
---

# EA Closed-Loop Builder — Spec for a Recurring Workflow

## What this skill does

You produce a **closed-loop spec** for a recurring Mavis workflow. A closed loop is:
- **Bounded** — clear scope, defined inputs, defined outputs
- **Gated** — verification step before "done" is reported
- **Affordable** — token/time/money ceiling is named
- **Stoppable** — explicit condition for when the loop ends

The spec is a markdown file that becomes the basis for a cron, a recurring dispatch, or a one-shot-but-idempotent script. The 5-section format is load-bearing — the section names match what Claude Code's `/loop` and `/goal` consume, and what OpenClaw's loop detector expects.

## When to run

**Trigger phrases:**
- "automate this" / "make this run on a schedule"
- "build a loop for X" / "set up a recurring check on Y"
- "I keep doing this by hand" / "this should be a cron"
- "weekly audit of Z" / "daily check on W"
- When a pattern shows up 3+ times in `01 Daily/` (per `ea-data-quality-audit` / `vault-30day-auditor`)

**Do NOT run for:**
- One-off tasks (use `ea-loop-thinking` to think, then execute)
- Human-only workflows (a closed loop requires an agent executor)
- Open-ended exploration (a closed loop is bounded; open loops use `ea-loop-thinking` to design instead)
- When the verification gate can't be defined — halt and surface, don't ship a loop without a gate

## The 5-section spec format (load-bearing)

The output file is a markdown document with these five sections, in this order, with these exact names. Each section has a defined purpose and a defined minimum content.

### Section 1: GOAL

**Purpose:** name what "done" looks like, precisely.

**Minimum content:**
- The outcome the loop produces (one sentence)
- The user-visible deliverable (where it lands, who reads it)
- The success criterion (what evidence = done)

**Anti-patterns to avoid:**
- Vague goals ("improve X", "monitor Y", "make sure Z is good")
- Goals that include the loop's own execution ("check daily", "run weekly" — that's the cadence, not the goal)
- Goals that conflate action and outcome ("audit the vault" is the action; "the audit report exists at <path> with PASS/WARN/FAIL per dimension" is the outcome)

### Section 2: CONTEXT

**Purpose:** name the persistent knowledge the loop reads on every run. The agent should not re-derive this from scratch.

**Minimum content:**
- **VISION.md reference** — what "good" looks like in this domain (link to file or quote the key sentence)
- **ARCHITECTURE.md reference** — what the system being monitored/acted-on looks like (link to file or summarize the structure)
- **RULES.md reference** — what the loop is never allowed to do (hard constraints, anti-patterns, "we don't do this because of that incident")

**Anti-patterns:**
- Putting all context inline in the spec — that's what VISION.md/ARCHITECTURE.md/RULES.md are for
- Omitting RULES.md — the loop will eventually violate an unwritten rule
- Linking to files that don't exist — disk is ground truth; missing context files are a halt condition

### Section 3: ACTION

**Purpose:** the atomic steps the executor takes on every run. Should be small enough to verify, large enough to be meaningful.

**Minimum content:**
- Numbered steps
- Each step has a clear input and output
- Steps are idempotent (running the loop twice doesn't break state)
- The minimum data the loop needs (file paths, env vars, API endpoints)

**Anti-patterns:**
- Steps that depend on unstated global state ("use the latest data" — which data? from where?)
- Steps with side effects that aren't named ("save to disk" — what disk, what path, what format?)
- Steps that include the verification gate — that's section 4, separate on purpose

### Section 4: FEEDBACK (the verification gate)

**Purpose:** the independent check that the action's output meets the goal. The maker is not the checker. This is the load-bearing section.

**Minimum content:**
- Who/what verifies (a different model, a different agent, a script, a human, a benchmark)
- What evidence counts as "verified" (file on disk, exit code 0, test passing, human thumbs-up)
- How often verification runs (every loop iteration, every N runs, on a sample)
- What happens on FAIL — does the loop retry, escalate, or halt?

**Anti-patterns:**
- The executor self-verifying ("I did the work and it looks right")
- Verification with no defined FAIL path (a gate that can't fail is a placebo)
- Verification that requires expensive human time on every run (use sampling)
- Verification gate that depends on the same model as the executor (Boris Cherny's load-bearing rule: "the maker is too nice grading its own homework")

**Strong patterns (rank-ordered):**
1. **Auto-verifiable** — tests, type checks, linters, schema validators, exit codes
2. **Cross-model verifier** — different model grades the work (e.g., M3 verifier for M2.7 executor)
3. **Cross-agent verifier** — different agent with different instructions
4. **Sampled human review** — 1 in 10 runs gets a human check
5. **Pre-commit hook** — verifier runs before the work is accepted into the trunk

### Section 5: STOP CONDITION

**Purpose:** name the explicit end-of-loop trigger. Without this, the loop runs until someone gets tired of it.

**Minimum content:**
- The trigger ("when all tests in test/auth pass and lint is clean", "when the report is written to <path>", "when N consecutive runs hit PASS")
- The cleanup (what state to leave behind when the loop ends)
- The escalation (what happens if the stop condition can't be met within the cost ceiling)

**Anti-patterns:**
- "Run forever" or "until told to stop" — not a stop condition
- A stop condition that requires expensive detection (the loop should be able to cheaply check)
- No escalation — every loop will eventually hit a cost ceiling; name what happens

## Output format

The spec is a single markdown file, written to `03 Projects/Mavis EA Design/loops/<loop-name>-spec.md` (or to a project-specific path if Andre specifies). Structure:

```markdown
# Closed-Loop Spec: [loop name]

**Owner:** Mavis (EA) | [or: worker name]
**Created:** [date]
**Cadence:** [cron / one-shot / on-demand]
**Cost ceiling:** [tokens, time, money per run]
**Verdict on first run:** [PASS / WARN / FAIL with one-line reason]

---

## 1. GOAL
[one-sentence outcome]
[user-visible deliverable]
[success criterion]

## 2. CONTEXT
**VISION:** [link or quote]
**ARCHITECTURE:** [link or summary]
**RULES:** [link or list]

## 3. ACTION
1. [step with input + output]
2. [step with input + output]
3. ...

## 4. FEEDBACK
- **Verifier:** [who/what]
- **Evidence:** [what counts as verified]
- **Frequency:** [every run / every N / sample]
- **On FAIL:** [retry / escalate / halt]

## 5. STOP CONDITION
- **Trigger:** [what tells the loop it's done]
- **Cleanup:** [state to leave behind]
- **Escalation:** [what happens if cost ceiling hit]
```

## The procedure

1. **Name the recurring pattern.** One sentence: "This loop exists because [recurring work] happens [cadence] and the cost of doing it by hand is [cost]."
2. **Write the goal.** Most important section. If you can't write a precise goal, the loop isn't ready — halt and ask.
3. **Write the context.** The three V/A/R files. If they don't exist, either point at the closest existing file OR write them first (a loop without V/A/R is fragile).
4. **Write the action.** Atomic, idempotent, named. No "and then we'll see" steps.
5. **Write the feedback.** The gate. This is the section that prevents the loop from shipping slop. Boris Cherny's pattern: a different model decides if the loop is done.
6. **Write the stop condition.** Plus cleanup plus escalation. Every loop has a budget; name what happens at the budget.
7. **Sanity-check the 5 sections.** For each, can the executor run this without asking Andre a clarifying question? If any section requires a follow-up question, the spec is incomplete.
8. **Decide and report.** File goes to the right path. Andre gets a 3-line summary (goal, cadence, verifier). Move on.

## Hard constraints

1. **No spec ships without a feedback section.** A loop without a verification gate is a task list, not a loop. Halt and surface.
2. **The verifier is never the executor.** Same model with a different prompt is not a verifier. Use a different agent, a different model, or a script.
3. **Cost ceiling is named upfront.** If you can't estimate a ceiling, the loop is open-ended — use `ea-loop-thinking` to think, don't ship as closed loop.
4. **Disk is ground truth.** All VISION/ARCHITECTURE/RULES references must resolve to actual files. If they don't, halt and surface.
5. **Mavis territory only.** Closed-loop specs are for Mavis-side work. For other agents' loops (Hermes, OpenClaw), the right move is to surface the pattern and let the owner build the spec. Per cross-team-discipline: don't write other teams' specs.

## Anchoring sources

- Boris Cherny's /loop + /goal workflow (Towards AI, Sequoia AI Ascent 2026)
- Claude Code `/loop` and `/goal` slash commands (code.claude.com)
- "12 Agentic Harness Patterns from Claude Code" (tool.lu/article/7L1) — for the architecture the loop sits in
- Garry Tan's "if I have to ask you twice, you failed" rule — the discipline that justifies writing a loop in the first place (Andre's user memory)
- `ea-loop-thinking` — run this first to think through the loop's shape
- `ea-loop-audit` — run this on the first 1-2 executions to verify the loop runs correctly
