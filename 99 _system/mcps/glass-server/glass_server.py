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

        # Mycelial network page
        if rel_path in ("_glass/mycelial", "mycelial"):
            self._serve_mycelial()
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

    def _serve_mycelial(self):
        """Render the /mycelial page — the living routing network visualization."""
        # Lazy-import MycelialResolver to avoid forcing the dependency
        try:
            import sys as _sys
            resolver_dir = self.vault_root / "99 _system" / "mcps" / "resolver"
            if str(resolver_dir) not in _sys.path:
                _sys.path.insert(0, str(resolver_dir))
            from mycelial import MycelialResolver
            mr = MycelialResolver(self.vault_root)
            state = mr.build_state()
        except Exception as e:
            self.send_error(503, f"MycelialResolver unavailable: {e}")
            return

        template = (_HERE / "templates" / "mycelial.html").read_text(encoding="utf-8")
        page = template
        page = page.replace("{{GENERATED_AT}}", html.escape(state["generated_at"]))
        page = page.replace("{{TOTAL_SKILLS}}", str(state["totals"]["skills"]))
        page = page.replace("{{TOTAL_HOT}}", str(state["totals"]["hot"]))
        page = page.replace("{{TOTAL_COLD}}", str(state["totals"]["cold"]))
        page = page.replace("{{TOTAL_FRESH}}", str(state["totals"]["fresh"]))
        page = page.replace("{{LOG_RECORDS}}", str(state["totals"]["log_records_30d"]))
        page = page.replace(
            "{{RESURRECTION_RULE}}",
            "Cold skills with explicit query matches remain in the candidate set. "
            "The decay is a default, not a hard filter. M3 may still select a cold skill "
            "if the query specifically targets it."
        )
        page = page.replace("{{HOT_SECTION}}", self._format_mycelial_table(state["hottest"], empty_msg="(no hot paths yet — system needs more invocations)"))
        page = page.replace("{{COLD_SECTION}}", self._format_mycelial_table(state["decaying"], empty_msg="(no decaying paths — all skills are active)"))
        page = page.replace("{{FRESH_SECTION}}", self._format_mycelial_table(state["boosted"], empty_msg="(no fresh boosts active)", fresh=True))
        # Routing decisions: top 10 by use count
        routing = [v for v in state["all_vines"] if v["use_count_30d"] > 0]
        routing.sort(key=lambda v: -v["use_count_30d"])
        routing = routing[:10]
        page = page.replace("{{ROUTING_SECTION}}", self._format_routing_table(routing))

        encoded = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    @staticmethod
    def _format_mycelial_table(vines: list, empty_msg: str = "(empty)", fresh: bool = False) -> str:
        """Render a mycelial state table for a list of vines."""
        if not vines:
            return f'<div class="empty-state">{empty_msg}</div>'
        rows = []
        for v in vines:
            confidence = v["final_confidence"]
            if confidence >= 0.7:
                bar_cls = "hot"
            elif confidence >= 0.4:
                bar_cls = "warm"
            else:
                bar_cls = "cold"
            verdict_cls = v["verdict"]
            if fresh:
                verdict_cls = "fresh"
            days_ago = v.get("days_since_used")
            days_ago_str = (
                f"{int(days_ago)}d ago" if days_ago is not None else "—"
            )
            age_str = f"{int(v['age_days'])}d old" if v.get("age_days") else "—"
            flow = v.get("flow_score", 0)
            fresh_score = v.get("fresh_score", 0)
            decay = v.get("decay_penalty", 0)
            rows.append(
                f'<tr>'
                f'<td class="name-col">{html.escape(v["name"])}</td>'
                f'<td><span class="verdict-tag {verdict_cls}">{v["verdict"]}</span></td>'
                f'<td class="num-col">'
                f'<span class="mycelial-bar"><span class="mycelial-bar-fill {bar_cls}" style="width:{int(confidence*100)}%"></span></span>'
                f'{confidence:.2f}'
                f'</td>'
                f'<td class="num-col">{v["use_count_30d"]}</td>'
                f'<td class="num-col">{int(v["success_rate"]*100)}%</td>'
                f'<td>{days_ago_str if not fresh else age_str}</td>'
                f'<td class="num-col" style="color:var(--fg-muted);font-size:0.78rem;">'
                f'flow {flow:+.2f} / fresh {fresh_score:+.2f} / decay {decay:+.2f}'
                f'</td>'
                f'</tr>'
            )
        return (
            '<table class="mycelial-table">'
            '<thead><tr>'
            '<th>Skill</th><th>Verdict</th><th class="num-col">Confidence</th>'
            '<th class="num-col">Use 30d</th><th class="num-col">Success</th>'
            f'<th>{"Last used" if not fresh else "Age"}</th>'
            '<th>Modifiers</th>'
            '</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody>'
            '</table>'
        )

    @staticmethod
    def _format_routing_table(vines: list) -> str:
        """Render the routing decisions table."""
        if not vines:
            return '<div class="empty-state">(no routing decisions in the last 30 days)</div>'
        rows = []
        for v in vines:
            rows.append(
                f'<tr>'
                f'<td class="name-col">{html.escape(v["name"])}</td>'
                f'<td class="num-col">{v["use_count_30d"]}</td>'
                f'<td class="num-col">{int(v["success_rate"]*100)}%</td>'
                f'<td class="num-col">{v["final_confidence"]:.2f}</td>'
                f'<td>{html.escape(v["source"])}</td>'
                f'</tr>'
            )
        return (
            '<table class="mycelial-table">'
            '<thead><tr>'
            '<th>Skill</th><th class="num-col">Selections (30d)</th>'
            '<th class="num-col">Success rate</th><th class="num-col">Confidence</th>'
            '<th>Source</th>'
            '</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody>'
            '</table>'
        )

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
        html_404 = html_404.replace("{{WHOLENESS_BADGE}}", "")
        html_404 = html_404.replace("{{WHOLENESS_SURGERY}}", "")
        html_404 = html_404.replace("{{WHOLENESS_FOOTER}}", "")
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

        # Wholeness badge + surgery panel + footer
        wholeness = data.get("wholeness")
        if wholeness:
            page = page.replace("{{WHOLENESS_BADGE}}", self._format_wholeness_badge(wholeness))
            page = page.replace(
                "{{WHOLENESS_SURGERY}}", self._format_wholeness_surgery(wholeness)
            )
            page = page.replace(
                "{{WHOLENESS_FOOTER}}",
                f' · wholeness {wholeness["total"]}/30 ({wholeness["verdict"]})',
            )
        else:
            page = page.replace("{{WHOLENESS_BADGE}}", "")
            page = page.replace("{{WHOLENESS_SURGERY}}", "")
            page = page.replace("{{WHOLENESS_FOOTER}}", "")

        return page

    @staticmethod
    def _format_wholeness_badge(wholeness: dict) -> str:
        """Format the wholeness score as a colored badge."""
        total = wholeness["total"]
        verdict = wholeness["verdict"]
        # Color class based on verdict
        if verdict == "exemplary":
            cls = "wholeness-badge wholeness-exemplary"
        elif verdict == "alive":
            cls = "wholeness-badge wholeness-alive"
        elif verdict == "working":
            cls = "wholeness-badge wholeness-working"
        else:
            cls = "wholeness-badge wholeness-weak"
        return (
            f'<a class="{cls}" '
            f'href="#wholeness" '
            f'title="Wholeness-Engine score: {total}/30 ({verdict}). Click to view details.">'
            f'Wholeness: {total}/30'
            f'</a>'
        )

    @staticmethod
    def _format_wholeness_surgery(wholeness: dict) -> str:
        """Format the structure surgery panel (if total < 18)."""
        total = wholeness["total"]
        surgery = wholeness.get("surgery", [])
        if total >= 18 or not surgery:
            return ""
        items = "".join(f"<li>{html.escape(s)}</li>" for s in surgery)
        return (
            f'<div class="wholeness-surgery" id="wholeness">'
            f'<div class="wholeness-surgery-header">'
            f'⚠️ Structure Surgery Required '
            f'<span class="wholeness-surgery-score">({total}/30 — below 18 threshold)</span>'
            f'</div>'
            f'<ol class="wholeness-surgery-list">{items}</ol>'
            f'<div class="wholeness-surgery-hint">'
            f'Apply each repair, then re-run <code>mavis-vault wholeness &lt;path&gt;</code> to verify.'
            f'</div>'
            f'</div>'
        )


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
