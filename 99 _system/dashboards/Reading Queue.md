# Reading Queue Dashboard

> Books, articles, papers. What to read next, what I'm reading, what I've finished.

## 📚 Currently reading

```dataview
LIST
FROM "04 Resources"
WHERE status = "reading"
SORT file.mtime DESC
```

## 📥 Up next (priority queue)

```dataview
LIST
FROM "04 Resources"
WHERE status = "queued"
SORT file.ctime ASC
LIMIT 10
```

## 🆕 Recently added

```dataview
LIST
FROM "04 Resources"
SORT file.ctime DESC
LIMIT 10
```

## ✅ Finished this month

```dataview
LIST
FROM "04 Resources"
WHERE status = "done" AND file.mtime >= date(today) - dur(30 days)
SORT file.mtime DESC
```

## 📊 By type

```dataview
TABLE
  length(rows) as "Count"
FROM "04 Resources"
GROUP BY type
SORT length(rows) DESC
```

## 🏆 Highest-rated (5-star)

```dataview
LIST
FROM "04 Resources"
WHERE rating = 5
SORT file.mtime DESC
```

## 🕸️ Most-linked resources

```dataview
LIST
FROM "04 Resources"
SORT length(file.inlinks) DESC
LIMIT 10
```

## 📖 Reading log (last 30 days)

```dataview
LIST
FROM "04 Resources"
WHERE file.mtime >= date(today) - dur(30 days)
SORT file.mtime DESC
```

## 💡 Stale (queued > 90 days, never started)

```dataview
LIST
FROM "04 Resources"
WHERE status = "queued" AND file.ctime < date(today) - dur(90 days)
```

**Action**: if not going to read in the next month, drop or archive.

---

## Capture workflow

1. See a link to read later → QuickAdd "Capture Reading" macro → adds to `04 Resources/`
2. When starting to read → flip status to `reading`
3. When finished → use `book-digest.md` or `article-digest.md` template, link to relevant notes
4. Move to `status: done`

---
*Empty state is normal — start by adding one thing you want to read*
