---
name: ea-state-audit
description: |
  Diagnostic skill that audits Mavis's current state vs a named framework
  (thin-harness, two-track, garry-tan-discipline, etc.), enumerates gaps in
  priority order, and proposes dial-ins. Takes FRAMEWORK, SURFACE, OUTPUT.
node_type: agent_parameter
parameter_id: ea-state-audit
generation: 1
fitness_score: null
last_optimized: null
---

# ea-state-audit

## When to use

- "audit my state vs framework X" / "what gaps in Mavis"
- "dial in [domain]" / "what's bleeding tokens"
- After a major architecture change (pivot, new model, new fleet member)
- Quarterly operating-model review

## Parameters

- **FRAMEWORK** — which framework to audit against. Options:
  - `thin-harness-fat-skills` (sairahul1 / Yegge) — 5 defs: skill files / harness / resolvers / latent-vs-deterministic / diarization
  - `two-track` (Tiago Forte) — spec throughput bottleneck, single Track 2 per spec
  - `garry-tan-discipline` — codify-after-3-runs, no one-off work
  - `memory-architecture` — vault = long-term, MEMORY.md = pointers
  - Custom (provide framework name + reference)
- **SURFACE** (optional) — limit audit to a specific surface. Options:
  - `always-on-context` (SOUL / MAVIS / MEMORY sizes + drift)
  - `skills` (descriptions, sizes, missing skills)
  - `crons` (registration, failure rates, redundancy)
  - `memory` (MEMORY.md size + topic files)
  - `harness` (CLI surface, MCPs, latency)
  - `routing` (resolver quality)
  - Default: all surfaces
- **OUTPUT** (optional) — output file path. Default: `00 Inbox/state-audit-<FRAMEWORK>-YYYY-MM-DD.md`

## The 5-step procedure

### Step 1 — Read the framework

Load the framework's reference doc. If custom framework, ask user for the doc path or a 2-3 sentence summary. Anchor your gap-detection in the framework's actual claims — don't improvise.

### Step 2 — Read the surface

For each surface in scope (from SURFACE param or all surfaces):
- Inventory the current state. Use deterministic CLI where possible:
  - `wc -c <file>` for always-on context sizes
  - `mavis usage list --json` for token burn
  - `mavis cron list <agent>` for cron registry
  - `ls + wc` for skill counts
  - `mavis memory tail` for recent memory state
- Capture: actual state, target state (from framework), delta.

### Step 3 — Enumerate gaps

For each surface, list every gap between actual and target. Tag each gap:
- **High urgency** — actively causing harm (token bleed, recurring failure, user pain)
- **Medium leverage** — would unlock future work
- **Low leverage** — nice-to-have, document and move on

### Step 4 — Prioritize dial-ins

Sort gaps by urgency × leverage. Propose 3-7 dial-ins in priority order, each with:
- **Move** (one-line description)
- **Files affected**
- **Token impact** (estimated savings or spend)
- **Time** (estimated minutes)
- **Reversibility** (green / yellow / red action class)
- **Done criteria** (verifiable)

### Step 5 — Write output

Write to `OUTPUT` (default `00 Inbox/state-audit-<FRAMEWORK>-YYYY-MM-DD.md`). Format:

```markdown
---
type: state-audit
framework: <FRAMEWORK>
surface: <SURFACE | all>
date: YYYY-MM-DD
token-budget-used: <estimated K>
---

# State Audit — <FRAMEWORK> — YYYY-MM-DD

## Current state summary
<2-3 sentences>

## Gaps by priority

### High urgency (fix first)
- [gap 1] — evidence, dial-in pointer
- [gap 2] — ...

### Medium leverage
- ...

### Low leverage (document, skip)
- ...

## Proposed dial-ins (priority order)
| # | Move | Files | Token impact | Time | Reversibility | Done criteria |
|---|---|---|---|---|---|---|
| 1 | ... | ... | ... | ... | ... | ... |

## Recommended next action
<one paragraph — what to do first, what to defer, what to escalate to Andre>

## Cross-references
- Framework reference: <doc path or URL>
- This audit output: <path>
- Related decisions: <list>
```

## Worked example (the canonical case)

The skill was codified on 2026-06-22 from the audit that produced the **MiniMax Token Plan Dial-In** (spec at `03 Projects/Mavis EA Design/specs/minimax-token-dialin-2026-06-22.md`).

Inputs:
- FRAMEWORK = `thin-harness-fat-skills`
- SURFACE = `all`
- OUTPUT = `03 Projects/Mavis EA Design/specs/minimax-token-dialin-2026-06-22.md` (used spec file as both audit output AND execution spec — collapsed them)

Audit findings (the 5 gaps that became dial-ins):
1. **mmx quota doesn't exist** — rate-limit-tracker broken → Dial-in #1
2. **MAVIS.md 32KB** (always-on bloat) → Dial-in #2
3. **SOUL.md 20KB** (operating contract creep) → Dial-in #3
4. **No resolver table** → Dial-in #4
5. **38 verbose skill descriptions** → Dial-in #5
6. **No `state-audit` skill itself** → Dial-in #6 (this skill)

## Hard rules

1. **Use deterministic CLI for state reads.** `wc -c`, `mavis usage list --json`, `mavis cron list`, `ls`. Don't rely on memory or approximation.
2. **Anchor gaps in the framework's actual claims.** Don't invent criteria the framework doesn't endorse.
3. **Every dial-in must have a verifiable done criterion.** "Make it better" is not a criterion.
4. **Reversibility tag is mandatory.** Green/yellow/red — and if red, surface before proposing.
5. **Total dial-in time estimate should be ≤8 hours.** If bigger, split or escalate to a spec block for Andre.
6. **Output is a markdown file, not chat.** Audit findings live on disk for future reference.

## Cross-references

- Origin: MiniMax Token Plan Dial-In (2026-06-22) — spec at `03 Projects/Mavis EA Design/specs/minimax-token-dialin-2026-06-22.md`, ledger at `03 Projects/Mavis EA Design/minimax-token-dialin-ledger-2026-06-22.md`
- Frameworks:
  - thin-harness-fat-skills — article referenced in `MAVIS.md` "What Andre is reading"
  - two-track — `02 Notes/decisions/2026-06-22-two-track-model.md`
  - garry-tan-discipline — user memory entry on codify-after-3-runs
- Topic files: `agent-harness-principles.md` (12-component checklist)
- Cron: optional `state-audit-quarterly` cron (Sunday every 13 weeks) — not yet registered
