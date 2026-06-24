---
name: pricing
description: "Pricing strategy for offers, not math for spreadsheets. Anchor analysis, elasticity, payment structure, charm vs premium positioning, decoy effect, tiered pricing, and price testing. For services, agencies, courses, coaching, info products, high-ticket B2B. Consumes /offers — run /offers first to lock the offer, then run /pricing to set the price. v2.5.0."
triggers:
  - pricing
  - pricing strategy
  - price anchor
  - price elasticity
  - payment plan
  - multi-pay
  - charm pricing
  - premium pricing
  - decoy pricing
  - tiered pricing
  - good better best
  - price test
---

# /pricing — Pricing Strategy Skill (v2.5.0)

## What this skill is

Pricing strategy for offers, not math for spreadsheets. The price has to defend itself against the buyer's "is this worth it?" calculation — which means anchoring, framing, and structuring it correctly. This skill handles the strategy; the operator's accounting software handles the math.

**Scope:** services, agencies, courses, coaching, info products, high-ticket B2B.

**Upstream:** Run `/offers` first. Pricing without a locked offer produces an unanchored number on a generic page — which converts poorly. The offer must be specific before the price can defend itself.

**Downstream:** Pricing feeds `/copywriting` (the words around the price) and `/launch` (cart-open/cart-close pricing tactics).

---

## When to invoke

- New offer is being priced for the first time.
- Existing offer is being re-priced (raise, repackage, reposition).
- Conversion is stuck — usually an anchoring problem, not a copy problem.
- Payment structure needs design (one-time, multi-pay, retainer, milestone).
- Tiered pricing is being introduced or restructured.
- Competitor pricing is materially different and you need to position against it.
- Buyer objections center on price ("too expensive") without engagement.

**Don't invoke for:** pure COGS or margin modeling (use accounting tools). Offer design (that's `/offers`). Sales-call pricing conversations (that's `/sales-enablement`).

---

## Inputs

Pull these from the operator before starting. If pricing is the question, the offer is already locked — these come from the `/offers` deliverable.

| # | Parameter | Why it matters |
|---|-----------|----------------|
| 1 | **Locked offer spec** | From `/offers` — six components + Value Equation score |
| 2 | **Target customer** | Their cashflow, their alternatives, their reference price |
| 3 | **Fulfillment cost per buyer** | Drives floor — price must exceed this + margin |
| 4 | **Capacity / volume target** | $10k/month × 10 buyers vs $1k × 100 buyers → different price architecture |
| 5 | **Comparable alternatives** | What else the buyer could spend this money on |
| 6 | **Buyer cashflow pattern** | Lump-sum available, monthly recurring, or milestone-based |
| 7 | **Existing price history** | If re-pricing — what worked, what didn't |
| 8 | **Competitor pricing** | If known — informs anchor |
| 9 | **Refund / risk tolerance** | Affects guarantee structure which affects price |

---

## The 5-stage procedure

### Stage 1 — Capture (5 min)

Pull the `/offers` spec and the parameters above. If pricing is being done in isolation (offer isn't locked yet), **stop and run `/offers` first**.

**Output:** Pricing brief — locked offer + parameters above.

---

### Stage 2 — Set the Floor (10 min)

The floor is the lowest defensible price. Below it, you can't fulfill the offer profitably.

```
Floor = Fulfillment cost per buyer + Acceptable margin (≥30%) + Risk buffer (refund/chargeback)
```

Common floors by business type:

| Type | Typical floor per buyer |
|------|------------------------|
| Info product ($200 course) | $20–$50 |
| Cohort course ($2k) | $200–$500 |
| 1:1 coaching ($5k) | $500–$1,500 (mostly operator time) |
| Agency retainer ($5k/mo) | $2k–$3k/mo (operator + delivery cost) |
| High-ticket B2B ($50k pilot) | $15k–$30k |

**Output:** Floor number. Pricing must clear this with margin. If the buyer can't pay a price above the floor, the offer isn't viable at scale — redesign the offer, not the price.

---

### Stage 3 — Set the Anchor (15 min)

The anchor is the reference price the buyer compares against. Without an anchor, any price reads as expensive. With a strong anchor, the right price reads as fair.

**Three anchor types:**

| Anchor | Example | When it works |
|--------|---------|---------------|
| **Alternative cost** | "vs. $25,000 agency engagement" | Service/agency offers where the buyer has a known alternative |
| **Total value** | "$3,000 in bonuses + $7,000 in core = $10,000 total value" | Offers with strong bonus stacks (rarely survives scrutiny — see anti-patterns) |
| **Future cost of inaction** | "vs. losing $40k MRR over the next 12 months" | High-ticket offers where inaction has a measurable cost |

**Anchoring rule:** the anchor must be **real** and **specific**. Generic anchors ("premium service") don't anchor. Specific anchors ("$25,000 for the same scope at an agency") do.

**Output:** Anchor price + anchor framing (the sentence that introduces the anchor in copy).

---

### Stage 4 — Pick the Price + Structure (20 min)

Set the actual price and how the buyer pays.

**Price levels (rule of thumb):**

| Level | Range | When it works |
|-------|-------|---------------|
| **Low-ticket** | <$500 | Self-paced info products, evergreen |
| **Mid-ticket** | $500–$2,500 | Cohort courses, premium info products, group coaching |
| **High-ticket** | $2,500–$10k | 1:1 coaching, agency retainers, premium courses |
| **Very high-ticket** | $10k–$50k | Masterminds, agency projects, B2B pilots |
| **Enterprise** | $50k+ | B2B contracts, custom engagements |

**Structure (see `references/payment-structure-math.md`):**

| Structure | When it works |
|-----------|---------------|
| One-time lump-sum | Info products, project services |
| Monthly recurring | Retainers, subscriptions, ongoing coaching |
| Multi-pay (2–6 installments) | Mid-to-high ticket where lump-sum blocks buyers |
| Milestone payments | Project services, B2B |
| Performance / hybrid | Lead gen, agencies with upside |
| Custom / proposal | High-ticket B2B |

**Premium for full pay rule:** when offering multi-pay, give 5–15% off for paying in full. Bigger discounts cannibalize the lump-sum option. Smaller discounts don't move the needle.

**Output:** Final price + payment structure + premium-for-full-pay discount.

---

### Stage 5 — Anti-pattern gate + Format (10 min)

Run the anti-pattern checklist before the price ships. Then format the price for the offer surface (sales page, email, proposal).

Anti-pattern checklist (full list in `references/anti-patterns-checklist.md`):

- [ ] No unanchored prices (every price has a reference)
- [ ] No fake discounts ("was $999, NOW $499" with no real prior price)
- [ ] No charm-pricing tricks on high-ticket ($9,997 instead of $10,000 reads as cheap at this level)
- [ ] No decoy tier that's transparently bad
- [ ] No "contact us" pricing on offer surface (with no anchor)
- [ ] No multi-pay with no premium for full pay
- [ ] No price without clear payment structure
- [ ] No price changes without justification

**Output:** Price + structure ready for `/copywriting`.

---

## Deliverable shape

```markdown
# Pricing: [Offer Name]

**Floor:** $X (fulfillment + 30% margin + risk buffer)
**Anchor:** $Y ([alternative cost | total value | future cost of inaction])
**Final price:** $Z ([one-time | monthly | multi-pay])
**Payment structure:** [one-time | multi-pay X×$Y | retainer | custom]
**Premium for full pay:** [X% discount if paying in full]

## Price summary by tier (if tiered)
| Tier | Price | Who it's for |
|------|-------|--------------|
| [Tier 1] | $X | [Audience] |
| [Tier 2] | $Y | [Audience] |
| [Tier 3] | $Z | [Audience] |

## Anti-pattern gate: PASS / list of items to fix
```

---

## Anti-patterns baked in (full list)

1. **Unanchored pricing** — "$5,000" alone reads as expensive. Always anchor.
2. **Fake discounts** — "Was $999, NOW $499" with no actual prior $999. Buyers can check.
3. **Charm pricing at high ticket** — $9,997 instead of $10,000 reads as cheap or hiding the round number.
4. **Transparently bad decoy** — a third tier that exists only to make the middle tier look good. Buyers see through it.
5. **"Contact us" pricing on offer surface** — without an anchor, reads as "this is expensive and we don't want to show you."
6. **No premium for full pay** — multi-pay with no lump-sum incentive means everyone picks multi-pay.
7. **Price without payment structure** — "$5,000" alone is harder to sell than "$5,000 or 3 × $1,750."
8. **Discounting without justification** — random "20% off this week" trains buyers to wait.

Full checklist with examples: `references/anti-patterns-checklist.md`.

---

## Cross-references

| Skill | When to hand off |
|-------|------------------|
| `/offers` | **Run first.** Pricing consumes the offer spec. |
| `/copywriting` | After pricing is locked — for the words around the price |
| `/launch` | For launch-specific pricing (early-bird, cart-close price increase) |
| `/sales-enablement` | For high-ticket — for handling "too expensive" objections on calls |

---

## Reference files (the fat layer)

| File | Purpose |
|------|---------|
| `references/anchor-analysis.md` | 3 anchor types, when each works, how to find real anchors |
| `references/elasticity-modeling.md` | How demand changes with price, when to raise, when to hold |
| `references/payment-structure-math.md` | Multi-pay math, premium for full pay, when to use each structure |
| `references/price-psychology.md` | Charm vs premium, decoy effect, anchoring psychology, framing |
| `references/tiered-pricing.md` | Good/better/best, when 1/2/3 tiers, decoy design |
| `references/price-testing.md` | When to test price, methodology, how to read results |
| `references/anti-patterns-checklist.md` | Full banned-moves list with examples + replacements |
