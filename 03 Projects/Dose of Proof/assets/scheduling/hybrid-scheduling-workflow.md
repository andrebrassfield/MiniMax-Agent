---
type: operational-guide
asset: hybrid-scheduling-workflow-v2
status: ✅ FINAL (locked 2026-06-24, Decision 18 revised)
purpose: clear operating manual for the Buffer + Postiz dual-tool architecture — REVISED to reflect that LinkedIn brand posting is LIVE on Dose of Proof LinkedIn Company Page (created 2026-06-24)
audience: Dre (operator) + Mavis (orchestrator)
companion_to: assets/scheduling/postiz-bulk-upload-week-1-2.csv + assets/scheduling/manual-x-scheduling-list.md + /tmp/buffer_bulk_push.py + /tmp/postiz_rest_push.py + assets/scheduling/linkedin-company-page-action.md
decision_locked: Decision 18 (REVISED) — Postiz primary for visual platforms, Buffer for X + LinkedIn (Dose of Proof Company Page, ACTIVE 2026-06-25), manual fallback for X during rate limits
---

# Hybrid Scheduling Workflow — Dose of Proof (v2, REVISED)

> The brand operates two schedulers in parallel: **Buffer for X** (and LinkedIn once the Company Page exists) and **Postiz for visual-first platforms**. This document is the single source of truth for how to use both, including the manual fallback when rate limits hit.

---

## 1. The Platform → Tool Map (REVISED Decision 18)

| Platform              | Tool       | Notes                                          | Status                |
|-----------------------|------------|------------------------------------------------|-----------------------|
| **X (Twitter)**       | **Buffer**  | Best thread support + proven API               | Rate limited 24h      |
| LinkedIn (Brand)      | **Buffer**  | **Dose of Proof Company Page ACTIVE (channel ID `6a3c4a245ab6d2f1066ad8be`)** — Postiz deprioritized per Decision 18 REV (Buffer is the LinkedIn home now) | ✅ **CONNECTED** |
| Instagram             | Postiz     | Already connected (visual-first)               | ✅ Ready              |
| TikTok                | Postiz     | Already connected (native video)               | ✅ Ready              |
| Facebook              | Postiz     | Already connected                              | ✅ Ready              |
| Pinterest             | Postiz     | Already connected (evergreen visual)            | ✅ Ready              |
| YouTube               | Postiz     | Already connected (long-form + Shorts)          | ✅ Ready              |
| Skool                 | Manual     | Not integrated with either scheduler           | Manual                |
| Substack              | Manual     | Native Substack scheduler                       | Manual                |

**Why this revised split:**
- **X is the highest-leverage platform** → Buffer (best thread support, proven GraphQL API)
- **Visual-first platforms** → Postiz (already connected, best for IG/TikTok/Pinterest/YouTube)
- **LinkedIn brand** → waiting on Company Page creation; will use Postiz once connected (preferred over Buffer for brand posts)
- **Personal LinkedIn** → NEVER use for brand content (boundary per Decision 18 correction)

---

## 2. Buffer — X workhorse (and LinkedIn once Company Page exists)

### 2.1 Setup (one-time, mostly done)
- Buffer account: andrebrassfield@gmail.com
- Organization ID: `69de6c292b24d8cddc01c3cb`
- X channel ID: `6a3c1df95ab6d2f10669e64e` (@doseofproof) — **PRIMARY CHANNEL**
- LinkedIn channel ID (personal — DO NOT USE): `6a3c1e195ab6d2f10669e738`
- LinkedIn Company Page ID: `6a3c4a245ab6d2f1066ad8be` (Dose of Proof, handle: doseofproof, URN: `urn:li:organization:109653219`) — CREATED 2026-06-24, ACTIVE in Buffer 2026-06-25 13:20 CT
- API key: in `/tmp/buffer_bulk_push.py`

### 2.2 Push script
- Location: `/tmp/buffer_bulk_push.py`
- Reads: `assets/scheduling/manual-x-scheduling-list.md` (manual fallback) OR CSV via push
- Writes: posts to Buffer via `createPost` GraphQL mutation
- Output: log to `/tmp/buffer_push_log.txt`

### 2.3 To push X posts:
**During rate-limit recovery (~24h from Jun 24 13:30 CT):**
- Use `assets/scheduling/manual-x-scheduling-list.md` for copy-paste manual publishing
- Total manual work: ~35-50 minutes for all 13 X posts

**After rate limit clears:**
1. Re-run: `python3 /tmp/buffer_bulk_push.py`
2. Verify in Buffer: https://publish.buffer.com/calendar
3. Approve + edit in Buffer UI as needed

### 2.4 Known Buffer behaviors (discovered during testing)
1. **Past-dated posts** → use `saveToDraft: true` (Buffer refuses past-dated `scheduled` posts)
2. **saveToDraft + thread** → broken (returns empty data); threads must be `scheduled` directly
3. **Rate limits** → ~10 calls/minute; exponential backoff required
4. **LinkedIn carousels** → no API asset support; manual upload in Buffer UI required
5. **First-comment** → supported via metadata but not implemented in our script yet

### 2.5 LinkedIn Company Page — activation complete ✅
- **Channel ID:** `6a3c4a245ab6d2f1066ad8be`
- **Display name:** Dose of Proof
- **Type:** page (LinkedIn Company Page, not profile)
- **Service ID:** `urn:li:organization:109653219`
- **Created:** 2026-06-24
- **Activated in Buffer:** 2026-06-25 13:20 CT (cron `linkedin-company-page-activation-retry`)
- **Posts currently scheduled on Company Page:**
  - LinkedIn Post 1 (Origin Story) → `id=6a3d72351d5ae3f1b8b07e99` (DRAFT — original CSV date Jun 24 was past; Dre to flip to scheduled via Buffer UI)
  - LinkedIn Carousel 1 (5 Biomarkers) → `id=6a3d721499c1f2a16760bf23` (SCHEDULED, due 2026-07-01 09:00 ET)
- **Personal LinkedIn (`6a3c1e195ab6d2f10669e738`):** deprecated for brand content per Decision 18. Dre to clean up duplicate carousel entries from earlier push run.

---

## 3. Postiz — visual-first scheduler

### 3.1 Setup (one-time, already done)
- Postiz account: connected
- Integrations connected: Facebook, Instagram, Pinterest, TikTok, YouTube (5 channels)
- **NOT connected:** X, LinkedIn (X → Buffer; LinkedIn → pending Company Page creation)
- API key: in `/tmp/postiz_rest_push.py`

### 3.2 Push script
- Location: `/tmp/postiz_rest_push.py`
- Reads: `assets/scheduling/postiz-bulk-upload-week-1-2.csv`
- Writes: posts to Postiz via REST API
- Output: log to `/tmp/postiz_push_log.txt`

### 3.3 Postiz-ready CSV (this iteration)
**Location:** `assets/scheduling/postiz-bulk-upload-week-1-2.csv`

**Contents:** 17 posts adapted for FB/IG/TikTok/Pinterest/YouTube voice, derived from the X/LinkedIn calendar:
- **Facebook (5 posts):** Text posts — publish as-is, no media required
- **Instagram (3 carousels + 1 reel):** Requires 9-slide images per carousel + 1 vertical video for the reel — **GATING ASSET: visuals must be created first**
- **TikTok (2 videos):** Requires 30-second vertical videos — **GATING ASSET: video scripts ready, recording pending**
- **Pinterest (3 pins):** Requires tall images — **GATING ASSET: visual asset needed**
- **YouTube Shorts (3 videos):** Requires vertical video — can be repurposed from TikTok scripts

**Note:** Visual assets are the bottleneck. Until they're created, Postiz can only push the 5 Facebook text posts.

### 3.4 What's ready to push immediately
- ✅ 5 Facebook text posts (no media required)
- ⚠️ All other platforms require visual asset creation first

### 3.5 To push Postiz content:
1. Run: `python3 /tmp/postiz_rest_push.py`
2. Verify in Postiz: https://postiz.com/agent
3. Visual assets must be uploaded via Postiz UI for IG/TikTok/Pinterest/YouTube posts

---

## 4. Manual scheduling (Buffer rate-limit fallback)

### 4.1 When Buffer is rate-limited (24h from push time):
- Use `assets/scheduling/manual-x-scheduling-list.md`
- Dre manually publishes the X posts via X.com / TweetDeck / X Studio
- Total work: ~35-50 minutes for all 13 X posts

### 4.2 When visual assets aren't ready:
- Skip IG/TikTok/Pinterest/YouTube posts
- Push Facebook text posts only
- Defer visual-first posts to Week 3-4 when assets are created

### 4.3 Manual scheduling for Skool + Substack (independent of schedulers):
- **Substack:** Publish via Substack dashboard (already set up)
- **Skool:** Post manually in Skool community (already set up)

---

## 5. The weekly calendar process (REVISED)

### 5.1 Monday morning — Dre's weekly prep

1. **Check rate limit status** for Buffer (recover window = ~24h from last push)
2. **Review last week's metrics** (X analytics, LinkedIn analytics, Postiz analytics)
3. **Open OPERATIONS-LOG** → check "Live Execution" section → review what published + iteration decisions
4. **Pull this week's posts** from the pre-launch calendar
5. **Determine push path per post:**
   - X → Buffer (or manual if rate limited)
   - FB text → Postiz
   - IG/TikTok/Pinterest/YT → Postiz (only if visual assets exist)
   - LinkedIn → Postiz (only after Company Page connected)
   - Substack → Manual (Substack dashboard)
   - Skool → Manual (Skool community)
6. **Generate CSVs** (one per tool) for the week
7. **Run push scripts** (or manual publish)
8. **Verify in tool UIs** — approve drafts, adjust timing

### 5.2 Tuesday–Saturday — monitoring loop

- Every evening, Mavis reviews the day's published assets
- If a post outperforms, Mavis queues a micro-iteration derivative
- Dre approves or modifies the iteration
- The iteration ships within 24h via the appropriate tool

### 5.3 Sunday — community + planning

- Skool community engagement (manual post)
- Substack long-form post (manual publish)
- Week ahead planning

---

## 6. Content preparation workflow per platform

### X (Buffer)
- Voice: raw, direct, "I'm still in this process"
- Format: 280-char tweets (single) or 6-10 tweet threads
- CTA: Substack link with UTM parameters
- Source files: `assets/social/x-thread-*.md`

### LinkedIn Company Page (Postiz — pending Company Page creation)
- Voice: professional but raw, personal story + proof
- Format: 200-500 word posts, 8-10 slide carousels
- CTA: Substack link in **first comment** (not post body)
- Source files: `assets/social/linkedin-post-*.md` + `assets/social/linkedin-carousel-*.md`

### Instagram (Postiz — pending visual assets)
- Voice: visual-first, lifestyle-aware
- Format: 9-slide carousels + 30-60s reels
- Source files: Postiz-ready CSV (this iteration)

### TikTok (Postiz — pending video assets)
- Voice: punchy, hook-first, data-visualization
- Format: 30-second vertical video
- Source files: Postiz-ready CSV (this iteration)

### Facebook (Postiz — ready now)
- Voice: longer-form text posts (Facebook tolerates 500+ words)
- Format: Text posts, link shares
- Source files: Postiz-ready CSV (5 posts ready to ship immediately)

### Pinterest (Postiz — pending images)
- Voice: educational, evergreen
- Format: Tall pins (2:3 ratio) with descriptive text
- Source files: Postiz-ready CSV

### YouTube Shorts (Postiz — pending video assets)
- Voice: same as TikTok (vertical-first)
- Format: 60-second Shorts
- Source files: Postiz-ready CSV (can repurpose TikTok scripts)

### Substack (manual)
- Voice: long-form, proof-anchored
- Format: 800-3,500 word posts
- Source files: `assets/social/substack-post-*.md`

### Skool (manual)
- Voice: community-conversational
- Format: discussion prompts
- Source files: `assets/skool/inner-circle-onboarding-first-7-days.md`

---

## 7. Cross-posting rules

### When to cross-post
- ❌ **NEVER** raw cross-post between X and LinkedIn (different voice + format)
- ❌ **NEVER** brand content on Dre's personal LinkedIn (boundary)
- ❌ **NEVER** cross-post between Skool/Substack (different brand surfaces)
- ✅ **OK** to repurpose: take a long Substack post → derive X thread + FB post + (later) IG carousel + TikTok video
- ✅ **OK** to share: share the Substack link across all platforms

### Voice adaptation per platform
Same data, different framing:
- **X:** raw, personal, immediate
- **LinkedIn:** professional framing, longer narrative
- **Facebook:** full story, longer posts OK
- **Instagram:** visual-first, lifestyle framing
- **TikTok:** hook in 3 seconds, data visualization
- **Pinterest:** evergreen, educational, searchable
- **YouTube Shorts:** same as TikTok, slightly longer form

---

## 8. Buffer vs Postiz decision matrix

| Use Buffer when...                          | Use Postiz when...                           |
|---------------------------------------------|----------------------------------------------|
| Posting to X (threads + standalones)        | Posting to FB / IG / TikTok / YT / Pinterest |
| LinkedIn once Company Page is connected     | Need a visual-first scheduler                |
| Need thread support (X)                     | FB/IG/TikTok/YT/Pinterest accounts already connected |
| Buffer rate limit hasn't been triggered     | Need visual asset upload support             |
| Want GraphQL API access (scriptable)         | LinkedIn Company Page is connected           |

---

## 9. Files referenced (this iteration)

| File | Purpose |
|------|---------|
| `assets/scheduling/postiz-bulk-upload-week-1-2.csv` | 17 Postiz-ready posts for FB/IG/TikTok/Pinterest/YouTube |
| `assets/scheduling/manual-x-scheduling-list.md` | Copy-paste ready X posts for manual publishing during Buffer rate limit |
| `assets/scheduling/linkedin-company-page-action.md` | Step-by-step action item for creating Dose of Proof Company Page |
| `/tmp/buffer_bulk_push.py` | Production Buffer push script |
| `/tmp/postiz_rest_push.py` | Production Postiz push script |
| `assets/scheduling/hybrid-scheduling-workflow.md` | v1 of this document (superseded by v2) |

---

## 10. Action items (priorities)

### 🔴 HIGH — this week (by Friday Jun 27)

1. **Create Dose of Proof LinkedIn Company Page** — Dre action, ~20 min
   - Action item: `assets/scheduling/linkedin-company-page-action.md`
   - Once created: connect to Postiz (preferred for brand posts)
   - Update hybrid-scheduling-workflow.md with the new channel ID

2. **Manual X publishing during Buffer rate limit** — Dre action, ~35-50 min
   - File: `assets/scheduling/manual-x-scheduling-list.md`
   - Push via X.com / TweetDeck while Buffer recovers

3. **Push 5 Facebook text posts via Postiz** — Dre or Mavis action, ~5 min after API verification
   - File: `assets/scheduling/postiz-bulk-upload-week-1-2.csv` (FB rows)
   - No visual assets required

### 🟡 MEDIUM — when assets exist

4. **Create visual assets for IG/TikTok/Pinterest/YouTube** — Dre or designer
   - 9-slide carousels × 3 (IG)
   - Vertical videos × 5 (TikTok + YT Shorts)
   - Tall pin images × 3 (Pinterest)

5. **Re-run Buffer bulk push** after rate limit clears (~24h)
   - Wait until Jun 25 ~13:30 CT
   - Run: `python3 /tmp/buffer_bulk_push.py`

### 🟢 LOW — Week 3+

6. **Postiz content expansion** — Q3 2026, when visual derivative assets exist
7. **Dose Calc SaaS** — Q4 2026 launch
8. **Reddit/Facebook group value-first participation** — Phase 2 of 90-day roadmap

---

*Last updated: 2026-06-24 15:30 CT*
*Decision 18 (revised): Postiz primary for visual platforms, Buffer for X (and LinkedIn Company Page once created), manual fallback for X during rate limits, LinkedIn Company Page pending creation by Friday Jun 27.*

---

## Appendix A — Known Buffer quirks (operational reference)

1. **saveToDraft + thread = broken** — threads must be `scheduled` directly
2. **Past-dated posts fail silently** — empty data response, no error
3. **Rate limits ~10 calls/min** — exponential backoff required
4. **LinkedIn carousels** require manual UI upload
5. **First-comment** supported but not yet in our script

## Appendix B — Postiz Push Notes

- REST API endpoint: `https://api.postiz.com/public/v1/`
- Auth: `Authorization: <API_KEY>` (no Bearer prefix)
- `createPost` payload structure per OpenAPI spec
- Asset upload (media) currently manual via UI

## Appendix C — Channel ID Reference

| Tool  | Platform | Channel ID | Notes |
|-------|----------|-----------|-------|
| Buffer | X | `6a3c1df95ab6d2f10669e64e` | @doseofproof — ready |
| Buffer | LinkedIn (personal) | `6a3c1e195ab6d2f10669e738` | ❌ DO NOT USE for brand content |
| Buffer | LinkedIn (Company) | `6a3c4a245ab6d2f1066ad8be` | Dose of Proof Company Page — ACTIVE 2026-06-25 13:20 CT |
| Postiz | Facebook | `cmqjmkoyf033cmm0ykc4p8hhg` | ready |
| Postiz | Instagram | `cmqjmlih500f1p40yrz8i37fp` | ready (visual assets pending) |
| Postiz | Pinterest | `cmqjn9qv003a1mm0y406rrdcd` | ready (visual assets pending) |
| Postiz | TikTok | `cmqjmn2gk00fnp40yvtllpvf2` | ready (video assets pending) |
| Postiz | YouTube | `cmqjmvmec0364mm0ykc8jfdrn` | ready (video assets pending) |