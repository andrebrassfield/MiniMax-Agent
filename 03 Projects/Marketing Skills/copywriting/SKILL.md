---
name: copywriting
description: "Copywriting for offers that already exist. Long-form sales pages, headline formulas, CTA design, email sequences (welcome, launch, abandoned cart, post-purchase), subject lines, voice & tone. Consumes /offers + /pricing — never run /copywriting on an offer that hasn't been locked. v2.5.0."
triggers:
  - copywriting
  - sales page
  - sales letter
  - landing page copy
  - headline
  - subject line
  - email sequence
  - welcome sequence
  - launch emails
  - abandoned cart
  - CTA
  - call to action
  - voice and tone
---

# /copywriting — Copywriting Skill (v2.5.0)

## What this skill is

Copywriting for offers that already exist. The offer is locked, the price is anchored, the components are built. This skill produces the words on the page — the long-form sales page, the launch emails, the subject lines, the CTAs.

**Scope:** long-form sales pages, landing pages, email sequences, ad copy, subject lines, CTAs. Not for branding, naming (use `/offers` for naming), or product copy (UX strings).

**Upstream:** Run `/offers` and `/pricing` first. Copy on a weak offer is wasted; copy on an unanchored price reads as expensive.

**Downstream:** Copy feeds `/launch` (the sequence of when to send what) and `/sales-enablement` (sales-call scripts).

---

## When to invoke

- Sales page is being written or rewritten.
- Launch sequence emails need to be drafted.
- Welcome sequence for new subscribers/buyers.
- Abandoned cart sequence needed.
- Subject line testing or refresh.
- CTA copy needs work (low click-through on buttons).
- Existing copy is converting below benchmarks.

**Don't invoke for:** offer design (`/offers`), pricing (`/pricing`), naming (`/offers`), UX/product copy, brand voice exploration (this skill assumes voice is already defined — see `voice-and-tone-rules.md` for the canonical voice).

---

## Inputs

| # | Parameter | Why it matters |
|---|-----------|----------------|
| 1 | **Locked offer spec** | From `/offers` — six components + Value Equation score |
| 2 | **Locked pricing** | From `/pricing` — final price, payment structure, anchor |
| 3 | **Voice guide** | The brand's voice rules (use `voice-and-tone-rules.md` if no internal guide) |
| 4 | **Audience profile** | One specific person, their language, their objections |
| 5 | **Surface** | Sales page, email, ad, landing page, etc. |
| 6 | **Goal** | Sell? Capture email? Book call? Each surface has a different job. |
| 7 | **Existing copy** | If rewriting — what's there, what's not working |
| 8 | **Proof assets** | Testimonials, case studies, logos, results — usable as social proof |
| 9 | **Mechanism / story** | The "how it works" or origin story that anchors the offer |

---

## The 5-stage procedure

### Stage 1 — Capture (5 min)

Pull the `/offers` spec, `/pricing` output, voice guide, and audience profile. If any are missing, **stop and run the upstream skill first**.

**Output:** Copywriting brief — locked offer + pricing + audience + surface + goal.

---

### Stage 2 — Build the long-form sales page (60–90 min)

If the surface is a sales page, this is the load-bearing step. Use the structure from `sales-page-structure.md`.

The 8 sections, in order:

1. **Headline** — outcome-shaped, specific, dream-outcome-forward.
2. **Sub-headline** — mechanism or differentiator.
3. **Problem** — articulate the buyer's pain in their language.
4. **Agitation** — cost of inaction, why it stays broken.
5. **Solution** — introduce the offer as the mechanism that fixes it.
6. **Proof** — testimonials, case studies, results that match the buyer.
7. **Offer + Guarantee** — six components + guarantee stated explicitly.
8. **CTA** — repeat the offer, push to action, lower the risk.

**Output:** Long-form sales page draft. See `sales-page-structure.md` for the per-section checklist + word-count targets.

---

### Stage 3 — Email sequences (45 min per sequence)

Email sequences depend on the surface:

| Sequence | When to write | Email count | Cadence |
|----------|---------------|-------------|---------|
| **Welcome** (new subscriber) | Always | 5–7 emails | Every 2–3 days |
| **Pre-launch** (waitlist) | Before launch | 3–5 emails | Daily |
| **Open cart** (launch day 1) | Cart opens | 1–3 emails | Same day + next day |
| **Mid-launch** (launch middle) | Days 2–5 | 2–3 emails | Every other day |
| **Close cart** (final days) | Days 5–7 | 2–3 emails | Daily |
| **Abandoned cart** | Always | 3 emails | 1 hour, 1 day, 3 days |
| **Post-purchase** | After purchase | 3–5 emails | Spread over first 30 days |

**Output:** Each sequence as a set of email drafts with subject lines, pre-headers, body, CTA.

---

### Stage 4 — Subject lines + pre-headers (20 min)

For each email (and any external send), write 3 subject line variants.

**Three formulas** (see `subject-line-formulas.md`):
- **Curiosity** — open loop, tease the answer.
- **Specificity** — concrete number, concrete outcome.
- **Urgency / personal** — time-bound, named, direct.

Test 2 of 3 in the first send. Use the winner as the template for the rest.

**Pre-headers:** the second line in inbox. Reinforce the subject or add a second hook. Never repeat the subject.

---

### Stage 5 — Anti-pattern gate + voice check (10 min)

Two checks before copy ships.

**Anti-pattern gate** (full list in `anti-patterns-checklist.md`):
- [ ] No banned hype words (`game-changing`, `revolutionary`, etc.)
- [ ] No fake urgency ("24 hours left!" with no real deadline)
- [ ] No corporate sludge ("synergy", "leverage", "unlock value")
- [ ] No generic testimonials ("This changed my life!")
- [ ] No fake scarcity ("Only 3 spots!" with no cap)
- [ ] No buried CTAs
- [ ] No unanchored prices on the page
- [ ] No fake authority ("As seen in..." without logo rights)

**Voice check** (per `voice-and-tone-rules.md`):
- [ ] Reads like the operator (not a generic "marketing voice")
- [ ] Specific > generic throughout
- [ ] Short sentences mixed with medium (no 40-word sentences)
- [ ] Active voice dominant
- [ ] No filler phrases ("In today's fast-paced world")

---

## Deliverable shape

A complete copy package looks like:

```markdown
# Copy: [Offer Name]

**Surface:** [sales page | welcome sequence | launch | etc.]
**Goal:** [sell | capture email | book call]

## Long-form sales page (if applicable)
- Headline:
- Sub-headline:
- Problem:
- Agitation:
- Solution:
- Proof:
- Offer + Guarantee:
- CTA:

## Email sequences
- Welcome: [list of emails with subject lines]
- Pre-launch: [...]
- Open cart: [...]
- Mid-launch: [...]
- Close cart: [...]
- Abandoned cart: [...]
- Post-purchase: [...]

## Anti-pattern gate: PASS / list of items to fix
## Voice check: PASS / list of items to fix
```

---

## Anti-patterns baked in (full list)

1. **Banned hype words** — `game-changing`, `revolutionary`, `secret`, `magic`, `breakthrough`, `unlock`, `unleash`. Replace with specifics.
2. **Fake urgency** — "24 hours left!" with no real deadline.
3. **Corporate sludge** — "synergy", "leverage", "value-add", "in today's fast-paced world", "solutions-driven".
4. **Generic testimonials** — "This changed my life!" with no specifics.
5. **Fake scarcity** — "Only 3 spots!" with no actual cap.
6. **Buried CTAs** — the offer is buried below 3,000 words of setup.
7. **Unanchored prices** — prices on the page without reference.
8. **Fake authority** — "As seen in Forbes" without logo rights.

Full checklist with examples: `references/anti-patterns-checklist.md`.

---

## Voice discipline

The operator's voice is the most important copy element. Without it, copy reads as "marketing voice" — generic, soft, forgettable.

Voice rules (canonical at `voice-and-tone-rules.md`):
- **Specific beats generic.** Always.
- **Short sentences mixed with medium.** No 40-word sentences.
- **Active voice dominant.** No passive constructions.
- **No filler.** Cut every phrase that doesn't add information.
- **Operator's voice > brand voice.** The person > the corporation.

When in doubt, write like the operator would talk to a smart friend over coffee.

---

## Cross-references

| Skill | When to hand off |
|-------|------------------|
| `/offers` | **Run first.** Copy consumes the offer spec. |
| `/pricing` | **Run first.** Copy on an unanchored price reads as expensive. |
| `/launch` | After copy is locked — for the sequence of when to send what |
| `/sales-enablement` | For sales-call scripts — uses the same voice and offer |

---

## Reference files (the fat layer)

| File | Purpose |
|------|---------|
| `references/sales-page-structure.md` | The 8-section sales page, per-section checklist, word-count targets |
| `references/headline-formulas.md` | 12+ headline templates, when each works, anti-patterns |
| `references/cta-design.md` | Button copy, link copy, micro-copy, placement, first vs second person |
| `references/email-sequence-blueprints.md` | Welcome, pre-launch, open/mid/close cart, abandoned, post-purchase |
| `references/subject-line-formulas.md` | Curiosity, specificity, urgency; testing methodology |
| `references/voice-and-tone-rules.md` | The canonical voice: specific, direct, builder-oriented |
| `references/anti-patterns-checklist.md` | Full banned-moves list with examples + replacements |
