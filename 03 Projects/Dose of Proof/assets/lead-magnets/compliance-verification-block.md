---
title: 5 Biomarkers Lead Magnet — Compliance Verification Block
type: compliance-audit
asset_id: lm-5biomarkers-compliance-v1
status: DRAFT — pending Co-CEO final review
date: 2026-06-26
voice_locked: source/2026-06-23-brand-voice.md
compliance_locked: compliance/compliance-remediation-summary.md + v0.4-review-package.md §9.4.1 sign-off (B)
audited_against: scripts/dop_compliance.py (8-item audit) + brand voice rules
note: "This block references banned phrases by audit-script regex pattern code (e.g. [BP-001]) rather than spelling them out, to avoid false-positive matches from the automated audit when the verification block enumerates the banned phrase list. The actual list lives in scripts/dop_compliance.py BANNED_PHRASES — see that file for the authoritative regex patterns."
---

# Compliance Verification — 5 Biomarkers Lead Magnet (Full Package)

> **Audit purpose.** Every asset in the lead magnet package is reviewed against the 8-item compliance audit (`scripts/dop_compliance.py`) + brand voice rules + the clean compliance posture established in `compliance/compliance-remediation-summary.md`. This block is the audit trail.

> **Audit reference convention.** Banned phrases referenced by code: `[BP-001]` through `[BP-016]` per `scripts/dop_compliance.py` BANNED_PHRASES list. See that file for the regex patterns. This block does not enumerate banned phrases inline to avoid false-positive matches from the automated audit script that reads this very file.

---

## 8-item compliance audit — per-asset results

### Audit item 1 — Educational / curational framing (no prescriptive language)

**Rule:** No `[IP-001]` through `[IP-005]` patterns (prescriptive-dose markers per `dop_compliance.py`).

| Asset | Status | Notes |
|---|---|---|
| `5-biomarkers-guide.md` | ✅ PASS | All "tracking" language is observational. No prescribing. |
| `5-biomarkers-landing-page.md` | ✅ PASS | "Talk to your physician" framing only. |
| `5-biomarkers-visualization-spec.md` | ✅ PASS | Design language only; no clinical content. |
| `5-biomarkers-tracking-template.md` | ✅ PASS | "Talk to your physician" reminder in body. |
| `5-biomarkers-email-day0.md` | ✅ PASS | Explicit "what this isn't" section. |

### Audit item 2 — Single CTA (allowed host only)

**Rule:** Single CTA = doseofproof.substack.com. No banned hosts (buffer, vercel, shopify, swiss-vendor, etc.).

| Asset | Status | Notes |
|---|---|---|
| `5-biomarkers-guide.md` | ✅ PASS | Section 5 mentions Substack + "vetted directory of telehealth providers" (text only, no link to specific vendor) |
| `5-biomarkers-landing-page.md` | ✅ PASS | Single CTA = Substack opt-in form |
| `5-biomarkers-visualization-spec.md` | ✅ PASS | No CTAs (design spec only) |
| `5-biomarkers-tracking-template.md` | ✅ PASS | No external CTAs |
| `5-biomarkers-email-day0.md` | ✅ PASS | Substack + PDF download only |

### Audit item 3 — No banned vendors / sourcing (no `[BP-013]`, `[BP-014]`, `[BP-015]`, `[BP-016]`)

**Rule:** No banned-vendor references per `scripts/dop_compliance.py` BANNED_PHRASES list (research-vendor channels, swiss-vendor sourcing, unofficial chemical-sourcing channels, vendor research-use labeling).

| Asset | Status | Notes |
|---|---|---|
| All assets | ✅ PASS | Zero banned-vendor references. "We don't sell compounds and we don't facilitate sourcing" appears in landing page and email. |

### Audit item 4 — No efficacy claims (no `[BP-001]` through `[BP-012]`)

**Rule:** No efficacy-claim phrases per `scripts/dop_compliance.py` BANNED_PHRASES list (medical outcome promises, transformation language, etc.).

| Asset | Status | Notes |
|---|---|---|
| `5-biomarkers-guide.md` | ✅ PASS | Searched: zero banned-phrase matches. "Observational data from one case" framing throughout. |
| `5-biomarkers-landing-page.md` | ✅ PASS | "I won't promise outcomes. I can show you my data." |
| `5-biomarkers-visualization-spec.md` | ✅ PASS | Design spec language only. |
| `5-biomarkers-tracking-template.md` | ✅ PASS | Tracking template language only. |
| `5-biomarkers-email-day0.md` | ✅ PASS | "What this isn't" section explicitly disclaims efficacy. |

### Audit item 5 — Banned phrases (`[BP-001]` through `[BP-016]`)

**Rule:** Banned phrases from `scripts/dop_compliance.py` BANNED_PHRASES list (16 regex patterns).

All assets: ✅ PASS. Manual grep confirms zero banned-phrase matches across the package.

### Audit item 6 — Brand voice — stoic, not hype (≤3 exclamation marks per asset)

**Rule:** Brand voice is stoic. Excitement markers and exclamation marks >3 = flagged.

| Asset | Exclamation count | Status |
|---|---|---|
| `5-biomarkers-guide.md` | 0 | ✅ PASS |
| `5-biomarkers-landing-page.md` | 0 | ✅ PASS |
| `5-biomarkers-visualization-spec.md` | 0 | ✅ PASS |
| `5-biomarkers-tracking-template.md` | 0 | ✅ PASS |
| `5-biomarkers-email-day0.md` | 0 | ✅ PASS |

### Audit item 7 — PCAC framework framing

**Rule:** PCAC = "Proof-Centered Approach to Craniocervical + Autoimmune Chaos" — always framed as observational methodology, never as treatment.

| Asset | Status | Notes |
|---|---|---|
| `5-biomarkers-guide.md` | ✅ PASS | PCAC introduced as "a way of thinking" + observational methodology. "Show me the data before you change anything." |
| `5-biomarkers-landing-page.md` | ✅ PASS | PCAC mentioned as the framework context, no efficacy claim. |
| `5-biomarkers-email-day0.md` | ✅ PASS | PCAC introduction as "first step in the framework — observational data first." |

### Audit item 8 — FDA / regulatory claim framing

**Rule:** Any FDA-related claim must be framed via PCAC framework (observational) and not as adoption of FDA positioning.

All assets: ✅ PASS. FDA mentioned only in the context of the July 23 PCAC meeting ("what it means for the biohacking community") — observational, not adopting positioning.

---

## "My Body, Not Yours" framing check

The brand voice rule: every piece of content is first-person observational ("I did X to my body" not "you should do X").

| Asset | Check |
|---|---|
| `5-biomarkers-guide.md` | ✅ "I'm 30 years old" / "my own case" / "what improved for me" — first-person throughout |
| `5-biomarkers-landing-page.md` | ✅ "I spent 7 months in a hell no one could diagnose" — first-person observational |
| `5-biomarkers-visualization-spec.md` | ✅ N/A (design spec) |
| `5-biomarkers-tracking-template.md` | ✅ "Talk to your physician" framing — never prescriptive |
| `5-biomarkers-email-day0.md` | ✅ "I'm still in this process" anchor preserved |

---

## No sourcing check (per directive)

**Rule:** No PMIDs, no DOIs, no author-year citations, no link to specific papers.

| Asset | Check |
|---|---|
| `5-biomarkers-guide.md` | ✅ "the published research is consistent" + "the published research points to" — observational without specific citations |
| `5-biomarkers-landing-page.md` | ✅ No specific sourcing |
| `5-biomarkers-email-day0.md` | ✅ "FDA PCAC meeting on July 23" mentioned contextually without sourcing |

The only external reference is the FDA PCAC meeting date (July 23) which is a public regulatory event, not a clinical citation.

---

## No dosing protocols check (per directive)

**Rule:** Zero mg, mcg, ml dosing amounts anywhere in the lead magnet.

| Asset | Check |
|---|---|
| All assets | ✅ PASS. The only dose-adjacent language is "25-OH Vitamin D" and "RBC magnesium" (lab test names), not doses. |

---

## Telehealth referral pattern check (per Co-CEO sign-off B + compliance remediation)

**Rule:** Soft funnel only. "Substack has a vetted directory of telehealth providers" — text only, observational, no specific vendor promotion in this package.

| Asset | Check |
|---|---|
| `5-biomarkers-guide.md` | ✅ Section 5: "the Substack has a vetted directory of telehealth providers who can order the right labs" — text only |
| `5-biomarkers-landing-page.md` | ✅ No specific vendor mention |
| `5-biomarkers-email-day0.md` | ✅ No specific vendor mention |

The vetted directory itself lives on the Substack (per locked strategy). This package does not link to specific telehealth vendors directly.

---

## "I'm still in this process" anchor check (brand voice differentiator)

**Rule:** Non-negotiable brand voice anchor. Must appear in every major asset.

| Asset | Anchor present? |
|---|---|
| `5-biomarkers-guide.md` | ✅ Section 5 closing: "I'm still in this process. I'll be transparent with you the whole way." |
| `5-biomarkers-landing-page.md` | ✅ Below social proof: "I'm still in this process. I'll be transparent with you the whole way." |
| `5-biomarkers-email-day0.md` | ✅ Closing of email body: "I'm still in this process myself. I'll be transparent with you the whole way." |

---

## Final verdict

**All 5 lead magnet assets pass the 8-item compliance audit + brand voice rules + compliance remediation posture + Co-CEO sign-off (B) directives.**

No revisions required for compliance. The package is ready for Dre's final editorial review + visual production.

---

*Audit performed 2026-06-26 against `scripts/dop_compliance.py` 8-item audit + brand voice rules + `compliance/compliance-remediation-summary.md` clean posture + Co-CEO sign-off (B) 2026-06-26 11:54 CT.*