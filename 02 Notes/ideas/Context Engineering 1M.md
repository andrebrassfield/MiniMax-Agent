---
type: idea
created: 2026-06-01
status: seed
tags: [idea, context-engineering, long-context, m3]
---

# Context Engineering for 1M Tokens

> 1M context is not "just more room" — it's a different design surface. You have to stop stuffing and start curating, or the lost-in-the-middle effect eats your signal.

## Why this matters

Anthropic made 1M tokens generally available on Claude Opus 4.6 / Sonnet 4.6 at flat per-token rates (no long-context premium). [[M3 Capabilities]] ships 1M as well with MSA at 1/20th the per-token compute of M2. The "wall-clock" bottleneck is mostly gone; the engineering bottleneck moved to *what to put in the window and in what order*.

The "Lost in the Middle" effect (Liu et al. 2023, replicated by Vectara's Hughes 2024 and others) is real and persistent: even frontier models show U-shaped recall — strong at the start and end of context, weak in the middle. MRCR v2 (the multi-round coreference benchmark) shows Opus 4.6 at 76% vs Gemini 3 Pro at 26.3% on long-context retention. **Big windows don't fix the U-shape automatically.**

So: bigger window ≠ better agent. The leverage is in *how* you fill it.

## Where this came from

Anthropic's "Effective context engineering for AI agents" engineering post (2024), the Vectara leaderboard, the MRCR v2 benchmark, plus the field reports from Bolt.new, iGent AI, and others on what 1M enabled for their code agents. Also: my own observation that loading the entire vault into a single M3 thread gives coherent cross-vault answers without RAG retrieval — but only if the most relevant chunks are at the start and end of the prompt.

## What would have to be true for this to be right

- Most production tasks at 1M scale will be **retrieval-plus-direct-context hybrids**, not pure RAG replacement. (RAG still wins on cost, latency, freshness, and when the corpus exceeds 1M tokens.)
- The right primitive isn't "more context" — it's **a context-budget allocator**: pre-prompt step that ranks candidate chunks by expected marginal information value, then places them in the prime attention slots (start + end) and demotes filler to the middle.
- **Compaction at 50K intervals** (Anthropic's pattern) is a default, not an optimization. The model needs to summarize what it just learned before the next batch of tool results hits.
- MSA-aware ordering matters: the model selects KV blocks by relevance score, so high-signal blocks near the query get attended more reliably than high-signal blocks buried mid-context.

## What would falsify this

- If MRCR-style retrieval benchmarks show flat performance from 200K to 1M for well-structured prompts, the U-shape concern was overblown. (So far: hasn't happened. Performance does degrade past ~256K even on Claude 4.6 — about 18% drop to 1M, vs Gemini's ~57% drop.)
- If a model trained with explicit "middle-context boost" (e.g., learned positional encodings that upweight mid-context) matches end-position accuracy, the U-shape is engineering-fixable. (Mixed evidence — positional encoding tricks help but don't fully close the gap.)
- If RAG + 200K context matches 1M-no-RAG on agentic long-horizon benchmarks, the whole 1M context-as-infrastructure argument collapses. (Havent seen this. Long-horizon agents strongly benefit from accumulated tool-result history that RAG can't reconstruct.)

## Connections

- [[M3 Capabilities]] — the 1M that makes this design surface usable
- [[M3 Edge]] — same content, framed as capability vs as engineering
- [[Paged Memory Pattern]] — the natural complement: tier 1 is curated context, tier 2 is the rest
- [[Mavis EA Workflow]] — every daily/weekly rollup is a context-engineering exercise
- [[Long-Horizon Patterns]] — 12h+ runs accumulate state; context budget is the constraint

## See also

- Anthropic's "Effective context engineering for AI agents" engineering post
- Vectara's lost-in-the-middle leaderboard (Hughes 2024)
- The "drop the long-context premium" coverage in The New Stack / Winbuzzer (Mar 2026)
- iGent AI on multi-day coding sessions with 1M context

---
*Seed from Operation Apex Phase 1 (2026-06-01). Falsifiable in 6 months when next-gen MRCR results come in.*
