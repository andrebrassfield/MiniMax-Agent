# Content Brief — 2026-06-16 18:38 CT

**Source file:** `03 Projects/Mavis EA Design/reports/2026-Q3-SMB-AI-Maturity-Report.md`
**Posts analyzed:** 10-page whitepaper (7 sections + appendix), freshly generated 2026-06-16 18:15 CT
**Bookmarks freshness:** fresh (generated today)
**Persona file:** loaded from `03 Projects/X-Content-Engine/agents/persona.md`
**Brain state before:** 15 hooks / 15 formats / 15 pain_points / 21 ideas (3 used, 18 pending)
**Brain state after:** 20 hooks / 20 formats / 20 pain_points / 24 ideas (3 used, 21 pending)

---

## Patterns appended to brain

### Hooks (5 new, all added — no duplicates)

All hooks extracted from whitepaper §1–§4. Key emotion theme: **fear + recognition**. The whitepaper's unit economics (the $876K/year missed-call math, the TikTok Shop penalty cliff) hit the fear axis hard. The FSM-layer revelation ("even ServiceTitan's own product can't write call notes") triggers recognition in anyone who owns one of these tools.

| # | Hook text (truncated) | Emotion | Whitepaper § |
|---|-----------------------|---------|-------------|
| H1 | "8 calls/day × $300/job × 365 = $876K/year..." | fear | §1.2, §4 |
| H2 | "TikTok Shop 2026 SLA: 4% LDR, 2.5% SFCR..." | fear | §1.1, §1.4 |
| H3 | "ServiceTitan's own voice agent FAQ (June 11, 2026): 'won't be able to add call notes...'" | recognition | §3.1 |
| H4 | "All 5 are wrappers at the FSM layer..." | defiance | §3.6 |
| H5 | "AI does not fix the system of record. AI exposes its tolerances." | clarity | §1.4 |

### Formats (5 new, all added — no duplicates)

Key structural pattern: **Vendor-Indictment + Audit-Drop hybrid**. The whitepaper uses vendor-self-citations as the primary evidence source, which is a format the persona has not yet produced. The Regulatory Cliff Drop and Audit Drop + Imperative Close are new structures not in the prior brain.

| # | Format name | Structure (truncated) | Whitepaper § |
|---|-------------|-----------------------|-------------|
| F1 | Regulatory Cliff Drop | "[Platform] [year] SLA: [threshold 1]..." | §1.1 |
| F2 | Audit Drop + Imperative Close | "I audited [N] tools. [Verdict]. [The fix]." | §3 |
| F3 | Vendor-Indictment Drop | "[Vendor]'s own [doc] ([date]): '[limitation quote]'" | §3.1 |
| F4 | Cost-Quantification Table | "[Line item] | Wrapper | True Agent |" | §4 |
| F5 | Structural Diagnosis + Pivot | "[Wrapper claim]. [System-of-record truth]. [Distinction]." | §1.4 |

### Pain Points (5 new, all added — no duplicates)

Key audience phrase (verbatim from whitepaper §1.4): **"AI does not fix the system of record. AI exposes its tolerances."** — this is the structural diagnosis that reframes the SMB's confusion about why their AI "isn't working."

| # | Exact audience language | Frequency | Whitepaper § |
|---|-------------------------|-----------|-------------|
| P1 | "missed 8 calls a day, $300 average job ticket, $876K a year burning" | 2 | §1.2 |
| P2 | "TikTok Shop 2026 SLA is 4% LDR and 2.5% SFCR, a merchant at 5% LDR on 10K orders/month is exposed to $2,500/month in penalties (10K × 5% × $5/order)" | 2 | §1.1 |
| P3 | "bought AI, still doing data entry" | 3 | §1.4 |
| P4 | "desktop applications do not have native webhooks, the system of record is built on a 1990s client-server model" | 2 | §1.2 |
| P5 | "AI does not fix the system of record, AI exposes its tolerances" | 2 | §1.4 |

---

## 3 Destroy or Defend scenarios (ideas_backlog, status: pending)

These are chief-prescribed templates — Scribe must rephrase in persona voice before drafting.

| # | Pillar | Hook (truncated) | Format | Whitepaper citation |
|---|--------|------------------|--------|---------------------|
| 1 | Pillar 2 — Trades / Missed Call | "8 calls/day × $300/job × 365 = $876K/year..." | Math-Problem Drop | §1.2, §4 |
| 2 | Pillar 1 — E-Commerce Logistics | "TikTok Shop 2026 SLA: 4% LDR, 2.5% SFCR, $5/late order..." | Regulatory Cliff + Math Drop | §1.1, §1.4 |
| 3 | Pillar 4 — Build Logs | "I audited 5 AI for SMB tools. All 5 are wrappers at the FSM layer..." | Audit Drop + Imperative Close | §3, §3.6 |

**Distribution note:** 1 Pillar 1, 1 Pillar 2, 1 Pillar 4. This is the chief's override of the standard P2/P5/P6 rotation. The Scribe should treat Pillar 4 voice-fit as the ceiling (the whitepaper is itself a Build Log; the persona's Pillar 4 posts historically outperform — 28 + 40 reposts on top two historical posts, per agency strategy briefing cited in whitepaper §6.1).

---

## Notes for the Scribe

1. **Pillar override active.** These 3 ideas are Pillar 1/2/4, not the standard P2/P5/P6 mix the persona typically favors. The chief has specified this mix. Do not default to Pillar 5 or 6 for these.
2. **Ideas are templates, not final drafts.** Each hook text is sourced from the whitepaper verbatim or near-verbatim. The Scribe must rephrase in Dre Builds voice (staccato, 3–5 sentences, dollar number first, imperative close). The whitepaper § citations are for verification — confirm numbers before drafting.
3. **Idea 1 (Pillar 2):** The $876K/year figure comes from §1.2 + §4 of the whitepaper. Confirm: 8 calls/day × $300/job × 365 days = $876,000. The "9.5x payback in 90 days" claim is implied by the §4 cost table ($1.28M lost → $22.5K True Agent cost) — confirm the math before using the "9.5x" framing.
4. **Idea 2 (Pillar 1):** The TikTok Shop SLA numbers (4% LDR, 2.5% SFCR, $5/late order, 31-day settlement hold) come from §1.1, sourced to Racklify (2026-03-19) — see Appendix §7.1, source #4. **Math correction (chief-fixed 2026-06-16 18:43 CT):** the correct figure for a 10,000 orders/month merchant at 5% LDR is **$2,500/month in late-order penalties** (10,000 × 0.05 × $5 = $2,500), not $500. The whitepaper §1.1 had a math error in its first draft; the chief has corrected the whitepaper (with errata note), the brief, and the brain entry for idea 2. **The Scribe should use $2,500/month as the dollar figure** in the post. The 1,000-orders/month merchant's $50 figure (1,000 × 0.05 × $5 = $50) was correct in both the whitepaper and the brief.
5. **Idea 3 (Pillar 4):** The "200 lines of Python + 30-second polling fallback" comes from §3 (ServiceTitan Voice Agent upgrade step 1). The §3.6 "Wrapper Tally" confirms "all 5 are wrappers at the FSM layer." Use the verbatim phrasing.
6. **Brain now has 21 pending ideas after this run.** The Scribe will flip the 3 new ones to "used" after drafting. The 18 pre-existing pending ideas stay pending for the next Scribe run.

---

## Notes for the chief

- **Brain hygiene flag:** none. 20 hooks, 20 formats, 20 pain_points, 24 ideas — all arrays are well below the 500-entry bloat threshold.
- **Prior ideas not overwritten.** The 18 pre-existing pending ideas remain pending. No deletion occurred.
- **3 ideas are Pillar 1/2/4 (chief override).** Standard rotation for future runs is P2/P5/P6 unless the chief specifies otherwise.
- **Validation needed before Scribe drafts Idea 2:** the "$500/month on 10K orders" math appears to be a transcription error in the brief text (whitepaper §1.1 calculates ~$2,500/month for 10K orders at 5% LDR × $5/order). The Scribe should verify the correct number before drafting. The whitepaper itself is the source of truth, not this brief.
- **Source file staleness:** not applicable — whitepaper generated today (2026-06-16 18:15 CT).

---

## Ledger entry

See `03 Projects/X-Content-Engine/briefs/_ledger.mdl` for the appended one-liner.
