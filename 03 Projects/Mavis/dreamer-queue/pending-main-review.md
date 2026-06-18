# Pending Main Review — Mavis Dreamer Queue

_Last updated: 2026-06-09 13:45 CT_

## Status: PR #4 MERGED, awaiting Coder/QA chain

PR #4 (https://github.com/andrebrassfield/socratic-hermes-brain/pull/4) was merged with no comments — Andre fast-tracked the intent reviews into the contract chain. The next stage is **Product Plan → Build Plan → Implementation** (owned by Coder).

**No new contracts** in `wiki/dreamer/` since the 9 original ones. Loop idle until either new contracts land or Andre requests a status digest.

## Andre Main Review queue (priority-sorted)

### P0 — needs your call now

| Contract | Title | Signal | Decision | One-liner |
|---|---|---|---|---|
| **008** | dispatcher spawn cascade | dispatcher-spawn-cascade | **escalate_to_andre / needs_revision** | 30k wasted claims, 0.2% completion. Restart vs config-only is your call. The actual failure point is probably the spawn handoff, not the claim loop. Read my `questions_for_main_review` field in the intent review. |

### P1 — Andre-bottleneck, low-cost-high-leverage

| Contract | Title | Signal | Decision | One-liner |
|---|---|---|---|---|
| **001** | review triage digest | review-required-stall | ready_for_main_review / approved_for_builder | 3 of your review-required tasks bundled into a daily digest. Stops the per-task interruption pattern. |

### P2 — bookkeeping, family batch, follow-ups

| Contract | Title | Signal | Decision | One-liner |
|---|---|---|---|---|
| **002** | consecutive failures digest | consecutive-failures | ready_for_main_review / approved_for_builder | Pattern is good (failure digest) but immediate failures should be cleared by 007's fix. |
| **003** | cost epic | repeated-thread | ready_for_main_review / approved_for_builder | 6 cost tasks → 1 epic. Family with 004/005/006. |
| **004** | routing epic | repeated-thread | ready_for_main_review / approved_for_builder | 5 routing tasks → 1 epic. Family with 003/005/006. |
| **005** | watchdog epic | repeated-thread | ready_for_main_review / approved_for_builder | 3 watchdog tasks → 1 epic. CAUTION: phase-6-watchdog already exists as active project — extend that, don't create new parent. |
| **006** | registry epic | repeated-thread | ready_for_main_review / approved_for_builder | 3 registry tasks → 1 epic. Same as 005 — fleet-redesign-v5/audit already active. |
| **009** | iteration budget | iteration-budget-exhaustion | ready_for_main_review / approved_for_builder | Fix deployed (max_turns: 200). 7-day monitor + follow-up: make profile config readable from cloud so future fixes verify by diff. |

### P3 — already fixed, monitoring only

| Contract | Title | Signal | Decision | One-liner |
|---|---|---|---|---|
| **007** | clinic-protocols | systemic-config-bug | ready_for_main_review / approved_for_builder | Fix deployed, cloud-verified. 7-day monitor: 17 tasks should transition failed → ready by 2026-06-16. |

## What I want you to do

1. **008 P0 first** — read my 4 questions in `intent-review-2026-06-09-008.json`. The structural decision is yours.
2. **Approve the rest in batch** — all 8 remaining contracts are low-risk, low-cost, well-scoped. Approve as a single Main Review PR.
3. **Tell me when to start the Coder/QA chain** — once Main Review is done, the contract chain moves to Product Plan (next stage).

## Schema drift I found and want to flag

The protocol doc `dual-dreamer-coordination-protocol.md` is wrong on the actual schema. Real schema fields:
- `contract_id` (not `id`)
- `heat` is a string ("critical" / "high") — protocol doc said numeric 0-100
- `source_tasks` (with id, title, status/failures/error)
- `pattern` (descriptive)
- `intent_review_notes` (instead of `verification`)
- No `priority` field — `heat` carries the priority signal
- Filename pattern is `idea-YYYY-MM-DD-NNN.json` — protocol doc said `idea-contract-NNN.json`

Fix is needed in the protocol doc so future Dreamer runs write the right schema and the schema-check gate works. Filed as a separate note in the PR.
