---
type: fleet-status
subject: openhuman-mcp
status: parked
created: 2026-06-13
session: mvs_bfc8f53ecb204fde9a84fbfb11104b81
owner: mavis
---

# openhuman-mcp — parked (not decommissioned)

## Current state (verified 2026-06-13 20:24)

- **Process:** not running. PID 792 was terminated (SIGTERM, no escalation needed).
- **Port 9300:** released. Zero clients were connected at time of kill.
- **launchd:** `com.hermes.openhuman-mcp` is `disabled` in `gui/$UID`. The plist is preserved at `~/Library/LaunchAgents/com.hermes.openhuman-mcp.plist` (1,586 bytes, 2026-06-13 12:24) for future re-enable work.
- **Unlinked binary:** none. `lsof +L1` shows zero `txt` handles with inode=0. The 86MB ghost that was held by PID 792 is gone.
- **Workspace:** `/Users/brassfieldventuresllc/.openhuman/workspace/` (memory.db, chunks.db, memory_tree/) is intact. Held the state the process was producing before it was killed.

## Why it was parked, not decommissioned

The decision was made to **stop the live state and defer the long-term call**. Andre's instruction was explicit: clean the live state, don't decide the future today.

## What the logs told us (don't re-debug this)

Last 30 minutes of `~/.hermes/logs/openhuman-mcp.out.log` before kill was 100% `WRN:log [memory] batch embed failed for 1 chunk(s) ... No backend session for cloud embeddings: log in to OpenHuman, or set memory.embedding_provider to "ollama" / "none" in config.toml`. The service was alive but doing nothing useful — it was storing every memory write as un-embedded rows, which means future semantic search across the workspace would have been broken even if the daemon kept running.

## To re-enable (when ready)

1. Decide which embedding backend to wire up (ollama at `http://localhost:11434` is the path of least resistance since bridgebrain on 18446 already runs an Ollama instance, or the cloud path with a real session).
2. Update `~/Library/LaunchAgents/com.hermes.openhuman-mcp.plist`'s `EnvironmentVariables` (`BACKEND_URL`, `OPENHUMAN_CORE_TOKEN`) or the openhuman config.toml to match.
3. `launchctl enable gui/$UID/com.hermes.openhuman-mcp`
4. `launchctl kickstart -k gui/$UID/com.hermes.openhuman-mcp`
5. Verify: `lsof -iTCP:9300 -sTCP:LISTEN -nP` should show the process back, and the embed warnings should stop.

## To decommission fully (separate decision)

- `mavis-trash /Users/brassfieldventuresllc/.openhuman/workspace` (run preflight first; some files may be live if anything else mounted them)
- `rm ~/Library/LaunchAgents/com.hermes.openhuman-mcp.plist`
- `launchctl print-disabled gui/$UID | grep openhuman` to confirm no stragglers

## Related

- `~/.hermes/skills/safe-trash-preflight/SKILL.md` — Scenario A recovery procedure (the gap-fill that came out of this incident)
- Incident: 2026-06-13 afternoon, Mavis's cleanup trashed `~/.cargo/` while openhuman-mcp was running from `~/.cargo/bin/openhuman-core`. This parked state is the recovery; the skill is the prevention.
