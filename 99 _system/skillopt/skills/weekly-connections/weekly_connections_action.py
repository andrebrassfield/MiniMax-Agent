#!/usr/bin/env python3
"""
action.py — I/O layer for the weekly-connections Skill.

Pure deterministic code. Reads M3's JSON output (list of 3-5 connection
objects) and creates one markdown file per connection in `06 Connections/`.
NO LLM calls here — all connection judgments come from M3's JSON.

Esalen split: M3 does the qualitative judgment (which notes connect, what
type, what's the bridge). Python does the deterministic I/O (filename,
write, body section validation, audit log). Tests cover Python.

Usage (programmatic):
    import action
    result = action.render_connections(m3_output, date="2026-06-02")

Usage (CLI):
    action.py --m3-output /tmp/m3-connections.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

__version__ = "0.1.0"

# ============================================================
# PATHS
# ============================================================

VAULT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent")
CONNECTIONS_DIR = VAULT_ROOT / "06 Connections"
AUDIT_LOG = VAULT_ROOT / "99 _system" / "logs" / "weekly-connections-audit.jsonl"

VALID_TYPES = {"A", "B", "C", "D"}
REQUIRED_BODY_SECTIONS = ["## Why this connection matters", "## The bridge"]


# ============================================================
# VALIDATION
# ============================================================

def validate_m3_output(m3_output: dict) -> None:
    """Raise ValueError on bad M3 output."""
    if not isinstance(m3_output, dict):
        raise ValueError(f"m3_output must be a dict, got: {type(m3_output).__name__}")
    if "week_label" not in m3_output or not str(m3_output["week_label"]).strip():
        raise ValueError("week_label is required and must be non-empty")
    if "connections" not in m3_output or not isinstance(m3_output["connections"], list):
        raise ValueError("connections must be a list")
    if len(m3_output["connections"]) > 5:
        raise ValueError(f"too many connections ({len(m3_output['connections'])}); max 5")
    for i, c in enumerate(m3_output["connections"]):
        for field in ("type", "bridge", "slug", "sources", "body"):
            if field not in c:
                raise ValueError(f"connections[{i}] missing field: {field!r}")
        if c["type"] not in VALID_TYPES:
            raise ValueError(
                f"connections[{i}].type must be one of {sorted(VALID_TYPES)}, got: {c['type']!r}"
            )
        if not isinstance(c["sources"], list) or len(c["sources"]) < 2:
            raise ValueError(
                f"connections[{i}].sources must be a list of 2+ wikilinks, got: {c['sources']!r}"
            )
        if c["type"] == "C" and len(c["sources"]) < 3:
            raise ValueError(
                f"connections[{i}] is type C but has only {len(c['sources'])} sources (need 3+)"
            )
        # body must contain the required sections
        for section in REQUIRED_BODY_SECTIONS:
            if section not in c["body"]:
                raise ValueError(
                    f"connections[{i}].body missing required section: {section!r}"
                )
        # slug must be kebab-case (no spaces, no uppercase)
        if not c["slug"].islower() or " " in c["slug"]:
            raise ValueError(
                f"connections[{i}].slug must be kebab-case (lowercase, hyphens, no spaces): {c['slug']!r}"
            )


# ============================================================
# MARKDOWN RENDER
# ============================================================

def render_connection_file(connection: dict, date_str: str) -> str:
    """Render a single connection object to the connection-note markdown."""
    type_label = {
        "A": "Same principle, different domains",
        "B": "Contradiction as insight",
        "C": "Pattern across 3+ notes",
        "D": "Accidental answer to a question",
    }[connection["type"]]

    sources_str = ", ".join(connection["sources"])
    body = connection["body"].strip()

    lines = [
        f"# {connection['slug']} — Type {connection['type']}: {connection['bridge']}",
        "",
        f"**Type**: {connection['type']} — {type_label}",
        f"**Date**: {date_str}",
        f"**Sources**: {sources_str}",
        "",
        body,
    ]
    return "\n".join(lines) + "\n"


# ============================================================
# AUDIT LOG
# ============================================================

def write_audit_log(entry: dict) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ============================================================
# MAIN ENTRYPOINT
# ============================================================

def render_connections(
    m3_output: dict,
    *,
    date: str | None = None,
    overwrite: bool = False,
) -> dict:
    """Validate M3's JSON, render each connection as a markdown file.

    Args:
        m3_output: the JSON object M3 produced per skill.md schema
        date: optional ISO date override (defaults to today)
        overwrite: if True, overwrite existing connection files

    Returns:
        dict with: week_label, files_written, types_distribution, audit_logged, status

    Raises:
        ValueError: bad m3_output
        FileExistsError: a connection file with the same slug already exists (when overwrite=False)
    """
    validate_m3_output(m3_output)

    date_str = date or datetime.now().strftime("%Y-%m-%d")
    CONNECTIONS_DIR.mkdir(parents=True, exist_ok=True)

    written = []
    types_dist = {t: 0 for t in VALID_TYPES}
    for c in m3_output["connections"]:
        types_dist[c["type"]] += 1
        fname = f"{date_str} - {c['slug']}.md"
        out_path = CONNECTIONS_DIR / fname
        if out_path.exists() and not overwrite:
            raise FileExistsError(
                f"connection file already exists: {out_path} (use overwrite=True)"
            )
        out_path.write_text(render_connection_file(c, date_str), encoding="utf-8")
        written.append(str(out_path.relative_to(VAULT_ROOT)))

    audit_entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "week_label": m3_output["week_label"],
        "date": date_str,
        "files_written": written,
        "count": len(written),
        "types_distribution": types_dist,
        "overwrite": overwrite,
        "script_version": __version__,
    }
    write_audit_log(audit_entry)

    return {
        "week_label": m3_output["week_label"],
        "date": date_str,
        "files_written": written,
        "types_distribution": types_dist,
        "count": len(written),
        "audit_logged": True,
        "status": "ok",
    }


# ============================================================
# CLI
# ============================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        prog="action.py",
        description="I/O layer for the weekly-connections Skill. Reads M3 JSON "
                    "from --m3-output and creates one file per connection in 06 Connections/.",
    )
    ap.add_argument("--m3-output", help="Path to a file containing M3's JSON output")
    ap.add_argument("--date", help="Override the date (YYYY-MM-DD, default: today)")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing connection files")
    ap.add_argument("--version", action="version", version=f"action.py v{__version__}")
    args = ap.parse_args()

    if not args.m3_output:
        ap.error("--m3-output is required (omit for --version)")

    try:
        m3_output = json.loads(Path(args.m3_output).read_text(encoding="utf-8"))
        result = render_connections(m3_output, date=args.date, overwrite=args.overwrite)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"action.py: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
