"""Research Analyst Agent — state definition for the LangGraph workflow."""

from __future__ import annotations

from typing import Annotated, Optional, Sequence

from langgraph.channels.base import BaseChannel
from langgraph.graph.message import add_messages
from langgraph.managed import RemainingSteps
from typing_extensions import TypedDict


class ResearchState(TypedDict):
    """State of the Research Analyst Agent graph.

    Each node reads from and writes to this dict.
    The graph passes it from node to node, checkpointing after each step.
    """

    # --- Input ---
    topic: str
    """The research question or topic to investigate."""

    # --- Planning ---
    plan: Optional[str]
    """TODO list / research plan written by the lead node."""
    search_subtopics: Optional[list[str]]
    """Subtopics extracted from the plan for parallel search."""

    # --- Search ---
    search_results: Annotated[list[dict], "add"]
    """Aggregated results from parallel search sub-agents.
    Each entry: {subtopic, source, content, url}
    Uses 'add' reducer to allow concurrent writes from parallel workers.
    """
    raw_results_dir: Optional[str]
    """Directory where sub-agents wrote their results files."""

    # --- Verification ---
    verified_claims: Annotated[list[dict], "add"]
    """Claims that passed citation verification.
    Uses 'add' reducer for parallel accumulation.
    """

    # --- Writing ---
    draft: Optional[str]
    """Initial markdown draft (without citations verified)."""
    final_report: Optional[str]
    """Final markdown report with inline citations."""

    # --- Budget & Control ---
    budget_spent: float
    """Dollar cost accumulated so far in this run."""
    budget_limit: float
    """Maximum dollar cost before HITL interrupt fires (default 1.0)."""
    current_node: Optional[str]
    """Name of the node currently executing (for observability)."""

    # --- Output ---
    trace_url: Optional[str]
    """LangSmith trace URL for this run."""

    # --- LangGraph internals ---
    __remaining_steps: RemainingSteps
    """Tracks remaining recursion steps for LangGraph."""


def initial_state(topic: str, budget_limit: float = 1.0) -> dict:
    """Create a fresh ResearchState dict for a new research run."""
    return {
        "topic": topic,
        "plan": None,
        "search_subtopics": None,
        "search_results": [],
        "raw_results_dir": None,
        "verified_claims": [],
        "draft": None,
        "final_report": None,
        "budget_spent": 0.0,
        "budget_limit": budget_limit,
        "current_node": None,
        "trace_url": None,
    }