# Roadmap Template — client-pov-tracker

The 7-section roadmap. The load-bearing structure for the
per-client POV artifact. The chief fills this template with
client-specific data from the local-audit briefs + the
whitepaper.

## File path

`03 Projects/Clients/[ClientName]/pov-roadmap.md`

One file per client. Created once (per the skill's intent —
the POV is the kickoff artifact, not a living document).

## Frontmatter

```markdown
---
client: [ClientName]
city: [City, ST]
niche: [Niche]
generated: [YYYY-MM-DD HH:MM CT]
generator: client-pov-tracker (Mavis, chief-of-staff)
whitepaper: 03 Projects/Mavis EA Design/reports/2026-Q3-SMB-AI-Maturity-Report.md
local_audits_ingested: [list of briefs file paths]
agentic_standard: §2 of the whitepaper (idempotency / real-time sync / FSM-native / outcome-priced)
blueprint_phases: §5 of the whitepaper (4-week install)
outcome_pricing: [% of captured revenue, default 10-20%]
install_start: [YYYY-MM-DD if known]
---
```

## Section template

```markdown
# POV Roadmap — [ClientName] — [City, ST] — [Niche] — [YYYY-MM-DD]

> **What this is.** Dre Builds' point-of-view on what we are
> building, why, and how we measure success. Single document.
> Kickoff artifact. Cited throughout to the SMB AI Maturity
> Report and the underlying local-audit intelligence.

---

## 1. The Friction (what we are solving)

[Per-competitor Friction Signals categorized by tier. Pulled
from the local-audit briefs. Each tier is a section.]

### Tier 1 — High-urgency revenue leaks

[List each Tier 1 signal with: business name (if from audit),
the signal itself, the revenue impact estimate (e.g., "8
missed calls/day × $300/job = $876K/year per the whitepaper
§4").]

### Tier 2 — Medium-leverage friction

[Same format.]

### Tier 3 — Low-leverage friction (noted, not prioritized)

[Same format.]

---

## 2. The Agentic Standard (how the fix must satisfy technical criteria)

[For each of the 4 Agentic Standard criteria, state what it
means for THIS client's stack. The criteria are the whitepaper's
§2 — quoted, then applied.]

- **Idempotency:** [specific test for this client's FSM — e.g.,
  "duplicate-call within 100ms must not create duplicate jobs
  in ServiceTitan."]
- **Real-time sync:** [specific SLA — e.g., "voice agent
  booking must appear on the ServiceTitan dispatch board within
  60 seconds."]
- **FSM-native:** [which FSM the client uses — Jobber,
  ServiceTitan, Housecall Pro, FieldEdge — and what canonical
  fields the agent must populate.]
- **Outcome-priced:** [the agency's billing model for this
  client — the agency bills on booked jobs that complete
  within 30 days; the voice-agent usage fee is the agency's
  cost, not the client's.]

---

## 3. Target ROI (the math)

[The dollar impact, anchored to whitepaper §4. If the client
has provided their own call volume, job ticket, or after-hours
%, override the whitepaper defaults with the client-specific
numbers.]

| Line item | Wrapper-tier (current state) | Dre Builds True Agent | Source |
|---|---|---|---|
| Missed-call revenue leak | $[X]/year | $0 (covered) | whitepaper §4 |
| After-hours revenue leak | $[X]/year | $0 (covered) | whitepaper §4 |
| ... (any client-specific line items) | | | |
| **Net annual impact** | **–$[X]** | **–$[X] net cost** | |
| **Dre Builds ROI (vs wrapper)** | — | **+$[X]/year** | |

**Realistic capture assumption:** 30–60% of the lost revenue
(per whitepaper §4 footnote). Conservative case: 30%. Base
case: 40%. Aggressive case: 60%.

**Payback period:** 30–90 days for any client doing $300K+ in
annual revenue (per whitepaper §4).

---

## 4. The Blueprint (what we are building)

[Per Blueprint phase from whitepaper §5: the deliverable, the
week, what the client sees. Full phase details in
`blueprint-phases.md`.]

### Phase 1 — Baseline Audit (Week 1)
- Deliverable: 1-page baseline doc with the 5 measurement numbers.
- Client sees: the baseline doc + a calibration call to confirm
  the numbers.

### Phase 2 — Voice Path (Week 2)
- Deliverable: working inbound voice path with idempotency +
  real-time sync + FSM-native write-back.
- Client sees: 5+ test calls, the agent's call outcomes in the
  FSM, the 5 numbers re-measured at Day 14.

### Phase 3 — Inventory/Ops Path (Week 3, e-com clients only)
- Deliverable: inventory reconciliation middleware (Shopify /
  TikTok Shop / Amazon).
- Client sees: daily inventory confidence report.

### Phase 4 — Outcome Loop (Week 4)
- Deliverable: 30-day retrospective + outcome invoice (agency
  billed on booked jobs that complete within 30 days) + 90-day
  forward plan.
- Client sees: ROI statement, the 5 numbers trended over 30
  days, the 90-day plan.

---

## 5. The 5 Measurement Numbers (baseline)

[From the Forbes/QuickBooks dissection cited in whitepaper
§5.1. The baseline is the agency's pre-install reference. The
30-day re-measure is the agency's success/failure indicator.]

1. **Time per task** (in seconds, stopwatch, baseline vs
   AI-assisted).
2. **Output quality** (edit rate on AI-generated content; 80%
   needs minor or no edits = pass).
3. **Revenue per AI-supported activity** (revenue from
   AI-drafted campaigns vs human-drafted).
4. **Error rate** (data-entry errors before vs after AI).
5. **Tool cost vs value delivered** (the dollar ratio of AI
   subscriptions to documented value).

---

## 6. The Outcome-Pricing Commitment

[From whitepaper §2.4. The agency bills the client on
outcomes, not inputs. The exact % is the `outcome_pricing`
field in the frontmatter. The agency's commitment: if the
30-day ROI is negative, the agency eats the cost of the
build.]

---

## 7. Caveats and open questions

[Anything that the local-audit data didn't resolve, anything
the client needs to confirm, any staleness warnings on the
source data, any novel frictions that don't fit the Friction
Filter taxonomy.]

---

## Appendix — sources

[List of local-audit briefs ingested, the whitepaper, the
persona, the client-specific data the operator provided.]
```

## Per-section content discipline

- **Section 1 (Friction):** every signal must come from a
  real local-audit brief. Citation pattern: "[business name
  if from audit], the signal itself, the revenue impact
  estimate." If the signal is novel (not in the Friction
  Filter taxonomy), flag in Section 7.
- **Section 2 (Agentic Standard):** must be applied
  specifically to THIS client's stack, not generic. The FSM
  name + the canonical fields + the SLA must be specific.
- **Section 3 (Target ROI):** the table must have ≥3 line
  items. Every number traces to whitepaper §4 OR to
  client-provided data (cited in the Source column).
- **Section 4 (Blueprint):** every Tier 1 friction must map
  to a Blueprint phase. If a friction has no phase, flag in
  Section 7.
- **Section 5 (5 Numbers):** all 5 numbers must be present.
  The baseline is the agency's pre-install reference.
- **Section 6 (Outcome-Pricing):** the commitment is
  stated. The 30-day negative-ROI = agency eats cost clause
  is included.
- **Section 7 (Caveats):** non-empty if any audit was >90
  days stale, if any novel friction was found, or if any
  client-specific data is missing.
