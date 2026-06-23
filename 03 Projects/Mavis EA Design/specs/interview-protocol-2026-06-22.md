---
date: 2026-06-22
type: closed-loop-spec
status: awaiting-approval-then-immediate
scope: interview-protocol
related:
  - ~/MiniMax-Agent/SOUL.md
  - ~/MiniMax-Agent/MAVIS.md
  - ~/.mavis/agents/mavis/memory/MEMORY.md
  - ~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/ea-contract.md
---

# Spec: Interview Protocol Skill

Codifies the procedure used to build SOUL.md and MAVIS.md — extracting operational context from a human through structured Q&A. Reusable for: new operators onboarding, new domain expansion (entering a new project area), stale-context refresh.

## Goal (done condition)

1. New skill `interview-protocol` at `~/.mavis/agents/mavis/skills/interview-protocol/SKILL.md`
2. Has the question templates + ordering rules + halt conditions
3. Produces structured output suitable for direct ingestion into SOUL.md / MAVIS.md / MEMORY.md
4. Vault mirror at `99 _system/skills/interview-protocol/SKILL.md`
5. MAVIS.md + MEMORY.md updates
6. Manual test: dry-run the protocol against an existing operator profile (e.g., "extract Andre's profile from SOUL.md") — verify output matches existing

## Context

We built SOUL.md and MAVIS.md through organic conversation. The process worked but isn't codified. Codifying enables: future-Mavis re-runs the protocol when context goes stale; new operators get a structured onboarding; project-domain expansion has a repeatable procedure.

The protocol's shape: 5 sections mirroring SOUL.md's structure (Identity / Stance / Accountability / Pushback / Autonomy Boundary Table / Mission / Tone / Operating Mode / Delegation / Standards / Lookup / Escalation / Self-Improvement / End State). Question by question, no batching. Wait for each answer.

## Action (atomic steps)

1. Write this spec (this file)
2. Build the skill file with question templates (one section at a time)
3. Mirror to vault
4. Update MAVIS.md Active Skill Mutations
5. Update MEMORY.md (pointer)
6. Manual test: dry-run against SOUL.md, verify protocol would produce same structure

## Feedback

- Per-interview state file at `~/.mavis/state/interview-protocol-YYYY-MM-DD.md` tracks progress
- Output file at `~/MiniMax-Agent/03 Projects/[operator-or-domain]/interview-output-YYYY-MM-DD.md`
- End-of-interview gate: all 14 sections covered + cross-check against existing SOUL.md/MAVIS.md for consistency

## Stop condition

Open-loop (run on demand). Halt conditions:
- Operator gives "I don't know" on >2 sections → flag, ask which to revisit later, end interview
- Answers contradict existing SOUL.md/MAVIS.md (when refreshing stale context) → HALT, surface the contradiction, ask operator to resolve
- Interview runs >2 hours → save partial output, end with summary of what's missing

## Reversibility

`<5 min: rm skill + vault mirror + revert MAVIS.md/MEMORY.md entries`
