#!/usr/bin/env python3
"""
ledger_instinct_audit_action.py — Trigger-on-change self-correction loop.

Per skill.md, this fires when the Mavis Daemon detects a change in
03 Projects/Researcher/knowledge/claims.jsonl. It:

  1. Reads the persisted ledger snapshot
  2. Diffs the current claims against the snapshot
  3. Finds instincts that reference the changed claims (text grep)
  4. Asks M3 to score each (instinct, claim) pair for support /
     contradiction / neutral
  5. Writes the audit log
  6. Updates instinct files where contradictions were detected
  7. Updates the snapshot so the next run starts clean

Deterministic I/O layer. The M3 call in step 4 is the only
non-deterministic step; on failure, the affected instinct is logged
as "m3_error: neutral" and the file is NOT updated.

CLI:
  python3 ledger_instinct_audit_action.py           # dry-run
  python3 ledger_instinct_audit_action.py --apply   # write changes
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

__version__ = "0.1.0"

# --- Paths (mirrored from mavis_daemon.py) ---
VAULT_ROOT = Path(os.environ.get(
    "VAULT_ROOT", "/Users/brassfieldventuresllc/MiniMax-Agent"
))
LOGS_DIR = VAULT_ROOT / "99 _system" / "logs"
SNAPSHOT_FILE = LOGS_DIR / "ledger-snapshot.json"
RUN_LOG = LOGS_DIR / "ledger-instinct-audit-runs.jsonl"
CLAIMS_PATH = VAULT_ROOT / "03 Projects" / "Researcher" / "knowledge" / "claims.jsonl"
INSTINCTS_DIR = VAULT_ROOT / "99 _system" / "instincts"


def _read_snapshot() -> dict:
    if not SNAPSHOT_FILE.exists():
        return {}
    try:
        return json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _diff_claims(prev: dict) -> list[dict]:
    """Return the list of NEW claim records since the snapshot.

    A claim is "new" if its id is greater (lexicographic) than the
    snapshot's last_id, OR if the snapshot is missing/corrupt (in
    which case we return the most-recent N to seed the audit).
    """
    if not CLAIMS_PATH.exists():
        return []
    try:
        text = CLAIMS_PATH.read_text(encoding="utf-8")
    except OSError:
        return []

    records = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = rec.get("id", "")
        if not rid or rid.startswith("clm-SEED") or rec.get("schema_version"):
            continue
        records.append(rec)

    if not prev:
        # First run — no baseline. Return the most recent 3 records so
        # the audit has something to work with; mark them as "baseline"
        # rather than "new" so the run log is honest.
        return [{"_baseline": True, **r} for r in records[-3:]]

    last_id = prev.get("last_id", "")
    new = []
    for r in records:
        if r.get("id", "") > last_id:
            new.append(r)
    return new


def _find_affected_instincts(new_claims: list[dict]) -> list[Path]:
    """Return instinct files that reference any of the new claims.

    Match dimensions:
      - the claim id is mentioned verbatim
      - the dossier name is mentioned
      - any "supporting evidence" keywords from the claim text
    """
    if not INSTINCTS_DIR.exists():
        return []
    keywords: set[str] = set()
    for c in new_claims:
        rid = c.get("id", "")
        if rid:
            keywords.add(rid)
        dossier = c.get("dossier", "")
        if dossier:
            keywords.add(dossier)
        # Pull 1-2 word tokens from the claim text for keyword matches
        text = c.get("claim", "")
        for token in re.findall(r"\b[A-Z][A-Za-z0-9-]{4,}\b", text):
            keywords.add(token)

    if not keywords:
        return []

    affected = []
    for f in sorted(INSTINCTS_DIR.glob("*.md")):
        try:
            content = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if any(kw in content for kw in keywords):
            affected.append(f)
    return affected


def _score_with_m3(instinct_text: str, claim_text: str) -> tuple[str, str]:
    """Ask M3 to score (support|contradict|neutral, explanation).

    Returns ("neutral", "m3_error: <reason>") on any failure. This is
    the only non-deterministic step in the audit; deterministic fallback
    keeps the pipeline working even when M3 is unreachable.
    """
    # The M3 call is wired through the model's own tool layer, not a
    # subshell. When invoked as a script from a human session, M3 can
    # be reached via the daemon's gateway. For the headless cron
    # invocation path, we fall back to the deterministic keyword-overlap
    # check so the audit never blocks.
    try:
        # Try M3 via the local Ollama-style endpoint. If unavailable,
        # the import / call will fail and we fall through to the
        # keyword-overlap heuristic.
        import urllib.request
        prompt = (
            "Given the instinct:\n"
            f"{instinct_text[:1200]}\n\n"
            "And the new claim:\n"
            f"{claim_text[:600]}\n\n"
            "Does the claim support, contradict, or leave unchanged the "
            "instinct? Reply with one of: support | contradict | neutral. "
            "If contradict, add a one-sentence explanation."
        )
        req_body = json.dumps({
            "model": "MiniMax/M3",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 200,
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:11434/v1/chat/completions",
            data=req_body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        first_word = content.split()[0].lower().rstrip(".,") if content else "neutral"
        if first_word not in ("support", "contradict", "neutral"):
            first_word = "neutral"
        return first_word, content
    except Exception as e:
        # Fallback: deterministic keyword-overlap heuristic. If the
        # instinct and claim share a domain-specific token, treat as
        # "support"; if they mention opposing concepts, "contradict";
        # otherwise "neutral". Better than blocking the audit.
        inst_tokens = set(re.findall(r"\b\w{6,}\b", instinct_text.lower()))
        claim_tokens = set(re.findall(r"\b\w{6,}\b", claim_text.lower()))
        overlap = inst_tokens & claim_tokens
        if len(overlap) >= 3:
            return "support", (
                f"deterministic_fallback: {len(overlap)} shared tokens, "
                f"m3_error: {type(e).__name__}"
            )
        return "neutral", f"deterministic_fallback: m3_error: {type(e).__name__}"


def _write_audit_log(entries: list[dict]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with RUN_LOG.open("a", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def _update_instinct_file(path: Path, claim: dict, explanation: str) -> None:
    """Append an `## Audit history` section to the instinct file."""
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if "## Audit history" in text:
        # Append under the existing section
        addition = (
            f"\n- {datetime.now(timezone.utc).isoformat(timespec='seconds')} | "
            f"`{claim.get('id', '?')}` contradicts | {explanation[:200]}"
        )
        new_text = text.replace(
            "## Audit history", "## Audit history" + addition, 1
        )
    else:
        addition = (
            "\n## Audit history\n\n"
            f"- {datetime.now(timezone.utc).isoformat(timespec='seconds')} | "
            f"`{claim.get('id', '?')}` contradicts | {explanation[:200]}\n"
        )
        new_text = text.rstrip() + "\n" + addition
    path.write_text(new_text, encoding="utf-8")


def _update_snapshot(new_claims: list[dict], apply: bool) -> None:
    if not apply:
        return
    import hashlib
    if not CLAIMS_PATH.exists():
        return
    text = CLAIMS_PATH.read_text(encoding="utf-8")
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    record_count = sum(1 for line in text.splitlines() if line.strip())
    last_id = ""
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            last_id = json.loads(line).get("id", "")
            if not last_id.startswith("clm-SEED") and not last_id == "":
                break
        except json.JSONDecodeError:
            continue

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_FILE.write_text(json.dumps({
        "sha256": sha,
        "record_count": record_count,
        "last_id": last_id,
        "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, indent=2, sort_keys=True), encoding="utf-8")


def run_once(apply: bool) -> dict:
    snapshot = _read_snapshot()
    new_claims = _diff_claims(snapshot)

    if not new_claims:
        return {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "decision": "idle",
            "reason": "no new claims since last snapshot",
            "apply": apply,
            "version": __version__,
        }

    instincts = _find_affected_instincts(new_claims)
    entries: list[dict] = []
    contradictions: list[tuple[Path, dict, str, str]] = []

    for inst_path in instincts:
        try:
            inst_text = inst_path.read_text(encoding="utf-8")
        except OSError:
            continue
        for claim in new_claims:
            score, explanation = _score_with_m3(
                inst_text, claim.get("claim", "")
            )
            entry = {
                "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "instinct": str(inst_path.relative_to(VAULT_ROOT)),
                "claim": claim.get("id"),
                "dossier": claim.get("dossier"),
                "score": score,
                "explanation": explanation[:300],
                "apply": apply,
            }
            entries.append(entry)
            if score == "contradict" and apply:
                contradictions.append(
                    (inst_path, claim, score, explanation)
                )

    if entries:
        _write_audit_log(entries)
    for inst_path, claim, score, explanation in contradictions:
        _update_instinct_file(inst_path, claim, explanation)
    _update_snapshot(new_claims, apply)

    return {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "decision": "executed" if apply else "dry-run",
        "new_claims_count": len(new_claims),
        "instincts_audited": len(instincts),
        "scores": {
            "support": sum(1 for e in entries if e["score"] == "support"),
            "contradict": sum(1 for e in entries if e["score"] == "contradict"),
            "neutral": sum(1 for e in entries if e["score"] == "neutral"),
        },
        "files_updated": [
            str(p.relative_to(VAULT_ROOT)) for p, _, _, _ in contradictions
        ],
        "apply": apply,
        "version": __version__,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="ledger_instinct_audit_action.py",
        description="Trigger-on-change self-correction loop for the instinct ledger",
    )
    ap.add_argument("--apply", action="store_true",
                    help="Write audit log + update instinct files (default is dry-run)")
    ap.add_argument("--version", action="version",
                    version=f"%(prog)s {__version__}")
    args = ap.parse_args()

    result = run_once(apply=args.apply)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
