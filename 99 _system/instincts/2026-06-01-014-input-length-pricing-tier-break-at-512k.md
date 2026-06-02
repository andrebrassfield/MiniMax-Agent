---
id: i-2026-06-01-014
type: instinct
title: "Input-length pricing tier break at 512K"
created: 2026-06-01
confidence: 0.95
cluster: m3
trigger_context: "When the prompt is over 512K tokens"
evidence_source: "learnings.md [gotcha] 2026-06-01 + M3 Edge note"
tags: [m3, pricing, gotcha]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# Input-length pricing tier break at 512K

<=512K input tokens: standard rate. >512K: long-context rate (higher). Don't accidentally route 1M-token docs into the priority queue by default. For EA work, 512K is plenty for most things.

## Trigger

When the prompt is over 512K tokens

## Evidence

learnings.md [gotcha] 2026-06-01 + M3 Edge note

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
