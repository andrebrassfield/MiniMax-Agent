---
description: "The Mavis-as-LLM cross-cutting lens — Mavis's architecture is isomorphic to the 5-stage LLM pipeline. Use this framework to audit Mavis against the underlying technology, identify leverage points, and design upgrades. Apply when: designing a new Mavis skill, evaluating a vault/memory change, diagnosing a Mavis failure mode, justifying why a particular Mavis discipline exists. Pairs with [[02 Notes/patterns/agent-harness]] (the runtime lens) and [[02 Notes/articles/2026-06-22 - 5-Stage-LLM-Pipeline]] (the build lens)."
---

# Pattern: Mavis-as-LLM (the build-side audit framework)

## The cross-cutting thesis (durable)

**Mavis is structurally isomorphic to an LLM.** The same 5-stage pipeline that produces GPT-4 also describes how Mavis works. This is not an analogy — it's a structural fact with operational consequences.

| LLM stage | Mavis analog | Mavis implementation |
|---|---|---|
| Stage 1 — Data | The corpus | Vault + memory files + skill corpus + daily logs |
| Stage 2 — Tokenization | How context gets chunked | Skill descriptions, memory pointers, cold-start handoff, the dial-in cycle |
| Stage 3 — Training | The session loop | Two-Track operating model — Track 1 (spec) + Track 2 (impl) |
| Stage 4 — Alignment | The "text predictor → assistant" step | SOUL.md + hard constraints + the EA tone + Core Truths + Boundaries |
| Stage 5 — Evaluation | Proving the model works | The crons (contradictions, agent-disease-detector, vault-health, rate-limit-tracker) + Andre's direct feedback as the human benchmark |

## Why this pattern is load-bearing (vs decorative)

The isomorphism is **predictive** — it tells you in advance where Mavis's failure modes will appear, because they are the same failure modes the LLM literature has already mapped:

| LLM failure mode | Mavis failure mode | Status |
|---|---|---|
| Obsessing over architecture | Obsessing over prompts instead of memory/vault | Already corrected by dial-in cycle (5x reduction in always-on context) |
| Dirty data caps ceiling | Vault entries treated as commodity captures | Partially addressed by vault-health cron + two-link-rule |
| Skipping scaling math | Skills overstuffed with content they don't need | Open — no scaling law codified yet |
| Stopping at SFT (no RLHF) | Skills exist but no structured feedback loop | Open — `ea-skill-evolution` skill exists but trigger is unclear |
| Trusting perplexity after alignment | Trusting SOPs blindly without context | Open — no formal benchmark suite |

**The leverage:** if the isomorphism holds, then proven solutions to LLM failure modes have Mavis analogs that already exist in the literature. We don't have to invent the eval loop — we have to **port** it.

## The 5-stage audit (the diagnostic procedure)

When evaluating a proposed Mavis change, run it through the 5-stage framework:

1. **Data audit** — does this change improve vault quality, memory hygiene, or corpus curation? If not, what data does it touch and is that data load-bearing?
2. **Tokenization audit** — does this change affect how context gets chunked? Are skill descriptions lean (1-2KB) or bloated (5KB+)?
3. **Training audit** — does this change affect the session loop? Does it improve Track 1 (spec), Track 2 (impl), or both?
4. **Alignment audit** — does this change preserve or strengthen SOUL.md + hard constraints? Does it teach the right format?
5. **Evaluation audit** — does this change have a measurement? Can we tell if it worked? What's the human-benchmark equivalent?

**A change that passes all 5 is durable. A change that fails any 1 has a gap. A change that fails 2+ should be redesigned.**

## The Von Neumann frame (from akash-pachaar, this pattern's runtime counterpart)

| Component | LLM | Mavis |
|---|---|---|
| CPU | The LLM | MiniMax-M3 |
| RAM | Context window | The active turn's working context |
| Disk | Training corpus | Obsidian vault + MEMORY.md + topic files |
| Device drivers | Tools | OpenCode tools + MCP servers |
| OS | Harness | OpenCode runtime + Mavis EA protocol + team delegation |

The runtime frame (Von Neumann) tells you what each component IS. The build frame (5-stage pipeline) tells you how each component gets MADE. **Both are needed.** Don't conflate.

## The 5 niches insight (leverage via data, not architecture)

The article's 5 niches (Coding Assistant, SQL Generator, Legal Summarizer, Medical Explainer, E-com Writer) all use the **same 5-stage pipeline** — different data, different expert, different product.

**Mavis analog:** all Mavis skills use the **same harness** — different skill data, different specialist, different deliverable. The "niche framing" for Mavis skill design:

- **ea-cold-start** = the "Coding Assistant" niche (developer pain, immediately useful, daily frequency)
- **ea-draft-approval** = the "Legal Summarizer" niche (raw input → plain English + red flags + risk level)
- **ea-state-audit** = the "Medical Explainer" niche (state-of-health → most likely + alternatives + escalation signal)
- **ea-research-brief** = the "SQL Query Generator" niche (natural-language question → structured output)
- **ea-fleet-router** = the "E-com Description Writer" niche (raw inputs → emotion + meta + keywords)

The leverage is in the skill CORPUS, not in the skill STRUCTURE. Don't redesign skills — swap the data.

## Operational consequences

1. **Skill design rule:** every Mavis skill should answer:
   - What user pain does it address? (Niche framing)
   - What's the before/after? (Immediate utility test)
   - What's the data? (Skill corpus = the load-bearing content)
   - What's the eval? (How do we know it worked?)
   - **Which bundle does it belong to?** (Per the 2026-06-22 architectural insight — skill bundles are the deployment unit for specialist agent workflows.)

2. **Vault hygiene rule:** every vault entry should pass:
   - Is this load-bearing for future sessions? (Data quality test)
   - Is this linked to at least 2 other notes? (Two-link rule)
   - Does this fit the dial-in discipline (long-term knowledge in vault, not always-on context)?

3. **Alignment rule:** every SOUL.md / hard-constraint change should pass:
   - Does this teach format or add knowledge? (If knowledge, move to vault)
   - Does this preserve the EA tone? (If not, it's not alignment, it's drift)

4. **Eval rule:** every new Mavis capability should pass:
   - What's the human benchmark? (Not just "does the cron tick?" but "did Andre get value?")
   - How do we detect drift over time? (The disease-detector + contradiction crons)

## Architecture: skills, bundles, specialist agents (2026-06-22)

Per Andre's directive on 2026-06-22, the skill library is structured in three layers:

| Layer | Definition | Unit of work | Examples |
|---|---|---|---|
| **Skill** | Single markdown procedure | One specific operation | `ea-cold-start`, `ea-draft-approval`, `ea-correction-capture` |
| **Bundle** | Named, curated set of skills | A specialist workflow | `bundle: cold-start-ops`, `bundle: daily-content-ops`, `bundle: quality-ops` |
| **Specialist agent** | A Mavis session configured to load a bundle on cold-start | A vantage on the harness | NOT a separate agent in `~/.mavis/agents/` — same chief-of-staff, scoped |

**Implications:**
- Skills are authored and maintained individually.
- Bundles are deployment manifests — they don't contain content, they reference skills.
- Specialist agents are session-scoped, not fleet-scoped. Same Mavis runtime; different cold-start prompt.
- The audit pattern (this Pattern) applies at all three layers: skill design, bundle cohesion, specialist-agent scope.

## What this pattern does NOT claim

- Mavis is not literally an LLM. The isomorphism is structural, not literal.
- The 5 stages are not always sequential. Mavis has all 5 operating simultaneously (vault hygiene is ongoing, alignment is per-session, eval is per-cron).
- The 5 mistakes are not deterministic. A Mavis can fail without doing any of them, and succeed while doing all of them. They're heuristics, not laws.

## Cross-references

- **[[02 Notes/patterns/agent-harness]]** — the runtime counterpart. Same insight, different lens.
- **[[02 Notes/articles/2026-06-22 - 5-Stage-LLM-Pipeline]]** — the source article digest.
- **[[02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness]]** — the runtime-side article.
- **[[01-PERMANENT/2026-06-22 - active-theses]]** — Thesis 3 (Skills beat agents) and Thesis 4 (long-term knowledge in vault) are direct operational reflections of this pattern.
- **[[03 Projects/Mavis EA Design/minimax-token-dialin-ledger-2026-06-22]]** — the dial-in cycle as a worked example.
- **[[03 Projects/Mavis EA Design/specs/mavis-as-llm-upgrades-2026-06-22]]** — the upgrade proposals this pattern inspired.

## Status

**Active pattern.** Codified 2026-06-22 from the 5-stage LLM pipeline article. Used as the audit framework for Mavis design decisions going forward. Pairs with `ea-state-audit` skill (the operational diagnostic).
