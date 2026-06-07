"""command_router.py — Mavis Harness, Sprint 3: command_router skeleton

Source: 03 Projects/Mavis/phase_next_architecture.md, Section 4.1
Status: APPROVED 2026-06-07 12:55 CT (Andre's locked decisions, Section 6a)

Purpose
-------
Classify incoming user requests and route them to the right execution lane.
Fail-closed: unmatched requests route to "ask_first", not "guess and execute".

Layered classification (v1 design doc §4.1):
  L1 — Regex pre-filter (whitelisted commands, slash commands, "go/yes/no" replies)
       Latency: <1ms. Coverage: ~80% of fixed commands. No model.
  L2 — Vector similarity against a labeled intent bank. Latency: ~50ms. M2.7-class.
  L3 — M3 LLM classification with structured output. Latency: ~1-3s. Long tail.

This module implements L1 only. L2 and L3 are stubs that raise NotImplementedError.

Execution lanes (§4.1 outputs):
  - capture     — write to inbox/notes
  - synthesize  — chief-of-staff synthesis
  - dispatch    — file-based handoff to a worker queue
  - observe     — read-only inspection
  - ask_first   — route back to user with a clarifying question (fail-closed default)

Constraints
-----------
- Standard library only. No external imports.
- Deterministic. No time-varying content. No stochastic generation.
- L1 rule order is reviewable in scaffolding_review cron.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple


# ---------------------------------------------------------------------------
# Intent dataclass
# ---------------------------------------------------------------------------

Lane = Literal["capture", "synthesize", "dispatch", "observe", "ask_first"]


@dataclass
class Intent:
    """Classified user intent.

    Fields
    ------
    intent : str
        Symbolic intent name (e.g. 'capture', 'confirm', 'slash_plan').
    confidence : float
        L1 regex always returns 1.0 on match, 0.0 on no-match (fail-closed).
        L2/L3 will return graded scores in [0, 1].
    payload : dict
        Extracted payload (e.g. the capture body, the slash command name).
        On ask_first: {'raw': original_text}.
    lane : Lane
        Execution lane this intent maps to. 'ask_first' is the safe default.
    matched_pattern : Optional[str]
        The regex pattern string that matched (None for L2/L3 / no-match).
    source : str
        Which layer classified: 'L1', 'L2', 'L3', or 'fallback'.
    """

    intent: str
    confidence: float
    payload: dict
    lane: Lane
    matched_pattern: Optional[str] = None
    source: str = "L1"


# ---------------------------------------------------------------------------
# L1 regex registry — order = priority (first match wins)
# ---------------------------------------------------------------------------
# Tuples: (compiled_pattern, intent_name, lane, group_keys)
#   group_keys maps regex capture groups to payload keys (in order).
# ---------------------------------------------------------------------------

_REGISTRY: List[Tuple[re.Pattern, str, Lane, Tuple[str, ...]]] = [
    # 1. Capture slash command — /capture <text>
    (
        re.compile(r"^/capture\s+(.+)$", re.IGNORECASE | re.DOTALL),
        "capture",
        "capture",
        ("body",),
    ),
    # 2. Dispatch slash command — /dispatch <worker> <task>
    (
        re.compile(r"^/dispatch\s+(\w+)\s+(.+)$", re.IGNORECASE | re.DOTALL),
        "dispatch",
        "dispatch",
        ("worker", "task"),
    ),
    # 3. Observe slash command — /observe <topic>
    (
        re.compile(r"^/observe\s+(.+)$", re.IGNORECASE | re.DOTALL),
        "observe",
        "observe",
        ("topic",),
    ),
    # 4. Plan slash command — /plan <topic>
    (
        re.compile(r"^/plan\s+(.+)$", re.IGNORECASE | re.DOTALL),
        "plan",
        "synthesize",
        ("topic",),
    ),
    # 5. Verify slash command — /verify <artifact>
    (
        re.compile(r"^/verify\s+(.+)$", re.IGNORECASE | re.DOTALL),
        "verify",
        "synthesize",
        ("artifact",),
    ),
    # 6. Inline @mention to a worker — @<name> <text>  → slash_<name>
    (
        re.compile(r"^@(\w+)\s+(.+)$", re.IGNORECASE | re.DOTALL),
        "slash_mention",
        "dispatch",
        ("name", "body"),
    ),
    # 7. Confirmation replies — go / continue building / yes / do it
    (
        re.compile(r"^(go|continue building|continue|yes|do it|proceed|ship it)$", re.IGNORECASE),
        "confirm",
        "dispatch",
        (),
    ),
    # 8. Negation replies — no / stop / wait / hold
    (
        re.compile(r"^(no|stop|wait|hold|cancel|don't|abort)$", re.IGNORECASE),
        "reject",
        "ask_first",
        (),
    ),
    # 9. Help / status — /help, /status, /health
    (
        re.compile(r"^/(help|status|health)$", re.IGNORECASE),
        "help",
        "observe",
        (),
    ),
    # 10. Inbox / review — /inbox, /review
    (
        re.compile(r"^/(inbox|review)$", re.IGNORECASE),
        "inbox",
        "observe",
        (),
    ),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def classify_l1(text: str) -> Intent:
    """L1 regex pre-filter.

    Walks the registry in order. First match wins. Returns an Intent with
    source='L1' and confidence=1.0. If no rule matches, returns the
    fail-closed Intent with intent='ask_first', confidence=0.0, lane='ask_first',
    source='fallback'. The L2/L3 layers are not consulted here.
    """
    if not isinstance(text, str):
        text = str(text)

    for pattern, intent_name, lane, group_keys in _REGISTRY:
        m = pattern.match(text)
        if not m:
            continue
        payload: Dict[str, str] = {"raw": text}
        # Bind regex capture groups (in order) to group_keys
        for key, value in zip(group_keys, m.groups()):
            payload[key] = value
        return Intent(
            intent=intent_name,
            confidence=1.0,
            payload=payload,
            lane=lane,
            matched_pattern=pattern.pattern,
            source="L1",
        )

    # Fail-closed default. Per §4.1: "Never-match → ask-first".
    return Intent(
        intent="ask_first",
        confidence=0.0,
        payload={"raw": text},
        lane="ask_first",
        matched_pattern=None,
        source="fallback",
    )


def classify(text: str) -> Intent:
    """Top-level classifier. v1 only implements L1; L2/L3 are stubs.

    Order: L1 → (L2 if L1 is low-confidence) → (L3 if L2 is ambiguous).
    For v1, L1 confidence is binary (1.0 on match, 0.0 on no-match), so the
    cascade is effectively: L1-matches → L1 result, else → ask_first.

    L2 and L3 raise NotImplementedError; once implemented, classify() will
    cascade through them and return the first non-ask_first result, or
    ask_first if all layers fall through.
    """
    l1 = classify_l1(text)
    if l1.lane != "ask_first":
        return l1

    # L2: vector similarity against a labeled intent bank
    l2 = classify_l2(text)
    if l2.lane != "ask_first":
        return l2

    # L3: M3 LLM classification with structured output
    l3 = classify_l3(text, context={})
    return l3


def classify_l2(text: str) -> Intent:
    """L2 vector similarity classifier — STUB.

    v1 design doc §4.1: L2 is a small embedding model (M2.7-class, fast),
    ~50ms latency, ~95% coverage of known intents.

    Returns an Intent with lane='ask_first' (fail-closed) once implemented.
    """
    raise NotImplementedError(
        "L2 = vector similarity against labeled intent bank; "
        "see v1 design doc Section 4.1."
    )


def classify_l3(text: str, context: dict) -> Intent:
    """L3 M3 LLM classifier — STUB.

    v1 design doc §4.1: L3 is M3 (chief-only) with structured output,
    ~1-3s latency, long-tail coverage.

    Returns an Intent with lane='ask_first' (fail-closed) once implemented.
    """
    raise NotImplementedError(
        "L3 = M3 LLM classification with structured output; "
        "see v1 design doc Section 4.1."
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    SAMPLES: List[str] = [
        "/capture architect the Mavis harness",
        "/dispatch builder scaffold context_loader.py",
        "@coder build the auth module",
        "go",
        "ship it",
        "what is the status of plan_c2389043?",  # → ask_first
        "/plan the next sprint",
        "no",  # → ask_first (reject)
    ]

    print("=" * 72)
    print("command_router self-test — L1 regex pre-filter (v1 design doc §4.1)")
    print("=" * 72)
    for s in SAMPLES:
        r = classify_l1(s)
        print()
        print(f"  input    : {s!r}")
        print(f"  intent   : {r.intent}")
        print(f"  lane     : {r.lane}")
        print(f"  conf     : {r.confidence}")
        print(f"  payload  : {r.payload}")
        print(f"  pattern  : {r.matched_pattern}")
        print(f"  source   : {r.source}")
    print()
    print("=" * 72)
    print("DONE — 8 samples classified; no L2/L3 calls (stubs NotImplementedError).")
