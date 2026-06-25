---
type: protocol
asset: redaction-anonymization-protocol
status: ✅ FINAL (locked 2026-06-24)
purpose: standardize how case studies + testimonials are anonymized + redacted before publication — protects people, prevents scope creep, ensures compliance
companion_to: stores/proof/README.md + stores/consent/README.md
applies_to: every case study + testimonial before publication in any surface
---

# Redaction + Anonymization Protocol — Dose of Proof

> Every case study and testimonial passes through this protocol before publication. No exceptions. The protocol protects the person, prevents scope creep, and ensures compliance with the brand's locked posture.

---

## The 4-rule redaction framework

### Rule 1 — Identity redaction (default: minimal disclosure)

| Element | Default | When expanded |
|---------|---------|---------------|
| Full name | ❌ NEVER (unless explicit consent in Section 8 of intake) | First name + last initial only, even with full-name consent, unless person explicitly asks for full name |
| Last name | ❌ NEVER (unless explicit consent) | — |
| Company name | ❌ NEVER (unless explicit consent) | — |
| City | ❌ NEVER (unless explicit consent) | Country / region only as default |
| Specific employer / workplace | ❌ NEVER | — |
| Date of birth | ❌ NEVER | Age only as default |
| Specific dates (day/month) | ❌ NEVER | Month + year only |
| Photos / video | ❌ NEVER (separate explicit consent) | — |

**Default identity disclosure:** First name + last initial + age + role only.

### Rule 2 — Data redaction (numbers + outcomes)

| Element | Default | When expanded |
|---------|---------|---------------|
| Specific lab values | ⚠️ PERMITTED if Dre verifies against original case | Round to nearest meaningful unit (HRV 53.7 → 54) |
| Specific imaging findings | ⚠️ PERMITTED if person consented + clinical verification | No patient IDs / accession numbers |
| Therapeutic-outcome language | ❌ NEVER | "I recovered from X" / "this cured me" / "I'm healed" all forbidden |
| Before/after photos of body | ❌ NEVER (separate consent) | — |
| Supplement/medication brand names | ❌ NEVER (unless person explicitly consented + clinically relevant) | Generic names only ("an SSRI" not "Lexapro") |
| Dosing protocols for compounds | ❌ NEVER | Frame as "physician-supervised" without specifics |
| Sourcing language | ❌ NEVER (no supplier names, no RUO labeling) | — |

**Default data disclosure:** Numbers + trends + clinical findings only. No brands, no doses, no sourcing.

### Rule 3 — Language redaction (therapeutic vs operational)

**FORBIDDEN language patterns** (auto-redact during draft production):

| Forbidden | Permitted alternative |
|-----------|----------------------|
| "I recovered from [condition]" | "My biomarkers trended from X to Y" |
| "This [compound/intervention] cured me" | "This [compound/intervention] was part of my protocol" |
| "I'm healed" / "I'm fixed" | "I'm still in this process" (or "my numbers are trending") |
| "[Compound] is the answer for [condition]" | "I track [compound] under physician supervision" |
| "You should try [intervention]" | "I tried [intervention] — here's what my data showed" |
| "I no longer have [symptom]" | "My [symptom] severity dropped from X to Y" |
| "This will help you with [condition]" | "This is how it showed up in my data" |

**The reframe principle:** All case studies describe what the person TRACKED + what the DATA SHOWED, never what the person recommends or prescribes for others.

### Rule 4 — Scope redaction (the surface discipline)

**Every published story matches the consent scope exactly.**

If person consented to "Substack About page Proof Section only," the story does NOT appear on:
- Course sales page
- Launch email
- Skool announcement
- LinkedIn post

Even if the content is identical. Even if "it's the same story." Scope is scope. **No scope creep.**

---

## The redaction audit (run before every publication)

For every case study / testimonial draft, Mavis runs this 13-item audit:

- [ ] **Identity:** First name + last initial only (or expanded per explicit consent)
- [ ] **No company name** (unless explicit consent)
- [ ] **No city** (unless explicit consent; country/region OK as default)
- [ ] **No employer / workplace specifics**
- [ ] **No date of birth** (age only)
- [ ] **No specific dates** (month + year only)
- [ ] **No photos / video / scan images** (separate explicit consent)
- [ ] **No therapeutic-outcome language** (replaced with data-trend language)
- [ ] **No sourcing language** (no supplier names, no RUO labeling)
- [ ] **No dosing protocols** (physician-supervised framing only)
- [ ] **No brand names for medications** (generic names only)
- [ ] **Scope match:** the published surface matches the consent scope exactly
- [ ] **Withdrawal right acknowledged:** the published version includes a note that the person can withdraw at any time

If any item fails, the draft goes back to redraft. No publication until the audit is clean.

---

## The cohort analysis protocol (separate from individual case studies)

For anonymized cohort analyses (e.g., "Across 47 Inner Circle members..."), additional rules:

| Element | Requirement |
|---------|-------------|
| Minimum cohort size | 10+ individuals (below this = no aggregate publication) |
| Individual identifiability | Cannot be reverse-engineered to a single person from the data |
| Consent | All individuals in the cohort must have explicitly opted into cohort analysis (separate consent field) |
| Opt-out | Any individual can opt out of cohort analysis at any time, removing their data from future publications |
| Recency cutoff | Cohort data only includes individuals who actively tracked in the last 90 days (or appropriate window) |
| Update cadence | Cohort analyses updated quarterly, not in real time |

**Cohort analysis template:** `anonymized-cohort/[topic]-cohort-analysis.md`

---

## Examples — before / after redaction

### Example 1 — Identity redaction

**BEFORE (forbidden):**
> Mark Richardson, 38, is the founder of Acme SaaS, based in Austin, TX.

**AFTER (permitted):**
> Mark R., 38, is a founder of two SaaS companies.

### Example 2 — Therapeutic language redaction

**BEFORE (forbidden):**
> BPC-157 cured my tendinopathy. After 3 months I was completely healed and back to lifting heavy.

**AFTER (permitted):**
> BPC-157 was part of my physician-supervised protocol for tendinopathy. Over 3 months, my pain scores dropped from 7/10 to 3/10, and my grip strength improved 40%. I'm still tracking.

### Example 3 — Data specificity redaction

**BEFORE (acceptable with verification, but tighten):**
> My morning HRV went from 38.4 on February 12, 2026 to 53.7 on June 23, 2026.

**AFTER (publication-ready):**
> My 7-day average morning HRV improved from 38 to 54 between February and June 2026.

### Example 4 — Brand name redaction

**BEFORE (forbidden):**
> I started Lexapro for anxiety.

**AFTER (permitted):**
> I started an SSRI for anxiety.

### Example 5 — Dosing protocol redaction

**BEFORE (forbidden):**
> I took 250mcg of BPC-157 subcutaneously 5 days per week.

**AFTER (permitted):**
> I ran a physician-supervised BPC-157 protocol with biomarker tracking throughout.

---

## How to apply the protocol in draft production

1. **Mavis produces draft** using the intake data + Dre's voice (per `stores/proof/README.md` Stage 3)
2. **Mavis runs the 13-item audit** automatically against the draft
3. **Any item fails** → Mavis flags for Dre review with specific redaction suggestions
4. **Dre reviews** the audit results + the draft
5. **Dre sends to person** for draft review (7-day window per consent pipeline)
6. **Person approves** → Mavis runs audit one more time before publication
7. **Final audit clean** → move to `approved/` + publish

**Time estimate:** 30-45 minutes of Mavis audit + 30-60 minutes of Dre review per case study.

---

## Edge cases + escalation rules

### Edge case 1 — Person requests to use real name + company publicly
- Explicit consent required in Section 8 of intake (Full name + role + company)
- Verify consent is unambiguous
- Default still goes to minimal disclosure unless explicit

### Edge case 2 — Person includes therapeutic-outcome language in their intake responses
- Auto-redact during draft production
- Don't ask the person to "tone it down" — just convert their language to data-trend language in the draft
- The published version may differ significantly from the person's own words, but it must be approved by them in the draft review stage

### Edge case 3 — Person withdraws after publication
- 24-hour removal SLA per consent pipeline
- Move file to `withdrawn/` with withdrawal date
- Remove from all published surfaces within 24 hours
- No "but this story is great" pushback — withdrawal is unconditional

### Edge case 4 — Person shares something during intake that wasn't in original consent scope
- Don't include it in the case study unless they explicitly expand the consent scope
- Surface it back to the person: "Hey, you shared X. That's interesting but outside our agreed scope. Want to expand consent to include it?"

---

## Why this protocol exists

Without structured redaction, the brand risks:
- Identifying people without their explicit consent (legal + reputational risk)
- Publishing therapeutic-outcome claims (FDA enforcement exposure under Objective Intent Doctrine)
- Scope creep (using a testimonial in a context the person didn't consent to)
- Lost credibility (if a story turns out to be embellished or unverifiable)
- Community trust erosion (if a member feels their story was misused)

This protocol makes case studies:
- **Compliant** — built-in 13-item audit
- **Respectful** — protects the person's identity and agency
- **Verifiable** — numbers are checked against original case
- **Scoped** — surface discipline prevents creep

---

*Last updated: 2026-06-24 (Live Execution pass)*
*Ship-ready: yes. Awaiting first real community member to consent + complete intake.*