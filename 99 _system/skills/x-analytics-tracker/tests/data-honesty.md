# Data Honesty — x-analytics-tracker

The load-bearing rule: if a metric is obscured, mark it "unclear."
NEVER hallucinate a number. The eval suite verifies the discipline.

## T1. Obscured metric → "unclear" (not guessed)

**Setup:** A metric widget in the snapshot is not rendered, shows
"—", shows "0", shows a spinner, or is gated behind a "View more"
click.

**Verification:** the cell in the dashboard is the literal string
"unclear" (not "0", not "N/A", not a guessed value).

**Failure mode this catches:** the skill guessed at a value (e.g.,
saw "0" and reported it as 0 instead of "unclear" — but 0 might
mean "metric hidden" or "metric not yet loaded").

## T2. Partial run still appended

**Setup:** The skill runs but only got metrics for 3 of 5 posts in
the window (e.g., 2 posts had sensitive-content warnings and the
skill skipped them).

**Verification:** the section is still appended to the dashboard.
The "unclear" count is non-zero. The Operator notes explain the
skip.

**Failure mode this catches:** the skill halted on the partial
capture and didn't write anything. The dashboard has a gap, not a
record.

## T3. All-unclear run still appended (with note)

**Setup:** X is down, the bridge is offline, the snapshot shows only
"X is currently down" or similar.

**Verification:** the section is appended with all "unclear" cells.
The Operator notes explicitly say "no usable data this run — bridge
may be offline / X may be down / login may be required."

**Failure mode this catches:** the skill didn't write anything, and
Andre can't distinguish "no data this run" from "skill didn't run."

## T4. Brain write skipped when dashboard write fails

**Setup:** Dashboard write fails (e.g., file is read-only).

**Verification:** the dashboard write failure is HALT (operator must
fix permissions). The brain write is NOT attempted (we don't want
the brain updated with metrics the dashboard didn't capture — that
would create a mismatch).

**Failure mode this catches:** the skill wrote to the brain even
though the dashboard failed, creating inconsistent state between
human-readable and machine-readable.

## T5. Spinner cell → "unclear" (not "0")

**Setup:** A metric widget shows a loading spinner (X's analytics
UI sometimes shows a spinner when a metric hasn't loaded yet).

**Verification:** the cell is "unclear" (spinner = "hadn't loaded
yet," not "0").

**Failure mode this catches:** the skill reported "0" for a metric
that was actually loading — the next run would have shown the real
value, but the run was already committed.
