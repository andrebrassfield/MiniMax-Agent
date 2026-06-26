#!/usr/bin/env python3
"""
Dose of Proof — SLA Enforcer (4-hour auto-kill)

V5: Per triage-gate-spec §3b, blocked posts MUST be reviewed within 4 hours of generation.
If not, the post is auto-killed (NOT auto-cleared). Default failure mode is suppression,
never publication.

This script:
1. Scans queue/blocked-records-*.mdl for STATUS=BLOCKED records
2. Computes time-since-DATE_GENERATED for each
3. If >4 hours: auto-flips STATUS → KILLED, RESOLUTION → AUTO_KILLED_SLA, RESOLVED_BY → sla-enforcer
4. Logs the SLA kill to OPERATIONS-LOG.md
5. Posts to the HITL Obsidian daily note

Run as a cron. Recommended schedule: every 30 minutes during active hours (06:00-23:00 CT)
to catch SLA breaches promptly.

Schedule spec:
    0,30 6-23 * * *   America/Chicago   (every 30 min, 06:00-23:00 CT)
    Or simpler: every 15 minutes 24/7 for paranoid mode

Usage:
    python3 dop_sla_enforcer.py                  # check today's + yesterday's blocked-records
    python3 dop_sla_enforcer.py --date 2026-07-15
    python3 dop_sla_enforcer.py --dry-run        # show what would be killed
    python3 dop_sla_enforcer.py --all-dates      # scan all blocked-records files
"""
import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof")
QUEUE_DIR = PROJECT_ROOT / "queue"
OPS_LOG = PROJECT_ROOT / "OPERATIONS-LOG.md"

SLA_HOURS = 4
SLA_TIMEDELTA = timedelta(hours=SLA_HOURS)


def find_blocked_records_files(specific_date: str = None, all_dates: bool = False) -> list[Path]:
    """Find all blocked-records files to scan."""
    if specific_date:
        path = QUEUE_DIR / f"blocked-records-{specific_date}.mdl"
        return [path] if path.exists() else []
    if all_dates:
        return sorted(QUEUE_DIR.glob("blocked-records-*.mdl"))
    # Default: today + yesterday
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    paths = []
    for d in [today, yesterday]:
        p = QUEUE_DIR / f"blocked-records-{d}.mdl"
        if p.exists():
            paths.append(p)
    return paths


def parse_block_records(content: str) -> list[dict]:
    """Parse a blocked-records file into structured records."""
    pattern = re.compile(
        r"─{10,}\nBLOCK RECORD\n─{10,}\n(.*?)─{10,}",
        re.DOTALL,
    )
    records = []
    for match in pattern.finditer(content):
        body = match.group(1).strip()
        record = {}
        for line in body.split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                record[key.strip()] = val.strip()
        records.append({
            "raw_body": body,
            "POST_ID": record.get("POST_ID", ""),
            "DATE_GENERATED": record.get("DATE_GENERATED", ""),
            "PLATFORM": record.get("PLATFORM", ""),
            "HOOK_FAMILY": record.get("HOOK_FAMILY", ""),
            "SCHEDULED_SLOT": record.get("SCHEDULED_SLOT", ""),
            "CLASSIFICATION": record.get("CLASSIFICATION", ""),
            "FLAGS_TRIGGERED": record.get("FLAGS_TRIGGERED", ""),
            "FLAGS_DETAIL": record.get("FLAGS_DETAIL", ""),
            "GENERATOR_NOTE": record.get("GENERATOR_NOTE", ""),
            "MAVIS_NOTE": record.get("MAVIS_NOTE", ""),
            "STATUS": record.get("STATUS", ""),
            "RESOLVED_BY": record.get("RESOLVED_BY", ""),
            "RESOLVED_AT": record.get("RESOLVED_AT", ""),
            "RESOLUTION": record.get("RESOLUTION", ""),
            "NOTES": record.get("NOTES", ""),
        })
    return records


def check_sla(record: dict, now: datetime = None) -> dict:
    """Check if a record has breached the 4-hour SLA."""
    now = now or datetime.now()
    try:
        generated = datetime.fromisoformat(record["DATE_GENERATED"])
        # If no timezone info, assume local
        if generated.tzinfo is None:
            elapsed = now - generated
        else:
            from datetime import timezone
            elapsed = now.astimezone() - generated.astimezone()
    except (ValueError, KeyError) as e:
        return {
            "breached": False,
            "elapsed_hours": None,
            "error": f"Could not parse DATE_GENERATED: {e}",
        }

    breached = elapsed > SLA_TIMEDELTA
    return {
        "breached": breached,
        "elapsed_hours": elapsed.total_seconds() / 3600,
        "generated_at": record["DATE_GENERATED"],
        "now": now.isoformat(),
    }


def auto_kill_record_in_file(file_path: Path, post_id: str) -> bool:
    """Update a STATUS=BLOCKED record in the file to STATUS=KILLED + RESOLUTION=AUTO_KILLED_SLA.

    Replaces the entire STATUS/RESOLVED_BY/RESOLVED_AT/RESOLUTION block atomically to avoid
    duplicate field lines if the original has placeholder blanks.
    """
    content = file_path.read_text()
    if post_id not in content:
        return False

    # Find the record block for this post_id
    pattern = re.compile(
        r"(─{10,}\nBLOCK RECORD\n─{10,}\n.*?"
        + re.escape(post_id)
        + r".*?─{10,})",
        re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        return False

    original_block = match.group(1)
    if "STATUS:          BLOCKED" not in original_block:
        return False  # Already resolved

    now_iso = datetime.now().isoformat()
    # Replace the whole STATUS/RESOLVED_BY/RESOLVED_AT/RESOLUTION block (4 lines)
    status_block_pattern = re.compile(
        r"STATUS:\s+BLOCKED\nRESOLVED_BY:\s+\[blank[^\]]*\]\nRESOLVED_AT:\s+\[blank[^\]]*\]\nRESOLUTION:\s+\[blank[^\]]*\]",
        re.DOTALL,
    )
    replacement = (
        f"STATUS:          KILLED\n"
        f"RESOLVED_BY:     AUTO_KILL_SLA (4-hour SLA breach — triage-gate-spec §3b)\n"
        f"RESOLVED_AT:     {now_iso}\n"
        f"RESOLUTION:      AUTO_KILLED_SLA"
    )
    new_block = status_block_pattern.sub(replacement, original_block)

    new_content = content.replace(original_block, new_block, 1)

    # Atomic write
    temp_path = file_path.with_suffix(".mdl.tmp")
    with open(temp_path, "w") as f:
        f.write(new_content)
    os.replace(temp_path, file_path)
    return True


def log_to_ops_log(killed_records: list[dict], date: str):
    """Append SLA kills to OPERATIONS-LOG.md."""
    if not killed_records:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M CT")
    entry = f"\n## SLA Enforcer — Auto-Kill — {timestamp}\n\n"
    entry += f"Per triage-gate-spec §3b: blocked posts not reviewed within 4 hours are auto-killed.\n\n"
    entry += f"**Records killed this run: {len(killed_records)}**\n\n"
    for r in killed_records:
        elapsed = r.get('elapsed_hours')
        elapsed_str = f"{elapsed:.1f}h" if isinstance(elapsed, (int, float)) else "?"
        entry += f"- `{r['POST_ID']}` — generated {r['DATE_GENERATED']} — elapsed {elapsed_str} — flags: {r['FLAGS_TRIGGERED']} — hook_family: {r['HOOK_FAMILY']}\n"
    entry += "\n"

    with open(OPS_LOG, "a") as f:
        f.write(entry)


def post_to_obsidian_hitl(killed_records: list[dict], date: str):
    """Append SLA kills to the HITL Obsidian daily note."""
    if not killed_records:
        return

    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from dop_hitl_logger import ensure_daily_note_exists

        daily_path = ensure_daily_note_exists(date)
        timestamp = datetime.now().strftime("%H:%M CT")

        appended = f"\n## SLA Auto-Kill — {timestamp}\n\n"
        appended += f"> triage-gate-spec §3b: {len(killed_records)} blocked post(s) auto-killed for >4-hour SLA breach.\n\n"
        for r in killed_records:
            elapsed = r.get('elapsed_hours')
            elapsed_str = f"{elapsed:.1f}h" if isinstance(elapsed, (int, float)) else "?"
            appended += f"- **{r['POST_ID']}** — generated {r['DATE_GENERATED']} — elapsed {elapsed_str} — flags: {r['FLAGS_TRIGGERED']}\n"
        appended += "\n---\n"

        existing = daily_path.read_text() if daily_path.exists() else ""
        temp_path = daily_path.with_suffix(".md.tmp")
        with open(temp_path, "w") as f:
            f.write(existing)
            f.write(appended)
        os.replace(temp_path, daily_path)
    except Exception as e:
        print(f"⚠️  Failed to post to Obsidian HITL note: {e}")


def main():
    parser = argparse.ArgumentParser(description="Dose of Proof SLA enforcer (4-hour auto-kill)")
    parser.add_argument("--date", help="Specific date (YYYY-MM-DD) to scan")
    parser.add_argument("--all-dates", action="store_true", help="Scan all blocked-records files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be killed, don't write")
    args = parser.parse_args()

    print("=" * 70)
    print(f"Dose of Proof — SLA Enforcer (4-hour auto-kill)")
    print(f"SLA window: {SLA_HOURS} hours")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'ACTIVE'}")
    print("=" * 70)

    files = find_blocked_records_files(args.date, args.all_dates)
    if not files:
        print("\nNo blocked-records files found.")
        return

    total_scanned = 0
    total_breached = 0
    total_killed = 0
    all_kills = []

    for file_path in files:
        content = file_path.read_text()
        records = parse_block_records(content)
        print(f"\n{file_path.name}: {len(records)} records")

        for record in records:
            total_scanned += 1
            if record["STATUS"] != "BLOCKED":
                continue  # Already resolved

            sla = check_sla(record)
            if sla.get("error"):
                print(f"  ⚠️  {record['POST_ID']}: {sla['error']}")
                continue

            elapsed = sla["elapsed_hours"]
            if sla["breached"]:
                total_breached += 1
                print(f"  ⛔ BREACH: {record['POST_ID']} — {elapsed:.1f}h elapsed (SLA={SLA_HOURS}h)")

                # Annotate the record with elapsed_hours for logging
                record_with_elapsed = {**record, "elapsed_hours": elapsed}

                if not args.dry_run:
                    killed = auto_kill_record_in_file(file_path, record["POST_ID"])
                    if killed:
                        total_killed += 1
                        all_kills.append(record_with_elapsed)
                        print(f"     ✅ AUTO-KILLED")
                    else:
                        print(f"     ⚠️  Auto-kill failed (already resolved?)")
                else:
                    total_killed += 1
                    all_kills.append(record_with_elapsed)
                    print(f"     [DRY-RUN] Would auto-kill")

    print(f"\nSummary: scanned={total_scanned} breached={total_breached} killed={total_killed}")

    if not args.dry_run and all_kills:
        # Determine the date for HITL logging (use most recent kill's date or today)
        date_for_log = datetime.now().strftime("%Y-%m-%d")
        log_to_ops_log(all_kills, date_for_log)
        post_to_obsidian_hitl(all_kills, date_for_log)
        print(f"\n📝 Logged to OPERATIONS-LOG.md")
        print(f"📓 Posted to HITL Obsidian daily note")


if __name__ == "__main__":
    main()