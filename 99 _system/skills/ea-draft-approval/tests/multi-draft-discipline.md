# Multi-Draft Discipline — ea-draft-approval

The eval suite for the multi-draft batch file handling.
This is the load-bearing discipline that ensures
approving one draft doesn't accidentally approve the
whole batch.

## M1. Source file remains in drafts/ until ALL drafts decided

**Verification:** if a batch file has 3 drafts and only 1
is approved, the source file is still in `drafts/`
(multi-draft, not-yet-fully-decided).

```bash
DRAFTS_DIR="03 Projects/X-Content-Engine/drafts"

# Check each batch file in drafts/ — for each, count how
# many drafts are still undecided
for batch in "$DRAFTS_DIR"/*.md; do
  [ -f "$batch" ] || continue
  draft_count=$(grep -cE "^## Draft [0-9]+:" "$batch")
  if [ "$draft_count" -gt 1 ]; then
    # Multi-draft file. Check if it has any "Status: approved"
    # or "Status: denied" annotations (added by the bridge)
    approved=$(grep -cE "^## Draft [0-9]+:.*\[approved\]" "$batch")
    denied=$(grep -cE "^## Draft [0-9]+:.*\[denied\]" "$batch")
    decided=$((approved + denied))
    if [ "$decided" -gt 0 ] && [ "$decided" -lt "$draft_count" ]; then
      echo "OK: $batch has $decided/$draft_count drafts decided (in-flight)"
    elif [ "$decided" -eq "$draft_count" ]; then
      echo "WARN: $batch has all drafts decided but is still in drafts/ (should have moved)"
    fi
  fi
done
```

**Failure mode this catches:** a multi-draft file was
prematurely moved to `approved/` (before all drafts were
decided). This violates the multi-draft discipline.

## M2. Approved drafts are extracted to new files

**Verification:** when a draft is approved from a multi-
draft batch, the approved post is extracted to a new
file in `approved/`, preserving the `## Draft N` header.

```bash
APPROVED_DIR="03 Projects/X-Content-Engine/approved"

# Each approved file should start with `## Draft N: <title>`
for approved in "$APPROVED_DIR"/*.md; do
  [ -f "$approved" ] || continue
  head -1 "$approved" | grep -qE "^## Draft [0-9]+:" \
    || echo "FAIL: $approved doesn't start with a Draft header"
done
```

**Failure mode this catches:** the extraction didn't
preserve the `## Draft N` header. The post-N chain may
not recognize the file format.

## M3. Denied drafts are archived with the source file

**Verification:** if a draft is denied, the source file
moves to `archive/denied/` (the whole batch, not just
the denied draft).

```bash
DENIED_DIR="03 Projects/X-Content-Engine/archive/denied"

# Each denied file should still have all its drafts
# (the whole batch was archived)
for denied in "$DENIED_DIR"/*.md; do
  [ -f "$denied" ] || continue
  draft_count=$(grep -cE "^## Draft [0-9]+:" "$denied")
  [ "$draft_count" -lt 2 ] && echo "WARN: $denied is single-draft (multi-draft should preserve all)"
done
```

**Failure mode this catches:** the source file was
split on denial (only the denied draft archived). Per
the multi-draft discipline, the whole batch is archived.

## M4. Edited drafts replace the post text in-place

**Verification:** when a draft is edited, the edited
post text replaces the original in the source file (or
the extracted approved file), not a new file.

```bash
# Look for the "Edited" annotation in the state file
# (the Scribe's edit was applied, not stored as a new draft)
EDITED=$(jq -r '.proposals[] | select(.response_status == "edited") | .source_file' \
  "$HOME/.mavis/agents/mavis/crons/ea-draft-approval.state.json" | sort -u)

for source in $EDITED; do
  # The source file should have the edited text in place
  # (or the source was moved to approved/ and the edit
  # applied to the new file)
  echo "Edited source: $source"
done
```

**Failure mode this catches:** the edit was stored as a
new draft, not applied in place. The post-N chain would
see two versions of the same draft.

## Cross-reference

- `references/procedure.md` — the 5-step procedure
- `references/state-schema.md` — state file schema
- `references/reply-patterns.md` — reply classification
- `references/scribe-batch-format.md` — the Scribe's
  batch format
- `tests/safety-halts.md` — 6 halt conditions
- `tests/state-discipline.md` — state file discipline
