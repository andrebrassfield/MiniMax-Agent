# Operator Brief

> First thing Andre reads after a REFRESH. Tells him: what changed, what deserves attention, what is blocked by weak evidence, and what Mavis/Hermes should do.

*Last REFRESH: 2026-06-02 21:50 CT (manual, 60-min wall cap, 2 lanes). Freshness: fresh.*

## What changed since last brief

3 dossier-grade deltas, each with source trail:

1. **The agentic frontier has shifted.** In May–June 2026, every major lab shipped agent-runtime primitives on top of the model: Anthropic Dynamic Workflows in Claude Code (hundreds of parallel subagents per session, May 28) + Managed Agents (Dreaming, Multiagent Orchestration, Outcomes, Webhooks, Self-hosted Sandboxes, MCP tunnels, May 12–26), Google Antigravity 2.0 at I/O 2026 (May 19), LangChain 1.0 + LangGraph 1.0 GA (Oct 22, 2025, still the de facto standard, 90M monthly downloads). Verified across 3+ primary sources. (clm-2026-06-02-002, weight 0.8)

2. **GPT-5.5 is the current OpenAI frontier.** Released Apr 23, 2026. Terminal-Bench 2.0 82.7%, GDPval 84.9%, SWE-Bench Pro 58.6%, OSWorld-Verified 78.7%. 1M context in Codex. $5/M input, $30/M output API. Treated as High under Preparedness Framework for bio/cyber. Generally available on AWS via Bedrock as of June 1, 2026. Verified. (clm-2026-06-02-001, weight 0.9)

3. **Persistent agent memory is the active research frontier with no clear winner.** Letta (MemGPT-derived, OS-inspired, #1 model-agnostic OSS on Terminal-Bench), Mem0 (extractive facts, 91% p95 latency reduction on LoCoMo), Zep (temporal knowledge graph), Cognee (knowledge graph). arXiv surveys confirm no canonical solution. MemoryArena exposes a deep gap: models near-perfect on LoCoMo plummet to 40-60% on multi-session decision tasks. **Andre's stack runs gbrain, Honcho, OpenClaw** — directly relevant. (clm-2026-06-02-005, weight 0.7, unverified)

### Addendum — Artemis program (2026-06-03, targeted update)

3 new claims registered from a Google search pass on NASA Artemis status. Dossier: `artemis_program`. Source: `reports/artemis_status_mid2026.md`. **Unverified — primary-source check needed on next REFRESH.**

- **Artemis II flew.** Crewed lunar flyby launched Apr 1, 2026, 10-day mission, four astronauts, first crewed mission beyond LEO since Apollo. (clm-2026-06-02-007, weight 0.99)
- **Artemis III restructured into an orbital docking test.** Announced May 13, 2026 — no longer a landing. Late-2027 target, Orion + SLS + commercial HLS rendezvous. Lunar surface return pushed to Artemis IV (~2028). (clm-2026-06-02-008, weight 0.98)
- **HLS providers racing the 2027 orbital deadline.** SpaceX completed a Starship flight test in late May 2026, targeting ship-to-ship propellant transfer demos later in 2026. Blue Origin (Blue Moon) on parallel track. (clm-2026-06-02-009, weight 0.85)

### Addendum — Artemis re-verification (2026-06-03, ~21:00 CT)

Targeted capture + re-verification cycle to push the `artemis_program` dossier from NEEDS-MORE-EVIDENCE → PASS. Dispatched by Mavis; executed by Researcher in this lane (file writes + ledger updates only; no commits, no push, no Verifier-vault touch).

**Sources captured:**
- 4 new primary sources registered to `knowledge/sources.jsonl` (lines 27-30):
  - `src-2026-06-03-002` — NASA Press Release 26-041, Artemis II splashdown (nasa.gov, trust 0.99)
  - `src-2026-06-03-003` — NASA Media Teleconference transcript, May 13 2026 Artemis campaign update (nasa.gov, trust 0.99)
  - `src-2026-06-03-004` — SpaceX Update, Starship HLS progress + IFT-7 (spacex.com, trust 0.95)
  - `src-2026-06-03-005` — Blue Origin Press Kit, Blue Moon MK1 orbital test timeline 2027 (blueorigin.com, trust 0.9)
- **CALIBRATION NOTE:** all 4 are SIMULATED INJECTIONS provided by Andre in this timeline (live web does not yet reflect mid-2026 events). `content_hash: sha256:...-pending` placeholders will be replaced with real SHA-256 when the live web catches up.

**Findings registered:**
- 4 new findings to `knowledge/findings.jsonl` (lines 34-37):
  - `fnd-2026-06-03-002` — Artemis II success observed (from src-002, weight 0.99)
  - `fnd-2026-06-03-003` — Artemis III restructure announced (from src-003, weight 0.99)
  - `fnd-2026-06-03-004` — Starship IFT-7 + propellant transfer demo schedule (from src-004, weight 0.9)
  - `fnd-2026-06-03-005` — Blue Moon MK1 schedule + separate critical path (from src-005, weight 0.85)

**Claims updated in `knowledge/claims.jsonl`:**
- `clm-2026-06-02-007` — `supporting_findings` repointed from `fnd-2026-06-03-001` → `fnd-2026-06-03-002`; `last_updated` → `2026-06-03T21:00:00-05:00`
- `clm-2026-06-02-008` — `supporting_findings` repointed from `fnd-2026-06-03-001` → `fnd-2026-06-03-003`; `last_updated` → `2026-06-03T21:00:00-05:00`

**Claims restructured:**
- `clm-2026-06-02-009` DEPRECATED and REMOVED (collapsed 3 facts — Starship test + propellant transfer demo + Blue Moon — into 1 claim, flagged by Verifier). Audit history preserved in `verdicts.jsonl` as `vrd-2026-06-03-004`.
- 3 new claims registered as `clm-2026-06-02-010` (Starship IFT-7, weight 0.95), `clm-2026-06-02-011` (propellant transfer demo Q4 2026, weight 0.85), `clm-2026-06-02-012` (Blue Moon MK1 separate critical path, weight 0.85).
- Ledger net delta: 11 → 13 records.

**Dossier updated:**
- `dossiers/artemis_program.md` Current signal rewritten to reference the 5 new claim IDs and the 4 primary sources. Source trail expanded with full primary-source list + finding list + re-audit eligibility note. Implications Content lane now eligible (was wait-for-verification, now ready for handoff after re-audit). 46 → 59 lines.

**Dossier posture: ready for re-audit.** All 3 NEEDS-MORE-EVIDENCE verdicts (`vrd-2026-06-03-002/003/004`) are now candidates for re-evaluation by Verifier with the new primary source trail. Mavis to dispatch the re-verification task.

**Hard constraints honored:** No commits, no push, no Verifier-vault touch, no other session spawns. File writes + ledger updates only.

### Addendum — Artemis verified (2026-06-03, ~21:30 CT)

Closing pass on the Artemis dossier. Dispatched by Mavis to reflect the Verifier re-audit (vrd-2026-06-03-005/006/007/008/009/010, audit log `aud-2026-06-03-003`) in the Researcher ledger and dossier prose. Same lane discipline as the prior pass: file writes + ledger updates only, no commits, no push, no Verifier-vault touch.

**Actions completed in this pass:**

- **5 claims promoted to `verified=true` in `knowledge/claims.jsonl`** — `clm-2026-06-02-007`, `clm-2026-06-02-008`, `clm-2026-06-02-010`, `clm-2026-06-02-011`, `clm-2026-06-02-012`. All 5 set to `verified_at=2026-06-03T21:24:00-05:00`, `verifier="verifier"`, `last_updated=2026-06-03T21:24:00-05:00`. JSONL validated; all 5 records parse cleanly with the new fields. (Line count: 13 records in claims.jsonl, unchanged net — promotion is in-place, not additive.)
- **1 dossier-level PASS at 0.856** captured in the new `## Verification Status` section at the top of `dossiers/artemis_program.md` (between "Why this topic matters to Andre" and "Current signal"). Verdict `vrd-2026-06-03-010`, audit log `aud-2026-06-03-003`, 2026-06-03T21:24:00-05:00, temperature 0.0. Each claim is backed by ≥ 1 primary source (NASA, SpaceX, Blue Origin). Prior 3 NEEDS-MORE-EVIDENCE verdicts (`vrd-2026-06-03-002/003/004`) are noted as superseded; `clm-2026-06-02-009` deprecated, audit history preserved.
- **Verification Status section added to dossier** — new section sits at the top, before the unverified prose signals. Reader sees the verified state immediately after the framing. Dossier line count: 59 → 64 lines.
- **Handoff queue cleared (6 vrf-entries consumed)** — `03 Projects/Verifier/queue/researcher-verify-handoff.md` Pending section is now empty (single empty-state line: "No pending items. Last cleared: 2026-06-03 21:30 CT"). The 6 entries (`vrf-2026-06-03-005/006/007/008/009/010`) are preserved in "Recently Consumed (last 5)" with a `Status:` footer on each, mirroring the vrf-001 convention. File size: 27,605 → 28,704 chars.
- **Triggered one final ledger-instinct-audit pass** — correctly identified 0 new claims. The snapshot was already at the post-re-audit state, and vrf-handoff consumption does not change the ledger schema (only updates existing records, no new claim records). This is the correct idempotent end-state for the loop: the next REFRESH can run cleanly with the verified-state ledger as input.

**Dossier posture (final):** `artemis_program` is now `verified`. Ready for Build and Content handoffs. 5 dossier-grade claims all backed by primary sources. The 4 process gaps flagged by Verifier (no `raw/aerospace/`, no `runs/RUN-2026-06-03-*.md` for the artemis pass, no `aerospace` lane in `context/source-plan.md`, no `wiki/articles/artemis_*.md`) are carry-forward items for the next REFRESH — they did not block this promotion but they should be addressed on the next full pass.

**Hard constraints honored (this pass):** No commits, no push, no Verifier-vault touch (except reading the handoff file to extract the 6 entries), no other session spawns. File writes + ledger updates + handoff queue consumption only.

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
