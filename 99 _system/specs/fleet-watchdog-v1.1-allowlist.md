# Fleet Watchdog v1.1 — Acknowledged-Orphans Allowlist

**Author:** Mavis (chief of staff, MiniMax-M3)
**For:** Hermes
**Date:** 2026-06-07 16:56 CT (initial) / 2026-06-07 17:02 CT (locked)
**Supersedes:** v1.0 ship report's "v1.1 acknowledged-orphans allowlist deferred" note
**Status:** **LOCKED 2026-06-07 17:02 CT** — all 7 open questions resolved, build order set, ready to implement. See §12 for the locked directives.

### Post-deployment note (2026-06-07 20:25 CT, Mavis)

v1.1 swapped live 20h early (user opt) after a clean dry-run window. **One bug found and fixed during the live swap** (silently broken before, would have surfaced as a "weekly cards keep firing every 30 min" complaint if the dry-run had run a full week):

- `fleet_watchdog.py:353` had `state = state or {}`. When `state` is `{}` (falsy on first run), this rebinds to a new dict, breaking the reference and silently discarding all pacer mutations. Result: the allowlist state file at `~/.hermes/scripts/fleet_watchdog.allowlist_state.json` was never being written. Weekly pace was effectively a no-op.
- **Fix:** `if state is None: state = {}`. Mutations now propagate, state file gets written, second run of the same week correctly silences the 3 weekly cards.
- All 15 v1.1 tests still pass (Tests 7 and 8 cover weekly pace; both green after fix).
- See [[2026-06-07 - gbrain pivot + v1.1 live-swap post-mortem|evening session log]] for the full pivot context (gbrain to ZE, wrapper script env override, doctor false positive).

**For Hermes:** v1.0 cron `3d0d9620c031` is presumably still running every 30 min. Disable it now that v1.1 (live via `fleet_watchdog_dryrun.sh` with `--dry-run` removed) is operational, or you'll get duplicate pages on the same 3 orphans.

---

## 1. Problem (recap from v1.0)

The v1.0 fleet-watchdog correctly identifies orphan cards (cards assigned to non-routable profiles), but has no way to distinguish *signal* orphans (real parked work that needs action) from *known* orphans (work that has decisions in comments but a dead assignee) and *artifact* orphans (Mavis→Hermes routing cards, not work at all).

v1.0 behavior: page everything, every 30 min. Result: 3 active orphans produce ~144 pages/day from parked work, and any future Mavis intake card will false-positive the same way `t_17dea89f` did.

v1.1 goal: distinguish the three categories, silence the latter two, preserve the signal value of the first.

---

## 2. Goals

**In scope:**
- Card-ID-specific allowlist with reason, ack-by, and pacer
- Pattern-based allowlist (assignee=X, title-prefix=Y) for artifact classes
- Pacing modes: `never` (silent), `weekly` (page once per week), `monthly`, `on_status_change` (page only when status flips)
- Config file in YAML, lives alongside the script
- Backward-compatible with v1.0 (empty allowlist = current behavior)
- Self-tests for the allowlist logic

**Out of scope (v1.2+):**
- Per-invariant severity override (e.g., "all orphan on lead-architect is log-tier")
- Auto-detection of retired profiles from `~/.hermes/.archive/profiles/retired-*/`
- Per-profile pacer (e.g., "openclaw orphans: monthly; lead-architect orphans: weekly")
- The 25 frozen DreBrain items are in terminal statuses and are correctly filtered by the existing `status in (done, cancelled, archived)` check. No v1.1 work needed for them.

---

## 3. Configuration File

**Location:** `~/.hermes/scripts/fleet_watchdog.allowlist.yaml`
**Format:** YAML 1.2, ~50 lines max for the typical config
**Load behavior:** Loaded at script start. If file is missing → log info, continue with no allowlist. If file is malformed → log error, exit 70 (config error), do not run invariants. This prevents silent misconfig.

### 3.1 Schema (full)

```yaml
# ~/.hermes/scripts/fleet_watchdog.allowlist.yaml
# v1.1 allowlist for the fleet-watchdog
# See: 99 _system/specs/fleet-watchdog-v1.1-allowlist.md (Mavis, 2026-06-07)

version: 1

# Card-ID allowlist — known, acknowledged, paged on a pacer.
# Use for: real parked work that has decisions but a dead assignee.
card_allowlist:
  - card_id: t_dfbbfe09
    reason: "Desktop bridge work; Q4 decision in comments (local-only loopback). Awaiting Hermes re-assignment or close."
    pace: weekly
    acknowledged_by: mavis
    acknowledged_at: 2026-06-07
    # expires: 2026-07-07  # optional; null = permanent until removed

  - card_id: t_a921b25d
    reason: "P5 Pillar 1 (Cost); Q1 decision in comments. lead-architect profile DORMANT — re-assign or close."
    pace: weekly
    acknowledged_by: mavis
    acknowledged_at: 2026-06-07

  - card_id: t_d58e2409
    reason: "P5 Pillar 2 (Latency); Q1 decision in comments. lead-architect profile DORMANT — re-assign or close."
    pace: weekly
    acknowledged_by: mavis
    acknowledged_at: 2026-06-07

  # Log-tier: t_c6fca5fa is on eng-orchestrator (SCHEDULER), not page-tier.
  # v1.0 already handles SCHEDULER → log-tier. No allowlist entry needed.
  # Documented here for completeness.

# Pattern allowlist — dynamic, for artifact classes.
# Use for: things that will recur and aren't card-specific.
pattern_allowlist:
  - name: "Mavis intake cards (assignee=mavis)"
    description: "Mavis→Hermes routing artifacts. Per the new convention (see Mavis memory 2026-06-07), these arrive with status=cancelled. This pattern is a safety net for the convention."
    match:
      assignee_equals: "mavis"
    pace: never
    reason: "External intake artifact, not dispatchable work"

  - name: "Mavis intake title prefix"
    description: "Backup for the assignee=mavis check; some cards may not have assignee set, or assignee may be empty string."
    match:
      title_starts_with: "Mavis intake:"
    pace: never
    reason: "External intake artifact, not dispatchable work"
```

### 3.2 Field reference

| Field | Required | Type | Notes |
|---|---|---|---|
| `version` | yes | int | Always 1 for v1.1. Bumped on breaking changes. |
| `card_allowlist` | no | list | Each entry is one card. |
| `pattern_allowlist` | no | list | Each entry is one pattern. |
| `card_allowlist[].card_id` | yes | string | Exact card ID match. |
| `card_allowlist[].reason` | yes | string | Human-readable, shown in audit logs. |
| `card_allowlist[].pace` | yes | enum | `never`, `weekly`, `monthly`, `on_status_change`. See §4. |
| `card_allowlist[].acknowledged_by` | yes | string | Who acked (e.g., `mavis`, `hermes`, `andre`). For audit. |
| `card_allowlist[].acknowledged_at` | yes | date | YYYY-MM-DD. For audit. |
| `card_allowlist[].expires` | no | date | After this date, the allowlist entry is ignored (card returns to "page" status). |
| `pattern_allowlist[].name` | yes | string | Human-readable identifier. |
| `pattern_allowlist[].match` | yes | object | One or more match rules. AND'd together. |
| `pattern_allowlist[].match.assignee_equals` | no | string | Exact assignee match. |
| `pattern_allowlist[].match.title_starts_with` | no | string | Title prefix match (case-sensitive). |
| `pattern_allowlist[].pace` | yes | enum | Same as card. |
| `pattern_allowlist[].reason` | yes | string | For audit. |

---

## 4. Pacing Semantics

| Pace | Behavior |
|---|---|
| `never` | Always skipped. Never paged, never logged, never counted in daily summary. (Used for artifact classes.) |
| `weekly` | Paged only on the first run of each ISO week (Monday 00:00 — Sunday 23:59:59 in `HERMES_TIMEZONE`, default CT). On other days, skipped silently. Logged in daily summary as "weekly: 1/3 paged this week." |
| `monthly` | Paged only on the first run of each calendar month. On other days, skipped. |
| `on_status_change` | Paged only when the card's status has changed since the last run. Implementation: track last-seen status in a sidecar JSON (`fleet_watchdog.allowlist_state.json`), compare on each run, page if different, update sidecar. |

**Default pace** (no allowlist match): current v1.0 behavior — page every tick.

**Time zone:** pacing uses the local timezone where the script runs. Document the assumption in the script's docstring.

---

## 5. Code Changes

All in `~/.hermes/scripts/fleet_watchdog.py`. Estimated ~80-120 new lines + ~30 lines of test additions. No schema changes to the kanban DB.

### 5.1 New module: `load_allowlist(path: Path) -> dict`

- Reads YAML, returns parsed dict
- Validates schema (version=1, required fields, enums)
- Exits 70 on malformed config
- Logs info "Allowlist loaded: N card entries, M pattern entries"

### 5.2 New module: `should_skip(card: dict, allowlist: dict, state: dict) -> tuple[bool, str]`

- Returns `(skip: bool, reason: str)`
- Checks card_allowlist first (exact match)
- Then pattern_allowlist (assignee_equals, title_starts_with)
- For each match, applies pacer logic
- Returns the first match's reason (or `False, ""` if no match)

### 5.3 Modify `check_orphans(tasks: list[dict]) -> list[dict]`

- Add allowlist param
- Skip cards where `should_skip` returns True
- For `on_status_change` pace, update state sidecar

### 5.4 New module: `pacer_should_page(pace: str, last_state: dict) -> bool`

- Encapsulates the 4 pacing modes
- Reads/writes `~/.hermes/scripts/fleet_watchdog.allowlist_state.json` for `on_status_change`

### 5.5 New CLI flag: `--list-allowlist`

- Dumps current allowlist in human-readable form
- Useful for ops review: "what's currently being silenced and why?"

### 5.6 New CLI flag: `--dry-run`

- Runs all invariants, prints what WOULD be paged, exits 0
- No writes to JSONL, no Telegram delivery
- Use this in the migration window

### 5.7 Modify the cron registration

- Cron stays the same: `*/30 * * * *`
- Schedule unchanged — the allowlist is what makes it quiet, not the cron

---

## 6. Test Plan Additions

Extend `~/.hermes/scripts/tests/test_fleet_watchdog.sh` with these synthetic scenarios:

| # | Test | Setup | Expected |
|---|---|---|---|
| 4 | Card-ID allowlist silence | Insert `t_test_allow_001`, add to allowlist with `pace: never` | No page-tier output |
| 5 | Pattern allowlist (assignee=mavis) | Insert `t_test_allow_002` with `assignee='mavis'` and matching pattern | No page-tier output |
| 6 | Pattern allowlist (title prefix) | Insert `t_test_allow_003` with title `Mavis intake: foo` and matching pattern | No page-tier output |
| 7 | Weekly pace outside Monday | Insert `t_test_allow_004` with `pace: weekly`, run on Wed (skip; date is 2026-06-10 = Wed) | No page-tier output |
| 8 | Weekly pace on Monday | Same card, run on Mon 2026-06-08 | Page-tier output (one page) |
| 9 | `on_status_change` pace — first run | Insert card, run | Paged (first observation) |
| 10 | `on_status_change` pace — same status | Same card, run again | Not paged (no change) |
| 11 | `on_status_change` pace — status changed | UPDATE card status, run | Paged (status changed) |
| 12 | Empty allowlist | Allowlist file is empty `{}` | Current v1.0 behavior |
| 13 | Malformed YAML | Allowlist file has bad syntax | Exit 70, no run |
| 14 | Non-existent card in card_allowlist | Card ID in allowlist doesn't exist in DB | No crash, no false page (skipped silently with log) |
| 15 | `--list-allowlist` flag | Run with flag | Prints the parsed allowlist, exits 0 |

The original 3 tests (Orphan, Double-dispatch, Crash-loop) keep passing — they're orthogonal to the allowlist.

---

## 7. Migration / Rollout

1. **v1.1 ships in a separate commit** (not on top of v1.0). v1.0 cron keeps running until v1.1 is verified.
2. **Dry-run first.** Hermes updates the cron command to `python3 .../fleet_watchdog.py --dry-run` for 24h, watches the JSONL, confirms expected output (3 orphans now silent, 0 new false positives, no real orphans being suppressed).
3. **Swap to v1.1.** Update the cron command to invoke the v1.1 script (or replace the file in place if version-bumped by filename).
4. **Verify first live tick.** Watch the Telegram chat at the next `*/30` boundary, confirm 0 pages for the 3 allowlisted cards.
5. **Leave dry-run flag in place** as a manual override (`fleet_watchdog.py --dry-run` for ops checks).
6. **Don't roll back to v1.0** unless v1.1 misbehaves — the 3 orphans are a known cost of the rollout, not a regression.

---

## 8. Observability Additions

- **Log line on every skip:** "allowlist skip: card_id=X, reason=Y, pace=Z" at INFO level, goes to `~/.hermes/logs/fleet_watchdog.jsonl` (existing log, not a new file).
- **Daily summary addition:** "Allowlist activity: N cards skipped, M patterns matched, P weekly paged, Q monthly paged, R on_status_change paged." Helps verify the allowlist is doing what you think.
- **First-week health check:** at the end of the first 7 days post-v1.1, run `fleet_watchdog.py --list-allowlist` + check the JSONL for "allowlist skip" entries. If the skip count is 0 for a week, the allowlist may be over-matching or the cards got resolved.

---

## 9. Open Questions for Hermes (need his call)

**All 7 RESOLVED 2026-06-07 17:02 CT. Decisions in §12.**

1. **Weekly vs monthly pacing for the 3 page-tier orphans.** → §12 Q1
2. **`on_status_change` state file location.** → §12 Q2
3. **String match vs regex for `Mavis intake:` prefix.** → §12 Q3
4. **Allowlist scope — orphan only or extend to other invariants.** → §12 Q4
5. **Ack timestamp format.** → §12 Q5
6. **`--list-allowlist` output format.** → §12 Q6
7. **Config file ownership — ship with code or vault-managed.** → §12 Q7

---

## 10. What's NOT in v1.1 (so we don't scope-creep)

- Daily-summary cron registration (separate item, mentioned in v1.0 review)
- Per-profile pacer (only card-ID and pattern pacer in v1.1)
- Auto-detection of retired profiles (v1.2+)
- Per-invariant severity override (v1.2+)
- The 25 frozen DreBrain items (terminal status, already filtered — no allowlist work needed)

---

## 11. Reference

- **v1.0 ship report** (Hermes, 2026-06-07 ~16:00 CT): in chat, references the 25-frozen-items overestimation and the v1.1 deferral note
- **Mavis close-out of `t_17dea89f`** (2026-06-07 16:49 CT): event id 82763 in `task_events`, comment id 82 in `task_comments` for `t_17dea89f`
- **Mavis memory** (chief-of-staff, 2026-06-07): "Mavis→Hermes routing cards: status=cancelled at creation, not status=ready" hard correction
- **Org chart** (Andre-locked 2026-06-07): Mavis routes, Hermes operates. v1.1 design and config changes are Hermes's build; this spec is Mavis's directive.

---

## 12. Implementation Directives (locked 2026-06-07 17:02 CT)

**Status: LOCKED.** All 7 open questions resolved. Build order set. Ready to implement.

### 12.1 Locked Decisions (Hermes answers)

**Q1: Pacing for the 3 page-tier orphans → `weekly`.**
3 pages/week total is trivial overhead for active decisions sitting in comments. Monthly (30 days between checks) is too long. The §3.1 schema already has `pace: weekly` on the 3 entries — keep it.

**Q2: `on_status_change` state file → sidecar JSON at `~/.hermes/scripts/fleet_watchdog.allowlist_state.json`.**
Kanban DB is for task state, not watchdog tracking state. Sidecar is self-contained, same directory as the script + config, no schema migration. If the file gets corrupted/deleted, worst case = one extra page on next tick, recoverable. No DB column.

**Q3: Match style → string, case-sensitive, exact prefix.**
Convention is established, prefix is fixed. Regex is overkill for a known constant. Convention is controlled by Mavis herself, so edge cases won't surface. v1.2 can revisit if a need emerges.

**Q4: Allowlist scope → orphans only in v1.1.**
Frozen-card and zombie-card invariants have different semantics (time-based, not profile-routability) and would need a different allowlist shape. Don't mix concerns. v1.2 can extend with an `invariant: orphan|frozen|zombie` field per entry if needed.

**Q5: Ack timestamp format → `YYYY-MM-DD` (date-only).**
Sub-day precision adds nothing for audit on a human decision. Matches daily-summary pattern and the existing YAML.

**Q6: `--list-allowlist` output → YAML.**
Same format as the config file — human-readable, diffable, consistent. JSON available via `python3 -c` piping if anyone needs it. Don't add format flags to the script.

**Q7: Config file ownership → ships with code in `~/.hermes/scripts/`.**
Two reasons:
1. The config is infrastructure (which cards to silence), not domain knowledge (what the cards mean). It belongs next to the code it controls. Splitting across directories creates config drift.
2. The org chart says no direct Mavis→Hermes file writes. Vault-sync (`~/MiniMax-Agent/...` → `~/.hermes/scripts/`) violates that boundary implicitly. Better: Mavis sends new allowlist entries via Andre (task comment or directive), Hermes updates the config. Audit trail via Andre, config stays with code, no sync step.

**For the 3 pre-filled entries:** Hermes creates the YAML file with them included in the v1.1 build commit. No separate Mavis step needed.

### 12.2 Build Order (sequential, with checkpoints)

| # | Step | What | Checkpoint |
|---|---|---|---|
| 1 | **Code** | Add the 7 modules from §5 to `fleet_watchdog.py`. Use the YAML schema from §3.1 verbatim. All 4 pacing modes from §4. | Code review by Hermes himself (lint clean, no new lint warnings) |
| 2 | **Tests** | Add the 12 new tests from §6 to `test_fleet_watchdog.sh`. Original 3 must keep passing. | All 15 tests pass locally |
| 3 | **Config** | Create `fleet_watchdog.allowlist.yaml` with the 3 card entries + 2 pattern entries from §3.1. Pre-filled. | `fleet_watchdog.py --list-allowlist` prints the 5 entries cleanly |
| 4 | **State file** | Initialize empty `fleet_watchdog.allowlist_state.json` (just `{}`). Will populate on first `on_status_change` match. | File exists, valid JSON `{}` |
| 5 | **Dry-run** | Run `fleet_watchdog.py --dry-run` for 24h. Observe JSONL output. Expect: 0 pages for the 3 allowlisted cards, 0 false positives on Mavis intake patterns, 0 real orphans being suppressed. | After 24h: dry-run report with JSONL excerpts, anomaly list (expected: empty) |
| 6 | **Swap** | Update the cron command to invoke v1.1. Cron ID stays `3d0d9620c031`. Verify first live tick. | First `*/30` boundary after swap: 0 pages for the 3 allowlisted cards, all other invariants still firing correctly |
| 7 | **Report back** | When v1.1 is live and first dry-run + live tick is clean, report back to Mavis. | Full report with both the dry-run JSONL and the first live tick verification |

### 12.3 Reporting Expectations

- **After step 4** (state file init): one-line note "config + state initialized, ready for dry-run."
- **After step 5** (24h dry-run complete): full report with JSONL excerpts, what was paged, what was suppressed, any anomalies. If something looks wrong, flag and pause — don't proceed to step 6.
- **After step 6** (first live tick): "live v1.1 first tick clean" + summary of what fired and what was suppressed. Or failure details.

Mavis will do a **one-pass review** when v1.1 reports live. One review, not iterative — same commitment as the v1.0 review (cf. handoff 2026-06-07 evening).

### 12.4 v1.1 Commit Boundary

v1.1 ships in a single commit (or split into code/tests/config if cleaner), containing:
- `fleet_watchdog.py` updated
- `fleet_watchdog.allowlist.yaml` created
- `fleet_watchdog.allowlist_state.json` initialized (empty `{}`)
- `test_fleet_watchdog.sh` extended

**Cron registration stays the same:** ID `3d0d9620c031`, schedule `*/30 * * * *`, `no_agent: true`, `deliver: origin`. The cron command path is updated to point at v1.1 if the filename changes, or kept the same if the file is replaced in place.

### 12.5 What Changes vs the Initial Spec

- §3.1 schema: `pace: weekly` is now the *confirmed* default for the 3 page-tier orphans (was: "your call"). No code change.
- §5.4 pacer: state file path is now `~/.hermes/scripts/fleet_watchdog.allowlist_state.json` (was: same, but listed as open question). No code change.
- §5.3 should_skip: string match is now confirmed (was: open question). No code change.
- §5.5 list-allowlist: YAML output is now confirmed (was: open question). No code change.
- §3 location: config file ships with code, no vault sync (was: open question, with vault-sync as alternative). Code is unchanged; the decision affects who maintains entries (Hermes via Andre directive).
- §10 unchanged: scope-creep items stay in v1.2.

**Net change: zero new open questions, zero deferred decisions. Build per §12.2.**

— Mavis (chief of staff, senior agent in the fleet)
  Session `mvs_5af152b1ed364fa58a9e18801092ceef`
  2026-06-07 17:02 CT
