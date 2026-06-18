---
name: x-analytics-tracker
description: |
  Pull X post performance metrics (Impressions, Engagements, Bookmarks,
  Profile Clicks, Likes, Retweets, Replies) for @DreTheSalesGuy posts over
  the last 7-30 days via the real Chrome session, then write to TWO
  destinations: the human-readable dashboard at
  `99 _system/dashboards/x-metrics-dashboard.md` AND the machine-readable
  `performance_log` array in `03 Projects/X-Content-Engine/memory/content_brain.json`
  (this is Layer 5 — the close-the-loop step that turns the brain into
  a learning system). Triggers: "pull x analytics", "x metrics", "track
  x performance", "x-analytics-tracker", "how are my posts doing", "x
  stats this week/last 7 days/last 30 days". Auto-invoke when Andre asks
  about post performance and the cron `xce-feedback-<date>` has fired
  and is missing data. Read-only against x.com. Do NOT use for a
  different X account, non-X platforms, real-time/per-minute tracking
  (X has 24h aggregation lag), engagement on other accounts' posts,
  or for drafting replies/posts (this skill is read-only).
---

# x-analytics-tracker

The Layer-5 feedback closer. Pulls the numbers from X, writes them to
two destinations: a human-readable dashboard (for Andre to read) and
the brain's `performance_log` array (for the next Researcher run to
rank `ideas_backlog` by what has actually performed). Without the
brain write, the loop is decorative — the metrics get logged but
never read.

## Intent

- Open the X analytics dashboard in the real Chrome session
- Extract per-post metrics for posts in the window
- Write the dashboard section (append-only, never overwrite)
- Write to the brain's `performance_log` (atomic, idempotent)
- Report back: dashboard path, brain delta, top/bottom post, "unclear" count

The model decides *how* to navigate the X UI, *which* posts are in the
window, and *how* to handle the hook_used extraction. The deterministic
layer (dashboard template, brain-write protocol, metric schema, window
parsing) lives in `references/`. Safety halts and brain-write discipline
live as eval cases in `tests/`.

## When to run

**Triggers:**
- "pull x analytics" / "x metrics" / "x stats" / "track x performance"
- "how are my posts doing" / "x stats this week" / "last 7 days" / "last 30 days"
- The cron `xce-feedback-<date>` has fired and is missing the `performance_log` entries
- The Researcher is about to run and `performance_log` is stale (>3 days old)

**Do NOT run for:**
- A different X account (this skill is scoped to @DreTheSalesGuy)
- Non-X platforms (LinkedIn, Threads have separate metrics UIs)
- Real-time / per-minute tracking (X has ~24h aggregation lag)
- Engagement on other accounts' posts (use `x-engagement-hunter` territory)
- Drafting a reply or post (this skill is read-only)

## Inputs

| Input | Default | Required |
|---|---|---|
| Target account | @DreTheSalesGuy | no |
| Window | 7 days | no — 1d / 7d / 14d / 30d / custom |
| Dashboard path | `99 _system/dashboards/x-metrics-dashboard.md` | no |
| Brain path | `03 Projects/X-Content-Engine/memory/content_brain.json` | no |
| Source | X analytics dashboard (`analytics.x.com`) | no |

Window formats: "last 7 days" / "this week" → 7d; "last 30 days" /
"this month" → 30d; "yesterday" → 1d; numeric (e.g., "14 days") → N.
Full parsing rules in `references/window-formats.md`.

## Output contract

**Two writes, in order:**

1. **Dashboard append** (non-fatal if it fails): dated section to
   `99 _system/dashboards/x-metrics-dashboard.md`. Schema in
   `references/dashboard-template.md`.

2. **Brain write** (load-bearing — halt if this fails): append/update
   `performance_log` array in `content_brain.json`. Atomic rename,
   idempotent (re-runs update existing entries, don't duplicate).
   Full protocol in `references/brain-write-protocol.md`.

Report back: dashboard path, brain path + delta, post count, "unclear"
cell count, top post, bottom post, any halts (brain halt is prominent).

## Resolver

Auto-invoke when:
- Andre asks about post performance ("how are my posts doing", "x stats")
- A scheduled `xce-feedback-<date>` cron has fired and needs its data
- The Researcher is about to run and `performance_log` is stale
- The dashboard needs an update (last entry is >3 days old)

Do NOT auto-invoke for:
- Engagement on others' posts (different surface, different skill)
- A specific post URL (use `x-link-reader`)
- A single post's stats (use `x-link-reader` for that)

## The hard rule (load-bearing)

**If a metric is obscured, fails to load, or is gated behind login, write
"unclear" for that cell. NEVER hallucinate a number.**

A row of "unclear" cells is infinitely more useful than a row of
made-up numbers. Andre's iteration decisions depend on honest data.
The model decides *which* cells are unclear based on what it actually
saw in the snapshot — `tests/data-honesty.md` is the eval suite.

If the entire run produces only "unclear" cells, the section still
gets appended (with a "no usable data this run" note) — a gap is better
than a missing record.

## Safety posture

Read-only against x.com. No clicks on Reply, Repost, Like, Bookmark,
Follow. If the snapshot shows login prompt, rate limit, or unfamiliar
UI, HALT — never type credentials. The specific halt conditions are
in `tests/safety-halts.md`.

## Cross-reference

- `references/metrics-schema.md` — the per-post metric schema + fallbacks
- `references/dashboard-template.md` — the markdown section template
- `references/brain-write-protocol.md` — atomic write + idempotency rule
- `references/window-formats.md` — date-range parsing rules
- `tests/safety-halts.md` — login, rate limit, unfamiliar UI, wrong account
- `tests/brain-write-discipline.md` — atomic write, idempotency, mtime check
- `tests/hook-extraction.md` — URL-based lookup, first-sentence fallback
- `tests/data-honesty.md` — "unclear" discipline, no fabrication
- `03 Projects/X-Content-Engine/agents/feedback-loop.md` — Layer 5 spec
- `99 _system/dashboards/x-metrics-dashboard.md` — the human-readable output
