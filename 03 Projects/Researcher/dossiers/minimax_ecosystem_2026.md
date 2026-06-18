# Dossier — MiniMax Ecosystem (Mid-2026)

> Living topic file. Built 2026-06-05 for Operation: Cognitive Architecture Phase 1+. Canonical reference for the MiniMax stack as it stands today: M3, M2.7, the Mavis (formerly MiniMax Agent) framework, and the macOS Desktop App. The intelligence here is the input for the Phase 3 Mavis Blueprint.
>
> **Cross-references:** [`dossiers/ai-landscape.md`](ai-landscape.md) (frontier model positioning) · [`dossiers/frontier_ai.md`](frontier_ai.md) (model release timeline) · [`dossiers/harness-engineering.md`](harness-engineering.md) (harness pattern, to be extended by Phase 2) · [`dossiers/memory_orchestration.md`](memory_orchestration.md) (memory architecture, to be extended by Phase 2)

## Why this topic matters to Andre

Andre's stack is MiniMax-native. M3 launched 2026-06-01 with the **MSA (MiniMax Sparse Attention)** architecture and a 1M-token context — a step-change for vault-scale context work. The Mavis agent framework (formerly MiniMax Agent, renamed 2026-05-13) is MiniMax's native answer to multi-agent orchestration, and the Leader/Worker/Verifier architecture is structurally identical to the Producer → Trust loop Andre has been building with `mavis-team`. The macOS Desktop App is the OS-integration surface: Computer Use, Pocket (IM relay), local file system, the Mavis CLI. Every Phase 3 design decision in the Mavis Blueprint draws on this dossier.

## Current signal (as of 2026-06-05 18:50 CT)

### 1. MiniMax M3 — the 1M-context open-weight flagship (released 2026-06-01)

**Headline:** First open-weights model to combine frontier coding + 1M context + native multimodality + desktop operation. Trades blows with Opus 4.7 on coding while costing ~5-10% of the API price. (src-2026-06-05-001, src-2026-06-05-002, src-2026-06-05-003)

**Architecture — MSA (MiniMax Sparse Attention).** Self-developed; not DSA, not MoBA. KV-block aggregation with query-hit gating, "访存比 Flash-sparse-attention 快4倍." The 1M context window is the structural anchor; MSA makes it economically viable. (src-2026-06-05-001, src-2026-06-05-004)

**Speed claims (per MiniMax's technical report):**
- At 1M context: **9.7x prefill speedup**, **15.6x decode speedup** vs full-attention M2.
- Throughput: **400 TPS** claim circulates in secondary press (php.cn, IT之家) but is **NOT confirmed in any accessible primary source** (MiniMax technical blog, OpenRouter, Ollama, rate limits page all silent on TPS as of 2026-06-05). **UNVERIFIED — NOT SAFE FOR PRODUCTION ROUTING.** Third-party benchmarks (lushbinary, datacamp, YouTube) report "excellent inference latency" qualitatively but no hard TPS numbers. (src-2026-06-05-001, src-2026-06-05-005, src-2026-06-05-006)

**Sizing & cost (M3):**
- Sparse MoE: **196B total / 11B active** parameter count circulates in secondary press but is **NOT confirmed in any accessible primary source** (MiniMax official blog, OpenRouter, Ollama all silent on model size as of 2026-06-05). **UNVERIFIED — MoE efficiency framing (11/196 = 5.6% active) pending primary confirmation.** (src-2026-06-05-007, src-2026-06-05-008)
- Context: **1M tokens API, 512K guaranteed minimum** (per Ollama spec). (src-2026-06-05-007, src-2026-06-05-008)
- Pricing (OpenRouter / pricepertoken): **$0.30/M input, $1.20/M output** blended. (src-2026-06-05-009, src-2026-06-05-010)

**Benchmarks (vs the frontier, 2026-06-04 snapshot):**

| Benchmark | M3 | Opus 4.7 | GPT-5.5 | Gemini 3.1 Pro |
|---|---|---|---|---|
| SWE-Bench Pro | **59.0%** | 60.2% | 57.3% | 56.8% |
| Terminal Bench 2.1 | **66.0%** | 62.3% | — | — |
| KernelBench Hard | **28.8%** | (lower) | — | — |
| BrowseComp | **83.5%** | (lower) | — | — |
| SVG-Bench | **wins** | loses | — | — |
| OmniDocBench | wins | — | — | loses |
| Claw-Eval (agent E2E) | **highest** | — | — | — |
| PostTrainBench | 0.37 | 0.42 | 0.39 | — |

(All from src-2026-06-05-001, src-2026-06-05-002, src-2026-06-05-005, src-2026-06-05-011, src-2026-06-05-012)

**Methodology footnote (load-bearing).** Per AIDeepDive / TMTPost (src-2026-06-05-013, src-2026-06-05-014): Terminal Bench 2, VIBE-Pro, and SWE-Bench tests used **Claude Code as the scaffolding** to evaluate M3. This is industry-standard for agent benchmarks (Claude Code, OpenCode, Hermes all serve as common scaffolds), and MiniMax disclosed this openly. The "M3 beats Opus 4.7" claim is therefore not strictly apples-to-apples — the *scaffolding* gives the model a Claude Code-shaped tool environment. Cross-source check confirms this is normal practice, not cherry-picking.

**Long-horizon capability demonstrations (the most interesting capability claims):**
- **PostTrainBench (12h autonomous):** M3 trained 4 models from pretrained bases in 12 hours, zero human intervention, full closed loop (data synthesis → training → eval → iteration). Final score 0.37 vs GPT-5.5 0.39 and Opus 4.7 0.42. (src-2026-06-05-015)
- **CUDA kernel optimization (24h, 1959 tool calls):** M3 optimized a Hopper FP8 kernel, took hardware utilization from 7.6% → 71.3%, **9.4x speedup**, sustained across 147 benchmark submissions. (src-2026-06-05-001, src-2026-06-05-015)
- **Implication:** M3 holds a context, a plan, and a tool loop for hours without drift. The MSA + 1M context is what makes this economically tractable. For a vault-scaling Mavis, this is the relevant capability — not just the SWE-bench scores.

**Native multimodality:** Image + video input. Can **operate the computer desktop** (the Mavis Computer Use module). First open-weight model with all three (long context + multimodality + desktop operation). (src-2026-06-05-001, src-2026-06-05-002)

**Open weights:** Announced 2026-06-01 for release "in 10 days" (~2026-06-11). As of 2026-06-05, weights not yet on HuggingFace. **UNVERIFIED** for self-hosting.

**Compatibility:** M3 is compatible with **Claude Code** and the **MCP protocol**, supports cloud + local deploy. (src-2026-06-05-001, src-2026-06-05-002)

### 2. M3 vs M2.7 — the model routing question

**M2.7 (released 2026-03-18, AA Intelligence Index 50, $0.22/M blended):**
- Sparse MoE: **230B total / 10B active**
- SWE-Pro **56.22%**, VIBE-Pro **55.6%**, Terminal Bench 2 **57.0%**, GDPval-AA 1495 ELO, Toolathon 46.3%
- SWE-Bench Verified 78% (per Thomas Wiegold), BrowseComp 76.3% (per datacamp / M2.5 lineage)
- 100 TPS throughput
- Self-evolution framing; M2.7 open-sourced 2026-03 (src-2026-06-05-016, src-2026-06-05-017, src-2026-06-05-018)

**The delta, M2.7 → M3:** +2.78 pts SWE-Pro, +8 pts Terminal Bench, ~3x throughput, 4x context (262K → 1M), native multimodality, Computer Use. For ~36% more input cost ($0.22 → $0.30).

**Routing decision (per Andre's directive 2026-06-05):**
- **Workers (Researcher, Verifier, Builder, Scribe, Coder)** → M2.7 for read/structure/cite work. The M2.7 IQ is sufficient; the cost savings compound at fleet scale.
- **Chief (Mavis)** → M3 for synthesis, design, and trust-loop verdicts. The M3 IQ matters when the verdict is load-bearing.
- **Long-horizon workers (PostTrainBench-style 12-24h tasks)** → M3 mandatory. M2.7 has not been shown to hold context + plan + tool loop at the same scale.

**Token Plan economics (the multiplier reality, 2026-06-05 announcement):**
- M3 verified base rates: **$0.30/M input, $1.20/M output** (confirmed in OpenRouter, pricepertoken, MiniMax rate limits page). (src-2026-06-05-009, src-2026-06-05-010, src-2026-06-05-022)
- M3 multiplier claims (1.3x input rate, 1.8x output rate, 0.2 token/char system-prompt surcharge): **UNVERIFIED in official MiniMax platform documentation.** The Token Plan FAQ (src-2026-06-05-021) and Rate Limits page (src-2026-06-05-022) contain no multiplier language. Secondary press (php.cn, IT之家) reports these figures but no primary source confirms them as of 2026-06-05. **NOT SAFE FOR PRODUCTION TOKEN ACCOUNTING** — apply only verified base rates until primary confirmation.
- Real-world M3 token consumption ~40% higher than M2.5 for similar tasks. (src-2026-06-05-019, src-2026-06-05-020) **UNVERIFIED** — pending confirmation against primary source.
- 5-hour rolling windows; dynamic rate limiting during peak (MiniMax Token Plan FAQ). (src-2026-06-05-021, src-2026-06-05-022)
- The June 5 announcement was an apology ("改用 Token 计费致歉") — MiniMax walked back the most aggressive limits, gave 3.22-pre subscribers no weekly cap, +50% weekly cap for current subscribers. **This is the political context for our rate-limit incident: MiniMax is mid-rollout, limits are still being tuned.** (src-2026-06-05-023, src-2026-06-05-024)

**Critical implementation note:** SDK `total_tokens` field does NOT include the multipliers. The Mavis harness's token accounting must apply the 1.3x/1.8x/0.2 surcharge **after** the API response, not trust the SDK's number. **UNVERIFIED in our harness** — needs a test fixture.

### 3. The Mavis Agent Framework — MiniMax's native multi-agent orchestration (renamed 2026-05-13)

**The big find.** On 2026-05-13, MiniMax renamed its desktop Agent product to **Mavis (MiniMax as a Jarvis)** and launched the **Agent Teams** feature. The architecture is **Leader / Worker / Verifier** — three roles, code-driven state machine runtime, with "Team Engine" as the infrastructure name. Multiple independent launch-day Chinese press sources (腾讯新闻, 网易, 硅星Breaknews, 爱范儿, all 2026-05-13/14) confirm Leader as the canonical term. The primary technical blog (minimaxi.com/blog/minimax-agent-team-long-running, src-2026-06-05-028) returned 404 at verification time and could not be checked directly. (src-2026-06-05-025, src-2026-06-05-026, src-2026-06-05-027)

**Why this matters for Andre's stack:** the Leader/Worker/Verifier pattern is **structurally identical to the Producer → Trust loop** that `mavis-team` already implements. This is not coincidence — it's the canonical multi-agent pattern that works at scale. The MiniMax team published a deep justification for why role-based Play (prompt-driven role play) doesn't work for long-horizon tasks, and why a code-driven state machine is required. (src-2026-06-05-028, src-2026-06-05-029)

**MiniMax's published rationale (translated to engineering):**
1. Single agents fail on long tasks in four distinct ways: (a) stop mid-task without being told to, (b) drift as context grows, (c) block the user when running in IM, (d) can't be specialized for coding/docs/research in the same loop. These are the same failure modes Andre's mavis-team already encodes against. (src-2026-06-05-028)
2. Prompt-driven role play ("you are the leader, you are the worker") collapses at 5-10 minute horizon. The roles get confused; the agents "媾和" (literally "have sex" — Chinese-language metaphor for colluding into agreement, losing the adversarial dynamic). Code-driven state machines are required to keep the roles distinct. (src-2026-06-05-028, src-2026-06-05-029)
3. The runtime is **deterministic**: a code state machine, not a prompt orchestrator. The Mavis CLI is at `platform.minimax.io/docs/token-plan/minimax-cli`. (src-2026-06-05-030)
4. "Immediate response + background execution" separation — the chief returns control to the user instantly while workers continue in the background. This is exactly what `mavis-team`'s `cycle` model does.

**Subscription changes:** TokenPlan + AgentPlan merged (2026-05-13). One subscription = CLI + API + Agent access, all models, cross-end credits. (src-2026-06-05-025, src-2026-06-05-031)

**The comparison to other frameworks (the "三省六部" framing, 三省 = three departments, 六部 = six ministries — Tang-dynasty bureaucracy metaphor):**
- **vs OpenAI Agents SDK / handoffs:** OpenAI uses explicit handoff; Mavis uses implicit ownership + verifier gate. Mavis's verifier is mandatory; OpenAI's is optional.
- **vs LangGraph:** LangGraph is a graph-DSL for orchestration; Mavis is a fixed 3-role topology. Mavis is less flexible; LangGraph is more flexible. Mavis wins on out-of-the-box correctness; LangGraph wins on bespoke workflows.
- **vs Claude Code Teams (Lead-Teammate):** Most similar in spirit. Both are role-based with state-machine runtime. Mavis is the open-weight-native answer.

**Implication for the Mavis Blueprint:** we should NOT try to build our own Leader/Worker/Verifier runtime. We should adopt Mavis's Team Engine as the orchestration substrate. The M3 + Mavis + Computer Use combination is the integrated OS-integration stack Andre is moving toward.

### 4. MiniMax macOS Desktop App — the OS-integration surface

**Distribution:** "MiniMax - Your AI Agent" on the Mac App Store (id6742651446). Also web (chat.minimaxi.com), developer console (platform.minimax.io), Mavis CLI (`MiniMax CLI` at platform.minimax.io/docs/token-plan/minimax-cli). Cross-platform: Windows, macOS, Linux. (src-2026-06-05-032, src-2026-06-05-033)

**Capabilities (confirmed from changelog + product pages + 凤凰网 Pock et al. articles):**
- **Local file system access:** Custom work path; agent reads, parses, and batch-operates files in the user-specified directory. (src-2026-06-05-034, src-2026-06-05-035)
- **Terminal execution:** Agent can write and execute scripts (timed tasks, automation). The Mavis CLI is the dedicated terminal surface. (src-2026-06-05-030, src-2026-06-05-034)
- **Computer Use:** Mouse + keyboard + screen capture. Drives any GUI app — local design tools, internal report systems, multi-app workflows. Released 2026-04-14 alongside Pocket. (src-2026-06-05-035)
- **Pocket (2026-04-14):** IM relay to Feishu (Lark), WeChat, WeCom (企业微信), Slack. User issues a task from IM, agent executes on their Mac, returns result to the IM thread. (src-2026-06-05-035)
- **Experts (用户-defined 专家智能体):** Vertical-domain agents, configurable tool permissions. Community-shared Experts marketplace. (src-2026-06-05-034)
- **Web automation:** Page navigation, element clicks, form submission, multi-step flows.
- **Long-context understanding** for large file sets and complex business logic.

**The permission system (from changelog 2026-05-13):** "Fixed permission system not handling file deletions correctly in full-authorize mode." This is a tell — the permission system has a "full-authorize mode" that grants broader file system access, and edge cases (specifically file *deletions*) are still being patched. **Implication for the Mavis Blueprint: we should NOT trust full-authorize mode for production workflows. Scope the file system access narrowly.** (src-2026-06-05-036)

**REST API hooks:** **UNVERIFIED — no public docs found for a localhost REST endpoint.** The Mavis CLI is the documented programmatic surface. If a localhost REST API exists, it's internal/unpublished as of 2026-06-05. (gap to fill in Phase 3)

**Cloud vs Desktop capability delta:**
| Capability | Cloud API | Desktop App |
|---|---|---|
| Chat, tool use, file I/O | ✓ | ✓ |
| Local file system | ✗ | ✓ (scoped) |
| Terminal execution | ✗ | ✓ |
| Computer Use (mouse/keyboard) | ✗ | ✓ |
| Pocket (IM relay) | ✗ | ✓ |
| Mavis Teams (multi-agent) | ✗ | ✓ |
| Mavis CLI | n/a | ✓ |
| Local REST API | n/a | **UNVERIFIED** |

The desktop app is the OS-integration surface. The cloud API is the inference surface. They are NOT equivalent; the desktop app is the strategically important target for Phase 3.

## Source trail

All sources accessed 2026-06-05. Trust weights 0.7-0.95.

- `src-2026-06-05-001` MiniMax M3 official launch blog (minimaxi.com/blog/minimax-m3) — 0.95
- `src-2026-06-05-002` Beijing Business Today M3 launch coverage (bbtnews.com.cn) — 0.9
- `src-2026-06-05-003` VentureBeat: MiniMax-M3 cost framing (venturebeat.com) — 0.85
- `src-2026-06-05-004` MSA technical report excerpts (腾讯/网易 summary) — 0.8
- `src-2026-06-05-005` Lushbinary M3 developer guide (lushbinary.com) — 0.8
- `src-2026-06-05-006` DataCamp M3 tutorial (datacamp.com) — 0.8
- `src-2026-06-05-007` Ollama M3 spec (ollama.com/library/minimax-m3) — 0.85
- `src-2026-06-05-008` 腾讯网 M3 1M context (news.qq.com) — 0.85
- `src-2026-06-05-009` OpenRouter M3 pricing (openrouter.ai/minimax/minimax-m3) — 0.9
- `src-2026-06-05-010` pricepertoken M3 pricing (pricepertoken.com) — 0.75
- `src-2026-06-05-011` OpenRouter M3 benchmarks (openrouter.ai/.../benchmarks) — 0.9
- `src-2026-06-05-012` php.cn SWE-Bench Pro detailed comparison (php.cn/faq/2585477.html) — 0.7
- `src-2026-06-05-013` AIDeepDive / TMTPost: M3 "指标很强,但社区炒翻了" (tmtpost.com/8011839.html) — 0.85
- `src-2026-06-05-014` 网易/今日头条 same article (163.com/dy/article/KUG2JD3205118O92.html) — 0.8
- `src-2026-06-05-015` 智东西 / 163 M3 long-horizon demos (163.com/news/a/KUBGGBRS051180F7.html) — 0.85
- `src-2026-06-05-016` NVIDIA NGC catalog M2.7 (catalog.ngc.nvidia.com) — 0.9
- `src-2026-06-05-017` Unsloth M2.7 tutorial (unsloth.ai/docs/models/tutorials/minimax-m27) — 0.85
- `src-2026-06-05-018` Thomas Wiegold M2.7 review (thomas-wiegold.com) — 0.7
- `src-2026-06-05-019` php.cn M3 token multiplier (php.cn/faq/2599756.html) — 0.7
- `src-2026-06-05-020` IT之家 M3 token anxiety (ithome.com/0/960/544.htm) — 0.85
- `src-2026-06-05-021` MiniMax Token Plan FAQ (platform.minimax.io/docs/token-plan/faq) — 0.95
- `src-2026-06-05-022` MiniMax Rate Limits (platform.minimax.io/docs/guides/rate-limits) — 0.95
- `src-2026-06-05-023` IT之家: MiniMax Token Plan apology (ithome.com/0/960/544.htm) — 0.85
- `src-2026-06-05-024` 凤凰网 same apology (tech.ifeng.com/c/8tiAPZOLfIS) — 0.85
- `src-2026-06-05-025` 网易: MiniMax Agent → Mavis, Agent Teams (163.com/dy/article/KSSR1TO405566WT8.html) — 0.9
- `src-2026-06-05-026` 腾讯网: Mavis Mavis 「三省六部」 (news.qq.com/rain/a/20260513A098U200) — 0.9
- `src-2026-06-05-027` 爱范儿: Mavis 实测体验 (ifanr.com/1665759) — 0.85
- `src-2026-06-05-028` MiniMax Agent Team technical blog (minimaxi.com/blog/minimax-agent-team-long-running) — 0.95
- `src-2026-06-05-029` 腾讯网: Mavis 之路 — 多 Agent 工程化 (news.qq.com/rain/a/20260515A06Y5H00) — 0.85
- `src-2026-06-05-030` MiniMax CLI docs (platform.minimax.io/docs/token-plan/minimax-cli) — 0.95
- `src-2026-06-05-031` 和讯: Mavis 合并 TokenPlan/AgentPlan (tech.hexun.com/2026-05-13/224145799.html) — 0.8
- `src-2026-06-05-032` Mac App Store: MiniMax - Your AI Agent (apps.apple.com/us/app/...id6742651446) — 0.95
- `src-2026-06-05-033` watcha.cn MiniMax Agent 2.0 product details (watcha.cn/products/1309) — 0.75
- `src-2026-06-05-034` php.cn minimax 官网入口 + 桌面版 (php.cn/faq/2026721.html) — 0.7
- `src-2026-06-05-035` 凤凰网: Pocket + Computer Use launch (tech.ifeng.com/c/8sJqimFLKp6) — 0.9
- `src-2026-06-05-036` MiniMax Agent Changelog (agent.minimax.io/docs/changelog) — 0.95

## Contradictions and open questions

- **M3 latency benchmarks (p50/p95/p99) are not published as of 2026-06-05.** **The 400 TPS throughput claim (UNVERIFIED in primary sources, see line 21)** is a throughput number, not a latency number. For latency-sensitive routing decisions (e.g., "is M3 fast enough for the Verifier's per-source re-derivation step?"), we need either a third-party benchmark or our own measurement. **UNVERIFIED — Phase 3 input.**
- **M3 open-weights release:** MiniMax said "10 days from 2026-06-01," which is 2026-06-11. As of 2026-06-05, no HuggingFace release. If the release slips, our ability to self-host M3 for token-cost reduction is gated.
- **Local REST API on the macOS Desktop App:** no public documentation found. If it exists, it's internal. The Mavis CLI is the documented programmatic surface. For Phase 3, this is a question for the MiniMax team or a community reverse-engineer.
- **Permission system correctness:** the 2026-05-13 changelog admits the file-deletion edge case in full-authorize mode. For the Mavis Blueprint, we should design with **narrow scope by default** and explicit elevation only when needed.
- **M2.7 → M3 routing in practice:** Andre's directive (M2.7 for workers, M3 for chief) is the right starting point, but the empirical IQ delta at the worker level (does M2.7 hold a 6-hour task as well as M3?) is not tested. Needs an eval.
- **The "Mavis" name collision:** MiniMax's desktop agent product is also called Mavis (since 2026-05-13). Andre's EA agent (me) is independently named Mavis. This is a name collision worth flagging in any external documentation, but doesn't change operational behavior — they're different systems.
- **GPT-6 / Claude 5 rumors:** no signal in this dossier cycle. Watch.

## Implications

- **Build (Phase 3 design — the Mavis Blueprint):**
  1. **Adopt the Mavis Team Engine as the orchestration substrate.** Don't build our own Leader/Worker/Verifier runtime — MiniMax already did, and the design rationale aligns with the Producer → Trust loop. The Mavis CLI is the integration point.
  2. **Use M3 for the chief and long-horizon workers; M2.7 for read/structure/cite workers.** Per Andre's 2026-06-05 directive. Wire this into the `mavis-team` agent configs.
  3. **Token Plan rate structure requires primary-source verification before production use.** The 1.3x input / 1.8x output / 0.2 token/char surcharge numbers circulate in secondary press (php.cn, IT之家) but are NOT in the official Token Plan FAQ or Rate Limits page as of 2026-06-05 (see line 74). Do NOT trust the SDK's `total_tokens`; do NOT apply the multipliers to Mavis's token accounting until a primary source confirms them. The verified base rates are $0.30/M input, $1.20/M output.
  4. **Design the macOS Desktop App integration as the OS surface.** Computer Use + Pocket + Mavis CLI for the Mavis Daily Check-in project. Scope file system access narrowly.
  5. **The MSA + 1M context is the long-context lever.** Vault-scale context work that was impossible on M2.7 (262K limit) is now economically tractable on M3. This unlocks the "100k+ token vault" design question in Phase 2.
  6. **Cache aggressively on the system prompt.** Token Plan's system-prompt economics (charge rate UNVERIFIED in primary sources, see line 74) — pending primary confirmation, assume a non-trivial per-turn cost that prompt caching on stable blocks can offset. Specific multiplier pending primary-source verification.
- **Content:** the "open-weight frontier parity" thesis is the strongest frame for the Scribe. M3 is the proof point: SWE-Bench Pro within 1.2 pts of Opus 4.7 at 5-10% of the cost. Combined with MSA's 9.7x/15.6x speedup at 1M context, the cost/performance story is the new lever.
- **Watch:** M3 open-weights release (~2026-06-11), Anthropic Mythos wider release, GPT-5.6 canary, MiniMax's rollout of the (UNVERIFIED, see line 74) multiplier structure (the June 5 apology walked back the most aggressive limits — second apology likely if user feedback continues on the unconfirmed 1.3x/1.8x/0.2 numbers).
- **Verify:** third-party latency benchmarks for M3 (p50/p95/p99), M2.7 vs M3 worker-quality evals on real production tasks, the desktop app's permission system for non-deletion operations.

## Routing history

| Date | Routed to | Item | Outcome |
|------|-----------|------|---------|
| 2026-06-05 | Phase 2 dossier (next) | feeds agent-harness + context-engineering research | Pending |
| 2026-06-05 | Phase 3 Mavis Blueprint | feeds the Mavis Phase 3 design | Pending |
| 2026-06-05 | queue/verification-review.md | src-2026-06-05-013, src-2026-06-05-019 (multiplier claim) | Awaiting Verifier |
| 2026-06-05 | knowledge/sources.jsonl | src-2026-06-05-001 through src-2026-06-05-036 | Appended |

---

*This dossier is the input for Phase 3. It is durable, sourced, and structured to answer the three Phase 3 design questions: infrastructure upgrade, the Mavis harness, and the context pipeline. The Mavis / MiniMax / macOS Desktop App combination is the integrated OS-integration stack Andre is moving toward — the blueprint should not invent, it should adopt and extend.*
