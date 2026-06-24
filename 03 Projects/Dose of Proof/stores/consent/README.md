---
type: spec
asset: consent-tracking-system
status: ✅ LOCKED (2026-06-23)
purpose: Templates, follow-up cadence, storage protocol — pipeline ready when real people step forward
storage_location: 03 Projects/Dose of Proof/stores/consent/
---

# Consent Tracking System — Case Studies + Testimonials (LOCKED)

> Pre-built pipeline for tracking consent requests, follow-up cadence, storage protocol. The moment real community members step forward, the system is ready.

---

## The Pipeline Stages

### Stage 1 — Initial Outreach (Day 0)
- Dre sends the appropriate consent email template from `assets/emails/consent-requests.md`
- Email is logged in the consent tracker (see below)

### Stage 2 — First Follow-up (Day 7 if no reply)
- Light nudge: "Hey [Name], wanted to circle back on this. No pressure either way — if you'd rather not be quoted, that's totally fine."
- Logged in tracker

### Stage 3 — Second Follow-up (Day 21 if still no reply)
- Closer: "Hey [Name], I'm following up one more time on the case study / testimonial request. If I don't hear back by [date], I'll close this out and won't include your story."
- Final close-out logged

### Stage 4 — Consent Received (anytime in pipeline)
- Email reply with explicit consent → Stage 5
- Reply requesting draft review first → Stage 4b (Draft Review)

### Stage 4b — Draft Review (if requested)
- Dre sends draft copy using the person's story/quotes
- Person has 7 days to approve, request edits, or decline
- Logged in tracker

### Stage 5 — Final Approval
- Person approves draft → move to Stage 6
- Person requests edits → Dre revises, sends back for re-approval
- Person declines → close-out logged, no publication

### Stage 6 — Publication
- Story goes live on the specified surface (course sales page, email, etc.)
- Logged in tracker with publication date + URL

### Stage 7 — Withdrawal Right (ongoing)
- Person can request withdrawal of their story at any time
- 24-hour removal SLA
- Logged in tracker

---

## Storage Protocol

### Folder structure
```
03 Projects/Dose of Proof/stores/consent/
├── README.md                           # this spec
├── tracker.md                          # active consent tracker
├── approved/
│   ├── [person-slug]-consent.md        # written consent record
│   ├── [person-slug]-draft.md          # draft sent for review
│   └── [person-slug]-published.md      # publication record + URL
├── declined/
│   └── [person-slug]-declined.md       # decline record (no detail)
└── withdrawn/
    └── [person-slug]-withdrawn.md      # withdrawal record + removal date
```

### tracker.md (active pipeline)

```markdown
# Consent Tracker — Dose of Proof

## Active requests (in pipeline)

| Name | Role | Type | Date Sent | Stage | Next Action | Notes |
|------|------|------|-----------|-------|-------------|-------|
| [Mark] | [38, entrepreneur] | Case study | 2026-06-25 | Stage 1 | Follow-up Day 7 if no reply | — |
| [Sarah] | [42, athlete/coach] | Case study | 2026-06-25 | Stage 1 | Follow-up Day 7 | — |
| [James] | [34, tech founder] | Case study | 2026-06-25 | Stage 1 | Follow-up Day 7 | — |
| [Dr. X] | Upper cervical chiro | Testimonial | 2026-06-25 | Stage 1 | Follow-up Day 7 | Awaiting name confirmation |
| [Marcus T.] | Founder & CEO | Testimonial | 2026-06-25 | Stage 1 | Follow-up Day 7 | Awaiting identity confirmation |

## Approved + published

| Name | Surface | Published Date | URL | Withdrawal Status |
|------|---------|----------------|-----|-------------------|
| (empty — no approved stories yet) |

## Declined

(none)

## Withdrawn

(none)

## Last updated
2026-06-23
```

### Approved/[person-slug]-consent.md format

```markdown
# Consent Record — [Name]

## Basic info
- **Name:** [First name + last initial, e.g., "Mark R."]
- **Role / Title:** [38, entrepreneur]
- **Date of consent:** [YYYY-MM-DD]
- **Consent type:** Case study OR Testimonial

## Scope of consent
- [ ] First name + age + role only (no last name, no company)
- [ ] First name + age + role + company name (explicit)
- [ ] Full name + role + company (explicit)
- [ ] Specific numbers (HRV, biomarkers, dates) included
- [ ] Specific quote included
- [ ] Photo / video / scan included (if applicable)
- [ ] Anonymized cohort analysis opt-in

## Asset(s) consented for
- [ ] Course sales page (Proof section)
- [ ] Launch email (Email 7)
- [ ] Substack post
- [ ] Skool community announcement
- [ ] Other: [specify]

## Consent text (verbatim from email reply)

> [Verbatim copy of the person's consent reply]

## Sent by (Dre's email): [Dre's email address]
## Received: [YYYY-MM-DD HH:MM]

## Status
- [ ] Consent recorded
- [ ] Draft sent for review
- [ ] Draft approved
- [ ] Published
- [ ] Withdrawal right acknowledged (can withdraw at any time, 24-hour removal SLA)

## Compliance check
- [ ] No therapeutic-outcome language in the story
- [ ] No sourcing language
- [ ] "I'm still in this process" framing if applicable (Dre's case study template)
- [ ] First name only (unless explicit consent for full name)
- [ ] Numbers verified against original case (Dre to confirm)
```

---

## Email Templates (5 — locked in `assets/emails/consent-requests.md`)

1. **Template A — Mark (case study, age 38, entrepreneur)**
2. **Template B — Sarah (case study, age 42, athlete/coach)**
3. **Template C — James (case study, age 34, tech founder)**
4. **Template D — Doctor (testimonial 1, upper cervical specialist)**
5. **Template E — Marcus T. (testimonial 2, founder & CEO)**

**Priority order for sending (when real subjects emerge):**
1. Doctor (Template D) first — clinicians are time-constrained, fast yes/no
2. Marcus T. (Template E) second — peer-to-peer, fast turnaround
3. Mark / Sarah / James (Templates A/B/C) third — detailed case studies, more back-and-forth

---

## Follow-up Cadence

| Day | Action |
|-----|--------|
| Day 0 | Initial outreach (consent email template) |
| Day 7 | First follow-up if no reply (light nudge) |
| Day 21 | Second follow-up if still no reply (final close-out) |
| Day 35 | Close out, no further contact |
| Anytime | Person can withdraw → 24-hour removal SLA |

**No aggressive follow-up.** No "checking in" beyond Day 21. After Day 35, the lead is cold. If the person re-engages later, the pipeline can restart from Stage 1.

---

## Compliance Audit (Quarterly)

- [ ] All active consent records have valid email consent on file
- [ ] All published stories match the consent scope (no scope creep)
- [ ] All consent records have a "status" field filled in
- [ ] All withdrawal requests processed within 24 hours
- [ ] No published story contains therapeutic-outcome claims
- [ ] No published story contains sourcing language

---

## When Real People Step Forward

The moment a community member says "Hey, I'd be open to sharing my story" in the Skool Inner Circle or via DM:

1. **Dre responds** with the appropriate consent email template (A/B/C for case study, D/E for testimonial)
2. **Dre logs** the request in `tracker.md`
3. **Pipeline runs** per the stages above (initial outreach → follow-ups → consent → draft review → publication)
4. **Compliance audit** quarterly by Mavis

---

## Why This System Matters

Without a structured consent pipeline, the brand risks:
- Using someone's story without written permission (FTC + reputational risk)
- Scope creep (using a testimonial in a context the person didn't consent to)
- Compliance drift (therapeutic-outcome language creeping into published stories)
- Lost testimonials (people who would have said yes but didn't get a clean follow-up)

This system makes the consent process:
- **Auditable** — every step logged with timestamps
- **Respectful** — clear cadence, no aggressive follow-up
- **Compliant** — built-in compliance checks at each stage
- **Scalable** — when 10+ people step forward, the pipeline doesn't break

---

## Quick-Start When First Real Subject Emerges

1. Open `tracker.md` and add the row
2. Open the appropriate template from `assets/emails/consent-requests.md`
3. Personalize: real name + role + specific story elements
4. Send from Dre's email
5. Log the send date in the tracker
6. Set follow-up reminder (Day 7) on Dre's calendar
7. The pipeline runs from here

Total time per new subject: ~10-15 minutes to set up + send.