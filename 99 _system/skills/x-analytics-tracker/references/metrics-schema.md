# Metrics Schema — x-analytics-tracker

Per-post metrics extracted from the X analytics dashboard + individual
post stat pages. Every cell has a source and a fallback ("unclear").

## The columns

| Column | Source | Fallback |
|---|---|---|
| Post | URL + first 200 chars of post text | — |
| Published | Date from analytics UI | "unclear" |
| Impressions | Analytics card | "unclear" |
| Engagements | Analytics card (total) | "unclear" |
| Bookmarks | Individual post stat page (sometimes gated) | "unclear" |
| Profile clicks | Individual post stat page (sometimes gated) | "unclear" |
| Likes | Individual post stat page | "unclear" |
| Retweets | Individual post stat page | "unclear" |
| Replies | Individual post stat page | "unclear" |
| Notes | Free-form (UI quirks, login-required, etc.) | — |

## When to mark "unclear"

- Metric widget not rendered in the snapshot
- Metric widget rendered but shows "—" / "0" / spinner
- Metric gated behind "View more" or "Show all" click (do not click — that's an interaction affordance)
- Snapshot was truncated mid-cell

A row of "unclear" cells is normal. Do not retry to "fill in" unclear
cells. The brain write should use `null` for "unclear" in JSON
(machine-readable); the dashboard uses the string "unclear" (human-readable).

## Engagement definitions (X's labels)

| X label | What it counts |
|---|---|
| Impressions | Times the post was rendered on a screen |
| Engagements | Total interactions (likes + retweets + replies + bookmarks + clicks) |
| Profile clicks | Clicks on the author's profile from this post |
| Likes | Heart icon |
| Retweets | Repost icon (excluding quote-tweets) |
| Replies | Reply icon (excluding thread self-replies) |
| Bookmarks | Bookmark icon (sometimes gated until N bookmarks) |

## Per-post drill-down (Step 6)

For the top 5 posts by impressions (or all if count is small), navigate
to the individual post stat page to extract:
- Profile clicks (often only on the per-post page, not the dashboard card)
- Bookmarks (sometimes gated)
- Detailed breakdown (replies, retweets, quote-tweets, likes as separate cells)

Close the drill-down tab when done. If a per-post page fails to load,
note in the row's Notes column and continue with dashboard data only.
