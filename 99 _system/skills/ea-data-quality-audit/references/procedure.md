# Procedure — ea-data-quality-audit

The 8-step procedure. The SKILL.md only carries the
high-level flow. The full detail lives here.

---

## Step 1: Pick the scope

All surfaces by default, or a specific surface if Andre
says so. The 6 surfaces:

| # | Surface | Path |
|---|---|---|
| 1 | Memory (canonical) | `~/.mavis/agents/mavis/memory/MEMORY.md` |
| 2 | Memory (topic files) | `~/.mavis/agents/mavis/memory/*.md` |
| 3 | Skills (agent home) | `~/.mavis/agents/mavis/skills/*/SKILL.md` |
| 4 | Skills (vault mirror) | `~/MiniMax-Agent/99 _system/skills/*/SKILL.md` |
| 5 | Vault | `~/MiniMax-Agent/01 Daily/`, `02 Notes/`, `03 Projects/` |
| 6 | Kanban | `~/.mavis/kanban.db` (sqlite) |

## Step 2: Run sub-step 1 (inventory)

```bash
# Memory canonical
wc -l ~/.mavis/agents/mavis/memory/MEMORY.md

# Memory topic files
for f in ~/.mavis/agents/mavis/memory/*.md; do
  head -3 "$f" | tail -1
  wc -c "$f"
done

# Skills agent home
for d in ~/.mavis/agents/mavis/skills/*/; do
  if [ -f "$d/SKILL.md" ]; then
    name=$(basename "$d")
    head -3 "$d/SKILL.md" | tail -1  # description line
    wc -l "$d/SKILL.md"
  fi
done

# Skills vault mirror (must be in sync per X-Content-Engine rule)
for d in ~/MiniMax-Agent/99\ _system/skills/*/; do
  if [ -f "$d/SKILL.md" ]; then
    name=$(basename "$d")
    wc -l "$d/SKILL.md"
  fi
done

# Vault (last 30 days)
find ~/MiniMax-Agent/01\ Daily ~/MiniMax-Agent/02\ Notes ~/MiniMax-Agent/03\ Projects -type f -mtime -30

# Kanban (last 30 days activity)
sqlite3 ~/.mavis/kanban.db "SELECT * FROM tickets WHERE updated_at > datetime('now', '-30 days')"
```

Disk hits only. No "I think there's an entry that
says X" — show the file:line.

## Step 3: Run sub-step 2 (filter)

For each entry in the inventory, apply the 5 filter
criteria from `5-sub-steps.md` §2:

- Harmful (memory contradicts Andre's later notes)
- Off-topic (topic file >60 days untouched)
- Personal data (PII, credentials, API keys)
- Stale claims (dated state claims >30 days old)
- Duplicates with drift (same fact in 3+ places, different
  wording)

Output: deletion/rewrite list with file:line references.

## Step 4: Run sub-step 3 (dedupe)

For each candidate dedup (3 levels: by file, by topic, by
line), use the tools from `5-sub-steps.md` §3:

```bash
# Find candidates
find ~/.mavis/agents/mavis/memory -type f -name "*.md" | xargs grep -l "<key phrase>"

# Identify drift
diff <file1> <file2>
```

**Read with intent** before merging. Two entries that
look the same may be two facets of the same claim.

Output: dedup map — for each duplicated claim, the
canonical file + links to update.

## Step 5: Run sub-step 4 (quality-score)

For each remaining entry, score it HIGH / MEDIUM / LOW /
DEAD per `5-sub-steps.md` §4. Apply the quality signals
(referenced in 30d, verifiable against disk, date still
relevant, contradicted by newer entry).

Output: per-entry score table with action.

## Step 6: Run sub-step 5 (balance)

Compare the corpus distribution to Andre's actual work
mix (use `vault-30day-auditor` for the baseline). Check
4 dimensions from `5-sub-steps.md` §5:

- Memory vs skills vs vault vs kanban
- Domain coverage
- Temporal balance
- Rule vs example vs context

Output: balance report — current distribution vs target.

## Step 7: Aggregate to the report

Use the template in `references/report-template.md`.
Prioritize the recommended actions. Top 3 should be
doable in one session.

## Step 8: Decide action

- **Cron run:** write the report to
  `03 Projects/Mavis EA Design/reports/data-quality-audit-YYYY-MM-DD.md`
  and notify Andre via the daily brief callout.
- **On-demand run:** present the report and ask Andre for
  go-ahead on the actions. Don't auto-apply.

The audit is read-only. Fixes are a separate step, owned
by the chief (e.g., `ea-skill-evolution` for skill
mutations, manual edit for memory entries).
