---
id: i-2026-06-01-053
type: instinct
title: "Python .format() with braces in LLM prompt templates"
created: 2026-06-01
confidence: 0.9
cluster: tools
trigger_context: "When writing a .format()-based prompt template with literal braces"
evidence_source: "MEMORY.md tool-quirk 2026-06-02 (hit in evaluator.py v0.2.0)"
tags: [tools, python, format, quirk]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# Python .format() with braces in LLM prompt templates

When using str.format() to render an LLM prompt template, escape literal { and } as {{ and }} in the FORMAT STRING. User-supplied content is passed as VALUES, not as format specifiers — {} chars in values are inserted as-is. Bug pattern: literal text in the template like say 'publish' or 'go' throws KeyError because the inner quotes look like field references.

## Trigger

When writing a .format()-based prompt template with literal braces

## Evidence

MEMORY.md tool-quirk 2026-06-02 (hit in evaluator.py v0.2.0)

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
