#!/usr/bin/env python3
"""test_mavis_cli.py — unit tests for mavis_cli.

Stdlib unittest only. No mocks framework. The HTTP layer is a single
function (request), so we monkey-patch it via the module's namespace.

Test matrix:
  1. POST /turn round-trip with positional prompt
  2. POST /turn with piped stdin (no TTY)
  3. POST /turn with multi-file -f concat (verifies "# File:" header)
  4. POST /turn with no input (must exit 64 + stderr message)
  5. POST /turn when daemon unreachable (must exit 64 + friendly stderr)
  6. POST /turn when input exceeds 1 MB cap (must exit 66)
  7. GET /health --json passthrough
  8. GET /stats pretty print

The HTTP layer is mocked; the input/parse/output logic is exercised for
real. Live integration against the running daemon is a manual smoke test,
not a unit test — see install_mavis_cli.sh and the boot-sequence report.
"""

from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import patch

# Make drafts/ importable so the test can `import mavis_cli`.
DRAFTS = Path(__file__).resolve().parent
sys.path.insert(0, str(DRAFTS))

import mavis_cli  # noqa: E402


# ---------------------------------------------------------------------------
# Test fakes — fake harness, fake connection errors
# ---------------------------------------------------------------------------


class FakeHarness:
    """In-process stand-in for the harness daemon.

    Stores calls, returns canned responses, simulates errors on demand.
    """

    def __init__(self, raise_conn: bool = False, status_override: int = 200) -> None:
        self.calls: List[Dict[str, Any]] = []
        self.raise_conn = raise_conn
        self.status_override = status_override
        self.health_payload = {
            "status": "ok",
            "session_id": "test-session",
            "uptime_seconds": 12.5,
            "bind": "127.0.0.1:11435",
            "ollama": {
                "url": "http://localhost:11434",
                "reachable": True,
                "error": None,
                "chat_model": "gemma4:12b-it-qat",
                "fast_model": "gemma4:e4b-it-qat",
            },
        }
        self.stats_payload = {
            "session_id": "test-session",
            "router": {
                "total_classifications": 5,
                "fallback_count": 1,
                "lane_distribution": {"capture": 2, "observe": 3},
                "l2_not_implemented": 0,
                "l3_not_implemented": 0,
                "rule_count": 10,
            },
            "loader": {
                "meta_entries": 3, "topic_entries": 0, "full_entries": 0,
                "hits": 10, "misses": 2, "evictions": 0,
                "bytes_served": 4096, "bytes_cached": 1024,
                "hard_floor_violations": 0, "recent_turns": 1,
                "avg_window_tokens": 0.0,
            },
            "safety": {
                "path_traversal_attempts_blocked": 0,
                "atomic_write_temp_file_leaks": 0,
                "total_atomic_writes": 4,
                "total_load_full_topic_calls": 3,
            },
            "cost": {
                "event_count": 2,
                "total_actual_cost": 0.0021,
                "total_planned_cost": 0.002,
                "cost_overrun_ratio_override": None,
                "last_verified": "2026-06-07",
            },
            "drift_score": 0.05,
            "ollama_call_count": 2,
            "ollama_fallback_count": 0,
        }
        self.turn_payload = {
            "response": "the model said this",
            "lane": "synthesize",
            "model": "gemma4:12b-it-qat",
        }

    def request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None,
                host: str = "127.0.0.1", port: int = 11435,
                timeout: int = 120) -> Tuple[int, Dict[str, Any]]:
        self.calls.append({
            "method": method, "path": path, "body": body,
            "host": host, "port": port, "timeout": timeout,
        })
        if self.raise_conn:
            raise ConnectionError(f"cannot reach http://{host}:{port}{path}: refused")
        if self.status_override != 200:
            return self.status_override, {"error": "synthetic failure"}
        if path == "/turn":
            return 200, self.turn_payload
        if path == "/health":
            return 200, self.health_payload
        if path == "/stats":
            return 200, self.stats_payload
        return 404, {"error": f"unknown endpoint: {path}"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestTurn(unittest.TestCase):
    """POST /turn: positional, stdin, file, errors."""

    def _run_with(self, fake: FakeHarness, argv: List[str],
                  stdin_data: str = "") -> int:
        with patch.object(mavis_cli, "request", side_effect=fake.request), \
             redirect_stdout(io.StringIO()) as out, \
             redirect_stderr(io.StringIO()) as err:
            if stdin_data:
                sys.stdin = io.StringIO(stdin_data)
            try:
                rc = mavis_cli.main(argv)
            finally:
                sys.stdin = sys.__stdin__
        self._stdout = out.getvalue()
        self._stderr = err.getvalue()
        return rc

    def test_positional_prompt_roundtrip(self) -> None:
        fake = FakeHarness()
        rc = self._run_with(fake, ["summarize", "this"])
        self.assertEqual(rc, 0)
        self.assertEqual(self._stdout, "the model said this\n")
        self.assertEqual(fake.calls[0]["method"], "POST")
        self.assertEqual(fake.calls[0]["path"], "/turn")
        self.assertEqual(fake.calls[0]["body"], {"input": "summarize this"})

    def test_stdin_piped(self) -> None:
        fake = FakeHarness()
        rc = self._run_with(fake, [], stdin_data="from a pipe\nline two\n")
        self.assertEqual(rc, 0)
        self.assertEqual(self._stdout, "the model said this\n")
        self.assertEqual(fake.calls[0]["body"], {"input": "from a pipe\nline two\n"})

    def test_multi_file_concat(self) -> None:
        # Write two temp files in DRAFTS so the test stays self-contained.
        a = DRAFTS / "_test_input_a.md"
        b = DRAFTS / "_test_input_b.md"
        a.write_text("alpha body", encoding="utf-8")
        b.write_text("beta body", encoding="utf-8")
        try:
            fake = FakeHarness()
            rc = self._run_with(fake, ["-f", str(a), "-f", str(b)])
            self.assertEqual(rc, 0, msg=self._stderr)
            sent = fake.calls[0]["body"]["input"]
            self.assertIn("# File: _test_input_a.md", sent)
            self.assertIn("alpha body", sent)
            self.assertIn("# File: _test_input_b.md", sent)
            self.assertIn("beta body", sent)
            # Files in order, joined by \n\n.
            self.assertLess(sent.index("alpha body"), sent.index("beta body"))
        finally:
            a.unlink(missing_ok=True)
            b.unlink(missing_ok=True)

    def test_no_input_exits_64(self) -> None:
        fake = FakeHarness()
        # Empty argv, no stdin → must hit the "no input" branch.
        rc = self._run_with(fake, [])
        self.assertEqual(rc, mavis_cli.EXIT_USAGE)
        self.assertIn("no input", self._stderr)
        self.assertEqual(fake.calls, [])  # no HTTP call attempted

    def test_connection_refused_exits_64(self) -> None:
        fake = FakeHarness(raise_conn=True)
        rc = self._run_with(fake, ["hello"])
        self.assertEqual(rc, mavis_cli.EXIT_USAGE)
        self.assertIn("Is the harness daemon running?", self._stderr)
        self.assertIn("com.mavis.harness", self._stderr)

    def test_input_too_large_exits_66(self) -> None:
        fake = FakeHarness()
        # Build a prompt that exceeds 1 MB when joined.
        big = "x" * (mavis_cli.MAX_BODY_BYTES + 1)
        rc = self._run_with(fake, [big])
        self.assertEqual(rc, mavis_cli.EXIT_INPUT_TOO_LARGE)
        self.assertIn("daemon cap", self._stderr)
        self.assertEqual(fake.calls, [])  # rejected before HTTP call

    def test_verbose_emits_metadata(self) -> None:
        fake = FakeHarness()
        rc = self._run_with(fake, ["--verbose", "hi"])
        self.assertEqual(rc, 0)
        self.assertIn("the model said this", self._stdout)
        # Verbose metadata goes to stderr.
        self.assertIn("lane", self._stderr)
        self.assertIn("synthesize", self._stderr)


class TestHealth(unittest.TestCase):
    """GET /health — pretty + --json passthrough."""

    def test_pretty(self) -> None:
        fake = FakeHarness()
        with patch.object(mavis_cli, "request", side_effect=fake.request), \
             redirect_stdout(io.StringIO()) as out, \
             redirect_stderr(io.StringIO()):
            rc = mavis_cli.main(["--health"])
        self.assertEqual(rc, 0)
        text = out.getvalue()
        self.assertIn("status:        ok", text)
        self.assertIn("chat_model:    gemma4:12b-it-qat", text)
        self.assertEqual(fake.calls[0]["path"], "/health")
        self.assertEqual(fake.calls[0]["method"], "GET")

    def test_json_passthrough(self) -> None:
        fake = FakeHarness()
        with patch.object(mavis_cli, "request", side_effect=fake.request), \
             redirect_stdout(io.StringIO()) as out, \
             redirect_stderr(io.StringIO()):
            rc = mavis_cli.main(["--health", "--json"])
        self.assertEqual(rc, 0)
        parsed = json.loads(out.getvalue())
        self.assertEqual(parsed["status"], "ok")
        self.assertEqual(parsed["ollama"]["chat_model"], "gemma4:12b-it-qat")


class TestStats(unittest.TestCase):
    """GET /stats — pretty + --json passthrough."""

    def test_pretty(self) -> None:
        fake = FakeHarness()
        with patch.object(mavis_cli, "request", side_effect=fake.request), \
             redirect_stdout(io.StringIO()) as out, \
             redirect_stderr(io.StringIO()):
            rc = mavis_cli.main(["--stats"])
        self.assertEqual(rc, 0)
        text = out.getvalue()
        self.assertIn("drift_score:   0.05", text)
        self.assertIn("router.classifications:  5", text)
        self.assertIn("loader.hits/misses:      10/2", text)
        self.assertIn("ollama.calls:       2", text)

    def test_json_passthrough(self) -> None:
        fake = FakeHarness()
        with patch.object(mavis_cli, "request", side_effect=fake.request), \
             redirect_stdout(io.StringIO()) as out, \
             redirect_stderr(io.StringIO()):
            rc = mavis_cli.main(["--stats", "--json"])
        self.assertEqual(rc, 0)
        parsed = json.loads(out.getvalue())
        self.assertEqual(parsed["router"]["total_classifications"], 5)
        self.assertEqual(parsed["cost"]["total_actual_cost"], 0.0021)


class TestArgvOverride(unittest.TestCase):
    """--host and --port override env defaults."""

    def test_host_port_propagate(self) -> None:
        fake = FakeHarness()
        with patch.object(mavis_cli, "request", side_effect=fake.request), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            rc = mavis_cli.main(["--host", "10.0.0.5", "--port", "9999", "ping"])
        self.assertEqual(rc, 0)
        self.assertEqual(fake.calls[0]["host"], "10.0.0.5")
        self.assertEqual(fake.calls[0]["port"], 9999)


if __name__ == "__main__":
    unittest.main(verbosity=2)
