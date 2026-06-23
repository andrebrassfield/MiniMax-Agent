---
name: fb-session-guardian
description: |
  Pre-flight auth check for the Facebook session. Connects to the user's
  real Chrome via CDP, verifies `c_user` and `xs` cookies are present,
  navigates to facebook.com, and confirms the page title is not a login
  wall. Returns PASS/FAIL with a JSON diagnostic. Auto-invoke before any
  fb-group-reader / fb-draft-scribe / fb-poster operation. Mirror of the
  x-session-guardian pattern, scoped to Facebook. Do NOT use to bypass
  bot detection, to authenticate a fresh session, or for non-FB sites.
---

# fb-session-guardian

Read-only auth check for the FB-Engine pipeline. Same shape as
`x-session-guardian`, scoped to Facebook.

## When to invoke

**Pre-flight (load-bearing):**
- Before `fb-group-reader` (the read path)
- Before `fb-draft-scribe` (draft generation)
- Before `fb-poster` (publish path)
- As a cron pre-flight hook for any FB-Engine loop

**Triggers (manual):**
- "is my Facebook session alive?"
- "run fb-session-guardian"
- "check fb login"
- "FB pre-flight"

**Do NOT use for:**
- Authenticating a fresh session — the user must log in manually in their
  real browser. This script does NOT log in.
- Bypassing Facebook's bot detection — this script drives the user's
  existing real Chrome via CDP, no detection circumvention.
- Other platforms — X has `x-session-guardian`, LinkedIn has its own.

## The mechanism (the discipline)

Facebook rotates / invalidates session cookies after:
- Idle periods (the `c_user` cookie has a 1-year max, but the underlying
  `xs` is server-side invalidated on suspicious activity)
- Security incidents (Facebook may force a re-login if it sees a new
  device fingerprint or unusual location)
- Password changes
- Navigating to `/login` or hitting a checkpoint wall

If a sweep starts logged out:
- The GraphQL call returns 401
- Worse: a checkpoint wall appears mid-scrape and the account is locked

The guardian catches this BEFORE the sweep starts.

## The procedure (the discipline)

### Step 1: Auto-detect CDP port

The script scans `ps -axww` for a Chrome process with
`--remote-debugging-port=N` (matches the Playwright MCP's managed Chrome
first, falls back to any valid Chrome). Override with `--cdp-port`.

### Step 2: Read cookies

Connect via CDP, read cookies from the default context, look for:
- `c_user` — Facebook's user ID cookie (always present when logged in)
- `xs` — Facebook's session token (the load-bearing one)

If either is missing → FAIL immediately, do not even navigate.

### Step 3: Title check

Navigate to `https://www.facebook.com/`, read the page title. Verify it
does NOT contain any of:
- `log in`
- `log into`
- `log in or sign up`
- `create new account`
- `sign up for facebook`
- `sign up`

If any marker matches → FAIL with diagnostic noting the title.

### Step 4: Report

```json
{
  "session_state": "PASS",
  "cookies_present": {"c_user": true, "xs": true, "fr": true, "datr": true},
  "title_check": "OK",
  "current_url": "https://www.facebook.com/",
  "page_title": "Facebook",
  "cdp_port": 58632,
  "diagnostic": "session authenticated",
  "ts": 1718712345
}
```

## CLI

```bash
# Auto-detect CDP port
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-session-guardian/scripts/guard.py

# Explicit port
python3 .../guard.py --cdp-port 58632

# Cron-friendly: JSON only, no stderr noise
python3 .../guard.py --json-only
```

Exit codes:
- `0` = PASS — proceed with downstream FB-Engine operations
- `1` = FAIL — halt and surface error to operator

## HALT conditions

- CDP connection fails → FAIL, the browser bridge is down
- Required cookies missing → FAIL, user must log in manually
- Login wall in title → FAIL, user must re-authenticate

The script does NOT attempt to re-authenticate. Re-auth is a manual
operator action: open Chrome, log in, then re-run the guardian.

## Hard constraints

- READ-ONLY: never writes to Facebook, never clicks anything
- NO bot-detection bypass: drives the user's existing real Chrome session
- NO credential storage: the script reads cookies that already exist in
  the browser; it does not store or transmit them
- NO automatic re-login: re-authentication is always operator-driven

## Integration with other skills

The fb-group-reader skill requires this guardian to return PASS first.
The cron chain is: `fb-session-guardian` → `fb-group-reader` →
`fb-draft-scribe` (next) → `fb-poster` (next, gated on `approved/`).

## Cross-references

- `x-session-guardian` — the X.com analog (same pattern, different cookies)
- `x-graphql-interceptor` — the X.com GraphQL feed extractor
- `fb-group-reader` — the next step in the pipeline
- `mavis browser bridge` — the underlying Chrome this skill connects to

## Source

- `~/.mavis/agents/mavis/skills/fb-engine/fb-session-guardian/scripts/guard.py`
- Mirror: `~/MiniMax-Agent/99 _system/skills/fb-engine/fb-session-guardian/scripts/guard.py`

## Changelog

- 1.0.0 (2026-06-18) — initial skill. Mirrors x-session-guardian. CDP port
  auto-detection (prefers Playwright MCP's managed Chrome, falls back to
  any valid Chrome). Cookie check covers `c_user` + `xs`. Title check
  covers FB's 6 known login markers. JSON output with PASS/FAIL
  diagnostic. Cron-friendly (`--json-only` flag).
