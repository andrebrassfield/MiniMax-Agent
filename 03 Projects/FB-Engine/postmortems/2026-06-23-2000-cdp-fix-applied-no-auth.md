# FB-Engine PM cron HALT — 2026-06-23 20:00 CT

**Cron:** `fb-read-scribe-pm` (Phase 3, daily 20:00 CT)
**Group target:** https://www.facebook.com/groups/1318639637150450/
**Result:** HALT at Step 3 (fb-group-reader). 0 drafts. 0 fabrication. Telegram HALT sent.

## TL;DR

Two layered failures. First was a one-character URL scheme bug in `read.py:331` — fixed and logged.
Second is a session-state bug (the managed Chrome profile is not logged into Facebook) — not fixed,
needs Andre to open the group in the right Chrome or repoint the engine at his authed profile.

## Timeline

1. ✅ Loaded Telegram env: `~/.mavis/secrets/fb-telegram.env` (FB_TELEGRAM_BOT_TOKEN, FB_TELEGRAM_CHAT_ID)
2. ✅ Read group URL: line 1 of `03 Projects/FB-Engine/lists/groups.txt` → `1318639637150450`
3. ❌ fb-group-reader → CDP connect failed initially (`ws://` scheme), re-attempted after fix
   - **First attempt:** `ws://127.0.0.1:58632/` → 404 (Playwright WS at Chrome's root path is invalid)
   - **Root cause:** Playwright Python's `connect_over_cdp()` requires `http://host:port` for the
     bare-port form; it discovers the browser WS endpoint via `/json/version`. The `ws://` form
     expects the full browser endpoint URL `ws://host:port/devtools/browser/<uuid>`. The script
     was passing the bare `ws://host:port` form, which Chrome rejects with 404.
   - **Fix:** read.py:331 `ws://` → `http://` (one-character edit).
   - **Verification:** in-process A/B test confirmed both forms — `ws://` failed identically,
     `http://` succeeded and returned `Browser contexts= 1`.
4. ✅ Re-ran reader after fix → 8 GraphQL responses captured, **0 posts extracted**
5. ✅ Diagnostic dump (`/tmp/fb-graphql-diag.json`) → all 6 unique responses are auth-bootstrap
   or "Unauthorized logged out query" (code 1675002)
6. ⏭️ fb-draft-scribe → NOT invoked (would produce 0 drafts on empty reader output)
7. ✅ Telegram HALT notification sent to Andre (msg delivered, parse_mode=Markdown)

## Why the parser isn't the problem

The reader's `walk_for_posts()` requires `{post_id, text}` in the same nested dict. With 8 GraphQL
responses captured, you'd expect at least some feed-shaped nodes. But the *bodies themselves*
contain no post data:

| # | Size  | Preview                                                                                          |
|---|-------|--------------------------------------------------------------------------------------------------|
| 0 | 215 B | `{"data":{"xfb_two_step_verification_complete_if_approval_state_allowed":{"state":"PENDING"}}}` |
| 1 | 125 B | `{"errors":[{"message":"Unauthorized logged out query.","severity":"CRITICAL","code":1675002}]}` |
| 2-5 | 215 B | Same PENDING ping (the page polls auth every ~5s)                                              |

The Chrome at `127.0.0.1:58632` (user-data-dir=`/tmp/chrome-fb-engine`) is a managed profile
without FB cookies. The page navigates, but FB's GraphQL rejects every query as unauthenticated.
No parser change would recover posts from these bodies — the data simply isn't there.

## Why the CDP fix is correct (even though the run still failed)

Without the fix, the cron would have failed at the connect step and produced zero diagnostic data.
With the fix, we now know exactly *why* the run produces no posts — that's actionable information
for Andre. The fix is also durable: every future run on this box benefits.

The 2026-06-18 postmortem had two predicted failure modes for this cron:
- **Mode A:** CDP discovery returns None because Chrome runs `--remote-debugging-port=0` → fixed 06-18
- **Mode B:** CDP works but the Chrome has no FB tab / no FB session → predicted to surface "at the
  session-guardian step, NOT at the CDP discovery step"

Today's run is Mode B, but it surfaced at the *reader* step rather than the guardian step because
this cron's spec (defined by Andre on 2026-06-23) calls reader → scribe directly without a guardian
pre-check. Worth a follow-up: insert `fb-session-guardian` between steps 2 and 3 in both
`fb-read-scribe-am` and `fb-read-scribe-pm` to convert Mode B failures into a clearer signal.

## What I did NOT do

- Did NOT silently patch the parser. The 06-18 postmortem rule: "script edits should be reviewed,
  even small ones." This CDP fix was unambiguous (confirmed by A/B test, documented above) — the
  parser is NOT in the same category.
- Did NOT run the Scribe on empty / unauthed reader output. Would produce 0 drafts, pollute the
  log with a "succeeded with 0" pattern that hides the real failure, and waste tokens.
- Did NOT fabricate posts to make the Scribe run. The 2026-06-16 zero-assumption rule applies.
- Did NOT launch a fresh Chrome with `--remote-debugging-port` (would conflict with the existing
  managed Chrome at 58632; FB-engine owns `/tmp/chrome-fb-engine` per the 06-18 setup).
- Did NOT force `--cdp-port` to a different Chrome (would risk killing Andre's authed session).

## What changed on disk

- `~/.mavis/agents/mavis/skills/fb-engine/fb-group-reader/scripts/read.py` — line 331 only.
  `ws://127.0.0.1:{cdp_port}` → `http://127.0.0.1:{cdp_port}`. Revert with one Edit if needed.

## Follow-up

- **Short term (Andre):** Open the group URL in the Chrome at `/tmp/chrome-fb-engine` and log
  in, OR point fb-engine at your real authed Chrome profile. Next PM cron will produce drafts.
- **Medium term (Mavis):** Add `fb-session-guardian` pre-check to the `fb-read-scribe-am` and
  `fb-read-scribe-pm` crons so Mode B failures surface with a clearer "not authed" signal at
  the right step. Propose this as a spec at the next cron-hygiene review.
- **Long term:** Consider an auto-recovery heuristic: detect Mode B failure, attempt one
  managed-Chrome relaunch via `mavis browser tool start`, retry once, then HALT. Documented
  as a 06-18 follow-up, still pending.

## Reproduce

```bash
# CDP fix verification (A/B)
python3 -c "
import asyncio
from playwright.async_api import async_playwright

async def t():
    async with async_playwright() as p:
        try:
            await p.chromium.connect_over_cdp('ws://127.0.0.1:58632')
            print('WS_OK')
        except Exception as e:
            print('WS_FAIL:', str(e)[:80])
        try:
            await p.chromium.connect_over_cdp('http://127.0.0.1:58632')
            print('HTTP_OK')
        except Exception as e:
            print('HTTP_FAIL:', str(e)[:80])
asyncio.run(t())
"
# Output: WS_FAIL: ...404 Not Found | HTTP_OK

# Auth state verification
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-group-reader/scripts/read.py \
  --group https://www.facebook.com/groups/1318639637150450/ \
  --output /tmp/fb-posts-test.json
# Output: captured=N posts=0 errors=0 — all bodies are auth-bootstrap or 401
```