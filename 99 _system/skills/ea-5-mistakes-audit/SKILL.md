---
name: ea-5-mistakes-audit
description: Diagnostic skill that audits a Mavis-side work surface (skill, workflow, recurring loop, project setup) against the 5-mistakes framework derived from the @sairahul1 "How To Build Your Own LLM" article, **augmented with the 2025-2026 missing-stage (RLVR), saturated-benchmark, prod-observability, and regulatory pitfalls** the article omits. The 5 mistakes mapped to EA work: (1) obsessing over architecture / tool surface instead of the data corpus; (2) treating vault/memory data as commodity; (3) skipping the scaling math (is this skill worth the human-time to codify?); (4) stopping at SFT (writing skills but not building feedback loops); (5) trusting surface metrics after alignment (looking at throughput, not whether the user is happy). The 2025-2026 additions: (6) skipping the verifiable-rewards stage (no auto-eval on tasks with programmatic success criteria); (7) using saturated benchmarks (MMLU-style tests that no longer discriminate frontier); (8) ignoring inference cost (loops that burn tokens without a ceiling); (9) no eval pipeline / no disease detection in production; (10) no observability (can't tell after the fact whether the loop ran correctly); (11) ignoring regulatory realities for high-stakes work surfaces (EU AI Act high-risk classification, FDA PCCP for medical AI/ML, HIPAA for PHI, state-bar UPL on legal AI). Use this skill as a pre-flight check before shipping a skill / workflow / loop, and as a self-audit on "why is this not working." Triggers on skill creation, workflow design, recurring-loop first run, on any work surface that touches regulated domains, and on Andre saying "audit this", "what's wrong with this", "is this good enough". Do NOT load for trivial single-step work or for tasks in other agents' trees.
---

# EA 5-Mistakes Audit — Self-Check Before Shipping Mavis Work

## What this skill does

You audit a Mavis-side work surface — a skill, a workflow, a recurring loop, a project setup — against the 5-mistakes framework from the LLM-training article, **plus 5 modern pitfalls the article omits**. The audit is a self-check, not a user-facing review. For each mistake, you answer:

- **Is this mistake present?** (yes / no / partially)
- **What's the evidence?** (a disk hit, not a recap)
- **What's the minimum fix?** (one sentence, no fixing in this audit)

The 5-mistakes framework is a **trigger** for thinking, not a canonical source. The 5 mistakes are correct as a teaching device; the 5 additions are what makes the framework current for 2025-2026 work.

## The 5 original mistakes (from the LLM article, mapped to EA work)

### Mistake 1: Obsessing over architecture / tool surface

**LLM analog:** Spending weeks on transformer variations, attention patterns, layer counts — when the architecture is already published and standardized.

**EA analog:** Spending time on Mavis's role definition, org-chart restructuring, or adding new MCP servers / skills — when the value is in the data corpus (memory, vault, gBrain) the agent reads.

**Self-check question:** Have I added any new tool, skill, or role definition in the last 30 days that wasn't already load-bearing? If yes, was the new addition justified by a clear gap, or by "this would be cool"?

**Evidence to look for:**
- Skill file created in the last 30 days
- MCP server added to config
- Role definition updated
- Org chart redrawn

**If present:** audit whether the addition is justified by a gap. If it's not load-bearing in any current workflow, it's tool-surface bloat. Per the `skill-infrastructure` topic: "no-wrappers fleet lock" — don't add wrappers, add primitives.

### Mistake 2: Treating data as commodity

**LLM analog:** "We have 250B web pages, that's enough" — when most of it is noise and the cleaning is the actual moat.

**EA analog:** Treating memory, vault, and gBrain as cheap infrastructure — when the quality of the agent's data corpus is the actual ceiling on output quality.

**Self-check question:** When did I last audit the memory corpus for quality (not just quantity)? When did I last deduplicate? When did I last verify the claims in memory against disk?

**Evidence to look for:**
- `~/.mavis/agents/mavis/memory/MEMORY.md` size > 15KB (hygiene ceiling)
- Topic files without YAML description
- Stale entries (claims that no longer match disk)
- Repeated entries (same fact in 3+ places)
- "Disk wins over recap" violations (memory claims that contradict disk)

**If present:** run `ea-data-quality-audit` for the full procedure. The minimum fix: identify the 3 worst stale entries, edit or remove them.

### Mistake 3: Skipping the scaling math

**LLM analog:** "Train a 70B model on 1T tokens" without asking whether the compute, data, and time actually add up to a useful model.

**EA analog:** "Write a new skill for X" without asking whether the human-time to design, build, test, and maintain the skill is justified by how often X comes up.

**Self-check question:** Has Andre asked me for the same thing 3+ times? Is the cost of the skill (design + build + test + maintain) less than the cost of doing it by hand 3 times?

**Evidence to look for:**
- Andre's repeated directives for the same outcome (search `01 Daily/`, kanban)
- Skills that exist but have never been triggered
- Skills that were triggered once and abandoned
- The "if I have to ask you twice, you failed" rule (Garry Tan / Andre's user memory)

**If present:** either the skill is over-engineered (simplify), the work is too rare to codify (revert to ad-hoc), or the work is rare but high-stakes (codify anyway, with a clear test surface). Use `ea-data-quality-audit` to find repeated manual patterns.

### Mistake 4: Stopping at SFT

**LLM analog:** Fine-tuning the model on prompt-response pairs and shipping — without RLHF, the model imitates but doesn't know what "good" means.

**EA analog:** Writing a skill, testing it on one example, and shipping — without a feedback loop, the skill never learns from real use.

**Self-check question:** Does this skill have a feedback mechanism? Does it update based on Andre's corrections, on kanban outcomes, on disease-detection reports, on user-rating signals?

**Evidence to look for:**
- Skills with no `--feedback` or `## Iteration` section
- Skills that run but never write back to memory
- Skills without a `## When NOT to run` section (a skill that doesn't know when to refuse is fragile)
- Missing `verifier_request` hooks for handoffs

**If present:** the minimum fix is to add a feedback section. The deeper fix is to add a verifier (different model / different agent) for the skill's outputs, paired with a kanban or memory write-back.

### Mistake 5: Trusting surface metrics after alignment

**LLM analog:** Perplexity is meaningful during pretraining, but after SFT/RLHF, perplexity goes up while the model gets better. Using perplexity as the only eval is a trap.

**EA analog:** Counting skills added, Mavis sessions completed, kanban tickets closed, files written — while the user-experience metrics (did Andre's blocker get unblocked? did the question get answered?) are flat or down.

**Self-check question:** What user-facing metric is this work actually moving? Is that metric improving? Have I asked Andre whether the work is landing?

**Evidence to look for:**
- Vanities: skill count, agent count, kanban throughput
- User-facing: time-to-answer, decision quality, "did this unblock Andre", and most importantly — Andre's direct feedback in `01 Daily/`
- "Looks good to me" without evidence (the surface-metric trap)
- `agent-disease-detector` outputs (Anosognosia, Disinhibition)

**If present:** the minimum fix is to name ONE user-facing metric per recurring work surface, and to ask Andre periodically whether the metric is moving.

## The 5 modern additions (2025-2026 pitfalls the article omits)

### Addition 6: Skipping the verifiable-rewards stage (RLVR miss)

**The 2025-2026 insight** (Karpathy's year-in-review): the de facto 4th stage of training is **RLVR** — train on math/code puzzles with auto-verifiable rewards, and the model spontaneously develops reasoning. The article's 5-stage pipeline is missing this stage.

**EA analog:** Tasks with programmatically checkable success (cron fired, kanban ticket moved, file committed, type check passed) are the analog of RLVR. If Mavis's work doesn't have auto-eval on these, the feedback loop is slow and lossy.

**Self-check question:** What percentage of my work has a programmatically checkable success criterion? For that percentage, is the check actually running?

**Evidence to look for:**
- `gepa-evaluator` skill usage (the fleet already has this)
- `agent-disease-detector` cron running
- Kanban fast-path check running
- Skills with `## Verification` sections that auto-execute
- Skills with verification sections that depend on human review only

**If present:** identify the top 3 Mavis workflows with checkable success, add a verifier, run it on the next 3 cycles.

### Addition 7: Using saturated benchmarks

**The 2025-2026 insight:** MMLU is saturated — frontier models hit 86-90%. The discriminating benchmarks are now MMLU-Pro, GPQA, SWE-bench Verified, ARC-AGI, Chatbot Arena Elo. Using only saturated benchmarks means the eval is no longer measuring the gap.

**EA analog:** Are the metrics Mavis reports on actually discriminating? Or is everything "PASS" because the bar was set in 2024 and the work is now well above it?

**Self-check question:** When did I last update the success criteria on a recurring work surface? Is the success bar still meaningful, or has it become table-stakes?

**Evidence to look for:**
- Success criteria last updated > 6 months ago
- All recent runs are PASS
- No FAIL in the last 30 days (could mean perfection; more likely means the bar is too low)
- "The loop just works" without a recent verification

**If present:** pick one work surface, raise the bar by 20%, see if the metric now discriminates. If everything still passes, the metric is wrong, not the work.

### Addition 8: Ignoring inference cost

**The 2025-2026 insight:** Open-ended agent loops burn tokens fast. The 90% of people without unlimited API budgets cannot run open loops safely. Cost is the load-bearing constraint, not intelligence.

**EA analog:** Does each recurring Mavis loop have a cost ceiling? Is the ceiling respected? When it's exceeded, is there a halt?

**Self-check question:** What's the worst-case token cost per run of each recurring loop? Is that ceiling written down? Is it actually enforced?

**Evidence to look for:**
- Loops without `## Cost ceiling` sections
- Loops that have run > 2x their expected cost in the last 30 days
- Token spend growth (look at `~/.mavis/agents/mavis/memory/`, `mavis session list`, or run logs)
- "Open loop" classification without explicit cost sign-off

**If present:** name the ceiling, enforce it, and convert open loops to closed loops where possible.

### Addition 9: No eval pipeline / no disease detection in production

**The 2025-2026 insight:** Agent systems need continuous eval in production, not just at training time. "Did the loop work" is the wrong question; "is the loop still working, today, on real inputs" is the right one.

**EA analog:** Does Mavis have cron-based disease detection (agent-disease-detector), health checks (kanban-health-check), or post-hoc audits? Or does work go unmonitored between Andre's complaints?

**Self-check question:** When did I last run `agent-disease-detector` or `kanban-health-check`? Are there any open alerts? Are the cron jobs still firing?

**Evidence to look for:**
- Stale cron jobs (last run > 30 days)
- Open disease alerts not actioned
- Unmonitored work surfaces (no verification, no health check)
- "It worked last time" without a current check

**If present:** restart the cron, action the alerts, add a health check to the surface.

### Addition 10: No observability

**The 2025-2026 insight:** "After the fact, can you tell whether the loop ran correctly" is the observability test. If you can't, the loop is running blind.

**EA analog:** After a Mavis loop runs, can you point to a log line, a disk artifact, a kanban ticket, a memory entry that proves the work was done correctly? Or do you have to take it on faith?

**Self-check question:** Pick the last recurring loop that ran. Show me three pieces of evidence it ran correctly. If you can't, the loop has an observability gap.

**Evidence to look for:**
- Logs that are written but never read
- Disk artifacts that are never audited
- Kanban tickets that are closed but not verified
- Memory entries that claim work was done but no disk hit

**If present:** the minimum fix is to add a write-back to disk (a log line, a kanban comment, a memory entry) on every loop iteration, with a verification read on the next iteration.

### Addition 11: Ignoring regulatory realities for high-stakes work surfaces

**The 2025-2026 insight:** Building LLM-backed workflows for medical, legal, financial, or other regulated domains without naming the regulator is malpractice in 2026. The "5 stages" article is silent on this — and the gap is what makes the framework unfit for any serious production system touching PHI, attorney-client communication, clinical decisions, or credit decisions. The 2024-2026 regulatory wave is the load-bearing constraint on real-world LLM deployment, not an edge case.

**EA analog:** Is this Mavis work surface shipping output that could touch a regulated decision (medical advice, legal guidance, credit decision, employment screening, biometric identification)? If yes, the regulatory layer is the first thing to design, not the last.

**Self-check question:** For this work surface — does it touch PHI, attorney-client privilege, credit decisions, biometric ID, or employment screening? If yes: which regulator? EU AI Act high-risk classification? FDA Predetermined Change Control Plan? HIPAA Security Rule? State bar UPL rule? GLBA Safeguards Rule? If the answer is "I don't know" — the work surface is not safe to ship.

**Evidence to look for:**
- Work surface description mentions: medical, clinical, patient, diagnosis, prescription, attorney, legal advice, client privilege, contract review, lending, credit, mortgage, employment, hiring, biometric, face recognition, ID verification
- No Data Protection Impact Assessment (DPIA) referenced
- No Business Associate Agreement (BAA) for PHI handling
- No risk classification against EU AI Act Annex III
- No "human-in-the-loop for high-risk decisions" clause in the loop's stop conditions
- No audit log retention policy named (HIPAA requires 6 years; FDA AI/ML guidance requires ongoing PCCP updates)
- Output language that asserts medical/legal certainty ("you have X condition", "you should sue", "you're approved") instead of deferring to a professional
- Cross-border data transfer without a transfer mechanism named (EU→US needs SCCs or DPF; UK needs IDTA)

**Regulatory frame (the four most common regimes, 2026):**

| Regime | Scope | Trigger | Penalty | What Mavis needs |
|---|---|---|---|---|
| **EU AI Act** (effective 2024-2026) | Any AI system deployed in or affecting the EU | High-risk per Annex III (medical, legal, credit, employment, biometric, critical infrastructure) | Up to **€15M or 3% global annual revenue** | Risk classification, conformity assessment, post-market monitoring, human oversight, technical documentation, data quality/governance |
| **FDA AI/ML guidance + PCCP** (2024-2025) | Software-as-Medical-Device (SaMD) with ML | Any LLM that informs clinical decisions (triage, diagnosis support, treatment recommendation) | Warning letter, recall, market withdrawal | Predetermined Change Control Plan (pre-spec what model can change without resubmission), locked + adaptive parts, ongoing performance monitoring |
| **HIPAA Security Rule** (US healthcare) | Any handling of PHI by or for a covered entity | LLM fine-tuned on PHI, processes PHI, or stores PHI in logs | Up to **$1.9M/year/incident tier** | Business Associate Agreement (BAA) with all vendors processing PHI, encryption at rest/in transit, audit logging, access controls, breach notification procedure |
| **State bar Unauthorized Practice of Law (UPL)** (US, per state) | AI systems providing legal guidance | Output resembles legal advice to a layperson on a specific matter | Attorney discipline for the deploying lawyer; no UPL remedy against the AI directly | Disclaimers, human-attorney review for any case-specific guidance, no jurisdiction-specific advice without a licensed attorney in the loop |

**EU AI Act high-risk categories (the full list that catches most "Build your own LLM" use cases):**
1. Biometric identification / categorization / emotion recognition
2. Critical infrastructure (water, gas, electricity, traffic)
3. Education and vocational training (admissions, assessment, proctoring)
4. Employment, worker management, access to self-employment (recruitment, decision-making, termination, task allocation)
5. Access to essential private and public services (credit scoring, insurance pricing, emergency dispatch, public benefit eligibility)
6. Law enforcement (risk assessment, lie detection, evidence reliability, profiling)
7. Migration, asylum, border control
8. Administration of justice and democratic processes (legal interpretation, fact-finding, influencing votes)

**If the work surface falls into any of these, the audit must include:**
- Risk classification written down (high-risk / limited-risk / minimal-risk per EU AI Act)
- Conformity assessment planned or completed
- Human oversight mechanism in the loop's stop conditions
- Data governance for training/eval data documented
- Transparency obligations met (users know they're interacting with AI, can request human review, can file complaints)
- For medical: PCCP submitted to FDA, locked-vs-adaptive model parts named
- For HIPAA: BAA chain complete, audit logging in place, encryption verified
- For legal: disclaimer language, human-attorney review, no jurisdiction-specific advice without licensed review

**Minimum fix when present:** name the regulator, name the trigger condition, name the compliance gap, and pause for Andre's call before shipping. This is not a "patch later" item. A regulated-domain work surface that ships without a regulator named is a liability, not a feature gap.

## The procedure

1. **Pick a work surface to audit.** One sentence: "I'm auditing [this skill / this loop / this workflow]."
2. **Walk the 5 + 5 dimensions.** For each, answer: present? evidence? minimum fix?
3. **Aggregate the findings.** Count the dimensions where the answer was "yes, this mistake is present." That count is the audit's severity.
4. **Prioritize the fixes.** Add the RLVR/saturated-benchmark/cost/eval/observability/regulatory fixes (additions 6-11) before the original 5 (mistakes 1-5) — they are higher leverage in 2026. For any work surface touching a regulated domain, the regulatory fix (addition 11) is the FIRST priority, not the last.
5. **Decide action.** If 3+ dimensions are present, the work surface needs a redesign, not a patch. If 1-2, fix inline. If 0, ship.
6. **Report.** "5-mistakes audit on [surface]: 3/10 dimensions present. Top fix: [RLVR / saturated-benchmark / cost ceiling]. Proceeding to fix / halting for Andre's call."

## Hard constraints

1. **Don't fix during audit.** The audit is read-only against the work. Fixes are a separate step.
2. **Disk wins over recap.** Every "is this present" answer must be a disk hit, not a memory-based claim.
3. **Cite primary sources for the modern additions.** Karpathy 2025 for RLVR, GEPA paper for verifiable rewards, the article's own text for the original 5. The article is a trigger, not a canonical source.
4. **Modern additions are 2025-2026 specific.** Don't apply "skipping RLVR" as a critique to anything pre-2025; the concept is new. Same for saturated benchmarks (MMLU is a 2024-2025 phenomenon).
5. **Mavis territory only.** This skill audits Mavis-side work. For peer audits (Hermes, OpenClaw), the cross-team-discipline rule applies: state findings, don't fix.

## Anchoring sources

- The 5 mistakes: @sairahul1 "How To Build Your Own LLM" (popularization, use as trigger)
- RLVR (Karpathy 2025 year-in-review) — https://karpathy.bearblog.dev/year-in-review-2025/
- GEPA — Agrawal et al., arXiv 2507.19457
- Self-Evolving Agents survey — Gao et al., arXiv 2507.21046
- Saturated benchmarks (MMLU-Pro) — Wang et al., arXiv 2406.01574
- Cost floor for "real" LLM training (2026) — jarvislabs.ai/blog/h100-price
- EU AI Act (regulatory framework, Annex III high-risk list) — https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
- FDA AI/ML SaMD guidance + Predetermined Change Control Plan — FDA 2024-2025 AI/ML-based SaMD action plan
- HIPAA Security Rule (45 CFR Part 160, 164) — covered-entity and BA obligations, 6-year audit retention
- State bar Unauthorized Practice of Law (UPL) rules — jurisdiction-specific, ABA Model Rule 5.5
- "No-wrappers fleet lock" — Mavis `skill-infrastructure` topic
- "Disk wins over recap" — Mavis MEMORY.md cross-cutting disciplines
- "If I have to ask you twice, you failed" — Garry Tan (Andre's user memory)
