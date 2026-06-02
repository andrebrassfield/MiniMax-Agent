---
id: i-2026-06-01-021
type: instinct
title: "Memory is a hint, not live state"
created: 2026-06-01
confidence: 0.9
cluster: memory
trigger_context: "Before executing on a remembered fact"
evidence_source: "MEMORY.md Memory hygiene section"
tags: [memory, verification, discipline]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# Memory is a hint, not live state

Memory can be wrong, stale, or contradicted. Verify before acting on it. If a memory says X but the current state says not-X, the current state wins. Memory entries should be cleaned up when they drift from reality.

## Trigger

Before executing on a remembered fact

## Evidence

MEMORY.md Memory hygiene section

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
