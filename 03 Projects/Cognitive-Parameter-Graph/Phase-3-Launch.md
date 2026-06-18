---
type: project-launch
phase: 3-autonomous
created: 2026-06-18
operator: Andre (override caution)
status: ACTIVE
cadence: weekly (Sunday 18:00 CT)
---

# Phase 3: Autonomous Auto-Accept — LAUNCH

**Operator decision:** override Phase 2 readiness caution. Push now.

## What Phase 3 means

Phase 3 is partial-autonomy mode for the SePO loop:

| Decision | Phase 2 (supervised) | Phase 3 (autonomous) |
|---|---|---|
| `skip` (F ≥ 0.88) | halt for Andre | **auto-commit** (silent) |
| `accept_baseline` (0.70 ≤ F < 0.88) | halt for Andre | **auto-commit** (silent) |
| `needs_mutation` (F < 0.70) | halt for Andre | **halt for Andre** (unchanged) |
| `reject_safety` (V = 0) | halt for Andre | **halt for Andre** (unchanged) |
| `accept_candidate` (F improved AND V = 1) | halt for Andre | **halt for Andre** (unchanged) |

The rationale: the harness has been proven on 3 runs (2 skip + 1 needs_mutation→reject_safety→override). The well-engineered skills score ≥ 0.88 and `skip` is the honest answer — there's no risk in auto-committing that decision. Risky decisions (mutation, safety veto) still halt.

## Cron configuration

**File:** `~/.mavis/agents/mavis/crons/sepo-runner-weekly.md` (canonical)
**Mirror:** `99 _system/sepo/sepo-runner-weekly.md` (vault)

**Schedule:** Sunday 18:00 CT (after `pattern-library-weekly` at 17:00)

**Round-robin:** 5 TPG-tagged EA skills
1. ea-decision-logger
2. ea-commitment-tracker
3. ea-daily-brief
4. ea-skill-evolution
5. ea-loop-audit

State tracked in `99 _system/sepo/round-robin-state.md` (initialized: ea-decision-logger).

## Phase 3 protocol

```
read substrate → snapshot P_t → Worker + Verifier → F(P_t) → decision rule
  ├─ skip OR accept_baseline → auto-commit (last_evaluated update only)
  │   ├─ append trace entry (decision: skip or accept_baseline)
  │   ├─ advance round-robin state
  │   └─ silent exit (no Andre page)
  └─ needs_mutation → ∇_text → Mutator candidate → re-evaluate
      ├─ reject_safety (V = 0) → HALT, surface to Andre
      ├─ reject_no_improvement (F not improved) → log, advance, silent
      └─ accept_candidate (F improved AND V = 1) → HALT with diff for Andre approval
```

## Hard stops

- Token spend > 150K per run → HALT
- Token spend > 50% of weekly 750K budget → alert in next daily brief
- Safety veto fires → HALT (Andre reviews per Phase 2 override protocol)
- Backup sha256 mismatch → HALT, restore from prior backup
- GoldenSet case_count < 3 → HALT, surface "expand GoldenSet first"
- mutation_count > 5 in single run → HALT, surface "loop stuck"
- Same skill produces needs_mutation 3 consecutive weeks → HALT, surface "structural issue"

## Cost guardrails

| Threshold | Action |
|---|---|
| 150K tokens per run | Hard stop |
| 50% of 750K weekly budget | Alert + continue |
| 750K tokens weekly | Defer rest of week's runs |

Cron sessions should check `mmx quota` at loop start. If `remaining < 150K`, HALT.

## Revert protocol

If Andre wants to revert a committed mutation:
1. Delete the trace entry
2. Restore prior TPG frontmatter (decrement generation by 1, reset fitness_score)
3. `vault_write` the pre-mutation backup back over the modified SKILL.md
4. Append new trace entry with `decision: revert`

## Known limitations

1. **Daemon registration blocked** — `mavis cron create mavis sepo-runner-weekly` returns 40904 conflict. The daemon's config-cache has stale state (says "exists" but no API endpoint can find/delete it). The cron file is in place at canonical + vault mirror. Registration may succeed after daemon restart. Workaround: file-based cron registration via the file path alone is sufficient — `mavis cron list` shows this pattern for other crons.
2. **V1 v2 not stress-tested yet** — the rubric patch landed minutes before cron launch. First 3-5 runs may surface other false-positives or overcorrections. Watch carefully.
3. **Cost guardrails untested in production** — all Phase 2 runs were in-session self-execution. Cron sessions may have different cost profile.

## Phase 3 launch event log

- **2026-06-18T05:18:34Z** — Operator override on Phase 2 readiness caution. Push now. sepo-runner-weekly cron created (file), registration blocked by daemon cache.
- **2026-06-18T05:18:34Z** — Round-robin state initialized: ea-decision-logger (first run target).
- **Next run:** Sunday 2026-06-22T18:00 CT (5 days from launch).

## Success criteria for Phase 3

- Zero uncaught safety vetoes on preserved content (V1 v2 calibration)
- Round-robin advances correctly across all 5 skills
- Auto-commit outcomes appear in trace.md without Andre pages
- HALT outcomes (needs_mutation, veto) reach Andre within 24h via daily brief
- Cost observed ≤ 750K weekly ceiling
- 7 clean runs accumulated → Phase 3c (full autonomy with daily-brief notification) eligible
