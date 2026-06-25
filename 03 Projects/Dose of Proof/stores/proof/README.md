---
type: spec
asset: proof-infrastructure
status: ✅ FINAL (locked 2026-06-24, ready before first real subject)
purpose: structural foundation for real case studies + testimonials — populated and ready the moment the first community member steps forward
storage_location: 03 Projects/Dose of Proof/stores/proof/
companion_to: stores/consent/ (the consent pipeline that this feeds into)
---

# Proof Infrastructure — Dose of Proof

> The structural foundation for real case studies and testimonials. Pre-built so the moment a community member steps forward with consent, the system is ready to capture, anonymize, redact, and publish.

**Why this matters:** The brand's "Proof Section" on Substack + course sales pages + launch assets needs real case studies. The framework asks "show me the data, show me the before and after." Real case studies are how the brand delivers that. But the capture, anonymization, redaction, and publication process must be airtight before the first real person steps forward.

---

## Folder structure

```
03 Projects/Dose of Proof/stores/proof/
├── README.md                           ← this spec
├── intake-template.md                  ← symptom inventory + imaging/labs checklist
├── redaction-protocol.md               ← anonymization + redaction rules
├── proof-section-layout.md             ← Substack About page + sales asset layout
├── drafts/                             ← in-progress case study drafts (per person)
│   └── [person-slug]-draft.md
├── approved/                           ← published case studies (per person)
│   └── [person-slug]-published.md
├── anonymized-cohort/                  ← aggregate cohort analysis (no individual IDs)
│   └── [topic]-cohort-analysis.md
└── withdrawn/                          ← withdrawn stories (24h removal SLA)
    └── [person-slug]-withdrawn.md
```

---

## The 5-stage proof pipeline

| Stage | What happens | Output location |
|-------|--------------|-----------------|
| 1. Intake | Community member steps forward → Dre sends consent email (from `assets/emails/consent-requests.md`) + intake form (from `intake-template.md`) | `stores/consent/tracker.md` |
| 2. Consent received | Person replies with explicit consent → Dre records in `stores/consent/approved/[slug]-consent.md` | consent record |
| 3. Draft production | Mavis produces draft case study using intake data + Dre's voice; passes compliance audit | `stores/proof/drafts/[slug]-draft.md` |
| 4. Draft review | Person reviews draft (7-day window per consent pipeline) | tracked in consent record |
| 5. Publication | Approved draft moves to `stores/proof/approved/[slug]-published.md` + goes live on specified surface | Proof Section + sales assets + Substack |

---

## What this infrastructure enables

The Proof Section on the Substack About page + future course sales page needs:
- 3-5 anonymized case studies in the first 90 days
- 2-3 named (consented) testimonials from clinicians + peer operators
- 1 cohort analysis showing aggregate biomarker trends across the community (no individual IDs)
- All publications must pass the redaction protocol + compliance audit

The infrastructure is ready before the first real subject arrives. When someone says "I'd be open to sharing my story" in the Skool Inner Circle or via DM, the pipeline captures them cleanly.

---

## Sub-pipeline: Anonymized cohort analysis

In addition to individual case studies, the brand can publish anonymized cohort analyses:
- "Across 47 Inner Circle members tracking morning HRV over 6 months, the average improvement was X%"
- "Of 23 community members on the 5-biomarker protocol, Y% showed improvement in Z biomarker"

**Critical rule:** Cohort analyses use only **explicit opt-in** data (separate consent field on intake form). No scraping of community data without explicit consent. The cohort analysis template lives in `anonymized-cohort/[topic]-cohort-analysis.md`.

---

## Compliance posture (carries from locked compliance posture)

Every case study, testimonial, and cohort analysis must pass:

- ✅ No sourcing language (no peptide supplier names)
- ✅ No therapeutic-outcome language ("I recovered from X" doesn't ship; "my biomarkers trended from X to Y" does)
- ✅ No un-redacted third-party data (everything redacted per `redaction-protocol.md`)
- ✅ First name + age + role only (unless explicit consent for full name + company)
- ✅ Numbers verified against original case (Dre to confirm)
- ✅ "I'm still in this process" framing when Dre is the subject (Dre's case study template)
- ✅ "I'm not a doctor. I don't prescribe" disclaimer on every surface
- ✅ Withdrawal right acknowledged (24-hour removal SLA, person can withdraw at any time)
- ✅ Consent scope strictly followed (no scope creep — if person consented to sales page only, doesn't appear on launch email)

---

## Quick-start when first real subject emerges

1. Open `intake-template.md` and send to the person
2. Open `stores/consent/README.md` and follow the 5-stage consent pipeline
3. When consent received, open `stores/proof/drafts/[slug]-draft.md` and produce the case study
4. Pass through `redaction-protocol.md` audit
5. Send draft for review (7-day window per consent pipeline)
6. On approval, move to `stores/proof/approved/` + publish to specified surface
7. Add to Proof Section layout per `proof-section-layout.md`

Total time per case study: ~2-3 hours of Mavis + Dre collaboration.

---

## What this infrastructure does NOT do

- ❌ It does not create fake case studies (only real people with explicit consent)
- ❌ It does not use community data without explicit consent
- ❌ It does not allow scope creep (consent is for specific surfaces)
- ❌ It does not produce therapeutic-outcome language (numbers + trends only)

The Proof Section is built on real people with real consent. The infrastructure makes the capture auditable.

---

*Last updated: 2026-06-24 (Live Execution pass)*
*Ship-ready: yes. Awaiting first real community member to step forward.*