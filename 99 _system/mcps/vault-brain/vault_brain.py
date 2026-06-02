#!/usr/bin/env python3
"""
vault_brain.py — Thin retrieval wrapper for the Mavis vault.

Esalen posture: deterministic I/O + heuristic retrieval, M3 does the synthesis.
The code is a candidate generator. The model ranks, synthesizes, and answers.
We do not store embeddings on disk (per Friction-free Esalen audit: this is
the thin deterministic layer, not a vector database; embeddings happen in
M3's context at query time when needed).

Per the Arsenal design (03 Projects/Mavis-Apex-Architecture/03 The Custom MCP Arsenal.md):
- Index = note paths + titles + tags + wikilinks + body excerpt (first 2000 chars)
- Search = BM25-ish (title +10, tag +5, body +1+sqrt) with recency boost
- Token budget = explicit; the caller controls the output size
- Anchor-ends packing: top-2 highest-scored at positions 0 and N-1, rest in middle
- Backlinks pulled at index time, not computed per-query

Usage:
    python3 vault_brain.py --reindex                     # rebuild the index
    python3 vault_brain.py --query "search terms"        # one-shot search
    python3 vault_brain.py --serve                       # run as MCP server (stdio)

When the self-model-card MCP is built, this server registers can_i() for its
own actions. Until then, the run-as-script path is the entry point.
"""

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

__version__ = "1.0.0"  # v1: + Headroom-style compression + CCR

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/Users/brassfieldventuresllc/MiniMax-Agent"))
INDEX_PATH = Path(os.environ.get("VAULT_BRAIN_INDEX", str(Path(__file__).parent / "index.json")))

# ============================================================
# HEADROOM-STYLE COMPRESSION (imported from direct-intake)
# ============================================================
#
# The deterministic compression primitive lives in the direct-intake package
# (built 2026-06-02 in Phase 1 of Operation Leviathan). We import it here
# so the same Headroom algorithm runs at every prompt boundary (vault-brain,
# intake, long-context-curator, self-model-card).
#
# If the direct-intake package isn't installed (e.g., vault-brain is being
# run standalone), we fall back to a no-op stub so the search still works.

_INT_INTAKE_PATH = Path(__file__).resolve().parent.parent / "direct-intake"
if str(_INT_INTAKE_PATH) not in sys.path:
    sys.path.insert(0, str(_INT_INTAKE_PATH))

try:
    from intake import compress as _headroom
    HEADROOM_AVAILABLE = True
except ImportError as e:
    print(
        f"WARNING: direct-intake/ intake.compress not importable ({e}). "
        f"vault-brain will run without the Headroom compression layer.",
        file=sys.stderr,
    )
    HEADROOM_AVAILABLE = False

    class _NoOpHeadroom:
        """Fallback when direct-intake isn't on the path. Pure no-op — search
        returns uncompressed content. CCR is unavailable."""

        @staticmethod
        def compress(text: str, **kwargs):
            class _Block:
                text = text
                ccr_hash = _headroom_unavailable_hash()
                original_tokens = len(text) // 4
                compressed_tokens = len(text) // 4
                compression_ratio = 1.0
                algorithms_applied = []
            return _Block()

        @staticmethod
        def sha256_hex(text: str) -> str:
            return _headroom_unavailable_hash()

        @staticmethod
        def get_store():
            return _NoOpCCRStore()

    class _NoOpCCRStore:
        def put(self, text): return "unavailable"
        def get(self, h): return None
        def has(self, h): return False
        def size(self): return 0
        def clear(self): pass

    def _headroom_unavailable_hash() -> str:
        return "0" * 64

    _headroom = _NoOpHeadroom()  # type: ignore[assignment]


# Module-level CCR store — process-local, but enough for a single session
_ccr_store = _headroom.get_store()

# Skip these directories when walking the vault
SKIP_DIRS = {".obsidian", ".git", ".smart-env", ".claude", ".claudian", "node_modules"}

# Skip these too (vault-internal noise, not searchable content)
SKIP_DIRS |= {"05 Archive", "99 _system/logs"}

# ============================================================
# INDEXER
# ============================================================

def parse_frontmatter(content: str) -> dict:
    """Extract frontmatter as a dict. Returns {} if no frontmatter."""
    if not content.startswith("---\n"):
        return {}
    try:
        end = content.index("\n---\n", 4)
        fm_text = content[4:end]
        result = {}
        for line in fm_text.split("\n"):
            if ":" in line:
                key, _, value = line.partition(":")
                result[key.strip()] = value.strip()
        return result
    except ValueError:
        return {}

def extract_title(content: str, fallback: str) -> str:
    """Get the H1 title from a note, or fallback to filename."""
    for line in content.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return fallback

def extract_tags(fm: dict) -> list:
    """Extract tags from frontmatter. Handles [tag1, tag2] and tag1,tag2."""
    tags_str = fm.get("tags", "")
    if not tags_str:
        return []
    tags_str = tags_str.strip("[]")
    return [t.strip().strip("\"'") for t in tags_str.split(",") if t.strip()]

def extract_wikilinks(content: str) -> list:
    """Find all unique [[wikilinks]] in content. Returns link targets, not display text."""
    return list(set(re.findall(r"\[\[([^\]\|]+?)(?:\|[^\]]+)?\]\]", content)))

def extract_body(content: str) -> str:
    """Get the body of a note, after the frontmatter (if any)."""
    if content.startswith("---\n"):
        body_start = content.find("\n---\n", 4)
        if body_start != -1:
            return content[body_start + 5:]
    return content

def build_index(vault_root: Path = VAULT_ROOT) -> list:
    """Walk the vault, extract metadata for every .md file. Returns a list of note dicts."""
    notes = []
    for md_path in vault_root.rglob("*.md"):
        # Skip files in excluded directories (anywhere in the path)
        if any(part in SKIP_DIRS for part in md_path.parts):
            continue
        try:
            content = md_path.read_text(encoding="utf-8", errors="ignore")
        except (IOError, OSError):
            continue
        rel = md_path.relative_to(vault_root)
        fm = parse_frontmatter(content)
        body = extract_body(content)
        notes.append({
            "path": str(rel),
            "title": extract_title(content, md_path.stem),
            "tags": extract_tags(fm),
            "wikilinks": extract_wikilinks(content),
            "body_excerpt": body[:2000],
            "mtime": md_path.stat().st_mtime,
        })
    return notes

def save_index(notes: list, path: Path = INDEX_PATH) -> None:
    """Write the index to a JSON file."""
    payload = {
        "vault_root": str(VAULT_ROOT),
        "indexed_at": time.time(),
        "note_count": len(notes),
        "notes": notes,
    }
    path.write_text(json.dumps(payload, indent=1))

def load_index(path: Path = INDEX_PATH) -> dict | None:
    """Load the index from a JSON file. Returns None if not found."""
    if not path.exists():
        return None
    return json.loads(path.read_text())

# ============================================================
# SEARCHER — BM25-ish scoring + anchor-ends packing
# ============================================================

def tokenize(text: str) -> list:
    """Lowercase + split on non-alphanumeric. Simple and effective for this corpus."""
    return re.findall(r"\w+", text.lower())

def score_note(note: dict, query_tokens: list) -> tuple:
    """Score a single note against the query tokens. Returns (score, signals_list)."""
    score = 0.0
    signals = []
    title_tokens = set(tokenize(note["title"]))
    tag_tokens = set()
    for tag in note["tags"]:
        tag_tokens.update(tokenize(tag))
    body_tokens = tokenize(note["body_excerpt"])
    body_token_counts = defaultdict(int)
    for t in body_tokens:
        body_token_counts[t] += 1

    for qt in query_tokens:
        if qt in title_tokens:
            score += 10
            signals.append(f"title:{qt}")
        if qt in tag_tokens:
            score += 5
            signals.append(f"tag:{qt}")
        if qt in body_token_counts:
            count = body_token_counts[qt]
            # Log-saturation prevents long notes from dominating
            score += 1 + (count ** 0.5) * 0.5
            signals.append(f"body:{qt}x{count}" if count > 1 else f"body:{qt}")

    # Slight recency boost (notes modified in the last 7 days)
    age_days = (time.time() - note.get("mtime", 0)) / 86400
    if age_days < 7:
        score += 1.0
    elif age_days < 30:
        score += 0.5

    return score, signals

def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token. Good enough for budgeting."""
    return len(text) // 4

def pack_anchor_ends(
    ranked: list,
    max_total_tokens: int,
    compress: bool = True,
) -> list:
    """Pack the ranked notes using anchor-ends strategy.

    Per the M3 MSA pattern: highest-signal content goes to positions 0 and
    (budget-1), where attention is strongest. We put the top-2 at the ends
    and the rest in the middle.

    If compress=True (default), each rendered chunk is run through the
    Headroom-style compression layer before being added to the pack. The
    original is stored in the CCR store with its SHA-256 hash; the
    compressed text + hash are returned to the model. The model can call
    ccr_retrieve(hash) when it needs the original.
    """
    # Filter zero-score, sort by score desc
    ranked = [(n, s, sigs) for n, s, sigs in ranked if s > 0]
    ranked.sort(key=lambda x: -x[1])
    if not ranked:
        return []

    # Pack within token budget
    packed = []
    tokens_used = 0
    for note, score, signals in ranked:
        # Render the note as a markdown chunk (this is what M3 will see)
        rendered = (
            f"# {note['title']}\n\n"
            f"Path: {note['path']}\n"
            f"Tags: {', '.join(note['tags'])}\n"
            f"Signals: {', '.join(signals[:5])}\n\n"
            f"{note['body_excerpt']}"
        )
        chunk_tokens = estimate_tokens(rendered)

        # Compress the chunk (Headroom). Token budget counts the *compressed*
        # size — that's what crosses the prompt boundary.
        if compress and HEADROOM_AVAILABLE and chunk_tokens >= 100:
            c = _headroom.compress(rendered, aggressive=False, min_tokens_to_compress=100)
            # Store the original in the CCR store (idempotent on hash)
            _ccr_store.put(rendered)
            rendered_to_pack = c.text
            chunk_tokens_estimate = c.compressed_tokens
            compression_info = {
                "ccr_hash": c.ccr_hash,
                "original_tokens": c.original_tokens,
                "compressed_tokens": c.compressed_tokens,
                "ratio": round(c.compression_ratio, 3),
                "savings_pct": round((1.0 - c.compression_ratio) * 100, 1),
                "algorithms": c.algorithms_applied,
            }
        else:
            rendered_to_pack = rendered
            chunk_tokens_estimate = chunk_tokens
            compression_info = None

        if tokens_used + chunk_tokens_estimate > max_total_tokens and packed:
            break
        chunk = {
            "path": note["path"],
            "title": note["title"],
            "tags": note["tags"],
            "score": round(score, 2),
            "signals": signals[:5],
            "rendered": rendered_to_pack,
            "tokens_estimate": chunk_tokens_estimate,
        }
        if compression_info is not None:
            chunk["compression"] = compression_info
        packed.append(chunk)
        tokens_used += chunk_tokens_estimate

    # Re-arrange anchor-ends: put [1st, 3rd, 5th, ..., 4th, 2nd] so 1st is at
    # position 0 and 2nd is at position N-1, the rest fan out from the ends.
    if len(packed) >= 4:
        first, second = packed[0], packed[1]
        middle = packed[2:]
        # Place remaining items alternating from the end inward
        arranged = [first]
        left, right = [], []
        for i, n in enumerate(middle):
            (left if i % 2 == 0 else right).append(n)
        arranged = [first] + left + list(reversed(right)) + [second]
        packed = arranged

    return packed

def search(query: str, top_k: int = 20, max_total_tokens: int = 50_000,
           include_backlinks: bool = True, compress: bool = True,
           index: dict | None = None) -> dict:
    """Main search entry point. Returns packed notes ready for M3 to reason over.

    Args:
        query: The search query.
        top_k: Maximum number of notes to return.
        max_total_tokens: Token budget for the returned content.
        include_backlinks: Whether to inject backlinks for each returned note.
        compress: If True (default), run the Headroom compression layer over
            each rendered chunk before returning. The original is held in the
            CCR store; the model can call ccr_retrieve(hash) to get it back
            if it detects signal decay in the compressed version.
        index: Pre-loaded index (for testing). Default: load from disk.

    Returns:
        dict with packed notes, total_tokens_estimate, and a
        compression_summary showing the overall ratio.
    """
    if index is None:
        index = load_index()
    if not index:
        return {"error": "no index loaded; run --reindex first"}

    query_tokens = tokenize(query)
    if not query_tokens:
        return {"error": "empty query (no extractable tokens)"}

    # Score every note
    scored = []
    for note in index["notes"]:
        s, sigs = score_note(note, query_tokens)
        if s > 0:
            scored.append((note, s, sigs))

    # Take top-K
    scored.sort(key=lambda x: -x[1])
    top = scored[:top_k]

    # Pack anchor-ends within budget (with optional compression)
    packed = pack_anchor_ends(top, max_total_tokens, compress=compress)

    # Optionally inject backlinks for each packed note
    if include_backlinks:
        path_to_note = {n["path"]: n for n in index["notes"]}
        for chunk in packed:
            this_path = chunk["path"]
            backlinks = []
            for n in index["notes"]:
                if this_path in n["wikilinks"] or any(this_path.split(".md")[0] in wl for wl in n["wikilinks"]):
                    backlinks.append(n["title"])
            chunk["backlinks"] = backlinks[:5]

    # Compression summary — surfaces the multiplier to the caller
    total_tokens = sum(c["tokens_estimate"] for c in packed)
    original_tokens = sum(
        c.get("compression", {}).get("original_tokens", c["tokens_estimate"])
        for c in packed
    )
    if original_tokens > 0 and total_tokens > 0 and compress:
        compression_summary = {
            "enabled": True,
            "headroom_available": HEADROOM_AVAILABLE,
            "chunks_compressed": sum(1 for c in packed if c.get("compression")),
            "original_tokens_estimate": original_tokens,
            "compressed_tokens_estimate": total_tokens,
            "overall_ratio": round(total_tokens / original_tokens, 3) if original_tokens else 1.0,
            "overall_savings_pct": round(
                (1.0 - (total_tokens / original_tokens)) * 100, 1
            ) if original_tokens else 0.0,
        }
    else:
        compression_summary = {
            "enabled": False,
            "headroom_available": HEADROOM_AVAILABLE,
        }

    return {
        "query": query,
        "vault_root": index.get("vault_root", str(VAULT_ROOT)),
        "indexed_at": index.get("indexed_at"),
        "note_count_in_index": index.get("note_count", 0),
        "candidates_scored": len(scored),
        "returned": len(packed),
        "total_tokens_estimate": total_tokens,
        "compression_summary": compression_summary,
        "notes": packed,
    }

# ============================================================
# MCP SERVER (thin wrapper)
# ============================================================

def run_mcp_server():
    """Run as MCP server over stdio. The Arsenal-spec tool surface."""
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
    except ImportError:
        print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
        sys.exit(1)

    server = Server("vault-brain")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="search",
                description=(
                    "Whole-vault semantic search. Returns top-K most relevant notes "
                    "packed anchor-ends style within an explicit token budget. "
                    "The model (M3) does the final ranking and synthesis over the returned notes. "
                    "By default, each chunk is compressed via the Headroom-style layer; "
                    "set compress=false to get the raw rendered markdown (use this when you "
                    "need exact content and are willing to spend the tokens). Use ccr_retrieve "
                    "to get the original text of a specific compressed chunk when you detect "
                    "signal decay in the compressed version."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "top_k": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100},
                        "max_total_tokens": {"type": "integer", "default": 50000, "minimum": 1000, "maximum": 200000},
                        "include_backlinks": {"type": "boolean", "default": True},
                        "compress": {
                            "type": "boolean",
                            "default": True,
                            "description": (
                                "Run Headroom compression on each chunk before returning. "
                                "Default True (recommended for budget). Set False to skip "
                                "compression (e.g., for high-fidelity debug or short queries)."
                            ),
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="ccr_retrieve",
                description=(
                    "Retrieve the original (uncompressed) text of a chunk by its CCR hash. "
                    "CCR = Content-Addressable Compression with Retrieval. The hash is "
                    "returned in the search() result's chunk['compression']['ccr_hash']. "
                    "Use this when you detect signal decay in the compressed version and "
                    "need the original to reason correctly. Returns the raw markdown text."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ccr_hash": {
                            "type": "string",
                            "description": "SHA-256 hash returned by a search() result",
                        },
                    },
                    "required": ["ccr_hash"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "search":
            result = search(**arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        if name == "ccr_retrieve":
            if not HEADROOM_AVAILABLE:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "ccr_retrieve unavailable: Headroom compression not loaded"}, indent=2),
                )]
            ccr_hash = arguments.get("ccr_hash", "")
            original = _ccr_store.get(ccr_hash)
            if original is None:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"ccr_hash not found in store: {ccr_hash[:16]}...",
                        "hint": "Hashes are process-local; only chunks returned by search() in this session are retrievable.",
                    }, indent=2),
                )]
            return [TextContent(type="text", text=original)]

        raise ValueError(f"Unknown tool: {name}")

    import asyncio
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    asyncio.run(main())

# ============================================================
# CLI
# ============================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="vault-brain — thin retrieval wrapper for Mavis (Esalen posture)")
    parser.add_argument("--reindex", action="store_true", help="Rebuild the vault index")
    parser.add_argument("--query", metavar="Q", help="Run a one-shot search query")
    parser.add_argument("--top-k", type=int, default=20, help="Top-K notes to return (default 20)")
    parser.add_argument("--max-tokens", type=int, default=50_000, help="Max total tokens to return (default 50000)")
    parser.add_argument("--no-backlinks", action="store_true", help="Skip backlink injection")
    parser.add_argument("--no-compress", action="store_true",
                        help="Disable Headroom compression (return raw rendered markdown)")
    parser.add_argument("--ccr-retrieve", metavar="HASH",
                        help="Retrieve the original text for a CCR hash and print it")
    parser.add_argument("--serve", action="store_true", help="Run as MCP server (stdio)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    if args.reindex:
        notes = build_index()
        save_index(notes)
        print(f"Indexed {len(notes)} notes → {INDEX_PATH}", file=sys.stderr)
        return 0

    if args.ccr_retrieve:
        if not HEADROOM_AVAILABLE:
            print("ERROR: Headroom compression not available.", file=sys.stderr)
            return 1
        original = _ccr_store.get(args.ccr_retrieve)
        if original is None:
            print(f"ccr_hash not found: {args.ccr_retrieve}", file=sys.stderr)
            return 1
        print(original)
        return 0

    if args.query:
        index = load_index()
        if not index:
            print("No index found. Run --reindex first.", file=sys.stderr)
            return 1
        result = search(
            args.query,
            top_k=args.top_k,
            max_total_tokens=args.max_tokens,
            include_backlinks=not args.no_backlinks,
            compress=not args.no_compress,
            index=index,
        )
        print(json.dumps(result, indent=2))
        return 0

    if args.serve:
        run_mcp_server()
        return 0

    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
