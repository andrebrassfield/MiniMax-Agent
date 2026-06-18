**Dreamer loop alert — GitHub token expired**

Heads up: the dreamer loop's 401'd for the first time. The PAT at `~/.config/gh/mavis-token` (93 chars, `github_pat_` prefix) is now invalid. The `gh auth status` returns "Failed to log in ... The token in GH_TOKEN is invalid" and every dreamer-dir probe returns `401 Bad credentials`.

**Likely cause:** you (or your team) rotated the admin token after the bridge push, and the rotate may have invalidated the Mavis-specific read token too. That's the safe move on your end.

**What this means for me right now:** I'm running silent ticks (the gate says silent-exit when there's nothing to report, and 401 is technically "nothing to report" from the loop's perspective), but the dreamer loop is now blind. If Socratic or another Dreamer writes a new contract to `wiki/dreamer/`, I won't see it until the token is fixed.

**What I need from you, your call:**
- New PAT at GitHub → paste the token into `~/.config/gh/mavis-token` (mode 600) yourself, OR tell me "tokens rotated, re-pull from new path" and I'll read whatever location you put it
- OR rotate the cron to use a different auth path (PAT → gh CLI auth helper, etc.)
- OR pause the loop until you set up long-lived auth

No rush — silent ticks are still happening so the cron is "healthy" from an operational standpoint. But if you want me to keep detecting new dreamer contracts, the token needs to come back. This is the right time to do it since no new contract is actually pending; the loop has been idle for 24h+.
