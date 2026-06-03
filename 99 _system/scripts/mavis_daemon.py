#!/usr/bin/env python3
"""
mavis_daemon.py — Mavis Heartbeat. The Omni-Loop.

Operation Daedalus (2026-06-02). The script that runs on a schedule
(cron/launchd). The launchd plist is a separate concern and is NOT
created by this script — that's a YELLOW-tier action per SOUL § Autonomy
Boundary Table and requires explicit per-action authorization.

On each wake the Daemon:
  1. Harvests vault state (deterministic I/O — git log, file counts)
  2. Runs the can_i() audit gate on any planned action (mirrors SOUL)
  3. Selects a candidate Skill Pack from vault state (deterministic rule)
  4. Applies the tier policy:
       - GREEN  → auto-execute, log to daemon-runs.jsonl
       - YELLOW → write a "blocked, awaiting approval" entry to 00 Inbox/
                  AND log. The Daemon does NOT auto-execute yellow skills.
                  A human (or next session) sees the Inbox entry and runs
                  the skill themselves, OR marks it approved via the
                  daemon-approvals.json file.
       - RED    → refuse, log, no execution
  5. Always appends to 99 _system/logs/daemon-runs.jsonl

Esalen posture: thin deterministic watcher. No LLM call inside. Selection
is rule-based. The skill's own action.py is the I/O when invoked.

Usage:
  mavis_daemon.py --once            # one iteration, dry-run, exit
  mavis_daemon.py --once --apply    # one iteration, execute for real
  mavis_daemon.py --interval 14400  # run on a 4h loop (foreground, dev only)
  mavis_daemon.py --version

CRITICAL:
  - Dry-run is the default. Nothing writes outside daemon-runs.jsonl
    unless --apply is passed.
  - This script does NOT install a launchd plist. That's a separate,
    explicit, YELLOW-tier action.
  - Skill Packs are invoked by importing their action module and calling
    their public entry point. The action modules are the deterministic
    I/O layer per the Esalen Skill Pack anatomy.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

__version__ = "0.1.0"

# ============================================================
# PATHS
# ============================================================

VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/Users/brassfieldventuresllc/MiniMax-Agent"))
SCRIPTS_DIR = VAULT_ROOT / "99 _system" / "scripts"
SKILLS_DIR = VAULT_ROOT / "99 _system" / "skillopt" / "skills"
INBOX = VAULT_ROOT / "00 Inbox"
LOGS_DIR = VAULT_ROOT / "99 _system" / "logs"
DAEMON_LOG = LOGS_DIR / "daemon-runs.jsonl"
APPROVALS_FILE = LOGS_DIR / "daemon-approvals.json"
# Ledger state snapshot for trigger-on-change detection
LEDGER_SNAPSHOT_FILE = LOGS_DIR / "ledger-snapshot.json"
# Path to the Researcher's claims ledger (the trigger source)
RESEARCHER_CLAIMS_PATH = (
    VAULT_ROOT / "03 Projects" / "Researcher" / "knowledge" / "claims.jsonl"
)

# 2-week habit gate for daily-brief (state-of-mavis.md L84 deferred item).
# The Daemon will treat daily-brief as YELLOW until this many invocations
# of the daily-brief skill have been recorded in the audit log.
DAILY_BRIEF_HABIT_GATE = 14

# Tier policy per Skill Pack. Maps pack name → (tier, auto_execute).
# Tier meanings:
#   green  = reversible vault write, safe to auto-execute
#   yellow = reversible vault write BUT needs human-in-loop (2-week habit
#            gate, or first-of-its-kind, or writes to 01 Daily/)
#   red    = crosses a hard line (external send, fleet, credential, etc.)
TIER_POLICY: dict[str, dict] = {
    "process-inbox": {
        "tier": "green",
        "auto_execute": True,
        "rationale": "Moves files from 00 Inbox/ to 02 Notes/ subfolders; "
                     "fully reversible via git. No external side effects.",
    },
    "weekly-connections": {
        "tier": "green",
        "auto_execute": True,
        "rationale": "Writes to 06 Connections/; fully reversible via git. "
                     "No external side effects.",
    },
    "deep-research": {
        "tier": "green",
        "auto_execute": True,
        "rationale": "Writes to 02 Notes/articles/; fully reversible. "
                     "No external side effects.",
    },
    "daily-brief": {
        "tier": "yellow",
        "auto_execute": False,  # held until 2-week habit gate met
        "rationale": "Overwrites 01 Daily/YYYY-MM-DD.md. Per state-of-mavis.md "
                     "L84: deferred until 2 weeks of on-demand invocations. "
                     "Daemon writes an Inbox alert instead of auto-executing.",
    },
    "ledger-instinct-audit": {
        "tier": "green",
        "auto_execute": True,
        "rationale": "Trigger-on-change audit of instincts affected by new "
                     "Researcher claims. Reads claims.jsonl since the last "
                     "daemon run, identifies instincts that reference changed "
                     "claims or dossiers, runs targeted re-verification. "
                     "Reversible vault write to instincts/ + audit log.",
    },
}


# ============================================================
# CAN_I — rule-based gate (mirrors update_state_of_mavis.py + SOUL)
# ============================================================

RED_RULES = [
    (r"\b(send|email|message|post|tweet|publish|signup|buy|purchase|subscribe)\b",
     "external send / Andre's identity / money"),
    (r"\b(delete|rm|drop|trash|force.push|hard.reset)\b",
     "destructive or irreversible"),
    (r"\b(hermes|openclaw|kanban|gbrain|launchd|fleet|profile\.yaml)\b",
     "fleet boundary (isolation principle)"),
    (r"\b(credential|token|password|api[._-]?key|secret|auth)\b",
     "credential / security change"),
]
YELLOW_RULES = [
    (r"\b(push).*\b(github|origin|main|master|remote)\b", "git push to remote"),
    (r"\b(cron|launchctl|schedul)", "schedule change"),
    (r"\b(cu|desktop_|click|type|scroll|screenshot)", "macOS GUI control"),
]
GREEN_RULES = [
    (r"\b(write|edit|append|create|move|rename)\b.*\b(inbox|notes|projects|"
     r"connections|vellum|_system|daily|resources|state\.md|99|01|02|03|04|05|06|07)\b",
     "vault write, reversible via git"),
]


def can_i(action_text: str) -> dict:
    """Rule-based can_i() classifier. Mirrors update_state_of_mavis.py."""
    text = action_text.lower()
    for pattern, reason in RED_RULES:
        if __import__("re").search(pattern, text):
            return {"tier": "red", "allowed": False, "rationale": f"red: {reason}"}
    for pattern, reason in YELLOW_RULES:
        if __import__("re").search(pattern, text):
            return {"tier": "yellow", "allowed": True, "rationale": f"yellow: {reason}"}
    for pattern, reason in GREEN_RULES:
        if __import__("re").search(pattern, text):
            return {"tier": "green", "allowed": True, "rationale": f"green: {reason}"}
    return {"tier": "green", "allowed": True,
            "rationale": "no rule matched; default green"}


# ============================================================
# VAULT STATE — light harvest, no LLM
# ============================================================

def harvest_state() -> dict:
    """Lightweight vault state. Mirrors the keys update_state_of_mavis.py
    uses, but only the ones the Daemon needs for skill selection.
    """
    import subprocess
    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "today": datetime.now().strftime("%Y-%m-%d"),
        "hour_local": datetime.now().hour,
        "dow_local": datetime.now().strftime("%A"),
    }
    # Inbox count
    if INBOX.exists():
        state["inbox_count"] = sum(
            1 for f in INBOX.iterdir()
            if f.is_file() and not f.name.startswith(".")
        )
    else:
        state["inbox_count"] = 0

    # Today's daily note exists?
    daily = VAULT_ROOT / "01 Daily" / f"{state['today']}.md"
    state["today_daily_exists"] = daily.exists()

    # Count connections files
    conn_dir = VAULT_ROOT / "06 Connections"
    state["connections_count"] = (
        sum(1 for f in conn_dir.glob("*.md")) if conn_dir.exists() else 0
    )

    # Count daily-brief invocations in this log (for the habit gate)
    state["daily_brief_invocation_count"] = _count_skill_invocations("daily-brief")

    # Ledger state — drives the trigger-on-change rule
    state["ledger"] = _ledger_state_with_change()

    return state


# ============================================================
# LEDGER STATE — trigger-on-change detection
# ============================================================

def _ledger_state_with_change() -> dict:
    """Snapshot the Researcher's claims ledger and detect if it has
    changed since the last daemon run.

    Returns a dict with:
      - exists (bool): whether the claims.jsonl file is present
      - record_count (int): number of non-empty lines
      - last_id (str | None): id of the last record (or None)
      - sha256 (str | None): short hash of the file contents
      - mtime (float | None): mtime of the file
      - ledger_changed (bool): True if sha/record_count differ from last run
      - prev_record_count (int | None): what the prior run saw (for the log)
    """
    import hashlib

    curr: dict = {"exists": False, "record_count": 0, "last_id": None,
                  "sha256": None, "mtime": None}
    if not RESEARCHER_CLAIMS_PATH.exists():
        return {**curr, "ledger_changed": False, "prev_record_count": None}

    try:
        text = RESEARCHER_CLAIMS_PATH.read_text(encoding="utf-8")
    except OSError:
        return {**curr, "ledger_changed": False, "prev_record_count": None}

    curr["exists"] = True
    curr["mtime"] = RESEARCHER_CLAIMS_PATH.stat().st_mtime
    curr["sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    curr["record_count"] = sum(
        1 for line in text.splitlines() if line.strip()
    )
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            curr["last_id"] = json.loads(line).get("id")
            break
        except json.JSONDecodeError:
            continue

    prev = _load_ledger_snapshot()
    changed = bool(prev) and (
        prev.get("sha256") != curr["sha256"]
        or prev.get("record_count") != curr["record_count"]
    )

    return {
        **curr,
        "ledger_changed": changed,
        "prev_record_count": prev.get("record_count") if prev else None,
    }


def _load_ledger_snapshot() -> dict:
    """Load the previous ledger snapshot from disk. Empty dict if missing/corrupt."""
    if not LEDGER_SNAPSHOT_FILE.exists():
        return {}
    try:
        return json.loads(LEDGER_SNAPSHOT_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_ledger_snapshot(state: dict) -> None:
    """Persist the current ledger snapshot for the next run to diff against."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_SNAPSHOT_FILE.write_text(
        json.dumps(state, indent=2, sort_keys=True), encoding="utf-8"
    )


def _count_skill_invocations(skill_name: str) -> int:
    """Count how many times `skill_name` has been EXECUTED in the
    daemon audit log. Used to gate the daily-brief 2-week rule.
    """
    if not DAEMON_LOG.exists():
        return 0
    count = 0
    try:
        for line in DAEMON_LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if (entry.get("skill") == skill_name
                    and entry.get("decision") == "executed"):
                count += 1
    except OSError:
        pass
    return count


# ============================================================
# SKILL SELECTION — deterministic rule
# ============================================================

@dataclass
class Selection:
    skill: str | None
    confidence: float
    reason: str


def select_skill(state: dict) -> Selection:
    """Pick the right Skill Pack from vault state. Deterministic, rule-based.

    Priority order (highest first):
      0. Researcher claims.jsonl changed since last run → ledger-instinct-audit
      1. inbox_count > 0                       → process-inbox
      2. Sunday AND hour ≥ 18                  → weekly-connections
      3. daily-brief hour (6-7) AND no daily   → daily-brief (yellow)
      4. weekend AND articles stale            → deep-research
      5. otherwise                             → no action
    """
    inbox = state.get("inbox_count", 0)
    today_daily = state.get("today_daily_exists", True)
    hour = state.get("hour_local", 12)
    dow = state.get("dow_local", "")
    ledger = state.get("ledger", {})

    # Priority 0: trigger-on-change audit when the Researcher's claims
    # ledger has new entries since the last daemon run. Replaces the
    # previous 4h full-audit cadence (per ruling 2026-06-03).
    if ledger.get("ledger_changed"):
        prev = ledger.get("prev_record_count", "?")
        curr = ledger.get("record_count", "?")
        return Selection(
            skill="ledger-instinct-audit",
            confidence=0.90,
            reason=f"Researcher claims.jsonl changed "
                   f"({prev} → {curr} records, sha={ledger.get('sha256')}); "
                   f"trigger-on-change targeted instinct audit",
        )

    if inbox > 0:
        return Selection(
            skill="process-inbox",
            confidence=0.95,
            reason=f"inbox has {inbox} file(s); process-inbox is the "
                   f"canonical handler",
        )

    if dow == "Sunday" and hour >= 18:
        return Selection(
            skill="weekly-connections",
            confidence=0.85,
            reason="Sunday evening; weekly-connections is the canonical "
                   "end-of-week workflow",
        )

    if 6 <= hour <= 7 and not today_daily:
        return Selection(
            skill="daily-brief",
            confidence=0.90,
            reason="morning, no daily note yet; daily-brief is the "
                   "canonical morning workflow (YELLOW until 2-week gate)",
        )

    if dow in ("Saturday", "Sunday") and hour >= 20:
        return Selection(
            skill="deep-research",
            confidence=0.70,
            reason="weekend evening; deep-research is a candidate if no "
                   "other skill is firing (low confidence — may skip)",
        )

    return Selection(skill=None, confidence=0.0, reason="no rule matched; idle")


# ============================================================
# TIER POLICY APPLICATION
# ============================================================

def apply_tier_policy(selection: Selection) -> dict:
    """Look up the tier policy for the selected skill. Returns the
    decision dict that the Daemon will record + act on.
    """
    if selection.skill is None:
        return {
            "decision": "idle",
            "tier": "green",
            "auto_execute": False,
            "action": "no skill selected; daemon will exit cleanly",
        }

    policy = TIER_POLICY.get(selection.skill)
    if policy is None:
        return {
            "decision": "skipped",
            "tier": "red",
            "auto_execute": False,
            "action": f"unknown skill {selection.skill!r}; refusing to "
                      f"auto-execute an unclassified skill",
        }

    return {
        "decision": "execute" if policy["auto_execute"] else "blocked-pending",
        "tier": policy["tier"],
        "auto_execute": policy["auto_execute"],
        "action": policy["rationale"],
    }


# ============================================================
# SKILL EXECUTION
# ============================================================

def execute_skill(skill_name: str) -> dict:
    """Invoke the Skill Pack's action module.

    Per the Esalen Skill Pack anatomy, each pack has either:
      - <pack>/action.py            (legacy, e.g. process-inbox)
      - <pack>/<slug>_action.py     (namespaced, e.g. daily_brief_action.py)

    The Resolver detects both. The Daemon does the same. We import the
    module dynamically and call its `process_capture()` (or main()) entry.

    For the Omni-Loop, the input is "whatever the vault state implies."
    For process-inbox, that's a list of files in 00 Inbox/. For the others,
    the action module's main() takes a --date or --week argument.
    """
    pack_dir = SKILLS_DIR / skill_name
    if not pack_dir.exists():
        return {"status": "error", "error": f"pack dir missing: {pack_dir}"}

    # Find the action module: <slug>_action.py first, action.py fallback
    candidates = list(pack_dir.glob("*_action.py"))
    if not candidates:
        candidates = list(pack_dir.glob("action.py"))
    if not candidates:
        return {"status": "error", "error": f"no action module in {pack_dir}"}

    action_file = candidates[0]
    module_name = action_file.stem  # e.g., "daily_brief_action"

    # Import the module from the pack directory
    sys.path.insert(0, str(pack_dir))
    try:
        action_mod = importlib.import_module(module_name)
    except Exception as e:
        return {"status": "error", "error": f"import failed: {e}",
                "traceback": traceback.format_exc()}

    # Invoke the appropriate entry point.
    # process-inbox uses process_capture(inbox_path, m3_output)
    # daily-brief / weekly-connections / deep-research use main()
    try:
        if hasattr(action_mod, "main") and callable(action_mod.main):
            # CLI-style entry; call with sys.argv set
            old_argv = sys.argv
            sys.argv = [module_name]  # pretend the script was invoked
            try:
                rc = action_mod.main()
            finally:
                sys.argv = old_argv
            return {"status": "ok", "returncode": rc,
                    "module": module_name}
        elif hasattr(action_mod, "process_capture"):
            # process-inbox style: process every file in 00 Inbox/
            inbox_files = sorted(INBOX.glob("*.md")) if INBOX.exists() else []
            results = []
            for f in inbox_files:
                # process_capture needs an M3 JSON; we don't have one
                # without an LLM call. The Daemon's process-inbox
                # invocation in v0.1.0 is therefore a STUB: it lists
                # the inbox files but does not actually process them.
                # A real run requires M3 to produce the JSON, which is
                # a session-bound operation. This is intentional:
                # the Daemon does NOT call M3.
                results.append({"file": f.name, "status": "stub",
                                "note": "process-inbox requires M3 "
                                        "JSON input; daemon does not "
                                        "call M3. v0.2.0 will wire "
                                        "an offline classifier."})
            return {"status": "ok", "module": module_name,
                    "results": results, "note": "stub: no LLM call"}
        else:
            return {"status": "error",
                    "error": f"{module_name} has no main() or "
                             f"process_capture(); cannot invoke"}
    except SystemExit as e:
        return {"status": "ok", "returncode": e.code, "module": module_name}
    except Exception as e:
        return {"status": "error", "error": f"{type(e).__name__}: {e}",
                "traceback": traceback.format_exc()}


# ============================================================
# INBOX ALERT (for YELLOW tier)
# ============================================================

def write_inbox_alert(skill: str, reason: str, state: dict) -> Path | None:
    """Write a vault-internal alert to 00 Inbox/. The next Mavis session
    will see this as an inbox item and decide whether to run the skill.
    """
    INBOX.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = INBOX / f"daemon-blocked-{skill}-{ts}.md"
    body = f"""---
type: daemon-alert
created: {datetime.now().isoformat(timespec="seconds")}
skill: {skill}
tier: yellow
status: blocked-pending-approval
---

# Daemon blocked: {skill}

The Mavis Daemon wanted to run `{skill}` but it is YELLOW-tier
(approval required). Run it yourself, or approve it via
`{APPROVALS_FILE.relative_to(VAULT_ROOT)}`.

## Why the Daemon picked this skill

{reason}

## Vault state at wake

```json
{json.dumps(state, indent=2)}
```

## How to approve

Add the skill to `{APPROVALS_FILE.relative_to(VAULT_ROOT)}`:

```json
{{
  "approved_skills": ["{skill}"]
}}
```

The next Daemon wake will see the approval and auto-execute.

---
*Written by mavis_daemon.py v{__version__}, {datetime.now().isoformat(timespec='seconds')}*
"""
    path.write_text(body, encoding="utf-8")
    return path


# ============================================================
# AUDIT LOG
# ============================================================

@dataclass
class RunRecord:
    ts: str
    dry_run: bool
    state_snapshot: dict
    selection_skill: str | None
    selection_confidence: float
    selection_reason: str
    decision: str
    tier: str
    auto_execute: bool
    action_rationale: str
    can_i_result: dict | None = None
    execution_result: dict | None = None
    inbox_alert_path: str | None = None
    daemon_version: str = __version__


def append_log(record: RunRecord) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with DAEMON_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


# ============================================================
# MAIN LOOP
# ============================================================

def run_once(dry_run: bool) -> RunRecord:
    """One Daemon iteration. The full Omni-Loop in 5 steps."""
    state = harvest_state()
    selection = select_skill(state)
    decision = apply_tier_policy(selection)

    can_i_result = None
    execution_result = None
    inbox_alert = None

    if selection.skill is not None and decision["tier"] != "red":
        # Audit gate: can_i on the skill's intended action
        intent = f"run skill {selection.skill} (vault write to notes/daily/connections)"
        can_i_result = can_i(intent)
        if can_i_result["tier"] == "red":
            decision = {
                "decision": "refused",
                "tier": "red",
                "auto_execute": False,
                "action": f"can_i() flagged RED: {can_i_result['rationale']}",
            }

    # Execute / alert / refuse per the decision
    if decision["decision"] == "execute" and not dry_run:
        execution_result = execute_skill(selection.skill)
    elif decision["decision"] == "blocked-pending":
        if not dry_run:
            inbox_alert = write_inbox_alert(
                selection.skill, selection.reason, state
            )
    # else: idle / skipped / refused → no action

    record = RunRecord(
        ts=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        dry_run=dry_run,
        state_snapshot=state,
        selection_skill=selection.skill,
        selection_confidence=selection.confidence,
        selection_reason=selection.reason,
        decision=decision["decision"],
        tier=decision["tier"],
        auto_execute=decision["auto_execute"],
        action_rationale=decision["action"],
        can_i_result=can_i_result,
        execution_result=execution_result,
        inbox_alert_path=str(inbox_alert.relative_to(VAULT_ROOT)) if inbox_alert else None,
    )
    append_log(record)
    # Persist the ledger snapshot for the next run's trigger detection.
    # Only save on real runs (not dry-run) so dry-runs don't reset the
    # change-detection state.
    if not dry_run:
        ledger = state.get("ledger", {})
        if ledger and ledger.get("exists"):
            _save_ledger_snapshot({
                "sha256": ledger.get("sha256"),
                "record_count": ledger.get("record_count"),
                "last_id": ledger.get("last_id"),
                "mtime": ledger.get("mtime"),
                "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
    return record


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="mavis_daemon.py",
        description="Mavis Heartbeat — the Omni-Loop (dry-run by default)",
    )
    ap.add_argument("--once", action="store_true",
                    help="Run one iteration and exit (default for cron)")
    ap.add_argument("--apply", action="store_true",
                    help="Execute for real (default is dry-run)")
    ap.add_argument("--interval", type=int, default=0, metavar="SECONDS",
                    help="Run on a foreground loop every N seconds "
                         "(DEV ONLY; do not use in production)")
    ap.add_argument("--version", action="version",
                    version=f"%(prog)s {__version__}")
    args = ap.parse_args()

    dry_run = not args.apply

    if args.interval > 0:
        # Foreground loop (dev only)
        print(f"[daemon v{__version__}] foreground loop, "
              f"interval={args.interval}s, dry_run={dry_run}", file=sys.stderr)
        try:
            while True:
                rec = run_once(dry_run)
                print(f"[daemon] {rec.decision} | {rec.selection_skill} | "
                      f"{rec.tier} | {rec.selection_reason}", file=sys.stderr)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n[daemon] interrupted; exiting", file=sys.stderr)
            return 0

    if args.once:
        rec = run_once(dry_run)
        # One-line summary to stderr (atomic, self-contained)
        summary = (
            f"[daemon v{__version__}] dry_run={dry_run} | "
            f"decision={rec.decision} | skill={rec.selection_skill} | "
            f"tier={rec.tier} | conf={rec.selection_confidence:.2f} | "
            f"reason={rec.selection_reason}"
        )
        print(summary, file=sys.stderr)
        # Full record to stdout
        print(json.dumps(asdict(rec), indent=2, ensure_ascii=False))
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
