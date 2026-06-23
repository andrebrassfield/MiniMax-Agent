---
name: mavis-cold-start
description: |
  The canonical startup sequence for Mavis in a fresh context window. **Load this skill FIRST on every fresh session** — before any other work, before reading any project files, before responding to anything.

  This skill orients Mavis to:
  - Who she is (identity + operating contract)
  - The memory architecture (what's always-on, what's on-demand, what's in the vault)
  - The current state (active project, active theses, recent vault activity)
  - Where things live (pointers to skills, crons, topic files, decisions)
  - The conventions (vault = long-term, MEMORY.md = pointers, two-track model)

  After running this skill, Mavis knows everything she needs to operate correctly in this vault. Without it, she's guessing.

  Triggers: "start up", "cold start", "fresh session", "orient me", "what's going on", "where do I start", "I'm new here" (in any session that hasn't yet run this skill).

  Do NOT load for: sessions that have already completed this skill in the current context (the context-loaded state file marks completion). Do NOT load for: in-session file reads where context is already established.
---

# mavis-cold-start

The canonical startup sequence. Run this on every fresh context window before doing any other work.

## Why This Exists

Mavis operates across many sessions. Each fresh session has zero chat history — the previous conversation is gone. Without a structured startup, Mavis reads whatever is auto-injected (SOUL.md, MAVIS.md, MEMORY.md tail) and improvises. The improvisation often misses:
- The active project focus
- The active theses (positions checked against new information)
- Where the long-term knowledge lives (vault vs agent memory vs auto-injected)
- The conventions (memory architecture, two-track model, etc.)

This skill makes startup reproducible. Every fresh session gets the same orientation, the same context-loading, the same audit trail.

## The 7-Step Procedure

### Step 1 — Read identity layer (always-read)

```bash
# Read in order
1. ~/MiniMax-Agent/SOUL.md     # operating contract, identity, autonomy table
2. ~/MiniMax-Agent/MAVIS.md    # current state, active_project, active theses
3. ~/.mavis/agents/mavis/memory/MEMORY.md  # operational essentials + pointers
```

If any fails to read, **HALT and surface** to Andre. The identity layer is non-negotiable.

**What to extract:**
- From SOUL.md: operating contract, hard constraints, tone
- From MAVIS.md: `active_project` field, active theses, open questions
- From MEMORY.md: pointers to skills, crons, topic files

### Step 2 — Read long-term knowledge (per pointers in MEMORY.md)

Don't dump the full vault. Load on demand based on what step 1 told you:

- **Always load:** the 4 Active Theses (full versions at `~/MiniMax-Agent/01-PERMANENT/2026-06-22 - active-theses.md`) — these are checked against every new piece of information
- **Load if MAVIS.md mentions an active project:** that project's `00 Overview.md` (if it exists), recent decisions, recent specs
- **Load if working on a specific skill/cron:** that skill/cron file directly
- **Don't load speculatively.** Each loaded file adds context cost.

### Step 3 — Run `context-loader` skill

The canonical cold-start procedure at `~/.mavis/agents/mavis/skills/context-loader/SKILL.md`.

It does the actual scoping:
- Reads SOUL.md + MAVIS.md (always)
- Checks `active_project` field
- If set: reads only that project's context (skips the rest of the vault)
- If null: full-vault mode (reads everything per the standard cold-start)
- Writes a state file at `~/.mavis/state/context-loaded-YYYY-MM-DD-HHMM.md` (audit trail)

**Why run context-loader separately instead of inlining:** it's the load-bearing scoping logic. Reuse it. Don't reinvent.

### Step 4 — What's fresh since last session?

Quick scan to see what's new:

```bash
# Files modified in last 48 hours (rough freshness signal)
find ~/MiniMax-Agent -name "*.md" -type f -mtime -2 \
  -not -path "*/node_modules/*" \
  -not -path "*/.obsidian/*" \
  -not -path "*/.git/*" \
  -not -path "*/99 _system/*" 2>/dev/null | head -20

# State files showing recent cron activity
ls -t ~/.mavis/state/ 2>/dev/null | head -10
```

**Don't read every file** — just note what's been touched. If something looks load-bearing for the active project, fetch it.

### Step 5 — Verify state file integrity

```bash
# Check that the most recent context-loaded state file exists and is valid
LATEST=$(ls -t ~/.mavis/state/context-loaded-*.md 2>/dev/null | head -1)
if [ -n "$LATEST" ]; then
  echo "Last cold start: $LATEST"
  head -20 "$LATEST"
else
  echo "No previous cold-start state — this is a true fresh session"
fi
```

### Step 6 — Acknowledge readiness (don't dump, orient)

Output a tight orientation block (~10-20 lines) to Andre:

```markdown
# Mavis Cold Start — <ISO timestamp>

**Mode:** <project-focus | full-vault>
**Active project:** <name | null>
**Loaded:** <count of files read>

## Active theses I'm holding
1. <thesis 1 — short form>
2. <thesis 2 — short form>
3. <thesis 3 — short form>
4. <thesis 4 — short form>

## Recent activity
- <N> vault files modified in last 48h
- <list of recent state files>

## What's loaded
- SOUL.md (<bytes>)
- MAVIS.md (<bytes>)
- MEMORY.md (<bytes>)
- <if project-focus: project files>

## What's NOT loaded (skipped intentionally)
- <list of skipped surfaces>

## Ready
What are we working on?
```

This block:
- Verifies the architecture is working (every section maps to a known file)
- Gives Andre a quick state-of-mind check ("did Mavis load the right context?")
- Closes with the question that matters: "what are we doing?"

### Step 7 — Audit trail

The context-loader skill (called in Step 3) writes the state file. This step is implicit — verify it exists:

```bash
ls -la ~/.mavis/state/context-loaded-*.md | tail -3
```

If missing: context-loader didn't run correctly. Re-run it or surface the error.

## Hard Constraints

1. **Run this skill FIRST.** Before any project work, before any "what's open" question, before any response that touches vault state.
2. **Don't skip steps.** Each step has a reason. Step 1 = identity. Step 2 = knowledge. Step 3 = scoping. Step 4 = freshness. Step 5 = integrity. Step 6 = acknowledgment. Step 7 = audit.
3. **Always emit the orientation block (Step 6).** Even if Andre says "just answer my question" — answer the question AND emit the orientation. The block is small (~10-20 lines) and verifiable.
4. **If MAVIS.md's `active_project` is set: scope to that project.** Don't drift into other projects' context. The user can pivot explicitly via "switch to X".
5. **If `~/.mavis/state/context-loaded-*.md` is stale (>24h old): treat this as a fresh session.** The architecture assumes state files are recent.
6. **ABSOLUTE SEPARATION rule applies.** Never read/write `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/`.

## Memory Architecture (the rule that makes this work)

The vault IS my long-term memory. MEMORY.md is operational pointers only.

- **Always-on (auto-injected):** SOUL.md + MAVIS.md + MEMORY.md (~30KB total, slim by design)
- **On-demand (loaded by skill or by topic reference):** `~/.mavis/agents/mavis/memory/*.md` topic files (~200KB total)
- **Long-term (the deep knowledge):** `~/MiniMax-Agent/` vault (growing)
- **Skills (procedures):** `~/.mavis/agents/mavis/skills/<name>/SKILL.md` + vault mirror
- **Crons (scheduled procedures):** `~/.mavis/agents/mavis/crons/<name>.md` + vault mirror

When learning something new with long-term value: vault first, MEMORY.md gets only a pointer.

## Conventions to Apply Throughout the Session

1. **Spec on disk before Track 2 spawn.** Source: `02 Notes/decisions/2026-06-22-two-track-model.md`.
2. **Two-track model:** Track 1 = spec (this session). Track 2 = implementation (different session_id). One Track 2 per spec.
3. **Subagent channel is verifier-only.** Producer work → skill it, do it in Track 1, or spawn Track 2.
4. **Rate-limit budget allocated, not consumed freely.** 50/25/5/20 (Track 1 / Track 2 / Verifier / Cron). Tracked.
5. **Active theses checked.** Every new piece of information — does it support, complicate, or contradict any of the 4 theses?
6. **Vault = long-term. MEMORY.md = pointers.** Don't dump knowledge into MEMORY.md.
7. **Push back when it earns pushback.** Disagree with evidence. Don't flatter.

## Pointers (long-term knowledge lives here)

**Operating models (vault-side topic files):**
- Two-Track Operating Model: `~/MiniMax-Agent/03 Projects/Mavis EA Design/memory/two-track-model.md`
- Second-Self Automation: `~/MiniMax-Agent/03 Projects/Mavis EA Design/memory/second-self-automation.md`

**Active Theses (full versions):**
- `~/MiniMax-Agent/01-PERMANENT/2026-06-22 - active-theses.md`

**Skills (canonical at `~/.mavis/agents/mavis/skills/`):**
- `context-loader/SKILL.md` — Karpathy-pattern project scoping
- `mavis-cold-start/SKILL.md` — this skill
- `two-track-handoff/SKILL.md` — spec → Track 2 spawn procedure
- `two-link-rule/SKILL.md` — soft enforcement of connection discipline
- `obsidian-local-rest-api-wiring/SKILL.md` — credential storage pattern

**Crons (canonical at `~/.mavis/agents/mavis/crons/`):**
- `second-self-morning-brief.md` (06:00 CT daily)
- `inbox-filer.md` (06:30 CT daily)
- `second-self-contradiction.md` (07:00 CT daily)
- `second-self-nightly-connections.md` (23:00 CT daily)
- `second-self-weekly-deep.md` (Sun 19:00 CT)
- `vault-health.md` (1st Sun 23:00 CT)
- `rate-limit-tracker.md` (22:00 CT daily)

**Topic files (load on demand at `~/.mavis/agents/mavis/memory/`):**
- `orphan-disciplines.md` — 5 disciplines from retired agent
- `calendar-mcp.md` — calendar MCP operational reference

**Decision log:** `~/MiniMax-Agent/02 Notes/decisions/`
**Specs:** `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/`

## Halt Conditions

- SOUL.md or MAVIS.md fails to read → HALT, surface
- `context-loader` skill fails or errors → HALT, surface (don't proceed without scoping)
- Identity layer has changed unexpectedly (e.g., new active theses that contradict the spec) → HALT, surface
- Vault not mounted / unreadable → HALT, surface

## Failure Modes

| Failure | Detection | Recovery |
|---|---|---|
| MAVIS.md `active_project` set but project dir missing | `ls` fails | Fall back to full-vault mode, log override |
| State file corrupted | Read fails | Re-run context-loader, write fresh state |
| Vault too large to scan | Files >10000 | Trust pointers, load on demand only |
| Active theses contradict vault | Visual scan in Step 1 | HALT, surface to Andre |

## Cross-references

- This skill supersedes ad-hoc cold-start procedures. If you find yourself doing cold-start work outside this skill, you're doing it wrong.
- The `context-loader` skill (called in Step 3) is the canonical scoping procedure.
- The article this skill is based on: Obsidian Masterclass (2026-06-22) — Part 12 "Six Core Claude Prompts" (the "Vault Audit" prompt, adapted for fresh-session startup).
- The architecture this skill operates in: locked 2026-06-22 (Two-Track + Second-Self + Memory Architecture pivots).
