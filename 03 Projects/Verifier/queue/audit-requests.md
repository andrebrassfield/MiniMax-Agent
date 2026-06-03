# Audit Requests — incoming lane

> Mavis, Hermes, and the cron loop drop audit requests here. The Verifier processes them on the next AUDIT (or immediately if marked `urgent`).

## Pending (Verifier to consume)

```yaml
- id: aud-req-2026-06-03-001
  requester: mavis
  target_agent: verifier
  target_artifact: "tests/VERIFIER-TEST.md"
  reason: process_compliance_check
  urgency: low
  context: "First calibration AUDIT (RUN-20260603-0319Z) hit a brief-vs-reality gap. The test plan assumed dossiers/ai_agents.md was an empty stub (vacuously PASS at 1.0 except freshness 0.5). The dossier is now a real, post-REFRESH artifact — scored 0.8025. The Verifier correctly scored reality over expectation, but the calibration baseline is stale. Consider re-baselining the test plan for future calibration runs (either update the expected score to match current state, or make the test plan dynamic — pull live dossier state at test time)."
  requested_at: 2026-06-03
```

## Convention

```yaml
- id: aud-req-YYYY-MM-DD-NNN
  requester: mavis | hermes | cron | andre
  target_agent: researcher | mavis | hermes
  target_artifact: "<artifact-id or handoff-id>"
  reason: claim_weight_dispute | handoff_audit | process_compliance_check | periodic_audit | appeal
  urgency: low | normal | high | urgent
  context: "<one sentence — what triggered this request>"
  requested_at: YYYY-MM-DD
```

## Recently Consumed (last 5)

*Empty.*

---

**Discipline:**
- The Verifier processes this queue on the next AUDIT cycle. Mark `urgent` only when the failure mode is propagating downstream.
- The Verifier does not gate AUDIT on this queue being non-empty. The cron loop runs AUDIT every 6h regardless.
- Mavis may also drop items here when she wants a second look at a claim Mavis is promoting or a connection she is about to publish.
