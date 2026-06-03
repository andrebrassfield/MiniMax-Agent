# Verification Review Queue

> Claims that are interesting but under-evidenced. They get triaged by Mavis (chief of staff) before being promoted to dossiers or routed to handoffs.

## Convention

Each entry is a YAML block:

```yaml
- id: clm-YYYY-MM-DD-NNN
  claim: "<one sentence>"
  weight: 0.0-1.0
  supporting_findings: [fnd-...]
  dossier: <lane>
  issue: under-evidenced | contradicts_existing_claim | single_source | stale_source | social_only
  routed_at: YYYY-MM-DD
```

## Pending Triage

```yaml
- id: clm-2026-06-02-026
  claim: "OpenAI released GPT-6 on April 14, 2026 with 2M context, 5-6T params, Symphony multimodal architecture, 40% perf improvement over GPT-5.4"
  weight: 0.15
  supporting_findings: [fnd-2026-06-02-026]
  dossier: frontier_ai
  issue: single_source
  issue: contradicts_existing_claim
  issue: extraordinary_claim
  routed_at: 2026-06-02
```

## Resolved This Cycle

*Empty.*

---

**Floor rule:** If this queue exceeds 50 items, REFRESH is blocked until Mavis triages. The Researcher surfaces this in the operator brief.

**Current size: 1.** Well under floor. No Mavis action needed this cycle.
