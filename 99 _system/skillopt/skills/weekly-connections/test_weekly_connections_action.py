"""
Tests for the weekly-connections Skill action.py.

Covers validation, render, and end-to-end file creation. Per Esalen
discipline, M3's content judgment is evaluated by SkillOpt, not here.
"""

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import weekly_connections_action as action  # noqa: E402


def _valid_connection(type_: str = "A", slug: str = "test-slug", sources=None) -> dict:
    if sources is None:
        sources = ["[[A]]", "[[B]]"]
    return {
        "type": type_,
        "bridge": "Test bridge",
        "slug": slug,
        "sources": sources,
        "body": "## Why this connection matters\n\nSome insight.\n\n## The bridge\n\nThe connection explained.",
    }


def _valid_m3_output(num_connections: int = 3) -> dict:
    return {
        "week_label": "2026-W22",
        "connections": [
            _valid_connection(slug=f"slug-{i}") for i in range(num_connections)
        ],
    }


# ============================================================
# VALIDATION
# ============================================================

class TestValidation:
    def test_minimal_valid(self):
        action.validate_m3_output(_valid_m3_output(3))

    def test_missing_week_label(self):
        m3 = _valid_m3_output(3)
        del m3["week_label"]
        with pytest.raises(ValueError, match="week_label"):
            action.validate_m3_output(m3)

    def test_too_many_connections(self):
        with pytest.raises(ValueError, match="max 5"):
            action.validate_m3_output(_valid_m3_output(6))

    def test_bad_type(self):
        c = _valid_connection()
        c["type"] = "E"
        with pytest.raises(ValueError, match="must be one of"):
            action.validate_m3_output({"week_label": "w", "connections": [c]})

    def test_type_c_needs_3_sources(self):
        c = _valid_connection(type_="C", sources=["[[A]]", "[[B]]"])  # only 2
        with pytest.raises(ValueError, match="type C"):
            action.validate_m3_output({"week_label": "w", "connections": [c]})

    def test_missing_body_section(self):
        c = _valid_connection()
        c["body"] = "## Why this connection matters\n\nonly one section"
        with pytest.raises(ValueError, match="## The bridge"):
            action.validate_m3_output({"week_label": "w", "connections": [c]})

    def test_bad_slug(self):
        c = _valid_connection(slug="Bad Slug With Spaces")
        with pytest.raises(ValueError, match="kebab-case"):
            action.validate_m3_output({"week_label": "w", "connections": [c]})

    def test_too_few_sources(self):
        c = _valid_connection(sources=["[[A]]"])  # only 1
        with pytest.raises(ValueError, match="2\\+ wikilinks"):
            action.validate_m3_output({"week_label": "w", "connections": [c]})


# ============================================================
# RENDER
# ============================================================

class TestRender:
    def test_renders_a_type(self):
        c = _valid_connection(type_="A", slug="anchor-msa")
        c["body"] = "## Why this connection matters\n\nInsight A.\n\n## The bridge\n\nThe bridge."
        md = action.render_connection_file(c, "2026-06-02")
        assert "# anchor-msa" in md
        assert "Type A" in md
        assert "Same principle" in md
        assert "2026-06-02" in md
        assert "[[A]]" in md
        assert "The bridge" in md

    def test_renders_b_type(self):
        c = _valid_connection(type_="B", slug="tension-x")
        c["body"] = "## Why this connection matters\n\nInsight B.\n\n## The bridge\n\nThe bridge."
        md = action.render_connection_file(c, "2026-06-02")
        assert "Type B" in md
        assert "Contradiction" in md


# ============================================================
# END-TO-END
# ============================================================

class TestEndToEnd:
    def test_writes_one_file_per_connection(self, tmp_path, monkeypatch):
        monkeypatch.setattr(action, "VAULT_ROOT", tmp_path)
        monkeypatch.setattr(action, "CONNECTIONS_DIR", tmp_path / "06 Connections")
        monkeypatch.setattr(action, "AUDIT_LOG", tmp_path / "99 _system" / "logs" / "wc-audit.jsonl")
        action.CONNECTIONS_DIR.mkdir(parents=True, exist_ok=True)
        action.AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

        m3 = _valid_m3_output(3)
        result = action.render_connections(m3, date="2026-06-02")
        assert result["status"] == "ok"
        assert result["count"] == 3
        for slug in ["slug-0", "slug-1", "slug-2"]:
            f = action.CONNECTIONS_DIR / f"2026-06-02 - {slug}.md"
            assert f.exists()
            content = f.read_text()
            assert f"# {slug}" in content
            assert "Type A" in content
        # Audit log
        assert action.AUDIT_LOG.exists()
        audit = json.loads(action.AUDIT_LOG.read_text().strip())
        assert audit["count"] == 3
        assert audit["types_distribution"]["A"] == 3

    def test_refuses_overwrite(self, tmp_path, monkeypatch):
        monkeypatch.setattr(action, "VAULT_ROOT", tmp_path)
        monkeypatch.setattr(action, "CONNECTIONS_DIR", tmp_path / "06 Connections")
        monkeypatch.setattr(action, "AUDIT_LOG", tmp_path / "99 _system" / "logs" / "wc-audit.jsonl")
        action.CONNECTIONS_DIR.mkdir(parents=True, exist_ok=True)
        (action.CONNECTIONS_DIR / "2026-06-02 - slug-0.md").write_text("existing", encoding="utf-8")

        m3 = _valid_m3_output(1)
        with pytest.raises(FileExistsError, match="already exists"):
            action.render_connections(m3, date="2026-06-02")
