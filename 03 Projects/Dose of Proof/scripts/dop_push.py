#!/usr/bin/env python3
"""
Dose of Proof — Queue-aware Postiz Push

Reads queue/drafts-YYYY-MM-DD.mdl, parses pipe-delimited rows, uploads images,
schedules posts via Postiz REST API. Skips Pinterest (Dre manual push).
"""
import argparse
import csv
import json
import os
import re
import requests
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof")
QUEUE_DIR = PROJECT_ROOT / "queue"

# =============================================================================
# §3d HALT HARD INTERLOCK — Co-CEO rule 2026-06-25
# Per [[triage-gate-spec]] §3d, the push script refuses to run if HALTED.
# This is a code-level precondition, not a prompt instruction.
# =============================================================================
HALT_STATE_FILE = Path.home() / ".mavis" / "state" / "dop-engine-halt.state"

def check_halt_precondition() -> int:
    """
    Returns 0 if push may run, non-zero if HALTED.
    Called as the FIRST action in main() before any work.
    """
    if not HALT_STATE_FILE.exists():
        return 0  # No halt state file → push may run
    try:
        state = json.loads(HALT_STATE_FILE.read_text())
        if state.get("halted"):
            print(f"⛔ PUSH HALTED — refusing to run.", file=sys.stderr)
            print(f"   Halted at: {state.get('halted_at')}", file=sys.stderr)
            print(f"   Halted by: {state.get('halted_by')}", file=sys.stderr)
            print(f"   Reason: {state.get('reason')}", file=sys.stderr)
            print(f"   To resume: edit {HALT_STATE_FILE} and set halted:false, OR delete the file.", file=sys.stderr)
            print(f"   See [[triage-gate-spec]] §3d.", file=sys.stderr)
            return 78  # EX_CONFIG — configuration error
        else:
            return 0  # Halt state file present but halted:false → push may run
    except (json.JSONDecodeError, KeyError) as e:
        print(f"⛔ PUSH HALTED — halt state file malformed: {e}", file=sys.stderr)
        print(f"   Treating as halted (fail-closed). See [[triage-gate-spec]] §3d.", file=sys.stderr)
        return 78  # Treat malformed as halted (fail-closed)

API_KEY = "3d484ba6f21899ad28365acbf29a3ebe30a1694aba811b4f414259581dcb5ccf"
BASE_URL = "https://api.postiz.com/public/v1"
HEADERS = {"Authorization": API_KEY, "Content-Type": "application/json"}


def log(line):
    print(line)


def list_integrations():
    r = requests.get(f"{BASE_URL}/integrations", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def upload_image(local_path):
    with open(local_path, "rb") as f:
        r = requests.post(
            f"{BASE_URL}/upload",
            headers={"Authorization": API_KEY},
            files={"file": (os.path.basename(local_path), f, "image/png")},
            timeout=60,
        )
    r.raise_for_status()
    data = r.json()
    return data["id"], data["path"]


def schedule_post(integration_id, content, publish_date_utc, images=None, channel="facebook"):
    if channel == "instagram":
        settings = {"__type": "post", "post_type": "post"}
    else:
        settings = {"__type": "post"}
    value_item = {"content": content, "image": images or []}
    payload = {
        "type": "schedule",
        "date": publish_date_utc,
        "shortLink": False,
        "tags": [],
        "posts": [{
            "integration": {"id": integration_id},
            "value": [value_item],
            "settings": settings,
        }],
    }
    r = requests.post(f"{BASE_URL}/posts", headers=HEADERS, json=payload, timeout=60)
    return r.status_code in (200, 201), r.json() if r.text else {}, r.status_code


def to_utc_iso(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    dt_utc = dt + timedelta(hours=4)  # EDT in June = UTC-4
    return dt_utc.strftime("%Y-%m-%dT%H:%M:00.000Z")


def parse_drafts_queue(drafts_path: Path) -> list[dict]:
    """Parse the drafts-{date}.mdl file. Format:
       post_id | pillar | channel | date | time | compliance | content | image_paths
    Lines starting with # are metadata/headers. Image paths are pipe-separated
    AFTER the content field — there can be many of them for carousels."""
    posts = []
    with open(drafts_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line == "---":
                continue
            parts = [p.strip() for p in line.split(" | ")]
            if len(parts) < 7:
                log(f"  SKIP malformed line: {line[:80]}")
                continue
            # Fields 0-5: post_id, pillar, channel, date, time, compliance
            # Field 6: content (may contain ' // ' but not ' | ')
            # Fields 7+: image paths (carousels have 9+ of these)
            post = {
                "post_id": parts[0],
                "pillar": parts[1],
                "channel": parts[2],
                "date": parts[3],
                "time": parts[4],
                "compliance": parts[5],
                "content": parts[6].replace(" // ", "\n"),
                "image_paths": [p for p in parts[7:] if p],
            }
            posts.append(post)
    return posts


def main():
    # §3d HALT HARD INTERLOCK — Co-CEO rule 2026-06-25
    # First action in main(): refuse to run if engine is HALTED.
    halt_rc = check_halt_precondition()
    if halt_rc != 0:
        sys.exit(halt_rc)

    parser = argparse.ArgumentParser(description="Dose of Proof queue → Postiz push")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Target date (default: today)")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually push")
    args = parser.parse_args()

    log("=" * 70)
    log(f"Dose of Proof — Queue Push")
    log(f"Date: {args.date}")
    log("=" * 70)

    drafts_path = QUEUE_DIR / f"drafts-{args.date}.mdl"
    if not drafts_path.exists():
        log(f"❌ No drafts file: {drafts_path}")
        return 1

    posts = parse_drafts_queue(drafts_path)
    log(f"Found {len(posts)} posts in queue")

    if args.dry_run:
        log("\n[dry-run] Would push:")
        for p in posts:
            log(f"  - {p['post_id']} | {p['channel']} | {p['date']} {p['time']} | imgs={len(p['image_paths'])}")
        return 0

    # Integrations
    integrations = list_integrations()
    integ_map = {i["identifier"]: i["id"] for i in integrations}

    # Upload images
    image_cache = {}
    for post in posts:
        for path in post["image_paths"]:
            if path in image_cache:
                continue
            if not os.path.exists(path):
                log(f"  ⚠️  Missing image: {path}")
                continue
            try:
                img_id, img_path = upload_image(path)
                image_cache[path] = (img_id, img_path)
                log(f"  ✅ Uploaded {os.path.basename(path)} → {img_path}")
            except Exception as e:
                log(f"  ❌ Upload failed: {path}: {e}")

    # Schedule posts
    success = 0
    errors = 0
    receipts = []
    for post in posts:
        channel = post["channel"]
        if channel not in integ_map:
            log(f"  ⏭  {post['post_id']} — channel {channel} not connected")
            continue
        integ_id = integ_map[channel]
        publish_date = to_utc_iso(post["date"], post["time"])
        images = []
        for path in post["image_paths"]:
            if path in image_cache:
                img_id, img_path = image_cache[path]
                images.append({"id": img_id, "path": img_path})

        try:
            ok, resp, status = schedule_post(integ_id, post["content"], publish_date, images, channel=channel)
            if ok:
                log(f"  ✅ {post['post_id']} | {channel} | {post['date']} {post['time']} ({len(images)} imgs)")
                success += 1
                receipts.append(f"{post['post_id']} | {channel} | {post['date']} {post['time']} | OK | postiz_id={resp.get('id', '?') if isinstance(resp, dict) else '?'}")
            else:
                log(f"  ❌ {post['post_id']} — HTTP {status}: {str(resp)[:200]}")
                errors += 1
                receipts.append(f"{post['post_id']} | {channel} | {post['date']} {post['time']} | FAIL | {status}")
        except Exception as e:
            log(f"  ❌ {post['post_id']} — {e}")
            errors += 1
            receipts.append(f"{post['post_id']} | {channel} | {post['date']} {post['time']} | ERROR | {e}")

    # Write receipts
    published_path = QUEUE_DIR / f"published-{args.date}.mdl"
    with open(published_path, "w") as f:
        f.write(f"# Dose of Proof — Push receipts for {args.date}\n")
        f.write(f"# Pushed {datetime.now().isoformat()} via dop_push.py\n\n")
        for line in receipts:
            f.write(line + "\n")
    log(f"\n📁 Receipts: {published_path}")

    log("\n" + "=" * 70)
    log(f"Pushed: {success} | Errors: {errors}")
    log("=" * 70)
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())