"""Tests for the Research Analyst Agent LangGraph workflow."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from apps.research_analyst.research_graph import (
    aggregator_node,
    build_research_graph,
    citation_node,
    compile_research_graph,
    hitl_gate_node,
    lead_node,
    run_research,
    search_map_edge,
    search_map_node,
    search_worker,
    writer_node,
)
from apps.research_analyst.state import ResearchState, initial_state


# ---------------------------------------------------------------------------
# Graph compilation
# ---------------------------------------------------------------------------

class TestBuildResearchGraph:
    def test_compiles_without_errors(self) -> None:
        builder = build_research_graph()
        graph = builder.compile()
        assert graph is not None

    def test_has_all_required_nodes(self) -> None:
        builder = build_research_graph()
        nodes = getattr(builder, "nodes", {})
        required = {
            "lead",
            "search_map",
            "search_worker",
            "aggregator",
            "citation",
            "writer",
            "hitl_gate",
        }
        assert required <= set(nodes.keys())

    def test_graph_runnable_with_mock_search(self) -> None:
        """End-to-end run with mocked sub-agents so no network calls."""
        builder = build_research_graph()
        graph = builder.compile()

        state = initial_state("quantum computing")

        # Define mock responses for each subtopic
        def mock_spawn(subtopics, max_results=3, max_workers=3):
            if not subtopics:
                return {"results_dir": "/tmp/fake", "subagents": [], "all_success": True}
            subtopic = subtopics[0]
            return {
                "results_dir": "/tmp/fake",
                "subagents": [{
                    "subtopic": subtopic,
                    "file_path": f"/tmp/fake/subagent_{hash(subtopic)%100:02d}.json",
                    "sources": [f"https://example.com/{subtopic.replace(' ', '_')}"],
                    "status": "success",
                    "error": None,
                }],
                "all_success": True,
            }

        def mock_read(results_dir):
            # Return results based on the subtopic files
            return [{
                "metadata": {"sources": ["https://example.com/test"], "status": "success"},
                "search_results": [{"title": "Test", "url": "https://example.com/test"}],
            }]

        with patch(
            "apps.research_analyst.research_graph.spawn_search_subagents",
            side_effect=mock_spawn,
        ):
            with patch(
                "apps.research_analyst.research_graph.read_subagent_results",
                side_effect=mock_read,
            ):
                result = graph.invoke(state)

        assert result["topic"] == "quantum computing"
        assert result["plan"] is not None
        assert result["search_results"]
        assert result["draft"] is not None
        assert result["final_report"] is not None


# ---------------------------------------------------------------------------
# Individual nodes
# ---------------------------------------------------------------------------

class TestLeadNode:
    def test_plan_and_subtopics(self) -> None:
        state = initial_state("AI safety")
        out = lead_node(state)
        assert "plan" in out
        assert "search_subtopics" in out
        assert len(out["search_subtopics"]) == 3
        assert out["current_node"] == "lead"


class TestSearchMap:
    def test_returns_send_list(self) -> None:
        state = initial_state("neural networks")
        state["search_subtopics"] = ["a", "b", "c"]
        sends = search_map_edge(state)
        assert len(sends) == 3
        assert sends[0].node == "search_worker"
        assert sends[0].arg["subtopic"] == "a"

    def test_fallback_when_no_subtopics(self) -> None:
        state = initial_state("neural networks")
        sends = search_map_edge(state)
        assert len(sends) == 1
        assert sends[0].arg["subtopic"] == ""


class TestSearchMapNode:
    def test_returns_dict(self) -> None:
        state = initial_state("neural networks")
        out = search_map_node(state)
        assert "current_node" in out
        assert out["current_node"] == "search_map"


class TestSearchWorker:
    def test_produces_search_results(self) -> None:
        state = initial_state("machine learning")
        state["subtopic"] = "machine learning overview"
        state["index"] = 0

        with patch(
            "apps.research_analyst.research_graph.spawn_search_subagents"
        ) as mock_spawn:
            mock_spawn.return_value = {
                "results_dir": "/tmp/fake",
                "subagents": [
                    {
                        "subtopic": "machine learning overview",
                        "file_path": "/tmp/fake/subagent_00.json",
                        "sources": ["https://example.com/ml"],
                        "status": "success",
                        "error": None,
                    }
                ],
                "all_success": True,
            }
            with patch(
                "apps.research_analyst.research_graph.read_subagent_results"
            ) as mock_read:
                mock_read.return_value = [
                    {
                        "metadata": {
                            "sources": ["https://example.com/ml"],
                            "status": "success",
                        },
                        "search_results": [
                            {"title": "ML", "url": "https://example.com/ml"}
                        ],
                    }
                ]

                out = search_worker(state)

        # Check the index-specific output key
        assert "search_results_0" in out
        assert len(out["search_results_0"]) > 0
        assert out["search_results_0"][0]["subtopic"] == "machine learning overview"

    def test_empty_subtopic(self) -> None:
        state = initial_state("machine learning")
        state["subtopic"] = ""
        state["index"] = 0
        out = search_worker(state)
        assert out["search_results_0"] == []


class TestAggregatorNode:
    def test_deduplicates_by_url(self) -> None:
        state = initial_state("topic")
        state["search_results_0"] = [
            {"subtopic": "a", "url": "https://example.com", "source": "ex"},
        ]
        state["search_results_1"] = [
            {"subtopic": "b", "url": "https://example.com", "source": "ex"},
            {"subtopic": "c", "url": "https://other.com", "source": "ot"},
        ]
        out = aggregator_node(state)
        assert len(out["search_results"]) == 2


class TestCitationNode:
    def test_creates_verified_claims(self) -> None:
        state = initial_state("topic")
        state["search_results"] = [
            {"subtopic": "a", "url": "https://example.com", "source": "ex"},
        ]
        out = citation_node(state)
        assert len(out["verified_claims"]) == 1
        assert out["verified_claims"][0]["status"] == "verified"
        assert out["verified_claims"][0]["confidence"] == 0.8


class TestWriterNode:
    def test_generates_markdown(self) -> None:
        state = initial_state("space exploration")
        state["plan"] = "Plan"
        state["search_results"] = [
            {"subtopic": "a", "url": "https://example.com", "source": "ex"},
        ]
        state["verified_claims"] = [
            {"claim": "C", "source": "ex", "status": "verified", "confidence": 0.8}
        ]
        out = writer_node(state)
        assert "draft" in out
        assert "final_report" in out
        assert "# Research Report: space exploration" in out["draft"]
        assert "https://example.com" in out["draft"]


class TestHITLGateNode:
    def test_interrupts_when_budget_threshold_crossed(self) -> None:
        state = initial_state("topic")
        state["budget_limit"] = 1.0
        state["budget_spent"] = 0.9

        with patch(
            "apps.research_analyst.research_graph.HITLInterrupt"
        ) as MockHITL:
            mock_hitl = MockHITL.return_value
            mock_hitl.maybe_interrupt = patch(
                "agent.langgraph.hitl.interrupt"
            ).start()
            out = hitl_gate_node(state)
            assert out["current_node"] == "hitl_gate"

    def test_does_not_interrupt_when_under_threshold(self) -> None:
        state = initial_state("topic")
        state["budget_limit"] = 1.0
        state["budget_spent"] = 0.1

        out = hitl_gate_node(state)
        assert out["current_node"] == "hitl_gate"


# ---------------------------------------------------------------------------
# Compile helper
# ---------------------------------------------------------------------------

class TestCompileResearchGraph:
    def test_with_none_checkpointer(self) -> None:
        graph = compile_research_graph(checkpointer=None)
        assert graph is not None

    def test_with_interrupts(self) -> None:
        graph = compile_research_graph(
            checkpointer=None,
            interrupt_before=["hitl_gate"],
            interrupt_after=["writer"],
        )
        assert graph is not None


# ---------------------------------------------------------------------------
# Run helper
# ---------------------------------------------------------------------------

class TestRunResearch:
    def test_run_research(self) -> None:
        with patch(
            "apps.research_analyst.research_graph.spawn_search_subagents"
        ) as mock_spawn:
            mock_spawn.return_value = {
                "results_dir": "/tmp/fake",
                "subagents": [
                    {
                        "subtopic": "a",
                        "file_path": "/tmp/fake/subagent_00.json",
                        "sources": ["https://example.com"],
                        "status": "success",
                        "error": None,
                    }
                ],
                "all_success": True,
            }
            with patch(
                "apps.research_analyst.research_graph.read_subagent_results"
            ) as mock_read:
                mock_read.return_value = [
                    {
                        "metadata": {
                            "sources": ["https://example.com"],
                            "status": "success",
                        },
                        "search_results": [
                            {"title": "T", "url": "https://example.com"}
                        ],
                    }
                ]

                result = run_research("AI ethics", budget_limit=0.5)

        assert result["topic"] == "AI ethics"
        assert result["final_report"] is not None
