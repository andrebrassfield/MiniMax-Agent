# Morning Brief Dashboard

> What to read first thing. Last updated: <% tp.date.now("YYYY-MM-DD HH:mm") %>

## 🎯 Today's single thing
*What's the ONE thing that would make today a success?*

## 📅 Today's calendar
*Add your calendar integration here when ready. Until then, paste manually.*

## 📥 Inbox (unprocessed)
```dataview
LIST
FROM "00 Inbox"
SORT file.ctime DESC
LIMIT 10
```

## 🔥 Active projects (by priority)
```dataview
LIST
FROM "03 Projects"
WHERE status = "active"
SORT priority DESC, started DESC
```

## ⏰ Tasks due today
```dataview
TASK
FROM ""
WHERE !completed AND due = date(today)
SORT priority DESC
```

## ⚠️ Overdue tasks
```dataview
TASK
FROM ""
WHERE !completed AND due < date(today)
SORT due ASC
```

## 📞 People to follow up with
```dataview
LIST
FROM "02 Notes"
WHERE contains(tags, "person")
SORT file.mtime DESC
LIMIT 5
```

## 📚 Reading queue (top 3)
```dataview
LIST
FROM "04 Resources"
WHERE status = "reading" OR status = "queued"
SORT file.ctime ASC
LIMIT 3
```

## 🌅 Yesterday's open threads
```dataview
LIST
FROM "01 Daily"
WHERE file.name = dateformat(date(today) - dur(1 day), "yyyy-MM-dd")
```

## 💭 Recent decisions to revisit
```dataview
LIST
FROM "02 Notes"
WHERE contains(tags, "decision")
SORT file.mtime DESC
LIMIT 5
```

---

## Quick prompts

- "Mavis, what's the most important thing today?"
- "Mavis, what did I commit to yesterday that I haven't done yet?"
- "Mavis, what's been on my mind lately that I haven't acted on?"

---
*Last touched by Mavis 2026-06-01 — empty state is normal on day 1*
