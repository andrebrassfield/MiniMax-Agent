---
name: inbox-filer
schedule: 30 6 * * *
timezone: America/Chicago
session:
  mode: new
  keepSessions: 5
---

# Inbox Filer — Daily Organization (06:30 CT)

Closes the gap between capture (morning brief surfaces new inbox files) and organization (files move to their proper locations). Per the article's Step 10: "Check my vault. File anything new sitting in Inputs folders into the right place and link it."

Fires 30 min after the morning brief, processes that day's inbox additions. Reaction discipline enforced — articles without `## Reaction` get routed to a pending-reaction subfolder, not directly into `02 Notes/articles/`.

## State File

`~/.mavis/state/inbox-filer.state.json` (init with `{"last_run_at": null, "processed_files": []}`). Tracks what's already been routed to avoid re-processing.

## Procedure

### Step 1 — Read state + identify new files

```bash
# Read state
STATE=~/.mavis/state/inbox-filer.state.json
LAST_RUN=$(python3 -c "import json; print(json.load(open('$STATE'))['last_run_at'])" 2>/dev/null || echo "1970-01-01")

# Find new files in 00 Inbox/ (modified since last run)
if [ "$LAST_RUN" = "1970-01-01" ] || [ "$LAST_RUN" = "null" ]; then
  # First run — process everything currently in inbox
  find ~/MiniMax-Agent/00\ Inbox/ -maxdepth 1 -type f -name "*.md" 2>/dev/null
else
  find ~/MiniMax-Agent/00\ Inbox/ -maxdepth 1 -type f -name "*.md" -newermt "$LAST_RUN" 2>/dev/null
fi
```

**HALT if 0 files found:** silent skip (first run with empty inbox, or no new files). Write to log + exit.

### Step 2 — Classify each file

For each file, classify into one of these buckets based on content + filename:

| Bucket | Indicators | Destination |
|---|---|---|
| `article` | Filename has date + source, body has author/URL/excerpts, NO existing `## Reaction` section | `02 Notes/articles/_pending_reaction/YYYY-MM-DD - <title>.md` |
| `article-with-reaction` | Same as article BUT has `## Reaction` section | `02 Notes/articles/YYYY-MM-DD - <title>.md` |
| `idea` | Body has position/thesis/personal observation, no source references | `02 Notes/ideas/YYYY-MM-DD - <title>.md` |
| `pattern` | Body explicitly references "this is a pattern" or cross-domain application | `02 Notes/patterns/YYYY-MM-DD - <title>.md` |
| `question` | Body is open-ended, no answer, ends with "?" | `02 Notes/questions/YYYY-MM-DD - <title>.md` |
| `number` | Body is a specific data point / stat / metric | `02 Notes/numbers/YYYY-MM-DD - <title>.md` |
| `project-note` | Filename or body references a project in `03 Projects/`, suggests active work | `03 Projects/<project>/notes/YYYY-MM-DD - <title>.md` |
| `task` | Body is action item, has checkbox, has owner | `02 Notes/_MOCs/tasks-YYYY-MM-DD.md` (append) |
| `link` | Body is just a URL with brief note | `00 Inbox/links/YYYY-MM-DD - <title>.md` (subfolder, low-priority) |
| `quote` | Body is a single quote with attribution | `02 Notes/_MOCs/quotes.md` (append) |
| `unclear` | None of the above match confidently | Leave in `00 Inbox/`, flag in output, append to `unclear_log` |

**Classification rule:** if confidence < 80% on the bucket → `unclear`. Don't force-fit.

### Step 3 — Move + add frontmatter

For each classified file:

```bash
# Build destination path based on classification
DEST="<per table above>"

# Ensure destination directory exists
mkdir -p "$(dirname "$DEST")"

# Add minimal frontmatter if missing
if ! head -1 "$FILE" | grep -q "^---$"; then
  # Insert YAML frontmatter
  TMP=$(mktemp)
  cat > "$TMP" <<EOF
---
date: $(date +%Y-%m-%d)
type: $BUCKET
tags: [auto-filed]
filed_by: inbox-filer
source: $FILE
---

EOF
  cat "$FILE" >> "$TMP"
  mv "$TMP" "$DEST"
else
  # Already has frontmatter — just move
  mv "$FILE" "$DEST"
fi
```

### Step 4 — Wikilink to related notes (best-effort)

For each moved file, scan the body for:
- `[[Note Title]]` — already a wikilink, leave as-is
- Capitalized phrases that match existing note titles in the destination folder — convert to wikilinks
- `#tag` patterns — add to frontmatter tags array

**Skip if no clear matches.** Don't force connections.

### Step 5 — Update state file

```bash
# Write updated state
PROCESSED=$(cat /tmp/inbox-filer-processed.txt | jq -R . | jq -s .)
NEW_STATE="{\"last_run_at\": \"$(date -Iseconds)\", \"processed_files\": $PROCESSED}"
echo "$NEW_STATE" > ~/.mavis/state/inbox-filer.state.json
```

### Step 6 — Write daily log

Output to `~/.mavis/state/inbox-filer-YYYY-MM-DD.md`:

```markdown
---
date: YYYY-MM-DD
files_processed: <N>
---

# Inbox Filer Log — YYYY-MM-DD

## Filed
- `original-name.md` → `02 Notes/ideas/title.md` (idea)
- `original-name.md` → `02 Notes/articles/_pending_reaction/title.md` (article, no reaction)
- ...

## Left in inbox (unclear)
- `original-name.md` — reason

## Notes
- <any decisions, conflicts, or observations>
```

Mirror to `99 _system/logs/inbox-filer-YYYY-MM-DD.md`.

### Step 7 — Surface (silent unless issues)

If `files_processed > 5` OR `unclear count > 2`: Telegram notification.
Otherwise: silent. Next-Mavis reads the log on session start.

## Hard Constraints

1. **No destructive moves without trace.** Every move is `mv` (preserves content), original path logged in state file.
2. **Reaction discipline non-negotiable.** Articles without `## Reaction` NEVER go directly to `02 Notes/articles/`. They go to `_pending_reaction/` for explicit human attention.
3. **State file is append-only.** Never edit `processed_files` array in place — only append.
4. **Daily limit:** 50 files max per run. If exceeded, process first 50 alphabetically + flag remainder.
5. **No cross-team reads.** All paths are `~/MiniMax-Agent/` and `~/.mavis/`. Per ABSOLUTE SEPARATION rule.
6. **Mavis territory only.** Don't touch files outside the vault.

## Halt Conditions

- Inbox file unreadable (permissions, encoding) → skip file, log warning, continue
- Classification ambiguous (confidence < 80%) → leave in inbox, flag in output
- Daily count > 50 → process first 50, surface remainder count
- Same file stays in inbox for 3 consecutive days → move to `05 Archive/`, log "stale — auto-archived"
- Destination directory not writable → HALT, surface (config issue, not data issue)

## Failure Modes

| Failure | Detection | Recovery |
|---|---|---|
| State file corrupted | jq parse fails | Init fresh state, log "state reset" |
| File has frontmatter but wrong type | Frontmatter mismatch | Update type field, log change |
| Move fails (cross-device, permissions) | mv returns non-zero | Leave file in place, log error |
| Wikilink detection creates false positives | Self-audit on a sample | Accept noise, log |

## Cross-references

- Spec: `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/inbox-filer-2026-06-22.md`
- Companion (runs 06:00 CT): `~/.mavis/agents/mavis/crons/second-self-morning-brief.md` (surfaces what's in inbox)
- Reaction discipline: `~/MiniMax-Agent/02 Notes/articles/_discipline/REACTION-RULE.md`
- State file: `~/.mavis/state/inbox-filer.state.json`
- Daily log: `~/.mavis/state/inbox-filer-YYYY-MM-DD.md`
