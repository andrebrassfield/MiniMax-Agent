# FB-Engine cron HALT — 2026-06-25 13:30 CT (AM)

**Cron:** `fb-read-scribe-am` (Phase 3, daily 13:30 CT)
**Group target:** https://www.facebook.com/groups/1318639637150450/
**Result:** HALT at Step 3 (fb-group-reader). 0 drafts. 0 fabrication. Telegram HALT sent (msg_id=91).

## TL;DR

The SAME Mode C failure from 06-24 PM (and the same substrate state — Chrome
149.0.7827.156 + Playwright 1.60.0) re-surfaced on this morning's AM cron.
This is the **3rd consecutive cron tick** to hit `Browser.setDownloadBehavior:
Browser context management is not supported`. No new state to report from a
diagnostic standpoint — this postmortem exists to keep the audit trail clean
and to surface the pattern that the substrate is now stable in this broken
state and will keep firing this HALT every tick until either the substrate
or the read path changes.

## Timeline

1. ✅ Loaded Telegram env: `~/.mavis/secrets/fb-telegram.env`
2. ✅ Read group URL: line 1 of `03 Projects/FB-Engine/lists/groups.txt` → `1318639637150450`
3. ❌ fb-group-reader → `connect_over_cdp` Protocol error
   - **Error:** `BrowserType.connect_over_cdp: Protocol error (Browser.setDownloadBehavior): Browser context management is not supported.`
   - **Captured:** 0 posts. **Errors:** 1. Output: `/tmp/fb-posts-am.json` (the 06-24 PM file, untouched — the script exited 1 before writing)
4. ⏭️ fb-draft-scribe → NOT invoked (per 06-24 discipline: would produce 0 drafts and mask the real failure)
5. ✅ Telegram HALT notification sent (msg_id=91)

## Substrate probe (per architecture-shift cron-audit rule)

| Component              | 06-23 PM state         | 06-24 PM state         | 06-25 AM state         | Delta vs 06-24              |
|------------------------|------------------------|------------------------|------------------------|------------------------------|
| Chrome binary          | 149.0.7827.x           | 149.0.7827.156         | 149.0.7827.156         | unchanged                    |
| Chrome --remote-debug  | running :58632         | running :58632         | running :58632         | unchanged                    |
| Chrome user-data-dir   | /tmp/chrome-fb-engine  | /tmp/chrome-fb-engine  | /tmp/chrome-fb-engine  | unchanged                    |
| Chrome FB session      | logged out (PENDING)   | logged out (PENDING)   | logged out (PENDING)   | unchanged                    |
| Playwright Python      | 1.60.0                 | 1.60.0                 | 1.60.0                 | unchanged                    |
| read.py CDP URL scheme | http:// (06-23 fix)    | http:// (still in)     | http:// (still in)     | unchanged                    |
| read.py `connect_over_cdp` call | unconditional     | unconditional          | unconditional          | unchanged — still broken     |
| Telegram bot token     | healthy                | healthy                | healthy                | unchanged                    |

**Verdict: zero substrate drift since 06-24 PM.** The Mode C failure is fully
deterministic now — same error, same line, same exit code.

## Pattern observation

This is the first time the FB-Engine cron has hit the **same substrate failure
across 3 consecutive fires** without any intervening fix. The 06-16 reply-sweep
postmortem identified "HALT-then-skip ≠ HALT-then-delete" — a cron that
HALTs but stays scheduled burns tokens + Telegram noise forever. We are now
in that regime on the fb-read-scribe-{am,pm} pair.

Options previously enumerated (06-24 postmortem §Follow-up):

- (A) Pin Chrome to a version that supports `Browser.setDownloadBehavior`
- (B) Update Playwright Python to 1.61+ (verify release first)
- (C) Migrate FB-Engine to the mavis browser bridge path
- (D) Add a wrapper around `connect_over_cdp` that suppresses the
  setDownloadBehavior call

None of A/B/C/D have been approved. The cron pair will continue to fire 2x
daily and HALT 2x daily until one of:
1. Andre picks a fix option
2. Mavis gets authority to pick one (not granted yet)
3. The cron pair is deleted (also needs Andre's go per the reply-sweep rule)

## What I did NOT do

- Did NOT silently patch read.py to skip `Browser.setDownloadBehavior`.
- Did NOT run the Scribe on empty reader output.
- Did NOT fabricate posts to make the Scribe run.
- Did NOT install / downgrade Playwright or Chrome.
- Did NOT relaunch Chrome.
- Did NOT delete the cron.

## Follow-up (escalated from 06-24)

The 06-24 follow-up section enumerates A/B/C/D. Today's addition: **option (E)
delete the cron pair and put FB-Engine in cold storage until the substrate
question is resolved.** Per the reply-sweep-daily precedent (deprecation
2026-06-24, see `03 Projects/X-Content-Engine/postmortems/2026-06-24-reply-sweep-deprecation.md`),
HALT-then-delete is the right move when no near-term fix exists. But I do
not have unilateral authority to delete FB-Engine crons — this needs Andre.

**Asking for a decision:** pick one of A/B/C/D/E so the daily 2x Telegram
HALT noise stops. If E (delete), the Scribe ammunition.mdl and skill files
stay on disk for revival.

## Reproduce

Same as 06-24 postmortem; error reproduced identically on first try.

```bash
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-group-reader/scripts/read.py \
  --group https://www.facebook.com/groups/1318639637150450/ \
  --output /tmp/fb-posts-am.json
# captured=0 posts=0 errors=1
# Error: BrowserType.connect_over_cdp: Protocol error (Browser.setDownloadBehavior): Browser context management is not supported.
```

## Log

- 2026-06-23 PM: HALT (cdp-bridge-offline, msg_id=84) — chrome CDP endpoint reachable but auth missing
- 2026-06-24 PM: HALT (cdp-setdownloadbehavior, msg_id=87) — Mode C protocol break identified
- **2026-06-25 AM: HALT (cdp-setdownloadbehavior AM, msg_id=91) — 3rd consecutive, no new info**