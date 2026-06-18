---
name: ea-skill-evolution
description: Operational skill that consumes the lesson brief from `session-lesson-extractor` and runs the **GEPA-anchored self-evolution loop** to mutate existing skills, generate new ones, and propose memory candidates. This is the *engine* that the lesson extractor's *suggestion engine* feeds — together they close the "loops that don't write back to memory" gap (see `ea-loop-thinking`, the MEMORY building block). Anchors in GEPA (Agrawal et al., arXiv 2507.19457), the Gao et al. self-evolving-agents survey (arXiv 2507.21046, 4-axis What/When/How/Where framework), Alita-G (Qiu et al., arXiv 2510.23601) for the "agent generates its own tools" pattern, and MUSE-Autoskill for the create/memory/manage/eval 4-stage discipline. Triggers on (a) a fresh `session-lesson-extractor` brief at `03 Projects/Mavis EA Design/reports/lesson-extract-*.md`, (b) Andre's "evolve the skill library" / "what should we codify" / "we keep correcting the same thing", or (c) the EA weekly reflection. **This skill proposes mutations and scaffolds; Mavis reviews and commits. It does NOT auto-write to memory, auto-archive skills, or auto-publish drafts.** The skill is the proposer; the EA is the gate. Do NOT load for one-off sessions with no extract, for ad-hoc memory writes (use the standard `mavis memory append` flow), or for skill work in other agents' trees (Mavis territory only).
---

# EA Skill Evolution — The Self-Evolution Engine Behind the MEMORY Building Block

## What this skill does

You take the **lesson brief** produced by `session-lesson-extractor` and turn it into **proposed evolutions** of the Mavis skill/memory corpus. You run the **GEPA-style reflective mutation loop** (Reflect → Mutate → Re-evaluate → Ship) against three artifact types:

1. **New skill scaffolds** — for HIGH-durability candidates that look like a recurring workflow with no current skill
2. **Skill mutations** — for HIGH/MEDIUM-durability candidates that point at a gap in an existing skill
3. **Memory candidates** — for HIGH-durability "Type A recurring correction" patterns that belong in `MEMORY.md` or a topic file (deferred to Mavis; this skill does not write to memory)

The output is a **proposed-evolution manifest** at `~/.mavis/agents/mavis/skills/ea-skill-evolution/manifest.jsonl` (one line per proposed change) plus the scaffolded SKILL.md / mutation diffs in a staging area. Mavis reviews the manifest, commits what passes the gate, and discards what doesn't.

**The frame:** A loop that doesn't write back to its own corpus is a loop that re-derives everything from zero on the next run. `session-lesson-extractor` is the suggestion engine. **This skill is the evolution engine.** Together they close the MEMORY building block in `ea-loop-thinking`.

## When to run

**Trigger phrases:**
- "evolve the skills" / "what should we codify from the brief"
- "I keep correcting the same thing" (a memory entry exists, but the skill hasn't been updated)
- "this skill is missing a case" / "the skill said X but the work needed Y"
- After a fresh `session-lesson-extractor` brief lands at `03 Projects/Mavis EA Design/reports/lesson-extract-YYYY-MM-DD.md`
- Weekly cadence (Sunday evening, paired with the lesson extractor's recommended schedule)
- After a major project transition or a series of 3+ corrections in a week
- "self-evolution cycle" / "GEPA run" / "mutate the corpus"

**Do NOT run for:**
- One-off sessions with no extract
- When the corpus is already up to date (run `ea-data-quality-audit` first)
- Ad-hoc memory entries (use `mavis memory append` directly — this skill is for evolution, not single-entry writes)
- Skill work in other agents' trees (Mavis territory only; do not propose Hermes/OpenClaw skill changes from here)
- Without first running `ea-loop-audit` on the target skill (you need a baseline to evolve against)

## Inputs

| Input | Default | Required |
|---|---|---|
| `lesson-extract-YYYY-MM-DD.md` brief path | (none — must be specified) | yes |
| Target surface (memory / skills / both) | `skills` | no |
| Mutation budget (max proposals per run) | 5 | no |
| Risk threshold (skip proposals that touch regulated domains) | `pause-and-flag` | no |

## The 4-axis framework (Gao et al., arXiv 2507.21046)

For every candidate from the brief, classify it on four axes before proposing a mutation:

| Axis | Question | Mavis's default |
|---|---|---|
| **What** to evolve | Surface type | Skill, memory, prompt, tool, agent spec |
| **When** to evolve | Trigger | On every fresh brief, or on a specific pattern (3+ occurrences), or on a new domain |
| **How** to evolve | Algorithm | GEPA-style reflective mutation (smallest change that closes the gap), or scaffold-from-template for new skills, or merge for overlapping skills |
| **Where** to evolve | Location | `~/.mavis/agents/mavis/skills/<name>/` (canonical), `99 _system/skills/<name>/` (vault mirror), `~/.mavis/agents/mavis/memory/MEMORY.md` (always-on memory), or topic file (on-demand memory) |

## The procedure (5 stages — same loop as `ea-loop-thinking`)

### 1. DISCOVER — read the brief, validate inputs

1. **Read the brief** at `03 Projects/Mavis EA Design/reports/lesson-extract-YYYY-MM-DD.md`. Skip the "discard with reason" section. Focus on HIGH and MEDIUM durability candidates.
2. **Cross-check against current corpus** — for each candidate, search `MEMORY.md`, topic files, and the skill library. If the rule is already canon, mark as `already-canon` and discard.
3. **Pull a fresh `ea-data-quality-audit` baseline** — note the current corpus size, skill count, and any open audit findings. You'll diff against this after the cycle.
4. **Run `ea-loop-audit` on any skill you're proposing to mutate** — you need a baseline. If the target skill is itself in violation of the 5-stage loop, the evolution will compound the bug. Surface that to Mavis before mutating.

### 2. PLAN — classify each candidate on the 4 axes

For each surviving candidate, write a one-line proposal: `[type: new|mutate|memory-candidate] [surface: skills|memory|prompts] [priority: HIGH|MED|LOW] [risk: low|med|high|regulated] — <one-sentence intent>`. Stop and ask Mavis if any candidate lands in `risk: regulated` — that's an Addition 11 (regulatory) trigger from `ea-5-mistakes-audit`, and the right action is to halt and surface, not to evolve.

### 3. EXECUTE — generate proposals

For each approved candidate, run the smallest evolution that closes the gap:

**For a new skill scaffold:**
1. Pull the relevant brief evidence (file:line refs from the extract).
2. Pick a template structure from the existing skill library (e.g., `ea-loop-thinking` is the meta-skill template; `ea-data-quality-audit` is the diagnostic template; `ea-closed-loop-builder` is the operational template).
3. Draft the new `SKILL.md` with: YAML frontmatter (name, description with triggers), What this skill does, When to run (trigger phrases), Inputs, Procedure, Hard constraints, Anchoring sources.
4. Stage the file at `~/.mavis/agents/mavis/skills/ea-skill-evolution/staging/<new-skill-name>/SKILL.md`. Do NOT write to the canonical path yet.
5. Add a manifest entry.

**For a skill mutation:**
1. Read the current `SKILL.md` end-to-end.
2. Identify the smallest change that closes the gap from the brief evidence. Per GEPA discipline: **one paragraph, one section, or one trigger phrase** at a time. Don't rewrite the whole skill.
3. Draft the diff as a unified-format patch against the current `SKILL.md`.
4. Stage the diff at `~/.mavis/agents/mavis/skills/ea-skill-evolution/staging/<target-skill>/<date>-mutation.diff`.
5. Add a manifest entry with the proposed change summary and the brief evidence it addresses.

**For a memory candidate:**
1. Draft the proposed `mavis memory append` invocation: agent name, content, suggested slot (MEMORY.md or topic file).
2. Stage the proposed invocation as a markdown file at `~/.mavis/agents/mavis/skills/ea-skill-evolution/staging/memory/<date>-<slug>.md`. Do NOT execute.
3. Add a manifest entry.

### 4. VERIFY — audit the proposals

Run the Mavis-side verification gates against each staged proposal. Do not use the global `gepa-evaluator` skill (that's an OpenClaw/Hermes tool; this is Mavis territory):

1. **`ea-5-mistakes-audit`** — for every new skill scaffold, run the 5 + 11 mistakes audit. Fail if any dimension is present. For mutations, audit only the changed section.
2. **`ea-loop-audit`** — for every new skill, confirm the 5-stage loop vocabulary is consistent with `ea-loop-thinking`. For mutations, confirm no 6-block coverage was broken.
3. **`ea-data-quality-audit`** — confirm the change doesn't create duplicates with existing skills/memory entries. Fail if a duplicate would be created.
4. **Regulated-domain check** — for any proposal touching medical, legal, credit, employment, biometric, or critical infrastructure: pause and flag for Mavis. Do not approve autonomously. The regulatory layer (EU AI Act, FDA PCCP, HIPAA, UPL) is the load-bearing constraint; it gates the evolution, not the other way around.
5. **Brief-evidence check** — for every proposal, confirm a file:line reference from the brief exists. No "I think Andre said X" — show the file. Per `ea-loop-thinking` hard constraint: disk wins over recap.

### 5. ITERATE — ship what passes, discard what doesn't

For each proposal that passes verification:
1. Move the staged file to the canonical path (`~/.mavis/agents/mavis/skills/<name>/SKILL.md` or apply the diff to the existing skill).
2. **Sync gate (home == mirror, atomic, byte-for-byte).** Mirror to `~/MiniMax-Agent/99 _system/skills/<name>/SKILL.md` using a single atomic write that writes BOTH paths, then runs `cmp` to verify byte-identity. The mirror write is a **precondition** for `status: shipped` — not a post-step. If the mirror write fails OR `cmp` reports a byte-difference, do NOT mark the proposal `shipped`; mark it `mirror-pending` and surface to Mavis with the diff. The agent home is what Mavis reads at session start; the vault is for user visibility. Both must be in sync at the byte level — no drift, no exceptions. The verification command is `cmp ~/.mavis/agents/mavis/skills/<name>/SKILL.md '~/MiniMax-Agent/99 _system/skills/<name>/SKILL.md'` and the exit code MUST be 0 for the gate to pass.
3. Update the manifest entry with `shipped-at: <timestamp>`, `mirrored: true`, and `mirror_verified: <cmp-exit-0-timestamp>`. If the mirror step failed, set `mirrored: false`, `mirror_status: pending`, and `mirror_error: <one-line>` — do NOT set `shipped-at`.
4. Append a short note to the Mavis session log: "Evolved `<skill>`: <one-sentence summary>. Brief: <path>. Diff: <path>. Mirror: <OK|pending>."

For each proposal that fails verification:
1. Update the manifest entry with `discarded: <reason>` and the failure dimension (mistake number, loop stage, or regulatory flag).
2. Do not delete the staging file immediately — keep it for one full cycle so Mavis can review what was rejected and why.

For memory candidates specifically:
1. Do not execute `mavis memory append` autonomously.
2. Surface the candidate to Mavis with the proposed invocation. Mavis reviews and either commits (with `mavis memory append`) or discards.
3. Update the manifest entry with the Mavis decision.

## The manifest (the audit trail)

`~/.mavis/agents/mavis/skills/ea-skill-evolution/manifest.jsonl` is the append-only log of every proposed evolution. One line per proposal in JSONL format:

```jsonl
{"ts": "2026-06-16T21:30:00-05:00", "type": "new", "target": "ea-regulatory-gate", "intent": "Gate that halts skill evolution when a proposal touches a regulated domain", "evidence": ["01 Daily/2026-06-16.md L8", "research-brief-articles-1-and-2.md L217"], "axes": {"what": "skill", "when": "on-evolution", "how": "scaffold-from-template", "where": "skills/ea-regulatory-gate"}, "staging": "ea-skill-evolution/staging/ea-regulatory-gate/SKILL.md", "audit": {"mistakes": "PASS", "loop": "PASS", "duplicate": "PASS", "regulatory": "PASS-NA"}, "status": "pending-review"}
```

Status values: `pending-review` (staged, awaiting Mavis) → `shipped` (moved to canonical + mirror-verified via `cmp` exit 0) | `mirror-pending` (canonical write succeeded but mirror write or `cmp` failed — held, surface to Mavis) | `discarded` (failed audit or Mavis rejected) | `memory-deferred` (memory candidate awaiting `mavis memory append`). The `mirror-pending` state is the **gate-keeper** — a proposal cannot reach `shipped` without first passing the home == mirror byte-identity check. Manifest entries must include `mirror_status: ok | pending | failed` and `mirror_verified: <ISO-timestamp>` whenever `status: shipped` is set.

## Hard constraints

1. **Never write to memory autonomously.** Memory writes are Mavis's decision, with Andre's approval for non-trivial entries. Stage the proposal; Mavis commits.
2. **Never write to canonical skill paths autonomously.** Stage in `ea-skill-evolution/staging/` first. Mavis moves to canonical after review.
3. **Never evolve a skill that has not been `ea-loop-audit`-ed.** The baseline is mandatory. Evolving a broken skill compounds the bug.
4. **Never evolve across the regulated-domain boundary without halting.** Any proposal touching medical, legal, credit, employment, biometric, or critical infrastructure: pause and flag. The Mavis EA reviews; the skill does not proceed.
5. **Mutations are surgical.** One section, one trigger phrase, or one description tweak at a time. Per GEPA discipline: smallest change that closes the gap. If the gap requires a full rewrite, surface that as a separate "scaffold-new" proposal instead.
6. **Mirror discipline (home == mirror, sync gate).** Every canonical write to `~/.mavis/agents/mavis/skills/<name>/SKILL.md` MUST be followed by a mirror write to `~/MiniMax-Agent/99 _system/skills/<name>/SKILL.md` AND a `cmp` verification that both files are byte-identical. The mirror step is a **precondition** for `status: shipped` — proposals that fail the mirror step are held in `status: mirror-pending`, NOT `shipped`. A skill that is canonical but unmirrored is treated as a **partial mutation**: Mavis will not see it on the next session (she reads the vault mirror at session start), and Andre will not see it on the vault surface. The sync gate prevents the silent-drift failure mode where the home is updated but the vault lags, and a future-Mavis re-litigates the change as if it never happened. Use the atomic-write helper in `~/.mavis/agents/mavis/skills/ea-skill-evolution/scripts/mirror-sync.sh` (a `tee` + `cmp` + manifest-update wrapper) — do not hand-roll the write, the gate is the wrapper.
7. **Mavis territory only.** Do not propose evolutions to Hermes skills, OpenClaw skills, Socratic, or any other agent's tree. Cross-team proposals go through Mavis (who decides whether to route to the other team).
8. **Manifest is append-only.** The JSONL is the audit trail. Never edit past entries; if a decision reverses, append a new entry referencing the old one.

## What this skill is NOT

- **Not a memory-write tool.** For single memory entries, use `mavis memory append` directly.
- **Not the global `gepa-evaluator`.** That's an OpenClaw/Hermes tool for fleet-level skill execution evaluation. This is the Mavis-side equivalent: corpus evolution, not execution evaluation.
- **Not autonomous.** Every proposal is reviewed by Mavis. The skill is the proposer; the chief is the gate. This is the load-bearing discipline that keeps self-evolution from drifting.
- **Not a work surface audit.** For auditing a specific skill, use `ea-5-mistakes-audit` or `ea-data-quality-audit`. This skill is for *evolving* the corpus based on observed outcomes, not for inspecting it in isolation.

## Anchoring sources

- **GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning** — Agrawal et al., arXiv 2507.19457 (July 2025) — 6% avg / 20% max improvement over GRPO with 35× fewer rollouts
- **A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve** — Gao et al., arXiv 2507.21046 (July 2025, rev Jan 2026) — the 4-axis framework
- **Alita-G: Self-Evolving Generative Agent for Agent Generation** — Qiu et al., arXiv 2510.23601 (Oct 2025) — agent generates its own MCP tools from observed patterns ("scaling data, not weights")
- **MUSE-Autoskill: Self-Evolving Agents via Skill Creation, Memory, Management, and Evaluation** — BAAI — 4-stage discipline (create / memory / manage / eval)
- **WebEvolver** — Fang et al., arXiv 2504.21024 (April 2025) — warning that self-improvement has a plateau; budget for it
- **Agent0-VL: Self-Evolving Agent for Tool-Integrated Vision-Language Reasoning** — Liu et al., arXiv 2511.19900 (Nov 2025) — self-rewarding agent
- **Loop engineering vocabulary** (5-stage + 6 building blocks) — `ea-loop-thinking` (Mavis skill)
- **Lesson extraction procedure** — `session-lesson-extractor` (Mavis skill)
- **Mistake audit** (5 + 11) — `ea-5-mistakes-audit` (Mavis skill)
- **Loop audit** — `ea-loop-audit` (Mavis skill)
- **Data quality audit** — `ea-data-quality-audit` (Mavis skill)
- **No-wrappers fleet lock** — Mavis `skill-infrastructure` topic — don't add wrappers, add primitives
- **Disk wins over recap** — Mavis MEMORY.md cross-cutting disciplines
- **If I have to ask you twice, you failed** — Garry Tan (Andre's user memory) — the discipline that justifies codifying this evolution loop
