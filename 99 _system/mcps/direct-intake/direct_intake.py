#!/usr/bin/env python3
"""
direct_intake.py — The Universal Ingestion Engine for Mavis.

Esalen posture: thin deterministic layer. This file is the MCP server.
The Python does fetch + convert + compress. The model (M3) does the
understanding + classification + linking.

Five tools exposed (per 04 Direct-Intake MCP design):
    1. intake.drop     — register a file/URL for ingestion
    2. intake.process  — run the ingestion pipeline (fetch/convert/compress)
    3. intake.review   — approve / edit / reject a processed drop
    4. intake.list     — list pending drops
    5. intake.explain  — show what links were suggested and why

The pipeline (per the design doc):
    drop → sniff (type detection)
        → convert (markitdown for files, scrapling for URLs)
            → compress (Headroom-style, deterministic, CCR)
                → M3 call (classification + linking) [out of scope for this server]
                    → file to 00 Inbox/ or permanent folder

This server is steps 1-3. Step 4 (M3 classification) is the model's job.
Step 5 (filing) happens in intake.review when the human (or model) approves.

Usage:
    # As a CLI (one-shot):
    python3 direct_intake.py --url "https://en.wikipedia.org/wiki/Markdown"
    python3 direct_intake.py --file /path/to/document.pdf

    # As an MCP server (stdio):
    python3 direct_intake.py --serve
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

# Allow `from intake import ...` when run as a script
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from intake import compress, convert, scrape, sniff, store  # noqa: E402

__version__ = "0.1.0"

log = logging.getLogger("direct-intake")

# Default drop folder (per design doc)
DEFAULT_DROP_ROOT = Path(
    os.environ.get("INTAKE_DROP_ROOT", "/Users/brassfieldventuresllc/Mavis-Inbox")
)
# Default Inbox in the vault (for the rendered markdown output)
DEFAULT_VAULT_INBOX = Path(
    os.environ.get(
        "INTAKE_VAULT_INBOX",
        "/Users/brassfieldventuresllc/MiniMax-Agent/00 Inbox",
    )
)

# Minimum tokens to trigger compression. Below this, the overhead isn't worth it.
COMPRESS_THRESHOLD_TOKENS = 200

# Maximum markdown size we'll keep in the audit log. Larger → truncate, store full elsewhere.
EXCERPT_CHARS = 500


# ============================================================
# INGESTION PIPELINE
# ============================================================

class IngestionResult:
    """The output of the ingestion pipeline (steps 1-3)."""

    def __init__(
        self,
        record: store.IntakeRecord,
        markdown: str,
        compressed: compress.CompressedBlock,
    ) -> None:
        self.record = record
        self.markdown = markdown
        self.compressed = compressed

    def to_dict(self) -> dict:
        d = self.record.to_dict()
        d["_compression"] = {
            "original_tokens": self.compressed.original_tokens,
            "compressed_tokens": self.compressed.compressed_tokens,
            "ratio": self.compressed.compression_ratio,
            "savings_pct": round(
                (1.0 - self.compressed.compression_ratio) * 100, 1
            ),
            "algorithms_applied": self.compressed.algorithms_applied,
            "ccr_hash": self.compressed.ccr_hash,
        }
        return d


def ingest(source: str, drop_root: Path = DEFAULT_DROP_ROOT) -> IngestionResult:
    """Run the full ingestion pipeline on a file path or URL.

    1. Sniff — type detection + security validation
    2. Convert — markitdown (files) or scrapling (URLs)
    3. Compress — Headroom-style deterministic compression
    4. Persist — write the intake-log entry

    The model (M3) is called next to classify + link, but that's outside
    this server's scope. The result returned here is everything the model
    needs to do its job.
    """
    record = store.IntakeRecord(
        intake_id=store.make_intake_id(source),
        dropped_at=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        source=source,
        type="unknown",
        converter="",
        size_bytes=None,
        status="processing",
    )

    # ---- Step 1: Sniff ----
    try:
        sn = sniff.sniff(source, drop_root=drop_root)
        record.type = sn.type
        record.converter = sn.converter
        record.size_bytes = sn.size_bytes
        record.extra = sn.extra
    except sniff.SniffError as e:
        record.status = "rejected"
        record.error = f"sniff: {e}"
        store.write_log(record)
        raise

    # ---- Step 2: Convert ----
    markdown = ""
    try:
        if sn.type == "url":
            html = scrape.fetch(sn.source)
            markdown = convert.convert_stream(html.encode("utf-8"), "text/html")
        elif sn.type == "text" or sn.type == "data":
            # Direct read, no conversion
            markdown = Path(sn.source).read_text(encoding="utf-8", errors="ignore")
        elif sn.converter == "markitdown":
            markdown = convert.convert_local(sn.source)
        else:
            record.status = "rejected"
            record.error = f"unsupported converter: {sn.converter} for type {sn.type}"
            store.write_log(record)
            raise RuntimeError(record.error)
    except (scrape.ScrapeError, convert.ConvertError) as e:
        record.status = "rejected"
        record.error = f"convert: {e}"
        store.write_log(record)
        raise

    # ---- Step 3: Compress ----
    compressed = compress.compress(
        markdown,
        aggressive=False,  # safe default: markdown_clean + whitespace_squash
        min_tokens_to_compress=COMPRESS_THRESHOLD_TOKENS,
    )
    # Always retain the original in the CCR store, regardless of whether
    # compression actually ran. The model can opt back in.
    ccr_hash = compress.sha256_hex(markdown)
    compress.get_store().put(markdown)
    if compressed.ccr_hash != ccr_hash:
        # The compress() function may have used a different hash path on
        # the no-op branch. Override to be consistent.
        compressed = compress.CompressedBlock(
            text=compressed.text,
            ccr_hash=ccr_hash,
            original_tokens=compressed.original_tokens,
            compressed_tokens=compressed.compressed_tokens,
            compression_ratio=compressed.compression_ratio,
            algorithms_applied=compressed.algorithms_applied,
        )

    # ---- Step 4: Persist audit trail ----
    record.markdown_excerpt = markdown[:EXCERPT_CHARS]
    record.status = "ready"  # awaiting M3 classification
    record.extra = {**record.extra, "ccr_hash": ccr_hash}
    store.write_log(record)

    return IngestionResult(record=record, markdown=markdown, compressed=compressed)


# ============================================================
# MCP SERVER
# ============================================================

def run_mcp_server() -> None:
    """Run the direct-intake MCP server over stdio."""
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent, Tool
    except ImportError:
        print(
            "ERROR: mcp package not installed. pip install mcp[cli]",
            file=sys.stderr,
        )
        sys.exit(1)

    server = Server("direct-intake")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="intake.drop",
                description=(
                    "Register a file or URL for ingestion. The Sniff router "
                    "detects the type and routes to the right converter "
                    "(markitdown for documents, scrapling for URLs, passthrough "
                    "for text/data). The output is clean markdown."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": (
                                "Absolute file path or HTTP(S) URL. URLs are "
                                "fetched via Scrapling with adaptive selectors. "
                                "Files are validated against the drop folder."
                            ),
                        },
                    },
                    "required": ["source"],
                },
            ),
            Tool(
                name="intake.process",
                description=(
                    "Run the ingestion pipeline on a registered drop: fetch "
                    "(if URL), convert to markdown, compress (Headroom-style, "
                    "deterministic, CCR-reversible), and write the audit log. "
                    "Returns the markdown + compression stats. The model does "
                    "the classification + linking step separately."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "The same source passed to intake.drop.",
                        },
                    },
                    "required": ["source"],
                },
            ),
            Tool(
                name="intake.review",
                description=(
                    "Approve / edit / reject a processed drop. Approval writes "
                    "the final note to its destination folder (00 Inbox/ or a "
                    "permanent folder) with the right wikilinks applied."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "intake_id": {"type": "string"},
                        "decision": {
                            "type": "string",
                            "enum": ["approve", "edit", "reject"],
                        },
                        "edits": {
                            "type": "object",
                            "description": "Optional overrides for classification, tags, destination.",
                        },
                    },
                    "required": ["intake_id", "decision"],
                },
            ),
            Tool(
                name="intake.list",
                description=(
                    "List drops in the intake-log, optionally filtered by status. "
                    "Newest first."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": [
                                "queued",
                                "processing",
                                "ready",
                                "needs-review",
                                "rejected",
                                "all",
                            ],
                            "default": "all",
                        },
                        "limit": {"type": "integer", "default": 20},
                    },
                },
            ),
            Tool(
                name="intake.explain",
                description=(
                    "Show the suggested links + tags for a processed drop, with "
                    "the matched-context snippets so a human can quickly decide."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "intake_id": {"type": "string"},
                    },
                    "required": ["intake_id"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "intake.drop":
                # drop = sniff + register; doesn't run the full pipeline yet
                try:
                    sn = sniff.sniff(
                        arguments["source"], drop_root=DEFAULT_DROP_ROOT
                    )
                    result = {
                        "intake_id": store.make_intake_id(arguments["source"]),
                        "type": sn.type,
                        "converter": sn.converter,
                        "is_url": sn.is_url,
                        "size_bytes": sn.size_bytes,
                        "extra": sn.extra,
                        "status": "queued",
                    }
                except sniff.SniffError as e:
                    result = {"error": str(e), "status": "rejected"}
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            if name == "intake.process":
                try:
                    ir = ingest(arguments["source"], drop_root=DEFAULT_DROP_ROOT)
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(ir.to_dict(), indent=2),
                        )
                    ]
                except (sniff.SniffError, scrape.ScrapeError, convert.ConvertError) as e:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps({"error": str(e)}, indent=2),
                        )
                    ]

            if name == "intake.review":
                # Minimal implementation: look up the record, update its status,
                # (optionally) write the markdown to the destination. Real
                # implementation would invoke the model's classification+linking.
                recs = store.list_pending(log_dir=store.DEFAULT_LOG_DIR, limit=500)
                target = next(
                    (r for r in recs if r.intake_id == arguments["intake_id"]),
                    None,
                )
                if not target:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {"error": f"intake_id not found: {arguments['intake_id']}"},
                                indent=2,
                            ),
                        )
                    ]

                decision = arguments["decision"]
                if decision == "reject":
                    target.status = "rejected"
                elif decision == "approve":
                    target.status = "ready"
                    # Optionally move the markdown to a destination folder
                    # (model will fill in the destination after classification)
                elif decision == "edit":
                    target.status = "needs-review"
                    edits = arguments.get("edits", {})
                    if "classification" in edits:
                        target.classification = edits["classification"]
                    if "summary" in edits:
                        target.summary = edits["summary"]
                    if "tags" in edits:
                        target.suggested_tags = edits["tags"]
                    if "destination" in edits:
                        target.proposed_destination = edits["destination"]

                store.write_log(target)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"intake_id": target.intake_id, "status": target.status},
                            indent=2,
                        ),
                    )
                ]

            if name == "intake.list":
                status = arguments.get("status", "all")
                if status == "all":
                    status = None
                limit = arguments.get("limit", 20)
                recs = store.list_pending(status=status, limit=limit)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            [r.to_dict() for r in recs], indent=2
                        ),
                    )
                ]

            if name == "intake.explain":
                recs = store.list_pending(log_dir=store.DEFAULT_LOG_DIR, limit=500)
                target = next(
                    (r for r in recs if r.intake_id == arguments["intake_id"]),
                    None,
                )
                if not target:
                    return [
                        TextContent(
                            type="text",
                            text=json.dumps(
                                {"error": f"intake_id not found: {arguments['intake_id']}"},
                                indent=2,
                            ),
                        )
                    ]
                # Build a human-readable explanation
                explanation = {
                    "intake_id": target.intake_id,
                    "source": target.source,
                    "type": target.type,
                    "classification": target.classification,
                    "confidence": target.confidence,
                    "summary": target.summary,
                    "suggested_tags": target.suggested_tags,
                    "suggested_links": target.suggested_links,
                    "proposed_destination": target.proposed_destination,
                    "rationale": target.rationale,
                    "markdown_excerpt": target.markdown_excerpt,
                }
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(explanation, indent=2),
                    )
                ]

            raise ValueError(f"unknown tool: {name}")

        except Exception as e:
            log.exception("tool %s failed", name)
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": f"{type(e).__name__}: {e}"}, indent=2),
                )
            ]

    import asyncio

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    asyncio.run(main())


# ============================================================
# CLI
# ============================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="direct-intake — the universal ingestion engine for Mavis"
    )
    parser.add_argument(
        "--url", metavar="URL", help="Ingest a URL (fetch via Scrapling, convert to markdown)"
    )
    parser.add_argument(
        "--file", metavar="PATH", help="Ingest a local file (markitdown → markdown)"
    )
    parser.add_argument(
        "--no-compress", action="store_true", help="Skip the compression step"
    )
    parser.add_argument(
        "--aggressive", action="store_true",
        help="Run aggressive compression (also strip stopwords from prose)"
    )
    parser.add_argument(
        "--out", metavar="PATH",
        help="Write the rendered markdown to PATH (in addition to the audit log)"
    )
    parser.add_argument(
        "--drop-root", type=Path, default=DEFAULT_DROP_ROOT,
        help=f"Path-traversal defense root (default: {DEFAULT_DROP_ROOT})"
    )
    parser.add_argument(
        "--serve", action="store_true", help="Run as MCP server (stdio)"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose logging"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.serve:
        run_mcp_server()
        return 0

    if not (args.url or args.file):
        parser.print_help()
        return 1

    source = args.url or args.file
    try:
        ir = ingest(source, drop_root=args.drop_root)
    except (sniff.SniffError, scrape.ScrapeError, convert.ConvertError) as e:
        print(f"INGEST FAILED: {e}", file=sys.stderr)
        return 2

    # Optional: write the markdown to --out
    if args.out:
        Path(args.out).write_text(ir.markdown, encoding="utf-8")

    # Print the result
    print("=" * 70)
    print(f"INTAKE OK · {ir.record.intake_id}")
    print("=" * 70)
    print(f"  source:    {ir.record.source}")
    print(f"  type:      {ir.record.type}")
    print(f"  converter: {ir.record.converter}")
    print(f"  size:      {ir.record.size_bytes} bytes")
    print(f"  status:    {ir.record.status}")
    print()
    print(f"  markdown:  {compress.estimate_tokens(ir.markdown)} tokens (raw)")
    print(
        f"  compressed:{ir.compressed.compressed_tokens} tokens "
        f"({ir.compressed.algorithms_applied})"
    )
    print(
        f"  ratio:     {ir.compressed.compression_ratio:.3f} "
        f"({(1.0 - ir.compressed.compression_ratio) * 100:.1f}% savings)"
    )
    print(f"  ccr_hash:  {ir.compressed.ccr_hash[:16]}...")
    print()
    if args.out:
        print(f"  written to: {args.out}")
    print()
    # Print first 500 chars of the markdown
    print("--- markdown excerpt (first 500 chars) ---")
    print(ir.markdown[:500])
    print("--- end ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
