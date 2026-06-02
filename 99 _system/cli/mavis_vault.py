"""
mavis-vault — the Mavis vault CLI toolkit.

A thin wrapper around the Glass Server's renderer module. The CLI is
one surface of one engine; the Glass Server (a daemon) is the other.

Subcommands:
    serve          Start the Glass Server (default: localhost:8765)
    render <path>  Render a single file to HTML
    audit          Vault health check (broken wikilinks, missing frontmatter)
    tree           Print the vault folder structure
    stats          Quick vault statistics

See 03 Projects/Obsidian-Glass/CLI-Toolkit.md for the full spec.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Reuse the Glass Server's renderer module
_HERE = Path(__file__).parent.resolve()
_GLASS_SERVER = _HERE.parent / "mcps" / "glass-server"
sys.path.insert(0, str(_GLASS_SERVER))

from renderer import MarkdownRenderer, parse_frontmatter  # noqa: E402

DEFAULT_VAULT = _HERE.parent.parent
DEFAULT_PORT = 8765


# ANSI colors (disabled when stdout is not a TTY)
class C:
    USE = sys.stdout.isatty()
    RED = "\033[31m" if USE else ""
    GREEN = "\033[32m" if USE else ""
    YELLOW = "\033[33m" if USE else ""
    BLUE = "\033[34m" if USE else ""
    BOLD = "\033[1m" if USE else ""
    DIM = "\033[2m" if USE else ""
    RESET = "\033[0m" if USE else ""


def ok(msg): return f"{C.GREEN}OK{C.RESET}    {msg}"
def warn(msg): return f"{C.YELLOW}WARN{C.RESET}  {msg}"
def err(msg): return f"{C.RED}ERROR{C.RESET}  {msg}"
def info(msg): return f"{C.BLUE}INFO{C.RESET}  {msg}"


def resolve_vault(args) -> Path:
    """Resolve the vault root from args or default."""
    p = Path(args.vault).resolve() if getattr(args, "vault", None) else DEFAULT_VAULT.resolve()
    if not p.is_dir():
        sys.stderr.write(f"Vault not found: {p}\n")
        sys.exit(1)
    return p


# ---------- Subcommand: serve ----------

def cmd_serve(args):
    """Start the Glass Server. Thin wrapper around glass_server.main()."""
    sys.argv = ["glass_server.py"]
    if args.port:
        sys.argv += ["--port", str(args.port)]
    if args.host:
        sys.argv += ["--host", args.host]
    if args.vault:
        sys.argv += ["--vault", args.vault]
    # Re-use the Glass Server's main
    import glass_server
    glass_server.main()


# ---------- Subcommand: render ----------

def cmd_render(args):
    """Render a single file to HTML."""
    vault = resolve_vault(args)
    renderer = MarkdownRenderer(vault)

    target = args.path
    file_path = (vault / target).resolve()
    # Path safety
    try:
        file_path.relative_to(vault)
    except ValueError:
        sys.stderr.write(f"Path escapes vault: {target}\n")
        sys.exit(1)

    if not file_path.is_file():
        sys.stderr.write(f"Not found: {file_path}\n")
        sys.exit(1)

    if file_path.suffix.lower() != ".md":
        sys.stderr.write(f"Not a .md file: {file_path}\n")
        sys.exit(1)

    data = renderer.render_file(file_path)
    if args.no_template:
        html = data["body_html"]
    else:
        # Use the Glass Server's page template
        from glass_server import load_template
        import html as html_lib
        template = load_template()
        page = template
        page = page.replace("{{TITLE}}", html_lib.escape(data["title"]))
        page = page.replace(
            "{{LEAD_QUOTE}}",
            f'<blockquote class="lead-quote">{html_lib.escape(data["lead_quote"])}</blockquote>'
            if data["lead_quote"] else "",
        )
        page = page.replace("{{BODY_HTML}}", data["body_html"])
        page = page.replace("{{METADATA_HTML}}", data["metadata_html"])
        page = page.replace("{{REL_PATH}}", str(file_path.relative_to(vault)))
        page = page.replace("{{MTIME}}", data["mtime"].isoformat(timespec="seconds"))
        page = page.replace("{{DATAVIEW_COUNT}}", str(len(data["dataview_count"])))
        html = page

    if args.out:
        Path(args.out).write_text(html, encoding="utf-8")
        sys.stderr.write(f"Wrote {args.out} ({len(html)} bytes)\n")
    else:
        sys.stdout.write(html)
        if not html.endswith("\n"):
            sys.stdout.write("\n")


# ---------- Subcommand: audit ----------

# Wikilink regex for audit (mirror of wikilinks.py)
WIKILINK_RE = re.compile(r"\[\[([^\[\]\n]+?)\]\]")

# Atomic note locations (mirror of CHIEF conventions)
ATOMIC_DIRS = [
    "02 Notes/patterns",
    "02 Notes/ideas",
    "02 Notes/articles",
    "02 Notes/questions",
    "06 Connections",
    "00 Inbox",
]


def cmd_audit(args):
    """Run a vault health check."""
    vault = resolve_vault(args)
    renderer = MarkdownRenderer(vault)
    index = renderer.wikilink_resolver._index
    index_set = set(index.keys())

    # 1. Index stats
    md_files = list(vault.rglob("*.md"))
    atomic_files = [
        f for f in md_files
        if str(f.relative_to(vault)).startswith(tuple(ATOMIC_DIRS))
    ]

    # 2. Broken wikilinks per file
    broken_wikilinks = defaultdict(list)
    orphan_atomic = []
    missing_frontmatter = []
    dataview_count = 0
    total_wikilinks = 0

    for md_file in md_files:
        if any(part.startswith(".") for part in md_file.parts):
            continue
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rel = str(md_file.relative_to(vault))
        # Frontmatter check (only for atomic)
        is_atomic = rel.startswith(tuple(ATOMIC_DIRS))
        if is_atomic:
            fm, _ = parse_frontmatter(text)
            if not fm:
                missing_frontmatter.append(rel)
        # Wikilink check
        for match in WIKILINK_RE.finditer(text):
            target = match.group(1).strip()
            if "|" in target:
                target = target.split("|", 1)[0]
            if "#" in target:
                target = target.split("#", 1)[0]
            if not target:
                continue
            total_wikilinks += 1
            key = target.lower()
            if key not in index_set:
                broken_wikilinks[rel].append(target)
        # Dataview check
        dataview_count += len(re.findall(r"```(?:dataview|dataviewjs)", text))

    # 3. Orphan atomic notes (no inbound links from any other file)
    inbound = defaultdict(int)
    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for match in WIKILINK_RE.finditer(text):
            target = match.group(1).strip()
            if "|" in target:
                target = target.split("|", 1)[0]
            if "#" in target:
                target = target.split("#", 1)[0]
            key = target.lower()
            inbound[key] += 1
    for md_file in atomic_files:
        rel = str(md_file.relative_to(vault))
        basename = md_file.stem.lower()
        # Check inbound by basename and by full path
        if inbound[basename] == 0:
            orphan_atomic.append(rel)

    # 4. Build report
    if args.json:
        report = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "vault_root": str(vault),
            "total_files": len(md_files),
            "atomic_files": len(atomic_files),
            "total_wikilinks": total_wikilinks,
            "broken_wikilinks": dict(broken_wikilinks),
            "orphan_atomic_notes": orphan_atomic,
            "missing_frontmatter_atomic": missing_frontmatter,
            "dataview_blocks": dataview_count,
        }
        print(json.dumps(report, indent=2))
    else:
        print(f"{C.BOLD}=== VAULT AUDIT — {datetime.now().isoformat(timespec='seconds')} ==={C.RESET}")
        print(f"Vault: {vault}")
        print()
        print(f"  {info(f'Indexed {len(md_files)} .md files ({len(atomic_files)} atomic)')}")
        print(f"  {info(f'{total_wikilinks} wikilinks total across the vault')}")
        print(f"  {info(f'{dataview_count} dataview/dataviewjs blocks')}")
        print()

        # Broken wikilinks summary
        total_broken = sum(len(v) for v in broken_wikilinks.values())
        if total_broken == 0:
            print(f"  {ok('0 broken wikilinks')}")
        else:
            print(f"  {warn(f'{total_broken} broken wikilinks across {len(broken_wikilinks)} files')}")
            # Show top 5 files with most broken links
            top = sorted(broken_wikilinks.items(), key=lambda x: -len(x[1]))[:5]
            for rel, links in top:
                print(f"      {C.DIM}{rel}{C.RESET}  {len(links)} broken")
                for l in links[:3]:
                    print(f"        {C.DIM}[[{l}]]{C.RESET}")
                if len(links) > 3:
                    print(f"        {C.DIM}... and {len(links) - 3} more{C.RESET}")

        # Orphan atomic notes
        if orphan_atomic:
            print(f"  {warn(f'{len(orphan_atomic)} orphan atomic notes (no inbound links)')}")
            for rel in orphan_atomic[:5]:
                print(f"      {C.DIM}{rel}{C.RESET}")
            if len(orphan_atomic) > 5:
                print(f"      {C.DIM}... and {len(orphan_atomic) - 5} more{C.RESET}")
        else:
            print(f"  {ok('No orphan atomic notes')}")

        # Missing frontmatter
        if missing_frontmatter:
            print(f"  {err(f'{len(missing_frontmatter)} atomic notes missing frontmatter')}")
            for rel in missing_frontmatter[:5]:
                print(f"      {C.DIM}{rel}{C.RESET}")
        else:
            print(f"  {ok('All atomic notes have frontmatter')}")

        print()
        print(f"  {C.BOLD}Suggested next steps:{C.RESET}")
        if total_broken > 5:
            print(f"    - Run `mavis-vault audit --json` for the full broken-wikilink list")
        if orphan_atomic:
            print(f"    - Review orphan notes; either link them in or archive them")
        if not total_broken and not orphan_atomic:
            print(f"    - Vault is healthy. Run `mavis-vault stats` for a deeper report.")

    # Exit code
    if args.strict and (total_broken > 0 or missing_frontmatter):
        sys.exit(1)


# ---------- Subcommand: tree ----------

def cmd_tree(args):
    """Print the vault's folder structure with file counts."""
    vault = resolve_vault(args)
    max_depth = args.depth or 5

    def walk(path: Path, prefix: str, depth: int):
        if depth > max_depth:
            return
        try:
            entries = sorted(
                [e for e in path.iterdir() if not e.name.startswith(".")],
                key=lambda e: (not e.is_dir(), e.name.lower()),
            )
        except PermissionError:
            return
        # Filter ignored
        skip_prefixes = (".git", ".obsidian", ".smart-env", ".claude", "node_modules")
        entries = [e for e in entries if not any(p in e.parts for p in skip_prefixes)]
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            if entry.is_dir():
                # Count files in this dir
                file_count = sum(1 for _ in entry.rglob("*.md"))
                print(f"{prefix}{connector}{C.BOLD}{entry.name}/{C.RESET}  {C.DIM}({file_count} .md files){C.RESET}")
                extension = "    " if is_last else "│   "
                walk(entry, prefix + extension, depth + 1)
            else:
                if entry.suffix.lower() == ".md":
                    size = entry.stat().st_size
                    print(f"{prefix}{connector}{entry.name}  {C.DIM}({size:,} bytes){C.RESET}")
                else:
                    print(f"{prefix}{connector}{entry.name}")

    print(f"{C.BOLD}{vault.name}/{C.RESET}")
    walk(vault, "", 1)


# ---------- Subcommand: stats ----------

def cmd_stats(args):
    """Quick vault statistics."""
    vault = resolve_vault(args)
    md_files = list(vault.rglob("*.md"))
    md_files = [f for f in md_files if not any(p.startswith(".") for p in f.parts)]

    # Type breakdown
    type_counts = Counter()
    folder_counts = Counter()
    tag_counts = Counter()
    frontmatter_field_count = 0

    for md_file in md_files:
        rel = str(md_file.relative_to(vault))
        # Determine atomic type
        for type_name, prefix in [
            ("pattern", "02 Notes/patterns/"),
            ("idea", "02 Notes/ideas/"),
            ("article", "02 Notes/articles/"),
            ("question", "02 Notes/questions/"),
            ("connection", "06 Connections/"),
            ("inbox", "00 Inbox/"),
        ]:
            if rel.startswith(prefix):
                type_counts[type_name] += 1
                break
        else:
            type_counts["other"] += 1
        # Top folder
        top_folder = rel.split("/")[0] if "/" in rel else "(root)"
        folder_counts[top_folder] += 1
        # Frontmatter
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
            fm, _ = parse_frontmatter(text)
            if fm:
                frontmatter_field_count += len(fm)
                for tag in fm.get("tags", []):
                    if isinstance(tag, str):
                        tag_counts[tag] += 1
        except Exception:
            pass

    if args.json:
        report = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "total_md_files": len(md_files),
            "by_type": dict(type_counts),
            "by_top_folder": dict(folder_counts),
            "top_tags": tag_counts.most_common(15),
            "total_frontmatter_fields": frontmatter_field_count,
        }
        print(json.dumps(report, indent=2))
    else:
        print(f"{C.BOLD}=== VAULT STATS — {datetime.now().isoformat(timespec='seconds')} ==={C.RESET}")
        print(f"Vault: {vault}")
        print()
        print(f"  Total .md files: {C.BOLD}{len(md_files)}{C.RESET}")
        print(f"  Total frontmatter fields: {frontmatter_field_count}")
        print()
        print(f"  {C.BOLD}By atomic type:{C.RESET}")
        for type_name, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"    {type_name:20s}  {count}")
        print()
        print(f"  {C.BOLD}By top-level folder:{C.RESET}")
        for folder, count in sorted(folder_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"    {folder:30s}  {count}")
        print()
        print(f"  {C.BOLD}Top tags:{C.RESET}")
        for tag, count in tag_counts.most_common(15):
            print(f"    {tag:35s}  {count}")


# ---------- Subcommand: wholeness (placeholder) ----------

def cmd_wholeness(args):
    """Score a single note on Alexander's 15 properties. Heuristic-only for now."""
    vault = resolve_vault(args)
    target = args.path
    file_path = (vault / target).resolve()
    try:
        file_path.relative_to(vault)
    except ValueError:
        sys.stderr.write(f"Path escapes vault: {target}\n")
        sys.exit(1)
    if not file_path.is_file():
        sys.stderr.write(f"Not found: {file_path}\n")
        sys.exit(1)
    text = file_path.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(text)

    # Heuristic scoring (full LLM-as-judge is Wholeness-Engine Pitch 2)
    scores = {}
    sections = re.findall(r"^##\s+(.+)$", body, re.MULTILINE)
    wikilinks = WIKILINK_RE.findall(body)
    has_lead_quote = bool(re.search(r"^>\s", body, re.MULTILINE))
    has_metadata = bool(fm)
    total_length = len(body)

    # Levels of Scale: do sections have sub-sections?
    subsections = len(re.findall(r"^###\s+", body, re.MULTILINE))
    scores["Levels of Scale"] = 2 if subsections >= 3 else 1 if subsections >= 1 else 0
    # Strong Centers: does it have a clear title + lead quote?
    scores["Strong Centers"] = 2 if has_lead_quote else 1
    # Thick Boundaries: rough proxy = sections that transition
    scores["Thick Boundaries"] = 1 if len(sections) >= 3 else 0
    # Alternating Repetition: examples + principles mixed?
    has_examples = "## Example" in body or "For example" in body
    has_principles = "## The principle" in body or "## Principle" in body
    scores["Alternating Repetition"] = 2 if has_examples and has_principles else 1
    # Positive Space: rough = uses tables / lists / structure
    scores["Positive Space"] = 2 if "|" in body or "- " in body else 0
    # Good Shape: sections present
    scores["Good Shape"] = 2 if len(sections) >= 3 else 1 if sections else 0
    # Local Symmetries: rough = parallel sections like "What this is NOT" + "What would falsify"
    has_negation = "What this is NOT" in body or "## What" in body
    has_falsify = "What would falsify" in body or "## What would" in body
    scores["Local Symmetries"] = 2 if has_negation and has_falsify else 1
    # Deep Interlock: outbound wikilinks
    scores["Deep Interlock"] = 2 if len(wikilinks) >= 5 else 1 if wikilinks else 0
    # Contrast: different section lengths
    if len(sections) >= 3:
        lens = [len(re.search(rf"## {re.escape(s)}.*?(?=^##|\Z)", body, re.MULTILINE | re.DOTALL).group(0)) for s in sections if re.search(rf"## {re.escape(s)}.*?(?=^##|\Z)", body, re.MULTILINE | re.DOTALL)]
        scores["Contrast"] = 2 if (max(lens) if lens else 0) > 2 * (min(lens) if lens else 1) else 1
    else:
        scores["Contrast"] = 0
    # Gradients: smooth energy — proxy = intro long, conclusion short or vice versa
    scores["Gradients"] = 1
    # Roughness: has honest aside?
    has_aside = "honest" in body.lower() or "caveat" in body.lower() or "limitation" in body.lower()
    scores["Roughness"] = 2 if has_aside else 0
    # Echoes: key term appears 2-3+ times
    words = re.findall(r"\b\w{6,}\b", body.lower())
    word_counts = Counter(words)
    has_echo = any(c >= 3 for c in word_counts.values())
    scores["Echoes"] = 2 if has_echo else 1
    # The Void: closing opens
    last_para = body.strip().split("\n\n")[-1] if body.strip() else ""
    has_void = any(phr in last_para.lower() for phr in ["open", "next", "see also", "anticipated", "future"])
    scores["The Void"] = 2 if has_void else 1
    # Simplicity: density
    word_count = len(body.split())
    scores["Simplicity"] = 2 if 200 <= word_count <= 3000 else 1
    # Not Separateness: ends with connections
    has_connections = "## Connections" in body or "## See also" in body or "[[" in body[-1000:]
    scores["Not Separateness"] = 2 if has_connections else 0

    total = sum(scores.values())
    max_total = 30

    if args.json:
        print(json.dumps({
            "file": str(file_path.relative_to(vault)),
            "score": total,
            "max": max_total,
            "properties": scores,
        }, indent=2))
    else:
        print(f"{C.BOLD}=== WHOLENESS — {file_path.relative_to(vault)} ==={C.RESET}")
        print(f"Score: {C.BOLD}{total}/{max_total}{C.RESET}  ({'alive' if total >= 24 else 'working' if total >= 18 else 'rough' if total >= 12 else 'weak'})")
        print()
        for name, score in scores.items():
            bar = "●" * score + "○" * (2 - score)
            color = C.GREEN if score == 2 else C.YELLOW if score == 1 else C.RED
            print(f"  {color}{bar}{C.RESET}  {name}")
        print()
        print(f"  {C.DIM}(Heuristic scorer — full LLM-as-judge is Wholeness-Engine Pitch 2){C.RESET}")


# ---------- Main ----------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mavis-vault",
        description="Mavis vault CLI toolkit — one engine, many surfaces",
    )
    p.add_argument(
        "--vault", type=Path, default=None,
        help=f"Path to vault root (default: {DEFAULT_VAULT})",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # serve
    sp = sub.add_parser("serve", help="Start the Glass Server")
    sp.add_argument("--port", type=int, default=DEFAULT_PORT)
    sp.add_argument("--host", default="127.0.0.1")
    sp.set_defaults(func=cmd_serve)

    # render
    sp = sub.add_parser("render", help="Render a single file to HTML")
    sp.add_argument("path", help="Path to file (relative to vault root)")
    sp.add_argument("--out", help="Write to file instead of stdout")
    sp.add_argument("--no-template", action="store_true", help="Output only body HTML")
    sp.set_defaults(func=cmd_render)

    # audit
    sp = sub.add_parser("audit", help="Vault health check")
    sp.add_argument("--json", action="store_true", help="Output as JSON")
    sp.add_argument("--strict", action="store_true", help="Exit non-zero on warnings")
    sp.set_defaults(func=cmd_audit)

    # tree
    sp = sub.add_parser("tree", help="Print vault folder structure")
    sp.add_argument("--depth", type=int, default=5, help="Max depth (default 5)")
    sp.set_defaults(func=cmd_tree)

    # stats
    sp = sub.add_parser("stats", help="Vault statistics")
    sp.add_argument("--json", action="store_true", help="Output as JSON")
    sp.set_defaults(func=cmd_stats)

    # wholeness
    sp = sub.add_parser("wholeness", help="Score a note on Alexander's 15 properties")
    sp.add_argument("path", help="Path to file (relative to vault root)")
    sp.add_argument("--json", action="store_true", help="Output as JSON")
    sp.set_defaults(func=cmd_wholeness)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
