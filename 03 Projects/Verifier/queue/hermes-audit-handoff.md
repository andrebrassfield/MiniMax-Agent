# Hermes Audit Handoff — Verifier → Hermes (fleet orchestrator)

> Verdicts on Hermes's routing decisions, task acceptance, and worker handoffs. Hermes reads this to enforce routing discipline.

## Pending (Hermes to consume)

*Empty. New verdicts appended by AUDIT.*

## Convention

```yaml
- id: hms-audit-handoff-YYYY-MM-DD-NNN
  audit_log_id: aud-...
  target: "<kanban-task-id | routing-decision-id | worker-handoff-id>"
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
    - "<researcher-verified-claim-link>"
    - "<kanban-task-source-trail-link>"
    - raw/.../snapshot.json
  issue: "<one sentence — what was found>"
  recommended_action: re_route | require_verified_claim | add_source_trail_to_task | demote_priority | close_task | freeze_routing
  snapshot_as_of: YYYY-MM-DDTHH:MM:SSZ
  issued_at: YYYY-MM-DD
  temperature: 0.0
```

## Recently Consumed (last 5)

*Empty.*

---

**Discipline:**
- The most common FAIL here is a task that was routed from an unverified claim. The Researcher's `queue/verification-review.md` should be checked before any task acceptance.
- A FAIL on routing does not delete the kanban task. It flags it for re-routing or re-prioritization.
- Verdicts are about routing decisions, not about Hermes's overall orchestrator behavior. Don't grade the whole fleet on one decision.
