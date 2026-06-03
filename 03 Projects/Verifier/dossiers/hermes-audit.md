# Dossier — Hermes Audit

> Per-agent audit dossier. Tracks Hermes's routing discipline, task acceptance criteria, and worker-handoff hygiene.

## Why this agent is audited

Hermes is Andre's fleet orchestrator. It routes work from the Researcher's `queue/hermes-handoff.md` to the worker pool. An orchestrator that routes unverified claims, or accepts tasks without source trails, propagates hallucination into the build layer.

## What Hermes does well
*Populated by AUDIT — observed routing discipline, source-trail enforcement, task acceptance criteria.*

## Common failure modes to watch
- **Routing unverified claims** — kanban task generated from a claim still in `queue/verification-review.md`.
- **Missing source trail** — task acceptance without the Researcher's source trail attached.
- **Premature completion** — task marked complete before the worker's output was verified.
- **Routing drift** — workers pulled for tasks they don't have the model/tools to execute.
- **Handoff hygiene** — tasks accepted without explicit acceptance criteria from the Researcher's handoff.

## Recent audit signal (last 5 verdicts)

| Date | Target | Verdict | Score | Issue |
|------|--------|---------|-------|-------|
| — | — | — | — | — |

## Process compliance checks (per routing)
- [ ] Task source claim is verified (`verified: true` in Researcher's `queue/hermes-handoff.md`)
- [ ] Source trail is attached to the kanban task
- [ ] Worker has the model/tools/runtime to execute
- [ ] Acceptance criteria are explicit and checkable
- [ ] Task did not bypass the Researcher's handoff lane
- [ ] Task completion triggered a verification step, not a self-report
- [ ] Failed routing (e.g. worker rejection) is logged with reason

## Audit cadence

- **Frequency:** every AUDIT cycle, sample-check 2-3 recent kanban tasks
- **Floor:** at least one audit per 7 days
- **SLA on FAIL verdicts:** routed to `queue/hermes-audit-handoff.md` within 24h

## Source trail

*Empty. First AUDIT will append.*
