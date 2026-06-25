---
type: spec
asset: content-engine-spec
status: ✅ DRAFT 1 (locked 2026-06-25, implementation in progress)
purpose: design the Dose of Proof daily content engine + cron + queue + push flow
scope: Phase 2 of postiz calendar repopulation; replaces the one-time 14-day CSV
audience: Mavis (implementation), Dre (review)
---

# Dose of Proof — Content Engine Spec

> **Why this spec exists:** The Postiz 14-day CSV was a one-time batch. We need a sustainable engine that produces 5-10 posts/day indefinitely. This document is the design.

---

## Goals (per Andre's directive)

1. **5-10 posts/day** across the 5 confirmed brand channels
2. **Sustainable cadence** — supply continues past July 7 without manual batches
3. **Strict compliance** — 8-item audit on every post
4. **Single Substack CTA** where conversion is present
5. **Three pillars + PCAC/regulatory angle** as the content backbone
6. **Hook bank + existing long-form corpus** as source material (no LLM-from-scratch every day)
7. **Lean volume** — protect sales blocks + terrain capacity

---

## Architecture (5 components)

```
                ┌─────────────────────────────────────────┐
                │  1. SOURCE CORPUS (read-only)            │
                │  - assets/social/* (10 X threads,        │
                │    5 LinkedIn carousels, 3 Substack)      │
                │  - assets/social/hook-bank-next-wave.md  │
                │  - specs/prelaunch-content-calendar.md   │
                └─────────────────┬───────────────────────┘
                                  │
                                  ▼
                ┌─────────────────────────────────────────┐
                │  2. COMPLIANCE GATE (hard block)         │
                │  - Banned phrases list                   │
                │  - Single-CTA rule                       │
                │  - Pillar rotation rule                  │
                │  - No prescriptive dosing                │
                │  - No Swiss Chems / gray-market         │
                │  - Brand voice anchor check              │
                │  - Editorial typography only             │
                │  - PCAC framework anchored               │
                └─────────────────┬───────────────────────┘
                                  │
                                  ▼
                ┌─────────────────────────────────────────┐
                │  3. DAILY GENERATOR (cron at 21:00 CT)   │
                │  - Pillar rotation (P1/P2/P3/PCAC)       │
                │  - Channel split (FB 3-4 / IG 1 / Pin 1) │
                │  - Adapts long-form → short-form         │
                │  - Generates carousel/pin images via MCP │
                │  - Writes to queue/drafts-YYYY-MM-DD.mdl │
                └─────────────────┬───────────────────────┘
                                  │
                                  ▼
                ┌─────────────────────────────────────────┐
                │  4. QUEUE                                │
                │  - queue/drafts-YYYY-MM-DD.mdl (auto)    │
                │  - queue/pins-YYYY-MM-DD.mdl (Dre push) │
                │  - Each line: pillar | channel | date |  │
                │    time | content | images | compliance │
                └─────────────────┬───────────────────────┘
                                  │
                                  ▼
                ┌─────────────────────────────────────────┐
                │  5. PUSH (cron at 21:30 CT)              │
                │  - Reads queue/ for tomorrow's posts    │
                │  - Uploads images to Postiz CDN          │
                │  - Calls Postiz REST API                 │
                │  - Pinterest: writes to pin queue for    │
                │    Dre's manual UI push                  │
                └─────────────────────────────────────────┘
```

---

## Component 1 — Source Corpus

**Locked inputs** (read-only):
- `assets/social/x-thread-1..10-*.md` (10 X threads)
- `assets/social/linkedin-carousel-1..5-*.md` (5 LinkedIn carousels)
- `assets/social/substack-post-1..3-*.md` (3 Substack posts)
- `assets/social/hook-bank-next-wave.md` (8 standalone tweet hooks + 6 next-wave hooks)
- `specs/prelaunch-content-calendar.md` (30-day plan)

**Adaptation strategy** (not LLM-from-scratch):
- Each X thread → compress into 1 Facebook text post (no hashtags, FB-voice)
- Each X thread → adapt into 1 Instagram carousel (9 slides, brand style)
- Each LinkedIn carousel → reuse slides for Instagram (already done in carousel-1-5biomarkers / carousel-2-pcac-framework / carousel-3-pcac-meeting)
- Each Substack post → 1 Pinterest pin (single image) + 1 FB text excerpt
- Each standalone hook → 1 FB text post (full hook + brief body)

This compresses ~30 source assets into ~90-120 derived short-form posts over the 14-day window.

---

## Component 2 — Compliance Gate (8-item)

Applied to every generated draft. Hard block on any failure.

1. **Educational/curatorial only** — no prescriptive dosing claims
2. **Single CTA discipline** — `doseofproof.substack.com` only; no Buffer/Vercel/Shopify URLs
3. **Zero unsubstantiated claims** — biomarker numbers = Dre's lived data (validated against `assets/social/x-thread-1-5-biomarkers.md`)
4. **No compound-specific dosing protocols** — Pillar 3 content framed as math/utility, not advice
5. **No Swiss Chems / gray-market mentions** — Decision 12 still binding
6. **Brand voice** — raw, stoic, proof-centered. Banned phrases: `cure`, `treat`, `heal`, `secret`, `game-changing`, `revolutionary`, `breakthrough`, `unlock`, `unleash`, `synergy`, `leverage`, `value-add`
7. **Editorial typography only** — no stock photos, no decorative imagery (visual layer)
8. **PCAC framework anchored** — claims stay upstream of regulatory decisions

Implementation: `scripts/dop_compliance.py` — programmatic checks for items 1-7, LLM-as-judge for item 6 (brand voice) optional.

---

## Component 3 — Daily Generator

**Schedule:** Cron at 21:00 CT daily (`mavis cron`).

**Inputs:**
- Current date → determines pillar + channel split
- Source corpus (read all `.md` files in `assets/social/`)
- Hook bank (read `assets/social/hook-bank-next-wave.md`)
- Pillar rotation rule (P1 → P2 → P3 → PCAC-Deep-Dive → repeat)

**Process per day:**
1. Determine pillar (rotation rule, weekday-derived)
2. Pick 1 source asset per channel from corpus
3. For Facebook (3-4 posts/day):
   - Extract 3-4 standalone hooks from the picked source
   - Each post = hook + 2-3 sentence context + Substack CTA + 2-3 hashtags
4. For Instagram (1 carousel/day):
   - Pick next source asset that has a carousel variant OR
   - Generate 9-slide carousel from source via LLM compression
   - Render slides via matrix MCP (proven at ~6 min/9 slides per Decision 25)
5. For Pinterest (1 pin/day):
   - Pick a Substack post or LinkedIn carousel
   - Render single 2:3 image via matrix MCP
   - Write to `queue/pins-YYYY-MM-DD.mdl` for Dre's manual UI push

**Output:** `queue/drafts-YYYY-MM-DD.mdl`

```
# Draft queue — YYYY-MM-DD
# Generated YYYY-MM-DD HH:MM CT by dop-engine v0.1

post_id | pillar | channel | date | time | status | compliance | content | image_paths

dop-fb-001 | P1 | facebook | YYYY-MM-DD | 09:00 | approved | PASS | ... | 
dop-fb-002 | P1 | facebook | YYYY-MM-DD | 14:00 | approved | PASS | ... |
...
```

---

## Component 4 — Queue

**Files:**
- `queue/drafts-YYYY-MM-DD.mdl` — all auto-pushed posts (FB + IG)
- `queue/pins-YYYY-MM-DD.mdl` — Pinterest pins for Dre manual push
- `queue/published-YYYY-MM-DD.mdl` — push receipts (after push)

**Append-only discipline:** No editing after write. Rejection = new draft with `status: rejected` + `status: replacement` line.

---

## Component 5 — Push

**Schedule:** Cron at 21:30 CT daily.

**Script:** `scripts/dop_push.py` — wraps `/tmp/postiz_push_v2.py` with queue-aware logic:
1. Read `queue/drafts-YYYY-MM-DD.mdl`
2. For each `status: approved` row:
   - Upload images to Postiz (cache by local path)
   - Schedule via Postiz API with correct channel settings
   - Move receipt to `queue/published-YYYY-MM-DD.mdl`
3. Pinterest rows: skip auto-push, write to `queue/pins-YYYY-MM-DD.mdl` with explicit "Dre manual push" annotation

**Brand/operator boundary check:** before pushing, verify the target channel is in the confirmed-brand list. Hard block if LinkedIn, Threads, or any unconfirmed channel.

---

## Volume math (lean ramp → scaled)

**Initial (week 1 of engine):** 5 posts/day
- Facebook: 3 text posts (cheap, sustainable)
- Instagram: 1 carousel (9 slides)
- Pinterest: 1 pin (Dre UI push)

**Target (week 2+):** 7-10 posts/day
- Facebook: 4-5 text posts
- Instagram: 1 carousel
- Pinterest: 1 pin (Dre)
- + ramp to 2 IG carousels/day once image generation proves reliable

**v0.2 (shipped 2026-06-25):** 11 posts/day — "take over the market"
- Facebook text: **6** posts (08:00 / 11:00 / 13:30 / 16:00 / 18:30 / 21:00 ET, ~2.5hr cadence)
- Facebook multi-image: **1** post/day (reuses IG carousel slides, 10-image cap)
- Instagram carousel: **1** carousel/day (10 slides, Postiz IG cap)
- Pinterest pins: **3** pins/day (cover / data / CTA — 3 angles per source, Dre UI push)
- **Total: 11 posts/day across 4 active channels (FB × 7, IG × 1, Pin × 3)**

**DEFERRED channels (per Andre 2026-06-25, Phase 2.5 DECISION):**
- **TikTok + YouTube Shorts** — DEFERRED until after Jul 7 PCAC recap window. Phase 2.5 video pipeline (matrix MCP text-to-video / image-to-video + ffmpeg + Postiz video attachments) NOT built. Reassess once we have real hook-family bias + performance data from the 11/day cadence. Do not add video attachments to this engine without explicit Andre go.
- **LinkedIn** — DEFERRED until Company Page is confirmed. Repurpose-only — no native posts from this engine.

**Total posts/day across the 4-week launch window (Jul 8 - Aug 4):** ~150-280 posts. Within the source corpus adaptation budget (30 source assets × 4-9 derivatives each).

---

## Files (this implementation)

- `specs/content-engine-spec.md` — this doc
- `scripts/dop_compliance.py` — 8-item audit module
- `scripts/dop_engine.py` — daily generator + queue writer
- `scripts/dop_push.py` — queue-aware Postiz push
- `queue/` — generated drafts + pin queue

---

## Authority

This engine executes within Decision 1 scope (full authority delegation for assets at 80%+ voice + compliance fit). REVIEW-labeled drafts escalate to Dre. Out-of-scope escalations (Swiss Chems, gray-market, dosing protocols, anything cross-team) escalate to Dre for explicit approval.

---

*Last updated: 2026-06-25 17:10 CT — v0.2 volume math section added (11 posts/day). DEFERRED channels section added (TikTok + YouTube Shorts, LinkedIn). Phase 2.5 video pipeline explicitly parked until post-Jul 7 reassessment.*