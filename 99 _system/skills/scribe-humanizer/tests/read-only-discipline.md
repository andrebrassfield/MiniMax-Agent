# Read-Only Discipline

The Humanizer is a refinement layer, not a Scribe replacement. It must
NEVER modify the Scribe's original draft file. The output is a new file
(`humanized-*.md`), the source is preserved verbatim.

## Test: source-file mtime unchanged

```bash
# Before Humanizer run
stat --format='%Y' "drafts/machine-batch-YYYY-MM-DD.md" > /tmp/before-mtime

# Run the Humanizer

# After Humanizer run
stat --format='%Y' "drafts/machine-batch-YYYY-MM-DD.md" > /tmp/after-mtime

# Verify
diff /tmp/before-mtime /tmp/after-mtime
# Expected: no diff (mtime unchanged)
```

## Test: source file content unchanged

```bash
sha256sum "drafts/machine-batch-YYYY-MM-DD.md" > /tmp/before-hash
# Run the Humanizer
sha256sum "drafts/machine-batch-YYYY-MM-DD.md" > /tmp/after-hash
diff /tmp/before-hash /tmp/after-hash
# Expected: no diff
```

## Failure mode this catches

The Humanizer accidentally writes to the source file (e.g., applies a
Stage 1 or Stage 2 rewrite directly to the Scribe's original). This breaks
the historical record and makes the Scribe ↔ Humanizer ↔ Andre workflow
un-auditable.

## Why this discipline exists

If Andre ever needs to revert a humanization, the Scribe's original must
be intact. The Humanizer's output is a PROPOSAL; the Scribe's original is
the canonical record. Mixing them destroys the audit trail.
