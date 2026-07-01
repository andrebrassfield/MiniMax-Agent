# FB-Engine AM cron HALT — 2026-06-27 13:30 CT

**Cron:** `fb-read-scribe-am` (Phase 3, daily 13:30 CT)
**Group target:** https://www.facebook.com/groups/1318639637150450/
**Result:** HALT at Step 3 (fb-group-reader). 0 drafts. 0 fabrication. Telegram HALT sent (msg_id 95).

## TL;DR

Identical to 2026-06-23 20:00 CT PM failure (Mode B — Chrome at /tmp/chrome-fb-engine port 58632 has
no Facebook session). Reader navigated to the group, captured 8 GraphQL responses, but every body
is auth-bootstrap or `Unauthorized logged out query` (code 1675002). Group is also effectively
empty: 1 member, 1 admin pin post, no public posts to scrape even if auth were restored.

Scribe NOT invoked (zero-output guard — running on empty reader output would pollute the log
with a "succeeded with 0" pattern that hides the real failure, per 2026-06-23 lesson).

## Timeline

1. ✅ Loaded Telegram env: `~/.mavis/secrets/fb-telegram.env`
   (`FB_TELEGRAM_BOT_TOKEN=8178596605:AAHk…`, `FB_TELEGRAM_CHAT_ID=6598264778`)
2. ✅ Read group URL: line 1 of `03 Projects/FB-Engine/lists/groups.txt` → `1318639637150450`
3. ❌ fb-group-reader (first attempt, default params) → `captured=1 posts=0 errors=0`
4. ❌ fb-group-reader (second attempt, aggressive params: `--scroll-passes 4 --scroll-wait 6.0
   --page-timeout-ms 60000`) → `captured=8 posts=0 errors=0`
5. ✅ Diagnostic via direct CDP dump (`/tmp/debug_fb_capture.py`)
   - Page title: `Dose of Proof | Facebook` (group loaded, not login wall)
   - Body innerText contains `Log In` / `Forgot Account?` form, `Email or phone number`,
     `Password` field, QR-code device-confirm prompt
   - Group shows `1 member`, `Join group` button — current user is not a member
6. ⏭️ fb-draft-scribe → NOT invoked (would produce 0 drafts; see "What I did NOT do")
7. ✅ Telegram HALT sent to Andre (msg_id 95)

## Why 0 posts is the right answer

The reader captures `/api/graphql/` responses via `page.on("response")` interception. On this
profile, every GraphQL response is one of:

| Size  | Shape                                                              |
|-------|--------------------------------------------------------------------|
| ~215B | `{"data":{"xfb_two_step_verification_complete_if_approval_state_allowed":{"state":"PENDING"}}}` — auth polling ping |
| ~125B | `{"errors":[{"message":"Unauthorized logged out query.","severity":"CRITICAL","code":1675002}]}` — rejected feed query |

Neither contains post records with both `post_id` AND `text` (the parser requirement in
`walk_for_posts()`), so the post list stays empty. No parser change would recover posts from
bodies that don't carry them.

## Why this isn't a CDP / browser bug

- CDP `127.0.0.1:58632` is up (Chrome 149.0.7827.197, `/json/version` returns clean)
- Playwright connects cleanly
- Navigation to the group succeeds; page DOM loads (`title`, body innerText are populated)
- The page IS the group, not a generic login redirect

The bug is upstream of the reader: the managed Chrome profile at `/tmp/chrome-fb-engine` has
no FB cookies, so every auth-gated GraphQL query rejects. The 2026-06-23 PM cron hit the same
condition; today it persisted.

## What I did NOT do

- Did NOT run the Scribe on the empty reader output. Would produce 0 drafts, mask the real
  failure, and waste tokens.
- Did NOT fabricate posts to make the Scribe run. Zero-assumption rule (2026-06-16) still applies.
- Did NOT touch `read.py` or `scribe.py`. The parser is correct; the data is empty.
- Did NOT relaunch Chrome at `/tmp/chrome-fb-engine` with `--remote-debugging-port`. Would
  conflict with the existing managed session; FB-engine owns that user-data-dir (2026-06-18
  setup convention).
- Did NOT point the reader at a different CDP port. Would risk killing Andre's authed session
  in his real Chrome.

## Action items (Andre)

1. Open https://www.facebook.com/groups/1318639637150450/ in the Chrome profile at
   `/tmp/chrome-fb-engine` (port 58632), log in, accept any "save device" prompts.
   Cookies will persist for future cron fires.
2. *OR* repoint fb-engine at a different authed Chrome — update `--cdp-port` in both
   `fb-read-scribe-am` and `fb-read-scribe-pm` cron prompts.

Either fix unblocks the next PM fire (2026-06-27 20:00 CT).

## Follow-up (Mavis)

- Add `fb-session-guardian` pre-check between Steps 2 and 3 in both `fb-read-scribe-am` and
  `fb-read-scribe-pm` so Mode B failures surface at the right step with a clearer "not authed"
  signal. Carried forward from 2026-06-23; still pending spec approval.

## Files referenced

- `~/.mavis/agents/mavis/skills/fb-engine/fb-group-reader/scripts/read.py`
- `~/.mavis/agents/mavis/skills/fb-engine/fb-draft-scribe/scripts/scribe.py` (NOT invoked)
- `~/MiniMax-Agent/03 Projects/FB-Engine/lists/groups.txt`
- `~/MiniMax-Agent/03 Projects/FB-Engine/postmortems/2026-06-23-2000-cdp-fix-applied-no-auth.md` (precedent)
- `/tmp/fb-posts-am.json` (this run's empty reader output, retained for diff)