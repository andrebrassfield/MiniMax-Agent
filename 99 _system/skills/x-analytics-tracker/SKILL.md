---
name: x-analytics-tracker
description: Open Chrome via `mavis browser` and pull hard performance metrics (Impressions, Engagements, Bookmarks, Profile Clicks, Likes, Retweets, Replies) for our published X posts over the last 7-30 days, then append to `99 _system/dashboards/x-metrics-dashboard.md` (human-readable dashboard) AND to the `performance_log` array in `03 Projects/X-Content-Engine/memory/content_brain.json` (machine-readable state — this is the Layer 5 feedback that closes the Content Brain loop). Triggers: "pull x analytics", "x metrics", "track x performance", "x-analytics-tracker", "how are my posts doing", "x stats this week". Hard constraint: if a metric is obscured by the X UI, fails to load, or is gated behind login, write "unclear" for that metric — NEVER hallucinate a number. Read-only against x.com; the skill extracts and writes to a vault dashboard + the brain JSON, does not post or interact. Cannot be invoked for mass-account scraping; it is scoped to the @DreTheSalesGuy account only.
---

# X Analytics Tracker

## What this skill does

Pulls the **hard performance metrics** for posts published from `@DreTheSalesGuy` (Andre's X account) over the last 7-30 days, using the user's real Chrome session via `mavis browser`. The metrics are written to **two destinations**:
1. `99 _system/dashboards/x-metrics-dashboard.md` — human-readable running dashboard (each run appends a dated section)
2. `03 Projects/X-Content-Engine/memory/content_brain.json` — machine-readable state, appending to the `performance_log` array (this is Layer 5 of the Content Brain: feedback)

The `performance_log` entry for each post is the close-the-loop step. The next Researcher run reads `performance_log` to rank `ideas_backlog` by what has actually performed for @DreTheSalesGuy — turning the brain from a static pattern store into a compounding learning system.

The dashboard is the input for content-engine iteration: which posts landed, which formats work, what time-of-day / topic / hook-pattern correlates with engagement. The data is descriptive, not prescriptive — Andre (and Mavis in synthesis work) reads the dashboard, decides the next move.

## When to run

**Trigger phrases:**
- "pull x analytics" / "x metrics" / "x stats"
- "track x performance" / "how are my posts doing"
- "x-analytics-tracker" / "x metrics dashboard"
- "x stats this week" / "x stats last 7 days" / "x stats last 30 days"

**Do NOT run for:**
- A different X account (this skill is scoped to @DreTheSalesGuy; the persona and X-Content-Engine pipeline are built for that voice)
- Non-X platforms (LinkedIn, Threads, etc. have separate metrics UIs)
- Real-time / per-minute tracking (X analytics UI has ~24h aggregation lag)
- Engagement on other accounts' posts (that's `x-engagement-hunter` territory)
- Drafting a reply or post (this skill is read-only; no reply or post is created)

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Target account | @DreTheSalesGuy | no |
| Window | 7 days (configurable to 30) | no |
| Dashboard path | `99 _system/dashboards/x-metrics-dashboard.md` | no |
| Source | X analytics dashboard (post-level stats pages) | no |

**Window formats accepted:**
- "last 7 days" / "this week" → 7d
- "last 30 days" / "this month" → 30d
- "yesterday" → 1d
- Numeric (e.g., "14 days") → N days

## Outputs

A dated section appended to `99 _system/dashboards/x-metrics-dashboard.md`. Each section contains:

1. **Run header** — timestamp, window, source URL(s)
2. **Per-post metrics table** — for each post published in the window:
   - Post URL
   - Published date
   - Post text excerpt (first 200 chars)
   - Impressions
   - Engagements (total)
   - Bookmarks
   - Profile clicks
   - Likes, Retweets, Replies (if visible)
   - Notes column (any UI quirks, "unclear" markers, etc.)
3. **Aggregate row** — totals / averages across all posts in the window
4. **Top 3 / Bottom 3** — ranked by impressions
5. **Operator notes** — anything that needs Andre's attention (post that needs a reply to a comment, post that got fewer than N impressions, etc.)

The file is **append-only** — the skill never overwrites a prior section. The dashboard grows linearly with each run.

## The Hard Constraint (READ THIS)

**If a metric is obscured, fails to load, or is gated behind login, write "unclear" for that cell. NEVER hallucinate a number.**

This is the load-bearing rule. Reasons:
1. X's analytics UI hides metrics behind login, shows some metrics only to the post author, and re-arranges the dashboard layout periodically.
2. Some metrics (e.g., "Profile clicks") are only available on the aggregate account-level dashboard, not the per-post view.
3. "Bookmark" counts are sometimes hidden until the post has N bookmarks.
4. The skill runs against the user's real Chrome session — if the login cookie is expired or X is rate-limiting, partial data is the realistic outcome.

A row of "unclear" is **infinitely more useful** than a row of made-up numbers. Andre's iteration decisions depend on the data being honest.

If the entire run produces only "unclear" cells (e.g., X is down or the bridge is offline), the section still gets appended — but the run summary explicitly tells Andre "no usable data this run" so he knows the dashboard has a gap, not a record.

## The Hard Safety Constraints (READ THIS)

1. **Read-only against x.com.** No clicks on Reply, Repost, Like, Bookmark, Follow, or any other interactive affordance. The skill only reads metric values.
2. **No credential entry.** If the snapshot shows "Sign in to X" / "Log in", halt and surface. The user logs in manually; the skill does not type credentials.
3. **No navigation outside analytics.** If the page would navigate to a profile, a single post's detail page, a thread, a DM, or a search result, halt and surface. The skill's only legitimate navigations are: analytics dashboard → individual post stat page (and back).
4. **No quote-reply, no new post.** The skill does not open the post composer, the DM composer, or any input affordance.
5. **Per-account scope.** Scoped to @DreTheSalesGuy only. The skill does not navigate to other accounts' analytics.
6. **Mass-scrape guard.** If the window would require reading > 50 posts, halt and ask the operator to narrow the window. 50 is the upper bound for a single run.
7. **Rate-limit halt.** If `mavis browser` returns 429 or the snapshot shows a rate-limit warning, halt and surface. Do not retry-loop.
8. **Unfamiliar UI halt.** If the snapshot shows a layout the skill does not recognize (X has changed the analytics UI), halt and surface. Do not guess at field names.

## Procedure

### Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected`, **HALT** and tell the operator to load the Chrome extension per `mavis browser install` output. Do not proceed with auto-spawned Chromium fallbacks for x.com.

### Step 2: Open the X analytics dashboard

```bash
mavis browser tool open_tab '{"url":"https://analytics.x.com"}'
```

Note the returned `tabId`. The tool is documented to auto-claim the tab for the calling session.

### Step 3: Authentication check + load wait

Wait 5-7 seconds for the analytics dashboard to render. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":3}'
```

**Halt conditions (operator-alert only, never type credentials):**
- Snapshot shows "Sign in to X" / "Log in" / "Sign up"
- Snapshot shows a rate-limit warning
- URL is not `analytics.x.com` after navigation
- Snapshot shows a layout the skill does not recognize

**Proceed conditions:**
- Analytics dashboard visible with the @DreTheSalesGuy header
- Post list visible with date range selector
- Aggregate metrics (impressions, engagements) visible at the top

### Step 4: Set the date range to the operator's window

The X analytics dashboard has a date-range selector. The skill should:

1. Click the date-range selector
2. Select the window (Last 7 days / Last 30 days / custom)
3. Wait for the page to re-render

If the selector uses a custom range picker:
1. Click the date-range selector
2. Click "Custom range"
3. Enter T-window → T in the date pickers
4. Click "Apply"
5. Wait for the page to re-render

**Halt condition:** if the date-range selector layout is not recognized, halt and surface.

### Step 5: Extract the post list

Take a snapshot of the post list area. For each post visible:

- Post URL (the link to the individual post stat page)
- Published date
- Post text excerpt (first 200 chars)
- Aggregate metrics visible on the card (impressions, engagements, sometimes likes/reposts/replies)

**Do NOT scroll the page via `press_key`.** Use `scroll` with explicit direction and amount. If the post list is paginated or infinite-scroll, navigate to the next page via the explicit "Next" button (which IS clickable — it's a pagination affordance, not an interaction affordance).

**Halt condition:** if the post list is longer than 50 posts in the window, halt and ask the operator to narrow the window.

### Step 6: Drill into individual post stat pages (optional, but recommended for Profile Clicks / Bookmarks)

For the top 5 posts by impressions (or for all posts if the count is small), navigate to the individual post stat page:

```bash
mavis browser tool open_tab '{"url":"<post-url>"}'
```

Take a snapshot. Extract:
- Profile clicks (often only visible on the individual post page, not the dashboard card)
- Bookmark count (sometimes gated)
- Detailed engagement breakdown (replies, retweets, quote-tweets, likes as separate cells)
- Any other metrics the individual page surfaces

Close the tab when done:

```bash
mavis browser tool close_tab '{"tabId":<id>}'
```

### Step 7: Mark obscured metrics as "unclear"

For every cell where the value was not visible in the snapshot:

- If the metric widget was not rendered → "unclear"
- If the metric widget was rendered but showed "—" / "0" / spinner → "unclear" (spinner means it hadn't loaded yet)
- If the metric was gated behind a "View more" or "Show all" click → "unclear" (do not click; that is an interaction affordance)
- If the snapshot was truncated → "unclear" (do not guess)

A row of "unclear" cells is normal. Do not retry to "fill in" unclear cells.

### Step 8: Append to the dashboard

Read the current dashboard to determine the format:

```bash
ls "/Users/brassfieldventuresllc/MiniMax-Agent/99 _system/dashboards/x-metrics-dashboard.md"
```

If the file does not exist, create it with a header:

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

If the file exists, append a new section. The format:

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

### Step 9: Write to content_brain.json (Layer 5 — close the Content Brain loop)

**This is the load-bearing step that turns the analytics dashboard into a learning system.** After the human-readable dashboard is updated, write the same metrics to the `performance_log` array in `03 Projects/X-Content-Engine/memory/content_brain.json`. The next Researcher run reads `performance_log` to rank `ideas_backlog` by what has actually performed for @DreTheSalesGuy.

**Read the brain:**

```python
import json, os, tempfile
from pathlib import Path

BRAIN = Path("03 Projects/X-Content-Engine/memory/content_brain.json")
read_time = BRAIN.stat().st_mtime  # for concurrency check
state = json.loads(BRAIN.read_text())

# Schema check
required = ["hooks", "formats", "pain_points", "ideas_backlog", "performance_log"]
for key in required:
    assert key in state, f"brain JSON missing required key: {key}"
```

If the brain is missing or malformed, **HALT** and surface to the operator. The dashboard write (Step 8) is non-fatal — but the brain write is the load-bearing step, and a missing brain means the next Researcher run cannot rank by performance.

**Concurrency check:**

```python
assert BRAIN.stat().st_mtime == read_time, "brain was modified between read and write — concurrent writer detected"
```

If the mtime changed, the Researcher or Scribe ran concurrently and modified the brain. HALT — re-read, re-merge, then write.

**Build the performance_log entries:**

For each post in the per-post metrics table (from Step 8), build a `performance_log` entry. Schema per the brain contract:

```json
{
  "post_id": "<x.com URL or post ID — use the URL as the stable identifier>",
  "hook_used": "<the hook text from the post, extracted from the post body or the corresponding ideas_backlog entry>",
  "views": <integer or null if "unclear">,
  "likes": <integer or null if "unclear">,
  "date": "<YYYY-MM-DD the post was published>"
}
```

**How to determine `hook_used`:** This is the hard part. X analytics shows the post text but not which `ideas_backlog` entry produced it. Two strategies:

1. **URL-based lookup.** If the post URL appears in any prior `drafts/` file (especially `drafts/machine-batch-YYYY-MM-DD.md`), read that file, find the section that cites the post, and pull the `Source idea` from the JSON snippet (the Scribe embeds the source idea in every batch section). This is reliable when the post went through the Scribe.
2. **First-sentence extraction.** If the URL is not in any prior draft (e.g., Andre posted manually from a phone), extract the first sentence of the post body as a best-effort `hook_used`. Tag the entry with `"hook_source": "first_sentence_fallback"` in a side note (the schema is the 5 fields per the contract, so put the tag in a sibling note in the dashboard, not in the JSON).

**How to handle missing data:** If `views` or `likes` is `"unclear"` (the X UI obscured it), write the integer as `null` in the JSON, not the string `"unclear"`. The brain is machine-readable and Python's `json` round-trip will treat `null` as missing; the string `"unclear"` would break any downstream sort/filter. The `"unclear"` semantics live in the dashboard, not the brain.

**Append + atomic write:**

```python
# Find or update the entry for this post_id (idempotency — re-running the skill should
# update existing entries, not duplicate them)
for entry in state["performance_log"]:
    if entry["post_id"] == new_entry["post_id"]:
        # Update in place: keep `date` and `hook_used` from the original; overwrite views/likes
        entry["views"] = new_entry["views"]
        entry["likes"] = new_entry["likes"]
        break
else:
    state["performance_log"].append(new_entry)

# Atomic write
with tempfile.NamedTemporaryFile(
    mode="w", dir=BRAIN.parent, prefix=".content_brain_", suffix=".tmp", delete=False
) as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
    f.flush()
    os.fsync(f.fileno())
    tmp_path = f.name

os.replace(tmp_path, BRAIN)
```

**Idempotency rule (load-bearing):** the `for ... else` pattern is the canonical way to "update if exists, else append." Re-running the skill on the same window should update existing `performance_log` entries (since `views` and `likes` may have grown), not duplicate them. The `post_id` (URL) is the stable identifier.

**Halt conditions for Step 9:**

- Brain JSON missing → HALT, surface, dashboard write still happened (non-fatal)
- Brain JSON malformed → HALT, surface
- Brain JSON missing required keys → HALT, suggest manual schema repair
- Concurrent write detected (mtime changed) → HALT, re-read and retry once
- `os.replace` raises → HALT, surface

### Step 10: Return summary to operator

Send a one-paragraph summary:

- Dashboard path
- Brain path (`content_brain.json`) and the delta to `performance_log` (was N entries, now M entries; if any were updates vs. new appends, note that)
- Posts covered
- Number of "unclear" cells (sanity check that the data is honest)
- Top post (link + impressions)
- Bottom post (link + impressions)
- Halt conditions, if any (brain write halt is the load-bearing one — surface prominently)

## The Data Schema (the dashboard row)

Per the Output spec, each row's columns are:

| Column | Source | Fallback |
|--------|--------|----------|
| Post | URL + first 200 chars of post text | — |
| Published | Date from analytics UI | "unclear" |
| Impressions | analytics card | "unclear" |
| Engagements | analytics card (total) | "unclear" |
| Bookmarks | individual post stat page (sometimes gated) | "unclear" |
| Profile clicks | individual post stat page (sometimes gated) | "unclear" |
| Likes | individual post stat page | "unclear" |
| Retweets | individual post stat page | "unclear" |
| Replies | individual post stat page | "unclear" |
| Notes | free-form | — |

## The Safety Halts (inherited, plus analytics-specific)

1. **Bridge offline.** `mavis browser status` shows `not connected` → Halt.
2. **Login prompt.** snapshot shows Sign in / Log in → Halt; tell operator to log in.
3. **Rate limit.** `mavis browser` returns 429 or snapshot shows rate-limit warning → Halt.
4. **Unfamiliar UI.** snapshot shows a layout the skill does not recognize → Halt.
5. **Wrong account.** analytics dashboard shows a handle other than @DreTheSalesGuy → Halt.
6. **Window too large.** > 50 posts in the window → Halt; ask operator to narrow.
7. **Per-post navigation blocked.** individual post stat page does not load → note in the row's Notes column; continue with dashboard data only.
8. **Sensitive content skip.** if a post in the window is flagged by X for sensitive content, do not drill into its stat page (the page may require an extra click to confirm age, which is an interaction affordance) → mark the row's drill-down metrics as "unclear".

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Bridge offline | `mavis browser status` | Halt; tell operator to load Chrome extension |
| Login prompt | snapshot | Halt; tell operator to log in |
| Date-range selector not recognized | snapshot | Halt; surface the snapshot for operator review |
| Post list > 50 | count | Halt; ask operator to narrow window |
| "unclear" cells everywhere | row contents | Append the run with all-unclear cells; tell operator "no usable data this run" |
| X UI changed | snapshot | Halt; surface the new layout for skill update |
| `mavis browser` returns 429 | response | Halt; do not retry |
| Dashboard file is read-only | `Write` fails | Halt; tell operator to fix permissions |
| X account suspended or restricted | analytics dashboard shows restriction banner | Halt; surface; do not proceed |
| Brain JSON missing | `BRAIN.exists() == False` | Halt; surface prominently — the dashboard write may have succeeded but the load-bearing Layer 5 feedback did not |
| Brain JSON malformed | `json.loads` raises | Halt; do not attempt partial write; surface |
| Brain JSON missing required keys | schema check fails | Halt; suggest manual schema repair |
| Concurrent brain write (mtime changed between read and write) | `BRAIN.stat().st_mtime > read_time` | Halt; re-read and retry once. If still racing, surface to operator |
| Atomic brain write fails (rename error) | `os.replace` raises | Halt; surface prominently — the brain is the load-bearing output |
| `hook_used` extraction can't find URL in any prior draft | URL not in any `drafts/*.md` | Fall back to first-sentence extraction; tag in the dashboard side note as `hook_source: first_sentence_fallback` |

## Verification

After appending the dashboard AND the brain:

1. `ls -la` confirms the dashboard file exists
2. The new section's date matches the run header
3. The new section is appended after (not before) any prior sections
4. The number of "unclear" cells is consistent with the snapshot (a quick `grep -c "unclear" <file>` cross-check)
5. The aggregate row's totals match the per-post rows (sum/avg)
6. **The brain JSON is valid:** `python3 -m json.tool < content_brain.json > /dev/null` exits 0
7. **The brain has the expected delta to `performance_log`:** count before run vs. count after run. If a re-run, the count should NOT grow (idempotency rule). If a fresh run, the count should grow by the number of posts in the window.
8. **The atomic write pattern was used:** the brain file's mtime is now() (the atomic rename updated it). If mtime is from a prior session, the write did not happen — HALT and surface.
9. The run summary correctly reports the top and bottom post + the brain delta

## Cross-reference

- `x-engagement-hunter` — drafts replies to other accounts' posts (different scope)
- `x-bookmark-parser` — parses bookmarks the user saved (subjective, not metrics)
- `x-niche-scraper` — searches X for top-N posts by query (wider market, not own-account metrics)
- `x-link-reader` — reads a single X URL without writing to the vault
- `03 Projects/X-Content-Engine/agents/persona.md` — voice source for the persona pillars; the dashboard surfaces which pillars are working
- `mavis browser` CLI — the underlying tool surface
- Garry Tan's "evals and integration tests, repeat" principle — the dashboard is the eval loop for X content
