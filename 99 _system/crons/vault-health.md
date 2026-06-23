---
name: vault-health
schedule: 0 23 1-7 * 0
timezone: America/Chicago
session:
  mode: new
  keepSessions: 3
---

# Vault Health — Monthly Audit

Monthly audit of the vault — finds orphan notes (no incoming links), stalled projects (no updates in 60+ days), inconsistent tags, missing frontmatter, broken wikilinks, oversized files, duplicate filenames. Produces a maintenance checklist.

Fires the first Sunday of each month at 23:00 CT. The article's "Vault Health Check" workflow, automated.

## Procedure

### Step 1 — Run the 7 audit checks

```bash
VAULT=~/MiniMax-Agent
DATE=$(date +%Y-%m-%d)
REPORT=~/MiniMax-Agent/00\ Inbox/vault-health-$DATE.md
LOG=~/.mavis/state/vault-health-history.jsonl

echo "--- Vault Health Audit: $DATE ---" > "$REPORT"
```

**Check 1: Orphan notes (no incoming wikilinks)**

```bash
echo "## 1. Orphan Notes (no incoming links)" >> "$REPORT"
# Find all .md files, check for any [[link]] pointing to them
find "$VAULT" -name "*.md" -type f -not -path "*/node_modules/*" -not -path "*/.obsidian/*" -not -path "*/.git/*" 2>/dev/null | while read f; do
  BASENAME=$(basename "$f" .md)
  # Search for [[$BASENAME]] or [[$BASENAME| in any other file
  COUNT=$(grep -rl "\[\[$BASENAME" "$VAULT" --include="*.md" 2>/dev/null | grep -v "$f" | wc -l | tr -d ' ')
  if [ "$COUNT" = "0" ]; then
    echo "- $f" >> "$REPORT"
  fi
done
```

**Check 2: Stalled projects (no updates in 60+ days)**

```bash
echo "## 2. Stalled Projects (no update in 60+ days)" >> "$REPORT"
find "$VAULT/03 Projects" -maxdepth 2 -name "*.md" -type f -mtime +60 2>/dev/null | while read f; do
  echo "- $f ($(stat -f '%Sm' "$f"))" >> "$REPORT"
done
```

**Check 3: Missing frontmatter**

```bash
echo "## 3. Missing Frontmatter" >> "$REPORT"
find "$VAULT" -name "*.md" -type f -not -path "*/node_modules/*" -not -path "*/.obsidian/*" -not -path "*/.git/*" 2>/dev/null | while read f; do
  if ! head -1 "$f" | grep -q "^---$"; then
    echo "- $f" >> "$REPORT"
  fi
done
```

**Check 4: Broken wikilinks (target doesn't exist)**

```bash
echo "## 4. Broken Wikilinks" >> "$REPORT"
grep -rohE '\[\[[^]]+\]\]' "$VAULT" --include="*.md" 2>/dev/null | sort -u | while read link; do
  TARGET=$(echo "$link" | sed -E 's/\[\[([^]|]+)(\|.*)?\]\]/\1/')
  # Check if a file with this name exists anywhere
  if ! find "$VAULT" -name "$TARGET.md" -not -path "*/node_modules/*" 2>/dev/null | head -1 | grep -q .; then
    echo "- [[$TARGET]] (no file found)" >> "$REPORT"
  fi
done
```

**Check 5: Oversized files (>50KB)**

```bash
echo "## 5. Oversized Files (>50KB)" >> "$REPORT"
find "$VAULT" -name "*.md" -type f -size +50k -not -path "*/node_modules/*" -not -path "*/.obsidian/*" 2>/dev/null | while read f; do
  SIZE=$(stat -f '%z' "$f")
  echo "- $f ($SIZE bytes)" >> "$REPORT"
done
```

**Check 6: Duplicate filenames (same name in multiple folders)**

```bash
echo "## 6. Duplicate Filenames" >> "$REPORT"
find "$VAULT" -name "*.md" -type f -not -path "*/node_modules/*" -not -path "*/.obsidian/*" -not -path "*/.git/*" 2>/dev/null | xargs -I{} basename {} .md 2>/dev/null | sort | uniq -c | awk '$1 > 1 {print "  - " $0}' >> "$REPORT"
```

**Check 7: Stale tags (tags used only once)**

```bash
echo "## 7. Stale Tags (used only once)" >> "$REPORT"
grep -rohE '#[a-zA-Z][a-zA-Z0-9_-]+' "$VAULT" --include="*.md" 2>/dev/null | sort | uniq -c | sort -n | awk '$1 == 1 {print "  - " $2}' | head -20 >> "$REPORT"
```

### Step 2 — Compute summary statistics

```bash
echo "## Summary" >> "$REPORT"
echo "- Total .md files: $(find "$VAULT" -name "*.md" -type f -not -path "*/node_modules/*" -not -path "*/.obsidian/*" -not -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' ')" >> "$REPORT"
echo "- Total wikilinks: $(grep -rohE '\[\[[^]]+\]\]' "$VAULT" --include="*.md" 2>/dev/null | wc -l | tr -d ' ')" >> "$REPORT"
echo "- Total tags: $(grep -rohE '#[a-zA-Z][a-zA-Z0-9_-]+' "$VAULT" --include="*.md" 2>/dev/null | sort -u | wc -l | tr -d ' ')" >> "$REPORT"
echo "- Active projects (modified in last 30d): $(find "$VAULT/03 Projects" -maxdepth 2 -name "*.md" -type f -mtime -30 2>/dev/null | wc -l | tr -d ' ')" >> "$REPORT"
```

### Step 3 — Append to history log

```bash
# Append one JSON record per run
RECORD="{\"date\":\"$DATE\",\"report\":\"$REPORT\",\"orphan_count\":$(grep -c '^- ' "$REPORT" 2>/dev/null || echo 0)}"
echo "$RECORD" >> "$LOG"
```

### Step 4 — Mirror to vault

```bash
mkdir -p ~/MiniMax-Agent/99\ _system/health
cp "$REPORT" ~/MiniMax-Agent/99\ _system/health/vault-health-$DATE.md
```

### Step 5 — Surface (silent unless issues)

```bash
# Count issues per category
TOTAL_ISSUES=$(grep -c "^- " "$REPORT" 2>/dev/null || echo 0)

if [ "$TOTAL_ISSUES" -gt 20 ]; then
  # High issue count — Telegram notification
  echo "Vault Health: $TOTAL_ISSUES issues found. See 00 Inbox/vault-health-$DATE.md"
  # (Telegram send handled by cron daemon)
fi
```

If `TOTAL_ISSUES < 20`: silent. The report is on disk.

## Hard Constraints

1. **Read-only against vault content.** This cron READS files, never modifies them. The output report is the only write.
2. **Append-only history log.** `~/.mavis/state/vault-health-history.jsonl` is append-only. Never edit past entries.
3. **Time budget.** Cron should complete in <5 minutes. If it exceeds, partial report with `-INCOMPLETE-` flag.
4. **Output size limit.** If report exceeds 1MB, truncate per-category to top 100 issues.
5. **Mavis territory only.** All paths are `~/MiniMax-Agent/` and `~/.mavis/`. No cross-team reads.

## Halt Conditions

- Vault unreadable → HALT, surface
- Audit exceeds 5 minutes runtime → partial report, flag incomplete
- Output file > 1MB → truncate per category, flag
- Permission denied on any folder → skip that folder, log warning, continue

## Failure Modes

| Failure | Detection | Recovery |
|---|---|---|
| Audit takes >5 min | Runtime check | Partial report, flag incomplete |
| Report > 1MB | Size check | Truncate per category |
| Vault mounted read-only | fs write test | Skip output write, log |
| Tag regex matches weird strings | Sample review | Accept noise, log |

## Cross-references

- Spec: `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/vault-health-2026-06-22.md`
- Companion (daily): `second-self-morning-brief`, `second-self-contradiction`, `inbox-filer`
- Companion (weekly): `second-self-weekly-deep`
- State file: `~/.mavis/state/vault-health-history.jsonl`
- Report directory: `~/MiniMax-Agent/00 Inbox/vault-health-*.md` (created by this cron)
- Vault mirror: `99 _system/health/vault-health-*.md`
