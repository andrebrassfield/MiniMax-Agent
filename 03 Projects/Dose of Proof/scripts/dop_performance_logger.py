#!/usr/bin/env python3
"""
Dose of Proof — Performance Logger (V7 + V9)

Per triage-gate-spec §6, every post is logged to a performance_log.json with
15 canonical fields. The log is the source of truth for the July 7 data read
(gate integrity metrics, hook-family bias, D1/D7 engagement).

V7 — Schema implementation: 15 fields per §6.
V9 — ENGAGEMENT_D1 (24h) + ENGAGEMENT_D7 (7d) capture windows.

The log captures:
- Auto-fired events: post publication, block, kill (from queue/published-*.mdl,
  queue/hold/, queue/blocked-records-*.mdl)
- Engagement windows: T+24h (D1) and T+168h (D7) via Postiz analytics fetch

Usage:
    python3 dop_performance_logger.py --date 2026-06-26 --action ingest   # read queue files, write log rows
    python3 dop_performance_logger.py --date 2026-06-26 --action capture-d1   # fetch D1 engagement from Postiz
    python3 dop_performance_logger.py --date 2026-07-03 --action capture-d7   # fetch D7 engagement from Postiz
    python3 dop_performance_logger.py --date 2026-06-26 --action status    # show what's logged for that date
    python3 dop_performance_logger.py --test-row                          # write a single test row to verify schema
"""
import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof")
QUEUE_DIR = PROJECT_ROOT / "queue"
MEMORY_DIR = PROJECT_ROOT / "memory"
LOG_PATH = MEMORY_DIR / "dose-of-proof-performance-log.json"

# V7: §6 schema fields (15 canonical)
PERFORMANCE_LOG_FIELDS = [
    "POST_ID", "DATE_GENERATED", "PLATFORM", "HOOK_FAMILY",
    "GENERATOR_CLASS", "MAVIS_CLASS", "FINAL_STATUS",
    "RESOLUTION", "RESOLVED_BY", "RESOLVED_AT", "PUBLISH_TIME",
    "ENGAGEMENT_D1", "ENGAGEMENT_D7", "FLAGS_TRIGGERED", "NOTES",
]

# §5 hook families (must match dop_engine.py HOOK_FAMILIES)
HOOK_FAMILIES_CANONICAL = {
    "regulatory-reality", "biomarker-education", "terrain-mechanics",
    "citizen-science", "literature-map", "reconstitution-math",
    "telehealth-routing", "community-proof",
}


def ensure_log_file():
    """Create the performance_log.json if it doesn't exist with empty array."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.write_text("[]")


def read_log() -> list:
    """Read the current performance_log."""
    ensure_log_file()
    try:
        return json.loads(LOG_PATH.read_text())
    except json.JSONDecodeError:
        return []


def write_log(log: list):
    """Atomic write of the performance_log."""
    temp_path = LOG_PATH.with_suffix(".json.tmp")
    with open(temp_path, "w") as f:
        json.dump(log, f, indent=2)
    os.replace(temp_path, LOG_PATH)


def find_post_in_queue(post_id: str, target_date: str) -> Optional[dict]:
    """Look up a post_id across the queue files for the target date."""
    # Check published, drafts, hold, blocked-records
    for filename in [
        f"published-{target_date}.mdl",
        f"drafts-{target_date}.mdl",
        f"hold/drafts-{target_date}.mdl",
        f"blocked-records-{target_date}.mdl",
    ]:
        path = QUEUE_DIR / filename
        if not path.exists():
            continue
        content = path.read_text()
        if post_id in content:
            return {"file": path.name, "found": True}
    return None


def parse_drafts_for_posts(target_date: str) -> list[dict]:
    """Parse queue/drafts-{date}.mdl into structured post dicts (V7 schema).

    Handles BOTH legacy v0.1/v0.2 format (single-row pipe-delimited) and new v0.3 format
    (--- separated block with POST_ID: prefix).
    """
    drafts_path = QUEUE_DIR / f"drafts-{target_date}.mdl"
    if not drafts_path.exists():
        drafts_path = QUEUE_DIR / "hold" / f"drafts-{target_date}.mdl"
    if not drafts_path.exists():
        return []

    content = drafts_path.read_text()

    # PILLAR → hook_family mapping (mirror of dop_engine.py PILLAR_TO_HOOK_FAMILY)
    pillar_to_hook_family = {
        "P1": "citizen-science",
        "P2": "regulatory-reality",
        "P3": "reconstitution-math",
        "PCAC": "regulatory-reality",
    }

    posts = []

    # First, try new v0.3 format with --- separated blocks
    if "POST_ID:" in content:
        blocks = re.split(r"^-{3,}$", content, flags=re.MULTILINE)
        for block in blocks:
            if "POST_ID:" not in block:
                continue
            post = {}
            for line in block.split("\n"):
                if ":" in line:
                    key, _, val = line.partition(":")
                    post[key.strip()] = val.strip()
            posts.append({
                "POST_ID": post.get("POST_ID", ""),
                "DATE_GENERATED": post.get("DATE_GENERATED") or datetime.now().isoformat(),
                "PLATFORM": post.get("PLATFORM") or post.get("CHANNEL", ""),
                "HOOK_FAMILY": post.get("HOOK_FAMILY", "regulatory-reality"),
                "GENERATOR_CLASS": "CLEAR" if post.get("CLASSIFICATION", "CLEAR") == "CLEAR" else "SENSITIVE",
                "MAVIS_CLASS": "CLEAR",
                "FINAL_STATUS": "BLOCKED" if "BLOCKED" in post.get("STATUS", "") else "PUBLISHED",
                "RESOLUTION": "—",
                "RESOLVED_BY": "—",
                "RESOLVED_AT": "—",
                "PUBLISH_TIME": "—",
                "ENGAGEMENT_D1": 0,
                "ENGAGEMENT_D7": 0,
                "FLAGS_TRIGGERED": post.get("SENSITIVE_REASONS", "none"),
                "NOTES": "",
            })

    # Also handle legacy v0.1/v0.2 format: `post_id | pillar | channel | date | time | compliance | content | image_paths`
    for line in content.split("\n"):
        if "|" not in line or line.startswith("#") or line.startswith("Format:") or line.startswith("---"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6 or not parts[0].startswith("dop-"):
            continue
        # Skip if we already captured this from the new format
        if any(p.get("POST_ID") == parts[0] for p in posts):
            continue
        post_id, pillar, channel, date, time, compliance = parts[:6]
        pillar_clean = pillar.replace("(calendar logic only)", "").strip()
        compliance_clean = compliance.replace("(calendar logic only)", "").strip()
        hook_family = pillar_to_hook_family.get(pillar_clean, "regulatory-reality")

        # In legacy format, no S1-S4 self-classification — assume CLEAR for PASS, SENSITIVE for FAIL
        generator_class = "CLEAR" if "PASS" in compliance_clean else "SENSITIVE"
        flags_triggered = "none" if "PASS" in compliance_clean else "S1,S2,S3,S4 (legacy format — re-run gate to verify)"

        posts.append({
            "POST_ID": post_id,
            "DATE_GENERATED": f"{date}T{time}:00",
            "PLATFORM": channel,
            "HOOK_FAMILY": hook_family,
            "GENERATOR_CLASS": generator_class,
            "MAVIS_CLASS": "CLEAR",  # Pre-v0.3: no first-pass screen under new gate
            "FINAL_STATUS": "PUBLISHED",  # Default for legacy queue items
            "RESOLUTION": "—",
            "RESOLVED_BY": "—",
            "RESOLVED_AT": "—",
            "PUBLISH_TIME": f"{date}T{time}:00",
            "ENGAGEMENT_D1": 0,
            "ENGAGEMENT_D7": 0,
            "FLAGS_TRIGGERED": flags_triggered,
            "NOTES": "Ingested from legacy v0.1/v0.2 format. Re-run gate for current classification.",
        })

    return posts


def parse_blocked_records_for_posts(target_date: str) -> list[dict]:
    """Parse queue/blocked-records-{date}.mdl into structured post dicts."""
    blocked_path = QUEUE_DIR / f"blocked-records-{target_date}.mdl"
    if not blocked_path.exists():
        return []

    content = blocked_path.read_text()
    posts = []
    pattern = re.compile(r"─{10,}\nBLOCK RECORD\n─{10,}\n(.*?)─{10,}", re.DOTALL)

    for match in pattern.finditer(content):
        body = match.group(1).strip()
        record = {}
        for line in body.split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                record[key.strip()] = val.strip()

        status = record.get("STATUS", "BLOCKED")
        is_killed = "KILLED" in status

        posts.append({
            "POST_ID": record.get("POST_ID", ""),
            "DATE_GENERATED": record.get("DATE_GENERATED", ""),
            "PLATFORM": record.get("PLATFORM", ""),
            "HOOK_FAMILY": record.get("HOOK_FAMILY", "regulatory-reality"),
            "GENERATOR_CLASS": "SENSITIVE",
            "MAVIS_CLASS": "SENSITIVE",
            "FINAL_STATUS": "KILLED" if is_killed else "BLOCKED",
            "RESOLUTION": record.get("RESOLUTION", "—") if is_killed else "—",
            "RESOLVED_BY": record.get("RESOLVED_BY", "—") if is_killed else "—",
            "RESOLVED_AT": record.get("RESOLVED_AT", "—") if is_killed else "—",
            "PUBLISH_TIME": "—",
            "ENGAGEMENT_D1": 0,
            "ENGAGEMENT_D7": 0,
            "FLAGS_TRIGGERED": record.get("FLAGS_TRIGGERED", "none"),
            "NOTES": record.get("NOTES", ""),
        })

    return posts


def parse_published_for_posts(target_date: str) -> list[dict]:
    """Parse queue/published-{date}.mdl for PUBLISH_TIME."""
    pub_path = QUEUE_DIR / f"published-{target_date}.mdl"
    if not pub_path.exists():
        return []
    content = pub_path.read_text()
    publish_times = {}
    for line in content.split("\n"):
        if "|" in line and "OK" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                post_id = parts[0]
                # Time format: 2026-06-26 09:00
                publish_times[post_id] = parts[2]
    return publish_times


def fetch_postiz_engagement(post_id: str, platform: str) -> Optional[dict]:
    """V9: Fetch engagement metrics from Postiz API.

    Returns {"engagement_d1": int, "engagement_d7": int} or None if API call fails.

    Note: Postiz may not have a direct engagement analytics endpoint. If unavailable,
    this function returns None and the metric must be captured manually via Postiz UI
    (logged in OPERATIONS-LOG with manual_override flag).
    """
    # Postiz API credentials are in OPERATIONS-LOG notes (referenced but not exposed here).
    # Without confirmed endpoint, return None and document as manual capture path.
    return None


def ingest_from_queue(target_date: str, dry_run: bool = False) -> dict:
    """V7 ingest: read queue files for the date, append performance_log rows."""
    log = read_log()
    existing_post_ids = {row.get("POST_ID") for row in log}

    # Parse drafts (auto-push eligible)
    drafts = parse_drafts_for_posts(target_date)
    # Parse blocked records (auto-killed or held)
    blocked = parse_blocked_records_for_posts(target_date)

    # Cross-reference with published to populate PUBLISH_TIME
    pub_times = parse_published_for_posts(target_date)

    new_rows = []
    for post in drafts + blocked:
        if post["POST_ID"] in existing_post_ids:
            continue
        if post["POST_ID"] in pub_times:
            post["PUBLISH_TIME"] = pub_times[post["POST_ID"]]
        new_rows.append(post)

    if dry_run:
        return {
            "date": target_date,
            "drafts_parsed": len(drafts),
            "blocked_parsed": len(blocked),
            "new_rows": len(new_rows),
            "log_size_before": len(log),
            "log_size_after": len(log) + len(new_rows),
            "status": "dry-run-not-written",
            "sample_new_row": new_rows[0] if new_rows else None,
        }

    log.extend(new_rows)
    write_log(log)

    return {
        "date": target_date,
        "drafts_parsed": len(drafts),
        "blocked_parsed": len(blocked),
        "new_rows": len(new_rows),
        "log_size_before": len(log) - len(new_rows),
        "log_size_after": len(log),
        "status": "ingested",
    }


def capture_engagement_window(target_date: str, window: str, dry_run: bool = False) -> dict:
    """V9: Capture engagement metrics at T+24h (D1) or T+168h (D7)."""
    log = read_log()

    # Find posts published on target_date
    published_posts = [
        row for row in log
        if row.get("DATE_GENERATED", "").startswith(target_date)
        and row.get("FINAL_STATUS") == "PUBLISHED"
    ]

    if not published_posts:
        return {"date": target_date, "window": window, "posts_found": 0, "updated": 0, "status": "no-published-posts"}

    field = f"ENGAGEMENT_{window.upper()}"
    updated_count = 0
    for post in published_posts:
        # Try Postiz API first
        engagement = fetch_postiz_engagement(post["POST_ID"], post.get("PLATFORM", ""))

        if engagement is None:
            # Manual capture path: append to NOTES, leave metric at 0
            # Co-CEO / Dre fills manually via Postiz UI
            post["NOTES"] = (post.get("NOTES", "") + f" | {window} capture: PENDING manual from Postiz UI").strip()
        else:
            post[field] = engagement.get(f"engagement_{window.lower()}", 0)
            updated_count += 1

    if not dry_run:
        write_log(log)

    return {
        "date": target_date,
        "window": window,
        "posts_found": len(published_posts),
        "updated": updated_count,
        "pending_manual": len(published_posts) - updated_count,
        "status": "captured" if not dry_run else "dry-run",
    }


def show_status(target_date: str) -> dict:
    """Show what's logged for a date."""
    log = read_log()
    matching = [row for row in log if row.get("DATE_GENERATED", "").startswith(target_date)]
    return {
        "date": target_date,
        "rows": len(matching),
        "sample": matching[0] if matching else None,
        "log_total_size": len(log),
    }


def write_test_row() -> dict:
    """V7 verification: write a single test row matching §6 schema."""
    test_row = {
        "POST_ID": "dop-fb-TEST-V7-001",
        "DATE_GENERATED": "2026-06-25T18:50:00",
        "PLATFORM": "facebook",
        "HOOK_FAMILY": "citizen-science",
        "GENERATOR_CLASS": "CLEAR",
        "MAVIS_CLASS": "CLEAR",
        "FINAL_STATUS": "PUBLISHED",
        "RESOLUTION": "—",
        "RESOLVED_BY": "—",
        "RESOLVED_AT": "—",
        "PUBLISH_TIME": "2026-06-26T09:00:00",
        "ENGAGEMENT_D1": 0,
        "ENGAGEMENT_D7": 0,
        "FLAGS_TRIGGERED": "none",
        "NOTES": "Test row for V7 schema verification (triage-gate-spec §6 15-field canonical schema).",
    }
    log = read_log()
    # Remove any prior test rows
    log = [row for row in log if not row.get("POST_ID", "").startswith("dop-")]
    log.append(test_row)
    write_log(log)
    return {"status": "test-row-written", "log_size": len(log), "row": test_row}


def main():
    parser = argparse.ArgumentParser(description="Dose of Proof performance logger (V7+V9)")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)")
    parser.add_argument("--action", choices=["ingest", "capture-d1", "capture-d7", "status", "test-row"],
                        default="status", help="Action to perform")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be written")
    args = parser.parse_args()

    if args.action == "test-row":
        result = write_test_row()
        print(json.dumps(result, indent=2))
        return

    if not args.date:
        print("ERROR: --date required for actions: ingest, capture-d1, capture-d7, status")
        sys.exit(1)

    print("=" * 70)
    print(f"Dose of Proof — Performance Logger (V7+V9)")
    print(f"Date: {args.date} | Action: {args.action}")
    print("=" * 70)

    if args.action == "ingest":
        result = ingest_from_queue(args.date, dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
    elif args.action == "capture-d1":
        result = capture_engagement_window(args.date, "d1", dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
    elif args.action == "capture-d7":
        result = capture_engagement_window(args.date, "d7", dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
    elif args.action == "status":
        result = show_status(args.date)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()