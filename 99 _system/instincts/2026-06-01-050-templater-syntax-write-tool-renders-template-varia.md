---
id: i-2026-06-01-050
type: instinct
title: "Templater syntax: Write tool renders template variables"
created: 2026-06-01
confidence: 0.95
cluster: tools
trigger_context: "When writing a .md file in 99 _system/templates/ with Templater syntax"
evidence_source: "MEMORY.md tool-quirk 2026-06-01 (verified)"
tags: [tools, templater, obsidian, quirk]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# Templater syntax: Write tool renders template variables

When writing Templater template files (.md) via the Write tool, the 2026-06-02 and 2026-06-01-041-quote-what-you-read-no-fabrication syntax gets RENDERED to static text. The template becomes dead. Workaround: use bash heredoc with a quoted delimiter, e.g. `cat > file.md << 'TEMPLATE_EOF'` ... `TEMPLATE_EOF`. Or use the Edit tool's exact-string replacement.

## Trigger

When writing a .md file in 99 _system/templates/ with Templater syntax

## Evidence

MEMORY.md tool-quirk 2026-06-01 (verified)

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
