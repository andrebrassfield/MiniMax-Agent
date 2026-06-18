# Mavis Harness Blueprint — Phase 3 Specification

> **Status:** DRAFT (awaiting Andre review)
> **Authored:** 2026-06-06 by Mavis (EA, synthesis)
> **Inputs:** Phase 1 dossier `minimax_ecosystem_2026.md` + Phase 2 dossier `harness_and_context_design.md` — both verified PASS on 2026-06-05
> **Promoted claims:** 11 (`clm-2026-06-05-009` through `clm-2026-06-05-019`)
> **UNVERIFIED holdouts:** 3 (model size, throughput, token multipliers — explicitly held pending primary source)
> **Intended consumer:** Builder agent for engineering sprint execution
> **Trust-loop posture:** This is a synthesis draft by the chief. Builder ships; Verifier re-audits before sprint commits merge to main.

---

## 0. Reading guide

- **§1 — The Core Substrate.** Adopt the official Mavis Team Engine (Leader/Worker/Verifier) as the orchestration runtime. We do NOT build a custom one.
- **§2 — The Context Pipeline.** 3-tier memory hierarchy + subagent isolation, sized for the verified 1M-token M3 context.
- **§3 — The Protection Layer.** Three defensive mechanisms that prevent the failure modes the 2026-06-05 operation surfaced: framework drift, long-inference aborts, production token accounting on unverified multipliers.
- **§4 — Cross-cutting.** Model routing, the 3 UNVERIFIED holdouts, sources-ledger hygiene.
- **§5 — Build sequencing.** Sprint order, dependencies, ship gates.
- **Appendix A — Claim traceability matrix.** Every design decision → its supporting claim IDs.

---

## 1. The Core Substrate — Mavis Team Engine

The orchestration layer is the **official Mavis Team Engine** from MiniMax (formerly MiniMax Agent, renamed 2026-05-13). We adopt it; we do not reinvent it. Per `clm-2026-06-05-013` (Mavis code-driven state machine, weight 0.80), the Team Engine is **code-driven, deterministic**, with a **mandatory Verifier role** for adversarial iteration. The same architecture that MiniMax's three-role Team Engine uses is structurally identical to the Producer→Trust loop `mavis-team` already implements.

### 1.1 Three-role instantiation

Per `clm-2026-06-05-019` (Mavis Leadership pattern, weight 0.85), the canonical role names are **Leader / Worker / Verifier** (NOT Owner/Worker/Verifier — that earlier draft was corrected against 4 independent launch-day Chinese press sources: 腾讯新闻, 网易, 硅星Breaknews, 爱范儿).

| Role | Model | Scope | Lifespan | Authority |
|---|---|---|---|---|
| **Leader** | M3 | Plan decomposition, user-facing dialogue, immediate response | Long-lived (chief session) | Sole authority to dispatch and accept; no worker self-promotes |
| **Worker** | M2.7 default; M3 for long-horizon (12h+) | Single focused task (read, build, write, code, cite) | Ephemeral (per-task) | Cannot dispatch other workers; cannot self-verify |
| **Verifier** | M2.7 | Adversarial re-derivation of one deliverable | Ephemeral (per-deliverable) | Mandatory gate; verdict is `VERDICT: PASS` or `VERDICT: FAIL` |

**Hard separation of authority.** A worker cannot promote its own output. A verifier cannot be the same session as the worker (per the Producer→Trust pattern: separate context, separate re-derivation). The leader is the only role that can accept a worker's output and only after a verifier has cleared it.

### 1.2 State machine topology

The Team Engine runtime is a code-driven state machine, not a prompt orchestrator. The state graph for any task:

```
INIT → PLAN → DISPATCH_WORKER → WORKER_RUNNING
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
       WORKER_DONE                                          WORKER_FAILED
            │                                                     │
            ▼                                                     │
     DISPATCH_VERIFIER ──── VERIFIER_RUNNING ──── VERIFIER_DONE   │
            │                                          │         │
            ▼                                          ▼         ▼
       VERDICT_PASS                                VERDICT_FAIL  RETRY
            │                                          │         │
            ▼                                          ▼         ▼
       ACCEPT                                     PATCH_REQUEST  (back to
            │                                          │         DISPATCH_WORKER,
            ▼                                          ▼         max 2 retries)
       RETURN_TO_USER                            (back to worker)
```

Each state transition is deterministic, code-driven, and observable. The runtime emits state-transition events that the leader subscribes to. No agent has the authority to skip a state.

### 1.3 Mavis CLI integration

The Mavis CLI (`platform.minimax.io/docs/token-plan/minimax-cli`) is the documented programmatic surface. It exposes:

- `mavis team spawn <role> --task <spec>` — create a worker or verifier session
- `mavis team state <session-id>` — read a session's current state
- `mavis team verdict <session-id>` — read the most recent verifier verdict
- `mavis team accept <session-id>` — leader accepts a verified deliverable

Per `clm-2026-06-05-014` (Mavis TokenPlan+AgentPlan merge, weight 0.85), the CLI is included in the merged TokenPlan subscription, so invocation is rate-limited against the same 5-hour rolling windows as the API. Per `clm-2026-06-05-015` (Token Plan rate windows, weight 0.9), the 5-hour rolling window + dynamic rate limiting during peak (15:00-17:30) is the verified pattern.

### 1.4 Why adopt, not build

- **Verified substrate exists.** Per `clm-2026-06-05-013`, MiniMax published a deep justification for the code-driven state machine runtime and the mandatory Verifier role. The 4 single-agent failure modes and the 5-10 min collapse claim are documented in the launch-day technical blog (src-2026-06-05-028 — note: the canonical blog is currently 404, but the architecture is independently confirmed by 4 launch-day press sources).
- **Convergence with our pattern.** The Producer→Trust loop in `mavis-team` is structurally identical. We get to adopt a battle-tested runtime without inventing a new one.
- **Cost of building is high; cost of adopting is low.** Per the dossier's implications section (line 187), the alternative ("build our own runtime") would have meant reproducing the state machine, the verifier gate, and the immediate-response/background-execution split. We are NOT doing that.

---

## 2. The Context Pipeline — 3-tier memory hierarchy

Per `clm-2026-06-05-018` (3-tier memory hierarchy, weight 0.85), the canonical 2026 pattern for vault-scale context is the Index / Topic files / Raw transcripts hierarchy with JIT retrieval. Per `clm-2026-06-05-017` (Liu et al. 2023 "Lost in the Middle", weight 0.95), the U-shaped attention curve still applies at any context size — including 1M — so the hierarchy is necessary, not optional.

Per `clm-2026-06-05-009` (M3 MSA architecture, weight 0.95), M3's MiniMax Sparse Attention makes the 1M context economically tractable (9.7x prefill, 15.6x decode speedup at 1M vs full-attention M2). This means Layer 2 (full topic files) can be a **single-turn load** instead of a multi-turn stitch.

### 2.1 Layer specifications

| Layer | Name | Size | Loaded | Content | Cost per load |
|---|---|---|---|---|---|
| **0** | Meta-index | ~2K tokens | Always (system prompt) | Topic names, dossier IDs, project hubs, current task queue | Always-on; no JIT cost |
| **1** | Topic indices | ~50K tokens each | JIT on demand | Table of contents, section headers, last-modified timestamps, key claims per topic file | ~1 embedding query + 1 retrieval |
| **2** | Full topic files | ~5K-50K tokens each | JIT on demand | Full content of one topic file | Single-turn load on M3 MSA; multi-turn stitch on M2.7 |
| **3** | Raw transcripts | unbounded | Search only, never auto-loaded | Conversation history, raw search results, daemon logs | `Grep` or `Read` only when explicitly queried |

### 2.2 M3 context economics

M3's 1M-token context with MSA makes Layer 2 a single-turn load. For the Chief (M3), the realistic budget per turn is:

- Layer 0 (always-on): 2K
- Active task's Layer 1+2: 50K + 50K = 100K
- Conversation history: 50K
- Buffer for retrieval + tool output: 50K
- **Total per turn: ~200K** (well under 1M)

This is the budget that makes the Chief's session sustainable. Workers (M2.7) have a tighter budget:

- Layer 0: 2K
- Single task's Layer 1+2: 50K + 50K = 100K
- Tool output: 30K
- **Total per turn: ~180K** (under M2.7's 200K-262K limit)

Per `clm-2026-06-05-016` (Token Plan June 5 apology, weight 0.85), MiniMax walked back the most aggressive limits and gave 3.22-pre subscribers no weekly cap. We are NOT 3.22-pre — our token budget needs to be conservative until/unless we negotiate similar terms.

### 2.3 Subagent isolation

Per the Producer→Trust pattern: each subagent gets a **focused context window**, not the chief's full context. The handoff is the load-bearing surface.

- **Chief (M3, Leader)** sees: Layer 0 always + the active task's Layer 1 + Layer 2
- **Worker (M2.7)** sees: only its task-specific Layer 1 + Layer 2 (no chief's conversation history, no peer workers' outputs)
- **Verifier (M2.7)** sees: only the worker's deliverable + Layer 0 (no worker context bleed)

The handoff from Chief to Worker is a **deliberate summary**, not a context dump. The Chief produces a focused brief (task spec + relevant Layer 1+2 entries), the Worker consumes only the brief + its task-specific Layer 1+2.

### 2.4 Lost-in-the-middle mitigations

Per `clm-2026-06-05-017`, even at 1M context the U-shaped attention curve applies. Mitigations built into the pipeline:

- **Re-ranking.** Sort retrieved chunks by relevance score, not by original position. The top-k retrieved chunks are placed at the START of the context window.
- **JIT retrieval.** Don't pre-load everything. Load on demand as the user references prior context. The chief's conversation buffer is bounded (50K, see §2.2).
- **Subagent isolation.** Each subagent gets a focused 100-200K context, not the chief's 200K+ buffer. The chief sees only the subagent outputs, not their full context.
- **Critical-info at the start/end.** System prompt has the role definition at the top and the verdict acceptance criteria at the bottom. Both get the attention peak.

---

## 3. The Protection Layer — Three defensive mechanisms

The 2026-06-05 operation surfaced three concrete failure modes. Each is addressed by a specific defensive mechanism in the harness.

### 3.1 `command_router` — the framework-drift defense

**Failure mode (2026-06-05 11:28 incident, vault destruction):** the user said "Mavis, boot sequence" — the boot was manually executed rather than automatically invoking the `session-boot-sync` skill. The skill should have fired on exact-string match, but it routed through LLM probabilistic matching instead, and the LLM decided to do its own boot logic.

**The mechanism:** a `command_router` skill that runs **BEFORE the model sees the user message**. It maintains a registry of `(regex_pattern, skill_name)` pairs. The router is the deterministic layer; the model is the probabilistic fallback.

**Initial registry (extend as we discover more command-shaped skills):**

| Regex | Skill | Trigger source |
|---|---|---|
| `^Mavis,\s*boot` | `session-boot-sync` | 2026-06-05 manual-execution incident |
| `^/plan\b` | `plan-mode` | Standard slash command |
| `^/verify\b` | `gepa-evaluator` | Standard slash command |
| `^/inbox\b` | `process-inbox` | Standard slash command |
| `^/health\b` | `gibson-watcher` | Standard slash command |
| `^/research\b` | `mavis-team-plan` | Chief's research dispatch |
| `^/blueprint\b` | `blueprint-mode` | Phase 3 directive pattern |

**Implementation:**
- The `command_router` skill runs as the first step of every chief turn
- Reads the user message, matches against the registry
- On match: invokes the skill, augments the model's input with the skill's output as a system-prompt addition
- On no match: message goes to the model as normal
- The router is a code path, not an LLM call — deterministic, observable, debuggable

**Why this fixes framework drift:** skill routing no longer depends on the LLM deciding "should I invoke this skill?" The platform does. Per MiniMax's published rationale (per `clm-2026-06-05-013`), prompt-driven role play collapses at the 5-10 min horizon — the same is true for prompt-driven skill routing. The router is the deterministic layer that prevents that collapse.

### 3.2 Chunked-write discipline — the long-inference-abort defense

**Failure mode (Operation: Cognitive Architecture 2026-06-05):** a Verifier session (M2.7) completed all 8 verification work items + adversarial probes in context, then attempted to write a final audit report. The Write aborted on the long-inference ceiling. The substantive verdict was in the worker's head/context but was NEVER delivered to the parent.

**The mechanism:** every long-form generation (dossiers, audits, build specs, blueprints) MUST be chunked into smaller Writes, with checkpoints between.

**Discipline (mandatory for any agent producing >30KB output):**

1. **Plan the sections first.** Use TodoWrite to list the deliverable's sections before any Write.
2. **Write in sections.** Each Write is ≤30KB. First Write: frontmatter + section 1. Second Write: section 2. Etc.
3. **Checkpoint to disk after each section.** A section is not "done" until it's on disk, not just in context.
4. **Cap parallel research calls to 4-6 per turn.** If a session is doing heavy web research, run subsequent batches in later turns, after checkpointing what you have.
5. **Verdict-before-synthesis for async verifiers.** Send the verdict message (`VERDICT: PASS` or `VERDICT: FAIL`) BEFORE writing the final synthesis. The verdict is the parent's permission to act; the synthesis is the human-readable deliverable. If the synthesis write aborts, the parent still has the verdict.

**Tooling support (build in Sprint 4):**
- A `chunked-write` library that takes a list of sections and writes them one-by-one
- A `checkpoint` helper that appends a section to a file and reports the new size
- An `auto-section` helper that splits a large Write at logical boundaries (headings)

**The architectural contract:** any agent producing >30KB output MUST use chunked-write. The Verifier checks for chunked-write compliance in its re-audit.

### 3.3 Dynamic token multiplier configuration — the production-accounting defense

**Failure mode (2026-06-05 audit, Cluster C):** the dossier's claim that M3's Token Plan applies 1.3x input / 1.8x output multipliers + 0.2 token/char system-prompt surcharge could NOT be verified in primary sources. The Token Plan FAQ and Rate Limits page do not contain these numbers. If the harness had baked them in, token accounting would have been systematically wrong.

**The mechanism:** the token multiplier layer is **runtime-configurable, NOT hardcoded**. The harness reads the multipliers from a config file at every accounting event. Until a primary source confirms the multipliers, the config defaults to 1.0/1.0/0.0 (verified base rates only).

**Config file shape (proposed `config/token-plan.yaml`):**

```yaml
# Token Plan multipliers — UNVERIFIED in primary sources as of 2026-06-05.
# Default: 1.0/1.0/0.0 (verified base rates only).
# Update ONLY after primary-source confirmation (e.g., a new Token Plan FAQ entry
# explicitly documenting these numbers).
multipliers:
  input_rate: 1.0           # UNVERIFIED, default 1.0
  output_rate: 1.0          # UNVERIFIED, default 1.0
  system_prompt_per_char: 0.0  # UNVERIFIED, default 0.0

# Base rates — VERIFIED via OpenRouter + M3 launch blog.
base_rates:
  input_per_m: 0.30         # USD per 1M input tokens
  output_per_m: 1.20        # USD per 1M output tokens

# Source status — what we know about where these numbers came from.
source_status:
  multipliers_primary_documented: false
  base_rates_primary_documented: true
  last_verified: 2026-06-05
  notes: >
    Per dossier UNVERIFIED status; primary source (platform.minimax.io/docs/token-plan/faq)
    does not contain multiplier language. Apply only verified base rates until
    primary-source confirmation. See dossier-audit-2026-06-05-m2.7-verifier.md.
```

**Accounting formula (in the harness):**

```python
reported = sdk.total_tokens  # the SDK's count, BEFORE any multipliers

actual_input_cost = (
    reported.input_tokens
    * config.multipliers.input_rate
    * config.base_rates.input_per_m
    / 1_000_000
)
actual_output_cost = (
    reported.output_tokens
    * config.multipliers.output_rate
    * config.base_rates.output_per_m
    / 1_000_000
)
actual_total = actual_input_cost + actual_output_cost
```

**The architectural contract:**

- The harness NEVER hardcodes the multipliers. They are read from `config/token-plan.yaml` at every accounting event.
- A primary-source confirmation event triggers a config-file update. The new values take effect immediately on the next accounting event — NO code change required.
- Every accounting event is logged with: timestamp, session-id, agent-role, sdk-reported tokens, multipliers applied, actual cost, config version.
- If the config file is missing or malformed, the harness fails closed: emits an error, refuses to start a new accounting event. No silent fallback to "default values."

---

## 4. Cross-cutting

### 4.1 Model routing

Per the locked 2026-06-05 directive:

| Role | Default model | Long-horizon (12h+) | Rationale |
|---|---|---|---|
| Chief / Leader | M3 | M3 mandatory | Synthesis + design + trust-loop verdicts are load-bearing |
| Worker (Researcher, Verifier, Builder, Scribe, Coder) | M2.7 | M3 mandatory | Read/structure/cite/build; M2.7 IQ sufficient for 8h tasks |
| Long-horizon workers | M3 mandatory | M3 | M2.7 has not been shown to hold context + plan + tool loop at 12h+ scale |

**Cost economics (per `clm-2026-06-05-016`):** M3 at $0.30/M input, $1.20/M output (verified). M2.7 at $0.22/M input, $0.22/M output (verified). The 27% input-cost delta compounds at fleet scale (10-50x worker burn per chief call). The verified base rates are applied via §3.3 — no multipliers.

### 4.2 UNVERIFIED holdouts (the 3 claims the trust loop correctly held)

The Producer→Trust loop did its job. These 3 claims did NOT promote because primary sources do not confirm them. The blueprint designs around them.

| Claim ID | Subject | Why held | Blueprint impact |
|---|---|---|---|
| (would-be) `clm-2026-06-05-M3-params` | 196B total / 11B active MoE parameters | No primary source. MiniMax M3 launch blog, OpenRouter, Ollama all silent on parameter count. | **Do not bake 196B/11B into the architecture.** Use the verified 1M context + 9.7x/15.6x speedup as the load-bearing levers. MoE ratios are an internal MiniMax detail; we don't need them. |
| (would-be) `clm-2026-06-05-M3-TPS` | 400 TPS throughput | No primary source. MiniMax docs, OpenRouter, Ollama, rate-limits page all silent on TPS. | **Do not bake 400 TPS into capacity planning.** Use third-party qualitative reports (lushbinary, datacamp) as upper-bound only. Real TPS measurement is a Sprint 5 task. |
| (would-be) `clm-2026-06-05-TokenPlan-multipliers` | 1.3x input / 1.8x output / 0.2 token/char surcharge | Not in Token Plan FAQ or Rate Limits page. Dossier carries UNVERIFIED flag with "NOT SAFE FOR PRODUCTION TOKEN ACCOUNTING" warning. | **See §3.3.** Runtime-configurable, default 1.0/1.0/0.0. The harness fails closed if the config is missing. |

**The lesson (architectural, not discipline):** a claim that the trust loop held is not a missing piece of the design — it's a piece of the design that has explicit UNVERIFIED posture. The blueprint encodes the uncertainty as a runtime configuration, not a TODO.

### 4.3 Sources ledger hygiene (non-blocking follow-up)

The 36 MiniMax dossier sources (`src-2026-06-05-001` through `src-2026-06-05-036`) are not in `knowledge/sources.jsonl`. The dossier is clean; the sources ledger is missing entries. ~5 min of producer work for the Researcher to append. Non-blocking for this blueprint.

---

## 5. Build sequencing

**Sprint order (proposed):**

### Sprint 1 — `command_router` (smallest scope, immediate ROI)

- **Why first:** the 2026-06-05 boot-sequence manual execution incident is the most recent pain. The router fixes it.
- **Scope:** regex registry, dispatch hook, ~150 lines of code.
- **Ship gate:** boot via `^Mavis,\s*boot` regex matches and fires `session-boot-sync` automatically. Manual execution is impossible.
- **Verifier check:** the Verifier dispatches 10 command-shaped inputs and asserts each fires the right skill.

### Sprint 2 — Dynamic token multiplier configuration

- **Why second:** production token accounting safety is a hard prerequisite for any cost-sensitive operation. We cannot ship a long-horizon worker without this.
- **Scope:** `config/token-plan.yaml` reader, accounting-event logger, fail-closed startup check.
- **Ship gate:** changing the config value takes effect on the next accounting event without code change. Missing config → harness refuses to start. Every event is logged.
- **Verifier check:** the Verifier runs an end-to-end accounting event with a mock SDK response and asserts the cost calculation matches the config.

### Sprint 3 — 3-tier context pipeline (largest scope)

- **Why third:** depends on §1 (subagent isolation) and §2 (3-tier hierarchy). Needs the M3 1M context to be load-bearing.
- **Scope:** meta-index generator, topic-index builder, JIT retriever (small embedding-based, local MLX), subagent-context-isolation hooks.
- **Ship gate:** a 100K-token vault scales without retrieval becoming the bottleneck. A 500K-token vault still passes the harness tests. (Load testing in Sprint 5.)
- **Verifier check:** the Verifier dispatches a worker that consumes Layer 0 + Layer 1 + Layer 2 across 5 topic files and asserts the worker can answer questions about each.

### Sprint 4 — Chunked-write discipline tooling

- **Why fourth:** the protection layer is in place (Sprints 1-2), the data layer is in place (Sprint 3). Now the discipline needs tooling so every agent uses it by default.
- **Scope:** `chunked-write` library, `checkpoint` helper, `auto-section` helper. Update Verifier contract to check chunked-write compliance.
- **Ship gate:** an agent writing a 50KB dossier uses the chunked-write tooling. The Verifier catches any monolithic Write >30KB.
- **Verifier check:** the Verifier dispatches a 50KB-write task and asserts the worker used chunked-write (file has multiple Writes, each <30KB).

### Sprint 5 — Mavis Team Engine integration

- **Why fifth:** the substrate is in place. Now adopt the official runtime.
- **Scope:** Mavis CLI integration, Leader/Worker/Verifier session orchestration, state-machine runtime wrapping the chief's dispatch flow.
- **Ship gate:** the chief dispatches a Worker via `mavis team spawn`, the Verifier audits the worker's output, the Leader accepts. All three roles are separate sessions with separate context.
- **Verifier check:** the Verifier asserts the worker's context window is NOT contaminated by the chief's conversation history, AND the verifier's context is NOT contaminated by the worker's intermediate state.

### Dependency graph

```
Sprint 1 (command_router)
   │
   ├─→ Sprint 2 (token multiplier config) ─→ Sprint 3 (context pipeline)
   │                                              │
   │                                              ├─→ Sprint 4 (chunked-write tooling)
   │                                              │       │
   └──────────────────────────────────────────────┴───────┴─→ Sprint 5 (Team Engine integration)
```

Sprints 1 and 2 can run in parallel. Sprints 3-4-5 are sequential.

---

## Appendix A — Claim traceability matrix

Every design decision in this blueprint traces back to a verified claim. The 3 UNVERIFIED holdouts are explicit; their architectural impact is in §4.2.

| Design decision | Supporting claim(s) | Status |
|---|---|---|
| Adopt Mavis Team Engine (vs build custom) | clm-2026-06-05-013 (code-driven state machine), clm-2026-06-05-019 (Leadership pattern) | VERIFIED |
| Three roles: Leader/Worker/Verifier | clm-2026-06-05-019 (corrected from Owner) | VERIFIED (corrected) |
| Mandatory Verifier gate (no worker self-promotion) | clm-2026-06-05-013 (mandatory Verifier role) | VERIFIED |
| Mavis CLI as integration point | clm-2026-06-05-014 (merged TokenPlan+AgentPlan, CLI included) | VERIFIED |
| 5-hour rolling rate-limit window | clm-2026-06-05-015 (Token Plan rate windows) | VERIFIED |
| 1M-token context with MSA speedup | clm-2026-06-05-009 (MSA architecture) | VERIFIED |
| 3-tier memory hierarchy | clm-2026-06-05-018 (canonical 2026 pattern) | VERIFIED |
| Subagent isolation (focused context) | clm-2026-06-05-018 (subagent isolation), clm-2026-06-05-013 (state machine with context isolation) | VERIFIED |
| Lost-in-the-middle mitigations | clm-2026-06-05-017 (Liu 2023) | VERIFIED |
| Workers on M2.7, Chief on M3 | clm-2026-06-05-016 (Token Plan June 5 apology — context for routing math) | VERIFIED |
| Token base rates ($0.30/M, $1.20/M) | (dossier body, confirmed by Verifier in round 3) | VERIFIED |
| CUDA long-horizon capability demo | clm-2026-06-05-010 (M3 CUDA 9.4x) | VERIFIED (corroborating only) |
| PostTrainBench 0.37 capability demo | clm-2026-06-05-011 (M3 PostTrainBench) | VERIFIED (corroborating only) |
| **NOT used: 196B/11B MoE parameter count** | (would-be) clm-2026-06-05-M3-params | **UNVERIFIED — held** |
| **NOT used: 400 TPS throughput** | (would-be) clm-2026-06-05-M3-TPS | **UNVERIFIED — held** |
| **NOT hardcoded: 1.3x/1.8x/0.2 token multipliers** | (would-be) clm-2026-06-05-TokenPlan-multipliers | **UNVERIFIED — runtime configurable, default 1.0/1.0/0.0** |

---

## Sign-off

- **Chief author (Mavis):** synthesis complete. The blueprint adheres strictly to the 11 promoted claims, explicitly notes the 3 UNVERIFIED holdouts, and designs around each of them.
- **Builder (next):** execute Sprints 1-2 in parallel; Sprints 3-5 sequential per dependency graph.
- **Verifier (next):** the Builder's output for each sprint gets re-audited before the sprint commit merges to main.

**This is a draft. Andre reviews before Builder ships.**
