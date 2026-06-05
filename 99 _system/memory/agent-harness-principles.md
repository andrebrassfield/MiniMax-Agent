---
description: "When to apply the agent-harness pattern (12 components, 7 decisions, future-proofing test, scaffolding-removal discipline). Read when designing, adding, or auditing an LLM-based agent system, deciding whether a new agent role is justified, diagnosing agent failures, or evaluating tool surface area. Anchors the cross-project principle 'the harness is the product, not the model.'"
---

description: When to apply the agent-harness pattern (12 components, 7 decisions, future-proofing test, scaffolding-removal discipline). Read when designing, adding, or auditing an LLM-based agent system, deciding whether a new agent role is justified, diagnosing agent failures, or evaluating tool surface area. Anchors the cross-project principle "the harness is the product, not the model." Full framework in `~/MiniMax-Agent/02 Notes/patterns/agent-harness.md` (project layer).
---

# Agent harness pattern — when to apply

## The trigger (cross-project, reusable)

Apply the agent-harness pattern when *any* of these are true:

- About to add a new agent role to a team → run the **future-proofing test** before committing
- A workflow is failing or compounding errors → **look at the harness first**, not the model
- Designing a new LLM-based tool, skill, or system → audit the **tool scope minimum** (Vercel removed 80% of tools, Claude Code does 95% context reduction via lazy loading)
- Reviewing existing agents for retirement → apply the **scaffolding-removal discipline** (Manus was rebuilt 5 times in 6 months, each removing complexity)
- The model fails a task → don't reach for a smarter model. Audit the prompt, the tool surface, the verification loop, the error path, the context window management.

## The four meta-principles (memorize these)

1. **If you're not the model, you're the harness.** (Vivek Trivedy, LangChain)
2. **Scaffolding is removed as the model improves — never accumulate.** Each new agent role, tool, or constraint must pass the *future-proofing test*: if this complexity stays necessary as the model improves, it's wrong complexity.
3. **Tool scope should be minimum for the current step.** Bias toward fewer tools, exposed on demand. More tools ≠ more capable. Vercel: -80% tools = better. Claude Code: 95% context reduction via lazy loading.
4. **The harness is the product, not the model.** TerminalBench: same model + different harness = 20+ ranking positions. LangChain jumped 25 ranks by changing only the infrastructure.

## The Von Neumann frame (one line, durable)

LLM = CPU. Context window = RAM. Vault/databases = disk. Tools = device drivers. Harness = OS.

## The 12 components (the canonical checklist)

1. Orchestration Loop (ReAct / TAO) 2. Tools 3. Memory 4. Context Management 5. Prompt Construction 6. Output Parsing 7. State Management 8. Error Handling 9. Guardrails 10. Verification Loops 11. Subagent Orchestration 12. Lifecycle / Scaffolding Management

## The 7 decisions (the architecture choices)

1. Single vs multi-agent 2. ReAct vs plan-and-execute 3. Context window management 4. Verification loop 5. Error handling 6. Guardrail placement 7. Subagent orchestration model

## The future-proofing test (verbatim)

> If performance scales up with more powerful models *without* adding harness complexity, the design is sound.

## The co-evolution warning (verbatim)

> Models are post-trained with specific harnesses in the loop. Changing tool implementations can degrade performance because of this tight coupling.

## Default biases (when in doubt)

- **Thin over thick.** Anthropic regularly deletes planning steps as new model versions internalize them.
- **Few tools over many.** Lazy-load aggressively.
- **Verification over trust.** Boris Cherny: verification = 2-3x quality improvement.
- **Restrictive permissions on irreversible actions; permissive on reversible ones.**
- **The model is rarely the problem. The harness usually is.**

## Failure-mode vocabulary (named to avoid)

- "More tools = more capable" intuition → wrong; it's a tax
- "We'll add a subagent to handle X" → check if the chief prompt can hold X first
- "The model can't do this" → almost always wrong; audit the harness
- "Permanent organ" framing for new agents → wrong; default to scaffolding-removable

## Where the full pattern lives

Vault: `02 Notes/patterns/agent-harness.md` (project memory — full 12 components, 7 decisions, Von Neumann frame, scaffolding-removal discipline, future-proofing test, Mavis's current implementation status). This topic file is the *trigger* to consult that pattern note.

Source article: Akash Pachaar, "The Anatomy of an Agent Harness," Apr 6. Digested in vault `02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness.md`.
