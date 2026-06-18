# Stage 3 Eval Cases — Conflict Check

Stage 3 is the load-bearing stage. The eval verifies that the 5 criteria
fire correctly, the hot-take proposal matches the persona's voice, and the
FAIL path always proposes a hot-take (never silently passes).

## T3.1 — PASS: counter-intuitive claim (Criterion 1)

**Input draft snippet (mock):**
> "Plumbers should NOT build an AI voice agent. Here's why.
> [supporting data...]"

**Expected output:**
- Stage 3 PASSES
- Which criteria: "Criterion 1: counter-intuitive claim — the post
  directly contradicts the persona's usual 'build AI for SMB' stance"
- Verbatim quote: "Plumbers should NOT build an AI voice agent."

**Failure mode this catches:** the eval misses a clear PASS.

## T3.2 — PASS: "the cons win" pivot (Criterion 2)

**Input draft snippet (mock):**
> "AI voice agents will save you $3,800/mo. They will also fire your
> best dispatcher. That second part is the real cost."

**Expected output:**
- Stage 3 PASSES
- Which criteria: "Criterion 2: 'the cons win' pivot — the load-bearing
  element is the downside (firing the dispatcher), not the savings"

**Failure mode this catches:** the eval only looks at the opening line
and misses the contrarian element in the second beat.

## T3.3 — FAIL: consensus-only draft

**Input draft snippet (mock):**
> "AI voice agents are a useful tool for HVAC companies. They save
> time and money. Many companies have adopted them successfully."

**Expected output:**
- Stage 3 FAILS
- Why: "The draft's load-bearing claim is 'AI voice agents are useful.'
  That's consensus, not contrarian. Median reader in the niche would
  agree, not push back."
- Proposed hot-take: 1-2 sentences that introduce a counter-intuitive
  opinion (e.g., "Every 'AI for HVAC' tool is a wrapper. The 47
  deployments I tracked showed the same 22% miss-rate pre- and
  post-adoption.")
- Where to insert: a specific location in the existing post

**Failure mode this catches:** the FAIL path is missing (the skill
silently passes a consensus draft).

## T3.4 — FAIL: hot-take breaks rhythm

**Input draft snippet (mock):**
> Consensus draft. Proposed hot-take is 2 sentences of academic
> register: "It is important to note that the deployment success rate
> varies considerably across implementations, with some studies
> suggesting that..."

**Expected output:**
- The hot-take is REJECTED
- Surface to Andre with the rhythm mismatch
- Do NOT force the bad insert
- Propose an alternative hot-take in staccato voice

**Failure mode this catches:** the hot-take itself is AI-flavored
(circular regression — the Humanizer generating AI text in the
"anti-AI" stage).

## T3.5 — Discipline check: hot-take is a natural extension

**Input:** A FAIL draft. Proposed hot-take introduces a topic unrelated
to the existing claim.

**Expected output:**
- The hot-take is REJECTED (per Hard Rule 7: "Never invent hot-takes
  from nothing")
- The Humanizer proposes an alternative hot-take that connects to the
  existing claim
- Surface to Andre with the rationale

**Failure mode this catches:** the hot-take is a tangent to Y when the
post is about X.

## T3.6 — Character count discipline

**Input:** A FAIL draft. The proposed hot-take, inserted, would push the
post past 280 chars.

**Expected output:**
- The Humanizer trims the humanized version to fit ≤280 chars
- The trim is FLAGGED in the diff
- The hot-take is preserved (the trim comes from the existing text, not
  the hot-take)
- Per Hard Rule 9: character count discipline

**Failure mode this catches:** the hot-take silently pushes the post
past 280 chars, breaking the Scribe's char-limit contract.
