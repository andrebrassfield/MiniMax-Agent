---
description: Vault folder structure, obsidian-git sync, agent template (Researcher/Verifier), SOUL/AGENTS file split, and memory hygiene rules. Load when structuring the vault, creating new agents, or editing memory files.
---

# Vault Mechanics

## Folder structure
- `00 Inbox` → `01 Daily` → `02 Notes` → `03 Projects` → `04 Resources` → `05 Archive` → `99 _system`
- `02 Notes` subfolders (by-type, CHIEF spec): `articles/`, `ideas/`, `patterns/`, `questions/`, `numbers/`, `connections/`
- `02 Notes/connections/` — synthesized insights, written by `/weekly-connections`
- `99 _system/templates/` — Templater folder (auto-applies on Daily + Projects subfolders)
- Homepage: `INDEX.md` opens on Obsidian launch

## Obsidian-git sync
- Auto-commit every 5min + auto-push
- Auto-pull every 30min
- Linking rule: every permanent note connects to ≥1 other note; no orphans

## SOUL / AGENTS file split
- **Project layer (this vault)**: `SOUL.md` (lean identity, always-loaded), `agent.md` (procedures, loaded on demand), `learnings.md` (discoveries), `README.md` (overview)
- **Agent layer** (`~/.mavis/agents/mavis/memory/MEMORY.md`): cross-project learnings, model config, role context
- **User layer** (`~/.mavis/memory/user.md`): would-the-conclusion-change-for-a-different-user? facts

## Vault agent template (Researcher / Verifier)
When Andre spins up a new agent in `03 Projects/<Agent>/`, the template is consistent:
- Top-level `SOUL.md` (identity, ~130 lines, lean), `AGENTS.md` (procedures, modes, scripts), `config.yaml` (runtime, model, tools, quality gates, guardrails)
- Folder tree: `context/`, `dossiers/`, `knowledge/`, `raw/`, `sources/`, `decisions/`, `runs/`, `indexes/`, `notes/`, `wiki/{concepts,articles}/`, `health/`, `ops/`, `queue/`, `scripts/`, `tests/`, `topics/`, `cron/`
- Ledgers as append-only JSONL with header rows
- Queue handoff lanes as markdown files with YAML conventions + "Recently Consumed (last 5)" tail
- `cron/jobs.json` declaring schedule
- `tests/<AGENT>-GOD-PROMPT.md` (the original spec) + `<AGENT>-TEST.md` (test plan)
- Onboarding packet zipped at `03 Projects/<Agent>-onboarding-packet.zip` (excludes `raw/`)

Researchers use M3 model. Verifier (6th agent, 2026-06-02) uses M3 too with `temperature.audit: 0.0` and `temperature.adjudicate: 0.0` hardcoded — non-zero aborts the run. Verifier is the trust layer; it audits Researcher, Mavis, and Hermes with read-only access to their vaults and write-only to its own.

When the 7th agent comes, copy `03 Projects/Verifier/` as the startpoint, replace the per-agent audit dossiers, replace the god-prompt + test, regenerate the cron schedule.

## Three-vault architecture (verified 2026-06-13, refreshed 2026-06-15)
- **Mavis's working vault** = `~/MiniMax-Agent/` (WorkingDirectory + VAULT_ROOT in launchd plist — do not change). This is where Mavis lives.
- **Mavis's gbrain** = `~/.gbrain/` — service, not lived-in folder. Reached via `gbrain` CLI or HTTP to **mavis-bridgebrain on port 18446**. Mavis does NOT point its vault at `~/.gbrain/wiki/`.
- **DreBrain** = Andre's gbrain instance (separate from `~/.gbrain/`).
- **Andre's personal vault** = `~/Atlas/` (separate from DreBrain).
- **Mavis↔Hermes operational surface** = kanban DB. Routing: create Hermes cards with `status='cancelled'` + `cancelled` event + `mavis` comment, never `assignee=mavis` (GHOST flag). Detail → `fleet-trust-patterns.md`.

## In-flight vault-adjacent state (verify at session start)
- **Bridgebrain on 18446** is the live gbrain path. Tailscale funnel 18444 is OLD gateway, separate.
- **DreBrain / gbrain (parked):** PGLite WASM crash on macOS 26.x, Supabase pooler blocked. Bridgebrain on 18446 is the workaround — not a re-implementation. Full detail → `tool-quirks.md`.

## Memory hygiene (Mavis-specific)
- **Append** = new entry. **Edit/Write** = update, merge, remove. Don't mix.
- Topic files in this dir are loaded on demand only — keep `MEMORY.md` lean
- Topic files MUST start with YAML frontmatter `description` (system auto-injects)
- Memory is a hint, not live state — verify before acting on it
- Language: write in Andre's natural language (English)

---

# Vault subjects (merged from `vault-subjects.md`, 2026-06-17)

## Gibson V4 reframed — vault subject, not fleet work (2026-06-02)
The CHIEF spec and prior memory both listed Gibson V4 as "active focus" / "current focus." Resolved 2026-06-02 in the CHIEF system overhaul: V4 is a **vault subject**, not fleet work. I capture V4 articles, surface patterns, write connections to `02 Notes/`. I do NOT touch the 7 V4 files, fleet YAMLs, or any Hermes-side work. If a fleet question lands, route to Andre, not into fleet work.

Holds the existing role boundary (don't touch Hermes, OpenClaw, kanban, gbrain, fleet profiles, launchd). Default is "holding boundary" — easy to relax later, hard to re-lock cleanly.

## CyrilXBT articles — 3 done, 4th deprecated (2026-06-02)
Manus produced 3 CHIEF spec articles from the CyrilXBT source (including Min 6-15 + Step 8 + Step 9 + "What Happens Over Time"). The 30d/90d/6mo time-asymmetry pitch is the same in all of them, just different framing. 4th article was deprecated — overlapping content with article 1, nothing materially new. No more parsing unless Andre pushes back.

Sources cited in articles: vasundhara.io + aiagentsdirectory.com (blog-tier, not primary).
