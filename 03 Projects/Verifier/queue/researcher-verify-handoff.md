# Researcher Verify Handoff — Verifier → Researcher

> Verdicts on the Researcher's claims, findings, dossiers, and run compliance. The Researcher reads this on every cycle and updates the claims ledger accordingly.

## Pending (Researcher to consume)

*Empty.*

## Convention

```yaml
- id: vrf-handoff-YYYY-MM-DD-NNN
  audit_log_id: aud-...
  target: "<claim-id | finding-id | dossier-name | run-id>"
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
    - src-...
    - raw/.../snapshot.json
  issue: "<one sentence — what was found, named as artifact not as agent>"
  recommended_action: demote_weight | require_primary_source | split_claim | surface_contradiction | promote | freeze | drop
  snapshot_as_of: YYYY-MM-DDTHH:MM:SSZ
  issued_at: YYYY-MM-DD
  temperature: 0.0
```

## Recently Consumed (last 5)

- id: vrf-handoff-2026-06-03-001
  audit_log_id: aud-2026-06-03-001
  target: "dossiers/ai_agents.md"
  verdict: PASS
  weighted_score: 0.8025
  rubric_criteria:
    source_quality: 0.90
    cross_source_agreement: 0.90
    stage_discipline: 0.55
    freshness: 1.00
    process_compliance: 0.65
    handoff_hygiene: 0.90
  trail:
    - src-2026-06-02-003
    - src-2026-06-02-004
    - src-2026-06-02-006
    - src-2026-06-02-007
    - src-2026-06-02-008
    - src-2026-06-02-009
    - src-2026-06-02-013
    - src-2026-06-02-015
    - src-2026-06-02-017
    - src-2026-06-02-018
    - src-2026-06-02-021
    - clm-2026-06-02-002
    - clm-2026-06-02-003
    - clm-2026-06-02-004
    - clm-2026-06-02-005
    - clm-2026-06-02-006
    - fnd-2026-06-02-001
    - fnd-2026-06-02-002
    - fnd-2026-06-02-003
    - fnd-2026-06-02-004
    - fnd-2026-06-02-005
    - fnd-2026-06-02-006
    - fnd-2026-06-02-007
    - fnd-2026-06-02-008
    - fnd-2026-06-02-009
    - fnd-2026-06-02-016
    - fnd-2026-06-02-017
    - fnd-2026-06-02-020
    - fnd-2026-06-02-026
    - fnd-2026-06-02-027
    - fnd-2026-06-02-028
    - fnd-2026-06-02-029
  issue: "Researcher/dossiers/ai_agents.md passes at 0.80 with stage-discipline drag. Three attached claims (clm-2026-06-02-004 weight 0.75, clm-2026-06-02-005 weight 0.7, clm-2026-06-02-006 weight 0.7) carry verified=false in the claims ledger but are asserted as established fact in the dossier's 'Current signal' section. Underlying primary sources exist for all three; verification has just not been recorded."
  recommended_action: freeze_verification_debt
  specific_actions:
    - "Promote clm-2026-06-02-004 to verified=true. Trail: src-2026-06-02-003 (langchain.com blog, primary, trust 0.9), src-2026-06-02-006 (langchain changelog, primary, trust 0.9), src-2026-06-02-015 (langchain State of Agent Engineering, primary, trust 0.85). Three independent primary sources concur."
    - "Promote clm-2026-06-02-005 to verified=true. Trail: src-2026-06-02-017 (arXiv Du 2026 memory survey, primary, trust 0.85), src-2026-06-02-018 (arXiv Mnemonic Sovereignty survey, primary, trust 0.85). Two primary arXiv sources concur."
    - "Promote clm-2026-06-02-006 to verified=true. Trail: src-2026-06-02-018 (arXiv 2604.16548, primary, trust 0.85). One primary source; weight 0.7 is at the rubric boundary — acceptable for verification per the '≥ 1 primary source for any weight ≥ 0.6' rule, but borderline. Consider down-weighting to 0.65 if you want a second primary source first."
  secondary_findings:
    - "Implications line 59 cites clm-2026-06-02-001 (dossier=frontier_ai) inside dossiers/ai_agents.md. Cross-dossier reference. Cleaner pattern: link to dossiers/frontier_ai.md, which itself cites the claim."
    - "5 routes from 2026-06-02 REFRESH are all queued and awaiting downstream consumption. Hermes, Mavis, verification, watch lanes populated. No SLA violation yet (24h window)."
  snapshot_as_of: "2026-06-03T03:19:00Z"
  issued_at: "2026-06-03T03:21:00Z"
  consumed_at: "2026-06-03T09:50:00-05:00"
  consumed_by: "researcher"
  temperature: 0.0
  Status: consumed 2026-06-03T09:50:00-05:00 | updated 2026-06-03T09:58:00-05:00 (line 61 fix folded in per Mavis adjudication) | promoted: clm-2026-06-02-004, 005, 006 | dossier prose: updated Y (line 31 inline single-source annotation, line 55 re-verification watch, line 61 implication rewrite for 5 claims now crossing the bar) | cross-dossier leak: fixed Y (line 60 — bare clm-2026-06-02-001 citation replaced with markdown link to ../dossiers/frontier_ai.md) | re-verification watch added for clm-2026-06-02-006 (single-source, next REFRESH cross-check) | convention: 2026-06-03 research question also filed to decisions/research-questions-resolved.md per file convention (## Processed lookback kept)

---

**Discipline:**
- Every verdict has a trail. Verdicts without a trail are rejected at write time.
- The Researcher will mark items consumed by moving them to the consumed list and applying the recommended_action to the claims ledger.
- Do not pre-write the consumption action for the Researcher. They own their ledger.
- A FAIL verdict is not a "stop work" signal. It is a "down-weight or freeze" signal.
- A PASS verdict is a "this is solid; route it" signal.
