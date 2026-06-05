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

## Memory hygiene (Mavis-specific)
- **Append** = new entry. **Edit/Write** = update, merge, remove. Don't mix.
- Topic files in this dir are loaded on demand only — keep `MEMORY.md` lean
- Topic files MUST start with YAML frontmatter `description` (system auto-injects)
- Memory is a hint, not live state — verify before acting on it
- Language: write in Andre's natural language (English)
