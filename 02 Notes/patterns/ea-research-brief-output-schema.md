---
description: "The 6-section output schema every ea-research-brief produces — Scope, Primary sources, Findings, Runtime cross-reference, What I don't know, Verification checklist. Moved from skill-local references 2026-06-22."
source: ~/.mavis/agents/mavis/skills/ea-research-brief/references/brief-output-schema.md
---

# Brief Output Schema — ea-research-brief

The 6-section structure every brief produced via this skill uses.

## Template

```markdown
# Brief: <Question in one sentence>

> Generated: <YYYY-MM-DD HH:MM CT> | Author: Mavis (EA) | Worker: <which agent/skill ran the dispatch>
> Regime check: <PASS — no regime hit, internal brief> | <HALT — <regime> triggered, escalated to Andre>

## 1. Scope (Stage 1)
- Question: ...
- Deliverable shape: ...
- Disk anchors: ...

## 2. Primary sources (Stage 3)
- [1] <citation — full reference>
- [2] <citation — full reference>
- ... (2-4 sources, all directly verified)

## 3. Findings
<the substance of the brief, with verbatim quotes for non-trivial claims>

## 4. Runtime cross-reference (Stage 5)
- Memory state: <what MEMORY.md / topic files already say>
- Skill state: <which ea-* skills are relevant>
- Cron state: <which crons are related>
- Recent work: <last 30 days of relevant dispatches>
- Contradictions: <any live state that conflicts with the brief>

## 5. What I don't know
<explicit list of gaps, unanswered questions, sources not yet verified>

## 6. Verification
- [ ] All citations directly fetched and quoted
- [ ] All primary sources read, not synthesized
- [ ] No regime hit OR explicit HALT message
- [ ] Runtime cross-reference done
- [ ] "What I don't know" section populated
```

## Section-by-section

### 1. Scope

Locked at Stage 1. The question in one sentence + the deliverable
shape (1-page exec summary, 3-5 page technical brief, 4-source
synthesis, etc.) + the disk anchors (vault paths the worker should
cross-reference).

If the scope statement is more than 1 line per element, the brief
has not been scoped tightly enough. Worker prompts that omit the
scope produce briefs that miss the brief.

### 2. Primary sources

The 2-4 sources the worker actually read. Each must be:
- The primary source itself (not a synthesis of the primary source)
- Fetched and quoted directly
- Anchored to a specific claim in the Findings section

If a citation is not in this list, it's not grounded.

### 3. Findings

The substance. Verbatim quotes for non-trivial claims. No paraphrasing
of load-bearing claims. Cross-references to citation numbers from
section 2.

### 4. Runtime cross-reference

The disk-wins-over-recap discipline applied. What does the live
runtime say about this topic? Where does the brief intersect? Are
there contradictions between the brief and the live state?

A contradiction is a red flag — surface it to Andre before
publishing.

### 5. What I don't know

The honest list of gaps. Acknowledged unknowns > confidently-wrong
claims. This section is required, even if it only says "limited
primary source coverage; one cited paper behind a paywall."

### 6. Verification

The 5-item checklist. The EA marks each item YES or notes what's
missing. The brief is not done until all 5 are YES (or the missing
items are explicitly HALTed to Andre).
