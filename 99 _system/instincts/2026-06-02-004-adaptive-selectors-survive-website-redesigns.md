---
id: i-2026-06-02-004
type: instinct
title: "Adaptive selectors survive website redesigns"
created: 2026-06-02
confidence: 0.85
cluster: ingestion
trigger_context: "When scraping a website and selectors break"
evidence_source: "Adaptive Selectors for Web Scraping note 2026-06-02"
tags: [ingestion, scraping, scrapling, adaptive]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# Adaptive selectors survive website redesigns

Scrapling's auto_save=True + adaptive=True pattern. The library learns the element's signature (DOM position, siblings, text, style) and re-finds it via similarity when the CSS selector breaks. Same shape as tool-self-healer, applied to web scraping. The 4-fetcher escalation chain (Fetcher -> StealthyFetcher -> DynamicFetcher -> cu MCP) is a routing decision.

## Trigger

When scraping a website and selectors break

## Evidence

Adaptive Selectors for Web Scraping note 2026-06-02

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
