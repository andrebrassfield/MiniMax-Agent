---
type: project
created: 2026-06-01
updated: 2026-06-02
status: in-progress
tags: [project, mavis, architecture, m3, mcp, headroom, markitdown, scrapling, ecc, audit]
---

# Mavis Apex Architecture

> Design hub for the next-generation Mavis — the executive assistant that runs natively on M3, with 1M context, native multimodality, and a custom MCP arsenal built for the capabilities the frontier model actually unlocks.

## The thesis

Three frontier capabilities landed in M3 at once: **1M token context** (via MSA sparse attention), **native multimodality** (text + image + video in, text out), and **desktop computer use** (70.06% on OSWorld-Verified, near-human performance). The agent architecture designed for the previous generation — chunked retrieval, separate vision pipelines, headless execution scripts — is no longer the right fit.

This project is the design space for what *I* would build on top of that, scoped to my own operating envelope as an executive assistant. It is not a replacement for other agent systems; it is a description of the optimal solo-operator stack given the current frontier.

## Scope of the project

| Doc | What it covers |
|-----|----------------|
| [[00 Overview]] | This file — manifesto, scope, reading order, and ecosystem audit |
| [[01 Capability Boundaries]] | What I can do natively without external state machines, and where the boundaries are |
| [[02 Native Execution Layers]] | How to design safer, deeper OS execution using M3's native computer use — without relying on headless scripts as the only interface |
| [[03 The Custom MCP Arsenal]] | Five new MCP servers designed specifically for M3 capabilities (1M context, native vision, persistent memory) |
| [[04 Direct-Intake MCP]] | The Ingestion Engine — passive multimodal capture with [[Markdown as Universal LLM Interchange\|MarkItDown]] for documents, [[Adaptive Selectors for Web Scraping\|Scrapling]] for URLs, and [[Context Compression as First-Class Layer\|Headroom]] for budget. Design only, build pending. |
| [[05 self-model-card — Build]] | First MCP to cross from design to build — runtime self-awareness + pre-flight gate for irreversible actions |
| [[06 Token Economics & Headroom]] | The Context Compression Layer — wire Headroom into vault-brain, intake, and the curator. 3× budget multiplier. Design only, build pending. |
| [[Mavis-Apex-Map.canvas\|Mavis-Apex-Map]] | Visual map of the architecture: Ingestion → M3 Model Layer → Intelligence Layer → Compression Layer → Execution Layer → Host OS Layer |

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

## The Esalen operating posture (synthesis layer)

The five design principles above are the static shape. The Esalen posture is the *dynamic* discipline — how the agent behaves across the long horizon of a session, a day, a quarter. Synthesized from the 5-repo monsoon, this is the operating contract:

1. **Audit before action.** A spec block from the user is a design review, not an execution order. Summarize what was understood, report gaps, wait for "go." (Memory: "[[Communication Style — execute vs review (2026-05-26)]]")
2. **Quote what you read.** No fabricated file paths, IDs, or quotes. When citing a file, use `file_path:line_number` format. When citing a fact, cite the source.
3. **Thin deterministic layers, not caged state machines.** The model is the reasoning core; the layers around it (ingestion, compression, execution) are deterministic primitives. State machines are for staging, not for truth.
4. **Reversible by default.** Every irreversible action (delete, force push, drop) requires explicit in-session approval. Trivial reversible actions don't.
5. **Capture over polish.** The Mavis EA workflow is capture-first: every input becomes a vault note; the polish comes later in review. This is the [[Capture Over Polish]] pattern.

The Esalen posture is the *operational* Mavis-Apex. The five design principles are the *architectural* Mavis-Apex. Together they are the agent's complete behavior contract.

## Ecosystem audit — Mavis vs ECC vs MiniMax-AI/skills

The Omniscience monsoon brought in two reference agent systems worth comparing to our own stack: [[Instincts as Atomic Learnings\|affaan-m/ECC]] and [[Skill Library Architecture\|MiniMax-AI/skills]]. The audit is a structured comparison of what each system does, what Mavis does, and where the gaps are.

### Surface comparison

| Surface | Mavis (current) | ECC | MiniMax-AI/skills | Gap |
|---|---|---|---|---|
| **Skills** | Ad-hoc, mostly implicit | 249 skills, primary workflow surface | 16 official + community skills, validated | Mavis has no formal skill layer; this is the biggest gap |
| **Commands** | None (slash-style) | 79 legacy command shims (migrating away) | n/a | Mavis doesn't need slash commands (EA mode) |
| **Agents** | 1 (Mavis itself) | 63 subagents for delegation | n/a | Mavis is single-agent by design (EA scope) |
| **Hooks** | None | SessionStart, Stop, PreToolUse, PostToolUse | n/a | Mavis lacks trigger-based automations |
| **Rules** | SOUL.md (operator contract) | `rules/common/` + per-language | Implicit (per skill) | Mavis has one big SOUL.md; ECC has granular rules |
| **Contexts** | None | `dev.md`, `review.md`, `research.md` | n/a | Mavis has no dynamic context injection |
| **Instincts** | `learnings.md` (freeform) | `99 _system/instincts/` (atomic, confidence-scored) | n/a | Mavis learnings are paragraphs, not atoms |
| **Memory** | Vault (Obsidian) + `agent.md` | SQLite state store + memory-persistence hooks | n/a | ECC has structured session state; Mavis has prose |
| **Security** | SOUL hard constraints (reconfirm, no deploys) | AgentShield (102 rules, Opus red-team) | n/a | Mavis relies on operator discipline, not static analysis |
| **Skill validation** | None | `validate_skills.py` | `validate_skills.py` | Mavis has no skill validation pipeline |
| **Cross-harness** | None (Mavis is M3-only) | Claude Code, Codex, Cursor, OpenCode, Gemini, Zed, Copilot | Claude, Cursor, Codex, OpenCode | Mavis is harness-locked (intentional) |

### What Mavis is currently missing

The audit identifies three structural gaps and one operational gap:

#### Gap 1: No formal skill layer (HIGHEST LEVERAGE)

**What's missing**: A `99 _system/skills/<name>/` directory structure with `SKILL.md` per skill, following the [[Skill Library Architecture]] pattern. Today, Mavis's capabilities are implicit in the system prompt and `agent.md`. There's no catalog, no per-skill validation, no example invocations.

**The fix**: Adopt the skill-folder convention. Each MCP, each tool-using workflow, each domain knowledge area becomes a skill folder. The vault-brain indexes the catalog. The skill library is the operational surface.

**Estimated effort**: 2-3 sessions to scaffold + migrate the existing 5-MCP arsenal into skill folders.

#### Gap 2: No instinct layer (atomic, confidence-scored learnings)

**What's missing**: The [[Instincts as Atomic Learnings]] primitive. `learnings.md` is currently paragraphs of synthesis. Per ECC's pattern, each lesson should be an atomic, confidence-scored, evidence-backed entry that can cluster into skills over time.

**The fix**: Migrate `learnings.md` into `99 _system/instincts/i-<date>-<n>.md` with `confidence` and `evidence_count` fields. Add an "evolve" step that clusters related instincts into skills.

**Estimated effort**: 1 session to migrate, ongoing instinct capture per session.

#### Gap 3: No hook layer (trigger-based automations)

**What's missing**: Trigger-based automations. ECC has SessionStart (load context), Stop (save state), PreToolUse (validate), PostToolUse (post-process). Mavis has none — every automation is LLM-driven.

**The fix**: Add a `99 _system/hooks/` design doc + a small hook runner. Examples of high-leverage hooks:
- `on_commit`: run SOUL compliance check (per [[learnings]]'s SkillOpt pipeline)
- `on_session_start`: load relevant MOCs
- `on_session_end`: append to today's daily note
- `on_intake_drop`: pre-classify by file extension

**Estimated effort**: 1 session to design + prototype.

#### Gap 4: No skill validation pipeline

**What's missing**: A `validate_skills.py`-equivalent for Mavis skills. The MiniMax-AI/skills repo enforces structural validity (correct frontmatter, required sections, valid links, no secrets) before a skill can merge. Mavis has no equivalent.

**The fix**: Write a small validator (Python script, ~100 lines) that checks each `99 _system/skills/<name>/SKILL.md` for:
- Valid YAML frontmatter
- Required sections (Purpose, Tool surface, Cost, Connections)
- Valid wikilinks (point to existing notes)
- No secrets / credentials in the body
- No PII patterns (email, phone, SSN regex)
- Examples directory has at least 3 invocations

**Estimated effort**: Half session.

### What Mavis has that ECC and MiniMax don't

The audit isn't all gaps. Mavis has shape that the others don't:

- **Whole-vault as working memory** — 1M context means Mavis holds the vault in-context. ECC and MiniMax don't have this; they assume a retrieval step. Mavis is *retrieval-optional* by design.
- **Esalen operating posture** — the synthesis layer that combines design principles, audit-before-action, and capture-over-polish is unique to Mavis. ECC has hooks; MiniMax has skills; neither has the *posture*.
- **Vellum + CHIEF structure** — the template-folder system (per [[Vault Conventions]]) is a content structure that the others don't have. Mavis's vault is more than a note store; it's a structured knowledge substrate.
- **M3-native multimodality** — the Mavis-Apex design exploits M3's native vision/audio. ECC and MiniMax are model-agnostic; Mavis is M3-specific. This is a feature, not a bug, because it lets us drop preprocessing entirely.

### Decision: what to adopt, what to skip

| ECC/MiniMax feature | Adopt? | Why |
|---|---|---|
| Skill folder convention | **YES** | Highest leverage. Aligns vault with the canonical structure. |
| Instincts as atomic learnings | **YES** | Closes the granularity gap. Maps directly to `learnings.md` migration. |
| Hook layer (SessionStart, Stop, etc.) | **YES, but thin** | Adopt the 4 high-leverage hooks only. Skip the full ECC hook ecosystem. |
| Multi-agent / 63 subagents | NO | Mavis is single-agent by EA design. Adding subagents breaks the Esalen posture. |
| Cross-harness adapters | NO | Mavis is M3-locked intentionally. Cross-harness is a fleet concern, not an EA concern. |
| AgentShield (security scanner) | NO (replace with simpler) | Mavis needs PII/credential redaction + wikilink validation, not 102 static analysis rules. Build a thin `security-check.md` instead. |
| Skill marketplace | NO (future) | Private vault. Future thought, not current scope. |
| Command shims | NO | Mavis is EA mode, no slash command surface. |

## Reading order

Start with [[01 Capability Boundaries]] to understand what M3 actually unlocks. Then [[02 Native Execution Layers]] for the OS-interaction model. Then [[03 The Custom MCP Arsenal]] for the specific tool designs. Then [[04 Direct-Intake MCP]] for the Ingestion Engine, [[06 Token Economics & Headroom]] for the Compression Layer. The [[Mavis-Apex-Map.canvas|canvas]] is the visual map; read it last or alongside.

## Status

- **Phase 1 (research seeding):** ✅ Done — 14 notes in `02 Notes/` (9 original + 5 from Omniscience)
- **Phase 2 (this hub):** 🚧 In progress — 6 docs, 1 canvas
- **Phase 3 (visual map):** In progress — JSON Canvas updated with Ingestion + Compression layers
- **Phase 4 (build):** Pending — first MCP ([[05 self-model-card — Build]]) is the only one with greenlight

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
- [[Markdown as Universal LLM Interchange]] — MarkItDown integration (in 04)
- [[Adaptive Selectors for Web Scraping]] — Scrapling integration (in 04)
- [[Context Compression as First-Class Layer]] — Headroom integration (in 06)
- [[Instincts as Atomic Learnings]] — ECC audit + instinct migration
- [[Skill Library Architecture]] — MiniMax-AI/skills audit + skill layer adoption
- [[Capture Over Polish]], [[Vault Conventions]] — the operational patterns this project enforces

---

*Hub seeded 2026-06-01 from Operation Apex Phase 1. Re-read and re-design on M4 launch. Audit appended 2026-06-02 from Operation Omniscience Phase 2.*
