"""
summarize.py — M3-summary compression mode for the intake pipeline.

Esalen posture: this module is a thin deterministic shim. It does NOT call
any LLM. It prepares a SummaryRequest (stores the original in CCR, produces
a prompt for M3), and applies a SummaryResult (records the summary, computes
the new compression ratio). The M3 call itself happens in the orchestrator
(Mavis / a worker / the human reviewer) — not in this module.

The reason: an LLM-in-the-deterministic-layer is the canonical "model judges
itself" Foxconn pattern (per 99 _system/ESALEN-NOT-FOXCONN.md audit Q2).
The regex layer (compress.py) is the thin deterministic shim. The M3 call
is a separate orchestrator step that USES the regex-compressed text as
input and EMITS a structured summary. CCR remains the escape hatch.

Flow:
    1. Pipeline produces regex-compressed text (compress.py).
    2. If --m3-summary-request-out is set, pipeline calls make_request() to
       store the original in CCR and write a SummaryRequest sidecar.
    3. The orchestrator (M3 / human) reads the sidecar, calls render_prompt()
       to get the prompt, emits a summary, and calls apply_summary() with
       the result. The summary is written next to the request.
    4. The pipeline's intake-log record is updated to reflect the M3 summary.

This file is zero-LLM. If you grep for "import openai" or "import anthropic"
or "from mavis" in this file, you should find nothing.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .compress import CCRStore, CompressedBlock

log = logging.getLogger(__name__)

__version__ = "0.1.0"


# ============================================================
# DATACLASSES
# ============================================================

@dataclass
class M3SummaryRequest:
    """A request to M3 to summarize a piece of text.

    The original text is already in the CCR store (keyed by original_ccr_hash);
    the model does NOT need to receive the original. The model receives the
    regex-compressed text and emits a structured summary.
    """

    request_id: str                       # unique id for this request
    source: str                           # original source (URL or file path)
    original_ccr_hash: str                # SHA-256 of the ORIGINAL text
    compressed_text: str                  # regex-compressed text (input to M3)
    compressed_tokens: int                # tokens of the regex-compressed text
    prompt_hint: str = ""                 # optional context for the model
    created_at: str = ""                  # ISO 8601
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class M3SummaryResult:
    """The output of the M3-summary step. CCR is preserved (escape hatch)."""

    request_id: str
    original_ccr_hash: str                # SHA-256 of the ORIGINAL (for retrieval)
    summary_text: str                     # the M3-produced summary
    summary_tokens: int                   # tokens of the summary
    original_tokens: int                  # tokens of the regex-compressed input
    summary_ratio: float                  # summary_tokens / original_tokens
    savings_pct: float                    # (1 - ratio) * 100
    algorithms_applied: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# REQUEST / APPLY (deterministic, no LLM)
# ============================================================

def make_request(
    source: str,
    compressed: "CompressedBlock",
    *,
    ccr_store: "CCRStore | None" = None,
    prompt_hint: str = "",
    request_id: str = "",
) -> M3SummaryRequest:
    """Build an M3SummaryRequest. Stores the regex-compressed text in CCR.

    Note: the regex-compressed text is the input to M3, not the original.
    The original is already in CCR (stored by direct_intake.ingest()).
    """
    from . import compress as _compress

    if ccr_store is None:
        ccr_store = _compress.get_store()

    # Store the regex-compressed text under its own hash, so the orchestrator
    # can also opt back into the regex version if the summary loses signal.
    ccr_store.put(compressed.text)

    import time
    if not request_id:
        import uuid
        request_id = f"m3sum-{int(time.time())}-{uuid.uuid4().hex[:6]}"

    return M3SummaryRequest(
        request_id=request_id,
        source=source,
        original_ccr_hash=compressed.ccr_hash,
        compressed_text=compressed.text,
        compressed_tokens=compressed.compressed_tokens,
        prompt_hint=prompt_hint,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
    )


def render_prompt(request: M3SummaryRequest) -> str:
    """Render the prompt for M3. Pure deterministic — no LLM call.

    The prompt is intentionally short. The model gets the regex-compressed
    text and is asked to emit a structured markdown summary. CCR is mentioned
    so the model knows it can opt back into the original via ccr_retrieve.
    """
    return f"""You are summarizing content that was just fetched and regex-compressed
by the Mavis intake pipeline. The original is held in the CCR store
(content-addressable compression with retrieval); the regex-compressed
version is below.

CCR hash of the original: {request.original_ccr_hash[:16]}...

Your task: produce a faithful, dense, structured summary in markdown.
Preserve all key facts, named entities, code references, and structure.
Do NOT invent. If something is ambiguous in the compressed version, note
it explicitly as "[ambiguous in compressed input]". The reader should be
able to use your summary as a working substitute for the original; the
CCR hash is the escape hatch for full-fidelity detail.

Source: {request.source}
{('Hint: ' + request.prompt_hint) if request.prompt_hint else ''}

--- BEGIN COMPRESSED INPUT ({request.compressed_tokens} tokens) ---

{request.compressed_text}

--- END COMPRESSED INPUT ---

Emit ONLY the summary markdown. No preamble, no postamble."""


def apply_summary(
    request: M3SummaryRequest,
    summary_text: str,
    *,
    store_summary_in_ccr: bool = True,
    ccr_store: "CCRStore | None" = None,
) -> M3SummaryResult:
    """Apply an M3-produced summary to a request. Deterministic, no LLM.

    Computes the new ratio (summary vs regex-compressed input) and records
    the result. Optionally stores the summary in CCR (so ccr_retrieve works
    on the summary too — but the original is the primary CCR entry).
    """
    from . import compress as _compress

    if ccr_store is None:
        ccr_store = _compress.get_store()

    if not summary_text or not summary_text.strip():
        raise ValueError("summary_text is empty")

    summary_tokens = _compress.estimate_tokens(summary_text)
    original_tokens = max(1, request.compressed_tokens)
    ratio = summary_tokens / original_tokens
    savings_pct = round((1.0 - ratio) * 100, 1)

    algorithms = ["m3_summary"]

    if store_summary_in_ccr:
        # The summary is also retrievable by its own hash; the original is
        # retrievable by request.original_ccr_hash.
        ccr_store.put(summary_text)

    return M3SummaryResult(
        request_id=request.request_id,
        original_ccr_hash=request.original_ccr_hash,
        summary_text=summary_text,
        summary_tokens=summary_tokens,
        original_tokens=original_tokens,
        summary_ratio=round(ratio, 3),
        savings_pct=savings_pct,
        algorithms_applied=algorithms,
    )


# ============================================================
# JSON I/O (deterministic, no LLM)
# ============================================================

def save_request_json(request: M3SummaryRequest, path: Path) -> Path:
    """Persist a request to disk as JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(request.to_dict(), indent=1, ensure_ascii=False))
    log.info("wrote M3SummaryRequest → %s", path)
    return path


def load_request_json(path: Path) -> M3SummaryRequest:
    """Load a request from disk."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return M3SummaryRequest(
        request_id=data["request_id"],
        source=data["source"],
        original_ccr_hash=data["original_ccr_hash"],
        compressed_text=data["compressed_text"],
        compressed_tokens=data["compressed_tokens"],
        prompt_hint=data.get("prompt_hint", ""),
        created_at=data.get("created_at", ""),
        meta=data.get("meta", {}),
    )


def save_summary_json(result: M3SummaryResult, path: Path) -> Path:
    """Persist a summary result to disk as JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=1, ensure_ascii=False))
    log.info("wrote M3SummaryResult → %s", path)
    return path


# ============================================================
# CONVENIENCE: end-to-end ratio accounting
# ============================================================

def overall_ratio(
    original_compressed: "CompressedBlock",
    summary_result: M3SummaryResult,
) -> dict:
    """Compute the end-to-end compression ratio (original → M3 summary).

    This is what the caller reports as the "headroom ratio" — the chain is
    original_text → regex_compress → m3_summarize → model_input.
    """
    original_tokens = max(1, original_compressed.original_tokens)
    summary_tokens = summary_result.summary_tokens
    ratio = summary_tokens / original_tokens
    return {
        "original_tokens": original_tokens,
        "regex_compressed_tokens": original_compressed.compressed_tokens,
        "m3_summary_tokens": summary_tokens,
        "regex_ratio": round(original_compressed.compression_ratio, 3),
        "end_to_end_ratio": round(ratio, 3),
        "end_to_end_savings_pct": round((1.0 - ratio) * 100, 1),
        "ccr_hash": original_compressed.ccr_hash,
    }
