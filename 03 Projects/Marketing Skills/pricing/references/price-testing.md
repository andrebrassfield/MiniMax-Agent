# Price Testing — Methodology

You don't know your elasticity until you test. But testing the price is one of the hardest things to do well — most tests are inconclusive or misleading.

---

## When to test the price

**Test when:**
- You have enough traffic to draw conclusions (>1,000 visitors/month to the offer).
- Conversion is steady but you suspect the price is wrong.
- You're re-pricing an existing offer.
- You have a clear hypothesis about what'll happen.

**Don't test when:**
- You don't have enough traffic — you'll read noise.
- The offer itself is unstable (still iterating the offer, not the price).
- You have a strong reason to believe the current price is correct.
- You're in launch mode and the launch sequence is the test.

---

## What "test" means

A price test changes the price for a subset of traffic and compares the outcome.

**Two approaches:**

### 1. Split-test (A/B)

Split traffic 50/50 between two prices. Measure conversion and revenue per visitor at each.

**Example:** 50% see $497, 50% see $697. After 200 conversions total, compare.

**Pros:** Clean signal.
**Cons:** Requires traffic volume. Takes time.

### 2. Sequential test

Run price A for a period, then price B for the same period. Compare.

**Example:** $497 for 2 weeks, then $697 for 2 weeks.

**Pros:** Lower traffic requirement.
**Cons:** Seasonality / timing affects results. Less clean signal.

**Default:** split-test if you have traffic. Sequential if you don't.

---

## What to measure

Three numbers matter, in order:

1. **Revenue per visitor.** Total revenue / total visitors. This is what you optimize for.
2. **Conversion rate.** Buyers / visitors. Sanity check that conversion isn't tanking.
3. **Average transaction value.** Revenue / buyers. Tracks price directly.

**Anti-pattern:** optimizing for conversion rate alone. 100% conversion at $1 = $1/visitor. 2% conversion at $500 = $10/visitor. Revenue per visitor is the right metric.

---

## How long to run the test

**Rule:** at least 100 conversions per arm before drawing conclusions.

If your conversion rate is 3% and you have 5,000 visitors/month, you need ~3,400 visitors per arm to get 100 conversions per arm. That's ~2 months per arm.

If you don't have that traffic, run sequential tests over longer periods and accept more noise.

**Don't:** end the test after 2 weeks because one arm looks better. End it when you have enough data.

---

## Test design

### Single variable at a time

Test the price, not the price AND the offer AND the copy. Change one thing.

If you change price and offer simultaneously, you don't know which moved the result.

### Same traffic source

Test price A and price B to traffic from the same source. Cold Facebook traffic behaves differently than warm email traffic. Match sources.

### Same time period (sequential) OR simultaneous (split)

Don't compare "last month at $497" with "this month at $697" if last month was Q4 and this month is Q1. Seasonality affects conversion.

### Same offer copy

Don't change the copy between arms. If you change copy + price, you can't isolate the price effect.

### Random assignment (split)

In a split test, random assignment. The user shouldn't be able to choose which arm they're in.

---

## Common mistakes

### Calling the test too early

"Week 1: $497 converted 4%, $697 converted 3%. So $497 is better."

With small samples, week-1 results are noise. Wait for 100+ conversions per arm.

### Optimizing the wrong metric

"Conversion is higher at $497, so $497 wins."

But revenue per visitor at $697 might be higher if conversion only dropped slightly. Always check revenue per visitor.

### Testing too small a price change

"$497 vs $547." Too close to detect. Most price tests need 30%+ change to register.

### Letting the test run forever

"I've been running this test for 6 months and still no clear winner." If no winner after 6 months, the difference doesn't matter. Pick a price and move on.

### External changes during the test

Competitor launched. Holiday season hit. Ad budget changed. Any of these invalidates the test.

---

## What to do with results

### Clear winner (revenue per visitor >20% better)
Adopt the winning price. Run again in 6+ months to confirm.

### Marginal winner (revenue per visitor <20% better)
Pick the price that aligns with positioning. Higher price = premium feel. Lower price = accessibility. Don't over-optimize.

### No difference
Pick the price that aligns with positioning. Test again when you have more data.

### Both prices lose money
Price isn't the problem. Offer or traffic is. Go back to `/offers` or audit traffic.

---

## When NOT to test the price

Some situations call for committing to a price, not testing.

### Brand-new offer, no traffic yet

Pick a reasonable price based on:
- Operator time × 3 minimum
- Comparable offers in the market
- The "would I pay this?" gut check

Ship, get data, test later.

### High-ticket B2B

Sales-driven, not price-driven. The price is set per engagement after discovery. Testing doesn't apply.

### Launch mode

You're testing the offer in a launch. Price is part of the offer. Don't split-test mid-launch.

### Premium positioning

You've decided this is a $10k offer. Don't second-guess it with a $7k test. Commit.

---

## Price testing — alternatives

Sometimes you can't run a clean test, but you can get signal from other sources.

### Pre-sale / waitlist

Offer the new price to a waitlist first. If 30%+ convert at the new price vs. the old, raise.

### Survey

Ask recent buyers: "Would you have paid 30% more for this?" If most say yes, raise.

### Comparable offers

What do comparable offers in your market charge? Use as a sanity check.

### Operator gut

"Would I pay this if I were the buyer?" If not, the price is probably wrong.

---

## Quick checklist

Before starting a price test:

- [ ] You have enough traffic (>1,000 visitors/month to the offer)
- [ ] The offer is locked and stable
- [ ] You're testing ONE variable (price)
- [ ] Same traffic source, same copy, same time period
- [ ] You have a clear hypothesis ("raising from $497 to $697 will increase revenue per visitor")
- [ ] You can wait for 100+ conversions per arm
- [ ] You're measuring revenue per visitor (not just conversion)
