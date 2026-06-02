---
type: idea
created: 2026-06-02
tags: [idea, compression, headroom, token-economics, context, rag, mavis-apex, $100-budget]
source: https://github.com/chopratejas/headroom
---

# Context Compression as a First-Class Layer

> Headroom is the most important architectural primitive I ingested in the Omniscience monsoon. The 60-95% token savings on real agent workloads aren't a nice-to-have — they're the difference between a $100/month budget lasting the quarter and burning out in two weeks. Compression is not an optimization. **It's a layer.**

## The thesis

The current Mavis pipeline has a gap. We pack context the naive way:

```
vault-brain FTS5 result (50-200K tokens)
  → long-context-curator (anchor-ends + marginal-value scoring, 50K interval compaction)
    → M3 prompt (1M context window)
```

This works for now — 1M context is huge. But three pressures push us toward compression:

1. **The $100 budget.** M3 is a frontier model. Even at $X/M tokens, a long research session with 200K of vault context, 50K of tool outputs, 80K of RAG results = $X per call × N calls = burnout by month-end. Compression at the edges stretches the runway.
2. **RAG chunk density.** A code search returning 100 results is 17,765 tokens. A SRE incident log dump is 65,694. The information density is *low* — most of those tokens are repeating the same patterns (function signatures, log lines, JSON keys). The signal-to-noise ratio screams for compression.
3. **Lost-in-middle.** The MSA signal decay doesn't go away at 1M context. Dense, repetitive content is exactly the kind of thing that causes attention dilution. Compression makes the content *denser*, not just shorter — which is the opposite of the dilution we want to avoid.

Headroom solves all three by inserting a compression layer between the *context source* (vault-brain, RAG, tool outputs) and the *model*. Same answers, fraction of the tokens.

## Headroom's six algorithms

| Algorithm | Targets | Compression | Reversible? |
|---|---|---|---|
| **SmartCrusher** | Universal JSON (arrays of dicts, nested objects) | High | Yes (CCR) |
| **CodeCompressor** | Source code (AST-aware for Python, JS, Go, Rust, Java, C++) | High; preserves semantics | Yes (CCR) |
| **Kompress-base** | Free-form text via trained HuggingFace model | 60-95% | Yes (CCR) |
| **Image compression** | Image bytes via trained ML router | 40-90% | Yes (CCR) |
| **CacheAligner** | Prompt prefixes | 0% (stabilizes) | N/A — *enables* cache hits |
| **IntelligentContext** | Whole-context scoring with importance weighting | Variable | No — selects what survives |

The killer feature is **CCR (Content-Addressable Compression with Retrieval)**: the compression is *reversible*. The original content is stored locally; when the LLM needs the full version, it calls `headroom_retrieve` and the original comes back. The prompt gets the compressed version; the LLM gets to opt back into the original when it needs the detail.

This is the same pattern as a RAG layer, but applied to *every* content type, not just documents. Tool output, log lines, RAG chunks, conversation history — all compressable, all retrievable on demand.

## The agent engineering principle

**Compression is not lossy if you can retrieve.** The whole "context window" abstraction is broken if you treat it as a one-shot read. CCR is a bet that the LLM can decide, mid-reasoning, that it needs the original — and the cost of that decision is cheap.

The 3-step pattern:

1. **Compress at ingest** — the prompt assembly layer routes everything through Headroom's ContentRouter
2. **Model gets dense content** — same answer, fewer tokens, denser signal
3. **Model calls `headroom_retrieve` on demand** — when it needs the original, it asks for it

This is dramatically different from "stuff the whole thing in the window and hope." It's the difference between a *reference library* and a *bookshelf*. A reference library has the index, the abstracts, the citations — and the librarian (CCR) knows where to find the full text.

## Real benchmarks (from Headroom's published numbers)

| Workload | Before | After | Savings |
|---|---:|---:|---:|
| Code search (100 results) | 17,765 | 1,408 | **92%** |
| SRE incident debugging | 65,694 | 5,118 | **92%** |
| GitHub issue triage | 54,174 | 14,761 | **73%** |
| Codebase exploration | 78,502 | 41,254 | **47%** |

Accuracy preserved on standard benchmarks:

| Benchmark | Baseline | With Headroom | Delta |
|---|---:|---:|---|
| GSM8K (math) | 0.870 | 0.870 | ±0.000 |
| TruthfulQA (factual) | 0.530 | 0.560 | +0.030 |
| SQuAD v2 (QA) | — | 97% | with 19% compression |
| BFCL (tool use) | — | 97% | with 32% compression |

The 92% on code search is the one that hits home for Mavis. A `vault-brain.search()` returning 100 notes currently lands in the prompt as-is. With Headroom in front, those 100 notes become ~12% of their size — same M3, much cheaper, same answers.

## CacheAligner — the unsung hero

Most of the compression work is invisible. CacheAligner is the visible win: it stabilizes prompt prefixes so that Anthropic/OpenAI KV caches *actually hit*. Provider KV cache misses are silent budget killers. Every time the prompt prefix changes by even one character, the cache misses. Headroom normalizes whitespace, key ordering, formatting variations — so the prefix is stable, the cache hits, and the cost drops by an order of magnitude on cached tokens.

For Mavis's recurring patterns (daily brief, weekly review, intake triage), the prompt template is the same every time. CacheAligner makes sure it stays the same down to the byte level.

## How Mavis-Apex uses it

The integration lives in the [[06 Token Economics & Headroom]] design doc. The pipeline becomes:

```
Source content (vault-brain result, RAG chunk, tool output, log)
  → Headroom ContentRouter detects type
    → SmartCrusher (JSON) / CodeCompressor (code) / Kompress-base (prose)
      → CacheAligner normalizes prefix
        → CCR stores original with content hash
          → compressed content + retrieve tool in prompt
            → M3 reasons over dense content
              → M3 may call headroom_retrieve when it needs the original
                → (optional) headroom_learn writes corrections to AGENTS.md
```

The four Headroom deployment modes map to four integration points:

| Mode | Where in Mavis-Apex |
|---|---|
| **Library** | Inside `vault-brain` results, `long-context-curator` packing, `intake.suggest_links` |
| **Proxy** | Wrapping the M3 API call at the network layer (transparent to M3) |
| **Agent wrap** | Not applicable — Mavis is one agent, not a fleet |
| **MCP server** | Standalone `headroom-mcp` exposing `headroom_compress`, `headroom_retrieve`, `headroom_stats` for any tool-using agent |

The MCP mode is the cleanest. Add `headroom` to the MCP config, route vault-brain results through `headroom_compress` before they hit the prompt, and the model can call `headroom_retrieve` when it needs the original.

## The $100 budget math

This is the part that closes the deal. Take a single Mavis research session:

- 200K of vault-brain FTS5 results
- 50K of M3 vision analysis outputs (image descriptions)
- 80K of RAG chunks (web pages, transcripts)
- 30K of conversation history
- 20K of tool outputs (kanban stats, calendar lookups)

= **380K tokens per prompt** at full fidelity.

With Headroom averaging 70% savings on this mix: **114K tokens per prompt** at ~95% fidelity (CCR retrievable for the other 5%).

At $X/1M input tokens (M3 frontier pricing, illustrative), 380K = $0.38X per call. 114K = $0.11X per call. **3.3× more sessions per dollar**. On a $100/month budget, that's 263 calls → 870 calls.

Compression isn't a 10% improvement. **It's a 3× budget multiplier.**

## The $100 budget rule

The hard rule this enables: **vault-brain must never return uncompressed content to the model**. Every retrieval that crosses the prompt boundary goes through Headroom. This is enforced at the `long-context-curator` layer (see [[03 The Custom MCP Arsenal]]), not at the model level.

The CCR retrieval is opt-in by the model. Headroom is a layer, not a rule.

## What this is NOT

- **Not a replacement for retrieval.** Headroom compresses what comes back. `vault-brain` is still the index. They're complementary.
- **Not always-on for everything.** A 1K token small prompt doesn't need compression. The threshold is "is the prompt bigger than the cache-aligned prefix + 10K tokens?" If yes, compress. If no, ship as-is.
- **Not a privacy mechanism.** Headroom runs locally but it's not a redaction layer. PII still needs to be redacted *before* compression. (See [[04 Direct-Intake MCP]] auto-redaction rules.)
- **Not magic on dense signal.** A proof with critical reasoning, a security-sensitive log dump, a contract clause — these don't compress well. Headroom knows this and routes them through `IntelligentContext` with importance scoring instead.

## Connections

- [[06 Token Economics & Headroom]] — the design doc for the integration
- [[03 The Custom MCP Arsenal#MCP #3: `long-context-curator`]] — the curator is the natural place to wire Headroom
- [[03 The Custom MCP Arsenal#MCP #1: `vault-brain`]] — vault-brain is the highest-leverage source to compress
- [[04 Direct-Intake MCP]] — intake drops should compress before they hit the inbox note
- [[Mavis EA Workflow]] — the daily brief, weekly review, and intake triage are cache-aligned prefix candidates
- [[Paged Memory Pattern]] — paged memory and compression are complementary
- [[learnings]] — `[capability]` entry on Headroom
- https://github.com/chopratejas/headroom — the source

## Anticipated future direction

- **Local Kompress-base fine-tune** on Andre's vault — the trained model is general; a vault-specific fine-tune would boost compression ratio on his actual content
- **Compression-aware curator** — the long-context-curator learns which content compresses well and packs denser
- **Budget-aware prompt building** — the prompt assembler tracks session spend and routes through heavier compression as the budget runs down

---

*Seeded 2026-06-02 from Operation Omniscience Phase 1. The integration design is in [[06 Token Economics & Headroom]].*
