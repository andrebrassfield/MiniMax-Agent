#!/usr/bin/env python3
"""fb-group-reader: read recent posts from a Facebook Group via real Chrome.

The mechanism: connect to the user's real Chrome via CDP (auto-detect
port), navigate to a Group URL the user is a member of, register
`page.on("response")` BEFORE navigation, capture every response matching
`/api/graphql/`, parse the JSON, and extract post records by heuristic
(post_id + message text present in the same nested object).

This is the FB analog of x-graphql-interceptor. Same interception
mechanism, different GraphQL endpoint, different parser.

Facebook's Group feed GraphQL endpoint:
  /api/graphql/  (with a query hash in the path)

The response body is deeply nested JSON. Post records appear as nodes
with both a numeric `post_id` and a `message` (or `text`) field. The
parser walks the tree and collects these nodes, keyed by post_id to
deduplicate across multiple intercepted responses (FB fires the same
feed query several times as the user scrolls).

This is READ-ONLY. The script does not click reply / post / like /
share. The user pastes and posts manually after reviewing the extracted
data. The mirror skill fb-draft-scribe (next) will read this JSON to
draft typology-1 + typology-2 content for human approval.

Usage:
    python3 read.py \
        --group "https://www.facebook.com/groups/<slug>" \
        --output /tmp/fb-group-posts.json

    # With explicit CDP port + tighter post cap
    python3 read.py --group "<url>" --output /tmp/posts.json \
        --cdp-port 58632 --max-posts 25 --scroll-passes 2 --scroll-wait 4

Output JSON schema:
    {
      "scan_time": "2026-06-18T12:30:00Z",
      "scan_method": "Playwright SDK page.on('response') over CDP",
      "cdp_port": 58632,
      "group_url": "https://www.facebook.com/groups/<slug>",
      "graphql_responses_captured": 7,
      "results": [
        {
          "post_id": "123456789012345",
          "author": "Jane Smith",
          "text": "Post text content...",
          "timestamp": 1718712000,
          "fetched_at": 1718712345,
          "source_query": "GroupFeedQuery"  // best-effort, may be null
        }
      ],
      "errors": []
    }
"""
import argparse
import asyncio
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

try:
    from playwright.async_api import async_playwright, Response
except ImportError:
    print(json.dumps({
        "error": "playwright Python SDK not installed. Run: pip install playwright && playwright install chromium",
        "results": [],
    }))
    sys.exit(1)


# ---------- CDP port discovery (mirror of guard.py) ----------

def find_cdp_port() -> int | None:
    try:
        result = subprocess.run(
            ["ps", "-axww", "-o", "command"],
            capture_output=True, text=True, timeout=10,
        )
        candidates: list[tuple[bool, int]] = []
        for line in result.stdout.split("\n"):
            if "Google Chrome" not in line and "chrome" not in line.lower():
                continue
            if "headless" in line.lower():
                continue
            match = re.search(r"--remote-debugging-port=(\d+)", line)
            if not match:
                continue
            port = int(match.group(1))
            if port <= 0:
                continue
            is_mcp = "ms-playwright" in line
            candidates.append((is_mcp, port))
        candidates.sort(key=lambda c: (0 if c[0] else 1, c[1]))
        if candidates:
            return candidates[0][1]
    except Exception:
        pass
    return None


# ---------- Response parsing ----------

# Facebook post / story / feedback IDs are 10-20 digit numbers.
ID_PATTERN = re.compile(r"\d{10,20}")

# Possible fields that hold the post text. FB's response shape varies
# across deploys; we look in all the common spots.
TEXT_FIELDS = ("message", "text", "story", "description", "title", "body")

# Possible fields for author / actor name.
ACTOR_FIELDS = ("name", "short_name", "username", "title")

# Possible fields for the post timestamp.
TS_FIELDS = ("timestamp", "creation_time", "published_time", "time")


def _walk(obj: Any, depth: int = 0) -> Any:
    if depth > 35:
        return None
    return obj


def _first_str(node: dict, fields: tuple[str, ...]) -> str | None:
    for f in fields:
        v = node.get(f)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _get_text(node: Any) -> str | None:
    """Best-effort extraction of post message text from a feed unit."""
    if not isinstance(node, dict):
        return None
    direct = _first_str(node, TEXT_FIELDS)
    if direct:
        return direct
    # Nested message containers FB commonly uses.
    for container in ("comet_sections", "feedback", "attachments", "story", "media", "title"):
        nested = node.get(container)
        if isinstance(nested, dict):
            inner = _first_str(nested, TEXT_FIELDS)
            if inner:
                return inner
            # Comet sections wraps message in { message: { text: "..." } }
            msg = nested.get("message")
            if isinstance(msg, dict):
                t = _first_str(msg, TEXT_FIELDS)
                if t:
                    return t
            # Story metadata structure
            story_msg = nested.get("message")
            if isinstance(story_msg, dict):
                t = _first_str(story_msg, TEXT_FIELDS)
                if t:
                    return t
    return None


def _get_author(node: Any) -> str | None:
    if not isinstance(node, dict):
        return None
    for actor_key in ("actor", "owner", "author", "poster", "from"):
        actor = node.get(actor_key)
        if isinstance(actor, dict):
            name = _first_str(actor, ACTOR_FIELDS)
            if name:
                return name
    return None


def _get_post_id(node: Any) -> str | None:
    if not isinstance(node, dict):
        return None
    for key in ("post_id", "id", "story_id", "feedback_id", "node_id", "ufi_id"):
        v = node.get(key)
        if isinstance(v, str) and ID_PATTERN.search(v):
            return v
        if isinstance(v, (int, float)) and ID_PATTERN.search(str(int(v))):
            return str(int(v))
    return None


def _get_timestamp(node: Any) -> int | None:
    if not isinstance(node, dict):
        return None
    for key in TS_FIELDS:
        v = node.get(key)
        if isinstance(v, (int, float)) and v > 1_000_000_000:
            return int(v)
        if isinstance(v, dict):
            for inner_key in ("time", "timestamp", "value"):
                iv = v.get(inner_key)
                if isinstance(iv, (int, float)) and iv > 1_000_000_000:
                    return int(iv)
    return None


def _extract_query_name(url: str) -> str | None:
    """Best-effort: pull the GraphQL query name from the URL path."""
    # FB URLs look like: /api/graphql/?q=<name> or /api/graphql/<hash>/<name>
    m = re.search(r"[?&]q=([^&]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"/api/graphql/[^/]+/([^?&/]+)", url)
    if m:
        return m.group(1)
    return None


def walk_for_posts(
    node: Any,
    posts: dict[str, dict],
    query_name: str | None,
    depth: int = 0,
) -> None:
    """Walk a JSON tree and collect post records keyed by post_id."""
    if depth > 35:
        return
    if isinstance(node, dict):
        pid = _get_post_id(node)
        text = _get_text(node)
        if pid and text and pid not in posts:
            posts[pid] = {
                "post_id": pid,
                "author": _get_author(node) or "unknown",
                "text": text,
                "timestamp": _get_timestamp(node),
                "fetched_at": int(time.time()),
                "source_query": query_name,
            }
        for v in node.values():
            walk_for_posts(v, posts, query_name, depth + 1)
    elif isinstance(node, list):
        for v in node:
            walk_for_posts(v, posts, query_name, depth + 1)


# ---------- Main read loop ----------

async def read_group(
    cdp_port: int,
    group_url: str,
    output_path: str,
    max_posts: int,
    scroll_passes: int,
    scroll_wait: float,
    page_timeout_ms: int,
) -> dict:
    result: dict = {
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "scan_method": "Playwright SDK page.on('response') over CDP",
        "cdp_port": cdp_port,
        "group_url": group_url,
        "graphql_responses_captured": 0,
        "results": [],
        "errors": [],
    }

    captured: list[tuple[bytes, str]] = []  # (body, url)

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(f"ws://127.0.0.1:{cdp_port}")
        except Exception as e:
            result["errors"].append(f"CDP connect failed: {e}")
            return result

        contexts = browser.contexts
        if not contexts:
            result["errors"].append("no browser context available")
            return result
        context = contexts[0]
        page = context.pages[0] if context.pages else await context.new_page()

        # CRITICAL: register listener BEFORE navigation.
        async def on_response(response: Response) -> None:
            try:
                url = response.url
                if "/api/graphql/" not in url:
                    return
                try:
                    body = await response.body()
                except Exception:
                    return
                captured.append((body, url))
            except Exception:
                return

        page.on("response", on_response)

        # 1. Navigate
        try:
            await page.goto(
                group_url,
                wait_until="domcontentloaded",
                timeout=page_timeout_ms,
            )
        except Exception as e:
            result["errors"].append(f"navigation failed: {e}")
            page.remove_listener("response", on_response)
            return result

        # 2. Initial settle wait (the feed renders + GraphQL fires)
        await page.wait_for_timeout(int(scroll_wait * 1000))

        # 3. Scroll N times to capture more posts
        for i in range(scroll_passes):
            try:
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
            except Exception as e:
                result["errors"].append(f"scroll {i + 1} failed: {e}")
            await page.wait_for_timeout(int(scroll_wait * 1000))

        # 4. Detach listener
        page.remove_listener("response", on_response)

    # 5. Process captured responses
    posts: dict[str, dict] = {}
    for body, url in captured:
        try:
            text = body.decode("utf-8", errors="replace")
        except Exception:
            continue
        # Facebook sometimes prefixes responses with "for (;;);" (JSON
        # hijacking defense). Handle multi-line JSON bodies too.
        for line in text.splitlines():
            line = line.strip()
            if not line or not (line.startswith("{") or line.startswith("[")):
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            walk_for_posts(data, posts, _extract_query_name(url))

    result["graphql_responses_captured"] = len(captured)

    # Sort by timestamp desc if available; stable for posts without ts.
    sorted_posts = sorted(
        posts.values(),
        key=lambda r: (r.get("timestamp") or 0, r.get("post_id") or ""),
        reverse=True,
    )[:max_posts]
    result["results"] = sorted_posts

    # 6. Write output
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception as e:
        result["errors"].append(f"output write failed: {e}")

    return result


# ---------- Entry point ----------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read Facebook Group posts via real Chrome (CDP interception)"
    )
    parser.add_argument("--group", required=True, help="Facebook Group URL")
    parser.add_argument("--output", required=True, help="Output JSON file path")
    parser.add_argument(
        "--cdp-port", type=int, default=None,
        help="CDP port (default: auto-detect from `ps`)",
    )
    parser.add_argument("--max-posts", type=int, default=25,
                        help="Max posts to keep (default: 25)")
    parser.add_argument("--scroll-passes", type=int, default=2,
                        help="Number of scroll passes (default: 2)")
    parser.add_argument("--scroll-wait", type=float, default=4.0,
                        help="Seconds to wait after each scroll (default: 4.0)")
    parser.add_argument("--page-timeout-ms", type=int, default=45000,
                        help="Navigation timeout in ms (default: 45000)")
    args = parser.parse_args()

    cdp_port = args.cdp_port or find_cdp_port()
    if cdp_port is None:
        out = {
            "error": "could not find a Chrome --remote-debugging-port. "
                     "Is Chrome running with --remote-debugging-port=N?",
            "results": [],
        }
        print(json.dumps(out))
        return 1

    out = asyncio.run(read_group(
        cdp_port=cdp_port,
        group_url=args.group,
        output_path=args.output,
        max_posts=args.max_posts,
        scroll_passes=args.scroll_passes,
        scroll_wait=args.scroll_wait,
        page_timeout_ms=args.page_timeout_ms,
    ))

    n_posts = len(out.get("results", []))
    n_resp = out.get("graphql_responses_captured", 0)
    errs = out.get("errors", [])
    print(
        f"[fb-group-reader] captured={n_resp} posts={n_posts} errors={len(errs)} → {args.output}",
        file=sys.stderr,
    )
    for e in errs:
        print(f"  ! {e}", file=sys.stderr)

    print(json.dumps(out))
    return 0 if n_posts > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
