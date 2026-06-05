# Verify Handoff — Researcher → Mavis (verification triage)

> Items the Researcher cannot or should not verify itself. Routed to Mavis for triage.

## Pending

*Empty. The Researcher's FDA 503A peptide dossier handoff to the Verifier is at `03 Projects/Verifier/queue/researcher-verify-handoff.md` (vrf-handoff-2026-06-05-001), the standard Researcher→Verifier lane. The Verifier owns scoring truth on that item. No additional items require a separate Mavis verify-handoff.*

## Convention

```yaml
- id: vfy-handoff-YYYY-MM-DD-NNN
  reason: needs_primary_source | needs_domain_expert | needs_expensive_observation | stale_since
  claim: "<the claim in question>"
  source_trail: [src-...]
  why_researcher_cant_verify: "<one sentence>"
  suggested_verifier: <mavis | hermes_qa | external_human | drop>
  routed_at: YYYY-MM-DD
```

## Recently Consumed (last 5)

*Empty. No items have been routed to Mavis from this queue in the current cycle.*

---

**Discipline:**
- Do not route items here just to clear your desk. The Researcher can verify many things via cross-source agreement and primary-source fetches. Use this queue only when verification requires a capability the Researcher does not have.
- Mavis may also drop items here when she wants a second look at a claim the Researcher is promoting.

**Cross-references:**
- 2026-06-05: Inaugural FDA 503A peptide dossier (8 claims) routed to **Verifier** (not Mavis) at `03 Projects/Verifier/queue/researcher-verify-handoff.md` — vrf-handoff-2026-06-05-001, audit_log_id aud-2026-06-05-001, dossier fda_503a_peptides. The Researcher self-weight is LIKELY PASS at ~0.93; two needs-adjudication items are flagged (docket-number inconsistency on the FDA meeting page, top-of-page meeting time vs. per-day FR times). Awaiting Verifier re-audit.
