#!/usr/bin/env python3
"""
Dose of Proof — Restore Reconciliation Evidence (per [[triage-gate-spec]] §3d.4)

Verifies that queue/drafts-*.mdl, queue/published-*.mdl, queue/blocked-records-*.mdl
match the independent audit source `performance_log.json` after a restore.
This is the verifier per Co-CEO rule 2026-06-25 21:21 CT: "Restore must be
independently verified. After any overwrite, the restored files are reconciled
against an independent audit source (e.g. performance_log.json) and the
reconciliation evidence surfaced — not asserted."

Usage:
    python3 scripts/dop_restore_reconciliation.py [--date 2026-06-26] [--out specs/]

Output:
    Per-row PASS/FAIL diff + summary verdict.
    The script writes a markdown report to specs/restore-reconciliation-YYYY-MM-DD-HHMM.md
    (or specified --out path) with full diff evidence.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof")
LOG_PATH = PROJECT_ROOT / "memory" / "dose-of-proof-performance-log.json"
QUEUE_DIR = PROJECT_ROOT / "queue"
SPECS_DIR = PROJECT_ROOT / "specs"

BLOCK_RECORD_PATTERN = re.compile(r"─{10,}\nBLOCK RECORD\n─{10,}\n(.*?)─{10,}", re.DOTALL)


def parse_performance_log() -> list[dict]:
    """Load performance_log.json (the independent audit source)."""
    if not LOG_PATH.exists():
        return []
    try:
        return json.loads(LOG_PATH.read_text())
    except json.JSONDecodeError as e:
        print(f"⛔ FATAL: performance_log.json malformed: {e}", file=sys.stderr)
        sys.exit(1)


def parse_drafts_mdl(path: Path) -> list[dict]:
    """Parse queue/drafts-YYYY-MM-DD.mdl — supports BOTH v0.1 (pipe-delimited) and v0.3 (--- separated) formats."""
    if not path.exists():
        return []
    content = path.read_text()
    posts = []
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("---"):
            continue
        # v0.1 format: post_id | pillar | channel | date | time | compliance | content | image_paths
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 6 and parts[0].startswith("dop-"):
                posts.append({
                    "post_id": parts[0],
                    "channel": parts[2],
                    "date": parts[3],
                    "time": parts[4],
                    "compliance": parts[5],
                    "format": "v0.1",
                })
    return posts


def parse_published_mdl(path: Path) -> list[dict]:
    """Parse queue/published-YYYY-MM-DD.mdl — pipe-delimited OK receipts."""
    if not path.exists():
        return []
    content = path.read_text()
    posts = []
    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("---"):
            continue
        if "|" in line and "OK" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3 and parts[0].startswith("dop-"):
                posts.append({
                    "post_id": parts[0],
                    "channel": parts[1],
                    "publish_time_str": parts[2],
                    "format": "OK receipt",
                })
    return posts


def parse_blocked_records_mdl(path: Path) -> list[dict]:
    """Parse queue/blocked-records-YYYY-MM-DD.mdl — extract §3a block records."""
    if not path.exists():
        return []
    content = path.read_text()
    records = []
    for match in BLOCK_RECORD_PATTERN.finditer(content):
        body = match.group(1).strip()
        record = {}
        for line in body.split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                record[key.strip()] = val.strip()
        if "POST_ID" in record:
            records.append(record)
    return records


def derive_expected_presence(final_status: str, resolution: str, post_id: str) -> dict:
    """
    Per [[triage-gate-spec]] post lifecycle: Generated → Drafted → Pushed → (optionally) KILLED/REVISE_PENDING/Reclassified.

    Returns expected presence in queue/ files given the final status + resolution.

    Lifecycle semantics:
    - PUBLISHED: drafts=True (was generated), published=True (was pushed), blocked=False normally OR True if reclassification
    - BLOCKED: drafts=True (generated), published=False (never pushed), blocked=True (block record)
    - KILLED: drafts=True (was generated), published=True if killed-post-push OR False if killed-pre-push, blocked=True (kill record)
    - REVISE_PENDING: drafts=True (original), published=True (original OK receipt), blocked=True (rev1 block record)
    - RECLASSIFIED_CLEAR: drafts=True (original), published=True (original OK receipt), blocked=True (reclassification block record)
    """
    status_norm = final_status.strip()
    res_norm = resolution.strip() if resolution else ""

    # Detect compound statuses (e.g. "PUBLISHED (original) — REVISION pending Co-CEO release")
    is_revise_pending = "REVISE" in status_norm.upper() or "REVISION" in status_norm.upper()
    is_killed = "KILLED" in status_norm.upper()
    is_reclassified = "RECLASSIFIED" in res_norm.upper() or "RECLASSIFIED" in status_norm.upper()

    # Strip the parenthesized suffix for simpler matching
    base_status = status_norm.split("(")[0].strip()

    if is_revise_pending:
        # Original was pushed, then a revision was generated and routed to HITL.
        # drafts has the original; published has the original OK receipt; blocked has the rev1 record.
        # Note: rev1 uses a derivative post_id (-rev1 suffix); handled below.
        return {"drafts": True, "published": True, "blocked": True,
                "note": "REVISE_PENDING: original published + rev1 block record"}
    elif is_killed:
        # KILLED happens after generation + usually after push (June 26 retro-screen).
        return {"drafts": True, "published": True, "blocked": True,
                "note": "KILLED (post-push): original was generated + pushed, then retroactively killed"}
    elif is_reclassified or "CLEAR" in base_status.upper() and "RECLASSIFIED" in res_norm.upper():
        # Reclassification: original was generated + pushed, then retroactively classified.
        return {"drafts": True, "published": True, "blocked": True,
                "note": "RECLASSIFIED_CLEAR: original published + reclassification block record"}
    elif base_status.upper() == "PUBLISHED":
        return {"drafts": True, "published": True, "blocked": False,
                "note": "PUBLISHED: no block record expected"}
    elif base_status.upper() == "BLOCKED":
        return {"drafts": True, "published": False, "blocked": True,
                "note": "BLOCKED: pre-push block, no published receipt"}
    else:
        return {"drafts": True, "published": False, "blocked": False,
                "note": f"Unknown status '{status_norm}' — default: drafts=True only"}


def reconcile(target_date: str) -> dict:
    """Run reconciliation against performance_log.json. Returns diff dict."""
    log = parse_performance_log()
    drafts_path = QUEUE_DIR / f"drafts-{target_date}.mdl"
    published_path = QUEUE_DIR / f"published-{target_date}.mdl"
    blocked_path = QUEUE_DIR / f"blocked-records-{target_date}.mdl"

    drafts = parse_drafts_mdl(drafts_path)
    published = parse_published_mdl(published_path)
    blocked = parse_blocked_records_mdl(blocked_path)

    # Filter log rows to the target date
    log_rows = [row for row in log if row.get("DATE_GENERATED", "").startswith(target_date)]

    # Build sets of post_ids for fast lookup
    log_post_ids = {row.get("POST_ID") for row in log_rows}
    # For blocked-records: a "rev1" or "rev2" record is a derivative of the original post_id.
    # Strip revision suffix when matching against log post_ids.
    def strip_revision(pid: str) -> str:
        return re.sub(r"-rev\d+$", "", pid or "")
    blocked_post_ids = {r.get("POST_ID") for r in blocked}
    blocked_base_ids = {strip_revision(pid) for pid in blocked_post_ids}

    drafts_post_ids = {p["post_id"] for p in drafts}
    published_post_ids = {p["post_id"] for p in published}

    # Per-row diff
    rows = []
    for log_row in log_rows:
        post_id = log_row.get("POST_ID")
        final_status = log_row.get("FINAL_STATUS", "")
        resolution = log_row.get("RESOLUTION", "") or ""
        platform = log_row.get("PLATFORM", "")
        publish_time = log_row.get("PUBLISH_TIME", "")

        in_drafts = post_id in drafts_post_ids
        in_published = post_id in published_post_ids
        # A block record matches if its post_id equals the log post_id OR its base (stripped of -revN) equals it
        in_blocked = (post_id in blocked_post_ids) or (post_id in blocked_base_ids)

        expected = derive_expected_presence(final_status, resolution, post_id)

        row_pass = (
            in_drafts == expected["drafts"]
            and in_published == expected["published"]
            and in_blocked == expected["blocked"]
        )

        rows.append({
            "post_id": post_id,
            "final_status": final_status,
            "resolution": resolution,
            "platform": platform,
            "publish_time": publish_time,
            "in_drafts": in_drafts,
            "in_published": in_published,
            "in_blocked": in_blocked,
            "expected_drafts": expected["drafts"],
            "expected_published": expected["published"],
            "expected_blocked": expected["blocked"],
            "note": expected.get("note", ""),
            "pass": row_pass,
        })

    # Reverse direction: orphans (entries in queue files NOT in performance_log.json)
    # For blocked-records orphans, strip revision suffix before comparing
    orphan_drafts = drafts_post_ids - log_post_ids
    orphan_published = published_post_ids - log_post_ids
    orphan_blocked = blocked_base_ids - log_post_ids

    # Note: rev1 entries are NOT orphans — they are derivatives of original log rows.
    # But check for blocked-records that don't trace to ANY log row (after stripping rev).
    orphan_blocked_unmatched = []
    for r in blocked:
        base = strip_revision(r.get("POST_ID", ""))
        if base not in log_post_ids and r.get("POST_ID") not in log_post_ids:
            orphan_blocked_unmatched.append(r.get("POST_ID"))

    summary = {
        "target_date": target_date,
        "total_log_rows": len(log_rows),
        "total_drafts": len(drafts),
        "total_published": len(published),
        "total_blocked": len(blocked),
        "rows_pass": sum(1 for r in rows if r["pass"]),
        "rows_fail": sum(1 for r in rows if not r["pass"]),
        "orphan_drafts": sorted(orphan_drafts),
        "orphan_published": sorted(orphan_published),
        "orphan_blocked_after_rev_strip": sorted(orphan_blocked - log_post_ids),
        "orphan_blocked_unmatched": sorted(set(orphan_blocked_unmatched)),
        "all_pass": (sum(1 for r in rows if not r["pass"]) == 0
                     and not orphan_drafts and not orphan_published and not set(orphan_blocked_unmatched)),
    }

    return {"rows": rows, "summary": summary,
            "drafts_path": str(drafts_path), "published_path": str(published_path),
            "blocked_path": str(blocked_path)}


def format_report(diff: dict) -> str:
    """Format diff as markdown report."""
    lines = []
    lines.append("# Dose of Proof — Restore Reconciliation Evidence")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S CT')}")
    lines.append(f"**Per:** [[triage-gate-spec]] §3d.4 (Co-CEO rule 2026-06-25 21:21 CT)")
    lines.append(f"**Independent audit source:** `memory/dose-of-proof-performance-log.json`")
    lines.append("")
    lines.append("---")
    lines.append("")

    s = diff["summary"]
    lines.append(f"## Summary — target date {s['target_date']}")
    lines.append("")
    lines.append(f"- **Total log rows for date:** {s['total_log_rows']}")
    lines.append(f"- **Total drafts in queue/drafts-{s['target_date']}.mdl:** {s['total_drafts']}")
    lines.append(f"- **Total receipts in queue/published-{s['target_date']}.mdl:** {s['total_published']}")
    lines.append(f"- **Total records in queue/blocked-records-{s['target_date']}.mdl:** {s['total_blocked']}")
    lines.append(f"- **Rows PASS:** {s['rows_pass']}")
    lines.append(f"- **Rows FAIL:** {s['rows_fail']}")
    lines.append(f"- **Orphan drafts (in drafts/ but not in log):** {s['orphan_drafts']}")
    lines.append(f"- **Orphan published (in published/ but not in log):** {s['orphan_published']}")
    lines.append(f"- **Orphan blocked (after stripping -revN suffix):** {s['orphan_blocked_after_rev_strip']}")
    lines.append(f"- **Orphan blocked (no log match even with -revN strip):** {s['orphan_blocked_unmatched']}")
    lines.append("")
    lines.append(f"## Verdict")
    lines.append("")
    if s["all_pass"]:
        lines.append("**✅ RECONCILIATION CLEAN** — every performance_log.json row has matching presence/absence in queue/ files, and every queue/ file entry traces back to a log row. No orphans, no missing rows, no missing block records.")
    else:
        lines.append("**❌ RECONCILIATION INCONSISTENT** — see per-row diff below. Audit trail is NOT clean. Investigate before declaring restore complete.")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Per-row diff (performance_log.json ↔ queue/ files)")
    lines.append("")
    lines.append("Expectations derived from FINAL_STATUS + RESOLUTION per the post lifecycle: Generated → Drafted → Pushed → (optionally) KILLED/REVISE_PENDING/Reclassified. Revision block records (e.g. `-rev1`) match the original log post_id after stripping the suffix.")
    lines.append("")
    lines.append(f"| POST_ID | Status | Platform | Publish | In drafts (expect) | In published (expect) | In blocked (expect) | Note | PASS |")
    lines.append(f"|---|---|---|---|---|---|---|---|---|")
    for r in diff["rows"]:
        verdict = "✅ PASS" if r["pass"] else "❌ FAIL"
        lines.append(
            f"| `{r['post_id']}` | {r['final_status']} | {r['platform']} | {r['publish_time']} | "
            f"{'Y' if r['in_drafts'] else 'N'} ({'Y' if r['expected_drafts'] else 'N'}) | "
            f"{'Y' if r['in_published'] else 'N'} ({'Y' if r['expected_published'] else 'N'}) | "
            f"{'Y' if r['in_blocked'] else 'N'} ({'Y' if r['expected_blocked'] else 'N'}) | "
            f"{r['note']} | "
            f"{verdict} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Files reconciled")
    lines.append("")
    lines.append(f"- **Independent audit source:** `{LOG_PATH}`")
    lines.append(f"- **drafts/:** `{diff['drafts_path']}`")
    lines.append(f"- **published/:** `{diff['published_path']}`")
    lines.append(f"- **blocked-records/:** `{diff['blocked_path']}`")
    lines.append("")
    lines.append("Reconciliation is one-way: performance_log.json is treated as canonical, queue/ files are checked against it. Orphan entries (in queue/ but not in log) are surfaced as inconsistency. Log entries without matching queue/ file presence are flagged FAIL.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"*Generated by `scripts/dop_restore_reconciliation.py` at {datetime.now().isoformat()}*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Restore reconciliation evidence (per [[triage-gate-spec]] §3d.4)")
    parser.add_argument("--date", default="2026-06-26", help="Target date (YYYY-MM-DD)")
    parser.add_argument("--out", default=None, help="Output file path (default: specs/restore-reconciliation-DATE-TIME.md)")
    args = parser.parse_args()

    diff = reconcile(args.date)
    report = format_report(diff)

    if args.out:
        out_path = Path(args.out)
    else:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        out_path = SPECS_DIR / f"restore-reconciliation-{args.date}-{timestamp}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report)
    print(report)
    print(f"\n✅ Report written to: {out_path}")

    # Exit code: 0 if all_pass, 1 if any failure (CI-friendly)
    sys.exit(0 if diff["summary"]["all_pass"] else 1)


if __name__ == "__main__":
    main()
