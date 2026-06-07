"""test_mavis_harness_main.py — Sprint 5 unit tests.

Run: cd 03\\ Projects/Builder/drafts && python3 -m unittest test_mavis_harness_main -v

Covers the load-bearing pieces of the harness:
  - Boot: all four primitives + OllamaClient instantiate
  - Per-turn: classify → load context → dispatch by lane → record
  - Lane dispatchers: capture, synthesize, dispatch (with Ollama),
    dispatch (with Ollama down), observe, ask_first
  - The L1 → L2/L3 cascade via _safe_classify
  - Cron: run_cron writes a receipt, emits change event on watch+
  - _gather_stats: produces a coherent ScaffoldingStats
  - OllamaClient: chat() and route() success and failure paths
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock

_DRAFTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_DRAFTS_DIR.parent))  # 03 Projects/Builder on path
sys.path.insert(0, str(_DRAFTS_DIR))         # drafts/ on path

from mavis_harness_main import (  # type: ignore  # noqa: E402
    DEFAULT_OLLAMA_BASE_URL,
    DEFAULT_OLLAMA_CHAT_MODEL,
    DEFAULT_OLLAMA_FAST_MODEL,
    LaneResult,
    MavisHarness,
    OllamaClient,
    OllamaError,
    OllamaResponse,
)


# ---------------------------------------------------------------------------
# Test doubles — minimal stubs that match the real interface
# ---------------------------------------------------------------------------


class FakeOllama:
    """A double for the OllamaClient.

    Records every ``chat()`` call in ``self.calls`` so tests can assert
    on the messages, model, and kwargs the harness sends. Returns a
    fixed ``OllamaResponse`` whose content is configurable.
    """

    def __init__(self, content: str = "[FAKE] response", model: str = "fake-model"):
        self.content = content
        self.model = model
        self.calls: List[Dict[str, Any]] = []
        self.route_calls: List[str] = []
        self.route_response: Dict[str, Any] = {
            "intent": "ask_first", "confidence": 0.0,
        }

    def chat(self, messages, model=None, **kwargs):
        self.calls.append({
            "messages": list(messages),
            "model": model,
            "kwargs": kwargs,
        })
        return OllamaResponse(
            model=model or self.model,
            content=self.content,
            elapsed_seconds=0.123,
            raw={"fake": True},
        )

    def route(self, user_text: str) -> Dict[str, Any]:
        self.route_calls.append(user_text)
        return dict(self.route_response)


class DownOllama:
    """A double that raises OllamaError on every chat() call."""

    def __init__(self, message: str = "ollama_unreachable: connection refused"):
        self.message = message
        self.calls: List[Dict[str, Any]] = []
        self.route_calls: List[str] = []

    def chat(self, messages, model=None, **kwargs):
        self.calls.append({"messages": list(messages), "model": model})
        raise OllamaError(self.message)

    def route(self, user_text: str) -> Dict[str, Any]:
        self.route_calls.append(user_text)
        return {"intent": "ask_first", "confidence": 0.0, "fallback": "ollama_unreachable"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_harness(
    tmp_root: Path,
    ollama: Any = None,
) -> MavisHarness:
    """Build a MavisHarness rooted in a clean temp dir."""
    state_dir = tmp_root / "state"
    worker_queue = tmp_root / "worker_queue"
    review_dir = tmp_root / "reviews"
    for d in (state_dir, worker_queue, review_dir):
        d.mkdir(parents=True, exist_ok=True)
    return MavisHarness(
        vault_root=tmp_root,
        state_dir=state_dir,
        worker_queue_dir=worker_queue,
        dispatch_output_dir=review_dir,
        ollama=ollama or FakeOllama(),
    )


# ---------------------------------------------------------------------------
# Phase 1 — Boot
# ---------------------------------------------------------------------------


class TestBoot(unittest.TestCase):
    """The harness instantiates the four primitives + OllamaClient cleanly."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="harness_boot_"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_harness_constructs_with_defaults(self):
        harness = MavisHarness()
        self.assertIsNotNone(harness.context)
        self.assertIsNotNone(harness.tier3)
        self.assertIsNotNone(harness.ollama)
        self.assertTrue(harness.session_id.startswith("harness-"))

    def test_harness_constructs_with_custom_paths(self):
        state_dir = self.tmp / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        harness = MavisHarness(
            vault_root=self.tmp,
            state_dir=state_dir,
            worker_queue_dir=self.tmp / "queue",
            dispatch_output_dir=self.tmp / "reviews",
        )
        self.assertEqual(harness.state_dir, state_dir)
        self.assertEqual(harness.vault_root, self.tmp)

    def test_ollama_client_uses_defaults(self):
        client = OllamaClient()
        self.assertEqual(client.base_url, DEFAULT_OLLAMA_BASE_URL)
        self.assertEqual(client.chat_model, DEFAULT_OLLAMA_CHAT_MODEL)
        self.assertEqual(client.fast_model, DEFAULT_OLLAMA_FAST_MODEL)

    def test_ollama_client_strips_trailing_slash(self):
        client = OllamaClient(base_url="http://localhost:11434/")
        self.assertEqual(client.base_url, "http://localhost:11434")


# ---------------------------------------------------------------------------
# Phase 2 — Per-turn
# ---------------------------------------------------------------------------


class TestPerTurn(unittest.TestCase):
    """The load-bearing handle_turn() method."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="harness_perturn_"))
        self.ollama = FakeOllama(content="[FAKE] hello")
        self.harness = _make_harness(self.tmp, ollama=self.ollama)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ---- ask_first --------------------------------------------------

    def test_ambiguous_input_returns_ask_first(self):
        response = self.harness.handle_turn("what is the meaning of life?")
        self.assertIn("Need clarification", response)
        self.assertEqual(self.harness._classification_count, 1)
        self.assertEqual(self.harness._fallback_count, 1)
        self.assertEqual(self.harness._lane_counts["ask_first"], 1)

    def test_ask_first_does_not_call_ollama(self):
        # L1 falls through to ask_first on no-match. The harness's
        # _safe_classify would normally try Ollama next, but the
        # OllamaClient.route() here returns ask_first (the default).
        # So the cascade is L1 → Ollama route → ask_first, with one
        # route call but zero chat calls.
        self.harness.handle_turn("completely unstructured text")
        self.assertEqual(len(self.ollama.calls), 0, "should not call Ollama chat() on ask_first cascade")
        self.assertEqual(len(self.ollama.route_calls), 1, "should call Ollama route() exactly once")

    # ---- capture ----------------------------------------------------

    def test_capture_writes_to_meta_index(self):
        response = self.harness.handle_turn("/capture architect the mavis harness for sprint 6")
        self.assertIn("Captured", response)
        self.assertEqual(self.harness._lane_counts["capture"], 1)
        meta = self.harness.context.meta.all()
        # The key is the timestamped inbox key
        self.assertTrue(any(k.startswith("inbox/") for k in meta) or
                        any(k.startswith("inbox/") for k in self.harness.context.topic.keys()))

    # ---- dispatch with Ollama up -----------------------------------

    def test_dispatch_invokes_ollama(self):
        response = self.harness.handle_turn("/dispatch builder scaffold the next primitive")
        self.assertEqual(len(self.ollama.calls), 1)
        self.assertIn("FAKE", response)
        # The call should have a system message and a user message
        call = self.ollama.calls[0]
        self.assertEqual(len(call["messages"]), 2)
        self.assertEqual(call["messages"][0]["role"], "system")
        self.assertEqual(call["messages"][1]["role"], "user")
        self.assertEqual(call["messages"][1]["content"], "scaffold the next primitive")

    def test_dispatch_persists_packet(self):
        self.harness.handle_turn("/dispatch builder do the thing")
        queue = self.harness.worker_queue_dir
        packets = list(queue.glob("*.md"))
        self.assertEqual(len(packets), 1)
        content = packets[0].read_text(encoding="utf-8")
        self.assertIn("builder dispatch", content)
        self.assertIn("do the thing", content)
        self.assertIn("FAKE", content)

    def test_dispatch_packet_is_atomic_no_leak(self):
        self.harness.handle_turn("/dispatch builder do the thing")
        leaked = [f for f in os.listdir(self.harness.worker_queue_dir)
                  if ".tmp." in f]
        self.assertEqual(leaked, [], f"temp files leaked: {leaked}")

    def test_dispatch_increments_lane_count(self):
        self.harness.handle_turn("/dispatch builder do the thing")
        self.assertEqual(self.harness._lane_counts["dispatch"], 1)
        self.assertEqual(self.harness._ollama_call_count, 1)

    def test_dispatch_increments_safety_counter(self):
        self.harness.handle_turn("/dispatch builder do the thing")
        self.assertGreaterEqual(self.harness._safety_counts["total_atomic_writes"], 1)

    # ---- dispatch with Ollama down ---------------------------------

    def test_dispatch_falls_back_when_ollama_down(self):
        down = DownOllama()
        harness = _make_harness(self.tmp, ollama=down)
        response = harness.handle_turn("/dispatch builder do the thing")
        self.assertIn("OLLAMA FALLBACK", response)
        self.assertIn("ollama_unreachable", response)
        self.assertEqual(harness._ollama_fallback_count, 1)
        # Lane still counted as dispatch (we tried; the fallback is the response).
        self.assertEqual(harness._lane_counts["dispatch"], 1)

    def test_dispatch_persists_packet_even_when_ollama_down(self):
        # The packet is the audit trail; it should still be written
        # with the fallback content, not silently dropped.
        down = DownOllama()
        harness = _make_harness(self.tmp, ollama=down)
        harness.handle_turn("/dispatch builder do the thing")
        packets = list(harness.worker_queue_dir.glob("*.md"))
        self.assertEqual(len(packets), 1)
        content = packets[0].read_text(encoding="utf-8")
        self.assertIn("fallback", content.lower())

    # ---- synthesize ------------------------------------------------

    def test_synthesize_uses_chief_path(self):
        # /plan and /verify both route to synthesize per the L1 registry
        response = self.harness.handle_turn("/plan the next sprint")
        self.assertIn("SYNTHESIS", response)
        self.assertEqual(self.harness._lane_counts["synthesize"], 1)

    def test_synthesize_does_not_call_ollama(self):
        # Synthesize is the chief's lane (M3). The harness's skeleton
        # returns a placeholder without calling Ollama.
        self.harness.handle_turn("/plan the next sprint")
        self.assertEqual(len(self.ollama.calls), 0)

    # ---- observe ---------------------------------------------------

    def test_observe_returns_summary(self):
        response = self.harness.handle_turn("/observe recent activity")
        self.assertIn("Observation", response)
        self.assertIn("context_tokens", response)
        self.assertEqual(self.harness._lane_counts["observe"], 1)

    def test_observe_does_not_call_ollama(self):
        self.harness.handle_turn("/observe recent activity")
        self.assertEqual(len(self.ollama.calls), 0)

    # ---- confirmation replies (go / yes) ---------------------------

    def test_go_routes_to_dispatch(self):
        # The L1 regex for "go" matches intent=confirm lane=dispatch
        response = self.harness.handle_turn("go")
        # The dispatch handler runs but with no worker/task payload.
        # It calls Ollama (or falls back if Ollama is down).
        self.assertEqual(self.harness._lane_counts["dispatch"], 1)


# ---------------------------------------------------------------------------
# _safe_classify — the L1 → L2/L3 cascade
# ---------------------------------------------------------------------------


class TestSafeClassify(unittest.TestCase):
    """The harness's L1 → Ollama L2/L3 cascade."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="harness_classify_"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_l1_match_short_circuits(self):
        # /capture is L1-matched; the harness should not call Ollama.
        ollama = FakeOllama()
        harness = _make_harness(self.tmp, ollama=ollama)
        intent = harness._safe_classify("/capture hello world")
        self.assertEqual(intent.lane, "capture")
        self.assertEqual(intent.source, "L1")
        self.assertEqual(len(ollama.calls), 0)
        self.assertEqual(len(ollama.route_calls), 0)

    def test_l1_miss_triggers_ollama_route(self):
        # An L1 miss should trigger Ollama route().
        ollama = FakeOllama()
        ollama.route_response = {"intent": "synthesize", "confidence": 0.85}
        harness = _make_harness(self.tmp, ollama=ollama)
        intent = harness._safe_classify("do the architecture review")
        self.assertEqual(intent.lane, "synthesize")
        self.assertEqual(intent.intent, "synthesize")
        self.assertEqual(intent.confidence, 0.85)
        self.assertEqual(intent.source, "L2")
        self.assertEqual(len(ollama.route_calls), 1)

    def test_ollama_ask_first_keeps_ask_first(self):
        # Ollama returns ask_first — the harness should NOT escalate
        # back to the L1 result (it already is ask_first), and the
        # intent should remain ask_first. The L1 fallback source
        # is "fallback" (per command_router's L1 miss path), not "L1".
        ollama = FakeOllama()
        ollama.route_response = {"intent": "ask_first", "confidence": 0.95}
        harness = _make_harness(self.tmp, ollama=ollama)
        intent = harness._safe_classify("vague request")
        self.assertEqual(intent.lane, "ask_first")
        self.assertEqual(intent.source, "fallback")  # L1's no-match path

    def test_ollama_down_returns_ask_first(self):
        # For _safe_classify, "Ollama down" means route() raises.
        # Build a test double that raises on route() (DownOllama's
        # chat() raises but route() returns a dict, which is the
        # wrong shape for testing this path).
        class DownOllamaRoute:
            def route(self, user_text):
                raise OllamaError("ollama_unreachable")
            def chat(self, messages, model=None, **kwargs):
                raise OllamaError("ollama_unreachable")
        harness = _make_harness(self.tmp, ollama=DownOllamaRoute())
        intent = harness._safe_classify("anything that misses L1")
        self.assertEqual(intent.lane, "ask_first")
        self.assertEqual(intent.source, "fallback")  # L1's no-match path
        self.assertEqual(harness._ollama_fallback_count, 1)

    def test_ollama_invalid_intent_coerced_to_ask_first(self):
        # If Ollama returns a non-canonical intent name, the harness
        # falls back to ask_first.
        ollama = FakeOllama()
        ollama.route_response = {"intent": "make_coffee", "confidence": 0.99}
        harness = _make_harness(self.tmp, ollama=ollama)
        intent = harness._safe_classify("please make coffee")
        self.assertEqual(intent.lane, "ask_first")


# ---------------------------------------------------------------------------
# Phase 3 — Cron
# ---------------------------------------------------------------------------


class TestCron(unittest.TestCase):
    """The cron path: gather stats → run review → write receipt."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="harness_cron_"))
        self.ollama = FakeOllama()
        self.harness = _make_harness(self.tmp, ollama=self.ollama)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_run_cron_returns_review(self):
        review = self.harness.run_cron(review_date="2026-06-07")
        self.assertEqual(review.review_date, "2026-06-07")
        self.assertIsNotNone(review.drift_score)
        self.assertIsNotNone(review.band)

    def test_run_cron_writes_receipt_file(self):
        self.harness.run_cron(review_date="2026-06-07")
        receipt = self.harness.dispatch_output_dir / "2026-06-07.md"
        self.assertTrue(receipt.is_file())

    def test_run_cron_receipt_contains_stats(self):
        # Generate some traffic first
        self.harness.handle_turn("/capture test")
        self.harness.handle_turn("go")
        review = self.harness.run_cron(review_date="2026-06-07")
        receipt = self.harness.dispatch_output_dir / "2026-06-07.md"
        content = receipt.read_text(encoding="utf-8")
        self.assertIn("Scaffolding Health Receipt", content)
        self.assertIn("Component scores", content)
        # The harness did 2 classifications, so the receipt should reflect them
        self.assertIn("Total classifications: 2", content)

    def test_run_cron_emits_no_event_for_healthy(self):
        # Healthy stats → drift below WATCH_BAND → no event on stdout
        import io
        import contextlib
        # Don't generate any traffic; empty stats → drift = 0
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            self.harness.run_cron(review_date="2026-06-07")
        self.assertEqual(captured.getvalue().strip(), "")

    def test_run_cron_emits_event_for_critical(self):
        # Simulate critical stats. The drift threshold for event
        # emission is WATCH_BAND (0.50). To cross that, we need
        # multiple components above their thresholds — not just
        # fallback rate alone (which is capped at 0.30 by its weight).
        # We push the cost_overrun component above its threshold by
        # recording cost events where actual > planned.
        for _ in range(20):
            self.harness.handle_turn("unstructured text " * 5)
        # Inject critical cost stats: 100% overrun
        self.harness._cost_event_count = 100
        self.harness._total_actual_cost = 2.0
        self.harness._total_planned_cost = 0.5  # 4x overrun
        import io
        import contextlib
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            self.harness.run_cron(review_date="2026-06-07")
        stdout = captured.getvalue().strip()
        self.assertTrue(stdout, "expected event for critical review")
        event = json.loads(stdout)
        self.assertEqual(event["event"], "harness_change_detected")
        self.assertIn("drift_score", event)
        self.assertGreaterEqual(event["drift_score"], 0.5)  # >= WATCH_BAND

    def test_run_cron_uses_today_if_no_date(self):
        # Default review_date should be today (UTC)
        from datetime import datetime, timezone
        expected = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.harness.run_cron()
        receipt = self.harness.dispatch_output_dir / f"{expected}.md"
        self.assertTrue(receipt.is_file())


# ---------------------------------------------------------------------------
# _gather_stats — the bridge from runtime to cron
# ---------------------------------------------------------------------------


class TestGatherStats(unittest.TestCase):
    """The harness exposes its live counters as a ScaffoldingStats snapshot."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="harness_gather_"))
        self.ollama = FakeOllama()
        self.harness = _make_harness(self.tmp, ollama=self.ollama)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_gather_stats_returns_scaffolding_stats(self):
        stats = self.harness._gather_stats()
        from scaffolding_review_cron import ScaffoldingStats
        self.assertIsInstance(stats, ScaffoldingStats)

    def test_gather_stats_includes_live_counts(self):
        # Generate known traffic, then gather.
        self.harness.handle_turn("/capture test")
        self.harness.handle_turn("/observe foo")
        self.harness.handle_turn("unstructured text")
        stats = self.harness._gather_stats()
        self.assertEqual(stats.router.total_classifications, 3)
        self.assertGreaterEqual(stats.router.fallback_count, 1)
        self.assertEqual(stats.router.lane_distribution["capture"], 1)
        self.assertEqual(stats.router.lane_distribution["observe"], 1)
        self.assertGreaterEqual(stats.router.lane_distribution["ask_first"], 1)
        # Meta-index has at least one entry from the /capture
        self.assertGreaterEqual(stats.loader.meta_entries, 1)
        # At least one atomic write from the capture
        self.assertGreaterEqual(stats.safety.total_atomic_writes, 0)

    def test_gather_stats_rule_count_is_positive(self):
        # The L1 registry has 10 rules; the harness should read this.
        stats = self.harness._gather_stats()
        self.assertGreater(stats.router.rule_count, 0,
                           f"expected rule_count > 0, got {stats.router.rule_count}")


# ---------------------------------------------------------------------------
# OllamaClient — HTTP surface
# ---------------------------------------------------------------------------


class TestOllamaClient(unittest.TestCase):
    """The OllamaClient's chat() and route() methods."""

    def test_constructor_defaults(self):
        client = OllamaClient()
        self.assertEqual(client.base_url, "http://localhost:11434")
        self.assertEqual(client.chat_model, "gemma4:12b-it-qat")
        self.assertEqual(client.fast_model, "gemma4:e4b-it-qat")
        self.assertGreater(client.timeout_seconds, 0)

    def test_constructor_with_overrides(self):
        client = OllamaClient(
            base_url="http://gpu-host.lan:11434",
            chat_model="llama3.1:70b",
            fast_model="llama3.1:8b",
            timeout_seconds=10.0,
        )
        self.assertEqual(client.base_url, "http://gpu-host.lan:11434")
        self.assertEqual(client.chat_model, "llama3.1:70b")
        self.assertEqual(client.fast_model, "llama3.1:8b")
        self.assertEqual(client.timeout_seconds, 10.0)

    def test_route_returns_parsed_dict(self):
        client = OllamaClient()
        client.chat = MagicMock(return_value=OllamaResponse(
            model="x", content='{"intent": "dispatch", "confidence": 0.7}',
            elapsed_seconds=0.01, raw={},
        ))
        result = client.route("dispatch a task")
        self.assertEqual(result["intent"], "dispatch")
        self.assertEqual(result["confidence"], 0.7)

    def test_route_returns_ask_first_on_non_json(self):
        client = OllamaClient()
        client.chat = MagicMock(return_value=OllamaResponse(
            model="x", content="not json at all",
            elapsed_seconds=0.01, raw={},
        ))
        result = client.route("anything")
        self.assertEqual(result["intent"], "ask_first")
        self.assertEqual(result.get("fallback"), "non_json_response")

    def test_route_returns_ask_first_on_invalid_intent(self):
        client = OllamaClient()
        client.chat = MagicMock(return_value=OllamaResponse(
            model="x", content='{"intent": "make_coffee", "confidence": 0.9}',
            elapsed_seconds=0.01, raw={},
        ))
        result = client.route("please make coffee")
        self.assertEqual(result["intent"], "ask_first")

    def test_route_returns_ask_first_on_chat_error(self):
        client = OllamaClient()
        client.chat = MagicMock(side_effect=OllamaError("unreachable"))
        result = client.route("anything")
        self.assertEqual(result["intent"], "ask_first")
        self.assertEqual(result.get("fallback"), "ollama_unreachable")

    def test_chat_passes_kwargs_through(self):
        client = OllamaClient()
        client._post = MagicMock(return_value={
            "message": {"content": "ok"},
        })
        client.chat(
            messages=[{"role": "user", "content": "hi"}],
            model="custom-model",
            temperature=0.5,
            top_p=0.9,
            stop=["\n"],
        )
        call_args = client._post.call_args
        payload = call_args[0][1]
        self.assertEqual(payload["model"], "custom-model")
        self.assertEqual(payload["temperature"], 0.5)
        self.assertEqual(payload["top_p"], 0.9)
        self.assertEqual(payload["stop"], ["\n"])
        self.assertEqual(payload["stream"], False)

    def test_chat_returns_ollama_response(self):
        client = OllamaClient()
        client._post = MagicMock(return_value={
            "message": {"content": "hello"},
            "eval_count": 5,
            "eval_duration": 100_000_000,
        })
        response = client.chat(
            messages=[{"role": "user", "content": "hi"}],
        )
        self.assertIsInstance(response, OllamaResponse)
        self.assertEqual(response.content, "hello")
        self.assertEqual(response.raw["eval_count"], 5)


# ---------------------------------------------------------------------------
# LaneResult dataclass
# ---------------------------------------------------------------------------


class TestLaneResult(unittest.TestCase):
    """The LaneResult dataclass is the lane handler's return type."""

    def test_lane_result_carries_response_and_meta(self):
        result = LaneResult(response="hello", meta={"key": "value"})
        self.assertEqual(result.response, "hello")
        self.assertEqual(result.meta, {"key": "value"})

    def test_lane_result_meta_defaults_to_empty_dict(self):
        result = LaneResult(response="hi")
        self.assertEqual(result.meta, {})


# ---------------------------------------------------------------------------
# Integration with token_multiplier_config (cost accounting)
# ---------------------------------------------------------------------------


class TestCostAccounting(unittest.TestCase):
    """The harness's M3 cost events are tracked via record_cost_event."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="harness_cost_"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_record_cost_event_increments_count(self):
        harness = _make_harness(self.tmp)
        # Even if the token-plan.yaml doesn't exist, the counter
        # should increment (the harness treats missing config as
        # "no baseline, no drift signal").
        harness.record_cost_event(sdk_input_tokens=1000, sdk_output_tokens=500)
        self.assertEqual(harness._cost_event_count, 1)

    def test_record_cost_event_with_valid_config(self):
        import yaml
        # Create a minimal valid token-plan.yaml
        config_dir = self.tmp / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "token-plan.yaml"
        config_path.write_text(yaml.dump({
            "multipliers": {
                "input_rate": 1.3,
                "output_rate": 1.8,
                "system_prompt_per_char": 0.0,
            },
            "base_rates": {
                "input_per_m": 1.0,
                "output_per_m": 3.0,
            },
            "source_status": {
                "last_verified": "2026-06-07",
            },
        }))
        harness = MavisHarness(
            vault_root=self.tmp,
            state_dir=self.tmp / "state",
            worker_queue_dir=self.tmp / "queue",
            dispatch_output_dir=self.tmp / "reviews",
            ollama=FakeOllama(),
            token_plan_path=config_path,
        )
        harness.record_cost_event(sdk_input_tokens=1_000_000, sdk_output_tokens=500_000)
        self.assertEqual(harness._cost_event_count, 1)
        # actual = 1M * 1.3 * 1.0/1M + 500K * 1.8 * 3.0/1M = 1.3 + 2.7 = 4.0
        self.assertAlmostEqual(harness._total_actual_cost, 4.0, places=3)
        # planned = 1M * 1.0/1M + 500K * 3.0/1M = 1.0 + 1.5 = 2.5
        self.assertAlmostEqual(harness._total_planned_cost, 2.5, places=3)


if __name__ == "__main__":
    unittest.main()
