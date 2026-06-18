#!/usr/bin/env python3
"""
Session Lesson Extractor — suggestion engine only. Never writes to memory.

Scans 5 Mavis surfaces for recurring patterns that could become memory entries.
Outputs a markdown brief. Mavis reviews and commits.

Usage:
  python3 extract.py [--window-days 7] [--output <path>] [--dry-run]

Default output: ~/MiniMax-Agent/03 Projects/Mavis EA Design/reports/lesson-extract-YYYY-MM-DD.md
"""

import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# --- Surfaces (Mavis territory only) ---

VAULT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent")
MEMORY_ROOT = Path("/Users/brassfieldventuresllc/.mavis/agents/mavis/memory")
SKILLS_ROOT = Path("/Users/brassfieldventuresllc/.mavis/agents/mavis/skills")
KANBAN_DB = Path("/Users/brassfieldventuresllc/.mavis/kanban.db")

DAILY_DIR = VAULT_ROOT / "01 Daily"
NOTES_DIR = VAULT_ROOT / "02 Notes"
PROJECTS_DIR = VAULT_ROOT / "03 Projects"

# --- Heuristics (deliberately conservative — false negatives are fine, false positives waste Mavis's review) ---

# Type A: Recurring correction — Andre has said "stop / from now on / I keep / don't / always / never" 3+ times
CORRECTION_PATTERNS = [
    r"\bstop\s+(?:doing|giving|asking|doing that)\b",
    r"\bfrom now on\b",
    r"\bI keep (?:telling you|saying|asking)\b",
    r"\bdon't (?:do that|ask|give me)\b",
    r"\balways (?:do|run|check)\b",
    r"\bnever (?:do|run|patch)\b",
    r"\bthat's not (?:right|what I (?:want|asked))\b",
    r"\bno,? (?:do|just|stop)\b",
]

# Type B: Course-correction with generalizable rule — bare URL signal, "go read the spec", "stop giving me problems solve them"
SIGNAL_PATTERNS = [
    (r"^https?://\S+$", "bare URL signal — possible 'go read the spec'"),
    (r"\bgo read the spec\b", "explicit spec-read directive"),
    (r"\bstop giving me problems solve them\b", "post-decision execution mode"),
    (r"\bpush\b|\bcommit\b|\bdeploy\b", "post-decision imperative"),
    (r"\bdecide and report\b|\bdecide, mention inline\b", "decision rule"),
]

# Type C: Worker failure indicators (2+ in window)
WORKER_FAIL_PATTERNS = [
    r"NEEDS-WORK",
    r"stalled at",
    r"FAIL",
    r"verdict: NEEDS-WORK",
    r"worker.*stalled",
    r"long[- ]running inference",
]


def run(cmd, cwd=None, capture=True):
    """Run a shell command, return stdout as string. Never raises on empty output."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=capture, text=True, timeout=30
        )
        return result.stdout.strip() if result.stdout else ""
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return ""


def file_age_days(path: Path) -> float:
    """Return file age in days, or 999 if missing."""
    if not path.exists():
        return 999.0
    mtime = path.stat().st_mtime
    return (datetime.now().timestamp() - mtime) / 86400


def find_files_modified_since(root: Path, days: int) -> list:
    """Find files modified in the last N days."""
    if not root.exists():
        return []
    out = run(f'find "{root}" -type f -mtime -{int(days)} 2>/dev/null')
    return [Path(line) for line in out.splitlines() if line]


def extract_lines_with_context(path: Path, pattern: str, context_lines: int = 0) -> list:
    """Extract lines matching pattern, with optional context. Returns list of (line_no, text)."""
    if not path.exists():
        return []
    matches = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append((i, line.rstrip()))
    except (PermissionError, OSError):
        pass
    return matches


def scan_daily_for_corrections(days: int) -> list:
    """Type A: recurring corrections in 01 Daily/."""
    files = find_files_modified_since(DAILY_DIR, days)
    occurrences = defaultdict(list)  # pattern -> [(file, line_no, text)]

    for f in files:
        for pat in CORRECTION_PATTERNS:
            for line_no, text in extract_lines_with_context(f, pat):
                # use pattern as the key for dedup
                key = pat
                occurrences[key].append((str(f), line_no, text))

    # Filter to 3+ occurrences
    candidates = []
    for pat, occs in occurrences.items():
        if len(occs) >= 3:
            candidates.append({
                "type": "A",
                "pattern": pat,
                "recurrence": len(occs),
                "evidence": occs[:5],  # cap at 5 examples
            })
    return candidates


def scan_for_signals(days: int) -> list:
    """Type B: course-correction with generalizable rule."""
    files = find_files_modified_since(DAILY_DIR, days)
    candidates = []
    for f in files:
        for pat, label in SIGNAL_PATTERNS:
            for line_no, text in extract_lines_with_context(f, pat):
                candidates.append({
                    "type": "B",
                    "label": label,
                    "pattern": pat,
                    "evidence": [(str(f), line_no, text)],
                })
    return candidates


def scan_worker_failures(days: int) -> list:
    """Type C: worker failure modes."""
    # Worker reports live in scratchpads and worker session dirs
    scratch_root = Path("/Users/brassfieldventuresllc/.mavis/scratchpads")
    occurrences = defaultdict(list)
    if scratch_root.exists():
        files = find_files_modified_since(scratch_root, days)
        for f in files:
            for pat in WORKER_FAIL_PATTERNS:
                for line_no, text in extract_lines_with_context(f, pat):
                    occurrences[pat].append((str(f), line_no, text))

    candidates = []
    for pat, occs in occurrences.items():
        if len(occs) >= 2:
            candidates.append({
                "type": "C",
                "pattern": pat,
                "recurrence": len(occs),
                "evidence": occs[:5],
            })
    return candidates


def read_current_memory() -> str:
    """Read MEMORY.md and topic files for cross-reference."""
    parts = []
    mem_file = MEMORY_ROOT / "MEMORY.md"
    if mem_file.exists():
        parts.append(mem_file.read_text(encoding="utf-8", errors="replace"))
    for tf in MEMORY_ROOT.glob("*.md"):
        if tf.name != "MEMORY.md":
            parts.append(tf.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def is_already_in_memory(candidate_phrase: str, memory_text: str) -> bool:
    """Loose check: does a key phrase from the candidate already appear in memory?"""
    # Extract 3+ word phrases from the candidate, check each
    words = re.findall(r"\b\w+\b", candidate_phrase.lower())
    if len(words) < 3:
        return False
    # Build 3-grams
    for i in range(len(words) - 2):
        phrase = " ".join(words[i : i + 3])
        if phrase in memory_text.lower():
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Extract candidate memory entries from Mavis state surfaces.")
    ap.add_argument("--window-days", type=int, default=7, help="Look-back window in days (default 7)")
    ap.add_argument("--output", type=str, default=None, help="Output brief path (default: vault reports dir)")
    ap.add_argument("--dry-run", action="store_true", help="Print brief to stdout, do not write file")
    args = ap.parse_args()

    window = args.window_days
    today = datetime.now().strftime("%Y-%m-%d")

    if args.dry_run or not args.output:
        out_path = None
    else:
        out_path = Path(args.output)
    if out_path is None and not args.dry_run:
        reports_dir = PROJECTS_DIR / "Mavis EA Design" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        out_path = reports_dir / f"lesson-extract-{today}.md"

    # Run scans
    print(f"[extract] window={window}d, scanning 5 surfaces...", file=sys.stderr)
    type_a = scan_daily_for_corrections(window)
    type_b = scan_for_signals(window)
    type_c = scan_worker_failures(window)
    print(f"[extract] found: A={len(type_a)} B={len(type_b)} C={len(type_c)}", file=sys.stderr)

    # Cross-reference with memory
    memory_text = read_current_memory()
    for cand in type_a + type_b + type_c:
        sample_text = cand["evidence"][0][2] if cand.get("evidence") else ""
        cand["already_in_memory"] = is_already_in_memory(sample_text, memory_text)

    # Sort: recurrence DESC, then unflagged-already first
    def sort_key(c):
        return (-c.get("recurrence", 1), c["already_in_memory"])
    type_a.sort(key=sort_key)
    type_b.sort(key=sort_key)
    type_c.sort(key=sort_key)

    # Render brief
    lines = [
        f"# Lesson Extract: {today}",
        "",
        f"**Window:** last {window} days",
        "**Auditor:** Mavis (EA) — auto-extracted, manual review",
        f"**Generated:** {datetime.now().isoformat(timespec='seconds')}",
        "",
        f"**Surfaces scanned:** 01 Daily/, ~/.mavis/scratchpads/, ~/.mavis/agents/mavis/memory/, ~/.mavis/agents/mavis/skills/",
        "",
        "## HIGH-durability candidates (Type A: recurring corrections, 3+ occurrences)",
        "",
    ]
    if not type_a:
        lines.append("_No Type A candidates in this window._")
        lines.append("")
    else:
        for i, c in enumerate(type_a, 1):
            tag = " ⚠ already in memory" if c["already_in_memory"] else ""
            lines.append(f"### {i}. Pattern: `{c['pattern']}` (recurrence: {c['recurrence']}){tag}")
            lines.append("")
            lines.append("Evidence:")
            for path, line_no, text in c["evidence"]:
                lines.append(f"- `{path}:{line_no}` — {text[:150]}")
            lines.append("")
            lines.append("**Action:** commit / defer / discard (reason: ___)")
            lines.append("")

    lines.append("## MEDIUM-durability candidates (Type B: course-correction with generalizable rule)")
    lines.append("")
    if not type_b:
        lines.append("_No Type B candidates in this window._")
        lines.append("")
    else:
        for i, c in enumerate(type_b, 1):
            tag = " ⚠ already in memory" if c["already_in_memory"] else ""
            lines.append(f"### {i}. {c['label']}{tag}")
            lines.append("")
            for path, line_no, text in c["evidence"]:
                lines.append(f"- `{path}:{line_no}` — {text[:200]}")
            lines.append("")
            lines.append("**Suggested slot:** MEMORY.md or topic file. **Action:** commit / defer / discard.")
            lines.append("")

    lines.append("## LOW-durability candidates (Type C: worker failure modes — file in fleet-trust-patterns, not memory)")
    lines.append("")
    if not type_c:
        lines.append("_No Type C candidates in this window._")
        lines.append("")
    else:
        for i, c in enumerate(type_c, 1):
            tag = " ⚠ already in memory" if c["already_in_memory"] else ""
            lines.append(f"### {i}. Pattern: `{c['pattern']}` (recurrence: {c['recurrence']}){tag}")
            lines.append("")
            for path, line_no, text in c["evidence"]:
                lines.append(f"- `{path}:{line_no}` — {text[:200]}")
            lines.append("")
            lines.append("**Suggested slot:** `fleet-trust-patterns.md` topic file (not MEMORY.md).")
            lines.append("")

    lines.append("## Stats")
    lines.append(f"- Total candidates: {len(type_a) + len(type_b) + len(type_c)}")
    lines.append(f"- HIGH (Type A): {len(type_a)}")
    lines.append(f"- MEDIUM (Type B): {len(type_b)}")
    lines.append(f"- LOW (Type C): {len(type_c)}")
    lines.append(f"- Memory conflicts: {sum(1 for c in type_a + type_b + type_c if c['already_in_memory'])}")
    lines.append("")

    brief = "\n".join(lines)

    if args.dry_run:
        print(brief)
    else:
        out_path.write_text(brief, encoding="utf-8")
        print(f"[extract] brief written to: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
