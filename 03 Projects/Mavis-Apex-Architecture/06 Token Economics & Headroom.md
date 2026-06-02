---
type: project
created: 2026-06-02
status: design
tags: [project, mavis, architecture, headroom, compression, token-economics, $100-budget, mcp]
---

# 06 Token Economics & Headroom

> Design doc for the **Context Compression Layer** — the Headroom integration that sits between the model's context sources (vault-brain, RAG, tool outputs, conversation history) and the M3 reasoning core. Written 2026-06-02 during Operation Omniscience. The thesis: **compression is not an optimization, it's a layer.** The 60-95% token savings Headroom delivers on real workloads are the difference between a $100/month budget lasting the quarter and burning out in two weeks. This doc is the spec for how to wire it in.

## Purpose

The current Mavis-Apex pipeline packs context the naive way:

```
vault-brain FTS5 result (50-200K tokens)
  → long-context-curator (anchor-ends + marginal-value scoring)
    → M3 prompt (1M context window)
```

This works for now — 1M context is huge. But three pressures push us toward compression:

1. **The $100 budget.** Even at frontier-model pricing, a 380K-token prompt × N calls = budget burnout. Compression at the edges stretches the runway 3×.
2. **RAG chunk density.** Code search (17,765 → 1,408 = 92% savings), SRE incident logs (65,694 → 5,118 = 92%), GitHub issue triage (54,174 → 14,761 = 73%). Most tokens are repeating structure, not signal.
3. **Lost-in-middle.** MSA signal decay at 1M context. Dense, repetitive content dilutes attention. Compression makes content *denser*, not just shorter.

The fix is a compression layer between the *context source* and the *model*. Same answers, fraction of the tokens.

## The Headroom architecture (the layer we're integrating)

Headroom ships as four deployment modes. We use the right one for each integration point:

| Mode | Shape | Mavis-Apex integration point |
|---|---|---|
| **Library** | `from headroom import compress` | Inline in `long-context-curator` packing and `intake.summarize` |
| **Proxy** | `headroom proxy --port 8787` | Wraps the M3 API call at the network layer (transparent) |
| **MCP server** | `headroom_compress`, `headroom_retrieve`, `headroom_stats` | Standalone MCP for any tool-using agent to call on demand |
| **`headroom learn`** | `npx headroom learn` | Mines failed sessions, writes corrections to `agent.md` / `learnings.md` |

The MCP mode is the cleanest. Add `headroom` to the MCP config; the model can call `headroom_compress` on any content and `headroom_retrieve` on any compressed content when it needs the original. The library mode is the fallback for places where the MCP overhead is too much (e.g., inside a hot loop processing 100 RAG chunks).

## The six algorithms (the type system of compression)

Headroom's content router detects the content type and dispatches to the right compressor:

| Algorithm | Targets | Compression | Reversible? | When to use |
|---|---|---|---|---|
| **SmartCrusher** | Universal JSON (arrays of dicts, nested objects) | High (60-80%) | Yes (CCR) | Tool outputs, RAG JSON, structured data |
| **CodeCompressor** | Source code (AST-aware for Python, JS, Go, Rust, Java, C++) | High (70-90%) | Yes (CCR) | Code search results, stack traces, diffs |
| **Kompress-base** | Free-form text via trained HuggingFace model | 60-95% | Yes (CCR) | Articles, transcripts, prose, log lines |
| **Image compression** | Image bytes via trained ML router | 40-90% | Yes (CCR) | Image bytes in tool outputs |
| **CacheAligner** | Prompt prefixes | 0% (stabilizes) | N/A — *enables* cache hits | Every prompt |
| **IntelligentContext** | Whole-context scoring with importance weighting | Variable | No — selects what survives | Last-resort fitting when context > window |

The killer feature is **CCR (Content-Addressable Compression with Retrieval)**: the compression is *reversible*. The original content is stored locally with a content hash; when the LLM needs the full version, it calls `headroom_retrieve(hash)` and the original comes back. The prompt gets the compressed version; the LLM gets to opt back into the original when it needs the detail.

This is the same pattern as a RAG layer, but applied to *every* content type, not just documents. Tool output, log lines, RAG chunks, conversation history — all compressable, all retrievable on demand.

## Where Headroom fits in the Mavis-Apex pipeline

```
Content source
  │ (vault-brain FTS5, RAG chunk, tool output, log line, conversation history)
  ▼
ContentRouter ─ detects type, picks compressor
  │
  ▼
CacheAligner ─ stabilize prefix for provider KV cache
  │
  ▼
SmartCrusher / CodeCompressor / Kompress-base
  │
  ▼
CCR store ─ keep original with content hash
  │
  ▼
compressed content + retrieve tool → M3 prompt
  │
  ▼
M3 reasons over dense content
  │
  ▼ (on demand)
M3 calls headroom_retrieve(hash) → original returns
```

The compression happens at the **prompt assembly layer** — every content block that crosses the prompt boundary is routed through Headroom. The M3 model never sees uncompressed content from a known source. CCR is opt-in: the model decides when to retrieve the original.

## Real benchmarks (the data behind the design)

From Headroom's published numbers:

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

The accuracy preservation is the one that makes it safe. ±0.000 on GSM8K means the math reasoning isn't degraded. +0.030 on TruthfulQA means the factual recall is *better* with compression (less noise to confuse the model). SQuAD v2 at 97% with 19% compression is the operational sweet spot — high accuracy, real savings.

## The $100 budget math (the killer slide)

A single Mavis research session, illustrative:

| Source | Tokens (uncompressed) |
|---|---:|
| vault-brain FTS5 results | 200,000 |
| M3 vision analysis outputs (image descriptions) | 50,000 |
| RAG chunks (web pages, transcripts) | 80,000 |
| Conversation history | 30,000 |
| Tool outputs (kanban stats, calendar lookups) | 20,000 |
| **Total** | **380,000** |

With Headroom averaging 70% savings on this mix: **~114,000 tokens per prompt** at ~95% fidelity (CCR retrievable for the other 5%).

At frontier-model pricing (illustrative, M3 frontier), 380K vs 114K = **3.3× more sessions per dollar**. On a $100/month budget, that's 263 calls → 870 calls.

**Compression is not a 10% improvement. It's a 3× budget multiplier.**

## The integration points (the concrete calls)

There are five places in the Mavis-Apex pipeline where Headroom gets called:

### 1. `vault-brain.search()` results

Every FTS5 result leaves `vault-brain` compressed:

```python
# Inside vault-brain MCP
def search(query: str, top_k: int = 20) -> list[Note]:
    results = fts5_search(query, top_k=top_k)
    serialized = [note.to_markdown() for note in results]

    # Compress before returning to the model
    if total_tokens(serialized) > 2000:
        compressed = compress(serialized, model="MiniMax/M3")
        return [CompressedNote(text=compressed.text, ccr_hashes=compressed.hashes)]

    return [Note(text=text) for text in serialized]
```

The model gets dense content. If the linker needs the original to make a connection, it calls `headroom_retrieve(hash)`.

### 2. `long-context-curator` packing

The curator (per [[03 The Custom MCP Arsenal#MCP #3: `long-context-curator`]]) packs context for M3. It calls Headroom on each content block before assembly:

```python
def pack_context(blocks: list[Block], token_budget: int) -> Prompt:
    compressed_blocks = []
    for block in blocks:
        if block.tokens > 1000:
            compressed = compress(block.content, model="MiniMax/M3")
            compressed_blocks.append(Block(
                content=compressed.text,
                ccr_hash=compressed.hash,
                original_tokens=block.tokens,
                compressed_tokens=compressed.tokens,
            ))
        else:
            compressed_blocks.append(block)

    return assemble_prompt(compressed_blocks, token_budget=token_budget)
```

### 3. `intake.summarize` and `intake.process`

The intake MCP (per [[04 Direct-Intake MCP]]) compresses large drops before the M3 reasoning call:

```python
def process(intake_id: str) -> ClassificationResult:
    drop = intake_log.get(intake_id)
    markdown = drop.markdown_content

    if tokenize(markdown) > 5000:
        compressed = compress(markdown, model="MiniMax/M3")
        return m3.classify(
            content=compressed.text,
            ccr_hashes=compressed.hashes,
            vault_context=vault_brain.top_20(),
        )
    else:
        return m3.classify(content=markdown, vault_context=vault_brain.top_20())
```

### 4. `self-model-card` introspection logs

The self-model-card (per [[05 self-model-card — Build]]) logs every tool call, including the tokens consumed. Compressed logs are 10× smaller:

```python
def log_tool_call(call: ToolCall, result: ToolResult):
    entry = {
        "timestamp": now(),
        "tool": call.name,
        "input_tokens": tokenize(call.input),
        "output_tokens": tokenize(result.output),
        "duration_ms": result.duration_ms,
    }

    if entry["input_tokens"] + entry["output_tokens"] > 500:
        compressed = compress(json.dumps(entry), model="MiniMax/M3")
        log.write(compressed.text, ccr_hash=compressed.hash)
    else:
        log.write(json.dumps(entry))
```

### 5. Conversation history compaction

At 50K-token intervals, the conversation history is compressed before being fed back into the prompt:

```python
def compact_history(history: list[Message]) -> CompressedHistory:
    serialized = [msg.to_markdown() for msg in history]

    # Preserve the most recent N messages verbatim, compress the rest
    verbatim = serialized[-10:]
    to_compress = serialized[:-10]

    compressed_old = compress("\n\n".join(to_compress), model="MiniMax/M3")
    return CompressedHistory(
        verbatim=verbatim,
        compressed_old=compressed_old.text,
        ccr_hashes=compressed_old.hashes,
    )
```

## CacheAligner — the unsung hero

Most of the compression work is invisible. CacheAligner is the visible win: it stabilizes prompt prefixes so that provider KV caches *actually hit*. Provider KV cache misses are silent budget killers. Every time the prompt prefix changes by even one character, the cache misses.

CacheAligner normalizes:
- Whitespace (collapse runs of spaces, normalize line endings)
- Key ordering in JSON tool definitions
- Tool list ordering (stable sort by name)
- Date format (ISO 8601 only)
- Markdown style (no trailing whitespace, consistent heading style)

For Mavis's recurring patterns (daily brief, weekly review, intake triage), the prompt template is the same every time. CacheAligner makes sure it stays the same down to the byte level. Cached tokens are typically 10× cheaper than uncached — CacheAligner is the difference between paying for and not paying for the prefix.

## The four hard rules

These are the discipline rules the layer enforces:

1. **`vault-brain` must never return uncompressed content to the model.** Every retrieval that crosses the prompt boundary goes through Headroom. Enforced at the `long-context-curator` layer, not at the model level.
2. **The CCR retrieval is opt-in by the model.** Headroom is a layer, not a rule. The model decides when to retrieve the original. We don't force retrieval on every block.
3. **Compression is never applied to proof-of-correctness content.** A math proof, a security audit, a contract clause — these don't compress well, and forced compression risks correctness. Headroom knows this and routes them through `IntelligentContext` with importance scoring instead. The model can override.
4. **PII is redacted before compression, not after.** Headroom runs locally but it's not a redaction layer. PII is redacted at the source (per [[04 Direct-Intake MCP]] auto-redaction rules), then compressed. Compressed PII is still PII.

## `headroom learn` — the closed loop

Headroom ships a learning loop: `headroom learn` mines failed sessions and writes corrections to `CLAUDE.md` / `AGENTS.md`. For Mavis, the equivalent is writing corrections to `agent.md` (the procedures file) and `learnings.md` (the instincts file).

The integration:

```bash
# After a session that produced errors
npx headroom learn
# or
~/.mavis/headroom/learn.sh

# Outputs corrections to:
#   agent.md — procedural updates
#   learnings.md — instinct additions (with confidence + evidence)
#   99 _system/instincts/i-<date>-<n>.md — atomic instinct entries
```

This is the [[Instincts as Atomic Learnings]] pattern applied to compression failures specifically. When Headroom's compressor degrades accuracy on a specific content type, the correction is "for content type X, use compressor Y with threshold Z." That correction is an instinct.

## Cost economics

- **Local Kompress-base** — free, host-side, ~50ms per 1K tokens on CPU, ~5ms on GPU. No API call.
- **CacheAligner** — free, deterministic, microseconds.
- **CCR storage** — local SQLite (or DuckDB), ~1KB per compressed block, ~10MB for a year of session history. Trivial.
- **`headroom learn`** — free, host-side, runs after session end.

The cost of running the layer is negligible. The savings are 50-90% of the M3 input token cost. The ROI is unbounded within the budget.

## Tool surface (the MCP server)

If we expose Headroom as an MCP server, the tool surface is:

```typescript
// Compress content (the main entry point)
headroom_compress({
  content: string,
  content_type?: "json" | "code" | "text" | "image" | "auto",
  model: string,
  aggressive?: boolean,        // trade accuracy for compression
}) => {
  compressed: string,
  ccr_hash: string,            // for retrieval
  original_tokens: number,
  compressed_tokens: number,
  compression_ratio: number,
}

// Retrieve original (the CCR primitive)
headroom_retrieve({
  ccr_hash: string
}) => {
  content: string,
  original_tokens: number,
  retrieved_at: string,
}

// Stats — what's been compressed, ratios, accuracy hits
headroom_stats({
  time_range?: { start: string, end: string }
}) => {
  total_compressed: number,
  total_original_tokens: number,
  total_compressed_tokens: number,
  avg_compression_ratio: number,
  retrieval_count: number,
  cache_hit_rate: number,      // CacheAligner effectiveness
}
```

The MCP server is the cleanest integration — the model can call `headroom_compress` on any content it produces or consumes, and `headroom_retrieve` on any hash it has.

## The 5 hard "when NOT to use" cases

Headroom is not always the answer:

1. **Small prompts** — A 1K-token prompt doesn't need compression. Threshold: skip compression if total prompt is < 10K tokens after the cache-aligned prefix.
2. **Proof-of-correctness content** — math proofs, security audits, contract clauses. Use `IntelligentContext` with high importance scoring, or don't compress.
3. **Real-time streaming** — when content is being streamed to the user as it's generated, compression adds latency. Skip for live UI.
4. **PII already in the prompt** — compress PII *after* redaction, not before. Pre-compression PII is still PII.
5. **Adversarial inputs** — when the prompt is untrusted, compression can hide prompt injection. Compress only the trusted parts.

## What this is NOT

- **Not a replacement for retrieval.** Headroom compresses what comes back. `vault-brain` is still the index. They're complementary.
- **Not a privacy mechanism.** Headroom runs locally but it's not a redaction layer. PII still needs to be redacted *before* compression.
- **Not magic on dense signal.** High-density content (proofs, security logs) doesn't compress well. Headroom knows this and routes around it.
- **Not a substitute for the long-context-curator.** The curator decides *what* goes into the prompt; Headroom decides *how dense* each piece is. Both are needed.

## Connections

- [[00 Overview]] — the project hub
- [[Context Compression as First-Class Layer]] — the deep-dive note on Headroom
- [[03 The Custom MCP Arsenal#MCP #3: `long-context-curator`]] — the curator is the primary integration point
- [[03 The Custom MCP Arsenal#MCP #1: `vault-brain`]] — vault-brain is the highest-leverage source to compress
- [[04 Direct-Intake MCP]] — intake drops should compress before they hit the inbox note
- [[Mavis EA Workflow]] — the daily brief, weekly review, and intake triage are cache-aligned prefix candidates
- [[Paged Memory Pattern]] — paged memory and compression are complementary
- [[Instincts as Atomic Learnings]] — `headroom learn` outputs become instincts
- [[learnings]] — `[capability]` entry on Headroom
- https://github.com/chopratejas/headroom — the source

## Anticipated future direction

- **Local Kompress-base fine-tune** on Andre's vault — the trained model is general; a vault-specific fine-tune would boost compression ratio on his actual content
- **Compression-aware curator** — the long-context-curator learns which content compresses well and packs denser
- **Budget-aware prompt building** — the prompt assembler tracks session spend and routes through heavier compression as the budget runs down
- **CCR cross-session memory** — the same content appearing in multiple sessions gets a stable CCR hash; the model can recognize it across sessions

---

*Design doc 2026-06-02. Written during Operation Omniscience Phase 2. The integration is wired into [[04 Direct-Intake MCP]] and the curator (per [[03 The Custom MCP Arsenal]]). Build pending greenlight.*
