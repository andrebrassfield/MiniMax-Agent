---
type: spec
feature: minimax-token-dialin
status: approved
created: 2026-06-22T22:30:00-05:00
owner: Mavis (Track 1)
track: Track 1 (interactive, this session)
ledger: 03 Projects/Mavis EA Design/minimax-token-dialin-ledger-2026-06-22.md
related: 02 Notes/decisions/2026-06-22-two-track-model.md
articles: [sairahul1-thin-harness-fat-skills, tiago-forte-two-tracks]
---

# Spec — MiniMax Token Plan Dial-In

## Goal

Cut Mavis's always-on context per session by ~50%, fix the broken rate-limit-tracker, sharpen resolver routing, and codify `ea-state-audit` as a reusable skill. **Done condition:** all 6 dial-ins complete + `mavis usage` measurement taken + ledger closed.

**Target metrics (after):**
- MAVIS.md ≤ 10KB (currently 32.4KB)
- SOUL.md ≤ 12KB (currently 19.8KB)
- MEMORY.md ≤ 5KB (currently 4.4KB — already in target)
- Always-on context total ≤ 27KB (currently 56.4KB)
- `mavis usage` shows lower per-turn average over 7-day window post-dial-in
- `rate-limit-tracker` cron registered + nightly log files produced

## Context

**Framework (two-track + thin-harness-fat-skills):**
- Mavis's bottleneck is spec throughput, not implementation. Adding agents multiplies the wrong variable. Source: `02 Notes/decisions/2026-06-22-two-track-model.md`.
- Skills beat agents when the work is non-trivial and the harness is mature. Codify-after-3-runs discipline applies. Source: topic `agent-harness-principles.md` + user memory (Garry Tan rule).
- Long-term knowledge in the vault, not always-on. MEMORY.md = pointers. Source: Obsidian Masterclass article.

**Audit findings (2026-06-22 22:19 CT, before dial-in):**
- Mavis = 90.8% of all-time token spend ($984.72 / $1,084.81)
- 41,347 turns lifetime; high-cost days ($126, $141) correlated with cache:input ratios <1x — meaning every turn paid full price for bloated always-on context
- 56.4KB always-on context vs article target ~10KB (5.6x over)
- `rate-limit-tracker` cron spec exists at `~/.mavis/agents/mavis/crons/rate-limit-tracker.md` but: (a) references `mmx quota` CLI that doesn't exist; (b) not registered in daemon (`mavis cron list mavis` shows 40 crons, no rate-limit-tracker)
- 38 skills with description field averaging 200-400 chars — too verbose for tight resolver matching
- No on-disk resolver table

## Architecture

**Always-on context layers (post-dial-in):**
```
┌─────────────────────────────────────────────────┐
│ SOUL.md (≤12KB)        ← operating contract     │
│ MAVIS.md (≤10KB)       ← current state, pointers│
│ MEMORY.md (≤5KB)       ← operational pointers   │
│ Total: ≤27KB                                 │
└─────────────────────────────────────────────────┘
         ↓ resolver (description-matched skills)
┌─────────────────────────────────────────────────┐
│ Skills (38+ markdown procedures, loaded on demand)│
│ Topic files (loaded on demand)                   │
│ Vault notes (loaded on demand)                   │
└─────────────────────────────────────────────────┘
```

**Resolver routing (post-dial-in):**
```
User signal → match against skill description field
            → invoke skill if confidence > threshold
            → skill loads topic files + vault notes on demand
            → returns judgment, not raw data
```

**Token budget tracker (post-dial-in):**
```
22:00 CT daily cron → mavis usage list --json (deterministic)
                    → categorize by track (T1 / T2 / verifier / cron)
                    → append to ~/.mavis/state/rate-limit-YYYY-MM-DD.md
                    → mirror to 99 _system/state/
                    → weekly rollup Sunday
```

## Action — 6 dial-ins

### Dial-in #1 — Fix rate-limit-tracker (15 min)

**Files:**
- `~/.mavis/agents/mavis/crons/rate-limit-tracker.md` (spec edit)
- Register cron via `mavis cron create`

**Edits:**
- Replace `mmx quota --format json` with `mavis usage list --json`
- Replace `mavis session list --since today --track 1` with `mavis usage list --group agent --json` + filter
- Verify cron file lints cleanly

**Acceptance:**
- Cron registered, status=enabled, lastRun=success within 24h
- First log file at `~/.mavis/state/rate-limit-2026-06-22.md`

### Dial-in #2 — Trim MAVIS.md to ≤10KB (30 min)

**Files:**
- Source: `~/MiniMax-Agent/MAVIS.md`
- Extract: `~/MiniMax-Agent/03 Projects/Mavis EA Design/active-skill-mutations.md`
- Extract: `~/MiniMax-Agent/03 Projects/Cognitive-Parameter-Graph/dashboard-2026-06-22.md`
- Update MEMORY.md pointer to extracted files

**Edits:**
- Remove `## Active Skill Mutations` section body → cross-link to extracted file
- Remove `## Phase 3 Dashboard` section body → cross-link to extracted file
- Keep: frontmatter + Who Mavis is + Active Theses (1-line each) + Hard Constraints + Vault Structure (1-line)
- Result: MAVIS.md goes from 32.4KB → ~10KB

**Acceptance:**
- MAVIS.md ≤ 10KB
- All 4 active theses still cross-linkable
- All hard constraints preserved
- No lost references in extracted files

### Dial-in #3 — Trim SOUL.md to ≤12KB (30 min)

**Files:**
- Source: `~/MiniMax-Agent/SOUL.md`

**Edits:**
- Keep: Identity + Stance + Memory Architecture + Accountability + Pushback + Autonomy Boundary Table + Two-Track Operating Model + Operating Mode + Delegation Rules + Standards + Lookup Protocol + Escalation + End State
- Trim: history/why-built paragraphs (move to vault where load-bearing), verbose examples, redundant explanations
- Result: SOUL.md goes from 19.8KB → ~12KB

**Acceptance:**
- SOUL.md ≤ 12KB
- All hard constraints preserved verbatim (these are the load-bearing parts)
- No loss of operating contract semantics

### Dial-in #4 — Write resolvers.md (20 min)

**Files:**
- New: `~/.mavis/agents/mavis/memory/resolvers.md`

**Content:**
- Explicit "when Andre signals X, load skill Y first" table
- Covers top 20 trigger patterns: cold-start, switch-to-X, write-a-decision, log-a-commitment, audit-X-vs-Y, codify-as-skill, etc.
- Add pointer to MEMORY.md
- Hard rule: when in doubt, fail open to context-loader (default project-focus or full-vault per MAVIS.md field)

**Acceptance:**
- File exists with ≥15 explicit resolver entries
- Pointer in MEMORY.md updated

### Dial-in #5 — Tighten 38 skill descriptions (45 min)

**Files:**
- All `~/.mavis/agents/mavis/skills/*/SKILL.md` files

**Edits:**
- Description field ≤ 200 chars (current avg ~280)
- Single sentence when possible
- Explicit parameter names in description where applicable ("takes TARGET, QUESTION, DATASET")
- No paragraph-long descriptions

**Acceptance:**
- All 38 skills have description ≤ 200 chars
- All YAML frontmatter still valid
- Resolver matching still works (spot-check 5 random skills)

### Dial-in #6 — Codify ea-state-audit skill (30 min)

**Files:**
- New: `~/.mavis/agents/mavis/skills/ea-state-audit/SKILL.md`
- Mirror: `~/MiniMax-Agent/99 _system/skills/ea-state-audit/SKILL.md`

**Pattern (used 3+ times today):** "Audit current Mavis state vs framework X, surface gaps in priority order, propose dial-ins."

**Parameters:**
- `FRAMEWORK` — e.g., "thin-harness-fat-skills", "two-track", "garry-tan-discipline"
- `SURFACE` — e.g., "always-on-context", "skills", "crons", "memory"
- `OUTPUT` — default to `00 Inbox/state-audit-YYYY-MM-DD.md`

**Acceptance:**
- Skill file follows standard SKILL.md format with YAML frontmatter (name, description)
- Mirror file at `99 _system/skills/` exists and is byte-identical
- Pattern document: 5-step procedure (1. read surface, 2. read framework, 3. enumerate gaps, 4. prioritize, 5. propose dial-ins)

## Feedback — verification gates

**Per dial-in:** verify acceptance criteria before marking ledger entry "done"

**Aggregate verification (after all 6 complete):**
- `wc -c` on SOUL.md / MAVIS.md / MEMORY.md → confirm size targets
- `mavis usage list --json --from <7d-ago>` → snapshot baseline
- `mavis cron list mavis | grep rate-limit-tracker` → confirm registered
- `ls ~/.mavis/agents/mavis/skills/ea-state-audit/SKILL.md` → confirm new skill exists
- Grep `~/.mavis/agents/mavis/skills/*/SKILL.md` description fields → confirm ≤200 chars
- Smoke test: invoke new `ea-state-audit` skill against a fresh framework → produces valid output
- No regression: 40 crons still registered, all enabled

**Spec block review gate:** before any **yellow** or **red** action in this spec, pause and surface. Most edits are green (reversible vault writes). The cron registration is yellow (persistent scheduled task) — report after, don't pre-ask.

## Stop condition

The dial-in loop is done when:
1. All 6 ledger entries marked "done"
2. MAVIS.md ≤ 10KB AND SOUL.md ≤ 12KB verified by `wc -c`
3. `rate-limit-tracker` cron registered and first log file exists
4. `ea-state-audit` skill loadable and smoke-tested
5. Spec archived to `03 Projects/Mavis EA Design/specs/done/minimax-token-dialin-2026-06-22.md`
6. Final token measurement (post-dial-in 7-day window) captured in `00 Inbox/dialin-measurement-2026-07-01.md`

**Halt conditions:**
- Any dial-in breaks a cron → HALT, surface to Andre
- MAVIS.md trim loses a load-bearing reference → HALT, restore from git
- `ea-state-audit` skill smoke test fails → HALT, surface, refactor skill
- Token spend on dial-in work > 500K tokens → HALT, surface (target was <100K)

## Cross-references

- Decision: `02 Notes/decisions/2026-06-22-two-track-model.md`
- Active theses: `01-PERMANENT/2026-06-22 - active-theses.md`
- Topic: `~/.mavis/agents/mavis/memory/agent-harness-principles.md`
- Articles:
  - "Thin Harness, Fat Skills" (sairahul1 / Steve Yegge reference)
  - "You don't need ten agents. You need two tracks." (Tiago Forte)
- User memory: Garry Tan codify-after-3-runs discipline
