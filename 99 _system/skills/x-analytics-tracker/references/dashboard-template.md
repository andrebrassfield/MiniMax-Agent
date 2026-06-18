# Dashboard Template — x-analytics-tracker

The markdown section appended to `99 _system/dashboards/x-metrics-dashboard.md`.

## Initial file header (created on first run)

```markdown
---
type: dashboard
domain: x.com
account: @DreTheSalesGuy
created: YYYY-MM-DD
---

# X Metrics Dashboard — @DreTheSalesGuy

<!-- Auto-appended by x-analytics-tracker. Do not edit manually. -->
```

## Per-run section (appended on each run)

```markdown
---

## Run: YYYY-MM-DD HH:MM CT · window: last Nd

**Source:** https://analytics.x.com (and <N> individual post stat pages)
**Generator:** Mavis (x-analytics-tracker)

### Per-post metrics

| Post | Published | Impressions | Engagements | Bookmarks | Profile clicks | Likes | Retweets | Replies | Notes |
|------|-----------|-------------|-------------|-----------|----------------|-------|----------|---------|-------|
| [link](url) excerpt... | YYYY-MM-DD | 1234 | 56 | 7 | unclear | 12 | 3 | 2 | — |
| ... | | | | | | | | | |

### Aggregate
- Posts in window: N
- Total impressions: <sum or unclear>
- Avg impressions/post: <avg or unclear>
- Total engagements: <sum or unclear>
- Avg engagement rate: <engagements/impressions or unclear>

### Top 3 (by impressions)
1. <post link + one-line takeaway>
2. ...
3. ...

### Bottom 3 (by impressions)
1. ...
2. ...
3. ...

### Operator notes
- <any "unclear" cells, UI quirks, login-required metrics, etc.>
- <posts that need Andre's attention: high impressions but few replies → maybe the hook is strong but the CTA is missing>
- <posts with 0 impressions → maybe got suppressed; check for X policy issues>
```

## File growth pattern

The file is **append-only**. The skill never overwrites a prior section.
The dashboard grows linearly with each run. To find a specific run,
grep for `## Run: YYYY-MM-DD`.
