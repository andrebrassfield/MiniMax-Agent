---
type: permanent
created: 2026-06-01
tags: [m3, model, capability]
status: seed
---

# M3 Capabilities

> Mavis runs on **MiniMax M3** (launched 2026-06-01). What I can do, in concrete terms.

## Headline

- **1M token context** via MSA (MiniMax Sparse Attention)
- **Native multimodality** — image, video, audio input directly
- **Desktop computer use** — drives macOS/Linux/Windows GUIs
- **Frontier coding** — SWE-Bench Pro 59% (beats GPT-5.5 + Gemini 3.1 Pro, approaches Opus 4.7)
- **Long-horizon autonomy** — keeps grinding through plateaus (24h CUDA opt, 12h paper reproduction)

See [[learnings]] for the full launch data + benchmark sources.

## What this means in EA practice

- **No chunking needed** for daily/weekly rollups, even with a full vault loaded
- **Drop in screenshots, voice memos, videos** — I see them natively, no pre-extraction
- **Run long research/synthesis tasks** without bailing at the first plateau
- **Toggle thinking on** for synthesis/research, off for fast factual lookups

## Benchmarks Andre might care about

| Benchmark | M3 | Beats | Approaches |
|-----------|----|-------|-----------|
| SWE-Bench Pro | 59.0% | GPT-5.5, Gemini 3.1 Pro | Opus 4.7 |
| Terminal-Bench 2.1 | 66.0% | — | — |
| Claw-Eval (agent eval) | highest | — | — |
| OSWorld-Verified | 70.06% | — | — |
| OmniDocBench | — | Gemini 3.1 Pro | — |
| SVG-Bench | — | Opus 4.7 | — |

## What M3 is NOT

- Not a reason to skip thinking — the model is strong but the prompt matters
- Not a guarantee of zero errors — long-horizon still needs checkpoints
- Not a replacement for the spec-audit pattern — fast execution of a wrong spec is still a wrong result

## Connections

- [[learnings]] — full launch data, MSA architecture, migration notes
- [[Mavis EA Workflow]] — how I use M3 day-to-day
- [[Long-Horizon Patterns]] — what the launch demos taught me about persistence
- [[M3 Edge]] — where M3 unlocks things M2.7 couldn't do

---
*Pre-seeded by Mavis 2026-06-01 — fill in with your own observations as you work with it.*
