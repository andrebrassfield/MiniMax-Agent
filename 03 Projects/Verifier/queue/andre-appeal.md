# Andre Appeal — Verifier ↔ Andre

> Cases where a verdict was appealed by the agent it concerns, or where the Verifier cannot adjudicate without Andre's input.

## Pending (Andre to consume)

*Empty. New appeals appended by ADJUDICATE or direct escalation.*

## Convention

```yaml
- id: appeal-YYYY-MM-DD-NNN
  appellant: researcher | mavis | hermes
  original_verdict: vrd-...
  original_audit_log: aud-...
  appeal_reason: "<one sentence — what the appellant believes is wrong or missing>"
  new_evidence:
    - "<source-1>"
    - "<source-2>"
  escalator: verdict_cannot_be_made | rubric_itself_is_wrong | conflict_between_agents | cross_agent_trust_failure
  decision_needed_by: YYYY-MM-DD
  raised_at: YYYY-MM-DD
```

## Decided (last 5)

*Empty.*

---

**Discipline:**
- Andre's word is final on disputed verdicts. The verdict trail is still recorded.
- A rubric-itself-is-wrong appeal is a signal that `context/audit-rubric.md` needs a revision. Apply the revision, then re-run the original audit.
- A verdict_cannot_be_made escalation is honest. The Verifier says "I cannot adjudicate this" rather than rubber-stamp a PASS.
- The Verifier surfaces the appeal timeline in the operator brief. Stale appeals (>48h) are flagged.
