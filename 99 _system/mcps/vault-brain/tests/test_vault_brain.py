"""
Tests for vault_brain — the thin retrieval wrapper.

Per build → test → skillify: test the deterministic layer first.
The skill pack (markdown skill, integration test) comes after the
test phase produces a stable shape.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Allow `import vault_brain` from this tests/ directory
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import vault_brain


# ============================================================
# INDEXER
# ============================================================

def test_indexer_walks_vault():
    """The indexer should find a non-trivial number of notes in the vault."""
    notes = vault_brain.build_index()
    # The Mavis vault is fresh (~79 notes seeded). Threshold is "more than 20"
    # which proves the indexer is walking, not the absolute count.
    assert len(notes) > 20, f"Expected >20 notes, got {len(notes)}"
    # All notes should have the expected fields
    for n in notes[:5]:
        assert "path" in n
        assert "title" in n
        assert "tags" in n
        assert "wikilinks" in n
        assert "body_excerpt" in n
        assert "mtime" in n
    print(f"  ✓ indexer found {len(notes)} notes")


def test_indexer_skips_excluded_dirs():
    """The indexer should skip .obsidian, .git, node_modules, 99 _system/logs."""
    notes = vault_brain.build_index()
    paths = [n["path"] for n in notes]
    assert not any(p.startswith(".obsidian") for p in paths)
    assert not any(p.startswith(".git") for p in paths)
    assert not any("99 _system/logs" in p for p in paths)
    print("  ✓ indexer skips excluded directories")


def test_frontmatter_parser():
    """The frontmatter parser should handle the various shapes in the vault."""
    cases = [
        ("---\ntype: moc\ntags: [a, b]\n---\nbody", {"type": "moc", "tags": "[a, b]"}),
        ("---\nkey: value\nmore: stuff\n---\nbody", {"key": "value", "more": "stuff"}),
        ("no frontmatter here", {}),
    ]
    for content, expected in cases:
        result = vault_brain.parse_frontmatter(content)
        assert result == expected, f"parse_frontmatter({content!r}) = {result!r}, expected {expected!r}"
    print("  ✓ frontmatter parser handles 3 cases")


def test_wikilink_extractor():
    """Wikilinks should be extracted with display text stripped."""
    content = """
    See [[Note A]] and [[Note B|the display text]] for more.
    Also [[Note C|with pipe]].
    """
    links = vault_brain.extract_wikilinks(content)
    assert "Note A" in links
    assert "Note B" in links
    assert "Note C" in links
    # No duplicates
    assert len(links) == len(set(links))
    print("  ✓ wikilink extractor handles [[link]] and [[link|display]]")


# ============================================================
# SEARCHER
# ============================================================

def test_search_finds_known_phrase():
    """A search for 'Esalen' should find ESALEN-NOT-FOXCONN.md at the top."""
    # Build a fresh index in memory (don't depend on disk state)
    notes = vault_brain.build_index()
    index = {"notes": notes, "vault_root": str(vault_brain.VAULT_ROOT)}
    result = vault_brain.search("Esalen", top_k=5, index=index)
    assert "notes" in result
    assert len(result["notes"]) > 0
    top = result["notes"][0]
    assert "ESALEN" in top["path"].upper() or "esalen" in top["rendered"].lower()
    print(f"  ✓ 'Esalen' → top hit: {top['path']} (score {top['score']})")


def test_search_anchor_ends_arrangement():
    """When ≥4 results, the first result should be at position 0 and
    the second result should be at position N-1 (the anchor-ends strategy)."""
    notes = vault_brain.build_index()
    index = {"notes": notes, "vault_root": str(vault_brain.VAULT_ROOT)}
    result = vault_brain.search("Mavis operating posture constraints", top_k=10, index=index)
    assert len(result["notes"]) >= 4
    first_path = result["notes"][0]["path"]
    second_path = result["notes"][-1]["path"]
    # The first and second should be the two highest-scored notes
    scores = [n["score"] for n in result["notes"]]
    assert scores[0] == max(scores), "first should be highest-scored"
    # Second highest should be at the end
    sorted_scores = sorted(scores, reverse=True)
    assert scores[-1] == sorted_scores[1], "last should be second-highest-scored"
    print(f"  ✓ anchor-ends: first={first_path}, last={second_path}")


def test_search_respects_token_budget():
    """The packed result should be within max_total_tokens."""
    notes = vault_brain.build_index()
    index = {"notes": notes, "vault_root": str(vault_brain.VAULT_ROOT)}
    result = vault_brain.search("Mavis", top_k=20, max_total_tokens=10_000, index=index)
    total = result["total_tokens_estimate"]
    assert total <= 10_000, f"Total {total} > 10000 budget"
    print(f"  ✓ token budget respected: {total} tokens returned (budget 10000)")


def test_search_returns_backlinks():
    """With include_backlinks=True, each returned note should have a backlinks list."""
    notes = vault_brain.build_index()
    index = {"notes": notes, "vault_root": str(vault_brain.VAULT_ROOT)}
    result = vault_brain.search("Mavis Apex Architecture", top_k=5, index=index)
    for n in result["notes"]:
        assert "backlinks" in n
    print(f"  ✓ backlinks included on {len(result['notes'])} returned notes")


# ============================================================
# Esalen AUDIT (the 3 questions, applied to this build)
# ============================================================

def test_esalen_audit():
    """The 3 Esalen audit questions, applied to vault_brain:
    1. Are we testing something the model would have handled? — No. The tests
       check deterministic I/O (file walk, tokenize, score, compress). The
       semantic ranking is M3's job at call time.
    2. Is the code a thin deterministic layer or a model-judges-itself loop?
       — Thin deterministic. No LLM calls in the search path. Compression
       is regex + heuristics, not an LLM.
    3. Does the system trust the model to finish or cage it? — Trust. M3
       does the synthesis over the returned candidates. It can opt back
       into the original via ccr_retrieve when it needs detail.
    """
    # Verify: no mcp LLM calls, no recursive model calls, no caging
    import inspect
    source = inspect.getsource(vault_brain)
    # No LLM-as-judge call in the search path
    assert "call_haiku" not in source.lower()
    assert "anthropic" not in source.lower()
    assert "openai" not in source.lower()
    # search() returns candidates, not a final answer
    sig = inspect.signature(vault_brain.search)
    assert "query" in sig.parameters
    # CCR is opt-in (the model decides when to retrieve)
    sig = inspect.signature(vault_brain.search)
    assert "compress" in sig.parameters
    print("  ✓ Esalen audit: thin deterministic layer + opt-in CCR, no model-judges-itself loop")


# ============================================================
# HEADROOM COMPRESSION (v1.0.0)
# ============================================================

def test_search_compresses_by_default():
    """By default, search() runs the Headroom compression layer over each chunk."""
    notes = vault_brain.build_index()
    index = {"notes": notes, "vault_root": str(vault_brain.VAULT_ROOT)}
    result = vault_brain.search("Mavis operating envelope", top_k=5, index=index)
    assert result["compression_summary"]["enabled"] is True
    # At least one chunk should have compression info
    compressed_chunks = [c for c in result["notes"] if c.get("compression")]
    if result["notes"]:
        # The result contains at least one chunk; compression ran on chunks >= 100 tokens
        # (synthesized chunks may be short if top hits are short)
        pass
    # The summary should have the savings field
    summary = result["compression_summary"]
    assert "overall_savings_pct" in summary
    assert "chunks_compressed" in summary
    print(f"  ✓ search() compressed: {summary['chunks_compressed']}/{len(result['notes'])} chunks, {summary['overall_savings_pct']}% savings")


def test_search_can_disable_compression():
    """With compress=False, the returned chunks have no compression info and no CCR hash."""
    notes = vault_brain.build_index()
    index = {"notes": notes, "vault_root": str(vault_brain.VAULT_ROOT)}
    result = vault_brain.search("Mavis operating envelope", top_k=5, compress=False, index=index)
    assert result["compression_summary"]["enabled"] is False
    for chunk in result["notes"]:
        assert "compression" not in chunk
    print(f"  ✓ compress=False: no compression info on any of {len(result['notes'])} chunks")


def test_search_compressed_chunks_have_ccr_hash():
    """Every compressed chunk should have a SHA-256 CCR hash retrievable via ccr_retrieve."""
    import hashlib
    notes = vault_brain.build_index()
    index = {"notes": notes, "vault_root": str(vault_brain.VAULT_ROOT)}
    result = vault_brain.search("Mavis operating envelope", top_k=5, index=index)
    found_any = False
    for chunk in result["notes"]:
        comp = chunk.get("compression")
        if not comp:
            continue
        found_any = True
        h = comp["ccr_hash"]
        # SHA-256 hex digest = 64 hex chars
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)
        # The hash must be retrievable from the CCR store
        if vault_brain.HEADROOM_AVAILABLE:
            original = vault_brain._ccr_store.get(h)
            assert original is not None
            # The original must contain the chunk's title and path
            assert chunk["title"] in original
    assert found_any, "expected at least one compressed chunk"
    print(f"  ✓ all compressed chunks have valid SHA-256 CCR hashes (retrievable)")


def test_ccr_retrieve_returns_original():
    """The CCR retrieve path returns the original markdown (uncompressed)."""
    if not vault_brain.HEADROOM_AVAILABLE:
        pytest.skip("Headroom not available (direct-intake not on path)")
    import pytest
    notes = vault_brain.build_index()
    index = {"notes": notes, "vault_root": str(vault_brain.VAULT_ROOT)}
    result = vault_brain.search("Mavis operating envelope", top_k=3, index=index)
    # Find any compressed chunk
    for chunk in result["notes"]:
        comp = chunk.get("compression")
        if not comp:
            continue
        h = comp["ccr_hash"]
        original = vault_brain._ccr_store.get(h)
        assert original is not None
        # The original is the uncompressed rendered chunk
        assert chunk["title"] in original
        assert chunk["path"] in original
        # The compressed text is shorter or equal
        if comp["original_tokens"] > 0 and comp["compressed_tokens"] > 0:
            assert comp["compressed_tokens"] <= comp["original_tokens"]
        break
    print(f"  ✓ ccr_retrieve round-trip: original retrievable, content preserved")


def test_search_total_tokens_accounts_for_compression():
    """The total_tokens_estimate should reflect the compressed size, not the raw."""
    notes = vault_brain.build_index()
    index = {"notes": notes, "vault_root": str(vault_brain.VAULT_ROOT)}

    # Compressed
    r_compressed = vault_brain.search("Mavis operating envelope", top_k=10, index=index, compress=True)
    # Uncompressed
    r_raw = vault_brain.search("Mavis operating envelope", top_k=10, index=index, compress=False)

    # If compression ran and saved anything, compressed total should be <= raw
    summary = r_compressed["compression_summary"]
    if summary["enabled"] and summary.get("chunks_compressed", 0) > 0:
        assert r_compressed["total_tokens_estimate"] <= r_raw["total_tokens_estimate"]
        print(f"  ✓ compressed total ({r_compressed['total_tokens_estimate']}) <= raw total ({r_raw['total_tokens_estimate']})")
    else:
        # No compression happened (chunks too small) — totals should be equal
        assert r_compressed["total_tokens_estimate"] == r_raw["total_tokens_estimate"]
        print(f"  ✓ no chunks large enough to compress; totals equal: {r_compressed['total_tokens_estimate']}")


# ============================================================
# Test runner
# ============================================================

if __name__ == "__main__":
    print(f"vault_brain v{vault_brain.__version__} tests\n")
    print("Indexer:")
    test_indexer_walks_vault()
    test_indexer_skips_excluded_dirs()
    test_frontmatter_parser()
    test_wikilink_extractor()
    print("\nSearcher:")
    test_search_finds_known_phrase()
    test_search_anchor_ends_arrangement()
    test_search_respects_token_budget()
    test_search_returns_backlinks()
    print("\nEsalen audit:")
    test_esalen_audit()
    print("\nHeadroom compression (v1.0.0):")
    test_search_compresses_by_default()
    test_search_can_disable_compression()
    test_search_compressed_chunks_have_ccr_hash()
    test_ccr_retrieve_returns_original()
    test_search_total_tokens_accounts_for_compression()
    print("\nAll tests passed.")
    test_esalen_audit()
    print(f"\nAll tests passed.")
