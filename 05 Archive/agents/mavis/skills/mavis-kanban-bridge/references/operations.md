# Operations — Full Command Surface

This is the executable companion to `SKILL.md`. The shell script
referenced as `scripts/kanban.sh` lives in the project root next to
SKILL.md. The script is the only mutating surface — all 5 operations
in SKILL.md route through it.

## Path resolution

The script uses `KANBAN_ROOT` from the environment, defaulting to
`~/Documents/Obsidian/MainVault/Kanban/`. Override with:

```bash
export KANBAN_ROOT=/path/to/alt/kanban
```

This matters when:
- Testing against a fixture tree (`KANBAN_ROOT=/tmp/kanban-test`)
- Running in CI (a hermetic per-run tree)
- Operating on a different vault branch (rare, not yet supported)

## Op 1 — `read`

```bash
./scripts/kanban.sh read [--owner <profile>] [--status <status>] [--tag <tag>]
```

**Behavior:**
- Scans `cards/active/*.md` (always — never reads `done/` or `dropped/`
  on cold start; that's archival, surface on explicit ask)
- Parses YAML frontmatter; filters by `--owner` and/or `--status`
- `--tag` filters on the optional `tags: [list]` frontmatter field
- Default owner = the calling profile (read `$MAVIS_PROFILE` first,
  then `~/.mavis/agents/mavis/.env`)
- Default status = `open`

**Output:** list of `id | title | owner | priority | next_action` —
one card per line, tab-separated. Exit 0 always (empty list is valid).

**Edge cases:**
- A card with malformed frontmatter → printed with `[MALFORMED]` prefix
  and a one-line error; doesn't fail the whole read
- A card with `blocked_by` referencing a non-existent id → printed
  with `[ORPHAN_BLOCK]` prefix (the bridge will not silently heal it)

## Op 2 — `new`

```bash
./scripts/kanban.sh new \
  --title "<verb-first, one line, max 80 chars>" \
  --owner <profile> \
  --priority <high|med|low> \
  --next-action "<concrete next step>" \
  [--description "<2-4 lines>"] \
  [--acceptance "<done criteria>"] \
  [--depends-on <kanban-id>] \
  [--tag <tag> --tag <tag>]
```

**Behavior:**
- Generates next id: `kanban-$(date +%Y-%m-%d)-NNN` where NNN is the
  next available 3-digit sequence for today's date (scans `cards/active/`
  + `cards/done/` for collisions)
- Slugifies title (2-4 lowercase-hyphenated words) for the filename:
  `kanban-2026-06-21-004-compile-agent-notes.md`
- Copies `templates/card.md`, fills frontmatter, writes to
  `cards/active/`
- Appends a `## Log` entry: `YYYY-MM-DD HH:MM — created by <actor>`
  where actor = `$MAVIS_PROFILE` or `human:andre`
- Filename conflict (extremely rare, only if two `new` calls in the
  same second) → sleeps 1s and retries

**Edge cases:**
- Title > 80 chars → HALT with a one-line error; don't truncate silently
- `--owner` doesn't exist in `~/.hermes/profiles/` AND isn't `human:andre`
  → HALT (SCHEMA rule 3)
- `--depends-on` references a non-existent id → HALT (SCHEMA rule 7
  shape; we don't allow deps on ghosts)

## Op 3 — `transition`

```bash
./scripts/kanban.sh transition <kanban-id> \
  --to <open|in_progress|blocked|done|dropped> \
  [--next-action "<new next action>"] \
  [--blocked-by <kanban-id>] \
  [--log "<free-text log entry>"]
```

**Behavior:**
- Reads the card, runs the 7 SCHEMA rules against the proposed
  transition (not the current state)
- On pass: updates frontmatter (`status`, `updated`, optionally
  `next_action`, optionally `blocked_by`), appends a `## Log` entry
- On fail: HALT with `ERROR rule-N: <one-line description>` and the
  current frontmatter; no partial writes

**Status transition validity:**

| From | Allowed → To |
|---|---|
| `open` | `in_progress`, `blocked`, `dropped` |
| `in_progress` | `done`, `blocked`, `dropped` |
| `blocked` | `in_progress`, `dropped` |
| `done` | (terminal, no transitions) |
| `dropped` | (terminal, no transitions) |

Backwards transitions (`in_progress → open`) are not allowed — the
right move is to add a new card if work reopens.

**Edge cases:**
- `--to done` while the card is in `cards/active/` → succeeds, status
  updated, but does NOT move the file. Use `move` for the file move.
  This split is intentional: you may want to update frontmatter
  first, then move in a separate audit step.
- `--to in_progress` with empty `next_action` → HALT (SCHEMA rule 6)

## Op 4 — `move`

```bash
./scripts/kanban.sh move <kanban-id> --to <done|dropped>
```

**Behavior:**
- Reads the card, asserts:
  - File is in `cards/active/`
  - `status` frontmatter matches `--to`
- Updates `updated` field, appends a final `## Log` entry
- `mv cards/active/<id>.md cards/<target>/<id>.md`
- Idempotent: if the file is already in the target dir, exit 0 no-op

**Edge cases:**
- `--to done` but file is in `cards/dropped/` → exit 1 (terminal
  cards don't move between terminal dirs; that's a manual fix)
- `mv` fails (e.g., disk full) → HALT, leave the card in `active/`,
  the frontmatter update is reverted on rollback

## Op 5 — `validate`

```bash
./scripts/kanban.sh validate [<kanban-id>]
```

**Behavior:**
- No id given → validate every card in `cards/active/`
- Id given → validate that one card
- Each card checked against all 7 SCHEMA rules
- On any failure: exit 1, print per-card error list
- On all pass: exit 0, print one-line summary (`N cards validated, 0 errors`)

**Edge cases:**
- A card with parse errors (not valid YAML) → reports `[YAML_PARSE]`
  and skips the rest of the rules for that card
- A card with missing required fields → reports `[MISSING_<field>]`
  and lists which fields

## Idempotency guarantees

- `read` → safe to call repeatedly, no side effects
- `new` → safe to retry on transient errors; the id generator is
  atomic per-day (locks the active+done scan, picks next NNN, releases)
- `transition` → safe to retry on transient errors; validates the
  proposed state, not the current state
- `move` → safe to retry; idempotent guard prevents double-move
- `validate` → safe to call from cron, exits cleanly

## Error format (machine-readable)

All errors emit a one-line `ERROR <code>: <message>` to stderr.
Codes:

- `ERROR id-format: id 'kanban-foo' does not match ^kanban-\\d{4}-\\d{2}-\\d{2}-\\d{3}$`
- `ERROR status-enum: status 'pending' is not in (open|in_progress|blocked|done|dropped)`
- `ERROR owner-unknown: owner 'spec-rogue' is not a registered profile and not 'human:andre'`
- `ERROR priority-enum: priority 'urgent' is not in (high|med|low)`
- `ERROR date-format: created '2026/06/21' is not ISO YYYY-MM-DD`
- `ERROR next-action-empty: status in_progress requires non-empty next_action`
- `ERROR block-orphan: blocked_by 'kanban-2026-06-21-999' does not reference an existing card`
- `ERROR yaml-parse: frontmatter is not valid YAML: <line>:<col> <reason>`
- `ERROR title-length: title is 87 chars; max 80`
- `ERROR file-missing: kanban-2026-06-21-001-compile-agent-notes.md not found in cards/active/`
- `ERROR terminal-move: card is in done/; cannot move between terminal dirs`
- `ERROR transition-invalid: cannot transition from <from> to <to>`

Cron + scripts parse on the `ERROR <code>:` prefix. The human message
after the colon is for humans.

## Examples

```bash
# Cold start
./scripts/kanban.sh read --owner mavis --status open
# → kanban-2026-06-21-005  | Audit X post cadence         | mavis  | high  | Pull last 7d analytics

# New card from a directive
./scripts/kanban.sh new \
  --title "Audit X post cadence against the 3-5d analytics window" \
  --owner mavis \
  --priority high \
  --next-action "Pull x-analytics-tracker for last 7d, compare to the 3-5d window in agents/feedback-loop.md" \
  --description "Verify the post-N cron chain actually waits 3-5d before measuring engagement, not 24h." \
  --acceptance "Report at 99 _system/dashboards/x-metrics-dashboard.md shows post_age ≥ 72h for all measured posts"

# Claim on cold start
./scripts/kanban.sh transition kanban-2026-06-21-005 \
  --to in_progress \
  --next-action "Reading agents/feedback-loop.md §3"

# Complete
./scripts/kanban.sh transition kanban-2026-06-21-005 --to done
./scripts/kanban.sh move kanban-2026-06-21-005 --to done
```
