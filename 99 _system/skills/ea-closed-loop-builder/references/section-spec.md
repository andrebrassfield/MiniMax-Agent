# Section Spec — ea-closed-loop-builder

The 5 sections, each with purpose, minimum content, and
anti-patterns. The deterministic content for the spec format.

---

## Section 1: GOAL

**Purpose:** name what "done" looks like, precisely. Most
important section. If you can't write a precise goal, the
loop isn't ready — HALT and ask.

**Minimum content:**
- The outcome the loop produces (one sentence)
- The user-visible deliverable (where it lands, who reads it)
- The success criterion (what evidence = done)

**Anti-patterns to avoid:**
- Vague goals ("improve X", "monitor Y", "make sure Z is good")
- Goals that include the loop's own execution ("check daily",
  "run weekly" — that's the cadence, not the goal)
- Goals that conflate action and outcome ("audit the vault" is
  the action; "the audit report exists at <path> with PASS/
  WARN/FAIL per dimension" is the outcome)

---

## Section 2: CONTEXT

**Purpose:** name the persistent knowledge the loop reads on
every run. The agent should not re-derive this from scratch.

**Minimum content:**
- **VISION.md reference** — what "good" looks like in this
  domain (link to file or quote the key sentence)
- **ARCHITECTURE.md reference** — what the system being
  monitored/acted-on looks like (link to file or summarize
  the structure)
- **RULES.md reference** — what the loop is never allowed to
  do (hard constraints, anti-patterns, "we don't do this
  because of that incident")

**Anti-patterns:**
- Putting all context inline in the spec — that's what
  VISION/ARCHITECTURE/RULES files are for
- Omitting RULES.md — the loop will eventually violate an
  unwritten rule
- Linking to files that don't exist — disk is ground truth;
  missing context files are a HALT condition

---

## Section 3: ACTION

**Purpose:** the atomic steps the executor takes on every
run. Should be small enough to verify, large enough to be
meaningful.

**Minimum content:**
- Numbered steps
- Each step has a clear input and output
- Steps are idempotent (running the loop twice doesn't break
  state)
- The minimum data the loop needs (file paths, env vars, API
  endpoints)

**Anti-patterns:**
- Steps that depend on unstated global state ("use the latest
  data" — which data? from where?)
- Steps with side effects that aren't named ("save to disk" —
  what disk, what path, what format?)
- Steps that include the verification gate — that's section 4,
  separate on purpose

---

## Section 4: FEEDBACK (the verification gate)

**Purpose:** the independent check that the action's output
meets the goal. The maker is not the checker. This is the
**load-bearing section**.

**Minimum content:**
- Who/what verifies (a different model, a different agent, a
  script, a human, a benchmark)
- What evidence counts as "verified" (file on disk, exit
  code 0, test passing, human thumbs-up)
- How often verification runs (every loop iteration, every N
  runs, on a sample)
- What happens on FAIL — does the loop retry, escalate, or
  halt?

**Anti-patterns:**
- The executor self-verifying ("I did the work and it looks
  right")
- Verification with no defined FAIL path (a gate that can't
  fail is a placebo)
- Verification that requires expensive human time on every
  run (use sampling)
- Verification gate that depends on the same model as the
  executor (Boris Cherny's load-bearing rule: "the maker is
  too nice grading its own homework")

**Strong patterns (rank-ordered)** in
`references/strong-patterns.md`:
1. Auto-verifiable (tests, type checks, linters, schema
   validators, exit codes)
2. Cross-model verifier (different model grades the work)
3. Cross-agent verifier (different agent with different
   instructions)
4. Sampled human review (1 in 10 runs)
5. Pre-commit hook (verifier runs before the work is accepted)

---

## Section 5: STOP CONDITION

**Purpose:** name the explicit end-of-loop trigger. Without
this, the loop runs until someone gets tired of it.

**Minimum content:**
- The trigger ("when all tests in test/auth pass and lint is
  clean", "when the report is written to <path>", "when N
  consecutive runs hit PASS")
- The cleanup (what state to leave behind when the loop
  ends)
- The escalation (what happens if the stop condition can't
  be met within the cost ceiling)

**Anti-patterns:**
- "Run forever" or "until told to stop" — not a stop condition
- A stop condition that requires expensive detection (the
  loop should be able to cheaply check)
- No escalation — every loop will eventually hit a cost
  ceiling; name what happens
