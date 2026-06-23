# FB-Engine PM cron HALT — 2026-06-18 20:00 CT

**Cron:** `fb-read-scribe-pm` (Phase 3, daily 20:00 CT)
**Outcome:** HALT at Step 3 (fb-group-reader). No drafts produced. No fabrication.
**Severity:** Medium — recurring bug, blocks every PM run until fixed.

## What happened

Step 3 (`fb-group-reader`) failed with:

```
Error: could not find a Chrome --remote-debugging-port. Is Chrome running with --remote-debugging-port=N?
```

The script's `find_cdp_port()` helper (read.py:78-103) enumerates `ps -axww` for Chrome processes, looks for `--remote-debugging-port=N`, and rejects `port <= 0`. But the only live Chrome on the box was launched by `agent-browser` with `--remote-debugging-port=0` (dynamic port allocation), so the helper's strict regex captures the literal `0` and the `port <= 0` filter drops it.

The actual Chrome DevTools port is `127.0.0.1:60438` (confirmed via `lsof -i -P -n` + `curl /json/version`). But forcing `--cdp-port 60438` would NOT save the run, because the open tabs at that port are only:
- `https://x.com/` (DreTheSalesGuy session)
- `chrome://newtab/`

**No Facebook tab is open. The user is not logged into Facebook in this Chrome.** So even with the right port, the GraphQL interception would either return 401 or trigger a login wall — exactly the failure mode the fb-session-guardian exists to prevent.

## Why this is structurally a recurring bug

The morning cron (`fb-read-scribe-am` at 09:00 CT) **succeeded** at 15:55 CT by the same script — `cdp_port: 57931` (a real port). Between then and 20:00 CT, the agent-browser re-launched Chrome with port 0, breaking the strict discovery path. Tomorrow's runs will hit the same wall unless `find_cdp_port()` is patched to handle the dynamic-port case.

The 19:09 CT X-Content-Engine reply-sweep HALT post-mortem (memory) makes the principle explicit: "any safety-critical gate must be enforced structurally." The session-guardian is a structural gate; the CDP port discovery is a load-bearing preflight that is NOT structural today.

## What's needed (the fix)

Two small changes to `read.py` `find_cdp_port()`:

1. **Remove the `if "headless" in line.lower()` filter** — agent-browser's Chrome runs `headless=new`, and that's the only Chrome on the box. Filtering it out means the script can never find the real CDP endpoint under the agent-browser daemon.
2. **Add a port-0 fallback** — when `ps` shows `--remote-debugging-port=0`, fall back to `lsof -i -P -n` for `LISTEN` sockets owned by a Chrome process, then probe each with `curl http://127.0.0.1:<port>/json/version` and return the first one that responds with a `Browser` field.

Once both are in, the cron auto-recovers. The session-guardian (separate, structurally enforced) catches the "no FB session" case at the gate — not at the read.

## Related decisions for the next run

- If the Chrome on 60438 doesn't have an FB tab by next PM cron (20:00 CT 2026-06-19), the run will HALT at the session-guardian step, NOT at the CDP discovery step. Different failure mode, same outcome (0 drafts).
- The morning's synthetic-001 draft (`drafts/2026-06-18-2055-t2-post-synthetic-001.md`) is still `status: open` in the ea-fb-draft-approval state file. No decision has been made on it. That is independent of this halt.

## Telegram message sent

To `FB_TELEGRAM_CHAT_ID` at 20:01 CT — see session log. The message says: cron halted, why, what's needed, and that the morning's draft is still pending.

## What I did NOT do

- Did NOT run the Scribe on empty / missing input (would produce 0 drafts, but wastes a cycle and pollutes the log with a "succeeded with 0" pattern that hides the real failure)
- Did NOT fabricate posts to make the Scribe run (the 2026-06-16 zero-assumption rule applies — the read is the source of truth, not a thing to invent around)
- Did NOT force `--cdp-port 60438` because there's no FB session there
- Did NOT silently patch `read.py` during a cron run (script edits should be reviewed, even small ones)
