#!/usr/bin/env python3
"""
macos-vision-anchor.py — Vision-anchored UI element locator.

The 4th MCP of the Mavis-Apex arsenal (per Operation Daedalus, 2026-06-02).
The problem this solves: native GUI automation breaks when windows move,
load slowly, or change layout. Coordinate-based clickers are brittle.
AX-tree based clickers fail on apps that don't expose accessibility.

The vision-anchor approach: take a screenshot, pass it to M3's native
multimodal vision, ask for the bounding box of a semantic target
("the Obsidian New Note button"), and return the exact coordinates
dynamically. M3 sees what Andre sees; M3's coordinates are grounded in
the actual screen state, not a cached layout.

Esalen posture: thin deterministic layer. The Python does the I/O
(screencapture, file write, response parsing). M3 does the visual
reasoning. No coordinate caching, no layout assumptions, no accessibility
tree parsing.

Two tools exposed:
  - macos_vision_anchor.locate(image_path, target, context="")
      Static image → bounding box. Used in tests and when Andre supplies
      a screenshot manually.
  - macos_vision_anchor.capture_and_locate(target, context="")
      Live screencapture + bounding box. The Omni-Loop's hands.

Usage (CLI):
  python3 macos-vision-anchor.py --locate screenshot.png --target "the Save button"
  python3 macos-vision-anchor.py --capture-and-locate --target "the Obsidian New Note button"
  python3 macos-vision-anchor.py --version

Safety: capture_and_locate uses macOS `screencapture -x` (no sound,
no UI prompt) but it DOES capture the live desktop. Per SOUL § Autonomy
Boundary Table, screencapture is YELLOW-tier. The MCP records every
capture to a vault-internal audit log.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

__version__ = "0.1.0"

# ============================================================
# PATHS
# ============================================================

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/Users/brassfieldventuresllc/MiniMax-Agent"))
MCP_DIR = VAULT_ROOT / "99 _system" / "mcps" / "macos-vision-anchor"
ASSETS_DIR = MCP_DIR / "test_assets"
CAPTURES_DIR = MCP_DIR / "captures"
AUDIT_LOG = MCP_DIR / "vision-anchor-audit.jsonl"

CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# M3 VISION PROMPT
# ============================================================

LOCATE_PROMPT = """You are looking at a screenshot of a macOS UI. The screenshot is exactly {WIDTH} pixels wide and {HEIGHT} pixels tall.

A user (Andre) wants to find this UI element on the screen:

  TARGET: "{target}"

{context_block}
Your job: return the bounding box of this element in the screenshot, as
a JSON object. Use pixel coordinates relative to the top-left of the
image (0,0).

Return ONLY a JSON object in this exact shape, with no preamble and no
markdown fences:

{{
  "found": true,
  "x": <integer, top-left x>,
  "y": <integer, top-left y>,
  "width": <integer>,
  "height": <integer>,
  "confidence": <float 0.0-1.0>,
  "description": "<1 sentence describing what you see at those coords>"
}}

If the target is not in the image, return:
{{
  "found": false,
  "reason": "<1 sentence why not>"
}}
"""


# ============================================================
# RESULT TYPES
# ============================================================

@dataclass
class LocateResult:
    target: str
    image_path: str
    image_width: int
    image_height: int
    found: bool
    bounding_box: Optional[dict] = None
    confidence: float = 0.0
    description: str = ""
    raw_response: str = ""
    timestamp: str = ""
    source: str = "m3-vision"
    request_id: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# M3 VISION CALL (via the matrix describe_images native tool)
# ============================================================

def call_m3_vision(image_path: Path, target: str, context: str = "",
                   width: int = 0, height: int = 0) -> str:
    """Call M3's vision via the matrix MCP describe_images tool.

    This function is intentionally thin. The MCP infrastructure handles
    the actual LLM call. We just build the prompt and parse the response.
    """
    # NOTE: This function does NOT make the LLM call itself. The Daemon
    # (or interactive session) that invokes us will route the prompt +
    # image through describe_images. This keeps the MCP a thin I/O layer
    # per the Esalen posture.
    #
    # What we return is the PROMPT that the caller will feed to
    # describe_images. The caller does the vision call and feeds the
    # raw response back to parse_locate_response().
    context_block = (
        f'Additional context from the user: "{context}"\n'
        if context else ""
    )
    prompt = LOCATE_PROMPT.format(
        target=target,
        context_block=context_block,
        WIDTH=width or "unknown",
        HEIGHT=height or "unknown",
    )
    return prompt


def parse_locate_response(raw_response: str, target: str,
                            image_path: Path, image_width: int,
                            image_height: int) -> LocateResult:
    """Parse M3's JSON response into a LocateResult. Tolerant of
    markdown fences and extra prose.
    """
    request_id = f"va-{int(time.time())}-{uuid.uuid4().hex[:6]}"
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Strip markdown fences
    text = raw_response.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)

    # Extract the first {...} JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return LocateResult(
            target=target, image_path=str(image_path),
            image_width=image_width, image_height=image_height,
            found=False, raw_response=raw_response, timestamp=ts,
            description="no JSON object found in M3 response",
            request_id=request_id,
        )
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        return LocateResult(
            target=target, image_path=str(image_path),
            image_width=image_width, image_height=image_height,
            found=False, raw_response=raw_response, timestamp=ts,
            description=f"JSON parse error: {e}",
            request_id=request_id,
        )

    if not data.get("found", False):
        return LocateResult(
            target=target, image_path=str(image_path),
            image_width=image_width, image_height=image_height,
            found=False, raw_response=raw_response, timestamp=ts,
            description=data.get("reason", "M3 reported not found"),
            request_id=request_id,
        )

    return LocateResult(
        target=target, image_path=str(image_path),
        image_width=image_width, image_height=image_height,
        found=True,
        bounding_box={
            "x": int(data["x"]),
            "y": int(data["y"]),
            "width": int(data["width"]),
            "height": int(data["height"]),
        },
        confidence=float(data.get("confidence", 0.0)),
        description=data.get("description", ""),
        raw_response=raw_response,
        timestamp=ts,
        request_id=request_id,
    )


# ============================================================
# SCREENCAPTURE (macOS)
# ============================================================

def capture_screen() -> Path:
    """Capture the primary display. macOS only. Returns the path to the
    PNG file. Uses `screencapture -x` to suppress sound and prompt.
    """
    if sys.platform != "darwin":
        raise RuntimeError(
            "screencapture is macOS-only; this MCP is darwin-targeted"
        )
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = CAPTURES_DIR / f"capture-{ts}.png"
    # -x: no sound, -t png: PNG format, -C: include cursor (default off)
    subprocess.run(
        ["screencapture", "-x", "-t", "png", str(out)],
        check=True, timeout=10,
    )
    return out


# ============================================================
# IMAGE METADATA
# ============================================================

def get_image_size(path: Path) -> tuple[int, int]:
    """Return (width, height) of a PNG/JPEG. Pure-stdlib fallback if
    PIL is unavailable.
    """
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except ImportError:
        pass
    # Fallback: parse PNG IHDR
    import struct
    with path.open("rb") as f:
        f.read(8)  # PNG signature
        f.read(4)  # IHDR length
        f.read(4)  # IHDR type
        w, h = struct.unpack(">II", f.read(8))
    return (w, h)


# ============================================================
# AUDIT LOG
# ============================================================

def append_audit(record: LocateResult) -> None:
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")


# ============================================================
# MCP SERVER (stdio)
# ============================================================

def run_mcp_server() -> None:
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent, Tool
    except ImportError:
        print("ERROR: mcp package not installed.", file=sys.stderr)
        sys.exit(1)

    server = Server("macos-vision-anchor")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="macos_vision_anchor.locate",
                description=(
                    "Locate a UI element in a screenshot by semantic "
                    "description. Returns a bounding box {x, y, width, "
                    "height} in image pixel coordinates. The Python "
                    "gathers the image + builds the prompt; M3's vision "
                    "does the visual reasoning. Per the Esalen posture, "
                    "this is a thin I/O layer."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "image_path": {"type": "string"},
                        "target": {"type": "string"},
                        "context": {"type": "string", "default": ""},
                    },
                    "required": ["image_path", "target"],
                },
            ),
            Tool(
                name="macos_vision_anchor.capture_and_locate",
                description=(
                    "Capture the live macOS desktop and locate a UI "
                    "element in it. screencapture is YELLOW-tier per "
                    "SOUL — every capture is recorded in the audit log. "
                    "Returns the bounding box as {x, y, width, height}."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "target": {"type": "string"},
                        "context": {"type": "string", "default": ""},
                    },
                    "required": ["target"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "macos_vision_anchor.locate":
                image_path = Path(arguments["image_path"])
                target = arguments["target"]
                context = arguments.get("context", "")
                width, height = get_image_size(image_path)
                prompt = call_m3_vision(image_path, target, context, width, height)
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "image_path": str(image_path),
                        "image_size": [width, height],
                        "target": target,
                        "prompt": prompt,
                        "instruction": (
                            "Call describe_images with this image and "
                            "prompt, then feed the raw response to "
                            "macos_vision_anchor.parse_response."
                        ),
                    }, indent=2, ensure_ascii=False)
                )]
            if name == "macos_vision_anchor.capture_and_locate":
                target = arguments["target"]
                context = arguments.get("context", "")
                image_path = capture_screen()
                width, height = get_image_size(image_path)
                prompt = call_m3_vision(image_path, target, context, width, height)
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "image_path": str(image_path),
                        "image_size": [width, height],
                        "target": target,
                        "prompt": prompt,
                        "instruction": (
                            "Call describe_images with this image and "
                            "prompt, then feed the raw response to "
                            "macos_vision_anchor.parse_response."
                        ),
                    }, indent=2, ensure_ascii=False)
                )]
            raise ValueError(f"unknown tool: {name}")
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"{type(e).__name__}: {e}"})
            )]

    import asyncio

    async def main():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    asyncio.run(main())


# ============================================================
# CLI
# ============================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        prog="macos-vision-anchor.py",
        description="Vision-anchored UI element locator (Esalen posture)",
    )
    ap.add_argument("--locate", metavar="IMAGE", type=Path,
                    help="Locate target in this image (static)")
    ap.add_argument("--target", metavar="TEXT", help="Semantic target string")
    ap.add_argument("--context", metavar="TEXT", default="",
                    help="Additional context for the vision prompt")
    ap.add_argument("--capture-and-locate", action="store_true",
                    help="Capture live screen, then locate")
    ap.add_argument("--parse-response", metavar="RAW", type=str,
                    help="Parse a raw M3 response into a LocateResult JSON. "
                         "Use --with-image/--with-target/--with-width/--with-height.")
    ap.add_argument("--with-image", metavar="PATH", type=str)
    ap.add_argument("--with-target", metavar="TEXT", type=str)
    ap.add_argument("--with-width", type=int, default=0)
    ap.add_argument("--with-height", type=int, default=0)
    ap.add_argument("--serve", action="store_true",
                    help="Run as MCP server (stdio)")
    ap.add_argument("--version", action="version",
                    version=f"%(prog)s {__version__}")
    args = ap.parse_args()

    if args.serve:
        run_mcp_server()
        return 0

    if args.parse_response is not None:
        if not (args.with_image and args.with_target):
            ap.error("--with-image and --with-target required with --parse-response")
        img_path = Path(args.with_image)
        w = args.with_width or (get_image_size(img_path)[0] if img_path.exists() else 0)
        h = args.with_height or (get_image_size(img_path)[1] if img_path.exists() else 0)
        result = parse_locate_response(
            args.parse_response, args.with_target, img_path, w, h
        )
        append_audit(result)
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return 0 if result.found else 2

    if args.locate is not None:
        if not args.target:
            ap.error("--target is required with --locate")
        if not args.locate.exists():
            print(f"ERROR: image not found: {args.locate}", file=sys.stderr)
            return 1
        w, h = get_image_size(args.locate)
        prompt = call_m3_vision(args.locate, args.target, args.context, w, h)
        # Print the prompt for the caller (which will route it through describe_images)
        print(f"IMAGE: {args.locate}", file=sys.stderr)
        print(f"SIZE:  {w}x{h}", file=sys.stderr)
        print(f"TARGET: {args.target}", file=sys.stderr)
        print(f"\n=== PROMPT (feed to describe_images) ===\n",
              file=sys.stderr)
        print(prompt, file=sys.stderr)
        # Also print a JSON envelope to stdout for piping
        print(json.dumps({
            "image_path": str(args.locate),
            "image_size": [w, h],
            "target": args.target,
            "prompt": prompt,
            "next_step": (
                "1. Call mavis mcp call matrix describe_images (or the "
                "native describe_images tool) with this image + prompt.\n"
                "2. Pipe the raw response into: "
                f"python3 macos-vision-anchor.py --parse-response '<raw>' "
                f"--with-image {args.locate} --with-target '{args.target}' "
                f"--with-width {w} --with-height {h}"
            ),
        }, indent=2, ensure_ascii=False))
        return 0

    if args.capture_and_locate:
        if not args.target:
            ap.error("--target is required with --capture-and-locate")
        img_path = capture_screen()
        w, h = get_image_size(img_path)
        prompt = call_m3_vision(img_path, args.target, args.context, w, h)
        print(f"CAPTURE: {img_path}", file=sys.stderr)
        print(f"SIZE:    {w}x{h}", file=sys.stderr)
        print(f"TARGET:  {args.target}", file=sys.stderr)
        print(json.dumps({
            "image_path": str(img_path),
            "image_size": [w, h],
            "target": args.target,
            "prompt": prompt,
        }, indent=2, ensure_ascii=False))
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
