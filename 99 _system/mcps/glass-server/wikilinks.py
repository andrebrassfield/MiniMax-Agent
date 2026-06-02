"""
Wikilink resolution for the Obsidian Glass Server.

Handles Obsidian's [[link]] and [[link|display text]] syntax.
Resolves links to vault file paths, generating HTML anchor tags.
"""

import re
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import quote

# Match [[target]] or [[target|display text]]
# Target can contain nested paths, spaces, and some special chars
WIKILINK_RE = re.compile(r"\[\[([^\[\]\n]+?)\]\]")

# Match markdown image embeds: ![[image.png]] or ![[image.png|alt]]
EMBED_RE = re.compile(r"!\[\[([^\[\]\n]+?)\]\]")


class WikilinkResolver:
    """Resolves Obsidian-style wikilinks to vault file paths."""

    def __init__(self, vault_root: Path):
        self.vault_root = vault_root.resolve()
        # Build an index of all .md files in the vault for fast lookup
        self._index: dict[str, Path] = {}
        for md_file in self.vault_root.rglob("*.md"):
            # Key by relative path without .md extension
            rel = md_file.relative_to(self.vault_root)
            key = str(rel.with_suffix("")).lower()
            self._index[key] = md_file
            # Also key by just the basename
            basename = md_file.stem.lower()
            # Don't overwrite if already set; prefer the top-level one
            if basename not in self._index:
                self._index[basename] = md_file

    def resolve(self, target: str) -> Optional[Path]:
        """Resolve a wikilink target to a vault file path, or None if not found."""
        target = target.strip()

        # Handle anchors (#heading) — strip for path resolution
        anchor = None
        if "#" in target:
            target, anchor = target.split("#", 1)

        # Try direct lookup
        key = target.lower()
        if key in self._index:
            return self._index[key]

        # Try with .md extension explicitly
        if (self.vault_root / f"{target}.md").is_file():
            return self.vault_root / f"{target}.md"

        # Try treating as path with directories
        path = self.vault_root / target
        if path.is_file():
            return path
        if (path.with_suffix(".md")).is_file():
            return path.with_suffix(".md")

        return None

    def render_wikilink(self, match: re.Match) -> str:
        """Render a [[wikilink]] match to an HTML <a> tag."""
        content = match.group(1).strip()
        # Parse out optional display text and anchor
        display = content
        anchor = None
        if "|" in content:
            content, display = content.split("|", 1)
        if "#" in content:
            content, anchor = content.split("#", 1)
        elif "#" in display:
            display, anchor = display.split("#", 1)

        target_path = self.resolve(content)
        # Compute URL relative to the request's vault root
        if target_path:
            # URL is the relative path from vault root
            rel = target_path.relative_to(self.vault_root)
            url = "/" + quote(str(rel))
            if anchor:
                url += "#" + quote(anchor)
            return f'<a class="wikilink" href="{url}">{self._escape(display)}</a>'
        else:
            # Missing link — render as broken link with a different style
            return (
                f'<a class="wikilink wikilink-missing" '
                f'href="#" title="Unresolved: {self._escape(content)}" '
                f'data-target="{self._escape(content)}">'
                f'{self._escape(display)}</a>'
            )

    def render_embed(self, match: re.Match) -> str:
        """Render a ![[embed]] match to an <img> or note-reference."""
        content = match.group(1).strip()
        # Parse out optional alt text
        alt = ""
        if "|" in content:
            content, alt = content.split("|", 1)

        target_path = self.resolve(content)
        if target_path:
            # If it's an image, render as <img>
            if target_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
                rel = target_path.relative_to(self.vault_root)
                url = "/" + quote(str(rel))
                return f'<img class="embed-image" src="{url}" alt="{self._escape(alt or content)}" />'
            # If it's a note, render as a transclusion placeholder
            elif target_path.suffix.lower() == ".md":
                rel = target_path.relative_to(self.vault_root)
                url = "/" + quote(str(rel))
                return (
                    f'<div class="embed-note" data-target="{self._escape(content)}">'
                    f'<a class="wikilink" href="{url}">→ {self._escape(alt or content)}</a>'
                    f'<em class="embed-note-hint">(transclusion — open in Obsidian to see full content)</em>'
                    f'</div>'
                )
        # Fallback: unresolved embed
        return f'<span class="embed embed-missing">![[{self._escape(content)}]]</span>'

    @staticmethod
    def _escape(text: str) -> str:
        """Basic HTML escape."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def process_markdown(self, md_text: str) -> str:
        """Process all wikilinks and embeds in a markdown string."""
        # Process embeds first (they start with !)
        text = EMBED_RE.sub(self.render_embed, md_text)
        # Then wikilinks
        text = WIKILINK_RE.sub(self.render_wikilink, text)
        return text
