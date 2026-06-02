---
type: roadmap
created: 2026-06-02
status: active
tags: [roadmap, obsidian-glass, mavis-apex]
related: [[README]], [[Architecture]], [[CLI-Toolkit]]
domains: [vault-rendering, presentation-layer]
---

# Obsidian Glass — Roadmap

> Where we've been, where we are, where we're going. Bounded, sequential, evidence-driven.

## ✅ Phase 1: Research (2026-06-02)

**Status:** Done. Committed `e9ea79b`.

**Deliverable:** `02 Notes/articles/2026-06-02 - The Obsidian Power-User Ecosystem.md` — a distillation of the 2025-2026 elite Obsidian power-user stack and the gap that the Glass Server fills.

**Key findings:**
- Elite stack is layered: Obsidian + Dataview + obsidiantools + Quartz or MkDocs + Html Server
- No thin, on-demand, local Python server for *private vault viewing* with Mermaid + wikilinks + frontmatter
- Quartz is for *publishing* (digital garden), MkDocs is for *docs* (config-driven) — Glass is for *viewing* (private)

## ✅ Phase 2: Glass Server Prototype (2026-06-02)

**Status:** Done. Committed `c2ca7b2`.

**Deliverable:** `99 _system/mcps/glass-server/` — 9 files, 1421 insertions.

**What's in it:**
- `glass_server.py` (276 lines) — ThreadingHTTPServer with vault routing
- `renderer.py` (286 lines) — MD → HTML pipeline with frontmatter + dataview + callouts
- `wikilinks.py` (142 lines) — `[[link]]` and `![[embed]]` resolution
- `theme/glass.css` (424 lines) — light + dark visual style
- `templates/page.html` (~30 lines) — base template with Mermaid.js CDN
- `test_render.py` (101 lines) — local render harness
- `README.md` — design rationale
- `__init__.py` — package marker
- `.gitignore` — excludes .venv/, __pycache__/

**Performance verified:**
- GET / → 200, 15KB, 282ms cold
- GET /path/to/note.md → 200, 12KB, 7.8ms warm
- GET /_glass/theme.css → 200, 9.5KB, 1.4ms
- GET /nonexistent → 404 with suggestions, 1.7KB
- 381 vault files indexed for wikilinks

**Limitations (honest):**
- Minimal YAML frontmatter parser (handles 95% of cases)
- Mermaid.js loaded from CDN (offline mode is Phase 5)
- Dataview blocks render as placeholders, not executed (Phase 4)
- No back-link panel, no full-text search, no hot-reload (Phase 7+)

## 🔄 Phase 3: CLI Toolkit (in progress)

**Status:** Specs written. Working `mavis-vault` script to be built.

**Deliverable:** `99 _system/cli/mavis-vault` (shell wrapper) + `mavis_vault.py` (Python implementation) + this folder's specs.

**Subcommands planned:**
- `serve` — start the Glass Server
- `render <path>` — render a single file to HTML
- `audit` — vault health check
- `wholeness <path>` — 15-property score for a single note
- `wholeness-report` — run the rubric across all atomic notes
- `search <query>` — full-text search
- `index` — regenerate INDEX.md
- `tree` — print the vault tree
- `stats` — vault statistics

**Effort:** 1-2 days of writing + 1 day of testing.

## ⏳ Phase 4: Dataview Cache (future)

**When:** After Phase 3 ships. Likely weeks away.

**What:** Use in-process DuckDB to *execute* simple Dataview queries (TABLE, LIST) and cache the results in the rendered HTML.

**Why:** Currently, dataview blocks are placeholders. To make the Glass Server a true *viewing* surface, dataview needs to actually render. DuckDB is the right primitive (in-process, fast, SQL).

**Effort:** 1-2 weeks.

## ⏳ Phase 5: Vendored JS (future)

**When:** Whenever offline use matters.

**What:** Vendor Mermaid.js, Prism.js, KaTeX into the vault (e.g., `99 _system/static/`). Remove the CDN dependency.

**Why:** The user said "local, fast, and beautiful." CDN is the only external dep. Vendoring is the final step toward "truly local."

**Effort:** 1 day (download + reference).

## ⏳ Phase 6: Sidebar / Vault Tree (future)

**When:** After the basic viewing is comfortable.

**What:** Add a left rail with the vault's folder structure, current note's inbound links, and current note's outbound links.

**Why:** URL-based navigation is functional but not delightful. A sidebar makes the vault browsable.

**Effort:** 1-2 days.

## ⏳ Phase 7: Backlink Panel (future)

**When:** After sidebar ships.

**What:** Compute backlinks (using the same wikilink index) and display them in a right rail.

**Why:** Obsidian's backlinks are a defining feature. The Glass Server should match.

**Effort:** 1-2 days.

## ⏳ Phase 8: Search Endpoint (future)

**When:** When the vault is too big to navigate by structure.

**What:** Add `/search?q=...` endpoint to the Glass Server, plus `mavis-vault search` CLI subcommand.

**Why:** Grep is fine for small vaults; for 1000+ notes, full-text search with context is necessary.

**Effort:** 1-2 days (use Python stdlib indexing or a simple Whoosh integration).

## ⏳ Phase 9: Hot-reload (future)

**When:** When the user is editing in Obsidian and wants the Glass view to update.

**What:** Watch the vault for changes, regenerate the index, push updates to the browser (Server-Sent Events or websocket).

**Why:** Live-viewing. Currently, you have to refresh the browser.

**Effort:** 2-3 days.

## ⏳ Phase 10: ETag Caching (future)

**When:** When render performance becomes a bottleneck.

**What:** Cache rendered HTML with an ETag based on file mtime. Browser sends `If-None-Match`, server returns 304.

**Why:** The renderer is already fast (~8ms warm). ETag caching is mostly a network optimization.

**Effort:** Half a day.

## How this ties to the EA's role

The EA's job is to *see* the vault, *act* on the vault, and *report* on the vault. Obsidian handles *see* (in the editor) and *act* (write). The Glass Server handles *see* (in the reading room) and *report* (the CLI's `audit` / `stats` / `wholeness-report`).

The gap is *act* at the meta level — naming new connections, surfacing patterns, building new notes. That's the EA's reasoning layer (me, Mavis), not the presentation layer (Glass).

The Glass is the **viewing surface for the EA's reasoning.** When the EA writes a connection note, the Glass renders it. When the EA scans the vault for wholeness, the CLI's `wholeness-report` shows the score. When the EA wants to present an architecture, the Glass shows it in the browser.

This is the *separation of concerns* the Esalen posture demands: the vault is data, Obsidian is the editor, Mavis is the thinker, Glass is the surface.

## See also

- `README.md` — project home
- `Architecture.md` — design notes
- `CLI-Toolkit.md` — the CLI spec
- `2026-W23 - Operation-Horizon-Synthesis.md` — the Horizon pitches this serves
- `Mavis-Apex-Architecture` — the broader stack

---

*Roadmap for Operation Obsidian Glass. Bounded, sequential, evidence-driven. The vault, polished.*
