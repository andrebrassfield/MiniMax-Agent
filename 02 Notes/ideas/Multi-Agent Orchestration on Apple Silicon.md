---
type: capture
created: 2026-06-02T18:30:00+00:00
source: crucible-synthetic
category: technical
tags: [crucible, technical, synthetic, m3-eval-lab]
---

# Multi-Agent Orchestration Architecture for Apple Silicon

Need to think through how to build a 5-agent pipeline (intake → router → executor → QA → reporter) that runs on M3 hardware with the M3 1M context window as the shared blackboard. Concerns:

1. **Token economics** — at 4-byte tokens, 1M context = 4MB. Apple Silicon UMA is unified memory so the cost is bandwidth not allocation. But each agent invocation copies the relevant prefix.

2. **Bounded vs unbounded agents** — the intake agent should be stateless and fast; the QA agent (Wholeness-Engine) needs the full rubric in context; the reporter can be templated. Mixed topologies.

3. **Failure modes** — if the QA agent rejects a note, do we loop back to intake (re-route), to executor (re-do), or to router (re-decide)? Each has different cost profiles.

4. **Esalen posture** — what should the deterministic Python layer enforce vs what should M3 decide? I think: Python enforces the topology (agent order, retry counts, timeouts), M3 decides per-call (which skill, which file, what sharpening).

Question: how would you structure the agent blackboard? Pass the full vault context to every agent, or maintain a per-agent working set with explicit handoff? I'm leaning toward handoff with named slots (intake-output, routing-decision, executor-result, qa-score) so each agent only sees what it needs, but I worry about the integration overhead.

Related: mycelial routing in the resolver (02 Notes/patterns/Mycelial Routing.md) suggests we should bias toward high-flow skills but I don't see how that fits cleanly into a sequential pipeline.
