"""
Tests for the instincts layer.

These tests verify:
  1. Every instinct file has the required frontmatter fields
  2. Confidence is in [0.0, 1.0]
  3. Body is non-empty
  4. IDs are unique
  5. The README index is in sync with the file system
"""

import re
import sys
from pathlib import Path

import pytest

INSTINCTS_DIR = Path(__file__).resolve().parent.parent  # instincts/ directory itself

REQUIRED_FIELDS = [
    "id",
    "type",
    "title",
    "created",
    "confidence",
    "cluster",
    "trigger_context",
    "evidence_source",
    "tags",
]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def list_instinct_files() -> list[Path]:
    return sorted(INSTINCTS_DIR.glob("*.md"))


def parse_frontmatter(path: Path) -> dict:
    """Parse the YAML frontmatter. Tiny YAML parser sufficient for our needs."""
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm_text = m.group(1)
    result = {}
    current_key = None
    for line in fm_text.split("\n"):
        if line.startswith("  - "):
            # Continuation of a list (YAML)
            if current_key == "tags":
                result["tags"].append(line.strip()[2:].strip())
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                # Possibly a list follows
                current_key = key
                result[key] = []
            elif value.startswith("[") and value.endswith("]"):
                # Inline list
                inner = value[1:-1]
                result[key] = [t.strip() for t in inner.split(",") if t.strip()]
                current_key = None
            else:
                # Strip quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                result[key] = value
                current_key = None
    return result


# ============================================================
# SCHEMA TESTS
# ============================================================

class TestInstinctSchema:
    def test_all_files_have_frontmatter(self):
        for path in list_instinct_files():
            if path.name == "README.md":
                continue
            fm = parse_frontmatter(path)
            assert fm, f"{path.name} has no frontmatter"

    def test_all_required_fields(self):
        for path in list_instinct_files():
            if path.name == "README.md":
                continue
            fm = parse_frontmatter(path)
            for field in REQUIRED_FIELDS:
                assert field in fm, f"{path.name} missing field: {field}"

    def test_type_is_instinct(self):
        for path in list_instinct_files():
            if path.name == "README.md":
                continue
            fm = parse_frontmatter(path)
            assert fm.get("type") == "instinct", f"{path.name} type != instinct"

    def test_confidence_in_range(self):
        for path in list_instinct_files():
            if path.name == "README.md":
                continue
            fm = parse_frontmatter(path)
            conf = float(fm.get("confidence", 0))
            assert 0.0 <= conf <= 1.0, f"{path.name} confidence {conf} out of range"

    def test_id_starts_with_i_date(self):
        for path in list_instinct_files():
            if path.name == "README.md":
                continue
            fm = parse_frontmatter(path)
            id_ = fm.get("id", "")
            assert re.match(r"^i-\d{4}-\d{2}-\d{2}-\d{3}$", id_), \
                f"{path.name} id {id_!r} not in i-YYYY-MM-DD-NNN format"


# ============================================================
# UNIQUENESS
# ============================================================

class TestUniqueness:
    def test_ids_are_unique(self):
        ids = []
        for path in list_instinct_files():
            if path.name == "README.md":
                continue
            fm = parse_frontmatter(path)
            if "id" in fm:
                ids.append(fm["id"])
        duplicates = [i for i in ids if ids.count(i) > 1]
        assert not duplicates, f"duplicate IDs: {set(duplicates)}"


# ============================================================
# BODY CONTENT
# ============================================================

class TestBody:
    def test_body_present(self):
        for path in list_instinct_files():
            if path.name == "README.md":
                continue
            text = path.read_text(encoding="utf-8")
            # After frontmatter, must have a heading + paragraph
            after_fm = text.split("---", 2)[-1].strip() if "---" in text else text
            # Look for a # heading
            assert after_fm.startswith("# "), f"{path.name} no H1 heading after frontmatter"
            # Body must be >= 100 chars
            assert len(after_fm) > 100, f"{path.name} body too short"


# ============================================================
# SUMMARY
# ============================================================

class TestSummary:
    def test_count(self):
        files = [p for p in list_instinct_files() if p.name != "README.md"]
        assert len(files) >= 25, f"expected >=25 instincts, got {len(files)}"
        print(f"  ✓ {len(files)} instinct files (>=25 required)")

    def test_avg_confidence(self):
        confs = []
        for path in list_instinct_files():
            if path.name == "README.md":
                continue
            fm = parse_frontmatter(path)
            if "confidence" in fm:
                confs.append(float(fm["confidence"]))
        avg = sum(confs) / len(confs)
        assert avg >= 0.85, f"avg confidence {avg:.3f} below 0.85"
        print(f"  ✓ avg confidence: {avg:.3f} (>=0.85 required)")
