#!/usr/bin/env python3
"""
validate-batch.py — Programmatic char-limit + indexing drift validator for Scribe batches.

Why this exists (2026-06-17): LLMs are notoriously unreliable at manual character
counting. The Scribe self-reports char counts in the batch file, but the chief (Mavis)
needs a *script-side* programmatic `len()` check before treating the batch as ready for
Andre's review. This is the gate.

The script:
  1. Parses the latest `## Run:` section of a `machine-batch-YYYY-MM-DD.md` file
  2. For each `### Draft N` block, extracts the **Post:** markdown body
  3. Computes `len(post_text)` programmatically (Python `len` on `str` — what X sees)
  4. Compares the Scribe's self-reported "Character count:" line against the programmatic count
  5. Validates ≤280 chars per draft (X free-tier hard limit)
  6. Optionally checks for 12 banned-phrase categories (defense-in-depth; Scribe is the
     primary filter, this is a backstop)
  7. Returns a JSON verdict to stdout

Exit codes:
  0 — all drafts pass (≤280, no banned phrases)
  1 — one or more drafts exceed 280 chars (BLOCK: do not file for Andre review)
  2 — one or more drafts contain banned-phrase patterns (WARN: surface, do not block)
  3 — parsing error (file unreadable, no `## Run:` section, no drafts found)
  4 — Scribe self-report drift (programmatic count != reported count by >2 chars)

Usage:
  python3 tools/validate-batch.py drafts/machine-batch-2026-06-17.md
  python3 tools/validate-batch.py drafts/machine-batch-2026-06-17.md --strict  # exit 4 on drift
  python3 tools/validate-batch.py drafts/machine-batch-2026-06-17.md --json     # JSON-only output

Wire-in: the EA (Mavis) runs this after every Scribe dispatch, BEFORE filing the drafts
in `00 Inbox/` or surfacing to Andre. A non-zero exit means the Scribe must be re-dispatched
with a fix request, or the chief takes over per the `orchestration-failure-modes.md`
escalation pattern.

Backstop to the Scribe's "Hard character limit" rule (scribe.md line 254). Not a replacement
for Scribe self-checks — those are the primary layer.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# --- constants -----------------------------------------------------------

HARD_LIMIT = 280  # X free-tier char limit
DRIFT_TOLERANCE = 2  # chars — anything beyond this is a Scribe self-report failure

# 12 banned-phrase categories (the original Scribe's enforcement list). These are
# defensive — Scribe is the primary filter. Patterns are case-insensitive.
BANNED_PHRASES: list[str] = [
    r"\bdive into\b",
    r"\bin today's fast-paced world\b",
    r"\bunlock\b",
    r"\bgame[\s-]?changer\b",
    r"\bgreat point\b",
    r"\bat the end of the day\b",
    r"\bin conclusion\b",
    r"\bdelve\b",
    r"\bwhether you're a\b",
    r"\bhere's why\b",
    r"\bthe bottom line is\b",
    r"\bin the world of\b",
]

# --- regexes -------------------------------------------------------------

# Match a "## Run: ..." section header (the latest one in the file is what we validate).
RUN_HEADER = re.compile(r"^##\s+Run:\s+", re.MULTILINE)

# Match "### Draft N (...)" block headers. Group 1 is the index.
DRAFT_HEADER = re.compile(r"^###\s+Draft\s+(\d+)\b", re.MULTILINE)

# Match the post body block — everything between "**Post:**" and the next "---" or
# "**Character count:**" line. We use the "**Character count:**" boundary as the
# stop signal because it's the most reliable end-of-post marker.
POST_BODY = re.compile(
    r"\*\*Post:\*\*\s*\n+(.*?)(?=\n\*\*Character count:\*\*|\n---\n|\n###\s+Draft\b|\Z)",
    re.DOTALL,
)

# Match the Scribe's self-reported character count.
REPORTED_COUNT = re.compile(r"\*\*Character count:\*\*\s+(\d+)\s*/\s*280", re.IGNORECASE)


def extract_latest_run(text: str) -> str:
    """Return just the latest `## Run:` section of the batch file."""
    matches = list(RUN_HEADER.finditer(text))
    if not matches:
        raise ValueError("no `## Run:` section found in batch file")
    return text[matches[-1].start():]


def parse_drafts(run_text: str) -> list[dict]:
    """Parse the run section into a list of drafts, each with: index, post, reported_count."""
    drafts: list[dict] = []
    headers = list(DRAFT_HEADER.finditer(run_text))
    if not headers:
        raise ValueError("no `### Draft N` blocks found in run section")

    for i, header in enumerate(headers):
        idx = int(header.group(1))
        # The block extends to the next draft header or end of run.
        start = header.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(run_text)
        block = run_text[start:end]

        # Extract the post body.
        post_match = POST_BODY.search(block)
        if not post_match:
            drafts.append({"index": idx, "error": "no `**Post:**` block found"})
            continue
        post = post_match.group(1).strip()

        # Extract the Scribe's reported char count.
        reported_match = REPORTED_COUNT.search(block)
        reported = int(reported_match.group(1)) if reported_match else None

        drafts.append(
            {
                "index": idx,
                "post": post,
                "programmatic_count": len(post),
                "reported_count": reported,
            }
        )
    return drafts


def check_banned_phrases(post: str) -> list[str]:
    """Return the list of banned-phrase regexes that matched (lowercased phrase)."""
    post_lower = post.lower()
    hits = []
    for pattern in BANNED_PHRASES:
        if re.search(pattern, post_lower):
            hits.append(pattern)
    return hits


def validate(batch_path: Path) -> dict:
    text = batch_path.read_text(encoding="utf-8")
    run_text = extract_latest_run(text)
    drafts = parse_drafts(run_text)

    results: list[dict] = []
    overall = {"status": "pass", "max_count": 0}

    for d in drafts:
        if "error" in d:
            results.append({"index": d["index"], "status": "error", "detail": d["error"]})
            overall["status"] = "error"
            continue

        pc = d["programmatic_count"]
        rc = d["reported_count"]
        drift = (rc - pc) if rc is not None else None

        issues: list[str] = []
        if pc > HARD_LIMIT:
            issues.append(f"exceeds 280 chars ({pc}/280)")
        if drift is not None and abs(drift) > DRIFT_TOLERANCE:
            issues.append(f"self-report drift (reported={rc}, programmatic={pc}, delta={drift:+d})")

        banned = check_banned_phrases(d["post"])
        if banned:
            issues.append(f"banned-phrase hits: {banned}")

        if pc > overall["max_count"]:
            overall["max_count"] = pc

        if not issues:
            results.append(
                {
                    "index": d["index"],
                    "status": "pass",
                    "programmatic_count": pc,
                    "reported_count": rc,
                    "drift": drift,
                }
            )
        else:
            results.append(
                {
                    "index": d["index"],
                    "status": "fail",
                    "programmatic_count": pc,
                    "reported_count": rc,
                    "drift": drift,
                    "issues": issues,
                }
            )
            if any("exceeds 280" in i for i in issues):
                overall["status"] = "fail" if overall["status"] != "fail" else overall["status"]
            elif any("drift" in i for i in issues) and overall["status"] == "pass":
                overall["status"] = "drift"
            elif overall["status"] == "pass":
                overall["status"] = "warn"

    return {"batch": str(batch_path), "verdict": overall, "drafts": results}


def main() -> int:
    parser = argparse.ArgumentParser(description="Programmatic char-limit validator for Scribe batches.")
    parser.add_argument("batch_file", type=Path, help="Path to the machine-batch-YYYY-MM-DD.md file")
    parser.add_argument("--strict", action="store_true", help="Exit 4 on Scribe self-report drift (default: warn only)")
    parser.add_argument("--json", action="store_true", help="JSON-only output (suppress human-readable summary)")
    args = parser.parse_args()

    try:
        result = validate(args.batch_file)
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        v = result["verdict"]
        print(f"Batch: {result['batch']}")
        print(f"Verdict: {v['status']} (max char count: {v['max_count']}/280)")
        print()
        for d in result["drafts"]:
            idx = d.get("index", "?")
            status = d.get("status", "?")
            if status == "pass":
                print(f"  Draft {idx}: PASS  ({d['programmatic_count']} chars, reported {d['reported_count']}, drift {d['drift']:+d})")
            elif status == "fail":
                print(f"  Draft {idx}: FAIL  ({d['programmatic_count']} chars, reported {d['reported_count']}, drift {d['drift']:+d})")
                for issue in d.get("issues", []):
                    print(f"          - {issue}")
            elif status == "warn":
                print(f"  Draft {idx}: WARN  ({d['programmatic_count']} chars, reported {d['reported_count']}, drift {d['drift']:+d})")
                for issue in d.get("issues", []):
                    print(f"          - {issue}")
            else:
                print(f"  Draft {idx}: ERROR  {d.get('detail', 'unknown')}")

    # Map verdict to exit code.
    if result["verdict"]["status"] == "fail":
        return 1
    if result["verdict"]["status"] == "warn":
        return 2
    if result["verdict"]["status"] == "drift" and args.strict:
        return 4
    if result["verdict"]["status"] == "error":
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
