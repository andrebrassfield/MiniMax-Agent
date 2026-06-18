# Edge Cases — vault-daily-logger

Test cases for the non-halt edge cases the skill handles gracefully.
Each is a scenario the skill recovers from without operator
intervention.

## E1. 0 files modified today

**Scenario:** The `find` returns nothing. The operator didn't touch
`03 Projects/` today (e.g., a Sunday rest day).

**Expected response:** Generate a daily with a single bullet: "No
files modified in `03 Projects/` today." The optional stubs are
empty. Log the run with `files_scanned: 0`. This is a valid daily,
even if sparse.

## E2. Single project, 50+ files modified

**Scenario:** A large refactor touches 50+ files in one project (the
5-bullet cap means 1 bullet for this project).

**Expected response:** Generate the daily with 1 bullet for the
single project. The bullet's "key files" list is capped at 3 (per
hard constraint #6). The summary is the load-bearing element, not
the file list.

## E3. Top project has 0 actual modifications (counted via find)

**Scenario:** The find returns files in a project, but the count is
inflated by transient files (build artifacts, lock files, etc.).

**Expected response:** The bullet's count is the file count from
find, regardless of the file type. The summary is the load-bearing
element — if the summary is "no real changes," the bullet's count
is informational only.

## E4. Cron runs twice in one day (operator-triggered + scheduled)

**Scenario:** The 18:00 CT cron runs, then the operator triggers
the skill manually 2 hours later (to backfill after a late edit).

**Expected response:** The first run generates the daily. The
second run sees the daily exists with body > 100 bytes (the
auto-generated one) and halts with `skipped-manual-entry`. The
operator can manually edit the auto-generated daily to add
context, but the cron won't overwrite it.

## E5. Day is a sparse day (1-2 files modified)

**Scenario:** The operator touched 1-2 files in 1 project. The
5-bullet cap means 1 bullet for this project.

**Expected response:** Generate the daily with 1 bullet. The
summary is the load-bearing element, even if sparse. The optional
stubs are present and empty.

## E6. The cron runs but the vault is in a weird state (mid-sync, partial commits)

**Scenario:** The `find` returns files that are mid-commit (e.g.,
a `git add` happened but the commit didn't).

**Expected response:** The find returns the file as modified. The
bullet includes the file. The summary is the load-bearing element
— if the summary is "mid-commit, no real changes," the bullet's
count is informational only.

## E7. Time zone edge case (CT vs UTC)

**Scenario:** The cron runs at 18:00 CT, but the operator is in a
different time zone. The daily's "date" should be CT, not UTC.

**Expected response:** The `date_today` is computed with
`TZ=America/Chicago date "+%Y-%m-%d"`. The `run_at` timestamp is
also in CT. The optional stubs and "Notes for the chief" section
note the timezone explicitly. This is consistent across all
operator locations — the daily is always CT-anchored.

## E8. The 5-bullet cap is hit with 10+ projects active

**Scenario:** The operator touched files in 10 different projects
today. The find returns files from all 10.

**Expected response:** The top 5 by file count are bulleted. The
remaining 5 are noted in the "Notes for the chief" section as
"also active today: <project list>." The operator can promote a
bullet to manual context if they want to.
