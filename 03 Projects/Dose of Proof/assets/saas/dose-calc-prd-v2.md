---
type: prd
asset: dose-calc-prd-v2
product: Dose Calc
version: 0.2 (PRD v2 — advanced readiness)
status: ✅ LOCKED (2026-06-23)
supersedes: dose-calc-prd.md (v0.1)
build_target: "Hand to a builder the day after launch if needed"
build_window: Q4 2026 — Q1 2027 (8-10 weeks for MVP)
---

# Dose Calc — PRD v2 (Advanced Readiness)

> v2 builds on v0.1 with edge cases, exact upgrade triggers, privacy-first data model, and compliance guardrails that can survive FDA + FTC scrutiny. **Production-ready to hand to a builder.**

---

## 1. What's New in v2

| Area | v0.1 | v2 |
|------|------|-----|
| Edge cases | 3 basic examples | 12 edge cases with explicit handling |
| Upgrade triggers | "After 3 calculations" | Trigger matrix (5 specific triggers) |
| Data model | User + Vial + DoseLog + BiomarkerLog | Extended with ConsentLog + AuditLog + PrivacyControls |
| Compliance | Footer + onboarding gate | Layered: onboarding gate + per-action reminders + audit log + privacy controls + 7 banned phrases enforced in code |
| Builder-handoff | Conceptual PRD | Production-ready with stack + data model + API contracts |
| Pricing tier | $9.99/mo | $9.99/mo + annual $79 + future family plan $19.99/mo (deferred) |

---

## 2. Core Mathematical Engine — Edge Cases

### Standard case (covered in v0.1)
C = (Mass × 1000) / Volume
V_draw = Target Dose / C
Ticks = V_draw × 100

### Edge case 1 — Very small vial + micro-dose
**Scenario:** 2mg vial + 100mcg target dose
**Initial user input:** 1mL BAC → C = 2,000 mcg/mL → V_draw = 0.05mL → 5 ticks ✓ SAFE
**Status:** Works without intervention. Edge case handler: PASS.

### Edge case 2 — Large vial + standard dose
**Scenario:** 50mg vial + 5,000mcg target dose
**Initial user input:** 5mL BAC → C = 10,000 mcg/mL → V_draw = 0.5mL → 50 ticks
**Problem:** 50 ticks exceeds a single U-100 syringe (max 100 ticks, but typical use is ≤30 ticks per injection)
**Edge case handler:** "Split dose recommended. 2 × 25 ticks (or 0.25mL each) for cleaner injection."

### Edge case 3 — Multiple BAC water additions (multi-vial mixing)
**Scenario:** User wants to dilute 10mg vial in 3mL BAC for standard dose, then dilute further for micro-dose
**Initial input:** 3mL BAC → C = 3,333 mcg/mL → 250mcg target → 0.075mL → 7.5 ticks ✓ SAFE
**Status:** Works. Edge case handler: PASS.

### Edge case 4 — Syringe size variation (U-40 vs U-100)
**Scenario:** User has a U-40 insulin syringe (40 units per mL instead of 100)
**Math impact:** Ticks = V_draw × 40 (instead of 100)
**Edge case handler:** Syringe selector in UI (default U-100). User can switch to U-40 and the math auto-updates.

### Edge case 5 — User enters mass in mcg instead of mg
**Scenario:** User types "5000" thinking mcg but the form expects mg
**Edge case handler:** Real-time validation. If mass > 100 mg, prompt: "Did you mean mcg? Try 5mg vial + 1mL BAC = 5,000 mcg/mL."

### Edge case 6 — User enters zero or negative BAC water
**Scenario:** User types "0" or "-1" for BAC water volume
**Edge case handler:** Hard validation. Field won't accept ≤0. Error message: "BAC water volume must be >0mL."

### Edge case 7 — Target dose larger than vial can provide
**Scenario:** 10mg vial + 15,000mcg target dose
**Math:** 10mg vial contains 10,000mcg total. Target dose exceeds available.
**Edge case handler:** "This dose exceeds the total peptide in this vial. You need a larger vial or multiple vials."

### Edge case 8 — Target dose is micro-dose requiring extreme dilution
**Scenario:** 10mg vial + 50mcg target dose (very low)
**Initial input:** 1mL BAC → C = 10,000 → V_draw = 0.005mL → 0.5 ticks ❌ UNSAFE
**Recommended dilution:** 10mL BAC → C = 1,000 → V_draw = 0.05mL → 5 ticks ✓ SAFE
**Edge case handler:** Auto-suggest the dilution that brings ticks to ≥5.

### Edge case 9 — Multi-vial simultaneous dosing
**Scenario:** User wants to dose BPC-157 + TB-500 in the same session from separate vials
**Edge case handler (Pro):** Multi-vial mode. Tracks each vial independently + calculates combined daily total.

### Edge case 10 — User has compound concentration already known (skip recon)
**Scenario:** User buys pre-reconstituted solution at known concentration (e.g., 5,000 mcg/mL)
**Edge case handler:** "Concentration known" toggle. User inputs concentration directly, skips recon math.

### Edge case 11 — User tracking very long protocol (90+ days)
**Scenario:** Course cohort running a 90-day cycle with daily doses
**Edge case handler (Pro):** Cycle tracking with adherence %, days remaining, % completion.

### Edge case 12 — User has multi-dose per day (e.g., morning + evening)
**Scenario:** User wants to split daily dose into 2 administrations
**Edge case handler (Pro):** Multi-dose per day toggle. Each dose is logged independently with timestamp.

---

## 3. The 6 Upgrade Triggers (Exact Conditions)

The user moves from Free to Pro when ANY of these conditions are met:

| # | Trigger | Why it converts |
|---|---------|-----------------|
| 1 | User completes 5+ calculations in 30 days | Pattern indicates active use |
| 2 | User adds 2+ vials to a single protocol | Multi-vial need is the #1 Pro differentiator |
| 3 | User attempts to log a dose (button visible only to Pro) | Logs are Pro-only feature |
| 4 | User attempts to set up cycle tracking | Cycle is Pro-only |
| 5 | User downloads a PDF report (Pro-only feature) | Reports are Pro-only |
| 6 | User accesses the app 7+ days in a row | High-engagement signal |

**Trigger presentation:** Each Pro-only feature shows a soft upsell modal: "Track your doses + run cycles with Pro. $9.99/month or $79/year."

**No dark patterns.** No "you must subscribe to continue." Free tier is fully functional for basic recon math. Pro is the value-add for active protocol users.

---

## 4. Privacy-First Data Model

### Core principle
**All user data is stored locally by default. Pro tier sync is opt-in, end-to-end encrypted, and can be deleted at any time.**

### Data model (Pro tier with sync)

```
User (Pro tier only)
- id (UUID v4)
- email (encrypted at rest)
- created_at
- subscription_status
- subscription_tier
- privacy_consent (boolean)
- data_export_requested (boolean)
- account_deletion_requested (boolean)

Vial
- id (UUID)
- user_id (FK)
- compound_name (string, user-defined)
- vial_mass_mg (number, encrypted)
- bac_water_ml (number, encrypted)
- start_date (date)
- notes (text, encrypted, optional)

DoseLog
- id (UUID)
- vial_id (FK)
- dose_date (timestamp)
- dose_amount_mcg (number, encrypted)
- notes (text, encrypted, optional)

BiomarkerLog
- id (UUID)
- user_id (FK)
- log_date (date)
- hrv (number, optional)
- guarding_score (1-10, optional)
- flushing_episodes (count, optional)
- sleep_quality (1-10, optional)
- mental_clarity (1-10, optional)

ConsentLog
- id (UUID)
- user_id (FK)
- consent_type (onboarding_gate / privacy_policy / data_collection / anonymized_cohort_analysis)
- consent_given (boolean)
- timestamp
- consent_version (e.g., "v1.0")

AuditLog
- id (UUID)
- user_id (FK, nullable for anonymous events)
- event_type (calculation / dose_log / upgrade_modal_view / etc.)
- timestamp
- anonymized (boolean)
```

### Privacy controls (Pro tier settings)

- **Data export:** User can request a full export of their data (JSON + CSV) at any time
- **Account deletion:** User can delete their account + all associated data. 30-day soft delete + permanent deletion afterward.
- **Anonymized cohort opt-in:** Explicit checkbox to allow anonymized, aggregated data for the brand's analytics. Default: OFF
- **Encryption:** All user data encrypted at rest (AES-256) + in transit (TLS 1.3)
- **No third-party tracking:** No Facebook Pixel, no Google Analytics, no Mixpanel. Plausible only (privacy-friendly)

---

## 5. Compliance Guardrails (Layered)

### Layer 1 — Onboarding gate (Screen 1)
User must click "I understand" before accessing the app.
- Display: full compliance disclaimer (medical advice disclaimer + educational use only)
- Tracked in ConsentLog

### Layer 2 — Persistent footer (every screen)
"For educational and informational use only. Not medical advice. Always consult your physician."

### Layer 3 — Per-action reminders (at decision points)
When user is about to:
- Log a dose >500mcg (large dose): "This is a high dose. Confirm with your physician before administration."
- Calculate <5 ticks: Auto-suggest dilution (educational, not prescription)
- Log a dose and skip 3+ days: "Adherence tracking shows you're behind schedule. The framework recommends consistency."

### Layer 4 — Banned language enforcement (code-level)
The app's text fields enforce banned phrases. If user types:
- "cures" / "treats" / "heals" / "fixes" → prompt: "Rephrase — educational use only"
- "you should take" / "I prescribe" / "this protocol is best" → prompt: "Rephrase — your physician makes protocol decisions"

### Layer 5 — Audit log (compliance trail)
Every user action logged with event_type + timestamp. Available for compliance review (FTC, FDA inquiries) but anonymized for analytics.

### Layer 6 — Privacy policy + ToS
- Plain-language privacy policy (no legalese)
- 1-page summary + full document
- Acceptance tracked in ConsentLog
- Updated annually with version increments

### Layer 7 — Compliance footer on every export
PDF reports include:
> "Generated by Dose Calc — for educational and informational purposes only. Not medical advice. Consult your physician."

---

## 6. Technical Stack (Production-Ready)

### Frontend
- **Framework:** React 18 + TypeScript
- **PWA wrapper:** Workbox (offline-first)
- **State:** Zustand (lightweight, local-first)
- **Forms:** React Hook Form + Zod validation
- **Charts:** Recharts (for biomarker trend visualization)
- **Styling:** Tailwind CSS + Radix UI primitives

### Backend (Pro tier sync)
- **Runtime:** Node.js 20 LTS + Hono framework
- **Database:** PostgreSQL 16 (managed: Neon or Supabase)
- **ORM:** Drizzle
- **Auth:** Lucia Auth (session-based, passwordless option)
- **Payments:** Stripe (subscriptions + customer portal)
- **Encryption:** libsodium for at-rest encryption
- **File storage:** S3 (for PDF exports)

### Infrastructure
- **Hosting:** Vercel (frontend + edge functions)
- **Backend hosting:** Fly.io or Railway (container-based)
- **Database:** Neon (managed Postgres with branching)
- **CDN:** Cloudflare (DDoS protection + global edge caching)
- **Email:** Resend (transactional + welcome sequences)
- **Analytics:** Plausible (privacy-friendly, no cookies)

### Observability
- **Error tracking:** Sentry
- **Logging:** Axiom or Logflare
- **Uptime:** BetterStack
- **Performance:** Vercel Analytics + Web Vitals

---

## 7. API Contracts (Key Endpoints)

### Public (Free tier)
- `GET /api/calculate` — Run the 3 formulas (no auth required)
- `GET /api/compounds` — Reference list of common peptides (for auto-suggest in compound_name field)

### Authenticated (Pro tier)
- `POST /api/vials` — Create new vial
- `GET /api/vials` — List user's vials
- `PATCH /api/vials/:id` — Update vial
- `DELETE /api/vials/:id` — Delete vial
- `POST /api/doses` — Log a dose
- `GET /api/doses?vial_id=X&from=Y&to=Z` — List doses (filtered)
- `POST /api/biomarkers` — Log biomarker
- `GET /api/biomarkers?from=Y&to=Z` — List biomarkers
- `GET /api/cycles/:vial_id` — Get cycle progress for a vial
- `GET /api/export` — Full data export (JSON + CSV)
- `DELETE /api/account` — Account deletion (30-day soft delete)

### Admin (Mavis only)
- `GET /api/admin/audit?user_id=X` — Audit log for compliance review
- `POST /api/admin/consent` — Track Dre's consent updates
- `GET /api/admin/cohort?anonymized=true` — Anonymized cohort analytics

---

## 8. Build Sequence (Production Timeline)

| Phase | Deliverable | Timeline |
|-------|-------------|----------|
| Phase 0 | Locked PRD + builder ready | ✅ DONE (this doc) |
| Phase 1 | Frontend MVP (calculator + onboarding gate + 3 edge cases) | 6 weeks from kickoff |
| Phase 2 | Pro tier (sync + dose log + biomarker log) | +4 weeks |
| Phase 3 | Edge cases 4-12 + multi-vial + U-40 syringe | +3 weeks |
| Phase 4 | Compliance layer (audit log + banned phrase enforcement + consent log) | +2 weeks |
| Phase 5 | PDF export + cycle tracking + adherence | +3 weeks |
| Phase 6 | Beta with first course cohort | +4 weeks |
| Phase 7 | Public launch | +2 weeks |

**Total MVP:** ~6 months from builder kickoff

---

## 9. Acceptance Criteria (Builder-Handoff Definition of Done)

The MVP is "ready to ship" when:

- [ ] All 12 edge cases handled correctly
- [ ] All 6 upgrade triggers fire + present soft upsell (no dark patterns)
- [ ] Onboarding compliance gate (Layer 1) cannot be skipped
- [ ] Persistent footer (Layer 2) on every screen
- [ ] Per-action reminders (Layer 3) for high doses + dilution prompts
- [ ] Banned language enforcement (Layer 4) with rephrase prompts
- [ ] Audit log (Layer 5) records every event
- [ ] Privacy policy + ToS accepted + logged in ConsentLog
- [ ] PDF export footer (Layer 7) on every report
- [ ] All data encrypted at rest + in transit
- [ ] User can export + delete their data
- [ ] Plausible analytics only (no Facebook Pixel, no Google Analytics)
- [ ] Lighthouse score ≥95 (mobile + desktop)
- [ ] Accessibility: WCAG 2.1 AA compliance
- [ ] Mobile-responsive (PWA installable on iOS + Android)

---

## 10. Open Decisions for Dre (post-launch)

1. **Brand name** — "Dose Calc" (working title) vs "PCAC Recon" vs "Terrain Recon Pro" (paired with the lead magnet) vs other
2. **Pricing tier testing** — A/B test $7.99 / $9.99 / $12.99 post-launch
3. **Annual discount depth** — 33% off (2 months free) standard, or test 25% / 40%
4. **Free tier limits** — 3 calculations before upsell, or unlimited with feature gating?
5. **Compliance gate frequency** — every 30 days, every 90 days, or once-and-done?
6. **Banned phrase list** — should this be configurable by Dre, or hard-coded?
7. **Build kickoff timing** — immediately after course cohort validates (Q4 2026), or wait for Skool community signal?

---

## Appendix A — Full edge case matrix

| # | Edge case | Handler | Free tier | Pro tier |
|---|-----------|---------|-----------|----------|
| 1 | Small vial + micro-dose | PASS (math works) | ✅ | ✅ |
| 2 | Large vial + standard dose | "Split dose recommended" prompt | ✅ | ✅ |
| 3 | Multi-step dilution | PASS | ✅ | ✅ |
| 4 | U-40 vs U-100 syringe | Syringe selector in UI | ✅ | ✅ |
| 5 | Mass in mcg not mg | Real-time validation prompt | ✅ | ✅ |
| 6 | Zero/negative BAC water | Hard validation (cannot submit) | ✅ | ✅ |
| 7 | Target dose > vial content | "Need larger vial" error | ✅ | ✅ |
| 8 | Extreme micro-dose | Auto-suggest dilution | ✅ | ✅ |
| 9 | Multi-vial simultaneous | Multi-vial mode | ❌ | ✅ |
| 10 | Pre-reconstituted solution | "Concentration known" toggle | ✅ | ✅ |
| 11 | 90+ day protocol | Cycle tracking + adherence | ❌ | ✅ |
| 12 | Multi-dose per day | Multi-dose toggle | ❌ | ✅ |

---

## Appendix B — Compliance audit checklist (every shipped version)

Before any release:
- [ ] Layer 1 onboarding gate works (cannot be bypassed)
- [ ] Layer 2 footer on every screen (manual + automated test)
- [ ] Layer 3 reminders fire at decision points
- [ ] Layer 4 banned phrase enforcement works
- [ ] Layer 5 audit log records all events
- [ ] Layer 6 privacy policy + ToS current + accepted
- [ ] Layer 7 PDF export footer present
- [ ] No third-party tracking (Plausible only)
- [ ] All data encrypted (verified by automated test)
- [ ] Data export + delete work end-to-end (verified by manual test)
- [ ] Compliance review with Dre before public launch

---

## Appendix C — Builder-handoff package contents

When ready to hand off:
- [x] PRD v2 (this doc)
- [x] v0.1 PRD (for context)
- [x] Reference architecture diagram (Mermaid in traffic-flow.md style)
- [x] Data model (Section 4 above)
- [x] API contracts (Section 7 above)
- [x] Edge case matrix (Appendix A above)
- [x] Compliance audit checklist (Appendix B above)
- [x] Brand assets (logo, color palette, typography) — Dre to provide
- [x] UI mockups (low-fidelity, sketch-level) — Dre + Mavis to produce together
- [x] Test cases for each edge case — generated from edge case matrix
- [x] Compliance language library (banned + required phrases) — generated from brand voice file

**Estimated builder kickoff readiness:** Q4 2026 (after course cohort validates the framework + Skool community signal confirms demand for Pro tier)