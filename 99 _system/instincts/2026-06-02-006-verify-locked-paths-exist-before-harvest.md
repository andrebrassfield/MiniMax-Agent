---
id: "i-2026-06-02-006"
type: "instinct"
title: "Verify locked paths exist before harvest"
created: "2026-06-02"
confidence: 0.85
cluster: "memory"
trigger_context: "When a spec block, a memory entry, or a Friction Log says a file lives at a specific path, before any harvester reads it, verify the file exists."
evidence_source: "Operation Ouroboros Phase 3 (2026-06-02); Friction 4 in state-of-mavis.md; dry-run of generate_instincts.py"
tags: ["audit", "harvester", "memory-hygiene", "ouroboros"]
body: "A locked path in a Friction Log is a promise, not a fact. Today's harvest surfaced audit_log.jsonl as missing despite Friction 4 having locked the path on 2026-06-02. The harvester (generate_instincts.py) handles the gap gracefully (skips + notes) — but the gap shouldn't have been there. Before any harvester reads a 'locked' path, ls the file. If it's missing, that's a candidate Friction (path locked but file never created = Memory Without Source). This is a more operational version of the existing 2026-06-01-021 'Memory is a hint, not live state' instinct: the discipline is audit-first, not read-first, when the source is a memory lock rather than a live system signal."
---


# Verify locked paths exist before harvest

A locked path in a Friction Log is a promise, not a fact. Today's harvest surfaced audit_log.jsonl as missing despite Friction 4 having locked the path on 2026-06-02. The harvester (generate_instincts.py) handles the gap gracefully (skips + notes) — but the gap shouldn't have been there. Before any harvester reads a 'locked' path, ls the file. If it's missing, that's a candidate Friction (path locked but file never created = Memory Without Source). This is a more operational version of the existing 2026-06-01-021 'Memory is a hint, not live state' instinct: the discipline is audit-first, not read-first, when the source is a memory lock rather than a live system signal.
