"""Tests for the Research Analyst parallel search sub-agents."""

from __future__ import annotations

import json
import os
from typing import Any
from unittest.mock import patch

import pytest

from apps.research_analyst.sub_agents import (
    read_subagent_results,
    spawn_search_subagents,
)


# ---------------------------------------------------------------------------
# spawn_search_subagents
# ---------------------------------------------------------------------------

class TestSpawnSearchSubagents:
    def test_spawns_three_parallel(self) -> None:
        subtopics = ["a", "b", "c"]

        with patch(
            "tools.web_tools.web_search_tool"
        ) as mock_search:
            mock_search.return_value = json.dumps(
                {
                    "success": True,
                    "data": {
                        "web": [
                            {"title": "T", "url": "https://example.com", "description": "D"}
                        ]
                    },
                }
            )
            with patch(
                "apps.research_analyst.sub_agents._run_async"
            ) as mock_async:
                mock_async.return_value = json.dumps(
                    {
                        "success": True,
                        "data": [
                            {"url": "https://example.com", "title": "T", "content": "C"}
                        ],
                    }
                )

                result = spawn_search_subagents(subtopics)

        assert result["all_success"] is True
        assert len(result["subagents"]) == 3
        assert os.path.isdir(result["results_dir"])

    def test_empty_subtopics(self) -> None:
        result = spawn_search_subagents([])
        assert result["subagents"] == []
        assert result["all_success"] is True

    def test_handles_search_failure(self) -> None:
        with patch(
            "tools.web_tools.web_search_tool"
        ) as mock_search:
            mock_search.return_value = json.dumps(
                {"success": False, "error": "API key missing"}
            )

            result = spawn_search_subagents(["query"])

        assert result["all_success"] is False
        assert result["subagents"][0]["status"] == "search_failed"


# ---------------------------------------------------------------------------
# read_subagent_results
# ---------------------------------------------------------------------------

class TestReadSubagentResults:
    def test_reads_all_files(self, tmp_path) -> None:
        results_dir = tmp_path / "results"
        results_dir.mkdir()
        for i in range(3):
            fpath = results_dir / f"subagent_{i:02d}.json"
            fpath.write_text(json.dumps({"idx": i}))

        data = read_subagent_results(str(results_dir))
        assert len(data) == 3
        assert data[0]["idx"] == 0

    def test_missing_dir(self) -> None:
        assert read_subagent_results("/nonexistent/path") == []

    def test_skips_non_subagent_files(self, tmp_path) -> None:
        results_dir = tmp_path / "results"
        results_dir.mkdir()
        (results_dir / "subagent_00.json").write_text(json.dumps({"ok": True}))
        (results_dir / "other.txt").write_text("hello")

        data = read_subagent_results(str(results_dir))
        assert len(data) == 1
        assert data[0]["ok"] is True
