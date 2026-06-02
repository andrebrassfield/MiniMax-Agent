---
id: i-2026-06-01-052
type: instinct
title: "LLM-as-judge temperature: 0.0 for graders, 0.2 for optimizers"
created: 2026-06-01
confidence: 0.85
cluster: tools
trigger_context: "When building an LLM-as-judge or eval pipeline"
evidence_source: "MEMORY.md discipline 2026-06-02"
tags: [tools, llm, temperature, discipline]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# LLM-as-judge temperature: 0.0 for graders, 0.2 for optimizers

Grader (LLM-as-judge for safety/correctness evals): temperature=0.0 — bit-deterministic. Optimizer (SkillOpt target, model improvement loops): temperature=0.2 — some noise OK because the optimizer aggregates. Don't conflate. Hardcode grader temperature; don't expose as a multi-purpose flag.

## Trigger

When building an LLM-as-judge or eval pipeline

## Evidence

MEMORY.md discipline 2026-06-02

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
