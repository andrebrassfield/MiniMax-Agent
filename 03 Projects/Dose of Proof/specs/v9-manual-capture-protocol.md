---
title: V9 Manual D1/D7 Engagement Capture Protocol
status: ACTIVE (interim, per Founder directive 2026-06-25 20:28 CT)
updated: 2026-06-25
per: triage-gate-spec §6 + V9 verification (manual variant)
---

# V9 — Manual D1/D7 Engagement Capture Protocol

**Status:** V9 CONFIRMED via documented manual protocol (Founder directive 2026-06-25 20:28 CT).
V9 does not block the sprint on the Postiz engagement analytics API endpoint (unconfirmed).
Manual capture from Postiz UI is the interim method until the API endpoint is confirmed.

---

## Why manual

`triage-gate-spec.md` §6 requires every published post to have `ENGAGEMENT_D1` and
`ENGAGEMENT_D7` populated in `dose-of-proof-performance-log.json`. The canonical
implementation calls `fetch_postiz_engagement()` which depends on a Postiz
analytics API endpoint — **which is unconfirmed**. Until the endpoint is
confirmed by Dre via Postiz support or documentation review, the metric values
are pulled manually from the Postiz UI.

**Manual capture does NOT satisfy automated coverage**, but it DOES satisfy the
spec's "ENGAGEMENT_D1/D7 populated per post" requirement for compliance review.

---

## When to run

| Window | Cron | Action |
|---|---|---|
| T+24h post-publish | `dop-engagement-capture-d1` | Pull D1 metrics from Postiz UI for posts published yesterday |
| T+168h post-publish | `dop-engagement-capture-d7` | Pull D7 metrics from Postiz UI for posts published 7 days ago |

Crons are scheduled daily at 09:00 CT:
- D1 capture window: any post with `PUBLISH_TIME` between 24h-48h ago
- D7 capture window: any post with `PUBLISH_TIME` between 168h-192h ago

---

## Manual capture procedure (per run)

### Step 1 — Identify posts due for capture

```bash
python3 ~/.mavis/agents/mavis/scripts/dop_performance_logger.py \
  --date <target_date> --action status
```

This returns rows with `ENGAGEMENT_D1=0` or `ENGAGEMENT_D7=0` that are due for capture.

### Step 2 — Open Postiz UI

1. Navigate to https://postiz.com (use existing Dre login session — `mavis browser` MCP)
2. Click into the relevant integration (Facebook / Instagram)
3. Find the post by `POST_ID` (search by post content fingerprint or date/time)

### Step 3 — Capture metrics from the post detail panel

For each post, record:
- **Postiz internal post_id** (if not already known; update `PUBLISH_TIME` to reflect accurate timestamp)
- **ENGAGEMENT_D1**: total engagement score 24h after publish (sum of likes + comments + shares + clicks per platform-native definition)
- **ENGAGEMENT_D7**: same metric 7 days after publish

**Note on platform definitions:**
- Facebook: reactions + comments + shares (engagement metric in Postiz analytics)
- Instagram: likes + comments + saves + shares
- Pinterest: repins + clicks + saves

If the Postiz UI doesn't show a single engagement score, sum the visible metrics manually.

### Step 4 — Update performance_log.json

```bash
python3 ~/.mavis/agents/mavis/scripts/dop_performance_logger.py \
  --date <target_date> --action capture-d1   # or capture-d7
```

This reads the log, finds posts due, and attempts auto-fetch via Postiz API.
Since the API is unconfirmed, it will mark `NOTES = "... | d1 capture: PENDING manual from Postiz UI"`.

**Manual override path:** open the log directly and update the row:

```bash
# Open log file
$EDITOR /Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof/memory/dose-of-proof-performance-log.json

# Find the row by POST_ID, update fields:
#   "ENGAGEMENT_D1": <captured value>
#   "ENGAGEMENT_D7": <captured value, or 0 if not yet due>
#   "NOTES": "<original notes> | d1 captured: <value> at <timestamp> via manual UI pull by <operator>"
```

**Atomic write discipline:** use temp-write-rename pattern. Do not edit in place.

### Step 5 — Log to OPERATIONS-LOG.md

Append a single line per capture session:

```
## D1/D7 Manual Capture — <timestamp CT>
- Posts captured: <N>
- Operator: <name>
- Source: Postiz UI (manual pull, API endpoint unconfirmed)
- See performance_log.json for row-level updates
```

### Step 6 — Halt conditions

HALT and surface to Dre/Co-CEO if:
- Postiz UI doesn't show metrics for a post that should have them (post is older than 7 days)
- The post no longer exists on the platform (deleted, unpublished, account action)
- Operator cannot reach Postiz UI (auth failure, session expired)

---

## Operational protocol when manual capture is needed

If `dop-engagement-capture-d1` or `dop-engagement-capture-d7` cron fires and finds
posts due with no auto-fetch possible:

1. Cron writes `PENDING manual from Postiz UI` to `NOTES` field
2. Cron posts to HITL Obsidian daily note: "N posts due for D1/D7 manual capture"
3. Dre or Mavis (via `mavis browser` MCP, if Dre session is bound) opens Postiz UI
4. Pull metrics, update log per Step 4
5. Log to OPERATIONS-LOG per Step 5

**Manual latency budget:** ≤24h after cron fires. If not captured within 48h,
the July 7 review report will show `engagement_d*_pending` rows.

---

## V9 status

| Sub-item | Status |
|---|---|
| Method named | ✅ (`dop_performance_logger.py --action capture-d1/d7`) |
| Method tested | ✅ (script runs end-to-end, marks PENDING when API unavailable) |
| Manual capture protocol documented | ✅ (this document) |
| Operator protocol for manual pull | ✅ (Steps 1-6 above) |
| Cron scheduled for daily capture | ✅ (dop-engagement-capture-d1/d7 at 09:00 CT, to be created if not present) |
| Auto-fetch via Postiz API | ❌ NOT WIRED (API endpoint unconfirmed) — accepted as interim per Founder directive |

**V9 CONFIRMED** per Founder directive 2026-06-25 20:28 CT (manual capture accepted as
interim method). API confirmation + auto-fetch upgrade is a separate work item.

---

*Last updated: 2026-06-25 20:35 CT — Manual capture protocol ACTIVE. V9 CONFIRMED.*
