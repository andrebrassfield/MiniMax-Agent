# Idempotency — agent-deployment-monitor

The dedup logic + atomic write pattern. The discipline:
re-running the skill on the same client subdirectory
**updates** the file (doesn't duplicate). The atomic
write is the load-bearing pattern.

## The dedup logic

| State | Action |
|---|---|
| `deployment-status.md` does NOT exist | **create** |
| `deployment-status.md` exists | **update** (overwrite) |
| God View always | full **rewrite** (snapshot, not ledger) |

The skill does not append; it rewrites. The status board
is a snapshot of the current state, not a history.

## Atomic write pattern (the discipline)

The pattern is **temp-write-fsync-rename**. Never write
directly to the target file. The pattern:

```bash
TMP="/tmp/deployment-status-${client_name}-$$.md"
cat > "$TMP" <<EOF
[content]
EOF
sync  # Force fsync to disk
mv -f "$TMP" "$client_dir/deployment-status.md"
```

Or in Python (atomic via `os.replace`):

```python
from pathlib import Path
import os
content = "..."
target = Path(f"03 Projects/Clients/{client_name}/deployment-status.md")
TMP = f"/tmp/deployment-status-{client_name}-{os.getpid()}.md"
with open(TMP, "w") as f:
    f.write(content)
os.replace(TMP, target)  # atomic on POSIX
```

## Why atomic write matters

If the skill writes directly to the target file:

1. Skill starts writing at second 0
2. Process is killed at second 0.5
3. Result: half-written file at the target path

The operator opens the file → corrupted content → loses
trust in the skill's output.

With the temp-write-rename pattern:

1. Skill writes to `/tmp/deployment-status-X.md` at
   second 0
2. Process is killed at second 0.5
3. Result: half-written file at `/tmp/...` (target is
   unchanged)

The target file is either the old content (rename never
happened) or the new content (rename succeeded atomically).
No partial state visible to the operator.

## Idempotency check (the eval case)

```bash
# Run the skill twice
agent-deployment-monitor --client ClientA
agent-deployment-monitor --client ClientA

# Count deployment-status.md files
count=$(find "03 Projects/Clients/ClientA" -name "deployment-status.md" | wc -l)
[ "$count" -ne 1 ] && echo "FAIL: skill created $count files (should be 1)"

# Verify the file's content is the second run's content, not
# the first run's
diff <(first_run_output) <(current_file_content) \
  || echo "WARN: file content differs from expected (may be due to time-based fields)"
```

## What idempotency is NOT

- **Not a no-op.** The skill reads filesystem state on
  every run. Re-running produces the current snapshot, not
  a cached result.
- **Not append-only.** The God View is a snapshot, not a
  ledger. It does not accumulate history.
- **Not version-controlled (locally).** The skill does not
  track previous versions. The git history of
  `03 Projects/Clients/` is the audit trail (if the
  operator commits).

## Cross-reference

- `references/data-sources.md` — the 4 data source patterns
- `references/output-format.md` — the per-client and God
  View templates
- `references/procedure.md` — the 8-step procedure
- `tests/idempotency-check.md` — re-run verification
