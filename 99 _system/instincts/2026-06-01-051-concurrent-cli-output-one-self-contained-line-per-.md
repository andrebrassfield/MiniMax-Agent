---
id: i-2026-06-01-051
type: instinct
title: "Concurrent CLI output: one self-contained line per worker"
created: 2026-06-01
confidence: 0.95
cluster: tools
trigger_context: "When writing multi-threaded CLI output"
evidence_source: "MEMORY.md antipattern 2026-06-02 (verified, hit twice)"
tags: [tools, concurrency, cli, antipattern]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# Concurrent CLI output: one self-contained line per worker

When running N workers that print to stdout, do NOT use the print(..., end="", flush=True) 'header' pattern followed by a later print(result) 'body' follow-up. Headers pile up before bodies, producing interleaved garbage. Correct pattern: one self-contained line per worker, printed at completion, atomic under a print_lock.

## Trigger

When writing multi-threaded CLI output

## Evidence

MEMORY.md antipattern 2026-06-02 (verified, hit twice)

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
