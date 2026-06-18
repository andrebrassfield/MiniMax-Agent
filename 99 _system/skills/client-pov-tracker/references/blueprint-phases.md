# Blueprint Phases — client-pov-tracker

The 4-week install phases from whitepaper §5. The
operational response to the Friction Filter (Tier 1
frictions map to specific phases).

## Phase 1 — Baseline Audit (Week 1)

**Deliverable:** 1-page baseline doc with the 5 measurement
numbers.

**Client sees:** the baseline doc + a calibration call to
confirm the numbers.

**What the agency does:**
- Run the `vault-30day-auditor`-style scan on the client's
  current operations
- Measure the 5 numbers pre-install (time per task, output
  quality, revenue per AI-supported activity, error rate,
  tool cost vs value delivered)
- Document the baseline in a 1-page report
- Schedule a 30-min calibration call with the client to
  confirm the numbers

**Maps to which frictions:** none (Phase 1 is the
"before" snapshot, not an intervention)

## Phase 2 — Voice Path (Week 2)

**Deliverable:** working inbound voice path with idempotency
+ real-time sync + FSM-native write-back.

**Client sees:** 5+ test calls, the agent's call outcomes
in the FSM, the 5 numbers re-measured at Day 14.

**What the agency does:**
- Stand up a voice agent (Vapi, Synthflow, Bland) wired to
  the client's FSM (ServiceTitan / Jobber / Housecall Pro)
- Test 5+ inbound calls end-to-end
- Verify idempotency (duplicate-call within 100ms → no
  duplicate jobs)
- Verify real-time sync (agent action appears in FSM within
  SLA)
- Re-measure the 5 numbers at Day 14

**Maps to which frictions:**
- Phone-only after-hours (Tier 1)
- No 24/7 web chat (Tier 1)
- "Call us for a quote" only (Tier 1)
- No instant-booking calendar (Tier 1)

## Phase 3 — Inventory/Ops Path (Week 3, e-com clients only)

**Deliverable:** inventory reconciliation middleware
(Shopify / TikTok Shop / Amazon).

**Client sees:** daily inventory confidence report.

**What the agency does:**
- Stand up inventory reconciliation (Shopify Admin API +
  Node.js middleware + Postgres ledger, or similar)
- Daily inventory confidence report emailed to the client
- Cross-channel sync verified (Shopify ↔ TikTok Shop ↔
  Amazon)

**Maps to which frictions:**
- Inventory sync failures (Tier 1, e-com clients only)
- TikTok Shop late-delivery rate (Tier 1, TikTok Shop
  merchants)

**Skip if:** the client is trades-only (no e-commerce). The
phase is conditional.

## Phase 4 — Outcome Loop (Week 4)

**Deliverable:** 30-day retrospective + outcome invoice
(agency billed on booked jobs that complete within 30 days)
+ 90-day forward plan.

**Client sees:** ROI statement, the 5 numbers trended over
30 days, the 90-day plan.

**What the agency does:**
- Run the 30-day retrospective (re-measure the 5 numbers,
  compute the ROI)
- Issue the outcome invoice (per whitepaper §2.4 — the
  agency bills on outcomes, not inputs)
- Draft the 90-day forward plan (what the agency will
  continue to do, what new frictions to address)
- If 30-day ROI is negative: agency eats the cost of the
  build (per whitepaper §2.4 outcome-pricing commitment)

**Maps to which frictions:**
- Stale site / no reviews / no FAQ (Tier 2) — the
  retrospective's content addresses these
- Outcome loop is the measurement phase for all prior
  phases

## Per-phase commitment language

For each phase, Section 4 of the roadmap states:
- Deliverable (one line)
- What the client sees (one line)
- Which frictions the phase closes (table of signals)

The blueprint is not a generic 4-week plan — it's the
specific install that closes the specific frictions
identified in Section 1.

## The conditional Phase 3

Phase 3 is conditional on client type:
- **Trades-only client:** skip Phase 3
- **E-com-only client:** Phase 3 is the primary install;
  Phase 2 is a smaller voice component for customer
  support
- **Trades + e-com (rare):** both Phase 2 and Phase 3 run
  in parallel; the 4-week timeline extends to 5-6 weeks

## Cross-reference

- `references/agentic-standard.md` — the 4 criteria each
  install must satisfy
- `references/roi-math.md` — the §4 math that prices the
  blueprint in dollars
- `references/roadmap-template.md` — Section 4 template
- The 2026 SMB AI Maturity Report §5 — the canonical source
