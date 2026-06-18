# Output Format — x-lead-qualifier

The queue file structure. The Scribe appends to
`03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl`.

## File path

`03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl`

One file per day, all drafts aggregated. The `.mdl`
suffix indicates "markdown ledger" (one entry per
line, append-only).

## Per-entry format (the load-bearing shape)

```markdown
- 2026-06-16 14:23 CT — @<handle> · <post-URL-or-DM-source> · intent: <signal-type>
  - Source: "<verbatim quote of the source text, ≤200 chars>"
  - Draft (from Scribe):
    > <the drafted DM, with technical tip + low-friction CTA>
  - Status: pending_review
  - Confidence: <0.0-1.0, how confident the intent detection was>
```

## Per-field content discipline

- **Timestamp + handle + source URL + intent type** (top
  line) — the metadata for the entry
- **Source quote** (verbatim, ≤200 chars) — the lead's
  actual text, so the operator sees the trigger
- **Draft** (block-quote, raw) — the Scribe's DM,
  copy-pasteable into x.com
- **Status** (pending_review) — the operator's review
  state
- **Confidence** (0.0-1.0) — the intent classification
  confidence score

## File growth pattern

One file per day, all drafts aggregated. The Scribe
appends each entry. The chief (Mavis) reads the file at
the end of the day to surface the strongest candidates
to Andre.

## Rolling ledger

In addition to the per-day file, there's a rolling
ledger at
`03 Projects/X-Content-Engine/queue/qualification-dms.mdl`:

```markdown
- 2026-06-16 14:23 CT — @<handle> · intent: <type> · confidence: <0.0-1.0> · drafted by Scribe · status: pending_review
```

The rolling ledger is the audit trail across days.
The per-day file is the per-day snapshot.

## Status lifecycle

```
[pending_review] ────► [sent_as_is]
       │
       ├────► [edited_then_sent]
       │
       ├────► [skipped_no_fit]
       │
       └────► [hold_warming_up]
```

The operator updates the status when they review the
queue:
- `pending_review` → initial state (the Scribe's draft
  is ready for review)
- `sent_as_is` → operator sent the draft as-is
- `edited_then_sent` → operator edited, then sent
- `skipped_no_fit` → operator decided the lead wasn't a
  fit
- `hold_warming_up` → operator wants to wait (e.g.,
  wait for the lead to engage more before sending)

## What this output is NOT

- **Not the published DM.** The queue is the review
  surface. The operator sends manually.
- **Not the Scribe's draft history.** The Scribe's
  drafts that were rejected by the Scribe's own
  verification checklist don't make it to the queue
  (they're logged elsewhere).
- **Not a CRM.** The queue is a markdown ledger. For
  full CRM features (contact management, deal
  tracking), use a different system.
- **Not a backup of x.com.** The queue is Mavis's
  review surface for Mavis's drafts. It's not a
  backup of the original X engagement (which is on
  x.com itself).
