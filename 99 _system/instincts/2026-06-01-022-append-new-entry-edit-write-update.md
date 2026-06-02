---
id: i-2026-06-01-022
type: instinct
title: "Append = new entry; Edit/Write = update"
created: 2026-06-01
confidence: 0.9
cluster: memory
trigger_context: "When writing a memory entry"
evidence_source: "MEMORY.md Memory hygiene section + append vs Edit"
tags: [memory, discipline, rule]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# Append = new entry; Edit/Write = update

mavis memory append = NEW entry. Edit/Write tool = UPDATE / MERGE / REMOVE. Don't mix. Append creates duplicate-ish entries; Edit breaks the append-only audit trail. Topic files in this dir are loaded on demand only - keep MEMORY.md lean (<100 lines).

## Trigger

When writing a memory entry

## Evidence

MEMORY.md Memory hygiene section + append vs Edit

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
