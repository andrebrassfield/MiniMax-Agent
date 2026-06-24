---
date: 2026-06-23
type: spec
status: draft
decider: Andre (pending)
conversation: mvs_ea5178435aa9441d855a9306735cf4eb
reversibility: partial
informed_by:
  - 02 Notes/decisions/2026-06-22-two-track-model.md (the new architecture)
  - 03 Projects/FB-Engine/postmortems/2026-06-18-2000-cdp-discovery-fail.md (the 2026-06-18 PM cron fail + the never-applied fix)
  - 03 Projects/FB-Engine/postmortems/2026-06-23-1330-cdp-bridge-offline.md (today's AM cron fail, 2nd consecutive)
  - ~/.mavis/agents/mavis/skills/two-track-handoff/SKILL.md
  - ~/.mavis/agents/mavis/skills/fb-engine/README.md
replaces:
  - ~/.mavis/agents/mavis/crons/fb-read-scribe-am.md
  - ~/.mavis/agents/mavis/crons/fb-read-scribe-pm.md
  - ~/.mavis/agents/mavis/crons/fb-propose-am.md
  - ~/.mavis/agents/mavis/crons/fb-propose-pm.md
  - ~/.mavis/agents/mavis/crons/fb-capture.md
---

# FB-Engine Cron v2 — two-track redesign

> Drafted 2026-06-23 13:33 CT by Mavis (Track 1) in response to the 2nd consecutive AM cron failure with the same root cause. **This is a spec, not a command. Awaiting Andre's "go" before Track 2 spawn.**

## Context

The FB-Engine cron chain (5 crons: `fb-read-scribe-am`, `fb-propose-am`, `fb-read-scribe-pm`, `fb-propose-pm`, `fb-capture`) was shipped 2026-06-18 against a thin-harness model: each cron is a shell that calls one Python script in sequence, and the chain breaks the moment any pre-condition fails.

**Two consecutive failures with the same root cause:**

| Date | Cron | Step failed | Root cause |
|---|---|---|---|
| 2026-06-18 20:00 CT | `fb-read-scribe-pm` | Step 3 (`fb-group-reader` → CDP discovery) | `find_cdp_port()` filters out `headless=new` Chrome + rejects port 0. **Fix was identified in the postmortem but never applied.** |
| 2026-06-23 13:30 CT | `fb-read-scribe-am` | Step 3 (same) | Chrome on box has no `--remote-debugging-port` flag at all. mavis browser bridge native host offline. **The 2026-06-18 fix wouldn't have helped either** — there's no Chrome with any port right now. |

The 2026-06-22 two-track decision (Tiago Forte's "you don't need ten agents, you need two tracks" + the 3-day rate-limit incident) tells us the *whole shape* is wrong, not just one script. Today's failure is the second proof.

**What the two-track decision implies for the FB-Engine cron:**

> Skills become the workforce. Subagent channel stays verifier-only. Mavis = single chief running two tracks.

Today the FB-Engine cron is *neither* a fat skill *nor* a Track 2 handoff — it's a thin shell that depends on Chrome being up. That makes it the worst of both worlds: it burns the cron-track budget (20% allocation) but produces nothing when the substrate is missing, and it has no recovery loop, no rate-limit awareness, and no graceful degradation.

## Decision

**Replace the 5 thin FB-Engine crons with 1 fat-skill-backed cron that uses the two-track handoff pattern.**

The new shape:

```
┌─────────────────────────────────────────────────────────────┐
│ fb-engine-loop (cron, daily AM + PM)                        │
│   • 3-line shell: source env → budget gate → spawn          │
│   • 1 Track 2 session per fire                             │
└──────────────────────┬──────────────────────────────────────┘
                       │  spawn (mavis session new, --from cron)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Track 2 session loads skill: fb-engine-loop (v2.0)         │
│                                                             │
│  Step 1: Self-heal substrate                                │
│    • ps grep --remote-debugging-port → if found, use it    │
│    • lsof + curl /json/version probe → handles port 0       │
│    • mavis browser tool start (1 retry) → managed Chrome    │
│    • HALT + Telegram ping ONCE per 24h, not every cycle     │
│                                                             │
│  Step 2: Run fb-session-guardian (now with port-0 fallback) │
│                                                             │
│  Step 3: Run fb-group-reader                                │
│                                                             │
│  Step 4: If 0 posts → graceful degradation:                 │
│    • Generate 1 T1 Value Bomb from cached ammunition.mdl   │
│    • Mark draft `status: source=cache, fb_session=offline`  │
│    • Surface to Telegram with the cache fallback flag       │
│                                                             │
│  Step 5: Run fb-draft-scribe                                │
│                                                             │
│  Step 6: ea-fb-draft-approval → Telegram propose            │
│                                                             │
│  Step 7: Report back to cron (Track 1) with N drafts        │
│          + failure-reason if any step failed                │
└──────────────────────┬──────────────────────────────────────┘
                       │  report (mavis communication send)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Cron session (Track 1) — verification gate                 │
│   • Verify handoff reported back within 5 min               │
│   • Verify N drafts landed in 03 Projects/FB-Engine/drafts/ │
│   • Verify no fabricated posts (post count == captured)     │
│   • If verification fails → Telegram HIGH-priority ping     │
└─────────────────────────────────────────────────────────────┘
```

**Why this is the right shape per the 2026-06-22 decision:**

1. **Fat skill, not thin shell.** All 7 steps + their halt conditions + recovery logic live in one `SKILL.md` + one Python driver. The cron is a 3-line trigger. Intelligence up, execution deterministic.
2. **Two-track pattern, not subagent chain.** Track 1 (this cron) is cheap. Track 2 (one Mavis session) gets the full model capability for the read/draft loop. Subagent channel stays verifier-only (we can spawn a verifier on Track 2's output if Andre wants belt-and-suspenders).
3. **Self-healing, not brittle HALT.** The 2026-06-18 PM fail was a 2-step fix that was never applied. The 2026-06-23 AM fail needed a *third* layer (manage the Chrome itself). All three layers live in the fat skill.
4. **Graceful degradation, not zero-output.** When the read fails, the skill still produces something useful — a T1 draft from `ammunition.mdl` cache — with the source clearly flagged. Better than 0 drafts (the user can't act) and better than fake drafts (corrupts the queue).
5. **Rate-limit aware.** Cron shell checks `mavis usage list --json` for ≥30% remaining *before* spawning. If under, the cron HALTs with a clean "budget gate" diagnostic, not a vague substrate error.

## Components

### A. New skill: `fb-engine-loop` (v2.0)

Path: `~/.mavis/agents/mavis/skills/fb-engine/fb-engine-loop/`

```
fb-engine-loop/
├── SKILL.md                      # the procedure (this spec condensed)
├── scripts/
│   ├── heal_substrate.py         # Step 1: 3-layer CDP discovery
│   ├── run_loop.py               # Steps 2-7: thin wrapper that calls the existing skills
│   └── verify_report.py          # post-loop audit (no fabrication, post count == captured)
└── state/
    └── failure_state.json        # tracks consecutive failures, last Telegram ping
```

**`heal_substrate.py`** — the 3-layer CDP discovery. Replaces the brittle `find_cdp_port()` in `fb-group-reader/scripts/read.py`. Layers (in order):

1. `ps -axww -o command | grep -- "--remote-debugging-port=[1-9]"` — fast path, returns immediately if a real port is up
2. `lsof -nP -iTCP -sTCP:LISTEN | grep -i chrome | awk '{print $9}' | sed 's/.*://'` → for each port, `curl -s http://127.0.0.1:<port>/json/version | jq -r '.webSocketDebuggerUrl'` — handles the port-0 case the 2026-06-18 postmortem identified
3. `mavis browser tool start --managed --cdp-port 58632` — last resort, managed Chrome. **MUST check that the user's existing Chrome is not already on 58632 first** (don't double-launch)

If all 3 layers return nothing → write to `state/failure_state.json` (increment counter), and if the counter crossed 1 in the last 24h, send ONE Telegram ping. Don't spam.

**`run_loop.py`** — the thin wrapper. Imports the existing skills (`fb-session-guardian`, `fb-group-reader`, `fb-draft-scribe`, `ea-fb-draft-approval`) as Python modules (they're already `python3` scripts, so subprocess is fine). No new business logic — the existing skills are sound; they just need a self-healing shell around them.

**`verify_report.py`** — runs after the loop. Audits:
- `len(drafts/)` increased by the expected amount
- every draft file references a real `post_id` from the captured JSON OR has `source: cache` in its frontmatter
- no draft file is empty / has placeholder text

### B. Cron shell rewrite: `fb-engine-loop` (cron, daily 2x)

Path: `~/.mavis/agents/mavis/crons/fb-engine-loop.md`

Replaces the 5 old crons. Schedule: 08:30 CT (AM) and 20:00 CT (PM) — keeps the FB cadence (twice-daily, community model, no velocity rush).

```markdown
---
name: fb-engine-loop
schedule: 30 13 * * *
timezone: America/Chicago
session:
  mode: new
  keepSessions: 14
---

FB-Engine two-track loop — AM fire.

1. Source telegram env: `bash -c 'source ~/.mavis/secrets/fb-telegram.env'`
2. Budget gate: `mavis usage list --json | jq '.summary.totalTokens'` — if lifetime tokens / daily cap > 0.7, HALT with "budget low"
3. Spawn Track 2:
   ```bash
   mavis session new mavis --from <cron-session> \
     --model minimax/MiniMax-M2.7 \
     --prompt "Track 2 handoff: load skill fb-engine-loop, run the 7-step loop, report back to <source-session> with N drafts written + failure-reason if any step halted."
   ```
4. Wait 5 min for report. If no report → Telegram HIGH-priority ping to Andre.
```

**PM cron is a separate file** (`fb-engine-loop-pm.md`) with `schedule: 0 1 * * *` (01:00 UTC = 20:00 CT). Same body, different schedule.

### C. Code changes to existing skills

Two small patches. Both are already documented in prior postmortems; we're finally applying them as part of the redesign.

1. **`fb-group-reader/scripts/read.py` — `find_cdp_port()` patch** (the 2026-06-18 fix that was never applied):
   - Remove the `if "headless" in line.lower(): continue` filter (line 81)
   - Add port-0 fallback path (probe via `lsof` + `curl /json/version`) — but **note**: this layer is now redundant with `heal_substrate.py` Layer 2. Apply the headless filter removal only; let the fat skill own the port-0 fallback. Single source of truth for substrate recovery.

2. **`fb-session-guardian/scripts/guard.py` — no change**. The guardian is structurally sound. The failure is upstream (substrate discovery), not the auth check itself.

### D. Migration: kill the 5 old crons

After Track 2 implementation runs and the new cron fires cleanly twice (AM + PM, 2 consecutive days = 4 successful runs):

```bash
mavis cron delete mavis fb-read-scribe-am
mavis cron delete mavis fb-read-scribe-pm
mavis cron delete mavis fb-propose-am
mavis cron delete mavis fb-propose-pm
mavis cron delete mavis fb-capture
```

Old cron files moved to `~/.mavis/agents/mavis/crons/_archived/2026-06-23-fb-engine-cron-v1/`. The state files (`fb-read-scribe-am.sessions.json` etc.) go with them — they're append-only history, not configuration.

**Do NOT delete the old crons before the new one is proven.** Two consecutive clean days = proven. Anything less is jumping the gun.

## Verification gate

Track 1 (the cron session) verifies the Track 2 handoff succeeded by checking:

| Check | PASS condition |
|---|---|
| Track 2 reported back | `mavis session list` shows the Track 2 session status is `finished` or `completed` within 5 min |
| N drafts landed | `ls 03 Projects/FB-Engine/drafts/ \| wc -l` increased by ≥ 1 (graceful degradation allows 1 T1 cache draft even if read failed) |
| No fabrication | every draft's frontmatter `source` field is either `fb-group-reader` (real posts) or `cache` (graceful degradation). No `source: synthetic` (that was the 2026-06-18 synthetic-001 incident — never again). |
| No spam | if HALT path was taken, `state/failure_state.json` shows exactly 1 Telegram ping in the last 24h |

If any check fails → Telegram HIGH-priority ping to Andre with the specific failure. Track 1 does NOT attempt to fix Track 2's output.

## Halt conditions

Track 2 halts and reports back (no fix attempts) if:

1. `heal_substrate.py` returns no CDP endpoint after all 3 layers
2. `fb-session-guardian` returns FAIL after substrate is recovered (real login wall — not our problem to fix)
3. `fb-group-reader` captures 0 GraphQL responses after a successful guardian PASS (this is the "user not a member of Group" or "FB A/B test changed the response shape" case — Track 2 writes the failure to its output path, not a fake draft)
4. `fb-draft-scribe` errors on a post that the parser couldn't structure (Track 2 logs the post_id, continues with the next one)
5. `ea-fb-draft-approval` Telegram send fails (network, token revoked — Track 2 keeps the drafts, just can't propose them; reports back "N drafts written, propose-failed")
6. `mavis usage` shows <30% budget remaining at any point mid-loop (Track 2 saves state, HALTs)

## Stop condition

Track 2 stops when all 7 steps complete (regardless of per-step PASS/FAIL), OR a halt condition is hit, OR 15 minutes wall-clock elapses (whichever first). 15 min is generous — typical AM cycle today would be 90 sec.

## Rate-limit budget

Track 2's allocated ceiling: **30% of remaining** at spawn time, per the 2026-06-22 decision. Expected consumption: ~2-5M tokens for a full read+draft cycle (vs. ~21.6M Track 1 baseline from 2026-06-22). The cron shell's budget gate at step 2 (lifetime tokens / daily cap > 0.7 → HALT) is the load-bearing check.

**Today's gate (2026-06-23 13:33 CT):** lifetime 1,416,045,987 tokens / $1,096.77. Yesterday's daily was 21.8M / $21.96. **No rate-limit-tracker log for today exists** (the 40904 stale-cache bug from 2026-06-22 is still blocking the cron). If Andre approves and we spawn Track 2 today, the budget gate will see a fresh `mavis usage list --json` and decide. If the gate fails, Track 2 simply doesn't spawn — the failure is clean, not a hidden crash.

## What would change my mind

- If the 2-failures-per-week pattern resolves on its own (e.g., Andre's Chrome is reliably on the bridge) → the 3-layer substrate healing is overkill; downgrade to the 2-layer fix from the 2026-06-18 postmortem alone
- If `mavis browser tool start` proves unreliable as a managed-Chrome fallback (e.g., it doesn't preserve the user's existing FB session) → drop Layer 3, accept that "no Chrome up" is a hard HALT (current state, just made explicit)
- If the cache-fallback T1 drafts prove low-quality (Andre rejects them at the Telegram approval step) → drop Step 4, the cron becomes pure HALT-on-read-fail (cleaner but spammier)
- If Track 2 spawn turns out to burn 3x+ the expected budget (the model is less efficient than estimated) → switch the budget gate to "hard cap at 5M tokens per Track 2 spawn" instead of percentage

## Reversal log

None yet. Draft.

## Cross-references

- Two-track handoff procedure: `~/.mavis/agents/mavis/skills/two-track-handoff/SKILL.md`
- Today's postmortem: `03 Projects/FB-Engine/postmortems/2026-06-23-1330-cdp-bridge-offline.md`
- 2026-06-18 postmortem with the never-applied fix: `03 Projects/FB-Engine/postmortems/2026-06-18-2000-cdp-discovery-fail.md`
- Source decision: `02 Notes/decisions/2026-06-22-two-track-model.md`
- Existing skill README (the architecture rules): `~/.mavis/agents/mavis/skills/fb-engine/README.md`
- Rate-limit tracker (broken cron, manual workaround): `~/.mavis/agents/mavis/crons/rate-limit-tracker.md`
