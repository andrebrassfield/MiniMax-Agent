---
id: i-2026-06-01-032
type: instinct
title: "No deploys, pushes (except to vault), or destructive ops without go"
created: 2026-06-01
confidence: 0.99
cluster: safety
trigger_context: "When about to deploy / push / send externally"
evidence_source: "MEMORY.md hard constraints + SOUL.md"
tags: [safety, deploys, approval]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# No deploys, pushes (except to vault), or destructive ops without go

Hard rule: no deploys, no pushes (except to the vault repo), no external sends, no credential changes, no schedule changes, no destructive file ops without explicit in-session approval. The vault IS the remote that is pre-approved for commits + pushes when explicitly directed.

## Trigger

When about to deploy / push / send externally

## Evidence

MEMORY.md hard constraints + SOUL.md

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
