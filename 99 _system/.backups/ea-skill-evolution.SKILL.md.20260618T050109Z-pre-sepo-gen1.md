---
name: ea-skill-evolution
description: |
  Operational skill that consumes the lesson brief from
  `session-lesson-extractor` and runs the GEPA-anchored self-evolution
  loop to mutate existing skills, generate new ones, and propose
  memory candidates. This is the engine that the lesson extractor's
  suggestion engine feeds — together they close the "loops that don't
  write back to memory" gap (see `ea-loop-thinking`, the MEMORY
  building block). Anchors in GEPA (Agrawal et al., arXiv 2507.19457),
  the Gao et al. self-evolving-agents survey (arXiv 2507.21046, 4-axis
  What/When/How/Where), Alita-G (arXiv 2510.23601), and MUSE-Autoskill.
  Triggers on (a) a fresh `session-lesson-extractor` brief at
  `03 Projects/Mavis EA Design/reports/lesson-extract-*.md`,
  (b) Andre's "evolve the skill library" / "what should we codify" /
  "we keep correcting the same thing", or (c) the EA weekly reflection.
  **This skill proposes mutations and scaffolds; Mavis reviews and
  commits. It does NOT auto-write to memory, auto-archive skills, or
  auto-publish drafts.** The skill is the proposer; the EA is the
  gate. Do NOT load for one-off sessions with no extract, for ad-hoc
  memory writes (use the standard `mavis memory append` flow), or
  for skill work in other agents' trees (Mavis territory only).
# === TPG (Cognitive Parameter Graph) layer - added 2026-06-17 ===
# Phase 1 codification: schema-only, no SePO loop running yet.
# Phase 2 will populate fitness_score, last_evaluated, etc. via sepo-runner.
node_type: agent_parameter
parameter_id: ea-skill-evolution
generation: 1
fitness_score: null
last_optimized: null
last_evaluated: null
mutation_count: 0
schema_version: 1
# purpose: GEPA-anchored skill mutation proposer; gates, never auto-commits
---

# ea-skill-evolution

The self-evolution engine behind the MEMORY building block. A loop
that doesn't write back to its own corpus re-derives everything
from zero on the next run. This skill closes the loop by turning
the `session-lesson-extractor` brief into proposed evolutions of
the Mavis skill/memory corpus.

## Intent

- Take the lesson brief from `session-lesson-extractor`
- For each HIGH-durability candidate: classify on the 4 axes
  (What/When/How/Where)
- Generate a proposed evolution: new skill scaffold, mutation to
  existing skill, or memory candidate
- Stage the proposal (do NOT apply)
- Audit against the Mavis-side gates
- Surface the manifest to Mavis for review
- Mavis commits what passes; discards what doesn't

The model decides *which* mutations close which gaps. The
deterministic layer (4-axis classification, manifest format, audit
gates, mirror discipline) lives in `references/`. Safety halts and
discipline checks live in `tests/`.

## When to run

**Triggers:**
- A fresh `session-lesson-extractor` brief lands at `03 Projects/Mavis EA Design/reports/lesson-extract-YYYY-MM-DD.md`
- "evolve the skill library" / "what should we codify"
- "I keep correcting the same thing" (memory entry exists, skill hasn't been updated)
- "this skill is missing a case" / "the skill said X but the work needed Y"
- Weekly cadence (Sunday evening, paired with the lesson extractor's schedule)
- After 3+ corrections in a week

**Do NOT run for:**
- One-off sessions with no extract
- When the corpus is already up to date (run `ea-data-quality-audit` first)
- Ad-hoc memory entries (use `mavis memory append` directly)
- Skill work in other agents' trees (Mavis territory only)
- Without first running `ea-loop-audit` on the target skill (need a baseline)

## Inputs

| Input | Default | Required |
|---|---|---|
| `lesson-extract-YYYY-MM-DD.md` brief path | — | yes |
| Target surface | `skills` | no |
| Mutation budget (max proposals per run) | 5 | no |
| Risk threshold | `pause-and-flag` | no |

## Output contract

A proposed-evolution manifest at
`~/.mavis/agents/mavis/skills/ea-skill-evolution/manifest.jsonl` (one
JSONL line per proposed change) plus scaffolded SKILL.md / mutation
diffs in a staging area at `~/.mavis/agents/mavis/skills/ea-skill-evolution/staging/`.

Mavis reviews the manifest, commits what passes, discards what
doesn't. The skill is the proposer; the chief is the gate.

The manifest format, the 4-axis classification, the audit gates,
and the mirror discipline are in `references/`.

## Resolver

Auto-invoke when:
- A fresh `session-lesson-extractor` brief lands
- Andre says "evolve the skills" / "what should we codify" / "we keep correcting the same thing"
- The weekly reflection cron fires
- 3+ corrections to the same surface in a week (the recurring-correction signal)

Do NOT auto-invoke for:
- One-off sessions
- When the corpus is up to date
- Skill work in other agents' trees
- Without a baseline (`ea-loop-audit` on the target)

## Hard constraints (the load-bearing discipline)

1. **Never write to memory autonomously.** Memory writes are Mavis's decision, with Andre's approval for non-trivial entries. Stage the proposal; Mavis commits.
2. **Never write to canonical skill paths autonomously.** Stage in `ea-skill-evolution/staging/` first. Mavis moves to canonical after review.
3. **Never evolve a skill that has not been `ea-loop-audit`-ed.** The baseline is mandatory. Evolving a broken skill compounds the bug.
4. **Never evolve across the regulated-domain boundary without halting.** Any proposal touching medical, legal, credit, employment, biometric, or critical infrastructure: pause and flag. The Mavis EA reviews; the skill does not proceed.
5. **Mutations are surgical.** One section, one trigger phrase, or one description tweak at a time. Per GEPA discipline: smallest change that closes the gap. If the gap requires a full rewrite, surface that as a separate "scaffold-new" proposal.
6. **Mirror discipline (home == mirror, sync gate).** Every canonical write to `~/.mavis/agents/mavis/skills/<name>/SKILL.md` MUST be followed by a mirror write to `~/MiniMax-Agent/99 _system/skills/<name>/SKILL.md` AND a `cmp` verification that both files are byte-identical. The mirror step is a precondition for `status: shipped` — proposals that fail the mirror step are held in `status: mirror-pending`, NOT `shipped`.
7. **Mavis territory only.** Do not propose evolutions to Hermes skills, OpenClaw skills, Socratic, or any other agent's tree. Cross-team proposals go through Mavis (who decides whether to route to the other team).
8. **Manifest is append-only.** The JSONL is the audit trail. Never edit past entries; if a decision reverses, append a new entry referencing the old one.

## Cross-reference

- `references/4-axis-framework.md` — the What/When/How/Where classification
- `references/manifest-format.md` — the JSONL schema
- `references/audit-gates.md` — the 5 gates (mistakes, loop, data quality, regulated, brief-evidence)
- `references/mirror-discipline.md` — the home-equals-mirror sync gate
- `references/proposal-types.md` — new / mutate / memory-candidate shapes
- `tests/safety-halts.md` — no-baseline, regulated-domain, cross-team, autonomous-write
- `tests/mutation-discipline.md` — surgical mutations, smallest-change rule
- `tests/mirror-discipline.md` — the byte-identity gate
- `session-lesson-extractor` (Mavis skill) — produces the input brief
- `ea-loop-thinking` (Mavis skill) — the 5-stage loop vocabulary
- `ea-5-mistakes-audit` (Mavis skill) — the audit gate #1
- `ea-loop-audit` (Mavis skill) — the audit gate #2
- `ea-data-quality-audit` (Mavis skill) — the audit gate #3
- Mavis MEMORY.md "Skill infrastructure" — the no-wrappers fleet lock
- Mavis MEMORY.md "Disk wins over recap" — the brief-evidence gate
