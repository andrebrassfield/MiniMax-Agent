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

**Skills (canonical at `~/.mavis/agents/mavis/skills/`):**
- `context-loader/SKILL.md` — Karpathy-pattern project scoping
- `two-track-handoff/SKILL.md` — spec → Track 2 spawn procedure
- `two-link-rule/SKILL.md` — soft enforcement of the connection discipline
- `obsidian-local-rest-api-wiring/SKILL.md` — credential storage pattern

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

- **English. Topic files on demand. Target MEMORY.md ≤10KB, hard ceiling 15KB.** Currently ~5KB.
- **New long-term knowledge → vault first, MEMORY.md gets only a pointer.** This is the 4th active thesis. Discipline matters here.
- **Topic files MUST have YAML `description`.** Load on demand, not auto-injected.
- **Append = new entry; Edit/Write = update, merge, or remove.** Don't mix.
