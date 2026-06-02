"""
Tests for the daily-brief Skill action.py.

Esalen posture: tests cover the deterministic I/O layer (validation,
markdown rendering, file write, audit log). They do NOT cover M3's
content judgment — that's evaluated by SkillOpt's M3-as-judge evals.
"""

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import daily_brief_action as action  # noqa: E402


# ============================================================
# VALIDATION
# ============================================================

class TestValidation:
    def test_minimal_valid(self):
        action.validate_m3_output({
            "brief_date": "2026-06-02",
            "connections": [],
            "pattern": {"name": "Nothing to surface this morning", "evidence_notes": ["[[A]]", "[[B]]", "[[C]]"]},
            "question": "Nothing to surface this morning",
        })

    def test_missing_brief_date(self):
        with pytest.raises(ValueError, match="brief_date"):
            action.validate_m3_output({
                "connections": [],
                "pattern": {"name": "x", "evidence_notes": ["a", "b", "c"]},
                "question": "q",
            })

    def test_bad_date_format(self):
        with pytest.raises(ValueError, match="YYYY-MM-DD"):
            action.validate_m3_output({
                "brief_date": "06/02/2026",
                "connections": [],
                "pattern": {"name": "x", "evidence_notes": ["a", "b", "c"]},
                "question": "q",
            })

    def test_too_many_connections(self):
        with pytest.raises(ValueError, match="max 3"):
            action.validate_m3_output({
                "brief_date": "2026-06-02",
                "connections": [
                    {"headline": "h", "source_note_1": "n1", "source_quote_1": "x" * 20,
                     "source_note_2": "n2", "source_quote_2": "y" * 20}
                    for _ in range(4)
                ],
                "pattern": {"name": "x", "evidence_notes": ["a", "b", "c"]},
                "question": "q",
            })

    def test_quote_too_short(self):
        with pytest.raises(ValueError, match="too short"):
            action.validate_m3_output({
                "brief_date": "2026-06-02",
                "connections": [{
                    "headline": "h", "source_note_1": "n1", "source_quote_1": "too short",
                    "source_note_2": "n2", "source_quote_2": "y" * 20
                }],
                "pattern": {"name": "x", "evidence_notes": ["a", "b", "c"]},
                "question": "q",
            })

    def test_pattern_evidence_under_3(self):
        with pytest.raises(ValueError, match="3\\+ items"):
            action.validate_m3_output({
                "brief_date": "2026-06-02",
                "connections": [],
                "pattern": {"name": "x", "evidence_notes": ["a", "b"]},
                "question": "q",
            })

    def test_missing_question(self):
        with pytest.raises(ValueError, match="question"):
            action.validate_m3_output({
                "brief_date": "2026-06-02",
                "connections": [],
                "pattern": {"name": "x", "evidence_notes": ["a", "b", "c"]},
            })


# ============================================================
# RENDER
# ============================================================

class TestRender:
    def test_renders_with_connections(self):
        m3 = {
            "brief_date": "2026-06-02",
            "connections": [
                {
                    "headline": "Two notes agree on X",
                    "source_note_1": "[[Note-A]]",
                    "source_quote_1": "exact quote from A here",
                    "source_note_2": "[[Note-B]]",
                    "source_quote_2": "exact quote from B here",
                }
            ],
            "pattern": {
                "name": "Pattern X is recurring",
                "evidence_notes": ["[[N1]]", "[[N2]]", "[[N3]]"],
            },
            "question": "What if X?",
        }
        md = action.render_brief_markdown(m3)
        assert "Daily Brief — 2026-06-02" in md
        assert "## CONNECTIONS" in md
        assert "Two notes agree on X" in md
        assert "[[Note-A]]" in md
        assert "exact quote from A here" in md
        assert "## PATTERN" in md
        assert "Pattern X is recurring" in md
        assert "[[N1]]" in md
        assert "## QUESTION" in md
        assert "What if X?" in md

    def test_renders_empty_inputs(self):
        m3 = {
            "brief_date": "2026-06-02",
            "connections": [],
            "pattern": {"name": "Nothing to surface this morning", "evidence_notes": ["a", "b", "c"]},
            "question": "Nothing to surface this morning",
        }
        md = action.render_brief_markdown(m3)
        assert "Nothing to surface" in md
        assert "## CONNECTIONS" in md
        assert "## PATTERN" in md
        assert "## QUESTION" in md


# ============================================================
# END-TO-END (writes to a temp vault)
# ============================================================

class TestEndToEnd:
    def test_writes_brief_to_inbox(self, tmp_path, monkeypatch):
        # Redirect vault paths to tmp_path
        monkeypatch.setattr(action, "VAULT_ROOT", tmp_path)
        monkeypatch.setattr(action, "INBOX", tmp_path / "00 Inbox")
        monkeypatch.setattr(action, "DAILY", tmp_path / "01 Daily")
        monkeypatch.setattr(action, "AUDIT_LOG", tmp_path / "99 _system" / "logs" / "daily-brief-audit.jsonl")
        action.INBOX.mkdir(parents=True, exist_ok=True)
        action.AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

        m3 = {
            "brief_date": "2026-06-02",
            "connections": [{
                "headline": "Test connection",
                "source_note_1": "[[A]]",
                "source_quote_1": "quote from A here is long enough",
                "source_note_2": "[[B]]",
                "source_quote_2": "quote from B here is long enough",
            }],
            "pattern": {"name": "Test pattern", "evidence_notes": ["[[X]]", "[[Y]]", "[[Z]]"]},
            "question": "Test question?",
        }
        result = action.render_brief(m3)
        assert result["status"] == "ok"
        assert result["connections_count"] == 1
        brief_path = tmp_path / "00 Inbox" / "brief-2026-06-02.md"
        assert brief_path.exists()
        content = brief_path.read_text()
        assert "Test connection" in content
        assert "Test pattern" in content
        # Audit log
        assert action.AUDIT_LOG.exists()
        audit_lines = action.AUDIT_LOG.read_text().strip().splitlines()
        assert len(audit_lines) == 1
        audit = json.loads(audit_lines[0])
        assert audit["brief_date"] == "2026-06-02"
        assert audit["connections_count"] == 1

    def test_refuses_overwrite_without_flag(self, tmp_path, monkeypatch):
        monkeypatch.setattr(action, "VAULT_ROOT", tmp_path)
        monkeypatch.setattr(action, "INBOX", tmp_path / "00 Inbox")
        monkeypatch.setattr(action, "DAILY", tmp_path / "01 Daily")
        monkeypatch.setattr(action, "AUDIT_LOG", tmp_path / "99 _system" / "logs" / "daily-brief-audit.jsonl")
        action.INBOX.mkdir(parents=True, exist_ok=True)
        (action.INBOX / "brief-2026-06-02.md").write_text("existing brief", encoding="utf-8")

        m3 = {
            "brief_date": "2026-06-02",
            "connections": [],
            "pattern": {"name": "x", "evidence_notes": ["a", "b", "c"]},
            "question": "q",
        }
        with pytest.raises(FileExistsError, match="already exists"):
            action.render_brief(m3)

    def test_overwrite_with_flag(self, tmp_path, monkeypatch):
        monkeypatch.setattr(action, "VAULT_ROOT", tmp_path)
        monkeypatch.setattr(action, "INBOX", tmp_path / "00 Inbox")
        monkeypatch.setattr(action, "DAILY", tmp_path / "01 Daily")
        monkeypatch.setattr(action, "AUDIT_LOG", tmp_path / "99 _system" / "logs" / "daily-brief-audit.jsonl")
        action.INBOX.mkdir(parents=True, exist_ok=True)
        (action.INBOX / "brief-2026-06-02.md").write_text("existing brief", encoding="utf-8")

        m3 = {
            "brief_date": "2026-06-02",
            "connections": [],
            "pattern": {"name": "x", "evidence_notes": ["a", "b", "c"]},
            "question": "q",
        }
        result = action.render_brief(m3, overwrite=True)
        assert result["status"] == "ok"
