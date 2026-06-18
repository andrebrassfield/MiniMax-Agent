# Stage 1 Eval Cases — Fluff Purge

Stage 1 is mechanical. The eval verifies that the regex actually fires on
real banned phrases and does NOT fire on false positives.

## T1.1 — Real match, all 12 categories

**Input draft snippet (mock):**
> "Let's dive into the world of AI automation. In today's fast-paced
> landscape, it's not just about productivity, it's about survival.
> Harness the power of seamless integration. The truth is, this is a
> game-changer."

**Expected output:**
- 5+ Stage 1 matches (dive into, in today's fast-paced landscape, not
  just about X it's about Y, harness the power of, the truth is,
  game-changer)
- Each match has a verbatim original + suggested fix
- All fixes preserve the load-bearing claim

**Failure mode this catches:** the regex doesn't fire on real matches
(probably broken regex).

## T1.2 — False-positive guard

**Input draft snippet (mock):**
> "I dove into the codebase yesterday. Diving boards at the pool were
> closed. The Diver movie was on TV."

**Expected output:**
- "dived/dove/diving" should NOT match `\bdive\s+into\b` (the word
  boundary is on "into", not on "dive")
- Zero Stage 1 matches for the "dive" family of words

**Failure mode this catches:** the regex is too loose (matches on
substring, missing the `\b` word boundary).

## T1.3 — Case-insensitive

**Input draft snippet (mock):**
> "DIVE INTO this. Let me DELVE INTO that."

**Expected output:**
- Both match the regex
- The output uses the original casing from the draft, not lowercased

**Failure mode this catches:** the regex is case-sensitive (the original
spec called for case-insensitive).

## T1.4 — Em-dash filler meta-rule

**Input draft snippet (mock):**
> "The 12% drop is real — and that's why we need to act. Revenue fell
> 22% — which means the second quarter is at risk."

**Expected output:**
- Both em-dash constructions flagged
- Suggested rewrites that don't use the em-dash-as-conjunction tic

**Failure mode this catches:** the meta-rule isn't being applied.

## T1.5 — Medium-article opener meta-rule

**Input draft snippet (mock):**
> "In this post, I'll explore why AI voice agents fail. Here's what I
> learned after 100 deployments."

**Expected output:**
- Both openers flagged
- Suggested rewrites that lead with the load-bearing claim, not the
  meta-commentary

**Failure mode this catches:** the opener meta-rule isn't being applied.
