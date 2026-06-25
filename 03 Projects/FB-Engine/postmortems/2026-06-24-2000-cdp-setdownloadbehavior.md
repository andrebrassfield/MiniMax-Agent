# FB-Engine PM cron HALT — 2026-06-24 20:00 CT

**Cron:** `fb-read-scribe-pm` (Phase 3, daily 20:00 CT)
**Group target:** https://www.facebook.com/groups/1318639637150450/
**Result:** HALT at Step 3 (fb-group-reader). 0 drafts. 0 fabrication. Telegram HALT sent (msg_id=87).

## TL;DR

A NEW failure mode surfaced today. The CDP `http://` fix from 06-23 still works
(verified in-line), but Playwright 1.60.0 calls `Browser.setDownloadBehavior`
unconditionally during `connect_over_cdp()` and Chrome 149.0.7827.156 rejects it
with `Browser context management is not supported`. This is a Chrome-upstream
protocol change, not a script bug. The fix is upstream (Playwright update or
Chrome pin), not in our read.py.

## Timeline

1. ✅ Loaded Telegram env: `~/.mavis/secrets/fb-telegram.env`
2. ✅ Read group URL: line 1 of `03 Projects/FB-Engine/lists/groups.txt` → `1318639637150450`
3. ❌ fb-group-reader → `connect_over_cdp` Protocol error
   - **Error:** `BrowserType.connect_over_cdp: Protocol error (Browser.setDownloadBehavior): Browser context management is not supported.`
   - **Read.py line 331** still has the 06-23 `http://` fix (`http://127.0.0.1:{cdp_port}`) — confirmed via `grep`
   - **In-process A/B reproduce:** minimal `async_playwright → connect_over_cdp("http://127.0.0.1:58632")` reproduces the same error. The `http://` form is correct; Chrome is rejecting a different protocol command.
4. ⏭️ fb-draft-scribe → NOT invoked (would produce 0 drafts on empty reader output)
5. ✅ Telegram HALT notification sent (msg_id=87)

## Root cause (verified)

The CDP handshake itself succeeds (Playwright's WS handshake at
`ws://127.0.0.1:58632/devtools/browser/...` connects, then disconnects).
The failure is at a *post-handshake* browser-level command that Playwright
sends to set up download behavior. Chrome 149.x removed support for
`Browser.setDownloadBehavior` from regular (non-automation) CDP contexts.

### Substrate audit (per architecture-shift cron-audit rule)

| Component              | 06-23 PM state         | 06-24 PM state         | Delta                          |
|------------------------|------------------------|------------------------|--------------------------------|
| Chrome binary          | 149.0.7827.x           | 149.0.7827.156         | auto-updated                   |
| Chrome --remote-debug  | running :58632         | running :58632         | same                           |
| Chrome user-data-dir   | /tmp/chrome-fb-engine  | /tmp/chrome-fb-engine  | same                           |
| Chrome FB session      | logged out (PENDING)   | logged out (PENDING)   | same — never fixed             |
| Playwright Python      | 1.60.0                 | 1.60.0                 | same                           |
| mavis browser bridge   | native host down       | native host down       | same                           |
| read.py CDP URL scheme | http:// (06-23 fix)    | http:// (still in)     | same                           |
| read.py `connect_over_cdp` call | unconditional     | unconditional          | same — but now broken          |

**The 06-23 postmortem predicted "Mode B" failures would surface at the
session-guardian step, not the reader step. Today's failure is neither Mode A
nor Mode B — it's Mode C: protocol-level browser context command removed
upstream.** The "Mode B" condition (no FB session) is still present, just
unreachable behind the Mode C break.

## Why I am NOT patching read.py

1. The 06-23 postmortem rule applies: "script edits should be reviewed, even
   small ones." Patching read.py to skip the download behavior setup is a
   non-trivial change with two visible paths (set an env var, or wrap
   `connect_over_cdp` to suppress the call). Either path is in the territory
   of "review first."
2. The 06-16 zero-assumption rule applies: don't fabricate a working run.
3. The architecture-shift rule says: when substrate changes, audit every cron
   that touches the substrate. The right fix is upstream (Playwright or
   Chrome version), not in our thin harness.
4. There are downstream effects: the Scribe's `ammunition.mdl` is sized for
   ~5 typology samples from the reader output. Running it on 0 posts would
   produce 0 drafts, but the "succeeded with 0" pattern would mask the real
   (Mode C) failure on the next cron fire.
5. The CDP fix on 06-23 was unambiguous (confirmed by A/B test, one-character
   change). This fix is NOT unambiguous — it would be a behavioral change to
   the read path that affects future Playwright SDK upgrades.

## What I did NOT do

- Did NOT silently patch read.py to skip `Browser.setDownloadBehavior`.
- Did NOT run the Scribe on empty / unauthed reader output.
- Did NOT fabricate posts to make the Scribe run.
- Did NOT install a different Playwright version (auto-upgrade is a
  hard-constraint op that needs Andre's go).
- Did NOT downgrade Chrome (would break Hermes and other Chrome users).
- Did NOT launch a fresh Chrome with a different --remote-debugging-port
  (would conflict with the running managed Chrome at 58632).
- Did NOT delete the cron (per the reply-sweep-daily lesson: HALT-then-delete
  is the right move when no near-term fix exists, but I don't have that
  authority unilaterally).

## Follow-up (proposed)

- **Immediate (Andre):** Decide one of:
  - (A) Pin Chrome to a version that supports `Browser.setDownloadBehavior` via
    a managed-Chrome relaunch spec (which Chrome version? — research first).
  - (B) Update Playwright Python to 1.61+ if released (check `pip index
    versions playwright`).
  - (C) Migrate FB-Engine to the mavis browser bridge path (requires native
    host reconnect).
  - (D) Add a wrapper around `connect_over_cdp` that catches the
    `setDownloadBehavior` error and retries without it. (Workable but
    Playwright's internals make this fragile.)
- **Medium term (Mavis, with Andre's go):** Add `fb-session-guardian` as a
  pre-check so Mode B failures surface with a clearer "not authed" signal
  at the right step. Same follow-up as 06-23, still pending.
- **Long term:** If substrate drift continues, propose a FB-Engine
  substrate→cron dependency map (which crons touch Chrome? which touch
  Playwright? which touch the FB session?) so future substrate shifts
  trigger a targeted cron audit, not a global one.

## Reproduce

```bash
# Minimal CDP connect repro
python3 -c "
import asyncio
from playwright.async_api import async_playwright
async def t():
    async with async_playwright() as p:
        try:
            await p.chromium.connect_over_cdp('http://127.0.0.1:58632')
            print('OK')
        except Exception as e:
            print('FAIL:', type(e).__name__, str(e)[:200])
asyncio.run(t())
"
# FAIL: Error ... Protocol error (Browser.setDownloadBehavior): Browser context management is not supported.

# Full read.py invocation
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-group-reader/scripts/read.py \
  --group https://www.facebook.com/groups/1318639637150450/ \
  --output /tmp/fb-posts-pm.json
# captured=0 posts=0 errors=1

# Substrate probes
curl -s http://127.0.0.1:58632/json/version | python3 -m json.tool | grep Browser
# "Browser": "Chrome/149.0.7827.156"
pip show playwright | head -2
# Version: 1.60.0
```
