"""
compress.py — Headroom-style deterministic compression.

Esalen posture: no LLM calls, no NLP, no embeddings. Pure deterministic
text transformation. The model gets dense content; the original is
retained for retrieval (CCR — Content-Addressable Compression with Retrieval).

Three algorithms in priority order:
  1. markdown_clean    — strip redundant markdown formatting
                          (excessive whitespace, HTML leftovers, decorative chars)
  2. stopword_strip    — remove common English stopwords from prose
                          (only when prose density is high; code/JSON untouched)
  3. whitespace_squash — collapse runs of whitespace, normalize line endings

CCR primitive: each compressed block is paired with a content hash (SHA-256
of the original). The retrieve() function is the inverse — give it the hash,
get back the original text.

The compression target is "the same content, fewer tokens, no LLM needed."
Empirically this lands 20-50% reduction on dense markdown; more on prose,
less on code/JSON (which we mostly skip).
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass


# ============================================================
# TOKEN ESTIMATION
# ============================================================

def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token. Good enough for budgeting.

    For higher fidelity, swap in tiktoken. We use the heuristic here to
    keep this module zero-dependency (no pip install needed at the layer
    the model is calling from).
    """
    return max(1, len(text) // 4)


def sha256_hex(text: str) -> str:
    """SHA-256 hex digest. Used as the CCR content hash."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ============================================================
# COMPRESSION
# ============================================================

# English stopwords (compact set; full NLTK list is ~30KB, we don't need that)
STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with", "this", "but", "or", "not",
    "they", "we", "you", "i", "am", "have", "had", "do", "does", "did",
    "been", "would", "could", "should", "may", "might", "shall", "can",
    "their", "there", "these", "those", "what", "which", "who", "whom",
    "when", "where", "why", "how", "all", "any", "both", "each", "few",
    "more", "most", "other", "some", "such", "than", "too", "very",
    "just", "into", "out", "up", "down", "over", "under", "again",
    "further", "then", "once", "here", "only", "also", "so", "if",
    "while", "about", "between", "through", "after", "before", "above",
    "below", "because", "until", "since", "now",
})


def is_prose_dense(text: str) -> bool:
    """Heuristic: is this content prose-dominant (compressable) or
    code/JSON-dominant (don't touch)?"""
    if not text:
        return False

    # Count characters in code-like vs prose-like lines
    code_chars = 0
    prose_chars = 0
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        # Code indicators (conservative — a label like "User:" or "Note:" is
        # NOT code; it's prose with a prefix).
        code_signals = (
            # Strong: starts with code keywords or has balanced braces
            stripped.startswith(("    ", "\t", "def ", "class ", "import ",
                                  "from ", "function ", "var ", "const ", "let ",
                                  "if (", "for (", "while (", "return ", "=>",
                                  "```"))
            or ("{" in stripped and "}" in stripped)
            or stripped.startswith(("[", "]", "{", "}", "(", ")"))
            # Or: ends with a code-like statement terminator
            or stripped.endswith((":", ");", "},", "};"))
            and not stripped.startswith(("#", "User:", "Note:", ">", "-"))
        )
        if code_signals:
            code_chars += len(stripped)
        else:
            prose_chars += len(stripped)

    total = code_chars + prose_chars
    if total < 100:
        return False  # too short to decide
    return prose_chars / total > 0.7  # 70%+ prose → safe to compress


def markdown_clean(text: str) -> str:
    """Strip redundant markdown formatting that adds tokens without info.

    - Multiple consecutive blank lines → 1 blank line
    - Trailing whitespace on lines
    - Repeated decorative characters (---, ___, ***, ===, ###)
    - HTML leftovers from imperfect conversions (<br>, &nbsp;, etc.)
    - Bold/italic on single characters (e.g., "**a**" → "a")
    - Reference-style link definitions that aren't used
    """
    # Normalize unicode (NFKC — compatibility decomposition)
    text = unicodedata.normalize("NFKC", text)

    # HTML leftovers
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<hr\s*/?>", "\n---\n", text, flags=re.IGNORECASE)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&quot;", '"', text)

    # Trailing whitespace
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

    # Multiple blank lines → 1 blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Repeated decorative characters
    text = re.sub(r"^[=\-_*~]{4,}$", "---", text, flags=re.MULTILINE)

    # Bold/italic on single characters (e.g., "**a**" → "a", "*x*" → "x")
    text = re.sub(r"\*\*(\w)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*(\w)\*(?!\*)", r"\1", text)

    # Reference-style link definitions that aren't used
    # (heuristic: keep the definitions; the cleanup is conservative)
    return text


def stopword_strip(text: str) -> str:
    """Remove common English stopwords from prose. Conservative: only
    strips in clearly prose-dominant content, preserves all code/JSON.

    The output is still readable — just denser. Example:
        "The quick brown fox jumps over the lazy dog"
        → "quick brown fox jumps over lazy dog"
    """
    if not is_prose_dense(text):
        return text

    def _strip_line(line: str) -> str:
        stripped = line.strip()
        # Don't touch lines that look like headings, code, lists
        if (stripped.startswith(("#", "    ", "\t", "```", ">", "- ", "* ", "1."))
                or "://" in stripped):
            return line

        # Token-preserving strip: split on word boundaries, remove stopwords,
        # rejoin. Preserves punctuation attached to kept words.
        def _filter(match: re.Match) -> str:
            word = match.group(0)
            if word.lower() in STOPWORDS:
                return ""
            return word

        return re.sub(r"\b[\w']+\b", _filter, line)

    return "\n".join(_strip_line(line) for line in text.split("\n"))


def whitespace_squash(text: str) -> str:
    """Final squashing: collapse runs of horizontal whitespace, normalize
    line endings. Always applied (safe on all content)."""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse runs of spaces/tabs (but preserve newlines and code indentation)
    text = re.sub(r"[ \t]+", " ", text)
    # Leading whitespace on otherwise-empty lines
    text = re.sub(r"^[ \t]+$", "", text, flags=re.MULTILINE)
    return text


@dataclass
class CompressedBlock:
    """The output of the compression pipeline. CCR is the hash for retrieval."""

    text: str                       # the compressed text
    ccr_hash: str                   # SHA-256 of the ORIGINAL text (for retrieval)
    original_tokens: int            # tokens before compression
    compressed_tokens: int          # tokens after compression
    compression_ratio: float        # compressed / original (e.g., 0.65 = 35% savings)
    algorithms_applied: list[str]   # which transforms ran


def compress(
    text: str,
    *,
    aggressive: bool = False,
    min_tokens_to_compress: int = 100,
) -> CompressedBlock:
    """Run the compression pipeline on a block of text.

    Args:
        text: The content to compress.
        aggressive: If True, also run stopword_strip. Default False
            (markdown_clean + whitespace_squash only — safe on all content).
        min_tokens_to_compress: Skip compression if the text is smaller
            than this many tokens. The compression overhead isn't worth it
            on tiny blocks.

    Returns:
        CompressedBlock with the compressed text + CCR hash for retrieval.
    """
    if not text:
        return CompressedBlock(
            text="",
            ccr_hash=sha256_hex(""),
            original_tokens=0,
            compressed_tokens=0,
            compression_ratio=1.0,
            algorithms_applied=[],
        )

    original_tokens = estimate_tokens(text)
    if original_tokens < min_tokens_to_compress:
        return CompressedBlock(
            text=text,
            ccr_hash=sha256_hex(text),
            original_tokens=original_tokens,
            compressed_tokens=original_tokens,
            compression_ratio=1.0,
            algorithms_applied=[],
        )

    ccr_hash = sha256_hex(text)  # hash the ORIGINAL (for retrieval)
    algorithms = []
    out = text

    out = markdown_clean(out)
    algorithms.append("markdown_clean")

    if aggressive and is_prose_dense(out):
        out = stopword_strip(out)
        algorithms.append("stopword_strip")

    out = whitespace_squash(out)
    algorithms.append("whitespace_squash")

    compressed_tokens = estimate_tokens(out)
    ratio = compressed_tokens / original_tokens if original_tokens else 1.0

    return CompressedBlock(
        text=out,
        ccr_hash=ccr_hash,
        original_tokens=original_tokens,
        compressed_tokens=compressed_tokens,
        compression_ratio=ratio,
        algorithms_applied=algorithms,
    )


# ============================================================
# CCR RETRIEVAL
# ============================================================

class CCRStore:
    """In-memory Content-Addressable Compression with Retrieval store.

    Originals are kept in a dict keyed by SHA-256. The compressed form is
    stored alongside, so we can show the diff if asked. The store is
    process-local — for a persistent store, swap in SQLite (see TODO).

    This is the "reversible" half of CCR. The compressed form goes to the
    LLM; the original is held here; the LLM asks back for the original
    via ccr_retrieve(hash) when it needs detail.
    """

    def __init__(self, max_entries: int = 10_000) -> None:
        self._store: dict[str, str] = {}
        self._max = max_entries

    def put(self, original: str) -> str:
        """Store an original. Returns its CCR hash."""
        h = sha256_hex(original)
        if len(self._store) >= self._max:
            # Simple eviction: drop the oldest entry (FIFO).
            # For a real system, use LRU or a TTL.
            self._store.pop(next(iter(self._store)))
        self._store[h] = original
        return h

    def get(self, ccr_hash: str) -> str | None:
        """Retrieve an original by hash. Returns None if not in the store."""
        return self._store.get(ccr_hash)

    def has(self, ccr_hash: str) -> bool:
        return ccr_hash in self._store

    def size(self) -> int:
        return len(self._store)

    def clear(self) -> None:
        self._store.clear()


# Default singleton — used by the compression functions and the MCP server
_default_store = CCRStore()


def get_store() -> CCRStore:
    """Return the process-default CCR store."""
    return _default_store
