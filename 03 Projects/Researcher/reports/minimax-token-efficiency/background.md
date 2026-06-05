# Background: MiniMax Token Plan — Rate Limits and Token Efficiency

User question: *We got rate limited on our MiniMax token plan earlier and that caused about an hour of inactivity. Can we do some research and design a plan if it's possible to be more efficient with our MiniMax token plan?*

This file collects verifiable facts from public sources. No analysis, no recommendations.

---

## 1. Historical facts (dated, source-supported)

### 1.1 MiniMax Token Plan — product timeline

- **2026-03-18** — MiniMax released **M2.7** (described by MiniMax as "首个参与自身迭代的 Cowork Agent 模型" — first model that participates in its own iteration). Source: <https://blog.csdn.net/qq_24252865/article/details/159465814>
- **2026-03-23** — MiniMax announced the **upgrade of Coding Plan → Token Plan**: Plus-tier and above users get the existing M2.7 usage plus additional multimodal (Hailuo video, Speech, Music, Image) call credits. Reported by Sina Finance, 中证网, Wallstreetcn, 网易, 腾讯 (multiple Chinese outlets). Sources:
  - <https://www.cs.com.cn/sylm/jsbd/202603/t20260323_6542478.html>
  - <https://wallstreetcn.com/livenews/3074863>
  - <https://news.qq.com/rain/a/20260323A059UP00>
  - <https://www.topnews.cn/news/145CD4EC45BE4B75>
- **2026-04-03** — Xiaomi launched **Xiaomi MiMo Token Plan** (4 tiers, ¥39–¥659/month), no 5-hour token limit, credit-based. Cited as direct competitor; some Chinese commentators compared its per-token cost unfavorably to MiniMax's plan. Sources:
  - <https://www.163.com/dy/article/KPJG9QMC0511B8LM.html>
  - <https://news.qq.com/rain/a/20260403A03KX600>
  - <https://news.qq.com/rain/a/20260406A03TB400> (critical comparison article)
- **2026-05-31** — MiniMax filed A-share (科创板) listing guidance agreement. Source: <https://news.qq.com/rain/a/20260602A05YGA00>
- **2026-06-01** — MiniMax released **M3** model:
  - Self-developed **MiniMax Sparse Attention (MSA)** architecture
  - 1M-token context window
  - Native multimodal
  - SWE-Bench Pro reported at **59%** (vs. GPT-5.5 and Gemini 3.1 Pro, near Opus 4.7)
  - At 1M context: ~9.7× prefill speedup and ~15.6× decode speedup vs. M2.7
  - Per-token compute at 1M context reduced to ~1/20 of M2
  - Decoding reported >15× faster in some scenarios
  - M3 launched alongside a new Token Plan pricing structure (Plus 49 元 / 6 亿 tokens; Max 119 元 / 18 亿 tokens; Ultra 469 元 / 55 亿 tokens; Plus tier ≈ 5× Claude Pro monthly capacity)
  - Sources:
    - <https://www.minimax.io/blog/minimax-m3>
    - <https://www.reddit.com/r/LocalLLaMA/comments/1ttdiq0/minimax_m3_coding_agentic_frontier_1m_context/>
    - <https://news.qq.com/rain/a/20260602A05YGA00>
    - <https://m.163.com/dy/article/KU5A1I1U05561FZE.html>
    - <https://c.m.163.com/news/a/KUE4UPML0512B07B.html>
- **June 2026 (post-M3 launch, date not specified in source)** — MiniMax responded to community complaints about the newly added weekly quota: "提高了周用量限额, 并对以前没有周限额的老用户保持了这个设定" (raised weekly limits and grandfathered legacy users who previously had no weekly limit). Source: <https://m.163.com/dy/article/KUF3V6NG0511DSSR.html>

### 1.2 Industry context — weekly quota precedent

- **2025-08-28** — Anthropic introduced weekly usage limits on Claude Pro and Claude Max, citing extreme "24/7 in background" usage and account-pool sharing. Anthropic stated <5% of subscribers would be affected. Sources:
  - <https://news.qq.com/rain/a/20250729A023J400>
  - <https://news.fromgeek.com/latest/237267.html>
  - <https://www.cls.cn/detail/2098899>

### 1.3 MiniMax financial figures related to Token Plan demand

- **2025 full-year** — Total revenue $79.038M USD (+158.9% YoY); adjusted net loss $251M USD; gross margin 25.4% (up from 12.2% in 2024); Open Platform / enterprise services revenue $25.963M (+197.8%). Source: <https://news.qq.com/rain/a/20260303A004VE00>
- **2026-02** — M2 series daily-average token consumption was 6× the December 2025 baseline; Coding-Plan-sourced token consumption grew >10×; new open-platform registrations >4×. Source: <https://news.qq.com/rain/a/20260303A004VE00>
- **2026-02** — ARR >$150M USD. Source: same as above.

---

## 2. Current state (only what is directly verifiable from official docs and recent sources)

### 2.1 Token Plan tiers and quota windows (as of 2026-06-04, per official docs)

From <https://platform.minimax.io/docs/guides/pricing-token-plan> and <https://platform.minimax.io/docs/token-plan/faq>:

| Tier | Price (USD/month) | Price (CNY/month, per June 1 launch) | 5-hour rolling | Weekly | Agent usage (peak) |
|---|---|---|---|---|---|
| Plus | $20 | 49 元 | yes | yes | ≈3–4 agents |
| Max | $50 | 119 元 | yes | yes | ≈4–5 agents |
| Ultra | $120 | 469 元 | yes | yes | ≈6–7 agents |

- Quota is **credit-based** and shared across text, image, speech, music, video, and code models on the API Platform.
- Unused subscription credits **do not carry over** to the next billing cycle.
- Console usage bar is the source of truth for current usage.
- Subscriptions can be upgraded mid-cycle; the price difference only is charged and the new plan takes effect immediately.

### 2.2 Credits packages (separately purchasable, no plan required)

From <https://platform.minimax.io/docs/guides/pricing-token-plan>:

- 1,000 credits = $1
- Packages: $5 (5,000), $25 (25,000), $100 (100,000)
- Validity: 365 days from purchase
- Used via Subscription Key with the same resource coverage as Token Plan
- When both Token Plan quota and Credits are available, Token Plan quota is used first; Credits cover eligible overflow automatically.

### 2.3 API rate limits — RPM and TPM (per official docs)

From <https://platform.minimax.io/docs/guides/rate-limits>:

| Model | RPM | TPM |
|---|---|---|
| MiniMax-M3 | 200 | 10,000,000 |
| MiniMax-M2.7 / M2.7-highspeed | 500 | 20,000,000 |
| MiniMax-M2.5 / M2.5-highspeed | 500 | 20,000,000 |
| MiniMax-M2.1 / M2.1-highspeed | 500 | 20,000,000 |
| MiniMax-M2 | 500 | 20,000,000 |

For non-LLM modalities: Video 5 RPM, T2A / Voice Cloning 60 RPM, Voice Design 20 RPM, Image Generation 10 RPM, Music Generation 120 RPM / 20 concurrent.

### 2.4 Pay-as-you-go pricing (per official docs)

From <https://platform.minimax.io/docs/guides/pricing-paygo>:

- **MiniMax-M3 ≤ 512k input tokens** (7-day 50% promo): input $0.30 / M tokens, output $1.20 / M tokens, cache read $0.06 / M tokens
- **MiniMax-M3 > 512k input tokens** (limited availability): input $1.20, output $4.80, cache read $0.24
- **MiniMax-M3 Priority tier** (service_tier param): 1.5× the standard prices
- **MiniMax-M2.7**: input $0.30 / M, output $1.20 / M, cache read $0.06 / M, cache write $0.375 / M
- **MiniMax-M2.7-highspeed**: input $0.60 / M, output $2.40 / M
- Legacy M2.5 / M2.1 / M2 listed at the same input/output rates as M2.7; cache read is $0.03 / M (vs $0.06 for M2.7/M3 standard).

### 2.5 Peak-hour dynamic throttling (per official docs)

From <https://platform.minimax.io/docs/token-plan/faq#token-plan-limit-rules>:

- "Plus: Supports approximately 3–4 agents" / "Max: 4–5 agents" / "Ultra: 6–7 agents" — only an order-of-magnitude hint
- Peak hours are "typically occurring on weekdays from 15:00–17:30" (presumably China time, based on the same phrasing in Chinese press releases)
- Reset window for included credits: 5-hour rolling + weekly; weekly reset occurs "in the next 5-hour window" per error code 2056
- The official FAQ calls these "Platform Rate Limiting Rules" and explicitly says they "may tighten during peak traffic"
- Press release (2026-03-23) confirms peak window: "工作日 15:00–17:30 实施动态限流策略" and a weekly cap "5小时用量的 10倍". Source: <https://news.qq.com/rain/a/20260323A059UP00>

### 2.6 Common error codes (per official docs)

From <https://platform.minimax.io/docs/api-reference/errorcode>:

| Code | Meaning | Stated solution |
|---|---|---|
| 1000 | unknown error | retry later |
| 1001 | request timeout | retry later |
| **1002** | **rate limit** | retry later |
| 1004 | not authorized / API key mismatch | check key |
| 1008 | insufficient balance | top up account |
| 1024 | internal error | retry later |
| 1026/1027 | input/output sensitive | change content |
| 1039 | token limit | retry later |
| 1041 | conn limit | contact us |
| 2045 | rate growth limit | "Please avoid sudden increases and decreases in requests" |
| **2056** | **usage limit exceeded** | "Please wait for the resource release in the next 5-hour window" |

The standard 429 / `RateLimitError` mentioned in third-party guides is mapped to 1002/2045/2056 in MiniMax's official error catalog.

### 2.7 Prompt caching — automatic (passive)

From <https://platform.minimax.io/docs/api-reference/text-prompt-caching>:

- Supported on **M3, M2.7, M2.5, M2.1** series (passive caching)
- Minimum **512 input tokens** for caching to apply
- **Prefix matching** order: "tool list → system prompts → user messages"
- Cached tokens are billed at a discounted rate (see PayGo table)
- Best practice (per docs): "Place static or repeated content (including tool list, system prompts, user messages) at the beginning of the conversation, and put dynamic user information at the end"
- Worked example in the doc: 50,000 total input, 45,000 cache hits, 5,000 new input, 1,000 output → total $0.0108 vs. $0.0324 without caching = **≈66.7% saving** at M3 standard pricing
- Expiration: "automatically adjusted based on system load"
- Caching still counts toward the 512k / >512k threshold: "long-context pricing applies when input tokens are greater than 512k, including cache-hit tokens"

### 2.8 Prompt caching — explicit (Anthropic API compatible)

From <https://platform.minimax.io/docs/api-reference/anthropic-api-compatible-cache>:

- Available on **M2.7, M2.5, M2.1, M2** series (M3 not listed)
- Set via `cache_control` parameter; first-time cache write incurs an additional charge; hits are discounted
- **Cache lifetime: 5 minutes**, refreshed automatically on hit
- Compatible with Anthropic SDK by setting `ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic`

### 2.8b Known issues / open bug reports

- **Issue MiniMax-AI/MiniMax-M2.7#47** — "remains_time drains passively without API calls + cache-read discount not verifiable in Token Plan Plus". Status: Open. Source: <https://github.com/MiniMax-AI/MiniMax-M2.7/issues/47>

### 2.9 M3 architecture (verifiable technical detail)

- M3 uses **MiniMax Sparse Attention (MSA)** — a sparse attention architecture with an index branch that pre-selects top-K KV blocks before full attention. Source: <https://m.163.com/dy/article/KU5A1I1U05561FZE.html>
- MiniMax publicly attributed M2 using full attention (not Lightning Attention) to an October 2025 technical post: "Why Did M2 End Up as a Full Attention Model?" (mentioned in the same M3 coverage article).
- 1M-token context window (verifiable from launch blog and multiple secondary sources).

### 2.10 Hermes Agent tips relevant to token efficiency

From <https://hermes-agent.nousresearch.com/docs/guides/tips> (Hermes Agent's own documentation, last built 2026):

- "Don't break the prompt cache" — keep system prompt stable; avoid changing model/system prompt mid-session
- "Use /compress before hitting limits" — compresses conversation history
- "Delegate for parallel work" — `delegate_task` runs subagents in parallel, only summaries return to the main context
- "Use execute_code for batch operations" — one script vs. many terminal calls
- "Choose the right model" — use `/model` to switch mid-session
- `/usage` shows per-session consumption; `/insights` shows 30-day patterns
- Memory is bounded: "≈2,200 chars for MEMORY.md, ≈1,375 chars for USER.md"
- Skills system: "if a task takes 5+ steps and you'll do it again, ask the agent to create a skill for it"
- Warning: "Memory is a frozen snapshot — changes made during a session don't appear in the system prompt until the next session starts. The agent writes to disk immediately, but the prompt cache isn't invalidated mid-session."

### 2.11 Cross-vendor industry practice (verifiable)

- "Rate limits (RPM / TPM)" is the standard pattern across OpenAI, Anthropic, Google Gemini, 阿里云通义, ByteDance 豆包, Moonshot. Any one of RPM, TPM, RPD, TPD, IPM, IPD can trigger a 429. Sources:
  - <https://blog.csdn.net/yjw123456/article/details/142305561>
  - <https://www.aliyun.com/sswd/10959449-1.html>
  - <https://new.qq.com/rain/a/20240521A05BK100> (豆包: 10K RPM, 800K TPM for 32K models)
- Common remedies documented across vendors: exponential backoff on 429, honouring `Retry-After`, batching, request-coalescing, multi-key load balancing, prompt caching, prompt compression.

### 2.12 Documented LLM cost-reduction techniques (academic / industry)

- **Prompt caching** — Anthropic, OpenAI, Google, and MiniMax all implement it. Documented savings: 50–90% on input tokens at high cache hit rates. Sources: <https://artificialanalysis.ai/models/caching>, <https://timwappat.info/auto-cache-passively-saves-on-you-ai-model-costs/>, <https://www.answeroverflow.com/m/1469497280133464204>
- **LLMLingua / LLMLingua-2** (Microsoft Research) — prompt compression that "can achieve up to 20× compression ratio with minimal performance loss". Source: <https://www.microsoft.com/en-us/research/project/llmlingua/llmlingua-2/>
- **LLM context compression** — multiple academic approaches including Activation Beacon, "Compressing Context to Enhance Inference Efficiency" (EMNLP 2023). Sources:
  - <https://arxiv.org/abs/2409.01227>
  - <https://doi.org/10.18653/v1/2023.emnlp-main.391>
  - <https://blog.csdn.net/beingstrong/article/details/145289852>
- **Structured output** — "Token Efficiency with Structured Output from Language Models". Source: <https://medium.com/data-science-at-microsofn/token-efficiency-with-structured-output-from-language-models-be2e51d3d9d5>
- **General reduction strategies** (verifiable compilation): optimize prompt length, control response length, cache intelligently, use appropriate model variants, batch operations, use cheaper models for sub-tasks. Source: <https://flowith.io/blog/minimax-api-pricing-tokens-concurrency/>, <https://www.glukhov.org/llm-performance/cost-effective-llm-applications/>

---

## 3. Disputes / competing viewpoints (sources disagree)

- **The weekly quota itself**: Some community posts in 2025/2026 on r/vibecoding and r/MiniMax_AI report the weekly cap as "the old 5-hour limits" being "switched" to weekly. Others note the dual-window (5-hour rolling AND weekly) has been in place since at least early 2026. The official docs explicitly state "5-hour rolling and weekly windows" (not a replacement, but a dual control). Sources: <https://www.reddit.com/r/vibecoding/comments/1rxwua3/minimax_just_switched_from_5hour_resets_to_weekly/>, <https://platform.minimax.io/docs/token-plan/faq#reset-calculation>
- **M3 launch date and Tier3 reorg**: Most sources say M3 launched 2026-06-01, but news articles from the same week use slightly different date stamps (2026-06-01 vs 2026-06-02). The blog post is dated 2026-06-01 per URL slug; Chinese press ran on 2026-06-02. Both consistent.
- **Is M3 "open source"?** — Multiple Chinese outlets (网易, 量子位, 36氪-style coverage) call M3 "开源" (open source). The MiniMax blog (<https://www.minimax.io/blog/minimax-m3>) does not explicitly confirm full open-source licensing in the page title/snippet we have. **To be verified** by checking the model release repo.
- **Caching discount visibility in Token Plan Plus**: Bug report MiniMax-AI/MiniMax-M2.7#47 claims the cache-read discount is "not verifiable in Token Plan Plus" — i.e., the billing display doesn't clearly break out the discounted amount. This is an open issue, not yet a settled finding.

---

## 4. To be verified (no reliable source found in this round)

- **Exact weekly credit allowance per tier** — official docs say "5-hour rolling and weekly windows" but do not publish the numeric per-week credit cap; only the 5-hour window applies visibly to user experience. Some press releases say "5小时用量的 10倍" (10× the 5-hour amount) as the weekly cap, but this is reported in third-party articles, not confirmed in the official FAQ I have.
- **What error code is returned for a true RPM (not TPM) cap hit** — docs list 1002, 2045, 2056 but don't map clearly to RPM vs TPM vs weekly credit exhaustion. To be verified empirically.
- **Whether M3 (vs. M2.7) automatically applies the passive cache, and at what hit rate** — the caching doc lists M3 in the supported models for passive caching, but the explicit `cache_control` Anthropic-style cache is NOT supported on M3 (only on M2.x). Exact implications for M3 callers are not fully detailed in the snippets we have.
- **Specific M3 TPM/RPM under Token Plan Plus** — the public Rate Limits table is at the API-key level, not the Token Plan tier level. Whether the peak-hour "3-4 agents" cap for Plus is enforced at the RPM/TPM level or as an aggregate agent-session counter is **to be verified**.
- **Whether the user's "1 hour of inactivity" was caused by a 429 hit, a Token Plan credit exhaustion, or a peak-hour throttle** — none of the searched sources link a specific incident to the user's experience. The user would need to check their usage bar and 429/2056 error responses.
- **M3 reasoning / "thinking" output tokens** — MiniMax's caching example includes thinking content, and there's an `reasoning_split=True` parameter for OpenAI SDK. How thinking tokens interact with prompt caching, output token pricing, and the TPM cap is **to be verified** beyond what the caching doc shows.

---

## 5. Source URLs (consolidated)

### MiniMax official
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

### MiniMax related press / secondary (Chinese)
- 中证网 Token Plan announcement: <https://www.cs.com.cn/sylm/jsbd/202603/t20260323_6542478.html>
- 顶端新闻 / 新浪科技: <https://www.topnews.cn/news/145CD4EC45BE4B75>
- 网易/智东西 套餐升级: <https://www.163.com/dy/article/KONFAE6L051180F7.html>
- 腾讯网 (腾讯): <https://news.qq.com/rain/a/20260323A059UP00>
- 量子位 M3 实测: <https://m.163.com/dy/article/KUF3V6NG0511DSSR.html>
- 智东西 M3 MSA: <https://m.163.com/dy/article/KU5A1I1U05561FZE.html>
- CSDN (2025 财报): <https://blog.csdn.net/qq_24252865/article/details/159465814>
- 闫俊杰 2026 定调: <https://news.qq.com/rain/a/20260303A004VE00>
- Xiaomi MiMo Token Plan 推出: <https://www.163.com/dy/article/KPJG9QMC0511B8LM.html>
- Xiaomi MiMo 横评: <https://news.qq.com/rain/a/20260406A03TB400>

### Industry context
- Anthropic Claude Code 限速: <https://news.qq.com/rain/a/20250729A023J400>
- 豆包定价/限流: <https://new.qq.com/rain/a/20240521A05BK100>
- Rate-limit 通用处理 (CSDN): <https://blog.csdn.net/yjw123456/article/details/142305561>
- Rate-limit 通用处理 (掘金): <https://juejin.cn/post/7637345418323968052>

### Efficiency research
- LLMLingua-2: <https://www.microsoft.com/en-us/research/project/llmlingua/llmlingua-2/>
- LLMLingua blog: <https://www.microsoft.com/en-us/research/blog/llmlingua-innovating-llm-efficiency-with-prompt-compression/>
- Compressing Context (EMNLP 2023): <https://doi.org/10.18653/v1/2023.emnlp-main.391>
- Prompt Compression paper: <https://arxiv.org/abs/2409.01227>
- Activation Beacon: <https://blog.csdn.net/beingstrong/article/details/145289852>
- Cache savings analysis: <https://artificialanalysis.ai/models/caching>
- Auto cache analysis: <https://timwappat.info/auto-cache-passively-saves-on-you-ai-model-costs/>

### Tooling / community
- Hermes Agent tips: <https://hermes-agent.nousresearch.com/docs/guides/tips>
- MiniMax-M2.7 issue #47: <https://github.com/MiniMax-AI/MiniMax-M2.7/issues/47>
- r/MiniMax_AI weekly limit threads: <https://www.reddit.com/r/vibecoding/comments/1rxwua3/minimax_just_switched_from_5hour_resets_to_weekly/>
- Token Plan overhaul + M3: <https://www.reddit.com/r/MiniMax_AI/comments/1tv58qc/minimax_token_plan_overhaul_m3_release_what_it/>
- M3 launch (r/LocalLLaMA): <https://www.reddit.com/r/LocalLLaMA/comments/1ttdiq0/minimax_m3_coding_agentic_frontier_1m_context/>

### Third-party vendor guides
- Flowith MiniMax API pricing: <https://flowith.io/blog/minimax-api-pricing-tokens-concurrency/>
- Verdent AI M2.5 pricing: <https://www.verdent.ai/guides/minimax-m2-5-pricing>
- Thomas Wiegold M2.7 review: <https://thomas-wiegold.com/blog/minimax-m-2-7-review-is-it-worth-the-hype/>

---

*End of background — facts only. No recommendations, no analysis. Next step (analysis stage) will use this to design a concrete plan.*
