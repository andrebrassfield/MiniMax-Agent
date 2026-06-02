#!/usr/bin/env python3
"""
action.py — I/O layer for the process-inbox Skill.

Pure deterministic code. Reads M3's JSON output and performs the file
operations: move capture to destination via git mv, append wikilinks to
related notes (backlinks), write an audit log entry. NO LLM calls here —
all routing decisions come from M3's JSON per the schema in skill.md.

The split is the Esalen discipline: M3 does the qualitative judgment
(routing, sharpening, tagging, linking). Python does the deterministic
I/O (file move, git, text append, audit log). Tests cover Python;
M3-as-judge evals cover M3.

Usage (programmatic):
    import action
    result = action.process_capture(
        inbox_path="00 Inbox/AI-Coding-Agents-2026-06-02.md",
        m3_output={...JSON from skill.md...},
    )

Usage (CLI):
    action.py --inbox "00 Inbox/foo.md" --m3-output /tmp/m3-decision.json
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

__version__ = "0.1.0"

# ============================================================
# PATHS — vault-resident, hardcoded for the MiniMax-Agent vault
# ============================================================

VAULT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent")
INBOX = VAULT_ROOT / "00 Inbox"
NOTES = VAULT_ROOT / "02 Notes"
AUDIT_LOG = VAULT_ROOT / "99 _system" / "logs" / "process-inbox-audit.jsonl"

# Canonical destination taxonomy. process-inbox must pick from this list;
# creating a new folder requires updating this list + this skill + tests.
VALID_DESTINATIONS = [
    "02 Notes/ideas",
    "02 Notes/patterns",
    "02 Notes/questions",
    "02 Notes/articles",
    "02 Notes/numbers",
]


# ============================================================
# VALIDATION — fail loudly on bad M3 output
# ============================================================

def validate_m3_output(m3_output: dict) -> None:
    """Raise ValueError if M3's output is missing required fields or has
    an invalid destination folder. This is the deterministic layer that
    refuses to silently do the wrong thing on bad input."""
    required = ["destination_folder", "destination_filename", "sharpened_note",
                "tags", "primary_wikilink", "rationale"]
    missing = [f for f in required if f not in m3_output]
    if missing:
        raise ValueError(f"M3 output missing required fields: {missing}")
    if not isinstance(m3_output["tags"], list):
        raise ValueError(f"tags must be a list, got: {type(m3_output['tags']).__name__}")
    if not isinstance(m3_output["destination_filename"], str) or not m3_output["destination_filename"].strip():
        raise ValueError("destination_filename must be a non-empty string")
    if m3_output["destination_folder"] not in VALID_DESTINATIONS:
        raise ValueError(
            f"destination_folder must be one of {VALID_DESTINATIONS}, "
            f"got: {m3_output['destination_folder']!r}"
        )
    if m3_output["primary_wikilink"].count("[[") != 1 or m3_output["primary_wikilink"].count("]]") != 1:
        raise ValueError(
            f"primary_wikilink must be exactly one [[Note Name]]-form link, "
            f"got: {m3_output['primary_wikilink']!r}"
        )


# ============================================================
# GIT OPERATIONS
# ============================================================

def git_mv(src: Path, dst: Path) -> None:
    """Move a file via `git mv` to preserve history. Falls back to
    shutil.move + git rm/add if the source isn't tracked yet."""
    src_rel = str(src.relative_to(VAULT_ROOT))
    dst_rel = str(dst.relative_to(VAULT_ROOT))
    try:
        result = subprocess.run(
            ["git", "mv", src_rel, dst_rel],
            cwd=VAULT_ROOT, check=True, capture_output=True, text=True,
        )
    except subprocess.CalledProcessError as e:
        # git mv failed — could be that the file is untracked. Fall back
        # to a regular move + git add/rm to teach git about it.
        shutil.move(str(src), str(dst))
        subprocess.run(["git", "rm", src_rel], cwd=VAULT_ROOT,
                       capture_output=True, text=True)
        subprocess.run(["git", "add", dst_rel], cwd=VAULT_ROOT,
                       capture_output=True, text=True)


# ============================================================
# WIKILINK BACKLINKS — append to related notes
# ============================================================

def _find_note_by_name(note_name: str) -> Path | None:
    """Find a note file in 02 Notes/ by its stem (no .md extension)."""
    matches = list(NOTES.rglob(f"{note_name}.md"))
    return matches[0] if matches else None


def append_wikilinks(related_note_names: list[str], new_note_name: str) -> int:
    """For each related note, append a backlink to the new note if not
    already present. Returns the count of notes updated.

    Where to append: if the note has a '## Connections' or '## Related'
    section, append under it. Otherwise create a '## Related' section
    at the end of the note."""
    if not related_note_names:
        return 0
    updated = 0
    for note_name in related_note_names:
        target = _find_note_by_name(note_name)
        if target is None:
            continue  # skip silently — M3 may have guessed a note that doesn't exist
        content = target.read_text(encoding="utf-8")
        wikilink = f"[[{new_note_name}]]"
        if wikilink in content:
            continue  # already linked
        new_line = f"- {wikilink} (backlink from process-inbox)"
        if "## Connections" in content:
            content = content.replace(
                "## Connections",
                f"## Connections\n{new_line}",
                1,
            )
        elif "## Related" in content:
            content = content.replace(
                "## Related",
                f"## Related\n{new_line}",
                1,
            )
        else:
            # No existing section — append at the end with a header
            content = content.rstrip() + f"\n\n## Related\n\n{new_line}\n"
        target.write_text(content, encoding="utf-8")
        updated += 1
    return updated


# ============================================================
# AUDIT LOG
# ============================================================

def write_audit_log(entry: dict) -> None:
    """Append a single JSONL entry to the process-inbox audit log.
    Audit path: <vault>/99 _system/logs/process-inbox-audit.jsonl"""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ============================================================
# MAIN ENTRYPOINT — process a single capture
# ============================================================

def process_capture(inbox_path: str, m3_output: dict) -> dict:
    """Move the inbox capture to its destination, append backlinks, log.

    Args:
        inbox_path: relative path to the capture in 00 Inbox/ (e.g.,
                    "00 Inbox/Some-Capture-2026-06-02.md")
        m3_output:  the JSON object M3 produced per the skill.md schema

    Returns:
        dict with: source, destination, backlinks_updated, audit_logged, status

    Raises:
        ValueError: bad m3_output (missing fields, invalid destination)
        FileNotFoundError: inbox capture doesn't exist
        FileExistsError: destination filename already taken
    """
    validate_m3_output(m3_output)

    # Resolve and validate the source path
    src = VAULT_ROOT / inbox_path
    if not src.exists():
        raise FileNotFoundError(f"Inbox capture not found: {src}")
    if not src.is_relative_to(INBOX):
        raise ValueError(f"Source must be inside {INBOX}, got: {src}")

    # Resolve the destination
    dst_folder = VAULT_ROOT / m3_output["destination_folder"]
    if not dst_folder.exists():
        raise FileNotFoundError(f"Destination folder not found: {dst_folder}")
    dst_filename = m3_output["destination_filename"]
    if not dst_filename.endswith(".md"):
        dst_filename += ".md"
    dst = dst_folder / dst_filename
    if dst.exists():
        raise FileExistsError(f"Destination already exists: {dst}")

    # Write the sharpened note content to the SOURCE file. The subsequent
    # git_mv moves the source (with the new content) to the destination.
    # This way the move preserves git history AND carries the sharpened
    # text along — writing to dst first would have git_mv overwrite it.
    src.write_text(m3_output["sharpened_note"], encoding="utf-8")

    # Git mv (preserves history in the original inbox file)
    git_mv(src, dst)

    # Append wikilinks to related notes
    all_links = [m3_output["primary_wikilink"]] + m3_output.get("additional_links", [])
    related_names = [link.strip("[]") for link in all_links if link]
    backlinks_updated = append_wikilinks(related_names, Path(dst_filename).stem)

    # Audit log entry
    audit_entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "source": str(src.relative_to(VAULT_ROOT)),
        "destination": str(dst.relative_to(VAULT_ROOT)),
        "category": m3_output["destination_folder"],
        "tags": m3_output["tags"],
        "primary_wikilink": m3_output["primary_wikilink"],
        "additional_links": m3_output.get("additional_links", []),
        "backlinks_updated": backlinks_updated,
        "rationale": m3_output.get("rationale", ""),
        "script_version": __version__,
    }
    write_audit_log(audit_entry)

    return {
        "source": str(src.relative_to(VAULT_ROOT)),
        "destination": str(dst.relative_to(VAULT_ROOT)),
        "backlinks_updated": backlinks_updated,
        "audit_logged": True,
        "status": "ok",
    }


# ============================================================
# CLI — read M3 output from a file, run process_capture, print result
# ============================================================

def main() -> int:
    ap = argparse.ArgumentParser(
        prog="action.py",
        description="I/O layer for the process-inbox Skill. Reads M3 JSON "
                    "from --m3-output and the inbox path from --inbox, "
                    "performs the move + backlinks, writes audit log.",
    )
    ap.add_argument("--inbox",
                    help="Relative path to the inbox capture "
                         '(e.g., "00 Inbox/Capture.md")')
    ap.add_argument("--m3-output",
                    help="Path to a file containing M3's JSON output")
    ap.add_argument("--version", action="version",
                    version=f"action.py v{__version__}")
    args = ap.parse_args()

    if not args.inbox or not args.m3_output:
        ap.error("--inbox and --m3-output are required (omit for --version)")

    try:
        m3_output = json.loads(Path(args.m3_output).read_text(encoding="utf-8"))
        result = process_capture(args.inbox, m3_output)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"action.py: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
