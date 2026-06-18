# Output Format — x-value-bomb-dropper

The markdown file structure for the rolling daily value-bombs
file.

## File path

`03 Projects/X-Content-Engine/drafts/value-bombs-YYYY-MM-DD.md`

One file per day, all targets in that day aggregated. The
Scribe appends each reply section to the existing file (or
creates the file if it doesn't exist).

## Per-reply section template (Scribe-enforced)

```markdown
## Value Bomb for @<handle> · <source post timestamp>

**Source:** <source-url>
**Quoted post (excerpt):** "<first 200 chars of source post>..."
**Operational question being answered:** <one-sentence paraphrase with the verb and the tool/domain>
**Format chosen:** <single-tweet | 🧵 3-tweet thread>
**Status:** pending_review

### Reply draft

<the actual reply text here, raw, ready to copy-paste into x.com. If thread, label tweets 1/, 2/, 3/.>

### Character count

<XX / 280 single | XXX / ~840 thread>

### Why this reply

[2-3 sentences: what stack you named, why it's the right stack for THIS question, and how the 3 steps take the person from zero to working solution in a week. If you chose thread format, explain why single-tweet would have lost the breathing room.]

### Notes for Andre

[Any specifics to verify — e.g., "step 2 references Vapi specifically; you may want to soften to 'a low-latency voice engine' if you're not ready to commit to one vendor publicly" or "the unit-economics line assumes the person is missing 8+ calls/day; you may want to scale the math up or down depending on the post's signal" or "this stack assumes a Shopify Plus plan; if the person is on basic Shopify, the API rate limits change the math — flag if the post doesn't reveal their plan tier."]

### Approval

- [ ] approved → copy/paste
- [ ] rejected (reason: ________)
- [ ] needs revision (notes: ________)
```

## File growth pattern

One file per day, all targets in that day aggregated. The
Scribe appends each reply to the existing file. The chief
(Mavis) reads the file at the end of the day to surface the
strongest reply candidates to Andre.

## Value-bombs ledger append

After each Scribe reply section is written, the chief appends
a one-line entry to
`03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — value-bomb to @<handle> (source: <source-url>, Scribe draft, pending)
```

The ledger is the audit trail. The next Scribe batch reads
it to know which sources have been replied to.

## When the operator rejects

When the operator marks a section as `rejected`, the chief
appends a second line to the ledger:

```markdown
- YYYY-MM-DD HH:MM CT — value-bomb to @<handle> REJECTED (reason: <one-line>)
```

This prevents the Scribe from re-drafting for the same target
on the next run.
