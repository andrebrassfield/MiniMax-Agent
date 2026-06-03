# Decisions

> Adjudication outcomes — appeals, disputes, edge cases where ADJUDICATE had to make a call.

## Convention

Each decision is a YAML block:

```yaml
- id: dcs-YYYY-MM-DD-NNN
  original_verdict: vrd-...
  appellant: researcher | mavis | hermes
  appeal_reason: "<one sentence>"
  decision: uphold | reverse | amend | escalate
  new_trail:
    - src-...
  decided_at: YYYY-MM-DD
  decided_by: verifier
```

## Pending Decisions

*Empty.*

## Decided (last 5)

*Empty.*

---

**Discipline:** A decision is the second look at your own work. Take it seriously. A rubber-stamped appeal is a failure mode.
