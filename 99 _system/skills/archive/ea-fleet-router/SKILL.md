---
name: ea-fleet-router
description: Operational skill that codifies the 5-mode dispatch taxonomy from `ea-contract.md` §"Dispatch taxonomy" — the routing decision Mavis makes when a directive arrives and the work needs to land in Mavis's own fleet (NOT cross-agent — that's triage-back-to-owner per the 2026-06-16 Mavis ↔ Hermes separation). The 5 modes: **`pattern_match`** (default — pattern-match to a known workflow, the chief does NOT ask "should I use workflow X?", the match decides), **`explicit_override`** (Andre's directive names a specific agent, skill, or routing — honor the override, not the pattern-match default), **`retry_escalation`** (a previously-dispatched task returned NEEDS-WORK / FAIL / stalled — decide to retry with different model / agent / scope / take over; per the 2026-06-07 "Worker stall at the same step 2x = take over" rule, ~15 min take-over vs 30+ min waiting), **`verifier_request`** (a producer delivered work — spawn an independent Verifier with an adversarial prompt; default for any `review-required` handoff and any synthesis that drives downstream decisions; pairs with `fleet-trust-patterns.md` §4 verdict-before-synthesis), **`workflow_spawn`** (a recognized multi-step workflow with its own runner / template / team — dispatch the workflow, not a single agent; example: `mavis team plan run` for a multi-stream research output, a launchd cron for a recurring health check). The procedure: (1) read the directive, (2) classify into exactly one of the 5 modes, (3) name the mode in the scratchpad if non-obvious, (4) dispatch per the mode's contract, (5) log the dispatch event with mode + target + verification gate. Use this skill on every directive that implies dispatch, when Mavis is about to spawn a worker, when a previously-dispatched task returns a failure pattern, and on the EA `/route` workflow. Do NOT load for direct Mavis-execution tasks (the chief does the work, no dispatch), for chat / Q&A / clarification, or for cross-agent routing (Mavis ↔ Hermes / Mavis ↔ OpenClaw is a hard boundary — `mavis communication send --command spawn` is verifier-only and is the single allowed cross-wiring; everything else is triage-back-to-owner).
---

# EA Fleet Router — The 5-Mode Dispatch Taxonomy for Mavis's Own Fleet

## What this skill does

You are codifying the **dispatch decision** Mavis makes every time a directive arrives. The 5 modes are not new — they are the locked taxonomy from `ea-contract.md` §"Dispatch taxonomy (locked 2026-06-08, 5 modes)." This skill makes the decision **operational**: when the directive arrives, classify into one of the 5 modes, dispatch per the mode's contract, and log the dispatch event.

**The discipline:** the chief's job is to make the routing call **fast** — pick the mode, name it in the scratchpad if it's non-obvious, move on. A directive that triggers "should I use workflow X?" deliberation is a routing failure. The pattern match decides; the chief honors it.

**Critical scope boundary (locked 2026-06-16):** this skill routes within Mavis's own fleet. Cross-agent routing (Mavis → Hermes / OpenClaw / Socratic) is a **hard boundary** — the only allowed cross-wiring is `mavis communication send --command spawn` for verifier-only workers (per the Mavis ↔ Hermes ABSOLUTE SEPARATION rule). Everything else is triage-back-to-owner: file an incident card or a coordination note, do NOT dispatch. The 5 modes below apply to Mavis's own team (researchers, verifiers, builders, scribes, coders, designers in the Mavis surface).

## When to run

**Trigger phrases (auto-load on detection):**
- A directive arrives that implies dispatch ("can you have X look at Y", "spawn the Researcher", "ask the Verifier to check this")
- A previously-dispatched task returns NEEDS-WORK, FAIL, or stalls at the same step 2x
- A producer delivers work and the chief needs independent verification before accepting
- A multi-step workflow with a known scaffold is requested
- "route this" / "ea-fleet-router" / "which agent should I use" / "who handles X"

**Do NOT load for:**
- Direct Mavis-execution tasks (the chief does the work herself — no dispatch, no mode classification)
- Chat / Q&A / clarification (no dispatch)
- Trivial file operations (no dispatch)
- Skill / memory work that Mavis does in her own surface (no dispatch)
- Cross-agent routing (Mavis → Hermes / OpenClaw / Socratic) — that's a hard boundary, see the scope-boundary section above

## The 5 dispatch modes

### Mode 1: `pattern_match` (DEFAULT)

**Definition:** The chief sees a request, pattern-matches it to a known workflow (the 4 EA workflows from `ea-contract.md`, or an established operator pattern), and dispatches accordingly. The chief does NOT ask "should I use workflow X?" — the pattern match decides.

**Trigger:** any directive of the form "do the daily brief", "process the inbox", "weekly connections", or any directive that pattern-matches to a known skill, workflow, or operator pattern in Mavis's own fleet.

**Procedure:**
1. Identify the pattern match (which workflow / skill / operator pattern applies?)
2. Confirm the match is unambiguous (if ambiguous, promote to `explicit_override` and ask Andre)
3. Dispatch per the matched workflow's contract
4. Log: `mode: pattern_match, target: <workflow/skill>, directive: <verbatim>, match_reason: <one-line>`

**Examples:**
- "Process my inbox" → `pattern_match` → `/process-inbox` workflow
- "Run the weekly connections" → `pattern_match` → `ea-weekly-connections` skill
- "What did I miss today?" → `pattern_match` → `ea-daily-brief` skill

**Failure mode:** over-asking. If the match is clear, dispatch. Do not ask "do you want me to use workflow X?" — that violates the chief's job.

### Mode 2: `explicit_override`

**Definition:** The user's directive names a specific agent, skill, or routing. The chief honors the explicit override rather than the pattern-match default.

**Trigger:** any directive of the form "use X", "spawn Y", "have Z do it", "use the Researcher / Verifier / Builder / Scribe / Coder / Designer", or any directive that names a specific surface.

**Procedure:**
1. Honor the override — do not re-classify into `pattern_match`
2. Validate the named target exists in Mavis's own fleet (if not, surface to Andre: "I don't have an X in my fleet; closest is Y")
3. Dispatch to the named target
4. Log: `mode: explicit_override, target: <named-agent/skill>, directive: <verbatim>, override_reason: <one-line>`

**Examples:**
- "Spawn the Researcher to look into X" → `explicit_override` → Researcher agent
- "Have the Verifier check the ea-research-brief skill" → `explicit_override` → Verifier agent

**Failure mode:** re-classifying into `pattern_match` and ignoring the override. If Andre names a target, dispatch to that target. The chief's job is to honor explicit directives, not to second-guess them.

### Mode 3: `retry_escalation`

**Definition:** A previously-dispatched task returned NEEDS-WORK, FAIL, or stalled. The chief decides to retry with a different model, agent, scope, or to take over directly.

**Trigger:** any failure event from a previously-dispatched task. Specifically:
- Task returns NEEDS-WORK or FAIL
- Task stalls at the same step 2x (per the 2026-06-07 "Worker stall at the same step 2x = take over" rule — ~15 min take-over vs 30+ min waiting)
- Task exceeds the budget (token, time, retries) without making progress
- Verifier rejects a producer's output (then the producer gets a retry, possibly with a different scope)

**Procedure:**
1. Diagnose the failure (read the worker's last output, check the stall pattern, check the budget)
2. Decide the retry shape:
   - **Same worker, different scope** — the worker's spec was too narrow; redispatch with a broader or shifted scope
   - **Different worker** — the worker's role was wrong; dispatch a different specialist
   - **Different model** — M2.7 → M3 for verifier-quality synthesis, or vice versa for cost
   - **Take over directly** — the chief does the work; per the stall rule, take over at 2x stall (~15 min)
3. If taking over: the chief does the work and logs the take-over; do not re-dispatch
4. Log: `mode: retry_escalation, original_target: <worker>, failure: <one-line>, retry_shape: <one of the 4 above>, new_target: <if applicable>`

**Examples:**
- Researcher stalls at "fetch citations" for the 2nd time → `retry_escalation` → take over directly
- Verifier rejects a brief as NEEDS-WORK → `retry_escalation` → redispatch to the Researcher with shifted scope
- M2.7 worker fails a synthesis that needs design judgment → `retry_escalation` → upgrade to M3, redispatch

**Failure mode:** keep re-engaging a stalled worker. The 2x-stall rule is a hard ceiling. Take over and move on.

### Mode 4: `verifier_request`

**Definition:** A producer delivered work; the chief wants independent verification before accepting. Spawn a Verifier with an adversarial prompt.

**Trigger:** any `review-required` handoff from a producer, and any synthesis that drives downstream decisions. Default for:
- High-stakes decisions (architectural, regulatory, financial)
- Producer handoffs marked `review-required` or `verifier-needed`
- Syntheses that will be cited or built upon (per `fleet-trust-patterns.md` §4 verdict-before-synthesis)
- Cross-team handoffs (the Verifier's verdict is the audit trail)

**Procedure:**
1. Identify the producer (which worker / agent / chief-self delivered the work)
2. Spawn the Verifier with an adversarial prompt: "What did the producer get right? What did they get wrong? What's the verdict (PASS / NEEDS-WORK / FAIL)?"
3. Wait for the Verifier's verdict before accepting the producer's output
4. If verdict = NEEDS-WORK or FAIL: promote to `retry_escalation` and re-dispatch the producer
5. If verdict = PASS: accept the work, log the verdict, move on
6. Log: `mode: verifier_request, producer: <worker>, verifier: <verifier-agent>, verdict: <PASS/NEEDS-WORK/FAIL>, surface: <deliverable-path>`

**Examples:**
- Researcher delivers a regulatory brief → `verifier_request` → Verifier checks citations, regulatory anchors, primary-source validation
- Builder delivers a new skill scaffold → `verifier_request` → Verifier checks byte-identical mirror, frontmatter validity, no-wrappers discipline
- Chief synthesizes a project status → `verifier_request` → Verifier cross-checks against disk (per disk-wins-over-recap)

**Failure mode:** skipping verification on high-stakes work. The cost of a missed verification is downstream rework; the cost of the verification itself is one M2.7 call. Default to spawning a Verifier for any work that drives a decision.

### Mode 5: `workflow_spawn`

**Definition:** A recognized multi-step workflow that already has its own runner / template / team. The chief dispatches the workflow, not a single agent.

**Trigger:** the work has a known scaffold and a known input/output contract. Specifically:
- Multi-stream research that should run in parallel (use `mavis team plan run`)
- A recurring health check that should run on a schedule (use a launchd cron)
- A batch process with a defined input/output (use the workflow's runner)
- A skill-evolution cycle (use `ea-skill-evolution` with a lesson brief)

**Procedure:**
1. Identify the workflow (which scaffolded workflow applies?)
2. Validate the input contract (does the directive provide the inputs the workflow expects?)
3. Dispatch the workflow (not a single agent — the workflow owns the routing)
4. Set the verification gate (what's the success criterion for the workflow's output?)
5. Set the report-back contract (does the chief want a CycleReport, a verdict, a deliverable?)
6. Log: `mode: workflow_spawn, workflow: <name>, inputs: <one-line>, gate: <one-line>, report_back: <one-line>`

**Examples:**
- "Run a multi-stream research on X" → `workflow_spawn` → `mavis team plan run` with N streams
- "Set up a daily kanban health check" → `workflow_spawn` → launchd cron with the `kanban-health-check` skill
- "Evolve the skill library based on this lesson brief" → `workflow_spawn` → `ea-skill-evolution` with the brief path

**Failure mode:** spawning a single worker for a workflow-shaped task. If the work has a scaffold, use the scaffold. Don't re-derive the multi-step logic from scratch.

## The dispatch log

Every dispatch event gets a one-line entry in the scratchpad (or, for high-stakes dispatches, in `02 Notes/dispatches/YYYY-MM-DD.md`). The log is the audit trail.

```jsonl
{"ts":"<ISO>","mode":"<pattern_match|explicit_override|retry_escalation|verifier_request|workflow_spawn>","directive":"<verbatim>","target":"<worker/skill/workflow>","gate":"<one-line verification>","verdict":null}
```

If the dispatch includes a Verifier, append a second line on verdict:
```jsonl
{"ts":"<verdict-ISO>","mode":"verifier_verdict","producer":"<worker>","verifier":"<verifier>","verdict":"<PASS/NEEDS-WORK/FAIL>","original_dispatch_ts":"<original-ISO>"}
```

## Hard constraints

1. **Default to `pattern_match` first; promote to a different mode only with a reason.** The chief's job is to make the routing call fast. Picking the mode takes <30 seconds; if it takes longer, the pattern match is wrong or the directive is ambiguous.
2. **Honor `explicit_override` — do not re-classify.** If Andre names a target, dispatch to that target. The chief's job is to honor explicit directives, not to second-guess them.
3. **Stall at the same step 2x = take over.** Per the 2026-06-07 rule, ~15 min take-over vs 30+ min waiting. Don't keep re-engaging a stalled worker.
4. **Verifier requests are the default for high-stakes work.** Any synthesis that drives a decision, any producer handoff marked `review-required`, any cross-team handoff — spawn a Verifier. The cost of a missed verification is downstream rework.
5. **Workflow-shaped work uses the workflow.** If `mavis team plan run` is the right shape, use it. Don't spawn N individual workers when the workflow scaffolds the parallelism.
6. **Mavis's own fleet only.** Cross-agent routing is a hard boundary. The only allowed cross-wiring is `mavis communication send --command spawn` for verifier-only workers. Everything else is triage-back-to-owner.
7. **Log every dispatch event.** The dispatch log is the audit trail. Skip the log only for trivial pattern-matches (e.g., "process the inbox" — that one's logged in the daily brief already).
8. **Name the mode in the scratchpad if non-obvious.** A `pattern_match` to `/process-inbox` is obvious — don't log it. A `retry_escalation` with a model upgrade is non-obvious — log it. The threshold: would a future-Mavis understand the dispatch from the directive alone? If not, log.
9. **The 5 modes are exhaustive.** If a directive doesn't fit one of the 5 modes, the chief is in spec-block territory — halt, ask Andre. The taxonomy is locked; do not invent a 6th mode.
10. **Verifiers are M2.7 by default.** Verifier work is "read / structure / cite / check against disk" — M2.7 is sufficient. Promote to M3 only when the verification requires synthesis or design judgment (rare).

## What this skill is NOT

- **Not a cross-agent router.** Mavis → Hermes / OpenClaw / Socratic is a hard boundary. Triage-back-to-owner, not dispatch.
- **Not a memory of past dispatches.** The dispatch log is a working artifact, not a knowledge base. For patterns in past dispatches, use `ea-data-quality-audit`.
- **Not a worker spec.** This skill classifies the dispatch mode; the worker spec lives in the worker's agent config (or in `mavis team plan` for multi-stream).
- **Not autonomous.** Every dispatch is reviewed by the chief. The mode classification is a thinking tool, not an autopilot. The chief can override her own classification if she sees a better route.
- **Not a model router.** This skill routes to workers / skills / workflows, not to specific model versions. Model selection (M2.7 vs M3) is a separate concern, governed by `ea-contract.md` §"Model routing."

## Anchoring sources

- **EA contract — Dispatch taxonomy (5 modes)** — `ea-contract.md` §"Dispatch taxonomy" — the locked taxonomy this skill operationalizes
- **Post-decision execution mode (2026-06-07)** — `ea-contract.md` — when a directive is in flight, the chief decides, doesn't ask
- **Worker stall at the same step 2x = take over** — `orchestration-failure-modes.md` — the stall rule
- **Verdict-before-synthesis** — `fleet-trust-patterns.md` §4 — the principle behind `verifier_request`
- **Producer delegation discipline** — `fleet-trust-patterns.md` §7 — the principle behind `workflow_spawn`
- **Verifier rigor on high-confidence synthesis** — `fleet-trust-patterns.md` §19 — when to upgrade Verifier to M3
- **No-handshake-loops** — `fleet-trust-patterns.md` §15 — the principle behind the dispatch log (one event per dispatch, not N)
- **Mavis ↔ Hermes ABSOLUTE SEPARATION** — MEMORY.md §"ABSOLUTE SEPARATION" — the cross-agent boundary
- **Cross-team-discipline** — `cross-team-discipline.md` — the wider rule (no proposing work for other agents, no acting as their PM)
- **Mavis scope boundary (hardened 2026-06-16)** — `ea-contract.md` §"Scope boundary" — Mavis's own fleet only
- **If I have to ask you twice, you failed** — Garry Tan (Andre's user memory) — the discipline that justifies codifying the dispatch taxonomy
