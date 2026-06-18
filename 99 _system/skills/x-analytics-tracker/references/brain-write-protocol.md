# Brain Write Protocol — x-analytics-tracker

The load-bearing step that turns the analytics dashboard into a learning
system. After the human-readable dashboard is updated, write the same
metrics to the `performance_log` array in
`03 Projects/X-Content-Engine/memory/content_brain.json`. The next
Researcher run reads `performance_log` to rank `ideas_backlog` by what
has actually performed for @DreTheSalesGuy.

## Schema check (read first)

```python
import json
from pathlib import Path

BRAIN = Path("03 Projects/X-Content-Engine/memory/content_brain.json")
state = json.loads(BRAIN.read_text())

required = ["hooks", "formats", "pain_points", "ideas_backlog", "performance_log"]
for key in required:
    assert key in state, f"brain JSON missing required key: {key}"
```

If the brain is missing or malformed, **HALT** and surface to Andre. The
dashboard write is non-fatal; the brain write is the load-bearing step.

## Concurrency check

```python
read_time = BRAIN.stat().st_mtime
# ... build new entries ...
assert BRAIN.stat().st_mtime == read_time, "brain was modified between read and write"
```

If mtime changed, the Researcher or Scribe ran concurrently. HALT,
re-read, re-merge, retry once.

## Build the performance_log entries

For each post in the dashboard, build an entry. Schema:

```json
{
  "post_id": "<x.com URL — use the URL as the stable identifier>",
  "hook_used": "<hook text — see hook-extraction strategy below>",
  "views": <integer or null if "unclear">,
  "likes": <integer or null if "unclear">,
  "date": "<YYYY-MM-DD the post was published>"
}
```

## Hook extraction (the hard part)

X analytics shows the post text but not which `ideas_backlog` entry
produced it. Two strategies, in order of preference:

1. **URL-based lookup.** If the post URL appears in any prior
   `drafts/*.md` file (especially `drafts/machine-batch-*.md`), read
   that file, find the section that cites the post, pull the
   `Source idea` from the embedded JSON snippet. This is reliable when
   the post went through the Scribe.

2. **First-sentence fallback.** If the URL is not in any prior draft
   (e.g., Andre posted manually from a phone), extract the first
   sentence of the post body as a best-effort `hook_used`. Tag in the
   dashboard's Notes column as `hook_source: first_sentence_fallback`.

The "what I don't know" sections in the brief should list any posts
where extraction fell back to first-sentence — these are candidates for
manual `ideas_backlog` enrichment.

## Missing data handling

If `views` or `likes` is "unclear" in the dashboard, write the integer
as `null` in the JSON (not the string `"unclear"`). The brain is
machine-readable; Python's `json` round-trip treats `null` as missing.
The string `"unclear"` would break downstream sort/filter.

## Idempotency rule (load-bearing)

```python
for entry in state["performance_log"]:
    if entry["post_id"] == new_entry["post_id"]:
        # Update in place: keep date and hook_used from original
        # Overwrite views/likes (may have grown)
        entry["views"] = new_entry["views"]
        entry["likes"] = new_entry["likes"]
        break
else:
    state["performance_log"].append(new_entry)
```

The `for ... else` is the canonical "update if exists, else append."
Re-running the skill on the same window UPDATES existing entries
(since views/likes may have grown), not duplicates them. The `post_id`
(URL) is the stable identifier.

## Atomic write (mandatory)

```python
import os, tempfile

with tempfile.NamedTemporaryFile(
    mode="w", dir=BRAIN.parent, prefix=".content_brain_", suffix=".tmp", delete=False
) as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
    f.flush()
    os.fsync(f.fileno())
    tmp_path = f.name

os.replace(tmp_path, BRAIN)
```

The atomic rename pattern: write to a temp file, fsync, then `os.replace`
(which is atomic on the same filesystem). If anything fails, the brain
file is unchanged. The eval suite in `tests/brain-write-discipline.md`
verifies the mtime updates and the JSON is valid after the write.

## Halt conditions

- Brain JSON missing → HALT, surface (dashboard write may have succeeded)
- Brain JSON malformed → HALT, surface
- Schema check fails (missing required keys) → HALT, surface
- Concurrency check fails (mtime changed) → HALT, re-read, retry once
- Atomic write fails (os.replace raises) → HALT, surface prominently
