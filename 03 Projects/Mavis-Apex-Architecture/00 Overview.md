---
type: project
created: 2026-06-01
status: seed
tags: [project, mavis, architecture, m3, mcp]
---

# Mavis Apex Architecture

> Design hub for the next-generation Mavis — the executive assistant that runs natively on M3, with 1M context, native multimodality, and a custom MCP arsenal built for the capabilities the frontier model actually unlocks.

## The thesis

Three frontier capabilities landed in M3 at once: **1M token context** (via MSA sparse attention), **native multimodality** (text + image + video in, text out), and **desktop computer use** (70.06% on OSWorld-Verified, near-human performance). The agent architecture designed for the previous generation — chunked retrieval, separate vision pipelines, headless execution scripts — is no longer the right fit.

This project is the design space for what *I* would build on top of that, scoped to my own operating envelope as an executive assistant. It is not a replacement for other agent systems; it is a description of the optimal solo-operator stack given the current frontier.

## Scope of the project

| Doc | What it covers |
|-----|----------------|
| [[00 Overview]] | This file — manifesto, scope, and reading order |
| [[01 Capability Boundaries]] | What I can do natively without external state machines, and where the boundaries are |
| [[02 Native Execution Layers]] | How to design safer, deeper OS execution using M3's native computer use — without relying on headless scripts as the only interface |
| [[03 The Custom MCP Arsenal]] | Five new MCP servers designed specifically for M3 capabilities (1M context, native vision, persistent memory) |
| [[04 Direct-Intake MCP]] | Design spec for passive multimodal capture (screenshots, voice memos, links) into the vault — design only, build pending |
| [[05 self-model-card — Build]] | First MCP to cross from design to build — runtime self-awareness + pre-flight gate for irreversible actions |
| [[Mavis-Apex-Map.canvas\|Mavis-Apex-Map]] | Visual map of the architecture: M3 Model Layer → Intelligence Layer → Execution Layer → Host OS Layer |

## What this is NOT

- **Not a competitor to Hermes, OpenClaw, or any other fleet system.** The fleet runs separately and independently. This is a design document for my own EA-mode operations.
- **Not a build directive.** These are design notes — actual implementation requires a separate "go" decision per project.
- **Not a research artifact.** The research foundation is in `02 Notes/` under patterns/, ideas/, and questions/. This project hub applies that research to my specific operating envelope.
- **Not a permanent fixture.** The frontier moves fast. This document should be re-read every 6 months and rewritten when M4 lands.

## The five design principles

1. **The model is the working memory.** With 1M context, the agent no longer needs to delegate state to external systems by default. External state is for staging, not for truth.
2. **Native > wrapper.** If M3 can see it natively, don't OCR. If M3 can drive the OS, don't headless-script the API. If M3 can hold the whole vault, don't chunk-and-retrieve.
3. **Failure modes are a first-class design surface.** Don't just make the happy path fast. Design for the failures: lost-in-middle, MSA selection errors, GUI grounding errors, schema drift, tool self-healing. See [[Reflexion Loop]] and [[MSA Signal Decay]].
4. **Tool surface area = audit surface area.** Every tool I expose to the model is something that can be called. Smaller, sharper, more-documented tool surface is safer than a broad API. (Anthropic: "We spent more time optimizing our tools than the overall prompt.")
5. **Composition over framework.** Per Anthropic's "Building Effective Agents": simple, composable patterns beat complex frameworks. Don't import a framework to do what 30 lines of code can do.

## Reading order

Start with [[01 Capability Boundaries]] to understand what M3 actually unlocks. Then [[02 Native Execution Layers]] for the OS-interaction model. Then [[03 The Custom MCP Arsenal]] for the specific tool designs. The [[Mavis-Apex-Map.canvas|canvas]] is the visual map; read it last or alongside.

## Status

- **Phase 1 (research seeding):** ✅ Done — 9 notes in `02 Notes/`
- **Phase 2 (this hub):** 🚧 In progress — 4 docs, 1 canvas
- **Phase 3 (visual map):** Pending — JSON Canvas

## Connections

- [[M3 Capabilities]] — the raw model capability this architecture sits on top of
- [[M3 Edge]] — what M3 unlocks that older models didn't
- [[Mavis EA Workflow]] — current workflow this project is the design evolution of
- [[Mavis EA Design/00 Overview]] — the broader design thinking that this project extends
- [[Mixture of Agents]], [[Reflexion Loop]], [[Paged Memory Pattern]] — the foundational patterns
- [[Context Engineering 1M]], [[Paged Attention Economics]], [[Multimodal GUI Loop]] — the design ideas
- [[State Machine Failure Modes]], [[MSA Signal Decay]], [[M3 Bypass Hypothesis]] — the open questions
- [[learnings]] — M3 launch data and architecture details
- [[Long-Horizon Patterns]] — what 12h+ autonomy looks like with M3

---
*Hub seeded 2026-06-01 from Operation Apex Phase 1. Re-read and re-design on M4 launch.*
