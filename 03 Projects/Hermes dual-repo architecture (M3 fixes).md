---
type: project
status: active
started: 2026-06-02
priority: medium
source_session: "[[2026-06-02 - Hermes workspace cleanup session]]"
---

# Hermes dual-repo architecture (M3 fixes)

## Goal

Document the **two-repos pattern** for the Hermes-side M3 rollout: the same symptom (truncated JSON output on M3) has two different fixes, at two different layers, in two different repos. Both are required.

## Why this matters

Hermes is not one repo. The M3 fixes that worked in the 2026-06-02 cleanup session are split across two upstream forks that Andre maintains, each with its own layer of responsibility. Confusing them — or fixing only one — is how you end up with "M3 works in dev, breaks in prod" or "M3 is flaky, must be the model."

## The two repos

### 1. `self-evolution` — Python / DSPy (NousResearch upstream)
- **Layer**: application
- **What it is**: the DSPy-based self-evolution stack — the part of Hermes that does prompt optimization, eval, and skill evolution in Python
- **M3 symptom here**: output JSON gets clipped at the **application-layer `max_tokens` cap** (the 8192 ceiling that surfaced on 2026-06-02)
- **Fix shape**: raise / unset the `max_tokens` cap so M3's native 128k+ output budget is actually available to the DSPy signature calls
- **Why it has a cap at all**: the cap is inherited from M2.7-era defaults (M2.7 had a 40k output cap per agent memory); when M3 swapped in, the cap didn't follow

### 2. `oh-my-pi` — TypeScript / provider (can1357 upstream)
- **Layer**: framework
- **What it is**: the TypeScript provider layer — the bridge between Hermes' framework code and the actual LLM API call
- **M3 symptom here**: even if `self-evolution` raises its app-layer cap, completions are still clipped because the provider's `transformModel` override is silently re-imposing an old ceiling
- **Fix shape**: override the `transformModel` to pass through M3's real budget; the provider layer needs to stop clamping
- **Why both layers**: the framework's `transformModel` is a separate code path from the application's `max_tokens` — they compose, and *both* must allow the larger budget for the larger budget to actually flow through

## The insight

Same symptom, two layers, both need to change. This is **not** a "fix it in one place and it'll be fine" situation. It's a "the cap exists in two independent code paths, and each one can independently clip the output" situation.

If you only fix `self-evolution` (the app-layer cap), completions still get clipped at the provider's `transformModel` and you see "we raised the cap, why is it still truncated?"

If you only fix `oh-my-pi` (the provider override), the DSPy signatures still pass an 8192 budget down to the provider, and the provider is happy to give you 8192 tokens of an M3 model that could do 128k+

Both. Always both.

## Cross-repo coordination pattern

From the 2026-06-02 cleanup session, the working order was:
1. Prune worktrees
2. Migrate to M3
3. Discover the 8192 cap (one cap, but the *fix* has two surfaces)
4. Identify the dual-repo insight
5. Bundle the M3 migration + cap fix into local commit `0cb3a5a`
6. Take a vault snapshot
7. Log deferrals

The dual-repo fixes themselves are a *next* session's work — they were deferred because the discovery is the value, and rushing the actual rollout across two repos without a clean separation would create a worse mess than the cap.

## Validation

**Stress-Test Prompt.** A single end-to-end test that exercises both layers at once. The test constructs a prompt that deterministically forces a >10k token response, routes it through both `self-evolution` (DSPy signature) and `oh-my-pi` (provider), and asserts the response is not truncated at any layer.

**Test design:**
- **Input prompt:** "List the first 2500 prime numbers, one per line, formatted as 'N: M' where N is the index (1, 2, 3, ...) and M is the prime. After each prime, include a 4-word note on its primality (e.g., 'divisible only by 1 and self')." This deterministically produces ~10,500 output tokens.
- **DSPy signature** (self-evolution layer, app-layer cap): `dspy.Signature("prime_list: str -> long_output: str = dspy.OutputField(description='full list', min_tokens=10000)")` — the signature declares the required output size, exposing the app-layer `max_tokens` cap.
- **Provider call** (oh-my-pi layer, framework-layer override): routes the call to M3 with the model's native output budget, exposing any silent re-clamping in `transformModel`.
- **Assertions:** `output_tokens >= 10000`, `not response.long_output.endswith('...')`, no truncation error string at the end of the response.
- **Failure mode:** if either layer still clamps, the response truncates (caps at 8192 or lower), the test fails. The test does NOT distinguish which layer clipped — that's the whole point. **Both. Always both.**

**Why one test, not two.** Splitting into "test app-layer cap" + "test provider-layer cap" defeats the rule. A partial fix that only unblocks one layer would pass a layer-specific test and silently fail the integration. The dual-repo discipline is enforced by a single test that fails if either layer is broken.

**How to run the test** (when the time comes): from the Hermes workspace, construct the signature and prompt, invoke the predictor against M3, count output tokens, assert the threshold. Run in a CI lane or a dedicated smoke-test session — NOT in production routing, because the test deliberately stresses both layers with a >10k token payload. Plan for ~30s wall, ~10k+ output tokens, single round-trip.

## Why I'm allowed to write this from EA mode

This project note describes the **architectural pattern**, not the code. I can name the repos and the layer each fix lives at because Andre told me in the 2026-06-02 capture session. I cannot (and will not) reach into `~/.hermes/` to quote line numbers from `self-evolution/...` or `oh-my-pi/...` — that would violate SOUL.md's fleet-off-limits constraint.

## Connections

- [[2026-06-02 - Hermes workspace cleanup session]] — the session this insight came out of
- [[learnings]] § "Migration notes: M2.7-highspeed → M3" — broader M3 migration context
- [[M3 Capabilities]] — model spec the caps were wrong about
- [[Hermes Version]] (in user profile, 2026-05-19 update) — v2026.5.16 is the version this all happened against
- [[Gibson V4 Architecture — Hermes-Native]] (in user profile, 2026-05-26) — the broader Hermes-native stack these repos sit inside
- User memory entry `Hermes two-repo layout` — one-liner summary for future cross-session reference
- [[2026-06-01-040-audit-before-action]] — the instinct that drove the "snapshot before dual-repo rollout" decision

## Next Action

**Trigger:** Schedule the dual-repo rollout as a single session once self-evolution main passes v0.X or at the start of the next Hermes cycle.

**Rollback:** If either fix fails validation, revert both to maintain state synchronization.

The actual cross-repo rollout of the two fixes is **out of scope for EA mode** — it must be done by Hermes (or by Andre directly in the Hermes workspace), not by Mavis.

What Mavis *can* do next: if Andre asks, draft a one-pager explainer of the dual-repo pattern for Hermes' own context (so the insight survives the next context-compaction), or a checklist of the validation steps to run once both fixes are deployed.
