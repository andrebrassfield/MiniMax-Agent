---
type: operational-guide
asset: postiz-setup-import-guide
status: ✅ FINAL (locked 2026-06-24, ship-ready)
purpose: Postiz account structure + import procedure for the 14-day bulk upload CSV
audience: Dre (operator)
companion_to: assets/scheduling/postiz-bulk-upload-week-1-2.csv (the bulk upload file)
---

# Postiz Setup + Import Guide — Dose of Proof

> Step-by-step instructions to set up the Postiz account structure and import the 14-day bulk upload CSV. Total setup + import time: ~30 minutes.

---

## Part 1 — Account Structure (10 minutes)

### 1.1 Connect integrations (verify all are linked)

Open Postiz → Settings → Integrations. Confirm these are connected:

| Channel | Username / handle | Connection status |
|---------|-------------------|-------------------|
| X (Twitter) | @doseofproof (or current handle) | ☐ Connected |
| LinkedIn (personal) | Andre Brassfield | ☐ Connected |
| LinkedIn (company page, optional) | Dose of Proof | ☐ Connected |
| Threads | (skip — not in calendar) | ☐ Skip |
| Facebook | (skip — not in calendar) | ☐ Skip |
| Instagram | (skip — not in calendar) | ☐ Skip |

If any integration is missing, click "Connect" and follow the OAuth flow.

### 1.2 Create folders / labels

Open Postiz → Settings → Labels (or Folders, depending on your Postiz version). Create these:

| Folder | Use |
|--------|-----|
| `pre_launch` | All content shipped Jun 24 → Jul 22 |
| `pcac` | FDA PCAC week content (Jul 21-24) |
| `mold_cirs` | Mold/CIRS cluster content (Q3 2026+) |
| `launch` | Launch week content (Jul 22-29) |
| `iteration` | Iteration derivatives from monitoring loop |

These folders map to the brand's content cluster architecture and let Dre filter the calendar by strategic vector.

### 1.3 Set up recurring time slots (optional but recommended)

Most Postiz accounts support "time slots" for recurring publish windows. Configure:

| Slot | Days | Time (ET) | Use |
|------|------|-----------|-----|
| X morning | Mon-Sat | 8:30 AM - 9:00 AM | Threads + standalones |
| X late-morning | Saturday | 11:00 AM | Long-form threads (Sat cadence) |
| LinkedIn weekday | Tue-Thu | 9:00 AM - 10:00 AM | Posts + carousels |
| LinkedIn first-comment | Tue-Thu | 9:01 AM (1 min after post) | Substack link drops |

The CSV already has these times baked in. If you change them later, update the CSV and re-import.

### 1.4 Set up brand voice / caption templates (optional)

Postiz supports saved caption templates. Create these as starting points:

**Template: X Thread opener**
```
[1-2 sentences of context]
[Specific data or insight]
🧵 A thread on [topic]:
```

**Template: X Standalone (data-anchored)**
```
[Brand context]

[Specific numbers with trends]

[Bigger picture takeaway]

[Brief CTA]
```

**Template: LinkedIn post opener**
```
[Origin story hook — 1-2 sentences]

[Specific experience — 3-5 sentences]

[What changed — 2-3 sentences]

[CTA + framework anchor]
```

Templates are starting points. The full content in the CSV is already voice-compliant and ready to copy-paste.

---

## Part 2 — Import the CSV (5 minutes)

### 2.1 Open Postiz → Schedule → Bulk Upload

Navigate to the bulk upload tool. In Postiz, this is usually under:
- Left sidebar → "Compose" → top-right → "Bulk Upload"
- OR: Settings → Bulk Schedule → Upload CSV

### 2.2 Upload the CSV file

Click "Upload CSV" or drag-and-drop `postiz-bulk-upload-week-1-2.csv` into the upload zone.

The file is at: `~/MiniMax-Agent/03 Projects/Dose of Proof/assets/scheduling/postiz-bulk-upload-week-1-2.csv`

### 2.3 Map columns to Postiz fields

Postiz will prompt you to map CSV columns to its internal fields. The CSV has these columns:

| CSV column | Postiz field |
|------------|--------------|
| `date` | Publish date |
| `time` | Publish time |
| `channel` | Account / integration |
| `type` | Post type (single / thread / carousel) |
| `content` | Post content (full caption / thread text) |
| `media` | Attached media (file references) |
| `link` | Outbound link (UTM-tagged Substack) |
| `tags` | Labels |
| `folder` | Folder / category |
| `asset_source` | (Postiz will ignore this — it's for Dre's reference) |
| `notes` | (Postiz will ignore this — it's for Dre's reference) |

**If Postiz uses different field names**, map the closest equivalent. The CSV is structured to be portable across schedulers.

### 2.4 Threads use `---` as the tweet separator

For X threads (rows where `type = thread`), the `content` field contains all tweets separated by `---`. Postiz should auto-detect this and split into a thread.

**If Postiz doesn't auto-detect threads**, you'll need to:
- Manually paste each tweet as a separate scheduled post
- Use the `notes` column in the CSV to identify which tweets go together

The CSV is structured so manual paste-into-X also works if needed (copy the content field, split on `---`, paste tweet by tweet).

### 2.5 Confirm + schedule

After mapping, Postiz will show a preview. Verify:
- Dates match the calendar (Jun 24 - Jul 7)
- Times match the calendar (X: 8:30-9:00 AM ET or 11:00 AM Sat; LinkedIn: 9-10 AM ET)
- Channels are correct (X / LinkedIn)
- Tags applied (pre_launch, lived_protocol, etc.)
- Folders applied (pre_launch etc.)

Click "Schedule All" or equivalent.

### 2.6 Verify in Postiz calendar view

After import, switch to Calendar view and confirm:
- ✅ 14 posts scheduled across Jun 24 - Jul 7
- ✅ Off days (Jun 29, Jul 4, Jul 6) are blank
- ✅ First-comment Substack links are queued for LinkedIn posts (manual step — see below)

---

## Part 3 — Manual follow-ups (15 minutes)

Postiz doesn't auto-handle some platform-specific behaviors. These need manual setup:

### 3.1 LinkedIn first-comment Substack links

For LinkedIn Post 1 (Jun 24) and Carousel 1 (Jul 1), the Substack link must go in the FIRST COMMENT, not the post body (LinkedIn de-prioritizes posts with outbound links in the body).

**Manual step:** After each LinkedIn post publishes, post the comment within 1-2 minutes:
- Post 1 comment: "Free PDF → https://doseofproof.substack.com/?utm_source=linkedin&utm_medium=social&utm_campaign=pre_launch&utm_content=comment_post_1"
- Carousel 1 comment: "Full breakdown + free PDF → https://doseofproof.substack.com/?utm_source=linkedin&utm_medium=social&utm_campaign=pre_launch&utm_content=comment_carousel_1"

Set a phone reminder for 1 minute after each LinkedIn publish.

**Alternative:** Use Postiz's "auto first comment" feature if available in your plan. Add the comment text to the scheduled post's settings.

### 3.2 X thread posting (if Postiz doesn't auto-thread)

If Postiz imports the thread as a single tweet with all 8 tweets concatenated, you'll need to either:
- Use Postiz's "thread" post type explicitly during import (select it per-row)
- Or post the thread manually: copy content, split on `---`, paste tweet by tweet in X

The CSV is structured so manual posting works as fallback.

### 3.3 Pin Thread 1 to X profile (Wed Jun 24 ~9:00 AM ET)

After Thread 1 publishes, manually pin it to the X profile. Pin lasts 2 weeks during the lead-magnet push window.

### 3.4 Pin LinkedIn Post 1 to profile (Wed Jun 24 ~10:00 AM ET)

After LinkedIn Post 1 publishes, manually pin it to the LinkedIn profile.

### 3.5 Skool pinned post (Fri Jun 27)

Skool is not a Postiz integration. Post the Skool pinned post manually on Fri Jun 27 morning. Source: `assets/skool/inner-circle-onboarding-first-7-days.md` Day 1.

### 3.6 Substack posts (Jun 24 + Jul 1)

Substack is not a Postiz integration. Post Substack content manually:
- Jun 24, 12:00 PM ET: Substack Post 1 (5 Biomarkers long-form) — assemble from Thread 1 + LinkedIn Post 1 + PDF
- Jul 1, 11:00 AM ET: Substack Post 2 (How to read your own bloodwork) — source: `assets/social/substack-post-2-read-your-own-bloodwork.md` (REVIEW label, await Dre finalization)

### 3.7 Substack Welcome Email automation queue

Substack automation runs separately. Load Welcome Emails 2-5 (from `assets/emails/substack-welcome-2-to-5.md`) into Substack's email automation queue. ~30 minutes of Dre time.

---

## Part 4 — Post-launch monitoring (after import)

### 4.1 Daily EOD check-in

Every evening, 9:00 PM CT:
- Open Postiz → Calendar
- Check what published that day
- Note any errors (failed publishes, draft saves instead of scheduled)
- Capture engagement metrics from each platform's native dashboard
- Log to `stores/live-execution/daily-rollups/[date]-rollup.md`

### 4.2 Micro-iteration queue

Per Decision 14, the iteration loop runs every 24 hours. When real data lands on each post, Mavis proposes a derivative. Dre approves + adds to Postiz as a new scheduled post.

### 4.3 Weekly content review (every Sunday)

- Review which posts performed best (per platform's native analytics)
- Adjust next week's calendar based on what landed
- Tag high-performing assets for repurposing

---

## What gets scheduled where (summary)

| Content type | Postiz? | Manual? |
|--------------|---------|---------|
| X threads | ✅ Bulk upload via CSV | Manual split if Postiz doesn't auto-thread |
| X standalones | ✅ Bulk upload via CSV | None |
| LinkedIn posts | ✅ Bulk upload via CSV | Manual first-comment link post |
| LinkedIn carousels | ✅ Bulk upload via CSV | ⚠️ Slides need to be created first (9 slides for Carousel 1) |
| Skool pinned posts | ❌ Not in Postiz | Manual post in Skool |
| Substack posts | ❌ Not in Postiz | Manual publish in Substack |
| Substack emails | ❌ Not in Postiz | Manual load into Substack automation |

---

## Time estimate

| Step | Time |
|------|------|
| 1.1 Connect integrations | 2 min |
| 1.2 Create folders | 2 min |
| 1.3 Set up time slots | 3 min |
| 1.4 Voice templates (optional) | 3 min |
| 2.1-2.6 Import CSV | 5 min |
| 3.1-3.7 Manual follow-ups | 10 min |
| **Total** | **~30 minutes** |

After setup, daily maintenance is ~10 minutes (EOD check-in + iteration proposals).

---

## Troubleshooting

### "Postiz doesn't recognize the thread format"
- Manual workaround: copy content from CSV, split on `---`, paste tweet-by-tweet in X
- Each tweet = one scheduled Postiz post
- Use the `notes` column to identify thread membership

### "Postiz asks for different column names"
- Map: `date` → publish date, `time` → publish time, `channel` → account, `type` → post type, `content` → content, `link` → outbound URL
- Ignore the `asset_source` and `notes` columns (Dre's reference only)

### "First-comment links not auto-posting"
- Manual: post the first-comment within 1-2 min of the LinkedIn publish
- Alternative: upgrade to a Postiz plan that supports auto first-comments

### "LinkedIn carousel needs slides that don't exist yet"
- ⚠️ The 9 slides for Carousel 1 (5 Biomarkers) need to be created BEFORE Postiz can upload the media
- Source design: `assets/social/linkedin-carousel-5-biomarkers.md`
- Time to render: ~2 hours (Mavis can generate via design tool once you provide the visual brief)

### "Schedule conflicts with manual posts"
- Skool Jun 27 + Substack Jun 24 + Jul 1 are managed separately. Don't double-schedule them in Postiz.

---

## What this guide enables

After import, the calendar runs on autopilot:
- 14 days of pre-scheduled content
- Every post has UTM attribution for tracking
- Every post is voice + compliance reviewed
- The monitoring loop runs daily + queues iterations
- The brand publishes 1-2 posts/day on X + 1-2 LinkedIn posts/week on schedule

The architecture shifts from "build assets" to "publish on autopilot + iterate on winners."

---

*Last updated: 2026-06-24 12:16 CT*
*Ship-ready: yes. Total setup + import time: ~30 minutes.*