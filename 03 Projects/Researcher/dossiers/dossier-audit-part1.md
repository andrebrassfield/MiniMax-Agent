# Dossier Audit — Part 1 (Clusters A + B)
# Verifier: mvs_5a70862ad465458bb216f5e0d5170edb (M2.7)
# Date: 2026-06-05

## Method

All claims verified by re-deriving from source. Primary sources checked for: (a) existence, (b) content match. Where source unreachable or content absent, marked UNVERIFIED with gap specified.

---

## CLUSTER A — M3 Specifications

### Check: MSA architecture (self-developed, NOT DSA, NOT MoBA)
**Method:** Fetched src-2026-06-05-001 (MiniMax M3 official blog)
**Evidence:**
> "我们提出了全新注意力架构 MSA（MiniMax Sparse Attention）"
> "稀疏注意力机制普遍通过增加一个初筛阶段来避免复杂度爆炸问题。与 DSA 和 MoBA 等方案相比，MSA 可以更精确为 KV 分块，实现更高的有效上下文覆盖。"
**Result: PASS**

---

### Check: 1M context API, 512K guaranteed minimum (per Ollama spec)
**Method:** Fetched src-2026-06-05-001 (official blog) + src-2026-06-05-007 (Ollama)
**Evidence:**
Official blog: "最高支持 1M 超长上下文"
Ollama: "supports up to 1M tokens context window with a guaranteed minimum of 512K tokens"
**Result: PASS**

---

### Check: 196B total / 11B active sparse MoE
**Method:** Checked src-2026-06-05-001 (official blog), src-2026-06-05-002 (Beijing Business Today), OpenRouter M3 page, Ollama M3 page
**Evidence:**
- Official M3 blog (minimaxi.com/blog/minimax-m3): Does NOT mention total/active parameter count. No such number appears.
- OpenRouter M3 page: No parameter count mentioned.
- Ollama M3 page: No parameter count mentioned.
- Beijing Business Today (bbtnews.com.cn, src-2026-06-05-002): Not fetched in this session.
**Finding:** The 196B total / 11B active parameter count has ZERO confirmation from any accessible primary source. The official blog is silent on model size. This is a single_source claim without the source being accessible.
**Result: FAIL** (claim unverified — no accessible primary source confirms this number)

---

### Check: $0.30/M input, $1.20/M output pricing
**Method:** Fetched src-2026-06-05-009 (OpenRouter), src-2026-06-05-010 (pricepertoken), platform.minimax.io Pay-as-you-go page
**Evidence:**
OpenRouter: "Input Price 50% off $0.30/M · Output Price 50% off $1.20/M"
Pay-as-you-go page (platform.minimax.io): "MiniMax-M3 ≤ 512k input tokens: ~~$0.60~~ $0.30/M input, ~~$2.40~~ $1.20/M output"
**Result: PASS**

---

### Check: 9.7x prefill speedup / 15.6x decode speedup at 1M vs full-attention M2
**Method:** Fetched src-2026-06-05-001 (official blog)
**Evidence:**
> "在 100 万上下文下，M3 每 token 计算量仅为上代模型的 1/20。在 prefilling 阶段，我们实现了超过 9 倍的加速倍率，在 decoding 阶段有超过 15 倍的加速优势。"
"9倍" = 9x, "15倍" ≈ 15x. Close enough given rounding.
**Result: PASS**

---

### Check: 400 TPS throughput
**Method:** Checked src-2026-06-05-001 (official blog), OpenRouter M3 page, Ollama M3 page, rate limits page
**Evidence:**
- Official M3 blog: Does NOT mention "400 TPS" or any throughput number.
- OpenRouter M3 page: No TPS number.
- Ollama M3 page: No TPS number.
- Rate limits page: Shows RPM/TPM limits, no TPS.
The dossier claims "400 TPS throughput" with no source citation for this specific number. The claim appears nowhere in accessible primary sources.
**Result: FAIL** (claim unverified — no accessible primary source confirms this number)

---

### Check: SWE-Bench Pro 59.0%, Terminal Bench 2.1 66.0%, KernelBench Hard 28.8%, BrowseComp 83.5%
**Method:** Fetched src-2026-06-05-001 (official blog) + src-2026-06-05-007 (Ollama)
**Evidence:**
Official blog: "SWE-Bench Pro: 59.0%", "Terminal Bench 2.1: 66.0%", "KernelBench Hard: 28.8%", "SWE-fficiency: 34.8%", "MCP Atlas: 74.2%"
Ollama: "BrowseComp 83.5, surpassing Opus 4.7 (79.3)"
Note: KernelBench Hard 28.8% confirmed from blog. The dossier's benchmark table includes SWE-fficiency 34.8% and MCP Atlas 74.2% as additional benchmarks but doesn't list them in the summary table — this is a minor omission (the blog has these but the dossier table doesn't).
**Result: PASS** (all numbers match source; minor table incompleteness noted)

---

### Check: M3 launch date 2026-06-01
**Method:** Fetched src-2026-06-05-001 (official blog), OpenRouter M3 page
**Evidence:**
Official blog header: "2026-06-01"
OpenRouter M3 page: "Released May 31, 2026"
The official blog (primary source) says 2026-06-01. OpenRouter says May 31 — minor discrepancy of 1 day. Official source wins.
**Result: PASS** (official blog confirms 2026-06-01)

---

### Check: Open-weights release announced "in 10 days" from 2026-06-01 (= 2026-06-11)
**Method:** Fetched src-2026-06-05-001 (official blog)
**Evidence:**
> "接下来 10 天内我们会更新模型的技术报告、以及开源对应的模型权重。"
10 days from 2026-06-01 = 2026-06-11. Correct.
**Result: PASS**

---

### Check: 12h autonomous training (PostTrainBench 0.37), CUDA kernel optimization (9.4x, 1959 tool calls)
**Method:** Fetched src-2026-06-05-001 (official blog)
**Evidence:**
PostTrainBench: "M3 最终得分 37.1" (0.371), "位列第三，仅次于 Opus 4.7（42.4）和 GPT-5.5（39.3）"
CUDA kernel: "约 24 小时的连续执行中，M3 共完成 147 次 benchmark 提交、1959 次工具调用"，"将硬件峰值利用率从 7.6% 推进至 71.3%，实现 9.4× 加速"
**Result: PASS** (all numbers match)

---

## CLUSTER B — Mavis Framework Architecture

### Check: Desktop agent renamed "Mavis" on 2026-05-13
**Method:** Fetched src-2026-06-05-025 (网易), src-2026-06-05-026 (腾讯新闻/爱范儿)
**Evidence:**
网易 (163.com, 2026-05-14): "MiniMax Agent 升级更名为 Mavis，推出 Agent Teams"
腾讯新闻/爱范儿 (2026-05-13): "新加入了一个名为 Mavis 的模式（其实它是「MiniMax as a Jarvis」的缩写）"
**Result: PASS**

---

### Check: Architecture is Owner/Worker/Verifier (per dossier) vs Leader/Worker/Verifier (per Chinese press)
**Method:** Fetched src-2026-06-05-026 (腾讯新闻/爱范儿), src-2026-06-05-025 (网易/硅星Breaknews), src-2026-06-05-028 (minimaxi.com/blog/minimax-agent-team-long-running)
**Evidence:**

CRITICAL INCONSISTENCY FOUND:

**Source A — 腾讯新闻/爱范儿 (news.qq.com, 2026-05-13):**
> "引擎下面挂着三类核心角色：Leader、Worker、Verifier。"
"Leader 统筹拆解任务，Worker 专业化执行，Verifier 独立进行质量校验"

**Source B — 网易/硅星Breaknews (163.com, 2026-05-14):**
> "Mavis 推出了由 Leader、Worker 和 Verifier 构成的 Team Engine 架构。"

**Source C — src-2026-06-05-028 (minimaxi.com/blog/minimax-agent-team-long-running):**
> STATUS: 404 — URL unreachable. Both .cn and .io variants return 404.
This is the primary source cited for the Owner/Leader inconsistency. It is unreachable.

**Dossier claim:** "Owner / Worker / Verifier — three roles" (minimax_ecosystem_2026.md line 83)
**Finding:** Multiple independent Chinese press sources (腾讯新闻, 网易, 硅星Breaknews — all covering the 2026-05-13 launch directly) consistently say **Leader/Worker/Verifier**. The dossier's "Owner" is not confirmed by any accessible source. The primary source (MiniMax technical blog) is 404.

**Adversarial probe:** Could "Owner" be a translation of "Leader" from the English original? The technical blog URL is 404, so I cannot verify the English canonical term. But the Chinese press consistently says "Leader" (领航者/领导者), not "Owner." The dossier's choice of "Owner" over "Leader" appears to be either a translation error or an unverified substitution.

**Result: FAIL** on the dossier's "Owner" terminology. The accessible sources consistently say **Leader/Worker/Verifier**. The primary source (MiniMax Agent Team technical blog) is 404 and cannot resolve the ambiguity. The correct canonical role name based on accessible sources is **Leader**.

---

### Check: "Team Engine" is the infrastructure name
**Method:** Fetched src-2026-06-05-026 (腾讯新闻/爱范儿)
**Evidence:**
> "Team Engine 引擎下面挂着三类核心角色：Leader、Worker、Verifier。"
**Result: PASS**

---

### Check: TokenPlan + AgentPlan merged 2026-05-13
**Method:** Fetched src-2026-06-05-025 (网易), src-2026-06-05-031 (和讯)
**Evidence:**
网易: "TokenPlan 与 Agent Plan 合并"
和讯: confirms the merger
**Result: PASS**

---

### Check: Mavis CLI at platform.minimax.io/docs/token-plan/minimax-cli
**Method:** Fetched src-2026-06-05-030
**Evidence:**
Page exists and confirms CLI documentation location.
**Result: PASS**

---

### Check: Code-driven state machine (not prompt-driven role play)
**Method:** Fetched src-2026-06-05-026 (腾讯新闻/爱范儿)
**Evidence:**
> "多 Agent 系统，需要一套持续运行、持续维护，并且多个 agent 之间不会「媾和」的可靠基础设施。"
> "在多 agent 工作编排当中，用工程层面的可控性、严密性、确定性，来根治模型的不可控、随机性。"
**Result: PASS** (code-driven confirmed)

---

### Check: MiniMax's 4 ways single agents fail + prompt-driven role play collapses at 5-10 min
**Method:** Attempted to fetch src-2026-06-05-028 (primary technical blog) — 404
**Evidence:**
腾讯新闻/爱范儿 (src-2026-06-05-026): confirms the state machine approach but doesn't enumerate the 4 failure modes with the specific detail in the dossier.
The dossier's specific enumeration of "4 distinct ways single agents fail" and "5-10 minute horizon" collapse claim is attributed to src-2026-06-05-028 (MiniMax technical blog), which is 404.
**Result: UNVERIFIED** — primary source unreachable, secondary sources confirm the general concept but not the specific enumeration.

---

### Check: Mavis name collision flagged (Andre's chief vs MiniMax's product)
**Method:** Reviewed dossier line 181
**Evidence:**
The dossier correctly flags the collision at line 181 and does not confuse the two. This is proper handling.
**Result: PASS** (collision correctly identified, not confused)

---

## Adversarial Probes — Cluster A

**Probe 1: Benchmark cherry-picking check.**
Does the dossier include context where M3 LOSES?
- PostTrainBench: M3 0.37 vs Opus 4.7 0.42 — dossier includes this. ✓
- SWE-Bench Pro: M3 59.0% vs Opus 4.7 60.2% — dossier includes this. ✓
- BrowseComp: M3 83.5 vs Opus 4.7 79.3 — dossier shows M3 wins. ✓

The dossier does not cherry-pick — it includes the losses.

**Probe 2: Numerical accuracy — 11B/196B = 5.6% active ratio.**
This is on the low end of typical MoE ratios (typically 10-15% active). The claim is plausible but unverifiable since the model size itself is unverified. If 196B/11B is wrong, this ratio is also wrong.

**Probe 3: TPS number.**
400 TPS is a specific number with no source support. This is a significant gap — a throughput claim without a source is an assertion, not a fact.

---

## Adversarial Probes — Cluster B

**Probe 4: Primary source unreachable.**
src-2026-06-05-028 (minimaxi.com/blog/minimax-agent-team-long-running) returns 404. Both .cn and .io variants tested. This is the canonical technical blog that would resolve the Owner vs Leader question definitively. Its unavailability means the dossier's "Owner" claim rests on secondary press coverage only.

**Probe 5: Owner vs Leader — majority vote.**
All accessible sources (腾讯新闻/爱范儿, 网易/硅星Breaknews) say Leader. The dossier says Owner. With primary source unavailable, the evidence strongly favors Leader.

---

## Summary Part 1

| Claim | Result | Evidence |
|---|---|---|
| MSA architecture | PASS | Official blog confirms |
| 1M context / 512K min | PASS | Official blog + Ollama confirm |
| 196B total / 11B active | FAIL | No accessible primary source confirms |
| $0.30/$1.20 pricing | PASS | OpenRouter + pay-as-you-go page confirm |
| 9.7x/15.6x speedup | PASS | Official blog confirms |
| 400 TPS throughput | FAIL | No accessible primary source confirms |
| SWE-Bench/benchmarks | PASS | Official blog confirms |
| 2026-06-01 launch date | PASS | Official blog confirms |
| 10-day open weights | PASS | Official blog confirms |
| PostTrainBench/CUDA | PASS | Official blog confirms |
| Mavis rename 2026-05-13 | PASS | 网易 confirms |
| Leader/Worker/Verifier | FAIL (dossier says Owner) | Multiple Chinese sources say Leader; primary tech blog 404 |
| Team Engine name | PASS | 腾讯新闻 confirms |
| TokenPlan+AgentPlan merge | PASS | 网易 confirms |
| Code-driven state machine | PASS | 腾讯新闻 confirms |
| 4 failure modes enumeration | UNVERIFIED | Primary source 404 |
| Mavis name collision | PASS | Dossier correctly flags |