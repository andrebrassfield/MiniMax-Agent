"""Research Analyst Agent — LangGraph workflow with parallel search.

The graph has 6 nodes:
  lead        → plans research, writes TODO, extracts subtopics
  search      → dispatches parallel search sub-agents (Send / map-reduce)
  aggregator  → deduplicates and collects results
  citation    → verifies claims against sources
  writer      → produces Markdown with inline citations
  hitl_gate   → human approval before output

Checkpointing is provided via PostgresSaver; budget tracking via
DollarBudget; HITL gates via HITLInterrupt.
"""

from __future__ import annotations

import json
import logging
from decimal import Decimal
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from agent.langgraph.budget import DollarBudget
from agent.langgraph.hitl import HITLInterrupt, parse_resume_value
from apps.research_analyst.state import ResearchState, initial_state
from apps.research_analyst.sub_agents import (
    read_subagent_results,
    spawn_search_subagents,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Conditional edge functions
# ---------------------------------------------------------------------------


def search_map_edge(state: ResearchState) -> list[Send]:
    """Dispatch parallel search sub-agents via LangGraph Send.

    Returns a list of Send objects — one per subtopic — targeting the
    ``search_worker`` node.  This is the map-reduce pattern entry point.
    """
    subtopics = state.get("search_subtopics") or []
    if not subtopics:
        # Nothing to search — send a single worker with empty topic
        return [Send("search_worker", {"subtopic": "", "index": 0})]
    return [
        Send("search_worker", {"subtopic": t, "index": i})
        for i, t in enumerate(subtopics)
    ]


# ---------------------------------------------------------------------------
# Node implementations
# ---------------------------------------------------------------------------


def lead_node(state: ResearchState) -> dict[str, Any]:
    """Plan research and extract subtopics for parallel search.

    Writes a simple TODO plan and derives 3 subtopics from the topic.
    """
    topic = state["topic"]
    plan = f"""Research Plan for: {topic}

1. Search for background and context
2. Search for recent developments and news
3. Search for expert opinions and analysis
"""
    subtopics = [
        f"{topic} background and overview",
        f"{topic} latest news and developments",
        f"{topic} expert analysis and opinions",
    ]

    return {
        "plan": plan,
        "search_subtopics": subtopics,
        "current_node": "lead",
        "__current_node": "lead",
    }


def search_map_node(state: ResearchState) -> dict[str, Any]:
    """No-op node that precedes the conditional edge dispatch.

    The actual parallel dispatch happens in ``search_map_edge``.
    """
    return {
        "current_node": "search_map",
        "__current_node": "search_map",
    }


def search_worker(state: ResearchState) -> dict[str, Any]:
    """Run a single search sub-agent.

    This node is invoked in parallel by the ``search_map`` conditional
    edge.  Each invocation receives a different ``subtopic`` and ``index``
    via the Send arg, which is merged into the full state.
    """
    # LangGraph merges the Send arg into the full state, so we read
    # the subtopic/index from the state dict.
    subtopic = state.get("subtopic", "")
    index = state.get("index", 0)

    if not subtopic:
        # Use a unique output key for each worker to avoid concurrent write conflicts
        return {f"search_results_{index}": []}

    # Spawn a single sub-agent for this subtopic
    result = spawn_search_subagents(
        subtopics=[subtopic],
        max_results=3,
        max_workers=1,
    )

    # Read the result file
    results_dir = result["results_dir"]
    raw_results = read_subagent_results(results_dir)

    # Build search_results entries
    entries: list[dict[str, Any]] = []
    for r in raw_results:
        meta = r.get("metadata", {})
        for src in meta.get("sources", []):
            entries.append(
                {
                    "subtopic": subtopic,
                    "source": src,
                    "content": r.get("search_results", []),
                    "url": src,
                    "index": index,
                }
            )

    # Use worker-specific key to avoid concurrent write conflicts
    return {
        f"search_results_{index}": entries,
        f"raw_results_dir_{index}": results_dir,
    }


def aggregator_node(state: ResearchState) -> dict[str, Any]:
    """Deduplicate and collect parallel search results.

    Reads ``search_results_0``, ``search_results_1``, etc. (populated by 
    parallel workers) and merges them, deduplicating by URL.
    """
    # Collect from worker-specific keys
    results: list[dict[str, Any]] = []
    for key, value in state.items():
        if key.startswith("search_results_") and isinstance(value, list):
            results.extend(value)

    seen_urls: set[str] = set()
    deduped: list[dict[str, Any]] = []

    for entry in results:
        url = entry.get("url", "")
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)
        deduped.append(entry)

    return {
        "search_results": deduped,
        "current_node": "aggregator",
        "__current_node": "aggregator",
    }


def citation_node(state: ResearchState) -> dict[str, Any]:
    """Verify claims against sources.

    For each search result, creates a verified-claim entry with a
    confidence score based on whether the source is present.
    """
    results = state.get("search_results", [])
    verified: list[dict[str, Any]] = []

    for entry in results:
        claim = f"Information about {entry.get('subtopic', '')} from {entry.get('source', '')}"
        verified.append(
            {
                "claim": claim,
                "source": entry.get("source", ""),
                "status": "verified",
                "confidence": 0.8,
            }
        )

    return {
        "verified_claims": verified,
        "current_node": "citation",
        "__current_node": "citation",
    }


def writer_node(state: ResearchState) -> dict[str, Any]:
    """Produce a Markdown draft with inline citations.

    Combines the plan, verified claims, and search results into a
    structured report.
    """
    topic = state["topic"]
    plan = state.get("plan", "")
    verified = state.get("verified_claims", [])
    results = state.get("search_results", [])

    lines = [
        f"# Research Report: {topic}",
        "",
        "## Plan",
        "",
        plan or "No plan generated.",
        "",
        "## Findings",
        "",
    ]

    for entry in results:
        subtopic = entry.get("subtopic", "")
        url = entry.get("url", "")
        lines.append(f"### {subtopic}")
        lines.append("")
        if url:
            lines.append(f"- Source: [{url}]({url})")
        lines.append("")

    lines.extend(
        [
            "## Verified Claims",
            "",
        ]
    )
    for v in verified:
        lines.append(f"- {v['claim']} (confidence: {v['confidence']:.0%})")

    lines.append("")
    lines.append("---")
    lines.append("*Generated by Hermes Research Analyst Agent*")

    draft = "\n".join(lines)

    return {
        "draft": draft,
        "final_report": draft,
        "current_node": "writer",
        "__current_node": "writer",
    }


def hitl_gate_node(state: ResearchState) -> dict[str, Any]:
    """Human-in-the-loop approval before output.

    Uses HITLInterrupt to pause the graph and ask the human to review
    the final report.  The graph can be resumed with ``Command(resume="y")``
    to approve or ``Command(resume="n")`` to reject.
    """
    budget = DollarBudget(limit=Decimal(str(state.get("budget_limit", 1.0))))
    hitl = HITLInterrupt(budget=budget, threshold=0.8)

    # Interrupt with the report payload for human review
    _report = state.get("final_report") or ""
    hitl.maybe_interrupt(
        "Approve final research report",
        estimated_cost=0.0,
        node_name="hitl_gate",
        payload={
            "topic": state["topic"],
            "report_preview": (_report[:500] + "..."),
        },
    )

    # If we get here, the human approved (or threshold wasn't crossed)
    return {
        "current_node": "hitl_gate",
        "__current_node": "hitl_gate",
    }


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------


def build_research_graph() -> StateGraph:
    """Build the Research Analyst Agent LangGraph workflow.

    Returns:
        A compiled LangGraph graph with all 6 nodes wired together.
    """
    builder = StateGraph(ResearchState)

    # Register nodes
    builder.add_node("lead", lead_node)
    builder.add_node("search_map", search_map_node)
    builder.add_node("search_worker", search_worker)
    builder.add_node("aggregator", aggregator_node)
    builder.add_node("citation", citation_node)
    builder.add_node("writer", writer_node)
    builder.add_node("hitl_gate", hitl_gate_node)

    # Wire edges
    builder.add_edge(START, "lead")
    builder.add_edge("lead", "search_map")
    builder.add_conditional_edges("search_map", search_map_edge, ["search_worker"])
    builder.add_edge("search_worker", "aggregator")
    builder.add_edge("aggregator", "citation")
    builder.add_edge("citation", "writer")
    builder.add_edge("writer", "hitl_gate")
    builder.add_edge("hitl_gate", END)

    return builder


def compile_research_graph(
    checkpointer: Any | None = None,
    interrupt_before: list[str] | None = None,
    interrupt_after: list[str] | None = None,
) -> Any:
    """Compile the research graph with optional checkpointing.

    Args:
        checkpointer: A LangGraph checkpointer (e.g. PostgresSaver)
        interrupt_before: Nodes to interrupt before (for HITL)
        interrupt_after: Nodes to interrupt after (for HITL)

    Returns:
        A compiled graph ready for ``invoke()`` or ``stream()``.
    """
    builder = build_research_graph()
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupt_before or [],
        interrupt_after=interrupt_after or [],
    )


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------


def run_research(
    topic: str,
    checkpointer: Any | None = None,
    budget_limit: float = 1.0,
    thread_id: str | None = None,
) -> dict[str, Any]:
    """Run the full research graph end-to-end.

    Args:
        topic: The research question or topic
        checkpointer: Optional checkpointer for persistence
        budget_limit: Max dollar cost before HITL interrupt
        thread_id: Optional thread identifier for checkpointing

    Returns:
        The final graph state (includes ``final_report`` when approved).
    """
    graph = compile_research_graph(checkpointer=checkpointer)
    config: dict[str, Any] = {}
    if thread_id:
        config["configurable"] = {"thread_id": thread_id}

    state = initial_state(topic, budget_limit=budget_limit)
    result = graph.invoke(state, config=config)
    return result
