# Decision Log Dashboard

> One-way vs two-way door decisions. What was decided, why, and what to revisit.

## 🔥 Recent decisions

```dataview
LIST
FROM "02 Notes"
WHERE contains(tags, "decision")
SORT file.mtime DESC
LIMIT 10
```

## ⏳ Pending decisions (need to be made)

```dataview
LIST
FROM "02 Notes"
WHERE contains(tags, "decision") AND status = "pending"
SORT file.mtime DESC
```

## 🔄 Decisions to revisit (review date passed)

```dataview
LIST
FROM "02 Notes"
WHERE contains(tags, "decision") AND status = "made" AND file.mtime < date(today) - dur(30 days)
SORT file.mtime ASC
```

**Action**: open each, write what you learned in the "What I learned" section.

## 🚪 One-way door decisions (irreversible)

```dataview
LIST
FROM "02 Notes"
WHERE contains(tags, "decision") AND contains(file.text, "[x] No — one-way door")
```

## ↩️ Reversible decisions (two-way door)

```dataview
LIST
FROM "02 Notes"
WHERE contains(tags, "decision") AND contains(file.text, "[x] Yes — easy to back out")
```

## 📊 By status

```dataview
TABLE
  length(rows) as "Count"
FROM "02 Notes"
WHERE contains(tags, "decision")
GROUP BY status
```

## 🔀 Reversed decisions (the regret column)

```dataview
LIST
FROM "02 Notes"
WHERE contains(tags, "decision") AND status = "reversed"
SORT file.mtime DESC
```

**Read these carefully** — they're the highest-signal entries. What did I miss?

## 📅 Decision cadence

```dataview
LIST
FROM "02 Notes"
WHERE contains(tags, "decision") AND file.cday >= date(today) - dur(30 days)
SORT file.cday DESC
```

---

## How to use

1. Big decision incoming? Open `decision-log.md` template (Cmd+P → Templates → decision-log)
2. Capture the options, the rationale, the reversibility, the predicted outcome
3. Set a review date — write it in the "Review date" field AND set a calendar reminder
4. When the review date hits, open the decision and write what you learned

The decision log is the most important habit in the vault. It compounds.

---
*Empty state is normal — the first decision is always the hardest to capture*
