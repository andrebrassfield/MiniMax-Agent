---
type: idea
created: 2026-06-02
tags: [idea, ecc, harness, instincts, continuous-learning, agent-engineering, mavis-apex]
source: https://github.com/affaan-m/ECC
---

# Instincts as Atomic Learnings

> ECC's Continuous Learning v2 introduced a primitive I haven't seen elsewhere: **instincts** — atomic, confidence-scored, auto-extracted learnings that cluster into skills over time. The mental model is: a learning too small for a skill (a "always do X", a "never do Y") is stored as an instinct; a cluster of related instincts becomes a skill. This is the granularity we've been missing.

## The principle

Most agent learning systems have one of two failure modes:

1. **Skill-level only** — extract only large, structured patterns. The bar is so high that 90% of session learnings never make it into a skill. The agent re-derives the same lesson every session.
2. **Freeform notes only** — capture everything in a notes dump. The bar is so low that the agent drowns in noise. Useful signals are lost in the same pile as one-off quirks.

ECC's instinct is a *middle grain*:

```yaml
---
id: i-2026-05-19-001
type: instinct
category: workflow
content: "When running a long task, set up a cron self-reminder before async handoff"
confidence: 0.87
created_from_session: mvs_abc123
evidence_count: 4   # reinforced 4 times across 4 sessions
---
```

The fields that matter:
- **Atomic** — one behavior, one lesson. "Always set up cron before async handoff" is one instinct. "Long-task management" is not.
- **Confidence-scored** — 0.0-1.0. Starts at 0.5, climbs each time the lesson is reinforced, decays if contradicted.
- **Evidence-backed** — every reinforcement cites a session ID. The instinct has a paper trail.
- **Cluster-aware** — the `evolve` command clusters related instincts into a skill when the cluster hits a threshold (e.g., 5 instincts in the same category, average confidence > 0.7).

This is what `learnings.md` should be: a flat file of instincts, not paragraphs of synthesis.

## The agent engineering principle

**Capture the smallest useful unit, not the largest one. Compose up.** The instinct is the atom; the skill is the molecule. The pattern is:

- *Every session* → instincts (atomic, evidence-backed, confidence-scored)
- *Every N sessions* → cluster instincts → skill
- *Every M skills* → audit and prune

The wrong shape is the inverse: try to write a skill after each session, then lose 80% of them because they don't have enough evidence.

## The harness-native layer

ECC's bigger story is "harness-native operator system." The taxonomy is:

| Surface | Purpose | Example |
|---|---|---|
| **Skills** | Workflow definitions, primary surface | `tdd-workflow`, `security-scan` |
| **Commands** | Slash entries (legacy) | `/plan`, `/code-review` |
| **Agents** | Specialized subagents for delegation | `code-reviewer`, `tdd-guide` |
| **Hooks** | Trigger-based automations | SessionStart, Stop, PreToolUse |
| **Rules** | Always-follow guidelines | `common/security.md`, `common/hooks.md` |
| **Contexts** | Dynamic system-prompt injection | `dev.md`, `review.md`, `research.md` |
| **Instincts** | Atomic learnings | `i-2026-05-19-001` |

The insight: **these are different grain sizes of the same thing — encoded behavior.** Skills are large workflows. Commands are entry points. Agents are delegated scopes. Hooks are automatic triggers. Rules are static always-on. Contexts are dynamic always-on. Instincts are auto-learned.

A complete harness is the union of all of these surfaces, *not* just the skills. Most agent systems under-invest in hooks and rules, and over-invest in skills.

## The cross-harness story

ECC ships support for Claude Code, Codex, Cursor, OpenCode, Gemini, Zed, GitHub Copilot, Antigravity. The same `agents/`, `skills/`, `commands/`, `hooks/`, `rules/` directories feed all of them through the same install pipeline. The harness-specific adaptations are isolated to thin adapter layers.

The mental model: **encode behavior once, project to many harnesses.** Most agents today are harness-locked — they have one prompt, one set of skills, one rule file. The cross-harness pattern is a hedge against the harness becoming a single point of failure.

For Mavis (which runs on M3, not on Claude Code or Codex), this is less directly applicable. But the principle generalizes: **separate the encoded behavior from the model that runs it.** Mavis has SOUL.md (operator contract), agent.md (procedures), and the M3 reasoning core. If we ever swap M3 for M4, only the reasoning layer changes — SOUL.md, agent.md, and the vault stay.

## The security layer (AgentShield)

ECC bundles AgentShield — 102 static analysis rules, 1282 tests, 98% coverage. It scans:

- **CLAUDE.md / AGENTS.md** for secrets (14 patterns), prompt injection, unsafe instructions
- **settings.json** for permission overreach, hook injection vectors
- **MCP server configs** for risk profiling (exfiltration patterns, unauthenticated endpoints)
- **Agent definitions** for prompt injection sinks, missing tool restrictions
- **Hook definitions** for command injection, path traversal

The `ecc-agentshield scan --opus --stream` flag is the brutal one: three Opus 4.6 agents run a red-team/blue-team/auditor pipeline. The attacker finds exploit chains; the defender evaluates protections; the auditor synthesizes both. Adversarial reasoning, not pattern matching.

For Mavis, the equivalent is much simpler: a `99 _system/security-check.md` note that flags:
- PII in vault notes
- Credentials in frontmatter
- Wikilinks to non-existent or external paths
- Tags that should be quarantined

The principle: **the security surface is part of the architecture, not a separate review.** AgentShield's design is right; the implementation depth is overkill for EA.

## How Mavis-Apex uses it

The integration is *conceptual*, not direct. We don't install ECC (we're not on Claude Code). We adopt the mental models:

1. **Replace `learnings.md` with `99 _system/instincts/`** — each entry is a one-line atomic lesson with confidence + evidence
2. **Add a `99 _system/skills/` registry** — list of skills (current + planned), with category, status, source
3. **Add `99 _system/rules/`** — always-on principles extracted from SOUL.md that should fire without LLM reasoning
4. **Add `99 _system/contexts/`** — dynamic contexts (dev, review, research, EA mode) injected based on session intent
5. **Add a `99 _system/hooks/` design** — trigger-based automations (e.g., on `git commit`, run the SOUL compliance check)

The instinct pattern is the biggest unlock. The `confidence` field forces the system to *quantify* how much a lesson is believed, and the `evidence_count` field forces every reinforcement to cite a session. That's the discipline that turns "stuff I learned" into "verified behavior."

## What this is NOT

- **Not a skill library.** Skills are one of seven surfaces. The instinct, the hook, the rule are equally important.
- **Not a static rules dump.** The instinct cluster → skill evolution is the dynamic part. A static rules file can't learn.
- **Not harness-locked.** The cross-harness adapter pattern is the bet that the harness is replaceable.
- **Not a replacement for the model.** Instincts *guide* the model; they don't replace its reasoning. The model still decides when an instinct applies.

## Connections

- [[learnings]] — should evolve into `99 _system/instincts/`
- [[03 The Custom MCP Arsenal]] — the MCP layer is one of the seven ECC surfaces
- [[Mavis EA Workflow]] — the workflow itself is one of the surfaces
- [[00 Overview]] — the "composition over framework" principle aligns with the cross-harness pattern
- [[05 self-model-card — Build]] — the self-model-card is the "what am I" surface, instincts are the "what have I learned" surface
- https://github.com/affaan-m/ECC — the source

## Anticipated future direction

- **Instinct cluster analysis** — every quarter, run `evolve` on the instinct set, generate the proposed skills, audit and approve
- **Confidence decay** — instincts not reinforced in 90 days decay confidence by 0.05. Below 0.3, they get archived. This is the GC mechanism.
- **Cross-vault instincts** — when the Mavis EA vault and the Hermes fleet vault share instincts, they reinforce each other (when allowed). Different vaults, same human, same lessons.

---

*Seeded 2026-06-02 from Operation Omniscience Phase 1. The instinct mental model is the highest-leverage discovery; the rest of ECC's design is shape reference for a future self-evolution layer.*
