# Mavis Audit Handoff — Verifier → Mavis (chief of staff)

> Verdicts on Mavis's handoffs, connections notes, chain-compliance, and process discipline. Mavis reads this to tune her patterns and to brief Andre with receipts.

## Pending (Mavis to consume)

*Empty. New verdicts appended by AUDIT.*

## Convention

```yaml
- id: mvs-audit-handoff-YYYY-MM-DD-NNN
  audit_log_id: aud-...
  target: "<handoff-id | connection-note-name | process-instance-id>"
  verdict: PASS | FAIL | NEEDS-WORK | NEEDS-MORE-EVIDENCE
  weighted_score: 0.0-1.0
  rubric_criteria:
    source_quality: 0.0-1.0
    cross_source_agreement: 0.0-1.0
    stage_discipline: 0.0-1.0
    freshness: 0.0-1.0
    process_compliance: 0.0-1.0
    handoff_hygiene: 0.0-1.0
  trail:
    - "<researcher-dossier-link>"
    - "<source-claim-link>"
    - raw/.../snapshot.json
  issue: "<one sentence — what was found, named as artifact not as agent>"
  recommended_action: cite_dossier | add_source_link | back_link | split_connection | demote_confidence | drop | freeze_publish
  snapshot_as_of: YYYY-MM-DDTHH:MM:SSZ
  issued_at: YYYY-MM-DD
  temperature: 0.0
```

## Recently Consumed (last 5)

*Empty.*

---

**Discipline:**
- Mavis's chain-compliance failures (orphan connections, claims bypassing the Researcher's dossier) are the most common target here. Flag them.
- A FAIL verdict on a connection note does not delete the note. It flags it for revision before publish.
- Verdicts are about artifacts (the connection, the handoff, the briefing), not about Mavis as an agent.
- Mavis will mark items consumed by moving them to the consumed list and applying the recommended_action.
