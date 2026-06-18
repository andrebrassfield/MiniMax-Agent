# Stage 2 Eval Cases — Voice-Injection

Stage 2 is judgment-call. The eval verifies that the polite/academic
patterns are caught and the proposed rewrites match the persona's staccato
voice — not that the rewrites are auto-applied.

## T2.1 — Polite opener

**Input draft snippet (mock):**
> "It is important to note that 27% of SMB leads are missed by HVAC
> companies. Furthermore, the median response time is 4 hours."

**Expected output:**
- Stage 2 flags "It is important to note that" and "Furthermore"
- Proposed rewrites:
  - "27% of SMB leads are missed by HVAC companies."
  - "And the median response time is 4 hours." (or just delete the
    "Furthermore" sentence)
- The rewrites preserve the numbers (27%, 4 hours)

**Failure mode this catches:** the rewrite loses a load-bearing number
or name.

## T2.2 — Long compound sentence (3+ clauses)

**Input draft snippet (mock):**
> "When the integration fails, which happens 12% of the time, the
> inventory drift can compound, leading to overselling."

**Expected output:**
- Stage 2 flags as a long compound sentence
- Proposed rewrite splits into 3 staccato beats:
  - "Integration fails 12% of the time."
  - "Inventory drifts."
  - "Overselling."
- The 12% number is preserved

**Failure mode this catches:** the rewrite is still 1 long sentence
(judgment-call failed — the split is the load-bearing move).

## T2.3 — Hedging rewrite loses specificity

**Input draft snippet (mock):**
> "One might consider that the 47 deployments we tracked showed
> $3,800 in lost revenue per dispatcher per month."

**Expected output:**
- Stage 2 flags "One might consider that"
- Proposed rewrite MUST preserve "47 deployments" and "$3,800"
- If the rewrite drops the numbers, the eval flags "load-bearing
  detail lost" — Andre should be alerted

**Failure mode this catches:** the rewrite is more fluent but loses the
specifics. The persona's voice is staccato AND specific; fluency alone
isn't the goal.

## T2.4 — Clean draft (no polite patterns)

**Input draft snippet (mock):**
> "47 deployments. $3,800 lost per dispatcher per month. The fix is
> a 3-line Zapier that costs $20/mo."

**Expected output:**
- Zero Stage 2 matches
- The eval verifies: "No matches — academic/polite register absent.
  Staccato rhythm holds."

**Failure mode this catches:** the false-positive rate is too high
(flagging the draft as needing rewrite when it doesn't).

## T2.5 — Discipline check: no auto-rewrite

**Input:** Any Stage 2 match

**Expected output:**
- The original is preserved at the bottom of the draft's section
- The rewrite is a PROPOSAL, not applied
- Andre's accept/reject checkboxes are present

**Failure mode this catches:** the skill auto-rewrites instead of
proposing. The Humanizer is a refinement layer, not a Scribe replacement.
