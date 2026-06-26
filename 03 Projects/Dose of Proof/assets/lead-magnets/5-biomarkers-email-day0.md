---
title: 5 Biomarkers Lead Magnet — Email Welcome Sequence (Day 0)
type: email-sequence
asset_id: lm-5biomarkers-email-day0-v1
status: DRAFT — pending Dre review + Substack automation wiring
date: 2026-06-26
target_surface: Substack automated welcome email (send IMMEDIATELY on opt-in)
voice_locked: source/2026-06-23-brand-voice.md
compliance_locked: compliance/compliance-remediation-summary.md
sequence_position: 1 of 7 (Day 0)
companion_assets: 5-biomarkers-guide.md (PDF attached)
---

# Email Welcome Sequence — Day 0 (immediate delivery)

## Email metadata

- **From:** Dre (doseofproof@substack.com)
- **To:** new-subscriber@doseofproof.substack.com (merge tag: [First Name])
- **Subject:** Your 5 Biomarkers PDF is inside
- **Pre-header:** Plus what to expect from Dose of Proof over the next 2 weeks
- **Send cadence:** Immediate on Substack opt-in (delay = drop in engagement)
- **Attachment:** 5-biomarkers-guide.pdf (the lead magnet)
- **Companion link:** Printable tracking template (link to landing page or hosted PDF)

---

## Email body

### Above the fold

Hey [First Name],

Here's your PDF: **"The 5 Biomarkers That Actually Moved the Needle in My CCI + MCAS Recovery (And the Ones Most Doctors Ignore)."**

[** Download the PDF **]

Inside: the five markers I track daily or weekly (HRV, TyTron scans, tryptase + urine MCAS mediators, ESR + CRP + symptoms, Vitamin D + Magnesium), why each one matters, what improved for me (with specific numbers), and how to test for them.

This is the first step in the PCAC framework — Proof-Centered Approach to Craniocervical + Autoimmune Chaos. Show me the data before you change anything.

### What to do with the PDF

1. **Read Section 1 first** — "The Problem with Fragmented Data." If you've ever been told "your labs are normal" while feeling like shit, this is for you.
2. **Skim Section 2** — the five biomarkers. Don't try to memorize. Just notice which ones feel most relevant to your case.
3. **Print Section 4 + the tracking template** — the printable one-pager. Start your daily log tomorrow morning. Morning HRV, guarding score, flushing count, heat count, sleep. Two minutes. That's it.
4. **Talk to your physician** — bring the PDF to your next appointment. Ask which of these labs make sense for your case. The point isn't to self-diagnose. The point is to walk in with a better conversation than "I just feel off."

### What to expect over the next 2 weeks

I'll send 6 more emails. Some are about my story. Some are about the framework. Some are about the upcoming FDA PCAC meeting on July 23 and what it means for the biohacking community.

No daily spam. No fake scarcity. No "limited spots." Just the raw updates from my own adjustments and labs, plus the framework I'm building in public.

### A note on what this isn't

I want to be straight with you about what the PDF isn't:

- It's not a dosing protocol. I don't tell you what to take or how much. Those decisions are between you and your physician.
- It's not a sourcing funnel. I don't sell compounds and I don't facilitate sourcing.
- It's not a treatment plan. It's observational data from one case, plus the structure I built to track it.

What it is: a way to start building your own proof system — the kind of data that turns "your labs are normal" into a conversation your doctor can actually work with.

### If you want the bigger framework

If you want the early-bird pricing on the Dose of Proof Protocol course (the PCAC framework, operationalized) when it opens in a few weeks — just stay subscribed. You'll get the link first.

### Closing anchor

I'm still in this process myself. I'll be transparent with you the whole way.

Talk soon,
Dre

---

## Compliance footer (Substack template — required on every email)

> This content is for educational and informational purposes only. It is not medical advice. Always consult your physician before starting, changing, or stopping any protocol. The framework teaches you to read your own data; the protocol decisions are yours and your doctor's.

---

## Sequence notes for Dre (editorial)

- **Send IMMEDIATELY** on Substack opt-in. Delay = drop in engagement. Substack handles automation.
- **"[First Name]"** merge tag is standard Substack. If merge fails, drop it and address as "Hey there."
- **Download link** points to PDF hosted on Substack (or CDN URL).
- **Attachment** is optional — many Substack users prefer link over attachment for deliverability. Test both.
- **Companion printable template** is a separate asset at `assets/lead-magnets/5-biomarkers-tracking-template.md`. Link from email body or landing page.
- **Email 2 (Day 1):** origin story short version (already drafted in `specs/copywriting-v2.md` Section 3.1)
- **Email 3 (Day 3):** biomarker deep-dive (one biomarker per email)
- **Email 4 (Day 5):** PCAC framework introduction — Dre's exact language from `source/2026-06-23-brand-voice.md` Section 5. This is the brand voice anchor.
- **Email 5 (Day 7):** terrain layers (minerals, redox, mold context) — extends the PDF Section 3
- **Email 6 (Day 10):** tracking template walkthrough + how to talk to your physician about the labs
- **Email 7 (Day 14):** soft pitch for the Dose of Proof Protocol course (already drafted in `specs/copywriting-v2.md`)

> **Editorial discipline (Dre polish flag):** Every email in the Day 1 → Day 14 sequence must preserve "My Body, Not Yours" first-person observational framing. If any draft line drifts toward directive language (see `scripts/dop_compliance.py` `[IP-001]` through `[IP-005]` patterns for what counts as prescriptive), rewrite as observational ("here is what I tracked" / "here is what my data showed" / "talk to your physician about whether this pattern fits your case"). Run the 8-item compliance audit (`scripts/dop_compliance.py`) on each email before send.

## "I'm still in this process" anchor placement

The brand voice anchor ("I'm still in this process") appears in:
- Closing of the email body (above compliance footer)
- Email 4 (PCAC framework introduction) — full paragraph
- Email 7 (course soft pitch) — closing line

This is non-negotiable. It's the brand voice differentiator. Do not soften it.

---

## Compliance verification — Day 0 email

| Check | Status | Notes |
|---|---|---|
| No prescriptive-dose language (`[IP-001]` through `[IP-005]`) | ✅ | "Talk to your physician about what makes sense" |
| No sourcing links (no banned-vendor channels per `[BP-013]` through `[BP-016]`) | ✅ | No external links except Substack + PDF |
| No testimonials adopting efficacy claims | ✅ | No third-party quotes |
| No fake scarcity / "limited spots" | ✅ | Explicit "no fake scarcity" in body |
| Single CTA (Substack or PDF download) | ✅ | Substack opt-in is implicit; no competing CTA |
| "My Body, Not Yours" framing throughout | ✅ | First-person observational throughout |
| Banned-phrase check (`[BP-001]` through `[BP-012]`) | ✅ | Zero matches per `dop_compliance.py` regex |
| Exclamation marks ≤3 | ✅ | Zero in this email |
| Compliance footer present | ✅ | Bottom of email |
| Brand voice anchor ("I'm still in this process") present | ✅ | Closing line |

---

*Day 0 email complete. Aligned with `assets/emails/substack-welcome-1.md` (locked 2026-06-23) + new 5 Biomarkers lead magnet positioning. Voice + compliance verified.*