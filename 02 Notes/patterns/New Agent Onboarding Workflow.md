---
type: capture
created: 2026-06-02T18:30:00+00:00
source: crucible-synthetic
category: workflow
tags: [crucible, workflow, synthetic, m3-eval-lab]
---

# New Agent Onboarding Workflow

When a new AI agent joins the Omni-Operator (e.g., when I bring in a second M3 instance, or when I spin up a specialized agent for a domain), I need to onboard it. The onboarding should:

1. **Read the existing vault** — the agent should know the CHIEF conventions, the existing MOCs, the user's voice, the recent projects.
2. **Take a self-test** — generate 5 atomic notes from prompts I give it, score them with the Wholeness-Engine. If average score < 20, the agent isn't ready.
3. **Shadow for 24 hours** — the new agent observes the daemon's invocations, my M3 routing decisions, the Wholeness-Engine's surgeries. It learns the patterns.
4. **Take a co-pilot test** — for one full day, the new agent and I both generate drafts of the same outputs (e.g., a connection note, a sharpening). Compare. If the agent's outputs are 90%+ as good, it's ready for solo.
5. **Solo trial** — for one week, the new agent runs the Omni-Loop alone. The human reviews a sample of outputs daily.
6. **Certify or reject** — at the end of the week, the human certifies the agent. If certified, it joins the fleet. If not, it goes back to step 3.

This is a multi-day workflow. The Wholeness-Engine is the gate. The PatternForge could generate the self-test prompts.

Where does this live? 03 Projects/Agent-Onboarding/. A reusable workflow.
