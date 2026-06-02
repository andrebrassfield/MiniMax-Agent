---
id: i-2026-06-01-060
type: instinct
title: "M2.7-highspeed -> M3 default swap (done)"
created: 2026-06-01
confidence: 0.99
cluster: m3
trigger_context: "When picking the default model for a call"
evidence_source: "learnings.md Migration notes 2026-06-01 + MEMORY.md Model section"
tags: [m3, migration, default]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# M2.7-highspeed -> M3 default swap (done)

Default model: minimax/MiniMax-M2.7-highspeed -> minimax/MiniMax-M3. No more 40k output cap. Stop pre-chunking long fleet logs into 200k windows. Drop pre-extraction in vision pipelines. What didn't change: memory file structure, linking principles, SOUL hard constraints, git SSH deploy key pattern.

## Trigger

When picking the default model for a call

## Evidence

learnings.md Migration notes 2026-06-01 + MEMORY.md Model section

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
