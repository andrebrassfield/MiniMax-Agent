# 4-Step Procedure — ea-weekly-connections

The 4-step procedure with detailed sub-procedures. The
SKILL.md only carries the 4-step list. The actual steps
live here.

---

## Step 1: Surface pull (the 5 surfaces, in order)

Pull from these 5 surfaces, in this order. Each surface
is a deterministic read, not a synthesis. Read what's
there, don't editorialize.

### Surface 1: Daily notes

```bash
# Last 7 entries, sorted by mtime
DAILY=$(find ~/MiniMax-Agent/01\ Daily -type f -mtime -7 -name "*.md" 2>/dev/null | xargs ls -t | head -7)

for note in $DAILY; do
  date=$(basename "$note" .md)
  echo "Daily note: $date"
  # Extract top 3-5 non-routine entries
  grep -E "^- |^[0-9]+\\." "$note" | head -5
done
```

**What to extract:** top 3-5 non-routine entries per
day, the date stamp, any links to other surfaces.

### Surface 2: Kanban moves

```bash
# Read-only mirror, Mavis↔Hermes separation in effect
KANBAN_DIR="$HOME/.hermes/kanban/"

# Last 7 days of kanban moves
find "$KANBAN_DIR" -type f -mtime -7 2>/dev/null

# Cross-team tags, escalations
grep -rE "(cross-team|escalat|@Hermes|@OpenClaw)" "$KANBAN_DIR" 2>/dev/null | head -10
```

**What to extract:** Cards that moved from `pending` →
`in_progress` or `done`, any cards with cross-team tags,
any escalations.

### Surface 3: Worker outputs

```bash
# Last 7 days across all project dossiers/queue/reports
for project in ~/MiniMax-Agent/03\ Projects/*/; do
  for sub in dossiers queue reports; do
    if [ -d "$project/$sub" ]; then
      find "$project/$sub" -type f -mtime -7 2>/dev/null
    fi
  done
done
```

**What to extract:** Completed dispatches, briefs
produced, verification verdicts, audit outputs.

### Surface 4: Memory appends

```bash
# Last 30 memory entries
mavis memory tail --limit 30
```

**What to extract:** New rules, corrections, lessons
that haven't yet been codified into a topic file.

### Surface 5: Skill activity

```bash
# Last 7 days of skill edits (agent home + vault mirror)
ls -lt ~/.mavis/agents/mavis/skills/*/SKILL.md 2>/dev/null | head -10
ls -lt ~/MiniMax-Agent/99\ _system/skills/*/SKILL.md 2>/dev/null | head -10
```

**What to extract:** New skills, edits to existing
skills, the skill-build-monitor's most recent tick
report.

**Discipline:** the surface pull is **read-only** and
**deterministic**. No summarizing, no "the gist is..."
— list the items with their dates and source paths. The
cross-domain detection happens in Step 2, not here.

**Output of Step 1:** a 5-section raw list, ~30-60
items total. Each item: date, surface, 1-line
description, source path.

---

## Step 2: Cross-domain pattern detection

For each item in the surface pull, ask: **does this
connect to anything from another surface?** A
"connection" requires ≥2 unrelated surfaces sharing an
underlying pattern. Full 4 connection types + 3
anti-patterns in `4-connection-types.md`.

**Output of Step 2:** 3-5 connections, each with:
- Title (5-10 words, descriptive)
- Surfaces (which ≥2 surfaces the connection spans)
- Underlying pattern (1-2 sentences)
- Evidence (file paths / line numbers / dates)
- What this means for Andre (1-2 sentences, EA voice)
- What to do about it (1-2 sentences, or "no action —
  informational")

---

## Step 3: Connection brief drafting

Format the 3-5 connections into a 1-page brief. The
brief is **dense**, not exhaustive. Andre should be able
to read it in 5 minutes and get the signal.

Full template in `brief-template.md`. Structure:

```markdown
# Weekly Connections — Week NN, YYYY (MM-DD to MM-DD)

> Generated: <YYYY-MM-DD HH:MM CT> | Author: Mavis (EA) | Window: last 7 days
> Connections surfaced: <N> | Surfaces scanned: 5 (daily, kanban, workers, memory, skills)

## Connection 1: <title>

**Surfaces:** <surface 1>, <surface 2>, ...
**Pattern:** <1-2 sentences>
**Evidence:** <file paths / dates>
**What this means for Andre:** <synthesis>
**What to do:** <action or "no action — informational">

## Connection 2: ...

## What's not on this list (deliberate omissions)

<1-2 sentences on what Mavis considered and rejected, so
Andre can audit the selection.>

## Open threads

<Any patterns that almost-connected but didn't quite —
keep for next week.>
```

**Discipline:**
- 3-5 connections. Not 2 (insufficient), not 7+ (loses
  signal-to-noise).
- Each connection must span ≥2 surfaces.
- "What this means for Andre" in **EA voice** —
  synthesis + why.
- "What to do" must be concrete. "Consider" / "monitor"
  are not actions.

---

## Step 4: Output + handoff

**Write to:** `02 Notes/connections/YYYY-WNN-synthesis.md`
(WNN = ISO week number, e.g., `2026-W25-synthesis.md`).

**Cron integration:** the cron `ea-weekly-connections`
is scheduled Sunday 18:00 CT. On tick:
1. Run the surface pull (Step 1)
2. Run the cross-domain detection (Step 2)
3. Draft the brief (Step 3)
4. Write the file (Step 4)
5. Surface to Andre via `<mavis-progress>` tag with
   the file path

**Manual handoff:** if Andre asks for the weekly
synthesis mid-week, run the same 4 steps with a 7-day
window ending at the request time, not Sunday.

**Halt conditions:**
- <3 items in the surface pull → too little activity,
  skip the brief, log "weekly skipped: <3 items in pull"
- All items are from a single surface → no cross-domain
  patterns possible, skip the brief, log the reason
- The vault has been heavily edited (git pull, obsidian
  sync) in the last 24h → run the brief anyway, but
  flag the recency caveat in the header
