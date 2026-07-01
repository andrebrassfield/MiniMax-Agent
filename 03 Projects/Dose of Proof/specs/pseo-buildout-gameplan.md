---
type: spec
asset: pseo-buildout-gameplan
status: DRAFT — for Andre review
date: 2026-06-26
purpose: Technical gameplan for the doseofproof site to absorb massive pSEO volume without breaking. Defines route architecture, template patterns, infrastructure, and build sequence.
supersedes: none
pairs_with:
  - mold-cirs-keyword-mapping.md (content strategy)
  - traffic-flow.md (CTA flow)
  - pcac-coverage-july-2026.md (editorial calendar)
---

# pSEO Buildout Gameplan — Dose of Proof

> How the site ships from ~36 routes to 500+ pages without breaking structure, performance, or compliance. Concrete route patterns, code-level template architecture, and a phased build sequence.

---

## 1. Current State Audit (T0)

### 1.1 Route inventory (existing)

| Route | Type | Content source | Page count | Notes |
|-------|------|----------------|------------|-------|
| `/` | static | `src/app/page.tsx` | 1 | Hero + bento + sections |
| `/about`, `/contact`, `/intake`, `/privacy`, `/terms`, `/medical-disclaimer`, `/affiliate-disclosure` | static | `src/app/*/page.tsx` | 7 | Mix of polished + 4 flagged incomplete |
| `/products/{mold-detox,peptide-database,what-doctors-miss,doctors-miss-guide}` | static | `src/app/products/*/page.tsx` | 4 | Sales-style product pages |
| `/programs/30-day-mold-detox` | static | `src/app/programs/*/page.tsx` | 1 | Single program page |
| `/{craniocervical-instability,mold-toxicity,mcas-histamine}` | static | `src/app/*/page.tsx` | 3 | Condition landing pages |
| `/start-here`, `/testing-roadmap`, `/protocol-vault`, `/vault`, `/work-with-me` | static | `src/app/*/page.tsx` | 5 | Funnel hub pages |
| `/blogs` | index | `src/lib/mdx.ts` | 1 | Hub with category grid |
| `/blogs/[slug]` | dynamic | MDX (26 files) | 26 | Article template |
| `/blogs/topics/[category]` | dynamic | MDX category meta | 1–6 | Category hub |
| `/tests/[slug]` | dynamic | `src/lib/testing-roadmap.ts` (DiagnosticTest[]) | 5 | Type-safe test pages |
| `/content`, `/content/[slug]` | dynamic | MDX | small | Content library |
| `/lead-magnet`, `/lead-magnet/[slug]`, `/lead-magnet/[slug]/thank-you` | dynamic | MDX | small | Gating funnel |
| `/shop`, `/shop/product/[handle]` | dynamic | Shopify GraphQL | live | Storefront |
| `/recommend/[category]` | dynamic | ? | small | Recommendation hub |
| `/api/{checkout,contact,intake,lead,shopify}` | API | Route handlers | 5 | Form + Shopify proxy |

**Total: ~36 page routes + ~26 blog articles + 5 tests + small static landing set = ~67 unique URLs serving.**

### 1.2 Existing pSEO-favorable patterns (already strong)

- ✅ **`src/lib/testing-roadmap.ts` is the gold-standard pattern.** `DiagnosticTest` is a typed interface with 11 fields including `nextTestSlug` (cross-page linking) + `faqs` (FAQ schema). This is the model to clone for every new route group.
- ✅ **`src/lib/mdx.ts` has clean content-reading API.** `getArticleSlugs()`, `getArticleBySlug()`, `getCategories()`, `getAllArticles()` — ready to scale.
- ✅ **`/blogs/[slug]/page.tsx`** uses `generateStaticParams()` + MDX with frontmatter. Pre-renders at build time.
- ✅ **Brand kit v2 is locked.** Black `#000000` + warning-yellow `#FFD60A` chrome, applied across 178 PNG assets + 11 SVG sprite files. (PR #6, commits `db04078..2ae2447`.)
- ✅ **Compliance infrastructure is intact.** ComplianceGate, FAQ compliance language, full disclaimer footer — all preserved.

### 1.3 Gaps identified

| Gap | Severity | Notes |
|-----|----------|-------|
| **Incomplete pages: `/about`, `/contact`, `/intake`, `/lead-magnet`** | HIGH — visible to visitors | 4 pages flagged as TODO/stub. Polish before pSEO scale-up. |
| **No sitemap.ts** | HIGH — pSEO blocker | Search engines can't discover 500+ pages without it. |
| **No JSON-LD structured data** | HIGH — pSEO blocker | Articles + tests + conditions are perfect for Article, FAQPage, MedicalCondition schema. |
| **No robots.txt in repo** (needs verify) | MEDIUM | Confirm Next.js defaults + Vercel handling |
| **No per-route OG image generation** | MEDIUM | Currently share-uses `/marketing-assets/images/favicon-icons/og-image-1200x630.png` for everything. With 500+ pages, every share should have a unique OG card. |
| **MDX frontmatter inconsistent** | LOW | `date` vs `publishedAt`, missing `readTime` on some, varying `category` formats. Validate via `scripts/validate-content.mjs` (already exists). |
| **No internal-link automation** | LOW | `nextTestSlug` is hand-set. At 500+ pages, automation needed. |
| **No search functionality** | MEDIUM | With 500+ pages, site search matters. Algolia DocSearch or local Lunr index. |
| **No analytics on pSEO performance** | HIGH | Need per-route attribution: which pSEO pages drive opt-ins vs dead-ends. |

---

## 2. pSEO Opportunity Matrix (8 route groups)

Volume estimates = realistic 6-month shipping targets assuming one writer + one engineer + this game's build pipeline.

### 2.1 Peptide database — `/peptides/[slug]`
- **Why:** Highest commercial intent. Peptide buyers are the same people buying $400/mo telehealth + supplements. The content sells itself.
- **Volume:** 30–50 pages (BPC-157, TB-500, GHK-Cu, NAD+, Thymosin Alpha-1, Selank, Semax, Dihexa, AOD-9604, Ibutamoren, etc.)
- **Data source:** `src/data/peptides.json` — fully data-driven (no MDX), templated from typed `Peptide` interface.
- **Internal link grid:** Every peptide links to its mechanism, dosing, research, comparison peptides, related tests.
- **Compliance:** Every page must end with FDA-disclaimer block (same pattern as `/products/peptide-database`).

### 2.2 Lab test interpretation — `/tests/[slug]`
- **Why:** Highest utility. Sells the brand's "proof" positioning. Drives newsletter opt-in.
- **Volume:** 50–80 pages (currently 5). Add: C4a, TGF-β1, MSH, VIP, MMP-9, VEGF, HLA-DR, ADH/osmolality, lipase, elastase, zonulin, histamine, DAO, prostaglandins, leukotriene E4, etc.
- **Data source:** Extend `DiagnosticTest[]` in `src/lib/testing-roadmap.ts`. Pure data, no MDX.
- **Schema.org:** Each test page emits `MedicalTest` + `FAQPage` JSON-LD.
- **Internal link grid:** `nextTestSlug` chain (existing pattern) + auto-link to relevant peptides + protocols.

### 2.3 Condition hubs — `/conditions/[slug]`
- **Why:** Broad-reach SEO. Catches "mold toxicity symptoms", "CCI treatment", "MCAS diagnosis" etc.
- **Volume:** 20–40 pages (mold toxicity, CIRS, CCI, MCAS, hEDS, vagus nerve dysfunction, long COVID, fibromyalgia, chronic fatigue, POTS, dysautonomia, SIBO, leaky gut, mastocytosis, etc.)
- **Data source:** `src/data/conditions.json` + per-condition MDX for long-form.
- **Schema.org:** `MedicalCondition` JSON-LD with `signOrSymptom`, `possibleTreatment`.

### 2.4 Supplement database — `/supplements/[slug]`
- **Why:** Affiliate revenue + commercial intent.
- **Volume:** 30–50 pages (lithium orotate, phosphatidylcholine, butyrate, melatonin, DAO, quercetin, luteolin, binders — GI Detox+, MicroChitosan, etc., mast cell stabilizers, etc.)
- **Data source:** `src/data/supplements.json` with affiliate URLs.

### 2.5 Comparison pages — `/compare/[slug-a]-vs-[slug-b]`
- **Why:** "X vs Y" search volume is enormous and under-served in this niche.
- **Volume:** 20–30 curated combos (BPC-157 vs TB-500, GHK-Cu vs BPC-157, liposomal vs oral glutathione, NR vs NMN, mold binders comparison, charcoal vs bentonite, etc.)
- **Data source:** `src/data/comparisons.json` referencing peptides.json + supplements.json.
- **Auto-generation:** Next.js route `/compare/[pair]/page.tsx` reads JSON; if pair exists, renders; else 404.

### 2.6 Protocol templates — `/protocols/[slug]`
- **Why:** Actionable content = highest opt-in conversion.
- **Volume:** 15–25 protocols (binder protocol, methylation support, vagal tone protocol, mast cell stabilization, CIRS step-down, sleep protocol, mold prep, CCI rehab, etc.)
- **Data source:** `src/data/protocols.json` with phases + steps + duration.

### 2.7 "What doctors miss" expansion — `/doctors-miss/[condition]`
- **Why:** Brand-defining content. The 6 existing PNGs in `/marketing-assets/images/doctors-miss-series/` are perfect content hooks.
- **Volume:** 20–30 conditions. Pattern: 4–6 specific tests + 4–6 specific root-cause framings the average doctor misses.
- **Data source:** `src/data/doctors-miss.json` referencing tests.json + peptides.json.

### 2.8 Lead magnets (gated) — `/lead-magnet/[slug]`
- **Why:** Email list is the moat. Every cluster gets its own lead magnet.
- **Volume:** 5–10 lead magnets (5 Biomarkers checklist, Mold Timeline PDF, CCI Self-Screen PDF, MCAS Trigger Tracker, Peptide Stack Comparison, etc.)
- **Data source:** Existing `/lead-magnet/[slug]` route — already templated, just needs more content.
- **Compliance:** Gating must preserve all medical disclaimers.

**Total target: ~190–325 new pages across 8 route groups.**

---

## 3. Template Architecture (Next.js code patterns)

### 3.1 Two template patterns — pick per group

**Pattern A: Pure-data, fully typed (no MDX)**
Best for: peptides, tests, conditions, supplements, comparisons, protocols, doctors-miss.

```ts
// src/lib/types.ts
export type Peptide = {
  slug: string;
  name: string;
  shortName: string;
  category: 'Tissue Repair' | 'Longevity' | 'Cognitive' | 'Metabolic' | 'Immune';
  status: 'category-1' | 'category-2' | 'research-only';
  mechanism: string;
  benefits: string[];
  dosing: { range: string; frequency: string; route: string };
  research: { year: number; finding: string; citation: string }[];
  stackWith?: string[]; // peptide slugs
  relatedTests?: string[]; // test slugs
  faqs: FAQ[];
  affiliateProducts?: AffiliateProduct[];
  complianceNote: string;
};

// src/data/peptides.ts
import type { Peptide } from '@/lib/types';
export const peptides: Peptide[] = [ ... ];

// src/app/peptides/[slug]/page.tsx
import { peptides } from '@/data/peptides';
export async function generateStaticParams() {
  return peptides.map(p => ({ slug: p.slug }));
}
export async function generateMetadata({ params }) { ... }
export default function PeptidePage({ params }) {
  const peptide = peptides.find(p => p.slug === params.slug);
  if (!peptide) notFound();
  return <PeptideTemplate peptide={peptide} />;
}
```

**Pattern B: MDX with frontmatter (rich long-form)**
Best for: `/blogs/[slug]`, `/content/[slug]`, `/lead-magnet/[slug]`.

Already implemented at `/blogs/[slug]/page.tsx`. Extend `ArticleMeta` with `pseoCluster`, `pseoIntent`, `relatedSlugs`, `canonicalUrl` fields.

### 3.2 Required shared components

```
src/components/templates/
├── PeptideTemplate.tsx     # data-driven peptide page
├── TestTemplate.tsx        # extends existing tests/[slug]
├── ConditionTemplate.tsx
├── SupplementTemplate.tsx
├── ComparisonTemplate.tsx
├── ProtocolTemplate.tsx
├── DoctorsMissTemplate.tsx
└── LeadMagnetTemplate.tsx  # extends existing lead-magnet/[slug]
```

Each template:
- Emits JSON-LD via `<Script type="application/ld+json">`
- Renders OG image via `app/opengraph-image.tsx` per route
- Includes 4 internal links minimum (hub + 3 siblings)
- Ends with compliance footer
- Has unique H1 + meta description

### 3.3 Infrastructure helpers (must build first)

```
src/lib/seo/
├── schema.ts          # JSON-LD builders (Article, FAQPage, MedicalTest, MedicalCondition)
├── metadata.ts        # generateMetadata() helper
├── canonical.ts       # canonical URL builder
└── internal-links.ts  # auto-suggest links from relatedSlugs + cluster

src/app/sitemap.ts     # dynamic sitemap aggregating all [slug] routes
src/app/robots.ts      # dynamic robots.txt

src/app/
├── peptides/opengraph-image.tsx
├── tests/opengraph-image.tsx
├── conditions/opengraph-image.tsx
├── ... (one per route group)
```

---

## 4. Infrastructure for Scale (build once, leverage everywhere)

### 4.1 Dynamic sitemap (`src/app/sitemap.ts`)

Next.js 13+ App Router supports native sitemap generation. Must enumerate:
- All static routes
- All `generateStaticParams()` outputs for `[slug]` routes
- All MDX file slugs
- All Shopify products (via `revalidate`)

Returns Sitemap object array. Auto-served at `/sitemap.xml`.

### 4.2 JSON-LD per page (SEO multiplier)

Schema.org types to use:
- **`Article`** on all `/blogs/[slug]`
- **`MedicalTest`** on all `/tests/[slug]`
- **`MedicalCondition`** on all `/conditions/[slug]`
- **`Drug`** (USCDI) on all `/peptides/[slug]` — risky for FDA, use `MedicalTherapy` or omit
- **`FAQPage`** on any page with `faqs` frontmatter
- **`BreadcrumbList`** on every templated page
- **`Organization`** in root layout (already have)
- **`WebSite`** + `SearchAction` in root layout (enables sitelinks searchbox)

**Critical:** Validate JSON-LD with Google's Rich Results Test before shipping each cluster.

### 4.3 Per-route OG image generation

Use Next.js `opengraph-image.tsx` convention. Renders a `ImageResponse` (satori) with:
- Brand chrome (yellow border, black background)
- Page H1
- Category badge
- Compliance footer (for medical pages)

Each route gets a unique OG card. Pages auto-share with branded cards on X/LinkedIn/Slack/Discord.

### 4.4 Internal-link automation

`src/lib/seo/internal-links.ts` — for each page, suggest 4–6 related pages via:
1. Explicit `relatedSlugs` in data
2. Same cluster fallback (peptides → other peptides)
3. `nextTestSlug` chain for tests
4. Compliance footer with 3 evergreen links (Substack, Vault, Disclaimer)

### 4.5 Content validation pipeline

`scripts/validate-content.mjs` (already exists) — extend to enforce:
- Required frontmatter fields per content type
- Valid category slugs
- Date format ISO 8601
- Slug uniqueness across all MDX + data files
- FAQ schema valid (question + answer non-empty)
- Internal links resolve (no dead links)

Run on every commit via pre-commit hook or CI.

### 4.6 Site search (Algolia DocSearch or local)

At 200+ pages, search matters. Algolia DocSearch is free for OSS-style sites (apply for inclusion). Alternative: local Lunr.js index built at compile time.

Recommend: Algolia DocSearch. Indexes every page, free tier handles up to 10K queries/mo, branded UI in nav.

### 4.7 CDN + caching

Already on Vercel. Configure:
- `Cache-Control: public, s-maxage=31536000, stale-while-revalidate=86400` for `/peptides/*`, `/tests/*`, `/conditions/*` (data rarely changes)
- `Cache-Control: public, s-maxage=3600, stale-while-revalidate=86400` for `/blogs/*` (new content ships weekly)
- `Cache-Control: no-cache` for `/api/*`, `/shop/*`

### 4.8 Analytics per pSEO cluster

Add to GA4 (or Plausible if preferred):
- Custom dimension: `pseo_cluster` (peptides / tests / conditions / etc.)
- Custom dimension: `pseo_intent` (commercial / informational / transactional)
- Goal: `newsletter_optin` per cluster
- Goal: `product_click` per peptide/supplement
- Dashboard: "pSEO Performance" — sessions, opt-ins, product clicks, by cluster

---

## 5. Build Sequence (3 phases, 6–8 weeks)

### Phase 1 — Foundation (Week 1)

**Goal:** Site is ready to absorb 500+ pages without breaking.

- [ ] Finish the 4 incomplete pages (`/about`, `/contact`, `/intake`, `/lead-magnet` index)
- [ ] Create `src/lib/seo/schema.ts`, `metadata.ts`, `canonical.ts`, `internal-links.ts`
- [ ] Add `src/app/sitemap.ts` (dynamic, all routes)
- [ ] Add `src/app/robots.ts`
- [ ] Extend `validate-content.mjs` — enforce frontmatter schema per type
- [ ] Add `src/components/SeoSchema.tsx` (JSON-LD renderer) + per-type schema builders
- [ ] Add WebSite + Organization JSON-LD in root layout
- [ ] Verify build + deploy to PR

**Deliverable:** Site foundation hardened. Ship the PR.

### Phase 2 — First cluster + per-route OG (Weeks 2–3)

**Goal:** One cluster live end-to-end (templates + data + OG + JSON-LD + sitemap).

- [ ] Pick **lab test interpretation** as first cluster (already has 5, type-safe pattern exists)
- [ ] Extend `DiagnosticTest[]` to 30 tests
- [ ] Add `MedicalTest` JSON-LD on every test page
- [ ] Add `/tests/opengraph-image.tsx`
- [ ] Add FAQ schema on tests with `faqs`
- [ ] Internal-link automation: tests link to each other + peptides + protocols
- [ ] Sitemap refresh + Search Console submit
- [ ] GA4 pSEO dimension instrumentation
- [ ] Ship PR

**Deliverable:** Tests cluster live. 30+ pages. Validated in Search Console.

### Phase 3 — Parallel cluster build (Weeks 4–8)

**Goal:** Ship remaining clusters in priority order.

- [ ] **Week 4:** Peptides cluster (30+ pages) — highest commercial intent
- [ ] **Week 5:** Conditions cluster (20+ pages) + Supplements (30+ pages) in parallel
- [ ] **Week 6:** Comparisons (20+ pages, auto-generated from existing data) + Protocols (15+ pages)
- [ ] **Week 7:** Doctors-miss (20+ pages) + Lead magnets (5+)
- [ ] **Week 8:** Apply Algolia DocSearch + add site-wide search + cross-cluster internal linking audit

**Deliverable:** ~200–300 new pages live, all templated, all with schema + OG + internal links.

### Phase 4 — Optimization (Week 9+, ongoing)

- Search Console monitoring: which pSEO pages rank, which get impressions, CTR
- A/B test CTAs per cluster (Substack vs Skool vs product)
- Add user-generated content loop (testimonials → SEO pages)
- Internal-link graph audit (orphan pages, low-link-count pages)

---

## 6. Top-10 Priority Pages (ship this week, smallest scope)

If you only ship 10 pages, ship these:

1. **`/tests/[slug]` extended to 30 tests** — smallest cluster, biggest type-safe extension
2. **`/sitemap.ts` + `/robots.ts`** — required for pSEO discoverability
3. **`/about`** — currently flagged incomplete, finish it
4. **`/contact`** — currently flagged incomplete, finish it
5. **`/intake`** — currently flagged incomplete, finish it (high-intent form)
6. **`/lead-magnet` index** — currently flagged incomplete, finish it (entry to all lead magnets)
7. **`/peptides/[slug]` with first 5 peptides** — proves the data-driven pattern works
8. **`/compare/bpc-157-vs-tb-500`** — quick win, comparison framework reusable
9. **`/doctors-miss/mold-toxicity`** — quick win, reuses 6 existing PNGs
10. **JSON-LD on `/blogs/[slug]`** — apply `Article` + `FAQPage` schema to 26 existing articles

---

## 7. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| FDA compliance on peptide pages | Compliance footer is mandatory. Run every peptide page past compliance review before publish. Use `MedicalTherapy` schema, not `Drug`. |
| MDX frontmatter drift at scale | `validate-content.mjs` runs on every commit + blocks merge on schema violation |
| Page weight (500+ URLs in sitemap) | Sitemap index file + multiple sub-sitemaps (`/sitemap-posts.xml`, `/sitemap-tests.xml`, etc.) |
| Cannibalization (multiple pages targeting same keyword) | Keyword registry: `data/keywords.json` assigns each target keyword to ONE primary URL + secondary URLs |
| Thin content | Each new page requires minimum 800-word unique body, NOT a stub |
| Build time at 500+ pages | Use ISR (`revalidate: 86400`) for Shopify + sitemap. Static for data-driven clusters (fast). |
| 404 storms on URL changes | Use `next.config.js` redirects. Always 301, never 302 for SEO. |

---

## 8. Pairing with Existing Strategy Docs

This spec is the **buildout gameplan**. It pairs with:

- **`mold-cirs-keyword-mapping.md`** — defines keyword clusters and content gaps; this spec defines how those gaps get turned into pages
- **`traffic-flow.md`** — defines where every page's CTA points; this spec ensures every template has a CTA slot in the right place
- **`pcac-coverage-july-2026.md`** — defines the editorial calendar; this spec defines the route infrastructure that calendar lands on
- **`p1-citation-framework.md`** — defines citation gates; this spec requires every pSEO page to pass citation gates before publish
- **`content-engine-spec.md`** — defines content production; this spec defines where produced content lands

---

## 9. Decision Points (need Andre's call)

Before building, I need Andre to confirm:

1. **Cluster priority:** Is peptide database really #2 (commercial) or do we lead with conditions (broader SEO)?
2. **Lead magnet gating:** Do we add a new gated route per cluster, or one mega-gate that covers all clusters?
3. **Algolia DocSearch:** Apply now or wait until 200+ pages live?
4. **OG image generation:** Auto-generate per slug via satori, or keep static brand image?
5. **Internal-link automation:** Auto-suggest (algorithmic) or hand-curated `relatedSlugs`?
6. **MDX vs pure-data:** For peptides, conditions, supplements — pure-data JSON or MDX-with-frontmatter? (Recommend pure-data — easier to scale + validate.)

---

*Spec author: Mavis (track 1). Track 2 buildout on Andre's go.*