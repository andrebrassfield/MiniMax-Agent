# SCHEMA Cheatsheet — 7 Validation Rules

Copy of `~/Documents/Obsidian/MainVault/Kanban/SCHEMA.md` rules for
offline use. The bridge script (`scripts/kanban.sh validate`) is the
authoritative enforcer. This is the human-readable form.

## Required frontmatter

| Field | Type | Rule |
|---|---|---|
| `id` | string | matches `^kanban-\d{4}-\d{2}-\d{2}-\d{3}$` |
| `title` | string | verb-first, one line, ≤80 chars |
| `status` | enum | `open \| in_progress \| blocked \| done \| dropped` |
| `owner` | string | profile name (in `~/.hermes/profiles/`) or `human:andre` |
| `priority` | enum | `high \| med \| low` |
| `created` | date | ISO `YYYY-MM-DD` |
| `updated` | date | ISO `YYYY-MM-DD` |
| `next_action` | string | non-empty when `status: in_progress` |

## Optional frontmatter

| Field | Type | Rule |
|---|---|---|
| `blocked_by` | string \| list | kanban-id(s) referencing an existing card in `active/` or `done/` |
| `depends_on` | string \| list | semantically same as `blocked_by`, kept for clarity |
| `tags` | list | free-form, for filtering |
| `estimate` | string | human time estimate (`5min`, `30min`, `2h`) |

## Required body sections

- `## Description` — 2-4 lines, no preamble
- `## Acceptance` — concrete done criteria, named signer if subjective
- `## Log` — append-only `YYYY-MM-DD HH:MM — <action>` entries

## The 7 rules (canonical)

1. `id` matches `^kanban-\d{4}-\d{2}-\d{2}-\d{3}$`
2. `status` ∈ {`open`, `in_progress`, `blocked`, `done`, `dropped`}
3. `owner` is a real profile name or `human:andre`
4. `priority` ∈ {`high`, `med`, `low`}
5. `created`, `updated` are valid `YYYY-MM-DD`
6. `next_action` is non-empty when `status: in_progress`
7. `blocked_by` references an existing card when `status: blocked`

## Status → directory mapping

| `status` | File location |
|---|---|
| `open` | `cards/active/` |
| `in_progress` | `cards/active/` |
| `blocked` | `cards/active/` |
| `done` | `cards/done/` |
| `dropped` | `cards/dropped/` |

The directory IS the status. `mv` on terminal transition is mandatory.

## Filename convention

`kanban-YYYY-MM-DD-NNN-slug.md` where:
- `YYYY-MM-DD` is the creation date
- `NNN` is a 3-digit zero-padded sequence for that date
- `slug` is 2-4 lowercase-hyphenated words from the title

Example: `kanban-2026-06-21-005-audit-x-post-cadence.md`
