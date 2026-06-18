---
type: cross-reference
date: 2026-06-10
subject: Self-Harness paper (arXiv 2606.09498) vs Hermes `self-improving-loop` skill
sources:
  - DreBrain/papers/self-harness-2606-09498.md
  - ~/hermes-skills/skills/self-improving-loop/{skill.md, impl.py}
  - ~/hermes-skills/skills/skill-quality-evaluator/SKILL.md (lines 185-198)
  - ~/.hermes/memories/MEMORY.md (line 32, pre-existing summary)
  - ~/.hermes/profiles/{coder,self-improver,researcher}/SOUL.md (bundle sites)
---

# Self-Harness paper ↔ `self-improving-loop` skill

## TL;DR

The paper **validates** what `self-improving-loop` is trying to do and gives it a formal name + a 3-stage pipeline. It does **not** invalidate the skill, but it does reveal **two concrete gaps** the skill should close if we want it to actually do what the paper describes:

1. **Weakness Mining** — the skill does not actually mine failure traces. It watches *usage counts* (loads, last-loaded timestamps) and counts research findings. It does not look at *what went wrong* when a skill was used.
2. **Proposal Validation** — the skill generates PR-ready suggestions and stops there. It does not run a regression test before accepting an evolution. The paper specifically calls this out as load-bearing.

Everything else in the skill (enhancement / deprecation / pattern / test-coverage categories, triggers, output schema) maps cleanly onto the paper's framing.

## Mapping table

| Self-Harness stage | Paper says | `self-improving-loop` does | Gap |
|---|---|---|---|
| **Weakness Mining** | Identify model-specific failure patterns from execution traces | Watches skill load counts + last-loaded timestamps; counts research findings by topic | **Real gap.** No trace mining. The "weakness" signal is just "loaded 10+ times" or "research topic has 3+ findings." A skill that succeeds badly (high load, low quality outcomes) is invisible. |
| **Harness Proposal** | Generate diverse yet minimal harness modifications tied to failures | Generates suggestions across 5 categories: enhancement, new_skill, deprecation, pattern, test_coverage | Mostly aligned. Output schema is PR-ready (lines 73-91 of skill.md). The "minimal" constraint from the paper is not enforced — a suggestion can recommend a 500-line modularization without bounded scope. |
| **Proposal Validation** | Accept candidate edits only after regression testing | Stops at suggestion output. Writes suggestion to disk via `_update_stats`, but does not run a test or score. | **Real gap.** The skill-quality-evaluator integration (skill-quality-evaluator/SKILL.md:185-198) gives a *static* score but is not wired into the loop as a regression gate. No "before/after" comparison, no benchmark, no eval. |

## What's already strong in the skill

- **Output schema is concrete and PR-ready** (skill.md:73-91). type, target_skill, suggestion, reason, priority, pr_ready. This is genuinely better than the paper's prose description — it can plug straight into a CI.
- **Triggers are well-shaped** (skill.md:62-69). Six explicit triggers including the meta-trigger "Dre says 'remember this'" and "New agent type added (Mavis)." These are higher-quality than what the paper implies.
- **The loop is observable.** `_analyze_usage` reads from `usage_stats.json`, `_update_stats` writes back. There is a stats file you can grep. Good.
- **The skill-quality-evaluator integration exists as a design intent** (lines 185-198 of skill-quality-evaluator/SKILL.md) — "Skills below 60 composite score get automatic evolution suggestions." That's the paper's validation stage, sketched but not yet wired.

## Concrete deltas to consider (not committed, just options)

These are the changes that would close the two gaps above. **Do not action without Andre's call** — this is a design surface, not a plan.

### Delta A — close the Weakness Mining gap

Add a `_mine_failures()` method to `SelfImprovingLoop` that reads from sources the workers actually produce:
- Hermes's worker session logs (`~/.hermes/sessions/...` or wherever the watchdog writes traces)
- The kanban DB's `cancelled` / `spawn_failed` events
- `verifier` skill verdicts (when a worker output fails verification, that's a failure pattern)

Output: a list of `{pattern, frequency, last_seen, suggested_skill_to_evaluate}` records. Feed these into the suggestions list as `weakness_mined` type suggestions, separate from `enhancement` and `deprecation`.

This is the single highest-value change. Without it, the skill is "counting what gets used" not "finding what breaks."

### Delta B — close the Proposal Validation gap

Two sub-options, cheap-to-expensive:

**B1 (cheap):** Require every `pr_ready: true` suggestion to also include a `regression_check` field pointing at an existing test file or eval. If no regression check is provided, downgrade `pr_ready` to `false`. This is a schema change, ~10 lines.

**B2 (expensive, more aligned with paper):** Wire `skill-quality-evaluator` into the loop as a pre-acceptance gate. Before a suggestion becomes `pr_ready`, run the evaluator against the target skill. If the score is below 60 *or* the suggestion doesn't improve the score, mark `pr_ready: false` with reason "no measurable improvement."

B2 is what the paper actually describes. B1 is a 90/10 version.

### Delta C — bound the proposals

Add a `scope` field to the suggestion schema: `bounded` (≤20 lines changed, no new files) / `moderate` (≤100 lines or one new file) / `large` (anything else). Default to `bounded` for `pr_ready: true`. This enforces the paper's "diverse yet minimal" requirement mechanically.

## What this is NOT

- This is **not** a critique of the skill. It is the right shape, written before the paper formalized the shape. The paper is the citation; the skill is the implementation.
- This is **not** an action plan. Andre decides whether to invest in closing the gaps. The cost of closing them is real worker time and a new signal pipeline for Delta A.
- This is **not** a request to rewrite the skill. The 5 categories, the triggers, the output schema, the stats file — all of that survives the cross-reference intact.

## The honest verdict

The skill as written is **observational**, not **self-improving** in the paper's sense. It tells you *what's being used*, not *what's breaking*, and it stops at *suggesting* instead of *validating*. Closing both gaps is the difference between "a skill that watches the library" and "an agent that improves its own operating harness" — which is the literal title of the paper.

If we close one gap, close Delta A. That's where the failure-pattern signal lives, and we already have the trace data (kanban events, verifier verdicts, session logs). Delta B is policy work; Delta A is plumbing.
