---
name: offers
description: "Offer design, not copywriting. Most 'my copy isn't converting' problems are offer problems — no headline saves a weak offer. Diagnoses offers for services, agencies, courses, coaching, info products, and high-ticket B2B using the Value Equation + Six-Component Anatomy. Includes 7 reference files and baked-in anti-patterns (no fake timers, no inflated bonus values, no banned hype). Cross-referenced from /pricing, /copywriting, /launch, /sales-enablement. v2.5.0."
triggers:
  - offers
  - offer design
  - offer audit
  - offer teardown
  - value equation
  - offer anatomy
  - pricing strategy
  - bonus stack
  - guarantee design
  - offer packaging
---

# /offers — Offer Design Skill (v2.5.0)

## What this skill is

Offer design, not copywriting. Most "my copy isn't converting" problems are offer problems at the root — the words on the page can't rescue an offer that doesn't earn the price. This skill fixes the thing underneath the words.

**Scope:** services, agencies, courses, coaching, info products, and high-ticket B2B.

**Out of scope:** pure copywriting (see `/copywriting`), pure pricing math (see `/pricing`), launch sequence mechanics (see `/launch`), sales-enablement assets (see `/sales-enablement`). Those skills consume the offer this skill produces.

---

## When to invoke

Invoke `/offers` when ANY of the following is true:

- The operator says "my copy isn't converting" → almost always an offer problem first.
- New product/service is being packaged.
- Existing offer is being re-priced, re-bundled, or re-positioned.
- Conversion rate is dropping or stuck despite traffic.
- A competitor's offer is materially stronger.
- A launch is being prepped and the offer needs to be locked before copy is written.
- Bonus stack feels bloated, "stacked," or hard to defend.
- Guarantee feels weak, missing, or boilerplate.
- Price feels arbitrary or pulled out of thin air.

**Don't invoke for:** pure pricing math (anchor analysis, elasticity modeling — that's `/pricing`). Pure copy critique (that's `/copywriting`). Sales call enablement (that's `/sales-enablement`). This skill produces the offer; the others consume it.

---

## Inputs (parameters the operator provides)

Before the procedure starts, gather the following. If any are missing, ask before proceeding — guessing on offer design produces a weak offer.

| # | Parameter | Why it matters |
|---|-----------|----------------|
| 1 | **Business type** | services / agency / course / coaching / info product / high-ticket B2B — drives format choice |
| 2 | **Dream outcome for customer** | the single transformation they're paying for, in their words |
| 3 | **Current offer** (if any) | what they sell today, at what price, in what format |
| 4 | **Price point** | current or aspirational — both useful |
| 5 | **Target customer** | one specific person, not a persona smear |
| 6 | **Time to result** | how long until the customer sees the dream outcome |
| 7 | **Effort required from customer** | hours/week, level of difficulty, prerequisites |
| 8 | **Track record / proof** | case studies, results, credentials — anything that moves Perceived Likelihood |
| 9 | **Known objections** | what stops people from buying |
| 10 | **Constraints** | capacity (1:1 vs cohort vs self-paced), fulfillment cost, calendar, refund tolerance |

If the operator has only some of these, run the procedure anyway — gaps get surfaced as leak points in Stage 2.

---

## The 5-stage procedure

### Stage 1 — Capture (5 min)

Pull the parameters above into a one-page brief. If writing on the page is the bottleneck, do it conversationally in chat. Either way, the brief is the input to Stage 2.

**Output:** `offer-brief.md` (or chat transcript) with the 10 parameters filled.

---

### Stage 2 — Diagnose with the Value Equation (10 min)

The Value Equation is the diagnostic. Run it before designing anything.

```
Value = (Dream Outcome × Perceived Likelihood) / (Time Delay × Effort)
```

Score each axis 1–10 against the operator's CURRENT offer.

| Axis | What it measures | Common leak |
|------|------------------|-------------|
| **Dream Outcome** | How vivid and desirable the result is | Generic outcome ("grow your business") vs specific ("add $40k MRR in 90 days") |
| **Perceived Likelihood** | How much the buyer believes THEY will get the result | No proof, weak guarantee, no mechanism explained |
| **Time Delay** | How long until they see the result | "Lifetime access" or open-ended timelines |
| **Effort** | How hard they have to work | 10 hrs/week of homework with no support |

**The leak is the lowest score.** That's where the offer is bleeding value. The next stages fix the leak, not the highest score.

**Output:** Value Equation scores + identified leak axis. If multiple axes tie, the leak is whichever the operator can move with the most credibility. See `references/value-equation.md` for the deep dive.

---

### Stage 3 — Apply the Six-Component Anatomy (30–60 min)

Every offer is built from six components. Build each one explicitly. None of them is optional — a missing component is a leak.

| # | Component | Question it answers |
|---|-----------|---------------------|
| 1 | **Core deliverable** | What do they actually get? |
| 2 | **Bonus stack** | What else comes with it, and why does each bonus exist? |
| 3 | **Guarantee** | How is risk removed or reversed? |
| 4 | **Scarcity / urgency** | Why buy now and not later? (real scarcity only — see anti-patterns) |
| 5 | **Name** | What's it called? (Ownable, specific, outcome-shaped) |
| 6 | **Price + payment structure** | How much, paid how? (anchor, payment plan, premium for full pay) |

For each component: state it in one sentence, then check it against the leak from Stage 2. If the component doesn't address the leak, redesign it.

**Output:** Six-component offer spec, one paragraph per component. See `references/six-component-anatomy.md` for the per-component checklist + worked examples.

---

### Stage 4 — Format by Business Type (15 min)

The same six components land differently depending on business type. Pick the format that matches the operator's business.

| Business type | Format patterns | See |
|---------------|-----------------|-----|
| **Services** (consulting, freelance) | diagnostic → paid engagement → retainer | `references/formats-by-business-type.md` |
| **Agencies** | retainer / performance / hybrid | same |
| **Courses** | cohort-based / self-paced / premium | same |
| **Coaching** | 1:1 / group / mastermind | same |
| **Info products** | low-ticket / mid-ticket / high-ticket | same |
| **High-ticket B2B** | enterprise / POC / pilot | same |

**Output:** Format locked + components adapted to that format.

---

### Stage 5 — Anti-pattern gate (5 min)

Before the offer is shipped, run the anti-pattern checklist. If any item is YES, the offer is not ready — even if every other stage passed.

- [ ] No fake countdown timers (real cohort caps only — see `references/scarcity-frameworks.md`)
- [ ] No inflated bonus values (real or perceived value only — see `references/bonus-stacking.md`)
- [ ] No banned hype words (full list in `references/anti-patterns-checklist.md`)
- [ ] No fake scarcity (manufactured "only 3 spots left" with no real cap)
- [ ] No buried terms (price, refund, conditions visible at offer surface)
- [ ] No made-up testimonials or stats
- [ ] No "secret method" / "they don't want you to know" framing

**Output:** Offer spec passes the gate OR a list of items to fix before shipping.

---

## Deliverable shape

A complete offer spec looks like:

```markdown
# Offer: [Name]

**Business type:** [services | agency | course | coaching | info product | B2B]
**Price:** [$X one-time | $X/mo for N months | custom]
**Dream outcome:** [one sentence]
**Time to result:** [N days/weeks/months]

## Value Equation score
| Axis | Score (1-10) |
|------|--------------|
| Dream Outcome | X |
| Perceived Likelihood | X |
| Time Delay | X (lower = faster) |
| Effort | X (lower = less) |

**Leak axis:** [which one, and why]

## Six components
1. **Core deliverable:** ...
2. **Bonus stack:** ... (each bonus named, justified, with stated value)
3. **Guarantee:** ... (type, terms, length)
4. **Scarcity / urgency:** ... (real reason, with specifics)
5. **Name:** ...
6. **Price + payment structure:** ...

## Anti-pattern gate: PASS / list of items to fix
```

---

## Anti-patterns baked in (full list)

These are non-negotiable. An offer that ships with any of them gets weaker, not stronger.

1. **Fake countdown timers** — evergreen "X hours left" with no real deadline. Buyers can tell. Use real cohort caps instead.
2. **Inflated bonus values** — "$997 bonus" for a 30-minute template. The math doesn't survive scrutiny. State real or perceived value, not fictional.
3. **Banned hype words** — `game-changing`, `revolutionary`, `secret method`, `magic`, `they don't want you to know`, `one weird trick`, `breakthrough`. Replace with specifics.
4. **Fake scarcity** — "Only 3 spots left" when there are no spots. Real scarcity has a real constraint.
5. **Buried terms** — refund policy hidden in fine print. Surface it.
6. **Made-up proof** — testimonials that don't exist, stats with no source, "as seen in" with no logo rights.
7. **Generic outcomes** — "Grow your business" / "Get healthier" / "Make more money." Specific beats generic every time.
8. **Bonus stacking theater** — stacking 12 bonuses to inflate perceived value without each earning its place.

Full checklist with examples: `references/anti-patterns-checklist.md`.

---

## Cross-references

| Skill | When to hand off |
|-------|------------------|
| `/pricing` | After the offer is locked — for anchor analysis, elasticity, payment-plan math |
| `/copywriting` | After the offer is locked — for the words on the page that deliver the offer |
| `/launch` | After the offer + copy are locked — for the sequence that brings people to the offer |
| `/sales-enablement` | For high-ticket offers — for the sales-call assets that close the offer |

This skill is upstream of all four. Don't run those skills on an offer that hasn't passed Stage 5.

---

## Reference files (the fat layer)

| File | Purpose |
|------|---------|
| `references/value-equation.md` | The math, scoring rubric, common leak patterns, worked example |
| `references/six-component-anatomy.md` | Per-component checklist + worked example for each of the 6 components |
| `references/guarantee-design.md` | 8 guarantee types, when each fits, risk profile |
| `references/bonus-stacking.md` | Bonus stack principles, real vs perceived value, anti-inflation rules |
| `references/scarcity-frameworks.md` | 5 scarcity frameworks, real vs manufactured urgency |
| `references/formats-by-business-type.md` | Services, agencies, courses, coaching, info products, high-ticket B2B |
| `references/before-after-teardowns.md` | 6 anonymized before/after examples across business types |
| `references/anti-patterns-checklist.md` | Full banned-moves list with examples + replacements |

---

## Operator-loop expectation

A clean run is ~60–90 minutes. That's it. Don't over-engineer. The offer should ship when Stage 5 passes — not after the 8th iteration.

If the operator wants to keep iterating after Stage 5, the right next move is to ship, measure conversion, and come back with data. Not to redesign in the abstract.
