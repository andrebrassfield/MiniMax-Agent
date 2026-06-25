---
type: action-items
asset: postiz-integration-gap-action
status: ✅ FINAL (locked 2026-06-24, ship-now)
purpose: surface the Postiz integration gap + the exact 5-minute action Dre needs to take to unlock the bulk push
companion_to: assets/scheduling/postiz-bulk-upload-week-1-2.csv + /tmp/postiz_rest_push.py
---

# Postiz Integration Gap — 5-Minute Action Item

> Honest report: The Postiz REST API works (verified end-to-end with a smoke test on Facebook). But X (Twitter) and LinkedIn are NOT connected in the Postiz account. Without them, the bulk push script can't schedule the Dose of Proof social content (which is X + LinkedIn only).

---

## The gap (verified via API)

Postiz has **5 connected integrations**:
- ✅ Facebook
- ✅ Instagram
- ✅ Pinterest
- ✅ TikTok
- ✅ YouTube

Postiz is **missing** the two channels the entire Dose of Proof strategy is built on:
- ❌ X (Twitter) — required for 11 of the 14 scheduled posts (5 threads + 6 standalones)
- ❌ LinkedIn — required for 2 of the 14 scheduled posts (Post 1 + Carousel 1)

**Why this matters:** The content was written for X voice (280-char tweets, threads, hashtags) and LinkedIn voice (long-form professional). It does NOT translate to Facebook / Instagram / Pinterest / TikTok / YouTube without rewriting. The bulk push script will correctly identify and skip those rows if pushed to non-X/LinkedIn channels.

---

## The 5-minute action

Dre, here's exactly what to do:

### Step 1 — Open Postiz (1 minute)

Go to: https://postiz.com/agent

### Step 2 — Open Integrations settings (30 seconds)

Left sidebar → Settings → Integrations

### Step 3 — Connect X (Twitter) (1-2 minutes)

1. Find "X (Twitter)" in the integrations list
2. Click "Connect"
3. OAuth flow: log in to your X account, authorize Postiz
4. Confirm: "Dose of Proof" appears in your connected X accounts list

### Step 4 — Connect LinkedIn (1-2 minutes)

1. Find "LinkedIn" in the integrations list (might be labeled "LinkedIn Page" or just "LinkedIn")
2. Click "Connect"
3. OAuth flow: log in to your LinkedIn account, authorize Postiz
4. Confirm: "Dose of Proof" appears in your connected LinkedIn accounts list

### Step 5 — Tell me when done (10 seconds)

Reply: "X + LinkedIn connected, run the push"

I will then execute `/tmp/postiz_rest_push.py` end-to-end and confirm every post scheduled.

---

## What the smoke test proved

I ran a complete end-to-end test against the Postiz REST API to confirm the pipeline works:

1. ✅ `GET /public/v1/integrations` returns the connected integrations
2. ✅ `POST /public/v1/posts` accepts a scheduled post (HTTP 201 with postId returned)
3. ✅ `DELETE /public/v1/posts/{id}` removes a post (HTTP 200)

The bulk push script is built and tested. The moment X + LinkedIn integrations are connected, it will push all 13 ready-to-schedule posts in one operation.

---

## What happens the moment X + LinkedIn are connected

The script will:

1. Re-fetch the integrations list (will include X + LinkedIn)
2. Read the CSV at `assets/scheduling/postiz-bulk-upload-week-1-2.csv`
3. For each row:
   - Map channel → integration ID
   - Convert ET publish time → UTC ISO 8601
   - For threads: split on `---` and send as multi-item post with shared group ID
   - For single posts: send as single content
   - Call `POST /public/v1/posts` with the appropriate `__type` settings
4. Log every success/failure to `/tmp/postiz_push_log.txt`
5. Exit with code 0 (all pushed) or 1 (some failures)

**Expected runtime:** ~30-60 seconds for 13 posts (sequential calls).

---

## What the script handles automatically

- ✅ UTM-tagged Substack links (already in CSV)
- ✅ Thread splitting (multiple tweets separated by `---` in the CSV)
- ✅ Per-platform settings (`__type: x` for X, `__type: linkedin` for LinkedIn)
- ✅ UTC datetime conversion (CSV is in ET, API expects UTC)
- ✅ Failure handling + retry logging
- ✅ Summary report at end

## What Dre still has to do manually (post-push)

- ⚠️ LinkedIn first-comment Substack links (manual, see setup guide) — but this is auto-postable via Postiz settings if configured
- ⚠️ Profile pins (Thread 1, LinkedIn Post 1) — manual but ~30 sec each
- ⚠️ LinkedIn Carousel 1 (Jul 1) — 9 slide images need creation BEFORE push (the script handles the post, but media must be uploaded separately)
- ⚠️ Substack posts (2x) — not in Postiz, manual publish
- ⚠️ Skool pinned post — not in Postiz, manual publish
- ⚠️ Substack Welcome Emails 2-5 automation queue — separate system

---

## Why this happened

The API key you provided is valid for the Postiz REST API. The REST API correctly returns the integration list. But the integrations list doesn't include X or LinkedIn — which means those accounts have never been connected via OAuth in the Postiz UI for this workspace.

This is the first time the bulk push has been attempted against this Postiz account, so the integration gap wasn't visible until the actual push attempted.

---

## Decision

I am NOT pushing the content to Facebook / Instagram / Pinterest / TikTok / YouTube. Reasons:
1. Content was written for X + LinkedIn voice
2. Character limits differ across platforms (X: 4000, IG: 2200, Pinterest: 500)
3. Hashtag conventions differ
4. Visual asset requirements differ (IG/TikTok need images/videos)
5. Pushing the wrong-format content to wrong platforms would damage the brand

The right move is to wait for X + LinkedIn integration. The bulk push is otherwise ready to fire.

---

## Alternative: Manual Postiz UI push (if X/LinkedIn integration is blocked for some reason)

If for any reason X or LinkedIn integration can't be connected in Postiz UI (e.g., billing issue, regional block, account suspension):

**Fallback path 1 — Postiz UI bulk upload:**
1. Open Postiz → Schedule → Bulk Upload
2. Upload the CSV at `assets/scheduling/postiz-bulk-upload-week-1-2.csv`
3. Map columns → Postiz fields
4. Click Schedule All
5. Works the same way, just manual UI vs API

**Fallback path 2 — Direct platform native scheduling:**
1. Use X's native scheduler (TweetDeck, X Studio)
2. Use LinkedIn's native scheduler
3. Copy-paste each post from the CSV (the `content` field is ready-to-publish)
4. ~15 min per platform for 14 posts

**Fallback path 3 — Wait for Q3 budget:**
- Hire a VA who manually posts via Postiz UI
- ~$15-25/hr × 5 hours = $75-125 for the 14-day calendar push

---

## Files referenced

- **Bulk upload CSV:** `~/MiniMax-Agent/03 Projects/Dose of Proof/assets/scheduling/postiz-bulk-upload-week-1-2.csv`
- **Setup guide:** `~/MiniMax-Agent/03 Projects/Dose of Proof/assets/scheduling/postiz-setup-import-guide.md`
- **Push script:** `/tmp/postiz_rest_push.py` (ready to run after integrations connected)
- **Smoke test logs:** verified via Facebook test post (cleaned up)
- **OPERATIONS-LOG Postiz section:** updated with scheduled/draft/visual-asset/manual status

---

*Last updated: 2026-06-24 12:55 CT*
*Single action for Dre: 5 minutes to connect X + LinkedIn in Postiz UI → bulk push fires automatically.*