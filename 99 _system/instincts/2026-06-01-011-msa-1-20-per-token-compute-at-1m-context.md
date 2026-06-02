---
id: i-2026-06-01-011
type: instinct
title: "MSA: 1/20 per-token compute at 1M context"
created: 2026-06-01
confidence: 0.95
cluster: m3
trigger_context: "When explaining why 1M context is feasible on M3"
evidence_source: "learnings.md [architecture] 2026-06-01 + Paged Attention Economics note"
tags: [m3, msa, architecture]
migrated_from: learnings.md + MEMORY.md
migration_date: 2026-06-02
---

# MSA: 1/20 per-token compute at 1M context

MiniMax Sparse Attention: pre-filtering stage partitions KV into blocks. KV outer gather Q operator: each block read once, contiguous memory. 4x faster than open-source Flash-Sparse-Attention and flash-moba. 9.7x faster prefilling, 15.6x faster decoding at 1M context.

## Trigger

When explaining why 1M context is feasible on M3

## Evidence

learnings.md [architecture] 2026-06-01 + Paged Attention Economics note

## Counter-evidence

What would contradict this instinct: a session where the trigger fired and the lesson didn't apply, or the lesson was actively wrong.
