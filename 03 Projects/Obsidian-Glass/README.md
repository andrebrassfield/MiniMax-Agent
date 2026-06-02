---
type: project
created: 2026-06-02
status: active
tags: [project, obsidian-glass, vault-renderer, presentation-layer, mavis-apex, mavis-infrastructure]
related: [[2026-W23 - Operation-Horizon-Synthesis]], [[Mavis-Apex-Architecture]], [[Esalen, Not Foxconn]]
domains: [vault-rendering, presentation-layer, knowledge-tools]
---

# Obsidian Glass — Project

> **The vault, polished.** A thin, local, on-demand presentation layer for the Omni-Operator vault. Renders any Markdown file as styled HTML in the browser. Esalen posture: deterministic, no auth, no DB, no caching, no production hardening. The *private reading room*, not a publishing platform.

## What this is

Three deliverables, in three phases:

1. **Phase 1: Research** — done. Survey of the 2025-2026 elite Obsidian power-user stack (Quartz v5, obsidian-html, obsidiantools, MkDocs Publisher, Html Server plugin, 700+ community plugins). Result: a *layered* stack with authoring in Obsidian, analysis in Python, publishing in Node-based SSGs, presentation in HTML. **The gap:** no thin, on-demand, local Python server for *private vault viewing* with Mermaid + wikilinks + frontmatter. Glass Server fills the gap.

2. **Phase 2: Glass Server** — done. A stdlib-Python HTTP server (`99 _system/mcps/glass-server/`) that renders any vault file as styled HTML on demand. ~1100 lines total. End-to-end verified: `/` 282ms cold, file renders 7.8ms warm.

3. **Phase 3: CLI Toolkit** — in progress. A `mavis-vault` shell command that wraps the same renderer module for one-shot operations: serve, render, audit, wholeness, search, index.

## What this is NOT

- Not Quartz (which is for *publishing* to a public digital garden).
- Not MkDocs (which is for *config-driven docs* sites).
- Not obsidian-html (which is *batch-mode* HTML export, not on-demand).
- Not a sync engine, not a write-back to the vault, not a security boundary.

## Architecture (current state)

```
99 _system/mcps/glass-server/
  glass_server.py        # HTTP server (ThreadingHTTPServer)
  renderer.py            # MD → HTML rendering pipeline
  wikilinks.py           # [[link]] and ![[embed]] resolution
  theme/glass.css        # The visual style (light + dark)
  templates/page.html    # Base template with Mermaid.js CDN
  test_render.py         # Local render harness
  __init__.py
  README.md
  .gitignore             # Excludes .venv/, __pycache__/

99 _system/cli/
  mavis-vault            # Shell entry
  mavis_vault.py         # Python implementation (CLI toolkit)
```

See `Architecture.md` for the full design notes, and `CLI-Toolkit.md` for the CLI spec.

## Roadmap

| Phase | Status | Deliverable |
|---|---|---|
| Phase 1: Research | ✅ Done | `02 Notes/articles/2026-06-02 - The Obsidian Power-User Ecosystem.md` |
| Phase 2: Glass Server | ✅ Done | `99 _system/mcps/glass-server/` (9 files, 1421 insertions) |
| Phase 3: CLI Toolkit | 🔄 In progress | `99 _system/cli/mavis-vault` + specs in this folder |
| Phase 4 (future): Dataview emulator | ⏳ Pending | Optional — render `dataview` blocks via in-process DuckDB |
| Phase 5 (future): Vendored JS | ⏳ Pending | Local Mermaid.js + Prism.js + KaTeX (no CDN) |
| Phase 6 (future): Sidebar / nav | ⏳ Pending | Vault tree in the left rail |
| Phase 7 (future): Backlink panel | ⏳ Pending | Uses obsidiantools-style vault index |

## Tying into the Horizon pitches

The Glass Server is the *delivery vehicle* for the Horizon pitches:

- **PatternForge** (Pitch 3) — workflow generative codes are best viewed in Glass, not in raw Obsidian
- **Wholeness-Engine** (Pitch 2) — the CLI's `wholeness` subcommand runs the 15-property rubric and the Glass Server displays the score
- **MycelialResolver** (Pitch 1) — the CLI's `audit` subcommand surfaces the routing data, the Glass Server visualizes it

In other words: **the Glass Server is how the Omni-Operator sees itself.** The vault is the source of truth. The Glass is the surface through which the EA reads the vault.

## See also

- `02 Notes/articles/2026-06-02 - The Obsidian Power-User Ecosystem.md`
- `99 _system/mcps/glass-server/README.md`
- `Mavis-Apex-Architecture` — the existing stack this fits into
- `Esalen, Not Foxconn` — the operating posture

---

*Project home for Operation Obsidian Glass. Andre's directive: thin, deterministic, local, beautiful. The vault, polished.*
