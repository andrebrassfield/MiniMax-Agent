---
type: design-doc
status: APPROVED
approved_at: 2026-06-07 12:55 CT
approved_by: Andre
created: 2026-06-07 12:46 CT
author: Mavis (chief-of-staff) — synthesized from Mavis-native Researcher ledger
for: Andre
model: M3
related_plans: [plan_cbc0bb0b (cancelled, ledger preserved)]
ledger_sources:
  claims: 03 Projects/Researcher/knowledge/claims.jsonl (clm-2026-06-07-001..016)
  findings: 03 Projects/Researcher/knowledge/findings.jsonl (18 entries)
  sources: 03 Projects/Researcher/knowledge/sources.jsonl (34 entries)
harness_decision: locked (Q1, 2026-06-07) — P50<2s, P95<8s, max 3 concurrent workers
phase_decisions: locked (2026-06-07 12:55 CT) — see Section 6a
---

# Phase Next Mavis Architecture

> v1 design synthesis. Mavis's next architectural phase: how to use M3 + the macOS Desktop App, how to scale context engineering to 100k+ vault tokens, and what the permanent runtime harness looks like. Synthesized from the Mavis-native Researcher's REFRESH-stage ledger (10 verified claims, 18 findings, 34 sources) plus the load-bearing vault notes.

## 1. Executive summary

M3 + the macOS Desktop App together are Mavis's load-bearing delivery surface for the companion-mode thesis. The chat API is a friction-bottleneck; the desktop app is what makes "presence on the Mac" possible (filesystem MCP, computer use, on-device state). The companion-mode reframe (Mavis as a stable, on-device presence rather than a chat reply) only becomes real when Mavis has desktop-level hooks — not just API calls.

Scaling context to 100k+ vault tokens is a **solved architectural problem** in 2026. The three-tier loader (meta-index → topic index → full topic) is the canonical pattern; the engineering primitives (MemGPT memory blocks, context trees, token-budgeted RAG, importance-aware eviction) exist. The leverage is in the operator-loop arithmetic: meta-index (~5KB) + system prompt + tool defs (~10–30KB) + 1–3 active topic-index entries (~10–50KB) + recent-turn context (~5–15KB) = ~30–100KB per turn, well under any latency ceiling. P50<2s / P95<8s is achievable with proper tiering and importance-aware eviction.

The Mavis Harness is a three-component runtime (`command_router`, `context_loader`, `scaffolding_review`) that maps 1:1 onto 2026 industry patterns (LangChain's harness move from #30 to #5 on Terminal-Bench 2.0 with the same model; Fudan's AHE +7.3 points via observability-driven harness self-evolution). The harness is the load-bearing production surface, not a wrapper around the model. Model drift is the primary failure mode; scaffolding-review crons are the safety net.

The three streams compound at exactly one axis: **Mavis as a desktop presence, with a hierarchical memory loader, governed by a self-reviewing harness.** That axis is the spine. Everything else (Skills, MCPs, tool integrations) is surface area on top of the spine.

## 2. Stream 1 — Minimax M3 & macOS Desktop App Synergy

**The thesis:** M3 is the load-bearing model for Mavis's next phase. It is the first open-weights model to ship 1M context (via MSA, ~1/20 the per-token compute of prior gen), native multimodality, and desktop computer use together. SWE-Bench Pro 59% (beats GPT-5.5, Gemini 3.1 Pro, approaches Opus 4.7), Claw-Eval highest score. Compatible with Claude Code and MCP protocol, supports cloud and local deployment (clm-2026-06-07-001).

**The surface:** Mavis's Mac-native presence is the load-bearing delivery surface for the companion-mode thesis. The 2026 stack is filesystem MCP (3-click install) + computer use (built-in MCP, no Docker/VM) + on-device state. Standard chat API is a friction-bottleneck (per-request token overhead, session fragmentation, no on-device FS). The desktop app is what makes "presence on the Mac" possible, not "a chat surface" (clm-2026-06-07-002).

**The protocol:** MCP is the de facto Agent-tool integration protocol (>97–110M monthly downloads, 4000+ servers, Linux Foundation stewardship). For a single-machine Mac deployment, the right pattern is the three-layer connection stack: **Skills** (domain knowledge in Markdown) + **CLI/Computer Use** (local execution, ~200 tokens/response, near-100% reliable) + **MCP** (selectively, for tasks that need OAuth/audit/governance) (clm-2026-06-07-003).

### Architectural hooks for the desktop app

Mavis's interface with the desktop app should bypass standard API friction at four specific points:

1. **Filesystem read path** — Read vault files directly via filesystem MCP. No HTTP roundtrip, no token overhead from API serialization. Single-shot reads of full-topic tier (Tier 3) are 1-50KB. Reads should be lazy and TTL-cached.

2. **Filesystem write path** — Atomic write pattern: write to temp file → fsync → rename. No partial writes visible to subsequent reads. Lock semantics: advisory file locks per (note-path, mtime-hash) for concurrent writers.

3. **Computer use (visual surface)** — Screenshot → vision-M3 → action primitives (click, type, key, scroll) → OCR round-trip for verification. Use for: scaffolding_review (visually verify Mavis's own surfaces), Telegram-side replies, any UI flow that doesn't have a programmatic API. Cost is ~200 tokens per action; reliability is near-100% for standard UI elements.

4. **Local state for the harness** — The `command_router` regex index, the `context_loader` cache, and the `scaffolding_review` health receipts all live in `~/MiniMax-Agent/.mavis/state/` (or wherever the vault-local state dir ends up). On-device means the harness is inspectable, debuggable, and replayable.

**Why this matters:** the desktop app turns Mavis from "a chat you go to" into "a presence on your Mac." For companion-mode to be a real product (not a metaphor), Mavis needs to be visually present — menu bar, notification surface, idle screen — and able to act on the desktop, not just in a chat panel.

## 3. Stream 2 — Context Engineering for 100k+ Vaults

**The thesis:** Hierarchical context loading for 100k+ vaults is a solved architectural problem in 2026. The three-tier pattern (meta-index → topic index → full topic) maps 1:1 onto: MemGPT/Letta Memory Blocks + Context Tree (AKL) + file-tree paging. Token-budgeted RAG (AdaGReS, TeaRAG) and importance-aware eviction (PagedEviction) provide the engineering primitives. The leverage: meta-index always-loaded (~3-8KB), topic indexes lazy (1-5KB each, on demand, TTL-cached), full topic loaded only when the user asks a question that requires it (clm-2026-06-07-004).

**The arithmetic (the load-bearing piece):** Mavis's operator-loop budget (P50<2s, P95<8s, locked 2026-06-07 Q1) is achievable at 100k+ vault tokens with the three-tier loader + cache-aligned prefix + importance-aware eviction. Per-turn token budget:

| Tier | Size | Loaded when | Frequency |
|------|------|-------------|-----------|
| Meta-index | 3-8KB | every turn | always |
| System prompt + tool defs | 10-30KB | every turn | always |
| Active topic indexes (1-3) | 10-50KB | per turn | per topic reference |
| Full topic (Tier 3) | 1-50KB | on demand | only when user asks |
| Recent-turn context | 5-15KB | every turn | always |
| **Total per turn** | **30-150KB** | | |

Well under any 200K context window. P50 fits in cache-warm path; P95 escapes are cache-miss + Tier 3 load + compression, which is bounded by the importance-aware eviction policy. The meta-index never goes cold (clm-2026-06-07-005).

**Eviction policy:** importance-aware, not LRU. A topic is evicted when (recency × user-intent-weight × freshness) falls below a threshold. The freshness dimension is what makes the loader different from a cache — a note cited 30 days ago that hasn't been re-verified should be re-loaded from source, not served from cache. This connects to the Researcher's context_decay_days discipline (already in `claims.jsonl` schema).

**Perfect-recall guarantee:** when the user asks about a topic that fell out of cache, the loader fetches the full topic from the filesystem, evicts the lowest-importance active topic, and serves the new one. Latency cost: 1 filesystem read + 1 cache swap. Bounded by file size and FS speed — typically <50ms for a single note. P95 spike on a "this user asked something exotic" question is a 1-second cost, not a 10-second one (clm-2026-06-07-008).

**The Lost-in-the-Middle problem:** Liu et al. 2023 documented the U-shaped attention curve. Mitigation: the meta-index always-loaded, full topics always-loaded with intent-key in the immediate context window (not "in the middle" of long context), recent-turn context pinned to the end (where attention is best). The loader's job is to keep the *active* context shaped for attention, not just for size.

## 4. Stream 3 — The Mavis Harness

**The thesis:** The agent harness is the load-bearing production surface. The 2026 evidence: LangChain moved from outside top 30 to rank 5 on Terminal Bench 2.0 (same model) via harness engineering. OpenAI's Codex shipped 1M+ lines of production code with zero human-written lines. Phil Schmid: the harness is the primary tool for solving model drift. Fudan's AHE added 7.3 points on Terminal-Bench 2.0 via observability-driven harness self-evolution (clm-2026-06-07-006).

Mavis's three-component harness (command_router, context_loader, scaffolding_review) maps 1:1 onto the 2026 industry patterns (clm-2026-06-07-007). Each component has a defined contract; the components compose.

### 4.1 `command_router`

**Purpose:** classify incoming user requests and route them to the right execution lane. Fail-closed: unmatched requests route to "ask first," not "guess and execute."

| Layer | Mechanism | Latency | Coverage |
|-------|-----------|---------|----------|
| L1 | Regex pre-filter (whitelisted commands, slash commands, "go/yes/no" replies) | <1ms | ~80% of fixed commands |
| L2 | Vector similarity against a labeled intent bank | ~50ms | ~95% of known intents |
| L3 | M3 LLM classification with structured output | ~1-3s | long tail |

**Inputs:** raw user text + (optionally) recent-turn context for disambiguation.
**Outputs:** classified intent + payload + confidence score.
**Execution lanes:** `capture` (write to inbox/notes), `synthesize` (chief-of-staff synthesis), `dispatch` (file-based handoff to a worker queue), `observe` (read-only inspection), `ask-first` (route back to user with a clarifying question).
**Failure modes:**
- Ambiguous match (L2 + L3 disagree) → default to ask-first with the two candidates shown
- Never-match → ask-first
- Over-match (regex fires for unintended input) → strict ordering of L1 rules; rule order is reviewable in the scaffolding_review cron
- The dispatch lane routes to a *file-based handoff* (queue/decision.md), not a worker-spawn. The Mavis-vs-Hermes boundary (Mavis may peek, may not manage) means command_router never directly spawns a worker; it writes a routing note (clm-2026-06-07-009).

**Model routing:** L1 is regex (no model). L2 is a small embedding model (M2.7-class, fast). L3 is M3 (for ambiguous or novel requests). Mavis (the chief) reads L3 outputs; M3-as-worker is what runs L3.

### 4.2 `context_loader`

**Purpose:** load the right tier of context for each Mavis turn, under the latency budget.

**Inputs:** command_router's intent classification + recent-turn context + the meta-index (always-loaded).
**Outputs:** a context window of 30-150KB, structured as [system prompt | meta-index | active topic indexes (1-3) | full topic (0-1) | recent turns | user input].
**Side effects:** cache updates (TTL refresh, importance score updates, eviction decisions).
**Failure modes:**
- Cache miss on a needed topic → graceful re-load from filesystem; no silent failure
- Importance score drift → scaffolding_review re-evaluates weekly
- All tiers cold → 1-second cold-start cost; logged for review

**Model routing:** the loader is *not* a model. It's a deterministic data structure (LRU+importance cache) with optional LLM-assisted importance scoring. The model is invoked only for LLM-assisted importance scoring on Tier 3 eviction decisions (M2.7-class for the scoring step).

### 4.3 `scaffolding_review` crons

**Purpose:** periodic review of Mavis's own runtime scaffolding. Prevent framework drift and silent timeouts.

**Cadence:** at least daily, plus event-driven on major harness change. Two cron types:
- **Daily scaffolding health check** (every 24h) — score drift, last-review timestamp, anomalies flagged
- **Event-driven scaffolding review** (on harness change, on major model update, on observed anomaly) — full re-audit

**Inputs:** command_router stats (L1/L2/L3 hit rates, ambiguous-match counts, ask-first rate), context_loader stats (cache hit rate, P50/P95 latency, eviction patterns), the vault's knowledge freshness (Researcher's context_decay_days distribution), and a golden test suite that asserts the harness's documented contract.
**Outputs:** a scaffolding health receipt — drift score (0-1), anomalies flagged, recommendations. Persisted to `99 _system/scaffolding-reviews/YYYY-MM-DD.md` (or wherever the local state dir ends up).
**Side effects:** a "harness change detected" event is published for the Builder to act on if drift crosses a threshold.

**The 2026 evidence for this being load-bearing:** model drift is the primary failure mode (Phil Schmid); observability-driven harness self-evolution added 7.3 points on Terminal-Bench 2.0 (Fudan AHE); golden-test suite + CI is the eval-vault pattern (Motomtech) (clm-2026-06-07-010). For Mavis: daily scaffolding review + event-driven on harness change + scaffolding review is the eval-vault for the harness itself.

**Model routing:** scaffolding_review is an M3 task (synthesis + judgment, not M2.7's read/structure/cite floor). The cron dispatches a fresh Mavis session to run the review; the session reads the harness stats, runs the golden test suite, writes the health receipt, and exits.

## 5. Cross-stream synthesis

### Where the streams COMPOUND

**Stream 1 (desktop) + Stream 2 (loader):** if Mavis is a desktop presence, the local FS access lets the context_loader bypass token cost on Tier 3 reads. Reading a full topic from the local FS is ~50ms; reading it through a hosted API is ~200-500ms (network + serialization). For the 1-3 full-topic loads per turn, that's 150ms-1.35s of saved latency. The desktop app makes the operator-loop budget *more* achievable, not less.

**Stream 2 (loader) + Stream 3 (router):** the router needs the meta-index to classify intent. The loader is what populates the meta-index. The two compose: the router classifies "user wants X" using the meta-index's section list; the loader then serves the relevant topic index. Without the meta-index, the router falls back to L3 (M3 classification) on every turn, blowing the latency budget.

**Stream 1 + Stream 3 (scaffolding_review):** Computer Use could be the scaffolding-review mechanism — visually verify Mavis's own surfaces (the menu bar, the notification surface, the chat surface) as part of the daily health check. This connects the desktop presence to the harness's self-review. Catches visual regressions, layout drift, and "the surface looks broken" failures that the harness stats alone wouldn't detect.

### Where the streams CONFLICT

**P95<8s vs perfect recall — resolvable, not a fundamental tension.** The resolution is: tiered loading is the answer, not "shove everything in 1M context." Meta-index always in window (1-2K tokens), topic indexes lazy (1-5K each, on demand, TTL-cached), full topic loaded only when the user asks a question that requires it. P95 latency spikes on cache miss: a "need this topic now" signal triggers load + compression, bounded by the importance-aware eviction policy. The user gets a 1-second spike on a "this user asked something exotic" question, not a 10-second one (clm-2026-06-07-008).

**Desktop app presence vs chat-surface simplicity — Mavis is both, but the mode-switching rule matters.** Mode-switching: if the user is in the chat surface, Mavis is in chat-mode (text I/O, command_router). If the user is in a desktop app context (menu bar, file action), Mavis is in desktop-mode (computer use, file I/O, on-device state). The transition rule: Mavis defaults to chat-mode unless the request originates from a desktop context (right-click on a file → "ask Mavis" → desktop-mode for that request). This is a design decision, not a hard conflict, but it needs to be explicit.

**Mavis-vs-Hermes boundary in the dispatch lane.** command_router's "dispatch" lane writes to a file-based handoff (queue/decision.md), not a worker-spawn. This is structurally sound (clm-2026-06-07-009) and locks the harness's interface surface. The trade-off: dispatch latency is bounded by the file-system roundtrip + the dispatcher's poll interval, not by direct spawning. For a chief-of-staff pattern where the user is waiting for a response, this is acceptable (file-writes are sub-10ms; the dispatcher polls every 1-5s).

## 6. Open questions for Andre

These are decisions only Andre can make. Surface them, don't resolve them.

1. **Menu bar presence.** Should Mavis be visible in the macOS menu bar? If yes, the menu bar item is a presence signal (idle, active, attention-needed). If no, Mavis stays a chat-surface-only presence and the companion-mode thesis is partially compromised. The design works either way; the choice is about how *visible* companion-mode is.

2. **Meta-index human-editability.** Should the meta-index (the always-loaded section headers + 1-line summaries) be human-editable? Pro: lets Andre override Mavis's auto-generated index. Con: drift between human-edited and auto-generated state. The Researcher's REFRESH mode currently regenerates the meta-index; making it human-editable adds a "respect manual edits" pass.

3. **Scaffolding-review opt-in vs opt-out.** The daily scaffolding review runs as a cron. Should it be opt-in (Andre enables it) or opt-out (it's on by default, Andre can disable)? The 2026 evidence says observability-driven self-evolution is the load-bearing pattern (Fudan AHE +7.3 points). But the user might want a quiet Mavis that doesn't review itself. Default to opt-out (it's on; user can disable in config) is the more conservative position; opt-in is more deferential.

4. **Tier 3 cache TTL.** How long should a full topic stay in the active cache before eviction? Default: until importance score falls below threshold. Alternative: fixed TTL (e.g., 30 min) regardless of importance. The fixed-TTL option is simpler but less responsive to user intent; the importance-score option is more adaptive but requires more compute for the scoring step. Recommend: importance-score with a 30-min hard floor (never evict in <30 min regardless of score).

5. **Computer Use reliability floor.** Computer Use is near-100% reliable for standard UI elements but degrades for custom-drawn surfaces. What's the reliability floor Mavis should require before falling back to a different mechanism? Default: 95% (fall back to ask-first or to a chat reply if computer use fails twice on the same action). The number is a design parameter; Andre may want different thresholds for different action types.

6. **M2.7 vs M3 model routing in the harness.** The plan called for M2.7 for the worker (cost floor). The actual session ran on M3 (the Researcher's default). Should Mavis workers be M2.7-enforced, or is the default M3 acceptable? M3 is higher capability but ~1.8x the output cost on the same plan. For a chief-of-staff running on the Mavis token plan, the M2.7 floor is the cost discipline; M3 is the quality floor. The choice is about where the chief draws the line.

## 6a. Andre's locked decisions (2026-06-07 12:55 CT)

1. **Menu bar presence — YES.** Companion-mode requires a persistent visual presence. The Mac menu bar is Mavis's primary state/attention signal.
2. **Meta-index editability — NO.** Mavis owns the index. Auto-generated only, prevent human/machine state drift.
3. **Scaffolding-review — OPT-OUT (on by default).** Observability-driven self-evolution is active. Daily crons run.
4. **Tier 3 cache TTL — Importance-score with 30-min hard floor.** Never evict before 30 min regardless of score.
5. **Computer Use reliability floor — 95%.** If an action fails twice, fall back to ask-first.
6. **Model routing — M2.7 ENFORCED for workers.** M3 reserved strictly for Mavis-the-chief (synthesis, orchestration, scaffolding reviews). Cost discipline is absolute.

## 7. Cross-references

- [[02 Notes/patterns/agent-harness]] — 12-component harness pattern, future-proofing test
- [[02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness]] — harness deep-dive
- [[02 Notes/ideas/Context Engineering 1M]] — 1M context as marketing claim
- [[02 Notes/ideas/Context Compression as First-Class Layer]] — compression as a layer
- [[02 Notes/ideas/Blockwise Paging for Long Context]] — blockwise paging
- [[02 Notes/patterns/Hot-Cold Inference Tiers on Apple Silicon]] — Apple Silicon substrate
- [[02 Notes/patterns/Paged Memory Pattern]] — paged memory
- [[02 Notes/ideas/Markdown as Universal LLM Interchange]] — markdown as interchange
- [[02 Notes/ideas/Memory Bandwidth is the Real LLM Inference Ceiling]] — bandwidth ceiling
- [[02 Notes/ideas/Mavis-Apex-Architecture]] — Mavis's prior architecture direction (Mavis-Apex predates this design)
- [[02 Notes/ideas/mavis-as-companion]] — companion-mode reframe (M3, 2026-06-04)
- [[MAVIS]] — weekly context (refreshed 2026-06-07)
- [[01 Daily/2026-06-04]] — Night Flight cascade (token-budget reality)
- [[01 Daily/2026-06-07]] — this morning's sweep (boundary lock, unblock, pivot)
- [[00 Inbox/2026-06-07 - Hermes Blocked Items Decision Context]] — Q1 latency/cost/safety criteria
- [[03 Projects/Researcher/knowledge/claims.jsonl]] — 10 verified claims (clm-2026-06-07-001..010) underpinning this doc
- [[03 Projects/Researcher/knowledge/findings.jsonl]] — 18 findings extracted during REFRESH
- [[03 Projects/Researcher/knowledge/sources.jsonl]] — 34 primary sources

---

*Status: APPROVED. The Mavis-native Researcher's first attempt stalled mid-design-doc writing; the second attempt was on the same trajectory. Owner (Mavis, on M3) took over and synthesized this from the 10 verified claims + vault pointers + spec. Andre approved 2026-06-07 12:55 CT and locked the 6 architectural decisions (Section 6a). Implementation is the next phase; the Mavis Harness scaffold is the first deliverable.*
