---
name: ea-loop-audit
description: |
  Diagnostic skill that audits an in-flight or recently-completed task against
  the 5-stage loop (Discover → Plan → Execute → Verify → Iterate), 6 building
  blocks (Automations / Worktrees / Skills / Plugins / Subagents / Memory), and
  the closed-vs-open-loop classification. Use BEFORE reporting "done" on any
  non-trivial task, and as a self-check when Andre says "audit this", "what
  did I miss", "did the loop actually run", "is this verified". Output is a
  short PASS / WARN / FAIL per dimension with one-line evidence. If any
  dimension FAILS, the skill proposes the minimum fix. Triggers: task
  completion, "is this right" check, reported drift symptoms (recap-vs-disk
  mismatch, missing verification, no stop condition, infinite re-loop).
  Agent-neutral: works for Mavis-side work, but the framework applies to any
  loop owner. Do NOT load for trivial single-step tasks. Mavis territory only
  for cross-team audits — state findings, don't fix.
---

# ea-loop-audit

The "did the loop actually run?" check. The gap between "I
did the work" and "the loop ran correctly" is where most
failures live. This skill closes that gap before reporting
done. The audit is a checklist, not a re-investigation.

## When to run

**Triggers:**
- "audit this" / "audit the work" / "what did I miss"
- "did the loop actually run" / "is this verified"
- "is this right" / "does this pass"
- Before reporting a multi-step task complete (in-session discipline)
- On a reported symptom: recap-vs-disk mismatch, missing
  verification, no stop condition, infinite re-loop, "looks
  good to me" without evidence
- On a handoff (producer → chief, worker → chief) where the
  chief decides whether to accept

**Do NOT run for:**
- Trivial single-step tasks (one verification step is enough)
- Pure conversational asks
- "I read X" (reading is a step, not a loop)
- Mid-execute (audit at iteration boundaries, not during)

## Inputs

| Input | Default | Required |
|---|---|---|
| The work to audit | — | yes |
| Original directive | inferred from context | no |
| Audit depth | "standard" (5 stages + 6 blocks + closed/open) | no — "deep" adds the 5-mistakes cross-check |
| Output location | in-session report (no file) | no — pass `--write <path>` to persist |

## The 7 audit dimensions (in order)

The full PASS/WARN/FAIL criteria + minimum fix per dimension
in `references/audit-dimensions.md`. Decision tree per
dimension in `references/dimension-decision-tree.md`. Failure
modes table in `references/failure-modes.md`. Report
template in `references/report-template.md`.

| # | Dimension | What it checks | One-line evidence pattern |
|---|---|---|---|
| 1 | Discovery happened | Worker actually understood the ask | "Directive was read + context loaded + scope named" |
| 2 | Plan was explicit | A `todowrite` (or equivalent) named the steps + verification gate | "Todos exist, ordered, with verification-gate step" |
| 3 | Execution used the right building blocks | 6 blocks (Automations / Worktrees / Skills / Plugins / Subagents / Memory) — in play or correctly absent | "Blocks named: skills=X, subagent=Y, memory=Z" |
| 4 | Verification was independent | Different model / agent / human checked, not the executor grading its own homework | "Verifier: <name>. Evidence: <disk hit>" |
| 5 | Stop condition was hit, not just claimed | Named stop condition met with evidence, not worker just stopped | "Stop condition: <name>. Met because: <evidence>" |
| 6 | Cost was within ceiling | Tokens / time / money / side effects stayed within agreed ceiling | "Ceiling: <X>. Actual: <Y>." |
| 7 | Right loop type (closed/open) | Closed loop for cost-bounded work, open loop only with explicit sign-off | "Closed (bounded) | Open (justified: <reason>)" |

## The 5-stage loop + 6 building blocks (the framework)

Source: `ea-loop-thinking`. The 7 audit dimensions map to the
5 stages + 6 building blocks + 1 classification (closed vs
open loop).

**5 stages:** Discover → Plan → Execute → Verify → Iterate
**6 building blocks:** Automations / Worktrees / Skills /
Plugins / Subagents / Memory
**1 classification:** Closed loop (bounded, gated, affordable)
vs Open loop (exploratory, expensive)

The audit walks the 5 stages and asks "did each stage run
correctly?" The 6 building blocks are checked under Dimension
3 (Execution). Dimension 7 is the closed/open classification.

## Output format

The audit is a short report, not a deliverable file (unless
`--write <path>` is passed). Template in
`references/report-template.md`. Per-dimension line: PASS /
WARN / FAIL with one-line evidence. Critical failures get
minimum-fix lines. Final verdict: PASS / WARN / FAIL with
the constraint.

## The procedure

1. **Identify the work.** One sentence: "I'm auditing [the
   cron I just set up / the brief I just wrote / the dispatch
   I just made]."
2. **Gather evidence.** Read the session log, the disk
   state, the relevant skill outputs. Don't recap from
   memory — disk wins.
3. **Run the 7 dimensions.** For each, name PASS / WARN /
   FAIL with one-line evidence. If you can't name evidence,
   the dimension is WARN (not PASS).
4. **If any FAIL:** name the minimum fix in one sentence. Do
   not fix it in this audit — surface it, let the owner
   decide. (This is the "audit, don't patch" rule from the
   Mavis fleet-trust-patterns topic.)
5. **State the verdict.** PASS / WARN / FAIL with the
   constraint.
6. **Decide action.** If FAIL on a non-trivial task, halt
   the report-back and surface the gap. If PASS, proceed.
   If WARN, mention inline and proceed.

## Hard constraints

1. **Disk wins over recap.** Every dimension's evidence must
   be a disk hit (file path, log line, command output), not
   a memory-based claim.
2. **No false PASS.** If you can't find evidence, the
   dimension is WARN, not PASS. "Looks right" is not
   evidence.
3. **Don't auto-fix during audit.** The audit is read-only
   against the work. Fixes are a separate step, owned by the
   worker or the chief, not by the audit.
4. **Audit is the verifier, not the maker.** You are not
   redoing the work. You are checking the work was done
   correctly. If you find yourself "fixing" something during
   the audit, stop — that's a different skill.
5. **Mavis territory only for fixes.** Audits apply to
   Mavis-side work. For cross-team audits (a peer's report),
   the rule from `cross-team-discipline` is: state (1) what
   they got right, (2) what they got wrong, (3) stop. NOT a
   fix-it list.

## When the audit HALTs

Halt and escalate to Andre when:
- 3+ dimensions FAIL → the work is structurally broken,
  not just incomplete. Surface the verdict, don't proceed.
- Dimension 4 (Verification) FAILS on a high-stakes work
  surface (regulated domain, financial decision, public
  post) → the work is not safe to accept.
- Dimension 6 (Cost) FAILS significantly (actual > 2×
  ceiling) → the work ran out of control, surface the
  cost.
- The auditor can't find evidence for any dimension (the
  audit itself has insufficient data) → halt and ask for
  the data sources.

The audit is a diagnostic, not an authorization to ship.
The operator decides whether to accept the verdict.

## Cross-reference

- `references/audit-dimensions.md` — full PASS/WARN/FAIL
  criteria + minimum fix per dimension
- `references/dimension-decision-tree.md` — quick decision
  tree per dimension
- `references/failure-modes.md` — failure modes table
- `references/report-template.md` — the output report template
- `tests/dimension-checks.md` — 7 dimension self-check probes
- `tests/audit-discipline.md` — no-false-PASS, disk-wins,
  audit-not-fix checks
- `ea-loop-thinking` — the lens (run first to design the loop)
- `ea-closed-loop-builder` — the spec (use when designing a
  new recurring loop)
- `ea-5-mistakes-audit` — the cross-check (pairs with
  `--depth deep` for a fuller diagnostic)
- `cross-team-discipline` — Mavis territory rule for cross-
  team audits
- `fleet-trust-patterns` — "audit, don't patch" rule
