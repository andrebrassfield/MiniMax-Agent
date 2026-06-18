# Agentic Standard — client-pov-tracker

The 4 technical criteria the install must satisfy. Per
whitepaper §2. The criteria are quoted, then applied
specifically to the client's stack in Section 2 of the
roadmap.

## The 4 criteria

| Criterion | Definition | Why it matters |
|---|---|---|
| **Idempotency** | The agent must not produce duplicate state on duplicate inputs (e.g., duplicate-call within 100ms must not create duplicate jobs in the FSM). | Without this, the agent creates more work than it saves. |
| **Real-time sync** | State changes in the agent's domain must propagate to the FSM / canonical store within an SLA (e.g., 60 seconds). | Without this, the dispatch board lags, and the operator's morning is spent reconciling. |
| **FSM-native** | The agent writes to the client's actual FSM (ServiceTitan / Jobber / Housecall Pro / FieldEdge) using canonical fields, not a parallel store. | Without this, the agent's data is a shadow system; the client's actuals are wrong. |
| **Outcome-priced** | The agency bills on outcomes, not inputs. The voice-agent usage fee is the agency's cost, not the client's. | Without this, the client pays for AI that may not produce ROI. |

## How the criteria are applied to a client

For each criterion, Section 2 of the roadmap states what
the criterion means for THIS client's stack. The pattern:

| Criterion | Applied to client |
|---|---|
| **Idempotency** | "Duplicate-call within 100ms must not create duplicate jobs in [the client's FSM — e.g., ServiceTitan]." |
| **Real-time sync** | "[Agent action — e.g., voice agent booking] must appear on the [client's dispatch board — e.g., ServiceTitan] within [SLA — e.g., 60 seconds]." |
| **FSM-native** | "The client uses [FSM — e.g., Jobber]. The agent must populate [canonical fields — e.g., customer name, address, job type, scheduled slot]." |
| **Outcome-priced** | "The agency bills on [outcome — e.g., booked jobs that complete within 30 days]. The voice-agent usage fee is the agency's cost, not the client's." |

The criteria are not generic ("we value idempotency") — they
are specific ("duplicate-call within 100ms must not create
duplicate jobs in ServiceTitan"). The specificity is the
load-bearing element.

## The FSM-specific canonical fields (per FSM)

Different FSMs have different canonical fields. The agent
must populate the right ones for the client's FSM:

| FSM | Canonical fields |
|---|---|
| **ServiceTitan** | Customer ID, Job ID, Appointment Slot, Technician ID, Job Type |
| **Jobber** | Client ID, Job ID, Scheduled Start, Property Address, Line Items |
| **Housecall Pro** | Customer ID, Job ID, Appointment Window, Service Type, Total Estimate |
| **FieldEdge** | Customer ID, Work Order ID, Scheduled Date, Technician, Job Description |

If the client uses a different FSM, the operator specifies
the canonical fields in Section 2.

## What this standard is NOT

- **Not a feature checklist.** The criteria are technical
  tests, not feature names. "Idempotency" is not "has a
  retry mechanism" — it's "duplicate input does not produce
  duplicate state."
- **Not a one-time pass.** The criteria apply to every
  install, every update, every new agent the agency
  deploys. Each new agent is re-tested against the 4
  criteria.
- **Not the whitepaper itself.** The whitepaper §2 is the
  source; the roadmap's Section 2 is the per-client
  application. Quote the whitepaper, then apply.

## Cross-reference

- `references/blueprint-phases.md` — the 4-week install
  phases that implement the criteria
- `references/roi-math.md` — the §4 math that quantifies
  the criteria's value (in dollars)
- `references/roadmap-template.md` — Section 2 template
  (where these criteria are applied)
- The 2026 SMB AI Maturity Report §2 — the canonical source
- The 2026 SMB AI Maturity Report §2.4 — the outcome-pricing
  commitment specifics
