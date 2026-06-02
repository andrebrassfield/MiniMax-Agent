"""
Tests for the deep-research Skill action.py.
"""

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import deep_research_action as action  # noqa: E402


def _valid_m3_output() -> dict:
    return {
        "topic": "Test topic",
        "research_date": "2026-06-02",
        "what_andre_believes": "First paragraph about what Andre believes.\n\nSecond paragraph adding more depth.",
        "what_contradicts": "First paragraph about the contradiction.\n\nSecond paragraph with the other side.",
        "what_is_missing": "First paragraph identifying the gap.\n\nSecond paragraph with specifics.",
        "unasked_question": "What if X?",
        "grounded_notes": ["[[A]]", "[[B]]", "[[C]]"],
    }


# ============================================================
# VALIDATION
# ============================================================

class TestValidation:
    def test_minimal_valid(self):
        action.validate_m3_output(_valid_m3_output())

    def test_missing_topic(self):
        m3 = _valid_m3_output()
        del m3["topic"]
        with pytest.raises(ValueError, match="topic"):
            action.validate_m3_output(m3)

    def test_bad_date(self):
        m3 = _valid_m3_output()
        m3["research_date"] = "06/02/2026"
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            action.validate_m3_output(m3)

    def test_section_too_few_paragraphs(self):
        m3 = _valid_m3_output()
        m3["what_andre_believes"] = "Only one paragraph."
        with pytest.raises(ValueError, match="2\\+ paragraphs"):
            action.validate_m3_output(m3)

    def test_grounded_notes_too_few(self):
        m3 = _valid_m3_output()
        m3["grounded_notes"] = ["[[A]]", "[[B]]"]
        with pytest.raises(ValueError, match="3\\+ items"):
            action.validate_m3_output(m3)

    def test_empty_unasked_question(self):
        m3 = _valid_m3_output()
        m3["unasked_question"] = "   "
        with pytest.raises(ValueError, match="unasked_question"):
            action.validate_m3_output(m3)


# ============================================================
# RENDER
# ============================================================

class TestRender:
    def test_renders_four_sections(self):
        md = action.render_research_markdown(_valid_m3_output())
        assert "## 1. What Andre already believes" in md
        assert "## 2. What contradicts that belief" in md
        assert "## 3. What perspective is clearly missing" in md
        assert "## 4. The single most important unasked question" in md
        assert "What if X?" in md
        assert "[[A]]" in md

    def test_renders_topic_in_header(self):
        md = action.render_research_markdown(_valid_m3_output())
        assert "# Deep Research: Test topic" in md


# ============================================================
# SLUG
# ============================================================

class TestSlugify:
    def test_basic(self):
        assert action.slugify_topic("Agent Memory Architectures") == "agent-memory-architectures"

    def test_truncates(self):
        long = "a" * 100
        slug = action.slugify_topic(long)
        assert len(slug) == 60

    def test_empty_falls_back(self):
        assert action.slugify_topic("!!!") == "untitled"


# ============================================================
# END-TO-END
# ============================================================

class TestEndToEnd:
    def test_writes_research_to_resources(self, tmp_path, monkeypatch):
        monkeypatch.setattr(action, "VAULT_ROOT", tmp_path)
        monkeypatch.setattr(action, "RESOURCES_DIR", tmp_path / "04 Resources")
        monkeypatch.setattr(action, "AUDIT_LOG", tmp_path / "99 _system" / "logs" / "dr-audit.jsonl")
        action.RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
        action.AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

        result = action.render_research(_valid_m3_output())
        assert result["status"] == "ok"
        out = tmp_path / "04 Resources" / "research-2026-06-02-test-topic.md"
        assert out.exists()
        content = out.read_text()
        assert "Test topic" in content
        # Audit log
        assert action.AUDIT_LOG.exists()
        audit = json.loads(action.AUDIT_LOG.read_text().strip())
        assert audit["topic"] == "Test topic"
        assert audit["grounded_notes_count"] == 3

    def test_refuses_overwrite(self, tmp_path, monkeypatch):
        monkeypatch.setattr(action, "VAULT_ROOT", tmp_path)
        monkeypatch.setattr(action, "RESOURCES_DIR", tmp_path / "04 Resources")
        monkeypatch.setattr(action, "AUDIT_LOG", tmp_path / "99 _system" / "logs" / "dr-audit.jsonl")
        action.RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
        (action.RESOURCES_DIR / "research-2026-06-02-test-topic.md").write_text("existing", encoding="utf-8")

        with pytest.raises(FileExistsError, match="already exists"):
            action.render_research(_valid_m3_output())
