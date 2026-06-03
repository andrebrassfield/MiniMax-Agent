# Verify Handoff — Researcher → Mavis (verification triage)

> Items the Researcher cannot or should not verify itself. Routed to Mavis for triage.

## Pending

*Empty. The single under-evidenced item surfaced this run (the GPT-6 rumor) is in `queue/verification-review.md` and is being triaged by Mavis via that lane. No additional items require a separate verify-handoff.*

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

*Empty.*

---

**Discipline:**
- Do not route items here just to clear your desk. The Researcher can verify many things via cross-source agreement and primary-source fetches. Use this queue only when verification requires a capability the Researcher does not have.
- Mavis may also drop items here when she wants a second look at a claim the Researcher is promoting.
