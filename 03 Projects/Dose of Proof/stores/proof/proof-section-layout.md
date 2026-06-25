---
type: layout-spec
asset: proof-section-layout
status: ✅ FINAL (locked 2026-06-24, ready for first real case study)
purpose: layout for the "Proof" section on Substack About page + future course sales page + launch assets — designed to display case studies + testimonials + cohort analysis consistently across all surfaces
applies_to: Substack About page, course sales page (when built), launch email, sales landing pages
companion_to: stores/proof/README.md + stores/proof/intake-template.md + stores/proof/redaction-protocol.md
---

# Proof Section Layout — Dose of Proof

> The structural layout for displaying proof on every surface. Standardized so case studies + testimonials + cohort analyses look consistent across the Substack About page, course sales page, and launch assets.

---

## The Proof Section (canonical structure)

### SECTION HEADER

**Eyebrow text:** "PROOF" (small, all caps, dark navy on light backgrounds, white on dark)

**Headline:** "What the framework actually looks like in real data"

**Subheadline:** "Three people running the PCAC framework under their physician's care. Same biomarker floor. Different upstream drivers. The data tells the story."

---

### SECTION COMPONENT 1 — Featured Case Study (above the fold)

**Format:** Single highlighted case study, full-width card

**Components:**
1. **Identity line:** "Mark R., 38, founder of two SaaS companies" (or per intake consent scope)
2. **The starting state:** 2-3 sentences on what Mark was dealing with before the framework
3. **The biomarker data table:** Before/after numbers for 2-3 of the 5 PCAC biomarkers
4. **The trend:** 1-2 sentences describing what changed over the tracking period
5. **Direct quote:** 1-2 sentences from Mark in his own voice (redacted per protocol)
6. **"I'm still in this process" anchor** if Mark is still tracking (matches Dre's brand voice)

**Visual style:**
- Dark navy background (#1a2a3a or similar)
- White text
- HRV / TyTron / biomarker trend chart as visual element (Dre's data or anonymized cohort chart)
- Small "View full case study" link at bottom

**Sample structure:**
```markdown
> ## Mark R., 38 — Founder, two SaaS companies
>
> "I'd been told my labs were normal for 4 years while I felt like I was disappearing."
>
> | Biomarker | Baseline (Feb 2026) | Current (Jun 2026) | Trend |
> |-----------|---------------------|---------------------|-------|
> | Morning HRV (7-day avg) | 38 | 54 | +42% |
> | Guarding score | 8/10 | 4/10 | -50% |
> | Flushing episodes/week | 12 | 3 | -75% |
>
> "The framework forced the data. I'm still tracking. The numbers move but they don't arrive at a finish line."
>
> *Numbers verified against Mark's original tracking. First-name + age + role only per intake consent scope. Mark can withdraw at any time.*
```

---

### SECTION COMPONENT 2 — Three Case Study Cards (below the fold)

**Format:** Three side-by-side cards (responsive — stacks on mobile)

**Each card contains:**
1. Identity line: First name + age + role (per consent)
2. One-liner opening: The starting state in one sentence
3. Two biomarker data points: Most-moved numbers
4. Direct quote: 1 sentence (redacted)
5. "Read full case study" link

**Sample card:**
```markdown
> ### Sarah L., 42 — Athlete + coach
>
> "Specialists kept treating symptoms separately. The 5-biomarker floor caught the upstream driver."
>
> **HRV:** 35 → 51 (6 months)
> **Sleep consolidation:** 4 hrs continuous → 6.5 hrs continuous
>
> [Read full case study →]
```

---

### SECTION COMPONENT 3 — Cohort Analysis Block (anonymized)

**Format:** Single full-width section, distinct visual treatment (lighter background, different typography)

**Eyebrow text:** "ACROSS THE COMMUNITY"

**Headline:** "What 47 Inner Circle members are tracking"

**Subheadline:** "Anonymized cohort data. Every individual explicitly opted in. No scraping of community data."

**Components:**
1. Cohort description: "Inner Circle members who actively tracked morning HRV over 6 months"
2. Aggregate trend chart: Average improvement, distribution chart
3. Sample data points (anonymized): "Median HRV improvement: 38% over 6 months. Top quartile: 65% improvement. Bottom quartile: 8% improvement."
4. Methodology note: How the data was collected + anonymized + opt-in process
5. Opt-out link: "If you're an Inner Circle member and want to opt out of cohort analysis, [click here]"

**Sample structure:**
```markdown
> ## Across the community
>
> **47 Inner Circle members** actively tracked morning HRV over the last 6 months. All explicitly opted in to anonymized cohort analysis.
>
> ### Median improvement: 38%
>
> | Quartile | HRV improvement |
> |----------|-----------------|
> | Top 25% | +65% |
> | Second quartile | +42% |
> | Third quartile | +28% |
> | Bottom 25% | +8% |
>
> **Methodology:** Daily morning HRV readings, free phone app, before caffeine. Data aggregated monthly. Individuals can opt out at any time.
>
> [If you're an Inner Circle member and want to opt out →]
```

---

### SECTION COMPONENT 4 — Clinician Testimonial (1 quote)

**Format:** Single pull-quote, large typography, optional clinician attribution

**Components:**
1. The quote: 1-3 sentences in the clinician's voice
2. Attribution: "Dr. [First Name Last Initial], [Specialty]" (per consent scope)
3. Compliance footer: "This testimonial reflects the clinician's professional experience and does not constitute medical advice for any individual reader."

**Sample structure:**
```markdown
> "The biomarker framework forces data-driven conversations between patient and physician. That's the part most approaches miss."
>
> — Dr. J.C., upper cervical specialist
>
> *This testimonial reflects Dr. J.C.'s professional experience. It does not constitute medical advice for any individual reader.*
```

---

### SECTION COMPONENT 5 — Peer Testimonial (1 quote)

**Format:** Single pull-quote, smaller typography than clinician quote

**Components:**
1. The quote: 1-2 sentences from a peer (Skool Inner Circle member or similar)
2. Attribution: "Marcus T., 42, founder & CEO" (per consent scope)
3. Compliance footer: "Marcus's experience. Not a guarantee of any outcome for any other person."

**Sample structure:**
```markdown
> "I stopped chasing symptoms and started mapping the terrain. The biomarker data told me what was working."
>
> — Marcus T., 42, founder & CEO
>
> *Marcus's experience. Not a guarantee of any outcome for any other person.*
```

---

### SECTION FOOTER

**Compliance footer (mandatory on every Proof Section):**

> *The case studies and testimonials on this page represent individual experiences within the PCAC framework. Outcomes are not guaranteed for any other person. Biomarker data is attributed to the named individuals with their explicit consent; first-name + age + role only by default. Every contributor can withdraw their consent at any time, with 24-hour removal SLA. This section is for informational purposes only and is not medical advice.*

---

## Where this layout ships

### Surface 1 — Substack About page (immediate)

**Where:** Substack publication's About page (the public-facing brand intro)
**Status when:** Once 3 case studies + 1 cohort analysis + 2 testimonials are approved
**Layout:** Components 1 + 2 + 3 + 4 + 5 in the order above

### Surface 2 — Course sales page (when built, target July 23 launch)

**Where:** Doseofproof.com course sales page (the launch landing page)
**Status when:** Cart opens July 23
**Layout:** Components 1 (featured case study) + 4 (clinician testimonial) — anchors the sales conversion

### Surface 3 — Launch email (Email 7)

**Where:** The July 22-23 launch email (soft-pitch for the course)
**Status when:** Cart opens July 23
**Layout:** Components 4 + 5 (the two testimonials) + a single quote pull — drives conversion to cart

### Surface 4 — Substack post (proof-specific post)

**Where:** A dedicated "Proof" Substack post (could ship July 18 or so as part of pre-launch)
**Status when:** Once 3 case studies approved
**Layout:** Components 2 + 3 (the three cards + the cohort analysis) — long-form version

### Surface 5 — LinkedIn post (case study format)

**Where:** LinkedIn long-form post (July 11 or 18, weekly cadence)
**Status when:** Once 1-2 case studies approved
**Layout:** Single featured case study (Component 1) reformatted for LinkedIn's professional-but-raw tone

---

## What this layout does NOT do

- ❌ It does not promise outcomes ("you will see X improvement") — only describes what happened for the named individual
- ❌ It does not use therapeutic-outcome language ("cured," "recovered," "healed")
- ❌ It does not include photos / video / scan images without separate explicit consent
- ❌ It does not include dosing protocols
- ❌ It does not include sourcing language
- ❌ It does not include company names without explicit consent
- ❌ It does not include therapeutic-outcome testimonials ("I recovered from X")

---

## Empty-state placeholder (before real case studies exist)

**For the launch window (July 23) when the brand has Dre as the only data subject:**

> ## PROOF — Dre's case study (first case)
>
> I'm still in this process.
>
> Four specialists. Five diagnoses. "Your labs are normal."
>
> | Biomarker | Baseline (Nov 2025) | Current (Jun 2026) | Trend |
> |-----------|---------------------|---------------------|-------|
> | Morning HRV (7-day avg) | 32 | 53 | +66% |
> | Guarding score | 9/10 | 4/10 | -56% |
> | Flushing episodes/week | 21 | 3 | -86% |
> | Sleep continuity | 3-4 hrs | 6-7 hrs | +75% |
> | Mental clarity | 3/10 | 7/10 | +133% |
>
> "The framework forced the data. I'm still tracking. The numbers move but they don't arrive at a finish line."
>
> *Dre's own data. The first case study in the Proof Section. Future case studies will feature community members running the framework under their physician's care.*

---

## What this layout enables

The Proof Section is the brand's "show me the data" promise made visible. When 3+ community members have consented, the section is populated with real people. Until then, Dre is the first case study — same framework, same redaction discipline, same data-trend language.

The layout scales: 1 case study → 3 case studies → 10 case studies → cohort analysis on top. Same components, same compliance posture, same discipline.

---

*Last updated: 2026-06-24 (Live Execution pass)*
*Ship-ready: yes. Awaiting first real community member to consent + complete intake.*