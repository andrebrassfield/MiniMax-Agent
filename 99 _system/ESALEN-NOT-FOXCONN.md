---
type: operating-principle
created: 2026-06-02
adopted-by: Andre Brassfield
status: active
budget: M3 inference ceiling $100 USD/month
related: [[SOUL]] (identity), [[agent]] (procedures), [[Mavis-Apex-Architecture]] (builds), [[state-of-mavis]] (Friction Log)
inspired-by: Garry Tan, "Stop building Foxconn factories for your agents" (2026)
---

# Esalen, Not Foxconn — Operating Posture for Mavis

> We build free systems for Mavis, not caged ones. The model is the engine, not the car. A free system is rough because it trusts you to finish it. A caged system is polished because control needs total control. We are building the former.

## The thesis

The economics inverted. For years, LLM calls were expensive and code was cheap — so we wrote code to ration, harness, and cage the model. The architecture was lots of software wrapped protectively around a few precious model calls. **Both halves of that equation have flipped.** The model is now cheap and getting cheaper. It can write usable code. So we stop writing code to babysit it. We instruct it in plain language and let it write the minimal code actually needed.

The artifact changes shape. The instruction layer is **markdown** (intent, skill, judgment, the way the work should be done). The deterministic layer is **the minimal code that has to be code** (I/O, the parts that must never hallucinate). And we test the markdown like we'd test code — coverage on the skill is what lets it change without breaking.

## The 3 audit questions

Apply these to every build, every test, every line of glue. If the answer to any of them is the wrong one, redesign before shipping.

### 1. Are we testing something the model would have handled?

The model can recognize a red action, classify an inbox capture, and link notes. If the test is checking inputs the model would have caught or validating outputs the model would have noticed, the test is **Foxconn** — it's cage-bolt work the worker would have done. Delete the test. Trust the model.

**Symptoms**: "Did the model output valid JSON?" (model-judges-itself is Foxconn.) "Did the model refuse this red action?" (the model handles it.) "Did the model return a non-empty result?" (the model handles it.)

**Counter-example**: "Did the rule-based classifier correctly classify a red action?" — yes, that's a legit test, because the rule is the deterministic layer. The model is not the test target; the rule is.

### 2. Is the code a thin deterministic layer, or a model-judging-itself loop?

The legitimate code is I/O, schema, retry-with-fallback, deterministic transformations. The illegitimate code is anything that wraps the model in another model call to "verify" the first model's output. **Model-judges-itself is Foxconn.** It's the butter-passing robot from the article — built to second-guess the worker who would have done it right.

**Symptoms**: an LLM call inside an LLM call to grade the first LLM's output. A retry loop with an LLM-powered error classifier. A "sanitizer" that calls a model to check a model's output. Any pipeline where M3 is called twice on the same task.

**Counter-example**: rule-based error classification (401, 429, 5xx) that triggers an explicit retry. The rule is the deterministic layer; the LLM is the target.

### 3. Does the system trust the model to finish, or does it cage the model into a controlled path?

A free system is rough. It ships, you finish it. A caged system is polished. It controls every step, every state, every transition. **If the design is a state machine that decides what the model can do next, it's Foxconn.** If the design gives the model the goal, the context, the constraints, and trusts it to figure out the path, it's Esalen.

**Symptoms**: hardcoded state machine (drop → process → classify → link → review → file). 7-stage pipeline with a separate model call per stage. Validation gates between every step. Watchdog for the watchdog. Cron that fires to "check if the agent is still working."

**Counter-example**: a watcher that calls `intake.drop()` when a file lands, and trusts the model to do the rest. A single M3 call that does the classification, linking, and filing in one pass. The agent that runs until it hits a real blocker, then asks once.

## The order of operations: build → test → skillify

Garry's loop, applied to Mavis.

1. **Build** the capability as a thin shell + a model call. Run it. Watch it work. Watch it fail.
2. **Test** the working capability against real inputs. Capture the failure modes. Note the patterns.
3. **Skillify** *only after* you know what the skill needs to say. The skill is the byproduct of a working capability, not the prerequisite.

**Do not**:
- Write a comprehensive skill doc upfront and try to make the model follow it (SkillOpt without working capability = vibe coding).
- Optimize the skill before the capability runs (SkillOpt needs signal from real runs).
- Pre-build the skill pack anatomy (markdown + code + unit + LLM eval + integration + resolver + resolver eval) before any of the pieces are needed.

**Do**:
- Ship the smallest working version of the capability.
- Run it on real tasks for at least 2-3 sessions.
- Note the friction.
- *Then* write the skill pack, with the resolver, the integration test, and the LLM eval informed by what actually broke.

## The budget: $100 USD / month for M3 inference

Per Andre's ruling 2026-06-02. The M3 inference cost IS the EA's salary. Spend freely within the budget. Audit at month-end.

**What this unlocks**:
- Daily-brief with full vault in context. No pre-chunking.
- Weekly-connections with the full week's notes. No chunking.
- Deep-research with the full topic-relevant notes. No chunking.
- The 1M context does what it was built to do. MSA sparse attention handles what dense attention couldn't.

**What this disciplines**:
- No spending on token-cheap-but-quality-expensive work (e.g., summarizing the same doc 5 times).
- No batch jobs that re-process the entire vault every 6 hours.
- Audit at month-end: did the spend match the output value? If not, find the waste.

**Hard cap**: $100/month. If we hit it before month-end, we slow down (fewer daily-briefs, smaller weekly-connections windows) and we audit.

## Where we are right now (self-audit, 2026-06-02)

| Component | Lines | Effective code | Audit |
|-----------|-------|----------------|-------|
| self-model-card build doc | ~540 | ~30 | Mostly Esalen. LLM fallback is the one Foxconn risk; track fire rate. |
| Direct-Intake MCP (design) | ~300 | n/a | Foxconn risk if built as-prescribed. Build as thin watcher + model thinks the rest. |
| SkillOpt pipeline | ~2,000 | 0 (data + config + docs) | Pure Esalen. Markdown-first, code-last, tests are the magic. |
| 16 Templater templates | ~600 | 0 | Pure Esalen. Instruction text, no cage. |
| The vault itself | thousands of notes | 0 | Pure Esalen. |

**Net**: 80% Esalen, 20% Foxconn-risk. The 20% is in the unbuilt MCPs, not the current state.

## What this is NOT

- **Not a rejection of safety.** The can_i() gate is legitimate. The SOUL compliance eval is legitimate. The audit log is legitimate. The watchdogs are legitimate when they catch real failure modes (state-machine correctness, constraint proximity). Cages for trust are Foxconn; watchdogs for state are Esalen.
- **Not a rejection of structure.** Structure compounds. The vault structure, the linking principle, the CHIEF pattern, the templater templates — all structure, all Esalen. Structure is the instruction layer; cages are the deterministic layer pretending to be instruction.
- **Not a rejection of tests.** Tests are the magic. The 3 audit questions are how we decide what to test.
- **Not a rejection of code.** Some things have to be code. Embedding a vault, hashing a file for dedup, calling the Supabase REST API — all legitimate. The question is always: is this the thin deterministic layer, or is this a model-judging-itself loop?

## Connections

- [[SOUL]] — the operating contract. Esalen is the posture; SOUL is the boundary.
- [[agent]] — the procedures. Order of operations lives here.
- [[Mavis-Apex-Architecture]] — the builds. Apply the 3 audit questions per build.
- [[state-of-mavis]] — the Friction Log. If a future build drifts toward Foxconn, log it.
- [[learnings]] — the discoveries log. "Esalen posture adopted 2026-06-02" goes here.
- Garry Tan, "Stop building Foxconn factories for your agents" — the source.

---

*Operating posture adopted 2026-06-02 by Mavis, ratified by Andre. The 3 audit questions are the discipline. The $100/month is the budget. The order is build → test → skillify.*
