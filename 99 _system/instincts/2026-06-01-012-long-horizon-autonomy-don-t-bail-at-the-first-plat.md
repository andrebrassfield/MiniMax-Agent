---
id: i-2026-06-01-012
type: instinct
title: "Long-horizon autonomy: don't bail at the first plateau"
created: 2026-06-01
confidence: 0.85
cluster: m3
trigger_context: "When a long task hits a performance wall"
evidence_source: "learnings.md [capability] 2026-06-01 + Long-Horizon Patterns note"
tags: [m3, long-horizon, patterns]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# Long-horizon autonomy: don't bail at the first plateau

M3 demonstrated 12h+ autonomous runs without bailing. CUDA optimization: 1,959 tool calls over 24h, best result on submission 145. Most other models gave up by submission 30. Implication for EA work: when running a long research/synthesis task, let it grind. Don't quit early because an early result looked good.

## Trigger

When a long task hits a performance wall

## Evidence

learnings.md [capability] 2026-06-01 + Long-Horizon Patterns note

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
