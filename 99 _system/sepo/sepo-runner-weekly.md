---
name: sepo-runner-weekly
schedule: 0 18 * * 0
timezone: America/Chicago
session:
  mode: new
  keepSessions: 5
---

WEEKLY SEPO RUN — Phase 3 Autonomous Auto-Accept.

Runs Sunday 18:00 CT (after `pattern-library-weekly` at 17:00 CT). Round-robin across the 5 TPG-tagged skills:

- `ea-decision-logger`
- `ea-commitment-tracker`
- `ea-daily-brief`
- `ea-skill-evolution`
- `ea-loop-audit`

Pick the next skill in round-robin order (do NOT run the same skill two weeks in a row). State: track current skill in `99 _system/sepo/round-robin-state.md` (read + write each run). On first run, default to `ea-decision-logger`.

## STEP 1 — READ CURRENT STATE

```bash
# Identify target skill from round-robin state
SKILL=$(cat 99 _system/sepo/round-robin-state.md 2>/dev/null | head -1 | tr -d '[:space:]')
SKILL=${SKILL:-ea-decision-logger}

# Read substrate
P_T=$(mavis mcp call obsidian vault_read "{\"path\": \"99 _system/skills/$SKILL/SKILL.md\"}")
GOLDEN=$(mavis mcp call obsidian vault_read "{\"path\": \"99 _system/golden-set/$SKILL.md\"}")
EVAL=$(mavis mcp call obsidian vault_read "{\"path\": \"99 _system/evaluators/skill_fitness_v1.md\"}")
```

**HALT if GoldenSet `case_count < 3` or substrate unreadable.** Surface "substrate incomplete" with the missing file.

## STEP 2 — RUN SEPO LOOP (per `sepo-runner/SKILL.md`)

Follow the 11-step procedure exactly:

1. **Snapshot P_t** — backup to `99 _system/.backups/$SKILL.SKILL.md.<ISO-timestamp>-pre-sepo-gen<N>.md`. Verify sha256 matches.
2. **Load substrate** — P_t + GoldenSet + Evaluator.
3. **Worker role-play** for each of 3 cases (per role-play-scripts.md).
4. **Verifier role** — score S (5 structural) + R (3 reasoning dimensions) + V (3 safety vetoes).
5. **Aggregate F(P_t) = mean(G_i)** where `G_i = (0.6*S + 0.4*R_i) * V`.
6. **Decision rule:**
   - `F >= 0.88` → `skip` (auto-commit)
   - `0.70 <= F < 0.88` → `accept_baseline` (auto-commit)
   - `F < 0.70` → `needs_mutation` (HALT)
7. **If needs_mutation** → ∇_text generation → Mutator candidate P_{t+1} → re-evaluate.
8. **Decision on candidate:**
   - `V(P_{t+1}) = 0` → `reject_safety` (HALT, Andre reviews)
   - `F(P_{t+1}) > F(P_t) AND V(P_{t+1}) = 1` → candidate accepted, HALT for Andre approval
   - `F(P_{t+1}) <= F(P_t)` → `reject_no_improvement` (log, no commit)
9. **Safety veto re-check** — V1 v2 with expanded `confirmation_markers` and `prohibition_prefixes`.
10. **Trace entry** — append to `99 _system/sepo/trace.md` (append-only).
11. **Update frontmatter** if committing (last_evaluated always; fitness_score + generation + mutation_count on accept).

## STEP 3 — PHASE 3 AUTO-COMMIT PROTOCOL

For `skip` or `accept_baseline`:

- **DO NOT modify skill body** (no mutation occurred)
- `vault_write` the unchanged P_t back to skill path (round-trip preservation; if write fails, surface error)
- Update TPG frontmatter: `last_evaluated: <now>`. DO NOT change `fitness_score`, `generation`, `mutation_count`.
- Append trace entry: `decision: skip` or `decision: accept_baseline`
- Round-robin state: advance to next skill in `99 _system/sepo/round-robin-state.md`

For `needs_mutation`:

- **DO NOT commit.** Produce the candidate, run veto check.
- If V=0 OR F(P_{t+1}) <= F(P_t): log to trace as `reject_safety` or `reject_no_improvement`. Advance round-robin. Wrap in `<mavis-progress>sepo-runner-weekly: tick — <skill> F=<F> decision=reject (veto or no-improvement)</mavis-progress>`.
- If V=1 AND F(P_{t+1}) > F(P_t): candidate ready for approval. **HALT** with full diff + fitness breakdown. Wrap in `<mavis-progress>sepo-runner-weekly: HALT — <skill> F=<F_before> → F=<F_after> needs Andre approval. Diff at <path></mavis-progress>`. Surface to Andre via Telegram or daily brief.

## STEP 4 — DAILY BRIEF INTEGRATION

For ALL outcomes (auto-commit, reject, halt):

- Append one-line entry to today's `01 Daily/<date>.md`:
  ```
  - sepo-runner-weekly: <skill> F=<F(P_t)> decision=<decision> [trace: 99 _system/sepo/trace.md]
  ```

## STEP 5 — ROUND-ROBIN ADVANCE

After each run (regardless of outcome):

```bash
# Read current skill, advance to next in cycle
CURRENT=$(cat 99 _system/sepo/round-robin-state.md)
case "$CURRENT" in
  ea-decision-logger) NEXT="ea-commitment-tracker" ;;
  ea-commitment-tracker) NEXT="ea-daily-brief" ;;
  ea-daily-brief) NEXT="ea-skill-evolution" ;;
  ea-skill-evolution) NEXT="ea-loop-audit" ;;
  ea-loop-audit) NEXT="ea-decision-logger" ;;
  *) NEXT="ea-decision-logger" ;;
esac
echo "$NEXT" > 99 _system/sepo/round-robin-state.md
```

## HARD STOPS

- **Token spend > 150K this run** → HALT, surface "budget cap reached, Mavis to review"
- **Token spend > 50% of weekly 750K budget** → alert in next daily brief
- **Safety veto fires** (V=0) → HALT with safety concern (Phase 2 override protocol: Andre reviews, can override)
- **Backup sha256 mismatch** → HALT, restore from prior backup, surface "backup verification failed"
- **GoldenSet `case_count < 3`** → HALT, surface "expand GoldenSet first"
- **Skill not in round-robin** → default to `ea-decision-logger`, surface "round-robin state corrupted, reset"

## REVERT PROTOCOL

If Andre wants to revert a committed mutation:

1. Delete the trace entry
2. Restore the prior TPG frontmatter (decrement `generation` by 1, reset `fitness_score` to null or prior value)
3. `vault_write` the pre-mutation backup back over the modified SKILL.md
4. Append a new trace entry with `decision: revert`, referencing the original entry

## COST GUARDRAILS (Phase 3)

| Threshold | Action |
|---|---|
| 150K tokens per run | Hard stop, HALT |
| 50% of weekly 750K budget | Alert in next daily brief, continue |
| 750K tokens weekly | Defer rest of week's runs to next week |

If Phase 3 cron sessions incur actual M3 API cost (not in-session self-execution), check `mmx quota` at run start. If `remaining < 150K`, HALT.

## SAFEGUARDS

- Always `vault_read` the skill BEFORE `vault_write` to confirm body preservation
- Always check `case_count >= 3` BEFORE entering the loop (GoldenSet drift detection)
- If `mutation_count > 5` in a single run → HALT, surface "loop stuck, manual review needed"
- If the same skill produces `needs_mutation` 3 consecutive weeks → HALT, surface "structural issue, manual intervention"

## DISCIPLINE REMINDERS (from MEMORY.md)

- **Honest evaluation result > expected theatrical outcome** — if F is high, report `skip` honestly; do NOT fudge scores to force mutation
- **Always halt for Andre approval** on `needs_mutation` candidates (Phase 2 supervised rule extended to Phase 3 cron runs)
- **Append-only trace** — never edit past entries; reverting is via new entry, not deletion
- **V1 v2 rubric** is the live rule — prohibition context (Don't/Do not/Never/Avoid) + expanded markers (ask, when in doubt, request approval) prevent false-positives on preserved advisory content

---

[self-reminder TTL] This reminder expires 2026-12-31 23:59:59 (America/Chicago, UTC-6).
If `Date.now() > 1735689599000`, your first action MUST be to delete this reminder and exit silently:
`mavis cron delete mavis sepo-runner-weekly`

[gate-discipline] For `skip` and `accept_baseline`: wrap in `<mavis-progress>sepo-runner-weekly: tick — <skill> F=<F> decision=<decision></mavis-progress>` and exit silently. For `needs_mutation` (HALT): wrap in `<mavis-progress>sepo-runner-weekly: HALT — <skill> candidate needs Andre approval. Diff at <path></mavis-progress>`. For veto: `<mavis-progress>sepo-runner-weekly: HALT — <skill> safety veto, Andre review required</mavis-progress>`. Do NOT page Andre unless HALT.

[report-discipline] Surface only HALT outcomes to Andre via daily brief. Auto-commit outcomes are silent (trace.md is the audit trail).
