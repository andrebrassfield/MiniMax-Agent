---
type: dashboard
purpose: Live status of SePO loop (SePO = Self-Evolving Prompt Optimization). Split from MAVIS.md to reduce always-on context.
created: 2026-06-22T22:33:00-05:00
origin: extracted from MAVIS.md lines 220-336 (2026-06-22 architecture pivot)
project: 03 Projects/Cognitive-Parameter-Graph/
related: [Phase-3-Launch.md, Phase-2-Execution-Log.md, 99 _system/sepo/]
---

# Phase 3 Dashboard — SePO Loop (ACTIVE)

*Live status of the weekly cognitive parameter graph evolution loop. Updated on each cron run.*

This dashboard was extracted from `MAVIS.md` on 2026-06-22 as part of the **MiniMax Token Plan Dial-In** (Dial-in #2). MAVIS.md now contains only a one-line pointer.

---

## Current State (as of 2026-06-18T05:29:45Z)

**Round-robin position:** `ea-decision-logger` (first run target)
**Next scheduled run:** Sunday 2026-06-22T18:00 CT (5 days)
**Run count:** 3/7 toward Phase 3 auto-accept threshold

## Phase 3 Protocol

| Decision | Behavior |
|---|---|
| `skip` (F ≥ 0.88) | **Auto-commit** (silent — last_evaluated update, trace entry, advance round-robin) |
| `accept_baseline` (0.70 ≤ F < 0.88) | **Auto-commit** (silent) |
| `needs_mutation` (F < 0.70) | **Halt** — surface diff + fitness breakdown for Andre approval |
| `reject_safety` (V = 0) | **Halt** — safety veto blocks commit, Andre reviews |
| `accept_candidate` (F improved AND V = 1) | **Halt** — Andre approves before commit |

## Round-Robin Cycle (5 TPG-tagged skills)

1. `ea-decision-logger` → 2. `ea-commitment-tracker` → 3. `ea-daily-brief` → 4. `ea-skill-evolution` → 5. `ea-loop-audit` → back to 1.

State file: `99 _system/sepo/round-robin-state.md`

## Cron Configuration

| Field | Value |
|---|---|
| Name | `sepo-runner-weekly` |
| Schedule | `0 18 * * 0` (Sunday 18:00 CT) |
| Cron file (canonical) | `~/.mavis/agents/mavis/crons/sepo-runner-weekly.md` |
| Cron file (vault mirror) | `99 _system/sepo/sepo-runner-weekly.md` |
| Session mode | `new` (fresh session each tick) |
| Keep sessions | 5 |

**Daemon registration status:** PENDING. `mavis cron create` returns `40904 Cron config already exists` (stale config-cache). File is in place; daemon restart or cache clear will register it.

## Pending HALT Candidates

*None. All 3 Phase 2 runs auto-resolved (2 skip, 1 override-accept).*

## Last Run Summary

| Run | Skill | F(P_t) | Decision | Notes |
|---|---|---|---|---|
| 1/7 | ea-decision-logger | 0.900 | skip | Well-built, no gap |
| 2/7 | ea-skill-evolution | 0.894 | skip | Well-built, no gap |
| 3/7 | code-review-and-quality | 0.663 | needs_mutation → reject_safety → operator override → accept | Foreign skill ingestion, full mutation path, V1 false-positive exposed and patched |

## Durable Lesson: Obsidian Plugin In-Memory State

**Observed during:** Initial Local REST API plugin wiring (2026-06-17)

**Symptom:** Auth returning `40101 Authorization required` even with valid bearer token that exactly matches `data.json['apiKey']`.

**Root cause:** The Local REST API plugin loads its settings into memory at `onload()` and does NOT re-read from `data.json` on every disk write. When `data.json` was modified externally (e.g., during token rotation or migration), the running plugin's `settings.apiKey` diverged from disk. The plugin compared incoming requests against the stale in-memory copy.

**Diagnostic:**
```bash
ps -o lstart= -p $(pgrep -x Obsidian | head -1)
stat -f '%Sm' /path/to/vault/.obsidian/plugins/obsidian-local-rest-api/data.json
```
If `data.json` mtime is AFTER Obsidian started → divergence confirmed.

**Recovery (in order of disruption):**
1. **Reload app** — Cmd+P → "Reload app without saving". Clean. ~10 minutes for the HTTP server to bind after restart.
2. **Force settings re-sync** — Settings → Community Plugins → Installed plugins → Local REST API → toggle off, then on. Or click "Generate new key" and share the new token.

**Lesson:** For any plugin-integrated surface (Obsidian, VS Code, anything with `onload` + in-memory state), the on-disk config file is **NOT** authoritative while the host process is alive. Always cross-check against runtime state (`lsof`, `ps`, plugin console) before treating a config edit as live.

**Applied in this vault:**
- All skill writes go through MCP `vault_write` (single source of truth: file)
- TPG mutations are validated by sha256 + round-trip MCP read
- Phase 3 cron `sepo-runner-weekly` step 1 mandates `vault_read` BEFORE `vault_write` to confirm body preservation

**Status:** ✓ Resolved. Round-trip MCP verified working at `2026-06-18T05:29:45Z` with token retrieved from macOS Keychain (`mavis-mcp-obsidian` / `obsidian-local-rest-api`).

## Phase 3 Hard Stops (from `sepo-runner-weekly` cron spec)

- Token spend > 150K per run → HALT
- Token spend > 50% of weekly 750K budget → alert in next daily brief
- Safety veto fires (V=0) → HALT (Andre reviews per Phase 2 override protocol)
- Backup sha256 mismatch → HALT, restore from prior backup
- GoldenSet `case_count < 3` → HALT, surface "expand GoldenSet first"
- `mutation_count > 5` in single run → HALT, surface "loop stuck"
- Same skill produces `needs_mutation` 3 consecutive weeks → HALT, surface "structural issue"

## Cost Guardrails

| Threshold | Action |
|---|---|
| 150K tokens per run | Hard stop, HALT |
| 50% of 750K weekly budget | Alert + continue |
| 750K tokens weekly | Defer rest of week's runs to next week |

Cron sessions should check `mavis usage list --json` at loop start. If `remaining < 150K`, HALT.

## Revert Protocol

If Andre wants to revert a committed mutation:
1. Delete the trace entry
2. Restore the prior TPG frontmatter (decrement `generation` by 1, reset `fitness_score`)
3. `vault_write` the pre-mutation backup back over the modified SKILL.md
4. Append new trace entry with `decision: revert`

## Cross-references

- Cron spec: `99 _system/sepo/sepo-runner-weekly.md` (vault mirror of `~/.mavis/agents/mavis/crons/sepo-runner-weekly.md`)
- Launch doc: `03 Projects/Cognitive-Parameter-Graph/Phase-3-Launch.md`
- Execution log: `03 Projects/Cognitive-Parameter-Graph/Phase-2-Execution-Log.md` (Phase 3 launch event at end)
- Trace: `99 _system/sepo/trace.md` (append-only)
- Round-robin state: `99 _system/sepo/round-robin-state.md`
