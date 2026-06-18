# Anchoring Sources — ea-loop-thinking

The 5-stage + 6-block vocabulary is industry-aligned, not a
Mavis-invented framework. Cite primary sources, not the @sairahul1
popularization that introduced the term.

## Primary sources (in priority order)

### Boris Cherny (Claude Code, head of Claude Code at Anthropic)
- His published /loop workflow (Towards AI: "Stopped Prompting Claude,
  Writes Loops, Merges 150 PRs from Phone")
- The load-bearing rule: "Maker ≠ checker"
- The closed-loop gold standard: "all tests in test/auth pass and
  lint is clean" as the verification gate
- Sequoia AI Ascent 2026 interview (where the /loop pattern got its
  primary-source stamp)

### Peter Steinberger (OpenClaw author)
- steipete.me/posts/2026/openclaw (Feb 14, 2026)
- "OpenClaw is a Ferrari you have to bring a wrench for" — the open
  loop framing
- The cost ceiling discipline: "willing to spend on the order of a
  million dollars a year in tokens"

### OpenClaw architecture docs
- github.com/openclaw/openclaw (the harness architecture)
- The 6-block vocabulary (Automations / Worktrees / Skills / Plugins /
  Subagents / Memory) is the same vocabulary OpenClaw uses
- The 5-stage loop is the same loop OpenClaw runs

### Claude Code docs
- code.claude.com/docs/en/sub-agents (Subagents = builder/checker
  separation)
- code.claude.com/docs/en/skills (Skills = the load-bearing context
  layer)
- code.claude.com/docs/en/hooks (Hooks = the automation layer)
- The "loop" / "agent" / "command" primitives

### "12 Agentic Harness Patterns from Claude Code" (tool.lu/article)
- Richer block vocabulary than the 6-block summary
- Useful for: detailed pattern matching when the 6-block lens is
  too coarse

## Academic anchors

### Karpathy 2025 year-in-review
- https://karpathy.bearblog.dev/year-in-review-2025/
- The new 4th stage = RLVR (Reinforcement Learning with Verifiable
  Rewards) — verification as the loop's load-bearing element

### GEPA (Agrawal et al., arXiv 2507.19457, July 2025)
- "Reflective Prompt Evolution Can Outperform Reinforcement Learning"
- 6% avg / 20% max improvement over GRPO with 35× fewer rollouts
- The "reflective mutation" pattern: small surgical changes that
  close gaps, validated by verification

### Self-Evolving Agents survey (Gao et al., arXiv 2507.21046)
- The canonical 4-axis (What / When / How / Where) framework for
  self-evolution
- The "loops that don't write back to memory are loops that
  re-derive everything from zero" diagnosis

### Alita-G (Qiu et al., arXiv 2510.23601, Oct 2025)
- "Self-Evolving Generative Agent for Agent Generation"
- Agent generates its own MCP tools from observed patterns
- "Scaling data, not weights" — the loop is the scaling surface

## What NOT to cite

- The @sairahul1 popularization thread (the "if I have to ask you
  twice, you failed" + 90% test coverage framing is real; the
  popularization itself is the introduction, not the canonical
  source)
- Blog posts that don't link to a primary source
- Marketing copy that wraps any of the above in ad-slot language

## Why the primary-source discipline matters

The 5-stage + 6-block vocabulary is real, but it was named by
multiple people independently. Citing the popularization
(@sairahul1) is the equivalent of citing a Wikipedia article in an
academic paper — it points to the work, but the work itself is
elsewhere. The Mavis-side memory and skills cite primary sources
because (a) it's the disk-wins-over-recap discipline (file:line vs.
vague recall), and (b) primary sources don't drift when the
popularization changes its framing.
