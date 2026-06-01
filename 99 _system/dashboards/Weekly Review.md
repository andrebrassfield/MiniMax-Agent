# Weekly Review Dashboard

> Run this on Sundays. 15 minutes. Empty inbox, prune projects, find missed links.

## 📊 This week's stats

```dataview
LIST
FROM "01 Daily"
WHERE file.cday >= date(today) - dur(7 days)
SORT file.name DESC
```

## 📥 Inbox status

```dataview
LIST
FROM "00 Inbox"
SORT file.ctime DESC
```

**Action**: For each item, decide → permanent note, project, resource, or archive.

## 🔥 Project check (one per project)

```dataview
TABLE
  status as "Status",
  priority as "Pri",
  started as "Started"
FROM "03 Projects"
WHERE status = "active"
SORT priority DESC
```

For each: did it move? what's the next action? keep / pause / archive?

## 🌱 Permanent notes added this week

```dataview
LIST
FROM "02 Notes"
WHERE file.cday >= date(today) - dur(7 days)
SORT file.ctime DESC
```

## 🔗 Linking pass (5 random notes)

```dataview
LIST
FROM "02 Notes"
SORT file.mtime ASC
LIMIT 5
```

For each, find at least one new link you missed.

## 🕸️ Orphan notes (need linking)

```dataview
LIST
FROM "02 Notes"
WHERE length(file.outlinks) = 0
```

## ⏸️ Stale notes (not touched in 90 days)

```dataview
LIST
FROM "02 Notes"
WHERE file.mtime < date(today) - dur(90 days)
SORT file.mtime ASC
LIMIT 10
```

## ⏰ Tasks I committed to that I haven't done

```dataview
TASK
FROM ""
WHERE !completed AND due < date(today)
SORT due ASC
```

## 📚 Reading progress

```dataview
LIST
FROM "04 Resources"
WHERE status = "reading"
```

## 🎯 Top 3 for next week

1. 
2. 
3. 

## 🔄 Archive candidates

- **Project X** — completed? stale? → archive
- **Note Y** — wrong/outdated? → archive
- **Resource Z** — never going to re-read? → archive

## 💭 Reflection

*What was the shape of the week? What got in the way? What worked?*

---

## Weekly review template

Use the `weekly-review.md` template (Cmd+P → "Templater: Insert template" → weekly-review) to create a dated weekly review note. Link to it from this dashboard.

---
*Empty state is normal on day 1 — these queries start populating as you use the vault*
