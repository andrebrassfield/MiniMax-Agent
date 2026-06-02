---
type: pattern
created: 2026-06-02
tags: [pattern, skills, minimax, skill-architecture, mavis-apex, canonical-structure]
source: https://github.com/MiniMax-AI/skills
---

# Skill Library Architecture

> The MiniMax-AI/skills repo is the canonical reference for what a modern AI agent skill library looks like. Sixteen skills, each in its own folder with a `SKILL.md` (or top-level README), each addressing one capability, each installable independently, each validated by the same script. This is the structure Mavis should adopt for its skill layer.

## The principle

A skill library is not a dump of prompts. It's a structured catalog with:

1. **One skill per folder** — every skill is a directory. The directory is the unit of install, the unit of test, the unit of versioning.
2. **A `SKILL.md` (or `README.md`) at the top** — single source of truth for what the skill does, how to invoke it, and what the input/output contract is.
3. **A category in the metadata** — frontend, fullstack, mobile, devops, media, etc. Categorization enables routing.
4. **A source field** — `Official` (maintained by MiniMax) or `Community`. The provenance matters.
5. **A validation script** — `validate_skills.py` enforces the structure (correct fields, required sections, valid links).
6. **A PR review skill** — `pr-review/SKILL.md` documents what a good PR looks like, so contributors and reviewers share standards.
7. **A CREDITS.md** — for skills derived from open-source work. Attribution isn't optional.

The result: a library that scales. Adding a new skill doesn't break the old ones. Removing a skill doesn't leave dead references. The structure is the contract.

## The sixteen skills (the catalog)

| Category | Skills | Notes |
|---|---|---|
| **Frontend / fullstack** | `frontend-dev`, `fullstack-dev` | Premium design, cinematic animations, full-stack architecture |
| **Mobile (native)** | `android-native-dev`, `ios-application-dev` | Material 3, Apple HIG, Compose / SwiftUI / UIKit |
| **Mobile (cross-platform)** | `flutter-dev`, `react-native-dev` | Riverpod/Bloc, Expo |
| **Specialized dev** | `shader-dev` | GLSL, ray marching, SDFs, ShaderToy |
| **Media generation** | `gif-sticker-maker`, `minimax-multimodal-toolkit` | Image, video, audio, music, TTS, character reference |
| **Music** | `minimax-music-gen`, `minimax-music-playlist`, `buddy-sings` | Songs, instrumentals, personalized playlists, /buddy pet sing |
| **Document deliverables** | `minimax-pdf`, `minimax-docx`, `minimax-xlsx`, `pptx-generator` | Print-ready PDF, OpenXML DOCX, financial XLSX, PptxGenJS |
| **Vision** | `vision-analysis` | Describe, OCR, mockup review, chart extraction |
| **Multimodal toolkit** | `minimax-multimodal-toolkit` | Unified entry for all MiniMax media APIs |

The taxonomy: **by capability surface, not by tool.** A skill covers a *what the model can do for the user*, not a *what API to call*. The user wants a "PDF deliverable" — they don't care if it's ReportLab, WeasyPrint, or wkhtmltopdf. The skill abstracts that.

## The agent engineering principle

**Skills are the unit of capability routing.** When the model needs to produce a PDF, the router looks at available skills, finds `minimax-pdf`, and routes. The model doesn't have to know which Python library to use. The skill is the abstraction.

For Mavis-Apex, this means:
- **Don't embed library choices in the model prompt.** The prompt says "produce a PDF" — the skill says "use `minimax-pdf` with cover style `editorial` and color palette `warm`."
- **Each skill is a deterministic primitive.** The skill knows its tool stack. The model doesn't.
- **Skills are composable.** Producing a PDF + a DOCX + an XLSX from the same research = three skills, no glue code.

## The skill install surface

Skills are installed per harness:
- **Claude Code**: `claude plugin install minimax-skills`
- **Cursor**: `git clone ... && point Cursor at the path`
- **Codex**: `git clone ... && symlink to ~/.agents/skills/`
- **OpenCode**: `git clone ... && symlink to ~/.config/opencode/skills/`

The same source repo feeds all four. The install layer is thin. The pattern is: **one catalog, many harnesses** (same as ECC's cross-harness story).

## The validation discipline

`python .claude/skills/pr-review/scripts/validate_skills.py` — runs the structural checks. A new skill can't merge unless it has:
- A valid frontmatter (name, description, source, category)
- Required sections in `SKILL.md`
- Working example invocations
- Valid wikilinks / URLs
- No secrets in the body

This is the kind of discipline most agent systems skip. Without it, the skill library rots: skills get out of date, links break, names drift. The validation script is the GC.

## The credits and provenance

`CREDITS.md` lists skills derived from open-source work, with attribution. The principle: **give credit where due.** A skill that's a thin wrapper around WeasyPrint should say so. A skill that's a domain-specific recipe should say where the recipe came from.

For Mavis, this maps to `learnings.md` and a future `99 _system/instincts/` — every entry should be attributable. Either a session ID (this came from a real session), a reference (this came from this paper / repo / book), or a reasoning chain (this is a derived insight from these priors). Unattributed learnings are the bottom of the evidence pyramid.

## How Mavis-Apex uses it

The Mavis-Apex skill layer is the operational surface for what Mavis does. The current candidates:

| Skill | Status | Notes |
|---|---|---|
| `vault-brain` | design | The semantic vault search MCP. Documented in [[03 The Custom MCP Arsenal]]. |
| `long-context-curator` | design | The context-budget allocator. |
| `macos-vision-anchor` | design | The persistent visual state. |
| `tool-self-healer` | design | The error recovery layer. |
| `self-model-card` | build (first to ship) | The runtime introspection. |
| `direct-intake` | design | The passive multimodal capture. |
| `intake-markitdown` | design (this monsoon) | The PDF/Office/Image → markdown ingest |
| `intake-scrapling` | design (this monsoon) | The adaptive web scraper |
| `headroom-compress` | design (this monsoon) | The context compression layer |

Each gets its own folder under `99 _system/skills/<name>/` with:
- `SKILL.md` — what it does, when to invoke, I/O contract
- `examples/` — at least 3 invocations (happy path, error path, edge case)
- `validation.md` — how to test the skill is working

The catalog is the single source of truth. When the model needs to do something, the catalog lookup is the first step. (See [[03 The Custom MCP Arsenal#MCP #1: `vault-brain`]] for how the catalog would be indexed.)

## What this is NOT

- **Not a prompt dump.** Skills are executable capabilities, not prompt fragments. A skill that doesn't run is dead code.
- **Not vendor-locked.** The MiniMax skills use the MiniMax API for media generation. Mavis doesn't have to — the skill structure is the contract; the tool stack is interchangeable.
- **Not a substitute for the model.** The model decides *when* to invoke a skill. The skill decides *how* to execute.
- **Not a substitute for instincts.** Skills are deterministic; instincts are learned. A skill implements a workflow; an instinct guides a decision.

## Connections

- [[03 The Custom MCP Arsenal]] — the MCP server design is the runtime for the skill library
- [[04 Direct-Intake MCP]] — the intake layer is a composition of three skills (intake, markitdown, scrapling)
- [[06 Token Economics & Headroom]] — `headroom-compress` is one of the skills
- [[00 Overview]] — the "composition over framework" principle
- [[learnings]] — instincts are the runtime learnings; skills are the codified workflows
- https://github.com/MiniMax-AI/skills — the source

## Anticipated future direction

- **Skill versioning** — each skill gets a `v0.X.Y` and a changelog. Breaking changes bump major. The model can pin a version.
- **Skill chaining** — `intake → markitdown → headroom-compress → vault-brain` is a chain. The catalog knows the chain signatures; the model composes.
- **Skill marketplace** — Andre's vault is private. But the same skill structure could be a public marketplace for verified M3-native skills. (Future thought, not current scope.)

---

*Seeded 2026-06-02 from Operation Omniscience Phase 1. The skill layer is the operational surface of Mavis-Apex; the catalog structure is the discipline.*
