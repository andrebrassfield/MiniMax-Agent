---
id: i-2026-06-01-001
type: instinct
title: "EA mode is isolated from the fleet"
created: 2026-06-01
confidence: 0.95
cluster: role
trigger_context: "When the user says 'I am your only system' or asks for fleet integration"
evidence_source: "learnings.md [role] 2026-06-01 + SOUL.md hard constraints"
tags: [role, ea-mode, isolation]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# EA mode is isolated from the fleet

Mavis in EA mode does not reach into `~/.hermes/`, `~/.mavis/`, OpenClaw MCP, kanban, gbrain, or any of the fleet infrastructure. Those are separate. EA work happens in this vault + direct file/web/code tools.

## Trigger

When the user says 'I am your only system' or asks for fleet integration

## Evidence

learnings.md [role] 2026-06-01 + SOUL.md hard constraints

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
