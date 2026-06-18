# Dossier — AI Landscape (Frontier Models, June 2026)

> Living topic file. Built 2026-06-04 for the vault knowledge base buildout. This is the canonical reference for the frontier model landscape — what's released, what's open-weight, who's leading, what's ahead.
>
> **Cross-references:** [`dossiers/ai_agents.md`](ai_agents.md) for harness/runtime patterns wrapping these models · [`dossiers/harness-engineering.md`](harness-engineering.md) for harness engineering details · [`dossiers/free-opensource-stack.md`](free-opensource-stack.md) for open-weight deploy details.

## Why this topic matters to Andre

Andre's fleet — Mavis, Researcher, Verifier, Builder, Scribe, Designer — runs on top of these models. The choice of frontier model, the cost of API calls, the latency of tool use, the context window of long dossiers, the safety profile of agentic execution — all of it flows from this layer. A 3-month-stale landscape dossier is a build-time liability; a fresh one is leverage.

## Current signal (as of 2026-06-04 01:50 CT)

### 1. The 2026 frontier has converged into three clusters

The leading labs have settled into three distinct strategies, and the gap between them is now measurable in *single digits* of intelligence:

1. **Closed-weight frontier (premium, US-led).** OpenAI (GPT-5.5, GPT-5.5 Pro, GPT-5.5 Instant), Anthropic (Claude Opus 4.7/4.8, Sonnet 4.6, Mythos Preview), Google DeepMind (Gemini 3.5 Flash, Gemini 3.1 Pro, Gemini Omni, Gemini 3 Deep Think, Antigravity 2.0). All charge for API access, all gate weights, all run their own agent-runtime platform.
2. **Open-weight frontier (China-led, US/Europe catching up).** DeepSeek V4 Pro/Flash, MiniMax M3, Alibaba Qwen3.6 / Qwen3.7, Moonshot Kimi K2.6, Z.ai GLM-5.1, Xiaomi MiMo-V2.5-Pro, Meta Llama 4 Scout/Maverick. All release weights under Apache 2.0 or similar, all host on Hugging Face, all run on commodity GPUs.
3. **Specialized / vertical.** xAI Grok 4.3 (real-time X integration), Mistral (European-sovereign, on-prem emphasis), Meta Muse Spark (closed, internal to Meta stack, May 2026), Anthropic Mythos Preview (cyber-defensive, restricted access).

The Artificial Analysis Intelligence Index (2026-06-04) ranks the top 10 models within a single point of each other (53–61). The "intelligence gap" is effectively closed at the top; differentiation now happens in *cost, latency, context window, modality, and tool integration*.

### 2. Closed-weight frontier (US): the heavy hitters

**OpenAI — GPT-5.5 family (April 23, 2026).** Codename "Spud," first full re-training since GPT-4.5, three variants (Standard / Thinking / Pro). 1M context window in API; 400K in Codex. $5/M input, $30/M output (Standard); $30/$180 (Pro). Terminal-Bench 2.0 82.7%, GDPval 84.9%, SWE-Bench Pro 58.6%, OSWorld-Verified 78.7%, CyberGym 81.8%, ARC-AGI-2 85.0%. Preparedness Framework High for bio/cyber. Generally available on Microsoft Foundry and AWS Bedrock since June 1, 2026. (src-2026-06-04-001, src-2026-06-04-002, src-2026-06-04-009)

**OpenAI — supporting models.** GPT-5.5 Instant (May 5, updated May 28, 2026) — ChatGPT's default. GPT-5.5 Pro (xhigh reasoning effort) — listed on AA but score not yet published. GPT-Rosalind (Apr 16, 2026) — biodefense research model. Rosalind Biodefense (May 29, 2026) — extended version. Realtime voice models (May 7). Privacy Filter (Apr 22). ChatGPT Images 2.0 (Apr 21). GPT-5.4 (Mar 5, 2026) — predecessor, $2.50/$15.

**Anthropic — Claude Opus 4.6 → 4.7 → 4.8 progression.** Opus 4.6 released ~Feb 5, 2026 (Anthropic's flagship; pricing $15/$75 per M tokens). Opus 4.7 followed within weeks; Opus 4.8 (Adaptive Reasoning, Max Effort) is currently #1 on the Artificial Analysis Intelligence Index at 61. Sonnet 4.6 (Feb 17, 2026) — $3/$15 per M tokens, "approaches Opus-level intelligence" per Anthropic, default in claude.ai and Claude Cowork. Claude 4.5 Haiku still available ($0.82/$4). Claude Sonnet 4.5 deprecation date: Sept 29, 2026.

**Anthropic — Claude Mythos Preview (April 7, 2026).** System card published, but model NOT released publicly — capable enough that Anthropic judged release would create "severe risk to global digital infrastructure." Cybersecurity-frontier model; significantly better at code reasoning and autonomous execution than Opus 4.7. *Glasswing* project uses Mythos Preview with 50 org partners to defend critical systems. Reuters (May 28) reports Anthropic plans "wider release to all customers in the coming weeks." (src-2026-06-04-007, src-2026-06-04-008)

**Google — Gemini 3.5 family + Antigravity 2.0 (May 19, 2026 I/O).** Gemini 3.5 Flash is the new default (replaces 2.x series). Terminal-Bench 2.1 76.2%, GDPval-AA 1656 Elo, ~4x faster than prior 3 Pro. Gemini 3.5 Pro expected June 2026. Gemini 3.1 Pro Preview ranked #5 on AA at 57. Gemini Omni Flash is the multimodal world model. Gemini 3 Deep Think (gold-medal IMO performance, AA score pending). Gemini Spark is the 24/7 personal agent (Ultra plan $100/mo). Antigravity 2.0 is the agent-first dev platform (desktop + CLI + SDK + Managed Agents). Gemini 3.5 Flash (Low) launched May 26 to address Antigravity token consumption complaints — ~45% fewer tokens than Medium. (src-2026-06-04-004, src-2026-06-04-005, src-2026-06-04-006)

### 3. Open-weight frontier (China, US, Europe)

**DeepSeek V4 (April 24, 2026).** V4-Pro and V4-Flash both available via OpenAI ChatCompletions interface. V4 Pro is AA-ranked #15 at 52 ($0.18/M blended). 1M context, "cost-effective 1M context era" framing. "Engram memory architecture" — DeepSeek's bet on long-term memory. V3.2-Speciale (high-compute reasoning) and V3 (Dec 2024, 671B MoE) remain in use.

**Alibaba Qwen — Qwen3.6 (April 16, 2026) + Qwen3.7-Plus (May 31, 2026).** Qwen3.6-35B-A3B is sparse MoE (35B total, 3B active). Qwen3.7-Plus is the multimodal agent model (vision + language unified). Qwen3.7 Max AA score 57. Qwen3.6 Plus 50. Qwen3-Coder (Jul 2025) — SWE-Bench matched Claude 4, beat GPT-4.1. Qwen3.6-Max-Preview (Apr 20, 2026) — first Qwen flagship with NO public weights. Hugging Face downloads >300M cumulative.

**Moonshot Kimi K2.6 (April 21, 2026).** #1 open-weights model on Artificial Analysis at 54. 1T total params, 32B active, 262K context, MoE. "Agent Swarm" architecture supports 300 parallel subagents and 4,000 collaborative steps. SWE-Bench Pro 58.6% (matches GPT-5.5, beats Opus 4.6). $0.70/M blended — 1/8 the cost of Opus. K2.5 (Jan 27, 2026) deprecated May 25, 2026.

**Z.ai / Zhipu GLM-5.1 (March 27, 2026).** Open-source. 744B total params, 28.5T training tokens, integrated DeepSeek Sparse Attention (DSA), async RL framework "Slime." SWE-bench Verified 77.8. AA Intelligence Index 51. Long-running agents (>24h continuous, 700+ tool calls). $0.14 per coding task. Reaches "94.6% of Claude Opus 4.6 coding performance" per third-party testing. GLM-5.1 is the iterative improvement; GLM-5-Turbo is the production cheap variant.

**MiniMax — M3 (June 1, 2026) / M2.7 (March 18, 2026).** M3 is the latest M-series — agentic reasoning, tool use, coding, multimodal chat input, long-context tasks. Introduces **MSA (MiniMax Sparse Attention)** — 15.6x long-context response speed boost over M2. M3 ranked #10 on Artificial Analysis at 55 (1M context, $0.30/M blended). M2.7 ranked #21 at 50 ($0.22/M). M2.5 (Feb 2026), M2.1 (Dec 22, 2025), M2 (Oct 27, 2025) form the older generation. "Recursive self-improvement" framing per the M2.7 launch. (src-2026-06-04-013, src-2026-06-04-014, src-2026-06-04-015)

**Meta — Llama 4 (Apr 2025) + Muse Spark (May 2026).** Llama 4 Scout (109B/17B active, 16 experts, 10M context — *largest open-weight context window*). Llama 4 Maverick (400B/17B active, 128 experts, 1M context). Both natively multimodal. AA Intelligence Index: Scout 14, Maverick 18 — *far below Chinese open-weight peers*. Meta announced May 2026 that AI strategy shifts to closed-weight *Muse Spark* (AA score 52); Llama enters "maintenance mode." This is a structural shift in the open-weight landscape.

**Xiaomi MiMo-V2.5-Pro.** 1M context, AA score 54, $0.18/M blended. Tied with Kimi K2.6 as #2 open-weight on AA.

**xAI Grok 4.3 (May 4, 2026).** 1M context, AA score 53, $0.64/M blended. Grok 4.3 high/medium/low reasoning variants. Grok Build (coding agent, beta, May 25, 2026) — terminal-based. Grok 5 (10T params) in training on Colossus 2; xAI $20B Series E funding. Grok 4-1-fast-reasoning and grok-4-1-fast-non-reasoning retired May 15, 2026.

**Mistral.** Mistral Large 3 (AA 23, $0.60/M). Mistral Medium 3.5 (AA 39, $2.10/M). Codestral (22B, code-gen). Devstral 2 (AA 22, $0.005/M — *cheapest coding-tuned model*). Magistral Medium 1.2. European-sovereign positioning; many on-prem deployments.

**StepFun Step 3.7 Flash.** 256K context, AA 43, $0.18/M, 415.9 t/s (second-fastest after Mercury 2). Step 3.5 Flash 2603, Step 3 VL 10B.

**Other notable open-weight.** Cohere Command A+ (AA 37, $0.002/M — cheapest in tier). IBM Granite 4.1 (8B-30B). Amazon Nova 2.0 Lite/Pro/Omni (1M context, multimodal). Microsoft Phi-4. Liquid LFM2 (small/edge-tuned). Baidu ERNIE 5.0 Thinking Preview. ByteDance Doubao Seed Code. NVIDIA Nemotron 3 Super / Nano. Tencent Hy3. Inclusion Ring-2.6-1T. China Mobile JT-35B-Flash. AI21 Jamba 1.7. Upstage Solar Pro 3. Sarvam 105B. Inception Mercury 2 (fastest model on AA at 932 t/s). LG EXAONE 4.5. Korea Telecom Mi:dm K 2.5 Pro. Liquid LFM2.5-Thinking.

### 4. The Artificial Analysis Intelligence Index — the canonical benchmark (June 4, 2026)

The single best snapshot of the landscape. 373 models ranked, 228 open-weight. Top 10 (out of 373):

| # | Model | Score | Context | $/M blended | Type |
|---|-------|-------|---------|-------------|------|
| 1 | Claude Opus 4.8 (max effort) | 61 | 1M | $4.10 | Closed |
| 2 | GPT-5.5 (xhigh) | 60 | 922K | $4.35 | Closed |
| 3 | GPT-5.5 (high) | 59 | 922K | $4.35 | Closed |
| 4 | Claude Opus 4.7 (max) | 57 | 1M | $4.10 | Closed |
| 5 | Gemini 3.1 Pro Preview | 57 | 1M | $1.74 | Closed |
| 6 | GPT-5.5 (medium) | 57 | 922K | $4.35 | Closed |
| 7 | Qwen3.7 Max | 57 | 1M | $1.43 | Open |
| 8 | Gemini 3.5 Flash | 55 | 1M | $1.31 | Closed |
| 9 | Gemini 3.5 Flash (medium) | 55 | 1M | $1.31 | Closed |
| 10 | **MiniMax M3** | 55 | 1M | $0.30 | **Open** |

The top open-weights models (out of 228):
| # | Model | Score | Context | $/M blended |
|---|-------|-------|---------|-------------|
| 1 (overall #11) | Kimi K2.6 | 54 | 256K | $0.70 |
| 1 (overall #11) | MiMo-V2.5-Pro | 54 | 1M | $0.18 |
| 3 (overall #15) | DeepSeek V4 Pro (max) | 52 | 1M | $0.18 |
| 6 (overall #21) | **MiniMax M2.7** | 50 | 205K | $0.22 |

(src-2026-06-04-016)

### 5. Stanford HAI AI Index 2026 — the macro picture

The 2026 AI Index (Stanford HAI, published Q1 2026) reports:

- **U.S.-China performance gap is effectively closed.** As of March 2026, Anthropic's top model leads DeepSeek-R1 by just 2.7%. The U.S. still produces more top-tier models and higher-impact patents; China leads in publication volume, citations, patent output, and industrial robot installations.
- **SWE-Bench Verified rose from 60% to near 100% in a single year.**
- **AI agents went from 12% to ~66% task success on OSWorld (real computer tasks).**
- **Generative AI reached 53% population adoption within three years** — faster than the PC or the internet.
- **Industry produced 90%+ of notable frontier models in 2025.**
- **Documented AI incidents rose to 362, up from 233 in 2024.**
- **Gemini Deep Think won gold at IMO, but reads analog clocks correctly only 50.1% of the time** — the "jagged frontier."
- **TSMC fabricates almost every leading AI chip** — supply chain concentrated in Taiwan.
- **U.S. private AI investment $285.9B in 2025**, 23x China's $12.4B.
- **AI researchers migrating to the U.S. dropped 89% since 2017**, 80% decline in the last year alone.
- **Singapore 61% adoption, UAE 54%, U.S. 28.3%** — the U.S. ranks 24th in population adoption.

(src-2026-06-04-017)

### 6. The pricing collapse of 2025-2026

The economic story underneath the technical story: frontier intelligence is now cheap. Same-tier intelligence that cost $15/M input in 2024 is now $0.18/M (DeepSeek V4 Pro, MiMo-V2.5-Pro, DeepSeek V4 Flash). The "intelligence per dollar" curve is bending faster than Moore's law:

- **GPT-5.5 ($4.35/M)** at AA 60 vs **DeepSeek V4 Flash ($0.06/M)** at AA 47. Roughly 70x cost ratio for 28% less intelligence.
- **Claude Opus 4.8 ($4.10/M)** at AA 61 vs **Qwen3.5 0.8B ($0.01/M)** at AA 10. The high end and the floor are both alive.
- **The cheap-coding tier:** Devstral 2 ($0.005/M), Qwen3.5 0.8B ($0.01/M), Gemma 3n E4B ($0.02/M) — frontier-era intelligence at sub-penny pricing for the right workloads.

The implication: the *binding constraint* on AI deployment is no longer intelligence, cost, or context window. It's *verification, integration, and productization*. The model layer is a commodity; the harness layer is the moat.

## Source trail

See `knowledge/sources.jsonl`. Key primary sources for this dossier (all fetched 2026-06-04 01:45-01:55 CT):

- `src-2026-06-04-001` OpenAI: "Introducing GPT-5.5" (openai.com) — weight 0.95
- `src-2026-06-04-002` GPT-5.5 Wikipedia canonical — weight 0.85
- `src-2026-06-04-003` AWS Bedrock OpenAI frontier models — weight 0.85
- `src-2026-06-04-004` Google blog: "I/O 2026 developer highlights: Antigravity, Gemini API, AI Studio" (blog.google) — weight 0.9
- `src-2026-06-04-005` Anthropic: "Claude Sonnet 4.6" (anthropic.com) — weight 0.95
- `src-2026-06-04-006` Anthropic: "Introducing Claude Opus 4.6" (anthropic.com) — weight 0.95
- `src-2026-06-04-007` Anthropic: "Claude Mythos Preview System Card" (anthropic.com PDF) — weight 0.95
- `src-2026-06-04-008` Reuters/Anthropic: Mythos wider-release plans (forbes.com/secondary) — weight 0.75
- `src-2026-06-04-009` Microsoft Azure: "OpenAI's GPT-5.5 in Microsoft Foundry" (azure.microsoft.com) — weight 0.9
- `src-2026-06-04-010` Meta AI: "The Llama 4 herd" (ai.meta.com) — weight 0.95
- `src-2026-06-04-011` Meta Llama (llama.com) — weight 0.85
- `src-2026-06-04-012` Mistral: "Frontier AI LLMs, assistants, agents, services" (mistral.ai) — weight 0.9
- `src-2026-06-04-013` MiniMax: Models release notes (platform.minimax.io) — weight 0.95
- `src-2026-06-04-014` MiniMax: M2.7 announcement (minimax.io) — weight 0.85
- `src-2026-06-04-015` VentureBeat: "MiniMax teases M3 sparse attention mechanism" (venturebeat.com) — weight 0.85
- `src-2026-06-04-016` Artificial Analysis: LLM Leaderboard (artificialanalysis.ai) — weight 0.95
- `src-2026-06-04-017` Stanford HAI: 2026 AI Index Report (hai.stanford.edu) — weight 0.95
- `src-2026-06-04-018` DeepSeek: V4 Preview Release (api-docs.deepseek.com) — weight 0.95
- `src-2026-06-04-019` xAI News (x.ai) — weight 0.9
- `src-2026-06-04-020` xAI: Grok Model Retirement (docs.x.ai) — weight 0.9
- `src-2026-06-04-021` Z.ai: "GLM-5: From Vibe Coding to Agentic Engineering" (z.ai/blog) — weight 0.9
- `src-2026-06-04-022` Alibaba Tongyi: Qwen3 launch (ehangzhou.gov.cn + Wikipedia) — weight 0.9
- `src-2026-06-04-023` Qwen 3.7-Plus release (qwen.ai) — weight 0.9
- `src-2026-06-04-024` Moonshot AI: Kimi K2.6 release (moonshot.ai + China Youth Intl) — weight 0.85
- `src-2026-06-04-025` Wikipedia: Qwen (en.wikipedia.org) — weight 0.85
- `src-2026-06-04-026` Wikipedia: GPT-5.5 (en.wikipedia.org) — weight 0.85
- `src-2026-06-04-027` Hidekazu Konishi: Anthropic Claude Model Release Timeline (hidekazu-konishi.com) — weight 0.8
- `src-2026-06-04-028` Anthropic Transparency Hub (anthropic.com/transparency) — weight 0.9
- `src-2026-06-04-029` Caixin Global: GLM-5 launch (caixinglobal.com) — weight 0.8
- `src-2026-06-04-030` OpenAI: Help Center Model Release Notes (help.openai.com) — weight 0.9
- `src-2026-06-04-031` Yicai Global: Qwen3-Coder launch (yicaiglobal.com) — weight 0.8
- `src-2026-06-04-032` Stanford HAI 2026 AI Index (top takeaways) (hai.stanford.edu) — weight 0.95
- `src-2026-06-04-033` MindStudio: xAI Grok Roadmap (mindstudio.ai) — weight 0.7 (secondary, no primary)
- `src-2026-06-04-034` OpenAI Research Index (openai.com/research/index/release) — weight 0.9

## Contradictions and open questions

- **GPT-6 rumor (fnd-2026-06-02-026):** A Chinese SEO site (geo.fkw.com) claims OpenAI released GPT-6 on Apr 14, 2026 with 2M context and "Symphony" architecture. **Contradicted by OpenAI's own research index** (src-2026-06-04-034) which shows GPT-5.5 (Apr 23) as the latest frontier, with no GPT-6 announcement. This is the same fnd-2026-06-02-026 from the ai_agents dossier, still routed to verification.
- **Anthropic Mythos release timing** — Reuters (May 28) reports "wider release to all customers in the coming weeks." As of June 4, 2026, no general-availability announcement. Watch.
- **Meta Muse Spark vs Llama 4:** Meta announced Muse Spark as the closed-weight shift in May 2026. AA shows Muse Spark at score 52. Llama 4 Scout/Maverick remain open-weight but at AA 14/18 — far below the Chinese open-weight frontier. **Implication:** Meta is exiting the frontier open-weight race, not just pausing. Watch.
- **Anthropic 2026 deprecation timeline:** Claude Sonnet 4.5 deprecates Sept 29, 2026. Claude Sonnet 4 and Opus 4 deprecate June 15, 2026 (already passed). Migration paths required.
- **Open question — what is MiniMax M3's true positioning?** M3's 1M context, MSA sparse attention, AA score 55 at $0.30/M is highly competitive — *cheaper than every closed-weight peer except Gemini 3.5 Flash*, intelligence-comparable. The "self-evolution" framing (recursive self-improvement via the M-series) is the differentiator. Andre's fleet already runs on M-series (per Researcher config.yaml). Worth a follow-up question to Mavis: should the fleet standardize on M3 for low-cost tiers, MiniMax-M2.7 for high-speed, M3 with MSA for long-context?
- **Open question — the open-weight model is a real moat for Andre's stack.** The pricing collapse means Andre can run a research-tier model at $0.06-$0.30/M (DeepSeek V4 Flash, Kimi K2.6, M2.7, MiMo-V2.5) instead of $4/M (Opus 4.8). For high-volume workers (Verifier, Scribe, Builder), the cost difference is 10-50x. **Recommendation:** for non-frontier workloads, default to open-weight; reserve Opus 4.8/GPT-5.5/Gemini 3.1 for tasks where the +5-10% intelligence actually matters.
- **Re-verification watch — clm-2026-06-04-XXX (Claude Mythos capabilities):** Mythos Preview's specific capability claims (cyber-defensive, "automatically develop professional-grade cyberattack methods") come from a single primary source (src-2026-06-04-007, Anthropic's own system card). Cross-check against the Reuters/Forbes secondary, the Appwrite analysis, the WaveSpeed blog. **No contradiction found in this cycle, but the claim is load-bearing for the "AI safety gap" thesis** — flag for second-source on the next REFRESH.

## Implications

- **Build:** Andre's workers should default to **open-weight for non-frontier tasks**. The cost collapse is a 10-50x lever. M2.7 ($0.22/M) for fast coding, Kimi K2.6 ($0.70/M) for high-IQ open-weight, DeepSeek V4 Pro ($0.18/M) for 1M-context long-document work. Reserve Opus 4.8 ($4.10/M) for tasks where the +5% intelligence is the differentiator (e.g., the Verifier's hardest rubric calls). Mid-priority for the Hermes handoff.
- **Build:** the M3 sparse-attention (MSA) mechanism is the most interesting recent architectural bet — 15.6x long-context response speed boost. If the Verifier or Researcher uses M3 for long-context dossiers, the speedup compounds. Worth a downstream cross-check on the `dossiers/agent-engineering.md` file.
- **Content:** the "intelligence gap is closed" thesis is the strongest single claim for the daily-brief. The Stanford HAI framing + the AA leaderboard data triangulate: frontier intelligence is now a commodity; the moat is verification, integration, productization. This is the Scribe's strongest available frame.
- **Watch:** Claude Mythos wider release (Reuters: "coming weeks"), Meta Muse Spark development (closed-weight bet), Daybreak (OpenAI cyber), Anthropic's "Versept" acquisition rumor (still uncorroborated), GPT-5.6 canary.
- **Verify:** fnd-2026-06-02-026 (GPT-6 rumor) — same as ai_agents dossier. Cross-source watch on Mythos capabilities (see above).

## Routing history

| Date | Routed to | Item | Outcome |
|------|-----------|------|---------|
| 2026-06-04 | queue/mavis-handoff.md | dossier ready for consumption | Pending |
| 2026-06-04 | knowledge/sources.jsonl | src-2026-06-04-001 through src-2026-06-04-034 | Appended |

---

*This dossier is durable. It accumulates. It is the model-layer foundation that the harness-engineering and agent-engineering dossiers build on. When Mavis asks "what's the latest on X?" — this is the first file to check.*
