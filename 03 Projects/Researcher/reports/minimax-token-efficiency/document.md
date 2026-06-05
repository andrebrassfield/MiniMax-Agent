# Deep Research: MiniMax Token Plan Efficiency and Rate-Limit Recovery

**Source query:** *"We got rate limited on our minimax token plan earlier and that caused about an hour of inactivity. Can we do some research and design a plan if its possible to be more efficient with our minimax token plan?"*

This document synthesizes background facts into a research document for the writing stage. It is denser than `background.md`: every fact carries a source URL, reliability tag, and confidence rating. Disagreements between sources are flagged inline. Gaps are annotated.

---

## 1. The four rate-limit mechanisms (the disambiguation that everything else depends on)

**Why this is the spine:** the user's "rate limited" report maps to at least five distinct throttles in the MiniMax catalog. Each has a different root cause and a different fix. A plan that treats them as one mechanism will fail.

| Code | Name | Trigger | Stated remedy | Likely surface in our setup |
|---|---|---|---|---|
| 1002 | API rate limit | RPM or TPM hard cap hit (per API key) | retry later | Bursty fleet requests, multiple agents in parallel |
| 1041 | Connection limit | Too many concurrent connections | contact us | Long-running streaming connections, model + image/video pipeline |
| 2045 | Rate-growth limit | Sudden increases or decreases in request rate | "avoid sudden spikes" | Cron jobs waking the fleet, scheduled tasks firing simultaneously |
| 2056 | Usage limit exceeded | 5h rolling or weekly credit exhaustion | "wait for next 5h window" | Sustained heavy use, batch workloads that burn the weekly cap |
| — | Peak-hour dynamic throttle | Weekdays 15:00–17:30 China time | "may tighten under load" | Anything running during CN business hours, especially fleet-wide |

**Sources:** <https://platform.minimax.io/docs/api-reference/errorcode>, <https://platform.minimax.io/docs/token-plan/faq#token-plan-limit-rules>, <https://news.qq.com/rain/a/20260323A059UP00>

**Reliability:** Official docs (high). **Confidence:** high on the existence of each code and the published error meanings; low on the precise mapping between code and throttle type (RPM vs TPM vs 5h vs weekly). The docs do not publish a code-to-throttle-type table. **To be verified** empirically against the user's logs.

**Judgment:** the 2045 "rate-growth" throttle is the silent killer. Most fleets naturally produce bursty traffic (cron waking, subagent fan-out, batch jobs starting on the hour) and the rate-growth limit will catch a smoothly-running system if the load curve has too sharp a knee. This is high-leverage and the user almost certainly doesn't know about it.

---

## 2. Token Plan tier mechanics and the "≈3–4 agents" hint

**The published tiers** (as of 2026-06-04, official docs):

| Tier | USD/month | CNY/month (per 2026-06-01 launch) | 5h rolling | Weekly | Agent count hint (peak) |
|---|---|---|---|---|---|
| Plus | $20 | ¥49 | yes | yes | ~3–4 agents |
| Max | $50 | ¥119 | yes | yes | ~4–5 agents |
| Ultra | $120 | ¥469 | yes | yes | ~6–7 agents |

**Key non-obvious mechanics:**

1. **Two windows, not one.** Both the 5h rolling and the weekly are active. Burning the 5h allowance does NOT relieve the weekly cap. Sustained heavy users hit the weekly first.
2. **Quota is credit-based and shared across modalities.** The same credits cover text, image, speech, music, video, and code. A busy video pipeline will deplete the same pool a busy code agent uses.
3. **Credits don't carry over.** Unused monthly credits are forfeit. A user running "easy" workloads wastes capacity.
4. **The "≈N agents" hint is order-of-magnitude only.** The docs explicitly call it approximate. It is enforced as an aggregate session counter at the platform layer, not as an RPM/TPM figure.
5. **Mid-cycle upgrades** are supported; price difference is pro-rated and the new tier takes effect immediately.
6. **Subscriptions can be supplemented with separately-purchased credits** (1,000 credits = $1, 365-day validity). When both Token Plan quota and Credits are available, the plan is consumed first; credits cover eligible overflow automatically.

**Sources:** <https://platform.minimax.io/docs/guides/pricing-token-plan>, <https://platform.minimax.io/docs/token-plan/faq>, <https://news.qq.com/rain/a/20260323A059UP00>

**Reliability:** Official (high) on the tier table and credits packages; medium on the "≈N agents" claim because the docs flag it as approximate. **Confidence:** high on tier structure, medium on the agent-count hint as a hard cap.

**Judgment:** if the user is on Plus and running 4+ agents, they are at the published cap. The "1 hour of inactivity" lines up with the 5h rolling window — most likely a 2056 hit on Plus during a peak burst, OR a 2045 (rate-growth) hit from a cron fan-out. The weekly cap is more often a slow-burn problem than an outage-grade event.

---

## 3. The M3 vs M2.x tradeoff (the model choice that drives the math)

**Published per-key rate limits** (API key, not Token Plan tier):

| Model | RPM | TPM |
|---|---|---|
| MiniMax-M3 | 200 | 10,000,000 |
| MiniMax-M2.7 / M2.7-highspeed | 500 | 20,000,000 |
| MiniMax-M2.5 / M2.5-highspeed | 500 | 20,000,000 |
| MiniMax-M2.1 / M2.1-highspeed | 500 | 20,000,000 |
| MiniMax-M2 | 500 | 20,000,000 |

**Pay-as-you-go pricing** (relevant if/when the user migrates workloads off Token Plan):

| Model | Input ($/M) | Output ($/M) | Cache read ($/M) | Cache write ($/M) |
|---|---|---|---|---|
| M3 ≤ 512k input | $0.30 | $1.20 | $0.06 | (see doc) |
| M3 > 512k input (limited) | $1.20 | $4.80 | $0.24 | — |
| M2.7 | $0.30 | $1.20 | $0.06 | $0.375 |
| M2.7-highspeed | $0.60 | $2.40 | — | — |
| M2.5 / M2.1 / M2 (legacy) | same as M2.7 input/output | — | $0.03 | — |
| M3 Priority tier | 1.5× the standard prices | | | |

**M3 launch (2026-06-01) and what it changes:**

- **MSA sparse attention** architecture — index branch pre-selects top-K KV blocks before full attention.
- **1M-token context window** (vs M2.7's shorter context).
- **SWE-Bench Pro: 59%** (near Opus 4.7, comparable to GPT-5.5 and Gemini 3.1 Pro).
- **At 1M context: ~9.7× prefill speedup, ~15.6× decode speedup vs M2.7.** Per-token compute at 1M reduced to ~1/20 of M2.
- **Decoding reportedly >15× faster** in some scenarios.

**Sources:** <https://platform.minimax.io/docs/guides/rate-limits>, <https://platform.minimax.io/docs/guides/pricing-paygo>, <https://www.minimax.io/blog/minimax-m3>, <https://m.163.com/dy/article/KU5A1I1U05561FZE.html>

**Reliability:** Official pricing (high). M3 launch claims from official blog (high); benchmark numbers from MiniMax itself (medium — vendor-reported, no independent verification yet). **Confidence:** high on rate-limit table and pricing; medium on the speedup claims (vendor-reported).

**Judgment:** the M3 RPM is 60% lower than M2.7 (200 vs 500) and TPM is 50% lower (10M vs 20M). This is a real constraint. M3 wins on:
- Long-context tasks (>512k input, where MSA is the only path to fast inference)
- Quality ceiling where the SWE-Bench Pro gain matters
- Per-token economics at long context (1/20 of M2's compute at 1M)

M3 loses on:
- Throughput (lower RPM/TPM)
- Explicit `cache_control` (not supported on M3; only on M2.x — see §4)

**Implication for the user's setup:** the right call is hybrid routing. Use M2.7 for high-throughput cache-friendly workloads (because the explicit cache_control makes a real dent on M2.7). Use M3 for long-context or quality-critical tasks only. Default everything else to M2.7. Don't let the fleet default to M3 just because it's the new model.

---

## 4. Prompt caching: the single highest-leverage default

**Two flavors:**

### Passive (automatic) caching
- Supported on **M3, M2.7, M2.5, M2.1**
- Minimum **512 input tokens** for caching to apply
- **Prefix matching order:** tool list → system prompts → user messages
- **Best practice from docs:** "Place static or repeated content (including tool list, system prompts, user messages) at the beginning of the conversation, and put dynamic user information at the end"
- **Worked example in the docs:** 50,000 total input, 45,000 cache hits, 5,000 new input, 1,000 output → $0.0108 vs $0.0324 without caching = **≈66.7% saving** at M3 standard pricing
- **Expiration:** "automatically adjusted based on system load"
- **Important caveat:** caching still counts toward the 512k / >512k threshold — long-context pricing applies when input > 512k, *including cache-hit tokens*

### Explicit (Anthropic-compatible) caching
- Available on **M2.7, M2.5, M2.1, M2** (M3 NOT listed)
- Set via `cache_control` parameter; first-time cache write incurs an additional charge; hits are discounted
- **Cache lifetime: 5 minutes**, refreshed on hit
- Compatible with Anthropic SDK: `ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic`

**Sources:** <https://platform.minimax.io/docs/api-reference/text-prompt-caching>, <https://platform.minimax.io/docs/api-reference/anthropic-api-compatible-cache>

**Reliability:** Official (high). **Confidence:** high on the cache mechanics; medium on the Token Plan-specific cache discount visibility (open issue MiniMax-AI/MiniMax-M2.7#47 claims the cache-read discount is "not verifiable in Token Plan Plus" — i.e., the billing display doesn't break it out cleanly).

**Judgment:** passive caching on M3 is the easiest win. The cost is prefix discipline — putting static content first. The benefit (up to 66.7% on input tokens per request, with the worked example) is enormous. For fleet setups, every agent that has a stable system prompt + tool list is leaving money on the table until the prefix is stable. This is a one-time audit, not ongoing work.

The M2.7 explicit cache_control is for callers who need guaranteed cache hit behavior or who are porting Anthropic-SDK code. The 5-min lifetime is shorter than Anthropic's (1 hour default) but the pattern works for high-frequency agents.

The open bug on cache discount visibility in Token Plan Plus (#47) means the user may need to *measure* the cache hit rate themselves (via the `remains` endpoint or by counting prompt-cache-* headers in the response) rather than trusting the usage bar to show it. Not a blocker, but worth knowing.

---

## 5. Hermes Agent native efficiency features (the low-hanging fruit for the user's likely setup)

The user is almost certainly running through Hermes Agent or a similar multi-agent orchestrator. Hermes ships efficiency primitives the user may not be using:

- **`/compress`** — compress conversation history before hitting limits. Should be called before the context fills.
- **`delegate_task`** — runs subagents in parallel; only summaries return to main context. This is the *single highest-leverage* trick for fleet setups because it keeps main-context tokens low (improving cache hit rate on the system prompt + tool list).
- **`execute_code`** — one script vs many terminal calls. Each shell call is a round-trip with overhead; batching into a script is ~2–3× faster.
- **`/model`** — switch mid-session. Enables hybrid routing per task (M2.7 for cache-friendly, M3 for long-context).
- **`/usage`** — per-session consumption.
- **`/insights`** — 30-day patterns.
- **Memory size caps** — `MEMORY.md ≈ 2,200 chars`, `USER.md ≈ 1,375 chars`. Memory bloat directly inflates every subsequent request's input cost.
- **Skill creation heuristic** — "if a task takes 5+ steps and you'll do it again, ask the agent to create a skill for it." Skills keep repeated workflows out of the main context.
- **Important warning from Hermes docs:** "Memory is a frozen snapshot — changes made during a session don't appear in the system prompt until the next session starts. The agent writes to disk immediately, but the prompt cache isn't invalidated mid-session." Implication: changing the system prompt mid-session is *cache-poisoning*; wait for the next session.

**Sources:** <https://hermes-agent.nousresearch.com/docs/guides/tips>

**Reliability:** Authoritative (Hermes's own docs, last built 2026). **Confidence:** high on the existence and behavior of these primitives.

**Judgment:** the chief-of-staff-level wins for the user are:
1. Audit every Hermes session: is the system prompt + tool list stable enough to cache hit? If not, the biggest single win is prefix discipline.
2. Replace serial multi-step flows with `delegate_task` parallel flows where possible. The main session gets *summaries* back, not full transcripts.
3. Set a session memory size cap and enforce it. Memory bloat is the slow poison.
4. Use `/compress` proactively, not reactively.
5. Use `/model` to route long-context work to M3 and everything else to M2.7.

---

## 6. Broader LLM cost-reduction techniques (the academic / industry toolkit)

These are documented across vendors and the academic literature. They are general-purpose, not MiniMax-specific:

### Prompt compression
- **LLMLingua / LLMLingua-2** (Microsoft Research) — "up to 20× compression ratio with minimal performance loss" for prompt text. Removes low-information tokens from long prompts before they hit the API.
- **EMNLP 2023 "Compressing Context to Enhance Inference Efficiency"** — context-side compression for long conversations. Source: <https://doi.org/10.18653/v1/2023.emnlp-main.391>
- **Activation Beacon** — long-context compression that preserves key signal. Source: <https://blog.csdn.net/beingstrong/article/details/145289852>

### Structured output
- "Token Efficiency with Structured Output from Language Models" — forcing the model to return JSON or a constrained schema reduces both output tokens and re-asking for malformed responses. Source: <https://medium.com/data-science-at-microsofn/token-efficiency-with-structured-output-from-language-models-be2e51d3d9d5>

### Batching and request-coalescing
- Cross-vendor: Anthropic, OpenAI, Google, 豆包, 阿里云通义, Moonshot — all publish guides recommending request batching, multi-key load balancing, exponential backoff with `Retry-After` honoring, and request coalescing (combine multiple small asks into one).
- Specifically for fleets: queue up sub-100-token asks into a single request rather than fanning out. Subagent delegation via `delegate_task` is the Hermes-flavored version of this.

### Cross-vendor industry pattern: weekly limits
- **Anthropic added weekly limits to Claude Pro/Max on 2025-08-28** citing extreme "24/7 in background" usage and account-pool sharing. <5% of subscribers affected. Sources: <https://news.qq.com/rain/a/20250729A023J400>, <https://news.fromgeek.com/latest/237267.html>, <https://www.cls.cn/detail/2098899>
- **This is the precedent for the MiniMax weekly cap.** Same 5h + weekly dual-window pattern. Anthropic's stated reason ("background automation" abuse) is likely the same motivation here.

**Sources:** <https://www.microsoft.com/en-us/research/project/llmlingua/llmlingua-2/>, <https://arxiv.org/abs/2409.01227>, <https://artificialanalysis.ai/models/caching>, <https://timwappat.info/auto-cache-passively-saves-on-you-ai-model-costs/>

**Reliability:** Mixed — Microsoft Research and EMNLP are authoritative; industry blog compilations are reliable for breadth but light on rigor. **Confidence:** high on the existence of these techniques; medium on the magnitude claims (20× compression with "minimal loss" is from the technique's authors).

**Judgment:** for the user's setup, the highest-leverage of these is request batching and subagent delegation. LLMLingua-style prompt compression is real but is *not* a one-line win — it requires running the compressor as a pre-step, which adds latency. Structured output is universally good and free. The weekly-limit precedent matters because it tells the user this is industry-wide behavior, not a MiniMax-specific quirk; they should plan for it as a permanent constraint, not a bug to file.

---

## 7. Disputes and competing viewpoints (flagged honestly)

- **Is M3 "open source"?** — Multiple Chinese outlets (网易, 量子位, 36氪-style coverage) call M3 "开源." The MiniMax blog does not explicitly confirm full open-source licensing in the page title/snippet we have. To be verified by checking the model release repo directly.
- **Weekly cap = "10× the 5-hour amount"** — Reported in third-party press (e.g., <https://news.qq.com/rain/a/20260323A059UP00>), not confirmed in the official FAQ. The official FAQ says "5-hour rolling and weekly windows" but does not publish the per-week credit cap numeric. Conflict: is it 10× or is it independent?
- **Cache-read discount visibility in Token Plan Plus** — Bug report MiniMax-AI/MiniMax-M2.7#47 claims the cache-read discount is "not verifiable in Token Plan Plus." Open issue, not settled. The user should not assume their usage bar reflects the cache savings until this is resolved.
- **"M3 1M context compute is 1/20 of M2"** — Vendor-reported. No independent benchmark reproduction confirmed in the sources we have.

**Sources:** as cited inline above.

**Judgment:** these disputes are real but they don't change the action plan. The user should:
1. Not assume any unverified number. Where the docs are silent, the plan should say "verify in your logs."
2. Not bet on M3 being open-source-licensed; that doesn't change the efficiency story.
3. Measure cache hit rate themselves (e.g., via response headers or by comparing input-token counts with and without cache prefix changes) rather than trusting the usage bar.

---

## 8. The MiniMax open bug (worth knowing about)

**MiniMax-AI/MiniMax-M2.7#47** — `remains_time` drains passively without API calls, AND cache-read discount is not verifiable in Token Plan Plus. Status: open.

**Implications:**
- The `remains` endpoint may show lower credits than actually available (passive drain), which could mislead a user into thinking they're near the cap when they aren't.
- The cache discount may not appear in the console usage bar, so users might not realize they're getting the savings.

**Source:** <https://github.com/MiniMax-AI/MiniMax-M2.7/issues/47>

**Reliability:** Authoritative (the official issue tracker). **Confidence:** high on the existence of the issue; the resolution path is unknown.

**Judgment:** the user should not trust the usage bar as a single source of truth. Cross-check by tracking input tokens in their own request log against the bar's reported consumption. The gap (if any) is the cache discount.

---

## 9. Gaps and to-be-verified items (the honest list)

The background research round was thorough but these remain open:

1. **Exact weekly credit allowance per tier.** Official docs don't publish a number. Some press releases cite "10× the 5-hour amount" but it's not in the official FAQ. The user should check their own usage over a full week to see the cap in action.
2. **What error code fires for a true RPM (not TPM) cap hit.** Docs list 1002/2045/2056 but don't map clearly to RPM vs TPM vs weekly credit exhaustion. The user's incident log should record the exact code, the time, the request pattern, and the usage-bar state at that moment.
3. **Whether M3 (vs M2.7) automatically applies the passive cache, and at what hit rate.** The caching doc lists M3 in the supported models for passive caching, but the explicit `cache_control` is NOT supported on M3 (only on M2.x). The implications for M3 callers are not fully detailed in the snippets we have.
4. **Specific M3 TPM/RPM under Token Plan Plus** — the public Rate Limits table is at the API-key level, not the Token Plan tier level. Whether the peak-hour "3-4 agents" cap for Plus is enforced at the RPM/TPM level or as an aggregate agent-session counter is to be verified.
5. **Root cause of the user's "1 hour of inactivity."** None of the searched sources link a specific incident to the user's experience. To diagnose, the user needs to:
   - Check the error code(s) returned during the 1-hour window
   - Check the time-of-day (was it within peak hours 15:00–17:30 China time?)
   - Check the request pattern (was there a burst? was it sustained?)
   - Check the usage-bar state at incident time and at recovery time
   - Cross-reference with the 5h rolling window (was the 5h allowance burned just before?)
6. **M3 thinking / reasoning output token interaction with prompt caching, output token pricing, and TPM cap.** The MiniMax caching example includes thinking content; there's a `reasoning_split=True` parameter for the OpenAI SDK. How thinking tokens interact with caching, output token pricing, and the TPM cap is to be verified beyond what the caching doc shows.

**Judgment:** the user can answer most of these themselves in 30 minutes of log review. The plan should not pretend to know what the user's incident actually was; it should give them a checklist to find out.

---

## 10. Source-graded reference list (de-duplicated, ranked by reliability)

### Official MiniMax documentation (high reliability)
- Token Plan FAQ: <https://platform.minimax.io/docs/token-plan/faq>
- Token Plan Overview: <https://platform.minimax.io/docs/token-plan/intro>
- Token Plan Pricing: <https://platform.minimax.io/docs/guides/pricing-token-plan>
- Rate Limits: <https://platform.minimax.io/docs/guides/rate-limits>
- Pay as You Go: <https://platform.minimax.io/docs/guides/pricing-paygo>
- Prompt Caching (passive): <https://platform.minimax.io/docs/api-reference/text-prompt-caching>
- Explicit Prompt Caching (Anthropic): <https://platform.minimax.io/docs/api-reference/anthropic-api-compatible-cache>
- Error Codes: <https://platform.minimax.io/docs/api-reference/errorcode>
- Hermes Agent integration: <https://platform.minimax.io/docs/token-plan/hermes-agent>
- M3 launch blog: <https://www.minimax.io/blog/minimax-m3>
- Token Plan usage endpoint: `https://www.minimax.io/v1/token_plan/remains`

### Vendor / authoritative (medium-to-high reliability)
- Hermes Agent tips: <https://hermes-agent.nousresearch.com/docs/guides/tips>
- MiniMax-M2.7 issue #47: <https://github.com/MiniMax-AI/MiniMax-M2.7/issues/47>
- LLMLingua-2 (Microsoft Research): <https://www.microsoft.com/en-us/research/project/llmlingua/llmlingua-2/>
- EMNLP 2023 paper (context compression): <https://doi.org/10.18653/v1/2023.emnlp-main.391>
- Cache savings analysis: <https://artificialanalysis.ai/models/caching>
- Auto-cache analysis: <https://timwappat.info/auto-cache-passively-saves-on-you-ai-model-costs/>

### Press / secondary (medium reliability; useful for chronology)
- 腾讯 M3 launch / Token Plan upgrade: <https://news.qq.com/rain/a/20260602A05YGA00>
- 中证网 Token Plan announcement: <https://www.cs.com.cn/sylm/jsbd/202603/t20260323_6542478.html>
- 量子位 M3 实测: <https://m.163.com/dy/article/KUF3V6NG0511DSSR.html>
- 智东西 M3 MSA architecture: <https://m.163.com/dy/article/KU5A1I1U05561FZE.html>
- Anthropic Claude Code 限速: <https://news.qq.com/rain/a/20250729A023J400>
- 闫俊杰 2026 定调 / 财务数据: <https://news.qq.com/rain/a/20260303A004VE00>
- Xiaomi MiMo 横评 (competitor context): <https://news.qq.com/rain/a/20260406A03TB400>

### Community (low-to-medium reliability; useful for real-world reports)
- r/MiniMax_AI weekly limit thread: <https://www.reddit.com/r/vibecoding/comments/1rxwua3/minimax_just_switched_from_5hour_resets_to_weekly/>
- r/MiniMax_AI Token Plan overhaul: <https://www.reddit.com/r/MiniMax_AI/comments/1tv58qc/minimax_token_plan_overhaul_m3_release_what_it/>
- r/LocalLLaMA M3 launch: <https://www.reddit.com/r/LocalLLaMA/comments/1ttdiq0/minimax_m3_coding_agentic_frontier_1m_context/>

---

*End of research document. Next step: writing the user-facing report from this material.*
