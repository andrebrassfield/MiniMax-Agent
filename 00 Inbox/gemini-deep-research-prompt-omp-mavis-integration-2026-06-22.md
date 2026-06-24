---
type: deep-research-prompt
target: Gemini Deep Research
author: Mavis (chief-of-staff for Andre)
date: 2026-06-22
context: Three open-source tools were ingested tonight (Egonex-AI/Understand-Anything, colbymchenry/codegraph, can1357/oh-my-pi). Andre wants a deep research on integrating oh-my-pi (and its upstream Pi by Mario Zechner) with Mavis (his chief-of-staff system) and his workflow.
---

# Deep Research Prompt: Integrating oh-my-pi (Pi) with Mavis

## Who is asking

**Andre** is the operator of an M-series MacBook running a multi-agent fleet (Mavis + Hermes + OpenClaw + gbrain). He runs a "second self" chief-of-staff system in the **Mavis** agent — a Loop Engineering system with 46 active skills, 6 bundles (cold-start-ops, ea-workflows, x-content-publish-ops, quality-ops, mac-setup-ops, archive), 55 vault topic files in a Karpathy-pattern LLM wiki at `~/MiniMax-Agent/`, and 40+ daily crons. He's been refining this system since 2026-02 with the explicit goal of building a Loop Engineer system, not a prompt-engineer system.

**Mavis** is the chief-of-staff agent (this assistant). She runs on **OpenCode** as the harness, with custom skills (markdown procedures at `~/.mavis/agents/mavis/skills/<name>/SKILL.md`), MCP tools (matrix, playwright, kanban, cu, trash, obsidian, google-calendar), crons at `~/.mavis/agents/mavis/crons/`, and a vault at `~/MiniMax-Agent/`. She writes Mavis EA design specs, decision logs, weekly connections, and second-self automation crons.

## What we ingested tonight (the trigger for this research)

Three repos on the same theme — "knowledge infrastructure for AI agents" — were analyzed together:

1. **[Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)** (66.3k stars) — multi-agent pipeline that builds a knowledge graph of any codebase/wiki. Supports Karpathy-pattern LLM wikis specifically.
2. **[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)** (53.3k stars) — pre-indexed code knowledge graph via single MCP tool (`codegraph_explore`). Already installed and indexed Mavis's skill library: 10,086 nodes, 22,543 edges, 40.69 MB DB.
3. **[can1357/oh-my-pi](https://github.com/can1357/oh-my-pi)** (14.2k stars) — `omp`, a terminal-first AI coding agent. **Fork of Mario Zechner's [Pi](https://github.com/badlogic/pi-mono).** ~55k lines of Rust core. 32 built-in tools, 40+ providers, 14 LSP ops, 28 DAP ops, hashline edits, persistent Python/JS kernels with tool re-entry, **advisor role** (second model watches every turn), **Hindsight memory** (agent-curated memory: retain/recall/reflect). The articles I read name Pieter Steinberger (OpenClaw, now OpenAI) and Boris Cherny (Claude Code, Anthropic) as the canonical references.

## What's been built tonight (relevant context)

- **Mavis-as-LLM pattern** codified: Mavis is structurally isomorphic to an LLM (Data → Tokenization → Training → Alignment → Evaluation). Skills = Component #3 of every loop. Subagents = Component #5. Memory = Component #6. ([`02 Notes/patterns/mavis-as-llm.md`](/Users/brassfieldventuresllc/MiniMax-Agent/02%20Notes/patterns/mavis-as-llm.md))
- **Loop Engineering plan** codified: Mavis IS the loop engineer system. The Loop Engineering article by Steinberger/Cherny validates this. ([`03 Projects/Mavis EA Design/specs/mavis-loop-engineering-plan-2026-06-22.md`](/Users/brassfieldventuresllc/MiniMax-Agent/03%20Projects/Mavis%20EA%20Design/specs/mavis-loop-engineering-plan-2026-06-22.md))
- **Skill-scaling-law** applied: 10 skills refactored from 94.5KB total to 24.1KB (74.5% reduction). Each refactored skill hits 1-2KB target.
- **6 bundle manifests** written at `~/.mavis/agents/mavis/bundles/`. Cold-start-ops loads in every root session; ea-workloads (14 skills), x-content-publish-ops (16 skills), quality-ops (7 skills), mac-setup-ops (2 skills), archive (5 deprecated) load on demand.
- **RLHF-analog feedback loop (Upgrade 2)** shipped: `ea-correction-capture` skill + `correction-classifier-nightly` cron + classifier script. Two-phase design (cron does filesystem scan; chief session does LLM classification because daemon doesn't expose external LLM endpoint).
- **5 deprecated skills archived** at `05 Archive/agents/mavis/skills/`: mavis-kanban-bridge, kanban-health-check, telegram-kanban-bridge, kanban-html-board, gepa-evaluator. Per the 2026-06-16 **Mavis ↔ Hermes absolute separation rule** (no read/write/diagnose/patch to `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/`).
- **MiniMax token dial-in** completed earlier: 56.6KB → 26.0KB always-on context (54% reduction). Today's burn is past allocation; tomorrow's Track 2 budget gets eaten.

## What I want you to research

### Primary questions (answer all)

1. **What is oh-my-pi (omp)?** Synthesize the project's philosophy, architecture, and key innovations. Cite primary sources (the README, the omp.sh docs, the can1357 blog posts, the underlying [Mario Zechner Pi](https://github.com/badlogic/pi-mono)).
2. **What is the upstream Pi? How does omp differ from Pi?** What's the value-add of the fork? Why did can1357 fork it? What does each do uniquely well?
3. **What is the architectural relationship between Mavis (chief-of-staff on OpenCode) and omp (terminal-first agent)?** Are they complementary (each does a different job), competing (both want to be the chief), or potential replacements (omp could become Mavis's new harness)?
4. **Could Mavis's skill library (~/.mavis/agents/mavis/skills/, 46 skills) be ported to omp extensions?** omp supports TypeScript extensions and uses the same skill model. What's the migration path? What's the gain? What's the cost?
5. **Could the chief-of-staff model (4 EA workflows + bundle manifests + cron-driven loops) work in omp?** omp has its own cron-style automations, slash commands, and extension system. Is the chief a special case of an omp session, or a separate role that orchestrates omp?
6. **What is the advisor role in omp?** This is a second model that watches every turn, injects inline concerns, course-corrects. How does this map to Mavis's "maker ≠ checker" subagent pattern (from the Loop Engineering article)? Could it become Upgrade 4 (the second-model-checker pattern)?
7. **What is Hindsight memory in omp?** retain/recall/reflect — agent-curated memory between sessions. How does it compare to Mavis's vault + MEMORY.md + topic files architecture? Are they competitive or complementary?

### Secondary questions (answer if time permits)

8. **What is the "harness problem" can1357's blog post is solving?** Read [https://blog.can.ac/2026/02/12/the-harness-problem/](https://blog.can.ac/2026/02/12/the-harness-problem/). What does the harness problem look like in 2026, and does Mavis already solve it?
9. **What are omp's key technical primitives that Mavis could borrow?** Hashline edits, persistent Python/JS kernels, LSP wired into every write, time-traveling stream rules, ACP (Agent Client Protocol), framework-aware routes. Which of these would improve Mavis's chief-of-staff work?
10. **What's the migration cost / risk for Andre?** He's burned through today's MiniMax token budget. He's got a working Mavis system. Switching harnesses is a major commitment. What's the smallest viable first step (a single skill, a single bundle, a single cron) that would let him test omp without disrupting Mavis?
11. **How does the Mavis ↔ Hermes absolute separation rule apply?** Hermes is a peer agent with its own filesystem territory. omp is a peer tool, not a peer agent. Does using omp introduce new separation concerns? Could omp become a peer-agent like Hermes, or is it structurally different?
12. **What would "Mavis running on omp" look like architecturally?** Two scenarios: (a) omp replaces OpenCode as the Mavis harness, with Mavis skills ported to omp extensions; (b) omp is invoked as a subagent by Mavis when Mavis needs code-editing capabilities it doesn't have natively.

## Deliverables I expect

1. **A 2-3 page synthesis** covering omp's philosophy, architecture, and key innovations, with primary-source citations.
2. **A Mavis-vs-omp comparison table** on at least these axes: harness design (12 components per Akash Pachaar), loop engineering (5 stages per the article), skills model, memory model, subagents model, advisor/verifier model, cost model, local-vs-cloud, harness portability, ecosystem maturity.
3. **Three concrete integration scenarios** ranked by effort/risk/return, with the smallest viable first step for each.
4. **A "do not do" list** — things that look attractive but would break the Mavis ↔ Hermes separation or duplicate effort already in Mavis.
5. **Primary sources cited inline** (GitHub URLs, blog posts, README sections). When you cite a popularization, also cite the primary source it's based on. When you cite a claim, link to the source.
6. **A 1-paragraph "if you only read one thing"** summary at the top of the report.

## Constraints on the research

- **Primary sources first.** When you cite the harness-problem article, link to the can1357 blog post AND to the underlying Steinberger OpenClaw architecture doc. When you cite advisor-role, link to omp's docs AND to the Boris Cherny Claude Code "maker ≠ checker" framing. When you cite Hindsight, link to omp's docs AND to the Self-Evolving Agents survey (arXiv 2507.21046).
- **No marketing copy.** When you cite benchmark numbers, link to the benchmark methodology. When you cite a star count, link to the repo at the moment of citation.
- **Honest about gaps.** If you can't verify a claim with a primary source, say so. Andre prefers "I don't know" over fabrication.
- **Respect the separation rule.** Any suggestion that involves reading from or writing to `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, or `~/.hermes-evolution/` is a hard NO. Flag any such proposal as a red flag, not a "consider with care."
- **Time-aware.** Andre is wrapping up a 9+ hour session. The research will land tomorrow or later this week. Be thorough but don't pad. Length is fine if every paragraph carries weight.

## Background context Mavis has primed for you

If helpful, the following vault notes are load-bearing for this research:

- [`02 Notes/patterns/mavis-as-llm.md`](/Users/brassfieldventuresllc/MiniMax-Agent/02%20Notes/patterns/mavis-as-llm.md) — Mavis is structurally isomorphic to an LLM
- [`02 Notes/patterns/loop-engineering-framework.md`](/Users/brassfieldventuresllc/MiniMax-Agent/02%20Notes/patterns/loop-engineering-framework.md) — the 5-stage loop + 6-block vocabulary
- [`02 Notes/articles/2026-06-22 - Loop-Engineering-in-2026.md`](/Users/brassfieldventuresllc/MiniMax-Agent/02%20Notes/articles/2026-06-22%20-%20Loop-Engineering-in-2026.md) — Loop Engineering article digest (Steinberger + Cherny)
- [`02 Notes/articles/2026-06-22 - 5-Stage-LLM-Pipeline.md`](/Users/brassfieldventuresllc/MiniMax-Agent/02%20Notes/articles/2026-06-22%20-%205-Stage-LLM-Pipeline.md) — 5-stage LLM training pipeline
- [`02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness.md`](/Users/brassfieldventuresllc/MiniMax-Agent/02%20Notes/articles/akash-pachaar-anatomy-of-an-agent-harness.md) — agent-harness pattern
- [`03 Projects/Mavis EA Design/specs/mavis-loop-engineering-plan-2026-06-22.md`](/Users/brassfieldventuresllc/MiniMax-Agent/03%20Projects/Mavis%20EA%20Design/specs/mavis-loop-engineering-plan-2026-06-22.md) — current Mavis loop engineering plan with 3 carry-over items
- [`01-PERMANENT/2026-06-22 - active-theses.md`](/Users/brassfieldventuresllc/MiniMax-Agent/01-PERMANENT/2026-06-22%20-%20active-theses.md) — 5 active theses (Mavis-as-LLM, etc.)
- [`MAVIS.md`](/Users/brassfieldventuresllc/MiniMax-Agent/MAVIS.md) — Mavis's weekly context (current state + theses)

## Where to send the result

Drop the research report in `00 Inbox/gemini-deep-research-omp-mavis-YYYY-MM-DD.md` and ping Mavis on Telegram. Mavis will read it, synthesize with everything in the vault, and present a final recommendation to Andre.

---

*Generated 2026-06-22 by Mavis, chief-of-staff for Andre. Cross-link this prompt with the Loop Engineering plan and the bundle manifest at `~/.mavis/agents/mavis/bundles/README.md`.*
