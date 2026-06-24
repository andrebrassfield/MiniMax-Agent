# FB-Engine cron AM failure — 2026-06-23 13:30 CT

**Cron:** `fb-read-scribe-am` (13:30 CT daily)
**Group target:** https://www.facebook.com/groups/1318639637150450/
**Result:** HALT at step 3 (fb-group-reader)

## Timeline

1. ✅ Loaded Telegram env: `~/.mavis/secrets/fb-telegram.env` (FB_TELEGRAM_BOT_TOKEN, FB_TELEGRAM_CHAT_ID)
2. ✅ Read group URL: line 1 of `03 Projects/FB-Engine/lists/groups.txt`
3. ❌ fb-group-reader → CDP connect failed
   - `ps -axww` showed 40+ Chrome helper/renderer processes but **zero** with `--remote-debugging-port` flag
   - `lsof -nP -iTCP -sTCP:LISTEN` for Chrome → empty
   - fb-session-guardian → FAIL with same error
4. ⏭️ fb-draft-scribe → NOT invoked (no reader output to draft from)
5. ✅ Telegram HALT notification sent to Andre (msg_id=84, chat 6598264778)

## Root cause

The user's real Chrome session is running but not in dev-mode. Two paths to CDP exist:

- **Direct flag:** Chrome launched with `--remote-debugging-port=N` — none currently running
- **Bridge path:** mavis browser bridge native host via the Chrome extension — `Browser Integration Status: Native host: not connected`

Both paths are dark. fb-group-reader needs a CDP endpoint to intercept Facebook's `/api/graphql/` responses.

## What I did NOT do

- Did not launch a fresh Chrome with `--remote-debugging-port` (would conflict with user's existing Chrome instance / risk killing FB session)
- Did not use playwright MCP as fallback (no FB cookies → login wall)
- Did not write empty/fake drafts to `03 Projects/FB-Engine/drafts/` (would corrupt the kanban queue)

## Follow-up

- Second consecutive AM cron failure with this root cause (verify in prior postmortems/)
- If pattern continues, propose an auto-recovery heuristic: detect the failure, attempt to spawn a managed Chrome via `mavis browser tool start`, retry once, then HALT
- Andre notified via Telegram; awaiting manual reload / extension reconnect

## Reproduce

```bash
ps -axww -o command | grep -- "--remote-debugging" | grep -v grep   # empty
lsof -nP -iTCP -sTCP:LISTEN | grep -i chrome                          # empty
mavis browser status                                                   # native host: not connected
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-session-guardian/scripts/guard.py   # FAIL
```