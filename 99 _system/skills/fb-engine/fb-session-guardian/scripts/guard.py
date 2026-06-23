#!/usr/bin/env python3
"""fb-session-guardian: pre-flight auth check for the Facebook session.

The mechanism: Facebook randomly invalidates session cookies (after idle
periods, security incidents, password changes, and especially after the
user navigates to /login or hits a checkpoint). If a sweep starts logged
out, the GraphQL call returns 401 and the script fails — or worse, a
checkpoint wall appears mid-scrape and the account is locked.

This script is the load-bearing pre-flight that runs BEFORE any
fb-group-reader invocation. Same pattern as x-session-guardian.

The check:
  1. Connect to the user's real Chrome via CDP (auto-detect port)
  2. Read cookies for facebook.com — look for `c_user` AND `xs`
  3. Navigate to https://www.facebook.com/
  4. Read the page title — verify it does NOT contain "Log in" /
     "Create new account" / "Sign up"
  5. Combine the two checks:
     - Both cookies present AND title does not contain a login marker → PASS
     - Either missing cookie OR title contains a login marker → FAIL

On FAIL:
  - Exit code 1
  - The calling cron / pipeline receives the JSON output and HALTs
  - Mavis surfaces a high-priority Telegram ping to Andre

Usage:
    python3 guard.py
    python3 guard.py --cdp-port 58632
    python3 guard.py --cdp-port 58632 --json-only

Output JSON:
    {
      "session_state": "PASS" | "FAIL",
      "cookies_present": {"c_user": true, "xs": true, "fr": true, "datr": true},
      "title_check": "OK" | "LOGIN_REQUIRED",
      "current_url": "https://www.facebook.com/",
      "page_title": "Facebook",
      "cdp_port": 58632,
      "diagnostic": "..."
    }
"""
import argparse
import asyncio
import json
import re
import subprocess
import sys
import time

try:
    from playwright.async_api import async_playwright
except ImportError:
    print(json.dumps({
        "session_state": "FAIL",
        "error": "playwright Python SDK not installed. Run: pip install playwright && playwright install chromium",
    }))
    sys.exit(1)


# ---------- CDP port discovery ----------

def find_cdp_port() -> int | None:
    """Scan Chrome processes for the --remote-debugging-port flag.

    The Playwright MCP launches Chrome with a dynamic port. This helper
    finds it. Only valid ports (N > 0) are returned. The user's real
    Chrome may also be detected — we prefer the one with ms-playwright
    in the path (the MCP's managed Chrome) but fall back to any.
    """
    try:
        result = subprocess.run(
            ["ps", "-axww", "-o", "command"],
            capture_output=True, text=True, timeout=10,
        )
        candidates: list[tuple[bool, int]] = []  # (is_mcp, port)
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
        # Prefer the MCP-managed Chrome; fall back to any valid candidate.
        candidates.sort(key=lambda c: (0 if c[0] else 1, c[1]))
        if candidates:
            return candidates[0][1]
    except Exception:
        pass
    return None


# ---------- Cookie / title check ----------

REQUIRED_COOKIES = {"c_user", "xs"}
LOGIN_MARKERS = (
    "log in",
    "log into",
    "log in or sign up",
    "create new account",
    "sign up for facebook",
    "sign up",
)


async def check_session(cdp_port: int, page_timeout_ms: int = 20000) -> dict:
    """Connect to the user's real Chrome via CDP and verify FB session."""
    result = {
        "session_state": "FAIL",
        "cookies_present": {},
        "title_check": "LOGIN_REQUIRED",
        "current_url": None,
        "page_title": None,
        "cdp_port": cdp_port,
        "diagnostic": "",
        "ts": int(time.time()),
    }

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(f"ws://127.0.0.1:{cdp_port}")
        except Exception as e:
            result["diagnostic"] = f"CDP connect failed: {e}"
            return result

        contexts = browser.contexts
        if not contexts:
            result["diagnostic"] = "no browser context available"
            return result
        context = contexts[0]

        # 1. Cookie check
        try:
            cookies = await context.cookies()
        except Exception as e:
            result["diagnostic"] = f"cookie read failed: {e}"
            return result
        cookie_names = {c["name"] for c in cookies}
        for name in ("c_user", "xs", "fr", "datr", "sb", "presence"):
            result["cookies_present"][name] = name in cookie_names
        missing = REQUIRED_COOKIES - cookie_names
        if missing:
            result["diagnostic"] = f"missing required cookies: {sorted(missing)}"
            return result

        # 2. Title check
        page = context.pages[0] if context.pages else await context.new_page()
        try:
            await page.goto(
                "https://www.facebook.com/",
                wait_until="domcontentloaded",
                timeout=page_timeout_ms,
            )
        except Exception as e:
            result["diagnostic"] = f"navigation failed: {e}"
            return result

        try:
            result["current_url"] = page.url
            result["page_title"] = await page.title()
        except Exception as e:
            result["diagnostic"] = f"page metadata read failed: {e}"
            return result

        title_lower = (result["page_title"] or "").lower()
        if any(marker in title_lower for marker in LOGIN_MARKERS):
            result["title_check"] = "LOGIN_REQUIRED"
            result["diagnostic"] = f"login wall detected (title='{result['page_title']}')"
            return result

        result["title_check"] = "OK"
        result["session_state"] = "PASS"
        result["diagnostic"] = "session authenticated"
        return result


# ---------- Entry point ----------

def main() -> int:
    parser = argparse.ArgumentParser(description="Facebook session guardian (pre-flight)")
    parser.add_argument(
        "--cdp-port", type=int, default=None,
        help="CDP port (default: auto-detect from `ps`)",
    )
    parser.add_argument(
        "--json-only", action="store_true",
        help="Suppress non-JSON output (cron-friendly)",
    )
    args = parser.parse_args()

    cdp_port = args.cdp_port or find_cdp_port()
    if cdp_port is None:
        out = {
            "session_state": "FAIL",
            "diagnostic": "could not find a Chrome --remote-debugging-port. "
                          "Is Chrome running with --remote-debugging-port=N?",
        }
        print(json.dumps(out))
        return 1

    out = asyncio.run(check_session(cdp_port))

    if not args.json_only:
        state = out.get("session_state")
        diag = out.get("diagnostic", "")
        title = out.get("page_title")
        print(f"[fb-session-guardian] {state} (port {cdp_port})", file=sys.stderr)
        if title:
            print(f"  title: {title}", file=sys.stderr)
        if diag:
            print(f"  diagnostic: {diag}", file=sys.stderr)

    print(json.dumps(out))
    return 0 if out.get("session_state") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
