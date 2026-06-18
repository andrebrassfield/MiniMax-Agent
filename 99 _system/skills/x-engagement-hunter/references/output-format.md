# Output Format — x-engagement-hunter

The markdown file structure for the rolling daily replies file.

## File path

`03 Projects/X-Content-Engine/drafts/replies-YYYY-MM-DD.md`

One file per day, all targets in that day aggregated. The Scribe
appends each reply section to the existing file (or creates the
file if it doesn't exist).

## Per-reply section template (Scribe-enforced)

```markdown
## Reply to @<handle> · <source post timestamp>

**Source:** <source-url>
**Quoted post (excerpt):** "<first 200 chars of source post>..."
**Status:** pending_review

### Reply draft

<the actual reply text here, raw, ready to copy-paste into x.com>

### Character count

XX / 280

### Why this reply

[2-3 sentences: what value-add angle, what technical/agentic insight is being added, why this specific angle vs. the alternatives. Link to the persona pillar if relevant — e.g., "extends the target's point using Andre's Pillar 4 build-log principle of <X>."]

### Notes for Andre

[Any specifics to verify — e.g., "this references a $0.40/call figure; confirm the latest number before posting" or "the @-mention is to a real account; double-check the handle."]

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
- YYYY-MM-DD HH:MM CT — reply to @<handle> (source: <source-url>, Scribe draft, pending)
```

The ledger is the audit trail. The next Scribe batch reads it to
know which targets have been replied to.

## When the operator rejects

When the operator marks a section as `rejected`, the chief
appends a second line to the ledger:

```markdown
- YYYY-MM-DD HH:MM CT — reply to @<handle> REJECTED (reason: <one-line>)
```

This prevents the Scribe from re-drafting for the same target on
the next run.
