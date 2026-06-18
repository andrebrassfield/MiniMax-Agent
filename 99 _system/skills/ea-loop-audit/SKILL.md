---
name: ea-loop-audit
description: Diagnostic skill that audits an in-flight or recently-completed task against the 5-stage loop (Discover → Plan → Execute → Verify → Iterate), 6 building blocks (Automations / Worktrees / Skills / Plugins / Subagents / Memory), and the closed-vs-open-loop classification. Use it BEFORE reporting "done" on any non-trivial task, and as a self-check when Andre says "audit this", "what did I miss", "did the loop actually run", or "is this verified". Output is a short PASS / WARN / FAIL per dimension with one-line evidence. If any dimension FAILS, the skill proposes the minimum fix. Triggers on task completion, on a "is this right" check, and on any reported symptom of drift (recap-vs-disk mismatch, missing verification, no stop condition, infinite re-loop). Do NOT load for trivial tasks with one verification step ("send the message", "find the file") — the loop audit is overhead there. Agent-neutral: works for Mavis-side work, but the framework applies to any loop owner.
---

# EA Loop Audit — Did the Loop Actually Run?

## What this skill does

You audit a piece of work (your own or someone else's) against the 5-stage loop + 6 building blocks framework from `ea-loop-thinking`. The audit is a **checklist, not a re-investigation**. For each dimension, you name PASS / WARN / FAIL with one line of evidence, and if FAIL, you name the minimum fix.

**The point:** the gap between "I did the work" and "the loop ran correctly" is where most failures live. This skill closes that gap before reporting done.

## When to run

**Trigger phrases:**
- "audit this" / "audit the work" / "what did I miss"
- "did the loop actually run" / "is this verified"
- "is this right" / "does this pass"
- Before reporting a multi-step task complete (in-session discipline)
- On a reported symptom: recap-vs-disk mismatch, missing verification, no stop condition, infinite re-loop, "looks good to me" without evidence
- On a handoff (producer → chief, worker → chief) where the chief is deciding whether to accept

**Do NOT run for:**
- Trivial single-step tasks (one verification step is enough)
- Pure conversational asks
- When the work is "I read X" — reading is a step, not a loop
- When the loop is in flight and not yet at the verify stage (don't audit mid-execute; audit at iteration boundaries)

## Inputs

| Input | Default | Required |
|---|---|---|
| The work to audit | (none — must be specified or implied) | yes |
| Original directive | (inferred from context) | no |
| Audit depth | "standard" (5 stages + 6 blocks + closed/open) | no — "deep" adds the 5-mistakes cross-check from `ea-5-mistakes-audit` |
| Output location | in-session report (no file) | no — pass `--write <path>` to persist |

## The audit dimensions (in order)

### Dimension 1: Discovery happened

**Question:** Did the worker actually understand what was being asked? Is there evidence the discovery stage ran, or is the work based on the worker's assumption of intent?

**Evidence:** The original directive is in the session log. The worker's first action was either to (a) clarify with the user, (b) read relevant context, or (c) start executing without clarification. (c) on a non-trivial task is FAIL.

**PASS:** directive was read, relevant vault/memory was consulted, scope was named before execution
**WARN:** directive was read, but no context load happened
**FAIL:** worker executed on assumed intent; no evidence of scope discovery

### Dimension 2: Plan was explicit

**Question:** Is there a `todowrite` (or equivalent) that names the steps, dependencies, and verification gate?

**PASS:** todos exist, named, ordered, with at least one verification-gate step
**WARN:** mental plan only, no todo surface
**FAIL:** no plan, work was sequential improvisation

### Dimension 3: Execution used the right building blocks

**Question:** For each of the 6 building blocks (Automations / Worktrees / Skills / Plugins / Subagents / Memory), is the block either in play or correctly absent?

**PASS:** for each block, the artifact is named (or named as correctly absent)
**WARN:** some blocks are ambiguous (e.g., "I used skills" without naming which)
**FAIL:** a block that should have been in play is missing (e.g., the verification gate was the executor's own claim, no subagent, no verifier)

### Dimension 4: Verification was independent

**Question:** Did a different model / agent / human check the work? Or is the worker grading its own homework?

**PASS:** verifier, disk re-read, independent re-run, or human-in-the-loop sign-off
**WARN:** verification was performed by the same model that executed, with a different prompt
**FAIL:** no verification, or "looks good to me" without evidence on disk

**Critical for Mavis:** "Disk wins over recap" (memory). If the verification is a recap rather than a disk hit, it's WARN, not PASS.

### Dimension 5: Stop condition was hit, not just claimed

**Question:** Does the work have evidence the loop's stop condition was met, not just that the worker chose to stop?

**PASS:** the named stop condition (token budget, time budget, condition met, escalation) is satisfied with evidence
**WARN:** worker stopped but the stop condition is ambiguous
**FAIL:** worker stopped because they ran out of patience, not because the stop condition was met

### Dimension 6: Cost was within ceiling

**Question:** Did the work stay within the agreed cost ceiling (tokens, time, money, side effects)?

**PASS:** ceiling was named and respected with evidence
**WARN:** ceiling was named but exceeded slightly
**FAIL:** no ceiling was named, or ceiling was exceeded significantly

### Dimension 7 (closed/open classification): The right loop type was used

**Question:** Was the work done as a closed loop (bounded, gated, affordable) or as an open loop (exploratory, expensive)? Was the right type picked for the cost budget?

**PASS:** closed loop for cost-bounded work, open loop only with explicit sign-off
**WARN:** open loop used without explicit cost sign-off
**FAIL:** open loop burned significant budget without sign-off, OR closed loop blocked work that needed exploration

## Output format

The audit is a short report, not a deliverable file (unless `--write <path>` is passed). Format:

```markdown
# Loop Audit: [work being audited]

**Audit time:** [timestamp]
**Auditor:** Mavis (EA) | [or: verifier agent]

## Dimensions
1. Discovery:  PASS | WARN | FAIL — [one-line evidence]
2. Plan:       PASS | WARN | FAIL — [one-line evidence]
3. Blocks:     PASS | WARN | FAIL — [one-line evidence; list which blocks were in play, which absent]
4. Verify:     PASS | WARN | FAIL — [one-line evidence; name the verifier]
5. Stop:       PASS | WARN | FAIL — [one-line evidence; state the stop condition]
6. Cost:       PASS | WARN | FAIL — [one-line evidence; state the ceiling + actual]
7. Type:       PASS | WARN | FAIL — [one-line evidence; closed or open, justified]

## Critical failures (if any)
- [Dimension name]: [minimum fix in one sentence]

## Verdict
- **PASS:** loop ran correctly, work is accepted
- **WARN:** minor gaps, acceptable with the named mitigations
- **FAIL:** loop did not run correctly, do not accept the work; surface the gaps to the owner
```

## The procedure

1. **Identify the work.** One sentence: "I'm auditing [the cron I just set up / the brief I just wrote / the dispatch I just made]."
2. **Gather evidence.** Read the session log, the disk state, the relevant skill outputs. Don't recap from memory — disk wins.
3. **Run the 7 dimensions.** For each, name PASS / WARN / FAIL with one-line evidence. If you can't name evidence, the dimension is WARN (not PASS).
4. **If any FAIL:** name the minimum fix in one sentence. Do not fix it in this audit — surface it, let the owner decide. (This is the "audit, don't patch" rule from the Mavis fleet-trust-patterns topic.)
5. **State the verdict.** PASS / WARN / FAIL with the constraint.
6. **Decide action.** If FAIL on a non-trivial task, halt the report-back and surface the gap. If PASS, proceed. If WARN, mention inline and proceed.

## Hard constraints

1. **Disk wins over recap.** Every dimension's evidence must be a disk hit (file path, log line, command output), not a memory-based claim.
2. **No false PASS.** If you can't find evidence, the dimension is WARN, not PASS. "Looks right" is not evidence.
3. **Don't auto-fix during audit.** The audit is read-only against the work. Fixes are a separate step, owned by the worker or the chief, not by the audit.
4. **Audit is the verifier, not the maker.** You are not redoing the work. You are checking the work was done correctly. If you find yourself "fixing" something during the audit, stop — that's a different skill.
5. **Mavis territory only.** Audits apply to Mavis-side work. For cross-team audits (a peer's report), the rule from `cross-team-discipline` is: state (1) what they got right, (2) what they got wrong, (3) stop. NOT a fix-it list.

## Pairing

- `ea-loop-thinking` (the lens) — run this first to design the loop
- `ea-loop-audit` (the audit) — run this to check the loop ran
- `ea-closed-loop-builder` (the spec) — use when designing a new recurring loop
- `ea-5-mistakes-audit` (cross-check) — pairs with `--depth deep` for a fuller diagnostic
