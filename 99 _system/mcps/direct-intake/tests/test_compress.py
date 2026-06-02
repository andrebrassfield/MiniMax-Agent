"""
Tests for the Headroom-style deterministic compression.

The compression layer is the budget multiplier. These tests verify:
  1. It reduces tokens on dense content
  2. It preserves content (lossless within the algorithm)
  3. CCR is reversible — original retrievable by hash
  4. Aggressive mode strips stopwords
  5. Non-prose content (code/JSON) is left alone
"""

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from intake import compress  # noqa: E402


# ============================================================
# BASICS
# ============================================================

class TestCompressionBasics:
    def test_empty_string(self):
        c = compress.compress("")
        assert c.text == ""
        assert c.original_tokens == 0
        assert c.compressed_tokens == 0
        assert c.compression_ratio == 1.0

    def test_small_text_not_compressed(self):
        """Below the threshold, no compression is applied (overhead not worth it)."""
        text = "Short text."
        c = compress.compress(text, min_tokens_to_compress=100)
        assert c.text == text
        assert c.algorithms_applied == []
        assert c.compression_ratio == 1.0

    def test_token_estimation(self):
        # ~4 chars per token
        assert compress.estimate_tokens("") == 1
        assert compress.estimate_tokens("abcd") == 1
        assert compress.estimate_tokens("a" * 100) == 25
        assert compress.estimate_tokens("a" * 1000) == 250

    def test_sha256_hex(self):
        h = compress.sha256_hex("hello")
        assert len(h) == 64
        assert h == compress.sha256_hex("hello")
        assert h != compress.sha256_hex("world")


# ============================================================
# MARKDOWN CLEAN
# ============================================================

class TestMarkdownClean:
    def test_collapses_blank_lines(self):
        text = "a\n\n\n\n\nb"
        out = compress.markdown_clean(text)
        assert out == "a\n\nb"

    def test_removes_trailing_whitespace(self):
        text = "line 1   \nline 2\t\t\nline 3"
        out = compress.markdown_clean(text)
        assert "   " not in out
        assert "\t\t" not in out

    def test_strips_html_leftovers(self):
        text = "hello<br>world&nbsp;foo&amp;bar"
        out = compress.markdown_clean(text)
        assert "<br>" not in out
        assert "&nbsp;" not in out
        assert "&amp;" not in out
        assert "foo&bar" in out

    def test_collapses_decorative_lines(self):
        text = "above\n\n=========\n\nbelow"
        out = compress.markdown_clean(text)
        assert "=========" not in out

    def test_strips_bold_on_single_char(self):
        text = "look at **a** and **z** here"
        out = compress.markdown_clean(text)
        assert "**a**" not in out
        assert "**z**" not in out


# ============================================================
# WHITESPACE SQUASH
# ============================================================

class TestWhitespaceSquash:
    def test_normalizes_line_endings(self):
        text = "a\r\nb\rc"
        out = compress.whitespace_squash(text)
        assert "\r" not in out
        assert out == "a\nb\nc"

    def test_collapses_horizontal_whitespace(self):
        text = "a    b\t\tc"
        out = compress.whitespace_squash(text)
        assert "    " not in out
        assert "\t\t" not in out


# ============================================================
# PROSE DENSITY DETECTION
# ============================================================

class TestProseDetection:
    def test_prose_dense(self):
        text = (
            "The quick brown fox jumps over the lazy dog. This is a sample of "
            "prose content that should be considered prose-dense because the "
            "majority of characters are in natural language sentences rather "
            "than in code blocks or structured data formats."
        )
        assert compress.is_prose_dense(text)

    def test_code_dense(self):
        text = (
            "def foo(x):\n"
            "    return x + 1\n"
            "def bar(y):\n"
            "    return y * 2\n"
            "def baz(z):\n"
            "    return z - 3\n"
        )
        assert not compress.is_prose_dense(text)

    def test_json_dense(self):
        text = '{"key": "value", "arr": [1, 2, 3], "nested": {"a": 1, "b": 2}}'
        assert not compress.is_prose_dense(text)


# ============================================================
# STOPWORD STRIPPING
# ============================================================

class TestStopwordStrip:
    def test_strips_stopwords_in_prose(self):
        # Use a realistic-length passage (>100 chars) so is_prose_dense returns True
        text = (
            "The quick brown fox jumps over the lazy dog and runs into the forest. "
            "It is a beautiful day in the neighborhood, and the fox is happy to be alive. "
            "The dog sleeps in the sun, and the cat watches from a nearby tree. "
            "All of the animals are content in their peaceful existence."
        )
        out = compress.stopword_strip(text)
        # Common stopwords removed (check with surrounding space to avoid substring matches)
        for stopword in [" the ", " and ", " is ", " a ", " in ", " of ", " to "]:
            assert stopword not in out.lower(), f"stopword {stopword!r} not stripped"
        # Content words preserved
        assert "quick" in out
        assert "fox" in out
        assert "forest" in out
        assert "dog" in out

    def test_does_not_touch_code(self):
        text = (
            "def the_func():\n"
            "    return the_value\n"
        )
        out = compress.stopword_strip(text)
        # Code preserved verbatim
        assert "def the_func" in out
        assert "return the_value" in out

    def test_does_not_touch_headings(self):
        text = "# The Quick Brown Fox\n\nA sample paragraph."
        out = compress.stopword_strip(text)
        # Heading preserved
        assert "# The Quick Brown Fox" in out


# ============================================================
# FULL COMPRESSION PIPELINE
# ============================================================

class TestFullCompression:
    def test_dense_markdown_compresses(self):
        """A real markdown document should compress meaningfully."""
        # Build a realistic markdown doc
        text = (
            "# The Quick Brown Fox\n\n"
            "The quick brown fox jumps over the lazy dog. "
            "This is a sample paragraph that has some prose in it. "
            "It contains the words 'the', 'and', 'is', 'a' which are stopwords. "
            "It also contains content words like 'fox', 'dog', 'sample'.\n\n"
            "## Section Two\n\n"
            "Another paragraph with more prose. The fox runs fast. The dog sleeps. "
            "The cat sits on the mat. The end.\n\n" * 10
        )
        c = compress.compress(text, aggressive=True)
        assert c.compression_ratio < 1.0, "should compress"
        assert c.compressed_tokens < c.original_tokens
        assert "markdown_clean" in c.algorithms_applied
        assert "whitespace_squash" in c.algorithms_applied
        assert "stopword_strip" in c.algorithms_applied
        # Content words preserved
        assert "fox" in c.text
        assert "dog" in c.text

    def test_code_does_not_compress_much(self):
        """Code is structurally important; aggressive mode should not touch it."""
        text = (
            "def calculate_total(items):\n"
            "    total = 0\n"
            "    for item in items:\n"
            "        total += item.price * item.quantity\n"
            "    return total\n\n" * 20
        )
        c = compress.compress(text, aggressive=True)
        # Whitespace might trim a tiny bit, but stopwords shouldn't fire
        assert "stopword_strip" not in c.algorithms_applied
        # Code still intact
        assert "def calculate_total" in c.text
        assert "return total" in c.text

    def test_ccr_hash_is_content_addressable(self):
        text1 = "hello world " * 50
        text2 = "hello world " * 50
        c1 = compress.compress(text1)
        c2 = compress.compress(text2)
        assert c1.ccr_hash == c2.ccr_hash  # same content → same hash

    def test_ccr_hash_stable_under_compression(self):
        """The hash should be of the ORIGINAL, not the compressed."""
        text = "The quick brown fox " * 50
        c = compress.compress(text, aggressive=True)
        assert c.ccr_hash == compress.sha256_hex(text)
        assert c.ccr_hash != compress.sha256_hex(c.text)


# ============================================================
# CCR STORE (reversibility)
# ============================================================

class TestCCRStore:
    def test_put_and_get(self):
        store = compress.CCRStore()
        original = "the original text " * 100
        h = store.put(original)
        assert store.has(h)
        assert store.get(h) == original

    def test_returns_none_for_unknown_hash(self):
        store = compress.CCRStore()
        assert store.get("0" * 64) is None
        assert not store.has("0" * 64)

    def test_size_and_clear(self):
        store = compress.CCRStore()
        assert store.size() == 0
        store.put("a")
        store.put("b")
        assert store.size() == 2
        store.clear()
        assert store.size() == 0

    def test_eviction(self):
        store = compress.CCRStore(max_entries=3)
        store.put("a")
        store.put("b")
        store.put("c")
        store.put("d")  # evicts "a"
        assert store.size() == 3
        assert not store.has(compress.sha256_hex("a"))
        assert store.has(compress.sha256_hex("d"))

    def test_round_trip_via_pipeline(self):
        """End-to-end: compress a block, then retrieve the original from the store."""
        store = compress.CCRStore()
        original = "The quick brown fox jumps over the lazy dog. " * 50
        c = compress.compress(original, aggressive=True)
        store.put(original)
        assert store.has(c.ccr_hash)
        assert store.get(c.ccr_hash) == original
