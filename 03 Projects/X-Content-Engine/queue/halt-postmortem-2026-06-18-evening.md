# reply-sweep-evening-2026-06-18 — HALT POST-MORTEM

**Time:** 2026-06-18 19:00 CT (scheduled fire)
**Sweep ID:** reply-sweep-evening-2026-06-18 (one-shot)
**Outcome:** HALT at Step 0 (x-session-guardian)
**Sweep shipped:** 0 replies
**Replies already published today:** 3 (10:56, 10:57 CT from v1 batch + 17:01 CT approved draft publish)
**Cap:** 10 replies/day

## Failing step

**Step 0: x-session-guardian (HARD GATE)**

```
$ python3 ~/.mavis/agents/mavis/skills/x-session-guardian/scripts/guard.py --output /tmp/session-check.json
{
  "session_state": "FAIL",
  "cdp_port": null,           ← root cause #1
  "cookies_present": {"twid": false, "auth_token": false, "ct0": false},
  "title_check": "UNKNOWN",
  "diagnostic": "could not find MCP Chrome CDP port — is the browser bridge connected?"
}
```

After manually passing `--cdp-port 60438` (read from `DevToolsActivePort`):
```
{
  "session_state": "FAIL",
  "cdp_port": 60438,
  "cookies_present": {"twid": false, "auth_token": false, "ct0": false},
  "title_check": "OK",
  "current_url": "https://x.com/",
  "page_title": "X. It's what's happening / X",
  "diagnostic": "session expired — missing cookies: ['twid', 'auth_token', 'ct0']"
}
```

## Root cause: architectural mismatch (the load-bearing bug)

The cron was designed before the mavis browser bridge was wired up. The pipeline expects:
- **Playwright MCP** → launches a dedicated Chrome with `--remote-debugging-port=N` (explicit)
- The x-session-guardian scans `ps -axww` for `--remote-debugging-port=N`
- It then checks that Chrome's context for `twid` + `auth_token` cookies

The actual runtime architecture (2026-06-17 wiring):
- **mavis browser bridge** → the user's real Chrome (with X session) + a native messaging host + a mavis-side broker
- The agent-browser Chrome (a separate headless Chrome in `/var/folders/.../agent-browser-chrome-...`) launches with `--remote-debugging-port=0` (dynamic)
- The CDP port is written to `DevToolsActivePort` file, NOT to the command line
- The agent-browser Chrome's default context has NO x.com cookies (the X session is in the user's real Chrome, which the mavis bridge talks to via the extension)

So:
- The Playwright Chrome (agent-browser) has no X session
- The user's real Chrome (mavis bridge) HAS the X session (active tab on `https://x.com/i/account_analytics/...` — only reachable when logged in)
- The guardian only checks the Playwright Chrome → FAILs every time

## Verification: session is alive

```
$ mavis browser tool get_active_tab
{
  "tabId": 1230105652,
  "url": "https://x.com/i/account_analytics/content?type=posts&sort=date&dir=desc&days=30",
  "title": "(21) X"
}
```

`/i/account_analytics/...` is only reachable to a logged-in user. Session is ALIVE in the mavis browser bridge, just not in the Playwright Chrome the guardian inspects.

## Why I didn't bypass the HALT

Per the cron prompt:
> "Session guardian MUST pass before any X.com action. No bypassing the guard."

This is a load-bearing safety gate designed for an architecture we no longer have. The HALT is correct per protocol. The bug is the protocol's assumption, not the gate's logic.

## Cleanup actions taken

1. ✅ Queue state snapshot saved: `/tmp/queue-snapshot-20260618-1903.json`
2. ✅ One-shot cron deleted: `mavis cron delete mavis reply-sweep-evening-2026-06-18` → success
3. ❌ Recurring cron `reply-sweep-daily` NOT touched (schedule change = hard constraint violation). It will HALT again tomorrow 19:00 CT and Telegram Andre. This needs Andre's call.

## Remediation options (for Andre to choose)

| Option | Description | Effort | Risk |
|---|---|---|---|
| **A. Update x-session-guardian** | Add a second auth-check path that uses the mavis browser bridge (query active tab URL, verify it's x.com authenticated pages). PASS if either Playwright cookies OR mavis bridge confirms X session. | 1-2 hours | Low — additive check, doesn't break Playwright path |
| **B. Rewrite x-reply-guy for mavis browser** | Replace Playwright MCP with `mavis browser tool` calls (navigate, snapshot, click, type). All other resilience skills (bouncer, locator, validator) need porting too. The graphql-interceptor specifically needs a new approach (mavis browser doesn't intercept network). | 4-6 hours | Medium — large surface change, needs thorough test |
| **C. Keep Playwright path, fix the session** | Launch a new Playwright Chrome instance with the user's real Chrome user-data-dir. This would inherit the X session cookies. The graphql-interceptor and bouncer work as-is. | 30 min - 1 hour | Low — known Playwright pattern. The risk: headless Chrome with real profile = X may detect automation |
| **D. Disable reply-sweep-daily until fix is in** | Disable the recurring cron. Resume when the pipeline is ported. | 5 min | None |

**Recommended:** Option C (lowest effort, highest reliability, preserves the existing skill surface). Fallback: Option A if C has anti-bot issues.

## Today's actual state

- Replies published today: 3 (from earlier sessions)
- Daily cap: 10
- Remaining capacity: 7
- Next scheduled sweep: tomorrow 19:00 CT (will HALT without a fix)
- The 17:01 CT `R1D2` approved draft publish is in the queue log but that's a draft → published, not a reply

## What Andre needs to do

Pick A / B / C / D. Or: "ship C now" and I'll do it in the next session. The HALT will repeat at 19:00 CT tomorrow without action.
