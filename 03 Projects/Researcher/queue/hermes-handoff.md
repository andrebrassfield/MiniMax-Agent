# Hermes Handoff — Researcher → Hermes (fleet orchestrator)

> Route to Hermes: buildable, verified, ready-to-route work. Hermes turns this into kanban tasks for the worker pool.

## Pending (Hermes to consume)

```yaml
- id: hms-handoff-2026-06-02-001
  type: build_task
  title: "Adopt Anthropic Claude Managed Agents patterns — Outcomes (rubric-graded task success) and Multiagent Orchestration (lead + specialist subagents, shared filesystem) — in Hermes worker pool"
  dossier: ai_agents
  evidence:
    claim: "Anthropic shipped Managed Agents on May 12, 2026 with four primitives: Dreaming, Multiagent Orchestration, Outcomes (+10pt task success on hardest problems per Anthropic's internal benchmarks), Webhooks. Claude Code 2.1.154 (May 28) ships Dynamic Workflows in research preview."
    weight: 0.85
    source_trail: [src-2026-06-02-009, src-2026-06-02-013, src-2026-06-02-008]
    verified: true
  scope: medium
  estimated_effort: 16
  depends_on: []
  routed_at: 2026-06-02

- id: hms-handoff-2026-06-02-002
  type: build_task
  title: "Default Hermes Codex workers to gpt-5.5 once OpenAI API is live ($5/M input, $30/M output, 1M context, Terminal-Bench 2.0 82.7%, GDPval 84.9%)"
  dossier: frontier_ai
  evidence:
    claim: "GPT-5.5 is the current OpenAI frontier as of June 2, 2026, available in Codex with 1M context. API access 'very soon' per OpenAI's Apr 24 update. Generally available on AWS Bedrock as of Jun 1, 2026."
    weight: 0.9
    source_trail: [src-2026-06-02-001, src-2026-06-02-002, src-2026-06-02-010]
    verified: true
  scope: small
  estimated_effort: 4
  depends_on: [hms-handoff-2026-06-02-001]
  routed_at: 2026-06-02
```

## Recently Consumed (last 5)

*Empty. Hermes has not yet consumed items from this file.*

---

**Discipline:**
- Verified-only. `verified: true` is required. If you have not verified, route to `queue/verify-handoff.md` instead.
- Source trail must survive audit. Hermes workers will pull it.
- Do not pre-assign workers; Hermes owns routing.
- Skip if the task is "research the X" — that is a research question for the Researcher, not a Hermes task.
