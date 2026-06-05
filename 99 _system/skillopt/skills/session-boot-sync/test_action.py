#!/usr/bin/env python3
"""
test_action.py — pytest unit tests for the session-boot-sync action.py.

The tests use a monkeypatched module-level path config to point
action.py at a temp vault. No real vault files are touched.

Run from the vault root:
    python3 -m pytest 99\\ _system/skillopt/skills/session-boot-sync/test_action.py -v
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

import pytest

# Make action.py importable from the same directory
sys.path.insert(0, str(Path(__file__).parent))
import action  # noqa: E402


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def temp_vault(tmp_path, monkeypatch):
    """Create a temp vault with git initialized and the directories
    action.py expects. Monkeypatches the module-level paths."""
    vault = tmp_path / "vault"
    vault.mkdir()

    # Required top-level dirs
    for d in ("00 Inbox", "01 Daily", "02 Notes", "03 Projects"):
        (vault / d).mkdir()

    # 99 _system/logs for the ledger snapshot
    (vault / "99 _system" / "logs").mkdir(parents=True)

    # A memory file (separate from the vault)
    agent_dir = tmp_path / "agent"
    (agent_dir / "memory").mkdir(parents=True)
    memory_path = agent_dir / "memory" / "MEMORY.md"
    memory_path.write_text(
        "# Mavis — Memory\n\n"
        "## Hard constraints (2026-06-04)\n"
        "- no deploys without approval\n"
        "\n"
        "### Vault destruction incident — 2026-06-05 11:28→11:42 CT (2026-06-05)\n"
        "Type: data-loss-prevention (hard correction)\n"
        "Three rules locked after the 11:28→11:42 CT incident.\n"
        "\n"
        "### Hung worker on rate-limited model → silent 12h orchestrator timeout (2026-06-04/05)\n"
        "Type: orchestration-failure-mode (hard correction)\n"
        "Abort-to-solo heuristic when worker hangs and parent had\n"
        "a rate-limit incident in the last 60 min.\n"
        "\n"
        "### Untitled (2026-06-04)\n"
        "Type: noise — should be filtered by M3 as low-signal.\n",
        encoding="utf-8",
    )

    # Init a real git repo + 3 commits
    subprocess.run(["git", "init", "-q"], cwd=vault, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"],
                   cwd=vault, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"],
                   cwd=vault, check=True, capture_output=True)
    (vault / "README").write_text("# Test Vault")
    subprocess.run(["git", "add", "."], cwd=vault, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"],
                   cwd=vault, check=True, capture_output=True)
    (vault / "01 Daily").mkdir(exist_ok=True)
    (vault / "01 Daily" / "2026-06-04.md").write_text("# 2026-06-04")
    subprocess.run(["git", "add", "."], cwd=vault, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "Add daily 2026-06-04"],
                   cwd=vault, check=True, capture_output=True)
    (vault / "03 Projects" / "Builder" / "queue").mkdir(parents=True)
    (vault / "03 Projects" / "Builder" / "queue" / "mavis-handoff.md").write_text(
        "---\nstatus: ready\n---\n# Handoff\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=vault, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "Add Builder handoff"],
                   cwd=vault, check=True, capture_output=True)

    # Ledger snapshot
    (vault / "99 _system" / "logs" / "ledger-snapshot.json").write_text(
        json.dumps({
            "last_id": "clm-2026-06-04-010",
            "mtime": datetime.now(tz=timezone.utc).timestamp(),
            "record_count": 22,
            "saved_at": "2026-06-05T12:42:07+00:00",
            "sha256": "abc123",
        }),
        encoding="utf-8",
    )

    # Monkeypatch module-level paths
    monkeypatch.setattr(action, "VAULT_ROOT", vault)
    monkeypatch.setattr(action, "MEMORY_FILE", memory_path)
    monkeypatch.setattr(action, "LEDGER_SNAPSHOT",
                        vault / "99 _system" / "logs" / "ledger-snapshot.json")
    monkeypatch.setattr(action, "PROJECTS_ROOT", vault / "03 Projects")
    monkeypatch.setattr(action, "DAILY_ROOT", vault / "01 Daily")

    return {
        "vault": vault,
        "memory_path": memory_path,
    }


# ============================================================
# MEMORY TAIL TESTS
# ============================================================

def test_gather_memory_tail_ok(temp_vault):
    result = action.gather_memory_tail(temp_vault["memory_path"], n=80)
    assert result["status"] == "ok"
    assert result["line_count"] > 0
    # The fixture has 4 dated entries:
    #   ## Hard constraints (2026-06-04)        [trailing-paren date]
    #   ### Vault destruction incident — 2026-06-05 11:28→11:42 CT (2026-06-05)  [trailing-paren date]
    #   ### Hung worker on rate-limited model → silent 12h orchestrator timeout (2026-06-04/05)  [trailing-paren date with /DD]
    #   ### Untitled (2026-06-04)               [trailing-paren date]
    # Both regexes (trailing-paren + inline) should fire. M3 will filter
    # for the 2-3 most-recent hard-correction entries in its synthesis.
    assert len(result["entries"]) == 4
    titles = [e["title"] for e in result["entries"]]
    assert any("Vault destruction" in t for t in titles)
    assert any("Hung worker" in t for t in titles)
    assert any("Untitled" in t for t in titles)
    # The Vault destruction title should preserve the long-form
    # "2026-06-05 11:28→11:42 CT" prefix that appears before the
    # trailing (2026-06-05) parens.
    vd = next(t for t in titles if "Vault destruction" in t)
    assert "11:28→11:42" in vd
    # The Hung worker entry's date should include the /05 day-range
    # suffix — the regex captures the full `(2026-06-04/05)` so M3
    # can see this was a multi-day incident, not just 06-04.
    hw = next(e for e in result["entries"] if "Hung worker" in e["title"])
    assert hw["date"] == "2026-06-04/05"
    # The title should preserve the "→ silent 12h orchestrator timeout" tail
    assert "→ silent 12h orchestrator timeout" in hw["title"]


def test_gather_memory_tail_inline_date(tmp_path):
    """Headers with the date embedded in the title (no trailing paren date)
    should still be captured by the inline-date regex. Example:
      ### Vault destruction incident — 2026-06-05 11:28→11:42 CT (hard correction)
    The trailing parens here are a type description, not a date."""
    mem = tmp_path / "MEMORY.md"
    mem.write_text(
        "## Hard constraints\n"
        "- no deploys\n"
        "\n"
        "### Vault destruction incident — 2026-06-05 11:28→11:42 CT (hard correction)\n"
        "Type: data-loss-prevention (hard correction)\n",
        encoding="utf-8",
    )
    result = action.gather_memory_tail(mem, n=80)
    assert result["status"] == "ok"
    assert len(result["entries"]) == 1
    entry = result["entries"][0]
    assert "Vault destruction" in entry["title"]
    assert entry["date"] == "2026-06-05"
    # The title should be truncated at the inline date (we don't want
    # the trailing "(hard correction)" clutter in the title field)
    assert "(hard correction)" not in entry["title"]


def test_gather_memory_tail_truncates(temp_vault):
    result = action.gather_memory_tail(temp_vault["memory_path"], n=5)
    assert result["line_count"] == 5
    # When truncated, we may find 0 or 1 entries — that's fine
    assert "entries" in result


def test_gather_memory_tail_missing(tmp_path):
    missing = tmp_path / "nope.md"
    result = action.gather_memory_tail(missing, n=80)
    assert result["status"] == "missing"
    assert result["entries"] == []


def test_gather_memory_tail_skips_untitled(temp_vault):
    result = action.gather_memory_tail(temp_vault["memory_path"], n=80)
    titles = [e["title"] for e in result["entries"]]
    # The "Untitled" entry in the fixture should still parse (it has
    # a date in parens), but M3 will filter it. The regex correctly
    # finds the dated entries regardless.
    assert "Untitled" in titles or len(titles) >= 2


# ============================================================
# RECENT COMMITS TESTS
# ============================================================

def test_gather_recent_commits(temp_vault):
    commits = action.gather_recent_commits(temp_vault["vault"], count=10)
    assert len(commits) == 3
    # Most recent first
    assert commits[0]["subject"] == "Add Builder handoff"
    assert "hash" in commits[0]
    assert "date" in commits[0]
    # Hash is 7+ chars
    assert len(commits[0]["hash"]) >= 7


def test_gather_recent_commits_not_a_git_repo(tmp_path, monkeypatch):
    # A path that exists but isn't a git repo
    monkeypatch.setattr(action, "VAULT_ROOT", tmp_path)
    commits = action.gather_recent_commits(tmp_path, count=5)
    assert commits == []


# ============================================================
# LEDGER SNAPSHOT TESTS
# ============================================================

def test_gather_ledger_snapshot_ok(temp_vault):
    result = action.gather_ledger_snapshot(temp_vault["vault"] / "99 _system" / "logs" / "ledger-snapshot.json")
    assert result["status"] == "ok"
    assert result["last_id"] == "clm-2026-06-04-010"
    assert result["record_count"] == 22
    assert result["sha256"] == "abc123"
    assert result["mtime_iso"] is not None


def test_gather_ledger_snapshot_missing(tmp_path):
    result = action.gather_ledger_snapshot(tmp_path / "nope.json")
    assert result["status"] == "missing"


def test_gather_ledger_snapshot_corrupt(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json {", encoding="utf-8")
    result = action.gather_ledger_snapshot(bad)
    assert result["status"] == "error"


# ============================================================
# PENDING HANDOFFS TESTS
# ============================================================

def test_gather_pending_handoffs(temp_vault):
    result = action.gather_pending_handoffs(temp_vault["vault"] / "03 Projects", top_n=5)
    assert len(result) == 1
    entry = result[0]
    assert "Builder" in entry["project"]
    assert entry["filename"] == "mavis-handoff.md"
    assert entry["status"] == "ready"
    assert "path" in entry
    assert "mtime" in entry
    # abs_path must be stripped from the bundle
    assert "abs_path" not in entry


def test_gather_pending_handoffs_empty(tmp_path):
    result = action.gather_pending_handoffs(tmp_path / "nope", top_n=5)
    assert result == []


def test_gather_pending_handoffs_sorts_by_mtime(temp_vault):
    # Add a second, more recent handoff
    newer_dir = temp_vault["vault"] / "03 Projects" / "Verifier" / "queue"
    newer_dir.mkdir(parents=True)
    (newer_dir / "audit-handoff.md").write_text(
        "---\nstatus: pending\n---\n# Audit\n",
        encoding="utf-8",
    )
    # Force its mtime to be newer
    import os
    new_mtime = datetime.now(tz=timezone.utc).timestamp() + 100
    os.utime(newer_dir / "audit-handoff.md", (new_mtime, new_mtime))

    result = action.gather_pending_handoffs(
        temp_vault["vault"] / "03 Projects", top_n=5
    )
    assert len(result) == 2
    # Newer first
    assert result[0]["project"] == "Verifier"
    assert result[1]["project"] == "Builder"


# ============================================================
# RECENT DAILY TESTS
# ============================================================

def test_gather_recent_daily_ok(temp_vault):
    result = action.gather_recent_daily(temp_vault["vault"] / "01 Daily")
    assert result is not None
    assert result["date"] == "2026-06-04"
    assert "2026-06-04.md" in result["path"]


def test_gather_recent_daily_empty(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    result = action.gather_recent_daily(empty)
    assert result is None


def test_gather_recent_daily_picks_most_recent(temp_vault):
    # Add an older daily
    (temp_vault["vault"] / "01 Daily" / "2026-06-01.md").write_text("# Old")
    result = action.gather_recent_daily(temp_vault["vault"] / "01 Daily")
    assert result["date"] == "2026-06-04"  # newer wins


# ============================================================
# VAULT STATUS TESTS
# ============================================================

def test_gather_vault_status_ok(temp_vault):
    result = action.gather_vault_status(temp_vault["vault"])
    assert result["status"] == "ok"
    assert result["missing_dirs"] == []


def test_gather_vault_status_partial(tmp_path, monkeypatch):
    partial = tmp_path / "partial"
    partial.mkdir()
    (partial / ".git").mkdir()
    (partial / "00 Inbox").mkdir()
    # Missing: 01 Daily, 02 Notes, 03 Projects
    monkeypatch.setattr(action, "VAULT_ROOT", partial)
    result = action.gather_vault_status(partial)
    assert result["status"] == "partial"
    assert "01 Daily" in result["missing_dirs"]


def test_gather_vault_status_missing(tmp_path):
    result = action.gather_vault_status(tmp_path / "nope")
    assert result["status"] == "missing"


# ============================================================
# BUNDLE & CHECK TESTS
# ============================================================

def test_gather_boot_state_full(temp_vault):
    bundle = action.gather_boot_state()
    assert bundle["schema_version"] == "0.1.0"
    assert "gathered_at" in bundle
    assert bundle["vault_status"]["status"] == "ok"
    assert bundle["memory"]["status"] == "ok"
    assert len(bundle["recent_commits"]) == 3
    assert bundle["ledger_snapshot"]["status"] == "ok"
    assert len(bundle["pending_handoffs"]) == 1
    assert bundle["recent_daily"]["date"] == "2026-06-04"


def test_check_inputs_all_ok(temp_vault):
    ok, issues = action.check_inputs()
    assert ok is True
    assert issues == []


def test_check_inputs_missing_memory(tmp_path, monkeypatch, temp_vault):
    # Replace MEMORY_FILE with a non-existent path
    monkeypatch.setattr(action, "MEMORY_FILE", tmp_path / "no-memory.md")
    ok, issues = action.check_inputs()
    assert ok is False
    assert any("memory" in i for i in issues)
