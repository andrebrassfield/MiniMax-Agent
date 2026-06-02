"""
Tests for the full ingestion pipeline (end-to-end with real fetches).

These tests hit real URLs and the local filesystem. They're marked
with the `integration` pytest marker so the fast unit tests can run
without network.
"""

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from intake import convert, scrape, sniff  # noqa: E402

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


# ============================================================
# SCRAPING (real network)
# ============================================================

class TestScraping:
    def test_fetch_wikipedia(self):
        """Sanity check: Scrapling can fetch a Wikipedia page."""
        url = "https://en.wikipedia.org/wiki/Markdown"
        html = scrape.fetch(url)
        assert "Markdown" in html
        assert "<html" in html.lower()
        assert len(html) > 10_000  # a real page, not a stub

    def test_fetch_anthropic_docs(self):
        """Fetch an Anthropic docs page (may be cached, may be 200)."""
        url = "https://docs.anthropic.com/en/docs/intro"
        try:
            html = scrape.fetch(url)
            assert len(html) > 1_000
        except scrape.ScrapeError as e:
            # Allow graceful skip if Anthropic blocks (Cloudflare, etc.)
            pytest.skip(f"Anthropic docs fetch blocked: {e}")


# ============================================================
# FULL PIPELINE (real network + real conversion)
# ============================================================

class TestFullPipeline:
    def test_ingest_wikipedia_url(self, tmp_path):
        """End-to-end: URL → fetch → markdown → compress → audit log."""
        # We need a drop_root for path validation; URLs skip the check
        # so we pass a fake root.
        from direct_intake import ingest

        url = "https://en.wikipedia.org/wiki/Markdown"
        ir = ingest(url, drop_root=tmp_path)

        # Record sanity
        assert ir.record.type == "url"
        assert ir.record.converter == "scrapling"
        assert ir.record.status == "ready"
        assert ir.record.intake_id

        # Markdown sanity
        assert len(ir.markdown) > 1_000
        assert "Markdown" in ir.markdown

        # Compression sanity
        assert ir.compressed.original_tokens > 100
        # The compression ratio should be < 1.0 (some savings)
        assert ir.compressed.compression_ratio <= 1.0
        assert "markdown_clean" in ir.compressed.algorithms_applied
        assert "whitespace_squash" in ir.compressed.algorithms_applied

        # CCR retrievability
        from intake.compress import get_store
        assert get_store().has(ir.compressed.ccr_hash)
        assert get_store().get(ir.compressed.ccr_hash) == ir.markdown

    def test_ingest_local_text_file(self, tmp_path):
        """End-to-end: local text file → passthrough → compress → audit log."""
        from direct_intake import ingest

        f = tmp_path / "note.txt"
        f.write_text(
            "# Test Note\n\n"
            "This is a test paragraph with enough content to be worth "
            "compressing. The quick brown fox jumps over the lazy dog. " * 30
        )

        ir = ingest(str(f), drop_root=tmp_path)
        assert ir.record.type == "text"
        assert ir.record.converter == "passthrough"
        assert "Test Note" in ir.markdown
        # Note: passthrough is unconverted, but compression still runs
        assert ir.compressed.original_tokens > 100

    def test_ingest_local_markdown_file(self, tmp_path):
        """A markdown file is treated as text (passthrough)."""
        from direct_intake import ingest

        f = tmp_path / "note.md"
        f.write_text("# Title\n\nContent here. " * 50)

        ir = ingest(str(f), drop_root=tmp_path)
        assert ir.record.type == "text"
        assert "Title" in ir.markdown

    def test_ingest_rejects_oversize(self, tmp_path):
        """A file over the cap is rejected with a clear error."""
        from direct_intake import ingest

        f = tmp_path / "huge.txt"
        f.write_bytes(b"x" * (sniff.MAX_FILE_SIZE_BYTES + 1))

        with pytest.raises(sniff.SniffError, match="file too large"):
            ingest(str(f), drop_root=tmp_path)

    def test_ingest_rejects_unsafe_url(self, tmp_path):
        """A URL to localhost is rejected."""
        from direct_intake import ingest

        with pytest.raises(sniff.SniffError, match="blocked host"):
            ingest("http://localhost:8080/admin", drop_root=tmp_path)
