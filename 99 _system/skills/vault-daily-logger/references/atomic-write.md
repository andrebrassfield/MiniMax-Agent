# Atomic Write — vault-daily-logger

The Python atomic-write pattern. The skill writes only to
`01 Daily/YYYY-MM-DD.md` using this pattern to prevent partial
writes on cron interruption.

## The pattern

```python
import os, tempfile
from pathlib import Path

DAILY = Path("01 Daily/YYYY-MM-DD.md")
content = f"""---
date: {date_today}
day: {day_of_week}
type: daily
tags: [auto-generated]
generator: vault-daily-logger
generator_version: 1.0
---

# {date_today}, {day_of_week}, ... 
...
"""
with tempfile.NamedTemporaryFile(
    mode="w", dir=DAILY.parent, prefix=".daily_", suffix=".tmp", delete=False
) as f:
    f.write(content)
    f.flush()
    os.fsync(f.fileno())
    tmp_path = f.name
os.replace(tmp_path, DAILY)
```

## Why atomic

If the cron is interrupted mid-write (system sleep, OOM, killed
process), a non-atomic write leaves a partial file. The
file-system sees a half-written daily. The next cron run sees the
partial file and the body-size check might pass (>100 bytes of
garbage), but the content is corrupted.

The atomic-write pattern: write to a temp file, fsync to flush
the buffer to disk, then `os.replace` (which is atomic on the same
filesystem). If anything fails, the original file is unchanged.
The next cron run sees the original (missing) file and proceeds
to generate fresh.

## Why `os.replace` and not `shutil.move`

`shutil.move` may fall back to copy+remove across filesystems,
which is NOT atomic. `os.replace` is guaranteed atomic on the same
filesystem. Since the daily lives in `01 Daily/`, the temp file
must be in the same directory (which `dir=DAILY.parent` ensures)
and `os.replace` is safe.

## The `fsync` is load-bearing

`f.flush()` flushes the Python buffer to the OS write buffer. But
the OS may not have flushed to disk yet. `os.fsync()` forces the
OS to flush. Without `fsync`, a power loss between `f.flush()` and
`os.replace` would lose the write. With `fsync`, the data is on
disk before the rename.

## The `dir=DAILY.parent` and `prefix=".daily_"` are discipline

The temp file is created in the same directory as the target
(same filesystem = atomic rename). The `prefix=".daily_"` makes
it easy to find if the rename failed (the temp file is left
behind, visible to `ls -la 01 Daily/`).

## What this is NOT

- Not a permission to skip `os.fsync`. The fsync is mandatory for
  cron-driven writes.
- Not a permission to use `Path.write_text()` directly. The atomic
  pattern is mandatory.
- Not a permission to overwrite an existing file. The skill halts
  if the file exists; the atomic write only runs on the
  "missing-or-empty" path.
