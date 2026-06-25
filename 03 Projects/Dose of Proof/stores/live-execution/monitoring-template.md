---
type: monitoring-template
asset: day-1-execution-monitoring
status: ✅ FINAL (locked 2026-06-24)
purpose: standing template for post-publish review + iteration decisions — the feedback loop
cadence: per-asset (within 24h of publish) + daily EOD rollup
audience: Mavis (operator) + Dre (approver)
---

# Day 1 Execution Monitoring + Iteration Loop

> The feedback loop that runs alongside the pre-launch calendar. Every published asset gets reviewed. Every review produces one micro-iteration or derivative within 24 hours. The loop compounds.

---

## Per-Asset Review Template (paste for each new publish)

### Asset metadata

| Field | Value |
|-------|-------|
| Asset name | |
| Asset type | X thread / X standalone / LinkedIn post / LinkedIn carousel / Substack post / Skool pinned / Email |
| Pillar | Lived Protocol / Macro-Longevity / Reconstitution / Hybrid |
| Publish date + time | |
| Canonical CTA used | https://doseofproof.substack.com/ |
| Status at publish | FINAL / REVIEW / BLOCKED |

### Performance snapshot (24h after publish)

| Metric | Day 1 | Day 3 | Day 7 |
|--------|-------|-------|-------|
| Impressions | | | |
| Engagement rate | | | |
| Link clicks (to Substack) | | | |
| Replies | | | |
| Quote-tweets / reshares | | | |
| Substack opt-ins attributed (UTM) | | | |
| New Skool reservations attributed | | | |
| Pin status | | | |

### Engagement quality (Dre's read)

- **Strongest reply or comment:** [paste verbatim]
- **Most-shared response:** [paste verbatim]
- **Most-asked question:** [paste verbatim]
- **Sentiment breakdown:** Positive / Neutral / Skeptical / Hostile — %

### What moved the data

The single strongest performing element on this asset:

- [ ] Hook (tweet 1 / opening line)
- [ ] CTA placement (in body / first comment / pinned)
- [ ] Visual (carousel slide X / static image / thread structure)
- [ ] Pillar framing (Lived / Macro / Reconstitution)
- [ ] Compliance posture (more explicit "I'm not a doctor" / framework anchor)
- [ ] Data specificity (real numbers vs abstract)
- [ ] Time of publish
- [ ] Other: ____

### Iteration decision (within 24h)

The one micro-iteration or derivative that doubles down on what worked:

- **Asset to create:** [X standalone / LinkedIn comment / Skool pinned / Substack excerpt / Email send]
- **What it copies from the winner:** [the hook / CTA / framing / visual]
- **What it changes:** [the data point / the angle / the platform]
- **Publish date:** [target within 24h of review]
- **Mavis drafts or Dre drafts:** [decision based on voice-fit]

---

## Daily EOD Rollup Template (paste every evening)

### Day [N] summary — [date]

**Posts shipped today:**
1. [Asset name + URL]
2. [Asset name + URL]
3. ...

**Substack email delta:** [+/- subscribers]
**Skool member delta:** [+/- free / +/- paid]
**Comments requiring Dre response:** [count]
**Compliance flags raised:** [count, with detail]

**Strongest single element today:** [paste asset + element + reasoning]
**Weakest single element today:** [paste asset + element + reasoning]

**Iteration queued for tomorrow:**
- [Asset to create]
- [Source asset + element it's copying]
- [Publish target time]

**One thing Mavis is escalating to Dre:**
- [Specific friction only Dre can clear]

---

## Iteration Cycle — the 24-hour rule

| Stage | Time after publish | Action |
|-------|---------------------|--------|
| Publish | T=0 | Asset goes live with FINAL/REVIEW/BLOCKED label |
| First read | T+2h | Dre replies to comments in the first 2 hours per engagement rules |
| Snapshot pull | T+6h | Mavis pulls first performance metrics (impressions, replies, link clicks) |
| Review | T+24h | Dre + Mavis complete the per-asset review template |
| Iteration decision | T+24h | One micro-iteration queued, owner assigned |
| Iteration publish | T+48h | The derivative ships, doubling down on what worked |
| Loop continues | T+72h, T+7d | Re-snapshot, re-iteration as needed |

---

## What the loop does NOT do

- ❌ It does NOT change the canonical CTA (`https://doseofproof.substack.com/` stays)
- ❌ It does NOT introduce sourcing language or compliance drift
- ❌ It does NOT create new assets that aren't on the pre-launch calendar
- ❌ It does NOT pivot away from the 3-pillar rotation mid-week
- ❌ It does NOT replace the original asset (the winner stays; the derivative doubles down)

---

## Iteration constraint rules

1. **The original asset is never deleted or modified.** It stays as published. The iteration is a derivative, not a replacement.
2. **Voice + compliance threshold applies.** Iteration assets must hit the same 80% threshold as originals. If they don't, they ship with the REVIEW label and Dre's eyes.
3. **Compliance footer carries forward.** Every derivative must carry the same compliance posture as the source.
4. **One iteration per asset per day, max.** No flooding the timeline.
5. **Iteration owner default:** Mavis drafts, Dre approves, unless voice-fit falls below 80% (then Dre drafts).

---

## What we're optimizing for (in priority order)

1. **Substack opt-ins attributed to each asset** — the email list is the moat, KPI #1
2. **Engagement rate on hook + CTA pairing** — the conversation is the qualification signal
3. **Pillar rotation working** — the 3-pillar mix should show in the engagement data
4. **Compliance posture intact** — zero flags, zero sourcing drift, zero "you should take" language
5. **Cross-platform distribution working** — X → LinkedIn → Substack → Skool flow shows up in attribution

---

## Logging location

All per-asset reviews live in: `stores/live-execution/reviews/[asset-name]-review.md`
Daily EOD rollups live in: `stores/live-execution/daily-rollups/YYYY-MM-DD-rollup.md`
Iteration decisions live in: `stores/live-execution/iteration-log.md`

The loop runs in the `stores/live-execution/` folder so it doesn't pollute the asset folders.

---

## What this template enables

When the pre-launch calendar runs in real time, this template ensures:

1. **Every published asset is reviewed within 24h** — nothing ships into the void
2. **One iteration per asset per day** compounds the winning patterns across the calendar
3. **Compliance drift is caught early** — REVIEW label = pause + Dre eyes
4. **The calendar's pillar rotation gets data** — which pillar is landing, which isn't
5. **The brand's voice + framework anchors stay locked** — every iteration passes the same threshold

The PCAC hair-trigger assets follow a parallel-but-different review template (see `specs/pcac-hair-trigger-activation.md` for the reaction-asset review pattern).

---

*Last updated: 2026-06-24 (Live Execution pass)*
*Activation: per-asset review within 24h + daily EOD rollup + one iteration queued per asset*