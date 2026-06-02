"""
Renderer for the Obsidian Glass Server.

Takes raw Markdown, parses frontmatter, resolves wikilinks, and produces
HTML ready for embedding in the page template.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension

from wikilinks import WikilinkResolver

# Match mermaid fenced code blocks so we can wrap them for client-side rendering
MERMAID_FENCE_RE = re.compile(
    r"^```mermaid\s*\n(.*?)\n```\s*$", re.MULTILINE | re.DOTALL
)

# Frontmatter regex (YAML between --- lines)
FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter. Returns (frontmatter_dict, body)."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    fm_text = match.group(1)
    body = text[match.end():]

    # Minimal YAML parser — supports key: value, key: [a, b, c], key: {a: b}
    # For anything complex, fall back to empty dict (we use the body as truth)
    fm = {}
    for line in fm_text.split("\n"):
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        # Parse simple lists
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if inner:
                fm[key] = [
                    item.strip().strip('"').strip("'")
                    for item in inner.split(",")
                ]
            else:
                fm[key] = []
        # Parse booleans
        elif value.lower() in ("true", "false"):
            fm[key] = value.lower() == "true"
        # Parse numbers
        elif value.isdigit():
            fm[key] = int(value)
        else:
            fm[key] = value
    return fm, body


def extract_title(fm: dict, body: str, fallback: str) -> str:
    """Extract the title from frontmatter or first H1."""
    if "title" in fm:
        return str(fm["title"])
    # Look for first H1 in the body
    h1_match = re.search(r"^#\s+(.+?)$", body, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()
    return fallback


def extract_lead_quote(body: str) -> Optional[str]:
    """Extract the lead blockquote (>) from the start of the body."""
    lines = body.split("\n")
    quote_lines = []
    started = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(">"):
            # Strip the > and any leading space
            content = stripped[1:].lstrip()
            quote_lines.append(content)
            started = True
        elif started and not stripped:
            # Empty line ends the quote
            break
        elif started:
            # Non-quote content ends the quote
            break
    if quote_lines:
        return " ".join(quote_lines)
    return None


def extract_metadata_table(fm: dict) -> str:
    """Render a small metadata table from frontmatter."""
    if not fm:
        return ""
    rows = []
    for key, value in fm.items():
        # Skip very long values to keep the table compact
        if isinstance(value, str) and len(value) > 200:
            value = value[:200] + "..."
        rows.append(
            f"<tr><th>{key}</th><td>{_format_value(value)}</td></tr>"
        )
    return (
        '<details class="metadata-panel">\n'
        "<summary>Metadata</summary>\n"
        '<table class="metadata-table">\n'
        + "\n".join(rows)
        + "\n</table>\n"
        "</details>\n"
    )


def _format_value(value) -> str:
    """Format a frontmatter value for the metadata table."""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def extract_dataview_blocks(body: str) -> tuple[str, list[str]]:
    """Find dataview code blocks and return (body_with_placeholders, query_texts).

    The Glass Server does not execute dataview queries — it renders a
    placeholder showing the query text, so the user can see the intent.
    """
    queries = []
    pattern = re.compile(
        r"```(?:dataview|dataviewjs)\s*\n(.*?)\n```", re.DOTALL
    )

    def replacer(match: re.Match) -> str:
        query_text = match.group(1).strip()
        queries.append(query_text)
        return (
            '<div class="dataview-placeholder">\n'
            '<div class="dataview-label">Dataview query (rendered in Obsidian):</div>\n'
            f'<pre><code class="language-dataview">{query_text}</code></pre>\n'
            "</div>"
        )

    new_body = pattern.sub(replacer, body)
    return new_body, queries


def extract_callouts(body: str) -> str:
    """Convert Obsidian-style callouts (!> [!note] Title) to styled blocks.

    Obsidian callout syntax:
        > [!note] Optional title
        > Body line

    This is a simplified implementation. TODO: handle nested callouts,
    multi-paragraph bodies, and callouts with explicit icon.
    """
    # Simple line-by-line approach — match consecutive > lines starting with [!type]
    lines = body.split("\n")
    out = []
    i = 0
    callout_open_re = re.compile(r"^>\s*\[!(\w+)\](?:\s+([^\n]*))?$")
    while i < len(lines):
        line = lines[i]
        m = callout_open_re.match(line)
        if m:
            callout_type = m.group(1).lower()
            title = m.group(2) or callout_type.capitalize()
            # Collect subsequent > lines
            body_lines = []
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if next_line.startswith(">"):
                    stripped = next_line.lstrip(">").lstrip()
                    if stripped:
                        body_lines.append(stripped)
                    j += 1
                elif next_line.strip() == "":
                    # Allow empty lines inside callouts
                    body_lines.append("")
                    j += 1
                else:
                    break
            # Trim trailing empty lines
            while body_lines and body_lines[-1] == "":
                body_lines.pop()
            inner = "<br>".join(body_lines) if body_lines else ""
            out.append(
                f'<div class="callout callout-{callout_type}">'
                f'<div class="callout-title">{title}</div>'
                f'<div class="callout-body">{inner}</div>'
                f'</div>'
            )
            i = j
        else:
            out.append(line)
            i += 1
    return "\n".join(out)


class MarkdownRenderer:
    """Renders Obsidian-flavored Markdown to HTML."""

    def __init__(self, vault_root: Path):
        self.vault_root = vault_root.resolve()
        self.wikilink_resolver = WikilinkResolver(vault_root)
        # The markdown parser is reused across requests
        self.md_parser = markdown.Markdown(
            extensions=[
                "extra",       # tables, footnotes, fenced code, etc.
                "sane_lists",
                "smarty",
                "meta",
                CodeHiliteExtension(css_class="codehilite", guess_lang=False),
                TocExtension(toc_depth="2-3"),
            ],
            output_format="html5",
        )

    def _format_mermaid(self, source: str, language: str, css_class: str, **options) -> str:
        """Format a mermaid code block — just wrap in a div for client-side rendering."""
        return f'<pre class="mermaid">{source}</pre>'

    def render_file(self, file_path: Path) -> dict:
        """Render a single vault file to HTML-ready data.

        Returns a dict with keys:
          - title: str
          - lead_quote: Optional[str]
          - body_html: str
          - metadata_html: str
          - frontmatter: dict
          - rel_path: str (path relative to vault root)
          - mtime: datetime
          - dataview_count: int
        """
        rel_path = file_path.relative_to(self.vault_root)
        text = file_path.read_text(encoding="utf-8", errors="replace")
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

        fm, body = parse_frontmatter(text)
        title = extract_title(fm, body, fallback=rel_path.stem)
        lead = extract_lead_quote(body)

        # Process in order:
        # 1. Extract dataview blocks (becomes placeholders)
        body, dataview_count = extract_dataview_blocks(body)
        # 2. Convert callouts to styled divs
        body = extract_callouts(body)
        # 3. Resolve wikilinks
        body = self.wikilink_resolver.process_markdown(body)
        # 4. Render to HTML
        # Reset the parser for each file (it has internal state)
        self.md_parser.reset()
        body_html = self.md_parser.convert(body)

        metadata_html = extract_metadata_table(fm)

        return {
            "title": title,
            "lead_quote": lead,
            "body_html": body_html,
            "metadata_html": metadata_html,
            "frontmatter": fm,
            "rel_path": str(rel_path),
            "mtime": mtime,
            "dataview_count": dataview_count,
        }
