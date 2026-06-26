# FB-Engine cron HALT — 2026-06-26 13:30 CT (AM)

**Cron:** `fb-read-scribe-am` (Phase 3, daily 13:30 CT)
**Group target:** https://www.facebook.com/groups/1318639637150450/
**Result:** HALT at Step 3 (fb-group-reader). 0 drafts. 0 fabrication. Telegram escalation sent (msg_id pending).
**Predecessor:** [`2026-06-25-2000-cdp-setdownloadbehavior-pm.md`](./2026-06-25-2000-cdp-setdownloadbehavior-pm.md) (this AM session was the documented AM 06-26 trigger)

## TL;DR

**5th consecutive** Mode C failure. Substrate state is functionally identical to the
06-25 PM run (Chrome 149.0.7827.197 vs 06-25's .156 — minor auto-bump, same major
`Browser.setDownloadBehavior` break). Andre has not responded to msg_id=91 (Telegram
getUpdates shows zero messages from chat_id 6598264778 in the recent update window).

The 06-25 PM postmortem set up an **AM 06-26 trigger** that, if conditions were met,
would auto-execute option E (delete the cron pair + cold-storage assets). I am
**NOT executing that destructive path unilaterally**. The 06-25 PM escalation plan
was a thoughtful pre-commitment, but the destructive ops it specifies (cron
deletion, asset relocation) require Andre's explicit go. This session executes
the conservative interpretation:

- ✅ HALT (no fabrication, no Scribe on empty input)
- ✅ Postmortem (this file — 5th consecutive, audit trail clean)
- ✅ Halt-state file (durable signal for future crons / sessions)
- ✅ ONE Telegram escalation to Andre with the explicit A/B/C/D/E choice
- ❌ Did NOT delete the cron pair (destructive op + schedule change — needs explicit go)
- ❌ Did NOT move assets to cold-storage (destructive op — needs explicit go)
- ❌ Did NOT silently patch read.py to suppress `setDownloadBehavior`

## Timeline

1. ✅ Loaded Telegram env: `~/.mavis/secrets/fb-telegram.env`
2. ✅ Read group URL: line 1 of `03 Projects/FB-Engine/lists/groups.txt` → `1318639637150450`
3. ❌ fb-group-reader → `connect_over_cdp` Protocol error (3+ min hang, killed by bash timeout)
   - **Error:** `BrowserType.connect_over_cdp: Protocol error (Browser.setDownloadBehavior): Browser context management is not supported.`
   - **Captured:** 0 posts. **Errors:** 1.
   - **Output:** `/tmp/fb-posts-am.json` UNTOUCHED (still the 06-24 PM file — script exits 1 before write)
   - **Minimal repro also hung:** bare `connect_over_cdp('http://127.0.0.1:58632')` timed out at 30s with the same error
4. ⏭️ fb-draft-scribe → NOT invoked (would produce 0 drafts on empty reader output; would mask real failure)
5. ✅ Telegram escalation sent (msg_id pending; pre-decision ping to Andre)

## Substrate probe (per architecture-shift cron-audit rule)

| Component              | 06-25 AM (yesterday) | 06-25 PM            | 06-26 AM (today)    | Delta vs 06-25 PM         |
|------------------------|----------------------|---------------------|---------------------|----------------------------|
| Chrome binary          | 149.0.7827.156       | 149.0.7827.156      | **149.0.7827.197**  | minor auto-bump (.156→.197) |
| Chrome --remote-debug  | running :58632       | running :58632      | running :58632      | unchanged                  |
| Chrome user-data-dir   | /tmp/chrome-fb-engine| /tmp/chrome-fb-engine| /tmp/chrome-fb-engine| unchanged                |
| Chrome FB session      | logged out (PENDING) | logged out (PENDING)| logged out (PENDING)| unchanged                  |
| Active tabs/contexts   | 57 (Andre idle)      | 57 (Andre idle)     | **66 (Andre browsing)**| Andre active in Chrome    |
| Playwright Python      | 1.60.0               | 1.60.0              | 1.60.0              | unchanged                  |
| read.py CDP URL scheme | http:// (06-23 fix)  | http:// (still in)  | http:// (still in)  | unchanged                  |
| read.py `connect_over_cdp` call | unconditional| unconditional       | unconditional       | unchanged — still broken   |
| Telegram bot token     | healthy              | healthy             | healthy             | unchanged                  |

**Verdict: zero substrate drift that matters.** Chrome auto-bumped from .156 to .197
within the 149.x line, but the `Browser.setDownloadBehavior` rejection is a
**major-version** behavior change (per 06-24 postmortem §Root cause). The minor
bump does not affect the failure mode. Andre has 66 active tabs (vs 57 yesterday)
— the more-tabs-attached problem gets worse with active use, not better.

## Andre-response check

| Channel | Status |
|---|---|
| Telegram (msg_id=91 from 06-25 AM) | **No reply.** `getUpdates?limit=20` returned 2 updates — both from chat_id 5946161407 (user 'Marjona'), zero from chat_id 6598264778 (Andre). |
| Any subsequent channel | None surfaced in this session. |

Per the 06-25 PM escalation plan §Step 2: "Verify Andre has not responded to
msg_id=91 (or any subsequent channel)." **Verified.** Andre has not responded.

## Why I am NOT auto-executing option E

The 06-25 PM postmortem §Escalation specified:

> **AM 06-26 trigger:** if the next AM run also fails identically (5th consecutive),
> this session will:
> 1. Read this file + the AM file as the durable record
> 2. Verify Andre has not responded to msg_id=91 (or any subsequent channel)
> 3. **Delete the cron pair** (`fb-read-scribe-am`, `fb-read-scribe-pm`)
> 4. Move `ammunition.mdl` and skill files to a `cold-storage/` subdirectory
> 5. Send ONE final Telegram: "FB-Engine cron pair deleted..."

Steps 1, 2, and 5 are observational / reversible. Steps 3 and 4 are
**destructive ops + schedule changes**. Per Mavis hard constraints:

> In-session approval required for: deploys, pushes, external sends, credential
> changes, destructive ops, schedule changes.

The 06-25 PM session was **authorizing itself** to delete the crons if conditions
were met. That self-authorization does not clear the destructive-ops constraint —
the constraint exists at the cross-session / agency level, not at the
single-session level. A prior Mavis session setting a trigger does not constitute
"in-session approval from Andre."

**Conservative interpretation:** execute steps 1, 2, and 5 (and add steps I did
add: halt-state file + this postmortem), defer steps 3-4 to an explicit Andre
directive.

This is consistent with the cron-discipline rule #3 ("HALT-then-skip ≠
HALT-then-delete") — that rule applies the deletion move specifically when
"no near-term fix exists." The substrate IS fixable (options A/B/C/D are all
available); what's missing is **Andre's choice between them**, which is
different from "no near-term fix."

If Andre replies with "do E" — the cron pair can be deleted in the next
session (or this one, if I'm still around). If Andre replies with "do A/B/C/D"
— the cron pair needs to stay so the fix can be tested.

## What I did NOT do

- Did NOT silently patch read.py to skip `Browser.setDownloadBehavior`.
- Did NOT run the Scribe on empty / unauthed reader output.
- Did NOT fabricate posts to make the Scribe run.
- Did NOT install / downgrade Playwright or Chrome.
- Did NOT relaunch Chrome with a different --remote-debugging-port.
- Did NOT delete the cron pair (deferred to Andre's go — see §Why I am NOT auto-executing).
- Did NOT move assets to cold-storage (deferred to Andre's go).

## Follow-up — explicit decision request to Andre

Pick one of A/B/C/D/E so the daily 2x Telegram halt noise stops:

| Option | What it requires | Risk |
|---|---|---|
| **A** Pin Chrome to a pre-149 version that supports `setDownloadBehavior` | Research target version, managed-Chrome relaunch spec, FB session re-auth | May break other Chrome consumers (Hermes, Gemini, GHL) |
| **B** Update Playwright Python to 1.61+ | `pip index versions playwright` to verify release exists, then `pip install --upgrade playwright` | Risk: same fix may need different upstream version |
| **C** Migrate FB-Engine to mavis browser bridge path | Native host reconnect (was down per 06-24 audit), bridge path substitution in read.py + scribe.py + guardian.py | Larger refactor; native host status unknown now |
| **D** Add wrapper around `connect_over_cdp` to suppress `setDownloadBehavior` | Catches the error and retries without the command | Workable but Playwright internals make it fragile |
| **E** Delete the cron pair, cold-storage assets | `mavis cron delete mavis fb-read-scribe-am` + `mavis cron delete mavis fb-read-scribe-pm` + move `ammunition.mdl` + skills to `cold-storage/` | Irreversible from cron side; revival requires explicit re-enable |

If no answer by the next cron fire (PM 06-26 20:00 CT — 6th consecutive), I will
**send the same Telegram ping again with a "final ask" prefix** rather than
auto-deleting. The destructive ops still need explicit go.

## Log

- 2026-06-23 PM: HALT (cdp-bridge-offline, msg_id=84)
- 2026-06-24 PM: HALT (cdp-setdownloadbehavior, msg_id=87)
- 2026-06-25 AM: HALT (cdp-setdownloadbehavior AM, msg_id=91) — asked for decision
- 2026-06-25 PM: HALT (no Telegram, set AM-06-26 trigger)
- **2026-06-26 AM: HALT (this file) — 5th consecutive, conservative interpretation, escalation Telegram sent**
