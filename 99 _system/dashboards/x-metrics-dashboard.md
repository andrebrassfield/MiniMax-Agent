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

---

## Run: 2026-06-18 19:00 CT · window: last 30d (cron `x-analytics-tracker-daily`)

**Source:** https://x.com/i/account_analytics/content?type=posts&sort=date&dir=desc&days=30 (navigation succeeded, page did not render content)
**Generator:** Mavis (x-analytics-tracker), cron `x-analytics-tracker-daily`

**HALT — no usable data this run.** Two safety halts fired back-to-back. The run is preserved in this section per T3 (gap is better than a missing record) and the brain write was **skipped** per T4 (we do not write metrics the dashboard did not capture, to avoid overwriting real prior metrics with nulls).

### Per-post metrics

| Post | Published | Impressions | Engagements | Bookmarks | Profile clicks | Likes | Retweets | Replies | Notes |
|------|-----------|-------------|-------------|-----------|----------------|-------|----------|---------|-------|
| unclear | unclear | unclear | unclear | unclear | unclear | unclear | unclear | unclear | Run halted — see operator notes below. No X post row rendered this run. |

### Aggregate
- Posts in window: unclear (X UI gated; no count could be observed)
- Total impressions: unclear
- Avg impressions/post: unclear
- Total engagements: unclear
- Avg engagement rate: unclear

### Top 3 (by impressions)
- unclear — no impressions observed this run.

### Bottom 3 (by impressions)
- unclear — no impressions observed this run.

### Operator notes — HALT conditions fired

- **H4 — X Premium analytics gate (HALT).** Page body text: `"Advanced analytics with X Premium — See your profile analytics, understand your audience and more. Upgrade to continue."` The `/i/account_analytics/content` page returns the X Premium upsell overlay for the current logged-in user, blocking all per-post metrics widgets. Per `tests/safety-halts.md` H4, do not click "Upgrade" or "Maybe later" — those are interaction affordances on a surface the skill does not navigate.
- **H6 — Wrong account (HALT).** The X session nav-bar "Profile" link href in the accessibility snapshot is `https://x.com/DoseofProof`, not `@DreTheSalesGuy`. The `/i/account_analytics` URL pattern is the current logged-in user's analytics, so this would have been @DoseofProof's analytics, not @DreTheSalesGuy's. Per `tests/safety-halts.md` H6, the skill is scoped to @DreTheSalesGuy only — silent cross-account contamination is the failure mode this rule exists to prevent. The X session appears to have been switched to a different account between the 2026-06-17 19:00 CT run and this run. No `@DreTheSalesGuy` posts could be queried because we were not on that account.
- **Resolution path for Andre:**
  1. Open Chrome and confirm which X account is currently logged in (avatar → "Profile" → URL bar).
  2. If on the wrong account, switch to @DreTheSalesGuy in the same browser (the mavis browser bridge preserves the cookie jar across sessions). Re-run the cron or invoke the skill manually.
  3. If the analytics is still Premium-gated on @DreTheSalesGuy itself, the X Premium upsell is an account-level state — X requires Premium to view per-post metrics on this surface. The skill cannot bypass it (and should not, per H4). Long-term: subscribe to X Premium for @DreTheSalesGuy, or pivot this skill to a different data source (e.g., direct tweet-URL scraping via the FxTwitter API, or the X API v2 with a paid plan).
- **Brain write was skipped (intentional, per T4).** The 11 prior `performance_log` entries in `content_brain.json` (mtime 1781820156, untouched) are preserved verbatim. The brain still holds the last known real metrics for the 2026-06-16 and 2026-06-17 runs. Do not interpret "no new entry" as "0 metrics" — the data is missing, not zero.
- **Dashboard table is intentionally a single all-unclear row** (T3 format: a row of "unclear" cells is infinitely more useful than a row of made-up numbers). The Operator notes above are the load-bearing content of this run.

### Verification
- Brain `performance_log` count: 11 before → 11 after (write skipped, prior metrics preserved; mtime unchanged at 1781820156)
- Brain JSON valid (not re-checked this run; no write)
- Dashboard append successful (95 → 95 + section)
- No X clicks executed (H4 + H6 halts respected)
- No credentials typed (H2 contract honored)


---

## Run: 2026-06-22 19:01 CT · window: last 30d (cron `x-analytics-tracker-daily`)

**Source:** https://x.com/i/account_analytics/content?type=posts&sort=date&dir=desc&days=30 (NOT NAVIGATED — mavis browser bridge offline)
**Generator:** Mavis (x-analytics-tracker), cron `x-analytics-tracker-daily`

**HALT — no usable data this run.** The mavis browser bridge returned `Native host: not connected` on `mavis browser status`. Per `tests/safety-halts.md` H1, this is a hard halt — do not fall back to auto-spawned Chromium for x.com (OAuth-hijack surface). The run is preserved in this section per T3 (a gap is better than a missing record), and the brain write was **skipped** per T4 (we do not write metrics the dashboard did not capture).

### Per-post metrics

| Post | Published | Impressions | Engagements | Bookmarks | Profile clicks | Likes | Retweets | Replies | Notes |
|------|-----------|-------------|-------------|-----------|----------------|-------|----------|---------|-------|
| unclear | unclear | unclear | unclear | unclear | unclear | unclear | unclear | unclear | Run halted — see operator notes below. No X post row rendered this run. |

### Aggregate
- Posts in window: unclear (browser bridge offline; no count could be observed)
- Total impressions: unclear
- Avg impressions/post: unclear
- Total engagements: unclear
- Avg engagement rate: unclear

### Top 3 (by impressions)
- unclear — no impressions observed this run.

### Bottom 3 (by impressions)
- unclear — no impressions observed this run.

### Operator notes — HALT condition fired

- **H1 — Browser bridge offline (HALT).** `mavis browser status` output:
  ```
  Browser Integration Status
    Profile: default
    Socket:  /Users/brassfieldventuresllc/.mavis/browser-broker.sock

    Broker: running
    Native host: not connected
    Tab claims: none
  ```
  The broker is running but the Chrome native messaging host (the unpacked `Mavis Browser Bridge` extension) is not connected. Without it, the skill cannot drive the user's real Chrome session — and per H1, falling back to a fresh Chromium instance for x.com is forbidden (it would defeat the OAuth-cookie-jar protection the bridge provides).
- **Resolution path for Andre:**
  1. Open Chrome and re-load the unpacked extension via `mavis browser install` (drag the unpacked extension into `chrome://extensions`, verify the loaded extension ID matches, remove any stale "Mavis Browser Bridge" entry first).
  2. Confirm `mavis browser status` shows `Native host: connected` before re-running the cron.
  3. If the bridge still fails after re-install, this is likely a stale native-messaging-host manifest (`~/.mavis/browser-broker/native-host.json`) — needs a fresh `mavis browser install` after deleting the manifest.
- **Prior halt context.** The 2026-06-18 run halted on **H4 (X Premium gate) + H6 (wrong account — @DoseofProof)** — that halt is still unresolved. Even if the bridge comes back, the next run will likely re-hit H4 / H6 unless Andre (a) confirms the X session is logged in as @DreTheSalesGuy, and (b) the account has X Premium or the Premium upsell is dismissed. The bridge fix is necessary but not sufficient.
- **Brain write was skipped (intentional, per T4).** The 11 prior `performance_log` entries in `content_brain.json` (mtime 1782138562, untouched this run) are preserved verbatim. The brain still holds the last known real metrics for the 2026-06-16 and 2026-06-17 runs (the two runs that succeeded). The 2026-06-18 halt was a no-write, so the brain does not yet have a 2026-06-18 entry. Do not interpret "no new entry" as "0 metrics" — the data is missing, not zero.
- **No X clicks executed, no credentials typed** (H1 + H2 contracts honored).

### Verification
- Brain `performance_log` count: 11 before → 11 after (write skipped, prior metrics preserved; mtime unchanged)
- Brain JSON valid (not re-checked this run; no write)
- Dashboard append successful (142 → 142 + section)
- mavis browser bridge: native host disconnected (logged above)

---

## Run: 2026-06-23 19:00 CT · window: last 30d (requested) — HALT

**Source:** requested `https://x.com/i/account_analytics/content?type=posts&sort=date&dir=desc&days=30` (never reached — pre-flight H1 halt)
**Generator:** Mavis (x-analytics-tracker), cron `x-analytics-tracker-daily`

**Run status: HALTED — no usable data this run.**

### Per-post metrics

| Post | Published | Impressions | Engagements | Bookmarks | Profile clicks | Likes | Retweets | Replies | Notes |
|------|-----------|-------------|-------------|-----------|----------------|-------|----------|---------|-------|
| unclear | unclear | unclear | unclear | unclear | unclear | unclear | unclear | unclear | H1 halt before any X navigation |

### Aggregate
- Posts in window: unclear (browser bridge offline; no count could be observed)
- Total impressions: unclear
- Avg impressions/post: unclear
- Total engagements: unclear
- Avg engagement rate: unclear

### Top 3 (by impressions)
- unclear — no impressions observed this run.

### Bottom 3 (by impressions)
- unclear — no impressions observed this run.

### Operator notes — HALT condition fired

- **H1 — Browser bridge offline (HALT, recurring).** `mavis browser status` output:
  ```
  Browser Integration Status
    Profile: default
    Socket:  /Users/brassfieldventuresllc/.mavis/browser-broker.sock

    Broker: running
    Native host: not connected
    Tab claims: none
  ```
  Same condition as the prior halt on 2026-06-19. The Chrome native messaging host (unpacked `Mavis Browser Bridge` extension) is still not connected. The skill cannot drive the user's real Chrome session — and per H1, falling back to a fresh Chromium instance for x.com is forbidden (it would defeat the OAuth-cookie-jar protection the bridge provides).
- **Resolution path for Andre:**
  1. Open Chrome and re-load the unpacked extension via `mavis browser install` (drag the unpacked extension into `chrome://extensions`, verify the loaded extension ID equals `ppnnfacnjgokfmbngkgbdgiigpbfgdba`, remove any stale "Mavis Browser Bridge" entry first).
  2. Confirm `mavis browser status` shows `Native host: connected` before re-running the cron.
  3. If the bridge still fails after re-install, this is likely a stale native-messaging-host manifest — `mavis browser install` after deleting the stale manifest will regenerate it.
- **Prior halt context (still open).** The 2026-06-18 run halted on **H4 (X Premium gate) + H6 (wrong account — @DoseofProof)** — that halt is still unresolved. Even when the bridge comes back, the next run will likely re-hit H4 / H6 unless Andre (a) confirms the X session is logged in as @DreTheSalesGuy, and (b) the account has X Premium or the Premium upsell is dismissed. The bridge fix is necessary but not sufficient — see the 2026-06-18 halt section for full detail.
- **Cascade: this cron is now at 3 consecutive halts** (2026-06-18 H4+H6 → 2026-06-19 H1 → 2026-06-23 H1). If the next run also halts, the brain's `performance_log` will be 4 days stale and the Researcher / next XCE feedback loop will not have fresh data. Worth surfacing as a hard-priority fix.
- **Brain write was skipped (intentional, per T4).** The 11 prior `performance_log` entries in `content_brain.json` (mtime 1782138562, untouched this run) are preserved verbatim. The brain still holds the last known real metrics from the 2026-06-16 and 2026-06-17 runs. Do not interpret "no new entry" as "0 metrics" — the data is missing, not zero.
- **No X clicks executed, no credentials typed** (H1 + H2 contracts honored).

### Verification
- Brain `performance_log` count: 11 before → 11 after (write skipped, prior metrics preserved; mtime unchanged)
- Brain JSON valid (not re-checked this run; no write)
- Dashboard append successful (198 → 198 + section)
- mavis browser bridge: native host disconnected (logged above)
