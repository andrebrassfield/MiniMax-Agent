# Step 3 — Deep Analysis: MiniMax Token Plan Efficiency After a 1-Hour Rate-Limit Outage

**Source query:** *"We got rate limited on our MiniMax token plan earlier and that caused about an hour of inactivity. Can we do some research and design a plan if its possible to be more efficient with our MiniMax token plan?"*

**Direction already set (from `judgment.md`):** Design a concrete, research-backed plan to (a) identify which rate-limit mechanism fired, (b) prevent recurrence, and (c) extract more useful work from the same quota. Deliverable is a three-horizon plan (immediate / short-term / medium-term), research-report style, ~3,000–4,000 words, jargon-OK, no vendor switching, no architecture deep-dive, professional-direct tone.

This analysis decomposes the question into the depth needed for the writing stage. It does **not** answer the question. It maps what to research, what to disambiguate, what is in/out of scope, what capabilities the answer must lean on, what facts to verify, who the reader is, and how the next stage should search and write.

---

## 1. Deep sub-topic breakdown

The question is a single user-facing problem ("we lost an hour to rate limiting"), but it decomposes into seven distinct sub-topics that the answer must address. Each has its own research targets, keyword set, importance, and connection to the others.

### 1.1 Diagnosis taxonomy — "which of the 4+ rate-limit mechanisms actually fired?"

**What needs researching:** The exact mapping between user-observable symptoms (HTTP 429, error code in body, console usage bar behavior, time-of-day, request pattern) and the four or more official MiniMax error codes — `1002` (true rate limit / RPM·TPM), `2045` (rate-growth), `2056` (usage limit / 5h rolling or weekly), `1041` (connection limit) — and the unnamed peak-hour dynamic throttle. The official error-code page is short; the *symptom-to-cause* mapping is not published and must be inferred from third-party guides and community reports. We need a checklist a user can run against their own logs (request timestamps, response codes, usage bar state at incident time) to land on a single root cause.

**Search keywords:**
- English: "MiniMax error code 1002 2045 2056", "MiniMax 429 rate limit diagnosis", "MiniMax token plan peak hour throttle", "MiniMax API rate growth limit 2045", "MiniMax usage limit 2056 weekly", "MiniMax 1002 vs 2045 vs 2056"
- Chinese: "MiniMax 1002 错误码", "MiniMax 限流 原因", "MiniMax 套餐 动态限流 15:00", "MiniMax 限速 增长 2045", "MiniMax 周限额 用尽", "MiniMax 套餐 限流 类型"

**Why it matters:** A plan that treats "rate limit" as one thing is wrong. Each mechanism has a different remedy. Misdiagnosing `2056` (credit exhaustion) as `1002` (RPM cap) leads the user to add rate-limiting code when they actually need to upgrade tier, batch, or schedule differently. Misdiagnosing `2045` (rate-growth) as `1002` leads the user to add backoff when they actually need to smooth the traffic shape.

**How it connects:** This is the gate. Every other sub-topic (1.2 mechanics, 1.3 efficiency techniques, 1.4 plan) starts from a diagnosis. The writing stage should put this first after the TL;DR.

### 1.2 Token Plan mechanics — the envelope that defines "efficiency"

**What needs researching:** The full set of constraints that govern how much work the user can extract from a Token Plan subscription. From the background: 5-hour rolling window, weekly window, peak-hour dynamic throttle (15:00–17:30 China time, workdays), per-tier agent count hint (Plus ≈3–4, Max ≈4–5, Ultra ≈6–7), API-key-level RPM/TPM (M3 200/10M vs M2.x 500/20M), shared credit pool across modalities, no credit carryover, M3 vs M2.x cache behavior. The to-be-verified items: exact numeric weekly cap, exact per-tier TPM/RPM under Token Plan (vs API key), peak-hour numeric threshold, M3 passive-cache behavior on Token Plan Plus.

**Search keywords:**
- English: "MiniMax token plan weekly quota", "MiniMax token plan 5 hour rolling", "MiniMax token plan peak hour 15:00 17:30", "MiniMax M3 RPM TPM token plan", "MiniMax token plan remains endpoint", "MiniMax plus max ultra comparison"
- Chinese: "MiniMax 套餐 周限额", "MiniMax 套餐 5小时 用量", "MiniMax 套餐 高峰 限流", "MiniMax M3 TPM 套餐", "MiniMax 套餐 remains 接口", "MiniMax 套餐 Plus Max Ultra 区别"

**Why it matters:** "Efficiency" without a constraint set is meaningless. The answer must define the envelope (5h × weekly × peak × RPM × TPM × credit pool) and then optimize inside it. The envelope is also where the user's tier dictates which tactics are even available (e.g., a Plus user cannot rely on the Ultra-tier per-call priority queue).

**How it connects:** Drives the capacity budget. Determines which of the techniques in 1.3 are worth pursuing. Constrains the contingency section in 1.4 (when to add credits, when to upgrade, when to switch to PayGo).

### 1.3 Efficiency technique stack — the levers the user can pull

**What needs researching:** A concrete, prioritized list of techniques, each with (a) what it does, (b) expected impact, (c) effort, (d) which MiniMax feature supports it, (e) what to verify in the user's own data. From the background, the candidate set is:

1. **Passive prompt caching** on M3 / M2.7 / M2.5 / M2.1 — prefix-stable system prompt + tool list, 512-token minimum, ~66.7% saving in the official example at 50k/45k hit/1k out
2. **Explicit `cache_control` caching** — Anthropic-style, M2.x only (M3 not supported), 5-minute lifetime
3. **Model selection** — M2.7-highspeed vs M2.7 vs M3 based on workload shape (cache-friendly → M2.7; quality/long-context → M3; high-volume boilerplate → M2.7-highspeed)
4. **Subagent delegation** — Hermes `delegate_task`, parallel sub-agents with their own context, only summaries return
5. **Conversation compression** — `/compress` in Hermes; LLMLingua-2 in academic; Activation Beacon for very long context
6. **Batching with `execute_code`** — one script replacing N terminal calls
7. **Peak-hour scheduling** — shift heavy work outside 15:00–17:30 China time weekdays
8. **Rate-growth smoothing** — exponential ramp-up instead of cold-start bursts; queue + jitter
9. **Structured output** — JSON mode / function-calling to suppress prose tokens
10. **Tool-list minimization** — fewer tools at the top of the prompt = larger stable prefix
11. **Memory discipline** — MEMORY.md 2,200-char cap, USER.md 1,375-char cap, session-start vs mid-session writes

**Search keywords:**
- English: "MiniMax prompt caching 66.7% saving", "MiniMax cache_control M2.7 5 minutes", "LLMLingua 20x compression", "Hermes delegate_task parallel", "Hermes /compress token", "MiniMax structured output JSON mode", "M3 MSA prefill decode speedup"
- Chinese: "MiniMax 缓存 命中率", "MiniMax 提示词 缓存", "LLMLingua 压缩", "MiniMax M3 速度", "MiniMax 结构化输出", "MiniMax 高速版 M2.7"

**Why it matters:** This is the heart of "extract more useful work from the same quota." Each technique has different effort/impact tradeoffs, and the answer must sequence them (low-effort first, high-leverage second) and show the user which to verify in their own data.

**How it connects:** Pulls from 1.1 (diagnosis tells you which lever matters most — e.g., 2045 → rate-growth smoothing; 2056 → caching + delegation; 1002 → model selection + batching) and 1.2 (envelope tells you the headroom for each lever). The M3-vs-M2.x split only matters here, not in 1.1 or 1.2.

### 1.4 Three-horizon plan — diagnose / protect / optimize

**What needs researching:** Concrete actions per horizon, with effort, owner (who in the user's team does it), and verification step. The horizons the judgment committed to: *immediate* (this week — diagnosis, baseline, smoothing, peak-hour awareness), *short-term* (this sprint — caching audit, subagent delegation, model selection, batching, compression), *medium-term* (this quarter — monitoring/alerting, contingency design, skill-creation pattern).

**Search keywords:**
- English: "exponential backoff 429 best practice", "rate growth limit mitigation", "MiniMax alert monitoring 429", "MiniMax /insights 30 day token usage", "MiniMax /usage per session", "MiniMax remains endpoint polling"
- Chinese: "MiniMax 监控 限流", "MiniMax 用量 查询", "指数退避 限流", "MiniMax 套餐 用量 看板"

**Why it matters:** A research report without a sequenced plan is just trivia. The horizons give the user an execution order: do the cheap diagnostic stuff this week, the structural work this sprint, the operational scaffolding this quarter. Each horizon's actions should be independently testable.

**How it connects:** Synthesizes 1.1, 1.2, 1.3 into a single executable sequence. Feeds 1.5 (monitoring) and 1.6 (contingency).

### 1.5 Monitoring & alerting — "the next incident detected in minutes, not hours"

**What needs researching:** What MiniMax-native observability exists (`/usage` per-session, `/insights` 30-day, console usage bar, `remains` endpoint polling), and what to instrument in the user's own system (request logging with error code, request-rate smoothing, peak-hour markers, cache-hit-rate logging). Target: detect a rate-limit condition *before* it stops work.

**Search keywords:**
- English: "MiniMax remains endpoint", "MiniMax usage bar source of truth", "MiniMax /usage per session", "MiniMax /insights 30 day", "LLM rate limit alerting prometheus", "request log 429 MiniMax"
- Chinese: "MiniMax 套餐 实时 余额", "MiniMax 用量 查询 接口", "MiniMax 监控 API"

**Why it matters:** A 1-hour outage should have been a 1-minute alert. Without observability, the user is reactive; with it, they are proactive. This section is also where the "if it's possible to be more efficient" hedge in the original query gets its strongest yes.

**How it connects:** Operationalizes 1.4. Without monitoring, the immediate/short-term actions are blind.

### 1.6 Contingency design — when to add credits, upgrade tier, or migrate to PayGo

**What needs researching:** The break-points where the right move is *spend money* (or move workload) rather than *spend engineering time*. From the background: Credits packages ($5 / $25 / $100 with 365-day validity, used after Token Plan quota exhausts), tier upgrade (Plus→Max, Max→Ultra, immediate effect, price-difference only charged), PayGo pricing for M3 ($0.30/$1.20 per M tokens standard, $1.20/$4.80 above 512k, M2.7 $0.30/$1.20, M2.7-highspeed $0.60/$2.40, M2.x legacy cache read $0.03/M vs M3/M2.7 $0.06/M), Priority tier (1.5× standard for stable latency).

**Search keywords:**
- English: "MiniMax credits package 365 days", "MiniMax upgrade tier mid-cycle", "MiniMax pay-as-you-go M3 0.30 1.20", "MiniMax priority service_tier", "MiniMax credits vs subscription"
- Chinese: "MiniMax 加油包", "MiniMax 套餐 升级", "MiniMax 按量付费", "MiniMax 优先级 service_tier"

**Why it matters:** Not every efficiency problem is a code problem. If the user is genuinely at the capacity ceiling, the right answer is "buy more capacity" — and the plan must say so. Conversely, the user should know when buying capacity is *not* the right answer (e.g., 2045 hits from bursts — buying more capacity won't help, smoothing will).

**How it connects:** Closes the loop with 1.1 (diagnosis decides which branch). The contingency section is the "if X, do Y" branching the judgment flagged.

### 1.7 Known unknowns — what the user must verify in their own logs

**What needs researching:** The list of facts the background flagged as "to be verified" — exact weekly credit cap, exact M3 passive-cache hit rate on Token Plan Plus, peak-hour numeric threshold, which mechanism actually fired for the user's incident, M3 thinking tokens interaction with caching/TPM, M3 TPM/RPM under Token Plan (vs API key). Each of these is a verification step the user can do locally with their own data.

**Search keywords:** N/A — these are user-side verification steps, not search targets. But for the report they should be presented as a checklist with concrete commands/queries the user can run.

**Why it matters:** A plan that pretends all numbers are known is fragile. The user is more likely to trust a plan that explicitly says "verify this in your data" than one that asserts numbers that may be wrong.

**How it connects:** Final section. Where the writing stage tells the user "here's how to close the gaps the research left open."

---

## 2. Precise concept disambiguation

The question is riddled with terms that *look* common-knowledge but carry MiniMax-specific or LLM-industry-specific meaning. Misreading any of these corrupts the plan.

### 2.1 "Rate limit" (MiniMax-specific)

**Precise meaning:** A user-observable condition in which the API returns an HTTP 429 / `RateLimitError` *or* a MiniMax-specific error code. In MiniMax's official taxonomy, "rate limit" maps to **at least four distinct official codes** plus a fifth unnamed mechanism. They are not interchangeable:

- **`1002` — true rate limit.** API-key-level hard cap. Per-minute requests (RPM) or per-minute tokens (TPM) exceeded. M3 200 RPM / 10M TPM; M2.x 500 RPM / 20M TPM. *Remedy:* add backoff, batch, parallelize across keys.
- **`2045` — rate-growth limit.** Triggered by *sudden* increases or decreases in request rate, not absolute rate. The official solution is "Please avoid sudden increases and decreases in requests." *Remedy:* smooth traffic (queue + jitter, exponential warm-up).
- **`2056` — usage limit.** The 5-hour rolling window or weekly window is exhausted. Quota, not rate. *Remedy:* wait for the next 5-hour window, upgrade tier, add credits, or move workload to PayGo.
- **`1041` — connection limit.** Long-lived socket count exceeded. The official solution is "contact us." *Remedy:* audit connection pooling, switch to short-lived requests.
- **Peak-hour dynamic throttle** — Unnamed in the error-code table, but the FAQ says limits "may tighten during peak traffic" and a press release quantifies the peak window (weekdays 15:00–17:30 China time). *Remedy:* schedule heavy work outside the window.

**Common misconception:** "A 429 is a 429." In MiniMax, a single 429-style error response can encode *five different conditions*, and the user's remediation depends on which. Reading the body and looking for the specific code is mandatory.

### 2.2 "Token Plan" vs API key

**Precise meaning:** A Token Plan is a *subscription product* with a credit-based shared quota across modalities (text/image/speech/music/video). An API key is an *access credential* with a *different* rate-limit table. The published RPM/TPM (M3 200/10M, M2.x 500/20M) is the API-key-level table. The Token Plan Plus "≈3–4 agents" hint is an aggregate session-counter hint, not a public numeric limit.

**Common misconception:** "The Token Plan and the API key have the same limits." They don't. The Token Plan adds the 5h/weekly/peak-hour envelope *on top of* the API-key rate limits. Hitting the API-key limit stops you even if you have Token Plan credits left. Hitting the Token Plan weekly stops you even if your API-key limits are fine. The two systems stack.

### 2.3 "Prompt caching" — passive vs explicit

**Precise meaning:** Two different mechanisms:
- **Passive (automatic) caching** — applies to M3, M2.7, M2.5, M2.1. Minimum 512 input tokens. Prefix-matching order: "tool list → system prompts → user messages." Cached tokens are billed at a discounted rate (e.g., M3 PayGo: $0.06/M cache read vs $0.30/M input). Lifetime is "automatically adjusted based on system load" — not user-controllable.
- **Explicit (Anthropic-API-compatible) caching** — set via `cache_control`. First-time write costs extra; hits are discounted. Lifetime is 5 minutes, refreshed on hit. Available on M2.7, M2.5, M2.1, M2 — **NOT M3**.

**Common misconception:** "All MiniMax caching is the same as Anthropic's." It is not. M3 only supports the passive kind. The explicit `cache_control` parameter is silently ignored on M3, and the user will think they have caching when they don't.

### 2.4 "5-hour rolling" vs "weekly" window

**Precise meaning:** Two *active* windows, not a replacement. The 5-hour is a rolling "sprint" cap. The weekly is a longer cap (reported as "5h × 10" = roughly 50h of 5h-equivalent in some press, but the exact number is not in the official FAQ). The user can burn the 5h allowance and *still* be capped by the weekly.

**Common misconception:** "If I don't hit the 5h cap, I'm fine." No — the weekly is independent. A user who paces themselves evenly within 5h windows can still hit the weekly by sustained use.

### 2.5 "Efficiency" (multi-dimensional)

**Precise meaning:** Four distinct meanings, often conflated:
- **Token-efficiency** — fewer input tokens per task (e.g., LLMLingua, structured output).
- **Capacity-efficiency** — more tasks per quota (e.g., caching, subagent delegation).
- **Latency-efficiency** — faster responses, not necessarily fewer tokens (e.g., M2.7-highspeed, M3 sparse attention).
- **Cost-efficiency** — dollars per task (PayGo math).

**Common misconception:** "Optimize for cost." The user's actual concern (1 hour of inactivity) is *capacity*, not cost. Optimizing token count without addressing capacity can *worsen* the outage. The plan must lead with capacity and treat cost as secondary.

### 2.6 "Subagent delegation" (Hermes-specific)

**Precise meaning:** The `delegate_task` tool in Hermes Agent runs subagents *in parallel* in their *own context windows*. Only the *summary* of each subagent's work returns to the main session's context. This is different from "calling another model." It's a way to *avoid putting intermediate tokens into the main session*, which both (a) keeps the main context small enough for cache hits, and (b) lets work run in parallel rather than serially.

**Common misconception:** "Subagents save tokens because they do less work." They don't do less work — they do *parallel* work that the main session would otherwise serialize, and only the summaries reach the main cache.

### 2.7 "M3" vs "M2.7" vs "M2.7-highspeed" (model-tier)

**Precise meaning:**
- **M3** — 1M context, MSA sparse attention, lower RPM (200) and TPM (10M) by design (sparser attention lets the same hardware handle longer context, so the per-minute cap is reduced to fit M3's bigger loads), SWE-Bench Pro ~59%, only supports passive caching.
- **M2.7** — 200k context, full attention, 500 RPM / 20M TPM, supports both passive and explicit caching, standard PayGo $0.30/$1.20.
- **M2.7-highspeed** — same context as M2.7, optimized for latency, PayGo $0.60/$2.40 (2× standard), still 500 RPM / 20M TPM.

**Common misconception:** "M3 is always better because it's newer." For high-volume boilerplate, M2.7-highspeed is the right call. For cache-friendly workloads, M2.7 is the right call. M3 wins on long context and quality, but its lower RPM is a real ceiling for high-throughput workloads.

### 2.8 "Quota" vs "Rate" vs "Priority"

**Precise meaning:** Three different axes:
- **Quota** — total credit consumption (5h, weekly).
- **Rate** — per-minute request/token caps (RPM, TPM).
- **Priority** — service-tier ordering when capacity is tight (PayGo `service_tier=priority` parameter = 1.5× price).

**Common misconception:** "Higher tier = higher rate limit." The Token Plan Ultra tier mostly gives more *quota*, not higher RPM/TPM. The API-key RPM/TPM table is the same across subscriptions.

---

## 3. Rough scope

### 3.1 In scope (must be covered, with explicit depth per dimension)

- **Diagnosis framework** — A checklist the user can run against their own logs to identify *which* of the 4–5 rate-limit mechanisms fired. One branch per mechanism. Concrete, runnable, with the log fields and timestamps to look at. *Why in scope:* The plan is wrong without a correct diagnosis; the user can't even tell which lever to pull.
- **Token Plan mechanics reference** — 5h rolling, weekly, peak-hour, rate-growth, RPM, TPM, per-tier envelope, shared credit pool, no carryover. *Why in scope:* Defines the optimization envelope. Without it, "efficiency" is undefined.
- **M3 vs M2.x tradeoff** — Specifically: M3's lower RPM (200 vs 500) and TPM (10M vs 20M) is a real constraint; M3's caching on Token Plan Plus is partially opaque (issue #47). *Why in scope:* A user running M3 vs M2.7 follows different optimization paths.
- **Quantified opportunity matrix** — A table of techniques (passive caching, explicit caching, subagent delegation, model selection, compression, batching, peak-hour scheduling, rate-growth smoothing) with: lever, effort, expected impact, what to verify. *Why in scope:* A research report without a quantified table is just a tip list.
- **Hermes Agent native features** — `/compress`, `delegate_task`, `execute_code`, `/model`, `/usage`, `/insights`, memory size caps. *Why in scope:* The user's profile strongly suggests Hermes-style orchestration; these are directly applicable levers.
- **Three-horizon action plan** — Immediate (this week: diagnosis, smoothing, peak-hour awareness, baseline), short-term (this sprint: caching audit, subagent delegation, model selection, batching, compression), medium-term (this quarter: monitoring/alerting, contingency, skill-creation). *Why in scope:* The user said "design a plan," and a plan is sequenced, not flat.
- **Monitoring & alerting setup** — What to instrument (request logging, error-code logging, usage-bar polling, `remains` endpoint, peak-hour markers) so the next incident is detected in minutes. *Why in scope:* The 1-hour outage is the problem; observability is the only way to prevent recurrence.
- **Contingency design** — Decision tree: when to add credits ($5/$25/$100 packages, 365-day validity), when to upgrade tier (Plus→Max→Ultra, immediate effect, price-difference only), when to move workload to PayGo. *Why in scope:* Not every problem is a code problem; the plan must say when spending money is the right move.
- **Known unknowns section** — Explicit list of what the user must verify in their own data: exact weekly cap, M3 passive-cache visibility on Token Plan, peak-hour threshold, which mechanism fired for the user's incident. *Why in scope:* A plan that asserts unknown numbers is fragile.

### 3.2 Out of scope (explicit "do not cover")

- **Switching vendors** — Xiaomi MiMo, Anthropic Pro, OpenAI Pro, self-hosted. The user asked about MiniMax Token Plan efficiency, not vendor comparison. *Why out:* Direct violation of "don't re-litigate scope." If a vendor switch comes up at all, it should be a one-line note in the contingency section, not a section.
- **Building a custom rate-limit dashboard from scratch** — Overkill. MiniMax's `/usage`, `/insights`, console usage bar, and `remains` endpoint cover this. *Why out:* The user is asking for efficiency, not new infrastructure.
- **Deep M3 MSA architecture explainer** — Mention briefly that M3 is sparser (and that's why the RPM is lower), don't deep-dive. *Why out:* Architecture depth doesn't help the user avoid the next outage.
- **Open-source vs closed-source M3 debate** — Unrelated to efficiency. *Why out:* Not in the user's question.
- **Speculative M4 roadmap** — Irrelevant to a current-state plan. *Why out:* Time-discounted information with no actionable leverage.
- **Detailed financial modeling of PayGo vs Token Plan** — One paragraph as fallback, not a section. *Why out:* The user's question is about preventing outages, not optimizing unit economics.
- **Building new Hermes skills from scratch in this plan** — That's a *follow-up* task. The plan can mention the skill-creation pattern; it should not draft skills. *Why out:* Scope creep; the user said "design a plan," not "build it."

### 3.3 Borderline areas (decide deliberately)

- **Anthropic / OpenAI / Google cache patterns as benchmarks** — Borderline. The user is on MiniMax, not on these vendors, but the *patterns* (prefix stability, system prompt design, tool ordering) are portable. *Decision rule:* Mention as a one-sentence comparative anchor when explaining a MiniMax-specific behavior, but don't run a vendor comparison section. The user is paying for MiniMax.
- **Academic prompt-compression techniques (LLMLingua, Activation Beacon)** — Borderline. They are real and documented (background section 2.12) but are research-grade, not production-grade. *Decision rule:* Mention in the medium-term/optimization horizon with a "consider, but expect engineering overhead" caveat. Do not recommend as a quick win.
- **MCP / dispatcher / kanban / agent-fleet architecture** — Borderline. The user is likely running a multi-agent system, but the *plan* is about Token Plan efficiency, not fleet topology. *Decision rule:* Mention Hermes Agent features where they directly apply (e.g., `delegate_task` is a subagent delegation lever). Do not redesign the fleet.
- **The "Xiaomi MiMo launched 2026-04-03 with no 5h limit" comparison** — Borderline. It is true per the background. *Decision rule:* Cite in the contingency section *only* as a one-liner showing the user has options outside MiniMax, but do not develop the comparison. The user is asking about MiniMax efficiency.
- **M3 "thinking" / reasoning tokens** — Borderline. Background flagged this as to-be-verified. *Decision rule:* Mention in the known-unknowns section, note that it can interact with TPM and caching, do not assert behavior we don't have data on.
- **General LLM cost-reduction surveys** — Borderline. The background's section 2.12 compiles them. *Decision rule:* Use them as evidence behind MiniMax-specific recommendations (e.g., "M3's passive caching follows the same 50–90% range documented industry-wide"). Do not list them as standalone techniques.
- **The "remains_time drains passively without API calls" bug** — Borderline. Open issue #47. *Decision rule:* Mention as a caveat on the `remains` endpoint monitoring recommendation. The user should know the data source has an open issue.

---

## 4. Question type and capabilities needed

This is a "design a plan" task with a concrete recent incident. It is not a survey, not a comparison, not a tutorial. The capabilities below are ranked by their centrality to the deliverable.

### 4.1 Framework building — **HIGH**

**Why:** The deliverable *is* a framework: a diagnosis taxonomy, a three-horizon plan, a quantified opportunity matrix, a monitoring checklist, a contingency decision tree. The user is asking for a structure they can use, not a list of tips. A report without explicit, reusable frameworks reads as advice column, not as a plan.

**Where to apply:**
- The **diagnosis section** must be a 1-page framework: 5 mechanisms × (symptoms × log fields × remedy). Should fit in a table.
- The **opportunity matrix** must be a table with columns: technique, lever, effort, expected impact, what to verify.
- The **three-horizon plan** must be three distinct sections with parallel structure (each action has: what, why, effort, owner, verification).
- The **contingency decision tree** must be a 3-branch tree on diagnosis (1002 → backoff/batch; 2045 → smooth; 2056 → quota management).

### 4.2 Actionable advice — **HIGH**

**Why:** The user said "design a plan." Every section must end in a concrete, do-this action. The judgment correctly flagged this as the spine.

**Where to apply:**
- Every sub-section in the plan should end with a bolded "Do this" imperative.
- Recommendations should be sequenced (do A before B because...).
- The quantified matrix should be a *prioritized* matrix, not alphabetical.
- The contingency section should be a decision tree ("if diagnosis = X, do Y; if = Z, do W").

### 4.3 Causal reasoning — **HIGH**

**Why:** The user is technical and will not be impressed by "best practices." They want to know *why* a rate limit fires, *what specifically triggers it*, and *what changes when they switch levers*. A plan without causal chains is brittle.

**Where to apply:**
- For each rate-limit mechanism, explain *what causes it* (RPM cap = too many requests per minute; rate-growth = traffic shape; 2056 = credit exhaustion; peak-hour = calendar load).
- For each technique, explain *why* it works (caching = prefix reuse = fewer billed input tokens; subagent = parallel work + context isolation = larger effective cache hit rate; rate-growth smoothing = fewer triggers of the 2045 threshold).
- For the M3 vs M2.x split, explain *why* M3's RPM is lower (MSA sparser attention, larger context load on the same hardware budget).

### 4.4 Critical annotation — **HIGH**

**Why:** The background's "to be verified" list is non-empty. The user must know what to verify in their own data. The plan must distinguish "what MiniMax says" from "what we can confirm from the data we have" from "what the user must check."

**Where to apply:**
- A dedicated **Known Unknowns** section at the end, listing each to-be-verified fact with a concrete verification step (e.g., "Poll the `remains` endpoint every 5 minutes for 24 hours and check if `remains_time` decrements without API calls — this is bug #47").
- Inline annotations in the plan where the recommendation depends on a fact the user must confirm (e.g., "M3 passive-cache hit rate is reportedly high on PayGo but partially opaque on Token Plan Plus; verify in your usage logs before assuming the 66.7% saving applies to your workload").
- Source-attribution for any number used (66.7% saving → official caching doc; 200/10M RPM/TPM → official rate-limits page; 5h/weekly → official FAQ).

### 4.5 Non-obvious insight — **MEDIUM**

**Why:** The judgment flagged three non-obvious insights that elevate the plan above a checklist. The user is technical; a research-report register calls for at least a few "I didn't know that" moments.

**Where to apply (the three insights the judgment committed to):**
- **Rate-growth (2045) is the silent killer** — bursts trigger it; smoothing is high-leverage. Most users add backoff when they hit 2045, but backoff is the wrong fix. Smoothing is.
- **Peak-hour dynamic throttle is a calendar problem, not a code problem** — schedule heavy work outside 15:00–17:30 China time weekdays. No amount of caching helps if you hit a calendar-based soft throttle.
- **Subagent delegation is a *caching* technique in disguise** — `delegate_task` puts work in subagent contexts, so the main session's prefix stays stable for cache hits. The lever is not "save tokens" but "keep the main prefix cacheable."

A fourth non-obvious insight worth surfacing: **the 5h and weekly windows stack.** A user can be *under* the 5h cap and *over* the weekly. Plan for the weekly as the binding constraint for sustained use, and the 5h as the binding constraint for sprints.

### 4.6 Scenario branching — **MEDIUM**

**Why:** The judgment said "mild" branching. A small branch on tier (Plus vs Max vs Ultra) and on which mechanism fired. Don't over-branch.

**Where to apply:**
- The contingency section can have one mini-branch on tier: "if you're on Plus and the 5h cap is the binding constraint, upgrading to Max doubles the per-5h envelope. If the weekly is the binding constraint, the upgrade ratio is similar but the spend is higher."
- The diagnosis section can have one mini-branch on whether the user is hitting 1002/2045/2056 — the recommended technique set differs.
- A scenario for "if the cause is peak-hour" → "if the cause is weekly" → "if the cause is RPM" — three paths, not ten.

### 4.7 Comparative analysis — **LOW**

**Why:** The user is on MiniMax. Comparing to Anthropic or OpenAI is a digression. The judgment is explicit: "don't recommend switching vendors."

**Where to apply:**
- At most one sentence in the contingency section: "Switching vendors (Xiaomi MiMo, Anthropic Pro) is an option but is a separate decision from Token Plan efficiency."
- The M3 vs M2.7 vs M2.7-highspeed *internal* comparison is fine and necessary — that's not vendor comparison, it's model selection within the user's stack.

### 4.8 Data-driven argumentation — **MEDIUM**

**Why:** The background has hard numbers (66.7% saving, 200/10M vs 500/20M, $0.30/$1.20 PayGo, 5h × 10 weekly). The plan must use them. Numbers without sourcing look like guesses; numbers with sourcing look like research.

**Where to apply:**
- The opportunity matrix should have an "expected impact" column with numbers where possible, "verify in your data" where not.
- The Token Plan mechanics section should have a single consolidated reference table.
- The contingency section can show a 2-line cost calc (e.g., "Plus at $20/mo + $25 credits = $45/mo for ~10× burst headroom").

### 4.9 Historical analogy — **LOW**

**Why:** The Anthropic Pro weekly-limit story (2025-08-28) is a useful one-liner to establish that "weekly caps are now industry standard," but should not become a section.

**Where to apply:**
- One sentence in the Token Plan mechanics section: "Anthropic added weekly limits to Claude Pro in Aug 2025 citing extreme '24/7 background' use; MiniMax's dual window is the same pattern."

### 4.10 Capabilities NOT to lean on

- **Pure tutorial mode** — The user knows what a token is, what caching is, what an LLM is. Don't teach.
- **Vendor cheerleading** — "MiniMax is great" is not a recommendation. Specific features are.
- **Hedging** — "You might consider" is weaker than "do this." The judgment was explicit: professional-direct tone.

---

## 5. Key facts and verification checklist

These are the facts the writing stage will likely rely on. For each: what it is, why it's central, why it might need verification, and where to verify.

### 5.1 M3 RPM/TPM (200 / 10,000,000)

- **Why central:** Determines whether a user's high-throughput workload can run on M3 or needs M2.7.
- **Why verify:** The background notes this is the API-key table, not the Token Plan table. If the Token Plan enforces a *lower* cap (e.g., to fit the "3–4 agents" hint), the user's optimization math is wrong.
- **Source:** <https://platform.minimax.io/docs/guides/rate-limits> (official, primary).
- **Verification path:** Run a controlled burst on M3 via Token Plan and observe the 1002 threshold empirically. Cross-check with M2.7.

### 5.2 M2.7 / M2.7-highspeed RPM/TPM (500 / 20,000,000)

- **Why central:** The M2.x ceiling. Determines how much headroom M2.7 gives over M3.
- **Why verify:** Same as 5.1. Token Plan vs API-key distinction applies.
- **Source:** Same official page.
- **Verification path:** Same as 5.1.

### 5.3 Token Plan tier prices ($20 / $50 / $120, 49 / 119 / 469 元)

- **Why central:** Anchors the contingency math.
- **Why verify:** Currency and pricing change. Background says "as of 2026-06-04." Check for post-M3-launch adjustments.
- **Source:** <https://platform.minimax.io/docs/guides/pricing-token-plan>.
- **Verification path:** Re-fetch the official pricing page; cross-check with the 2026-06-02 M3 launch press.

### 5.4 Token Plan agent count hints (Plus 3–4, Max 4–5, Ultra 6–7)

- **Why central:** The only published hint of Token Plan envelope. The user almost certainly falls into one of these.
- **Why verify:** "Approximately" is a wide range. The user needs to know whether 3.5 or 4.5 is the binding number.
- **Source:** <https://platform.minimax.io/docs/token-plan/faq#token-plan-limit-rules>.
- **Verification path:** Community reports on r/MiniMax_AI, user-side testing, MiniMax support ticket.

### 5.5 5h rolling and weekly dual window

- **Why central:** Defines the envelope. The user said "1 hour of inactivity" — likely a 5h or weekly cap, not a per-minute cap (a per-minute cap would be 60 seconds, not 60 minutes).
- **Why verify:** Disputed in the community. Some say it's a switch from 5h to weekly; the official says it's a *dual* window.
- **Source:** <https://platform.minimax.io/docs/token-plan/faq#reset-calculation>.
- **Verification path:** Watch the usage bar for a full 5h cycle, then a full weekly cycle. Confirm the reset behavior empirically.

### 5.6 Peak-hour window (weekdays 15:00–17:30 China time)

- **Why central:** A calendar-based throttle. The user can avoid it by scheduling.
- **Why verify:** The "15:00–17:30" is from a press release, not the official FAQ. The FAQ uses softer language ("may tighten during peak traffic"). The exact window may be approximate.
- **Source:** Press release 2026-03-23, cross-checked with the official FAQ.
- **Verification path:** Plot 429 timestamps over a 2-week window. If they cluster 15:00–17:30 China time on weekdays, the window is real.

### 5.7 66.7% saving on M3 passive caching (the official example)

- **Why central:** The headline number for the highest-leverage technique.
- **Why verify:** The example is in the official docs but is a *worked example*, not a *guaranteed saving*. Hit rate depends on prefix stability. The user may see different numbers.
- **Source:** <https://platform.minimax.io/docs/api-reference/text-prompt-caching>.
- **Verification path:** Run a controlled workload with stable prefix; measure hit rate and cost reduction in the user's own `/usage` output.

### 5.8 Passive cache minimum (512 input tokens)

- **Why central:** Workloads under 512 tokens get no cache benefit at all.
- **Why verify:** Stated in the official docs, but the user's *effective* threshold may be higher if their prefix is dynamic.
- **Source:** Same.
- **Verification path:** Inspect the user's typical prompt sizes. If most are < 1k tokens, caching is a secondary lever, not a primary one.

### 5.9 M3 supports passive caching but NOT explicit `cache_control`

- **Why central:** A user migrating from M2.7 to M3 will lose explicit-cache control.
- **Why verify:** Documented, but the M3 release notes (2026-06-01) may have updated this. Re-check.
- **Source:** <https://platform.minimax.io/docs/api-reference/anthropic-api-compatible-cache> (lists M2.x only, not M3).
- **Verification path:** Re-fetch the explicit-caching page; check the M3 release blog for any addendum.

### 5.10 Anthropic-compatible `cache_control` lifetime (5 minutes)

- **Why central:** Determines whether explicit caching is useful for the user's traffic shape.
- **Why verify:** Stable per the docs.
- **Source:** Same.
- **Verification path:** If using, observe hit rate in production.

### 5.11 PayGo pricing (M3 $0.30/$1.20 standard, $1.20/$4.80 above 512k; M2.7 $0.30/$1.20; M2.7-highspeed $0.60/$2.40; cache read $0.06/M; legacy M2.x cache read $0.03/M)

- **Why central:** Anchors the contingency section.
- **Why verify:** M3 launch came with a 7-day 50% promo — the user's pricing math should use the post-promo number for forward planning.
- **Source:** <https://platform.minimax.io/docs/guides/pricing-paygo>.
- **Verification path:** Re-fetch. Cross-check the M3 launch announcement for the promo end date.

### 5.12 Credits packages ($5 / $25 / $100, 365-day validity)

- **Why central:** Cheapest hedge for a one-time burst. The user can buy once and not lose it.
- **Why verify:** Stable. Re-check.
- **Source:** <https://platform.minimax.io/docs/guides/pricing-token-plan>.
- **Verification path:** Re-fetch.

### 5.13 M2.7-highspeed = 2× standard PayGo ($0.60/$2.40)

- **Why central:** A "faster but more expensive" option. The plan should not recommend it as a default.
- **Why verify:** Stable.
- **Source:** Same PayGo page.
- **Verification path:** Re-fetch.

### 5.14 Hermes Agent tips (`/compress`, `delegate_task`, `execute_code`, `/model`, `/usage`, `/insights`)

- **Why central:** The user's "natural" lever set if they're running on Hermes.
- **Why verify:** Stable per the Hermes docs. The skill-creation pattern (5+ steps → make a skill) is also stable.
- **Source:** <https://hermes-agent.nousresearch.com/docs/guides/tips>.
- **Verification path:** Re-fetch. The user's specific Hermes version may have additional commands.

### 5.15 Memory size caps (MEMORY.md 2,200 chars, USER.md 1,375 chars)

- **Why central:** Determines the maximum stable prefix the user's prompts can hold.
- **Why verify:** Stable per the docs. These are *prompt* caps, not disk caps.
- **Source:** Same.
- **Verification path:** Check the user's actual MEMORY.md / USER.md file sizes.

### 5.16 M3 SWE-Bench Pro 59% / M3 sparse attention 9.7× prefill / 15.6× decode / 1/20 per-token compute at 1M

- **Why central:** Marketing numbers. Useful for *justifying* the M3 model choice in the model-selection section, but not for the plan itself.
- **Why verify:** Vendor-published; not independently audited at the time of the background.
- **Source:** MiniMax blog <https://www.minimax.io/blog/minimax-m3>, secondary press.
- **Verification path:** Re-fetch; check for third-party benchmarks (Reddit, r/LocalLLaMA, academic).

### 5.17 Open issue: cache-read discount not visible in Token Plan Plus; remains_time drains passively (#47)

- **Why central:** Caveat on observability. The user may *think* caching is saving them money when the console doesn't show it.
- **Why verify:** Open issue. Could be resolved any time.
- **Source:** <https://github.com/MiniMax-AI/MiniMax-M2.7/issues/47>.
- **Verification path:** Check the issue's current state. Re-verify on the user's own console.

### 5.18 Anthropic 2025-08-28 weekly limit precedent

- **Why central:** Industry context. One-line mention.
- **Why verify:** Stable, multiple-source confirmed.
- **Source:** news.qq.com, fromgeek.com, cls.cn (per background).
- **Verification path:** Re-check Anthropic's official changelog if needed.

### 5.19 Xiaomi MiMo Token Plan (2026-04-03, 4 tiers, ¥39–¥659/month, no 5h limit)

- **Why central:** Industry context. Vendor-comparison cautionary mention.
- **Why verify:** Stable.
- **Source:** 163.com, news.qq.com (per background).
- **Verification path:** Re-check only if the contingency section needs it.

### 5.20 M3 launch date (2026-06-01)

- **Why central:** Establishes that M3 has been live for 3 days at the time of the user's question. Any "M3 has cache issues" reports are still very fresh.
- **Why verify:** Confirmed.
- **Source:** MiniMax blog, multiple press.
- **Verification path:** Done.

---

