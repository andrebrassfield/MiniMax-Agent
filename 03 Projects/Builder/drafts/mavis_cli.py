#!/usr/bin/env python3
"""mavis_cli.py — frictionless terminal client for the Mavis Harness daemon.

Source: 03 Projects/Mavis/phase_next_architecture.md §5 (CLI bridge)
Status: BUILD 2026-06-07 15:45 CT (Andre-approved design)
Daemon: http://127.0.0.1:11435 (com.mavis.harness LaunchAgent)

What it does
------------
Wraps the harness's HTTP API in a curl-free command-line surface.

  mavis-cli "summarize this"          POST /turn  → stdout
  cat notes.md | mavis-cli            POST /turn  → stdout (stdin body)
  mavis-cli -f a.md -f b.md           POST /turn  → stdout (multi-file concat)
  mavis-cli --health                  GET  /health → stdout
  mavis-cli --stats                   GET  /stats  → stdout (pretty)
  mavis-cli --stats --json            GET  /stats  → stdout (raw JSON)

Design choices (Andre-locked 2026-06-07):
  - Stdlib only. No pip dependencies. Matches the harness's stdlib-only ethos.
  - No REPL. Default mode is "stdin if piped, args if present, error if neither."
    Fast, programmatic, perfect for pipe compatibility.
  - Multi-file concat: each -f file becomes "# File: <name>\n<contents>\n\n".
  - No color. Plain text. Pipe-safe.
  - Default host/port from MAVIS_HARNESS_HOST / MAVIS_HARNESS_PORT env vars,
    fall back to 127.0.0.1:11435.
  - Exit codes: 0 ok, 64 connection refused, 65 harness error, 66 input too large.

Not implemented yet (explicit non-goals):
  - Streaming response (the harness /turn is fire-and-forget; no chunked output).
  - TLS (the daemon binds 127.0.0.1 only; loopback plaintext is fine).
  - Auth (also 127.0.0.1 only; no token).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Daemon endpoint defaults — overridable via env or --host/--port.
DEFAULT_HOST = os.environ.get("MAVIS_HARNESS_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("MAVIS_HARNESS_PORT", "11435"))
DEFAULT_TIMEOUT = 120  # seconds; the 12B QAT cold path is the worst case.
MAX_BODY_BYTES = 1024 * 1024  # mirror the daemon's 1 MB cap on /turn

EXIT_OK = 0
EXIT_USAGE = 64       # connection refused, daemon not running
EXIT_DATA = 65        # harness-side error or malformed payload
EXIT_INPUT_TOO_LARGE = 66


# ---------------------------------------------------------------------------
# HTTP layer — separated so tests can mock the request() function.
# ---------------------------------------------------------------------------


def request(method: str, path: str, body: Optional[Dict[str, Any]] = None,
            host: str = DEFAULT_HOST, port: int = DEFAULT_PORT,
            timeout: int = DEFAULT_TIMEOUT) -> Tuple[int, Dict[str, Any]]:
    """Single low-level HTTP call. Returns (status_code, parsed_json)."""
    url = f"http://{host}:{port}{path}"
    data: Optional[bytes] = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                # The harness always returns JSON; if not, it's a bug.
                return resp.status, {"_raw": raw}
    except urllib.error.HTTPError as exc:
        # 4xx/5xx — body is still JSON, surfacing the harness's error message.
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw) if raw else {"error": exc.reason}
        except json.JSONDecodeError:
            return exc.code, {"error": raw or exc.reason}
    except urllib.error.URLError as exc:
        # Connection refused / DNS / etc. Re-raise as a typed error so the
        # caller can map to a friendly message and the right exit code.
        raise ConnectionError(f"cannot reach {url}: {exc.reason}") from exc


# ---------------------------------------------------------------------------
# Input assembly — args, stdin, files. No REPL.
# ---------------------------------------------------------------------------


def read_stdin() -> str:
    """Read all of stdin until EOF. Returns the decoded text. Empty if no data."""
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read()


def concat_files(paths: List[Path]) -> str:
    """Read each file in order; emit a `# File: <name>` header per file.

    The harness /turn takes a single string, so the multi-file mode is
    client-side concat. The `# File:` header lets the model cite the source
    in its response, and makes the concat auditable in logs.
    """
    if not paths:
        return ""
    parts: List[str] = []
    for p in paths:
        try:
            contents = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"mavis-cli: cannot read {p}: {exc}", file=sys.stderr)
            sys.exit(EXIT_DATA)
        parts.append(f"# File: {p.name}\n{contents}")
    return "\n\n".join(parts) + "\n"


def assemble_input(args: argparse.Namespace) -> Optional[str]:
    """Build the POST /turn `input` string from args, stdin, and -f files.

    Order of precedence (first non-empty wins):
      1. -f files (concat with # File: headers)
      2. piped stdin (only if not a TTY)
      3. positional args (joined with single spaces)
    Returns None if none of those produce input; the caller prints the
    usage error and exits with the appropriate code.
    """
    files_input = concat_files(args.file) if args.file else ""
    if files_input:
        return files_input

    stdin_input = read_stdin()
    if stdin_input:
        return stdin_input

    if args.prompt:
        return " ".join(args.prompt)

    return None


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def cmd_turn(args: argparse.Namespace) -> int:
    """POST /turn and print the response. Plus lane + model in --verbose."""
    input_text = assemble_input(args)
    if input_text is None:
        print(
            "mavis-cli: no input. Provide one of:\n"
            "  positional prompt: mavis-cli \"summarize this\"\n"
            "  piped stdin:       echo \"hello\" | mavis-cli\n"
            "  file(s):          mavis-cli -f notes.md [-f context.md]\n"
            "Or use --health / --stats for daemon introspection.",
            file=sys.stderr,
        )
        return EXIT_USAGE
    if len(input_text.encode("utf-8")) > MAX_BODY_BYTES:
        print(
            f"mavis-cli: input is {len(input_text)} bytes; "
            f"daemon cap is {MAX_BODY_BYTES}. Trim the input.",
            file=sys.stderr,
        )
        return EXIT_INPUT_TOO_LARGE
    try:
        status, payload = request(
            "POST", "/turn",
            body={"input": input_text},
            host=args.host, port=args.port, timeout=args.timeout,
        )
    except ConnectionError as exc:
        print(
            f"mavis-cli: {exc}\n"
            f"         Is the harness daemon running? Try:\n"
            f"           launchctl print gui/$UID/com.mavis.harness",
            file=sys.stderr,
        )
        return EXIT_USAGE
    if status != 200 or "response" not in payload:
        print(
            f"mavis-cli: harness returned {status}: {json.dumps(payload)}",
            file=sys.stderr,
        )
        return EXIT_DATA
    sys.stdout.write(str(payload["response"]))
    if not str(payload["response"]).endswith("\n"):
        sys.stdout.write("\n")
    if args.verbose:
        meta = {k: payload.get(k) for k in ("lane", "model") if k in payload}
        if meta:
            print(f"# {json.dumps(meta)}", file=sys.stderr)
    return EXIT_OK


def cmd_health(args: argparse.Namespace) -> int:
    """GET /health. Pretty-print or raw JSON (--json)."""
    try:
        status, payload = request(
            "GET", "/health",
            host=args.host, port=args.port, timeout=min(args.timeout, 10),
        )
    except ConnectionError as exc:
        print(f"mavis-cli: {exc}", file=sys.stderr)
        return EXIT_USAGE
    if status != 200:
        print(f"mavis-cli: /health returned {status}: {payload}", file=sys.stderr)
        return EXIT_DATA
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return EXIT_OK
    # Plain-text pretty form.
    print(f"status:        {payload.get('status', '?')}")
    print(f"session_id:    {payload.get('session_id', '?')}")
    print(f"uptime_sec:    {payload.get('uptime_seconds', '?')}")
    print(f"bind:          {payload.get('bind', '?')}")
    ollama = payload.get("ollama", {})
    print(f"ollama.url:    {ollama.get('url', '?')}")
    print(f"ollama.up:     {ollama.get('reachable', '?')}")
    print(f"ollama.error:  {ollama.get('error') or '-'}")
    print(f"chat_model:    {ollama.get('chat_model', '?')}")
    print(f"fast_model:    {ollama.get('fast_model', '?')}")
    return EXIT_OK


def cmd_stats(args: argparse.Namespace) -> int:
    """GET /stats. Pretty-print or raw JSON (--json)."""
    try:
        status, payload = request(
            "GET", "/stats",
            host=args.host, port=args.port, timeout=min(args.timeout, 10),
        )
    except ConnectionError as exc:
        print(f"mavis-cli: {exc}", file=sys.stderr)
        return EXIT_USAGE
    if status != 200:
        print(f"mavis-cli: /stats returned {status}: {payload}", file=sys.stderr)
        return EXIT_DATA
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return EXIT_OK
    # Plain-text pretty form — just the headline numbers.
    print(f"session_id:    {payload.get('session_id', '?')}")
    print(f"drift_score:   {payload.get('drift_score', '?')}")
    r = payload.get("router", {})
    print(f"router.classifications:  {r.get('total_classifications', '?')}")
    print(f"router.fallback_count:   {r.get('fallback_count', '?')}")
    print(f"router.lane_distribution: {r.get('lane_distribution', '?')}")
    l = payload.get("loader", {})
    print(f"loader.hits/misses:      {l.get('hits', '?')}/{l.get('misses', '?')}")
    s = payload.get("safety", {})
    print(f"safety.path_traversal_blocked: {s.get('path_traversal_attempts_blocked', '?')}")
    c = payload.get("cost", {})
    print(f"cost.events:        {c.get('event_count', '?')}")
    print(f"cost.actual_usd:    {c.get('total_actual_cost', '?')}")
    print(f"cost.planned_usd:   {c.get('total_planned_cost', '?')}")
    print(f"ollama.calls:       {payload.get('ollama_call_count', '?')}")
    print(f"ollama.fallbacks:   {payload.get('ollama_fallback_count', '?')}")
    return EXIT_OK


# ---------------------------------------------------------------------------
# argparse wiring
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mavis-cli",
        description=(
            "Frictionless terminal client for the Mavis Harness daemon "
            "(http://127.0.0.1:11435). POST /turn is the default action; "
            "--health and --stats are daemon introspection."
        ),
    )
    p.add_argument("--host", default=DEFAULT_HOST,
                   help=f"daemon host (default: {DEFAULT_HOST}, "
                        f"env: MAVIS_HARNESS_HOST)")
    p.add_argument("--port", type=int, default=DEFAULT_PORT,
                   help=f"daemon port (default: {DEFAULT_PORT}, "
                        f"env: MAVIS_HARNESS_PORT)")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                   help=f"request timeout in seconds (default: {DEFAULT_TIMEOUT})")
    p.add_argument("--verbose", action="store_true",
                   help="print lane + model metadata to stderr after the response")
    p.add_argument("--json", action="store_true",
                   help="(with --health / --stats) emit raw JSON instead of pretty text")

    # Subcommand-style flags. The default action is "turn" if neither
    # --health nor --stats is given. No argparse subparsers — keeps the
    # surface to a flat list of mutually compatible flags.
    p.add_argument("--health", action="store_true",
                   help="GET /health instead of POST /turn")
    p.add_argument("--stats", action="store_true",
                   help="GET /stats instead of POST /turn")

    # /turn-specific (ignored for --health/--stats).
    p.add_argument("-f", "--file", action="append", type=Path, default=[],
                   help="read input from this file; can be repeated for multi-file concat")
    p.add_argument("prompt", nargs="*",
                   help="positional prompt (joined with spaces). "
                        "Ignored if -f or piped stdin is provided.")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.health:
        return cmd_health(args)
    if args.stats:
        return cmd_stats(args)
    return cmd_turn(args)


if __name__ == "__main__":
    sys.exit(main())
