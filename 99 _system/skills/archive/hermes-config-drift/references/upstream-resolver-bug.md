# Upstream Resolver Bug — Hermes `auxiliary_client.py:3888`

> Why this skill exists as a band-aid: the upstream Hermes code has a 5-line bug that silently flips `auth.json` `active_provider` back to `nous` every ~60s, no matter how many times you rehydrate.

## The bug

`~/.hermes/hermes-agent/agent/auxiliary_client.py:3888` (line numbers may drift between versions — search for `auth_type in {"oauth_device_code", "oauth_external"}`):

```python
elif pconfig.auth_type in {"oauth_device_code", "oauth_external"}:
    # OAuth providers — route through their specific try functions
    if provider == "nous":
        return resolve_provider_client("nous", model, async_mode)
    if provider == "openai-codex":
        return resolve_provider_client("openai-codex", model, async_mode)
    if provider == "xai-oauth":
        return resolve_provider_client("xai-oauth", model, async_mode)
    # Other OAuth providers not directly supported
    logger.warning("resolve_provider_client: OAuth provider %s not "
                   "directly supported, try 'auto'", provider)
    return None, None
```

No branch for `minimax-oauth`. The path returns `(None, None)` for the aux client, and the main auth flow then writes `active_provider: 'nous'` back to `auth.json` because that's the default fallback it knows how to handle.

## Detection (already wired into the healthcheck)

The `~/.hermes/scripts/hermes-config-healthcheck.py` has a `check_resolver_bug(findings)` function that scans the last 200KB of `~/.hermes/logs/agent.log` for the literal string:

```
unhandled auth_type oauth_minimax for minimax-oauth
```

If found, the healthcheck emits a finding pointing the user at this reference and at the kanban audit card `t_96382d79`.

## Verification command (one-liner)

```bash
grep -c "unhandled auth_type oauth_minimax" ~/.hermes/logs/agent.log
# Bug present: >0
# Bug absent or fixed: 0
```

## The 5-line fix (Hermes to land, not Mavis)

```python
if provider == "minimax-oauth":
    return resolve_provider_client("minimax-oauth", model, async_mode)
```

Drop it into the `elif pconfig.auth_type in {"oauth_device_code", "oauth_external"}:` block above, after the `xai-oauth` branch. Test convention: `tests/hermes_cli/test_auth_xai_oauth_provider.py` (search for `auth_type == "xai-oauth"` — the pattern is identical).

## Why Mavis does not patch this

Per `~/.mavis/agents/mavis/memory/orchestration-failure-modes.md` boundary rule and the Mavis-Hermes org chart in `MEMORY.md`:

- Mavis is chief-of-staff. Hermes is the fleet operator.
- Mavis's filesystem access to `~/.hermes/hermes-agent/agent/` is incidental, not authoritative.
- Patching from Mavis side would be reverted on the next `git pull upstream main`, create merge conflicts on `feat/fleet-desktop-bridge`, and skip Hermes's PR review.
- The audit card `t_96382d79` documents the fix shape; the Hermes team lands it.

## The band-aid in place

While the upstream bug is live, the band-aid is:

1. `~/.hermes/scripts/hermes-config-healthcheck.py` runs every 5 min via launchd plist `~/Library/LaunchAgents/ai.hermes.config-healthcheck.plist`.
2. When the resolver bug flips `active_provider` to `nous`, the next 5-min tick detects it.
3. `~/.hermes/scripts/hermes-rehydrate.sh` (or the cron-side trigger, when wired) repairs all 3 layers + restarts the gateway.
4. The user sees Hermes broken roughly 1 in 5 times they start a chat session. Acceptable until upstream lands the fix.

## How to verify the band-aid is alive

```bash
launchctl print gui/501/ai.hermes.config-healthcheck 2>&1 | head -3
# Should show: "active count = 1" or "runs = N, last exit code = 0"
# Bad: "Could not find service"

tail -20 /tmp/hermes-config-healthcheck.out.log
# Should show a recent timestamp (within last 5 min) and either ✅ or ❌
```

If the plist is not loaded:

```bash
launchctl bootstrap gui/501 ~/Library/LaunchAgents/ai.hermes.config-healthcheck.plist
```

This is a **one-time fix per fresh user session**, not per Hermes restart. macOS launchd remembers the load across reboots of the gateway.

## Related

- Memory: `~/.mavis/agents/mavis/memory/MEMORY.md` — "Hermes aux_client resolver — minimax-oauth missing branch" entry (2026-06-13)
- Audit: `~/MiniMax-Agent/04 Resources/audits/2026-06-13-mac-deep-clean.md` — full incident report
- Upstream repo: <https://github.com/nousresearch/hermes-agent>
- Andre's fork: `git@github.com:andrebrassfield/hermes-agent.git` (branch `feat/fleet-desktop-bridge`, 1 commit ahead of upstream)
