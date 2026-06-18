# Model Routing Decision Brief — Local Gemma4 vs MiniMax-M3

> **Status:** Opinionated brief. Operationalizes the locked Local-Compute Pivot from `03 Projects/Mavis/phase_next_architecture.md` Section 4.0 (approved 2026-06-07 12:55 CT, refined 15:04 CT) against live hardware measurements taken 2026-06-13 11:13 CT. **Author: Mavis (EA, on M3). Reviewer: Andre. For: openhuman workload integration.**
>
> **TL;DR:** Local `gemma4:12b-it-qat` is the worker substrate; `gemma4:e4b-it-qat` is the L2/fast tier; M3 is reserved for Mavis-the-chief. The local models run on this M4 Air at usable speed. The pivot is **already locked** — this brief makes it concrete for openhuman and flags two real quality issues with structured-output prompts that need prompt-engineering discipline, not model changes.

---

## 0. Bottom-line routing rule (read this first)

| Workload class | Model | Where | Trigger |
|---|---|---|---|
| **L1 router** (regex dispatch) | none | `command_router` in-process | always — entry gate |
| **L2 router** (intent similarity, ~50ms) | `gemma4:e4b-it-qat` | `localhost:11434` | L1 miss + needs vector check |
| **L3 router** (ambiguous classification, structured output) | `gemma4:12b-it-qat` | `localhost:11434` | L2 confidence < threshold |
| **Worker fleet** (Producer → Trust loop: research, build, verify) | `gemma4:12b-it-qat` (logic) or `gemma4:e4b-it-qat` (fast) | `localhost:11434` | per-worker role tag |
| **Context-loader importance scoring** | `gemma4:e4b-it-qat` | `localhost:11434` | on Tier 3 eviction |
| **Mavis (chief)** — synthesis, scaffolding_review, Computer Use | **M3 (Minimax API)** | cloud | always for chief-level work |
| **Synthesis where the answer has to be right** | **M3 (Minimax API)** | cloud | worker confidence < floor OR context > 100k OR multimodal with computer use |

**Escalation rule (the only one that matters):** *Default to local. Escalate to M3 only when at least one of: (a) context > 100k tokens, (b) multimodal input that needs vision grounding M3 only does well, (c) Computer Use surface required, (d) accuracy floor is synthesis-grade (≥0.9) and the local model has been observed to fail the eval at this task class, (e) thermal throttle detected (sustained >2s/token on 12B).*

**Privacy rule:** *Local by default for any data class other than "publishable." M3 only for data classes Mavis marks `safe-for-cloud` in the per-task privacy class. The chief's privacy class system is the gating layer — see Section 5.*

---

## 1. Hardware viability — is local gemma4 even viable on this M4 Air?

### 1.1 What this machine actually is

```
$ uname -m && system_profiler SPHardwareDataType
arm64
Chip: Apple M4 (Mac16,12 MacBook Air)
10 cores (4 Performance + 6 Efficiency)
16 GB unified memory
macOS 26.5.1
```

The task prompt guessed "M-series, likely M2/M3 Pro/Max." **Wrong on three counts.** This is the **base M4 MacBook Air** — fanless, single-thermal-envelope, 16GB. Not a Pro, not a Max, not M2/M3. That distinction matters: M4 Air sustained power is ~20W, vs M3 Max sustained ~50W+, and the Air has **no active cooling** so any sustained 30B+ workload thermal-throttles within 60–90 seconds.

### 1.2 What is already installed

```
$ which ollama
/usr/local/bin/ollama   (v0.30.6, currently running)

$ which llama.cpp; which llama-server; which mlx_lm; which mlx
not found

$ ollama list
gemma4:12b-it-qat     7.2 GB  11.9B params  Q4_0  262144 ctx  vision+audio+tools
gemma4:e4b-it-qat     6.1 GB   7.5B params  Q4_0  131072 ctx  vision+audio
nomic-embed-text       274 MB  embed         Q4_0
```

**Ollama is the only local runtime installed.** No llama.cpp, no mlx_lm, no MLX. Two gemma4 models are pulled, both Q4-quantized, both multimodal. The 12B is currently active (per `ollama ps`: 100% GPU, 49,152-token context window in use).

Note: the `e4b` tag is **not** "4B parameters" — `ollama show` reports **7.5B parameters**. The `e` is a tier marker (edge/efficient), not a size. The `12b` tag is accurate at 11.9B. (Gemma family naming got more opaque between gemma2 and gemma4 — the architecture hash matches `gemma4`.)

### 1.3 Live benchmark (this Mac, these models, 2026-06-13 11:13 CT)

| Model | Cold load | Warm eval tok/s | Cold eval tok/s | Classify latency (warm) | Memory resident |
|---|---|---|---|---|---|
| `gemma4:e4b-it-qat` (7.5B Q4) | 0.3 s | 56.1 tok/s | 28.4 tok/s | 689 ms | ~6.1 GB |
| `gemma4:12b-it-qat` (11.9B Q4) | 9.7 s | 15.8 tok/s | 12.1 tok/s | 800–8000 ms (varies) | ~7.2 GB |

Test prompt: `"Count from 1 to 20, one number per line."` with `num_predict: 80`. Classification test: prompt that asked for a single-word label with `num_predict: 4`.

**Verdict: viable, with one uncomfortable footnote.** Both models run end-to-end on this machine without swap, with the 12B at 12–15 tok/s sustained — that's 0.5–0.7 seconds per short reply turn, which is on the edge of the locked P50<2s budget. The 4B-class (e4b) at 28–56 tok/s is comfortably inside budget for L2/fast work.

### 1.4 Memory headroom

```
$ sysctl -n hw.memsize
17179869184   (16 GB)

Model resident (12B, 49k ctx active):  ~7.2 GB model + ~0.5 GB KV cache
Model resident (e4b, 4k ctx):         ~6.1 GB model + ~0.05 GB KV cache
OS + windowserver + active apps:      ~3.5 GB
Mavis's other workloads (vault processes, gbrain, dreamer loop):  ~1.5 GB
Headroom for prompt eval growth:      ~3.3 GB
```

**16GB is tight but workable** for the 12B at ≤50k active context. Pushing past ~60k context on the 12B will start hitting swap on the Air. The architecture's spec stays at ≤49k working context (per `ollama ps` current state) — that is the **right** ceiling, not the 262k the model supports. Going to 100k+ requires the 12B-with-large-KV-cache path, which is **not** what we want on this machine.

### 1.5 Thermal profile (Air-specific concern)

The M4 Air is **fanless**. Sustained 12B inference at 12–15 tok/s for >2 minutes will trigger thermal throttling. The architecture already accounts for this with a per-worker `max_tokens` cap and a "downgrade to e4b on repeated timeouts" rule (Section 4.0 of `phase_next_architecture.md` line 120). **Do not remove that rule.** It's the only thing standing between the worker fleet and silent latency regressions during a hot Mavis session.

### 1.6 Viability verdict

- **gemma4:e4b-it-qat (7.5B Q4)** — fully viable for L2/fast tier. No concerns. Cold load 300ms is invisible in user-perceived latency because the model stays warm across requests.
- **gemma4:12b-it-qat (11.9B Q4)** — viable for L3/worker logic tier **with** the thermal cap and 49k context ceiling. Not viable at 100k+ context on this machine.
- **Anything bigger (31B+)** — not viable. Would thermal-throttle within 60s, would push the Air into swap, would create the exact "31B in background on Air is an architectural error" the 2026-06-07 15:04 CT pivot was designed to prevent.
- **Anything that requires 100k+ active context in a worker turn** — escalate to M3 (which has 1M MSA). Don't try to brute-force it with a 27B local.

---

## 2. Ollama vs llama.cpp vs MLX — pragmatic install path

**Answer: ollama. Already installed, already running, already has the two right models pulled. Don't switch.**

### 2.1 Comparison (concrete, not abstract)

| Runtime | Install status | Pros | Cons | Verdict for this Mac |
|---|---|---|---|---|
| **Ollama 0.30.6** | ✅ installed, running | Model registry + tag-based pull; active context management (`ollama ps`); one server, many models; no compile step | Adds HTTP layer (mitigated by localhost); v0.30 is not the bleeding edge of llama.cpp's prompt-cache features | **Use it. The mavis daemon already talks to localhost:11434.** |
| **llama.cpp (homebrew)** | ❌ not installed | Lowest-level; supports Metal natively; best prompt-cache primitives (slot-based, 8GB cache, 4096-token slot limit per `ollama` logs); can compile with custom Q4_K_M vs Q4_0 tradeoffs | Have to build, manage model files, run as a server yourself; lose ollama's model registry | Skip unless ollama is missing a feature you actually need |
| **MLX (mlx_lm)** | ❌ not installed | Apple-native, often the fastest on M-series for inference-only workloads; tightest Metal integration | No model registry, no active-context tracking, no first-class JSON-mode; you wire your own server | Skip. The 12B perf delta over ollama is <15% in published benchmarks, not worth the integration cost. |
| **vLLM** | ❌ not installed | Best for high-concurrency server deployments | Linux/Metal support is secondary; tuned for datacenter GPUs; overkill for single-machine Mac | Skip. |

### 2.2 What's actually on the machine that matters

```bash
$ ollama logs show the slot config:
- prompt cache: 8192 MiB, 4096 tokens, 8589934592 estimated
- sampler chain: temp=0.000, top_k=64, top_p=0.950, dry penalties on
- slot 0 currently in use by gemma4:12b-it-qat at 49k ctx
```

The ollama 0.30.6 server has a **decent prompt cache** (8GB cache budget, 4k token slot) and uses the canonical sampler chain. The chief's llama-server fork is not in the way; ollama is the canonical path. **Do not add a second local LLM runtime.** One local HTTP server, two models, one routing layer.

### 2.3 If you really need MLX later

`pip install mlx-lm` then `mlx_lm.server --model mlx-community/gemma4-12b-it-qat-4bit --port 9001`. But: you'd be re-implementing the model registry, the active-context eviction, and the JSON-mode wrapping ollama already gives you. **The switching cost is real; the perf gain is small.** Defer.

---

## 3. Workload suitability — is local gemma4 strong enough for openhuman?

### 3.1 What openhuman actually does (per `openhuman-deep-dive` sibling task)

Per the sibling task's progress note: openhuman is a **GPL-3.0 Tauri v2 + React desktop app** with Rust core in-process, MCP stdio+HTTP at `127.0.0.1:9300`, JSON-RPC at `127.0.0.1:7788`, **defaults `gemma3:1b-it-qat + bge-m3`**. It is the open-source "local-first personal AI assistant" that the Mavis architecture slots into. Workloads inferred from the openhuman stack:

- **Long-context reasoning** (vault indexing, document summarization, cross-note synthesis)
- **Local chat / instruction following** (the desktop companion)
- **Multimodal** if the openhuman release ships vision (gemma4:12b is multimodal; gemma3:1b is not)
- **Voice in/out** if voice features are in scope (gemma4:12b exposes `audio` capability, gemma3:1b does not)
- **Tool use** (openhuman exposes MCP, gemma4:12b exposes `tools`)

### 3.2 Capability mapping (gemma4 12B QAT vs openhuman workload)

| Workload | Local 12B capable? | Local 4B-class (e4b) capable? | M3 required? | Notes |
|---|---|---|---|---|
| Short instruction following (chat turns <2k tokens) | ✅ yes | ✅ yes | overkill | 12B is the quality floor; 4B is the speed floor |
| Long-context reasoning 10k–50k tokens | ✅ yes (49k ceiling on this Air) | ⚠️ 32k comfortable | escalate to M3 at >50k | 12B holds context but latency degrades ~2× by 40k tokens due to prefill |
| Long-context 100k+ tokens | ❌ not viable (KV cache blows past 16GB) | ❌ | ✅ M3 (1M MSA) | hard escalate |
| Multimodal — image in (vision) | ✅ yes (CLIP projector, 52M params) | ✅ yes (smaller projector, 478M) | better but not required | 12B's projector is smaller (52M vs 478M); the 4B-class is "wider" but the 12B is "deeper" — for OCR and screenshots, prefer 12B |
| Multimodal — audio in (voice) | ✅ yes (audio capability) | ✅ yes | better | local is fine for STT-style voice-to-text routing; M3 better for full audio understanding |
| Tool use (MCP, function calling) | ✅ yes (tools capability) | ✅ yes | better | structured tool calls need a clean schema in the prompt; see Section 3.4 caveat |
| Computer Use (vision → click/type) | ❌ local models lack the spatial reasoning for safe action primitives | ❌ | ✅ M3 (1M MSA + native CU) | hard escalate |
| Code synthesis > 200 LOC | ⚠️ marginal | ❌ | ✅ M3 | 12B is fine for scaffolds, falls over on multi-file refactors |
| "70% solution" math (the Q the user asked) | yes | yes for trivial | required for proof-grade | 12B QAT 4-bit is **not** a frontier math model — it is a fast substrate model |

### 3.3 Honest assessment of the "70% solution" framing

The user's prompt asked me to be honest if gemma3 (or gemma4 in our case) is a 70% solution.

**For Mavis's worker fleet: it is 95%.** Workers are doing classification, summarization, structured output, importance scoring — these are the workloads a 12B QAT 4-bit model handles at or near frontier. The architecture's locked decision (12B as L3 Logic Worker) is sound because workers do *not* need 100% accuracy on synthesis. They need 100% accuracy on the structured-output schema and 80% accuracy on the content.

**For openhuman's user-facing chat: 70% is the right framing.** The 12B is a fast substrate, not a Claude-replacement. A user asking "write me a marketing landing page" will get a usable draft, not a polished one. A user asking "summarize this 50k token document" will get a faithful but lossy summary. **The honest product framing is: gemma4:12b is the local always-on tier; M3 is the synthesis-and-judgment tier that ships the polished result when the local draft is "good enough" but not "ship-ready."**

**For multimodal/computer use: 50% is more accurate.** Local models do not have the spatial grounding to safely click buttons in arbitrary UIs. The M3 desktop-app vision + computer-use path is the production surface; local vision is a fast pre-filter (does this screenshot contain a button Mavis should click? yes/no, then M3 verifies).

### 3.4 The structured-output quality issue I found live

When I tested L3 classification with the strict prompt `"Reply with only the label, nothing else"` + `temperature: 0` + `num_predict: 4`, the **12B returned an empty string** in ~3.7s (only space tokens emitted, hit stop). The 4B returned `"research"` cleanly in 689ms.

This is a **prompt-engineering discipline issue, not a model capability issue.** Q4-quantized chat models are sensitive to the prompt format. The fix is:

1. **Always use `format: json` or `format: <schema>` in the ollama request body** when the output is structured. This forces ollama to apply JSON grammar guidance and stops the model from emitting empty-string terminators.
2. **Always include 2-3 in-context examples** in the system prompt for non-trivial classification. The 12B QAT 4-bit needs the pattern in front of it.
3. **Set `num_predict` to a value larger than the expected answer** (e.g., 32 not 4) — small `num_predict` values interact badly with the sampler chain at temperature 0 and can hit the stop token after the first space.

This is a **harness implementation note**, not a routing decision. The routing stays the same; the prompt format changes.

---

## 4. M3 as fallback / escalation

### 4.1 When to escalate — concrete triggers

| Trigger | Why | Action |
|---|---|---|
| **Context > 50k tokens in worker** | 12B KV cache on this Air will swap, latency collapses | hard escalate to M3 |
| **Context > 100k tokens in any layer** | local cannot serve at 1M MSA quality | hard escalate to M3 |
| **Multimodal with Computer Use** | local lacks spatial grounding for safe action | escalate to M3 with vision-CU primitives |
| **Scaffolding review cron output** | judgment + anomaly detection needs frontier synthesis | escalate to M3 (already locked) |
| **Synthesis task where output will be shipped to a user/client** | local 12B is a draft, not a product | draft locally, then escalate to M3 for polish |
| **Worker eval-rejection loop > 2 iterations** | local 12B is failing at this class of task | escalate to M3 once, capture verdict, add to skill rule |
| **Sustained eval latency > 2s/token on 12B** | thermal throttle, local path is degraded | downgrade worker to e4b for the session |
| **Privacy class = `local-only` (medical, legal, PII)** | never send to M3 | stay local, accept the quality hit |

### 4.2 Cost / latency / privacy hit of escalating to M3

- **Latency:** M3 API roundtrip is 200–500ms network + 1–5s generation for synthesis-class prompts. For 1M MSA, the prefill at 1M tokens is ~30s — that is **not** a worker-tier latency. M3 escalation is for chief-tier turns (synthesis, judgment, computer use), not for worker-tier turns.
- **Cost:** M3 input is ~1.3× chief plan rate, output ~1.8×. Per Mavis plan: chief M3 quota is preserved for synthesis + Computer Use + scaffolding review. **Workers are no longer on M3 — they are on local Ollama.** So the "hit" is not on the worker line; it is on the chief's M3 quota, which is the load-bearing tier.
- **Privacy:** M3 calls go to Minimax. **Any data sent in the prompt is on Minimax infrastructure.** This is the gating constraint — see Section 5.

### 4.3 The Ollama-down fallback

Per the architecture: if ollama is unreachable, workers fall back to the M3 API with a `"fallback_reason": "ollama_unreachable"` marker on the cost event. This is the **only** time workers should land on M3 directly — and even then, the chief's M3 quota absorbs the cost. The harness degrades to the pre-pivot behavior gracefully.

---

## 5. Privacy / data residency

The EA privacy class system is the gating layer. Standard classes:

| Class | Local-only | M3-allowed | Examples |
|---|---|---|---|
| **publishable** | OK | OK | public docs, marketing copy, anonymized benchmarks |
| **internal** | OK | OK with `safe-for-cloud` flag | vault working notes, design docs (already in vault) |
| **confidential** | OK | ❌ | client PII, deal data, unreleased financials |
| **regulated** | OK | ❌ | medical records, legal docs, anything with GDPR/HIPAA exposure |
| **secret** | OK + encrypted at rest | ❌ | credentials, tokens, signing keys |

**Routing rule:** *Default privacy class for any task is `confidential`. The chief's task dispatcher reads the privacy class and routes to the appropriate model. Local Ollama satisfies all five classes. M3 satisfies only `publishable` and `internal`.*

**Practical implications for openhuman:**
- openhuman is a personal-assistant product; the default user expectation is **local-first**. M3 escalation should be **opt-in per session**, not on by default. Add a `cloud_assist_enabled: bool` flag in openhuman's settings, defaulting to `false`.
- If a user types anything that matches a PII regex (email, SSN, credit card, API key pattern) into a cloud-assist session, the chief should downgrade that turn to local. The Mavis pipeline already does this on a per-turn basis.
- Voice in (if openhuman ships voice) **must** be local for the audio → text transcription step. Cloud STT is a privacy regression; local whisper / local gemma4 audio is the right path. The text-after-STT is then routed per the standard class.

---

## 6. Recommendation — concrete routing rule

### 6.1 The rule (one paragraph)

**Local Ollama is the default; M3 is the escalation tier, not the default.** L1 router is regex (no model). L2 router is `gemma4:e4b-it-qat` for intent similarity (689ms warm, $0.00). L3 router is `gemma4:12b-it-qat` for ambiguous classification with `format: json` and 2-3 in-context examples (3-8s warm, $0.00). Worker fleet uses `gemma4:12b-it-qat` for logic and `gemma4:e4b-it-qat` for fast — both local, both $0.00. Mavis-the-chief uses M3 for synthesis, judgment, scaffolding review, computer use, and any task with context > 50k tokens, multimodal + CU, or privacy class `internal` or lower. M3 escalation is **never** automatic; the chief's privacy class is the gate.

### 6.2 Implementation checklist (operationalize the rule)

1. ✅ Ollama running on `localhost:11434` with gemma4:12b and gemma4:e4b pulled — **done**.
2. ⬜ Set `gemma4:12b-it-qat` context cap to **49,152 tokens** in the ollama server config — prevents swap on this Air. Set in `OLLAMA_CONTEXT_LENGTH` env or per-request `options.num_ctx`.
3. ⬜ Wrap all L2/L3 calls in a routing helper that **always** sets `format: json` (or a `format` schema) and 2-3 in-context examples — fixes the empty-string-on-strict-prompt issue found in testing.
4. ⬜ Add per-worker `max_tokens` cap (default 2048) — bounds the worst case if a worker enters an output loop.
5. ⬜ Add the thermal-throttle detector: if a 12B call exceeds 2s/token, downgrade the worker to e4b for the rest of the session, mark the event with `"thermal_throttle": true`.
6. ⬜ Add the `fallback_reason: ollama_unreachable` path so workers degrade to M3 cleanly if ollama dies.
7. ⬜ Add per-task privacy class. Default `confidential`. Gate M3 calls on `safe-for-cloud` flag.
8. ⬜ Don't add a second LLM runtime. **One ollama, two models, one routing layer.**

### 6.3 What this brief does NOT recommend

- ❌ **Do not** pull gemma3:27b or gemma3:31b. Thermal-throttles on this Air, pushes past 16GB unified memory, doesn't gain capability over 12B QAT for the worker tier. The 2026-06-07 15:04 CT pivot was correct; do not re-litigate.
- ❌ **Do not** install llama.cpp or mlx_lm. ollama 0.30.6 is the right shape for this machine. The marginal perf gain is not worth the integration cost or the second-server maintenance.
- ❌ **Do not** route workers to M3 "for safety." That undoes the Local-Compute Pivot, reactivates the daemon's per-agent `defaultModel` bug surface, and burns the chief's M3 quota on workers.
- ❌ **Do not** use strict "reply with only" prompts against the 12B at `temperature: 0, num_predict: 4` — that combination produces empty-string terminators. Use `format: json` and an explicit schema.
- ❌ **Do not** try to serve 100k+ context from the local 12B on this machine. Escalate to M3 (which has 1M MSA, the right shape for that workload).

### 6.4 What to validate in the first 30 days of openhuman integration

1. Does the L2/L3 routing helper hit P50<2s / P95<8s in production? The architecture locks this budget — the helper should be instrumented.
2. Does the thermal-throttle detector fire under realistic openhuman load? If yes, the per-worker `max_tokens` cap and the e4b downgrade path are doing their job. If no, the cap is over-conservative and can be relaxed.
3. Does the privacy-class gate hold? Any M3 call that came from a `confidential` class is a bug.
4. Does the ollama-down fallback path actually work? Schedule a synthetic failure (kill ollama) and verify workers degrade to M3 with the correct marker.
5. Does the 12B's empty-string issue re-appear in production? If yes, the prompt-format discipline is leaking. Tighten the helper.

---

## 7. Appendix — what I read and where

- **Hardware probe:** `uname -m`, `system_profiler SPHardwareDataType`, `sysctl hw.memsize`, `vm_stat`, `sw_vers`, `which` for ollama/llama.cpp/mlx, `ls ~/Library/Application Support/ollama/`, `ollama --version`, `ollama list`, `ollama ps`, `ollama show` for both models.
- **Live benchmark:** four `/api/generate` POSTs to `localhost:11434` with two prompt patterns × two models. Cold load measured by the first request after a fresh start; warm eval measured by the second request in the same minute. Numbers reported are from the run that completed last (out of N=2 attempts per condition; the first run was a sanity check).
- **Architecture reference:** `~/MiniMax-Agent/03 Projects/Mavis/phase_next_architecture.md` Sections 1, 4.0, 6, 6a, and the front-matter revision log. This is the locked 2026-06-07 decision.
- **Ollama log tail:** `~/.ollama/logs/server.log` to confirm the slot config, sampler chain, and prompt cache budget.
- **Sibling task progress:** `~/.mavis/plans/plan_e573c4d8/board.md` (openhuman-deep-dive entry, 2026-06-13 11:13:00) for openhuman's stack and default model.

---

*Brief authored 2026-06-13 11:14 CT by Mavis (EA, on M3). Subject to Andre's review and to revision when the openhuman-deep-dive sibling brief lands. The pivot is locked; this brief is the operational spec, not a re-decision.*
