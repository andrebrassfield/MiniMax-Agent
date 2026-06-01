# INDEX — Mavis Vault

> Andre's second brain. Mavis (M3) is the steward.

## 📍 You are here

This is the entry point. Open this on Obsidian launch (Homepage plugin → `INDEX.md`).

## 🗺️ Quick navigation

| Where | What lives there |
|-------|------------------|
| [[README]] | Vault overview |
| [[SOUL]] | Who Mavis is, hard constraints |
| [[agent]] | Operating procedures, M3 cheat sheet |
| [[learnings]] | Discoveries, M3 capabilities, role history |

## 📂 Folder map

- **[[00 Inbox/]]** — raw captures, processed daily
- **[[01 Daily/]]** — one note per day (`yyyy-mm-dd.md`)
- **[[02 Notes/]]** — permanent notes, one concept each
- **[[03 Projects/]]** — active project subfolders
- **[[04 Resources/]]** — reference material by topic
- **[[05 Archive/]]** — completed / obsolete
- **[[99 _system/]]** — templates, dashboards, meta

## 🔥 Right now

```dataview
LIST
FROM ""
WHERE file.cday = date(today)
SORT file.ctime DESC
```

## 📋 Active projects

```dataview
LIST
FROM "03 Projects"
WHERE status = "active"
SORT priority DESC, started DESC
```

## 📥 Inbox (count)

```dataview
LIST
FROM "00 Inbox"
SORT file.ctime DESC
LIMIT 20
```

## 📅 Recent daily notes

```dataview
LIST
FROM "01 Daily"
SORT file.name DESC
LIMIT 7
```

## 🌱 Recent permanent notes

```dataview
LIST
FROM "02 Notes"
SORT file.ctime DESC
LIMIT 10
```

## ⏰ Overdue tasks

```dataview
TASK
FROM ""
WHERE !completed AND due < date(today)
SORT due ASC
```

## 🏷️ Most-used tags

```dataview
LIST
FROM ""
GROUP BY tags
SORT length(rows) DESC
LIMIT 15
```

---

## 🛠️ Templates

Located in [[99 _system/templates/]]:

- `daily.md` — daily note
- `meeting.md` — meeting note
- `note.md` — permanent concept note
- `project.md` — project overview
- `capture.md` — raw inbox capture
- `resource.md` — reference material

## 🔌 Plugins powering this vault

Dataview · Templater · Calendar · Tasks · obsidian-git · Smart Connections · Local REST API · Homepage · QuickAdd

## 📦 Backup

Backed up to `git@github.com:andrebrassfield/MiniMax-Agent.git` via `obsidian-git`.

---

*Last touched by Mavis: 2026-06-01*
