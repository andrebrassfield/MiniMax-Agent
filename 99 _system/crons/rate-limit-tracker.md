---
name: rate-limit-tracker
schedule: 0 22 * * *
timezone: America/Chicago
session:
  mode: new
  keepSessions: 7
---

# Rate-Limit Budget Tracker

Daily cron (22:00 CT) that logs the day's MiniMax Code rate-limit consumption against the two-track allocation model. Per the 2026-06-22 two-track-model decision, the budget is allocated, not consumed freely.

**EXECUTE the procedure:**

1. **QUERY** current rate-limit state via `mmx quota` (or the equivalent daemon call):
   ```bash
   mmx quota --format json
   ```
   Capture: `used_today`, `remaining`, `reset_at`, `weekly_used`, `weekly_remaining`.

2. **READ** today's existing log at `~/.mavis/state/rate-limit-YYYY-MM-DD.md` (init if missing). If a log exists, append; if not, create.

3. **CATEGORIZE** today's consumption by track:
   - **Track 1 (spec, interactive):** sessions that ran with Andre in the chat surface. Count: `mavis session list --since today --track 1` (or equivalent).
   - **Track 2 (implementation, autonomous):** sessions spawned via `two-track-handoff`. Count: `cat ~/.mavis/state/handoffs/registry.jsonl | grep '"status":"claimed"' | grep today`.
   - **Verifier:** verifier subagent spawns. Count: grep session logs for verifier agent.
   - **Cron / autonomous:** X-Content-Engine, FB-Engine, daily brief, weekly connections, etc.

4. **WRITE** the daily log at `~/.mavis/state/rate-limit-YYYY-MM-DD.md`:

   ```markdown
   ---
   date: YYYY-MM-DD
   ---

   # Rate-Limit Daily Log

   **Total used today:** N tokens
   **Remaining:** M tokens
   **Weekly used:** P tokens / 750K ceiling
   **Reset at:** <ISO timestamp>

   ## Allocation (target vs actual)

   | Track | Target % | Actual tokens | Actual % | Status |
   |---|---|---|---|---|
   | Track 1 (spec) | 50% | N1 | % | 🟢/🟡/🔴 |
   | Track 2 (impl) | 30% | N2 | % | 🟢/🟡/🔴 |
   | Verifier | 5% | Nv | % | 🟢/🟡/🔴 |
   | Cron / autonomous | 15% | Nc | % | 🟢/🟡/🔴 |

   Status thresholds:
   - 🟢 within ±10% of target
   - 🟡 10-25% over/under target
   - 🔴 >25% over/under target (action required)

   ## Track 2 sessions today

   | Handoff ID | Status | Duration | Tokens |
   |---|---|---|---|
   | ... | open/claimed/completed/failed/halted | ... | ... |

   ## Action items

   - [list any track that's 🔴]
   - [list any handoff in failed/halted state]
   - [recommend adjustment if pattern persists]
   ```

5. **MIRROR** the daily log to `~/MiniMax-Agent/99 _system/state/rate-limit-YYYY-MM-DD.md` so it's in the vault.

6. **WEEKLY ROLLUP** (Sunday only — day-of-week check):
   ```bash
   [ "$(date +%u)" = "7" ] && {
     cat ~/.mavis/state/rate-limit-$(date -v-6d +%Y-%m-%d).md ... rate-limit-$(date +%Y-%m-%d).md > ~/.mavis/state/rate-limit-WEEK-YYYY-MM-DD.md
     # Mirror to vault
     cp ~/.mavis/state/rate-limit-WEEK-YYYY-MM-DD.md ~/MiniMax-Agent/99\ _system/state/
   }
   ```

7. **END** — wrap status in `<mavis-progress>rate-limit-tracker: tick — used N today, weekly P/750K</mavis-progress>` and exit silently. Do NOT page Andre unless a track is 🔴 AND the action item requires his decision.

**HALT conditions:**
- `mmx quota` query fails → HALT, surface (the tracker is the gate for two-track handoffs; if it's broken, handoffs are blocked)
- Daily log write fails → HALT, surface (don't lose the data)
- Weekly rollup arithmetic fails → log the error to daily file, continue

**Decision rule on 🔴:**
- If Track 1 is 🔴 over → reduce Track 2 spawn rate next day
- If Track 2 is 🔴 over → defer new Track 2 handoffs until balance restores
- If Verifier is 🔴 over → defer non-critical verifier audits
- If Cron is 🔴 over → audit cron frequency, consider deferring non-critical crons

---

[gate-discipline] If the cron fails silently, Track 2 handoffs must verify budget via `mmx quota` directly before spawning (the `two-track-handoff` skill has this check as Step 1). The cron is the daily ledger; the skill has the per-spawn gate. Both must work.
