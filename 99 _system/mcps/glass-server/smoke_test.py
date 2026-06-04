#!/usr/bin/env python3
"""
smoke_test.py — Render-and-curl smoke test for the Obsidian Glass Server.

Per the instinct `2026-06-03-001-html-render-and-curl-verification-is-required`,
any change to glass_server.py or its templates MUST pass this script
before a `git commit` is allowed.

Behavior:
  1. Locate or create the venv at <this_dir>/.venv.
  2. Start the server in the background on a free port (or --port).
  3. curl -I each touched route; assert HTTP 200.
  4. curl -s each touched route; assert a key content fragment is present.
  5. Kill the server. Print pass/fail report. Exit non-zero on any failure.

Usage:
  python3 smoke_test.py                              # default route set
  python3 smoke_test.py --port 8766                 # alternate port
  python3 smoke_test.py --route /manifesto --route /crucible  # custom routes

Exit codes:
  0  all checks passed
  1  one or more HTTP status / content checks failed
  2  the server failed to start within the timeout
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VAULT_ROOT = SCRIPT_DIR.parent.parent.parent
VENV_PY = SCRIPT_DIR / ".venv" / "bin" / "python3"
SERVER_PY = SCRIPT_DIR / "glass_server.py"
REQUIREMENTS = SCRIPT_DIR / "requirements.txt"

# Default route set. Each entry: (path, status_expected, content_fragment).
# Add routes here as the Glass server gains new pages.
DEFAULT_ROUTES = [
    ("/", 200, "Fleet Command HUD"),
    ("/fleet", 200, "Fleet Command HUD"),
    ("/mycelial", 200, "Mycelial"),
    ("/crucible", 200, "Crucible"),
    ("/manifesto", 200, "Omni-Operator"),
]


def _pick_free_port(preferred: int) -> int:
    """If preferred is free, use it. Otherwise pick a random free one."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _ensure_venv() -> Path:
    """Make sure the venv exists and has markdown + Pygments installed."""
    if not VENV_PY.exists():
        print(f"[smoke] creating venv at {VENV_PY.parent}", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_PY.parent)])
    # Idempotent dep install
    try:
        subprocess.check_call(
            [str(VENV_PY), "-c", "import markdown, pygments"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print("[smoke] installing markdown + Pygments into venv", file=sys.stderr)
        subprocess.check_call(
            [str(VENV_PY), "-m", "pip", "install"] + (
                ["-r", str(REQUIREMENTS)] if REQUIREMENTS.exists() else ["markdown", "Pygments"]
            )
        )
    return VENV_PY


def _wait_for_server(port: int, timeout_s: float = 8.0) -> bool:
    """Poll the server's port until it accepts a TCP connection."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def _http_head(url: str, timeout_s: float = 5.0) -> int:
    """Return the HTTP status code for a HEAD/GET request."""
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def _http_body(url: str, timeout_s: float = 5.0) -> str:
    """Return the response body (UTF-8 text, errors='replace')."""
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Glass server render-and-curl smoke test"
    )
    ap.add_argument(
        "--port", type=int, default=8765,
        help="Preferred port (will pick another if busy; default: 8765)",
    )
    ap.add_argument(
        "--route", action="append", default=[],
        help="Add a route in the form PATH[:EXPECTED_FRAGMENT]. Repeatable. "
             "Default fragment if omitted: 'Glass'.",
    )
    ap.add_argument(
        "--timeout", type=float, default=8.0,
        help="Seconds to wait for server startup (default: 8)",
    )
    args = ap.parse_args()

    # Resolve routes
    if args.route:
        routes = []
        for spec in args.route:
            if ":" in spec:
                path, frag = spec.split(":", 1)
            else:
                path, frag = spec, "Glass"
            routes.append((path, 200, frag))
    else:
        routes = DEFAULT_ROUTES

    # Ensure venv
    py = _ensure_venv()

    # Pick a free port
    port = _pick_free_port(args.port)
    print(f"[smoke] using port {port}", file=sys.stderr)

    # Start the server
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SCRIPT_DIR)
    log_path = Path("/tmp/glass-smoke.log")
    log_fh = log_path.open("w")
    proc = subprocess.Popen(
        [str(py), str(SERVER_PY), "--port", str(port)],
        cwd=str(VAULT_ROOT),
        env=env,
        stdout=log_fh,
        stderr=subprocess.STDOUT,
    )
    try:
        if not _wait_for_server(port, timeout_s=args.timeout):
            print(f"[smoke] server failed to start within {args.timeout}s", file=sys.stderr)
            print(f"[smoke] log: {log_path}", file=sys.stderr)
            return 2

        # Run the checks
        passed = 0
        failed = 0
        for path, expected_status, fragment in routes:
            url = f"http://127.0.0.1:{port}{path}"
            status = _http_head(url)
            status_ok = status == expected_status
            body_ok = True
            body_excerpt = ""
            if status_ok:
                body = _http_body(url)
                body_ok = fragment in body
                body_excerpt = body[:60].replace("\n", " ") if body else "(empty)"

            if status_ok and body_ok:
                passed += 1
                print(f"  PASS  {path:20s}  HTTP {status}  contains {fragment!r}")
            else:
                failed += 1
                reason = (
                    f"status {status} != {expected_status}" if not status_ok
                    else f"body missing {fragment!r}"
                )
                print(f"  FAIL  {path:20s}  {reason}  excerpt={body_excerpt!r}")

        print()
        print(f"[smoke] {passed} passed, {failed} failed (out of {len(routes)})")
        return 0 if failed == 0 else 1
    finally:
        # Clean up
        try:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        log_fh.close()


if __name__ == "__main__":
    sys.exit(main())
