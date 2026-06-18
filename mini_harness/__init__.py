"""
Mini-Harness: A reference implementation of an agent harness.

Components:
- Tool registry with @tool decorator + JSON-schema generation
- CLAUDE.md-style system prompt loader
- SKILL.md progressive disclosure loader
- Sub-agent spawn with isolated context
- Filesystem offload for large results (>20K tokens)
- Auto-compaction at 85% context window
- Pluggable hook system (pre_tool, post_tool, stop)
- OpenTelemetry tracing
- Durable SQLite checkpointing
"""

__version__ = "0.1.0"