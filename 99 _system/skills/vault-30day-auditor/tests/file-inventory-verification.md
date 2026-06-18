# File Inventory Verification — vault-30day-auditor

The eval suite verifies the file inventory + appendix
completeness + count consistency. The audit's claims must
match the disk.

## I1. files_in_window count matches `find | wc -l`

```bash
report="03 Projects/Mavis EA Design/reports/30-day-footprint-2026-06-17.md"

# Claimed count
claimed=$(grep "^files_in_window:" "$report" | awk '{print $2}')

# Actual count (re-run the audit's find)
actual_daily=$(find "$VAULT/01 Daily" -type f -mtime -30 2>/dev/null | wc -l | tr -d ' ')
actual_projects=$(find "$VAULT/03 Projects" -type f -mtime -30 2>/dev/null | wc -l | tr -d ' ')
actual=$((actual_daily + actual_projects))

if [ "$claimed" -ne "$actual" ]; then
  echo "FAIL: files_in_window mismatch (claimed=$claimed, actual=$actual)"
else
  echo "PASS: count matches ($claimed files)"
fi
```

**Failure mode this catches:** the report's count is stale
or fabricated. The audit must reflect the disk at the
time of writing.

## I2. Daily notes cadence dates are accurate

```bash
# Extract the "days with notes" list from the report
claimed_dates=$(awk '/^## 3\. Daily notes cadence/,/^## 4\./' "$report" \
  | grep -oE "20[0-9]{2}-[0-9]{2}-[0-9]{2}" | sort)

# Actual dates (from the daily notes dir)
actual_dates=$(find "$VAULT/01 Daily" -type f -mtime -30 -name "*.md" \
  | xargs -I{} basename {} .md 2>/dev/null | sort)

# Compare
if [ "$claimed_dates" != "$actual_dates" ]; then
  echo "FAIL: dates mismatch"
  diff <(echo "$claimed_dates") <(echo "$actual_dates")
else
  echo "PASS: dates match"
fi
```

**Failure mode this catches:** the report's daily notes
cadence is wrong. The dates must come from `ls`, not
recap.

## I3. Top-N project counts match the appendix

```bash
# For each project in section 4, count files in the appendix
for project in $(awk '/^## 4\. Active project pipelines/,/^## 5\./' "$report" \
  | grep -E "^\d+\. \*\*" | awk -F'\\*\\*' '{print $2}'); do
  # Extract claimed count
  claimed=$(awk "/^## 4\\. Active project pipelines/,/^## 5\\./" "$report" \
    | grep "^\d\+\. \*\*$project\*\*" | head -1 | grep -oE "[0-9]+ files")

  # Count in appendix
  appendix_count=$(awk '/^## 9\. Appendix/,/^$/' "$report" \
    | grep -c "/$project/")

  echo "$project: claimed=$claimed, appendix count=$appendix_count"
done
```

**Failure mode this catches:** the report's project
rankings don't match the appendix. The audit must be
internally consistent.

## I4. Every appendix file is in the inventory

```bash
# The appendix should list every file from the `find` output
# (in window, in target dirs)

# Get the file paths from the appendix
appendix_paths=$(awk '/^## 9\. Appendix/,EOF' "$report" | grep -oE "/.+\.md" | sort)

# Get the file paths from the actual find
actual_paths=$(find "$VAULT/01 Daily" "$VAULT/03 Projects" -type f -mtime -30 | sort)

# Compare counts
appendix_count=$(echo "$appendix_paths" | wc -l | tr -d ' ')
actual_count=$(echo "$actual_paths" | wc -l | tr -d ' ')

if [ "$appendix_count" -ne "$actual_count" ]; then
  echo "FAIL: appendix count mismatch (appendix=$appendix_count, actual=$actual_count)"
else
  echo "PASS: appendix is complete ($appendix_count files)"
fi
```

**Failure mode this catches:** the appendix is missing
files. The audit must be exhaustive.

## I5. The report is at the correct path

```bash
# The report should be at:
# 03 Projects/Mavis EA Design/reports/30-day-footprint-YYYY-MM-DD.md
# where YYYY-MM-DD is today's date

expected_path="$VAULT/03 Projects/Mavis EA Design/reports/30-day-footprint-$(date +%Y-%m-%d).md"

if [ ! -f "$expected_path" ]; then
  echo "FAIL: report not at expected path: $expected_path"
fi
```

**Failure mode this catches:** the report is at the wrong
path. The convention is `reports/30-day-footprint-YYYY-MM-DD.md`.

## I6. Date in the filename matches the generation date

```bash
# The YYYY-MM-DD in the filename should match today's date
# (the audit is "30-day footprint as of today")

filename_date=$(basename "$report" | grep -oE "20[0-9]{2}-[0-9]{2}-[0-9]{2}")
today=$(date +%Y-%m-%d)

if [ "$filename_date" != "$today" ]; then
  echo "WARN: filename date $filename_date != today $today"
fi
```

**Failure mode this catches:** the report is named for
yesterday's audit but the content is today's. Date
mismatch.
