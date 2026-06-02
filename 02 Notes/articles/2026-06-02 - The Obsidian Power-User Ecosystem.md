---
type: article
created: 2026-06-02
tags: [article, obsidian, vault-rendering, glass-server, mavis-apex, horizon, research]
source: https://quartz.jzhao.xyz/, https://github.com/obsidian-html/obsidian-html, https://github.com/mfarragher/obsidiantools, https://github.com/Pr0dt0s/obsidian-html-server, https://mkdocs-publisher.github.io/, https://www.mkdocs.org/, https://squidfunk.github.io/mkdocs-material/, https://forum.obsidian.md/, https://www.obsibrain.com/blog/top-obsidian-plugins-in-2026-the-essential-list-for-power-users
related: [[Mycelial Routing]], [[Topological Skill Composition (Braiding)]], [[Mavis EA Workflow]], [[MAVIS]]
domains: [obsidian-ecosystem, vault-rendering, knowledge-tools]
---

# 2026-06-02 — The Obsidian Power-User Ecosystem: What Elite Vaults Look Like

> **Operation Obsidian Glass, Phase 1 distillation.** Before building a local server for the Omni-Operator vault, I surveyed the world's most advanced Obsidian power users — Quartz v5, obsidian-html, obsidiantools, MkDocs Publisher, the Html Server plugin, and 700+ community plugins. The findings: the elite stack is **layered, with clear separation of concerns** (authoring in Obsidian, analysis in Python, publishing in Node-based SSGs, presentation in HTML). **The gap:** no thin, on-demand, local Python server for *private vault viewing* with mermaid + wikilinks + frontmatter. That gap is the Glass Server. This article distills what I learned, what I rejected, and what I'm building.

## The current elite stack (what power users actually do in 2025-2026)

The "elite Obsidian vault" today is not one tool. It's a **stack** of tools, each with a single responsibility:

| Layer | Tool | Purpose | Tech |
|---|---|---|---|
| **Authoring** | Obsidian desktop / mobile | Writing, capturing, browsing | Electron (closed source) |
| **Indexing** | Dataview / DataviewJS | Query frontmatter + tags as a database | JS plugin |
| **Diagramming** | Excalidraw / Mermaid / Obsidian Canvas | Visual thinking | Embedded JS plugins |
| **Capture** | QuickAdd / Templater / Obsidian Clipper | Inbox-to-note discipline | JS plugins |
| **Backups** | Obsidian Git | Auto-commit, multi-device sync | JS plugin + Git |
| **Quality** | Linter | Auto-format on save | JS plugin |
| **Analysis** | obsidiantools (Python) | Backlinks, orphan detection, vault metrics | Python package |
| **Publishing** | Quartz v4/v5 (Jacky Zhao) | Public digital garden | Node + TypeScript + Eleventy |
| **Publishing alt** | MkDocs + Material (multiple plugins) | Public docs site | Python + mkdocs-material |
| **Export to HTML** | obsidian-html (krissrex) | Full vault to HTML | Python |
| **Local HTTP serving** | Html Server plugin (Pr0dt0s) | View vault in browser, local network | Obsidian plugin |
| **Database** | Bases (1.10+ native) | Native Obsidian DB view | Built-in |
| **SQL on vault** | DuckDB + MotherDuck plugin | Run SQL on notes, cache results | External DuckDB |

The pattern: **Obsidian is the authoring tool; everything else is a leaf in the ecosystem.** No single tool does it all. Power users compose.

## What I rejected (and why)

| Tool | Why rejected |
|---|---|
| **Quartz v4/v5** | Heavy (Node v22 + Eleventy). Designed for *publishing* to a public digital garden. We need *private viewing* with the same fidelity. Quartz is overkill. |
| **MkDocs + Material** | Excellent for *docs sites* but oriented around a `mkdocs.yml` config. Obsidian's mental model is "vault = folder of MD files," not "config-driven site." Adapting the two requires constant maintenance. |
| **obsidian-html (krissrex)** | Closest analog. Single-shot conversion to HTML. But it's *batch-mode*, not *on-demand*. Recompiling the whole vault to view one note is wasteful. |
| **Lithos (Nuxt + Docus)** | Recent, looks polished. But Nuxt is a heavy JS framework; we're a Python shop. Pulling in a Node-side framework for a thin viewer is the wrong tool. |
| **Html Server plugin (Pr0dt0s)** | This is the *right shape* — view-only HTTP server for vault. But it lives inside Obsidian (you must launch Obsidian first) and is JS-based. We want a standalone Python process that serves the vault directly. |

## The gap (and the Glass Server)

**What doesn't exist yet (as of 2026-06-02):** a *thin, on-demand, local Python server* that:

- Takes a Markdown file path as a URL
- Parses frontmatter (python-frontmatter)
- Renders Markdown to HTML (with extensions: tables, footnotes, codehilite, toc)
- Resolves `[[wikilinks]]` to file paths or external URLs
- Embeds Mermaid.js for client-side diagram rendering
- Embeds Prism.js or highlight.js for syntax highlighting
- Embeds MathJax or KaTeX for math (when needed)
- Embeds a lightweight Dataview-equivalent (render `dataview` and `dataviewjs` code blocks as best-effort; full Dataview emulation is out of scope)
- Serves the result as a styled HTML page
- Renders JSON Canvases (basic; full interactivity is out of scope)
- Has zero external services (CDNs are fine, but no API calls)
- Runs as a single Python file, stdlib only (or near-stdlib)

The Glass Server fills this gap. **Quartz is the digital garden. MkDocs is the docs site. The Glass Server is the private reading room.**

## The naming (why "Glass")

The user named this Operation **Obsidian Glass** — the material obsidian (volcanic glass) is the *natural* metaphor. The vault is the obsidian (the dark, dense, sharp material). The Glass Server is a *cut and polished obsidian* — a smooth, transparent surface that lets you see the vault. It doesn't change the vault; it just makes it visible in a new way. The Esalen posture: **the medium is the message, and the message is the vault itself.**

## The architecture (what I'm building)

```
glass-server/
  glass_server.py      # main HTTP server (stdlib http.server)
  renderer.py          # MD → HTML rendering
  wikilinks.py         # [[link]] resolution
  theme/
    glass.css          # the visual style (typography, color, spacing)
  templates/
    page.html          # base template (Mermaid + Prism + KaTeX via CDN)
  README.md            # how to use
```

**Stack:**
- Python 3 stdlib (no pip dependencies — `http.server` for HTTP, `markdown` library for MD)
- Actually: `python-markdown` for parsing (it's a single-file pure-Python library, installable via `pip install markdown`). The `markdown` library is one of the most ubiquitous Python libs and well-maintained.
- Mermaid.js + Prism.js + KaTeX via CDN (client-side, no Python overhead)
- Custom CSS that matches the obsidian "feel" but is more "presentation"

**Routes:**
- `GET /` → redirect to `/INDEX.md`
- `GET /<path>` → render the markdown file at that path
- `GET /raw/<path>` → return the raw markdown (for debugging)
- `GET /theme/glass.css` → serve the CSS
- `GET /favicon.ico` → 204 (we don't care)

**Render pipeline:**
1. Read file from vault
2. Parse frontmatter (YAML)
3. Render body Markdown to HTML
4. Post-process:
   - Convert `[[wikilinks]]` to `<a href="/path">title</a>` (resolve via wikilinks.py)
   - Identify ` ```mermaid ` code blocks, leave them as `<pre class="mermaid">`
   - Identify ` ```dataview ` blocks, render as `<div class="dataview-placeholder">` (or run a simple in-process implementation)
   - Other code blocks → keep as `<pre><code>` for Prism to highlight
5. Embed result in `page.html` template with frontmatter as `<meta>` tags
6. Return as `text/html`

**Performance target:** < 100ms per file. The vault is ~50MB, the file size is < 1MB usually. Stdlib HTTP + single-pass Python is plenty.

## The CLI toolkit (Phase 3 preview)

The same Python codebase that powers the server also powers the CLI:

```
mavis-vault serve           # start the glass server on port 8765
mavis-vault render <path>    # render a single file to HTML (stdout or file)
mavis-vault audit            # health check (broken wikilinks, missing frontmatter, etc.)
mavis-vault wholeness <path> # score a single note on Alexander's 15 properties
mavis-vault index            # regenerate the vault's INDEX.md
mavis-vault tree             # print the vault tree
mavis-vault search <query>   # full-text grep
```

The CLI is a thin shell around the same Python modules the server uses. The server is a *daemon* that uses the renderer; the CLI is a *one-shot* that uses the renderer. Same code, different interface. This is the Esalen posture: one engine, many surfaces.

## What this is NOT (the discipline)

- **Not a Quartz clone.** Quartz is for publishing. The Glass Server is for *viewing.* No deploy, no HTML export, no `quartz create` ceremony. You point it at your vault and it serves.
- **Not a MkDocs replacement.** MkDocs is for *docs* (config-driven, versioned, public). The Glass Server is for *private* (vault-driven, live, read-only).
- **Not a full Dataview emulator.** Dataview has a rich query language and JS API. The Glass Server handles *simple* Dataview blocks (render as a placeholder with the query text) and *advanced* Dataview (silently no-op). For full Dataview, use Obsidian.
- **Not a Canvas renderer.** JSON Canvases get a "this is a Canvas — open in Obsidian" placeholder. Full Canvas rendering is out of scope.
- **Not a sync engine.** The Glass Server is read-only. No write-back to the vault.
- **Not a security boundary.** It's a local server. Don't expose it to the internet without a reverse proxy + auth.

## What would falsify the whole approach

- **The vault is too small to need a viewer.** A 50-note vault doesn't need a server — Obsidian is enough. The Glass Server's value starts at ~200 notes.
- **The vault is too dynamic to cache or render in real-time.** If notes are written faster than the server can render, the server becomes a bottleneck. Counter: Python `http.server` handles 1k+ req/sec trivially. The bottleneck is rendering, not serving. And the renderer is < 100ms per file.
- **CDN dependence is unacceptable.** If the network is down, the Mermaid/Prism/KaTeX CDN scripts won't load. Counter: ship the JS as local files. The user has them in their vault anyway (e.g., in `99 _system/static/`).
- **The user just wants Quartz.** Counter: this is a separate project. Quartz is heavy. The Glass Server is 200 lines of Python. Different audiences.

## What I'm taking from the elite stack

1. **From Quartz:** the wikilink + transclusion + backlinking concepts (we render the link; we don't compute back-links — that's a separate job for obsidiantools).
2. **From MkDocs Publisher:** the `pub-obsidian` plugin's approach to callouts, frontmatter, and `[[wikilinks]]` resolution.
3. **From obsidian-html:** the template-driven render pipeline and KaTeX support.
4. **From Html Server (Pr0dt0s):** the *view-only* posture and the frontmatter-driven templating. The Pr0dt0s plugin is the closest in spirit, but it lives inside Obsidian and is JS-based.
5. **From obsidiantools:** the Python pattern for parsing frontmatter, traversing wikilinks, identifying orphan notes. We use the *same* mental model (frontmatter is dict, wikilinks are a list per file).

## The 2026 trend: SQL on vaults

The most interesting 2026 development: **DuckDB + MotherDuck plugin** lets you run SQL on your vault from inside a note, caching results as inline markdown tables. This is the first sign of vaults becoming *queryable databases*, not just text collections. The Glass Server won't run SQL (yet), but the architecture is compatible — the renderer can be extended to handle `dataview` SQL blocks by running them through an in-process DuckDB.

## Sources

- [Quartz 5](https://quartz.jzhao.xyz/) — Jacky Zhao, fast batteries-included SSG for Obsidian
- [obsidian-html (obsidian-html/obsidian-html)](https://github.com/obsidian-html/obsidian-html) — Python Obsidian → HTML
- [obsidiantools (mfarragher)](https://github.com/mfarragher/obsidiantools) — Python vault analysis
- [Html Server plugin (Pr0dt0s)](https://github.com/Pr0dt0s/obsidian-html-server) — view-only local HTTP server
- [obsidian-publish-mkdocs (jobindjohn)](https://github.com/jobindjohn/obsidian-publish-mkdocs) — Obsidian + MkDocs template
- [MkDocs Publisher](https://mkdocs-publisher.github.io/) — full-featured Obsidian → MkDocs plugin
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) — the most popular MkDocs theme
- [Top Obsidian Plugins 2026](https://www.obsibrain.com/blog/top-obsidian-plugins-in-2026-the-essential-list-for-power-users) — community-curated plugin list
- [obsidian-stats (plugin stats)](https://www.obsidianstats.com/) — plugin downloads and ratings
- Sam Rambles' [mkdocs-obsidian setup](https://samrambles.com/guides/dotfiles/how-i-setup-this-blog/index.html) — example of full stack with `[[wikilink]]` handling

---

*Seeded 2026-06-02 from Operation Obsidian Glass Phase 1. The elite stack is layered; the Glass Server fills the on-demand local-viewing gap. Building now.*
