---
type: architecture
created: 2026-06-02
status: design
tags: [architecture, obsidian-glass, design-notes, mavis-apex]
related: [[README]], [[CLI-Toolkit]]
domains: [vault-rendering, presentation-layer]
---

# Obsidian Glass — Architecture Notes

> Design rationale, decisions, and tradeoffs for the Glass Server + CLI toolkit. The *why* behind the *what*.

## The core decision: separate presentation from authoring

Obsidian is an *authoring* tool. Its UI is designed for writing, browsing, and capturing — not for *presenting* the vault to an outside reader. The Glass Server is the inverse: it has no editing surface, no file picker, no command palette. It takes a URL, fetches the file, renders it, and returns HTML. **The separation of concerns is the architecture.**

This means:
- The vault is the source of truth. The Glass never modifies the vault.
- Obsidian is the editor. The Glass is the reader.
- Both look at the same files (markdown, frontmatter, wikilinks) but interpret them differently.
- The Glass is *Esalen* (thin layer, no opinions about content). The vault's structure is preserved exactly.

## The 3 layers

### Layer 1: The Renderer (`renderer.py`)

A pure-Python module. Given a vault root and a file path, it returns a `dict` with:
- `title`: extracted from frontmatter or first H1
- `lead_quote`: the opening blockquote, if any
- `body_html`: the rendered HTML
- `metadata_html`: a `<details>` panel with the frontmatter
- `frontmatter`: the raw dict
- `rel_path`: path relative to vault root
- `mtime`: file modification time
- `dataview_count`: list of dataview query strings (for placeholders)

The renderer has no I/O beyond reading the file. It is *pure* — no network, no cache, no state. You can render 10,000 files in a tight loop and the only side effect is the filesystem reads.

### Layer 2: The Wikilink Resolver (`wikilinks.py`)

Builds an index of all `.md` files in the vault at startup. Resolves `[[link]]` to file paths, `![[embed]]` to images or transclusion placeholders.

The index is built by walking `vault_root.rglob("*.md")` and keying by:
1. Relative path without `.md` extension (case-insensitive)
2. Just the basename (so `[[My Note]]` resolves to `02 Notes/ideas/My Note.md` if there's no top-level match)

This is fast (1k files index in < 1s) and simple. The tradeoff: a small amount of duplication (the same file may be reachable via two keys). The resolver prefers the top-level match.

### Layer 3: The Server (`glass_server.py`)

A `ThreadingHTTPServer` (stdlib) with one handler class. The handler:
1. Parses the URL path
2. Resolves the file (with path-traversal protection)
3. Renders if `.md`, serves as-is otherwise
4. Returns 404 with suggestions if missing

The server has no global state beyond the renderer (which holds the wikilink index). Restart = fresh index. That's the Esalen posture.

## Why stdlib HTTP and not Flask/FastAPI

The user said "thin, deterministic, no over-engineering." `ThreadingHTTPServer` is:
- Zero dependencies (just Python)
- Threading model out of the box (one thread per request)
- Stable, well-tested, no security CVEs
- Easy to read in 50 lines

Flask and FastAPI are great for production apps with routing, middleware, sessions, etc. We don't have any of that. A 250-line server with stdlib is the right size for the problem.

## Why Mermaid.js via CDN (not local)

The user said "local, fast, and beautiful." CDN is *not* local. But:
- Mermaid.js is ~3MB minified. Vendoring it adds 3MB to the repo.
- The CDN (jsdelivr) is fast and reliable.
- For an offline-mode feature, vendoring is on the roadmap (Phase 5).

The trade-off is acceptable for the prototype. The CDN is a single external dependency; if it's down, Mermaid blocks render as `<pre class="mermaid">` text (still legible, just not pretty).

## Why python-markdown (not mistune, not commonmark, not pandoc)

| Library | Why rejected |
|---|---|
| `mistune` | Fast, but extension ecosystem is small. No codehilite, no TOC. |
| `commonmark` (or `cmarkgfm`) | Strict CommonMark; doesn't natively support Obsidian-style extensions. |
| `pandoc` | Excellent, but a separate binary (1GB+), not pure Python. Overkill. |
| `python-markdown` | **Chosen.** Pure Python, ubiquitous, extensible. Built-in extensions: extra, codehilite, toc, meta. Battle-tested. |

## Why minimal YAML parser (not `python-frontmatter`)

`python-frontmatter` is a great library, but it adds another dep. The minimal YAML parser in `renderer.py` handles:
- `key: value` (string, number, boolean)
- `key: [list, of, items]`
- Quoted strings (`"..."` or `'...'`)

That's enough for ~95% of the vault's frontmatter. For complex YAML (nested objects, multiline strings), the parser falls back to the body as truth. This is the Esalen posture: handle the common case, fail gracefully on the rare case.

## The Dataview decision (placeholder, not emulator)

`dataview` is a query language; full emulation is a 1000+ line project. The Glass Server's choice: **render dataview blocks as placeholders showing the query text.** This:
- Tells the user "this would render in Obsidian" (honest)
- Doesn't pretend to evaluate the query (no false positives)
- Is small (~10 lines of code)
- Is the right shape for the v0.1

If the user wants to *see* the result, they open in Obsidian. If the user wants to *commit* the result, they use the `mavis-vault dataview-cache` subcommand (Phase 4 roadmap, would use in-process DuckDB).

## The security posture

The Glass Server is **localhost only by default** (`--host 127.0.0.1`). It does:
- Path-traversal protection (`_resolve_safe` ensures resolved paths stay inside vault_root)
- Prefix blocking (`.git`, `.obsidian`, etc.)
- No write operations

It does NOT do:
- HTTPS (the user is on localhost; if exposing, use a reverse proxy)
- Auth (same)
- Rate limiting (single-user)
- CSRF protection (no forms)

This is a *viewing tool*, not a public service. Don't expose to the internet.

## What I'd add in Phase 4+

| Phase | Feature | Why |
|---|---|---|
| 4 | Dataview cache (DuckDB) | Render cached results instead of placeholders |
| 5 | Vendored Mermaid.js + Prism.js + KaTeX | Offline mode, no CDN |
| 6 | Vault-tree sidebar | Better navigation than URL paths |
| 7 | Backlink panel | Show what links to this note |
| 8 | Search endpoint (full-text) | Find notes by content |
| 9 | Hot-reload | Watch vault for changes, regenerate |
| 10 | Per-file ETag caching | Avoid re-rendering unchanged files |

Each is a bounded addition. The Esalen posture is *add one thing at a time, in response to actual need, not speculation.*

## See also

- `CLI-Toolkit.md` — the CLI spec
- `99 _system/mcps/glass-server/README.md` — the prototype README
- `2026-W23 - Operation-Horizon-Synthesis.md` — the meta-pattern
- `Esalen, Not Foxconn` — the operating posture

---

*Architecture notes for Operation Obsidian Glass. The vault, polished — by the same design discipline as the vault itself.*
