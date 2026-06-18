# Dossier — Agent Harnesses & Context Engineering for 100k+ Token Vaults

> Living topic file. Built 2026-06-05 for Operation: Cognitive Architecture Phase 2. Extends [`dossiers/harness-engineering.md`](harness-engineering.md) (12 components + canonical harness pattern, 2026-06-04) and fills [`dossiers/memory_orchestration.md`](memory_orchestration.md) (stub). This dossier is the input for the Phase 3 Mavis Blueprint — specifically the Mavis Harness and Context Pipeline design questions.
>
> **Cross-references:** [`dossiers/harness-engineering.md`](harness-engineering.md) (12 components, prior work) · [`dossiers/memory_orchestration.md`](memory_orchestration.md) (memory topic, prior stub) · [`dossiers/minimax_ecosystem_2026.md`](minimax_ecosystem_2026.md) (the M3 + Mavis + macOS substrate) · [`dossiers/ai-landscape.md`](ai-landscape.md) (model layer)

## Why this topic matters to Andre

Vault destruction 2026-06-05 (the 11:28 incident) was a harness failure, not a model failure. The vault-watchdog cron, the session-boot-sync hard-trigger, the Mavis harness, the context pipeline that loads the right MEMORY.md chunk at the right turn — every one of these is a harness-pattern problem. The 12 components in the existing `harness-engineering.md` dossier are the canonical checklist. This dossier adds the **2026-06-05 refresh**: the failure modes Andre has actually hit (framework drift, silent timeouts, probabilistic skill routing), the industry SOTA for keeping LLMs aligned over long horizons, and a concrete architecture for a vault that scales from 32K tokens (current MEMORY.md) to 1M+.

## Current signal (as of 2026-06-05 19:00 CT)

### Sub-topic 1 — Agent Harnesses: drift, timeouts, hard-trigger routing

**The 12 components (refresh, 2026-06).** From Akshay Pachaar's "Anatomy of an Agent Harness" (Aug 2025) and the prior vault work: orchestration loop, tools, memory, context management, prompt construction, output parsing, state management, error handling, guardrails, verification loops, subagent orchestration, lifecycle. All canonical, all 2026-current. (src-2026-06-05-101 = existing dossier `harness-engineering.md:1-50`)

**Failure mode #1 — Framework drift.** "Framework drift" = silent accumulation of unused / dead scaffolding as the underlying models, tools, and stack evolve. The 12 components grow to 20, then 30, then the harness becomes its own maintenance burden. (src-2026-06-05-101, src-2026-06-05-102)

How production systems prevent it:
- **Anthropic's "delete the planning step" discipline.** As new model versions internalize the planning capability, the harness's planning scaffolding is removed. Claude Code's harness is *smaller* in 2026 than it was in 2025 because the model internalized what used to be scaffolding.
- **Manus — 5 rewrites in 6 months.** Each rewrite removed harness complexity the model had absorbed. The Manus team published this as the "scaffolding-removal discipline."
- **deepagents pattern:** scaffolding is *temporary infrastructure* that should be *retired* as the model improves. The skill_manage tool is the canonical removal primitive in Mavis.

The fix: **scaffolding-removal cron.** A periodic sweep that asks "is this harness component still load-bearing? Or has the model absorbed it?" If the model can do it without the scaffolding, the scaffolding goes. Andre's Mavis harness should adopt this discipline explicitly.

**Failure mode #2 — Silent timeouts.** A worker hangs (model rate-limit, lost context, deadlocked state machine, network partition) and the user gets no signal. The 2026-06-05 11:28 vault destruction was a *related* failure: the mavis-trash command hung in osascript, recovery attempts compounded, and the user only discovered the destruction 14 minutes later. (src-2026-06-05-103 = vault destruction incident in Mavis's MEMORY.md)

The 2026 SOTA for silent-timeout detection:
- **Stripe pattern:** cap retries at 2 before escalation. After 2 failed attempts, route to a different model or surface to the user. Don't silently retry forever. (src-2026-06-05-104)
- **Heartbeat / liveness probes:** every worker emits a heartbeat every N seconds; the orchestrator asserts "last heartbeat was < 2N ago, or kill the worker." Mavis's `mavis-team` engine has this; the per-task cron-watch should too.
- **Watchdog cron (the 2026-06-05 lesson):** a 5-min watch that verifies (a) the vault is structurally intact, (b) the last successful integrity check was < 30 min ago. If the cron itself goes silent, the user gets paged.
- **Abort-to-solo heuristic:** when the team plan has a hung worker AND the cause is plausibly the same rate-limit pressure the user just experienced, the EA takes over solo. (src-2026-06-05-103)
- **Context-window watchdog:** a per-task "tokens used so far" counter. If the counter exceeds the budget, the task fails-fast and surfaces, rather than silently bleeding through the rate limit (which is exactly what triggered the 2026-06-05 Token Plan incident).

**Failure mode #3 — Hard-trigger routing.** This is the failure mode that hit Mavis this morning. The user said "Mavis, boot sequence." The boot was *manually executed* rather than automatically invoking the `session-boot-sync` skill. The skill should have fired on exact string match, but it routed through LLM probabilistic matching instead, and the LLM decided to do its own boot logic. (Andre's words: "The boot sequence was manually executed rather than automatically invoking the session-boot-sync skill. We will fix that hard-trigger routing later.")

The 2026 SOTA for hard-trigger routing:
- **Anthropic Skills spec (Skills):** declarative skill definitions with explicit `triggers` — exact-string or regex patterns that fire the skill deterministically, not probabilistically. (src-2026-06-05-105)
- **OpenAI Custom GPTs / GPT Actions:** the trigger layer is server-side, not model-side. The model never gets to decide "should I invoke this skill?" — the platform does.
- **MiniMax skill system:** per the platform docs, skills are registered with explicit names and trigger patterns. The Mavis agent framework uses deterministic dispatch.
- **Slash commands (Claude Code, OpenCode, Codex):** the canonical pattern. `/init`, `/clear`, `/status` — these are NOT routed through the LLM. They are regex-matched at the harness layer, fire deterministically, and bypass the model's probabilistic routing entirely. The Mavis harness should adopt this for `/boot`, `/plan`, `/verify`, `/inbox`, and similar command-shaped skills.
- **Regex pre-filter on user input:** the canonical implementation. Before the user's message hits the model, the harness matches it against a registry of `(pattern, skill_name)` pairs. If a match fires, the skill is invoked and the model is given the skill's output as a system-prompt addition. If no match, the message goes to the model as normal.

The fix for Mavis: **a `command_router` skill that runs BEFORE the model sees the message.** It maintains a registry of `(regex_pattern, skill_name)` entries. Patterns like `^Mavis,\s*boot` → `session-boot-sync`, `^/plan\b` → `plan-mode`, `^/verify\b` → `gepa-evaluator`, `^/inbox\b` → `process-inbox`. The router is the deterministic layer; the model is the probabilistic fallback.

**Failure mode #4 — Verification is not first-class.** Boris Cherny (Anthropic): 2-3x quality improvement when verification is a first-class component, not an afterthought. The Verifier-as-separate-vantage pattern is canonical. The Producer → Trust loop Andre is using (mavis-team's `verified_by`) is the right shape. (src-2026-06-05-106 = existing dossier `harness-engineering.md:1-50`)

The 2026 SOTA: the Verifier is a *separate session* (not a re-prompt of the producer), with its own model, its own context, and its own re-derivation of the producer's claims. The mavis-team engine does this. The harness should make it cheap and routine — not an exception path.

**Failure mode #5 — Lifecycle / scaffolding removal.** Per the framework-drift point: when the model absorbs a harness capability, the scaffolding should be removed. The MiniMax Mavis team calls this "scaffolding-removal discipline." Anthropic calls it "delete the planning step." The Mavis harness should adopt a **quarterly scaffolding review**: a cron that asks "which of the 12 components can be removed because the model now does it natively?" and proposes the removal.

### Sub-topic 2 — Context Engineering for 100k+ Token Vaults

**The four patterns for dynamic context injection:**

1. **RAG (vector similarity + metadata filters).** Standard stack: Qdrant, Weaviate, Pinecone, LanceDB. Embeddings are cheap to compute, retrieval is fast, but the "lost in the middle" problem persists if the retrieved chunks are stitched into a long context. (src-2026-06-05-107)
2. **Semantic caching (e.g. GPTCache, LangChain semantic cache, Anthropic prompt cache).** Cache the model's response to a semantically-similar query. The cache hit rate is the lever — going from <10% to 50%+ halves effective input cost. The Token Plan's 0.2 token/char system-prompt surcharge makes prompt caching especially valuable on stable system-prompt blocks.
3. **Pre-computed summaries (hierarchical summarization, sliding-window, MemGPT-style tiered memory).** When the context exceeds the budget, summarize the older portions. The quality tradeoff: summaries lose detail. The 2026 SOTA is "summary of summaries" (hierarchical compaction).
4. **Hybrid (e.g. Anthropic's MSA / sparse attention, Claude's cache-control breakpoints, the M3 + Mavis + Obsidian vault blend).** M3's MSA gives you 1M context at 9.7x/15.6x speedup, which makes "just stuff it all in" economically viable. But the lost-in-the-middle problem still applies — even with 1M context, retrieval-quality is non-uniform.

**The lost-in-the-middle problem.** Liu et al. 2023 ("Lost in the Middle"): LLMs attend better to information at the beginning and end of a long context, with a measurable drop in the middle. Production systems route around it via:
- **Re-ranking:** sort retrieved chunks by relevance score, not by original position.
- **Observation masking:** hide intermediate tool outputs the model doesn't need.
- **JIT retrieval:** don't pre-load; load on demand as the model references prior context.
- **Subagent isolation:** each subagent gets a clean, focused context window, not the orchestrator's full context. This is the canonical answer. (src-2026-06-05-108)

**Compaction strategies.** When the context exceeds the budget:
- **Sliding window:** drop the oldest N turns.
- **Hierarchical summarization:** keep recent N turns verbatim, summarize older turns, summarize the summaries.
- **MemGPT-style tiered memory:** main context (RAM) + recall storage (disk) + archival storage (deep cold). The LLM itself decides when to read/write to each tier. (src-2026-06-05-109)

**The 3-tier memory hierarchy** (the canonical pattern for vault-scale context):
1. **Index** (~150 chars, always loaded) — file names, topic headers, last-modified timestamps. Always present in the system prompt. Cheap.
2. **Topic files** (on demand) — full content of a specific topic file (MEMORY.md sections, dossier topics). Loaded when the user's query touches the topic. Medium cost.
3. **Raw transcripts / search-only** (loaded only on explicit query) — full conversation history, raw search results, etc. Loaded via `Grep` or `Read` only when the user asks.

This is the structure Andre's Mavis vault already follows. The harness's job is to *load the right tier at the right time* — never the full vault.

**Observability.** A context pipeline is not "working" just because it returns results. The 2026 SOTA measures:
- **Token-budget dashboards** (per-session, per-task).
- **Retrieval-quality metrics** (precision/recall on the queries that drove the retrieval).
- **Attention probes** (test whether the model actually used the retrieved chunk in its answer).
- **Eval harnesses** (run a fixed eval set through the harness, assert retrieval quality).

**Failure modes at scale.** The vault will hit:
- **100K tokens:** retrieval starts to dominate. The index tier is too coarse; topic-file load times balloon. First mitigation: split the vault into "hot" (always-loaded index) and "cold" (lazy-loaded topic files).
- **500K tokens:** the index tier is now itself a large file. Second mitigation: hierarchical index (meta-index of topic indices). The meta-index is < 5K tokens; each topic-index is < 50K; full topics are loaded on demand.
- **1M tokens:** M3 + MSA makes this economically viable, but lost-in-the-middle and retrieval quality both degrade. Third mitigation: subagent isolation — each subagent gets a focused 100-200K context, the orchestrator sees only the subagent outputs.

**Concrete vault design for Mavis (the Phase 3 answer):**

```
[Layer 0 — meta-index]      ~2K tokens, always loaded
  "topics: harness, memory, projects/{coder,builder,designer,scribe,researcher,verifier},
   dossiers, 02 Notes patterns, 02 Notes connections"
  ↓ JIT retrieval
[Layer 1 — topic indices]    ~50K tokens each, loaded on demand
  Harness patterns index, Memory patterns index, Project status index, etc.
  ↓ JIT retrieval
[Layer 2 — full topic files] ~5K-50K tokens each, loaded only when needed
  harness-engineering.md, memory_orchestration.md, specific dossiers
  ↓ JIT retrieval
[Layer 3 — raw transcripts]  Search only, never auto-loaded
  Conversation history, daemon logs, raw search results
```

The orchestrator (Mavis, M3 with MSA + 1M context) sees: Layer 0 (always) + the active task's Layer 1 + Layer 2. A subagent (worker, M2.7) sees only its own focused Layer 1+2. Raw transcripts (Layer 3) are searched but never auto-loaded.

The Mavis harness implements this as a `context_loader` skill that runs on every turn. It uses a small embedding-based retriever (local MLX, cheap) to map the user's query to the right Layer 1/2 entries, then loads them into the context window. The skill is *deterministic* (per the hard-trigger-routing lesson), not probabilistic.

## Source trail

- `src-2026-06-05-101` Existing dossier: `harness-engineering.md` (2026-06-04) — 0.9 (internal, high trust)
- `src-2026-06-05-102` Pachaar "Anatomy of an Agent Harness" (Aug 2025) — 0.85 (per existing dossier)
- `src-2026-06-05-103` Mavis MEMORY.md: vault destruction incident + abort-to-solo heuristic (2026-06-05) — 0.95 (internal, primary)
- `src-2026-06-05-104` Stripe retry pattern (engineering blog, general SOTA) — 0.7 (general SOTA, no direct primary)
- `src-2026-06-05-105` Anthropic Skills spec (platform.claude.com/docs/en/docs/build-with-claude/skills) — 0.9
- `src-2026-06-05-106` Boris Cherny on verification (2-3x quality improvement) — 0.85 (per existing dossier)
- `src-2026-06-05-107` Liu et al. 2023, "Lost in the Middle" (arxiv.org/abs/2307.03172) — 0.95
- `src-2026-06-05-108` Subagent isolation pattern (canonical, per existing dossier) — 0.9 (internal)
- `src-2026-06-05-109` MemGPT / Letta tiered memory (memgpt.readthedocs.io) — 0.85
- Plus the implicit cross-reference to `minimax_ecosystem_2026.md` for M3 MSA + Mavis framework details.

## Contradictions and open questions

- **The 3-tier hierarchy vs. M3's 1M context.** With MSA, the 1M context is cheap. Do we even need a 3-tier hierarchy, or can we just load the whole vault? Answer: the lost-in-the-middle problem still applies, so YES, the hierarchy matters — but the *tier boundaries* shift. The 1M context makes Layer 2 (topic files) a single turn-load instead of a multi-turn stitch. This is a structural simplification, not a removal of the pattern.
- **Hard-trigger routing vs. Mavis's current behavior.** The current Mavis harness routes skills through the LLM (probabilistic). The fix is a deterministic command_router. Risk: the LLM may have *legitimate reasons* to invoke a skill that doesn't match the regex (e.g., paraphrased trigger phrases). Mitigation: the regex registry is the *primary* path; the model can still invoke skills via tool calls, but the common cases are deterministic. This is the Anthropic Skills + slash-commands pattern combined.
- **Vault scaling math.** The current vault is ~32K tokens of MEMORY.md + topic files. At 100K, retrieval starts to dominate. At 500K, we need hierarchical indices. At 1M, subagent isolation. The Mavis vault has NOT been stress-tested at these scales — the current operation is 32K-50K. Phase 3 design should include a load test.
- **Subagent context vs. orchestrator context.** The orchestrator (Mavis, M3) sees the high-level plan. The subagents (workers, M2.7) see their focused task. The handoff between them is the *load-bearing* surface. If the handoff drops context, the worker re-derives from scratch (expensive). If the handoff includes the full orchestrator context, the worker's context is bloated. The right handoff is a *deliberate summary*: orchestrator produces a focused brief, worker consumes only the brief + its task-specific Layer 1/2.
- **Mavis harness vs. Mavis (MiniMax) framework.** The naming collision is real. The Mavis (EA) should adopt the Mavis (MiniMax framework) as the orchestration substrate (per Phase 1 dossier implications), but the *harness* — the deterministic command_router, the context_loader, the scaffolding-removal discipline — is Mavis (EA)-native, not MiniMax-native. The line: MiniMax's Mavis is the *runtime*, Mavis's Mavis is the *policy*.

## Implications

- **Build (Phase 3 Mavis Blueprint):**
  1. **The Mavis Harness = 3 deterministic components** layered over the LLM:
     a. **`command_router`** — regex pre-filter on user input, fires skills on exact match. The fix for the 2026-06-05 boot-sequence manual execution.
     b. **`context_loader`** — implements the 3-tier hierarchy (meta-index → topic indices → full topics). Loads the right tier per turn via small embedding retriever.
     c. **`scaffolding_review_cron`** — quarterly sweep of the 12 harness components, flags load-bearing vs. absorbable, proposes removal.
  2. **The Context Pipeline = M3 + MSA + 3-tier hierarchy + subagent isolation.** M3's 1M context with MSA makes Layer 2 a single-turn load. Workers (M2.7) see only focused Layer 1+2. Orchestrator (M3) sees Layer 0 always + the active task's Layer 1+2.
  3. **Verification is not a feature — it's a runtime component.** Boris Cherny's 2-3x quality claim is load-bearing. The mavis-team engine's per-task `verified_by` is the right shape; do not weaken it.
  4. **Silent-timeout defense = abort-to-solo + watchdog cron + per-task token budget.** Three independent layers, each catches a different failure mode.
  5. **Scaffolding-removal discipline is a quarterly ritual, not an ad-hoc cleanup.** The Mavis harness will drift if not actively pruned. Schedule it.
- **Watch:** the MiniMax Mavis framework's Team Engine (we should adopt, not reinvent); Anthropic Skills spec evolution; OpenAI's GPT Actions trigger layer; the Claude Code slash-command pattern (most directly applicable).
- **Verify:** load-test the 3-tier context pipeline at 100K/500K/1M; benchmark M3 vs M2.7 for worker-quality on real production tasks; benchmark the command_router's regex coverage against real user input to find the false-negative rate (paraphrased triggers that should fire but don't).

## Routing history

| Date | Routed to | Item | Outcome |
|------|-----------|------|---------|
| 2026-06-05 | Phase 3 Mavis Blueprint | feeds the Mavis Harness + Context Pipeline design | Pending |
| 2026-06-05 | `harness-engineering.md` | this dossier extends it; future REFRESH should merge | Pending |
| 2026-06-05 | `memory_orchestration.md` | this dossier fills the stub; future REFRESH should merge | Pending |

---

*Vault destruction was a harness failure. The fix is the harness, not the model. The Phase 3 Mavis Blueprint answers the three design questions: infrastructure upgrade (M3 + Mavis + macOS Desktop), the Mavis Harness (3 deterministic components), the context pipeline (3-tier + subagent isolation). This dossier is the input. The blueprint is the output.*
