---
name: context-loader
description: |
  Cold-start context loader with Karpathy-pattern project scoping. When Mavis boots cold (session start, session rotation, or post-pivot), this skill decides whether to load the full vault or scope to a single active project. Writes an auditable state file at `~/.mavis/state/context-loaded-YYYY-MM-DD-HHMM.md` on every invocation.

  Triggers: automatically on cold-start (per the MEMORY.md session-start checklist), or explicitly on "set active project to X" / "switch to X" / "clear active project" / "back to inbox" / "what's open" / "load context".

  Do NOT load for: mid-session file reads (just Read directly), explicit "load everything" requests (use the standard ad-hoc procedure instead), second-self cron invocations (they explicitly bypass scope per Step 4).
---

# context-loader

The canonical cold-start procedure. Replaces ad-hoc discovery with a structured 5-step load + an auditable state file. Karpathy's "open one project at a time" pattern adapted for our flat vault + 03 Projects/ subdir structure.

## Intent

When Mavis boots or pivots, decide what context to load. Scope to one project when Andre is in project-focus mode (faster cold-start, sharper focus, lower token cost). Load the full vault for cross-project moments (briefs, synthesis, weekly deep). Audit every invocation via a state file.

## When to run

**Triggers:**
- Cold start (every session — invoked automatically by the MEMORY.md session-start checklist step 3)
- "set active project to X" / "switch to X" / "let's work on X" — explicit set + load
- "clear active project" / "back to inbox" / "what's open" — explicit clear + load
- Session rotation (when Mavis detects it's a new session)
- Mid-session pivot (Andre signals a topic change)

**Do NOT run for:**
- Mid-session file reads (just Read directly)
- Explicit "load everything" / "search the whole vault" requests (use the standard ad-hoc procedure)
- Second-self cron invocations (morning brief, contradiction, weekly deep — they bypass scope by design, see Step 4)
- Already-loaded state file exists for current session within last hour (verify, don't re-load)

## The 5-step procedure

### Step 1 — Always-read identity layer

Read in order:
1. `~/MiniMax-Agent/SOUL.md` — the operating contract (always)
2. `~/MiniMax-Agent/MAVIS.md` — current state (always — includes `active_project` field)

If either fails to read, HALT and surface.

### Step 2 — Check `active_project`

Read the `active_project` field from MAVIS.md YAML frontmatter.

- If `active_project: null` (or missing/empty) → MODE = full-vault
- If `active_project: <name>` → MODE = project-focus (active_project = `<name>`)

### Step 3 — Branch on mode

**MODE = full-vault** (active_project is null):
- Continue with the standard cold-start: MEMORY.md (auto-injected), topic files on demand, ad-hoc discovery as needed
- Skip the project-scoping block (don't read project-specific files)
- Still write the state file (Step 5) with mode = full-vault

**MODE = project-focus** (active_project is set):
- Verify the project directory exists: `ls ~/MiniMax-Agent/03\ Projects/<active_project>/`
  - If missing → HALT, surface "active_project '<name>' directory does not exist, falling back to full-vault mode" + log to state file as an override
- Read the project root .md file:
  - First check `~/MiniMax-Agent/03 Projects/<active_project>/00 Overview.md`
  - If missing, read the most-recently-touched .md in that project's root
  - If still no candidate (project is empty), HALT — surface "active_project '<name>' has no readable content, falling back"
- Read the project's recent decisions: `~/MiniMax-Agent/03 Projects/<active_project>/decisions/` — last 14 days by mtime
  - If no decisions/ subdir exists, skip silently (most projects don't have one yet)
- Read the project's recent specs: `~/MiniMax-Agent/03 Projects/<active_project>/specs/` — last 14 days by mtime
  - If no specs/ subdir exists, skip silently
- **Skip the rest of the vault** (other projects, 02 Notes/, 06 Connections/, 07 Vellum/)

### Step 4 — Cross-project bypass check

Before writing the state file, check: is this invocation from a second-self cron or explicit "load everything" request?

If yes:
- Override mode = full-vault (regardless of `active_project` field)
- Load the full vault per the standard cold-start
- Note the override in the state file's "Cross-project bypass check" section

Detection — current session is one of these crons (per session_id or call context):
- `second-self-morning-brief` (06:00 CT daily)
- `second-self-contradiction` (07:00 CT daily)
- `second-self-weekly-deep` (Sunday 19:00 CT)
- Any future cron with "second-self" or "cross-project" or "synthesis" in the name
- Explicit Andre request: "load everything" / "full vault" / "synthesis mode"

**Why the bypass:** the second-self crons are designed to surface cross-project connections (per the article: "What does this collection of thinking, when read as a whole, reveal"). Scoping them to one project defeats their purpose. They always see the full vault.

### Step 5 — Write state file (mandatory)

Write to `~/.mavis/state/context-loaded-YYYY-MM-DD-HHMM.md`:

```markdown
---
loaded_at: <ISO-timestamp>
mode: project-focus | full-vault
active_project: <name> | null
session_id: <session-id>  # if known
trigger: cold-start | set | clear | pivot | cron-bypass
---

# Context Loaded

**Mode:** <mode>
**Active project:** <name | null>
**Loaded at:** <ISO>
**Trigger:** <what caused this load>

## Loaded
- SOUL.md (<bytes>)
- MAVIS.md (<bytes>)
<if project-focus, list each project file read with byte count>
- 03 Projects/<name>/00 Overview.md (<bytes>)
- <N> decisions from 03 Projects/<name>/decisions/ — total <bytes>
- <N> specs from 03 Projects/<name>/specs/ — total <bytes>

## Skipped (intentionally, mode = project-focus)
- 02 Notes/ — skipped (out of project scope)
- 06 Connections/ — skipped (cross-project synthesis layer, separate)
- 03 Projects/<other projects>/ — skipped (not in focus)
- 07 Vellum/ — skipped (out of project scope)

## Cross-project bypass check
- Second-self cron firing? — no / yes (<cron name>)
- If yes, switched to full-vault mode for this invocation

## Cold-start time
- Started: <ISO>
- Completed: <ISO>
- Total: <seconds>
```

The state file IS the audit trail. Future-Mavis can verify what was loaded by reading the most recent state file. Per Andre's decision 2026-06-22 21:10 CT: **state files kept forever** (each ~1KB, trivial cost).

## Explicit set/clear operations

When Andre says "let's work on X" / "switch to X" / "set active project to X":
1. Edit `MAVIS.md` YAML frontmatter: `active_project: X` + `active_project_set_at: <ISO-now>`
2. Run this skill (mode will switch to project-focus on this invocation)
3. Write the state file with `trigger: set`

When Andre says "clear active project" / "back to inbox" / "what's open":
1. Edit `MAVIS.md` YAML frontmatter: `active_project: null` + `active_project_set_at: null`
2. Run this skill (mode will switch to full-vault on this invocation)
3. Write the state file with `trigger: clear`

When Andre says "switch to Y" while active_project was X:
1. Treat as clear-then-set: clear X, set Y
2. Run the skill (mode = project-focus with Y)
3. Write the state file with `trigger: pivot`

## Hard constraints

1. **Spec on disk before any set/clear.** If Andre asks to set active_project to a project that has no `00 Overview.md` and no readable root .md, surface this BEFORE setting the field. Don't point Mavis at an empty project.
2. **Cross-project bypass is automatic and mandatory.** Second-self crons NEVER scope. They always see the full vault.
3. **State file is mandatory.** Every invocation writes the state file. If the write fails, HALT and surface.
4. **No folder moves.** The skill only READS files. It never moves, renames, or creates.
5. **Mavis territory only.** All paths are `~/MiniMax-Agent/` and `~/.mavis/`. No cross-team reads.
6. **Append-only audit trail.** State files are written, never edited or deleted (per Andre's keep-forever decision). Old state files stay on disk for long-term audit.

## Halt conditions

- `active_project` is set but the project directory doesn't exist → HALT, surface, fall back to full-vault mode (logged in state file)
- Project has no readable content (no `00 Overview.md`, no recent .md) → HALT, surface, fall back to full-vault mode
- State file write fails → HALT, surface (the audit trail is the value)
- Cross-project bypass attempted but vault is unreachable → HALT, surface
- SOUL.md or MAVIS.md fails to read → HALT, surface (these are always required)

## Rollback (full revert in <5 minutes)

To remove the Context Loader entirely:

1. Remove the `active_project` + `active_project_set_at` fields from `MAVIS.md` YAML frontmatter
2. Delete `~/.mavis/agents/mavis/skills/context-loader/` directory
3. Delete `99 _system/skills/context-loader/` vault mirror
4. Restore `MEMORY.md` session-start checklist to the original 5 ad-hoc steps
5. Remove the "Context Loader (2026-06-22)" entry from `MEMORY.md`
6. Remove the usage note from `SOUL.md` Two-Track Operating Model section
7. (Optional) Delete `~/.mavis/state/context-loaded-*.md` files — they're the audit trail, no data loss if deleted

No data at risk. No external dependencies to disconnect. No folder moves.

## Cross-references

- Spec: `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/context-loader-2026-06-22.md` (the formal artifact)
- Decision: `~/MiniMax-Agent/02 Notes/decisions/2026-06-22-two-track-model.md` (the operating model this skill extends)
- Companion spec: `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md` (the second-self crons explicitly bypass scope per Step 4)
- Operating contract: `~/MiniMax-Agent/SOUL.md`
- Active state: `~/MiniMax-Agent/MAVIS.md` (the `active_project` field lives in YAML frontmatter)
- Source article: "How to Build an AI Second Brain With Claude and Obsidian That Gets Smarter Every Day" (Andre shared 2026-06-22, inspired by Karpathy's LLM Wiki pattern April 2026)
