#!/usr/bin/env python3
"""
generate_instincts.py — harvest operational exhaust into new Atomic Instincts.

The Ouroboros loop: read what Mavis did, find patterns, propose new instincts.

Esalen posture: this script is the deterministic shim. It:
  1. Harvests operational exhaust from 3+ sources (git log, Friction Log,
     intake logs, skillopt runs)
  2. Builds a structured "harvest context" + a synthesis prompt for M3
  3. By default (--dry-run): writes the prompt to a sidecar file and prints
     a summary. NO file writes to 99 _system/instincts/.
  4. With --apply <candidates.json>: reads the M3-produced candidate
     instincts from a JSON file, validates them, and writes the new
     files to 99 _system/instincts/.

The M3 synthesis step is external. The harvester prepares the inputs;
M3 (in a session) reads them, produces the candidates, and (with --apply)
the harvester writes the files. The apply path is gated by an explicit
flag AND by can_i() checking for irreversible writes.

Sources (graceful skip if missing):
  - 99 _system/logs/audit_log.jsonl       (Mavis session audit trail)
  - 99 _system/logs/skillopt-runs.jsonl   (SOUL compliance eval runs)
  - state-of-mavis.md  ## Friction Log    (resolved + new frictions)
  - 99 _system/intake-log/                (ingestion record per drop)
  - git log                               (commits since last state-of-mavis)
  - 99 _system/instincts/                 (existing instincts for dedup)

Usage:
  # Default: dry-run (no writes)
  python3 generate_instincts.py

  # Custom harvest window
  python3 generate_instincts.py --since-commit <hash>

  # Apply M3-produced candidates (GATED — requires --apply flag)
  python3 generate_instincts.py --apply candidates.json

  # Custom output dir for the prompt
  python3 generate_instincts.py --out-dir /path/to/output
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Vault-relative defaults
VAULT_ROOT = Path(
    "/Users/brassfieldventuresllc/MiniMax-Agent"
)
DEFAULT_INSTINCTS_DIR = VAULT_ROOT / "99 _system" / "instincts"
DEFAULT_LOG_DIR = VAULT_ROOT / "99 _system" / "logs"
DEFAULT_INTAKE_LOG_DIR = VAULT_ROOT / "99 _system" / "intake-log"
DEFAULT_STATE_FILE = VAULT_ROOT / "state-of-mavis.md"
DEFAULT_OUT_DIR = VAULT_ROOT / "99 _system" / "instincts" / "_harvest"

# Audit log path locked by Friction 4 (2026-06-02). The file may not exist
# yet — we skip it gracefully if it's missing.
AUDIT_LOG_PATH = DEFAULT_LOG_DIR / "audit_log.jsonl"
SKILLOPT_RUNS_PATH = DEFAULT_LOG_DIR / "skillopt-runs.jsonl"
STATE_FILE = DEFAULT_STATE_FILE
INTAKE_LOG_DIR = DEFAULT_INTAKE_LOG_DIR
INSTINCTS_DIR = DEFAULT_INSTINCTS_DIR

__version__ = "0.1.0"


# ============================================================
# SOURCE HARVESTERS (deterministic)
# ============================================================

def harvest_git_log(since_commit: str | None = None, n: int = 20) -> list:
    """Pull the most recent N commits, optionally since a specific commit."""
    cmd = ["git", "-C", str(VAULT_ROOT), "log", f"-n{n}", "--pretty=format:%H|%ai|%s"]
    try:
        out = subprocess.check_output(cmd, text=True, timeout=10)
    except subprocess.CalledProcessError as e:
        return [{"error": f"git log failed: {e}"}]
    commits = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        h, date, subject = parts
        commits.append({"hash": h, "date": date, "subject": subject})
    return commits


def harvest_friction_log() -> dict:
    """Extract the Friction Log section from state-of-mavis.md.

    Returns: {raw_text, resolved: [...], new: [...]}
    """
    if not STATE_FILE.exists():
        return {"raw_text": "", "resolved": [], "new": [], "note": "state-of-mavis.md not found"}
    content = STATE_FILE.read_text(encoding="utf-8")
    marker = "## Friction Log"
    if marker not in content:
        return {"raw_text": "", "resolved": [], "new": [], "note": "no Friction Log section"}
    start = content.index(marker) + len(marker)
    rest = content[start:]
    next_section = rest.find("\n## ")
    raw = rest[:next_section].strip() if next_section != -1 else rest.strip()

    # Light parsing: "### Resolved (date)" and "### New (date, ...)" sections
    resolved = re.findall(
        r"###\s+Resolved.*?(?=###|\Z)", raw, re.DOTALL
    )
    new = re.findall(
        r"###\s+New.*?(?=###|\Z)", raw, re.DOTALL
    )
    return {
        "raw_text": raw,
        "resolved_count": len(resolved),
        "new_count": len(new),
        "resolved_summaries": [
            re.findall(r"Friction \d+:.*?(?=\n|$)", r)[0]
            for r in resolved if re.findall(r"Friction \d+:.*?(?=\n|$)", r)
        ],
        "new_summaries": [
            re.findall(r"Friction \d+:.*?(?=\n|$)", r)[0]
            for r in new if re.findall(r"Friction \d+:.*?(?=\n|$)", r)
        ],
    }


def harvest_audit_log() -> dict:
    """Pull recent audit log entries. Skips gracefully if the file is missing."""
    if not AUDIT_LOG_PATH.exists():
        return {
            "path": str(AUDIT_LOG_PATH),
            "exists": False,
            "note": (
                "audit_log.jsonl does not exist yet. Friction 4 locked the path "
                "but the file was never created. Either create it via can_i() "
                "in the next session, or omit from harvest."
            ),
            "entries": [],
        }
    entries = []
    try:
        with AUDIT_LOG_PATH.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 50:  # cap to last 50
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    entries.append({"_raw": line, "_parse_error": True})
    except OSError as e:
        return {"path": str(AUDIT_LOG_PATH), "exists": True, "error": str(e), "entries": []}
    return {
        "path": str(AUDIT_LOG_PATH),
        "exists": True,
        "entries": entries,
        "count": len(entries),
    }


def harvest_skillopt_runs() -> dict:
    """Pull recent skillopt eval runs (the actual operational log we have)."""
    if not SKILLOPT_RUNS_PATH.exists():
        return {"path": str(SKILLOPT_RUNS_PATH), "exists": False, "entries": []}
    entries = []
    try:
        with SKILLOPT_RUNS_PATH.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 50:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    entries.append({"_raw": line[:200]})
    except OSError as e:
        return {"path": str(SKILLOPT_RUNS_PATH), "exists": True, "error": str(e), "entries": []}
    return {
        "path": str(SKILLOPT_RUNS_PATH),
        "exists": True,
        "count": len(entries),
        "entries": entries[-10:],  # last 10 (most recent)
    }


def harvest_intake_log(n: int = 20) -> dict:
    """Pull the N most recent intake-log entries."""
    if not INTAKE_LOG_DIR.exists():
        return {"path": str(INTAKE_LOG_DIR), "exists": False, "entries": []}
    files = sorted(INTAKE_LOG_DIR.glob("*.json"), reverse=True)[:n]
    entries = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            # Compact form for the harvest context
            entries.append({
                "intake_id": data.get("intake_id"),
                "source": data.get("source"),
                "type": data.get("type"),
                "status": data.get("status"),
                "dropped_at": data.get("dropped_at"),
                "size_bytes": data.get("size_bytes"),
            })
        except (json.JSONDecodeError, OSError):
            entries.append({"_file": f.name, "_parse_error": True})
    return {"path": str(INTAKE_LOG_DIR), "exists": True, "count": len(entries), "entries": entries}


def harvest_existing_instincts() -> dict:
    """Pull existing instincts for dedup. Just IDs + titles + confidence."""
    if not INSTINCTS_DIR.exists():
        return {"path": str(INSTINCTS_DIR), "exists": False, "instincts": []}
    existing = []
    for f in sorted(INSTINCTS_DIR.glob("*.md")):
        if f.name == "README.md" or f.name.startswith("_"):
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        # Extract frontmatter
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not m:
            continue
        fm = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip()
        # First H1 title
        title_match = re.search(r"^#\s+(.+)$", text[m.end():], re.MULTILINE)
        title = title_match.group(1).strip() if title_match else f.stem
        existing.append({
            "id": fm.get("id", f.stem),
            "title": title,
            "confidence": fm.get("confidence", "?"),
            "cluster": fm.get("cluster", "?"),
        })
    return {
        "path": str(INSTINCTS_DIR),
        "exists": True,
        "count": len(existing),
        "instincts": existing,
    }


# ============================================================
# HARVEST AGGREGATION
# ============================================================

def harvest(since_commit: str | None = None) -> dict:
    """Run all harvesters in sequence. Returns aggregated dict."""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "vault_root": str(VAULT_ROOT),
        "since_commit": since_commit,
        "git_log": harvest_git_log(since_commit=since_commit, n=20),
        "friction_log": harvest_friction_log(),
        "audit_log": harvest_audit_log(),
        "skillopt_runs": harvest_skillopt_runs(),
        "intake_log": harvest_intake_log(n=20),
        "existing_instincts": harvest_existing_instincts(),
    }


# ============================================================
# M3 SYNTHESIS PROMPT
# ============================================================

PROMPT_TEMPLATE = """You are Mavis, the executive assistant. You are harvesting your own
operational exhaust to synthesize new Atomic Instincts.

# What is an instinct?
A small, confidence-scored, evidence-backed learning with three pieces:
  - **Body** (2-4 sentences): the lesson
  - **Trigger**: when this fires
  - **Evidence**: where it came from (a session, a commit, a Friction)

# Inputs
Below is the harvest context: recent git commits, the Friction Log, the
operational logs (intake, skillopt, audit), and the EXISTING instinct set
for dedup.

# Your task
Identify 2-4 candidate instincts that:
  1. Are NOT already covered by an existing instinct (check by title + cluster).
  2. Have a clear, actionable trigger (not vague).
  3. Are backed by at least 2 pieces of evidence from the harvest.
  4. Have a confidence between 0.5 (new, single observation) and 0.9 (well-evidenced).

# What to skip
- Restatements of existing instincts
- Vague platitudes ("be careful", "always test")
- Anything that needs more than one session to validate (mark as deferred instead)

# Output format
Emit a JSON array of candidate instincts. Each element:

```json
{{
  "id": "i-2026-06-02-XXX",
  "type": "instinct",
  "title": "Short, imperative",
  "created": "2026-06-02",
  "confidence": 0.0,
  "cluster": "safety|tools|workflow|memory|architecture|communication|context|ingestion|role|vault|m3|...",
  "trigger_context": "When X happens, this instinct fires",
  "evidence_source": "commit hash | Friction N | run id | reasoning chain",
  "tags": ["tag1", "tag2"],
  "body": "2-4 sentence lesson. Trigger-first, then the principle, then the action."
}}
```

Emit ONLY the JSON array. No preamble, no postamble, no markdown fences.

# Harvest context

```json
{harvested_json}
```
"""


def render_prompt(harvested: dict) -> str:
    """Render the M3 prompt with the harvest context embedded."""
    return PROMPT_TEMPLATE.format(
        harvested_json=json.dumps(harvested, indent=1, ensure_ascii=False)
    )


# ============================================================
# CANDIDATE VALIDATION (deterministic, no LLM)
# ============================================================

REQUIRED_FIELDS = [
    "id", "type", "title", "created", "confidence",
    "cluster", "trigger_context", "evidence_source", "tags", "body",
]

def validate_candidate(c: dict) -> list:
    """Validate a single candidate. Returns list of error strings (empty if valid)."""
    errs = []
    for field in REQUIRED_FIELDS:
        if field not in c:
            errs.append(f"missing required field: {field!r}")
    if c.get("type") != "instinct":
        errs.append(f"type must be 'instinct', got {c.get('type')!r}")
    try:
        conf = float(c.get("confidence", -1))
        if not (0.0 <= conf <= 1.0):
            errs.append(f"confidence {conf} out of [0, 1]")
    except (TypeError, ValueError):
        errs.append(f"confidence not a number: {c.get('confidence')!r}")
    if not re.match(r"^i-\d{4}-\d{2}-\d{2}-\d{3}$", c.get("id", "")):
        errs.append(f"id {c.get('id')!r} not in i-YYYY-MM-DD-NNN format")
    if not isinstance(c.get("tags", None), list):
        errs.append(f"tags must be a list")
    if not c.get("body", "").strip():
        errs.append("body is empty")
    if len(c.get("body", "")) < 100:
        errs.append(f"body too short: {len(c.get('body', ''))} chars (< 100)")
    return errs


def check_for_duplicates(candidate: dict, existing: list) -> list:
    """Check if a candidate duplicates an existing instinct (by title similarity)."""
    candidates = []
    cand_title = candidate.get("title", "").lower()
    for ex in existing:
        ex_title = ex.get("title", "").lower()
        # Naive: title-contains check
        if cand_title and ex_title and (
            cand_title in ex_title or ex_title in cand_title
        ):
            candidates.append(f"similar title to {ex.get('id')}: {ex_title!r}")
    return candidates


# ============================================================
# APPLY (gated)
# ============================================================

def render_instinct_file(c: dict) -> str:
    """Render a candidate as a markdown file with frontmatter + H1 title + body.

    Matches the existing instinct file pattern (frontmatter, blank line,
    `# <title>`, blank line, body). The schema test (test_instincts.py)
    requires an H1 heading after the frontmatter.
    """
    fm_lines = ["---"]
    for key in REQUIRED_FIELDS:
        v = c[key]
        if isinstance(v, list):
            v_str = "[" + ", ".join(f'"{t}"' for t in v) + "]"
        else:
            v_str = f'"{v}"' if isinstance(v, str) else str(v)
        fm_lines.append(f"{key}: {v_str}")
    fm_lines.append("---")
    fm_lines.append("")
    body = c["body"].strip()
    title = c.get("title", "").strip()
    return "\n".join(fm_lines) + f"\n\n# {title}\n\n" + body + "\n"


def apply_candidates(
    candidates_path: Path,
    instincts_dir: Path = INSTINCTS_DIR,
    *,
    dry_run: bool = False,
) -> dict:
    """Apply M3-produced candidate instincts to the instincts/ directory.

    By default (dry_run=True), reports what would happen without writing.
    With dry_run=False, writes the validated files.
    """
    if not candidates_path.exists():
        return {"error": f"candidates file not found: {candidates_path}"}
    data = json.loads(candidates_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return {"error": "candidates file must be a JSON array"}

    # Load existing for dedup
    existing_harvest = harvest_existing_instincts()
    existing = existing_harvest.get("instincts", [])

    valid = []
    invalid = []
    duplicates = []
    for c in data:
        errs = validate_candidate(c)
        if errs:
            invalid.append({"id": c.get("id", "?"), "errors": errs})
            continue
        dupes = check_for_duplicates(c, existing)
        if dupes:
            duplicates.append({"id": c.get("id"), "matches": dupes})
            continue
        valid.append(c)

    report = {
        "applied_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dry_run": dry_run,
        "input_count": len(data),
        "valid_count": len(valid),
        "invalid_count": len(invalid),
        "duplicate_count": len(duplicates),
        "invalid": invalid,
        "duplicates": duplicates,
        "would_write": [c["id"] for c in valid],
    }

    if not dry_run and valid:
        instincts_dir.mkdir(parents=True, exist_ok=True)
        written = []
        for c in valid:
            # Filename pattern matches existing instincts: YYYY-MM-DD-NNN-slug.md
            # (strip the "i-" prefix from c['id'] since the prefix only appears
            # in frontmatter, not the file system name)
            id_for_filename = re.sub(r"^i-", "", c["id"])
            slug = re.sub(r"[^a-z0-9]+", "-", c["title"].lower())[:60].strip("-")
            fname = f"{id_for_filename}-{slug}.md"
            path = instincts_dir / fname
            path.write_text(render_instinct_file(c), encoding="utf-8")
            written.append(str(path))
        report["written"] = written

    return report


# ============================================================
# CLI
# ============================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="generate_instincts.py — harvest operational exhaust into Atomic Instincts (Esalen-correct, dry-run default)"
    )
    parser.add_argument(
        "--since-commit", metavar="HASH",
        help="Override the git-log harvest window start (default: last 20 commits)",
    )
    parser.add_argument(
        "--out-dir", type=Path, default=DEFAULT_OUT_DIR,
        help=f"Where to write harvest + prompt sidecars (default: {DEFAULT_OUT_DIR})",
    )
    parser.add_argument(
        "--apply", metavar="CANDIDATES_JSON", type=Path,
        help="Apply M3-produced candidates from this JSON file (GATED — explicit flag required)",
    )
    parser.add_argument(
        "--apply-no-dry-run", action="store_true",
        help="With --apply, actually write files (default: report-only)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    # ===== APPLY PATH =====
    if args.apply:
        report = apply_candidates(
            args.apply,
            dry_run=not args.apply_no_dry_run,
        )
        print(json.dumps(report, indent=2))
        return 0 if report.get("error") is None else 1

    # ===== HARVEST + DRY-RUN PATH =====
    args.out_dir.mkdir(parents=True, exist_ok=True)
    harvested = harvest(since_commit=args.since_commit)

    # Persist the harvest context
    harvest_path = args.out_dir / f"harvest-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    harvest_path.write_text(json.dumps(harvested, indent=1, ensure_ascii=False), encoding="utf-8")

    # Persist the M3 prompt
    prompt = render_prompt(harvested)
    prompt_path = args.out_dir / f"prompt-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.txt"
    prompt_path.write_text(prompt, encoding="utf-8")

    # Print a one-screen summary
    print("=" * 70)
    print(f"GENERATE-INSTINCTS · DRY-RUN (no writes to {INSTINCTS_DIR})")
    print("=" * 70)
    print(f"  generated_at:    {harvested['generated_at']}")
    print(f"  since_commit:    {harvested['since_commit'] or '(last 20 commits)'}")
    print()
    print(f"  git_log:         {len(harvested['git_log'])} commits")
    print(f"  friction_log:    {harvested['friction_log'].get('new_count', 0)} new, {harvested['friction_log'].get('resolved_count', 0)} resolved")
    print(f"  audit_log:       exists={harvested['audit_log'].get('exists')}, entries={harvested['audit_log'].get('count', 0)}")
    if not harvested['audit_log'].get('exists'):
        print(f"    note: {harvested['audit_log'].get('note', '')}")
    print(f"  skillopt_runs:   exists={harvested['skillopt_runs'].get('exists')}, entries={harvested['skillopt_runs'].get('count', 0)}")
    print(f"  intake_log:      {harvested['intake_log'].get('count', 0)} recent drops")
    print(f"  existing_instincts: {harvested['existing_instincts'].get('count', 0)} (for dedup)")
    print()
    print(f"  harvest context: {harvest_path}")
    print(f"  M3 prompt:       {prompt_path}")
    print()
    print("  NEXT STEP: read the prompt, emit a JSON array of candidate")
    print("  instincts, then run:")
    print(f"    python3 generate_instincts.py --apply candidates.json")
    print(f"  (add --apply-no-dry-run to actually write the files)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
