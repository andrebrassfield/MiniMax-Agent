---
date: 2026-06-22
type: closed-loop-spec
status: awaiting-approval
scope: context-loader
related:
  - ~/MiniMax-Agent/02 Notes/decisions/2026-06-22-two-track-model.md
  - ~/MiniMax-Agent/MAVIS.md (will gain active_project field)
  - ~/.mavis/agents/mavis/memory/MEMORY.md (session-start checklist)
  - ~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md (companion spec)
informed_by:
  - "How to Build an AI Second Brain With Claude and Obsidian" (article shared by Andre 2026-06-22)
  - Karpathy's LLM Wiki pattern (April 2026) — "open one project at a time" scoping
  - Two-track operating model (2026-06-22)
  - Second-self automation layer (2026-06-22)
---

# Spec: Context Loader — Karpathy-Pattern Project Scoping

The first upgrade to the shared brain. A cold-start procedure that loads ONLY the active project's context when Mavis is in project-focus mode, skipping the rest of the vault. Closes the cold-start time + token-cost + context-drift bottlenecks. Foundational — every future project work benefits.

## Goal (precise done condition)

This spec is DONE when:
1. **MAVIS.md frontmatter** has the `active_project` + `active_project_set_at` fields with documented semantics
2. **`context-loader` skill** exists at `~/.mavis/agents/mavis/skills/context-loader/SKILL.md` with the 5-step procedure (always-read SOUL + MAVIS + branch on active_project + write state file)
3. **Session-start checklist** in MEMORY.md references the skill (replaces ad-hoc discovery with skill invocation)
4. **State file schema** at `~/.mavis/state/context-loaded-YYYY-MM-DD-HHMM.md` is documented and the skill writes it on every invocation
5. **Cross-project bypass** is explicit in the skill — second-self crons (morning brief, contradiction, weekly deep) and explicit "load everything" requests bypass the scope
6. **Manual test passes:** Mavis cold-start with `active_project: FB-Engine` loads only FB-Engine context (verified via state file showing what was loaded and what was skipped)
7. **Reversibility verified:** a documented rollback path removes all 5 changes in <5 minutes
8. **MAVIS.md Active Skill Mutations entry** + MEMORY.md update written

## Context

**Source article:** The article Andre shared 2026-06-22 ("How to Build an AI Second Brain") highlights Karpathy's LLM Wiki pattern (April 2026): "The big vault plans. A single project ships." The article's Step 7 is the load-bearing move — open just the project folder as the vault so Claude sees only that job.

**Current bottleneck:** Mavis's cold-start takes ~3 minutes (per the session-start checklist in MEMORY.md: re-read SOUL + MAVIS + MEMORY + check crons + topic files). When Andre is deep in project work, most of the loaded context is irrelevant. Token cost per session is ~40% higher than it needs to be. Context drift happens when 02 Notes/ideas/ from one domain bleeds into a different project's reasoning.

**What we already have:**
- SOUL.md + MAVIS.md + MEMORY.md (the identity layer, more granular than CLAUDE.md)
- ~40 skills at `~/.mavis/agents/mavis/skills/` (the saved-workflow pattern is established)
- 25+ crons at `~/.mavis/agents/mavis/crons/` (the auto-pilot pattern is established)
- 03 Projects/ folder structure (each project is a subdir, but no session-level scoping)
- Obsidian MCP wired (the article's Step 3 is done)

**What's missing (the gap this spec closes):**
- Project-level scoping at session start (Karpathy's Step 7)
- Active-project awareness (Mavis doesn't know what Andre is focused on without asking)

**Why this is the first upgrade, not Calendar MCP / Inbox Filer / Interview Protocol / Vault Health:**
- Foundational — every future project work gets scoped automatically
- Low-risk — additive, reversible, no folder moves, no OAuth/credentials
- Real bottleneck — cold-start time + token cost are measurable today
- Aligns with article — directly implements the load-bearing pattern

## Action (atomic steps)

The execution can happen in this session (Track 1) since the scope is small + contained. Estimated effort: ~30 minutes total.

1. **Write this spec** — DONE (this file)
2. **Update MAVIS.md frontmatter** — add `active_project: null` + `active_project_set_at: null` fields, document the semantics inline
3. **Create `~/.mavis/agents/mavis/skills/context-loader/SKILL.md`** — full procedure with 5 steps + the cross-project bypass logic + the state file schema
4. **Update MEMORY.md session-start checklist** — replace steps 3-5 with "Run context-loader skill" + add the state-file verification step
5. **Write a usage note in SOUL.md** — single paragraph under Two-Track Operating Model about how Track 1 uses active_project for project focus
6. **Manual test** — set `active_project: FB-Engine` in MAVIS.md, run the skill, verify state file shows the correct load + the correct skips
7. **Document rollback** — append a "Rollback" section to the skill file with the exact 5-step revert
8. **Mirror skill to vault** — `99 _system/skills/context-loader/SKILL.md`
9. **Update MAVIS.md Active Skill Mutations** — "2026-06-22 — Context Loader (Karpathy-Pattern Project Scoping)"
10. **Update MEMORY.md** — add "Context Loader (2026-06-22)" entry under Core Identity section

## Feedback (verification gate)

Each context-loader invocation writes a state file. The state file IS the verification.

**Per-invocation state file schema:**
```markdown
---
loaded_at: <ISO-timestamp>
mode: project-focus | full-vault
active_project: <name> | null
---

# Context Loaded

**Mode:** project-focus (active_project: FB-Engine) | full-vault

## Loaded
- SOUL.md (<bytes>)
- MAVIS.md (<bytes>)
- <project root .md path> (<bytes>)
- <N> decisions from <path>
- <N> specs from <path>

## Skipped (intentionally, mode = project-focus)
- 02 Notes/ — skipped
- 06 Connections/ — skipped
- 03 Projects/<other projects>/ — skipped

## Cross-project bypass check
- Second-self cron firing? — no/yes
- If yes, switched to full-vault mode for this invocation

## Cold-start time
- Started: <ISO>
- Completed: <ISO>
- Total: <seconds>
```

**End-of-week gate (Sunday after the weekly-deep cron fires):**
- Next-Mavis reads the week's state files
- Verifies: project-focus mode fires ~60-80% of the time (heavy project work), full-vault mode fires ~20-40% (briefs, cross-project synthesis)
- Reports any anomalies (e.g., project-focus mode firing 100% of time → active_project never cleared, scope too aggressive)

**Manual test (Step 6 above):** set `active_project: FB-Engine`, run the skill, verify state file. Repeat for one other project to confirm branching works.

## Stop condition

The spec itself is DONE when the 8 Goal conditions are met. The skill itself is OPEN-LOOP (it runs on every cold-start indefinitely).

**Halt conditions for the context-loader skill:**
- `active_project` is set but the project directory doesn't exist → HALT, surface "active_project points to missing directory, falling back to full-vault mode"
- State file write fails → HALT, surface (the audit trail is the value)
- Cross-project bypass attempted but vault is unreachable → HALT, surface

**Halt conditions for the spec overall:**
- Andre reverses the upgrade direction
- End-of-week verification shows scope too aggressive (>90% project-focus, missing cross-project moments)
- Token cost reduction <10% in practice (not worth the complexity)

## Reversibility

Fully reversible in <5 minutes. The 5 changes are:
1. Remove `active_project` + `active_project_set_at` from MAVIS.md frontmatter
2. Delete `~/.mavis/agents/mavis/skills/context-loader/` directory
3. Delete `99 _system/skills/context-loader/` mirror
4. Restore MEMORY.md session-start checklist to ad-hoc discovery
5. Remove the "Context Loader" entry from MEMORY.md

No data at risk. No folder moves. No external dependencies to disconnect.

## Related surfaces

- `~/MiniMax-Agent/02 Notes/decisions/2026-06-22-two-track-model.md` — the operating model this upgrade extends
- `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md` — companion spec (the second-self crons explicitly bypass the context scope)
- `~/.mavis/agents/mavis/skills/ea-daily-brief/SKILL.md` — the existing daily-brief skill that benefits from scoped context
- `~/MiniMax-Agent/MAVIS.md` — gains the active_project field
- `~/.mavis/agents/mavis/memory/MEMORY.md` — session-start checklist gets the context-loader reference

## Open questions for Andre

1. **Should `active_project` be a single-value field or a list?** **DECIDED (Andre, 2026-06-22 21:10 CT):** Single value. One active project per session. Simpler state, clearer mental model, matches Karpathy's pattern.
2. **Auto-set vs manual-set?** **DECIDED (Andre, 2026-06-22 21:10 CT):** Explicit only. Andre says "let's work on X" or "switch to X" → Mavis sets the field. No surprise context shifts. The `active-project-suggester` is deferred to a future upgrade if needed.
3. **State file retention?** **DECIDED (Andre, 2026-06-22 21:10 CT):** Keep forever. Each file is ~1KB, trivial cost, audit trail preserved indefinitely. No weekly trash cron.

## Status

Spec locked. Awaiting explicit "go" from Andre to begin implementation per the two-track model's spec-track discipline.
