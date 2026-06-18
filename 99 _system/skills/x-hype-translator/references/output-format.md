# Output Format — x-hype-translator

The markdown file structure for the Scribe's output. The chief
(Mavis) writes the file, but the Scribe's draft IS the bulk of
the content.

## File path

`03 Projects/X-Content-Engine/drafts/hype-translations-<tool-slug>-YYYY-MM-DD-HHMM.md`

Where `<tool-slug>` is the tool name lowercased with spaces → hyphens
and non-alphanumerics stripped. Example: `"Claude Code"` → `claude-code`.

The operator can override the per-tool slug to a single rolling file
`hype-translations-YYYY-MM-DD.md` if they want a daily-rolling
destination instead of per-tool files.

## Template

```markdown
## Hype Translation: <tool name> — YYYY-MM-DD HH:MM CT

**Source announcement:** <source-url>
**Tool capability (one line):** <what it does>
**Target audience (one line):** <the boring audience you're mapping to>

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

[2-3 sentences: why this specific boring audience was the right pick, what tactical detail makes the 4-step implementation actionable, how the dollar + time math is grounded]

### Notes for Andre

[Any specifics to verify — e.g., "this assumes the tool is free during preview; check pricing before posting" or "the audience (roofer) is a guess based on a 2026 trend; adjust if you have a different one in mind."]

### Approval

- [ ] approved → post
- [ ] rejected (reason: ________)
- [ ] needs revision (notes: ________)
```

## File growth pattern

One file per tool per run. To compare multiple tools, the operator
opens the files in order. To backfill a daily with multiple tools, the
operator can manually merge into a daily-rolling file.

## Drafts ledger append

After the Scribe writes, append one line to
`03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — hype-translation-<tool-slug> from <source-url> (Scribe draft, pending)
```

The ledger is the audit trail. The dispatcher (chief) reads it when
running the next Scribe batch to know what's been translated already.
