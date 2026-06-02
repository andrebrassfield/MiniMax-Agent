---
type: question
created: 2026-06-01
status: open
tags: [question, agent-architecture, state-machines, workflows]
---

# When Do Rigid State Machines Beat Open-Ended Execution?

> Anthropic's "Building Effective Agents" cleanly draws the workflow/agent line: workflows = predefined code paths, agents = model-directed control. But which wins in production is context-dependent. The interesting question is: at what task shape and scale does the rigidity become a liability instead of a feature?

## Why this matters

State machines (LangGraph-style, n8n-style) are how the field actually ships production agents in 2026. The OpenAI/LangChain debate is real: OpenAI's "Practical Guide" pushes model-led agents; LangChain's Harrison Chase pushed back hard, saying "most production 'agents' are workflows with agent-flavored steps." The honest answer is *both work, in different regimes*. The question is where the line is.

What I see in the research:
- **Workflows win on:** predictable, well-defined, latency-sensitive, regulated, low-tolerance-for-surprise tasks. Customer support routing. ETL pipelines. Form processing.
- **Agents win on:** open-ended, hard-to-spec, model-may-find-better-path tasks. SWE-bench. Long-horizon research. Code refactoring across many files.
- **Failure mode of workflows:** they don't recover from path-not-in-state-graph. If the user says something the workflow designer didn't anticipate, it either loops or fails.
- **Failure mode of agents:** errors compound. Anthropic's own multi-agent research post is explicit: "minor system failures can be catastrophic" because restarts are expensive and trajectories diverge.

The deeper question: **does M3's 1M context + native multimodality shift the line?** If the agent can hold the entire system spec in its head and reason about it as it goes, does that reduce the value of pre-defining the paths?

## What I've already considered

- **Position A (rigid SMs are always safer):** you audit the paths, you know what runs, you can prove compliance. The downside is brittleness when reality deviates. This is the regulated/enterprise default.
- **Position B (open-ended agents with M3 are better):** the model can adapt to situations the designer didn't anticipate. The downside is non-determinism — same prompt can give different plans. Hard to test, hard to certify.
- **Position C (the answer is hybrid):** rigid skeleton with agent-flexible joints. State machine defines the major states; the model picks actions within each state. This is what most production systems actually do, but it's an unstable equilibrium — pressure pulls in both directions.

What I don't have a clear answer on: **how to decide where to put the joints.** That's the engineering question that the literature doesn't solve.

## What I would need to answer this

- Real telemetry on production agent systems: where do they fail? Is the failure distribution "rare edge cases the workflow didn't cover" or "the agent went off the rails"?
- A side-by-side benchmark: same task corpus, workflow vs. M3-agent harness, measure completion rate + steps-to-complete + failure-mode distribution. OSWorld-Human (Abhyankar et al., June 2025) does this for GUI tasks; need it for general agentic.
- A theory of which task features predict the right answer: branching factor? number of valid paths? cost of wrong step? time horizon? My guess: **the number of valid plans per task** is the dominant variable. Single-plan = workflow, multi-plan = agent.

## When to revisit

- [x] When M3 with 1M context is benchmarked on multi-step production tasks vs. workflow equivalents
- [ ] When LangGraph / OpenAI / Anthropic publish next-gen multi-agent production data
- [x] Evergreen — this is a foundational architectural question

## Connections

- [[M3 Capabilities]] — what 1M context changes
- [[Multimodal GUI Loop]] — GUI tasks are the case where agents clearly beat workflows
- [[Reflexion Loop]] — self-correction inside an open-ended loop
- [[Mavis EA Workflow]] — my own hybrid: rigid rules (no deploys without approval) + flexible execution
- [[Anthropic Building Effective Agents]] — the source for the workflow/agent taxonomy
- [[Mavis EA Design]] — broader design context for where I sit on this spectrum

---
*Question seeded 2026-06-01 from Operation Apex Phase 1. Likely re-visited in Q3 2026 when more production data on M3-class agents lands.*
