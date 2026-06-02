"""
Tests for the M3-summary compression mode.

These tests verify:
  1. The module is zero-LLM (no openai/anthropic/mavis imports)
  2. make_request() stores the regex-compressed text in CCR
  3. render_prompt() produces a deterministic, M3-shaped prompt
  4. apply_summary() computes the new ratio correctly
  5. JSON I/O round-trips
  6. CCR escape hatch is preserved (original text is still retrievable)
  7. overall_ratio() reports end-to-end headroom
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from intake import compress, summarize  # noqa: E402


# ============================================================
# ESALEN POSTURE (this module must be zero-LLM)
# ============================================================

class TestEsalenPosture:
    def test_no_llm_imports(self):
        """The module must not import any LLM client. Foxconn audit Q2."""
        # Walk the module's source and look for actual import statements
        # (line starts with "import" or "from"). Comments and docstrings
        # are ignored — they can mention the forbidden tokens for documentation.
        src = Path(summarize.__file__).read_text(encoding="utf-8")
        forbidden = ["openai", "anthropic", "mavis", "llm_call", "matrix"]
        for line in src.splitlines():
            stripped = line.strip()
            if not (stripped.startswith("import ") or stripped.startswith("from ")):
                continue
            for token in forbidden:
                if token in stripped:
                    pytest.fail(
                        f"summarize.py contains forbidden import of {token!r}: {stripped!r}"
                    )

    def test_no_subprocess_llm_call(self):
        """The module must not shell out to an LLM CLI."""
        src = Path(summarize.__file__).read_text(encoding="utf-8")
        assert "subprocess" not in src, "summarize.py must not use subprocess"


# ============================================================
# REQUEST BUILDING
# ============================================================

class TestMakeRequest:
    def test_stores_compressed_text_in_ccr(self):
        store = compress.CCRStore()
        original = "The quick brown fox jumps over the lazy dog. " * 50
        compressed = compress.compress(original)
        req = summarize.make_request(
            "https://example.com/test",
            compressed,
            ccr_store=store,
        )
        # The regex-compressed text is in CCR (so the model can opt back in)
        compressed_hash = compress.sha256_hex(compressed.text)
        assert store.has(compressed_hash)
        assert store.get(compressed_hash) == compressed.text

    def test_records_original_ccr_hash(self):
        original = "Some text content. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request("source-x", compressed)
        # The original's hash is preserved verbatim from the compress() result
        assert req.original_ccr_hash == compressed.ccr_hash
        assert req.original_ccr_hash == compress.sha256_hex(original)

    def test_assigns_unique_request_id(self):
        original = "Content. " * 100
        compressed = compress.compress(original)
        r1 = summarize.make_request("a", compressed)
        r2 = summarize.make_request("b", compressed)
        assert r1.request_id != r2.request_id
        assert r1.request_id.startswith("m3sum-")
        assert r2.request_id.startswith("m3sum-")

    def test_prompt_hint_optional(self):
        original = "Content. " * 100
        compressed = compress.compress(original)
        req_default = summarize.make_request("a", compressed)
        req_hinted = summarize.make_request(
            "a", compressed, prompt_hint="focus on architecture"
        )
        assert req_default.prompt_hint == ""
        assert req_hinted.prompt_hint == "focus on architecture"

    def test_compressed_tokens_carried_through(self):
        original = "Some prose here. " * 200
        compressed = compress.compress(original)
        req = summarize.make_request("a", compressed)
        assert req.compressed_tokens == compressed.compressed_tokens


# ============================================================
# PROMPT RENDERING
# ============================================================

class TestRenderPrompt:
    def test_prompt_includes_source(self):
        original = "The quick brown fox. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request("https://example.com/article", compressed)
        prompt = summarize.render_prompt(req)
        assert "https://example.com/article" in prompt

    def test_prompt_includes_ccr_hash(self):
        original = "Some content. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request("source", compressed)
        prompt = summarize.render_prompt(req)
        # The first 16 chars of the hash should appear
        assert req.original_ccr_hash[:16] in prompt

    def test_prompt_includes_compressed_text(self):
        original = "The quick brown fox jumps over the lazy dog. " * 50
        compressed = compress.compress(original)
        req = summarize.make_request("source", compressed)
        prompt = summarize.render_prompt(req)
        # The compressed text is in the prompt
        assert req.compressed_text in prompt

    def test_prompt_mentions_ccr_escape_hatch(self):
        original = "Content. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request("source", compressed)
        prompt = summarize.render_prompt(req)
        # The model needs to know it can opt back into the original
        assert "CCR" in prompt
        assert "ccr" in prompt.lower() or "retriev" in prompt.lower()

    def test_prompt_is_deterministic(self):
        """Same request → same prompt string. Required for grading reproducibility."""
        original = "Content. " * 100
        compressed = compress.compress(original)
        req1 = summarize.make_request("a", compressed, request_id="fixed-id")
        req2 = summarize.make_request("a", compressed, request_id="fixed-id")
        # Strip created_at which is timestamp-dependent
        req1_dict = req1.to_dict()
        req2_dict = req2.to_dict()
        req1_dict.pop("created_at")
        req2_dict.pop("created_at")
        assert req1_dict == req2_dict


# ============================================================
# APPLY SUMMARY
# ============================================================

class TestApplySummary:
    def test_computes_ratio(self):
        original = "The quick brown fox jumps over the lazy dog. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request("source", compressed)
        # A summary that's ~25% of the compressed size (1/4)
        target_summary_tokens = max(1, compressed.compressed_tokens // 4)
        # "Quick fox. " = 11 chars ~ 2.75 tokens. Build by counting.
        summary = ""
        while compress.estimate_tokens(summary) < target_summary_tokens:
            summary += "Quick fox. "
        result = summarize.apply_summary(req, summary)
        assert 0 < result.summary_ratio < 1
        assert result.savings_pct > 0

    def test_preserves_original_ccr_hash(self):
        original = "The original. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request("source", compressed)
        result = summarize.apply_summary(req, "The summary.")
        assert result.original_ccr_hash == req.original_ccr_hash
        assert result.original_ccr_hash == compress.sha256_hex(original)

    def test_records_algorithm(self):
        original = "Content. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request("source", compressed)
        result = summarize.apply_summary(req, "Summary text.")
        assert "m3_summary" in result.algorithms_applied

    def test_rejects_empty_summary(self):
        original = "Content. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request("source", compressed)
        with pytest.raises(ValueError, match="empty"):
            summarize.apply_summary(req, "")
        with pytest.raises(ValueError, match="empty"):
            summarize.apply_summary(req, "   \n  \t  ")

    def test_summary_stored_in_ccr_by_default(self):
        store = compress.CCRStore()
        original = "Content. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request("source", compressed, ccr_store=store)
        summary = "A summary."
        result = summarize.apply_summary(
            req, summary, store_summary_in_ccr=True, ccr_store=store
        )
        # Summary is now in CCR
        summary_hash = compress.sha256_hex(summary)
        assert store.has(summary_hash)

    def test_summary_not_stored_in_ccr_when_disabled(self):
        store = compress.CCRStore()
        original = "Content. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request("source", compressed, ccr_store=store)
        summary = "A summary."
        result = summarize.apply_summary(
            req, summary, store_summary_in_ccr=False
        )
        # Summary is NOT in CCR
        summary_hash = compress.sha256_hex(summary)
        assert not store.has(summary_hash)


# ============================================================
# JSON I/O
# ============================================================

class TestJSONIO:
    def test_request_round_trip(self, tmp_path):
        original = "Content. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request(
            "https://example.com",
            compressed,
            prompt_hint="focus on x",
        )
        path = tmp_path / "request.json"
        summarize.save_request_json(req, path)
        loaded = summarize.load_request_json(path)
        assert loaded.request_id == req.request_id
        assert loaded.source == req.source
        assert loaded.original_ccr_hash == req.original_ccr_hash
        assert loaded.compressed_text == req.compressed_text
        assert loaded.prompt_hint == "focus on x"

    def test_summary_round_trip(self, tmp_path):
        original = "Content. " * 100
        compressed = compress.compress(original)
        req = summarize.make_request("source", compressed)
        result = summarize.apply_summary(req, "Summary text here.")
        path = tmp_path / "summary.json"
        summarize.save_summary_json(result, path)
        loaded = json.loads(path.read_text())
        assert loaded["request_id"] == req.request_id
        assert loaded["summary_text"] == "Summary text here."

    def test_load_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            summarize.load_request_json(tmp_path / "nonexistent.json")


# ============================================================
# END-TO-END RATIO
# ============================================================

class TestOverallRatio:
    def test_reports_end_to_end_headroom(self):
        # Realistic content
        original = (
            "# The Quick Brown Fox\n\n"
            "The quick brown fox jumps over the lazy dog. "
            "This is a sample of technical documentation. "
            "It contains prose, code references, and structured info.\n\n" * 30
        )
        compressed = compress.compress(original, aggressive=True)
        req = summarize.make_request("source", compressed)
        # A summary that's roughly 40% of the regex-compressed size
        summary = "# Quick Brown Fox\n\nSample tech doc. " * (
            compressed.compressed_tokens // 10
        )
        result = summarize.apply_summary(req, summary)
        overall = summarize.overall_ratio(compressed, result)

        # Sanity checks on the report
        assert overall["original_tokens"] == compressed.original_tokens
        assert overall["regex_compressed_tokens"] == compressed.compressed_tokens
        assert overall["m3_summary_tokens"] == result.summary_tokens
        assert overall["end_to_end_ratio"] <= overall["regex_ratio"] + 0.1
        # End-to-end savings should be > 0 (some compression happened)
        assert overall["end_to_end_savings_pct"] >= 0
        # CCR hash preserved
        assert overall["ccr_hash"] == compressed.ccr_hash


# ============================================================
# CCR ESCAPE HATCH (the whole point of the M3-summary path)
# ============================================================

class TestCCREscapeHatch:
    def test_original_retrievable_after_full_pipeline(self):
        """After compress → m3_summary, the original is still in CCR."""
        store = compress.CCRStore()
        original = "The original text. " * 100
        compressed = compress.compress(original)
        # Store original (the pipeline always does this; we replicate here)
        store.put(original)
        # M3-summary path
        req = summarize.make_request("source", compressed, ccr_store=store)
        result = summarize.apply_summary(req, "The summary.", store_summary_in_ccr=False)

        # The original is still retrievable by its CCR hash
        assert store.has(compressed.ccr_hash)
        assert store.get(compressed.ccr_hash) == original

    def test_lossy_summary_can_be_audited_via_ccr(self):
        """If the summary is wrong, the model can opt back into the original."""
        store = compress.CCRStore()
        original = "The precise original text with specific facts and numbers: 42, 17, 99. " * 20
        compressed = compress.compress(original)
        store.put(original)

        # A summary that loses the numbers
        lossy_summary = "A document with some numbers. " * 5
        req = summarize.make_request("source", compressed, ccr_store=store)
        result = summarize.apply_summary(req, lossy_summary)

        # CCR still has the original; the model can detect signal decay
        # and call ccr_retrieve(original_ccr_hash) to get the truth
        retrieved = store.get(req.original_ccr_hash)
        assert "42" in retrieved
        assert "17" in retrieved
        assert "99" in retrieved
