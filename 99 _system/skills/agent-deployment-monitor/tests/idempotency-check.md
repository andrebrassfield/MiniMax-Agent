# Idempotency Check — agent-deployment-monitor

The eval suite verifies re-running the skill does NOT
duplicate files. The dedup logic is the load-bearing
discipline.

## I1. Re-run does not create a second deployment-status.md

```bash
# Run the skill
agent-deployment-monitor

# Count files for ClientA
file_count=$(find "03 Projects/Clients/ClientA" -name "deployment-status.md" | wc -l | tr -d ' ')
[ "$file_count" -ne 1 ] && echo "FAIL: $file_count deployment-status.md files (should be 1)"

# Run again
agent-deployment-monitor

# Re-count
file_count_2=$(find "03 Projects/Clients/ClientA" -name "deployment-status.md" | wc -l | tr -d ' ')
[ "$file_count_2" -ne 1 ] && echo "FAIL: after re-run, $file_count_2 files (should be 1)"
```

**Failure mode this catches:** the skill created a
duplicate file instead of updating.

## I2. Re-run preserves the file's mtime logic (current state)

```bash
# Save first run's mtime
first_mtime=$(stat -f "%m" "03 Projects/Clients/ClientA/deployment-status.md")
sleep 2

# Re-run the skill
agent-deployment-monitor

# Check the file's mtime was updated
second_mtime=$(stat -f "%m" "03 Projects/Clients/ClientA/deployment-status.md")
[ "$second_mtime" -le "$first_mtime" ] \
  && echo "FAIL: file mtime not updated after re-run (still $first_mtime)"
```

**Failure mode this catches:** the re-run produced the
same content with stale timestamps. The file should
reflect the current run.

## I3. No half-written file exists (atomic write check)

```bash
# Look for tmp files that should have been renamed
tmp_files=$(find /tmp -name "deployment-status-*.md" 2>/dev/null | wc -l | tr -d ' ')
[ "$tmp_files" -gt 0 ] && echo "WARN: $tmp_files tmp files in /tmp (atomic write may have failed)"
```

**Failure mode this catches:** the atomic write pattern
failed (tmp file was not renamed). The skill may have
been killed mid-write.

## I4. God View is rewritten (not appended)

```bash
# Save first run's line count
first_lines=$(wc -l < "03 Projects/Clients/_god-view.md")
sleep 1

# Add a new client
mkdir -p "03 Projects/Clients/ClientZ"
echo "test" > "03 Projects/Clients/ClientZ/README.md"

# Re-run the skill
agent-deployment-monitor

# Check God View now has ClientZ
grep -qF "ClientZ" "03 Projects/Clients/_god-view.md" \
  || echo "FAIL: new client ClientZ not in God View after re-run"

# Line count should be reasonable (not double)
second_lines=$(wc -l < "03 Projects/Clients/_god-view.md")
ratio=$(echo "scale=2; $second_lines / $first_lines" | bc)
[ "$(echo "$ratio > 1.5" | bc)" -eq 1 ] \
  && echo "WARN: God View line count grew $ratio x (may be appending instead of rewriting)"
```

**Failure mode this catches:** the God View is appending
clients instead of rewriting. The aggregation is
stale-on-stale.

## I5. Skip patterns are honored (no _template, _archive, _god-view)

```bash
# _template/ should NOT be in the God View
grep -qF "_template" "03 Projects/Clients/_god-view.md" \
  && echo "FAIL: _template in God View (should be skipped)"

# _archive/ should NOT be in the God View
grep -qF "_archive" "03 Projects/Clients/_god-view.md" \
  && echo "FAIL: _archive in God View (should be skipped)"
```

**Failure mode this catches:** the skill included
operator-curated subdirs as clients. The God View is
cluttered with non-clients.

## Cross-reference

- `references/idempotency.md` — full dedup logic + atomic
  write pattern
- `references/procedure.md` — the 8-step procedure
- `references/data-sources.md` — the 4 data source patterns
- `references/output-format.md` — the per-client and God
  View templates
