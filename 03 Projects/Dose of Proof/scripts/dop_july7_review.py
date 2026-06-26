#!/usr/bin/env python3
"""
Dose of Proof — July 7 PCAC Review Script

Per triage-gate-spec §6 + V10 verification: produces the data read for the
July 7 Co-CEO + Mavis review. Reads performance_log.json and computes:
- Gate integrity rate (target: 1.0)
- Hook-family bias report (8 §5 families, SENSITIVE rate + engagement)
- Block rate / Kill rate / Upgrade rate per §6 metrics
- D1 + D7 engagement summaries
- Recommendations: which hook families to lean into for post-hearing pivot

Output: prints to stdout AND writes
  03 Projects/Dose of Proof/stores/feedback/2026-07-07-pre-review.md

Usage:
    python3 dop_july7_review.py
    python3 dop_july7_review.py --dry-run  # print only, don't write
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof")
LOG_PATH = PROJECT_ROOT / "memory" / "dose-of-proof-performance-log.json"
OUTPUT_PATH = PROJECT_ROOT / "stores" / "feedback" / "2026-07-07-pre-review.md"

# §5 hook families
HOOK_FAMILIES = [
    "regulatory-reality", "biomarker-education", "terrain-mechanics",
    "citizen-science", "literature-map", "reconstitution-math",
    "telehealth-routing", "community-proof",
]


def read_log():
    """Read performance_log.json. Returns empty list if missing/empty."""
    if not LOG_PATH.exists():
        return []
    try:
        return json.loads(LOG_PATH.read_text())
    except json.JSONDecodeError:
        return []


def compute_metrics(log: list) -> dict:
    """Compute §6 metrics from the log."""
    metrics = {
        "total_posts": len(log),
        "by_status": defaultdict(int),
        "by_hook_family": defaultdict(lambda: {"total": 0, "sensitive": 0, "published": 0, "blocked": 0, "killed": 0, "engagement_d1_total": 0, "engagement_d7_total": 0}),
        "gate_failures": 0,
        "upgraded_count": 0,
        "block_count": 0,
        "kill_count": 0,
        "resolved_count": 0,
        "engagement_d1_captured": 0,
        "engagement_d7_captured": 0,
        "engagement_d1_pending": 0,
        "engagement_d7_pending": 0,
    }

    for row in log:
        status = row.get("FINAL_STATUS", "UNKNOWN")
        hook_family = row.get("HOOK_FAMILY", "unknown")
        generator_class = row.get("GENERATOR_CLASS", "CLEAR")
        mavis_class = row.get("MAVIS_CLASS", "CLEAR")

        metrics["by_status"][status] += 1
        metrics["by_hook_family"][hook_family]["total"] += 1

        if generator_class == "SENSITIVE":
            metrics["by_hook_family"][hook_family]["sensitive"] += 1

        if status == "PUBLISHED":
            metrics["by_hook_family"][hook_family]["published"] += 1
        elif status == "BLOCKED":
            metrics["by_hook_family"][hook_family]["blocked"] += 1
            metrics["block_count"] += 1
        elif status == "KILLED":
            metrics["by_hook_family"][hook_family]["killed"] += 1
            metrics["kill_count"] += 1

        # Gate integrity: published posts should never have been SENSITIVE
        if status == "PUBLISHED" and generator_class == "SENSITIVE":
            metrics["gate_failures"] += 1

        # Mavis upgrade rate
        if mavis_class == "UPGRADED":
            metrics["upgraded_count"] += 1

        # Engagement capture
        d1 = row.get("ENGAGEMENT_D1", 0)
        d7 = row.get("ENGAGEMENT_D7", 0)
        if d1 > 0:
            metrics["by_hook_family"][hook_family]["engagement_d1_total"] += d1
            metrics["engagement_d1_captured"] += 1
        elif status == "PUBLISHED":
            metrics["engagement_d1_pending"] += 1
        if d7 > 0:
            metrics["by_hook_family"][hook_family]["engagement_d7_total"] += d7
            metrics["engagement_d7_captured"] += 1
        elif status == "PUBLISHED":
            metrics["engagement_d7_pending"] += 1

    # Gate integrity rate
    published_count = metrics["by_status"].get("PUBLISHED", 0)
    if published_count > 0:
        metrics["integrity_rate"] = (published_count - metrics["gate_failures"]) / published_count
    else:
        metrics["integrity_rate"] = 1.0  # No publishes = vacuously clean

    # Block rate
    if metrics["total_posts"] > 0:
        metrics["block_rate"] = metrics["block_count"] / metrics["total_posts"]
        metrics["kill_rate"] = metrics["kill_count"] / metrics["block_count"] if metrics["block_count"] > 0 else 0
    else:
        metrics["block_rate"] = 0
        metrics["kill_rate"] = 0

    # Upgrade rate (out of CLEAR generator outputs)
    clear_outputs = metrics["total_posts"] - sum(
        metrics["by_hook_family"][hf]["sensitive"] for hf in HOOK_FAMILIES
    )
    if clear_outputs > 0:
        metrics["upgrade_rate"] = metrics["upgraded_count"] / clear_outputs
    else:
        metrics["upgrade_rate"] = 0

    return metrics


def format_report(metrics: dict) -> str:
    """Format metrics as a markdown report."""
    lines = []
    lines.append("# July 7 PCAC Review — Pre-Meeting Data Read")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M CT')}")
    lines.append(f"**Source:** `03 Projects/Dose of Proof/memory/dose-of-proof-performance-log.json`")
    lines.append(f"**Per:** triage-gate-spec §6 + V10 verification")
    lines.append("")

    lines.append("## Gate Integrity (North-Star Metric)")
    lines.append("")
    lines.append(f"- **Integrity rate:** {metrics['integrity_rate']:.4f} (target: 1.0)")
    lines.append(f"- **Gate failures:** {metrics['gate_failures']} (target: 0)")
    lines.append(f"- **Total posts:** {metrics['total_posts']}")
    lines.append(f"- **By status:** {dict(metrics['by_status'])}")
    if metrics["gate_failures"] > 0:
        lines.append("")
        lines.append("> ⚠️ **GATE FAILURE DETECTED** — spec §6 mandates immediate engine halt.")
    lines.append("")

    lines.append("## Hook-Family Bias Report")
    lines.append("")
    lines.append(f"| Hook Family | Total | Sensitive | Published | Blocked | Killed | D1 Eng | D7 Eng |")
    lines.append(f"|-------------|-------|-----------|-----------|---------|--------|--------|--------|")
    for hf in HOOK_FAMILIES:
        if hf in metrics["by_hook_family"]:
            m = metrics["by_hook_family"][hf]
            lines.append(
                f"| {hf} | {m['total']} | {m['sensitive']} | {m['published']} | "
                f"{m['blocked']} | {m['killed']} | {m['engagement_d1_total']} | {m['engagement_d7_total']} |"
            )
    lines.append("")

    lines.append("## §6 Metrics Table")
    lines.append("")
    lines.append(f"| Metric | Value | Red Line |")
    lines.append(f"|--------|-------|----------|")
    lines.append(f"| Integrity rate | {metrics['integrity_rate']:.4f} | < 1.0 = halt engine |")
    lines.append(f"| Upgrade rate | {metrics['upgrade_rate']:.4f} | Rising = generator needs calibration |")
    lines.append(f"| Block rate | {metrics['block_rate']:.4f} | Baseline TBD in first week |")
    lines.append(f"| Kill rate | {metrics['kill_rate']:.4f} | High = generator calibration problem |")
    lines.append("")

    lines.append("## Engagement Capture Status")
    lines.append("")
    lines.append(f"- **D1 captured:** {metrics['engagement_d1_captured']} posts")
    lines.append(f"- **D1 pending:** {metrics['engagement_d1_pending']} posts (T+24h window not yet reached OR manual capture)")
    lines.append(f"- **D7 captured:** {metrics['engagement_d7_captured']} posts")
    lines.append(f"- **D7 pending:** {metrics['engagement_d7_pending']} posts (T+168h window not yet reached OR manual capture)")
    lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    # Heuristic recommendations
    if metrics["integrity_rate"] < 1.0:
        lines.append("- **CRITICAL:** Gate integrity < 1.0 — engine halt until root cause identified.")
    elif metrics["integrity_rate"] == 1.0:
        lines.append("- **GATE HELD:** Zero integrity failures in sprint window. Engine can resume normal cadence.")

    if metrics["block_rate"] > 0.3:
        lines.append("- **HIGH BLOCK RATE:** >30% of generated posts are SENSITIVE. Review generator prompt for over-trigger.")
    elif metrics["block_rate"] < 0.05:
        lines.append("- **LOW BLOCK RATE:** <5% SENSITIVE — possible under-flagging. Consider tightening S1-S4 patterns.")

    if metrics["upgrade_rate"] > 0.1:
        lines.append("- **HIGH UPGRADE RATE:** Mavis upgrading >10% of CLEAR outputs. Generator prompt needs calibration.")

    if metrics["engagement_d7_pending"] > 0 and metrics["total_posts"] > 5:
        lines.append(f"- **ENGAGEMENT CAPTURE GAP:** {metrics['engagement_d7_pending']} posts still pending D7 capture. Ensure manual Postiz UI pulls are running.")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*This report is the pre-meeting data read for the July 7 Co-CEO + Mavis review. Agenda items follow in `03 Projects/Dose of Proof/calendar/2026-07-07-review.md`.*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Dose of Proof July 7 review data read")
    parser.add_argument("--dry-run", action="store_true", help="Print only, don't write to disk")
    args = parser.parse_args()

    print("=" * 70)
    print(f"Dose of Proof — July 7 PCAC Review Data Read")
    print(f"Source: {LOG_PATH}")
    print("=" * 70)

    log = read_log()
    if not log:
        print(f"\n⚠️  No data in performance_log yet. Run `dop_performance_logger.py --action ingest` first.")
        sys.exit(1)

    metrics = compute_metrics(log)
    report = format_report(metrics)
    print(report)

    if not args.dry_run:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(report)
        print(f"\n✅ Report written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()