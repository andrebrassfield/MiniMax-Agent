---
type: tpg-folder
purpose: SePO loop artifacts (trace log, generation history, textual gradients)
created: 2026-06-17
parent: Cognitive Parameter Graph
schema_version: 1
---

# 99 _system/sepo/

SePO loop artifacts. **Append-only** trace of every loop run, every candidate mutation, every accept/reject decision.

## Files

- `trace.md` — chronological log of SePO events (one entry per loop iteration, one entry per commit, one entry per rejection)

## Entry schema

```markdown
## YYYY-MM-DDTHH:MM:SSZ — <event_type>

- parameter_id: <id>
- generation: <int>
- fitness_before: <float or null>
- fitness_after: <float or null>
- decision: accept | reject | halt
- rationale: <one-line>
- diff_summary: <count of lines added/removed>
- tokens_used: <int estimate>
- safety_veto: pass | fail
- run_by: Mavis (sync) | <cron-name> (autonomous)
```

## Why append-only

The trace is the audit trail. If something goes wrong (regression, missed revert), the trace shows what changed and when. Editing past entries destroys this. Same discipline as `ea-decision-logger` for decisions-in-chat-vanish-within-2-weeks.
