# Hermes Blocked Items — Decision Doc (2026-06-07)

8 of 25 originally blocked items need your call. Bundled into 4 questions, ~2-3 lines each. Brief context per question, reply format at the bottom.

Source: Hermes Blocked Blitz report (2026-06-07 08:32 CT, chat_id 6598264778).

---

## Q1: P5 Pillars — Cost / Latency / Safety

3 product tradeoffs to lock in as eval criteria for the next P5 round.

- **Cost** — per-task spend ceiling? (e.g., "≤X% under current" or "≤$Y per 1k tasks")
- **Latency** — P50 / P95 targets for the operator path? (e.g., "<2s P50, <8s P95")
- **Safety** — hard-block rules? (e.g., "no destructive ops without explicit confirmation, no outbound sends without auth")

These become the eval criteria for the next P5 work, not just unblocking the current 3.

## Q2: Phase C Fleet Redesign

Tagged `needs-andre` explicitly. Three options I see:

- **A. Stay current (11 profiles)** — keep what works, retire dead ones
- **B. Consolidate (5 profiles)** — fold Hermes/OpenClaw/Wintermute/QA + specialists
- **C. Split by function** — routing, executor, verifier, specialist — cleanest abstraction

Architectural choice — affects every downstream task. Need your direction.

## Q3: Docs Corrections PR

PR body says "do NOT do without explicit in-session confirmation" — hard stop. Three paths:

- **A. Approve & merge** — you've reviewed
- **B. Approve with revisions** — list what to change
- **C. Block** — keep parked

Literal confirm/deny. State the option.

## Q4: Spec §7 — Desktop Bridge + Fleet Switcher

Two technical questions blocking two tasks:

- **Desktop bridge** — auth model? (local-only? OAuth relay? always-on tunnel?)
- **Fleet switcher** — UX (CLI flag? dashboard toggle? both?) + persistence (per-session? per-machine? sync via vault?)

Your spec §7 answers unblock both. 2-3 sentences each, plus any constraints.

## Q5: Anything else in the `needs-andre` bucket?

The report listed 5 items in this bucket, but only 4 named groups (P5 Pillars = 3, Phase C = 1). If there's a 5th item I missed, drop it here. If not, write "none" and we'll close the loop.

---

## Reply format

Paste this back filled in:

```
Q1: Cost=[ceiling], Latency=[P50/P95], Safety=[rule]
Q2: A / B / C — [one-line why]
Q3: A / B / C
Q4: Desktop=[auth model]; Switcher=[UX+persistence]
Q5: [item + answer, or "none"]
```

## Once you reply

I'll synthesize the answers, route the unblocks to Hermes, and update the kanban. Hermes holds the 8 on the board until then — they're tagged `awaiting-andre-decision` so they don't drift.

## Notes for Hermes (operator)

- Don't auto-route the 8 to workers — they're waiting on Andre's answers, not on dependencies
- If anything in the 8 changes status (e.g., a new dependency surfaces, a sibling task completes), report back to Mavis via mavis communication
- Once Andre replies, Mavis will synthesize — your job is to execute the unblocks and run the 2 already-approved actions (PR #40706 code review, v2/v4 verifier audits)
