---
date: 2026-06-22
type: connection
trigger: nightly-finder
strength: strong
thesis-relevant: false
operational: true
---

# Connection: Cron Registration Daemon-Blocker (40904) ↔ Obsidian Plugin In-Memory State Lesson

**Why this connection matters:** Today's dial-in cycle hit a 40904 stale-cache error when trying to register the `rate-limit-tracker` cron — the spec file was correct on disk but the daemon (managed by the desktop app, not CLI-accessible) had a stale config cache that wouldn't refresh. The Phase 3 Dashboard for the Cognitive-Parameter-Graph project documents an identical 40904 error blocking the `sepo-runner-weekly` cron. The Phase 2 Obsidian MCP wiring (2026-06-17) hit a structurally identical lesson — the Local REST API plugin loads settings into memory at `onload()` and does NOT re-read `data.json` on subsequent disk writes. **These are three different surfaces (cron daemon, plugin host, MCP config) all expressing the same operational principle: spec-on-disk ≠ live-state-while-host-is-running.** The durable lesson from 2026-06-17 was already general — "for any plugin-integrated surface, the on-disk config file is NOT authoritative while the host process is alive." Today's dial-in + this morning's SePO cron blocker are the second and third instances. The lesson deserves to move from "load-bearing for Obsidian MCP" to "load-bearing for the entire local service ecosystem."

**Note A:**
- Title: Phase 3 Dashboard — SePO Loop (ACTIVE)
- Path: `~/MiniMax-Agent/03 Projects/Cognitive-Parameter-Graph/dashboard-2026-06-22.md`
- Claim: `sepo-runner-weekly` cron blocked by `40904 Cron config already exists` stale-cache. Daemon restart or cache clear required to register. Spec file is on disk and correctly written.

**Note B:**
- Title: Dial-in Ledger — MiniMax Token Plan
- Path: `~/MiniMax-Agent/03 Projects/Mavis EA Design/minimax-token-dialin-ledger-2026-06-22.md`
- Claim: Dial-in #1 (rate-limit-tracker fix) blocked by identical `40904 stale-cache` error. Same root cause: daemon's stale config-cache. `mavis restart` refused ("Daemon is managed by the MiniMax desktop app"). Workaround: executed procedure manually, captured today's log manually.

**What reading both reveals:** This is a recurring failure mode, not a one-off. Three surfaces, same error, same fix-shape (host restart). The Obsidian MCP lesson captures the principle. The cron daemon blocker extends it. **Generalizing the durable lesson: any locally-hosted service with an `onload` + in-memory state (Obsidian plugin, cron daemon, possibly MCP servers) will exhibit the disk-vs-runtime divergence.** The fix-pattern generalizes too: (1) edit disk file, (2) verify spec lints correctly, (3) attempt registration, (4) on 4xx stale-cache, accept manual workaround OR escalate to host-process restart (yellow action). The Phase 2 vault already prescribes the "for any plugin-integrated surface" diagnostic (`lsof` + `ps` cross-check). The cron daemon diagnostic is `mavis cron list` + `mavis cron info` + checking daemon's process state. Both are: "verify what the host thinks, not just what disk says."

**Suggested next step:**
- Promote the durable lesson in the Phase 3 Dashboard from "Obsidian plugin-specific" to "any locally-hosted service with in-memory state." Cross-link to the dial-in ledger #1 entry and this connection note.
- Codify as a skill: `ea-config-host-restart` (or `ea-spec-vs-runtime-check`) — pattern: edit disk spec → verify lint → register → if 4xx stale-cache, check host process state (`lsof`, `ps`, daemon logs) → choose manual workaround vs host restart.
- Track as a candidate for `ea-cron-repair` codification per the Garry Tan 3-runs rule. Today's instance + Phase 3 cron instance + Obsidian plugin instance = 3 runs across 6 days. Threshold met. Codify.
