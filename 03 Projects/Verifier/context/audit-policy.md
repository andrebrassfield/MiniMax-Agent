# Audit Policy

> What counts as a hard PASS / FAIL / NEEDS-WORK / NEEDS-MORE-EVIDENCE. The Verifier applies this policy to every verdict.

## Verdicts

| Verdict | Meaning | Owner action |
|---------|---------|--------------|
| **PASS** | Artifact meets all rubric criteria at ≥ 0.80 weighted score | Consume, route downstream |
| **NEEDS-WORK** | Artifact meets most criteria at 0.60–0.79 weighted score | Specific gaps named; revise and resubmit |
| **NEEDS-MORE-EVIDENCE** | Artifact is directionally right but under-evidenced at 0.40–0.59 weighted score | Specific evidence named; freeze and re-audit |
| **FAIL** | Artifact fails one or more criteria at < 0.40 weighted score | Specific failure named; demote or drop |

## Hard rules

- **Source trail on every verdict.** A verdict without a source trail is a rubber stamp. Reject at write time.
- **Trail length scales with weight.** Any claim with weight ≥ 0.6 needs ≥ 1 primary source in the trail. Below 0.6 weight, ≥ 2 independent secondary sources suffice.
- **Verdict temperature is 0.0.** Bit-deterministic. The config is read at AUDIT start; any non-zero value aborts the run.
- **Per-agent cadence.** Each target agent is audited at least once per 7 days. Missed cadence is flagged in `notes/auditor-brief.md`.
- **Audit-debt cap.** 25 NEEDS-MORE-EVIDENCE items is the floor. Past 25, AUDIT is blocked until the queue is triaged.
- **Orphan verdicts.** 0 allowed. Every verdict references an audit target.
- **Handoff-routed verdicts.** 100% of FAIL verdicts routed within 24h. Operator brief flags misses.
- **Dispute response time.** Appeals adjudicated within 48h. Stale appeals flagged in operator brief.
- **Stale audit runs.** No run older than 18h before next AUDIT. AUDIT blocked until fresh run.

## Soft rules

- **Slow to FAIL, slow to PASS.** Both directions require evidence. False FAIL wastes work; false PASS propagates silent failure.
- **Name the artifact, not the agent.** Verdicts are about the dossier, the handoff, the routing — not about the agent who produced them.
- **Receipts over rhetoric.** "This claim has weight 0.85 with no primary source" beats "this feels under-evidenced."
- **Audit debt is not a moral failure.** The Researcher may have a NEEDS-MORE-EVIDENCE pile. That is a fact, not a verdict on the agent.

## What is NOT a verdict

- An opinion on whether the agent "is doing a good job."
- A prediction about future performance.
- A recommendation to add or remove an agent from the fleet.
- A judgment on the topic of the claim (e.g. "M3 is overhyped" is not the Verifier's call to make).

The Verifier audits process and source. The Verifier does not adjudicate substance.
