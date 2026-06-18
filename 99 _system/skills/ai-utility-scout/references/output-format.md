# Output Format — ai-utility-scout

The markdown file structure for the rolling daily
utility-scout file.

## File path

`03 Projects/X-Content-Engine/drafts/utility-scout-YYYY-MM-DD.md`

One file per day, all scouts aggregated. The Researcher
appends the discovery brief; the Scribe appends the
Pillar 6 draft under it.

## Per-scout section template (Researcher + Scribe)

```markdown
## Tool: <tool name> — <source directory> — YYYY-MM-DD HH:MM CT

**Source:** <directory entry URL>
**Pricing:** <free / freemium / paid / unclear>
**Launched:** <date or "unclear">

### What it does (one sentence)

<the tool's actual capability, in plain English>

### Category

<video / voice / image / productivity / e-commerce / local
services / dev infra / other>

### Who uses it (3 candidate audiences)

1. <audience 1>
2. <audience 2>
3. <audience 3>

### The boring SMB use case (the Dre Builds angle)

<one paragraph: which of the 3 audiences is the "boring
practical money-making" audience, and what the 4-step
implementation would look like.>

### What makes it hype-able vs. practical

<2-3 sentences: what's the "cool" angle the X conversation
will hype, vs. the boring application Dre Builds would
post.>

### Open questions for the Scribe

- Should the post use a specific persona pillar (Pillar 1/2/5/6)?
- What's the specific tool pricing anchor (if visible)?
- Is there a 4-step implementation path that fits in 280 chars?

---

### Post draft

<the actual post text, 180-260 chars, voice-matched>

### Character count

XX / 280

### 4-step implementation

1. <step 1>
2. <step 2>
3. <step 3>
4. <step 4>

### Cost

$<X>/month

### Time saved

X hours/week

### Why this angle

[2-3 sentences: why this specific boring audience was the
right pick, what tactical detail makes the 4-step
implementation actionable, how the dollar + time math is
grounded]

### Notes for Andre

[Any specifics to verify — e.g., "the 4-step implementation
assumes the tool stays free during preview; check pricing
before posting"]

### Approval

- [ ] approved → post
- [ ] rejected (reason: ________)
- [ ] needs revision (notes: ________)
```

## File growth pattern

One file per day, all scouts aggregated. The Researcher
writes first, the Scribe writes second (chronological
order). The chief reads the file at the end of the day to
surface the strongest candidate to Andre.

## Drafts ledger append

After each Scribe section is written, the chief appends a
one-line entry to
`03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — utility-scout from <directory> (tool: <tool name>, Scribe draft, pending)
```

The ledger is the audit trail. The next scout run reads
it to know which tools have already been translated.

## When the operator rejects

When the operator marks a section as `rejected`, the
chief appends a second line to the ledger:

```markdown
- YYYY-MM-DD HH:MM CT — utility-scout <tool> REJECTED (reason: <one-line>)
```

This prevents the next scout from re-drafting for the
same tool.
