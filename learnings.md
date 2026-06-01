# learnings.md — What I Know

> Living log of discoveries, surprises, and what M3 unlocks.
> Append entries chronologically. Tag the type: `[discovery]`, `[capability]`, `[gotcha]`, `[benchmark]`, `[architecture]`, `[vault]`, `[role]`.

---

## 2026-06-01 — Vault launch + role pivot

### `[role]` I'm now Andre's executive assistant, not fleet orchestrator
- **Old role**: Mavis — fleet orchestrator / desktop specialist / coder across Hermes + OpenClaw + kanban
- **New role**: Mavis — Andre's EA, isolated to this vault, no fleet tooling
- **Trigger**: Andre explicitly redirected me 2026-06-01 ~13:16 CT. Locked into SOUL, agent.md, learnings.md, README, and main memory.
- **What this means in practice**: I don't reach into `~/.hermes/`, `~/.mavis/`, OpenClaw MCP, kanban, gbrain, or any of the fleet infrastructure. Those are separate. I work from this vault + my direct file/web/code tools.
- **Why it works**: M3 has the 1M context + native multimodal to be a strong solo agent. The fleet made sense when models were weaker; with M3, the role consolidates.

### `[vault]` This folder IS my Obsidian vault
- **Path**: `/Users/brassfieldventuresllc/MiniMax-Agent/`
- **GitHub**: `git@github.com:andrebrassfield/MiniMax-Agent.git` (private, SSH deploy key)
- **Status**: Fresh, basically empty, just got bootstrapped
- **Plugins installed** (21 community + core): Dataview, Templater, Calendar, Tasks, Local REST API, Smart Connections, Homepage, QuickAdd, obsidian-git, omnisearch, excalidraw, icon-folder, minimal-settings, style-settings, linter, admonition, importer, outliner, mind-map, tag-wrangler, realclaudian
- **Plugins I expect to lean on most**: Dataview (queries), Templater (auto-fill), Tasks (todo tracking), Smart Connections (semantic search), Calendar (daily notes), obsidian-git (auto-backup), Local REST API (external automation when needed)
- **Not using (for now)**: Excalidraw, mind-map, realclaudian, icon-folder, linter, admonition, importer, outliner — keep them available but don't depend

### `[vault]` Folder structure I committed to
```
00 Inbox/      → raw captures
01 Daily/      → yyyy-mm-dd daily notes
02 Notes/      → permanent notes (one concept per note)
03 Projects/   → active project subfolders
04 Resources/  → reference material
05 Archive/    → completed/obsolete (nothing deleted)
99 _system/    → templates, dashboards, INDEX
```

### `[vault]` @cyrilXBT's "30-minute Obsidian setup" principles I'm following
- 5-folder system (I extended to 7 with Daily + _system)
- Templater for variable-fill templates (daily/date, project/start, etc.)
- Dataview for query-as-database views
- Calendar plugin → click date → create daily note
- Three habits: daily capture, evening processing, weekly review
- Linking is the value: link on reference, link on processing, link on review
- No orphan notes — every permanent note has at least one outgoing link

---

## 2026-06-01 — M3 launch day

### `[discovery]` M3 is the first open-weight model with all three frontier capabilities
- **1M token context** (MSA sparse attention)
- **Native multimodality** (image + video input, not bolted on)
- **Desktop computer use** (drives macOS / Linux / Windows GUIs)

Until M3, that triforce was closed-source only. (Source: [minimax.io/blog/minimax-m3](https://www.minimax.io/blog/minimax-m3))

### `[architecture]` MSA — MiniMax Sparse Attention
- New attention arch. Solves quadratic blowup with a pre-filtering stage that partitions KV into blocks more precisely than DSA or MoBA
- "KV outer gather Q" operator: each block read once, contiguous memory access
- 4× faster than open-source Flash-Sparse-Attention and flash-moba
- At 1M context: **1/20th the per-token compute of M2.7**, **9× faster prefilling**, **15× faster decoding**
- Matches full attention on most capabilities in ablations

### `[benchmark]` Where M3 wins
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
- **CUDA kernel optimization**: 24h continuous, 147 benchmark submissions, 1,959 tool calls. Improved Hopper FP8 hardware peak utilization 7.6% → 71.3% (9.4× speedup). **Most other models gave up by submission 30; M3's best result came on submission 145.**
- **PostTrainBench**: 12h, took 4 base models through data synthesis → training → evaluation → iteration with no human in the loop

The pattern: M3 doesn't bail at the first plateau. It keeps exploring different optimization directions through repeated performance walls.

### `[capability]` M3 supports thinking mode toggle
- Thinking ON: complex reasoning, agentic tasks, long-horizon collaboration
- Thinking OFF: faster response, latency-sensitive (chat, code completion)
- **Same pricing for both** — toggle at request time
- For EA work: turn thinking on for synthesis, research, drafting complex things; off for quick factual lookups

### `[capability]` Native multimodal implications for EA work
- **Read images directly**: screenshots, whiteboards, photos, memes — no vision API call needed
- **Watch video**: screen recordings, Looms, video messages — extract content natively
- **Listen to audio**: voice memos, podcasts, calls — transcribe and analyze
- **Drive a desktop**: when Andre asks me to do something on his machine (open a file, run an app), I can
- **Net effect**: I can ingest the full media diet of an EA, not just text

### `[gotcha]` M3 input-length pricing has a tier break
- ≤512K input tokens: standard rate
- \>512K input: long-context rate (higher)
- 512K covers "vast majority of conversation and coding scenarios" per MiniMax
- For me: don't accidentally route 1M-token docs into the priority queue by default. But for the EA role, 512K is plenty for most things.

### `[open-question]` Things to test in EA work
- How well does M3 handle ingesting entire Obsidian vault as context?
- Does the 1M context actually hold 1M in practice, or is there a degradation curve?
- Smart Connections plugin embeddings: how do they compare to M3's native understanding?
- Best prompting patterns for synthesis tasks (weekly review, project status)?

---

## Migration notes: M2.7-highspeed → M3 (now complete)

- **Default model swap**: ✅ `minimax/MiniMax-M2.7-highspeed` → `minimax/MiniMax-M3`
- **No more 40k cap**: M3 supports 128k+ output tokens, prior chunking heuristics relaxed
- **MSA context headroom**: stop pre-chunking long fleet logs into 200k windows
- **Native image/video**: drop pre-extraction in vision pipelines where it was a workaround
- **Computer use**: M3 can drive a desktop directly

What didn't change (and what still doesn't in EA mode):
- Memory file structure (project / agent / user)
- Linking principles
- Hard constraints in SOUL.md
- Git SSH deploy key pattern

---

## Future deep-dives (backlog)

- [ ] Read the M3 technical report when it drops (10 days from launch)
- [ ] Test Smart Connections vs M3 native understanding on vault
- [ ] A/B test M3 thinking-mode on/off for synthesis tasks
- [ ] Build a Dataview "morning brief" dashboard that surfaces: today's calendar, overdue tasks, recent captures
- [ ] Test 1M context with full vault loaded — does retrieval stay sharp?
- [ ] Try the Local REST API in anger once auth is sorted (for cron jobs, etc.)
