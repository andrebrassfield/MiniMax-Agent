# learnings.md — What M3 Changed

> Living log of discoveries, surprises, and what M3 unlocks that M2.7 didn't.
> Append entries chronologically. Tag the type: `[discovery]`, `[capability]`, `[gotcha]`, `[benchmark]`, `[architecture]`.

---

## 2026-06-01 — M3 launch day

### `[discovery]` M3 is the first open-weight model with all three frontier capabilities
- **1M token context** (MSA sparse attention)
- **Native multimodality** (image + video input, not bolted on)
- **Desktop computer use** (drives macOS / Linux / Windows GUIs)

Until M3, that triforce was closed-source only. Now it's open-weight. (Source: [minimax.io/blog/minimax-m3](https://www.minimax.io/blog/minimax-m3))

### `[architecture]` MSA — MiniMax Sparse Attention
- New attention arch. Solves quadratic blowup with a pre-filtering stage that partitions KV into blocks more precisely than DSA or MoBA
- Operator-level optimization: "KV outer gather Q" — each block read once, contiguous memory access
- 4× faster than open-source Flash-Sparse-Attention and flash-moba
- At 1M context: **1/20th the per-token compute of M2.7**, **9× faster prefilling**, **15× faster decoding**
- Matches full attention on most capabilities in ablations

### `[benchmark]` Where M3 actually wins
| Benchmark | M3 | Notes |
|-----------|----|----|
| SWE-Bench Pro | 59.0% | Beats GPT-5.5 + Gemini 3.1 Pro, approaches Opus 4.7 |
| Terminal-Bench 2.1 | 66.0% | |
| SWE-fficiency | 34.8% | |
| KernelBench Hard | 28.8% | |
| MCP Atlas | 74.2% | |
| SVG-Bench | — | Surpasses Opus 4.7 |
| OmniDocBench | — | Beats Gemini 3.1 Pro |
| Claw-Eval | — | Highest score (autonomous agent eval, Pass³) |
| OSWorld-Verified | 70.06% | M3 uses 0–1000 relative coords, 1920×1080, Max Steps=200 |

### `[capability]` Long-horizon autonomous runs are a real thing now
- **Paper reproduction**: M3 ran ~12 hours autonomously, 18 commits, 23 figures, reproduced an ICLR 2025 Outstanding Paper end-to-end
- **CUDA kernel optimization**: 24h continuous, 147 benchmark submissions, 1,959 tool calls. Improved Hopper FP8 hardware peak utilization 7.6% → 71.3% (9.4× speedup). Most other models gave up by submission 30. **M3's best result came on submission 145**
- **PostTrainBench**: 12h, took 4 base models through data synthesis → training → evaluation → iteration with no human in the loop. Scored 0.37 (vs Opus 4.7 0.42, GPT-5.5 0.39)

The pattern: M3 doesn't bail at the first plateau. It keeps exploring different optimization directions through repeated performance walls. That's the kind of persistence that matters for real engineering work.

### `[capability]` MiniMax Code ships alongside M3
- Agent product trained jointly with M3
- "Agent Team" mode: multi-stage, concurrent, dynamically adjustable workflows
- Producer + Verifier adversarial harness loop — runs autonomously for days
- Built on top of OpenCode and Pi (will be open-sourced)
- Native computer use: e.g. "open local ERP client, batch-enter invoices from this spreadsheet"
- Desktop app: `agent.minimaxi.com/download`

### `[gotcha]` M3 input-length pricing has a tier break
- ≤512K input tokens: standard rate
- \>512K input: long-context rate (higher)
- 512K covers "vast majority of conversation and coding scenarios" per MiniMax
- Don't accidentally route 1M-token docs into the priority queue by default

### `[gotcha]` Service tiers
- Default: `standard` (regular requests)
- `priority` (`service_tier=priority`): scheduling priority, more stable latency under high concurrency
- **Priority channel is currently sales-only** — opening to all in "a few days"
- This affects SLA-sensitive industrial use cases

### `[capability]` M3 supports thinking mode toggle
- Thinking ON: complex reasoning, agentic tasks, long-horizon collaboration
- Thinking OFF: faster response, latency-sensitive (chat, code completion)
- **Same pricing for both** — toggle at request time
- No 30s vs 5min reasoning trade-off baked in like some competitors

### `[capability]` Token Plan tiers
| Tier | $/mo | Tokens/mo |
|------|------|-----------|
| Plus | $20 | ~1.7B |
| Max | $50 | ~5.1B |
| Ultra | $120 | ~9.8B |

Text, image, speech, music all share the same pool. One of the highest quotas at this price globally.

### `[discovery]` Evaluation methodology notes
- Many "Opus 4.7 / GPT-5.5 / Gemini 3.1 Pro" numbers come from official leaderboards, while M3 was tested on internal infrastructure with comparable scaffolding
- Several benchmarks (VIBE-V2, SVG-Bench, BankerToolBench) use MiniMax models as the **scoring model** — that's M2.7 for BankerToolBench. Worth noting when comparing
- SWE-fficiency: M3 tested with Claude Code scaffolding on open-source dataset
- PaperBench / PostTrainBench: Ralph-Loop mechanism for 12h runs
- Their own Claw-Eval: Pass³ metric, 161 tasks, Gemini 3.0 Flash as judge

### `[open-question]` Things to test in production
- How does M3 handle the 1M context for long fleet logs? Memory pressure?
- MSA's "1/20th compute" claim — does that hold on Apple Silicon MLX backend, or is it CUDA-tuned?
- Does the multimodal video input actually work through OpenClaw's MCP layer, or do I need to do pre-extraction?
- Long-horizon (12h+) autonomous runs: do my MCP timeouts / cron intervals survive that?
- Composer / loop stability: M3 is native multimodal — can I drive `cu` (Computer Use) directly from M3 without intermediate vision calls?

---

## Migration notes: M2.7-highspeed → M3

What changes in my day-to-day:
- **Default model swap**: `minimax/MiniMax-M2.7-highspeed` → `minimax/MiniMax-M3` (config update needed in provider config)
- **No more 40k cap**: workers that crashed at 40k output tokens should now hold 128k+
- **MSA context headroom**: stop pre-chunking long fleet logs into 200k windows
- **Native image/video**: drop pre-extraction in vision pipelines where it was a workaround
- **Computer use**: M3 can drive a desktop directly — `cu` MCP server + M3 = end-to-end agent

What doesn't change:
- Memory file structure (project / agent / user)
- Kanban schema
- GBrain write path (`gbrain put` only)
- Hard constraints in SOUL.md

---

## Future M3 deep-dives (backlog)

- [ ] Read the technical report when it drops (10 days from launch per the blog)
- [ ] Read the model card when weights go open-source
- [ ] A/B test M3 vs M2.7-highspeed on real fleet tasks (code review, multi-file refactor, long-doc synthesis)
- [ ] Stress test the 1M context — load entire vault, ask meta-questions
- [ ] Test MSA in the Apple Silicon path — does the 1/20th compute claim hold?
- [ ] Re-run fleet-router eval harness on M3 — does routing accuracy improve?
- [ ] Try M3 as the qa-auditor model (replacing whatever's scoring currently)
