#!/usr/bin/env python3
"""
action.py — I/O layer for the session-boot-sync Skill.

Pure deterministic code. Gathers the cross-session state needed for a
fresh-boot briefing: MEMORY.md tail, recent git commits, ledger
snapshot, pending queue handoffs, most recent daily note. Returns a
JSON dict that M3 (the model) reads and synthesizes into a 3-bullet
"Where we left off" briefing.

NO LLM calls. The split is the Esalen discipline: M3 does the
qualitative synthesis (what's load-bearing, what's stale, what's
in flight). Python does the deterministic data gathering (read
files, parse JSON, sort by mtime, format output).

Usage (programmatic):
    import action
    bundle = action.gather_boot_state()
    # bundle is a dict; pass to M3 with the skill.md instructions

Usage (CLI):
    action.py             # prints the bundle as JSON
    action.py --check     # exit 0 if all required inputs present, 1 otherwise
    action.py --memory-tail 50  # override the default 80-line tail
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

__version__ = "0.1.0"

# ============================================================
# PATHS — vault-resident + agent config, hardcoded for this host
# ============================================================

HOME = Path("/Users/brassfieldventuresllc")
VAULT_ROOT = HOME / "MiniMax-Agent"
AGENT_CONFIG = HOME / ".mavis" / "agents" / "mavis"
MEMORY_FILE = AGENT_CONFIG / "memory" / "MEMORY.md"
LEDGER_SNAPSHOT = VAULT_ROOT / "99 _system" / "logs" / "ledger-snapshot.json"
PROJECTS_ROOT = VAULT_ROOT / "03 Projects"
DAILY_ROOT = VAULT_ROOT / "01 Daily"

# Memory tail: how many lines to read from the bottom of MEMORY.md.
# 80 is enough to capture 2-3 dated entries + a few untitled ones
# while staying well under a 4k context budget.
DEFAULT_MEMORY_TAIL = 80

# Recent commits: how many to surface in the bundle.
DEFAULT_COMMIT_COUNT = 10

# Pending handoffs: top N by mtime.
DEFAULT_HANDOFF_COUNT = 5

# Dated memory entry header pattern. Matches the LAST (YYYY-MM-DD)
# at the end of a `##/###/####` header line. Tolerates:
#   ### Topic name (2026-06-05)
#   ### Vault destruction incident — 2026-06-05 11:28→11:42 CT (2026-06-05)
#   ### Hung worker (2026-06-04/05)
# The trailing /DD in 2026-06-04/05 is a day-range (2 days, e.g.
# incident spanning the 4th and 5th), not a full MM-DD. The regex
# anchors on the trailing paren + EOL so the captured date is the
# canonical "last touched" date, not a date in the title body.
MEMORY_ENTRY_RE = re.compile(
    r"^#{2,4}\s+(?P<title>.+?)\s+\((?P<date>\d{4}-\d{2}-\d{2}"
    r"(?:/\d{2})?)\)\s*$",
    re.MULTILINE,
)

# Inline-date fallback: a header whose date is embedded in the title
# rather than trailing parens. Example:
#   ### Vault destruction incident — 2026-06-05 11:28→11:42 CT (hard correction)
# In this case, the FIRST YYYY-MM-DD in the line is the canonical date.
MEMORY_ENTRY_INLINE_RE = re.compile(
    r"^#{2,4}\s+(?P<title>.+?)\s+(?P<date>\d{4}-\d{2}-\d{2})(?:[^\d].*)?$",
    re.MULTILINE,
)


# ============================================================
# CORE GATHERERS — one per data source
# ============================================================

def gather_memory_tail(memory_path: Path, n: int) -> dict:
    """Read the last N lines of MEMORY.md. Returns dict with the
    raw lines and the parsed list of dated entry headers found
    in that tail.

    Status flags:
      - "ok"   — file exists, read succeeded
      - "missing" — file does not exist
    """
    if not memory_path.exists():
        return {
            "status": "missing",
            "path": str(memory_path),
            "lines": [],
            "line_count": 0,
            "entries": [],
        }

    try:
        text = memory_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {
            "status": "error",
            "path": str(memory_path),
            "error": str(e),
            "lines": [],
            "line_count": 0,
            "entries": [],
        }

    all_lines = text.splitlines()
    tail = all_lines[-n:] if len(all_lines) > n else all_lines
    tail_text = "\n".join(tail)

    # Build a dedup-aware set of entries. Prefer trailing-paren date,
    # fall back to inline date for headers that don't have one.
    entries_by_line: dict[int, dict] = {}
    for m in MEMORY_ENTRY_RE.finditer(tail_text):
        line_no = tail_text[: m.start()].count("\n")
        entries_by_line[line_no] = {
            "title": m.group("title").strip(),
            "date": m.group("date"),
        }
    for m in MEMORY_ENTRY_INLINE_RE.finditer(tail_text):
        line_no = tail_text[: m.start()].count("\n")
        if line_no not in entries_by_line:
            entries_by_line[line_no] = {
                "title": m.group("title").strip(),
                "date": m.group("date"),
            }
    entries = [entries_by_line[k] for k in sorted(entries_by_line.keys())]

    return {
        "status": "ok",
        "path": str(memory_path),
        "lines": tail,
        "line_count": len(tail),
        "total_lines": len(all_lines),
        "entries": entries,
    }


def gather_recent_commits(vault: Path, count: int) -> list[dict]:
    """Run `git log --oneline -<count>` and parse into structured dicts.
    Returns empty list if git is unavailable or the repo isn't a git repo.
    """
    try:
        result = subprocess.run(
            ["git", "log", f"-{count}", "--pretty=format:%h%x09%ad%x09%s",
             "--date=short"],
            cwd=vault, capture_output=True, text=True, timeout=10,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []

    if result.returncode != 0:
        return []

    commits = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        commits.append({
            "hash": parts[0],
            "date": parts[1],
            "subject": parts[2],
        })
    return commits


def gather_ledger_snapshot(snapshot_path: Path) -> dict:
    """Read and parse ledger-snapshot.json. Returns dict with the
    parsed payload (or status: missing/error).
    """
    if not snapshot_path.exists():
        return {"status": "missing", "path": str(snapshot_path)}

    try:
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {"status": "error", "path": str(snapshot_path), "error": str(e)}

    # Convert mtime (epoch seconds) to ISO for human readability
    mtime = data.get("mtime")
    if isinstance(mtime, (int, float)):
        try:
            mtime_iso = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(
                timespec="seconds"
            )
        except (OSError, ValueError, OverflowError):
            mtime_iso = None
    else:
        mtime_iso = None

    return {
        "status": "ok",
        "path": str(snapshot_path),
        "last_id": data.get("last_id"),
        "saved_at": data.get("saved_at"),
        "record_count": data.get("record_count"),
        "sha256": data.get("sha256"),
        "mtime_iso": mtime_iso,
    }


def gather_pending_handoffs(projects_root: Path, top_n: int) -> list[dict]:
    """Find all `*.md` files in `03 Projects/*/queue/`, sort by mtime
    descending, return the top N. Each entry: path, mtime, status
    (from frontmatter), project name.

    Frontmatter is YAML-ish; we extract a `status:` line if present
    without requiring a full YAML parser. Good enough for a boot sync.
    """
    if not projects_root.exists():
        return []

    queue_files = []
    for queue_dir in projects_root.glob("*/queue"):
        if not queue_dir.is_dir():
            continue
        for md in queue_dir.glob("*.md"):
            try:
                stat = md.stat()
            except OSError:
                continue
            queue_files.append({
                "path": str(md.relative_to(projects_root.parent)),
                "abs_path": str(md),
                "mtime_epoch": stat.st_mtime,
                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(
                    timespec="seconds"
                ),
                "project": md.relative_to(projects_root).parts[0],
                "filename": md.name,
            })

    queue_files.sort(key=lambda f: f["mtime_epoch"], reverse=True)
    top = queue_files[:top_n]

    # Parse frontmatter status from each
    status_re = re.compile(r"^status:\s*(.+?)\s*$", re.MULTILINE)
    for entry in top:
        try:
            text = Path(entry["abs_path"]).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            entry["status"] = "unknown"
            continue
        m = status_re.search(text[:1000])  # status is in the first KB
        entry["status"] = m.group(1).strip() if m else "unknown"
        # Don't leak the abs_path into the bundle — M3 can re-resolve
        del entry["abs_path"]
        del entry["mtime_epoch"]

    return top


def gather_recent_daily(daily_root: Path) -> dict | None:
    """Find the most recent `01 Daily/YYYY-MM-DD.md` file. Return its
    path and mtime, or None if no daily notes exist.
    """
    if not daily_root.exists():
        return None
    daily_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
    files = []
    for f in daily_root.glob("*.md"):
        m = daily_pattern.match(f.name)
        if m:
            try:
                stat = f.stat()
            except OSError:
                continue
            files.append({
                "path": str(f.relative_to(daily_root.parent)),
                "date": m.group(1),
                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(
                    timespec="seconds"
                ),
            })
    if not files:
        return None
    files.sort(key=lambda f: f["date"], reverse=True)
    return files[0]


def gather_vault_status(vault: Path) -> dict:
    """Light check: is the vault a git repo? when was the last
    commit? are the required directories present?
    """
    if not vault.exists():
        return {"status": "missing", "path": str(vault)}
    git_dir = vault / ".git"
    if not git_dir.exists():
        return {"status": "not_a_git_repo", "path": str(vault)}

    required_dirs = ["00 Inbox", "01 Daily", "02 Notes", "03 Projects"]
    missing_dirs = [d for d in required_dirs if not (vault / d).exists()]

    return {
        "status": "ok" if not missing_dirs else "partial",
        "path": str(vault),
        "missing_dirs": missing_dirs,
    }


# ============================================================
# MAIN — gather everything into one bundle
# ============================================================

def gather_boot_state(
    memory_tail: int = DEFAULT_MEMORY_TAIL,
    commit_count: int = DEFAULT_COMMIT_COUNT,
    handoff_count: int = DEFAULT_HANDOFF_COUNT,
) -> dict:
    """Gather the full boot-sync bundle. The bundle is the
    deterministic substrate; M3 reads it and synthesizes the
    3-bullet briefing per skill.md.
    """
    return {
        "schema_version": "0.1.0",
        "gathered_at": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
        "vault_status": gather_vault_status(VAULT_ROOT),
        "memory": gather_memory_tail(MEMORY_FILE, memory_tail),
        "recent_commits": gather_recent_commits(VAULT_ROOT, commit_count),
        "ledger_snapshot": gather_ledger_snapshot(LEDGER_SNAPSHOT),
        "pending_handoffs": gather_pending_handoffs(PROJECTS_ROOT, handoff_count),
        "recent_daily": gather_recent_daily(DAILY_ROOT),
    }


def check_inputs() -> tuple[bool, list[str]]:
    """For the --check flag: return (ok, list_of_issues). Each issue
    is a one-line string M3 can surface to Andre.
    """
    bundle = gather_boot_state()
    issues = []
    if bundle["vault_status"]["status"] != "ok":
        issues.append(
            f"vault: {bundle['vault_status']['status']} ({bundle['vault_status']['path']})"
        )
    if bundle["memory"]["status"] != "ok":
        issues.append(f"memory: {bundle['memory']['status']} ({bundle['memory']['path']})")
    if bundle["ledger_snapshot"]["status"] != "ok":
        issues.append(
            f"ledger: {bundle['ledger_snapshot']['status']} "
            f"({bundle['ledger_snapshot'].get('path', '?')})"
        )
    return (len(issues) == 0, issues)


# ============================================================
# CLI
# ============================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        prog="action.py",
        description="I/O layer for the session-boot-sync Skill. Gathers "
                    "MEMORY.md tail, git log, ledger snapshot, queue "
                    "handoffs, recent daily note. Outputs JSON; M3 "
                    "synthesizes the 3-bullet briefing.",
    )
    ap.add_argument("--memory-tail", type=int, default=DEFAULT_MEMORY_TAIL,
                    help=f"Lines to read from MEMORY.md bottom "
                         f"(default: {DEFAULT_MEMORY_TAIL})")
    ap.add_argument("--commits", type=int, default=DEFAULT_COMMIT_COUNT,
                    help=f"Number of recent commits "
                         f"(default: {DEFAULT_COMMIT_COUNT})")
    ap.add_argument("--handoffs", type=int, default=DEFAULT_HANDOFF_COUNT,
                    help=f"Number of pending handoffs "
                         f"(default: {DEFAULT_HANDOFF_COUNT})")
    ap.add_argument("--check", action="store_true",
                    help="Validate inputs (exit 0 if all OK, 1 otherwise)")
    ap.add_argument("--version", action="version",
                    version=f"action.py v{__version__}")
    args = ap.parse_args()

    if args.check:
        ok, issues = check_inputs()
        if ok:
            print("session-boot-sync: all inputs present.")
            return 0
        print("session-boot-sync: missing inputs:", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        return 1

    bundle = gather_boot_state(
        memory_tail=args.memory_tail,
        commit_count=args.commits,
        handoff_count=args.handoffs,
    )
    print(json.dumps(bundle, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
