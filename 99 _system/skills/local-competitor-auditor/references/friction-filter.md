# Friction Filter (3-tier taxonomy) — local-competitor-auditor

The 3-tier taxonomy. The load-bearing classification system
for Friction Signals. Per-competitor PRESENT/ABSENT
checkboxes populate the brief's friction signals list. The
same taxonomy feeds `client-pov-tracker` (per-client POV).

## Tier 1 — High-leverage friction (Pillar 2 anchor)

Phone-only after-hours, no 24/7 web chat, "Call us for a
quote" only, no instant-booking calendar. These are the
frictions a voice-AI / web-chat / instant-booking install
directly closes.

| Signal | What it leaks | Install that closes it |
|---|---|---|
| **Phone-only after-hours** | Missed calls on weekends, evenings, holidays | Voice AI dispatcher (Vapi, Synthflow) + 24/7 web chat |
| **No 24/7 web chat** | After-hours visitors see contact form and leave | 24/7 web chat widget + voice AI |
| **"Call us for a quote" only** | Lead gated by phone call business may not answer | Voice AI answers, captures intent, books job |
| **No instant-booking calendar** | Customer calls, leaves message, waits for callback | Calendly / ServiceTitan / Jobber / Housecall Pro embed |

## Tier 2 — Medium-leverage friction

No service-area map, no online pricing, no reviews linked,
no FAQ/process page, site is dated. These are the frictions
that erode trust at first contact.

| Signal | What it costs | Install that addresses it |
|---|---|---|
| **No service-area map** | Customer has to call to confirm coverage | Add a map (Google Maps embed) |
| **No online pricing** | Customer has to call to get any cost info | Add "starting at $X" rate sheet |
| **No reviews linked / social proof** | Business doesn't actively surface proof | Add Google reviews badge, Yelp link, testimonials |
| **No FAQ / process page** | Customer has to call to learn anything | Add "How it works" / "Our process" page |
| **Site is dated (last update > 2 years)** | Business isn't investing in web presence | Refresh site (Phase 4 Outcome Loop content) |

## Tier 3 — Low-leverage friction (noted, not prioritized)

No blog/content/SEO, no team page, no video/photo of
completed work. Lower priority — some local businesses
intentionally don't have these.

| Signal | What it costs | Notes |
|---|---|---|
| **No blog / content / SEO play** | Missing free organic traffic | Phase 4 content may address |
| **No team page / About us** | Business is faceless | Lower priority |
| **No video / photo of completed work** | Homepage is text-only | Lower priority |

## How to apply the filter

For each competitor's homepage, scan the snapshot's text
for the friction signals in the filter list. Mark each
signal as PRESENT (leak) or ABSENT (no leak). Tally
per-competitor.

**Do NOT scroll.** The friction signals live on the
homepage. If the business has friction on a sub-page
(e.g., the booking flow is broken on /book but the
homepage hides it), note in "Open questions for the
operator" but don't deep-crawl.

**One homepage per competitor.** Per hard constraint #6,
do NOT click into sub-pages.

## What this taxonomy is NOT

- **Not a complete list.** Novel frictions exist; the
  taxonomy covers the common 80%. Operator judgment for
  the long tail.
- **Not severity-scored per signal.** The taxonomy is
  per-signal; the per-competitor severity is computed
  separately (1-5 based on how many Tier 1 + 2 are
  PRESENT). See `severity-scoring.md`.
- **Not the Dre Builds 4-week Blueprint.** The Blueprint
  phases are in the client-pov-tracker's
  `blueprint-phases.md`. The taxonomy is the input; the
  Blueprint is the response.
- **Not a feature checklist.** The signals describe user
  friction, not feature presence. A chat widget is not
  present just because it's in the footer; it's present
  when it's visible and functional on the homepage.

## Cross-reference

- `references/severity-scoring.md` — per-competitor 1-5
  scoring rules
- `references/procedure.md` — the 9-step procedure with
  bash
- `references/output-format.md` — the markdown brief
  format
- `client-pov-tracker` — the downstream skill that
  categorizes the signals per per-client context
