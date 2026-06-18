"""Research Analyst Agent — run manager and CLI entry point."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone

from apps.research_analyst.research_graph import (
    BUDGET_LIMIT,
    build_research_graph,
    initial_state,
)
from apps.research_analyst.state import ResearchState

log = logging.getLogger(__name__)

# Optional: LangSmith integration
try:
    from plugins.observability.langsmith_relay.tracer import (
        get_trace_url,
        trace_graph_run,
    )
    HAS_LANGSMITH = True
except ImportError:
    HAS_LANGSMITH = False

# Optional: PostgresSaver
try:
    from agent.langgraph.checkpointer import HermesPostgresSaver
    HAS_CHECKPOINTER = True
except ImportError:
    HAS_CHECKPOINTER = False


def run_analyst(topic: str, output_dir: str | None = None) -> dict:
    """Run the Research Analyst Agent on a topic and return results.

    Args:
        topic: Research question.
        output_dir: Directory for output files. Default: ~/research/

    Returns:
        Dict with keys: topic, report_path, trace_url, budget_spent, status
    """
    if output_dir is None:
        output_dir = os.path.expanduser("~/research/")
    os.makedirs(output_dir, exist_ok=True)

    # Try to attach checkpointer
    checkpointer = None
    if HAS_CHECKPOINTER:
        try:
            checkpointer = HermesPostgresSaver.from_hermes_config()
            log.info("PostgresSaver connected — checkpoints enabled")
        except Exception as e:
            log.warning("PostgresSaver unavailable (running without checkpoints): %s", e)

    # Build and run graph
    graph = build_research_graph(checkpointer=checkpointer)
    state = initial_state(topic, budget_limit=BUDGET_LIMIT)

    thread_id = f"research_{_slugify(topic)}_{os.urandom(4).hex()}"

    config = {"configurable": {"thread_id": thread_id}}
    if checkpointer:
        config["checkpointer"] = checkpointer

    result = graph.invoke(state, config=config)

    final_report = result.get("final_report", "")
    budget_spent = result.get("budget_spent", 0.0)

    # Write report
    report_filename = f"research_{_slugify(topic)}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    report_path = os.path.join(output_dir, report_filename)
    with open(report_path, "w") as f:
        f.write(final_report)

    # Get trace URL if available
    trace_url = None
    if HAS_LANGSMITH:
        try:
            trace_url = get_trace_url(thread_id, project="research-analyst")
        except Exception:
            pass

    return {
        "topic": topic,
        "report_path": report_path,
        "trace_url": trace_url,
        "budget_spent": budget_spent,
        "budget_limit": BUDGET_LIMIT,
        "status": "completed",
        "thread_id": thread_id,
    }


def main():
    """CLI entry point: python -m apps.research_analyst.run 'your question'"""
    topic = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Default research topic"
    result = run_analyst(topic)
    print(json.dumps(result, indent=2, default=str))
    print(f"\nReport: {result['report_path']}")


def _slugify(text: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in text).strip("_").lower()[:60]


if __name__ == "__main__":
    main()
