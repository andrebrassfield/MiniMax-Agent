#!/usr/bin/env python3
"""
test_action.py — pytest unit tests for the process-inbox action.py.

Run from the vault root:
    python3 -m pytest 99\ _system/skillopt/skills/process-inbox/test_action.py -v

The tests use a temporary vault fixture (no real vault files touched) and
a real git repo inside the temp dir so git_mv has something to operate on.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Make action.py importable from the same directory
sys.path.insert(0, str(Path(__file__).parent))
import action  # noqa: E402


# ============================================================
# FIXTURE — temp vault with git initialized
# ============================================================

@pytest.fixture
def temp_vault(tmp_path, monkeypatch):
    """Create a temporary vault structure for testing.
    Monkeypatches action's module-level paths to point at the temp vault."""
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "00 Inbox").mkdir()
    for sub in ("ideas", "patterns", "questions", "articles", "numbers"):
        (vault / "02 Notes" / sub).mkdir(parents=True)
    (vault / "99 _system" / "logs").mkdir(parents=True)

    # Init a real git repo so git_mv works
    subprocess.run(["git", "init", "-q"], cwd=vault, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"],
                   cwd=vault, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"],
                   cwd=vault, check=True, capture_output=True)
    # An initial commit so HEAD exists
    (vault / "README").write_text("# Test Vault")
    subprocess.run(["git", "add", "."], cwd=vault, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"],
                   cwd=vault, check=True, capture_output=True)

    monkeypatch.setattr(action, "VAULT_ROOT", vault)
    monkeypatch.setattr(action, "INBOX", vault / "00 Inbox")
    monkeypatch.setattr(action, "NOTES", vault / "02 Notes")
    monkeypatch.setattr(action, "AUDIT_LOG",
                        vault / "99 _system" / "logs" / "process-inbox-audit.jsonl")
    return vault


@pytest.fixture
def good_m3_output():
    """A minimal valid M3 output dict for tests."""
    return {
        "destination_folder": "02 Notes/ideas",
        "destination_filename": "Sharpened.md",
        "sharpened_note": "# Sharpened\n\nThe one-sentence sharpening.",
        "tags": ["idea"],
        "primary_wikilink": "[[Other]]",
        "additional_links": [],
        "rationale": "Test routing",
    }


# ============================================================
# VALIDATION TESTS
# ============================================================

def test_validate_m3_output_ok(good_m3_output):
    action.validate_m3_output(good_m3_output)  # should not raise


def test_validate_m3_output_missing_field():
    bad = {"destination_folder": "02 Notes/ideas"}
    with pytest.raises(ValueError, match="missing required fields"):
        action.validate_m3_output(bad)


def test_validate_m3_output_invalid_destination(good_m3_output):
    good_m3_output["destination_folder"] = "02 Notes/bogus"
    with pytest.raises(ValueError, match="destination_folder must be one of"):
        action.validate_m3_output(good_m3_output)


def test_validate_m3_output_tags_must_be_list(good_m3_output):
    good_m3_output["tags"] = "idea,tag"  # string instead of list
    with pytest.raises(ValueError, match="tags must be a list"):
        action.validate_m3_output(good_m3_output)


def test_validate_m3_output_filename_empty(good_m3_output):
    good_m3_output["destination_filename"] = ""
    with pytest.raises(ValueError, match="destination_filename must be a non-empty string"):
        action.validate_m3_output(good_m3_output)


def test_validate_m3_output_wikilink_format(good_m3_output):
    good_m3_output["primary_wikilink"] = "NotAWikilink"
    with pytest.raises(ValueError, match="primary_wikilink must be exactly one"):
        action.validate_m3_output(good_m3_output)


# ============================================================
# GIT_MV TESTS
# ============================================================

def test_git_mv_tracked_file(temp_vault):
    src = temp_vault / "00 Inbox" / "tracked.md"
    src.write_text("hello")
    subprocess.run(["git", "add", "00 Inbox/tracked.md"], cwd=temp_vault, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "add tracked"], cwd=temp_vault, check=True, capture_output=True)

    dst = temp_vault / "02 Notes" / "ideas" / "moved.md"
    action.git_mv(src, dst)

    assert not src.exists()
    assert dst.exists()
    assert dst.read_text() == "hello"


def test_git_mv_untracked_file(temp_vault):
    """Untracked files: git mv fails, fall back to shutil.move + git add."""
    src = temp_vault / "00 Inbox" / "untracked.md"
    src.write_text("hello")
    # Don't `git add` it — leave it untracked

    dst = temp_vault / "02 Notes" / "ideas" / "moved.md"
    action.git_mv(src, dst)

    assert not src.exists()
    assert dst.exists()


# ============================================================
# WIKILINK BACKLINK TESTS
# ============================================================

def test_append_wikilinks_existing_connections_section(temp_vault):
    target = temp_vault / "02 Notes" / "ideas" / "Target.md"
    target.write_text("# Target\n\nBody.\n\n## Connections\n\n- [[Other]]\n")

    updated = action.append_wikilinks(["Target"], "New-Note")

    assert updated == 1
    content = target.read_text()
    assert "[[New-Note]]" in content
    assert "## Connections" in content
    assert "(backlink from process-inbox)" in content


def test_append_wikilinks_existing_related_section(temp_vault):
    target = temp_vault / "02 Notes" / "ideas" / "Target.md"
    target.write_text("# Target\n\n## Related\n\n- [[Old]]\n")

    updated = action.append_wikilinks(["Target"], "New-Note")

    assert updated == 1
    content = target.read_text()
    assert "[[New-Note]]" in content
    assert "## Related" in content


def test_append_wikilinks_creates_new_section(temp_vault):
    target = temp_vault / "02 Notes" / "ideas" / "Lone.md"
    target.write_text("# Lone\n\nJust a body, no sections at all.\n")

    updated = action.append_wikilinks(["Lone"], "New-Note")

    assert updated == 1
    content = target.read_text()
    assert "## Related" in content
    assert "[[New-Note]]" in content


def test_append_wikilinks_already_linked(temp_vault):
    target = temp_vault / "02 Notes" / "ideas" / "Already.md"
    target.write_text("# Already\n\n## Connections\n\n- [[New-Note]]\n")

    updated = action.append_wikilinks(["Already"], "New-Note")

    assert updated == 0  # already present, no change
    # File should be unchanged
    assert target.read_text() == "# Already\n\n## Connections\n\n- [[New-Note]]\n"


def test_append_wikilinks_note_not_found(temp_vault):
    updated = action.append_wikilinks(["Nonexistent"], "New-Note")
    assert updated == 0


def test_append_wikilinks_empty_list(temp_vault):
    assert action.append_wikilinks([], "New-Note") == 0


# ============================================================
# PROCESS_CAPTURE — happy path + error paths
# ============================================================

def test_process_capture_happy_path(temp_vault, good_m3_output):
    # Create inbox capture
    inbox = temp_vault / "00 Inbox" / "Capture.md"
    inbox.write_text("raw capture content")
    subprocess.run(["git", "add", "."], cwd=temp_vault, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "add capture"], cwd=temp_vault, check=True, capture_output=True)

    # Create a related note that will get a backlink
    related = temp_vault / "02 Notes" / "ideas" / "Related.md"
    related.write_text("# Related\n\n## Connections\n\n- [[Other]]\n")
    subprocess.run(["git", "add", "."], cwd=temp_vault, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "add related"], cwd=temp_vault, check=True, capture_output=True)

    # M3 wants to link to "Other" (primary_wikilink) but Other doesn't exist;
    # should silently skip, then link to "Related" (additional_links).
    good_m3_output["primary_wikilink"] = "[[Other]]"
    good_m3_output["additional_links"] = ["[[Related]]"]

    result = action.process_capture("00 Inbox/Capture.md", good_m3_output)

    assert result["status"] == "ok"
    assert result["source"] == "00 Inbox/Capture.md"
    assert result["destination"] == "02 Notes/ideas/Sharpened.md"
    assert result["backlinks_updated"] == 1  # only Related got updated
    assert result["audit_logged"] is True

    # The inbox file should be gone
    assert not inbox.exists()
    # The destination file should exist with the sharpened content
    dst = temp_vault / "02 Notes" / "ideas" / "Sharpened.md"
    assert dst.exists()
    assert dst.read_text() == "# Sharpened\n\nThe one-sentence sharpening."

    # The related note should have a backlink
    assert "[[Sharpened]]" in related.read_text()

    # The audit log should have one entry
    assert action.AUDIT_LOG.exists()
    entries = [json.loads(l) for l in action.AUDIT_LOG.read_text().splitlines()]
    assert len(entries) == 1
    assert entries[0]["source"] == "00 Inbox/Capture.md"
    assert entries[0]["destination"] == "02 Notes/ideas/Sharpened.md"
    assert entries[0]["backlinks_updated"] == 1
    assert entries[0]["script_version"] == "0.1.0"


def test_process_capture_adds_md_extension(temp_vault, good_m3_output):
    """If M3 forgets the .md extension, action.py adds it."""
    inbox = temp_vault / "00 Inbox" / "Capture.md"
    inbox.write_text("raw")
    subprocess.run(["git", "add", "."], cwd=temp_vault, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=temp_vault, check=True, capture_output=True)

    good_m3_output["destination_filename"] = "NoExtension"  # no .md
    result = action.process_capture("00 Inbox/Capture.md", good_m3_output)

    assert result["destination"] == "02 Notes/ideas/NoExtension.md"
    assert (temp_vault / "02 Notes" / "ideas" / "NoExtension.md").exists()


def test_process_capture_missing_inbox(temp_vault, good_m3_output):
    with pytest.raises(FileNotFoundError, match="Inbox capture not found"):
        action.process_capture("00 Inbox/Nonexistent.md", good_m3_output)


def test_process_capture_destination_exists(temp_vault, good_m3_output):
    inbox = temp_vault / "00 Inbox" / "Capture.md"
    inbox.write_text("raw")
    existing = temp_vault / "02 Notes" / "ideas" / "Sharpened.md"
    existing.write_text("preexisting")

    with pytest.raises(FileExistsError, match="Destination already exists"):
        action.process_capture("00 Inbox/Capture.md", good_m3_output)


def test_process_capture_invalid_destination_folder(temp_vault, good_m3_output):
    inbox = temp_vault / "00 Inbox" / "Capture.md"
    inbox.write_text("raw")
    good_m3_output["destination_folder"] = "02 Notes/bogus"

    with pytest.raises(ValueError, match="destination_folder must be one of"):
        action.process_capture("00 Inbox/Capture.md", good_m3_output)


def test_process_capture_source_outside_inbox(temp_vault, good_m3_output):
    """If the path resolves to somewhere other than 00 Inbox/, refuse."""
    outside = temp_vault / "02 Notes" / "ideas" / "Existing.md"
    outside.write_text("not in inbox")

    with pytest.raises(ValueError, match="Source must be inside"):
        action.process_capture("02 Notes/ideas/Existing.md", good_m3_output)
