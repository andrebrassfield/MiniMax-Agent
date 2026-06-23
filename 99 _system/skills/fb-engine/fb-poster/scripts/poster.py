#!/usr/bin/env python3
"""fb-poster: publish approved FB-Engine drafts to Facebook via CDP.

The mechanism: read `03 Projects/FB-Engine/approved/` for files with
`status: approved`, navigate to the target (Group URL for Typology 1,
post URL for Typology 2), find the composer / comment input via
semantic locators, paste the approved text using `page.fill()` (NOT
`page.type()` — same React-controlled input duplication issue as
`x-publish`), HALT for human verification by default, then click
Post and capture the post URL.

Hard Rule: HALT immediately if the draft is not in `approved/`. The
Poster NEVER reads from `drafts/` (open) — only `approved/`. This is
the safety gate.

Output: post URL captured; draft moved to
`03 Projects/FB-Engine/archive/published/`.

Usage:
    # Default: process the next approved draft, HALT before clicking Post
    python3 poster.py

    # Process a specific draft
    python3 poster.py --draft "2026-06-18-1330-t2-post-1234567890.md"

    # Process all approved drafts in one run
    python3 poster.py --all

    # Fully-automated: skip the HALT
    python3 poster.py --no-halt

    # Custom paths
    python3 poster.py --approved-dir /path/to/approved/

The default HALT is a stdin-based pause: the script pastes the text,
prints a message, waits for Enter, then clicks Post. Press Ctrl+C to
abort. The `--no-halt` flag skips this (use with care; the draft was
already operator-approved via Telegram, so the only check this HALT
adds is "the text looks right in the live UI before it's sent").
"""
import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    print(json.dumps({
        "error": "playwright Python SDK not installed. Run: pip install playwright && playwright install chromium",
    }))
    sys.exit(1)


# ---------- Paths ----------

DEFAULT_VAULT = Path.home() / "MiniMax-Agent"
DEFAULT_APPROVED = DEFAULT_VAULT / "03 Projects" / "FB-Engine" / "approved"
DEFAULT_PUBLISHED = DEFAULT_VAULT / "03 Projects" / "FB-Engine" / "archive" / "published"
DEFAULT_PUBLISH_LEDGER = DEFAULT_VAULT / "03 Projects" / "FB-Engine" / "queue" / "drafts-published.mdl"

CDP_DEFAULT = "ws://localhost:58632"


# ---------- CDP port discovery ----------

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


# ---------- Draft parsing ----------

def parse_draft(path: Path) -> dict[str, Any] | None:
    """Parse the YAML frontmatter of an approved draft. Returns dict or None."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fm = text[3:end].strip()
    result: dict[str, Any] = {}
    for line in fm.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        result[k.strip()] = v.strip().strip('"')
    return result


def extract_body(path: Path) -> str:
    """Extract the text under '## Generated draft' (or '## Edited draft')."""
    text = path.read_text(encoding="utf-8")
    for header in ("## Generated draft", "## Edited draft"):
        m = re.search(rf"{re.escape(header)}\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
        if m:
            return m.group(1).strip()
    return ""


# ---------- Posting mechanics ----------

async def _get_or_create_context(browser: Browser) -> BrowserContext:
    contexts = browser.contexts
    if contexts:
        return contexts[0]
    return await browser.new_context()


async def post_to_facebook(
    browser: Browser,
    target_url: str,
    text: str,
    typology: str,
    halt: bool,
    timeout_ms: int = 30000,
) -> dict[str, Any]:
    """Navigate, fill the composer/comment input, halt, click Post, capture URL."""
    result: dict[str, Any] = {
        "target_url": target_url,
        "typology": typology,
        "text_chars": len(text),
        "staged": False,
        "submitted": False,
        "post_url": None,
        "error": None,
    }

    context = await _get_or_create_context(browser)
    page = context.pages[0] if context.pages else await context.new_page()

    # 1. Navigate
    try:
        await page.goto(target_url, wait_until="domcontentloaded", timeout=timeout_ms)
    except Exception as e:
        result["error"] = f"navigation failed: {e}"
        return result

    # 2. Wait for the composer / comment input
    try:
        # The composer / comment input is a [contenteditable] div.
        # Multiple may exist (e.g., main composer + reply composers on each post).
        # For T1 (original post): the Group's main composer at the top of the feed.
        # For T2 (reply): the comment input below the specific post.
        # We pick the first visible, enabled [contenteditable] on the page.
        await page.wait_for_selector(
            '[contenteditable="true"]',
            state="visible",
            timeout=15000,
        )
    except Exception as e:
        result["error"] = f"composer / comment input not found: {e}"
        return result

    # 3. Find the right input
    # For T1: the first contenteditable on the page is usually the main composer.
    # For T2: we want the comment input below the post. The page may have multiple;
    # we use the LAST visible one (which is usually the post's comment input).
    composers = page.locator('[contenteditable="true"]')
    count = await composers.count()
    if count == 0:
        result["error"] = "no contenteditable elements on page"
        return result
    if typology == "T1":
        composer = composers.first
    else:
        # For replies, prefer the last visible composer (post's comment input)
        composer = composers.last

    # 4. Click to focus, then fill the text
    try:
        await composer.click(timeout=5000)
    except Exception as e:
        result["error"] = f"could not click composer: {e}"
        return result

    # Use page.fill() for contentEditable. This sets the value directly
    # without firing keyboard events, which avoids the React-controlled
    # input duplication bug (same fix as x-publish for X).
    try:
        await composer.fill(text, timeout=10000)
        result["staged"] = True
    except Exception as e:
        result["error"] = f"could not fill composer: {e}"
        return result

    # 5. Verify the staged text (programmatic, not visual)
    try:
        staged_text = await composer.inner_text()
        if staged_text.strip() != text.strip():
            # Sometimes contentEditable adds trailing newline; tolerate that
            if staged_text.strip() + "\n" != text.strip() and text.strip() + "\n" != staged_text.strip():
                result["error"] = (
                    f"staged text mismatch: "
                    f"expected {len(text)} chars, got {len(staged_text)} chars"
                )
                return result
    except Exception as e:
        result["error"] = f"could not verify staged text: {e}"
        return result

    # 6. HALT for human verification (default)
    if halt:
        print(
            f"\n[fb-poster] HALT: draft staged in the live Chrome.\n"
            f"  Target: {target_url}\n"
            f"  Typology: {typology}\n"
            f"  Text length: {len(text)} chars\n"
            f"  First 80 chars: {text[:80]!r}{'...' if len(text) > 80 else ''}\n"
            f"\n"
            f"  Verify the text in the live Chrome composer.\n"
            f"  Press Enter to click Post, or Ctrl+C to abort.\n",
            file=sys.stderr,
            flush=True,
        )
        try:
            input()
        except (KeyboardInterrupt, EOFError):
            result["error"] = "aborted at HALT"
            return result

    # 7. Find and click the Post button
    try:
        # Try a few semantic locator patterns (FB's button text varies)
        post_button = None
        for button_text in ("Post", "Share", "Send", "Comment", "Reply"):
            loc = page.get_by_role("button", name=button_text, exact=False)
            if await loc.count() > 0:
                # Filter to visible, enabled buttons only
                for i in range(await loc.count()):
                    btn = loc.nth(i)
                    if await btn.is_visible() and await btn.is_enabled():
                        post_button = btn
                        break
                if post_button:
                    break
        if post_button is None:
            result["error"] = "no Post / Share / Comment button found"
            return result
        await post_button.click(timeout=5000)
    except Exception as e:
        result["error"] = f"could not click Post: {e}"
        return result

    # 8. Wait for the post to land and capture the URL
    result["submitted"] = True
    try:
        await page.wait_for_timeout(3000)  # let FB complete the post
        result["post_url"] = page.url
    except Exception as e:
        result["error"] = f"could not capture post URL: {e}"

    return result


def archive_published(published_dir: Path, source: Path) -> Path:
    """Move the draft to archive/published/, update frontmatter status."""
    published_dir.mkdir(parents=True, exist_ok=True)
    dest = published_dir / source.name
    text = source.read_text(encoding="utf-8")
    # Update frontmatter
    text = re.sub(r"^status:\s*approved\s*$", "status: published", text, flags=re.MULTILINE)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if "published_at:" in text:
        text = re.sub(r"^published_at:.*$", f"published_at: {ts}", text, flags=re.MULTILINE)
    else:
        text = text.replace("status: published\n", f"status: published\npublished_at: {ts}\n", 1)
    dest.write_text(text, encoding="utf-8")
    source.unlink()
    return dest


def append_publish_ledger(ledger: Path, source: Path, post_url: str, typology: str) -> None:
    """Append a one-line entry to the publish ledger."""
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M CT")
    line = f"- {ts} — {source.name} → {post_url} | T{typology[-1]} | fb.com"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ---------- Entry point ----------

def list_approved(approved_dir: Path) -> list[Path]:
    if not approved_dir.exists():
        return []
    out: list[Path] = []
    for p in sorted(approved_dir.glob("*.md")):
        if not p.is_file():
            continue
        fm = parse_draft(p)
        if not fm:
            continue
        if fm.get("status") == "approved":
            out.append(p)
    return out


async def process_one(
    cdp_url: str,
    draft_path: Path,
    published_dir: Path,
    publish_ledger: Path,
    halt: bool,
) -> int:
    fm = parse_draft(draft_path)
    if not fm:
        print(f"ERROR: could not parse frontmatter in {draft_path}", file=sys.stderr)
        return 1
    if fm.get("status") != "approved":
        # SAFETY GATE: HALT if not in approved/
        print(
            f"FATAL: draft {draft_path.name} is not in 'approved/' state (status={fm.get('status')}).\n"
            f"  Per the safety gate, the Poster HALTs immediately.\n"
            f"  Move the draft to 03 Projects/FB-Engine/approved/ first.",
            file=sys.stderr,
        )
        return 2

    target_url = fm.get("target_url") or fm.get("group_url") or fm.get("post_url") or fm.get("original_url")
    typology = fm.get("typology", "T2")
    text = extract_body(draft_path)
    if not text:
        print(f"ERROR: no body extracted from {draft_path}", file=sys.stderr)
        return 1
    if not target_url:
        print(f"ERROR: no target URL in frontmatter of {draft_path}", file=sys.stderr)
        return 1

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            print(f"ERROR: CDP connect failed at {cdp_url}: {e}", file=sys.stderr)
            return 1

        result = await post_to_facebook(browser, target_url, text, typology, halt=halt)

    print(f"[fb-poster] {draft_path.name}: {json.dumps(result, ensure_ascii=False)}")

    if result.get("error"):
        print(f"ERROR during post: {result['error']}", file=sys.stderr)
        return 1

    if result.get("submitted") and result.get("post_url"):
        # Archive the published draft
        archive_dest = archive_published(published_dir, draft_path)
        append_publish_ledger(publish_ledger, archive_dest, result["post_url"], typology)
        print(f"[fb-poster] archived → {archive_dest}", file=sys.stderr)
        return 0

    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="FB-Engine Poster (CDP-driven, gated on approved/)")
    parser.add_argument("--approved-dir", type=Path, default=DEFAULT_APPROVED)
    parser.add_argument("--published-dir", type=Path, default=DEFAULT_PUBLISHED)
    parser.add_argument("--publish-ledger", type=Path, default=DEFAULT_PUBLISH_LEDGER)
    parser.add_argument("--cdp-url", default=CDP_DEFAULT,
                        help=f"CDP bridge URL (default: {CDP_DEFAULT})")
    parser.add_argument("--cdp-port", type=int, default=None,
                        help="CDP port (overrides --cdp-url; default: auto-detect from `ps`)")
    parser.add_argument("--draft", type=str, default=None,
                        help="Process a specific draft filename (default: next in approved/)")
    parser.add_argument("--all", action="store_true",
                        help="Process all approved drafts in one run")
    parser.add_argument("--max-posts", type=int, default=1,
                        help="Max drafts to process in this run (default: 1)")
    parser.add_argument("--no-halt", action="store_true",
                        help="Skip the HALT between fill and click (fully-automated)")
    args = parser.parse_args()

    cdp_url = args.cdp_url
    if args.cdp_port:
        cdp_url = f"ws://127.0.0.1:{args.cdp_port}"
    else:
        port = find_cdp_port()
        if port:
            cdp_url = f"ws://127.0.0.1:{port}"

    approved = list_approved(args.approved_dir)
    if not approved:
        print(f"[fb-poster] no approved drafts in {args.approved_dir}", file=sys.stderr)
        return 0

    if args.draft:
        # Process a specific draft
        target = next((p for p in approved if p.name == args.draft), None)
        if not target:
            print(f"ERROR: draft {args.draft} not found in approved/", file=sys.stderr)
            return 1
        approved = [target]
    elif not args.all:
        approved = approved[:1]  # default: one at a time
    else:
        approved = approved[: args.max_posts]

    halt = not args.no_halt
    rc = 0
    for draft in approved:
        result = asyncio.run(process_one(
            cdp_url=cdp_url,
            draft_path=draft,
            published_dir=args.published_dir,
            publish_ledger=args.publish_ledger,
            halt=halt,
        ))
        if result != 0:
            rc = result
            break
    return rc


if __name__ == "__main__":
    import asyncio
    sys.exit(main())
