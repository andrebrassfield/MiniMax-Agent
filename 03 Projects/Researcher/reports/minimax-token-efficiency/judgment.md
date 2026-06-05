# Step 2 — Direction Judgment

**Source query:** *"We got rate limited on our MiniMax token plan earlier and that caused about an hour of inactivity. Can we do some research and design a plan if its possible to be more efficient with our MiniMax token plan?"*

**Background already collected:** Token Plan tiers (Plus/Max/Ultra), 5h rolling + weekly windows, peak-hour dynamic throttle (weekdays 15:00–17:30 China time), M3 vs M2.7 rate limits (200 RPM / 10M TPM vs 500 RPM / 20M TPM), error codes (1002 / 1041 / 2045 / 2056), passive + explicit prompt caching (66.7% saving example), Hermes Agent's own efficiency tips, and broader LLM cost-reduction techniques (LLMLingua, context compression, structured output).

---

## Step 1: Understand the question

Decompose the keywords:

- **"rate limited"** — the trigger event. They hit some kind of throttle, got a 429-ish error, and their workload paused for ~1 hour.
- **"minimax token plan"** — the specific subscription product. Not PayGo, not API key with credits — the bundled quota plan. This matters because: (a) quota is credit-based and shared across text/image/speech/music/video; (b) it has *two* reset windows (5h rolling AND weekly) plus a peak-hour dynamic throttle; (c) credits don't carry over.
- **"an hour of inactivity"** — impact is concrete and measurable. This isn't a casual complaint; they have a workload that depends on the API.
- **"do some research"** — they want evidence-backed recommendations, not vibes.
- **"design a plan"** — deliverable is structured, actionable, sequenced. Not a single tip.
- **"if its possible to be more efficient"** — they hold the assumption that it *is* possible but are not certain. The "if" is a politeness hedge, not a real uncertainty.

**What the question is really getting at:** after a real outage-grade rate-limit event, *what concrete, evidence-rooted set of changes* can we adopt so that (a) we don't get rate-limited again at the same scale, and (b) we get more useful work per token/quota we already pay for?

**Easy-to-confuse concepts that the report must disambiguate:**

1. **"Rate limit" is plural.** The official catalog has at least 4 distinct mechanisms that all look like "rate limit" to a user:
   - **1002** — true API rate limit (RPM/TPM hard cap, per-key)
   - **2045** — *rate-growth* limit (sudden increases/decreases trigger it)
   - **2056** — *usage limit* (5h rolling or weekly credit exhaustion)
   - **1041** — *connection* limit
   - **Peak-hour dynamic throttle** — soft, may tighten under load, no public numeric threshold
   Each of these has a different remedy. A "plan" that treats them as one thing will fail.
2. **Token Plan vs API key limits.** The published RPM/TPM table (200 / 10M for M3) is the *API-key* limit. The Token Plan Plus tier "≈3–4 agents" is an *aggregate session-counter* hint that is enforced differently. Hitting one does not necessarily mean the other is the bottleneck.
3. **Passive vs explicit prompt caching.** M3 supports passive (automatic, prefix-matched, 512+ tokens). Explicit `cache_control` (Anthropic-style) is **NOT** supported on M3 — only M2.x. The Token Plan Plus cache-read discount is also reportedly not visible in the usage bar (open issue #47).
4. **5h rolling vs weekly.** Both windows are active. The weekly is the dominant cap for sustained heavy use; the 5h is the "sprint" cap. The user can burn the 5h allowance and *still* be capped by the weekly.
5. **"Efficiency" is multi-dimensional.** Token-efficiency (fewer tokens per task), capacity-efficiency (more tasks per quota), latency-efficiency (faster, not necessarily fewer tokens), and cost-efficiency (dollars, not credits). They mostly care about capacity (avoid the next 1-hour outage), with cost as a secondary concern.

---

## Step 2: Set the boundaries

**Clearly in scope:**

- Diagnosis framework: how to look at logs, error responses, and the usage bar to identify *which* of the 4 rate-limit mechanisms actually fired.
- Quantified opportunity table: which techniques give the biggest wins (passive prompt caching, subagent delegation, model selection, conversation compression, batching, peak-hour scheduling).
- The Token Plan quota mechanics — 5h rolling, weekly, peak-hour, rate-growth, RPM, TPM — and how to live within each.
- The M3 vs M2.x tradeoff for Token Plan: M3's lower RPM (200 vs 500) and TPM (10M vs 20M) is a real constraint; M3's caching behavior on Token Plan Plus is partially opaque (issue #47).
- Hermes Agent native efficiency features (`/compress`, `delegate_task`, `execute_code`, `/model`, `/usage`, `/insights`, memory size caps) — directly applicable because the user appears to be running through Hermes-style orchestration.
- A tiered action plan: **diagnose** (immediate, this week) → **protect** (short-term, this sprint) → **optimize** (medium-term, this quarter).
- Monitoring/alerting setup so the next incident is detected in minutes, not discovered after an hour.
- Contingency: when to add credits, when to upgrade tier, when to switch a workload to PayGo.

**Tangential / out of scope:**

- Building a custom rate-limit dashboard from scratch (overkill; built-in `/usage` + `/insights` cover this).
- Switching vendors entirely (e.g., to Xiaomi MiMo or Anthropic Pro) — not a Token-Plan-efficiency move.
- Deep MSA architecture explainer — mention briefly that M3 is sparser, don't deep-dive.
- M3 open-source licensing debate — unrelated to efficiency.
- Speculative M4 roadmap — irrelevant to a current-state plan.
- Detailed financial modeling of PayGo vs Token Plan — only worth a paragraph as a fallback.

**Hard "don't go there" zones:**

- Recommending an open-source LLM swap without a clear capacity use case.
- Building new Hermes skills from scratch in this plan (that's a *follow-up* task, not part of the plan itself).
- Speculative claims about the 2056/1002 mapping without flagging it as "to be verified."

---

## Step 3: Read the user

**Signals from the query:**

- *"We got rate limited"* — first-person plural, team/company context.
- *"earlier"* — recent, time-pressured. They want this turned around.
- *"that caused about an hour of inactivity"* — they have observability. They noticed. This is not "the API felt slow"; this is "we lost 1 hour of production time."
- *"Can we do some research and design a plan"* — they value both rigor (research) and structure (plan). This is not a "give me a one-liner" request.
- *"if its possible to be more efficient"* — the "if" is courtesy. They believe it is possible; they're asking for evidence + method.
- Use of *minimax* (lowercase, with a typo) and *minimax* (with another typo) — they are technical but not formal. They type fast.
- No mention of "model," "M2.7," "M3" — they think in terms of the *plan* abstraction, not the model layer. They expect us to translate.
- They use "token plan" (lowercase) — they probably pay for one but don't think in tier-name ("Plus" / "Max" / "Ultra") terms.

**Inferred profile:**

- **Role:** developer, tech lead, or platform owner running an automation/agent fleet on top of the MiniMax API. Almost certainly using Hermes Agent or a similar multi-agent orchestrator (the background's heavy Hermes section matches the use case).
- **Expertise:** high technical fluency (knows what rate limiting is, knows the product name, has monitoring), but probably not deeply familiar with the M3/M2.7 split, MSA architecture, or the specific error code taxonomy.
- **Likely tier:** Plus or Max. If they were on Ultra, "an hour of inactivity" would be unusual unless they were doing something very heavy. The Plus tier's "≈3–4 agents" hint suggests they are at or near the agent count they're running.
- **Workload pattern:** continuous / background / batched, with peak bursts. The "1 hour of inactivity" implies something that was meant to be running but got cut off — not interactive coding.
- **Reason for asking:** prevent recurrence. The cost of one outage was high enough that they're now budgeting cycles to fix it properly. This is a *real* problem with a *real* business cost, not an academic exercise.

**What this implies for tone and structure:**

- They will not be impressed by hedging or generic "best practices." They want a *specific* plan that *names* the Token Plan and the M3 model.
- They will be impressed by: a diagnosis checklist, a prioritized action list, quantified savings where possible, and explicit "if X, do Y" branching.
- They will *not* be impressed by: vendor cheerleading, broad "move to PayGo" suggestions, or hand-wavy "optimize your prompts" advice.
- A research-report register, not a casual chat register. But not academic — they want pragmatic signal.

---

## Step 4: Make the call

**What is this question really asking, in one sentence?**

> *After a 1-hour rate-limit-induced outage on our MiniMax Token Plan, what concrete, evidence-rooted plan — diagnostic, protective, and optimizing — will prevent recurrence and let us extract more useful work per quota we already pay for?*

**Which analytic capabilities will matter most, in priority order:**

1. **Actionable advice (PRIMARY).** This is the spine of the deliverable. Every section must end in a concrete, do-this action, ideally with an effort/impact tag.
2. **Framework building (PRIMARY).** A diagnosis taxonomy (4+ rate-limit mechanisms), a tiered action plan (immediate / short-term / medium-term), and a quantified opportunity matrix. The reader should be able to *use* the framework, not just read the report.
3. **Causal reasoning (HIGH).** For each rate-limit mechanism, explain *what causes it* and *what specifically triggers it in the Token Plan context*. This is what makes the plan defensible, not just a list of tips.
4. **Critical annotation (HIGH).** Flag the gaps the background left open (M3 passive-cache on Token Plan, exact weekly cap, root cause of the user's incident) so the user knows what to verify in their own logs.
5. **Non-obvious insight (MEDIUM).** Rate-growth throttle (2045) is the silent killer — sudden bursts trigger it, so smoothing traffic is high-leverage. Peak-hour dynamic throttle is a calendar problem, not a code problem. Subagent delegation with Hermes is a way to *avoid putting context into the main session* (which is what makes caching effective).
6. **Scenario branching (LOWER).** A small branch on tier (Plus vs Max vs Ultra) and a small branch on whether they're hitting the 5h cap or the weekly cap — but don't over-branch.

**What this is NOT:**

- Not a comprehensive LLM cost-optimization survey.
- Not a Token Plan upgrade pitch.
- Not a vendor comparison.
- Not a deep-dive into M3's MSA architecture.

---

## Step 5: Suggested writing spec

- **Style:** **research-report with a deep-analysis edge.** Structured sections, named subsections, a few tables. Not academic; not chatty. Should read like a senior engineer's internal design doc.
- **Length:** **substantial — target ~3,000–4,000 words.** This is a "design a plan" deliverable, not a one-pager. But resist filler; every paragraph should earn its place.
- **Vocabulary:** **jargon OK.** Use error codes (1002/2045/2056), RPM/TPM, "passive caching," "prefix matching," "subagent delegation," "connection pooling." Define only the genuinely non-obvious terms (e.g., explain what "rate-growth limit" is the first time).
- **Depth:** **skip the basics, dive into specifics.** No "an LLM is a model that…" explanation. Start at the Token Plan mechanics. The reader knows what a token is.
- **Tone:** **professional and direct.** "Do X" not "you might consider X." Use the imperative where appropriate. Avoid corporate hedging.
- **Structure:** **mixed.** Recommended skeleton (writing stage can adjust):
  1. **TL;DR** — 5-bullet executive summary at the top so a busy reader can act on it without reading the rest.
  2. **Diagnosis: what actually happened?** — a checklist the user can run against their logs to identify which of the 4 rate-limit mechanisms fired; one branch per mechanism.
  3. **The Token Plan mechanics you need to know** — concise reference: 5h rolling, weekly, peak-hour, rate-growth, RPM, TPM, per-tier envelope. **One table** that consolidates it.
  4. **Quantified opportunity matrix** — table of techniques (passive caching, explicit caching on M2.7, subagent delegation, model selection, conversation compression, batching, peak-hour scheduling, rate-growth smoothing, etc.) with: lever, effort, expected impact, what to verify in the user's own data.
  5. **The plan** — three horizons:
     - **Immediate (this week):** diagnosis, rate-growth smoothing, peak-hour awareness, /usage + /insights baseline.
     - **Short-term (this sprint):** prompt-caching audit and prefix stabilization, subagent delegation for parallel work, model selection (M2.7 for cache-friendly or highspeed for non-cache, M3 only when context >512k or quality demand warrants), conversation compression, batching.
     - **Medium-term (this quarter):** monitoring/alerting before-the-fact, contingency design (when to add credits vs upgrade tier vs migrate workload to PayGo), skill-creation pattern (per Hermes: if 5+ steps and repeated, make it a skill).
  6. **Monitoring & alerting** — what to instrument so the next incident is detected in minutes, not after an hour. `/usage` is per-session; `/insights` is 30-day. Console usage bar is source of truth. The `remains` endpoint can be polled.
  7. **Known unknowns** — explicit list: exact weekly numeric cap, M3 passive-cache visibility on Token Plan, peak-hour throttle thresholds, which mechanism actually fired for the user's incident. **Tell the user how to verify each in their own logs.**
  8. **Appendix:** quick-reference tables (error codes, model rate limits, tier envelope, caching behavior per model).

- **What to avoid in writing:**
  - Don't recommend switching vendors. Don't recommend open-source self-hosting as a default.
  - Don't oversell any single technique. Passive caching is a high-leverage default, but not magic.
  - Don't over-quantify. Where the background has hard numbers (66.7% saving on the M3 caching example, 200/10M for M3, 500/20M for M2.x), use them. Where it doesn't, say so.
  - Don't conflate "rate limit" categories. Each of 1002/2045/2056/1041 is a separate diagnosis path.

---

## Final Call

**The question, in one sentence:** After a 1-hour rate-limit outage on the MiniMax Token Plan, design a concrete, research-backed plan to identify which rate-limit mechanism fired, prevent recurrence, and extract more useful work from the same quota.

**Primary analytic capabilities:** actionable advice + framework building, supported by causal reasoning and critical annotation. Non-obvious insight on rate-growth smoothing, peak-hour awareness, and Hermes subagent delegation. Mild scenario branching on which mechanism fired and which tier the user is on.

**Writing spec, in one line:** Research-report style, ~3,000–4,000 words, jargon-OK, skip-the-basics, professional-direct tone, sectioned with a TL;DR at the top, a diagnosis checklist, a quantified opportunity table, a three-horizon action plan, a monitoring section, and an explicit known-unknowns section. No vendor switching, no architecture deep-dive, no corporate hedging.
