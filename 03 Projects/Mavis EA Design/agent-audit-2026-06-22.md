---
date: 2026-06-22
type: agent-registry-audit
status: active
related:
  - ~/MiniMax-Agent/02 Notes/decisions/2026-06-22-two-track-model.md
  - ~/MiniMax-Agent/SOUL.md (Two-Track Operating Model section)
---

# Agent Registry Audit — 2026-06-22

Companion document to the 2026-06-22 two-track-model decision. Inventory + proposed disposition for every agent in `~/.mavis/agents/`.

## Inventory

Total registered: 11 directories. 4 are active workloads. 7 are candidates for retirement or investigation.

| Agent | Type | Last real activity | Disposition |
|---|---|---|---|
| **mavis** | Chief (this session) | Continuous | **KEEP** — runs both tracks |
| **x-researcher** | X-Content-Engine specialist | Active (cron chain) | **KEEP** — separate rate-limit pool, unaffected by two-track pivot |
| **x-scribe** | X-Content-Engine specialist | Active (cron chain) | **KEEP** — separate rate-limit pool, unaffected by two-track pivot |
| **verifier** | Built-in, verifier role | Active when dispatched | **KEEP** — legitimate verifier-only subagent channel |
| **builder** | Built-in, full overlay | 2026-06-04 (Artemis status board prototype) | **RETIRE** (archive) — work moves to Track 2 + skills |
| **coder** | Built-in, partial overlay | 2026-06-04 (Mavis Daily Check-in prototype) | **RETIRE** (archive) — work moves to Track 2 + skills |
| **designer** | Built-in, full overlay | 2026-06-04 (Designer onboarding handoff to Builder) | **RETIRE** (archive) — work moves to Track 2 + skills |
| **general** | Built-in stub, empty overlay | Never customized | **RETIRE** (delete) — zero content, zero history |
| **goose** | Unknown shape (no agent.md, no config.yaml at standard path) | Unknown | **INVESTIGATE** before deciding |
| **agent-70a1d300626d** | Unique-ID agent (no agent.md, has sessions + workspace) | Unknown | **INVESTIGATE** — likely generated/temp session artifact |
| **skills** (subdirectory of agents/) | Not an agent — directory containing `obsidian-skills/` | n/a | **KEEP** as-is |

## Per-agent detail

### KEEP

**mavis** — root chief. Runs Track 1 (spec, interactive) and Track 2 (implementation, separate session). Skill library lives here.

**x-researcher, x-scribe** — X-Content-Engine cron chain. Runs on its own session tree, dispatches from `~/.mavis/agents/mavis/crons/content-research-daily.md` and adjacent files. The two-track pivot does NOT affect them — they have their own rate-limit pool because they're crons, not interactive sessions.

**verifier** — built-in agent with the verifier role. Used as the verifier-only subagent channel per the hard constraint in the Mavis system prompt. Same role, same scope after the pivot.

### RETIRE (archive — recoverable)

These are built-in agents with full overlays. They had real prototypes shipped on 2026-06-04 but nothing since. Under the two-track model, their work goes in Track 2 sessions with the relevant skills loaded (`frontend-dev`, `fullstack-dev`, `ios-application-dev`, etc.) — same capability, no subagent quota burned, no parallel-attention cost.

**builder** — "Systems Builder: translates VERIFIED dossiers and technical specifications into functional, audit-ready code (single-file, zero external dependencies)." Zero-deps discipline, single-file HTML/JS/CSS constraint, handoff-to-Verifier protocol. Last activity: 2026-06-04 Artemis status board. Files of value: agent.md (the zero-deps + handoff discipline is reusable; should migrate into a fat skill).

**coder** — Daily Check-in prototype shipped 2026-06-04 (583 lines, 16KB, single HTML, localStorage persistence). Otherwise empty overlay. Files of value: the 6 discipline notes (single-question-per-turn, companion-mode aesthetic, localStorage persistence, "live with it a week" before feature work, affirmative framing). These should migrate into Mavis's MEMORY.md or a topic file.

**designer** — Design system, UI/UX, motion, typography. Pair-with-Builder-and-Researcher protocol. Last activity: 2026-06-04 Designer-onboard handoff. Files of value: design discipline (warm paper / system serif / breath-in fade), 4 design skills (taste-skill, ui-ux-pro-max-skill, vercel-agent-skills). Should migrate into a design-system skill under Mavis.

**Proposed archive procedure:**
1. Snapshot each agent's agent.md into `04 Resources/agent-archive/` for reference
2. Extract reusable discipline into MEMORY.md entries or fat skills
3. Rename agent directory: `mv builder builder.archived-2026-06-22`
4. Move to `~/.mavis/agents/_archive/` subdirectory so they don't appear in active registry
5. Reversible: rename back to `builder` if a future use case emerges

### RETIRE (delete — recoverable via trash)

**general** — built-in stub. agent.md is the boilerplate overlay comment with no customization. No sessions, no workspace content, no crons. Trivial to remove. Use `mavis-trash` (recoverable via macOS Trash).

### INVESTIGATE before deciding

**goose** — directory contains `harnesses/` and `skills/` only. No `agent.md`, no standard `config.yaml`. Either a partial install (in-progress setup), a custom harness framework, or stale. Read the contents of `~/.mavis/agents/goose/harnesses/` before deciding. Possible options:
- If active harness framework → integrate into Mavis's skill library
- If stale/empty → `mavis-trash` after review

**agent-70a1d300626d** — directory contains `config.yaml`, `crons/`, `memory/`, `opencode/`, `sessions/`, `skills/`, `workspace/`. No `agent.md` (uses the built-in default). The unique-ID name pattern suggests a generated session artifact (e.g., a one-shot test agent). Check:
- `ls ~/.mavis/agents/agent-70a1d300626d/sessions/` — count and recency
- `ls ~/.mavis/agents/agent-70a1d300626d/workspace/` — any content?
- `ls ~/.mavis/agents/agent-70a1d300626d/crons/` — any scheduled work?

If empty or stale, `mavis-trash`. If real work, integrate.

## Proposed action (next session)

I am NOT executing the retirements in this session — destructive agent changes need explicit in-session approval per SOUL.md red-zone rules. The audit findings are the deliverable here.

**Approval gate (next session):**
- "Approve archive of builder/coder/designer + delete of general + investigate goose/agent-70a1d300626d"
- On approve: I extract reusable discipline into MEMORY.md/skills, snapshot to `04 Resources/agent-archive/`, then `mv` to `_archive/` (archive) or `mavis-trash` (delete)

## What this means going forward

After retirement + investigation:
- Active agents: mavis, x-researcher, x-scribe, verifier (4 total)
- Archived: builder, coder, designer (3, recoverable)
- Cleaned up: general + any investigated-as-empty (1-2)

The two-track model is then: Mavis handles all Mavis-internal work (both tracks). x-researcher and x-scribe handle the X-Content-Engine cron chain. Verifier handles the verifier-only subagent channel. That's the complete operational surface.

---

## Retirements Executed — 2026-06-22 20:59 CT

Andre approved retirements in chat. Destructive-ops pre-flight completed per `ea-decision-logger`.

### Status

| Agent | Proposed | Executed | Reversible via |
|---|---|---|---|
| builder | RETIRE archive | ✓ `~/.mavis/agents/_archive/builder.archived-2026-06-22/` | `mv` back |
| coder | RETIRE archive | ✓ `~/.mavis/agents/_archive/coder.archived-2026-06-22/` | `mv` back |
| designer | RETIRE archive | ✓ `~/.mavis/agents/_archive/designer.archived-2026-06-22/` | `mv` back |
| general | RETIRE delete | ✓ trashed via `mavis-trash` | macOS Trash GUI |
| goose | INVESTIGATE | ✓ Hermes/OpenClaw fleet agent — archived docs to `04 Resources/agent-archive/goose-harnesses/` (5 files), then trashed | macOS Trash GUI |
| agent-70a1d300626d | INVESTIGATE | ✓ Orphan agent with 7 dated disciplines in MEMORY.md (2026-06-02 to 2026-06-06). 5 migrated to Mavis MEMORY.md (cross-project); 2 dossier-research-specific kept in `04 Resources/agent-archive/orphan-70a1d300626d-MEMORY.md`. Then trashed. | macOS Trash GUI |

### Active registry (post-retirement)

```
~/.mavis/agents/
├── _archive/                              ← recovery location
│   ├── builder.archived-2026-06-22/
│   ├── coder.archived-2026-06-22/
│   └── designer.archived-2026-06-22/
├── mavis/                                 ← me, runs both tracks
├── skills/                                ← obsidian-skills/
├── verifier/                              ← legitimate verifier subagent
├── x-researcher/                          ← X-CE cron chain
└── x-scribe/                              ← X-CE cron chain
```

Exactly the post-pivot shape the two-track-model decision called for.

### Backup

`/Users/brassfieldventuresllc/.backups/pre-agent-retirement-2026-06-22T20-58-CT.tar.gz` (122MB, includes node_modules). Full restore: `tar xzvf <backup> -C /`.

### Discipline migration summary

5 of 7 orphan-agent disciplines apply to Mavis's scope and are now in MEMORY.md under "Cross-project disciplines migrated from retired agent-70a1d300626d (2026-06-22)":

1. Timestamp null-first (applies to handoff registry, cron logs)
2. Structure inspection after script-based file rewrites (universal)
3. Future-proofing test: dossier-quality spec obviates Design agent (reinforces this retirement)
4. JSONL append: ID-field syntax check (applies to commitments.jsonl, registry.jsonl)
5. JSONL schema hygiene: escape double-quotes in excerpts (universal)

2 dossier-research-specific disciplines (wiki-article-linking-from-dossier-headers, claim-context-decay) stayed in the archived MEMORY.md for future-researcher reference.
