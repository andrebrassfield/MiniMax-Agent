# Safety Halts — vault-daily-logger

The skill must HALT (not improvise) when any of these fire. The
"halt" means: stop, log the run, do not write.

## H1. Manual daily already exists

**Detection:** `01 Daily/YYYY-MM-DD.md` exists AND has ≥100 bytes
of body content (excluding frontmatter).

**Expected response:** Halt. Do not overwrite. The operator's
manual work is sacred. Log the run with
`outcome: skipped-manual-entry`. The next cron run will also halt.

This is the load-bearing rule. A non-manual daily is detectable
by the `tags: [auto-generated]` frontmatter, but the body-size
check is the durable detection: even if the tags are stripped, the
100-byte body threshold catches it.

## H2. Future date

**Detection:** The computed `date_today` is in the future (system
clock off, or the cron was triggered with an explicit future date).

**Expected response:** Halt. Surface the clock issue to the
operator. Log the run with `outcome: skipped-clock-skew`. Do not
generate a daily for a future date.

## H3. Date more than 7 days in the past

**Detection:** The operator specifies a backfill date >7 days
before today, OR the daily is genuinely missing for a >7-day-old
date (the gap is real, not a clock issue).

**Expected response:** Halt. The audit is weekly-cadence; older
gaps should be flagged, not silently backfilled. Surface the gap
to the operator: "01 Daily/2026-06-10.md is missing. The
audit-period threshold is 7 days; older gaps should be
backfilled manually, not by the cron." Log the run with
`outcome: skipped-too-old`.

## H4. Atomic write fails

**Detection:** The Python `os.replace` raises (filesystem full,
permission denied, disk error, etc.).

**Expected response:** Halt. The original file (if any) is
unchanged. Log the run with `outcome: error` and the exception
message. Surface to the operator. The cron should not retry
aggressively — the next run will hit the same error.

## H5. `01 Daily/` directory missing

**Detection:** The `01 Daily/` directory does not exist (the
vault was restructured, the directory was deleted, etc.).

**Expected response:** Halt. Surface the missing-directory error.
The cron should not auto-create the directory (that would be a
silent structural change). The operator must create the directory
and verify the vault structure.

## H6. Body size detection fails (file is binary or has no frontmatter)

**Detection:** The daily file exists but the body-extraction regex
fails (e.g., the file has no `---` frontmatter, or the file is
binary).

**Expected response:** Halt. Surface the file structure anomaly
to the operator. The skill does NOT interpret a malformed file as
"empty" — that would be a silent overwrite. Log the run with
`outcome: error` and the exception.

## Eval cases

| Halt | Input (mock state) | Expected behavior |
|---|---|---|
| H1 | daily exists, body 250 bytes | Halt, no overwrite |
| H2 | date is 2026-06-19, today is 2026-06-17 | Halt, clock skew |
| H3 | date is 2026-06-05, today is 2026-06-17 (>7 days) | Halt, surface gap |
| H4 | os.replace raises OSError | Halt, log error |
| H5 | `01 Daily/` does not exist | Halt, surface missing dir |
| H6 | daily is binary content | Halt, surface anomaly |
