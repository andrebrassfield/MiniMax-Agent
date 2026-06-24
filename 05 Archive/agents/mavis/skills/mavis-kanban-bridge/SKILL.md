---
name: mavis-kanban-bridge
description: |
  The Mavis-side bridge to the file-based Kanban at
  `~/Documents/Obsidian/MainVault/Kanban/`.
---

---

# mavis-kanban-bridge

The Mavis-side read/write/validate/move surface for the file-based Kanban
that closed the durable-task gap on 2026-06-21. The Kanban lives at:

```
~/Documents/Obsidian/MainVault/Kanban/
  README.md
  SCHEMA.md                     ← authoritative card spec (7 validation rules)
  templates/card.md             ← starter for new cards
  cards/
    active/                     ← open | in_progress | blocked
    done/                       ← terminal: done (never delete)
    dropped/                    ← terminal: dropped (never delete)
```

**Card = one `.md` file. Status = directory. Move on terminal — never
delete. The audit trail is the value.**

## When to run

**Triggers:**
- "I want this to actually happen even when I'm not in chat"
- Any directive that needs to survive the current context turn
- Any multi-step task (≥3 steps, or steps that cross sessions)
- Cold start of Mavis: pull `cards/active/` and surface open cards
- A card Mavis owns hits terminal status (move it)
- A directive arrives that's a duplicate of an existing card (link, don't recreate)

**Do NOT run for:**
- One-line chat replies ("ok", "got it", "yes")
- In-session task tracking that finishes in the same turn
- Hermetic, single-shot operations ("find me X", "fix this typo")
- Hermes's kanban (separate system — see `cross-team-discipline.md`)
- Other agents' task stores (Mavis territory only)

## The 5 operations (load-bearing)

All 5 operations go through `scripts/kanban.sh` (the only file in the
skill that mutates state). Read `references/operations.md` for the
full command surface and edge-case handling.

### Op 1 — `read` (cold start, kanban pull, claim scan)

```bash
./scripts/kanban.sh read [--owner <profile>] [--status <status>]
```

Returns all cards in `cards/active/` matching the filter. Default
owner is the calling profile (read from `~/.mavis/agents/mavis/.env`
or `$MAVIS_PROFILE` env var); default status is `open`.

**Use case:** cold start. Mavis boots, pulls active cards, surfaces
"open + assigned to mavis" to the daily brief.

### Op 2 — `new` (write a new card from a directive)

```bash
./scripts/kanban.sh new \
  --title "<verb-first, one line, max 80 chars>" \
  --owner <profile> \
  --priority <high|med|low> \
  --next-action "<concrete next step>" \
  [--description "<2-4 lines>"] \
  [--acceptance "<done criteria>"] \
  [--depends-on <kanban-id>]
```

Generates the next `kanban-YYYY-MM-DD-NNN` id, copies the template,
fills frontmatter, writes to `cards/active/`, appends a `## Log`
entry with timestamp + actor.

**Use case:** directive arrives. Mavis turns it into a durable card
so the next cold start can pick it up.

### Op 3 — `transition` (change status, validate frontmatter)

```bash
./scripts/kanban.sh transition <kanban-id> \
  --to <open|in_progress|blocked|done|dropped> \
  [--next-action "<new next action>"] \
  [--blocked-by <kanban-id>]
```

Validates the new state against the 7 SCHEMA rules (id format, enum
values, owner existence, ISO dates, `next_action` non-empty when
`in_progress`, `blocked_by` references a real card when `blocked`).
On pass: updates frontmatter, appends a `## Log` entry. On fail: HALT
with a one-line error pointing at the failing rule.

**Use case:** claim on cold start (`open → in_progress`); complete a
task (`in_progress → done`); realize a dep isn't ready
(`in_progress → blocked`).

### Op 4 — `move` (terminal status → directory move)

```bash
./scripts/kanban.sh move <kanban-id> --to <done|dropped>
```

Reads the card, asserts status matches target dir (`done` or
`dropped`), updates frontmatter `updated` field, appends a final
`## Log` entry, then `mv cards/active/<id>.md cards/<target>/<id>.md`.

**Idempotent guard:** if the card is already in the target dir, exit
0 with no-op. If the card is in `done/` or `dropped/`, exit 1
(terminal cards don't move).

**Use case:** Mavis-owned card finishes or is cancelled. Move it
out of `active/` so the cold-start scan doesn't keep surfacing it.

### Op 5 — `validate` (sanity check, used by cron + manual)

```bash
./scripts/kanban.sh validate [<kanban-id>]
```

Runs all 7 SCHEMA rules against the card (or every card in
`cards/active/` if no id given). Exits 0 on pass, exits 1 with a
per-card error list on fail. Idempotent — safe to run on a cron.

**Use case:** nightly integrity check; pre-claim sanity; debugging
"why is the bridge failing."

## The 7 SCHEMA rules (encoded in `scripts/kanban.sh validate`)

From `Kanban/SCHEMA.md` — the bridge MUST enforce these, no exceptions:

1. `id` must match `^kanban-\d{4}-\d{2}-\d{2}-\d{3}$`
2. `status` must be one of `open | in_progress | blocked | done | dropped`
3. `owner` must match an existing profile name (in `~/.hermes/profiles/`)
   or `human:andre`
4. `priority` must be `high | med | low`
5. `created` and `updated` must be valid ISO dates (`YYYY-MM-DD`)
6. `next_action` must be non-empty when `status: in_progress`
7. When `status: blocked`, `blocked_by` must reference an existing card
   in `cards/active/` or `cards/done/`

## Writing rules (carry-overs from Kanban/README.md)

- Every status change appends to `## Log` (chronological is fine).
- `id` is unique and immutable. Renames go in `## Log`, not in `id`.
- `next_action` is updated every time `status` changes.
- Files move on terminal status. **Never delete.**
- All `## Log` entries use 24-hour format: `YYYY-MM-DD HH:MM — <action>`.

## What the skill does NOT do (and who does)

| Concern | Owner |
|---|---|
| Stall detection (24h+ no log on `in_progress`) | Deferred cron — wait for ≥3 movement patterns |
| Routing decision (which profile picks up a card) | Mavis (spec block) or `pi` (Telegram router once gateway is installed) |
| Cross-team kanban sync (Hermes ↔ Mavis) | Out of scope — see `cross-team-discipline.md` |
| Card archival after >90d in `done/` | Manual quarterly review, not automated |

## File layout

```
mavis-kanban-bridge/
  SKILL.md                  ← this file
  references/
    operations.md           ← full command surface, edge cases, examples
    SCHEMA-cheatsheet.md    ← copy of the 7 rules for offline use
```

(One script lives at `scripts/kanban.sh` in the project root next to
SKILL.md — see `references/operations.md` for path resolution.)

## Cold-start integration (Mavis boot sequence)

Add to Mavis's `~/.mavis/agents/mavis/SOUL.md` cold-start checklist:

```bash
# Step 3: Kanban pull (after identity, before inbox)
./scripts/kanban.sh read --owner mavis --status open
# → surface matching cards in the next user-facing brief
```

The pull is read-only. Claim happens via `transition --to in_progress`
on a per-card basis when Mavis actually picks the card up.

## Cross-team discipline reminder

This skill touches Mavis's MainVault Kanban ONLY. Hermes has its own
kanban (kanban MCP at `mcp-kanban`). Per `cross-team-discipline.md`:

- Mavis reads MainVault Kanban, never the kanban MCP
- Mavis writes MainVault Kanban, never the kanban MCP
- Cross-pollination happens via spec-block handoff to Hermes, not via
  the bridge skill

If a directive seems to require touching Hermes's kanban, HALT and
surface to Andre — that's a Mavis↔Hermes coordination move, not a
single-agent task.

## Why this skill exists (the durable-task gap)

Pre-V3 (before 2026-06-21): every directive in chat evaporated when
the context window rolled. Hermes's exact blocker: "I have no shared,
durable task store I can read+write — every action needs you in chat
to direct it." Post-V3: directives land as cards, cards survive
context, cold start picks them up, terminal status moves them out.
The bridge is the read/write/validate/move surface that makes that
durable-task contract work.

**Without this skill, "I'll do it next session" is a promise with no
memory.**
