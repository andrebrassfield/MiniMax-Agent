# Window Formats — x-analytics-tracker

The X analytics dashboard has a date-range selector. The skill accepts
natural-language window specifiers and translates them to the
date-range picker.

## Accepted formats

| User input | Parsed window |
|---|---|
| "last 7 days" / "this week" | 7d |
| "last 30 days" / "this month" | 30d |
| "yesterday" | 1d |
| "14 days" / "last 14 days" | 14d |
| "since YYYY-MM-DD" | custom range (from that date to today) |
| "between YYYY-MM-DD and YYYY-MM-DD" | custom range |

## Default

7 days. The dashboard refreshes daily; 7d is the natural cadence for
the X-Content-Engine feedback loop (per `agents/feedback-loop.md`).

## Ceiling

30 days. Beyond 30 days, X's analytics UI changes behavior (some
metrics truncate, some are not aggregated). If Andre asks for >30d,
suggest splitting into 2-3 runs of 30d windows.

## Custom range picker

When the window is custom (operator specified a date or range), the
skill clicks the date-range selector → "Custom range" → enters the
dates → "Apply". The X UI re-renders with the custom range data.

## The 50-post cap

X analytics shows up to 50 posts in a window. If the window would
return >50 posts, the skill halts and asks the operator to narrow.
This is the mass-scrape guard, not a window-format constraint. Full
halt behavior in `tests/safety-halts.md#H5`.
