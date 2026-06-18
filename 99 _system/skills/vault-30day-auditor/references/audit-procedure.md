# Audit Procedure — vault-30day-auditor

The 9-step procedure with bash commands. The SKILL.md only
carries the 9-section report shape + procedure overview +
hard constraints. The actual bash pipeline lives here (the
deterministic layer).

---

## Step 1: Verify ground truth

Confirm the vault root and target dirs exist.

```bash
VAULT="/Users/brassfieldventuresllc/MiniMax-Agent"
[ -d "$VAULT" ] || { echo "HALT: vault root not found: $VAULT" >&2; exit 1; }
[ -d "$VAULT/01 Daily" ] || { echo "HALT: target dir missing: 01 Daily/" >&2; exit 1; }
[ -d "$VAULT/03 Projects" ] || { echo "HALT: target dir missing: 03 Projects/" >&2; exit 1; }
```

If either target dir is missing, HALT and surface. The
audit cannot proceed without these.

## Step 2: Establish the 30-day window

```bash
# Today
T=$(date "+%Y-%m-%d")
# T-30 (macOS)
T_MINUS_30=$(date -v-30d "+%Y-%m-%d")
# The window is [T-30, T] inclusive
echo "Window: [$T_MINUS_30, $T]"
```

Record both in the report header.

## Step 3: Inventory files modified in the window

```bash
# Primary target dirs
DAILY=$(find "$VAULT/01 Daily" -type f -mtime -30 2>/dev/null)
PROJECTS=$(find "$VAULT/03 Projects" -type f -mtime -30 2>/dev/null)

# Also pull 00 Inbox/ (out of target scope but operationally important)
INBOX=$(find "$VAULT/00 Inbox" -type f -mtime -30 2>/dev/null)

# Counts
DAILY_COUNT=$(echo "$DAILY" | grep -c . 2>/dev/null || echo 0)
PROJECTS_COUNT=$(echo "$PROJECTS" | grep -c . 2>/dev/null || echo 0)
INBOX_COUNT=$(echo "$INBOX" | grep -c . 2>/dev/null || echo 0)
TOTAL=$((DAILY_COUNT + PROJECTS_COUNT))

echo "Files in window: $TOTAL (01 Daily: $DAILY_COUNT, 03 Projects: $PROJECTS_COUNT)"
echo "00 Inbox: $INBOX_COUNT"
```

The line count and the file list are the basis for every
claim in the report.

## Step 4: Project ranking

Count modifications per project dir.

```bash
PROJECT_RANKING=$(echo "$PROJECTS" | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn)
echo "Project ranking (top 10):"
echo "$PROJECT_RANKING" | head -10
```

This gives a ranked list of active projects. The top 5 (by
count) are the "active pipelines" — read their top files in
Step 5.

## Step 5: Read the top files

For each of the top-N projects AND for the daily notes:

```bash
# For each top project, find the most-recently-modified file
for project in $(echo "$PROJECT_RANKING" | head -5 | awk '{print $2}'); do
  latest=$(find "$project" -type f -mtime -30 | xargs ls -t 2>/dev/null | head -1)
  echo "Reading: $latest"
  # Read the file in full (or chunked if very large)
done
```

**Read budget:** at most ~20 files in full. If a top
project has too many large files, sample (read the most
recent + 1-2 more, skip the rest).

Topics are extracted from file **content**, not file name.
A file called "research-brief.md" with content about "M3
eval lab" gets categorized under M3 eval lab, not research.

## Step 6: Daily notes cadence

```bash
# List all daily notes in the window
NOTES=$(find "$VAULT/01 Daily" -type f -mtime -30 -name "*.md" 2>/dev/null)

# Extract the dates
DATES=$(echo "$NOTES" | sed 's|.*/||' | sed 's|\.md$||' | sort)

# Days with notes
echo "Days with notes: $DATES"

# Days missing (between T-30 and T)
ALL_DATES=$(seq 0 30 | xargs -I{} date -v-{}d "+%Y-%m-%d")
MISSING=$(comm -23 <(echo "$ALL_DATES" | sort) <(echo "$DATES" | sort))
echo "Days missing: $MISSING"

# Longest gap
# (compute the maximum gap between consecutive dates)
```

This surfaces the daily-notes habit's health. A 6-day gap
at the end of the window is a finding.

## Step 7: Synthesize

In-session synthesis. Three sections:

1. **Core topics** — subjects that appear in 2+ files across
   the window. Examples: "X content engine", "Mavis role
   design", "fleet architecture", "agent disease model",
   "skill codification". List each topic with the files it
   appears in.
2. **Repetitive manual tasks** — workflows that show up in
   3+ files. Examples from prior runs: "ledger append",
   "skill codification", "weekly review".
3. **Active pipelines** — projects with file activity,
   ranked by modification count. The top 5 are the most
   active.

The synthesis must be **defensible**: every claim has a file
reference in the appendix.

**The synthesis happens in this session, not dispatched.**
Per hard constraint #3, dispatching to x-researcher would
be a domain mismatch.

## Step 8: Write the report

```bash
REPORT_DIR="$VAULT/03 Projects/Mavis EA Design/reports"
mkdir -p "$REPORT_DIR"
REPORT_PATH="$REPORT_DIR/30-day-footprint-$(date +%Y-%m-%d).md"
```

Use the `Write` tool. Follow the 9-section report template
(see `references/report-template.md`). The report is one
file, one session's worth of synthesis — do not append to a
prior report.

## Step 9: Return summary to operator

Send a short summary:

- Report path
- Total files in window
- Top 3 active projects
- Top 3 core topics
- The single most-obvious automation candidate
- Any halt conditions or window edge cases

## Decision log entries (the discipline)

The Decision Log captures any non-obvious choices. Common
entries:

- **Path correction:** "Operator specified `Mavis-EA-Design`
  but actual path is `Mavis EA Design` (with space). Used
  actual path."
- **Window partial:** "Vault's oldest file is 12 days old
  (vault created 2026-06-05). Window coverage is 12 days,
  not 30."
- **Domain decision:** "Synthesis done in-session, not
  dispatched to x-researcher (domain mismatch — that's an
  X content research agent, not a vault activity agent)."
- **Read budget hit:** "Top project has 47 files; sampled
  top 3 by mtime per read-budget constraint."

If no decisions were non-obvious, the Decision Log is
`(none)`.
