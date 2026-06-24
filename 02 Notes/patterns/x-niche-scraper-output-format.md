---
description: "Output format schema for x-niche-scraper — file location, markdown template, niches ledger append. Schema inherited from x-bookmark-parser; this file documents only the niche-scrape-specific differences. Moved from skill-local references 2026-06-22 as part of Upgrade 1 skill-scaling-law refactor."
source: ~/.mavis/agents/mavis/skills/x-niche-scraper/references/output-format.md
---

# Output Format — x-niche-scraper

The per-post schema is inherited from `x-bookmark-parser` (see
`../../x-bookmark-parser/references/data-schema.md`). This file documents
only what's different: the file-level header, the niches ledger append,
and the "Notes for the Content Researcher" section.

## File location

`00 Inbox/x-niche-<query-slug>-YYYY-MM-DD-HHMM.md` (CT timezone)

`<query-slug>` is the query with spaces replaced by hyphens, lowercased,
non-alphanumerics stripped. Example: `"HVAC: AI agents"` → `hvac-ai-agents`.

## Template

```markdown
# X Niche Scrape — <query> — YYYY-MM-DD HH:MM CT

**Query:** "<query>"
**Search tab:** Top
**Engagement floor:** 1,000 views
**Posts captured:** N
**Source:** https://x.com/search?q=<encoded>&f=<tab>

---

## Post 1 — @<author> · <relative_time>

- **URL:** https://x.com/<handle>/status/<id>
- **Type:** <Text|Article|Quote|Reply|Repost>
- **Pull-quote:** "..."
- **Full text:** ...
- **Engagement:** <N> replies · <N> reposts · <N> likes · <N>K views

---

## Post 2 — ...

---

## Notes for the Content Researcher

<One-paragraph synthesis: dominant format, voice profiles of top accounts,
common thread types, hook patterns observed. If the operator specified a
search tab, note the differences in results between Top and Latest.>
```

## Niches ledger append

After writing the capture, append one line to `00 Inbox/_x-niche-ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — <query-slug> (N posts, <tab> tab, floor <N>K)
```

The ledger is append-only. The Researcher reads it to find prior captures
without re-scanning `00 Inbox/`.
