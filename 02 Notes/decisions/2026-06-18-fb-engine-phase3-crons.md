# FB-Engine Phase 3 — Cron + Telegram Bridge Decision

**Date:** 2026-06-18 15:45 CT
**Session:** mvs_26cff8b71d7b44c49405b9a0a8407e64
**Decision:** Ship Phase 3 — twice-daily read/draft/propose/capture cycle

## Decision

Deploy the FB-Engine Phase 3 cron cycle with Telegram approval bridge:
- 5 crons: `fb-read-scribe-am`, `fb-propose-am`, `fb-read-scribe-pm`, `fb-propose-pm`, `fb-capture`
- Schedule: 08:30/09:00/14:00/14:30/20:00 CT
- Telegram delivery enabled on all 5 crons (chat ID: 6598264778)
- Target group: `https://www.facebook.com/groups/1318639637150450/` (Dose of Proof)

## Rationale

Facebook Group engagement is asynchronous and community-driven — no velocity-based feed
algorithm like X. Twice-daily gives a comfortable buffer to batch-approve via Telegram
before evening traffic spikes.

## Alternatives Considered

1. **X-Engine-style (post-N crons, high frequency):** Rejected — X's velocity
   algorithm rewards fast engagement; FB's community model rewards thoughtful, less-
   frequent presence. 2x/day is the right cadence.
2. **Single daily cycle:** Rejected — misses afternoon window when group members
   are active post-lunch.
3. **Autonomous deployment (no Telegram gate):** Rejected — Hard Rule #10 applies
   to all content engines. No bot-deployment without human approval.

## Key Technical Notes

- Bridge uses `urllib.request` (stdlib) — no `requests` dependency
- CDP port auto-detected via `find_cdp_port()` in read.py (scans `ps -axww` for
  `--remote-debugging-port=N`)
- **CDP port requirement:** Andre's real Chrome must be running with
  `--remote-debugging-port=58632`. The Playwright MCP browser (port 57931)
  does NOT have Andre's Facebook session.
- Bot token: stored in `~/.mavis/secrets/fb-telegram.env` mode 600
- Chat ID: 6598264778 (Andre)

## Artifacts

- Skills: `~/.mavis/agents/mavis/skills/fb-engine/`
- Vault mirror: `~/MiniMax-Agent/99 _system/skills/fb-engine/`
- Pipeline runbook: `03 Projects/FB-Engine/PIPELINE.md`
- Ammunition ledger: `03 Projects/FB-Engine/ammunition.mdl` (18 entries, 3 pillars)

## What Would Change My Mind

- If FB introduces a velocity-based feed similar to X — switch to higher-frequency
  cadence with X-Engine pattern
- If Telegram approval creates friction that causes drafts to pile up — shift to
  async capture with longer reply window
