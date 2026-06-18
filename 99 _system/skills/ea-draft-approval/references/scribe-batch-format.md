# Scribe Batch Format — ea-draft-approval

How the Scribe's batch files are structured. Mavis parses
these to extract individual posts for proposal.

## The batch file structure

A Scribe batch file contains 2-4 posts, separated by
`## Draft N` headers:

```markdown
## Draft 1: <title>
<post text>
<load-bearing specifics callout>

## Draft 2: <title>
<post text>
<load-bearing specifics callout>

## Draft 3: <title>
<post text>
<load-bearing specifics callout>
```

## Per-draft fields

Each `## Draft N` block may contain:
- **Title** (in the header, after `## Draft N:`)
- **Post text** (the main content)
- **Load-bearing specifics callout** (optional; the Scribe
  may include verification notes, source links, or
  other context that should be surfaced to Andre but is
  not part of the post itself)

## Parsing procedure

Use `awk` or `python3` to split on `^## Draft ` headers:

```python
import re

def parse_scribe_batch(file_path: str) -> list:
    """Parse a Scribe batch file into a list of individual drafts."""
    with open(file_path) as f:
        content = f.read()

    # Split on `## Draft N:` headers
    pattern = r"^## Draft (\d+): (.+?)$"
    matches = re.finditer(pattern, content, re.MULTILINE)

    drafts = []
    for match in matches:
        draft_number = int(match.group(1))
        title = match.group(2)
        start = match.end()

        # Find the next `## Draft` or end of file
        next_match = re.search(r"^## Draft \d+:", content[start:], re.MULTILINE)
        end = start + next_match.start() if next_match else len(content)

        post_text = content[start:end].strip()

        drafts.append({
            "draft_number": draft_number,
            "title": title,
            "post_text": post_text
        })

    return drafts
```

## Single-draft vs multi-draft

**Single-draft file:** contains only `## Draft 1: <title>`.
When approved, the whole file moves to `approved/`. When
denied, the whole file moves to `archive/denied/`.

**Multi-draft file:** contains 2-4 `## Draft N` blocks.
When ONE draft is approved, only that draft is extracted
to a new `approved/` file. The source file remains in
`drafts/` until ALL drafts are decided. When ALL drafts
are decided (any combination of approved / denied /
edited), the source file is processed:
- If at least one approved: the source file's remaining
  drafts (if any) move to `archive/denied/`
- If all denied: the source file moves to
  `archive/denied/`

## Why multi-draft handling matters

The Scribe batches drafts for efficiency (one file write
= 2-4 posts). The bridge proposes each post
individually (one Telegram message per draft). The
multi-draft handling ensures:

- Approving one draft doesn't accidentally approve the
  whole batch
- The source file structure is preserved for the post-N
  chain (which may have a specific expected format)
- The audit trail shows which drafts were decided when

## Eval cases

```bash
# Verify the Scribe's batch file has the expected structure
draft_file="03 Projects/X-Content-Engine/drafts/scribe-batch-2026-06-16.md"

# Count `## Draft N:` headers
draft_count=$(grep -cE "^## Draft [0-9]+:" "$draft_file")
[ "$draft_count" -lt 1 ] && echo "FAIL: no draft headers"
[ "$draft_count" -gt 4 ] && echo "WARN: $draft_count drafts (2-4 is the standard)"
```
