---
type: article
source: Loop Engineering synthesis citing Peter Steinberger (OpenClaw creator, OpenAI) + Boris Cherny (Claude Code, Anthropic), captured 2026-06-22
captured: 2026-06-22
tags: [article, loop-engineering, agent-loops, closed-loop, subagents, maker-vs-checker, mavis-design, mavis-loop-engineer]
status: processed
cross-refs: [02 Notes/patterns/mavis-as-llm.md, 02 Notes/patterns/loop-engineering-framework.md, 02 Notes/patterns/mavis-skill-scaling-law.md, 02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness.md, 02 Notes/articles/2026-06-22 - 5-Stage-LLM-Pipeline.md, 03 Projects/Mavis EA Design/specs/mavis-loop-engineering-plan-2026-06-22.md]
---

# Loop Engineering — What Every AI Engineer Needs in 2026

> Article digest. The thesis: **prompting is the old way; designing loops is the new way.** Two senior engineers (Steinberger + Cherny) named the shift independently. The rest of the article is the operational spec.

## The headline reframing (load-bearing for Mavis)

> "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents." — Peter Steinberger
> "I don't prompt Claude anymore. I have loops running that prompt Claude and figure out what to do. My job is to write loops." — Boris Cherny

**For Mavis:** Mavis is fundamentally a **Loop Engineer system**, not a prompt-engineer system. Every EA workflow, every cron, every skill is a loop. The article's vocabulary — Goal → Context → Action → Feedback → Stop — is the same shape as the 5-stage pipeline (Discover → Plan → Execute → Verify → Iterate) we already codified in `[[02 Notes/patterns/ea-loop-vocabulary]]`.

## The cost problem (the hidden blocker)

The article names what nobody else says: **loops are not hard to design, hard to afford.**

| Loop type | Token cost per run |
|---|---|
| Single-agent coding loop | 50K-200K tokens |
| Fleet loop (1 orchestrator + 3 specialists) | 500K-2M tokens |
| Daily cron loop | millions per week |

**For Mavis:** today's Track 1 burn (~$22 at 22:00 CT, likely $35-40+ now after the article ingest + spec + 11-skill refactor) is exactly the article's "single agent loop on a medium task" range. The dial-in cycle (56.6KB → 26.0KB always-on) was right; we just need to keep the discipline. The article justifies cheaper models for loop-heavy work; we don't have that lever (we use MiniMax-M3) so our lever is **lean skills + vault depth + cost ceilings per loop**.

## The 6 building blocks (the load-bearing components)

| # | Block | What it does | Mavis instantiation |
|---|---|---|---|
| 1 | **Automations** | Triggers DISCOVER; the heartbeat | 40+ crons at `~/.mavis/agents/mavis/crons/` |
| 2 | **Worktrees** | Parallel EXECUTE without collision | `mavis team plan` parallel streams (analog) |
| 3 | **Skills** | Project knowledge that compounds every run | 46 skills at `~/.mavis/agents/mavis/skills/` + 55 vault topic files |
| 4 | **Plugins/Connectors** | EXECUTE acts in real env, not just filesystem | MCP servers (matrix, playwright, kanban, cu, trash, obsidian, google-calendar) |
| 5 | **Subagents** | VERIFY is honest — maker ≠ checker | `verifier` agent, `gepa-evaluator`, `fleet-trust-patterns` topic |
| 6 | **Memory** | Loop never forgets between runs | MEMORY.md + topic files + vault + kanban as operational memory |

**For Mavis:** we have all 6. The article is essentially an external confirmation of the architecture. What's NEW is the explicit framing: **every cron is a loop; every loop needs all 6 components; missing any one breaks the loop.**

## The 5 parts of every good loop (cleaner reformulation)

| Part | Definition | Mavis discipline |
|---|---|---|
| **Goal** | What "done" means precisely | `ea-decision-logger` + scope statements in skills |
| **Context** | VISION.md / ARCHITECTURE.md / RULES.md | SOUL.md + MEMORY.md + MAVIS.md + vault |
| **Action** | Only what the agent needs | Lean skill bodies (1-2KB after the refactor) |
| **Feedback** | Tests, type checks, linters, structured errors | `ea-loop-audit` + `agent-disease-detector` cron |
| **Stop condition** | When the loop knows it's finished | HALT conditions + verification gates per skill |

## Closed loop vs Open loop (the practical distinction)

| Loop type | Use case | Cost | Mavis posture |
|---|---|---|---|
| **Closed** | Bounded, gated, has stop condition | Affordable | **Default for Mavis** — every cron is a closed loop |
| **Open** | Exploratory, wide latitude, no fixed stop | Expensive (millions/week) | **Justified only with explicit cost sign-off + bounded ceiling** |

The article: "For most real work today, closed looping is the one that pays off." Our `ea-loop-thinking` skill already encodes this as a hard constraint (default closed loop; open loop requires explicit Andre sign-off + bounded ceiling).

## Real loop examples (mapped to Mavis)

| Article's loop | Mavis analog |
|---|---|
| Coding Loop (read VISION → plan → edit → test → fix → summarize → stop) | `ea-5-mistakes-audit` on a work surface |
| Research Loop (define Q → search → summarize → verify → synthesize → stop on confidence threshold) | `ea-research-brief` (already a loop) |
| Content Loop (topic → draft → critique → rewrite → score → publish if pass) | `x-reply-guy` (5-phase loop with validation gate) |
| Sales Outreach Loop (ICP → find leads → enrich → qualify → personalize → quality review → send) | Not yet built — opportunity for future bundle |

## The mindset shift (load-bearing)

> **Prompt Engineer:** craft better instructions, linguistic skill, reviews output manually, you are the loop.
> **Loop Engineer:** design better feedback cycles, software engineering skill, system runs + checks + self-corrects, the system is the loop.

**For Mavis:** the chief-of-staff role IS loop engineering. The 4 EA workflows (`ea-daily-brief`, `ea-research-brief`, `ea-weekly-connections`, `ea-decision-logger`) are closed loops with goal → context → action → feedback → stop. The EA's value is NOT prompting Andre's agents — it's designing the loops around them.

## The closing insight (the part nobody says out loud)

> "Two people can build the exact same loop and get completely opposite results. One uses it to move faster on work they understand deeply. The other uses it to avoid understanding the work at all. The loop does not know the difference. You do."

**For Mavis:** the loop is a tool. Andre's judgment is what gives it direction. The chief-of-staff role is to encode Andre's judgment into loop design (goal definition, stop conditions, evaluation gates), not to replace it. This is exactly the "spec on disk before Track 2 spawn" discipline from SOUL.md: the spec IS the encoding of human judgment into the loop.

## Connections to existing Mavis operational model

- **`[[02 Notes/patterns/mavis-as-llm]]`** — the build-side lens. This article is the runtime-side lens. Together they describe Mavis.
- **`[[02 Notes/patterns/ea-loop-vocabulary]]`** — the 5-stage + 6-block vocabulary. This article is the same vocabulary at a higher level of operational detail.
- **`[[02 Notes/patterns/mavis-skill-scaling-law]]`** — the "Skills" component (#3) of every loop.
- **`[[02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness]]`** — the runtime architecture lens. This article is the loop-design lens. Together: how to build a harness + how to design loops that run on it.
- **`[[02 Notes/articles/2026-06-22 - 5-Stage-LLM-Pipeline]]`** — the data side. Loops consume tokens; data quality determines loop effectiveness.

## What I'd push back on or sharpen

The article is a popularization, not a primary source. The mechanics are older:
- **5-stage loop:** Karpathy "Let's build GPT from scratch" (2023), Boris Cherny's /loop (2024)
- **Subagents:** Claude Code docs (2024), OpenClaw architecture (2025)
- **Skills:** Akash Pachaar's anatomy article, `~/.claude/skills/` convention
- **Worktrees:** git worktrees (pre-LLM), adapted for parallel agent execution

The article's value is the SYNTHESIS — naming the loop engineering discipline + the cost problem + the mindset shift. Use it as the trigger; cite the primaries for the canonical references.

The "1M context + cheap models" framing at the end is a DeepSeek advertisement. The cost-discipline insight is real; the model recommendation is irrelevant to us (we use MiniMax-M3).

## Bottom line for Mavis

The article is an external validation of Mavis's architecture. The discipline is right; we have all 6 building blocks; we run closed loops as the default. The next steps are operational refinements, not architectural changes. See `[[03 Projects/Mavis EA Design/specs/mavis-loop-engineering-plan-2026-06-22]]` for the plan.
