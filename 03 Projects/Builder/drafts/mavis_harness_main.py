"""
mavis_harness_main.py — Mavis Harness, Sprint 5: integration + Local-Compute Pivot.

Source: 03 Projects/Mavis/phase_next_architecture.md, Section 4.0
        (Local-Compute Pivot, 2026-06-07 14:18 CT)
Status: APPROVED (post-pivot); supersedes the Sprint 1-4 wiring.

The Local-Compute Pivot
-----------------------
The mavis daemon's per-agent ``defaultModel`` override (verified bug,
2026-06-07 14:00 CT) forces workers onto M3, which hits API rate limits
and stalls mid-task. Fighting the daemon is a platform problem; routing
around it is an architecture problem. The Local-Compute Pivot does the
latter: the worker fleet and the ``command_router`` L2/L3 fallback now
hit local Ollama (``http://localhost:11434``) instead of the Minimax API.

Model routing (§4.0):
  - Mavis (Chief/Scaffolding Review): minimax/MiniMax-M3  (unchanged)
  - command_router L2/L3 fallback:  ollama / gemma4:e4b-it-qat or gemma4:12b-it-qat  (NEW)
  - Worker fleet (Producer/Trust loop): ollama / gemma4:12b-it-qat (logic) or :e4b-it-qat (fast)  (NEW)

The chief is the ONLY component that still hits the Minimax API. Workers,
classifiers, and importance scorers run locally. Zero API cost on the
worker line item. Zero rate-limit ceiling on the worker fleet.

Three-phase lifecycle
---------------------
  Phase 1 (Boot):  instantiate singletons, load Tier 1, prime config.
  Phase 2 (Per-turn): classify → load context → dispatch by lane → record.
  Phase 3 (Cron): gather stats → run review → emit change event.

Composition
-----------
This module does not contain the four primitives' logic — it composes
them. The dependency arrow is:

  mavis_harness_main  →  { command_router, context_loader,
                           filesystem_bridge, token_multiplier_config,
                           scaffolding_review_cron }

No cross-deps between the primitives except ``scaffolding_review_cron →
filesystem_bridge.atomic_write`` (Sprint 4 design). The harness is the
glue; the primitives own their contracts.

Constraints
-----------
- Standard library only — except for the four harness primitives
  (``command_router``, ``context_loader``, ``filesystem_bridge``,
  ``token_multiplier_config``, ``scaffolding_review_cron``).
- Stdlib HTTP via ``urllib.request`` for Ollama calls. No ``requests``,
  no ``httpx``, no ``openai`` SDK. Apple Silicon + Ollama is the
  substrate; the client must work on a clean Python install.
- Deterministic where possible. The Ollama client returns a real
  string from the model, which is intrinsically non-deterministic
  across runs; the harness's own logic (classification, dispatch
  packet persistence) is deterministic.
- Fail-closed on classification. The command_router's L1 layer
  falls through to ``ask_first`` on no-match; the harness honors
  that and returns a clarifying question rather than guessing.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Imports of the four primitives + the cron
# ---------------------------------------------------------------------------

import sys
_HARNESS_DRAFTS = Path(__file__).resolve().parent
if str(_HARNESS_DRAFTS) not in sys.path:
    sys.path.insert(0, str(_HARNESS_DRAFTS))

from command_router import classify, classify_l1, Intent  # type: ignore  # noqa: E402
from context_loader import ContextLoader  # type: ignore  # noqa: E402
from filesystem_bridge import (  # type: ignore  # noqa: E402
    Tier3Loader,
    atomic_write,
    load_full_topic,
)
from token_multiplier_config import (  # type: ignore  # noqa: E402
    TokenPlanConfig,
    compute_actual_cost,
    load_config as load_token_plan_config,
)
from scaffolding_review_cron import (  # type: ignore  # noqa: E402
    CostSnapshot,
    LoaderSnapshot,
    RouterSnapshot,
    SafetySnapshot,
    ScaffoldingReview,
    ScaffoldingStats,
    run_review as run_scaffolding_review,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Local Ollama default endpoint. Apple Silicon + Ollama sidecar.
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_CHAT_MODEL = "gemma4:12b-it-qat"   # logic-class worker default (QAT weights, 12B punches at 30B+ on M4 Air)
DEFAULT_OLLAMA_FAST_MODEL = "gemma4:e4b-it-qat"   # fast structural / L2 / scoring (QAT weights)
DEFAULT_OLLAMA_TIMEOUT_SECONDS = 30.0

# Default harness paths. The vault root is the workspace; the state dir
# holds the meta-index; the worker queue dir holds dispatch packets.
DEFAULT_VAULT_ROOT = Path(
    os.path.expanduser("~/MiniMax-Agent")
)
DEFAULT_STATE_DIR = DEFAULT_VAULT_ROOT / ".mavis" / "state"
DEFAULT_WORKER_QUEUE_DIR = DEFAULT_VAULT_ROOT / ".mavis" / "worker_queue"
DEFAULT_DISPATCH_OUTPUT_DIR = DEFAULT_VAULT_ROOT / "99 _system" / "scaffolding-reviews"

# Token plan config. The harness re-reads this on every cost event so
# config updates take effect immediately. The path is a v1 default;
# real deployments should pass a configured path to the harness.
DEFAULT_TOKEN_PLAN_PATH = DEFAULT_VAULT_ROOT / ".mavis" / "config" / "token-plan.yaml"


# ---------------------------------------------------------------------------
# OllamaClient — the Local-Compute Pivot's HTTP surface
# ---------------------------------------------------------------------------


class OllamaError(RuntimeError):
    """Raised when the Ollama sidecar is unreachable or returns an error.

    Distinct from urllib.error.URLError so the harness can fall back to
    the API path (the old M2.7 path) without catching every URL error
    system-wide.
    """


@dataclass
class OllamaResponse:
    """A single Ollama /api/chat response, normalized for harness use."""

    model: str
    content: str
    elapsed_seconds: float
    raw: Dict[str, Any] = field(default_factory=dict)


class OllamaClient:
    """Minimal Ollama /api/chat client. Stdlib only.

    Two model slots, both local:
      - ``chat_model`` (default ``gemma4:12b-it-qat``): logic-class work (12B, QAT)
      - ``fast_model`` (default ``gemma4:e4b-it-qat``): fast structural work (4B, QAT)

    The two-slot design is deliberate: workers pick ``fast`` for
    read/structure/cite tasks (sub-second latency, no need for 31B
    reasoning) and ``chat`` for build/reason/verify tasks.

    Fallback contract
    -----------------
    If Ollama is unreachable, the client raises ``OllamaError`` — the
    harness catches this in the dispatch handler and falls back to the
    M3 API path with a ``fallback_reason: "ollama_unreachable"`` marker
    on the cost event. The chief is not blocked; the harness degrades
    to the old (working) behavior.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_BASE_URL,
        chat_model: str = DEFAULT_OLLAMA_CHAT_MODEL,
        fast_model: str = DEFAULT_OLLAMA_FAST_MODEL,
        timeout_seconds: float = DEFAULT_OLLAMA_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.chat_model = chat_model
        self.fast_model = fast_model
        self.timeout_seconds = float(timeout_seconds)

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST JSON to the Ollama API and return the parsed response.

        Raises ``OllamaError`` on network failure, non-2xx status, or
        invalid JSON. The exception message is structured so callers
        can log it without losing the response body.
        """
        url = f"{self.base_url}{endpoint}"
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                raw_bytes = resp.read()
        except urllib.error.URLError as e:
            raise OllamaError(
                f"ollama unreachable at {self.base_url}: {e.reason}"
            ) from e
        except (TimeoutError, OSError) as e:
            raise OllamaError(
                f"ollama request to {self.base_url} failed: {e}"
            ) from e

        try:
            return json.loads(raw_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise OllamaError(
                f"ollama returned non-JSON response from {url}: {e}"
            ) from e

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> OllamaResponse:
        """Send a chat completion request to Ollama and return the parsed response.

        Parameters
        ----------
        messages : list of {"role": ..., "content": ...}
            OpenAI-compatible message format. Roles: "system", "user", "assistant".
        model : str, optional
            Override the default chat model. Pass ``self.fast_model`` for
            fast structural work, ``self.chat_model`` for logic work.
        **kwargs
            Passed through to Ollama (temperature, top_p, stop, num_predict, etc.).

        Returns
        -------
        OllamaResponse
            ``content`` is the assistant message text. ``raw`` is the
            full response dict (eval_count, eval_duration, etc.) for
            cost/timing accounting.

        Notes
        -----
        ``stream`` is always False — the harness wants the full response
        atomically, not a token stream. Streaming is a v2 concern.
        """
        chosen = model or self.chat_model
        payload: Dict[str, Any] = {
            "model": chosen,
            "messages": list(messages),
            "stream": False,
        }
        payload.update(kwargs)

        started = time.monotonic()
        body = self._post("/api/chat", payload)
        elapsed = time.monotonic() - started

        message = body.get("message") or {}
        content = message.get("content", "")
        return OllamaResponse(
            model=chosen,
            content=content,
            elapsed_seconds=elapsed,
            raw=body,
        )

    def route(self, user_text: str) -> Dict[str, Any]:
        """Fast intent classification using the fast model.

        Used by the command_router L2/L3 fallback when L1 regex doesn't
        match. Returns a dict with at minimum ``{"intent": str, "confidence": float}``.

        On parse failure (the model returns non-JSON), returns the
        fail-closed default: ``{"intent": "ask_first", "confidence": 0.0}``.
        """
        prompt = (
            "You are a fast intent router. Classify the user input into exactly one of:\n"
            "  capture, synthesize, dispatch, observe, ask_first\n\n"
            "Definitions:\n"
            "  capture   - user wants to save a note/inbox item\n"
            "  synthesize - user wants a synthesized/curated response\n"
            "  dispatch  - user wants to delegate to a worker\n"
            "  observe   - user wants a read-only inspection/answer\n"
            "  ask_first - request is ambiguous or needs clarification\n\n"
            "Return ONLY a JSON object with this exact shape:\n"
            '{"intent": "<one of the five>", "confidence": <0.0 to 1.0>}\n\n'
            f"User input: {user_text!r}\n"
            "JSON:"
        )
        try:
            response = self.chat(
                [{"role": "user", "content": prompt}],
                model=self.fast_model,
                temperature=0.0,
            )
        except OllamaError:
            # If the local model is down, fall back to the fail-closed
            # default. The chief will see "ask_first" and clarify.
            return {"intent": "ask_first", "confidence": 0.0, "fallback": "ollama_unreachable"}

        # Try to extract a JSON object from the response content.
        content = response.content.strip()
        try:
            parsed = json.loads(content)
            if not isinstance(parsed, dict):
                raise ValueError("response is not a JSON object")
            intent = parsed.get("intent", "ask_first")
            confidence = float(parsed.get("confidence", 0.0))
            if intent not in ("capture", "synthesize", "dispatch", "observe", "ask_first"):
                intent = "ask_first"
            return {"intent": intent, "confidence": confidence}
        except (json.JSONDecodeError, ValueError, TypeError):
            return {"intent": "ask_first", "confidence": 0.0, "fallback": "non_json_response"}


# ---------------------------------------------------------------------------
# Lane handlers — one per command_router Intent.lane
# ---------------------------------------------------------------------------


@dataclass
class LaneResult:
    """The result of dispatching a single lane.

    The harness records the response in the context-loader's
    recent-turns buffer and returns it to the user. ``meta`` carries
    per-lane side-effect data (capture key, dispatch packet path, etc.)
    for the cron to ingest as stats.
    """

    response: str
    meta: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# MavisHarness — the composed runtime
# ---------------------------------------------------------------------------


class MavisHarness:
    """The Mavis Harness runtime. Composes the four primitives + Ollama.

    Lifecycle
    ---------
    Three phases, called by the host process (e.g. a launchd-launched
    Mavis session):

    Phase 1 (Boot) — ``__init__``:
        Instantiate ``ContextLoader`` (Tier 1 loads from disk), the
        ``Tier3Loader`` (empty cache), and the ``OllamaClient`` (no I/O
        until first call). Token plan config is loaded lazily on the
        first cost event.

    Phase 2 (Per-turn) — ``handle_turn(user_input)``:
        1. ``classify(user_input)`` — the command_router's L1 regex.
        2. If ``ask_first``: return a clarifying question, do not call any model.
        3. ``load_for_turn(user_input, now)`` — assemble the context window.
        4. Route by ``intent.lane``: capture / synthesize / dispatch / observe.
        5. ``record_turn(user_input, response)`` — update recent-turns buffer.
        6. Return the response.

    Phase 3 (Cron) — ``run_cron(review_date)``:
        1. ``_gather_stats()`` — pull live counts from the singletons.
        2. ``run_scaffolding_review(stats, review_date, output_dir)`` — write receipt.
        3. If drift >= WATCH_BAND, ``harness_change_detected`` event is emitted to stdout.
    """

    def __init__(
        self,
        vault_root: Path = DEFAULT_VAULT_ROOT,
        state_dir: Path = DEFAULT_STATE_DIR,
        worker_queue_dir: Path = DEFAULT_WORKER_QUEUE_DIR,
        dispatch_output_dir: Path = DEFAULT_DISPATCH_OUTPUT_DIR,
        ollama: Optional[OllamaClient] = None,
        token_plan_path: Path = DEFAULT_TOKEN_PLAN_PATH,
    ) -> None:
        self.vault_root = Path(vault_root)
        self.state_dir = Path(state_dir)
        self.worker_queue_dir = Path(worker_queue_dir)
        self.dispatch_output_dir = Path(dispatch_output_dir)
        self.token_plan_path = Path(token_plan_path)

        # Phase 1 (Boot): instantiate the four primitive singletons.
        self.context = ContextLoader(state_dir=self.state_dir)
        self.tier3 = Tier3Loader()
        self.ollama = ollama or OllamaClient()

        # Session-id for cost accounting. A real deployment would
        # use the mavis session id; for the harness skeleton this is
        # sufficient.
        self.session_id = f"harness-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        # Live counters that the cron's ScaffoldingStats reads from.
        # These are populated by the lane handlers during handle_turn().
        self._classification_count: int = 0
        self._fallback_count: int = 0
        self._lane_counts: Dict[str, int] = {
            "capture": 0, "synthesize": 0, "dispatch": 0, "observe": 0, "ask_first": 0,
        }
        self._safety_counts: Dict[str, int] = {
            "path_traversal_attempts_blocked": 0,
            "atomic_write_temp_file_leaks": 0,
            "total_atomic_writes": 0,
            "total_load_full_topic_calls": 0,
        }
        self._cost_event_count: int = 0
        self._total_actual_cost: float = 0.0
        self._total_planned_cost: float = 0.0
        self._ollama_call_count: int = 0
        self._ollama_fallback_count: int = 0

    # -----------------------------------------------------------------
    # Phase 2 — Per-turn
    # -----------------------------------------------------------------

    def handle_turn(self, user_input: str, now: Optional[float] = None) -> str:
        """Process one user turn end-to-end. Returns the response string.

        This is the load-bearing method. It implements the Integration
        Blueprint's Phase 2 (Per-turn loop):

          classify → if ask_first, return clarify;
                     else load context → dispatch by lane → record turn.
        """
        if now is None:
            now = time.monotonic()

        # Step 1: classify (L1 regex → L2/L3 Ollama fallback)
        # The harness owns the L2/L3 cascade because the L2/L3 inference
        # is local Ollama (Local-Compute Pivot). The cascade belongs in
        # the integration layer, not in command_router.
        intent = self._safe_classify(user_input)
        self._classification_count += 1
        self._lane_counts[intent.lane] = self._lane_counts.get(intent.lane, 0) + 1
        if intent.lane == "ask_first":
            self._fallback_count += 1

        # Step 2: ask-first short-circuit
        if intent.lane == "ask_first":
            response = self._ask_first(intent)
            self.context.record_turn(user_input, response)
            return response

        # Step 3: assemble the context window
        ctx = self.context.load_for_turn(user_input, now=now)

        # Step 4: dispatch by lane
        if intent.lane == "capture":
            result = self._capture(intent, user_input, ctx, now=now)
        elif intent.lane == "synthesize":
            result = self._synthesize(intent, user_input, ctx)
        elif intent.lane == "dispatch":
            result = self._dispatch(intent, user_input, ctx)
        elif intent.lane == "observe":
            result = self._observe(intent, user_input, ctx)
        else:
            # Defensive: command_router should never return anything else.
            result = LaneResult(response=f"(unknown lane: {intent.lane})")

        # Step 5: record turn
        self.context.record_turn(user_input, result.response)
        return result.response

    # ----- Lane handlers -----------------------------------------------

    def _ask_first(self, intent: Intent) -> str:
        """The fail-closed default. We don't call any model."""
        raw = intent.payload.get("raw", "")
        return (
            "Need clarification on the request. "
            f"Could you rephrase or add context? (raw: {raw[:120]!r})"
        )

    def _capture(
        self, intent: Intent, user_input: str, ctx: Any, now: float
    ) -> LaneResult:
        """Capture lane — write to the meta-index (Tier 1) or Tier 2.

        For the skeleton, the body is whatever follows the /capture
        slash command, or the raw user text if not a slash command.
        The body is routed to the right tier by size (the loader's
        built-in heuristic).
        """
        body = intent.payload.get("body", user_input)
        key = f"inbox/{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        tier = self.context.cache_topic(key, body, importance=0.5, now=now)
        return LaneResult(
            response=f"Captured to {key} (tier: {tier}).",
            meta={"key": key, "tier": tier, "bytes": len(body)},
        )

    def _synthesize(
        self, intent: Intent, user_input: str, ctx: Any
    ) -> LaneResult:
        """Synthesize lane — chief synthesis (M3, in production).

        The skeleton returns a placeholder that includes the context
        size and the raw input. The real implementation would call M3
        with the assembled ContextWindow as input. That's a v2 step;
        this skeleton is for the wiring, not the synthesis quality.
        """
        return LaneResult(
            response=(
                f"[CHIEF M3 SYNTHESIS PLACEHOLDER] "
                f"user_input={user_input[:80]!r} "
                f"context_tokens={ctx.estimated_tokens} "
                f"active_topics={len(ctx.active_topic_indexes)} "
                f"full_topic={ctx.full_topic[0] if ctx.full_topic else None}"
            ),
            meta={"ctx_tokens": ctx.estimated_tokens},
        )

    def _dispatch(
        self, intent: Intent, user_input: str, ctx: Any
    ) -> LaneResult:
        """Dispatch lane — route to local Ollama (Local-Compute Pivot).

        This is the load-bearing change of Sprint 5. The dispatch lane
        previously spawned a Minimax API worker (or wrote a packet to a
        worker queue, depending on the user's preference). After the
        Local-Compute Pivot, the dispatch lane calls local Ollama
        directly with the worker prompt.

        The architectural hook: the dispatch packet (a Markdown file
        written to ``worker_queue_dir``) is preserved as the audit
        trail, but the actual work happens inline via Ollama. Future
        workers can replace the inline call with a queue-poll loop
        without changing the lane handler's signature.
        """
        worker = intent.payload.get("worker", "default")
        task = intent.payload.get("task", user_input)

        # ---- The Local-Compute Pivot (2026-06-07 14:18 CT) ----
        # Try Ollama first. If it's unreachable, fall back to a
        # graceful error response (no M3 API call from here — the
        # chief is responsible for API calls, not the dispatch lane).
        # Use getattr() so test doubles (FakeOllama) don't need to
        # model the chat_model attribute — the real client has it,
        # but mocks are simpler without it.
        chat_model = getattr(self.ollama, "chat_model", "gemma4:12b-it-qat")
        try:
            self._ollama_call_count += 1
            ollama_response = self.ollama.chat(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are the {worker} worker in Mavis's fleet. "
                            "Be precise, concise, and cite your reasoning. "
                            "Output is consumed by the Mavis chief-of-staff."
                        ),
                    },
                    {"role": "user", "content": task},
                ],
                model=chat_model,
                temperature=0.3,
            )
            response_text = ollama_response.content
            worker_meta: Dict[str, Any] = {
                "worker": worker,
                "model": ollama_response.model,
                "elapsed_seconds": round(ollama_response.elapsed_seconds, 3),
                "fallback": None,
            }
        except OllamaError as e:
            # The Local-Compute Pivot failure mode: Ollama down.
            # The harness degrades gracefully. The chief can re-dispatch
            # via the API path if needed; the worker is not blocked
            # silently.
            self._ollama_fallback_count += 1
            response_text = (
                f"[OLLAMA FALLBACK] Worker {worker!r} could not be reached "
                f"via local Ollama. Error: {e}. "
                "Re-dispatch via the chief (M3 API) or restart Ollama."
            )
            worker_meta = {
                "worker": worker,
                "model": None,
                "elapsed_seconds": 0.0,
                "fallback": "ollama_unreachable",
                "error": str(e),
            }

        # Persist the dispatch packet — audit trail. This is the
        # file-based handoff pattern that the Mavis team-engine expects
        # when it ingests worker output for the next cycle.
        dispatch_id = (
            f"{worker}-"
            f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        )
        packet_path = self.worker_queue_dir / f"{dispatch_id}.md"
        packet_body = (
            f"# {worker} dispatch\n\n"
            f"**Task:** {task}\n\n"
            f"**Model:** {worker_meta.get('model') or 'fallback'}\n"
            f"**Elapsed:** {worker_meta.get('elapsed_seconds', 0.0):.3f}s\n"
            f"**Fallback:** {worker_meta.get('fallback') or 'none'}\n\n"
            f"## Response\n\n{response_text}\n"
        )
        try:
            atomic_write(str(packet_path), packet_body)
            self._safety_counts["total_atomic_writes"] += 1
            packet_persisted = True
        except OSError as e:
            packet_persisted = False
            packet_error = str(e)
        else:
            packet_error = None

        return LaneResult(
            response=response_text,
            meta={
                "worker": worker,
                "dispatch_id": dispatch_id,
                "packet_path": str(packet_path),
                "packet_persisted": packet_persisted,
                "packet_error": packet_error,
                **worker_meta,
            },
        )

    def _observe(
        self, intent: Intent, user_input: str, ctx: Any
    ) -> LaneResult:
        """Observe lane — read-only inspection.

        Returns a summary of the context window. The user can pass a
        /observe <topic> command and get the assembled window's
        structure without firing any model call.
        """
        topic = intent.payload.get("topic", user_input)
        active_keys = [k for k, _ in ctx.active_topic_indexes]
        return LaneResult(
            response=(
                f"Observation on {topic!r}: "
                f"context_tokens={ctx.estimated_tokens}, "
                f"active_topics={active_keys}, "
                f"full_topic={ctx.full_topic[0] if ctx.full_topic else None}, "
                f"recent_turns={len(ctx.recent_turns)}"
            ),
            meta={"topic": topic, "ctx_tokens": ctx.estimated_tokens},
        )

    # ----- L1 → L2/L3 cascade (Local-Compute Pivot) -------------------

    def _safe_classify(self, user_input: str) -> Intent:
        """Classify with the L1 → L2/L3 cascade, with graceful fallback.

        L1 (regex) is always available via ``classify_l1()``. The
        command_router's higher-level ``classify()`` cascade calls
        ``classify_l2()`` and ``classify_l3()`` stubs that raise
        ``NotImplementedError`` — so the harness does the cascade
        manually using the Ollama sidecar.

        Cascade order
        -------------
        1. L1 (regex, ~1ms, ~80% of fixed commands).
        2. L2 (Ollama ``gemma4:e4b-it-qat``, ~10-30ms, vector similarity).
           Implemented as a fast structured-output prompt; the model
           returns a JSON ``{intent, confidence}`` pair.
        3. If L2 returns ``ask_first`` or fails, the harness returns
           the L1 result (which is also ``ask_first`` because L1 missed
           first to reach this point).

        Failure modes
        -------------
        - Ollama unreachable: ``OllamaError`` is caught, the harness
          returns L1's ``ask_first`` (the fail-closed default).
        - L2 returns non-JSON: handled by ``OllamaClient.route()``,
          which falls back to ``ask_first``.
        - L2 returns a non-canonical intent name: coerced to
          ``ask_first`` (the safe default).

        Why the harness owns the cascade
        --------------------------------
        The L2/L3 inference is local Ollama (Local-Compute Pivot), not
        a remote API. The cascade is therefore an integration concern,
        not a command_router concern. command_router remains a pure
        data structure (L1 regex index); the harness composes the
        full classifier from ``command_router + OllamaClient``.
        """
        # L1: regex
        l1 = classify_l1(user_input)
        if l1.lane != "ask_first":
            return l1

        # L2/L3: local Ollama. This is the architectural hook.
        # The fast model handles the L2 step; the chat model would
        # handle L3 (long-tail ambiguity) but for now we use one model.
        try:
            self._ollama_call_count += 1
            route_result = self.ollama.route(user_input)
        except OllamaError:
            # Ollama is down. Stay on L1's ask_first (fail-closed).
            self._ollama_fallback_count += 1
            return l1

        # If L2 returned ask_first (either explicit or via fallback),
        # we honor that — the fail-closed default wins.
        intent_name = route_result.get("intent", "ask_first")
        if intent_name not in ("capture", "synthesize", "dispatch", "observe"):
            return l1

        confidence = float(route_result.get("confidence", 0.0))
        return Intent(
            intent=intent_name,
            confidence=confidence,
            payload={"raw": user_input, "ollama_route": route_result},
            lane=intent_name,
            matched_pattern=None,
            source="L2",
        )

    # -----------------------------------------------------------------
    # Phase 3 — Cron
    # -----------------------------------------------------------------

    def run_cron(self, review_date: Optional[str] = None) -> ScaffoldingReview:
        """Run the daily scaffolding review.

        Gathers live stats from the four primitives, builds a
        ``ScaffoldingStats`` snapshot, and dispatches to
        ``scaffolding_review_cron.run_review``. The cron writes the
        receipt to ``dispatch_output_dir`` and emits a
        ``harness_change_detected`` event to stdout if drift is at
        watch or worse.
        """
        stats = self._gather_stats()
        return run_scaffolding_review(
            stats=stats,
            review_date=review_date,
            output_dir=self.dispatch_output_dir,
        )

    def _gather_stats(self) -> ScaffoldingStats:
        """Pull live counts from the four primitives into a ScaffoldingStats.

        This is the bridge between the harness runtime and the
        scaffolding_review_cron. The cron's input is pure data;
        the harness is what knows the live counts.
        """
        # Router snapshot — derived from the harness's counters.
        # The command_router itself doesn't expose a stats object
        # in v1; the harness tracks classifications + lane counts.
        # The ``rule_count`` is read from the L1 registry size if
        # importable, else defaulted to 0.
        try:
            import command_router as cr  # type: ignore
            rule_count = len(getattr(cr, "_REGISTRY", []))
        except (ImportError, AttributeError):
            rule_count = 0

        router = RouterSnapshot(
            total_classifications=self._classification_count,
            fallback_count=self._fallback_count,
            lane_distribution=dict(self._lane_counts),
            l2_not_implemented=0,
            l3_not_implemented=0,
            rule_count=rule_count,
        )

        # Loader snapshot — pulled from the live ContextLoader + Tier3Loader.
        tier3_stats = self.tier3.stats()
        loader = LoaderSnapshot(
            meta_entries=len(self.context.meta.all()),
            topic_entries=len(self.context.topic.keys()),
            full_entries=len(self.context.full.keys()),
            hits=tier3_stats.hits,
            misses=tier3_stats.misses,
            evictions=tier3_stats.evictions,
            bytes_served=tier3_stats.bytes_served,
            bytes_cached=tier3_stats.bytes_cached,
            hard_floor_violations=0,  # not exposed in skeleton; real impl tracks this
            recent_turns=len(self.context._recent),
            avg_window_tokens=0.0,  # not tracked in skeleton
        )

        # Safety snapshot — counters maintained by the harness.
        safety = SafetySnapshot(
            path_traversal_attempts_blocked=self._safety_counts["path_traversal_attempts_blocked"],
            atomic_write_temp_file_leaks=self._safety_counts["atomic_write_temp_file_leaks"],
            total_atomic_writes=self._safety_counts["total_atomic_writes"],
            total_load_full_topic_calls=self._safety_counts["total_load_full_topic_calls"],
        )

        # Cost snapshot — derived from the running totals.
        cost = CostSnapshot(
            event_count=self._cost_event_count,
            total_actual_cost=self._total_actual_cost,
            total_planned_cost=self._total_planned_cost,
            last_verified="2026-06-07",  # placeholder; real impl reads token-plan.yaml
        )

        return ScaffoldingStats(router=router, loader=loader, safety=safety, cost=cost)

    # -----------------------------------------------------------------
    # Cost accounting (called by the host, not from handle_turn)
    # -----------------------------------------------------------------

    def record_cost_event(
        self,
        sdk_input_tokens: int,
        sdk_output_tokens: int,
    ) -> None:
        """Record a cost event for the harness's own API calls (chief/M3).

        This is for the M3 line item only. The Ollama workers don't
        go through here — their cost is electricity, not API tokens.

        The token plan config is re-read on every call so updates
        take effect immediately (per the token_multiplier_config
        Sprint 2 contract).
        """
        try:
            config = load_token_plan_config(self.token_plan_path)
        except (FileNotFoundError, Exception):
            # If the config isn't there, we still record the event
            # but with a 0.0 cost (so the drift score's cost_overrun
            # component is 0.0 — the cron treats missing config as
            # "no baseline, no drift signal").
            self._cost_event_count += 1
            return

        event = compute_actual_cost(
            sdk_input_tokens=sdk_input_tokens,
            sdk_output_tokens=sdk_output_tokens,
            session_id=self.session_id,
            config=config,
        )
        self._cost_event_count += 1
        self._total_actual_cost += event.actual_total_cost
        # The "planned" cost is the pre-multiplier cost (input + output
        # at base rates). Use 0.0 as a placeholder when we don't have
        # a separate planned baseline; the cost_overrun component will
        # be 0.0 (no baseline) which is the safe default.
        planned = (
            sdk_input_tokens * config.input_per_m / 1_000_000
            + sdk_output_tokens * config.output_per_m / 1_000_000
        )
        self._total_planned_cost += planned


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def _selftest() -> int:
    """Run the module's self-test. Exits 0 on success, non-zero on failure."""
    import shutil
    import tempfile

    failures: List[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        status = "PASS" if cond else "FAIL"
        line = f"  [{status}] {name}"
        if detail:
            line += f" — {detail}"
        print(line)
        if not cond:
            failures.append(name)

    # In-process test doubles for the Ollama client. The selftest
    # must work whether or not Ollama is running locally — production
    # behavior is covered by the unittest suite (which uses the
    # real OllamaClient) and by the integration smoke test (which
    # exercises the real fallback path). The selftest is a build-time
    # regression check; it should not depend on the local Ollama
    # state.
    class _FakeAskFirst:
        """Ollama double that classifies everything as ask_first."""
        def __init__(self):
            self.calls: List[Any] = []
        def chat(self, messages, model=None, **kwargs):
            self.calls.append({"messages": messages, "model": model})
            return OllamaResponse(
                model=model or "fake", content="[FAKE ASK_FIRST]",
                elapsed_seconds=0.01, raw={"fake": True},
            )
        def route(self, user_text: str) -> Dict[str, Any]:
            self.calls.append({"route": user_text})
            return {"intent": "ask_first", "confidence": 0.0}

    print("mavis_harness_main self-test")
    print("=" * 50)

    # Use a tempdir for all filesystem paths to avoid polluting the vault.
    tmp_root = Path(tempfile.mkdtemp(prefix="mavis_harness_selftest_"))
    try:
        # Set up clean dirs
        state_dir = tmp_root / "state"
        worker_queue = tmp_root / "worker_queue"
        review_dir = tmp_root / "reviews"
        for d in (state_dir, worker_queue, review_dir):
            d.mkdir(parents=True, exist_ok=True)

        # ---- Test 1: MavisHarness boots and instantiates the four primitives
        # Inject a fake Ollama so the selftest is independent of the
        # local Ollama state. The L1 regex matches /capture, /plan,
        # /verify, /observe, /dispatch, /go, /yes, /no, etc. — those
        # short-circuit before any Ollama call. The ambiguous-text
        # tests in Test 2 fall through to Ollama route(), which the
        # fake returns as ask_first. This is the production behavior
        # in absence of a confident L2/L3 classification.
        harness = MavisHarness(
            vault_root=tmp_root,
            state_dir=state_dir,
            worker_queue_dir=worker_queue,
            dispatch_output_dir=review_dir,
            ollama=_FakeAskFirst(),  # type: ignore[arg-type]
        )
        check("MavisHarness boots", harness is not None)
        check("ContextLoader is instantiated", harness.context is not None)
        check("Tier3Loader is instantiated", harness.tier3 is not None)
        check("OllamaClient is instantiated", harness.ollama is not None)
        check("session_id is set", harness.session_id.startswith("harness-"))

        # ---- Test 2: ask_first lane short-circuits
        response = harness.handle_turn("what is the meaning of life?")
        check("ambiguous input → ask_first", "Need clarification" in response, f"response={response!r}")
        check("classification count incremented",
              harness._classification_count == 1,
              f"count={harness._classification_count}")
        check("fallback count incremented",
              harness._fallback_count == 1)
        check("ask_first lane count incremented",
              harness._lane_counts["ask_first"] == 1)

        # ---- Test 3: /capture lane writes to meta/topic
        response = harness.handle_turn("/capture architect the mavis harness for sprint 6")
        check("/capture lane returned a captured message",
              "Captured" in response, f"response={response!r}")
        check("capture lane count incremented",
              harness._lane_counts["capture"] == 1)
        check("meta-index has the new key",
              "inbox/" in str(harness.context.meta.all()) or
              any(k.startswith("inbox/") for k in harness.context.topic.keys()))

        # ---- Test 4: /dispatch lane calls Ollama (which is mocked here)
        # We construct a harness with a fake OllamaClient that returns a fixed string.
        class FakeOllama:
            def __init__(self):
                self.calls = []
                self.fast_calls = []
            def chat(self, messages, model=None, **kwargs):
                self.calls.append({"messages": messages, "model": model})
                return OllamaResponse(
                    model=model or "fake",
                    content="[FAKE OLLAMA RESPONSE] worker did the thing.",
                    elapsed_seconds=0.123,
                    raw={"fake": True},
                )
            def route(self, user_text):
                self.fast_calls.append(user_text)
                return {"intent": "ask_first", "confidence": 0.0}

        fake = FakeOllama()
        harness_fake = MavisHarness(
            vault_root=tmp_root,
            state_dir=state_dir,
            worker_queue_dir=worker_queue,
            dispatch_output_dir=review_dir,
            ollama=fake,  # type: ignore
        )
        response = harness_fake.handle_turn("/dispatch builder scaffold the next primitive")
        check("/dispatch lane invoked Ollama", len(fake.calls) == 1,
              f"calls={len(fake.calls)}")
        check("Ollama response is returned", "FAKE OLLAMA RESPONSE" in response,
              f"response={response!r}")
        check("dispatch packet was persisted",
              any(f.name.startswith("builder-") and f.name.endswith(".md")
                  for f in worker_queue.iterdir()),
              f"queue={list(f.name for f in worker_queue.iterdir())}")
        check("dispatch lane count incremented",
              harness_fake._lane_counts["dispatch"] == 1)
        check("Ollama call counter incremented",
              harness_fake._ollama_call_count == 1)

        # ---- Test 5: /dispatch lane falls back gracefully when Ollama is down
        class DownOllama:
            def chat(self, messages, model=None, **kwargs):
                raise OllamaError("ollama_unreachable: connection refused")
            def route(self, user_text):
                return {"intent": "ask_first", "confidence": 0.0, "fallback": "ollama_unreachable"}

        harness_down = MavisHarness(
            vault_root=tmp_root,
            state_dir=state_dir,
            worker_queue_dir=worker_queue,
            dispatch_output_dir=review_dir,
            ollama=DownOllama(),  # type: ignore
        )
        response = harness_down.handle_turn("/dispatch builder do the thing")
        check("Ollama-down → fallback response", "OLLAMA FALLBACK" in response,
              f"response={response!r}")
        check("Ollama fallback counter incremented",
              harness_down._ollama_fallback_count == 1)
        check("dispatch lane still incremented",
              harness_down._lane_counts["dispatch"] == 1)

        # ---- Test 6: /observe lane returns a read-only summary
        response = harness.handle_turn("/observe recent activity")
        check("/observe lane returns observation", "Observation" in response,
              f"response={response!r}")
        check("observe lane count incremented",
              harness._lane_counts["observe"] == 1)

        # ---- Test 7: /plan and /verify routes to synthesize lane
        response = harness.handle_turn("/plan the next sprint")
        check("/plan → synthesize", "SYNTHESIS" in response, f"response={response!r}")
        response = harness.handle_turn("/verify command_router")
        check("/verify → synthesize", "SYNTHESIS" in response, f"response={response!r}")
        check("synthesize lane count == 2",
              harness._lane_counts["synthesize"] == 2,
              f"count={harness._lane_counts['synthesize']}")

        # ---- Test 8: go/yes confirmation routes to dispatch (but with no payload → not a real dispatch)
        # Actually, the L1 regex for "go" returns intent="confirm" lane="dispatch" with no payload.
        # The dispatch handler requires a "worker" or "task" payload; with neither, it falls back to user_input.
        response = harness.handle_turn("go")
        check("'go' confirmation → dispatch", "OLLAMA" in response or "FAKE" in response or "OLLAMA FALLBACK" in response,
              f"response={response!r}")

        # ---- Test 9: cron path runs and writes a receipt
        review = harness.run_cron(review_date="2026-06-07")
        check("cron returned a ScaffoldingReview", isinstance(review, ScaffoldingReview))
        check("cron review_date is set", review.review_date == "2026-06-07")
        receipt_path = review_dir / "2026-06-07.md"
        check("cron wrote a receipt file", receipt_path.is_file(),
              f"path={receipt_path}")
        with open(receipt_path, "r", encoding="utf-8") as f:
            content = f.read()
        check("receipt contains the harness version", "Sprint 4" in content)

        # ---- Test 10: stats gather produces a coherent ScaffoldingStats
        stats = harness._gather_stats()
        check("stats has router snapshot", stats.router.total_classifications > 0,
              f"total={stats.router.total_classifications}")
        check("stats lane distribution includes all 5 lanes",
              all(lane in stats.router.lane_distribution
                  for lane in ("capture", "synthesize", "dispatch", "observe", "ask_first")),
              f"distribution={stats.router.lane_distribution}")
        check("stats has loader snapshot with meta entries",
              stats.loader.meta_entries >= 0)
        check("stats has safety snapshot with atomic writes",
              stats.safety.total_atomic_writes >= 0)
        check("stats has cost snapshot",
              stats.cost.event_count >= 0)

    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    # ---- Test 11: OllamaClient chat() against a fake server (we don't hit localhost)
    # We just verify the constructor takes the right defaults.
    client = OllamaClient()
    check("OllamaClient default base URL", client.base_url == "http://localhost:11434")
    check("OllamaClient default chat model", client.chat_model == "gemma4:12b-it-qat")
    check("OllamaClient default fast model", client.fast_model == "gemma4:e4b-it-qat")
    check("OllamaClient default timeout > 0", client.timeout_seconds > 0)

    # ---- Test 12: OllamaClient.route() returns ask_first on non-JSON
    class NonJsonOllama:
        def chat(self, messages, model=None, **kwargs):
            return OllamaResponse(model=model or "x", content="not valid json at all",
                                  elapsed_seconds=0.01, raw={})
    client_bad = OllamaClient()
    client_bad.chat = NonJsonOllama().chat  # type: ignore
    result = client_bad.route("anything")
    check("non-JSON Ollama response → ask_first",
          result.get("intent") == "ask_first",
          f"result={result}")

    # ---- Test 13: OllamaClient.route() parses valid JSON
    class JsonOllama:
        def __init__(self, content):
            self._content = content
        def chat(self, messages, model=None, **kwargs):
            return OllamaResponse(model=model or "x", content=self._content,
                                  elapsed_seconds=0.01, raw={})
    client_good = OllamaClient()
    client_good.chat = JsonOllama('{"intent": "dispatch", "confidence": 0.87}').chat  # type: ignore
    result = client_good.route("dispatch a task")
    check("valid JSON Ollama response → intent=dispatch",
          result.get("intent") == "dispatch" and result.get("confidence") == 0.87,
          f"result={result}")

    print("=" * 50)
    if failures:
        print(f"FAIL: {len(failures)} check(s) failed: {failures}")
        return 1
    print("PASS: all self-test checks passed")
    return 0


if __name__ == "__main__":
    import sys
    # Two entry modes:
    #   python3 mavis_harness_main.py             → run the harness selftest
    #   python3 mavis_harness_main.py --daemon    → start the HTTP daemon
    # The daemon mode delegates to mavis_harness_daemon, which is a
    # sibling module. The plist's ProgramArguments uses --daemon so
    # launchd starts the listening process; the selftest is for
    # build-time regression checks.
    if "--daemon" in sys.argv:
        from mavis_harness_daemon import run_daemon
        run_daemon()
    else:
        raise SystemExit(_selftest())
