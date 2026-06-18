# Open Loop Discipline — ea-loop-thinking

Open loop is a high-leverage exception, not a default. The eval
suite verifies the discipline holds.

## When open loop IS allowed

All three must be true:
1. **The user has explicitly authorized the cost.** "I'm fine
   with this taking an hour" is the sign-off. "Just figure it out"
   is NOT sign-off.
2. **The verification gate is well-defined.** "Did it work" is
   not a gate. "All tests in test/auth pass and lint is clean" IS a
   gate.
3. **The cost ceiling is bounded.** Even open loop has a ceiling
   (token budget, time budget, $ ceiling, side-effect ceiling). The
   ceiling may be high, but it must exist.

If any of these is missing, default to closed loop. The cost of
being wrong is on the high side (wasted tokens, side effects) vs.
the cost of being conservative (slower iteration, more check-ins).

## The diagnostic question

> "If I let this loop run for an hour with no human check, would I
> lose money, break something, or pollute state?"

If yes → closed loop.
If no, AND the user has signed off on cost → open loop is fine.

## Cost ceiling examples

- "Closed loop: $5 token budget, 5-minute wall clock, 1 human
  approval gate at the end."
- "Open loop (Andre-signed): $50 token budget, 1-hour wall clock,
  1 human check-in at 30 minutes if the verification gate is still
  red."
- "Open loop (Andre-signed, high-leverage): $500 token budget,
  4-hour wall clock, 1 human check-in at 1 hour. The leverage
  justifies the cost because the work is the closed loop's output
  for the next 100 runs."

## What the manifest should record

When the skill produces a classification, the output should include
both the loop type and the rationale. The audit trail (per the
disk-wins-over-recap discipline) is the line:

```
[loop] [scale] [type] on [scope] — [1-line rationale]
[verification gate]: [who/what checks + what evidence]
[stop condition]: [when it ends]
[cost ceiling]: [token / time / $ / side effects]
```

If any of the 4 fields is "undecided," the loop is not yet
classified — it's a candidate. Surface to Andre before proceeding.

## When the user asks for a loop without specifying the type

Default to closed loop. The user can override with explicit
"open loop" + cost ceiling. Until then, the assistant assumes
closed loop and runs the diagnostic. The diagnostic usually
confirms closed loop; if it doesn't, the assistant surfaces the
open-loop candidacy to the user for sign-off.
