---
type: linkedin-company-page-readiness
asset: linkedin-company-page-post-creation-checklist
status: ✅ FINAL (locked 2026-06-24 15:50 CT)
purpose: step-by-step checklist for AFTER Dre creates the Dose of Proof LinkedIn Company Page
companion_to: assets/scheduling/linkedin-company-page-action.md (page creation guide) + assets/scheduling/find-linkedin-company-page-channel.sh (channel ID discovery)
---

# LinkedIn Company Page — Post-Creation Readiness Checklist

> **This document is for AFTER Dre has created the Dose of Proof LinkedIn Company Page.** The page creation guide is at `linkedin-company-page-action.md`. This document walks through what happens next.

---

## Phase 1 — Verify the Company Page is live (5 min)

After Dre completes the page creation steps in `linkedin-company-page-action.md`:

1. [ ] Log out of personal LinkedIn (`andré@...` or whatever the personal email is)
2. [ ] Log into LinkedIn as the **Dose of Proof Company Page admin** (use the admin personal account)
3. [ ] Verify the page is visible: search "Dose of Proof" in LinkedIn → should appear with company logo
4. [ ] Verify you can post to the page (test post is optional — just check the UI shows "Post as Dose of Proof")
5. [ ] Verify page followers = 0 (expected, since brand-new)

**If any of these fail:** LinkedIn Company Pages can take 5-30 minutes to fully propagate. Wait 10 min and retry. If still failing, contact LinkedIn support via the page admin UI.

---

## Phase 2 — Connect the Company Page to Buffer (5 min)

The Company Page needs to be connected to Buffer before Mavis can push content to it.

1. [ ] Open Buffer in browser: https://buffer.com
2. [ ] Click your avatar (top-right) → **Channels**
3. [ ] Click **Connect a Channel** → Select **LinkedIn** → Click **Connect**
4. [ ] Buffer redirects to LinkedIn OAuth screen
5. [ ] **CRITICAL:** When LinkedIn asks "Which profile do you want to connect?" — **select the Dose of Proof Company Page**, NOT the personal profile
6. [ ] LinkedIn may ask "Allow Buffer to manage your LinkedIn Page?" — click **Allow**
7. [ ] Buffer confirms connection — page now shows in Channels list with the Company Page name
8. [ ] **Verify the channel name shows "Dose of Proof" or the company name, not your personal name**

**If Buffer shows the personal profile:** You selected the wrong account in OAuth. Disconnect, retry, and select the Company Page explicitly. (Buffer sometimes defaults to the most recently authenticated LinkedIn account, which is usually personal.)

**If Buffer doesn't show Company Page as option:** The Company Page may not be a "Super Admin" or "Content Admin" for your personal LinkedIn account. To fix:
- Go to LinkedIn Company Page → Settings → Admins → verify your personal account is listed as Super Admin
- If not, add yourself as Super Admin via the existing admin
- Wait 5 minutes for LinkedIn to propagate
- Retry Buffer connection

---

## Phase 3 — Discover the new channel ID (1 min)

Once the Company Page is connected to Buffer:

1. [ ] Open Terminal
2. [ ] Run: `bash "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof/assets/scheduling/find-linkedin-company-page-channel.sh"`
3. [ ] Script queries Buffer API and outputs ALL channels
4. [ ] Look for the line that says `[COMPANY PAGE - USE THIS]`
5. [ ] Copy the channel ID (looks like `6a3c1e195ab6d2f10669e738`)
6. [ ] **Send that channel ID to Mavis** (via chat reply, screenshot, or paste into the next conversation)

**What Mavis does with the channel ID:**
- Updates `/tmp/buffer_bulk_push.py` with the new channel ID (replaces the personal LinkedIn one)
- Updates `assets/scheduling/buffer-bulk-upload-week-1-2.csv` LinkedIn rows with the new channel ID
- Re-queues LinkedIn Post 1 (Origin Story) + LinkedIn Carousel 1 (5 Biomarkers) for the Company Page
- Runs the Buffer push script with the new channel

---

## Phase 4 — Schedule the LinkedIn brand content (Mavis fires automatically)

Once Mavis receives the new channel ID, Mavis:

1. **Re-queues LinkedIn Post 1 (Origin Story)** — original target was Tue Jun 24 10:00 AM ET (now past, so Mavis schedules for next available slot on Company Page)
2. **Re-queues LinkedIn Carousel 1 (5 Biomarkers)** — original target was Tue Jul 1 9:00 AM ET (still in the future)
3. **Pushes both via Buffer API** to the Company Page
4. **Verifies** both posts are scheduled on the Company Page (not personal) by re-querying Buffer
5. **Adds the LinkedIn first-comment Substack link** per the brand's locked convention (1-2 min after publish)
6. **Updates OPERATIONS-LOG** with the Company Page channel ID + post confirmation

**Time to ship both posts:** ~5 min of automated push + 5 min of Mavis verification.

---

## Phase 5 — Brand boundary cleanup (Dre action, 2 min)

The Jul 1 LinkedIn carousel that was accidentally pushed to **personal LinkedIn** during API exploration needs to be deleted:

1. [ ] Open Buffer UI → Channels
2. [ ] Click the **personal LinkedIn channel** (the one labeled with your personal name)
3. [ ] Click **Queue** or **Scheduled**
4. [ ] Find the post: "5 Biomarkers That Actually Moved the Needle" (scheduled for Jul 1, 9:00 AM ET)
5. [ ] Click the post → **Edit** → **Delete this post**
6. [ ] Confirm deletion

**Why this matters:** Brand content on personal LinkedIn is a brand/operator boundary violation. The Company Page exists now, so the brand surface for LinkedIn moves there. The personal LinkedIn post must be removed.

**After deletion:** Update OPERATIONS-LOG via Mavis — the personal LinkedIn cleanup is logged as complete.

---

## Phase 6 — Verify everything (Dre + Mavis)

Final verification before the LinkedIn brand surface is fully operational:

- [ ] Company Page exists and is searchable on LinkedIn ✅ (Phase 1)
- [ ] Company Page connected to Buffer ✅ (Phase 2)
- [ ] Channel ID discovered via shell script ✅ (Phase 3)
- [ ] Mavis updated Buffer push script + CSV with new channel ID ✅ (Phase 4)
- [ ] LinkedIn Post 1 scheduled on Company Page ✅ (Phase 4)
- [ ] LinkedIn Carousel 1 scheduled on Company Page ✅ (Phase 4)
- [ ] First-comment Substack links queued ✅ (Phase 4)
- [ ] Personal LinkedIn Jul 1 carousel deleted ✅ (Phase 5)
- [ ] OPERATIONS-LOG updated with new channel ID + post confirmations ✅ (Phase 4)

**Once all 9 are checked:** The LinkedIn brand surface is fully operational and the Buffer channel architecture matches Decision 18 (REVISED).

---

## Timeline summary (target completion)

| Phase | Owner | Time | Status |
|-------|-------|------|--------|
| 1 — Verify page live | Dre | 5 min | ⏳ After page creation |
| 2 — Connect to Buffer | Dre | 5 min | ⏳ After page creation |
| 3 — Discover channel ID | Dre | 1 min | ⏳ After Buffer connection |
| 4 — Schedule brand posts | Mavis | ~10 min | ⏳ After Dre sends channel ID |
| 5 — Delete personal LinkedIn cleanup | Dre | 2 min | ⏳ After Mavis confirms scheduling |
| 6 — Verify all green | Dre + Mavis | 5 min | ⏳ Final pass |

**Total post-creation work:** ~28 minutes (split Dre ~13 min + Mavis ~15 min).

**Target completion:** Same day as page creation. If Dre creates the page on Fri Jun 27, everything is operational by Fri Jun 27 evening.

---

## What Mavis will fire AUTOMATICALLY (no Dre input needed)

Once Dre sends the channel ID:
- Buffer push script re-run with new channel
- LinkedIn Post 1 + Carousel 1 scheduled on Company Page
- OPERATIONS-LOG updated

**Dre just needs to:**
1. Create the Company Page (20 min, separate guide at `linkedin-company-page-action.md`)
2. Connect to Buffer (5 min)
3. Run the channel discovery shell script (1 min)
4. Send Mavis the channel ID (30 sec)

---

## Fallback if Company Page creation hits friction

**If the Company Page can't be created today:**
- Continue publishing on personal LinkedIn for ad-hoc brand mentions (NOT scheduled brand content)
- LinkedIn Post 1 + Carousel 1 stay in Buffer as drafts until Company Page exists
- Manual X publishing via `manual-x-scheduling-list.md` continues as the primary authority engine
- Buffer push script remains disabled for LinkedIn (no Company Page to push to)

**Friction log:** If Company Page creation hits unexpected friction, log it in OPERATIONS-LOG as "Decision 21 — LinkedIn Company Page friction event" with the specifics. Mavis can then advise on the workaround path.

---

*Last updated: 2026-06-24 15:50 CT*
*Companion to: `assets/scheduling/linkedin-company-page-action.md` (page creation guide)*
*Companion to: `assets/scheduling/find-linkedin-company-page-channel.sh` (channel ID discovery script)*