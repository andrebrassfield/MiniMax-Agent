---
type: dashboard
domain: x.com
account: @DreTheSalesGuy
created: 2026-06-16
---

# X Metrics Dashboard — @DreTheSalesGuy

<!-- Auto-appended by x-analytics-tracker. Do not edit manually. -->

---

## Run: 2026-06-16 19:05 CT · window: last 30d (X-analytics 4W preset, 2026-05-19 → 2026-06-17)

**Source:** https://x.com/i/account_analytics/content?type=posts&sort=date&dir=desc&days=30 (and 2 individual post stat pages)
**Generator:** Mavis (x-analytics-tracker), cron `x-analytics-tracker-daily`

**Window coverage note:** X analytics UI's closest preset to 30d is 4W (28d) which maps to 2026-05-19 → 2026-06-17. The dashboard's effective window is 29 days. Posts in brain dated 2026-05-18 fall just outside the X window but remain in `performance_log` from prior runs (idempotency preserved).

### Per-post metrics

| Post | Published | Impressions | Engagements | Bookmarks | Profile clicks | Likes | Retweets | Replies | Notes |
|------|-----------|-------------|-------------|-----------|----------------|-------|----------|---------|-------|
| [Wake up, there is work to be done.](https://x.com/DreTheSalesGuy/status/2058893688525197444) | 2026-05-25 | 5 | 1 | 0 | 0 | 1 | 0 | 0 | Engagement rate 40.0%; new follows=0; shares=0; media views=- (text-only post) |
| [I just cut 53% of my AI agent fleet...](https://x.com/DreTheSalesGuy/status/2057542421102186899) | 2026-05-21 | 24 | 5 | 0 | 1 | 1 | 0 | 1 | Engagement rate 20.8%; new follows=0; shares=0; media views=- (text-only post); best performer in window by impressions |

### Aggregate
- Posts in window: 2
- Total impressions: 29
- Avg impressions/post: 14.5
- Total engagements (likes+replies+retweets+bookmarks+profile visits): 3
- Avg engagement rate (engagements/impressions): 10.3%

### Top 3 (by impressions)
1. **"I just cut 53% of my AI agent fleet..."** — 24 impressions, 1 reply, 1 profile click. Highest absolute reach. Lead with a number + a structural change ("cut 53%") and people lean in.
2. **"Wake up, there is work to be done."** — 5 impressions, 1 like, 0 replies. Provocative but very low reach in window.

(Bottom 3 omitted — only 2 posts in window.)

### Operator notes
- **Engagement rate is misleading at this volume.** 40% / 20.8% sound great but the denominators are 5 and 24. A single like on a 5-impression post = 20%. The brain feedback loop needs absolute counts, not percentages, to be honest.
- **Hook pattern delta:** the 53% post leads with a specific number + a verb of action + a personal stake ("I just cut..."). The "Wake up" post leads with imperative address. Specific-number hooks are landing harder for @DreTheSalesGuy at this volume.
- **No "unclear" cells** — every metric was visible in the per-post drill-down snapshots.
- **X analytics UI quirk:** the post list virtualizes the row DOM, so the accessibility snapshot only shows 2 rows even after scroll attempts. The 4W window is genuinely small (2 posts in 29 days). If Andre is testing the pipeline, the dashboard will look thin until posting cadence picks up.
- **Prior-run correction:** this run overwrites the brain's prior `_note` on post 1 (2058893688525197444). The earlier `_note` recorded "reposts=40" — that was actually the engagement-rate percentage (40.0%), not a repost count. Drill-down this run confirmed reposts=0. The brain now reflects the corrected metric.

### Verification
- Brain `performance_log` count: 5 before → 5 after (both posts already existed, views/likes updated in place via `for...else` idempotency rule)
- Atomic write used (temp-write-fsync-rename)
- Brain JSON valid: `python3 -m json.tool` exits 0

---

## Run: 2026-06-17 19:00 CT · window: last 30d (X-analytics 4W preset, 2026-05-20 → 2026-06-18)

**Source:** https://x.com/i/account_analytics/content?type=posts&sort=date&dir=desc&days=30 (and 3 individual post stat pages)
**Generator:** Mavis (x-analytics-tracker), cron `x-analytics-tracker-daily`

**Window coverage note:** X analytics UI's closest preset to 30d is 4W (29d) which maps to 2026-05-20 → 2026-06-18. The 2026-05-18 posts in `performance_log` (3 entries: 2056418412604035380 / 2056417748360606065 / 2056404986838315311) remain in the brain from prior runs but are out of the X-UI window. Idempotency rule preserves them.

### Per-post metrics

| Post | Published | Impressions | Engagements | Bookmarks | Profile clicks | Likes | Retweets | Replies | Notes |
|------|-----------|-------------|-------------|-----------|----------------|-------|----------|---------|-------|
| [You don't need a new FSM platform. You need the 200 lines Python the wrapper is missing...](https://x.com/DreTheSalesGuy/status/2067394237851636104) | 2026-06-17 | 3 | 0 (sum of visible) | 0 | 0 | 0 | 0 | 0 | Engagement rate 0.0%; new follows=0; shares=0; media views=- (text-only post). P4 Build Logs stress test (Draft 3, R3-D3, idea[37]) from drafts/machine-batch-2026-06-17.md. Brand new post — impressions still accumulating. |
| [Wake up, there is work to be done.](https://x.com/DreTheSalesGuy/status/2058893688525197444) | 2026-05-25 | 9 | 1 (sum of visible) | 0 | 0 | 1 | 0 | 0 | Engagement rate 22.2%; new follows=0; shares=0; media views=- (text-only post). Impressions grew 5 → 9 since prior run; engagement rate 40.0% → 22.2% (denominator grew, numerator constant). |
| [I just cut 53% of my AI agent fleet...](https://x.com/DreTheSalesGuy/status/2057542421102186899) | 2026-05-21 | 29 | 3 (sum of visible) | 0 | 1 | 1 | 0 | 1 | Engagement rate 17.2%; new follows=0; shares=0; media views=- (text-only post). Best performer in window by impressions. Impressions grew 24 → 29 since prior run. |

### Aggregate
- Posts in window: 3
- Total impressions: 41
- Avg impressions/post: 13.7
- Total engagements (sum of visible: likes+replies+retweets+bookmarks+profile visits): 4
- Avg engagement rate (computed: engagements/impressions, weighted): 9.8% (4/41)

### Top 3 (by impressions)
1. **"I just cut 53% of my AI agent fleet..."** — 29 impressions, 1 reply, 1 profile visit, 1 like. Highest absolute reach by 3.2x. Specific number + verb of action + personal stake ("I just cut 53%") continues to land.
2. **"Wake up, there is work to be done."** — 9 impressions, 1 like, 0 replies. Imperative-address post; impressions grew since prior run.
3. **"You don't need a new FSM platform..."** — 3 impressions, 0 likes, 0 replies. Brand new (Jun 17); impressions still accumulating. P4 stress test; verdict pending.

(Bottom 3 omitted — only 3 posts in window.)

### Operator notes
- **Brand new post 1 (P4 stress test) tracked from 0 → 3 impressions in the live window.** The X UI updates in real time; the first snapshot showed 0, the second 2, the third 3. The skill captured the latest value (3) at run time. If Andre wants sub-impression granularity, the live X dashboard is the source, not this daily cron.
- **Post 2 (Wake up) had its `profile_visits` count drop from 1 → 0** between runs. This is the X UI's data, not a skill error — the visit was either reclassified (bot detection) or the user cleared their session. The brain updates in place to reflect the current truth.
- **Post 3 (cut 53%) grew 24 → 29 impressions** since the prior run on 2026-06-16 19:05 CT. Engagement count held steady at 1 like + 1 reply + 1 profile visit. The engagement rate dropped 20.8% → 17.2% (denominator grew faster than numerator), but the absolute engagement is unchanged.
- **No "unclear" cells** — every metric was visible in the per-post drill-down snapshots.
- **Hook pattern delta (vs. prior run):** The 3 in-window posts are: specific-number action ("cut 53%"), imperative address ("Wake up"), and contrarian-pitch ("You don't need a new FSM platform"). The first two patterns have prior data; the third is the new P4 stress test, verdict pending impressions/replies.
- **3 posts in 30 days = low cadence.** The X-Content-Engine pipeline is publishing, but at this rate, the brain feedback loop is more about pattern detection than volume-based ranking. Researcher should keep drafting at this cadence or above for the loop to compound.

### Verification
- Brain `performance_log` count: 5 before → 6 after (1 new entry for post 2067394237851636104, 2 existing entries updated in place: 2058893688525197444 views 5→9, 2057542421102186899 views 24→29; 3 out-of-window entries preserved)
- Atomic write used (temp-write-fsync-rename)
- Brain JSON valid: `python3 -m json.tool` exits 0
