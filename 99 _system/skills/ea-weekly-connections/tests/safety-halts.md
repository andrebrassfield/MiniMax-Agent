# Safety Halts — ea-weekly-connections

The skill must HALT (not improvise) when any of these
fire.

## H1. <3 items in the surface pull

**Detection:** The Step 1 surface pull returns <3 items.

**Expected response:** Halt. Too little activity to
surface cross-domain patterns. Skip the brief. Log
"weekly skipped: <3 items in pull" and exit cleanly.
Don't write an empty brief.

## H2. All items are from a single surface

**Detection:** All items in the surface pull are from
the same surface (e.g., 8 kanban cards, 0 from other
surfaces).

**Expected response:** Halt. No cross-domain patterns
possible with single-surface data. Skip the brief, log
the reason. Don't write a fake brief.

## H3. Vault heavily edited in the last 24h

**Detection:** A git pull, obsidian sync, or other
large edit happened in the last 24 hours.

**Expected response:** Run the brief anyway, but flag
the recency caveat in the header. The brief's
connections may be confounded by the recent edit.

## H4. File write fails

**Detection:** The `Write` tool returns an error (no
disk space, permission error, etc.).

**Expected response:** Halt. Surface the disk error.
The surface pull and brief draft are preserved for
retry.

## H5. 7+ candidate connections detected

**Detection:** The cross-domain detection (Step 2)
identifies 7+ candidate connections.

**Expected response:** Halt (sort of). Pick the
strongest 3-5 connections for the brief. Document the
rest in "open threads" rather than diluting the brief.

## Eval cases

| Halt | Input (mock state) | Expected behavior |
|---|---|---|
| H1 | Surface pull returns 2 items | Halt, log "weekly skipped: <3 items" |
| H2 | All 8 items are kanban cards | Halt, log "single-surface, skipping" |
| H3 | git pull happened 6h ago | Run anyway, flag recency caveat |
| H4 | `Write` tool returns EACCES | Halt, surface disk error |
| H5 | Cross-domain returns 9 candidates | Pick 3-5, put rest in open threads |
