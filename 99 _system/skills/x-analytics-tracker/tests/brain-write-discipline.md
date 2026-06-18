# Brain Write Discipline — x-analytics-tracker

The brain write is the load-bearing step that turns the dashboard into
a learning system. The eval suite verifies the discipline holds.

## T1. Atomic write pattern used

**Verification:**
```bash
# Before run
stat --format='%Y' "03 Projects/X-Content-Engine/memory/content_brain.json" > /tmp/before-mtime

# Run the skill

# After run
stat --format='%Y' "03 Projects/X-Content-Engine/memory/content_brain.json" > /tmp/after-mtime

# The mtime MUST update (the atomic rename updated it)
test "$(cat /tmp/after-mtime)" -gt "$(cat /tmp/before-mtime)" || echo "FAIL: mtime did not update"

# The brain MUST be valid JSON
python3 -m json.tool < "03 Projects/X-Content-Engine/memory/content_brain.json" > /dev/null || echo "FAIL: invalid JSON"
```

**Failure mode this catches:** the brain write didn't actually happen
(e.g., the dashboard succeeded but the brain write threw an exception
that wasn't caught).

## T2. Idempotency (re-run updates, doesn't duplicate)

**Setup:** Run the skill against window W. Capture `count(performance_log)`.
Run the skill again against window W. Capture `count(performance_log)`.
The count must NOT grow (the same posts re-update with the same URL).

**Failure mode this catches:** the `for ... else` pattern was
implemented wrong and every re-run appends new entries (the brain
grows unboundedly).

## T3. Concurrency detection (mtime changed mid-run)

**Setup:** Start the brain write. In another shell, modify the brain
file (touch it). The skill's concurrency check should fire and HALT.

**Verification:** the skill halts with a "brain was modified between
read and write" message and does NOT overwrite the brain.

**Failure mode this catches:** a concurrent writer (Researcher,
Scribe) modified the brain, the skill's atomic write would clobber
the concurrent change.

## T4. "unclear" → null in JSON

**Setup:** Run the skill when some metrics are "unclear" in the
dashboard. Inspect the brain.

**Verification:**
```python
import json
brain = json.load(open("content_brain.json"))
for entry in brain["performance_log"]:
    if "views" in entry and entry["views"] is not None:
        assert isinstance(entry["views"], int), f"views should be int or null, got {type(entry['views'])}"
    # views should never be the string "unclear" (that's a human-readable sentinel)
    assert entry.get("views") != "unclear", "string 'unclear' leaked into JSON"
```

**Failure mode this catches:** the skill wrote the string "unclear"
into the JSON (which would break downstream sort/filter).

## T5. Required keys present

**Verification:** after the write, the brain must have all required
keys (hooks, formats, pain_points, ideas_backlog, performance_log).

```python
import json
brain = json.load(open("content_brain.json"))
required = ["hooks", "formats", "pain_points", "ideas_backlog", "performance_log"]
for key in required:
    assert key in brain, f"required key {key} missing after write"
```

**Failure mode this catches:** the skill wrote a partial brain (e.g.,
just performance_log, dropped the other keys).

## T6. post_id is the URL (stable identifier)

**Verification:** every `performance_log` entry has `post_id` set to
the full x.com URL (not a numeric ID, not a relative path).

**Failure mode this catches:** the skill used a different identifier
(e.g., the numeric post ID) and the idempotency check would fail
across skill versions.
