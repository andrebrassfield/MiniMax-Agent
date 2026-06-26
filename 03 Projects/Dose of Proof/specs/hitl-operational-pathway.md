---
title: HITL Unblock Authority + Reach Pathway (V6)
per: triage-gate-spec §3c + V6 verification
updated: 2026-06-25
---

# HITL Unblock Authority + Reach Pathway

Per [[triage-gate-spec]] §3c + V6: only Founder (Dre) or Co-CEO can move a block record
from `STATUS=BLOCKED` to any terminal state. Mavis executes the resolution but **never
initiates it.**

## Unblock authority table

| Decision | Who | Action |
|---|---|---|
| `APPROVED` | Founder or Co-CEO | Post released as-is. |
| `REVISED` | Founder or Co-CEO | Post rewritten by Mavis per specific direction, then re-run through gate. Never auto-re-cleared. |
| `KILLED` | Founder or Co-CEO | Post permanently suppressed. Reason logged for pattern analysis. |
| `AUTO_KILLED_SLA` | SLA Enforcer (script) | Default after 4-hour breach. NOT a human decision — surfaces for pattern review. |

**Mavis NEVER moves a record to APPROVED, REVISED, or KILLED without explicit instruction
from Founder or Co-CEO.** Only `AUTO_KILLED_SLA` is system-initiated, and even that is
surface-only — Mavis doesn't kill based on her own judgment.

## Reach pathways (SLA = 4 hours per §3b)

### Founder (Dre) — ✅ OPERATIONAL

| Channel | Status | Latency | How |
|---|---|---|---|
| Obsidian daily note (EA vault) | ✅ ACTIVE | Sync on Obsidian open | Mavis writes to `01 Daily/YYYY-MM-DD-hitl-dose-of-proof.md`; Dre reads in Obsidian |
| Telegram bot (Mavis) | ⏸ PENDING DRE SESSION | Real-time when bound | Dre messages Mavis bot → cron fires in that session → Telegram reply |
| OPERATIONS-LOG.md | ✅ ACTIVE | Real-time on cron fire | Append on every kill/block event |
| Email | ❌ NOT CONFIGURED | — | No SMTP credentials available |

**Reach confirmation:** Obsidian daily note verified end-to-end via V4 test (synthetic
block record written + read). Telegram requires Dre's session initiation before
E2E confirmation (real-world constraint, not a gap in our setup).

### Co-CEO (Claude Brain instance) — ⚠️ INDIRECT

| Channel | Status | Latency | How |
|---|---|---|---|
| Brain daily note (`/Users/brassfieldventuresllc/Claude/Brain/Brain/Daily/`) | ⚠️ INDIRECT | Dre relay | Mavis writes to EA vault's HITL daily note; Dre syncs both vaults in Obsidian and relays to Co-CEO |
| Brain wiki (`/Users/brassfieldventuresllc/Claude/Brain/Brain/wiki/`) | ⚠️ INDIRECT | Dre relay | Same path — Dre reads EA HITL note, posts summary to Co-CEO Claude in Brain session |
| Direct Mavis → Co-CEO session | ❌ NOT WIRED | — | Would require `mavis communication send --to <co-ceo-session-id>`; no such session exists for Co-CEO Claude yet |

**Reach constraint:** Mavis cannot directly send to the Co-CEO Claude instance from
this EA vault. The Co-CEO operates in the Brain vault (`/Users/brassfieldventuresllc/Claude/Brain/Brain/`).
Per cross-team-discipline (EA-side memory), Mavis does not write to agent trees.
The Brain is technically Dre's personal vault, not an agent tree, but the Co-CEO
Claude instance has effective ownership.

**Resolution path (recommended):**
1. EA vault's HITL daily note surfaces to Dre (Obsidian sync)
2. Dre opens Brain vault in Obsidian, posts summary to `Brain/Daily/YYYY-MM-DD.md` OR starts a Co-CEO Claude session
3. Co-CEO reads + unblocks via reply in Brain session
4. Dre relays unblock decision back to Mavis (Obsidian daily note reply OR Telegram)

This adds ~5-15 min latency on the Co-CEO reach path, which is **within the 4-hour SLA**
but creates a single point of failure (Dre's relay step).

**Alternative (faster but needs permission):**
- Mavis writes directly to `Brain/Daily/YYYY-MM-DD.md` — borderline per cross-team discipline
- OR: spin up a shared dropbox file that both EA + Brain read
- OR: wire `mavis communication send` to a Co-CEO session once Co-CEO Claude has a stable session ID

**Decision needed from Co-CEO + Dre:** which reach path for the 4-hour SLA? Default =
indirect via Dre relay (current setup). Faster paths available if explicitly approved.

## SLA window enforcement

- **Per spec §3b:** 1-hour SLA from generation to HITL surface, 4-hour SLA to resolution.
- **Enforcement:** `scripts/dop_sla_enforcer.py` runs every 30 min during active hours
  (06:00-23:00 CT) via cron `dop-sla-enforcer`. Auto-kills blocked records past 4-hour SLA.
- **Manual fallback:** documented in `~/.mavis/agents/mavis/crons/dop-sla-enforcer.md`.

## V6 status

| Sub-item | Status |
|---|---|
| Founder unblock authority clear | ✅ |
| Co-CEO unblock authority clear | ✅ (authority table documented above) |
| Founder reach pathway operational | ✅ (Obsidian + Telegram when bound) |
| Co-CEO reach pathway operational | ⚠️ INDIRECT (Dre relay, within SLA but slower than ideal) |
| SLA window enforcement live | ✅ (4-hour auto-kill via `dop_sla_enforcer.py`) |
| Manual fallback documented | ✅ |

**V6 PARTIAL** — Founder path is operational, Co-CEO path is indirect via Dre relay.
Full V6 confirmed requires either (a) Dre-relay step validated end-to-end, or (b) direct
Mavis → Co-CEO channel wired.

*Last updated: 2026-06-25 — V6 PARTIAL.*