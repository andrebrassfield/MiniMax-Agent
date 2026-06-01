---
type: permanent
created: 2026-06-01
tags: [vault, conventions, process]
status: seed
---

# Vault Conventions

> How the vault is organized. Naming, linking, processing rules.

## Folder structure (locked)

| Folder | Purpose | Naming |
|--------|---------|--------|
| `00 Inbox/` | Raw captures, unprocessed | descriptive or `yyyy-mm-dd-topic.md` |
| `01 Daily/` | One note per day | `yyyy-mm-dd.md` |
| `02 Notes/` | Permanent notes — one concept per note | `Concept Name.md` (Title Case) |
| `03 Projects/` | Active project subfolders | `Project Name/` with `00 Overview.md` |
| `04 Resources/` | Reference material by topic | `Topic/Name.md` |
| `05 Archive/` | Completed/obsolete | inherits name |
| `99 _system/` | Templates, dashboards, meta | descriptive |

The `_` prefix on `99 _system/` sorts it last in the file explorer.

## Linking rules (the network is the value)

1. **Link on reference** — any time you mention a concept with its own note, use `[[wikilink]]`
2. **Link on processing** — when moving a note from Inbox to Notes, find ≥1 existing note to connect
3. **Link on review** — during weekly review, open 5 random notes and add 1 missed link each
4. **No orphan notes** — every permanent note has ≥1 outgoing link

## Frontmatter conventions

Every note has YAML frontmatter. Required fields by type:

- **Permanent note**: `type: permanent`, `created:`, `tags:`, `status:`
- **Daily**: `type: daily`, `date:`, `day:`
- **Project**: `type: project`, `status:`, `started:`, `priority:`
- **Meeting**: `type: meeting`, `date:`, `attendees:`, `status:`
- **Resource**: `type: resource`, `created:`, `source:`, `tags:`

## Status field semantics

- **Inbox items**: `inbox` → `processing` → `done` | `archived`
- **Projects**: `active` | `paused` | `completed` | `archived`
- **Notes**: `seed` | `developing` | `mature` | `archived`
- **Decisions**: `pending` | `made` | `reversed`

## Processing rules

- **Inbox → Notes** = generalize (extract the concept, link to related notes)
- **Inbox → Projects** = assign (move to the right project subfolder, link)
- **Inbox → Resources** = preserve (save the reference with context)
- **Inbox → Archive** = drop (note what it was and why we dropped it)
- **Daily → Notes** = extract any decisions, insights, or lasting thoughts
- **Project complete → Archive** = don't delete, move with a "completed on" date

## Naming

- **No special chars** in filenames (breaks wikilinks)
- **Title Case** for permanent notes (`M3 Capabilities`, not `m3-capabilities`)
- **kebab-case** for project subfolders (`m3-eval-lab`)
- **Dates in ISO format** (`2026-06-01`)

## Tag conventions

- **Lowercase, kebab-case**: `ai-foundation-models`, `second-brain`
- **Type tags**: `m3`, `mavis`, `vault`
- **Domain tags**: as concepts emerge
- **Don't over-tag**: 1-3 tags per note, max 5

## Connections

- [[SOUL]] — identity
- [[Mavis EA Workflow]] — how I work
- [[Linking Principle]] — why linking matters
- [[Capture Over Polish]] — the bias toward action
