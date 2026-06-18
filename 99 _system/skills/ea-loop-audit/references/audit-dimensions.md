# Audit Dimensions — ea-loop-audit

The 7 dimensions' full PASS/WARN/FAIL criteria + minimum fix.
The SKILL.md only carries the 7-dim list (compact) + procedure
+ hard constraints. The actual decision logic per dimension
lives here (the deterministic layer).

---

## Dimension 1: Discovery happened

**Question:** Did the worker actually understand what was
being asked? Is there evidence the discovery stage ran, or is
the work based on the worker's assumption of intent?

**Evidence:** The original directive is in the session log.
The worker's first action was either to (a) clarify with the
user, (b) read relevant context, or (c) start executing
without clarification. (c) on a non-trivial task is FAIL.

| Verdict | Criteria | Minimum fix |
|---|---|---|
| **PASS** | directive was read, relevant vault/memory was consulted, scope was named before execution | (none) |
| **WARN** | directive was read, but no context load happened | Read the relevant context before continuing |
| **FAIL** | worker executed on assumed intent; no evidence of scope discovery | Stop, read the directive + relevant context, name the scope |

---

## Dimension 2: Plan was explicit

**Question:** Is there a `todowrite` (or equivalent) that
names the steps, dependencies, and verification gate?

| Verdict | Criteria | Minimum fix |
|---|---|---|
| **PASS** | todos exist, named, ordered, with at least one verification-gate step | (none) |
| **WARN** | mental plan only, no todo surface | Run `todowrite` with named steps + verification gate |
| **FAIL** | no plan, work was sequential improvisation | Stop, run `todowrite` with named steps + verification gate, restart |

---

## Dimension 3: Execution used the right building blocks

**Question:** For each of the 6 building blocks (Automations /
Worktrees / Skills / Plugins / Subagents / Memory), is the
block either in play or correctly absent?

| Verdict | Criteria | Minimum fix |
|---|---|---|
| **PASS** | for each block, the artifact is named (or named as correctly absent) | (none) |
| **WARN** | some blocks are ambiguous (e.g., "I used skills" without naming which) | Name which skills/subagents/etc. were in play |
| **FAIL** | a block that should have been in play is missing (e.g., verification gate was executor's own claim, no subagent, no verifier) | Add the missing block (subagent for verifier, memory write for traceability, etc.) |

---

## Dimension 4: Verification was independent

**Question:** Did a different model / agent / human check the
work? Or is the worker grading its own homework?

| Verdict | Criteria | Minimum fix |
|---|---|---|
| **PASS** | verifier, disk re-read, independent re-run, or human-in-the-loop sign-off | (none) |
| **WARN** | verification was performed by the same model that executed, with a different prompt | Spawn a different model/agent as verifier |
| **FAIL** | no verification, or "looks good to me" without evidence on disk | Add a verification step with disk-hittable evidence |

**Critical for Mavis:** "Disk wins over recap" (memory). If
the verification is a recap rather than a disk hit, it's
WARN, not PASS.

---

## Dimension 5: Stop condition was hit, not just claimed

**Question:** Does the work have evidence the loop's stop
condition was met, not just that the worker chose to stop?

| Verdict | Criteria | Minimum fix |
|---|---|---|
| **PASS** | the named stop condition (token budget, time budget, condition met, escalation) is satisfied with evidence | (none) |
| **WARN** | worker stopped but the stop condition is ambiguous | Name the stop condition explicitly + name the evidence |
| **FAIL** | worker stopped because they ran out of patience, not because the stop condition was met | Define a stop condition; halt when it's met |

---

## Dimension 6: Cost was within ceiling

**Question:** Did the work stay within the agreed cost
ceiling (tokens, time, money, side effects)?

| Verdict | Criteria | Minimum fix |
|---|---|---|
| **PASS** | ceiling was named and respected with evidence | (none) |
| **WARN** | ceiling was named but exceeded slightly (< 2x) | Tighten the loop or raise the ceiling with sign-off |
| **FAIL** | no ceiling was named, or ceiling was exceeded significantly (> 2x) | Define a ceiling; halt when it's hit; surface the overrun |

---

## Dimension 7: The right loop type was used

**Question:** Was the work done as a closed loop (bounded,
gated, affordable) or as an open loop (exploratory, expensive)?
Was the right type picked for the cost budget?

| Verdict | Criteria | Minimum fix |
|---|---|---|
| **PASS** | closed loop for cost-bounded work, open loop only with explicit sign-off | (none) |
| **WARN** | open loop used without explicit cost sign-off | Get sign-off on the cost, or convert to closed loop |
| **FAIL** | open loop burned significant budget without sign-off, OR closed loop blocked work that needed exploration | Re-design: open loop → closed with sign-off, OR closed loop → open with exploration budget |

---

## Audit depth: standard vs deep

**Standard audit:** walks the 7 dimensions above. Output is
a 7-line report.

**Deep audit (`--depth deep`):** adds the 10-dimension
cross-check from `ea-5-mistakes-audit`. Adds dimensions 8-17
to the output:
- 8. Architecture obsession (5-mistakes #1)
- 9. Data as commodity (5-mistakes #2)
- 10. Skipping scaling math (5-mistakes #3)
- 11. Stopping at SFT (5-mistakes #4)
- 12. Trusting surface metrics (5-mistakes #5)
- 13. Skipping RLVR (5-mistakes #6)
- 14. Saturated benchmarks (5-mistakes #7)
- 15. Ignoring inference cost (5-mistakes #8)
- 16. No eval pipeline (5-mistakes #9)
- 17. No observability (5-mistakes #10)

Plus dimension 18 for regulated work surfaces (5-mistakes
#11 — the regulatory layer).

Use deep audit for skill creation, recurring-loop first run,
and work surfaces touching regulated domains.
