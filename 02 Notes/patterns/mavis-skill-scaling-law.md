---
description: "Skill-vs-vault ratio target for Mavis skills — the Chinchilla scaling-law analog. Use when designing a new skill, auditing an existing skill, or refactoring overstuffed skills. Codifies the 1-2KB skill-instruction ceiling with vault topic files providing depth on demand. Locked 2026-06-22 per Andre's 'aggressive' target choice."
---

# Mavis Skill Scaling Law (Chinchilla analog)

## The target (locked 2026-06-22)

**A Mavis skill's instruction length should be 1-2 KB. Depth lives in vault topic files, not inline.**

This is the Mavis analog of the Chinchilla scaling law (Hoffmann et al. 2022): model capability is bounded by the ratio between model size and training-data size, not by either alone. For Mavis:

- **Skill instruction (always-on when skill loads)** = "model size." Determines context cost.
- **Vault topic file (load-on-demand)** = "training data." Determines capability depth.
- **Ratio:** ~1:10 to ~1:50 (skill bytes : vault bytes referenced) is the sweet spot.

## The audit baseline (2026-06-22, pre-refactor)

| Metric | Current | Target |
|---|---|---|
| Total skills | 51 | 51+ (library grows) |
| Total skill bytes | 378.5 KB | ≤100 KB |
| Median skill size | ~7 KB | 1-2 KB |
| Skills at target | 0 of 51 | all of them |
| Skills over 8 KB | ~19 (37%) | 0 |
| Best ratio (skill bytes / vault refs) | `context-loader` (9.5 KB / 19 refs = ~500 B/ref) | — |

## The refactor rule

When refactoring a skill to the 1-2 KB target:

1. **Keep inline:**
   - Trigger phrases (when to load)
   - Procedure skeleton (3-7 numbered steps, each ≤1 sentence)
   - Inputs/outputs table
   - HALT conditions
   - Cross-references to vault topic files

2. **Move to vault topic files:**
   - Detailed procedure content (>2 sentences per step)
   - Code examples
   - Reference tables (timing, formats, command syntax)
   - Worked examples
   - Framework definitions
   - Tool inventories
   - Diagnostic checklists

3. **Decision rule:** if a section is "what to do" → keep inline. If a section is "how to do it in detail" or "why this works" → move to vault.

## Vault topic file naming convention

When extracting content from a skill, the vault topic file goes at:

```
02 Notes/patterns/<skill-name>-<topic>.md    (for reusable patterns)
02 Notes/decisions/<skill-name>-<topic>.md   (for decision rationale)
02 Notes/questions/<skill-name>-<topic>.md   (for open questions)
02 Notes/numbers/<skill-name>-<topic>.md     (for data points)
```

The skill cross-references the vault file with a wikilink: `[[02 Notes/patterns/<file>]]`.

## Worked example (post-refactor template)

A refactored skill looks like:

```markdown
---
name: <skill-name>
description: <one-line trigger description>
---

# <Skill Name>

## When to load

Triggers: <phrase list>

Do NOT load for: <anti-pattern list>

## Procedure

1. <step 1 — 1 sentence, links to vault for detail>
2. <step 2 — 1 sentence>
3. <step 3 — 1 sentence>

## Inputs / outputs

<small table>

## HALT conditions

<list>

## Depth (load on demand)

- [[02 Notes/patterns/<skill>-framework]] — the framework this skill applies
- [[02 Notes/patterns/<skill>-examples]] — worked examples
- [[02 Notes/numbers/<skill>-calibration]] — calibration data if any

## Cross-references

- [[02 Notes/patterns/mavis-as-llm]] — the parent pattern
- [[02 Notes/patterns/agent-harness]] — the runtime counterpart
```

This template is ~1-1.5 KB. The depth lives in 3-5 vault topic files at ~2-5 KB each.

## Success criteria (post-refactor)

After the 11-skill first pass (2026-06-22 batch):

- All 11 refactored skills ≤2 KB
- Each refactored skill references ≥2 vault topic files
- No loss of capability (procedure still loadable, still produces correct output)
- Library total: 378.5 KB → ≤300 KB (≥20% reduction from this batch alone)
- Long-term target: ≤100 KB total as the library grows

## What this rule does NOT say

- It does NOT say "skills are bad, vault is good." Both are needed. Skills = dispatch; vault = depth.
- It does NOT say "all skills should be the same size." Some skills are pure procedure (smaller); some are orchestration (slightly larger, but reference vault for the orchestration logic).
- It does NOT say "move everything to vault." Inline content that's load-bearing for the dispatch decision (triggers, HALT conditions) MUST stay inline.

## Cross-references

- **[[02 Notes/patterns/mavis-as-llm]]** — the parent pattern (5-stage audit framework)
- **[[02 Notes/articles/2026-06-22 - 5-Stage-LLM-Pipeline]]** — the source article (Chinchilla scaling law)
- **[[03 Projects/Mavis EA Design/specs/mavis-as-llm-upgrades-2026-06-22]]** — the upgrade spec that produced this pattern
- **[[03 Projects/Mavis EA Design/minimax-token-dialin-ledger-2026-06-22]]** — the dial-in cycle as a worked example (applied to MEMORY.md/SOUL.md)
- **`context-loader` skill** — the current best-ratio example in the library (9.5 KB / 19 vault refs)

## Status

**Active pattern.** Codified 2026-06-22 from the 5-stage LLM pipeline article + Andre's "aggressive" target choice. First refactor batch in progress.
