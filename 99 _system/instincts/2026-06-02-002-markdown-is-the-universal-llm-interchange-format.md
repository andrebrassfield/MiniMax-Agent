---
id: i-2026-06-02-002
type: instinct
title: "Markdown is the universal LLM interchange format"
created: 2026-06-02
confidence: 0.9
cluster: ingestion
trigger_context: "When ingesting a PDF, Office file, image, or audio"
evidence_source: "Markdown as Universal LLM Interchange note 2026-06-02"
tags: [ingestion, markdown, markitdown]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# Markdown is the universal LLM interchange format

Convert every structured document to markdown before the model sees it. M3 already speaks markdown natively. The model gets dense content, not binary formats it has to parse. Use markitdown for PDF/Office/Image/Audio. The narrow convert_local() / convert_stream() APIs only — never the permissive convert() that can fetch URLs.

## Trigger

When ingesting a PDF, Office file, image, or audio

## Evidence

Markdown as Universal LLM Interchange note 2026-06-02

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
