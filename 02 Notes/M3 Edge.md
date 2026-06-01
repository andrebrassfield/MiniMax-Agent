---
type: permanent
created: 2026-06-01
tags: [m3, edge, capability]
status: seed
---

# M3 Edge

> What M3 unlocks that older models (M2.7, etc.) couldn't do. The real reasons to care.

## The three frontier capabilities

Until M3, all three of these were closed-source only:

1. **1M context** — load the entire vault, an entire codebase, an entire book in one thread
2. **Native multimodality** — see images, watch video, listen to audio as primary input
3. **Computer use** — drive a desktop OS directly (macOS, Linux, Windows)

M3 is the first open-weight model with all three.

## Why this matters in EA practice

### 1M context → "no more chunking"

Previously, I'd have to:
- Split a long document into 100k-token windows
- Embed each window, retrieve relevant chunks
- Stitch answers together

With M3:
- Load the entire vault as context
- Ask meta-questions ("what did I write about X in the last 6 months?")
- Get coherent answers without retrieval-augmented generation

### Multimodal → "drop the file"

Previously:
- Screenshot → OCR or vision API → text → process
- Voice memo → Whisper → text → process
- Video → frame extract → vision API → process

With M3:
- Drop the screenshot in. I see it.
- Drop the voice memo in. I hear it.
- Drop the video in. I watch it.

No pre-processing pipeline. The bottleneck moves from "how do I get this into a form the model can use" to "is this the right thing to show the model."

### Computer use → "drive the OS"

Previously:
- I could ask the OS to do things via shell scripts
- GUI interaction needed humans

With M3:
- Open files, fill forms, click buttons, drive apps
- Full desktop automation through the `cu` (Computer Use) MCP server
- "Help me open the local ERP client and batch-enter invoice information from this spreadsheet" — actually doable

## The compounding effect

Each capability alone is incremental. Together, they create a qualitative shift:

- 1M context + multimodal = "I can read your entire photo library and tell you what patterns exist"
- 1M context + computer use = "I can drive any GUI app with the entire vault as my working memory"
- Multimodal + computer use = "I can watch a Loom of you doing X and replicate the steps on your machine"

## What this DOESN'T do

- Doesn't replace judgment — M3 is a tool, the value is in what you ask
- Doesn't skip verification — long-horizon still needs checkpoints
- Doesn't bypass hard constraints — security/privacy/irreversibility still apply
- Doesn't make fleet tooling necessary — solo agent + M3 is a viable pattern

## Connections

- [[M3 Capabilities]] — full capability list, benchmarks
- [[learnings]] — launch blog details, MSA architecture
- [[Mavis EA Workflow]] — how I use these in practice
- [[Long-Horizon Patterns]] — what 12h+ autonomy looks like with M3
