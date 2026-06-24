---
name: launch
description: "Launch sequence mechanics — pre-launch, open cart, mid-launch, close cart. Launch types (PLF, audience, signature, evergreen). Launch calendar templates. Email cadence per phase. Consumes /offers + /pricing + /copywriting. v2.5.0."
triggers:
  - launch
  - product launch
  - cart open
  - cart close
  - pre-launch
  - PLF
  - product launch formula
  - signature launch
  - audience launch
  - evergreen launch
  - launch calendar
  - launch sequence
---

# /launch — Launch Sequence Skill (v2.5.0)

## What this skill is

Launch sequence mechanics. The offer is locked, the price is anchored, the copy is written. This skill sequences when to send what — pre-launch anticipation, cart open, mid-launch momentum, cart close.

**Scope:** the launch sequence itself — emails, social posts, calendar, cadence. Not for ongoing nurture (that's `/copywriting` post-purchase).

**Upstream:** Run `/offers`, `/pricing`, and `/copywriting` first. Launching a weak offer with great sequence is wasted motion; the offer has to earn the launch.

**Downstream:** Launch feeds `/copywriting` (post-purchase) and `/sales-enablement` (for high-ticket launches with sales calls).

---

## When to invoke

- New offer is launching for the first time.
- Existing offer is being re-launched (after a pause, new audience, or relaunch).
- Cart-open / cart-close dates need to be locked.
- Launch calendar needs to be built.
- Launch performance is below benchmark.
- Considering evergreen vs. cohort launch.

**Don't invoke for:** offer design (`/offers`), pricing (`/pricing`), copy (`/copywriting`), post-launch nurture (`/copywriting` post-purchase), ongoing marketing (different cadence).

---

## Inputs

| # | Parameter | Why it matters |
|---|-----------|----------------|
| 1 | **Locked offer spec** | From `/offers` — six components + guarantee |
| 2 | **Locked pricing** | From `/pricing` — final price + structure |
| 3 | **Sales page** | From `/copywriting` — the destination |
| 4 | **Email list size + quality** | Cold vs. warm, engagement level |
| 5 | **Audience size (social, podcast, etc.)** | Drives awareness vs. conversion focus |
| 6 | **Launch type** | PLF / audience / signature / evergreen |
| 7 | **Cart-open / cart-close dates** | Specific dates drive the calendar |
| 8 | **Capacity** | Cohort cap, fulfillment capacity, support bandwidth |
| 9 | **Existing customer base** | Warm buyers for early access, testimonials, referrals |
| 10 | **Promotion partners** | Joint venture partners, affiliates, podcast features |

---

## The 5-stage procedure

### Stage 1 — Choose launch type (10 min)

Pick the launch type that matches the offer and the audience. See `launch-types.md`.

| Launch type | When it works | Cart window |
|-------------|---------------|-------------|
| **PLF (Product Launch Formula)** | New mechanism or category, warm list | 5–7 days |
| **Audience launch** | Strong existing audience, offer fits them | 3–5 days |
| **Signature launch** | First-time launch, building from scratch | 7–10 days |
| **Evergreen** | Self-paced, low-ticket, scalable | Continuous |

**Default:** PLF or signature for new offers. Audience launch for established operators. Evergreen only for low-ticket self-paced.

**Output:** Launch type chosen.

---

### Stage 2 — Build the launch calendar (30 min)

Lock the dates. Build the calendar backwards from cart-close.

**Typical signature/PLF launch calendar (14 days):**

| Day | Phase | Action |
|-----|-------|--------|
| T-14 | Pre-launch | "Something is coming" email |
| T-12 | Pre-launch | Problem-deepening email |
| T-10 | Pre-launch | Mechanism reveal |
| T-7 | Pre-launch | Cart opens tomorrow |
| T-6 | Open cart | Cart is open |
| T-5 | Open cart | Why I built this |
| T-4 | Open cart | Quick case study |
| T-3 | Mid-launch | Objection handling |
| T-2 | Mid-launch | More case studies |
| T-1 | Mid-launch | FAQ |
| T-0 | Close cart | 48 hours left |
| T+1 | Close cart | Last day |
| T+2 | Close cart | Doors close tonight |
| T+3 | Close cart | Final call |

See `launch-calendar-template.md` for full templates by launch type.

**Output:** Locked calendar with dates, emails, and posts.

---

### Stage 3 — Pre-launch phase (T-14 to T-7)

**Job:** Build anticipation. Seed the problem. Tease the mechanism. Grow the waitlist.

See `pre-launch-phase.md` for the full sequence.

**Key actions:**
- 3–5 emails building anticipation
- 1–3 social posts teasing the launch
- (Optional) waitlist with early-bird incentive
- (Optional) free preview / workshop to build the list

**Output:** Pre-launch emails drafted and queued.

---

### Stage 4 — Cart open + mid-launch + cart close (T-7 to T+2)

**Job:** Drive conversion. Handle objections. Build urgency. Close.

See `open-cart-phase.md`, `mid-launch-phase.md`, `close-cart-phase.md`.

**Key actions:**
- 3 emails on cart-open day (morning, afternoon, next morning)
- 2–3 mid-launch emails (objections, case studies, FAQ)
- 3 cart-close emails (48 hours, 24 hours, doors closing)
- 2–3 social posts per phase

**Output:** Cart-phase emails drafted and queued.

---

### Stage 5 — Anti-pattern gate + post-launch plan (15 min)

**Anti-pattern gate** (full list in `anti-patterns-checklist.md`):
- [ ] Cart-open date is real (not fake evergreen countdown)
- [ ] Cart-close date is real and enforced
- [ ] No "limited spots" without an actual cap
- [ ] No "last chance" emails after cart closes
- [ ] Launch is sent to engaged subscribers (not full unsegmented list)
- [ ] No manufactured urgency layered on top of real urgency
- [ ] No fake scarcity on social posts

**Post-launch plan:**
- [ ] Post-purchase sequence queued (see `/copywriting` post-purchase)
- [ ] Testimonial collection planned for buyers
- [ ] Re-engagement sequence for non-buyers planned
- [ ] Next launch date calendared (or evergreen routing set)

**Output:** Launch ready to ship.

---

## Deliverable shape

```markdown
# Launch: [Offer Name]

**Launch type:** [PLF | audience | signature | evergreen]
**Cart open:** [Date + time + timezone]
**Cart close:** [Date + time + timezone]
**Capacity:** [N buyers / cohort cap]

## Calendar
| Day | Date | Phase | Email | Subject |
|-----|------|-------|-------|---------|
| T-14 | [...] | Pre-launch | [...] | [...] |
| ... | ... | ... | ... | ... |

## Email queue
[List of all emails, subject lines, scheduled sends]

## Social posts
[List of social posts, dates, copy snippets]

## Anti-pattern gate: PASS / list of items to fix
## Post-launch plan: [queued / in progress]
```

---

## Anti-patterns baked in (full list)

1. **Evergreen countdown with no real deadline** — "5 hours left" that resets on every visit.
2. **"Limited spots" without an actual cap** — fake scarcity.
3. **Cart-close extension** — extending the deadline publicly after launch starts. Once is forgivable. Twice destroys trust.
4. **Reopening "one more spot"** — turns scarcity into theater.
5. **Launch to unengaged list** — sending launch emails to subscribers who haven't opened in 6+ months burns deliverability.
6. **Stacked fakes** — fake countdown + fake scarcity + fake bonus values + fake testimonials.
7. **No cart-close plan** — launching without a real closing mechanism.
8. **Launching without fulfillment capacity** — selling 100 cohort spots with capacity for 30.
9. **Post-launch re-engagement to non-buyers without a plan** — losing the launch list's value.

Full checklist: `references/anti-patterns-checklist.md`.

---

## Cross-references

| Skill | When to hand off |
|-------|------------------|
| `/offers` | **Run first.** Launch consumes the offer spec. |
| `/pricing` | **Run first.** Launch consumes the pricing. |
| `/copywriting` | **Run first.** Launch consumes the emails, sales page, subject lines. |
| `/sales-enablement` | For high-ticket launches — sales calls during cart-open. |

---

## Reference files (the fat layer)

| File | Purpose |
|------|---------|
| `references/launch-types.md` | PLF, audience, signature, evergreen — when each works |
| `references/pre-launch-phase.md` | Pre-launch sequence, waitlist, anticipation-building |
| `references/open-cart-phase.md` | Cart-open day emails and posts |
| `references/mid-launch-phase.md` | Objection handling, case studies, FAQ |
| `references/close-cart-phase.md` | Cart-close emails, last-call, final push |
| `references/launch-calendar-template.md` | Calendar templates for each launch type |
| `references/anti-patterns-checklist.md` | Full banned-moves list with examples + replacements |
