# 2026-06-10 00:39 CT — Hermes Gateway Rescue

## What happened

1. **User:** "I think Hermes messed his config up he won't respond"
2. **First action:** Ran `mavis-doctor`-style diagnostic. Found:
   - Gateway died at 00:26:12 CT with `BrokenPipeError` in `gateway/hooks.py:140` (print to closed pipe during hook discovery)
   - `gateway_state.json` stuck at `starting`, `pid: 45372` (the crashed instance)
   - User-allowlist warning: `No user allowlists configured. All unauthorized users will be denied.`
   - Config diff vs 2026-06-08 backup showed provider changed from `opencode-go/deepseek-v4-flash` to `nous/nvidia/nemotron-3-ultra:free` at 00:17 CT (the 00:17 config edit)
3. **User:** "I need you to restart the gateway so I can tell him that"
4. **Action:** Identified launchd supervisor (gui/501 domain), used `launchctl kickstart -k` on `ai.hermes.gateway` to restart the canonical service. New PID 46788 came up healthy, Telegram reconnected within 30s.
5. **User:** "Kill the orphans for good"
6. **Action:** Discovered two launchd services were orphans: `ai.hermes.gateway-general-executor` and `ai.hermes.gateway-secure-executor`. Both had `KeepAlive: true` and respawned after every `pkill -9`. The fix:
   - `pkill -9 -f "hermes_cli.main.*--profile.*gateway run"` (immediate)
   - `mv` the plists to `.DISABLED-2026-06-10-mavis-cleanup` (on-disk signal)
   - `launchctl bootout user/501/ai.hermes.gateway-{general,secure}-executor` (in-memory state)
   - The key insight: the services were in the `user/501` domain, NOT `gui/501`. Initial `bootout` attempts failed with "No such process" or "I/O error" because I was using the wrong domain.
7. **Result:** Clean state. Only the canonical gateway remains.

## What I touched

- `~/Library/LaunchAgents/ai.hermes.gateway-general-executor.plist` → renamed to `.DISABLED-2026-06-10-mavis-cleanup`
- `~/Library/LaunchAgents/ai.hermes.gateway-secure-executor.plist` → renamed to `.DISABLED-2026-06-10-mavis-cleanup`
- No config files modified, no env files modified, no service definitions changed.

## Out-of-scope items I flagged but did not fix

1. **BrokenPipeError in gateway boot** — `gateway/hooks.py:140,143` should wrap `print(..., flush=True)` in try/except BrokenPipeError so a closed pipe doesn't kill the gateway. This is a Hermes code change, not a state change.
2. **Provider config switch** — the 00:17 CT config change moved from `opencode-go/deepseek-v4-flash` to `nous/nvidia/nemotron-3-ultra:free`. The free model is slower and historically rate-limits. This may have caused the slow boot that made the broken-pipe race more likely. Hermes should review whether the provider change was intentional.
3. **User allowlist warning** — `~/.hermes/.env` has `TELEGRAM_HOME_CHANNEL=6598264778` but no `TELEGRAM_ALLOWED_USERS` or `GATEWAY_ALLOW_ALL_USERS`. Gateway says "All unauthorized users will be denied" but the home channel is likely auto-allowed. If Hermes doesn't respond to a test message, this is the next thing to check.
4. **gateway_state.json stale display** — the file still shows the original crash (pid 45372) instead of the new run (pid 46788). It only updates on state transitions. Cosmetic.

## Rollback if Hermes wants profile gateways back

```bash
# Restore the plist files
mv ~/Library/LaunchAgents/ai.hermes.gateway-general-executor.plist.DISABLED-2026-06-10-mavis-cleanup \
   ~/Library/LaunchAgents/ai.hermes.gateway-general-executor.plist
mv ~/Library/LaunchAgents/ai.hermes.gateway-secure-executor.plist.DISABLED-2026-06-10-mavis-cleanup \
   ~/Library/LaunchAgents/ai.hermes.gateway-secure-executor.plist

# Re-load into launchd
launchctl bootstrap user/501 ~/Library/LaunchAgents/ai.hermes.gateway-general-executor.plist
launchctl bootstrap user/501 ~/Library/LaunchAgents/ai.hermes.gateway-secure-executor.plist
```

## Key learning (reusable next time)

**macOS launchd has two user domains: `user/$UID` and `gui/$UID`.** They're NOT interchangeable. When `launchctl bootout gui/501/<service>` returns "No such process" but `launchctl list` shows the service, the service is likely in `user/501`. Always try both domains before concluding the service is gone.

This is the first time I've had to deal with this in this fleet. Worth filing in `orchestration-failure-modes.md` or similar.
