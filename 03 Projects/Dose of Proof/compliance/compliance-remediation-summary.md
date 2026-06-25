---
type: compliance-remediation-summary
asset: hotfix/compliance-remediation-2026-06-24
status: ✅ READY FOR HUMAN REVIEW (no commit, no push)
branch: hotfix/compliance-remediation-2026-06-24
patch_file: apps/doseofproof/remediation-diff.patch
build_status: ✅ Passes (npm run build)
date: 2026-06-24 19:55 CT
---

# Compliance Remediation Summary — Dose of Proof

> **Mission:** strip gray-market, sourcing, dosing-protocol, testimonial-adoption, and Discord community framing from the live production site before the June 27 PCAC content calendar launches. Add a persistent, non-dismissible compliance gate.

## Files touched (5)

| File | Lines added | Lines removed | Net |
|---|---:|---:|---:|
| `src/components/compliance/ComplianceGate.tsx` (NEW) | 41 | 0 | +41 |
| `src/app/layout.tsx` (wire ComplianceGate) | 2 | 0 | +2 |
| `src/app/products/peptide-database/page.tsx` | 50 | 58 | −8 |
| `src/app/shop/product/[handle]/page.tsx` (productData entries) | 15 | 16 | −1 |
| `src/app/shop/page.tsx` (intro copy + metadata) | 4 | 2 | +2 |
| **Total** | **112** | **76** | **+36** |

## Change map — every edit mapped to the violation it fixes

### File: `src/components/compliance/ComplianceGate.tsx` (NEW)

| Change | Locked source it enforces |
|---|---|
| New persistent global banner rendered inside `RootLayout`, above all page content | Decisions 8 + 12 (compliance gates on every asset); 4 Traps framework (Trap 1–4, every page shows the line) |
| Exact compliance text (per directive): *"Dose of Proof is an educational bridge only. We do not sell compounds, provide dosing protocols, or facilitate sourcing. All health decisions require licensed medical oversight. This site demonstrates the proof-centered approach — not the patterns that create regulatory exposure."* | "My Body, Not Yours" rule + Objective Intent Doctrine (21 CFR 201.128) |
| Non-dismissible (no close button), `aside` with `role="note"`, persistent across all routes via layout shell | Required by directive — non-dismissible educational disclaimer on every page |

### File: `src/app/layout.tsx`

| Change | Locked source |
|---|---|
| Import `ComplianceGate` | — |
| Render `<ComplianceGate />` inside `<body>` after `SmoothScroll`, before `{children}` — appears above all page content on every route | Compliance layer enforcement |

### File: `src/app/products/peptide-database/page.tsx`

| Change | Violation removed | Locked source it fixes |
|---|---|---|
| Removed entire `<script type="application/ld+json">` JSON-LD schema with fabricated `aggregateRating: 4.9/42 reviews` | Fabricated social proof / schema.org misuse | Decision 8 (strict compliance gates — every asset must be truthful); consumer-trust fraud exposure |
| Title + metadata: "Peptide Protocol Database" → "Peptide Research Index"; description rephrased to remove "exact dosing protocols", "reconstitution guides", and "sourcing links" | Marketing gray-market + dosing + sourcing framing | Decision 12 (Swiss Chems + all gray-market permanently blocked) + Trap 4 (ecosystem separation) |
| H1 + intro paragraph: removed "exact dosing protocols, reconstitution guides, and sourcing links for BPC-157, TB-500, GHK-Cu, and more" | Same | Same |
| Benefits list (6 items) replaced: removed "BPC-157 & TB-500 stack for tissue repair", "GHK-Cu protocol for systemic inflammation", "Reconstitution math made simple (calculators included)", "Verified sourcing links to avoid bunk peptides", "Access to the private community Discord"; replaced with FDA-briefing-digest / PCAC docket tracker / 503A compounding eligibility / Marek + Lifeforce telehealth directory / compliance-first sourcing checklist / Substack delivery | Specific dosing stack + sourcing + Discord community = textbook integrated-ecosystem pattern | Decision 12 + Traps 1 + 4 + "My Body, Not Yours" rule + Objective Intent Doctrine |
| Testimonials section (Robert P. + Alyssa T. quotes) **removed entirely** | Robert P.: *"The reconstitution calculator alone saved me hours of head scratchers. Sourcing links are verified and saved me from buying bunk products online."* — adopts sourcing benefit as labeling. Alyssa T.: *"I used the BPC-157 and GHK-Cu stacks to support my gut mucosal lining. The dosing updates are backed by PubMed citations"* — adopts specific-compound efficacy as labeling | Trap 3 (Section 505(a) testimonial adoption: hosting/boosting a testimonial that says "[compound] healed my [condition]" = you adopt it as labeling) + "My Body, Not Yours" rule |
| Replaced testimonial section with prominent **compliance banner** (amber): "This index is educational research only. We do not sell compounds, provide dosing protocols, or facilitate sourcing. Any peptide access happens through board-certified physicians and 503A compounding pharmacies — never through integrated storefronts or gray-market channels." | Compensating control replacing social-proof block | All 5 unbreakable rules + Trap 4 explicit reference |
| Guarantee block rephrased: removed "calculators" mention (no calculators exist yet in the codebase — was aspirational false advertising) | False advertising | Decision 8 (truthful assets only) |
| Medical disclaimer block rephrased: "documents my personal experience and research with peptides" + "Peptide therapy is experimental" → "documents published research and federal regulatory process" + "Always consult your physician before making any health decision" | Personal-experience framing risked adopting user's experience as medical advice | "My Body, Not Yours" rule (always observational, never prescribing) |
| Related Reading section: **removed BPC-157 Dosage Guide cross-link entirely** (per directive "do not touch content yet"); replaced with link to compliance-aligned peptide-tracker lead magnet at `/lead-magnet/peptide-tracker` | Cross-link promoted a blog post that prescribes specific dosing ("250mcg to 500mcg twice daily") + has a gray-market affiliate link (`pspeptides.com?ref=dre`) | Decision 12 + "My Body, Not Yours" rule. Blog post itself is **not edited** this pass per directive (later literature-review rewrite) |

### File: `src/app/shop/product/[handle]/page.tsx`

| Change | Violation removed | Locked source it fixes |
|---|---|---|
| `peptide-protocol-database` productData entry: title + description + benefits + testimonials rewritten to match the compliance-aligned `/products/peptide-database` page | Same violations as above (sourcing, dosing stacks, Discord, testimonials) | Same as above — keeps the shop detail page consistent with the marketing page |
| `peptide-protocol-database` testimonials array: `[]` (empty) — preserves type contract, removes adopting testimonials | Robert P. + Alyssa T. | Trap 3 testimonial adoption |
| `30-day-mold-detox` productData entry: subtitle "Complete Protocol" → "Educational Workbook"; description rephrased ("exact supplement stack" → "supplement stack … educational reference only — work with a licensed physician for personal protocol design"); benefit "Daily supplement stack with exact dosing" → "Daily supplement reference stack (educational — not a prescription)" | "Exact dosing" framing + "Complete Protocol" implied prescribing | "My Body, Not Yours" rule (no prescribing) |
| `30-day-mold-detox` testimonials (Marcus W. + Sarah K.) **kept** — they describe mycotoxin testing outcomes, not specific compound efficacy claims for research-chemicals. No gray-market exposure. | (none — kept intentionally) | — |

### File: `src/app/shop/page.tsx`

| Change | Violation removed | Locked source it fixes |
|---|---|---|
| Metadata description: "peptide databases, and recovery tools" → "research indexes, and recovery tools. Educational bridge only — no compounds sold, no dosing protocols, no sourcing" | Implicit peptide-database promotion | Decision 12 + 4 Traps framing |
| Intro paragraph: "Every protocol includes sourcing verification, dosing guidelines, and tracking templates" → "Educational workbooks, research indexes, and tracking templates — no compounds sold, no dosing protocols, no sourcing. Health decisions happen with your physician" | Shop-level "sourcing verification + dosing guidelines" promise | Decision 12 + Objective Intent Doctrine |

## Files deliberately NOT touched

Per directive scope + strategy:

| File | Why left alone |
|---|---|
| `src/content/articles/bpc-157-dosage-guide.mdx` | Directive: "do not touch content yet" — flagged for later literature-review rewrite. Cross-link from `/products/peptide-database` removed; blog post still reachable by direct URL but no longer promoted from sales surface. |
| `src/app/lead-magnet/[slug]/page.tsx` (peptide-tracker entry) | Already compliance-first: "FDA status tracker for 20+ popular peptides (Golden Zone vs Danger Zone)", "PCAB-accredited 503A/503B pharmacy directory", "Telehealth provider network with prescribing authority", "Compliance-first sourcing checklist - never buy from gray market again". Aligned with locked strategy — should be the *promoted* lead magnet, not `peptide-protocol-database`. |
| `src/app/about/page.tsx` Blair Chiropractic links (Dr. Jackson Chism, Blair Chiropractic Society) | Legitimate chiropractors, not gray-market chemical sourcing. Aligned with the "specialist referral" pattern, not the "sourcing funnel" pattern. |
| `src/components/layout/Footer.tsx` | Existing footer text is generic ("Not selling. Just proving." + "This site contains affiliate links…"). ComplianceGate above the footer carries the harder compliance language. Footer still legal and on-brand. |
| `src/app/products/{doctors-miss-guide,mold-detox,what-doctors-miss}/page.tsx` | No gray-market or research-chemical sourcing language found in grep sweep. Keep as-is. |
| Other product pages | Same — clean |

## Open questions for human review (flagged, not guessed)

1. **`peptide-protocol-database` Shopify listing still exists in the live store.** This hotfix edits the local `productData` entry (which is the dev fallback for the shop detail page) but the live Shopify product is fetched dynamically via `src/app/shop/page.tsx` → `shopifyFetch`. If the Shopify listing still exists with the old title/description, the shop page will still render it. **Action needed:** update or unpublish the Shopify listing directly in the Shopify admin.
2. **Other product handles in `iconMap` (shop/page.tsx:29-36)** still reference `peptide-protocol-database` icon — harmless (it's just an icon mapping) but worth updating once the Shopify product is renamed/removed.
3. **`recommend/[category]/page.tsx`** category pages (peptides, mold-detox, diagnostics) exist but were not deep-read this pass. Worth a follow-up sweep before June 27 to confirm none of them re-introduce compound or sourcing framing.

## Verification status

| Check | Result |
|---|---|
| `npm run build` | ✅ Passes — all 24 routes prerender cleanly, no errors |
| `grep -E "Discord\|bunk\|verified sourcing\|exact dosing protocol\|peptide stack\|aggregateRating\|Robert P\.\|Alyssa T\.\|sourcing verification\|dosing guidelines"` against edited files | ✅ **Zero matches** |
| ComplianceGate present in `src/app/layout.tsx` | ✅ Line 76: `<ComplianceGate />` rendered after `<SmoothScroll />` before `{children}` |
| ComplianceGate component renders on every page | ✅ Wired in root layout — covers all 24 routes |
| No commit, no push | ✅ Working tree has changes unstaged; branch is `hotfix/compliance-remediation-2026-06-24` checked out but no commit made |
| `git diff` patch file exists | ✅ `apps/doseofproof/remediation-diff.patch` (327 lines, 5 files) |

## Reviewer quick-start

```bash
# 1. Inspect the patch
cd /Users/brassfieldventuresllc/MiniMax-Agent/apps/doseofproof
cat remediation-diff.patch

# 2. (Optional) Preview each change
git diff src/app/layout.tsx
git diff src/app/products/peptide-database/page.tsx
git diff src/app/shop/product/[handle]/page.tsx
git diff src/app/shop/page.tsx
cat src/components/compliance/ComplianceGate.tsx

# 3. Build to confirm clean
npm run build

# 4. Visually verify the pages
npm run dev
# → http://localhost:3000/products/peptide-database
# → http://localhost:3000/shop/product/peptide-protocol-database
# → http://localhost:3000/shop
# ComplianceGate banner should appear above all content

# 5. When satisfied, commit + push
git add -A
git commit -m "fix(compliance): remediate gray-market sourcing, dosing-protocol, testimonial-adoption, Discord references + add persistent ComplianceGate banner

Pre-launch hotfix ahead of June 27 PCAC content calendar. Maps to
Decisions 8, 12 + 4 Traps framework + Objective Intent Doctrine.
See compliance-remediation-summary.md for full change map."

git push -u origin hotfix/compliance-remediation-2026-06-24
```

---

*Last updated: 2026-06-24 19:58 CT*
*Patch: `apps/doseofproof/remediation-diff.patch` (327 lines, 5 files)*
*Branch: `hotfix/compliance-remediation-2026-06-24` (no commit, awaiting review)*
