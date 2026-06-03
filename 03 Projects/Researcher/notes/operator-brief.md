# Operator Brief

> First thing Andre reads after a REFRESH. Tells him: what changed, what deserves attention, what is blocked by weak evidence, and what Mavis/Hermes should do.

*Last REFRESH: 2026-06-02 21:50 CT (manual, 60-min wall cap, 2 lanes). Freshness: fresh.*

## What changed since last brief

3 dossier-grade deltas, each with source trail:

1. **The agentic frontier has shifted.** In May–June 2026, every major lab shipped agent-runtime primitives on top of the model: Anthropic Dynamic Workflows in Claude Code (hundreds of parallel subagents per session, May 28) + Managed Agents (Dreaming, Multiagent Orchestration, Outcomes, Webhooks, Self-hosted Sandboxes, MCP tunnels, May 12–26), Google Antigravity 2.0 at I/O 2026 (May 19), LangChain 1.0 + LangGraph 1.0 GA (Oct 22, 2025, still the de facto standard, 90M monthly downloads). Verified across 3+ primary sources. (clm-2026-06-02-002, weight 0.8)

2. **GPT-5.5 is the current OpenAI frontier.** Released Apr 23, 2026. Terminal-Bench 2.0 82.7%, GDPval 84.9%, SWE-Bench Pro 58.6%, OSWorld-Verified 78.7%. 1M context in Codex. $5/M input, $30/M output API. Treated as High under Preparedness Framework for bio/cyber. Generally available on AWS via Bedrock as of June 1, 2026. Verified. (clm-2026-06-02-001, weight 0.9)

3. **Persistent agent memory is the active research frontier with no clear winner.** Letta (MemGPT-derived, OS-inspired, #1 model-agnostic OSS on Terminal-Bench), Mem0 (extractive facts, 91% p95 latency reduction on LoCoMo), Zep (temporal knowledge graph), Cognee (knowledge graph). arXiv surveys confirm no canonical solution. MemoryArena exposes a deep gap: models near-perfect on LoCoMo plummet to 40-60% on multi-session decision tasks. **Andre's stack runs gbrain, Honcho, OpenClaw** — directly relevant. (clm-2026-06-02-005, weight 0.7, unverified)

## What deserves attention

Prioritized for this cycle:

1. **Hermes handoff ready:** clm-2026-06-02-003 (Anthropic Managed Agents — Dreaming, Multiagent Orchestration, Outcomes, Self-hosted Sandboxes, MCP tunnels) and clm-2026-06-02-001 (adopt gpt-5.5 as default for high-stakes Codex tasks). Both verified, both buildable. `queue/hermes-handoff.md` has the YAML.

2. **Persistent memory — research question for Mavis:** Does the Researcher know enough about gbrain / Honcho / OpenClaw to map them onto the Letta/Mem0/Zep/Cognee taxonomy? If yes, this is exactly the kind of synthesis Mavis would write a `06 Connections/` note from. Standing by for the question.

3. **One single-source contradiction to ignore:** SEO source geo.fkw.com claims GPT-6 released Apr 14, 2026 with 2M context. Contradicted by OpenAI's own research index. Routed to verification queue, not dossier, not Hermes, not content.

## Blocked / under-evidenced

- **GPT-6 rumor** (fnd-2026-06-02-026): single SEO source, contradicted. Verification queue, size 1. Well under the 50-item floor. No Mavis action needed yet.
- **SubQ 1M-Preview benchmarks** (fnd-2026-06-02-021): single secondary source (whatllm.org). 52x attention claim is unverified. Watch-only, not dossier.
- **Anthropic Mythos** and **Versept acquisition**: only mentioned in third-party Substacks/YouTube, not in any Anthropic primary. Watch-only.
- **Realtime voice model availability in Codex CLI**: confirmed not in Codex CLI surface (fazm May 2026 ledger). No action needed; just noting because it matters for any voice-routing work.

## Handoffs ready for consumption

- Mavis: 1 item in `queue/mavis-handoff.md` (priority_alert, this run as source trail)
- Hermes: 2 items in `queue/hermes-handoff.md` (Managed Agents adoption, GPT-5.5 default flip)
- Build: 0 items (no cross-validated product opportunity surfaced yet)
- Content: 0 items (no publishable claim with full source trail ready)
- Watch: 1 item in `queue/watch-handoff.md` (Mythos, Versept, GPT-5.6 canary, Daybreak)
- Verify: 1 item in `queue/verification-review.md` (GPT-6 rumor)

## Collector health

- **ai_agents lane:** primary sources clean (langchain.com, letta.com, anthropic.com, arxiv.org). Secondary corroboration from Medium, Substack, Alice Labs (low-trust, downweighted). arXiv surveys strong.
- **frontier_ai lane:** primary sources clean (openai.com, blog.google, anthropic.com). 1 SEO contradiction identified and routed. whatllm.org and Fazm are secondary; flagged as such.
- **No degraded collectors this run.** All collection methods (web_search, webfetch) responded.

## Source balance

- ai_agents: 11 primary, 4 secondary, 0 social. Social: 0%.
- frontier_ai: 7 primary, 4 secondary, 0 social. Social: 0%.
- No dossier exceeds 60% social. Well under 40% soft warning floor for both lanes.

## Vault health

**PASS.** Schema valid on all three ledgers. All dossiers updated. All queue files conform to YAML schema. No orphan findings. Verification queue size 1 (well under 50 floor). 1 known contradiction surfaced and routed, not papered over.

## Suggested next actions for Mavis

1. **Read `queue/mavis-handoff.md`** — this run's priority_alert with the run receipt as source trail.
2. **Read `dossiers/ai_agents.md` and `dossiers/frontier_ai.md`** for the full picture.
3. **Decide on the gbrain ↔ memory-systems question:** if you want a synthesis, drop it in `queue/research-questions.md` and I'll process on the next REFRESH. This is the highest-leverage follow-up available.
4. **No need to triage the verification queue this cycle** — single item, well under floor, no urgency.

---

**Discipline:** This file is rewritten on every REFRESH, not appended. Andre should never have to scroll.
