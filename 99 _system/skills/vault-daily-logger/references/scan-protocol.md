# Scan Protocol — vault-daily-logger

The find/awk/sort pipeline for extracting the day's technical
footprint from `03 Projects/`.

## The pipeline

```bash
# Step 1: Find files modified today
find "03 Projects" -type f -mtime 0 -not -name ".DS_Store" 2>/dev/null
```

`-mtime 0` matches files modified within the last 24 hours. This
is a wider window than "today" (it includes the previous evening's
late work). For a tighter window:

```bash
find "03 Projects" -type f -newermt "$(TZ=America/Chicago date +%Y-%m-%d)" -not -name ".DS_Store" 2>/dev/null
```

## Group by top-level project, count modifications

```bash
find "03 Projects" -type f -mtime 0 -not -name ".DS_Store" 2>/dev/null \
  | awk -F'/' '{print $3}' \
  | sort | uniq -c | sort -rn | head -5
```

This gives the top 5 project names by modification count. The
`awk -F'/'` extracts the third path component (the top-level
project name under `03 Projects/`).

## For each top-5 project, extract 2-3 key files

```bash
for project in <top-5-project-list>; do
    find "03 Projects/${project}" -type f -mtime 0 -not -name ".DS_Store" 2>/dev/null \
      | head -3
done
```

The "key files" heuristic: pick the 2-3 most-recently-modified, OR
the 2-3 most load-bearing by name match — files with "00 Overview"
or "README" or "agent.md" or "SKILL.md" are usually the structural
files. The cap at 3 is the "top project with 50+ files modified"
halt (per hard constraint #6).

## The 1-line summary per project

The 1-line summary is a synthesis of what the project is + what
changed. Heuristics:

- If the project has an `00 Overview.md` modified today, read the
  first 30 chars of the `## Goal` section
- If the project has a `README.md` modified today, read the first
  30 chars of the `## What this is` section
- If neither, fall back to a generic "active" line (e.g., "active
  project, N files modified today")

The summary is the LLM-callable step. The chief (Mavis) is the
natural LLM caller; a future automation could call a small model
for the summary. For the cron-driven case, the chief's daily note
IS the summary; the cron just generates the bullet structure.

## What "0 files modified today" looks like

```bash
find "03 Projects" -type f -mtime 0 -not -name ".DS_Store" 2>/dev/null
# Returns nothing
```

The skill still generates a daily with a single bullet: "No files
modified in `03 Projects/` today." This is a valid daily, even if
sparse — the operator gets a clear "nothing happened" signal
instead of a missing-file signal.
