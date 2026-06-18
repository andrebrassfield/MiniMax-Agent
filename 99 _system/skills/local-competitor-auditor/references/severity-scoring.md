# Severity Scoring — local-competitor-auditor

The per-competitor severity scoring rules. The auditor
assigns a 1-5 score to each competitor based on the
PRESENT/ABSENT tally of Tier 1 + Tier 2 friction signals.

## Scoring rubric

| Tier 1 count | Tier 2 count | Severity | Description |
|---|---|---|---|
| 1-2 | 0-1 | **3/5** | The business is leaking after-hours revenue |
| 3-4 | 0-1 | **4/5** | The business is bleeding revenue. Voice-AI + instant-booking install would close most gaps |
| Any | 2+ | **5/5** | The business is the perfect prospect. A single 4-week install would 2-3x their lead capture |
| 0 | 0-1 | **2/5** | The business is operating OK; not a hot prospect |
| 0 | 0 | **1/5** | The business is already operating at a high level; not a prospect |

## How to apply the rubric

1. Tally PRESENT Tier 1 signals per competitor
2. Tally PRESENT Tier 2 signals per competitor
3. Match the (Tier 1, Tier 2) combination to the rubric
   above
4. Assign the severity score (3/5, 4/5, 5/5, 2/5, or 1/5)

The severity score is the operator's filter: 4/5 and 5/5
are the hot prospects for sales outreach; 1/5 and 2/5 are
not prospects.

## The "mixed signals" case

Some businesses have friction signals present but are
clearly already investing in AI (chat widget, modern site).
For these:
- Mark signals as PRESENT/ABSENT per the rubric
- Assign severity 3/5 (mixed)
- Note "the install is incremental, not greenfield" in
  the competitor's "Notes for the operator" section

## The "JS-rendered homepage" case

If the snapshot is empty (homepage requires JavaScript to
render):
- Mark all signals as `unclear`
- Note "JS issue" in the competitor's notes
- Don't infer severity; let the operator decide

## The "parked domain" case

If the homepage is a parked domain (copyright 2024, no
content):
- Severity 1/5
- Note "parked domain — not a real prospect"
- Mark all signals as ABSENT (technically, the absence of
  content is the absence of friction)

## The cross-competitor summary

After scoring all 3 competitors, the cross-competitor
summary identifies the **top 3 most-egregious friction
patterns** across the cohort. These are the patterns that
become the "Destroy or Defend" angle for the Scribe.

Example:
1. "All 3 sites are phone-only after-hours — 100% of
   after-hours revenue is leaking"
2. "None of the 3 have instant booking — every job
   requires a phone call to schedule"
3. "None of the 3 surface Google reviews on the homepage
   — trust friction at first contact"

The "Destroy or Defend" angle:
"I audited 12 plumbers in Dallas. None of them can book a
job online. Here's the 4-week install I'd pitch to all of
them."

## What the scoring is NOT

- **Not a probability score.** Severity 5/5 doesn't mean
  the business will buy. It means the friction is severe
  enough to justify the operator's pitch.
- **Not a price anchor.** Severity 3/5 doesn't mean
  "$3K install." The price is per the Dre Builds pricing
  model.
- **Not static.** A competitor can move from 2/5 to 5/5
  in 6 months if they remove their chat widget. The audit
  is a snapshot, not a permanent score.

## Cross-reference

- `references/friction-filter.md` — the 3-tier taxonomy
- `references/procedure.md` — the 9-step procedure
- `references/output-format.md` — the markdown brief
  format (where the score is recorded)
- `client-pov-tracker` — downstream; the per-client POV
  uses the per-competitor scores as input
