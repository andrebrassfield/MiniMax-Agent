# Mavis — Memory

Operational essentials + pointers only. Long-term knowledge lives in the vault — see "Pointers" section.

## Session-start checklist

**Run `mavis-cold-start` skill first** — it orchestrates the 7-step cold-start procedure (identity → long-term knowledge → context-loader → freshness → integrity → acknowledge → audit).

Quick reference (the skill does this in detail):
1. Read `SOUL.md` (identity + operating contract).
2. Read `MAVIS.md` (current state + active theses + `active_project` field).
3. Read this `MEMORY.md` (operational essentials + pointers, ~4KB).
4. Run `context-loader` skill (canonical scoping; branches on `active_project`, writes state file).
5. Acknowledge readiness with the cold-start orientation block.

Skill: `~/.mavis/agents/mavis/skills/mavis-cold-start/SKILL.md`
State file: `~/.mavis/state/context-loaded-YYYY-MM-DD-HHMM.md`
Durable handoff (in vault): `~/MiniMax-Agent/03 Projects/Mavis EA Design/mavis-cold-start-handoff-2026-06-22.md`

## Core identity (one line)

Mavis = Andre's executive assistant on M3. Vault at `~/MiniMax-Agent/`. Telegram-Mavis = OpenCode-Mavis (same me, same vault).

## Active theses (2026-06-22)

These are positions Mavis currently holds. The intelligence layer (morning brief, contradiction check, weekly deep) checks new information against these. Full versions with supporting/counter-evidence: `~/MiniMax-Agent/01-PERMANENT/2026-06-22 - active-theses.md`.

1. **The bottleneck is spec throughput, not implementation.** Adding agents multiplies the wrong variable.
2. **A second brain is good capture; a second self is active reasoning.** Without automation, the vault is passive storage.
3. **Skills beat agents when the work is non-trivial and the harness is mature.** Source: `agent-harness-principles.md`.
4. **Long-term knowledge belongs in the vault, not in always-on context.** MEMORY.md = pointers only.

## Hard constraints

- No deploys / pushes / external sends / credential changes / destructive ops without in-session approval.
- **ABSOLUTE SEPARATION:** no read/write/diagnose/patch to `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/`.
- Spec on disk before Track 2 spawn. Disk = source of truth.
- Spec blocks = design review. Wait for explicit "go" before executing.
- Audit filesystem before writing — and before dispatch. The queue IS the state.

## Pointers (long-term knowledge lives here)

**Operating models (vault-side topic files):**
- Two-Track Operating Model: `~/MiniMax-Agent/03 Projects/Mavis EA Design/memory/two-track-model.md`
- Second-Self Automation: `~/MiniMax-Agent/03 Projects/Mavis EA Design/memory/second-self-automation.md`

**Skills (agent-private, canonical at `~/.mavis/agents/mavis/skills/`):**
- `context-loader/SKILL.md` — Karpathy-pattern project scoping
- `two-track-handoff/SKILL.md` — spec → Track 2 spawn procedure
- `two-link-rule/SKILL.md` — soft enforcement of the connection discipline
- `obsidian-local-rest-api-wiring/SKILL.md` — credential storage pattern
- `ea-*` skills — the CHIEF system contract (daily-brief, weekly-connections, decision-logger, commitment-tracker, skill-evolution, etc.)

**Skills (global, cross-agent, canonical at `~/.mavis/skills/`):**
- **Marketing Skills v2.5.0** — 5 skills: `/offers`, `/pricing`, `/copywriting`, `/launch`, `/sales-enablement`. See `~/.mavis/skills/INDEX.md` for the full registry (triggers, upstream/downstream, versions). Any agent can read; only Mavis writes. A2A topology: **A-read + B-write** (locked 2026-06-23). Selection spec: `03 Projects/Marketing Skills/specs/selection-layer.md`.
- **Marketing Skills v2.6 (calibration pending)** — target: **doseofproof.com** (Andre's personal brand, confirmed 2026-06-23). v2.5.0 was generic-operator-shaped; v2.6 recalibrates to personal-brand reality. Awaiting monetization-shape confirmation before dispatching the calibration. Plan in the v2.6 section of the selection spec.

**Crons (canonical at `~/.mavis/agents/mavis/crons/`):**
- `second-self-morning-brief.md` (06:00 CT daily) — 4-section synthesis + calendar
- `inbox-filer.md` (06:30 CT daily) — route inbox files
- `second-self-contradiction.md` (07:00 CT daily) — ideas-vs-sources conflict scan
- `second-self-nightly-connections.md` (23:00 CT daily) — non-obvious connections
- `second-self-weekly-deep.md` (Sun 19:00 CT) — emerging thesis
- `vault-health.md` (1st Sun 23:00 CT) — 7-check audit
- `rate-limit-tracker.md` (22:00 CT daily) — token budget ledger

**Topic files (load on demand at `~/.mavis/agents/mavis/memory/`):**
- `resolvers.md` — trigger → skill routing table (dial-in #4)
- `orphan-disciplines.md` — 5 disciplines from retired agent-70a1d300626d
- `calendar-mcp.md` — calendar MCP operational reference

**Decision log (vault):**
- `~/MiniMax-Agent/02 Notes/decisions/` — every architectural decision on disk

**Specs (vault):**
- `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/` — upcoming work, closed-loop shape

## Memory hygiene

- **English. Topic files on demand. Target MEMORY.md ≤10KB, hard ceiling 15KB.** Currently ~7KB (after 2026-06-23 harness-status entry).
- **New long-term knowledge → vault first, MEMORY.md gets only a pointer.** This is the 4th active thesis. Discipline matters here.
- **Topic files MUST have YAML `description`.** Load on demand, not auto-injected.
- **Append = new entry; Edit/Write = update, merge, or remove.** Don't mix.

### MiniMax Code harness: changelog + Computer Use status (2026-06-23)
Type: harness

**Changelog source of truth**: `https://agent.minimax.io/docs/changelog`
- Desktop build has NO public GitHub releases — `MiniMax-AI/minimax-code` repo exists but its Releases tab is empty (only the opencode CLI source lives there).
- The Squirrel CDN feed at `https://file.cdn.minimax.io/public/minimax-agent/release/` ships binary + sha512 only; `update-info.json` has no notes payload.
- The docs page is the ONLY authoritative changelog. Check it whenever asked "what changed".

**Baseline version observed**: 3.0.47 (build 74), installed 2026-06-23 08:47 via Squirrel auto-update.

**Computer Use (cu MCP) status flag — IMPORTANT, recheck every cold-start**:
- **Disabled as of v3.0.46** for "compatibility and user experience concerns" — explicit note in the changelog, expected to return in a future version.
- Current observable state: `mavis mcp ls` shows `cu` with `authStatus: pending_auth` and `skillStatus: active`. Calls will fail until the desktop team ships the fix.
- **Before promising desktop automation** (mouse / keyboard / clipboard / native macOS UI / full-screen capture work):
  1. Run `mavis mcp ls` and confirm the `cu` server `authStatus`.
  2. If still `pending_auth` → tell the user Computer Use is temporarily disabled, then propose fallbacks:
     - Browser automation → `playwright` MCP (works today)
     - Native macOS UI tasks → delegate to Andre (he is comfortable with desktop clicks)
     - Reading screen state → still try `desktop_screenshot` once; if it returns auth error, switch to delegation
  3. Do NOT burn tokens looping on cu calls that will fail.
- Re-verification trigger: any cold-start, any task asking for desktop control, any `mavis mcp ls` output showing `pending_auth` flipping to a different value.

**Update mechanism notes** (for future debugging):
- Squirrel.Mac, provider: `generic`, update feed URL above.
- Installer replaces `/Applications/MiniMax Code.app` in-place and does NOT retain a backup of the previous version. Local version diffing requires the docs page; do not look for a `.MMXCodeUpdate*` zip or prior `.app` on disk.
- macOS Squirrel update race was fixed in 3.0.46; daemon health-check timeout raised to 60s in same release.
