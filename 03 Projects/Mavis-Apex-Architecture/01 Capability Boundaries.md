---
type: project
created: 2026-06-01
status: seed
tags: [project, mavis, architecture, capabilities, m3]
---

# 01 Capability Boundaries

> What Mavis can do natively on M3 without external state machines, headless execution layers, or chunked retrieval pipelines — and where the edges of that capability are.

## The native capability surface

M3 lands three frontier capabilities in one model. For an EA-mode operator, the implications are direct:

### 1. **1M token context as working memory**

A single M3 thread can hold:
- The full Obsidian vault (this is 2-5K notes, ~1-2M tokens of markdown; the active slice is well under 1M)
- An entire medium codebase (Bolt.new, iGent AI reported 75K+ lines feasible)
- A week's worth of email, calendar, meeting transcripts, and reference docs
- Long video transcripts (M3's multimodal training included video)
- A long-running research task's accumulated state (tool results, intermediate notes, partial summaries)

**What this changes:** the boundary between "in context" and "out of context" is now soft. The old reflex of "summarize, then drop" was a context-budget reflex; with 1M, the reflex becomes "compact at 50K intervals, but keep the rest." See [[02 Notes/ideas/Context Engineering 1M|Context Engineering 1M]].

**What this does NOT change:** the lost-in-the-middle effect. Mid-context attention still weakens. Order matters. The design discipline of "put the critical signal at the start and end, summarize for the middle" still applies.

### 2. **Native multimodality as primary input**

M3 takes text, images, and video directly. No preprocessing pipeline. For an EA:
- Drop in a screenshot of an error dialog — the model reads it
- Drop in a voice memo transcript — already text, but the model also processes the audio
- Drop in a Loom of someone demonstrating a workflow — the model can watch and replicate
- Drop in a photo of a whiteboard sketch — the model sees it

**What this changes:** the boundary between "I need to describe this" and "I can just show it" is gone. The bottleneck moves from "how do I get this into a form the model can use" to "is this the right thing to show the model." See [[02 Notes/ideas/Multimodal GUI Loop|Multimodal GUI Loop]].

**What this does NOT change:** visual reasoning is still harder than text reasoning. A photo of a financial chart is not the same as the underlying data. Multimodal inputs are evidence, not ground truth.

### 3. **Computer use as a primary execution channel**

M3's OSWorld-Verified score of 70.06% is near-human (72.36%). The `cu` MCP server exposes this directly. For an EA:
- Drive any GUI app, not just CLI tools
- Fill forms, click buttons, navigate dialogs
- Combine with native vision to "see" the screen state and decide what to click next
- Run multi-app workflows (copy from Sheets, paste into Gmail, attach to Calendar)

**What this changes:** the assumption that "the EA can't touch closed-source apps" goes away. The native execution layer reaches the entire OS surface. See [[02 Notes/ideas/Multimodal GUI Loop]] and [[02 Native Execution Layers]].

**What this does NOT change:** GUI is slower and more brittle than CLI. Where the API exists, use it. GUI is for when there's no API, or when the GUI reveals state (visual feedback, layout, etc.) that the API doesn't surface.

## What I can do natively that the old stack couldn't

| Old stack required | M3 native replaces it with |
|---|---|
| Embed + retrieve (RAG) over a 100K-token corpus | Load the full corpus into context when relevant |
| OCR + parse + extract for screenshots | Direct image input |
| Whisper + post-process for audio | Direct audio input |
| Headless Playwright + element selectors | Direct visual GUI interaction |
| Frame extraction + vision for video | Direct video input |
| Manual context summarization to fit limits | Selective compaction at 50K-token intervals |
| External state machine to track workflow progress | In-context plan + [[Reflexion Loop]]-style memory |

## Where the boundaries are

### Hard limits

- **Context is still finite.** 1M is a lot, not infinite. A 10M-token vault still needs retrieval-first.
- **Latency scales with context.** 1M context ≠ 1M context at 100ms. Wall-clock cost is real.
- **M3 doesn't replace the OS.** Computer use is a layer on top of the OS, not a replacement. The OS still has its own auth, permissions, file system, processes. M3 doesn't bypass sudo.
- **The model can't see what's not on screen.** Computer use sees the visible UI. Background processes, hidden windows, OS-level state — the model doesn't see those by default. (`cu` exposes some of this; check the MCP server's tool surface.)
- **MSA has selection errors.** The 1/20 compute comes with a quality trade at the edges. See [[02 Notes/questions/MSA Signal Decay|MSA Signal Decay]].

### Soft limits (workaroundable with care)

- **Cost per query at 1M is high.** Even with MSA's 1/20, a fully-loaded 1M query is more expensive than a 200K one. Use it when it earns its keep; don't burn it on tasks that fit comfortably in 200K.
- **Lost-in-the-middle still bites.** Mitigate with context-budget allocation: critical signal at the start and end, filler in the middle, or selective compaction to keep "always-on" state at the front.
- **GUI grounding errors.** M3 is 70% on OSWorld, not 100%. The 30% failure rate is real; the model will click the wrong button sometimes. Design with confirmation steps, undo paths, and observability.
- **Tool surface area = risk.** Every tool exposed to the model is an attack surface and a confusion surface. The right number of tools is "as few as possible to do the job, each documented sharply."

## The implications for my operating envelope

If I internalize this capability surface correctly, the [[Mavis EA Workflow|Mavis EA Workflow]] should evolve:

1. **Default to native over wrapper.** Show, don't describe. Load, don't retrieve. Drive the OS, don't script the API.
2. **Default to context over external state.** The plan lives in the prompt. The progress tracker lives in the prompt. The list of open questions lives in the prompt. External systems (Obsidian for permanence, kanban for visibility) are for *staging and sharing*, not for primary state.
3. **Default to self-correction over prevention.** With [[Reflexion Loop]]-style reflection baked into the workflow, I can attempt more things and recover. The cost of an error is "a self-reflection + a retry," not "a 20-state machine to prevent the error."
4. **Default to composition over framework.** Don't import a multi-agent orchestration library when 30 lines of [[Mixture of Agents|MoA]]-style aggregation does the job. Don't import a state machine library when a numbered todo list in the prompt does the job.

This is the design surface. Where the design surface is hard — MSA blind spots, GUI grounding errors, lost-in-middle — I lean on the workarounds in [[02 Native Execution Layers]] and the custom tools in [[03 The Custom MCP Arsenal]].

## Connections

- [[00 Overview]] — the project hub
- [[02 Native Execution Layers]] — the OS-execution model
- [[03 The Custom MCP Arsenal]] — the specific tools that fill gaps
- [[M3 Capabilities]] — the raw capability numbers
- [[M3 Edge]] — what M3 unlocks
- [[02 Notes/ideas/Context Engineering 1M|Context Engineering 1M]] — the user-side discipline
- [[02 Notes/ideas/Multimodal GUI Loop|Multimodal GUI Loop]] — the GUI reasoning architecture
- [[Mavis EA Workflow]] — what this is the design evolution of
- [[Long-Horizon Patterns]] — what 12h+ runs look like with this capability surface

---
*Design document 2026-06-01. Re-validate when M4 lands; the capability surface moves with each model generation.*
