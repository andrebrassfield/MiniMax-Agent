---
id: i-2026-06-02-005
type: instinct
title: "Skills are installable atomic units, validated"
created: 2026-06-02
confidence: 0.85
cluster: architecture
trigger_context: "When building a new agent capability"
evidence_source: "Skill Library Architecture note 2026-06-02"
tags: [architecture, skills, structure]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# Skills are installable atomic units, validated

The MiniMax-AI/skills canonical structure: one folder per skill, SKILL.md at the top, validation script enforces structure, source field tracks provenance, CREDITS.md for attribution. Skills are the unit of capability routing. The model doesn't embed library choices; the skill abstracts them.

## Trigger

When building a new agent capability

## Evidence

Skill Library Architecture note 2026-06-02

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
