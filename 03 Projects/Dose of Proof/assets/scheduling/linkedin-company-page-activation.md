---
type: linkedin-company-page-activation-workflow
asset: linkedin-company-page-activation
status: ✅ FINAL (locked 2026-06-24 16:48 CT) — auto-firing cron in place; workflow documented for Dre
purpose: step-by-step activation workflow for the Dose of Proof LinkedIn Company Page (now that it exists and is connected to Buffer)
key_dependency: Buffer rate limit (24h window) — auto-fires via cron at Thu Jun 25 13:34 CT
---

# LinkedIn Company Page — Activation Workflow

> **Status:** Dose of Proof LinkedIn Company Page is created + connected to Buffer. Buffer API is currently rate-limited (24h window; resets ~Thu Jun 25 13:34 CT). Mavis has set a cron that auto-fires the activation workflow the moment rate limit clears.
>
> **What this document covers:** the full activation workflow that fires automatically once Buffer unlocks, plus what Dre needs to do in parallel.

---

## Part 1 — Mavis auto-fires (when Buffer rate limit clears)

A cron (`linkedin-company-page-activation`) is set to poll every 10 minutes. When Buffer's rate limit resets (~Thu Jun 25 13:34 CT, based on `x-ratelimit-reset` header from the 429 response), the cron executes the following 8 steps:

### Step 1 — Run channel discovery
```bash
bash "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof/assets/scheduling/find-linkedin-company-page-channel.sh"
```

**What it does:** queries Buffer GraphQL API for all channels, filters for LinkedIn, identifies which is PERSONAL (do not use) vs COMPANY PAGE (use this).

**Expected output:**
```
LINKEDIN CHANNELS:
  [PERSONAL - DO NOT USE]
     ID: 6a3c1e195ab6d2f10669e738
     Name: André Brassfield
     Handle: andre-brassfield
  [COMPANY PAGE - USE THIS]
     ID: <NEW_ID_HERE>            ← This is what we need
     Name: Dose of Proof
     Handle: doseofproof
```

### Step 2 — Capture the new channel ID
Save the Company Page channel ID (the one labeled `[COMPANY PAGE - USE THIS]`) for use in subsequent steps.

### Step 3 — Update `/tmp/buffer_bulk_push.py`
Replace the personal LinkedIn channel ID (`6a3c1e195ab6d2f10669e738`) with the new Company Page channel ID in the LinkedIn rows.

**Specifically:** find every line that contains `6a3c1e195ab6d2f10669e738` and replace with the new channel ID. There should be 2 such lines (LinkedIn Post 1 + LinkedIn Carousel 1).

### Step 4 — Update `assets/scheduling/buffer-bulk-upload-week-1-2.csv`
Same replacement: find `6a3c1e195ab6d2f10669e738` in the `channel_id` column and replace with the new Company Page channel ID.

### Step 5 — Re-run Buffer push script
```bash
python3 /tmp/buffer_bulk_push.py
```

**What it does:** pushes LinkedIn Post 1 (Origin Story) + LinkedIn Carousel 1 (5 Biomarkers) to Buffer with the updated channel ID.

**Expected result:** 2 successful posts scheduled on the Company Page.

### Step 6 — Verify both posts scheduled on Company Page (not personal)
Re-query the Buffer channels API and verify the new posts appear under the Company Page channel (not the personal channel).

### Step 7 — Update OPERATIONS-LOG
Add the new channel ID + post confirmation IDs to OPERATIONS-LOG. Decision 24 (LinkedIn Company Page activation complete) gets logged.

### Step 8 — Delete the cron
The cron auto-deletes itself after the workflow completes successfully.

---

## Part 2 — What Dre does in parallel

While the cron is firing (or after it fires), Dre has 2 actions:

### Action A — DELETE the Jul 1 LinkedIn carousel from personal LinkedIn (30 sec)

**Why this matters:** The carousel was accidentally pushed to personal LinkedIn during earlier API exploration. Brand content on personal LinkedIn is a boundary violation. Now that the Company Page is live, the personal version must be removed.

**How to do it:**
1. Open Buffer UI: https://buffer.com
2. Click your avatar → Channels
3. Click the **personal LinkedIn channel** (labeled with your personal name, channel ID `6a3c1e195ab6d2f10669e738`)
4. Click "Queue" or "Scheduled"
5. Find the post scheduled for **Jul 1, 9:00 AM ET** titled "5 Biomarkers That Actually Moved the Needle"
6. Click the post → "Edit" → "Delete this post"
7. Confirm deletion

**After deletion:** Reply to Mavis "Personal LinkedIn carousel deleted" so the cleanup can be logged in OPERATIONS-LOG.

### Action B — Verify the Company Page is searchable (1 min)

After the cron fires and posts are scheduled on the Company Page:

1. Open LinkedIn (separate tab from your personal account if possible)
2. Search "Dose of Proof" in the LinkedIn search bar
3. Verify the **Company Page** appears (with the brand logo)
4. Click on the page → verify the Origin Story post appears in the recent activity
5. Verify the post shows the Substack link in the first comment (Mavis adds this automatically)

**If the Company Page doesn't appear in search:** LinkedIn's search index can take 24-48h to pick up new pages. Wait 24h and retry.

---

## Part 3 — Fallback (if cron doesn't fire / fails)

If the cron fails for any reason (Buffer API key rotated, Buffer outage, etc.), Dre can run the workflow manually:

### Manual activation workflow

1. **Run the channel discovery script** (in Terminal):
   ```bash
   bash "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof/assets/scheduling/find-linkedin-company-page-channel.sh"
   ```

2. **Copy the Company Page channel ID** from the output

3. **Open `/tmp/buffer_bulk_push.py`** in a text editor

4. **Replace the personal LinkedIn channel ID** (`6a3c1e195ab6d2f10669e738`) with the new Company Page channel ID on 2 lines (LinkedIn Post 1 + LinkedIn Carousel 1)

5. **Open `assets/scheduling/buffer-bulk-upload-week-1-2.csv`** in a spreadsheet editor

6. **Replace the same channel ID** in the `channel_id` column

7. **Run the push script**:
   ```bash
   python3 /tmp/buffer_bulk_push.py
   ```

8. **Verify the posts appear on the Company Page** in Buffer UI

9. **Tell Mavis the activation is complete** (so OPERATIONS-LOG can be updated)

---

## Part 4 — Timeline expectations

| Time | Event | Owner |
|------|-------|-------|
| Now → Thu Jun 25 13:34 CT | Buffer rate limit active; cron polling every 10 min | Mavis (cron) |
| Thu Jun 25 13:34 CT (estimated) | Buffer rate limit resets; cron executes workflow | Mavis (cron) |
| Thu Jun 25 ~13:40 CT | Mavis completes channel discovery + script update + push | Mavis (auto) |
| Thu Jun 25 ~13:45 CT | Mavis tells Dre the LinkedIn brand surface is live | Mavis |
| Thu Jun 25 evening | Dre deletes personal LinkedIn carousel | Dre |
| Fri Jun 26 morning | Dre verifies Company Page is searchable + posts are visible | Dre |

**Target:** LinkedIn brand surface fully operational by Thu Jun 25 evening. The personal LinkedIn cleanup is the only Dre action that gates the brand-boundary integrity.

---

## Part 5 — Compliance audit (LinkedIn brand surface activation)

When the workflow completes:

- ✅ LinkedIn Post 1 (Origin Story) scheduled on Company Page (NOT personal)
- ✅ LinkedIn Carousel 1 (5 Biomarkers) scheduled on Company Page (NOT personal)
- ✅ Both posts have first-comment Substack link with UTM parameters
- ✅ Personal LinkedIn carousel (the accidentally-pushed Jul 1 one) deleted from Buffer
- ✅ No brand content scheduled on personal LinkedIn
- ✅ OPERATIONS-LOG reflects the new channel ID + post confirmation IDs

**If any of these fail:** log to OPERATIONS-LOG as Decision 24 sub-note with the specific failure. Mavis proposes remediation.

---

## What's NOT in this workflow

This activation workflow handles the LinkedIn brand surface for Week 1-2 content. The Week 3-4+ LinkedIn content (LinkedIn Post 3 "What's coming Jul 23", LinkedIn Carousel 2 "PCAC framework", etc.) is not yet queued — those get queued as part of the Week 3-4 CSV draft after Week 1-2 reviews complete.

This is intentional: the Week 1-2 activation gets the Company Page live + 2 posts scheduled (proves the architecture works), then Week 3-4 content builds on top of that foundation.

---

*Last updated: 2026-06-24 16:48 CT*
*Cron name: `linkedin-company-page-activation` (10-minute polling, auto-expires 2026-07-08)*
*Activation trigger: Buffer rate limit reset (estimated Thu Jun 25 13:34 CT)*
*Source: Dre confirmed Company Page exists + is connected to Buffer (this pass)*