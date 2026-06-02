"""
The Obsidian Glass Server.

A thin, local, on-demand HTTP server that renders vault Markdown files
as styled HTML. Esalen posture: deterministic, no auth, no DB, no caching,
no production hardening. Local viewing room, not a production server.

Usage:
    python glass_server.py [--port 8765] [--vault /path/to/vault]

Then open http://localhost:8765/ in your browser.
"""

import argparse
import html
import json
import mimetypes
import re
import sys
import urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Allow `import renderer` / `import wikilinks` when invoked as a script
_HERE = Path(__file__).parent.resolve()
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from renderer import MarkdownRenderer

# Default vault root: parent of the mcp dir (the vault itself)
DEFAULT_VAULT = _HERE.parent.parent.parent
DEFAULT_PORT = 8765

# Path patterns to ignore when serving (matches the user's vault conventions)
IGNORED_PATH_PREFIXES = (
    ".git",
    ".obsidian",
    ".smart-env",
    ".claude",
    ".claudian",
    "99 _system/intake-log",
    "node_modules",
)


class GlassHandler(BaseHTTPRequestHandler):
    """HTTP handler for the Glass Server."""

    # The renderer is set by the server factory below
    renderer: MarkdownRenderer = None  # type: ignore
    vault_root: Path = None  # type: ignore
    template: str = ""  # filled at server start

    def log_message(self, format, *args):
        """Quieter logging — prepend [glass] to stderr lines."""
        sys.stderr.write(f"[glass] {self.address_string()} - {format % args}\n")

    def do_GET(self):
        try:
            self._handle_get()
        except Exception as e:
            sys.stderr.write(f"[glass] ERROR: {e}\n")
            self.send_error(500, f"Internal error: {e}")

    def _handle_get(self):
        # Parse URL
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        # Strip leading slash
        if path == "/" or path == "":
            path = "/INDEX.md"
        rel_path = path.lstrip("/")

        # Check ignored prefixes
        for prefix in IGNORED_PATH_PREFIXES:
            if rel_path.startswith(prefix):
                self.send_error(403, f"Path starts with ignored prefix: {prefix}")
                return

        # Theme / template routes
        if rel_path == "_glass/theme.css":
            self._serve_file(_HERE / "theme" / "glass.css", "text/css")
            return

        # Raw markdown (for debugging)
        if rel_path.startswith("_glass/raw/"):
            raw_path = rel_path[len("_glass/raw/"):]
            file_path = self._resolve_safe(raw_path)
            if file_path and file_path.is_file():
                self._serve_file(file_path, "text/markdown; charset=utf-8")
                return
            self.send_error(404, f"Not found: {raw_path}")
            return

        # Resolve the file path
        file_path = self._resolve_safe(rel_path)
        if not file_path or not file_path.is_file():
            self._send_404(rel_path)
            return

        # If it's a non-markdown file, serve as-is
        if file_path.suffix.lower() != ".md":
            mime, _ = mimetypes.guess_type(str(file_path))
            self._serve_file(file_path, mime or "application/octet-stream")
            return

        # Render markdown
        try:
            data = self.renderer.render_file(file_path)
        except Exception as e:
            self.send_error(500, f"Render error: {e}")
            return

        # Embed in the page template
        page_html = self._render_page(data)
        encoded = page_html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _resolve_safe(self, rel_path: str) -> Path | None:
        """Resolve a path relative to vault root, ensuring it stays inside.

        Returns None if the path would escape the vault.
        """
        # URL-decode
        rel_path = urllib.parse.unquote(rel_path)
        # Strip any leading slashes
        rel_path = rel_path.lstrip("/")
        # Resolve
        candidate = (self.vault_root / rel_path).resolve()
        # Ensure it's inside the vault
        try:
            candidate.relative_to(self.vault_root)
        except ValueError:
            return None
        return candidate

    def _serve_file(self, file_path: Path, content_type: str):
        try:
            data = file_path.read_bytes()
        except OSError as e:
            self.send_error(500, f"Read error: {e}")
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_404(self, rel_path: str):
        # Render a nice 404 with suggestions
        html_404 = self.template.replace("{{TITLE}}", "404 — Not Found")
        html_404 = html_404.replace("{{LEAD_QUOTE}}", "")
        html_404 = html_404.replace("{{BODY_HTML}}", _render_404_body(rel_path, self.vault_root))
        html_404 = html_404.replace("{{METADATA_HTML}}", "")
        html_404 = html_404.replace("{{REL_PATH}}", rel_path)
        html_404 = html_404.replace("{{MTIME}}", datetime.now().isoformat(timespec="seconds"))
        html_404 = html_404.replace("{{DATAVIEW_COUNT}}", "0")
        encoded = html_404.encode("utf-8")
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _render_page(self, data: dict) -> str:
        page = self.template
        page = page.replace("{{TITLE}}", html.escape(data["title"]))
        page = page.replace(
            "{{LEAD_QUOTE}}",
            f'<blockquote class="lead-quote">{html.escape(data["lead_quote"])}</blockquote>'
            if data["lead_quote"] else "",
        )
        page = page.replace("{{BODY_HTML}}", data["body_html"])
        page = page.replace("{{METADATA_HTML}}", data["metadata_html"])
        page = page.replace("{{REL_PATH}}", html.escape(data["rel_path"]))
        page = page.replace(
            "{{MTIME}}", data["mtime"].isoformat(timespec="seconds")
        )
        page = page.replace("{{DATAVIEW_COUNT}}", str(len(data["dataview_count"])))
        return page


def _render_404_body(rel_path: str, vault_root: Path) -> str:
    """Render the body of a 404 page with vault suggestions."""
    # Find a few similar files
    target = Path(rel_path).stem.lower()
    suggestions = []
    for md in vault_root.rglob("*.md"):
        if target in md.stem.lower():
            suggestions.append(md.relative_to(vault_root))
            if len(suggestions) >= 5:
                break

    items = "".join(
        f'<li><a href="/{html.escape(str(s))}">{html.escape(str(s))}</a></li>'
        for s in suggestions
    )

    return f"""
<h1>404 — Not Found</h1>
<p>The file <code>{html.escape(rel_path)}</code> does not exist in the vault.</p>
{"<h2>Did you mean?</h2><ul>" + items + "</ul>" if items else ""}
<p><a href="/">← Back to INDEX</a></p>
"""


def load_template() -> str:
    """Load the page.html template."""
    template_path = _HERE / "templates" / "page.html"
    return template_path.read_text(encoding="utf-8")


def make_handler(renderer: MarkdownRenderer, vault_root: Path, template: str):
    """Create a handler class bound to the given renderer and template."""

    class BoundHandler(GlassHandler):
        pass

    BoundHandler.renderer = renderer
    BoundHandler.vault_root = vault_root
    BoundHandler.template = template
    return BoundHandler


def main():
    parser = argparse.ArgumentParser(
        description="Obsidian Glass Server — view your vault in a browser",
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"Port to listen on (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--vault", type=Path, default=DEFAULT_VAULT,
        help=f"Path to the vault root (default: {DEFAULT_VAULT})",
    )
    parser.add_argument(
        "--host", default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1 — local only)",
    )
    args = parser.parse_args()

    vault_root = args.vault.resolve()
    if not vault_root.is_dir():
        sys.stderr.write(f"[glass] Vault not found: {vault_root}\n")
        sys.exit(1)

    sys.stderr.write(f"[glass] Vault: {vault_root}\n")
    sys.stderr.write(f"[glass] Indexing wikilinks...\n")
    renderer = MarkdownRenderer(vault_root)
    sys.stderr.write(f"[glass] Indexed {len(renderer.wikilink_resolver._index)} vault files\n")

    template = load_template()
    handler = make_handler(renderer, vault_root, template)

    server = ThreadingHTTPServer((args.host, args.port), handler)
    sys.stderr.write(f"[glass] Serving on http://{args.host}:{args.port}/\n")
    sys.stderr.write(f"[glass] Open http://localhost:{args.port}/ in your browser.\n")
    sys.stderr.write(f"[glass] Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write(f"\n[glass] Shutting down.\n")
        server.shutdown()


if __name__ == "__main__":
    main()
