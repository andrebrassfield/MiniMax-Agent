"""
Tests for the resolver Skill Router.

Esalen posture: tests cover the deterministic I/O layer (discovery,
request building, validation, persistence, apply_ranking). The
classification itself is M3's job — tested via SkillOpt's M3-as-judge
evals (or in a real session).
"""

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
RESOLVER = HERE.parent / "99 _system" / "mcps" / "resolver"
sys.path.insert(0, str(RESOLVER))

import resolver  # noqa: E402


# ============================================================
# SKILL DISCOVERY
# ============================================================

class TestDiscovery:
    def test_finds_all_4_skill_packs(self, monkeypatch):
        # The real SKILLS_DIR should have all 4 packs
        skills = resolver.discover_skills()
        names = {s.name for s in skills}
        assert "process-inbox" in names
        assert "daily-brief" in names
        assert "weekly-connections" in names
        assert "deep-research" in names

    def test_skill_summary_has_metadata(self):
        skills = resolver.discover_skills()
        for s in skills:
            assert s.name
            assert s.path
            assert s.description
            # All 4 should have action.py and test_action.py
            assert s.has_action, f"{s.name} missing action.py"
            assert s.has_tests, f"{s.name} missing test_action.py"

    def test_skips_non_pack_dirs(self, tmp_path, monkeypatch):
        # Make a fake skills dir with valid pack + a junk dir
        fake = tmp_path / "skills"
        fake.mkdir()
        (fake / "valid-pack").mkdir()
        (fake / "valid-pack" / "skill.md").write_text(
            "---\ntitle: Valid\n---\n\n> A valid pack.\n",
            encoding="utf-8",
        )
        (fake / "no-skill-md").mkdir()
        (fake / "__pycache__").mkdir()
        (fake / "loose-file.md").write_text("not a pack", encoding="utf-8")
        monkeypatch.setattr(resolver, "SKILLS_DIR", fake)
        skills = resolver.discover_skills()
        assert len(skills) == 1
        assert skills[0].name == "valid-pack"


# ============================================================
# REQUEST BUILDING
# ============================================================

class TestRequestBuilding:
    def test_builds_with_vault_state(self):
        req = resolver.build_ranking_request("Test query", top_k=2)
        assert req.query == "Test query"
        assert req.top_k == 2
        assert len(req.available_skills) >= 1
        assert req.vault_state
        assert "today" in req.vault_state

    def test_builds_without_vault_state(self):
        req = resolver.build_ranking_request("q", include_vault_state=False)
        assert req.vault_state == {}

    def test_unique_request_ids(self):
        r1 = resolver.build_ranking_request("q")
        r2 = resolver.build_ranking_request("q")
        assert r1.request_id != r2.request_id
        assert r1.request_id.startswith("rank-")

    def test_prompt_contains_skills_and_query(self):
        req = resolver.build_ranking_request("Clear out my tabs", top_k=2)
        prompt = resolver.render_ranking_prompt(req)
        assert "Clear out my tabs" in prompt
        assert "process-inbox" in prompt
        assert "rank" in prompt.lower()
        assert "How to score" in prompt


# ============================================================
# RANKING VALIDATION
# ============================================================

class TestValidation:
    def _req(self):
        return resolver.build_ranking_request("test", top_k=2)

    def test_valid_ranking(self):
        req = self._req()
        ranking = {
            "ranking": [
                {"skill_name": "process-inbox", "confidence": 0.9,
                 "one_line_match": "perfect fit for inbox cleanup"},
                {"skill_name": "daily-brief", "confidence": 0.3,
                 "one_line_match": "not quite right"},
            ],
            "reasoning": "Inbox cleanup is clearly process-inbox territory.",
        }
        errors, valid = resolver.validate_ranking(req, ranking)
        assert errors == []
        assert len(valid) == 2
        assert valid[0]["skill_name"] == "process-inbox"

    def test_unknown_skill_name(self):
        req = self._req()
        ranking = {
            "ranking": [
                {"skill_name": "nonexistent-skill", "confidence": 0.9,
                 "one_line_match": "doesn't exist"},
            ],
            "reasoning": "x",
        }
        errors, valid = resolver.validate_ranking(req, ranking)
        assert any("not in available skills" in e for e in errors)
        assert valid == []

    def test_confidence_out_of_range(self):
        req = self._req()
        ranking = {
            "ranking": [
                {"skill_name": "process-inbox", "confidence": 1.5,
                 "one_line_match": "x"},
            ],
            "reasoning": "x",
        }
        errors, _ = resolver.validate_ranking(req, ranking)
        assert any("out of" in e for e in errors)

    def test_too_many_entries(self):
        req = self._req()
        ranking = {
            "ranking": [
                {"skill_name": "process-inbox", "confidence": 0.5,
                 "one_line_match": f"x{i}"} for i in range(5)
            ],
            "reasoning": "x",
        }
        errors, _ = resolver.validate_ranking(req, ranking)
        assert any("max is" in e for e in errors)

    def test_missing_reasoning(self):
        req = self._req()
        ranking = {
            "ranking": [{"skill_name": "process-inbox", "confidence": 0.5,
                        "one_line_match": "x"}],
        }
        errors, _ = resolver.validate_ranking(req, ranking)
        assert any("reasoning" in e for e in errors)

    def test_empty_one_line_match(self):
        req = self._req()
        ranking = {
            "ranking": [{"skill_name": "process-inbox", "confidence": 0.5,
                        "one_line_match": "   "}],
            "reasoning": "x",
        }
        errors, _ = resolver.validate_ranking(req, ranking)
        assert any("one_line_match" in e for e in errors)


# ============================================================
# APPLY RANKING
# ============================================================

class TestApply:
    def test_apply_succeeds_with_valid_ranking(self, tmp_path, monkeypatch):
        monkeypatch.setattr(resolver, "REQUESTS_DIR", tmp_path / "_requests")
        monkeypatch.setattr(resolver, "AUDIT_LOG", tmp_path / "audit.jsonl")
        req = resolver.build_ranking_request("q", top_k=2)
        resolver.save_request(req)

        ranking = {
            "ranking": [
                {"skill_name": "process-inbox", "confidence": 0.85,
                 "one_line_match": "inbox cleanup"},
            ],
            "reasoning": "obvious fit",
        }
        result = resolver.apply_ranking(req.request_id, ranking)
        assert result["status"] == "ok"
        assert result["ranking"][0]["skill_name"] == "process-inbox"
        # Audit log written
        assert resolver.AUDIT_LOG.exists()
        audit = json.loads(resolver.AUDIT_LOG.read_text().strip())
        assert audit["request_id"] == req.request_id
        assert audit["top_skill"] == "process-inbox"

    def test_apply_invalid_request_id(self, tmp_path, monkeypatch):
        monkeypatch.setattr(resolver, "REQUESTS_DIR", tmp_path / "_requests")
        result = resolver.apply_ranking("nonexistent-id", {"ranking": [], "reasoning": "x"})
        assert "error" in result

    def test_apply_with_invalid_ranking(self, tmp_path, monkeypatch):
        monkeypatch.setattr(resolver, "REQUESTS_DIR", tmp_path / "_requests")
        monkeypatch.setattr(resolver, "AUDIT_LOG", tmp_path / "audit.jsonl")
        req = resolver.build_ranking_request("q")
        resolver.save_request(req)
        result = resolver.apply_ranking(req.request_id, {"ranking": [], "reasoning": ""})
        assert result["status"] == "invalid"
        assert "errors" in result


# ============================================================
# PERSISTENCE
# ============================================================

class TestPersistence:
    def test_save_and_load_round_trip(self, tmp_path, monkeypatch):
        monkeypatch.setattr(resolver, "REQUESTS_DIR", tmp_path / "_requests")
        req = resolver.build_ranking_request("test q", top_k=3, prompt_hint="focus on X")
        resolver.save_request(req)
        loaded = resolver.load_request(req.request_id)
        assert loaded is not None
        assert loaded.query == "test q"
        assert loaded.top_k == 3
        assert loaded.prompt_hint == "focus on X"
        assert len(loaded.available_skills) == len(req.available_skills)
