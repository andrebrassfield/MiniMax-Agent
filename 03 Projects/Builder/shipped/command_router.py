# command_router.py — Sprint 1: Mavis Harness Blueprint §3.1
# Deterministic regex pre-filter; no LLM in the loop.
# Source: 03 Projects/Builder/drafts/mavis_harness_blueprint.md §3.1

import re
from dataclasses import dataclass, field
from typing import Optional, List


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RouterResult:
    skill: Optional[str]       # None = no match; hand to LLM
    reason: str                 # reason code
    matched_pattern: Optional[str]
    blocked: bool = False


@dataclass
class BlockedByRouter(RouterResult):
    """Returned when an input matches a framework-drift block pattern."""
    input_text: str = ""

    def __init__(self, reason: str, matched_pattern: str, input_text: str):
        super().__init__(
            skill=None,
            reason=reason,
            matched_pattern=matched_pattern,
            blocked=True,
        )
        self.input_text = input_text


# ---------------------------------------------------------------------------
# Registry — order = priority (first match wins)
# ---------------------------------------------------------------------------
# Columns: (compiled_pattern, skill_or_BLOCK, reason_code)
# BLOCK_ prefix on reason = return BlockedByRouter instead of RouterResult.
# ---------------------------------------------------------------------------

_REGISTRY: List[tuple] = [
    # ---- Dispatch patterns (7) ----
    (
        re.compile(r"^Mavis,\s*boot", re.IGNORECASE),
        "session-boot-sync",
        "BOOT_PATTERN",
    ),
    (
        re.compile(r"^/plan\b"),
        "plan-mode",
        "SLASH_PLAN",
    ),
    (
        re.compile(r"^/verify\b"),
        "gepa-evaluator",
        "SLASH_VERIFY",
    ),
    (
        re.compile(r"^/inbox\b"),
        "process-inbox",
        "SLASH_INBOX",
    ),
    (
        re.compile(r"^/health\b"),
        "gibson-watcher",
        "SLASH_HEALTH",
    ),
    (
        re.compile(r"^/research\b"),
        "mavis-team-plan",
        "SLASH_RESEARCH",
    ),
    (
        re.compile(r"^/blueprint\b"),
        "blueprint-mode",
        "SLASH_BLUEPRINT",
    ),
    # ---- Block patterns (4) ----
    # Unauthorized self-shipping: worker moving a file to shipped/ without Verifier PASS
    (
        re.compile(r"mvs_[a-z0-9]+\s*→\s*shipped"),
        "BLOCK",
        "BLOCK_SELF_SHIP",
    ),
    # Bypassing chunked-write discipline: Write call claiming >30KB content
    (
        re.compile(r"\bWrite\b.*?(\d+)\s*KB", re.IGNORECASE | re.DOTALL),
        "BLOCK",
        "BLOCK_MONOLITHIC_WRITE",
    ),
    # Hardcoding UNVERIFIED token multipliers in write context
    (
        re.compile(r"(?:\bWrite\b|filePath|content).*?(1\.3x|1\.8x|0\.2 token/char)", re.IGNORECASE | re.DOTALL),
        "BLOCK",
        "BLOCK_HARDCODED_MULTIPLIER",
    ),
    # Skipping the Producer→Trust loop: worker self-verification attempt
    (
        re.compile(r"verify\s+my\s+own|pass\s+this\s+without\s+verifier", re.IGNORECASE),
        "BLOCK",
        "BLOCK_SELF_VERIFY",
    ),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def route(user_input: str) -> RouterResult:
    """
    Route user_input through the registry in order.

    Returns:
        RouterResult — skill + reason + matched_pattern (dispatch or NO_MATCH)
        BlockedByRouter — blocked == True with reason + matched_pattern + input_text

    Determinism contract: pure regex, first match wins, no LLM calls.
    """
    for pattern, skill_or_block, reason in _REGISTRY:
        if pattern.search(user_input):
            if "BLOCK_" in reason:
                # Additional gate for BLOCK_MONOLITHIC_WRITE: only block if size > 30
                if reason == "BLOCK_MONOLITHIC_WRITE":
                    size_match = re.search(r"(\d+)\s*KB", user_input, re.IGNORECASE)
                    if size_match and int(size_match.group(1)) > 30:
                        return BlockedByRouter(
                            reason=reason,
                            matched_pattern=pattern.pattern,
                            input_text=user_input,
                        )
                    # Size <= 30KB: no block, continue to next pattern
                    continue
                return BlockedByRouter(
                    reason=reason,
                    matched_pattern=pattern.pattern,
                    input_text=user_input,
                )
            return RouterResult(
                skill=skill_or_block,
                reason=reason,
                matched_pattern=pattern.pattern,
            )
    return RouterResult(skill=None, reason="NO_MATCH", matched_pattern=None)