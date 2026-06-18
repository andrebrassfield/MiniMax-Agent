# Output Format — x-empowerment-hunter

The markdown file structure for the rolling daily replies file.

## File path

`03 Projects/X-Content-Engine/drafts/empowerment-replies-YYYY-MM-DD.md`

One file per day, all targets aggregated. The Scribe appends each
reply to the existing file (or creates the file if it doesn't
exist).

## Per-reply section template

```markdown
## Reply to @<handle> · <source post timestamp>

**Source:** <source-url>
**Quoted post (excerpt):** "<first 200 chars of source post>..."
**Fear being addressed:** <one-sentence paraphrase>
**Status:** pending_review

### Reply draft

<the actual reply text here, raw, ready to copy-paste into x.com>

### Character count

XX / 280

### Why this reply

[2-3 sentences: what the empathy opener does, what the tactical pivot is, why this specific tool/workflow is the right play for THIS person's specific anxiety. If the reply generalizes, flag that — the post is too specific for a generic play.]

### Notes for Andre

[Any specifics to verify — e.g., "the tactical play assumes the person has ChatGPT Plus; if they're on free, the time-saved math is different" or "this reference to 'last 4 weekly reports' is a guess; you may want to substitute 'last 4 status emails' or 'last 4 sprint retros' depending on the person's role."]

### Approval

- [ ] approved → copy/paste
- [ ] rejected (reason: ________)
- [ ] needs revision (notes: ________)
```

## File growth pattern

One file per day, all targets in that day aggregated. The Scribe
appends each reply to the existing file. The chief (Mavis) reads
the file at the end of the day to surface the strongest reply
candidates to Andre.

## Replies ledger append

After each Scribe reply section is written, the chief appends a
one-line entry to `03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — empowerment-reply to @<handle> (source: <source-url>, Scribe draft, pending)
```

The ledger is the audit trail. The next Scribe batch reads it to
know which sources have been replied to.
