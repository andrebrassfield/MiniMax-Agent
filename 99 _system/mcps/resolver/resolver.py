#!/usr/bin/env python3
"""
resolver.py — the Skill Resolver. Routes a user query to the right Skill Pack.

The brain stem. When Mavis gets a generic prompt ("Clear out my tabs",
"What happened this week?", "Do I have anything on memory architectures?"),
the Resolver:
  1. Walks 99 _system/skillopt/skills/ to find all available Skill Packs
  2. Reads each skill.md to extract a description + tag set
  3. Optionally queries vault-brain for current vault state
  4. Builds a "ranking request" JSON that M3 fills in
  5. Validates the M3-produced ranking and returns it

Esalen posture: this is a thin API router. The Python does the I/O
(directory walking, file reading, JSON construction, validation). The
M3 context window does the actual classification and confidence scoring.
Per ESALEN-NOT-FOXCONN.md audit Q2: a deterministic layer trying to
classify prompts is the canonical Foxconn pattern. The Python gathers
inputs; M3 makes the call.

Two tools exposed:
  - resolver.build_ranking_request(query, top_k=2, include_vault_state=True)
      Gathers inputs, returns a ranking request JSON for M3 to fill in.
  - resolver.apply_ranking(request_id, ranking_json)
      Validates the M3-produced ranking, returns the final result.

Usage (CLI):
  # Build a request (writes sidecar JSON to 99 _system/mcps/resolver/_requests/)
  python3 resolver.py --query "Clear out my tabs"
  python3 resolver.py --query "What happened this week?" --top-k 3

  # Apply an M3-produced ranking from a file
  python3 resolver.py --apply-ranking <ranking.json>
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

__version__ = "0.1.0"

# ============================================================
# PATHS
# ============================================================

VAULT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent")
SKILLS_DIR = VAULT_ROOT / "99 _system" / "skillopt" / "skills"
RESOLVER_DIR = VAULT_ROOT / "99 _system" / "mcps" / "resolver"
REQUESTS_DIR = RESOLVER_DIR / "_requests"
AUDIT_LOG = RESOLVER_DIR / "resolver-audit.jsonl"

# Path to vault-brain for optional vault-state queries
VAULT_BRAIN_INDEX = VAULT_ROOT / "99 _system" / "mcps" / "vault-brain" / "index.json"
VAULT_BRAIN_PATH = VAULT_ROOT / "99 _system" / "mcps" / "vault-brain"

# Skip these when walking skills (the trailblazer and any non-pack dirs)
SKIP_SKILL_DIRS = {"__pycache__", "_archive"}


# ============================================================
# SKILL DISCOVERY
# ============================================================

@dataclass
class SkillSummary:
    """A minimal summary of a Skill Pack, used for routing."""
    name: str                           # e.g., "process-inbox"
    path: str                           # absolute path to the pack dir
    description: str                    # 1-line description from skill.md
    tags: list[str] = field(default_factory=list)
    has_action: bool = False
    has_tests: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def _read_first_paragraph(text: str) -> str:
    """Pull the first paragraph (or quoted tagline) from the skill.md body."""
    # Strip frontmatter
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5:]
    # Look for a blockquote tagline first (the Mavis style)
    m = re.search(r"^>\s*(.+?)$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    # Otherwise the first non-heading, non-empty line
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(">"):
            continue
        return line[:200]
    return "(no description)"


def _read_tags_from_skill_md(text: str) -> list[str]:
    """Extract tags from frontmatter if present, else from any 'tags:' list."""
    if not text.startswith("---\n"):
        return []
    end = text.find("\n---\n", 4)
    if end == -1:
        return []
    fm = text[4:end]
    m = re.search(r"^tags:\s*\[(.+?)\]", fm, re.MULTILINE | re.DOTALL)
    if m:
        return [t.strip().strip('"\'') for t in m.group(1).split(",") if t.strip()]
    return []


def discover_skills() -> list[SkillSummary]:
    """Walk SKILLS_DIR and return a SkillSummary for each valid Skill Pack."""
    if not SKILLS_DIR.exists():
        return []
    summaries = []
    for pack_dir in sorted(SKILLS_DIR.iterdir()):
        if not pack_dir.is_dir():
            continue
        if pack_dir.name in SKIP_SKILL_DIRS or pack_dir.name.startswith("_"):
            continue
        skill_md = pack_dir / "skill.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8", errors="ignore")
        summaries.append(SkillSummary(
            name=pack_dir.name,
            path=str(pack_dir),
            description=_read_first_paragraph(text),
            tags=_read_tags_from_skill_md(text),
            # Convention: action script is either `action.py` (legacy) or
            # `<skill_slug>_action.py` (newer per-skill namespacing)
            has_action=(
                (pack_dir / "action.py").exists()
                or any(p.name.endswith("_action.py") for p in pack_dir.glob("*_action.py"))
            ),
            has_tests=any(p.name.startswith("test_") for p in pack_dir.glob("test_*.py")),
        ))
    return summaries


# ============================================================
# VAULT STATE (lightweight, optional)
# ============================================================

def get_vault_state(include_notes: bool = False, max_notes: int = 5) -> dict:
    """Lightweight vault state for the ranking request.

    Returns: {today, recent_daily_exists, recent_intake_count, recent_commits: [...], top_notes: [...]}
    """
    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "today": datetime.now().strftime("%Y-%m-%d"),
    }

    # Today's daily note exists?
    today_daily = VAULT_ROOT / "01 Daily" / f"{state['today']}.md"
    state["today_daily_exists"] = today_daily.exists()

    # Inbox count + last few intake drops
    inbox = VAULT_ROOT / "00 Inbox"
    if inbox.exists():
        state["inbox_count"] = sum(1 for _ in inbox.glob("*.md"))
    else:
        state["inbox_count"] = 0

    # Last 5 git commits
    try:
        out = subprocess.check_output(
            ["git", "-C", str(VAULT_ROOT), "log", "-n5", "--pretty=format:%h|%ai|%s"],
            text=True, timeout=5,
        )
        state["recent_commits"] = [
            {"hash": h, "date": d, "subject": s}
            for line in out.splitlines() if "|" in line
            for h, d, s in [line.split("|", 2)]
        ][:5]
    except subprocess.CalledProcessError:
        state["recent_commits"] = []

    # Optional: top notes from vault-brain index (if it exists)
    if include_notes and VAULT_BRAIN_INDEX.exists():
        try:
            idx = json.loads(VAULT_BRAIN_INDEX.read_text(encoding="utf-8"))
            # Top-level summary only — don't dump the whole index
            state["vault_brain_indexed_at"] = idx.get("indexed_at")
            state["vault_brain_note_count"] = idx.get("note_count", 0)
            # Top 5 by title (we don't have scores pre-query, so just the first 5)
            if isinstance(idx.get("notes"), list):
                state["top_notes"] = [
                    {"path": n.get("path"), "title": n.get("title")}
                    for n in idx["notes"][:max_notes]
                ]
        except (json.JSONDecodeError, OSError):
            state["top_notes"] = []

    return state


# ============================================================
# RANKING REQUEST
# ============================================================

@dataclass
class RankingRequest:
    """A request for M3 to rank Skill Packs against a user query.

    Built by build_ranking_request(). M3 fills in `ranking` (top-K skills
    with confidence scores) and `reasoning` (1-2 sentence justification).
    """
    request_id: str
    query: str
    top_k: int
    generated_at: str
    available_skills: list[dict]
    vault_state: dict
    prompt_hint: str = ""
    ranking: list[dict] = field(default_factory=list)
    reasoning: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def build_ranking_request(
    query: str,
    top_k: int = 2,
    include_vault_state: bool = True,
    prompt_hint: str = "",
) -> RankingRequest:
    """Build a RankingRequest. M3 fills in the `ranking` field."""
    skills = discover_skills()
    vault_state = get_vault_state(include_notes=False) if include_vault_state else {}
    return RankingRequest(
        request_id=f"rank-{int(time.time())}-{uuid.uuid4().hex[:6]}",
        query=query,
        top_k=top_k,
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        available_skills=[s.to_dict() for s in skills],
        vault_state=vault_state,
        prompt_hint=prompt_hint,
    )


def render_ranking_prompt(req: RankingRequest) -> str:
    """Render the M3 prompt for filling in the ranking. Pure deterministic."""
    skills_list = "\n".join(
        f"  - name: `{s['name']}`\n    description: {s['description']}\n    tags: {', '.join(s.get('tags', [])) or '(none)'}\n    has_action: {s.get('has_action')}, has_tests: {s.get('has_tests')}"
        for s in req.available_skills
    )
    vault_state_str = json.dumps(req.vault_state, indent=2)

    return f"""You are Mavis, the executive assistant. A user (Andre) just said:

  > {req.query}

Your job: rank the available Skill Packs by how well they apply to this query.
Return the top {req.top_k} skills with a confidence score in [0.0, 1.0] and
a 1-2 sentence justification. **The Python script does NOT make this call —
you do, in your context window.**

## Available Skill Packs

{skills_list}

## Current vault state

```json
{vault_state_str}
```

{('## Hint\n' + req.prompt_hint) if req.prompt_hint else ''}

## How to score

- 0.95-1.00: this skill was built for exactly this query
- 0.85-0.94: strong match, minor gap
- 0.70-0.84: relevant but not the best fit
- 0.50-0.69: weak match
- < 0.50: don't include in the ranking

## Output format

Emit ONLY a JSON object with this exact shape (no preamble, no markdown fences):

```json
{{
  "ranking": [
    {{"skill_name": "skill-pack-name", "confidence": 0.0, "one_line_match": "why this fits"}},
    ...up to {req.top_k} entries
  ],
  "reasoning": "1-2 sentence overall justification"
}}
```"""


# ============================================================
# APPLY RANKING (validates M3's output)
# ============================================================

def validate_ranking(req: RankingRequest, ranking_data: dict) -> tuple[list[str], list[dict]]:
    """Validate M3's ranking output. Returns (errors, valid_entries).

    - `ranking_data` must be a dict with `ranking` (list) and `reasoning` (str)
    - Each ranking entry: skill_name (must exist), confidence (in [0,1]),
      one_line_match (non-empty)
    - At most req.top_k entries
    """
    errors = []
    if not isinstance(ranking_data, dict):
        return ([f"ranking_data must be a dict, got: {type(ranking_data).__name__}"], [])

    if "ranking" not in ranking_data or not isinstance(ranking_data["ranking"], list):
        errors.append("ranking must be a list")
    if "reasoning" not in ranking_data or not str(ranking_data["reasoning"]).strip():
        errors.append("reasoning is required and must be non-empty")

    if errors:
        return (errors, [])

    if len(ranking_data["ranking"]) > req.top_k:
        errors.append(f"ranking has {len(ranking_data['ranking'])} entries, max is {req.top_k}")

    valid_names = {s["name"] for s in req.available_skills}
    valid = []
    for i, e in enumerate(ranking_data["ranking"]):
        if not isinstance(e, dict):
            errors.append(f"ranking[{i}] is not a dict")
            continue
        for field in ("skill_name", "confidence", "one_line_match"):
            if field not in e:
                errors.append(f"ranking[{i}] missing field: {field!r}")
        if errors and len(errors) > 10:
            break
        if e.get("skill_name") not in valid_names:
            errors.append(f"ranking[{i}].skill_name not in available skills: {e.get('skill_name')!r}")
            continue
        try:
            conf = float(e["confidence"])
            if not (0.0 <= conf <= 1.0):
                errors.append(f"ranking[{i}].confidence {conf} out of [0,1]")
                continue
        except (TypeError, ValueError):
            errors.append(f"ranking[{i}].confidence not a number: {e.get('confidence')!r}")
            continue
        if not str(e.get("one_line_match", "")).strip():
            errors.append(f"ranking[{i}].one_line_match is empty")
            continue
        valid.append({
            "skill_name": e["skill_name"],
            "confidence": round(conf, 3),
            "one_line_match": e["one_line_match"].strip(),
        })
    return (errors, valid)


def apply_ranking(
    request_id: str,
    ranking_data: dict,
    *,
    request: RankingRequest | None = None,
) -> dict:
    """Apply M3's ranking to a saved or in-memory request.

    If `request` is None, the request is loaded from the saved sidecar.
    """
    if request is None:
        request = load_request(request_id)
        if request is None:
            return {"error": f"request_id not found: {request_id}"}

    errors, valid = validate_ranking(request, ranking_data)
    if errors:
        return {
            "request_id": request_id,
            "status": "invalid",
            "errors": errors,
        }

    # Write the sidecar
    result = {
        "request_id": request_id,
        "query": request.query,
        "top_k": request.top_k,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "reasoning": ranking_data.get("reasoning", "").strip(),
        "ranking": valid,
        "status": "ok",
    }

    # Audit log
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        audit_entry = {
            "ts": result["generated_at"],
            "request_id": request_id,
            "query": request.query,
            "top_k": request.top_k,
            "ranking_count": len(valid),
            "top_skill": valid[0]["skill_name"] if valid else None,
            "top_confidence": valid[0]["confidence"] if valid else None,
            "script_version": __version__,
        }
        f.write(json.dumps(audit_entry) + "\n")

    return result


# ============================================================
# REQUEST PERSISTENCE
# ============================================================

def save_request(req: RankingRequest) -> Path:
    """Persist a request to disk for later apply_ranking() calls."""
    REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REQUESTS_DIR / f"{req.request_id}.json"
    path.write_text(json.dumps(req.to_dict(), indent=1, ensure_ascii=False), encoding="utf-8")
    return path


def load_request(request_id: str) -> RankingRequest | None:
    """Load a saved request from disk."""
    path = REQUESTS_DIR / f"{request_id}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return RankingRequest(
        request_id=data["request_id"],
        query=data["query"],
        top_k=data["top_k"],
        generated_at=data["generated_at"],
        available_skills=data["available_skills"],
        vault_state=data.get("vault_state", {}),
        prompt_hint=data.get("prompt_hint", ""),
        ranking=data.get("ranking", []),
        reasoning=data.get("reasoning", ""),
    )


# ============================================================
# MCP SERVER
# ============================================================

def run_mcp_server() -> None:
    """Run the resolver MCP server over stdio."""
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import TextContent, Tool
    except ImportError:
        print("ERROR: mcp package not installed. pip install mcp[cli]", file=sys.stderr)
        sys.exit(1)

    server = Server("resolver")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="resolver.build_ranking_request",
                description=(
                    "Build a Skill-Pack ranking request for a user query. "
                    "Gathers the available Skill Packs and (optionally) the "
                    "current vault state, then returns a request JSON. "
                    "M3 fills in the ranking + confidence scores; you then "
                    "call resolver.apply_ranking() with the result. Per the "
                    "Esalen posture, the Python does the I/O; M3 does the "
                    "classification — model-judges-itself is Foxconn."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The user's query"},
                        "top_k": {"type": "integer", "default": 2, "minimum": 1, "maximum": 5},
                        "include_vault_state": {"type": "boolean", "default": True},
                        "prompt_hint": {"type": "string", "default": ""},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="resolver.apply_ranking",
                description=(
                    "Apply M3's ranking to a previously-built request. "
                    "Validates the ranking structure (top-K, confidence in [0,1], "
                    "skill names exist, one-line matches non-empty) and returns "
                    "the final routing decision. Reads the saved request from "
                    "the sidecar at 99 _system/mcps/resolver/_requests/."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "request_id": {
                            "type": "string",
                            "description": "The request_id returned by build_ranking_request()",
                        },
                        "ranking_data": {
                            "type": "object",
                            "description": "M3's ranking output: {ranking: [...], reasoning: '...'}",
                        },
                    },
                    "required": ["request_id", "ranking_data"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "resolver.build_ranking_request":
                req = build_ranking_request(
                    arguments["query"],
                    top_k=arguments.get("top_k", 2),
                    include_vault_state=arguments.get("include_vault_state", True),
                    prompt_hint=arguments.get("prompt_hint", ""),
                )
                # Persist for later apply_ranking
                path = save_request(req)
                # Return both the request and the prompt
                result = {
                    "request_id": req.request_id,
                    "saved_to": str(path.relative_to(VAULT_ROOT)),
                    "request": req.to_dict(),
                    "prompt": render_ranking_prompt(req),
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

            if name == "resolver.apply_ranking":
                result = apply_ranking(
                    arguments["request_id"],
                    arguments["ranking_data"],
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

            raise ValueError(f"unknown tool: {name}")

        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": f"{type(e).__name__}: {e}"}, indent=2))]

    import asyncio

    async def main():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    asyncio.run(main())


# ============================================================
# CLI
# ============================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        prog="resolver.py",
        description="Skill Resolver — routes a user query to the right Skill Pack",
    )
    ap.add_argument("--query", metavar="Q", help="Build a ranking request for this query")
    ap.add_argument("--top-k", type=int, default=2, help="Top-K skills to return (default 2)")
    ap.add_argument("--no-vault-state", action="store_true", help="Skip vault-state gathering")
    ap.add_argument("--list-skills", action="store_true", help="List all discovered Skill Packs and exit")
    ap.add_argument("--apply-ranking", metavar="RANKING_JSON", type=Path,
                    help="Apply M3's ranking from this file (use --with-request-id)")
    ap.add_argument("--with-request-id", metavar="RID",
                    help="The request_id for --apply-ranking (required with --apply-ranking)")
    ap.add_argument("--serve", action="store_true", help="Run as MCP server (stdio)")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = ap.parse_args()

    if args.serve:
        run_mcp_server()
        return 0

    if args.list_skills:
        skills = discover_skills()
        print(json.dumps([s.to_dict() for s in skills], indent=2))
        return 0

    if args.apply_ranking:
        if not args.with_request_id:
            ap.error("--with-request-id is required with --apply-ranking")
        ranking_data = json.loads(args.apply_ranking.read_text(encoding="utf-8"))
        result = apply_ranking(args.with_request_id, ranking_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("status") == "ok" else 1

    if args.query:
        req = build_ranking_request(
            args.query,
            top_k=args.top_k,
            include_vault_state=not args.no_vault_state,
        )
        path = save_request(req)
        prompt = render_ranking_prompt(req)
        prompt_path = REQUESTS_DIR / f"{req.request_id}-prompt.txt"
        prompt_path.write_text(prompt, encoding="utf-8")
        # Print a one-line report + the prompt on stdout
        print(f"OK  request_id    = {req.request_id}", file=sys.stderr)
        print(f"    query         = {req.query}", file=sys.stderr)
        print(f"    top_k         = {req.top_k}", file=sys.stderr)
        print(f"    available     = {len(req.available_skills)} skills: {[s['name'] for s in req.available_skills]}", file=sys.stderr)
        print(f"    request saved = {path.relative_to(VAULT_ROOT)}", file=sys.stderr)
        print(f"    prompt saved  = {prompt_path.relative_to(VAULT_ROOT)}", file=sys.stderr)
        print(f"\nNEXT STEP: read the prompt, emit a JSON ranking per the format,", file=sys.stderr)
        print(f"           then run:", file=sys.stderr)
        print(f"             python3 resolver.py --apply-ranking ranking.json --with-request-id {req.request_id}", file=sys.stderr)
        # Also print the request JSON to stdout for piping
        print(json.dumps(req.to_dict(), indent=2, ensure_ascii=False))
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
