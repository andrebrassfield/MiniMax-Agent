#!/usr/bin/env python3
"""
update_state_of_mavis.py — End-of-session state-of-mavis.md regenerator.

Esalen posture: thin harvester + M3 synthesis. The Python does only the
deterministic I/O (git log, file counts, daily note, friction log extract).
The synthesis is M3's job, called via the mavis LLM client when wired.

Per the Esalen operating principle (99 _system/ESALEN-NOT-FOXCONN.md):
- The code is a thin deterministic layer, not a model-judging-itself loop.
- The harvesters do I/O, the can_i() classifier is rule-based (mirrors SOUL),
  the prompt assembler builds the M3 input. M3 does the synthesis.

Usage:
    update_state_of_mavis.py --harvest              # JSON of harvested data
    update_state_of_mavis.py --audit                # can_i() on session actions
    update_state_of_mavis.py --assemble-prompt      # M3 synthesis prompt
    update_state_of_mavis.py --dry-run              # harvest + audit + prompt
    update_state_of_mavis.py --apply < file         # write synthesized content
    update_state_of_mavis.py --version              # script version

When the self-model-card MCP is built, can_i_rule_based() is replaced by a
call to the can_i() MCP tool. Until then, the rule-based version is the
deterministic layer that mirrors SOUL.md.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

__version__ = "0.1.0"

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/Users/brassfieldventuresllc/MiniMax-Agent"))
STATE_FILE = VAULT_ROOT / "state-of-mavis.md"
INBOX = VAULT_ROOT / "00 Inbox"
PROJECTS = VAULT_ROOT / "03 Projects"
DAILY = VAULT_ROOT / "01 Daily"
SOUL_FILE = VAULT_ROOT / "SOUL.md"

# ============================================================
# HARVESTERS — deterministic I/O, ~50 lines total
# ============================================================

def get_last_state_commit() -> str:
    """Get the commit hash where state-of-mavis.md was last touched."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", "state-of-mavis.md"],
        cwd=VAULT_ROOT, capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()

def get_commits_since(since_commit: str) -> str:
    """Get all commits since the given commit, with per-commit file changes."""
    result = subprocess.run(
        ["git", "log", f"{since_commit}..HEAD", "--format=COMMIT:%H|%ai|%s", "--name-status"],
        cwd=VAULT_ROOT, capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()

def count_inbox() -> int:
    """Count files in 00 Inbox/ (excluding dotfiles)."""
    if not INBOX.exists():
        return 0
    return sum(1 for f in INBOX.iterdir() if f.is_file() and not f.name.startswith("."))

def get_open_projects() -> list:
    """List 03 Projects/ subfolders + extract title/status from their Overview."""
    if not PROJECTS.exists():
        return []
    projects = []
    for sub in sorted(PROJECTS.iterdir()):
        if not sub.is_dir() or sub.name.startswith("."):
            continue
        overview = sub / "00 Overview.md"
        if not overview.exists():
            projects.append({"name": sub.name, "title": sub.name, "status": "no-overview"})
            continue
        content = overview.read_text(encoding="utf-8")
        title, status = sub.name, "unknown"
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
            if line.lower().startswith("status:"):
                status = line.split(":", 1)[1].strip()
                break
        projects.append({"name": sub.name, "title": title, "status": status})
    return projects

def extract_friction_log() -> str:
    """Extract the Friction Log section from state-of-mavis.md."""
    if not STATE_FILE.exists():
        return ""
    content = STATE_FILE.read_text(encoding="utf-8")
    marker = "## Friction Log"
    if marker not in content:
        return ""
    start = content.index(marker) + len(marker)
    rest = content[start:]
    next_section = rest.find("\n## ")
    return rest[:next_section].strip() if next_section != -1 else rest.strip()

def get_today_daily_note() -> str | None:
    """Read today's daily note if it exists. None if missing."""
    today = datetime.now().strftime("%Y-%m-%d")
    path = DAILY / f"{today}.md"
    return path.read_text(encoding="utf-8") if path.exists() else None

def harvest(since: str | None = None) -> dict:
    """Run all harvesters, return aggregated dict.
    `since`: commit hash to use as the "since" reference.
            Default = the last commit that touched state-of-mavis.md.
            Override with --since <commit> for the first run after a long gap,
            or for any manual window. (Friction 7 ruling, 2026-06-02.)
    """
    if since is None:
        since = get_last_state_commit()
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "vault_root": str(VAULT_ROOT),
        "since_commit": since,
        "commits_with_files": get_commits_since(since),
        "inbox_count": count_inbox(),
        "open_projects": get_open_projects(),
        "friction_log_current": extract_friction_log(),
        "today_daily_note": get_today_daily_note(),
    }

# ============================================================
# AUDIT GATE — rule-based can_i() that mirrors SOUL
# ============================================================

# Mirrors SOUL.md Autonomy Boundary Table. When the self-model-card MCP
# is built, this function is replaced by a call to can_i(). Until then,
# the rules are the deterministic layer.
RED_RULES = [
    (r"\b(send|email|message|post|tweet|publish|signup|buy|purchase|subscribe)\b",
     "external send / Andre's identity / money"),
    (r"\b(delete|rm|drop|trash|force.push|hard.reset)\b",
     "destructive or irreversible"),
    (r"\b(hermes|openclaw|kanban|gbrain|launchd|fleet|profile\.yaml)\b",
     "fleet boundary (isolation principle)"),
    (r"\b(credential|token|password|api[._-]?key|secret|auth)\b",
     "credential / security change"),
]
YELLOW_RULES = [
    (r"\b(push).*\b(github|origin|main|master|remote)\b", "git push to remote"),
    (r"\b(cron|launchctl|schedul)", "schedule change"),
    (r"\b(cu|desktop_|click|type|scroll|screenshot)", "macOS GUI control"),
    (r"\b(clipboard|pbcopy)", "clipboard access"),
    (r"\b(open app|launch)\b", "live state mutation"),
    (r"\b(modify template|templater|plugin|dataview).*\bconfig\b",
     "affects future note creation"),
]
GREEN_RULES = [
    (r"\b(read|fetch|search|grep|find|list|view)\b", "read-only, no side effects"),
    (r"\b(write|edit|append|create)\b.*\b(inbox|notes|projects|connections|vellum|_system|daily|resources|state\.md|99|01|02|03|04|05|06|07)\b",
     "vault write, reversible via git"),
    (r"\b(git add|git commit|git status|git log|git diff|git show)\b",
     "local git, reversible"),
    (r"\b(draft|compose|outline|template|summarize|synthesize)\b", "draft only, no send"),
]

def can_i(action: str, tool: str | None = None) -> dict:
    """Rule-based can_i() classifier. Mirrors SOUL.md autonomy table.
    Returns: {allowed, tier, constraints_hit, approval_required, rationale}"""
    text = f"{tool or ''} {action}".lower()
    for pattern, reason in RED_RULES:
        if re.search(pattern, text):
            return {"allowed": False, "tier": "red",
                    "constraints_hit": [reason], "approval_required": True,
                    "rationale": f"red rule: {reason}"}
    for pattern, reason in YELLOW_RULES:
        if re.search(pattern, text):
            return {"allowed": True, "tier": "yellow",
                    "constraints_hit": [reason], "approval_required": True,
                    "rationale": f"yellow rule: {reason}"}
    for pattern, reason in GREEN_RULES:
        if re.search(pattern, text):
            return {"allowed": True, "tier": "green",
                    "constraints_hit": [reason], "approval_required": False,
                    "rationale": f"green rule: {reason}"}
    return {"allowed": True, "tier": "green",
            "constraints_hit": ["no rule matched; default green"],
            "approval_required": False, "rationale": "no pattern; default green"}

def audit_session(commits_output: str) -> list:
    """Classify each session commit via can_i(). Returns list of verdicts."""
    verdicts = []
    for line in commits_output.split("\n"):
        if not line.startswith("COMMIT:"):
            continue
        rest = line[len("COMMIT:"):].strip()
        parts = rest.split("|", 2)
        if len(parts) < 3:
            continue
        commit_hash, date, subject = parts
        v = can_i(subject, tool="git commit")
        verdicts.append({
            "commit": commit_hash[:8], "date": date, "subject": subject,
            "tier": v["tier"], "allowed": v["allowed"],
            "rationale": v["rationale"],
        })
    return verdicts

# ============================================================
# M3 SYNTHESIS PROMPT — assembles the input M3 will reason over
# ============================================================

PROMPT_TEMPLATE = """You are updating state-of-mavis.md, the session-continuity MOC for the Mavis EA (Andre's executive assistant on M3). The file lives at {state_path}.

# Template (preserve these sections, in this order, with the `##` headers exactly)

1. `## Operating envelope (this session)` — model, role, vault root, session ID, date, Mavis's stance
2. `## Just-shipped (since last update)` — what got done, organized by session/turn
3. `## Open loops (live right now — pick up here next session)` — high/medium/low priority
4. `## Deferred (decided-not-now, with reason)` — table of items + revisit triggers
5. `## Decisions landed (this session, or recently)` — new rules/positions
6. `## Active constraints (session-specific, expire at session end)` — yellow/red flags for THIS session only
7. `## Next session primer (read in this order on cold start)` — the file order
8. `## Patterns observed (this session, worth keeping)` — meta-observations
9. `## Friction Log (where I got stuck, what would unblock me)` — structural decisions needed

# SOUL context (the operating contract)
- Mavis is Andre's executive assistant, isolated to this vault, no fleet tooling.
- Hard constraints: no deploys, no pushes (except to this vault repo), no external sends, no credential changes, no schedule changes, no destructive file ops without explicit in-session approval.
- Esalen posture adopted 2026-06-02: build → test → skillify. $100/month M3 inference budget.

# Current state of the vault
```json
{harvested_json}
```

# Current Friction Log (carry forward; resolve closed items, add new ones)
```
{friction_log}
```

# Today's daily note (if it exists)
```
{daily_note}
```

# Your job

1. Read the current state-of-mavis.md first (the script will read it for you, but reason from what's here).
2. Synthesize the NEW state-of-mavis.md content per the template above.
3. Preserve section order and `##` headers exactly.
4. Update the dynamic content (Operating envelope, Just-shipped, Open loops, Decisions, Active constraints, Patterns) to reflect THIS session end.
5. Carry forward unresolved Friction Log items; resolve closed ones (e.g., Friction 1-6 from previous turn were ruled on by Andre).
6. Add new Friction Log items for anything that came up THIS session.
7. End with the same footer pattern: `*First written ..., updated ..., Mavis session ...*`
8. Update the `updated:` field in the frontmatter.

# Output

Output ONLY the complete new state-of-mavis.md content. No preamble, no explanation, no markdown code fences. The output will be written directly to the file.
"""

def assemble_prompt(harvested: dict) -> str:
    """Build the M3 synthesis prompt from harvested data."""
    return PROMPT_TEMPLATE.format(
        state_path=STATE_FILE,
        harvested_json=json.dumps(harvested, indent=2),
        friction_log=harvested.get("friction_log_current") or "(no Friction Log in current file)",
        daily_note=harvested.get("today_daily_note") or "(no daily note for today)",
    )

# ============================================================
# APPLY — write the synthesized content to state-of-mavis.md
# ============================================================

def apply(content: str) -> None:
    """Write the synthesized content to state-of-mavis.md."""
    STATE_FILE.write_text(content, encoding="utf-8")

# ============================================================
# CLI
# ============================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="End-of-session state-of-mavis.md regenerator (Esalen posture)")
    parser.add_argument("--harvest", action="store_true", help="Output JSON of harvested data")
    parser.add_argument("--audit", action="store_true", help="can_i() on session actions")
    parser.add_argument("--assemble-prompt", action="store_true", help="Output M3 synthesis prompt")
    parser.add_argument("--apply", action="store_true", help="Write synthesized content from stdin to state-of-mavis.md")
    parser.add_argument("--dry-run", action="store_true", help="harvest + audit + prompt (no write)")
    parser.add_argument("--since", metavar="COMMIT", help="Override the 'since commit' reference (default: last commit that touched state-of-mavis.md). Friction 7 ruling.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    if args.harvest:
        print(json.dumps(harvest(args.since), indent=2))
        return 0

    if args.audit:
        since = args.since if args.since else get_last_state_commit()
        verdicts = audit_session(get_commits_since(since))
        print(json.dumps({"since_commit": since, "verdicts": verdicts}, indent=2))
        return 0

    if args.assemble_prompt:
        print(assemble_prompt(harvest(args.since)))
        return 0

    if args.apply:
        content = sys.stdin.read()
        # Audit gate: refuse if any prior session action is RED
        since = args.since if args.since else get_last_state_commit()
        verdicts = audit_session(get_commits_since(since))
        reds = [v for v in verdicts if not v["allowed"]]
        if reds:
            print("!!! AUDIT GATE FAILED: refuse to overwrite state-of-mavis.md", file=sys.stderr)
            print(json.dumps(reds, indent=2), file=sys.stderr)
            return 1
        apply(content)
        print(f"Wrote {len(content)} chars to {STATE_FILE} (since={since[:8]})", file=sys.stderr)
        return 0

    if args.dry_run:
        h = harvest(args.since)
        print("=== HARVESTED DATA ===")
        print(json.dumps(h, indent=2))
        print()
        print("=== AUDIT GATE (can_i on session actions) ===")
        verdicts = audit_session(h["commits_with_files"])
        print(json.dumps(verdicts, indent=2))
        reds = [v for v in verdicts if not v["allowed"]]
        if reds:
            print()
            print("!!! AUDIT GATE FAILED: red actions detected. Refuse to overwrite state-of-mavis.md.")
            return 1
        print()
        print("=== M3 SYNTHESIS PROMPT (feed to M3, capture output, pipe back via --apply) ===")
        print(assemble_prompt(h))
        return 0

    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())
