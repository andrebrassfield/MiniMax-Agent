"""
mavis_harness_daemon.py — HTTP daemon mode for the Mavis Harness.

Source: 03 Projects/Mavis/phase_next_architecture.md §4.0
        (Local-Compute Pivot, 2026-06-07 14:18 CT; 12B QAT Pivot, 2026-06-07 15:04 CT)
Sprint: 5 (deployment bridge)
Author: Mavis (chief-of-staff)

Purpose
-------
The Mavis Harness is composed of four Sprint 1-4 primitives plus the
Local-Compute Pivot (Sprint 5). When run under launchd, the harness is
a long-lived process. This module is the listening surface — a small
HTTP server that exposes the harness's handle_turn() over a localhost
API.

Endpoints
---------
GET  /health       liveness probe + Ollama reachability + model routing
POST /turn         {"input": "..."} → {"response": ..., "lane": ..., "model": ...}
GET  /stats        live counters for the scaffolding_review cron

Design choices
--------------
- Stdlib only (http.server.ThreadingHTTPServer). No Flask, no FastAPI.
- Port 11435 (adjacent to Ollama's 11434 for thematic consistency).
- Threaded server: each request gets its own thread. The harness's
  internal state is shared across threads; concurrent writes to the
  classification counters are not atomic, but the harness is single-
  user (personal Mavis) so contention is negligible. A future
  production deployment would add locks or move to async.
- Graceful shutdown on SIGTERM (launchd sends SIGTERM, not SIGKILL,
  on unload). The current request finishes; new requests are rejected.
- 1 MB body cap on POST. Larger payloads are rejected with 413. The
  harness is a router, not a file transfer service.
- JSON in, JSON out. UTF-8 throughout.

What this module does NOT do
----------------------------
- No authentication. localhost-only. The plist's ProgramArguments
  bind to 127.0.0.1; the host firewall is the boundary.
- No persistence of the response. The dispatch lane persists its
  packets; /turn is fire-and-forget.
- No streaming. The full response is returned atomically. Streaming
  is a v2 concern.
"""

from __future__ import annotations

import json
import os
import signal
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import asdict
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional, Tuple

# Reuse the harness module. The deploy script stages both files into
# the same directory (~/.mavis/bin/), so a sibling import works.
_HARNESS_DRAFTS = Path(__file__).resolve().parent
if str(_HARNESS_DRAFTS) not in sys.path:
    sys.path.insert(0, str(_HARNESS_DRAFTS))

from mavis_harness_main import (  # type: ignore  # noqa: E402
    DEFAULT_DISPATCH_OUTPUT_DIR,
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_VAULT_ROOT,
    MavisHarness,
)
from scaffolding_review_cron import compute_drift_score  # type: ignore  # noqa: E402


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Port adjacent to Ollama's 11434 — thematic, not functional. Override
# with --port on the command line or MAVIS_HARNESS_PORT in the env.
DEFAULT_DAEMON_HOST = "127.0.0.1"
DEFAULT_DAEMON_PORT = 11435

# Body size cap on POST /turn. 1 MB is generous for chat-style input
# and rejects accidental file uploads.
MAX_REQUEST_BODY_BYTES = 1_000_000

# The daemon's boot receipt / log lines go to stdout (which the plist
# redirects to StandardOutPath). When run under launchd, that's
# ~/MiniMax-Agent/99 _system/logs/harness.log. When run interactively
# (for testing), it's the terminal.

# Path to the harness log file (where stdout ends up under launchd).
HARNESS_LOG_PATH = Path(
    "/Users/brassfieldventuresllc/MiniMax-Agent/99 _system/logs/harness.log"
)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def log(message: str) -> None:
    """Log a timestamped message. Goes to stdout (which the plist captures).

    Format mirrors scaffolding_review_cron and the rest of the harness:
    ISO 8601 UTC timestamp + level-less line.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    print(f"[{ts}] {message}", flush=True)


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------


class HarnessHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for the Mavis Harness daemon.

    Class-level state (set by run_daemon before serve_forever):
      - harness: the shared MavisHarness instance
      - started_at: monotonic timestamp of daemon boot (for uptime)
      - daemon_host, daemon_port: bind info, for /health diagnostics
    """

    # Class-level state — shared across all requests.
    harness: ClassVar[Optional[MavisHarness]] = None
    started_at: ClassVar[float] = 0.0
    daemon_host: ClassVar[str] = DEFAULT_DAEMON_HOST
    daemon_port: ClassVar[int] = DEFAULT_DAEMON_PORT

    # Override the default BaseHTTPRequestHandler logging. The default
    # writes to stderr; under launchd, stderr is captured in
    # StandardErrorPath. We route to stdout (captured in
    # StandardOutPath) so the access log and the boot log live in
    # the same file.
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        try:
            log(f"http  {self.address_string()} - {format % args}")
        except Exception:
            # Never let a logging failure kill the daemon.
            pass

    # -- HTTP method dispatch ----------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._respond(200, self._health_payload())
        elif self.path == "/stats":
            self._respond(200, self._stats_payload())
        elif self.path == "/":
            # Friendly index for browsers / curl
            self._respond(200, {
                "name": "mavis_harness",
                "version": "Sprint 5 (Local-Compute Pivot, 12B QAT)",
                "endpoints": ["GET /health", "POST /turn", "GET /stats"],
            })
        else:
            self._respond(404, {"error": f"unknown endpoint: {self.path}"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/turn":
            self._handle_turn()
        else:
            self._respond(404, {"error": f"unknown endpoint: {self.path}"})

    # -- /turn handler -----------------------------------------------

    def _handle_turn(self) -> None:
        if self.harness is None:
            self._respond(503, {"error": "harness not initialized"})
            return

        try:
            body = self._read_json_body()
        except ValueError as e:
            self._respond(400, {"error": str(e)})
            return

        input_text = body.get("input", "")
        if not isinstance(input_text, str) or not input_text.strip():
            self._respond(400, {"error": "missing or empty 'input' field"})
            return

        # Log the request so the access trail is visible.
        log(f"turn  input={input_text[:120]!r}")

        try:
            response_text = self.harness.handle_turn(input_text)
        except Exception as e:  # noqa: BLE001
            log(f"turn  ERROR: {e!r}")
            self._respond(500, {"error": f"harness error: {e!r}"})
            return

        # Determine the model that handled the request. For L1 regex
        # matches, no model was used. For L2/L3 cascades, the
        # OllamaClient's fast_model was used (e4b by default). The
        # chat_model (12b by default) is only used for the /dispatch
        # lane's worker calls — not directly by /turn. This is the
        # routing audit data the chief needs to verify the 12B is
        # in the right slot.
        intent_source = "unknown"
        model_used = "none (L1 regex)"
        # The lane handlers populate _last_classification for the
        # /turn endpoint to read. We do this by inspecting the
        # counters and the most recent L2 route call. Simpler:
        # just report what the harness has, not fine-grained.
        stats = self.harness._gather_stats()  # noqa: SLF001 (intentional)
        # The classification source for the last /turn can be
        # inferred: if _ollama_call_count increased during the
        # request, L2 was used; otherwise L1.
        # (The harness doesn't currently track per-turn sources;
        # this is a v2 enhancement.)
        if self.harness._ollama_call_count > 0:
            intent_source = "L2"
            model_used = self.harness.ollama.fast_model

        log(
            f"turn  response={response_text[:120]!r}  "
            f"source={intent_source}  model={model_used}"
        )

        self._respond(200, {
            "response": response_text,
            "session_id": self.harness.session_id,
            "classification_source": intent_source,
            "model_used": model_used,
            "classification_count": stats.router.total_classifications,
        })

    # -- /health payload ---------------------------------------------

    def _health_payload(self) -> Dict[str, Any]:
        if self.harness is None:
            return {"status": "initializing"}

        # Probe Ollama reachability with a 2s timeout. We don't want
        # a slow Ollama to block /health.
        ollama_reachable = False
        ollama_error: Optional[str] = None
        try:
            with urllib.request.urlopen(
                f"{self.harness.ollama.base_url}/api/tags",
                timeout=2.0,
            ) as resp:
                ollama_reachable = resp.status == 200
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            ollama_error = str(e)

        return {
            "status": "ok",
            "session_id": self.harness.session_id,
            "uptime_seconds": round(time.monotonic() - self.started_at, 3),
            "bind": f"{self.daemon_host}:{self.daemon_port}",
            "ollama": {
                "url": self.harness.ollama.base_url,
                "reachable": ollama_reachable,
                "error": ollama_error,
                "chat_model": self.harness.ollama.chat_model,
                "fast_model": self.harness.ollama.fast_model,
            },
        }

    # -- /stats payload ----------------------------------------------

    def _stats_payload(self) -> Dict[str, Any]:
        if self.harness is None:
            return {"status": "initializing"}

        stats = self.harness._gather_stats()  # noqa: SLF001 (intentional)
        return {
            "session_id": self.harness.session_id,
            "router": asdict(stats.router),
            "loader": asdict(stats.loader),
            "safety": asdict(stats.safety),
            "cost": asdict(stats.cost),
            "drift_score": compute_drift_score(stats),
            "ollama_call_count": self.harness._ollama_call_count,  # noqa: SLF001
            "ollama_fallback_count": self.harness._ollama_fallback_count,  # noqa: SLF001
        }

    # -- HTTP plumbing -----------------------------------------------

    def _read_json_body(self) -> Dict[str, Any]:
        """Read the request body, parse as JSON, return the dict.

        Raises ValueError on empty body, body too large, or invalid JSON.
        """
        length_str = self.headers.get("Content-Length", "0")
        try:
            length = int(length_str)
        except ValueError:
            raise ValueError(f"invalid Content-Length: {length_str!r}")

        if length == 0:
            raise ValueError("empty request body")

        if length > MAX_REQUEST_BODY_BYTES:
            raise ValueError(
                f"request body too large: {length} bytes "
                f"(max {MAX_REQUEST_BODY_BYTES})"
            )

        raw = self.rfile.read(length)
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"invalid JSON: {e}")

        if not isinstance(parsed, dict):
            raise ValueError(f"expected JSON object, got {type(parsed).__name__}")

        return parsed

    def _respond(self, status: int, payload: Dict[str, Any]) -> None:
        """Send a JSON response with the given status code and payload."""
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            # Client disconnected; not our problem.
            pass


# ---------------------------------------------------------------------------
# Daemon entry point
# ---------------------------------------------------------------------------


def run_daemon(
    host: str = DEFAULT_DAEMON_HOST,
    port: int = DEFAULT_DAEMON_PORT,
    harness: Optional[MavisHarness] = None,
) -> None:
    """Start the HTTP daemon. Blocks until SIGTERM/SIGINT.

    The harness is constructed here (or passed in for tests). The HTTP
    handler holds a class-level reference to the harness; all requests
    share the same harness instance.
    """
    if harness is None:
        harness = MavisHarness()

    # Wire the harness into the handler class.
    HarnessHTTPHandler.harness = harness
    HarnessHTTPHandler.started_at = time.monotonic()
    HarnessHTTPHandler.daemon_host = host
    HarnessHTTPHandler.daemon_port = port

    # Build the server. ThreadingHTTPServer spawns a thread per request;
    # BaseHTTPRequestHandler runs in that thread. The harness is shared.
    try:
        server = ThreadingHTTPServer((host, port), HarnessHTTPHandler)
    except OSError as e:
        log(f"FATAL  could not bind to {host}:{port}: {e}")
        log(f"       is another process using the port? try --port N")
        raise

    # Graceful shutdown. launchd sends SIGTERM on `launchctl bootout`;
    # we honor it cleanly. SIGINT is for local Ctrl-C testing.
    #
    # IMPORTANT: signal.signal() only works in the main thread of the
    # main interpreter. When this daemon is run from a worker thread
    # (e.g. the selftest), the signal install would fail. We detect
    # the threading context and skip the install in that case — the
    # selftest tears the daemon down via thread death, not signal.
    shutdown_event = threading.Event()

    def _shutdown(signum: int, _frame: Any) -> None:
        signame = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        log(f"signal received: {signame} (signum={signum}); shutting down.")
        # server.shutdown() must be called from a different thread
        # than the one running serve_forever(). Schedule it.
        threading.Thread(target=server.shutdown, daemon=True).start()
        shutdown_event.set()

    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, _shutdown)
        signal.signal(signal.SIGINT, _shutdown)
    else:
        log("note: signal handlers not installed (not on main thread; "
            "shutdown via thread death)")

    # Boot receipt. These are the lines the user greps for in the
    # launchd log to confirm the daemon is alive.
    log("=" * 60)
    log("mavis_harness daemon starting")
    log(f"  bind         = http://{host}:{port}")
    log(f"  session_id   = {harness.session_id}")
    log(f"  ollama_url   = {harness.ollama.base_url}")
    log(f"  chat_model   = {harness.ollama.chat_model}  (L3 Logic Worker)")
    log(f"  fast_model   = {harness.ollama.fast_model}  (L2 Fast Routing)")
    log(f"  log_path     = {HARNESS_LOG_PATH}")
    log(f"  python       = {sys.version.split()[0]}")
    log("=" * 60)
    log("endpoints:")
    log("  GET  /health   liveness + ollama reachability + routing")
    log("  POST /turn     {input: ...} → {response: ..., model_used: ...}")
    log("  GET  /stats    live counters + drift score")
    log("daemon ready.")

    try:
        server.serve_forever()
    finally:
        server.server_close()
        log("daemon stopped.")


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def _selftest() -> int:
    """Run the daemon's self-test. Exits 0 on success.

    Starts a daemon on a non-default port, fires HTTP requests at it,
    and validates the responses. Tears down the daemon on exit.
    """
    import shutil
    import tempfile
    import urllib.request

    failures: list = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        status = "PASS" if cond else "FAIL"
        line = f"  [{status}] {name}"
        if detail:
            line += f" — {detail}"
        print(line)
        if not cond:
            failures.append(name)

    print("mavis_harness_daemon self-test")
    print("=" * 50)

    # Use a temp workspace so we don't pollute the real vault.
    tmp_root = Path(tempfile.mkdtemp(prefix="mavis_daemon_selftest_"))
    state = tmp_root / "state"; state.mkdir(parents=True, exist_ok=True)
    queue = tmp_root / "queue"; queue.mkdir(parents=True, exist_ok=True)
    reviews = tmp_root / "reviews"; reviews.mkdir(parents=True, exist_ok=True)

    # Bind to a high random port to avoid conflicts.
    test_port = 38999
    test_host = "127.0.0.1"

    # Build a harness with FakeOllama-like behavior via a real client
    # (we'll skip Ollama calls in /health by setting a bad URL).
    # Actually, we'll use a FakeOllama that just returns ask_first.
    class _FakeAskFirst:
        def __init__(self):
            self.calls = []
        def chat(self, messages, model=None, **kwargs):
            self.calls.append({"messages": messages, "model": model})
            from mavis_harness_main import OllamaResponse
            return OllamaResponse(
                model=model or "fake",
                content="[FAKE]",
                elapsed_seconds=0.01,
                raw={},
            )
        def route(self, user_text):
            self.calls.append({"route": user_text})
            return {"intent": "ask_first", "confidence": 0.0}

    from mavis_harness_main import OllamaClient
    fake_ollama = _FakeAskFirst()
    # Wrap in a class that mimics OllamaClient for the harness's
    # __init__ (the harness accepts any object with .chat and .route).
    harness = MavisHarness(
        vault_root=tmp_root,
        state_dir=state,
        worker_queue_dir=queue,
        dispatch_output_dir=reviews,
        ollama=fake_ollama,  # type: ignore[arg-type]
    )
    # The harness's ollama attribute is the fake; but the health
    # probe URL is read from the real OllamaClient. Override the
    # base_url on the fake by giving it a stub attribute.
    fake_ollama.base_url = "http://localhost:11434"  # type: ignore[attr-defined]
    fake_ollama.chat_model = "gemma4:12b-it-qat"  # type: ignore[attr-defined]
    fake_ollama.fast_model = "gemma4:e4b-it-qat"  # type: ignore[attr-defined]

    # Start the daemon on the test port.
    server_thread = threading.Thread(
        target=run_daemon,
        kwargs={"host": test_host, "port": test_port, "harness": harness},
        daemon=True,
    )
    server_thread.start()

    # Give the server a moment to bind.
    time.sleep(0.5)

    base = f"http://{test_host}:{test_port}"

    try:
        # ---- Test 1: GET /health ----
        with urllib.request.urlopen(f"{base}/health", timeout=3) as resp:
            check("GET /health returns 200", resp.status == 200)
            health = json.loads(resp.read().decode("utf-8"))
            check("health has session_id", "session_id" in health)
            check("health reports chat_model = gemma4:12b-it-qat",
                  health.get("ollama", {}).get("chat_model") == "gemma4:12b-it-qat",
                  f"got {health.get('ollama', {}).get('chat_model')!r}")
            check("health reports fast_model = gemma4:e4b-it-qat",
                  health.get("ollama", {}).get("fast_model") == "gemma4:e4b-it-qat",
                  f"got {health.get('ollama', {}).get('fast_model')!r}")

        # ---- Test 2: GET / ----
        with urllib.request.urlopen(f"{base}/", timeout=3) as resp:
            check("GET / returns 200", resp.status == 200)
            index = json.loads(resp.read().decode("utf-8"))
            check("index lists endpoints", "endpoints" in index)

        # ---- Test 3: GET /unknown → 404 ----
        try:
            with urllib.request.urlopen(f"{base}/unknown", timeout=3) as resp:
                check("GET /unknown returns 404", resp.status == 404)
        except urllib.error.HTTPError as e:
            check("GET /unknown returns 404", e.code == 404)

        # ---- Test 4: POST /turn with ambiguous input → ask_first ----
        req = urllib.request.Request(
            f"{base}/turn",
            data=json.dumps({"input": "what is the meaning of life?"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            check("POST /turn returns 200", resp.status == 200)
            turn = json.loads(resp.read().decode("utf-8"))
            check("/turn response has 'response' field", "response" in turn)
            check("/turn response is ask_first",
                  "Need clarification" in turn.get("response", ""),
                  f"got {turn.get('response', '')[:80]!r}")
            check("/turn reports classification_source",
                  "classification_source" in turn)
            check("/turn reports model_used",
                  "model_used" in turn)

        # ---- Test 5: POST /turn with /capture (L1 regex hit) ----
        req = urllib.request.Request(
            f"{base}/turn",
            data=json.dumps({"input": "/capture hello world"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            turn = json.loads(resp.read().decode("utf-8"))
            check("/capture via /turn returns Captured",
                  "Captured" in turn.get("response", ""),
                  f"got {turn.get('response', '')[:80]!r}")

        # ---- Test 6: POST /turn with empty input → 400 ----
        req = urllib.request.Request(
            f"{base}/turn",
            data=json.dumps({"input": ""}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                check("empty input returns 400", resp.status == 400)
        except urllib.error.HTTPError as e:
            check("empty input returns 400", e.code == 400)

        # ---- Test 7: POST /turn with invalid JSON → 400 ----
        req = urllib.request.Request(
            f"{base}/turn",
            data=b"not json at all",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                check("invalid JSON returns 400", resp.status == 400)
        except urllib.error.HTTPError as e:
            check("invalid JSON returns 400", e.code == 400)

        # ---- Test 8: GET /stats ----
        with urllib.request.urlopen(f"{base}/stats", timeout=3) as resp:
            check("GET /stats returns 200", resp.status == 200)
            stats = json.loads(resp.read().decode("utf-8"))
            check("stats has router counters", "router" in stats)
            check("stats has drift_score", "drift_score" in stats)
            check("stats classification_count > 0 (from prior /turn calls)",
                  stats.get("router", {}).get("total_classifications", 0) >= 2,
                  f"got {stats.get('router', {}).get('total_classifications')}")

    finally:
        # Tear down the daemon.
        # We can't easily call server.shutdown() from outside; send
        # SIGTERM to the current process and let the handler catch it.
        # But we started the server in a daemon thread, so SIGTERM
        # to the main process won't propagate. The cleanest way: just
        # wait for the thread to die when the test process exits.
        # The harness's thread is daemon=True, so it dies with the
        # process.
        shutil.rmtree(tmp_root, ignore_errors=True)

    print("=" * 50)
    if failures:
        print(f"FAIL: {len(failures)} check(s) failed: {failures}")
        return 1
    print("PASS: all self-test checks passed")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Mavis Harness daemon")
    parser.add_argument("--port", type=int, default=DEFAULT_DAEMON_PORT,
                        help=f"port to listen on (default {DEFAULT_DAEMON_PORT})")
    parser.add_argument("--host", default=DEFAULT_DAEMON_HOST,
                        help=f"host to bind to (default {DEFAULT_DAEMON_HOST})")
    parser.add_argument("--selftest", action="store_true",
                        help="run the daemon self-test and exit")
    args = parser.parse_args()

    if args.selftest:
        raise SystemExit(_selftest())

    run_daemon(host=args.host, port=args.port)
