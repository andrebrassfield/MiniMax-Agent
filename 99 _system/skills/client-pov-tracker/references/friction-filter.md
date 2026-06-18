# Friction Filter (3-tier taxonomy) — client-pov-tracker

The 3-tier taxonomy for categorizing Friction Signals. The
load-bearing classification system. Per the
`local-competitor-auditor` skill's Friction Filter, which
produces the signals this skill ingests.

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
| **No service-area map** | Customer has to call to confirm coverage | Add a map (Google Maps embed is fine) |
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

## Categorization procedure

For each unique friction signal across the local-audit
briefs:

1. Match against the Tier 1 / 2 / 3 table above
2. Assign the tier
3. If the signal is novel (not in the taxonomy), flag in
   Section 7 of the roadmap and ask the operator to confirm
   the tier

A signal can be in multiple tiers (e.g., "no online pricing"
could be Tier 1 if it's a trades business with 80% of leads
asking for quotes, Tier 2 if it's a less price-sensitive
niche). Use operator judgment.

## What this taxonomy is NOT

- **Not a complete list.** Novel frictions exist; the
  taxonomy covers the common 80%. Operator judgment for the
  long tail.
- **Not severity-scored per signal.** The taxonomy is
  per-signal; the per-competitor severity is computed in
  `local-competitor-auditor` (1-5 based on how many Tier 1
  + 2 are PRESENT).
- **Not the Dre Builds 4-week Blueprint.** The Blueprint
  phases are in `references/blueprint-phases.md`. The
  taxonomy is the input; the Blueprint is the response.

## Cross-reference

- `local-competitor-auditor` — the upstream skill that
  produces the per-competitor friction signals + severity
  scores. The taxonomy here is the categorization system
  applied AFTER the signals are extracted.
- `references/agentic-standard.md` — the 4 criteria the
  install must satisfy
- `references/blueprint-phases.md` — the 4-week install
  phases that address the friction
- `references/roi-math.md` — the whitepaper §4 math that
  prices the friction in dollars
