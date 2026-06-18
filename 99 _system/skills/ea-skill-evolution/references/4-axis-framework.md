# 4-Axis Framework — ea-skill-evolution

Per the Gao et al. self-evolving-agents survey (arXiv 2507.21046).
Every candidate from the lesson brief gets classified on these 4
axes before a proposal is generated.

## The 4 axes

| Axis | Question | Mavis's options |
|---|---|---|
| **What** to evolve | Surface type | Skill, memory, prompt, tool, agent spec |
| **When** to evolve | Trigger | On every fresh brief, or on a specific pattern (3+ occurrences), or on a new domain |
| **How** to evolve | Algorithm | GEPA-style reflective mutation (smallest change that closes the gap), or scaffold-from-template for new skills, or merge for overlapping skills |
| **Where** to evolve | Location | `~/.mavis/agents/mavis/skills/<name>/` (canonical), `99 _system/skills/<name>/` (vault mirror), `~/.mavis/agents/mavis/memory/MEMORY.md` (always-on memory), or topic file (on-demand memory) |

## Why these 4 axes

The survey's load-bearing claim: "Self-evolution systems that don't
classify on What/When/How/Where tend to produce unstable or
self-defeating mutations." The 4 axes are the classification that
makes a mutation auditable.

- **What** = the surface (the file/directory being modified)
- **When** = the trigger (what conditions cause this mutation to fire)
- **How** = the algorithm (the pattern of change — single-point edit, scaffold, merge)
- **Where** = the canonical storage (so the mutation has a "home" that future runs can find)

## Applying the 4 axes

For each surviving candidate from the brief, write a one-line
classification:

```
[axis: what] [axis: when] [axis: how] [axis: where] — <one-sentence intent>
```

Example:
```
[skill] [3+ corrections on a specific trigger] [GEPA-style single-trigger edit] [skills/x-bookmark-parser/SKILL.md] — Add a halt condition for the Focus Rule's tabId mismatch.
```

If any candidate lands in the "regulated" risk category
(medical/legal/credit/employment/biometric/critical infrastructure),
halt and surface to Mavis. The regulatory layer (EU AI Act, FDA PCCP,
HIPAA, UPL) is the load-bearing constraint.

## The 3 proposal types

The "How" axis maps to one of 3 proposal types:

1. **New skill scaffold** — for HIGH-durability candidates that look
   like a recurring workflow with no current skill
2. **Skill mutation** — for HIGH/MEDIUM-durability candidates that
   point at a gap in an existing skill
3. **Memory candidate** — for HIGH-durability "Type A recurring
   correction" patterns that belong in `MEMORY.md` or a topic file
   (deferred to Mavis; this skill does not write to memory)

The full per-type procedure (how to scaffold, how to mutate, how to
propose memory) is in `references/proposal-types.md`.
