---
id: i-2026-06-02-001
type: instinct
title: "Compression as a first-class layer (Headroom)"
created: 2026-06-02
confidence: 0.85
cluster: context
trigger_context: "When the prompt is over 50K tokens or the budget is tight"
evidence_source: "Context Compression as First-Class Layer note 2026-06-02"
tags: [context, compression, headroom, budget]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# Compression as a first-class layer (Headroom)

Headroom's 60-95% token savings on real agent workloads are the difference between a $100/mo budget lasting the quarter and burning out in two weeks. Compression is not an optimization; it's a layer. CCR (reversible compression) via SHA-256 content hash means the model can opt back into the original when it detects signal decay.

## Trigger

When the prompt is over 50K tokens or the budget is tight

## Evidence

Context Compression as First-Class Layer note 2026-06-02

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
