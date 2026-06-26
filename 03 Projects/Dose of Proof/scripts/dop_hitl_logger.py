#!/usr/bin/env python3
"""
Dose of Proof — HITL Logger (Obsidian Leg)

V4 §3b bridge: reads block records from `queue/blocked-records-YYYY-MM-DD.mdl`
and appends a structured entry to the daily Obsidian HITL note at
`01 Daily/YYYY-MM-DD-hitl-dose-of-proof.md`.

The Telegram leg is handled separately by the ea-draft-approval-daily cron
pattern (Telegram requires a Dre-initiated session to send — see the
daily note for the constraint).

Called from `dop_engine.py v0.3` immediately after every SENSITIVE post.
Also can be run standalone to backfill or re-sync the daily note.

Usage:
    python3 dop_hitl_logger.py                  # process today's blocked-records
    python3 dop_hitl_logger.py --date 2026-07-05  # specific date
    python3 dop_hitl_logger.py --dry-run        # print what would be written
"""
import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof")
VAULT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent")
QUEUE_DIR = PROJECT_ROOT / "queue"
DAILY_DIR = VAULT_ROOT / "01 Daily"


def find_block_records(target_date: str) -> list[str]:
    """Read all block records from queue/blocked-records-{target_date}.mdl."""
    blocked_path = QUEUE_DIR / f"blocked-records-{target_date}.mdl"
    if not blocked_path.exists():
        return []
    content = blocked_path.read_text()
    # Extract block record blocks (between ─── lines)
    pattern = re.compile(
        r"(─{10,}\nBLOCK RECORD\n─{10,}\n.*?─{10,})",
        re.DOTALL,
    )
    return pattern.findall(content)


def format_block_record_for_obsidian(record: str, target_date: str) -> str:
    """Format a queue block record as an Obsidian-friendly entry."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M CT")
    return (
        f"\n### Block record — logged {timestamp}\n\n"
        f"```\n{record.strip()}\n```\n\n"
        f"> Per triage-gate-spec §3b: 1-hour SLA from generation to HITL surface. "
        f"4-hour SLA to resolution (auto-kill if exceeded).\n\n"
        f"---\n"
    )


def get_daily_note_path(target_date: str) -> Path:
    """Get the Obsidian daily note path for the target date. Create if missing."""
    daily_path = DAILY_DIR / f"{target_date}-hitl-dose-of-proof.md"
    return daily_path


def ensure_daily_note_exists(target_date: str) -> Path:
    """Create the daily note if it doesn't exist, with the V4 channel definition header."""
    daily_path = get_daily_note_path(target_date)
    if daily_path.exists():
        return daily_path
    content = f"""---
date: {target_date}
type: dose-of-proof-hitl-daily-note
status: auto-created-by-dop-hitl-logger
---

# Dose of Proof — HITL Daily Note ({target_date})

This file is the **Obsidian leg** of the HITL channel per [[triage-gate-spec]] §3b.
Mavis appends SENSITIVE post records here as the engine generates them.

See `01 Daily/2026-06-25-hitl-dose-of-proof.md` for the full channel definition
(V4 setup), or run `dop_hitl_logger.py --help` for context.

---

## Block records — {target_date}

"""
    daily_path.write_text(content)
    return daily_path


def log_to_obsidian(target_date: str, dry_run: bool = False) -> dict:
    """Append block records from queue/ to the Obsidian daily note."""
    records = find_block_records(target_date)
    if not records:
        return {
            "date": target_date,
            "records_found": 0,
            "records_logged": 0,
            "obsidian_path": None,
            "status": "no-blocked-records",
        }

    daily_path = ensure_daily_note_exists(target_date)
    appended_text = "\n## Block records logged — " + datetime.now().strftime("%H:%M CT") + "\n"

    for record in records:
        appended_text += format_block_record_for_obsidian(record, target_date)

    if dry_run:
        return {
            "date": target_date,
            "records_found": len(records),
            "records_logged": 0,
            "obsidian_path": str(daily_path),
            "status": "dry-run-not-written",
            "preview": appended_text[:500],
        }

    # Append to daily note (atomic write)
    temp_path = daily_path.with_suffix(".md.tmp")
    existing = daily_path.read_text() if daily_path.exists() else ""
    with open(temp_path, "w") as f:
        f.write(existing)
        f.write(appended_text)
    os.replace(temp_path, daily_path)

    return {
        "date": target_date,
        "records_found": len(records),
        "records_logged": len(records),
        "obsidian_path": str(daily_path),
        "status": "logged",
    }


def main():
    parser = argparse.ArgumentParser(description="Dose of Proof HITL Obsidian logger")
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Target date (default: today)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be written")
    args = parser.parse_args()

    print("=" * 70)
    print(f"Dose of Proof — HITL Logger (Obsidian Leg)")
    print(f"Target date: {args.date}")
    print("=" * 70)

    result = log_to_obsidian(args.date, dry_run=args.dry_run)
    print(f"\nRecords found: {result['records_found']}")
    print(f"Records logged: {result['records_logged']}")
    print(f"Obsidian path: {result['obsidian_path']}")
    print(f"Status: {result['status']}")

    if args.dry_run and "preview" in result:
        print(f"\n[DRY-RUN PREVIEW]:\n{result['preview']}")


if __name__ == "__main__":
    main()