# Strong Patterns (Verifiers) — ea-closed-loop-builder

Rank-ordered verifier patterns. The verifier is the load-bearing
section of a closed-loop spec. Pick the strongest pattern that
the work surface supports — fall back to weaker patterns only
when the stronger ones don't fit.

## 1. Auto-verifiable (the gold standard)

The verifier is a deterministic check: a test, a type check, a
linter, a schema validator, an exit code, a database constraint.

**When to use:** the work has programmatic success criteria
(cron fired, file committed, test passed, type check clean,
schema valid).

**Examples:**
- "All tests in test/auth pass" (Boris Cherny's gold standard)
- "Exit code 0 from `make build`"
- "File exists at <path> with size > 0"
- "Type check clean (no `tsc --noEmit` errors)"
- "Kanban ticket moved to 'done' state"

**Why it's best:** the verifier never lies, never gets tired,
never disagrees with itself, never grades too nicely. Cost per
verification is essentially zero.

## 2. Cross-model verifier

The verifier is a different model with different weights. Boris
Cherny's pattern: the maker is M2.7, the verifier is M3 (or
vice versa). The two models will disagree on borderline cases,
which is exactly the point.

**When to use:** the work is qualitative (writing, design,
synthesis, judgment calls) and there's no deterministic check.

**Examples:**
- M2.7 drafts the post, M3 grades it on a 5-point rubric
- M3 writes the spec, M2.7 reviews for plausibility
- M2.7 implements, M3 reviews the diff

**Anti-pattern to avoid:** the verifier is the same model with
a different prompt. "Now grade your own work" is not a
verifier — it's the executor in a hat.

## 3. Cross-agent verifier

The verifier is a different agent with different instructions
and possibly different tools. The agents can be both Mavis-
side, but the agent identity is what matters.

**When to use:** the work has domain-specific quality criteria
that a generalist model misses, and a specialist agent is
available.

**Examples:**
- Content Scribe drafts, Content Verifier reviews
- Researcher compiles sources, Fact-Checker verifies
- Worker builds, Chief-of-Staff reviews for fit

**Anti-pattern:** the verifier has the same system prompt
with "but now grade this instead" appended. That's still
self-verification, just with extra steps.

## 4. Sampled human review

The verifier is a human, but only on a sample (1 in 10 runs,
or 1 per day, or 1 per 100 outputs). The sample rate is named
in the spec.

**When to use:** the work needs human judgment that no
model/agent can replicate, but the human is expensive.

**Examples:**
- 1 in 10 published posts gets a human eyeball
- 1 in 100 generated emails gets a human sanity check
- Every Monday at 9am, the operator reviews the week's
  output

**Anti-pattern:** "human review" with no sample rate defined.
That's an open-ended human time cost, not a verifier.

## 5. Pre-commit hook (the last resort)

The verifier is a pre-commit hook that gates the work from
entering the trunk. The hook can be a script, a test runner,
or a model call.

**When to use:** the loop produces artifacts that go into a
shared surface (git repo, vault, kanban) and the trunk itself
is the verification boundary.

**Examples:**
- "The pre-commit hook runs `pytest tests/` and blocks the
  commit if any test fails"
- "The hook runs `mavis doctor` and blocks if any session
  is in a broken state"
- "The hook runs the persona-banned-phrase re-grep and blocks
  if any draft contains them"

**Anti-pattern:** the hook is so lenient that everything
passes. The hook is a placebo.

## Choosing the pattern

Decision tree:
1. Can the work be checked deterministically? → Use pattern 1
2. Is the work qualitative but model-gradable? → Use pattern 2
3. Is there a specialist agent that knows the domain? → Use
   pattern 3
4. Does the work need human judgment? → Use pattern 4
5. None of the above (the work is structurally unverifiable)?
   → Don't ship as a closed loop. Use `ea-loop-thinking` to
   design, then escalate to Andre.

The pattern choice is itself a design decision. The spec
should explain WHY the chosen pattern is the right one for
this work surface.
