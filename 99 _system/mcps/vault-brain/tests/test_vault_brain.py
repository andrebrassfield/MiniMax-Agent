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
       check deterministic I/O (file walk, tokenize, score). The semantic
       ranking is M3's job at call time.
    2. Is the code a thin deterministic layer or a model-judges-itself loop?
       — Thin deterministic. No LLM calls in the search path.
    3. Does the system trust the model to finish or cage it? — Trust. M3
       does the synthesis over the returned candidates.
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
    print("  ✓ Esalen audit: thin deterministic layer, no model-judges-itself loop")


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
    print(f"\nAll tests passed.")
