#!/usr/bin/env python3
"""
baseline_health_check.py — Run a baseline health check for the
Researcher and Verifier vault trees, then rewrite the health files.

Each check verifies the structural integrity of one agent's vault and
writes a structured pass/fail report to its `health/` file. The
report is what the Fleet Command HUD reads to render the badge.

Usage:
  python3 baseline_health_check.py            # both agents
  python3 baseline_health_check.py --agent researcher
  python3 baseline_health_check.py --agent verifier
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(os.environ.get(
    "VAULT_ROOT", "/Users/brassfieldventuresllc/MiniMax-Agent"
))


def _check_researcher() -> dict:
    """Run structural checks for the Researcher vault.

    Checks:
      - knowledge/claims.jsonl exists, non-empty, has real records
      - dossiers/ has at least 1 .md file
      - notes/operator-brief.md exists
      - AGENTS.md and SOUL.md exist
    """
    root = VAULT_ROOT / "03 Projects" / "Researcher"
    checks: list[dict] = []
    issues: list[str] = []

    # claims.jsonl
    claims = root / "knowledge" / "claims.jsonl"
    if claims.exists():
        try:
            lines = [l for l in claims.read_text(encoding="utf-8").splitlines() if l.strip()]
            real = [
                l for l in lines
                if not l.lstrip().startswith("{") is False
                and json.loads(l).get("id", "").startswith("clm-2026")
            ]
            count = len(real)
            checks.append({
                "name": "claims.jsonl present and non-empty",
                "status": "pass" if count > 0 else "fail",
                "detail": f"{count} claim records",
            })
            if count == 0:
                issues.append("claims.jsonl has no real claim records")
        except (OSError, json.JSONDecodeError) as e:
            checks.append({
                "name": "claims.jsonl present and non-empty",
                "status": "fail",
                "detail": f"parse error: {e}",
            })
            issues.append(f"claims.jsonl parse error: {e}")
    else:
        checks.append({
            "name": "claims.jsonl present and non-empty",
            "status": "fail",
            "detail": "file missing",
        })
        issues.append("claims.jsonl missing")

    # dossiers/
    dossiers = root / "dossiers"
    if dossiers.exists():
        md_count = sum(1 for f in dossiers.iterdir() if f.is_file() and f.suffix == ".md")
        checks.append({
            "name": "dossiers/ has at least 1 dossier",
            "status": "pass" if md_count >= 1 else "fail",
            "detail": f"{md_count} dossier files",
        })
        if md_count < 1:
            issues.append("no dossiers present")
    else:
        checks.append({"name": "dossiers/ has at least 1 dossier",
                       "status": "fail", "detail": "dir missing"})
        issues.append("dossiers/ missing")

    # operator-brief.md
    brief = root / "notes" / "operator-brief.md"
    checks.append({
        "name": "notes/operator-brief.md exists",
        "status": "pass" if brief.exists() else "fail",
        "detail": "present" if brief.exists() else "missing",
    })
    if not brief.exists():
        issues.append("operator-brief.md missing")

    # AGENTS.md and SOUL.md
    for f in ("AGENTS.md", "SOUL.md"):
        p = root / f
        checks.append({
            "name": f"{f} exists",
            "status": "pass" if p.exists() else "fail",
            "detail": "present" if p.exists() else "missing",
        })
        if not p.exists():
            issues.append(f"{f} missing")

    return {
        "agent": "Researcher",
        "verdict": "PASS" if not issues else "FAIL",
        "issues": issues,
        "checks": checks,
    }


def _check_verifier() -> dict:
    """Run structural checks for the Verifier vault.

    Checks:
      - knowledge/verdicts.jsonl exists, non-empty, has real records
      - dossiers/ has at least 1 .md file
      - context/audit-policy.md and context/audit-rubric.md exist
      - AGENTS.md and SOUL.md exist
    """
    root = VAULT_ROOT / "03 Projects" / "Verifier"
    checks: list[dict] = []
    issues: list[str] = []

    # verdicts.jsonl
    verdicts = root / "knowledge" / "verdicts.jsonl"
    if verdicts.exists():
        try:
            text = verdicts.read_text(encoding="utf-8")
            real = []
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    rid = rec.get("id", "")
                    if rid.startswith("vrd-") or rec.get("audit_log_id"):
                        real.append(rid)
                except json.JSONDecodeError:
                    continue
            count = len(real)
            checks.append({
                "name": "verdicts.jsonl present with audit records",
                "status": "pass" if count > 0 else "fail",
                "detail": f"{count} verdict records",
            })
            if count == 0:
                issues.append("verdicts.jsonl has no real verdict records")
        except OSError as e:
            checks.append({
                "name": "verdicts.jsonl present with audit records",
                "status": "fail",
                "detail": f"read error: {e}",
            })
            issues.append(f"verdicts.jsonl read error: {e}")
    else:
        checks.append({
            "name": "verdicts.jsonl present with audit records",
            "status": "fail",
            "detail": "file missing",
        })
        issues.append("verdicts.jsonl missing")

    # dossiers/
    dossiers = root / "dossiers"
    if dossiers.exists():
        md_count = sum(1 for f in dossiers.iterdir() if f.is_file() and f.suffix == ".md")
        checks.append({
            "name": "dossiers/ has at least 1 dossier",
            "status": "pass" if md_count >= 1 else "fail",
            "detail": f"{md_count} dossier files",
        })
        if md_count < 1:
            issues.append("no dossiers present")
    else:
        checks.append({"name": "dossiers/ has at least 1 dossier",
                       "status": "fail", "detail": "dir missing"})
        issues.append("dossiers/ missing")

    # context files
    for f in ("context/audit-policy.md", "context/audit-rubric.md"):
        p = root / f
        checks.append({
            "name": f"{f} exists",
            "status": "pass" if p.exists() else "fail",
            "detail": "present" if p.exists() else "missing",
        })
        if not p.exists():
            issues.append(f"{f} missing")

    # AGENTS.md and SOUL.md
    for f in ("AGENTS.md", "SOUL.md"):
        p = root / f
        checks.append({
            "name": f"{f} exists",
            "status": "pass" if p.exists() else "fail",
            "detail": "present" if p.exists() else "missing",
        })
        if not p.exists():
            issues.append(f"{f} missing")

    return {
        "agent": "Verifier",
        "verdict": "PASS" if not issues else "FAIL",
        "issues": issues,
        "checks": checks,
    }


def _write_health_file(agent_name: str, result: dict, health_path: Path) -> None:
    """Rewrite the agent's health file with the structured report."""
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    verdict = result["verdict"]
    issues = result["issues"]
    checks = result["checks"]

    lines: list[str] = []
    if agent_name == "Researcher":
        lines += [
            "# Latest Health Check",
            "",
            f"**{verdict}.**",
            "",
            f"*Last run: {ts} — baseline health check (manual).*",
            "",
            "## What this file checks",
            "",
        ]
    else:
        lines += [
            "# Health — Audit Vault",
            "",
            "> Structural integrity of the audit vault. Run on every AUDIT.",
            "",
            f"*Last run: {ts} — baseline health check (manual).*",
            "",
        ]

    lines += [
        "## Checks",
        "",
    ]
    for c in checks:
        marker = "✅" if c["status"] == "pass" else "❌"
        lines.append(f"- {marker} **{c['name']}** — {c['detail']}")
    lines.append("")

    if issues:
        lines += [
            "## Issues found",
            "",
        ]
        for issue in issues:
            lines.append(f"- {issue}")
        lines.append("")
    else:
        lines += [
            "## Issues found",
            "",
            "*None.*",
            "",
        ]

    lines += [
        "---",
        "",
        f"*Generated by `baseline_health_check.py` at {ts}.*",
    ]

    health_path.parent.mkdir(parents=True, exist_ok=True)
    health_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="baseline_health_check.py",
        description="Run baseline health check for Researcher/Verifier and rewrite health files",
    )
    ap.add_argument(
        "--agent", choices=["researcher", "verifier", "both"], default="both",
        help="Which agent to check (default: both)",
    )
    args = ap.parse_args()

    results = []
    if args.agent in ("researcher", "both"):
        r = _check_researcher()
        _write_health_file(
            "Researcher", r,
            VAULT_ROOT / "03 Projects" / "Researcher" / "health" / "latest-health-check.md",
        )
        results.append(r)
    if args.agent in ("verifier", "both"):
        r = _check_verifier()
        _write_health_file(
            "Verifier", r,
            VAULT_ROOT / "03 Projects" / "Verifier" / "health" / "audit-health.md",
        )
        results.append(r)

    for r in results:
        print(json.dumps(r, indent=2, ensure_ascii=False))
        print()
    return 0 if all(r["verdict"] == "PASS" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
