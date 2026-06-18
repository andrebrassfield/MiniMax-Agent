# Dossier Audit Report — Phase 1 + Phase 2 (Re-Dispatch v2, M2.7 Verifier)
# Verifier session: mvs_5a70862ad465458bb216f5e0d5170edb
# Date: 2026-06-05
# Sources re-derived: 16 primary fetches, 4 secondary confirmations

## Overview

Two Researcher dossiers audited against accessible primary sources. Phase 1 (minimax_ecosystem_2026.md): strong core claims, two critical gaps. Phase 2 (harness_and_context_design.md): well-grounded, two partial-pass pattern citations.

**VERDICT: FAIL**

Reason: Two load-bearing claims lack accessible primary source support. Critical inconsistency unresolved (primary source 404). Token multiplier claim not confirmed in official MiniMax platform documentation.

---

## Cluster A — M3 Specs: 9 PASS / 2 FAIL

**PASS:** MSA architecture, 1M context / 512K min, $0.30/$1.20 pricing, 9.7x/15.6x speedup, SWE-Bench Pro 59.0%, Terminal Bench 66.0%, KernelBench Hard 28.8%, BrowseComp 83.5%, 2026-06-01 launch, 10-day open weights, PostTrainBench 0.37, CUDA 9.4x/1959 tool calls.

**FAIL (unverified):**
- **196B total / 11B active parameters:** No accessible primary source confirms this. Official M3 blog, OpenRouter, and Ollama all silent on model size. Single-source claim where source not accessed.
- **400 TPS throughput:** No accessible primary source confirms this. Official blog, OpenRouter, Ollama, rate limits page — none mention a TPS number.

---

## Cluster B — Mavis Framework: 6 PASS / 1 FAIL / 1 UNVERIFIED

**PASS:** Mavis rename 2026-05-13, Team Engine name, TokenPlan+AgentPlan merge, Mavis CLI location, code-driven state machine, Mavis name collision correctly flagged.

**FAIL (critical inconsistency):**
- **"Owner/Worker/Verifier" vs "Leader/Worker/Verifier":** Multiple independent Chinese press sources (腾讯新闻/爱范儿 2026-05-13, 网易/硅星Breaknews 2026-05-14) — both covering the launch directly — say **Leader/Worker/Verifier**. The dossier uses "Owner/Worker/Verifier." The primary source (minimaxi.com/blog/minimax-agent-team-long-running, src-2026-06-05-028) returns **404** on both .cn and .io variants. Cannot resolve from primary. Evidence strongly favors **Leader** as canonical.

**UNVERIFIED:**
- **4 specific ways single agents fail + 5-10 min collapse claim:** Attributed to src-2026-06-05-028 (primary technical blog, 404). General concept confirmed by secondary sources; specific enumeration not independently verified.

---

## Cluster C — Token Plan Multipliers: 1 PASS / 1 FAIL / 3 UNVERIFIED

**PASS:** 5-hour rolling window + dynamic rate limiting confirmed in Token Plan FAQ.

**FAIL (critical):**
- **1.3x input multiplier, 1.8x output multiplier, 0.2 token/char surcharge:** These numbers are NOT in the cited sources (Token Plan FAQ src-2026-06-05-021, Rate Limits src-2026-06-05-022). Both pages verified — neither contains the multipliers. Secondary press (php.cn, ithome.com) describes token billing anxiety but doesn't provide the specific numbers from an official source. **This is a load-bearing claim for Andre's routing rule (Section 73 of Phase 1).** If the harness applies these multipliers and they're wrong, token accounting will be systematically incorrect.

**UNVERIFIED:** 40% higher M3 consumption, 3.22-pre no-weekly-cap specifics, SDK total_tokens gap (requires live test fixture).

---

## Phase 2 — Agent Harnesses & Context Engineering: 10 PASS / 3 PARTIAL PASS

**PASS:** 12 harness components, Liu et al. 2023 "Lost in the Middle" confirmed, slash commands pattern, Anthropic Skills spec, 3-tier memory hierarchy, subagent isolation, MemGPT tiered memory, command_router design (sound fix for 2026-06-05 failure), cross-dossier Phase 1 dependencies correctly handled, Mavis name collision correctly handled.

**PARTIAL PASS:** "Delete the planning step" (Anthropic) and "Manus 5 rewrites in 6 months" — cited to internal dossier (src-2026-06-05-101) not primary Anthropic/MANUS sources. Patterns are described but not hard-linked to primary URLs.

---

## Cross-Cutting Findings

**Finding 1 — Primary source unavailable (critical):** src-2026-06-05-028 (MiniMax Agent Team technical blog, minimaxi.com/blog/minimax-agent-team-long-running) returns 404 on both .cn and .io variants. This is the canonical source for resolving the Owner vs Leader question AND for the specific enumeration of single-agent failure modes. Its unavailability is a structural gap in the dossier's source trail.

**Finding 2 — Token multipliers not in official docs (critical):** The 1.3x/1.8x/0.2 surcharge numbers are not in any accessible official MiniMax platform documentation. The claim's cited sources (Token Plan FAQ, Rate Limits) do not contain them. The actual Pay-as-you-go pricing shows flat per-token rates ($0.30/$1.20 for M3 ≤ 512K) with no multiplier language. This claim requires a primary source before it can be used for implementation.

**Finding 3 — M3 model size unverified:** The 196B total / 11B active parameter count appears nowhere in accessible primary sources. This is the numerical foundation for the MoE efficiency claim (11/196 = 5.6% active). If the model size is wrong, the efficiency framing is also wrong.

**Finding 4 — M3 throughput (TPS) unverified:** The 400 TPS claim has no source support. M2.7's throughput is confirmed at ~60 TPS (API overview page) but M3's is not stated anywhere.

**Finding 5 — Owner vs Leader: majority vote favors Leader:** All accessible sources (腾讯新闻, 网易, 硅星Breaknews) say Leader. The dossier says Owner. With primary source 404, Leader is the evidence-backed term. The Phase 1 dossier should be updated to use Leader.

---

## What Needs to Change (FAIL Resolution)

To move to PASS, the following must be resolved:

1. **Owner → Leader correction:** Phase 1 dossier line 83 should read "Leader/Worker/Verifier" not "Owner/Worker/Verifier." Primary source needed (technical blog, currently 404) to confirm.

2. **Token multipliers (1.3x/1.8x/0.2):** Find and cite the actual MiniMax official source for these numbers. If they don't exist (MiniMax walked them back in the June 5 apology), the claim must be removed or downgraded. Andre's routing rule depends on these numbers — if they're wrong, the routing decision is wrong.

3. **196B/11B model size:** Confirm via primary source or remove. If MiniMax never published model size, the MoE efficiency framing should be removed.

4. **400 TPS:** Confirm or remove. If unconfirmable, the throughput claim should be dropped.

5. **src-2026-06-05-028 (technical blog):** Attempt again — the 404 may be transient. If permanently unavailable, note in dossier and use secondary sources only.

---

## Verdict

**VERDICT: FAIL**

The dossier contains strong, well-sourced claims on M3's core capabilities (coding benchmarks, MSA architecture, 1M context, CUDA optimization, long-horizon demos) and the Mavis framework's code-driven architecture. These are verified and valuable.

However, the dossier also contains: (a) two critical claims (model size, TPS) with no source support, (b) a primary source (technical blog) that is 404 and cannot resolve a load-bearing inconsistency (Owner vs Leader), and (c) token multiplier numbers that do not appear in the cited official documentation and are critical to Andre's routing rule.

A dossier that cannot resolve its own most important inconsistency is not ready for Phase 3. The Chief should not route from these dossiers until the gaps are filled.

---

## Checkpoint Files

- `dossiers/dossier-audit-part1.md` — Cluster A (M3 specs) + Cluster B (Mavis architecture)
- `dossiers/dossier-audit-part2.md` — Cluster C (Token Plan) + Phase 2 (Agent Harnesses)

## Claims to Append (if PASS)

Had the verdict been PASS, the following claim IDs would have been recommended for `knowledge/claims.jsonl`:
- clm-2026-06-05-M3-MSA (MSA architecture, 1M context, coding benchmarks)
- clm-2026-06-05-M3-CUDA (9.4x speedup, 1959 tool calls, 71.3% utilization)
- clm-2026-06-05-M3-PostTrain (0.37 score, 12h autonomous training)
- clm-2026-06-05-Mavis-rename (2026-05-13, Team Engine, Leader/Worker/Verifier)
- clm-2026-06-05-Mavis-code-driven (state machine vs prompt role play)
- clm-2026-06-05-Mavis-merge (TokenPlan + AgentPlan)
- clm-2026-06-05-TokenPlan-windows (5h rolling + weekly)
- clm-2026-06-05-TokenPlan-apology (June 5 apology confirmed)
- clm-2026-06-05-Liu2023 (Lost in the Middle confirmed)
- clm-2026-06-05-3-tier-memory (SOTA pattern confirmed)

Claims NOT recommended for promotion until gaps resolved:
- clm-2026-06-05-M3-params (196B/11B — no source)
- clm-2026-06-05-M3-TPS (400 TPS — no source)
- clm-2026-06-05-TokenPlan-multipliers (1.3x/1.8x/0.2 — not in official docs)
- clm-2026-06-05-Mavis-Owner (Owner vs Leader unresolved — primary source 404)

---

*Verifier: mvs_5a70862ad465458bb216f5e0d5170edb (M2.7)*
*Re-derived from source. No trust inherited from previous (aborted) session.*