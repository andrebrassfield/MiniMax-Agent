"""
Quick test harness for the Glass Server.

Renders INDEX.md (and a few other key files) to HTML and prints a snippet
so we can verify the pipeline works end-to-end. Does NOT start the HTTP
server — that's done by glass_server.py.

Usage:
    .venv/bin/python test_render.py
"""

import sys
from pathlib import Path

_HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(_HERE))

from renderer import MarkdownRenderer

VAULT_ROOT = _HERE.parent.parent.parent
renderer = MarkdownRenderer(VAULT_ROOT)

print(f"Vault: {VAULT_ROOT}")
print(f"Indexed {len(renderer.wikilink_resolver._index)} files")
print()

# Render INDEX.md
test_files = [
    "INDEX.md",
    "SOUL.md",
    "06 Connections/2026-W23 - Operation-Horizon-Synthesis.md",
    "00 Inbox/Horizon-Pitches-2026.md",
    "02 Notes/patterns/Mycelial Routing.md",
]

for rel_path in test_files:
    file_path = VAULT_ROOT / rel_path
    if not file_path.is_file():
        print(f"SKIP: {rel_path} (not found)")
        continue
    try:
        data = renderer.render_file(file_path)
        print(f"=== {rel_path} ===")
        print(f"  title: {data['title']}")
        print(f"  lead: {(data['lead_quote'] or '')[:100]}")
        print(f"  body length: {len(data['body_html'])} chars")
        print(f"  dataview blocks: {len(data['dataview_count'])}")
        print(f"  mtime: {data['mtime']}")
        # Check for unresolved wikilinks
        import re
        broken = re.findall(r'data-target="([^"]+)"', data['body_html'])
        if broken:
            print(f"  broken wikilinks: {len(broken)} (showing first 3: {broken[:3]})")
        # Check for mermaid blocks
        mermaid = data['body_html'].count('class="mermaid"')
        if mermaid:
            print(f"  mermaid blocks: {mermaid}")
        print()
    except Exception as e:
        print(f"ERROR rendering {rel_path}: {e}")
        import traceback
        traceback.print_exc()
        print()

# Now actually render INDEX.md to an HTML file we can inspect
print("=" * 60)
print("Rendering INDEX.md to test_output.html...")
print("=" * 60)

from glass_server import load_template
template = load_template()

index_data = renderer.render_file(VAULT_ROOT / "INDEX.md")
import html
page = template
page = page.replace("{{TITLE}}", html.escape(index_data["title"]))
page = page.replace(
    "{{LEAD_QUOTE}}",
    f'<blockquote class="lead-quote">{html.escape(index_data["lead_quote"])}</blockquote>'
    if index_data["lead_quote"] else "",
)
page = page.replace("{{BODY_HTML}}", index_data["body_html"])
page = page.replace("{{METADATA_HTML}}", index_data["metadata_html"])
page = page.replace("{{REL_PATH}}", "INDEX.md")
page = page.replace("{{MTIME}}", index_data["mtime"].isoformat(timespec="seconds"))
page = page.replace("{{DATAVIEW_COUNT}}", str(len(index_data["dataview_count"])))

output_path = _HERE / "test_output.html"
output_path.write_text(page, encoding="utf-8")
print(f"Wrote {output_path} ({len(page)} chars)")

# Print a snippet — the first 2000 chars of body_html, then a peek at the page
print()
print("=" * 60)
print(f"HTML SNIPPET (first 2000 chars of body, then 1000 of full page):")
print("=" * 60)
print()
print(index_data['body_html'][:2000])
print()
print("---FULL PAGE (first 1500 chars)---")
print(page[:1500])
