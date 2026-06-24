---
type: prd
asset: dose-calc-prd
product: Dose Calc
version: 0.1 (PRD — no code yet)
status: ✅ LOCKED for spec (2026-06-23)
author: Mavis (with Dre's voice + input)
target_build_window: Q4 2026 - Q1 2027
target_launch: Q1 2027
architecture_decision: "Two distinct tools (health-tracker free CLI + Dose Calc paid SaaS) — locked 2026-06-23 20:04 CT"
supersedes: Dose Calc concept in business-model-v1.md Section 3 Stream C
---

# Dose Calc — Product Requirements Document (PRD v0.1)

> The paid SaaS for the Dose of Proof brand. Peptide reconstitution math + dose history + multi-vial tracking. Compliance-locked at the structural level. **No code written yet** — this is the spec that a future build will follow.

## 1. Product Overview

### What it is
Dose Calc is a web-first Progressive Web App (PWA) that solves the volumetric dilution math for peptide reconstitution. It runs the three core formulas (C, V_draw, Ticks) + tracks multi-vial protocols + logs dose history + syncs across devices.

### What it isn't
- NOT a medical device
- NOT a prescribing tool
- NOT a sourcing aggregator
- NOT a community platform

### Why it exists
The recon math is unforgiving. A 2.5-tick dose on a U-100 syringe is gambling. Most existing calculators handle only single vials. None integrate with the daily tracking discipline the PCAC framework requires. Dose Calc solves the math, removes the gambling, and integrates with the brand's biomarker-tracking workflow.

### Differentiators vs existing tools (Peptide Calculator, PepCalc)
| Feature | Existing tools | Dose Calc |
|---------|----------------|-----------|
| Single-vial recon math | ✅ | ✅ |
| Multi-vial tracking | ❌ | ✅ |
| BAC water volume selector (force safer tick counts) | ❌ | ✅ |
| Dose history logging | ❌ | ✅ |
| Multi-device sync | Partial | ✅ |
| Biomarker correlation (HRV/guarding scores vs dose) | ❌ | ✅ (manual entry + chart) |
| Compliance copy throughout ("educational use only") | Partial | ✅ (structural) |
| Brand-aligned dark theme | ❌ | ✅ |

---

## 2. The Mathematical Engine

### The 3 core formulas

**Formula 1 — Concentration:**
```
C = (Mass × 1000) / Volume

Where:
- C = concentration in mcg/mL
- Mass = vial mass in mg
- Volume = BAC water volume in mL
```

**Formula 2 — Required Draw Volume:**
```
V_draw = Target Dose / C

Where:
- V_draw = required draw volume in mL
- Target Dose = desired dose in mcg
- C = concentration from Formula 1 in mcg/mL
```

**Formula 3 — Syringe Ticks:**
```
Ticks = V_draw × 100

Where:
- Ticks = syringe units on a U-100 insulin syringe
- V_draw = from Formula 2 in mL
```

### Worked example (Dre's "the math that almost killed me")

Input:
- Vial mass: 10 mg
- BAC water volume: 1 mL
- Target dose: 250 mcg

Output:
- C = (10 × 1000) / 1 = 10,000 mcg/mL
- V_draw = 250 / 10,000 = 0.025 mL
- Ticks = 0.025 × 100 = 2.5 ticks

**The dangerous output:** 2.5 ticks on a U-100 syringe cannot be measured by eye.

### The Dose Calc fix (BAC water volume selector)

When the math produces a tick count below a safety threshold (default: 5 ticks), Dose Calc prompts the user to increase BAC water volume and re-runs the math.

Re-input (after Dose Calc suggestion: "Try 2mL BAC water"):
- Vial mass: 10 mg
- BAC water volume: 2 mL
- Target dose: 250 mcg

Re-output:
- C = (10 × 1000) / 2 = 5,000 mcg/mL
- V_draw = 250 / 5,000 = 0.05 mL
- Ticks = 0.05 × 100 = 5 ticks

**The safer output:** 5 ticks is measurable. The math doesn't change; the dilution does.

### Advanced calculations (Pro tier only)

**Formula 4 — Multi-vial dosing schedule:**
```
Daily dose = Sum across active vials of (V_draw × Concentration)

Where each vial's parameters are independently tracked.
```

**Formula 5 — Cost per dose:**
```
Cost per dose = (Vial cost / Total doses in vial)

Where Total doses = (Mass × 1000) / Target dose
```

**Formula 6 — Cycle tracking:**
```
Days remaining in cycle = (Total doses - Doses administered) / Doses per day
```

---

## 3. Freemium Tier Structure

### Free Tier (no account required)

**What's included:**
- Basic single-vial reconstitution calculator
- The 3 core formulas (C, V_draw, Ticks)
- BAC water volume selector
- Safety threshold prompts

**What's NOT included:**
- Multi-vial tracking
- Dose history logging
- Multi-device sync
- PDF progress reports
- Cycle tracking
- Adherence streaks

**Goal:** Top-of-funnel for the brand. Solves the basic math, builds trust, drives Substack opt-in via the "Want multi-vial tracking? Upgrade to Pro" prompt after 3 calculations.

### Pro Tier ($9.99/month or $79/year)

**What's included:**
- Everything in Free, PLUS:
- Multi-vial tracking (compare protocols across compounds)
- Dose history log (with calendar view)
- Multi-device sync (web PWA → iOS/Android native later)
- Adherence streaks + gamification
- PDF progress reports (export for doctor visit)
- Cycle tracking (days remaining, % completion)
- Biomarker correlation chart (manual entry of HRV/guarding scores, overlay with dose log)

**Goal:** Recurring revenue + retention. The "I want my data tracked" tier for active protocol users.

### Annual discount: 33% off (2 months free)
- $9.99/mo = $119.88/yr
- $79/yr saves $40.88
- Annual lock-in improves LTV + reduces churn

### Future: Enterprise Tier (deferred)
- White-label licensing for telehealth platforms (Marek, Lifeforce)
- $5K-20K/year per partner
- See `business-model-v1.md` Stream M

---

## 4. UI Flow

### Screen 1 — Calculator (the home screen)

```
┌──────────────────────────────────────┐
│   DOSE CALC                          │
│   [Math] [History] [Settings]        │
├──────────────────────────────────────┤
│                                      │
│   Vial mass                          │
│   ┌──────────────┐  mg               │
│   │ 10           │                   │
│   └──────────────┘                   │
│                                      │
│   BAC water volume                   │
│   ┌──────────────┐  mL               │
│   │ 2            │                   │
│   └──────────────┘  [Suggest: 2mL]    │
│                                      │
│   Target dose                        │
│   ┌──────────────┐  mcg              │
│   │ 250          │                   │
│   └──────────────┘                   │
│                                      │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━        │
│                                      │
│   Concentration                      │
│   5,000 mcg/mL                       │
│                                      │
│   Required draw                      │
│   0.05 mL                            │
│                                      │
│   Syringe ticks (U-100)              │
│   5 ticks ✓ SAFE                     │
│                                      │
│   [Add to history] [Reset] [Pro:    │
│    Multi-vial]                       │
│                                      │
├──────────────────────────────────────┤
│  Compliance footer:                  │
│  "For educational use only. Not     │
│   medical advice. Consult your       │
│   physician."                        │
└──────────────────────────────────────┘
```

### Screen 2 — Multi-vial tracking (Pro)

```
┌──────────────────────────────────────┐
│   DOSE CALC · MY PROTOCOL            │
├──────────────────────────────────────┤
│   Active vials                       │
│                                      │
│   ┌─────────────────────────────┐    │
│   │ BPC-157                     │    │
│   │ 10mg vial · 2mL BAC         │    │
│   │ Concentration: 5,000 mcg/mL│    │
│   │ Last dose: 250 mcg · Day 12  │    │
│   │ Doses remaining: 36         │    │
│   │ [Log dose] [Edit vial]      │    │
│   └─────────────────────────────┘    │
│                                      │
│   ┌─────────────────────────────┐    │
│   │ TB-500                      │    │
│   │ 5mg vial · 2mL BAC          │    │
│   │ ...                         │    │
│   └─────────────────────────────┘    │
│                                      │
│   [+ Add new vial]                   │
└──────────────────────────────────────┘
```

### Screen 3 — Dose history (Pro)

```
┌──────────────────────────────────────┐
│   DOSE CALC · HISTORY                 │
├──────────────────────────────────────┤
│   Last 30 days                        │
│                                      │
│   Calendar view (heatmap)            │
│   ████░░██░░██████░░░░██░░███████    │
│                                      │
│   Date | Vial | Dose | Notes          │
│   ──────────────────────────         │
│   Jun 23 | BPC-157 | 250mcg | Day 12  │
│   Jun 22 | BPC-157 | 250mcg | Day 11  │
│   Jun 21 | BPC-157 | 250mcg | Day 10  │
│   ...                                 │
│                                      │
│   [Export PDF] [Share with doctor]   │
└──────────────────────────────────────┘
```

### Screen 4 — Compliance gate (first-time user)

```
┌──────────────────────────────────────┐
│   BEFORE WE START                    │
├──────────────────────────────────────┤
│                                      │
│   Dose Calc is for EDUCATIONAL and   │
│   INFORMATIONAL use only.            │
│                                      │
│   It is NOT medical advice.           │
│   It does NOT prescribe.              │
│   It does NOT diagnose.              │
│                                      │
│   Always consult your physician      │
│   before starting, changing, or       │
│   stopping any protocol.             │
│                                      │
│   The math is correct. The protocol  │
│   decisions are yours and your       │
│   doctor's.                           │
│                                      │
│   [I understand — Continue]          │
│   [Learn more about the framework]   │
└──────────────────────────────────────┘
```

**This screen is required on first launch.** Cannot be skipped. Stored in localStorage to prevent re-prompting (re-prompted every 30 days for active users).

---

## 5. Compliance Guardrails (structural)

### 5.1 — In-app copy

Every screen has a compliance footer:
> "For educational and informational use only. Not medical advice. Always consult your physician before starting, changing, or stopping any protocol."

### 5.2 — Onboarding compliance gate (Screen 4)

Required on first launch. Cannot be skipped. The user must affirmatively click "I understand."

### 5.3 — Banned language (enforced in code + copy review)

The app's text content is reviewed against the banned phrases list:
- cure / treat / heal / fix
- prescribe / diagnose / recommend (for protocols)
- "you should take" (always "your doctor may consider")
- sourcing language (no peptide supplier names)
- fake urgency / fake scarcity

If the banned language is detected in any user-generated content (notes, dose history entries), the app prompts: "Rephrase this — educational use only."

### 5.4 — FDA compliance posture (Objective Intent Doctrine)

The app does NOT:
- Sell compounds
- Recommend suppliers
- Cross-sell to research-chem sites
- Host user-generated reviews of suppliers

The app DOES:
- Run the math
- Track the user's data
- Integrate with the Substack (educational content)
- Direct users to "consult your physician" for protocol decisions

This structural posture means Dose Calc operates squarely on the educational side of the Objective Intent Doctrine line.

### 5.5 — Data privacy

- All user data is stored locally (localStorage) by default
- Pro tier sync uses end-to-end encrypted cloud storage
- No data sold to third parties
- No data shared with telehealth partners without explicit user opt-in
- Compliance with HIPAA is OUT OF SCOPE for v1 (deferred to v2 if needed for telehealth partnership)

### 5.6 — Age gate

Required on first launch: "Are you 18 or older?" If no, app closes. This protects against marketing the tool to minors.

---

## 6. User Personas

### Persona 1 — The PCAC user (primary)

- 25-45 years old
- Has been to multiple specialists for chronic symptoms
- Tracks some biomarkers (HRV at minimum)
- Knows the recon math exists, finds it intimidating
- Wants a tool that "just runs the math"
- Will pay $9.99/mo if it saves time + reduces errors
- Likely to come from the Substack list or the course

### Persona 2 — The biohacker (secondary)

- 30-50 years old
- Already running peptide protocols
- Uses competitor tools (Peptide Calculator) but wants something better
- Will upgrade to Pro within 2 weeks of starting
- Likely to refer friends (the refer-a-friend feature is deferred but planned)

### Persona 3 — The clinician (deferred)

- Functional medicine doctor or upper cervical specialist
- Would use the white-label version to track patient protocols
- B2B sales motion (not in v1 scope)
- Future: enterprise tier with patient management

---

## 7. Technical Architecture (proposed — no code yet)

### Stack
- **Frontend:** React (web) + PWA wrapper for mobile
- **Backend:** Node.js + PostgreSQL (Pro tier sync)
- **Hosting:** Vercel (web) + AWS S3 (PDF exports)
- **Auth:** Email + password (no social login in v1)
- **Payments:** Stripe (monthly + annual)
- **Analytics:** Plausible (privacy-friendly, no cookies)

### Data model (Pro tier)

```
User
- id
- email
- password_hash
- created_at
- subscription_status
- subscription_tier (free | pro)
- subscription_renews_at

Vial
- id
- user_id
- compound_name (string, user-defined)
- vial_mass_mg (number)
- bac_water_ml (number)
- start_date
- notes

DoseLog
- id
- vial_id
- dose_date
- dose_amount_mcg
- notes

BiomarkerLog (manual entry)
- id
- user_id
- log_date
- hrv (number, optional)
- guarding_score (1-10, optional)
- flushing_episodes (count, optional)
- sleep_quality (1-10, optional)
- mental_clarity (1-10, optional)
```

---

## 8. Success Metrics

| KPI | Target (90 days post-launch) |
|-----|------------------------------|
| Free tier signups | 5,000 |
| Free → Pro conversion | 5% (250 paid) |
| Monthly Pro churn | <10% |
| Pro subscribers (steady state) | 250 |
| Monthly recurring revenue | $2,500 |
| Annual subscribers | 50 (at $79) |
| Daily active users (Pro) | 30% of subscribers |

---

## 9. Build Sequence

| Phase | Deliverable | Timeline |
|-------|-------------|----------|
| Phase 1 | Web PWA MVP (calculator + compliance gate + free tier) | Q4 2026 (8-10 weeks) |
| Phase 2 | Pro tier (multi-vial + history + sync) | Q1 2027 (6 weeks) |
| Phase 3 | Native iOS/Android | Q2 2027 (8 weeks) |
| Phase 4 | Enterprise white-label | Q3 2027 (12 weeks) |

**Build doesn't start until:** Course cohort validates the framework + first Pro pre-orders from email list.

---

## 10. Out of Scope (v1)

- Prescription features
- Telehealth integration (deferred to v2)
- White-label for telehealth partners (deferred to v3)
- Native mobile apps (deferred)
- Multi-language support (English-only v1)
- Integration with Apple Health / Google Fit (deferred)
- HIPAA compliance (deferred)
- Clinical decision support (deferred — would change compliance posture)

---

## 11. Open Questions for Dre (post-launch)

1. **Brand name for the SaaS** — "Dose Calc" (working title) vs. "PCAC Recon" vs. other
2. **Pricing tier** — is $9.99/mo the right price, or test $7.99 / $12.99?
3. **Annual discount depth** — 33% off (2 months free) vs. 25% off vs. flat $79
4. **Free tier limits** — 3 calculations before upsell, or unlimited with feature gating?
5. **Compliance gate frequency** — every 30 days, every 90 days, or once-and-done?

---

## Appendix A — The math worked examples

### Example 1: Basic recon (BPC-157)
- Vial: 10mg
- BAC: 2mL
- Target: 250mcg
- C = 10,000/2 = 5,000 mcg/mL
- V_draw = 250/5,000 = 0.05mL
- Ticks = 0.05 × 100 = 5 ticks ✅ SAFE

### Example 2: Micro-dose with safety prompt
- Vial: 10mg
- BAC: 1mL (user initial input)
- Target: 250mcg
- C = 10,000/1 = 10,000 mcg/mL
- V_draw = 250/10,000 = 0.025mL
- Ticks = 0.025 × 100 = 2.5 ticks ❌ UNSAFE → prompt: "Try 2mL BAC water"

### Example 3: Larger vial (TB-500)
- Vial: 5mg
- BAC: 2mL
- Target: 500mcg (2x weekly)
- C = 5,000/2 = 2,500 mcg/mL
- V_draw = 500/2,500 = 0.2mL
- Ticks = 0.2 × 100 = 20 ticks (split dose) — note: 20 ticks > 10-tick syringe limit, would prompt split dose

### Example 4: Multi-vial daily total
- Vial 1 (BPC-157): 250mcg
- Vial 2 (TB-500): 500mcg
- Daily total: 750mcg across 2 vials
- Pro tier tracks both vials independently + sums the daily total