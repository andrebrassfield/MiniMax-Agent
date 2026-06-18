# ROI Math — client-pov-tracker

The whitepaper §4 math defaults + scaling per client. The
dollar anchor for the Target ROI table (Section 3 of the
roadmap).

## Whitepaper §4 defaults (the anchor numbers)

| Client archetype | Default math | Annual impact |
|---|---|---|
| 2-truck HVAC shop, $300/job | 8 missed calls/day × $300 × 365 | **$876K/year** |
| 10K orders/month TikTok Shop, 5% LDR | $500/month late-order penalties + 31-day settlement hold + 10% order cap | **$6K/year penalties + ~$310K working capital hold** |
| Single-truck plumbing shop, $250/job | 5 missed calls/day × $250 × 365 | **$456K/year** |
| $40K/mo Shopify, 3% oversell rate | 3% × $40K × 12 = $14.4K/year oversell cost | **$14.4K/year** |
| 9-to-5 knowledge worker, 30% time on admin | 30% × 2080 hours × $50/hr fully-loaded | **$31K/year** |

The defaults are the canonical anchor. The roadmap's
Section 3 may override with client-specific numbers (the
override is cited in the Source column).

## Capture assumption (per whitepaper §4 footnote)

Realistic capture: 30-60% of the lost revenue.

| Case | Capture % | Use when |
|---|---|---|
| Conservative | 30% | Worst-case scenario; first-time client; conservative operator |
| Base | 40% | Default for most clients |
| Aggressive | 60% | Experienced client; operator confident in the install |

The roadmap's Section 3 must state the case used.

## Payback period

30-90 days for any client doing $300K+ in annual revenue
(per whitepaper §4).

| Client revenue | Payback |
|---|---|
| < $100K | Not a fit for the install (cost exceeds benefit) |
| $100K - $300K | 60-90 day payback |
| $300K - $1M | 30-60 day payback |
| $1M+ | 30-day payback or less |

The roadmap's Section 3 should state the payback period
based on the client's revenue tier.

## Scaling per client

If the client has provided their own numbers (call volume,
job ticket, order volume, after-hours %), override the
whitepaper defaults. The override is logged in the Source
column.

### Scaling formula: missed-call revenue leak

```
annual_leak = missed_calls_per_day × average_job_ticket × 365
```

Where:
- `missed_calls_per_day` = whitepaper default 8 (trades) or
  client-specific
- `average_job_ticket` = whitepaper default $300 (trades) or
  client-specific
- `365` = days per year

### Scaling formula: e-com oversell cost

```
annual_oversell = monthly_revenue × oversell_rate × 12
```

Where:
- `monthly_revenue` = client-specific
- `oversell_rate` = whitepaper default 3% (Shopify) or
  client-specific
- `12` = months per year

### Scaling formula: knowledge worker time-saved

```
annual_value = hours_per_week_saved × fully_loaded_hourly_rate × 50
```

Where:
- `hours_per_week_saved` = client-specific (or whitepaper
  default 30% of admin time)
- `fully_loaded_hourly_rate` = client-specific
- `50` = working weeks per year

## The Target ROI table (Section 3 of the roadmap)

The table structure:

| Line item | Wrapper-tier (current state) | Dre Builds True Agent | Source |
|---|---|---|---|
| Missed-call revenue leak | $[X]/year | $0 (covered) | whitepaper §4 |
| After-hours revenue leak | $[X]/year | $0 (covered) | whitepaper §4 |
| ... (any client-specific line items) | | | |
| **Net annual impact** | **–$[X]** | **–$[X] net cost** | |
| **Dre Builds ROI (vs wrapper)** | — | **+$[X]/year** | |

Every line item must have a Source citation. If the source
is client-provided data, name the data ("client call volume
report, 2026-06-01").

## What this math is NOT

- **Not a guarantee.** The math is the base case. Actual
  results depend on install quality + client cooperation +
  market conditions. The base case is the planning number,
  not a promise.
- **Not the only line item.** Other revenue leaks exist
  (e.g., bad reviews from missed calls, employee turnover
  from overwork). The roadmap's Section 3 includes
  client-specific line items as the operator identifies
  them.
- **Not the agency's billing.** The agency bills on outcomes
  (per whitepaper §2.4), not on the projected ROI. The ROI
  is the value to the client; the billing is the agency's
  capture of that value.

## Cross-reference

- `references/agentic-standard.md` — the 4 criteria that
  determine whether the install produces the projected ROI
- `references/blueprint-phases.md` — the 4-week install
  that produces the value
- `references/roadmap-template.md` — Section 3 template
- The 2026 SMB AI Maturity Report §4 — the canonical source
- The 2026 SMB AI Maturity Report §2.4 — outcome-pricing
  commitment (the agency's capture of the value)
