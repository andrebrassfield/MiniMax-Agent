---
name: sales-enablement
description: "Sales-call assets for high-ticket offers. Discovery call framework, sales call structure, objection handling, proposal templates, case study format, follow-up sequences, ROI calculator. For services, agencies, B2B, high-ticket coaching. Consumes /offers + /pricing. v2.5.0."
triggers:
  - sales enablement
  - sales call
  - discovery call
  - sales script
  - objection handling
  - sales proposal
  - proposal template
  - case study
  - ROI calculator
  - sales follow up
  - close rate
  - sales process
---

# /sales-enablement — Sales Enablement Skill (v2.5.0)

## What this skill is

Sales-call assets for high-ticket offers. The offer is locked, the price is anchored, the launch sequence has primed the buyer. This skill produces the assets the sales process needs — discovery framework, call structure, objection handling, proposal template, case studies, follow-up.

**Scope:** the sales call process itself and the assets that support it. Not for low-ticket self-serve offers (no sales call).

**Upstream:** Run `/offers` and `/pricing` first. Sales assets on a weak offer produce weak closes.

**Downstream:** Sales assets feed the actual sales conversations. This skill produces the artifacts; the operator runs the calls.

---

## When to invoke

- High-ticket offer ($2.5k+) needs a sales process.
- Conversion rate from call → close is below benchmark.
- Sales calls feel like pitches instead of help.
- Objections are recurring and unhandled.
- Proposals are inconsistent across deals.
- Follow-up is ad-hoc instead of systematic.

**Don't invoke for:** low-ticket self-serve offers (no call), offer design (`/offers`), pricing (`/pricing`), copy on sales pages (`/copywriting`).

---

## Inputs

| # | Parameter | Why it matters |
|---|-----------|----------------|
| 1 | **Locked offer spec** | From `/offers` — what you're selling on the call |
| 2 | **Locked pricing** | From `/pricing` — what they're buying |
| 3 | **Buyer profile** | Who calls you, what they need, what they object to |
| 4 | **Typical objections** | The 3–5 things that stop them from saying yes |
| 5 | **Sales call length** | 30 min vs. 60 min vs. 90 min |
| 6 | **Sales process** | One call close vs. multi-call |
| 7 | **Proposal format** | Sent after call vs. on the call |
| 8 | **CRM** | Where leads and deals are tracked |
| 9 | **Past wins** | Case studies from past buyers |
| 10 | **Buyer's alternatives** | What else they're considering |

---

## The 5-stage procedure

### Stage 1 — Build the discovery framework (45 min)

The discovery call is where the buyer qualifies themselves (or doesn't). Build the framework before running any calls.

See `discovery-call-framework.md` for SPIN-style questions.

**Key questions:**
- Situation (where are they now?)
- Problem (what's broken?)
- Implication (what does staying stuck cost?)
- Need-payoff (what would solving this be worth?)

**Output:** Discovery question list (10–15 questions, in order).

---

### Stage 2 — Build the sales call structure (45 min)

The sales call has a structure that the operator can run without thinking. Connect → Qualify → Diagnose → Prescribe → Close.

See `sales-call-structure.md` for the full structure.

**Output:** Call script with timing per section + transition phrases.

---

### Stage 3 — Build the objection-handling scripts (30 min)

The 5 most common objections get scripted responses. Not memorized — internalized.

See `objection-handling.md` for LAER framework + 12 common objections with responses.

**Output:** Objection-response pairs for the 5 most common objections.

---

### Stage 4 — Build the proposal template + case studies (60 min)

The proposal is sent after the call. It should mirror the call's structure and include 2–3 matching case studies.

See `proposal-template.md` and `case-study-format.md`.

**Output:** Proposal template + 3 case studies (or placeholders).

---

### Stage 5 — Build the follow-up sequence (30 min)

The follow-up is where most deals die. Build a sequence for post-call and post-proposal.

See `follow-up-sequences.md`.

**Output:** Post-call email + post-proposal email sequence (3–5 emails over 14 days).

---

## Anti-pattern gate

Run the anti-pattern checklist before the sales process ships.

Full list in `anti-patterns-checklist.md`:
- [ ] No pitchy discovery call (the buyer should be doing 70% of the talking)
- [ ] No "always be closing" — closing is a moment, not a vibe
- [ ] No fake scarcity on calls ("we only take 4 clients" when capacity is unlimited)
- [ ] No proposal sent without a call first
- [ ] No follow-up that asks "still interested?" without adding value
- [ ] No case studies without specifics
- [ ] No objection handling that's dismissive ("that's not really a concern")
- [ ] No price discussions without anchoring

---

## Deliverable shape

```markdown
# Sales Enablement: [Offer Name]

**Call length:** [30 min | 45 min | 60 min | 90 min]
**Process:** [one-call close | two-call close | multi-call]
**Typical close rate:** [X%]

## Discovery call framework
- Situation questions (3–5)
- Problem questions (3–5)
- Implication questions (2–3)
- Need-payoff questions (2–3)

## Sales call structure
| Section | Time | Goal |
|---------|------|------|
| Connect | 5 min | Build rapport |
| Qualify | 10 min | Confirm fit |
| Diagnose | 15 min | Find root issue |
| Prescribe | 15 min | Present offer |
| Close | 10 min | Get decision |

## Objection handling
[5 objection-response pairs]

## Proposal template
[Standard sections with placeholders]

## Case studies
[3 case studies with specifics]

## Follow-up sequence
[Post-call + post-proposal emails]

## Anti-pattern gate: PASS / list of items to fix
```

---

## Anti-patterns baked in (full list)

1. **Pitchy discovery call** — operator talks 70%+, buyer feels pitched, doesn't open up.
2. **"Always be closing"** — pressure throughout the call. Buyer feels sold, not helped.
3. **Fake scarcity on calls** — "we only take 4 clients" when capacity is unlimited.
4. **Proposal without a call** — sending a generic proposal to a cold lead.
5. **Follow-up that asks "still interested?"** — adds no value.
6. **Case studies without specifics** — "we helped them grow" with no numbers.
7. **Dismissive objection handling** — "that's not really a concern."
8. **Price without anchoring** — quoting the price on the call without a reference.
9. **Multi-call process without value at each stage** — dragging the buyer through calls.
10. **Closing attempts before diagnosis** — pushing for close before understanding the buyer's situation.

Full checklist: `references/anti-patterns-checklist.md`.

---

## Sales process archetypes

### One-call close (30–60 min)

**Best for:** mid-ticket ($2.5k–$10k) where the buyer has done their research and is ready to decide.

**Structure:** Discovery + diagnosis + prescribe + close, all in one call.

**When to use:** The buyer comes to the call knowing the price range and the offer. The call confirms fit.

### Two-call close

**Best for:** high-ticket ($10k–$25k) where the buyer needs setup time.

**Structure:**
- Call 1: Discovery + diagnosis + light prescribe.
- Call 2 (3–7 days later): Deep prescribe + close.

**When to use:** The buyer needs time to process the offer or involve stakeholders.

### Multi-call (3+ calls)

**Best for:** very high-ticket ($25k+) or B2B where multiple stakeholders are involved.

**Structure:**
- Call 1: Discovery.
- Call 2: Diagnosis + recommend proposal.
- Call 3: Stakeholder call.
- Call 4: Final close.

**When to use:** Enterprise sales where buying is committee-driven.

---

## Cross-references

| Skill | When to hand off |
|-------|------------------|
| `/offers` | **Run first.** Sales assets consume the offer spec. |
| `/pricing` | **Run first.** Sales assets consume the pricing. |
| `/copywriting` | For the post-call email copy + proposal copy |
| `/launch` | For launches that include sales calls (high-ticket cohort launches) |

---

## Reference files (the fat layer)

| File | Purpose |
|------|---------|
| `references/discovery-call-framework.md` | SPIN-style questions, qualifying, listening for fit |
| `references/sales-call-structure.md` | Connect → Qualify → Diagnose → Prescribe → Close |
| `references/objection-handling.md` | LAER framework + 12 common objections with responses |
| `references/proposal-template.md` | Standard sections, what to include, anti-patterns |
| `references/case-study-format.md` | Before/after/bridge format + worked example |
| `references/follow-up-sequences.md` | Post-call + post-proposal email sequences |
| `references/anti-patterns-checklist.md` | Full banned-moves list with examples + replacements |
