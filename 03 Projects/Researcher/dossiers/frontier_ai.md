# Dossier — Frontier AI

> Living topic file. Model releases, capability shifts, context length, multimodality.
>
> **Canonical synthesis pointer:** [`wiki/articles/2026-agentic-frontier.md`](../wiki/articles/2026-agentic-frontier.md) — cross-vendor long-form synthesis. Update that article on deltas that span both this dossier and `ai_agents.md`.

## Why this topic matters to Andre

Andre's agents run on the frontier. Model capability changes shift his stack's ceiling — what an agent can do, how long it can grind, what modalities it can ingest. M3 is his current default; the moment a successor emerges with material capability gains, the stack needs to know.

## Current signal (last refresh: 2026-06-02 21:50 CT)

**As of June 2, 2026: GPT-5.5 is the current OpenAI frontier. Gemini 3.5 Flash is the current Google frontier. Claude Opus 4.8 is the current Anthropic frontier.**

1. **OpenAI GPT-5.5** (Apr 23, 2026) — Terminal-Bench 2.0 82.7%, GDPval 84.9%, SWE-Bench Pro 58.6%, OSWorld-Verified 78.7%, CyberGym 81.8%. 1M context in Codex. $5/M input, $30/M output API. Treated as High under Preparedness Framework for bio/cyber. (clm-2026-06-02-001, fnd-2026-06-02-010)

2. **GPT-5.5 Instant** (May 5, 2026) — new ChatGPT default, replacing GPT-5.3 Instant. 52.5% reduction in hallucinated claims on high-stakes prompts per OpenAI. Available in API as `chat-latest`. (fnd-2026-06-02-011)

3. **GPT-5.5 realtime voice models** (May 7, 2026) — can reason, translate, and transcribe. In the realtime API surface, not Codex CLI. (fnd-2026-06-02-012)

4. **OpenAI on AWS** (Jun 1, 2026) — frontier models and Codex GA on Amazon Bedrock (Commercial + GovCloud). Daybreak (vision for secure software build) coming later. (fnd-2026-06-02-013)

5. **GPT-Rosalind + Rosalind Biodefense** (Apr 16 + May 29, 2026) — frontier reasoning model for life sciences, plus biodefense initiative with trusted access for U.S. government and allied partners (LLNL, Johns Hopkins APL, CEPI). (fnd-2026-06-02-014)

6. **Anthropic Claude Opus 4.8** (May 28, 2026) — Dynamic Workflows in Claude Code: hundreds of parallel subagents in a single session. Effort Control Low/Med/High/Max. Fast Mode: 2.5x output tokens/sec at 3x lower cost. Mid-conversation System Messages preserve prompt cache. (fnd-2026-06-02-015)

7. **Anthropic Opus 4.7** (Apr 16, 2026) — predecessor.

8. **Google Gemini 3.5 family** (I/O 2026, May 19) — 3.5 Flash GA same day in Gemini app, AI Mode, AI Studio, Gemini Enterprise, Android Studio, Antigravity. 3.5 Pro in internal use, rolling out next month. Framed as "frontier intelligence with action." (fnd-2026-06-02-018)

9. **Google Gemini Omni** (May 19, 2026) — any-to-any model. Powers Google Pics, intelligent eyewear, Ask YouTube. (fnd-2026-06-02-019)

10. **SubQ 1M-Preview** (May 5, 2026) — first commercial LLM with fully subquadratic sparse attention, 12M token context. Architecture could change long-context unit economics if benchmarks hold. (fnd-2026-06-02-021)

11. **Grok 4.3** (xAI, May 6, 2026) — wider rollout. **ZAYA1-8B** (Zyphra, May 6-7) — Apache 2.0 MoE, 8B total / 760M active, AMD-trained. **Gemini 3.1 Flash Lite** (Google, May 8). (fnd-2026-06-02-022, fnd-2026-06-02-023)

12. **Hugging Face trending (May 11, 2026):** google/gemma-4-31B-it (8.9M dl, 2.6K likes), Qwen/Qwen3.6-35B-A3B, deepseek-ai/DeepSeek-V4-Pro (1.3M dl), XiaomiMiMo/MiMo-V2.5-Pro (agent-focused, Chinese ecosystem), unsloth/MiniMax-M2.7-GGUF, openai/privacy-filter (PII). (fnd-2026-06-02-024)

13. **GPT-5.6 canary** — in Codex internal canary logs mid-May 2026. NO public release, no model card, no pricing sheet. Community base case: GPT-5.6 Jun 2026, GPT-6 Q3-Q4 2026. Daybreak (OpenAI cyber vision) coming later. (fnd-2026-06-02-025)

## Source trail

See `knowledge/sources.jsonl`. Key primary sources:
- `src-2026-06-02-001` OpenAI GPT-5.5 release page (openai.com) — weight 0.95
- `src-2026-06-02-002` OpenAI research index (openai.com) — weight 0.95
- `src-2026-06-02-005` Google Gemini 3.5 blog (blog.google) — weight 0.9
- `src-2026-06-02-008` Anthropic Dynamic Workflows in Claude Code (anthropic.com) — weight 0.9
- `src-2026-06-02-010` OpenAI on AWS (openai.com) — weight 0.9
- `src-2026-06-02-011` whatllm.org May 2026 roundup — weight 0.7 (secondary)
- `src-2026-06-02-012` Fazm OpenAI May 2026 ledger — weight 0.65 (secondary)
- `src-2026-06-02-013` Releasebot Anthropic — weight 0.7 (secondary)
- `src-2026-06-02-016` HF Trending Models digest — weight 0.7 (secondary)
- `src-2026-06-02-021` geo.fkw.com GPT-6 claim — weight 0.2 (CONTRADICTED, verification)

## Contradictions and open questions

- **GPT-6 rumor (fnd-2026-06-02-026)**: SEO source claims GPT-6 released Apr 14, 2026 with 2M context. CONTRADICTED by OpenAI's own research index. Routed to verification queue.
- **Context length honesty:** Multiple sources cite 1M+ context (GPT-5.5, Opus 4.6+, Gemini 3.1 Pro) but the gap between "marketed context" and "real working context" remains. OpenAI's own MRCR v2 results show meaningful degradation at 128K-1M. Worth deeper follow-up.
- **SubQ 1M-Preview** — single secondary source (whatllm.org). The 52x attention claim is unverified. Verification queue.
- **Open question:** What does the OpenAI ↔ Anthropic ↔ Google agent-runtime arms race look like 6 months out? Dynamic Workflows (Anthropic), Managed Agents (Anthropic), Antigravity (Google) all launched in May 2026. Is OpenAI's Codex CLI/ACP the equivalent surface, or is the "agent runtime" the next battleground for distribution?

## Implications

- **Build:** clm-2026-06-02-001 — adopt gpt-5.5 as default for Codex workers. Mid-priority for Hermes.
- **Watch:** GPT-5.6 canary, Daybreak, Claude 5 (rumored Q3-Q4 2026), Anthropic Mythos, Anthropic Versept. Routed to watch-handoff.
- **Verify:** SubQ benchmarks, GPT-6 rumor. Routed to verification.
- **Content:** No claim ready for content framing. clm-2026-06-02-002 (agentic frontier shift) is close but spans both dossiers.

## Routing history

| Date | Routed to | Item | Outcome |
|------|-----------|------|---------|
| 2026-06-02 | queue/hermes-handoff.md | hms-handoff-2026-06-02-002 (GPT-5.5 default flip) | Awaiting Hermes consumption |
| 2026-06-02 | queue/verification-review.md | clm-2026-06-02-026 (GPT-6 rumor) | Awaiting Mavis triage |
| 2026-06-02 | queue/watch-handoff.md | wch-handoff-2026-06-02-001 | Awaiting Andre consumption |
| 2026-06-02 | queue/mavis-handoff.md | priority_alert (run receipt as source trail) | Awaiting Mavis consumption |

---

*Dossier is the lever. Knowledge ledgers are the receipts. Refresh is the engine.*
