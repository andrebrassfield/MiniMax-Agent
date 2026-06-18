# Output Format — x-bookmark-parser

## File location

`00 Inbox/x-bookmarks-YYYY-MM-DD-HHMM.md` (CT timezone)

## Template

```markdown
# X Bookmarks Capture — YYYY-MM-DD HH:MM CT

**Handle:** @<user_handle>
**Source:** https://x.com/i/bookmarks
**Captured:** YYYY-MM-DD HH:MM:SS CT
**Posts captured:** N

---

## Post 1 — @<author> · <relative_time>

- **URL:** https://x.com/<handle>/status/<id>
- **Type:** <Text|Article|Quote|Reply|Repost>
- **Title:** <if Article, the bolded first line>
- **Pull-quote:** "<first 1-2 sentences if there's a strong hook>"
- **Full text:** <everything between author block and engagement metrics>
- **Engagement:** <N> replies · <N> reposts · <N> likes · <N>K views

---

## Post 2 — ...

---

## Themes

<One-paragraph synthesis of the dominant format, voice, and topic patterns
across all captured posts. The Researcher consumes this directly.>
```

## Verification commands

```bash
ls -la "00 Inbox/x-bookmarks-YYYY-MM-DD-HHMM.md"
wc -l "00 Inbox/x-bookmarks-YYYY-MM-DD-HHMM.md"
grep -c "^## Post" "00 Inbox/x-bookmarks-YYYY-MM-DD-HHMM.md"
```

Expected: file exists, non-zero size, `grep -c "^## Post"` matches the
reported post count.
