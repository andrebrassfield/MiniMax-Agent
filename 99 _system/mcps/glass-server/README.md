# Obsidian Glass

> A thin, local, on-demand HTTP server for viewing your Obsidian vault in a browser. Esalen posture: deterministic, no auth, no DB, no caching, no production hardening. The vault's private reading room, not a publishing platform.

## What it does

- Serves any `.md` file in the vault as styled HTML
- Renders frontmatter, wikilinks, Mermaid diagrams, code blocks (syntax highlighted), callouts, embeds
- Resolves `[[wikilinks]]` to file paths in the vault
- Embeds Mermaid.js via CDN for client-side diagram rendering
- Single-page styled layout with light/dark mode (auto via `prefers-color-scheme`)

## What it does NOT do

- No Dataview execution (renders `dataview` blocks as placeholders showing the query)
- No Canvas rendering (renders JSON canvases as missing-link placeholders, or serves the JSON if requested)
- No write-back to the vault (read-only)
- No auth (don't expose to the internet)
- No caching or pre-rendering (every request is fresh)
- No Dataview SQL, no Templater execution, no other Obsidian plugin emulation

## Quick start

```bash
# 1. Create a venv (one-time)
python3 -m venv 99 _system/mcps/glass-server/.venv
99 _system/mcps/glass-server/.venv/bin/pip install markdown pygments

# 2. Start the server
99 _system/mcps/glass-server/.venv/bin/python 99 _system/mcps/glass-server/glass_server.py --port 8765

# 3. Open in your browser
open http://localhost:8765/
```

## Routes

| URL | Returns |
|---|---|
| `/` | Redirects to `/INDEX.md` |
| `/<path>.md` | Rendered HTML of the markdown file |
| `/<any-file>` | Raw file (e.g., `/README.md` for source, `/some-image.png` for images) |
| `/_glass/theme.css` | The Glass CSS theme |
| `/_glass/raw/<path>` | Raw markdown source (for debugging) |

## CLI

The Glass Server is one half of the `mavis-vault` CLI toolkit. See `03 Projects/Obsidian-Glass/CLI-Toolkit.md` for the full spec.

## Architecture

```
glass-server/
  glass_server.py      # HTTP server (stdlib http.server, threading)
  renderer.py          # MD → HTML rendering pipeline
  wikilinks.py         # [[link]] resolution
  theme/
    glass.css          # The visual style (light + dark via prefers-color-scheme)
  templates/
    page.html          # Base template (Mermaid.js via CDN)
  __pycache__/         # (gitignored)
  .venv/               # (gitignored) — venv with markdown + pygments
  .gitignore
```

The render pipeline:
1. Read file from vault
2. Parse frontmatter (minimal YAML parser; falls back to dict)
3. Extract title, lead quote, metadata
4. Replace `dataview`/`dataviewjs` blocks with placeholders
5. Convert Obsidian callouts (`> [!note]`) to styled divs
6. Resolve `[[wikilinks]]` and `![[embeds]]` via the index
7. Render Markdown to HTML via python-markdown with extensions
8. Embed in `page.html` template with frontmatter as `<details>` metadata

## Why this is "thin"

- ~300 lines of Python in `glass_server.py`
- ~200 lines in `renderer.py`
- ~100 lines in `wikilinks.py`
- One CSS file (~400 lines)
- One HTML template (~30 lines)
- Total: < 1100 lines of code

The `python-markdown` library does the heavy lifting. Mermaid.js is loaded from a CDN. That's the whole stack.

## Why this is "Esalen"

- The medium is the message: the server doesn't add anything, it reveals what's there.
- The vault is the source of truth: nothing is cached, nothing is transformed for export.
- The reader sees the vault, not the tool.
- A polished obsidian surface, viewing through to the other side.

## Configuration

The server takes a few CLI flags:

| Flag | Default | Description |
|---|---|---|
| `--port` | 8765 | Port to listen on |
| `--host` | 127.0.0.1 | Host to bind (local only by default) |
| `--vault` | Parent of glass-server dir | Path to the vault root |

## Limitations (honest)

- **Frontmatter parser is minimal.** It supports `key: value`, `key: [list]`, `key: true/false`, `key: number`, and quoted strings. Anything more complex (nested objects, multiline strings) is silently ignored. For complex frontmatter, swap in `python-frontmatter`.
- **Wikilink resolution is greedy.** The first match wins. If two notes have the same basename in different folders, the top-level one is preferred.
- **Dataview blocks are not executed.** They render as placeholders. Full Dataview emulation is out of scope (use Obsidian).
- **Mermaid requires the CDN to be reachable.** If the network is down, Mermaid diagrams won't render. The Mermaid.js file could be vendored locally for offline use.
- **No HTTPS.** The server is plaintext HTTP on localhost. Don't expose to a network.

## Future work

- [ ] Vendor Mermaid.js + Prism.js + KaTeX locally (no CDN)
- [ ] Add a basic Dataview interpreter for simple `TABLE` and `LIST` queries
- [ ] Add a "search" endpoint that does full-text search across the vault
- [ ] Add per-file caching with ETag (for browser-side caching)
- [ ] Add a vault-tree navigation sidebar
- [ ] Add a backlink panel (requires obsidiantools-style vault index)
- [ ] Support the `mavis-vault` CLI toolkit (Phase 3)

## See also

- `02 Notes/articles/2026-06-02 - The Obsidian Power-User Ecosystem.md` — the research that informed this design
- `03 Projects/Obsidian-Glass/` — the project home
- Quartz 5 — https://quartz.jzhao.xyz/ — for public digital gardens
- obsidian-html — https://github.com/obsidian-html/obsidian-html — for batch HTML export
- obsidiantools — https://github.com/mfarragher/obsidiantools — for Python vault analysis

---

*Seeded 2026-06-02 from Operation Obsidian Glass Phase 2. The vault, polished.*
