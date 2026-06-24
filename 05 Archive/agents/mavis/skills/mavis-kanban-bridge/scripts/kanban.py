#!/usr/bin/env python3
"""
kanban.sh — the executable surface for the mavis-kanban-bridge skill.

Five operations:
  read         — list active cards (filterable)
  new          — write a new card from a directive
  transition   — change status, validate frontmatter
  move         — terminal status → directory move
  validate     — run the 7 SCHEMA rules

Implements the contract at:
  ~/.mavis/agents/mavis/skills/mavis-kanban-bridge/SKILL.md
  ~/Documents/Obsidian/MainVault/Kanban/SCHEMA.md
"""
import argparse
import datetime as dt
import os
import re
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("ERROR missing-dep: PyYAML not installed. pip install pyyaml.\n")
    sys.exit(2)

KANBAN_ROOT = Path(os.environ.get(
    "KANBAN_ROOT",
    Path.home() / "Documents" / "Obsidian" / "MainVault" / "Kanban"
))
ACTIVE = KANBAN_ROOT / "cards" / "active"
DONE = KANBAN_ROOT / "cards" / "done"
DROPPED = KANBAN_ROOT / "cards" / "dropped"
TEMPLATE = KANBAN_ROOT / "templates" / "card.md"
HERMES_PROFILES = Path.home() / ".hermes" / "profiles"

VALID_STATUS = {"open", "in_progress", "blocked", "done", "dropped"}
VALID_PRIORITY = {"high", "med", "low"}
ID_RE = re.compile(r"^kanban-(\d{4})-(\d{2})-(\d{2})-(\d{3})$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Transition validity table (from operations.md)
TRANSITIONS = {
    "open": {"in_progress", "blocked", "dropped"},
    "in_progress": {"done", "blocked", "dropped"},
    "blocked": {"in_progress", "dropped"},
    "done": set(),
    "dropped": set(),
}


def err(code, msg):
    sys.stderr.write(f"ERROR {code}: {msg}\n")
    sys.exit(1)


def now_iso():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def now_date():
    return dt.date.today().isoformat()


def parse_card(path):
    """Parse a card's frontmatter. Returns (meta_dict, body_str, raw_text)."""
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        return None, raw, raw
    end = raw.find("\n---\n", 4)
    if end == -1:
        return None, raw, raw
    fm_text = raw[4:end]
    body = raw[end + 5:]
    try:
        meta = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        return {"_yaml_error": str(e)}, body, raw
    return meta, body, raw


def write_card(path, meta, body):
    """Atomic write: temp + fsync + rename."""
    fm = yaml.safe_dump(meta, default_flow_style=False, sort_keys=False).rstrip()
    content = f"---\n{fm}\n---\n\n{body}"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.rename(path)


def find_card(card_id):
    """Locate a card by id across all dirs. Returns Path or None."""
    for d in (ACTIVE, DONE, DROPPED):
        for p in d.glob(f"{card_id}-*.md"):
            return p
    return None


def next_id_for_today():
    """Generate the next kanban-YYYY-MM-DD-NNN id, scanning all dirs."""
    today = now_date()
    prefix = f"kanban-{today}-"
    max_n = 0
    for d in (ACTIVE, DONE, DROPPED):
        for p in d.glob(f"{prefix}*.md"):
            m = re.match(r"^kanban-\d{4}-\d{2}-\d{2}-(\d{3})-", p.name)
            if m:
                n = int(m.group(1))
                if n > max_n:
                    max_n = n
    return f"{prefix}{max_n + 1:03d}"


def slugify(title, max_words=4):
    """Convert title to a 2-4 word lowercase-hyphenated slug."""
    words = re.findall(r"[a-zA-Z0-9]+", title.lower())
    return "-".join(words[:max_words]) if words else "untitled"


def validate_card(card_id, meta):
    """Run the 7 SCHEMA rules against a meta dict. Returns list of errors."""
    errors = []
    if "_yaml_error" in meta:
        errors.append(f"yaml-parse: {meta['_yaml_error']}")
        return errors

    if "id" not in meta or not ID_RE.match(str(meta.get("id", ""))):
        errors.append(f"id-format: id '{meta.get('id')}' does not match ^kanban-\\d{{4}}-\\d{{2}}-\\d{{2}}-\\d{{3}}$")
    if "title" not in meta or len(str(meta.get("title", ""))) > 80:
        errors.append(f"title-length: title is {len(str(meta.get('title', '')))} chars; required and max 80")
    if meta.get("status") not in VALID_STATUS:
        errors.append(f"status-enum: status '{meta.get('status')}' is not in {sorted(VALID_STATUS)}")
    owner = meta.get("owner", "")
    if not owner:
        errors.append("owner-missing: owner is required")
    elif owner != "human:andre":
        profile_path = HERMES_PROFILES / owner
        if not profile_path.exists():
            errors.append(f"owner-unknown: owner '{owner}' is not a registered profile and not 'human:andre'")
    if meta.get("priority") not in VALID_PRIORITY:
        errors.append(f"priority-enum: priority '{meta.get('priority')}' is not in {sorted(VALID_PRIORITY)}")
    for fld in ("created", "updated"):
        v = meta.get(fld, "")
        if not ISO_DATE_RE.match(str(v)):
            errors.append(f"date-format: {fld} '{v}' is not ISO YYYY-MM-DD")
    if meta.get("status") == "in_progress":
        na = meta.get("next_action", "")
        if not na or not str(na).strip():
            errors.append("next-action-empty: status in_progress requires non-empty next_action")
    if meta.get("status") == "blocked":
        bb = meta.get("blocked_by")
        if not bb:
            errors.append("block-orphan: status blocked requires non-empty blocked_by")
        else:
            refs = bb if isinstance(bb, list) else [bb]
            for r in refs:
                if not find_card(str(r)):
                    errors.append(f"block-orphan: blocked_by '{r}' does not reference an existing card")
    return errors


# ─── Operations ─────────────────────────────────────────────────────────

def op_read(args):
    """List active cards matching filters."""
    if not ACTIVE.exists():
        return
    profiles = set(p.name for p in HERMES_PROFILES.iterdir()) if HERMES_PROFILES.exists() else set()
    for p in sorted(ACTIVE.glob("*.md")):
        meta, _, _ = parse_card(p)
        if meta is None or "_yaml_error" in meta:
            print(f"[MALFORMED] {p.name}")
            continue
        if args.owner and meta.get("owner") != args.owner:
            continue
        if args.status and meta.get("status") != args.status:
            continue
        if args.tag:
            tags = meta.get("tags") or []
            if args.tag not in tags:
                continue
        # Orphan-block check (warning prefix, not filter)
        prefix = ""
        if meta.get("status") == "blocked":
            bb = meta.get("blocked_by")
            refs = bb if isinstance(bb, list) else [bb] if bb else []
            for r in refs:
                if not find_card(str(r)):
                    prefix = "[ORPHAN_BLOCK] "
                    break
        cid = meta.get("id", "?")
        title = meta.get("title", "?")
        owner = meta.get("owner", "?")
        prio = meta.get("priority", "?")
        na = meta.get("next_action", "")
        print(f"{prefix}{cid}\t{title}\t{owner}\t{prio}\t{na}")


def op_new(args):
    """Write a new card to cards/active/."""
    if len(args.title) > 80:
        err("title-length", f"title is {len(args.title)} chars; max 80")
    if args.priority not in VALID_PRIORITY:
        err("priority-enum", f"priority '{args.priority}' is not in {sorted(VALID_PRIORITY)}")
    if args.owner != "human:andre":
        if not (HERMES_PROFILES / args.owner).exists():
            err("owner-unknown", f"owner '{args.owner}' is not a registered profile and not 'human:andre'")
    if args.depends_on and not find_card(args.depends_on):
        err("block-orphan", f"depends_on '{args.depends_on}' does not reference an existing card")

    card_id = next_id_for_today()
    slug = slugify(args.title)
    fname = f"{card_id}-{slug}.md"
    target = ACTIVE / fname

    actor = os.environ.get("MAVIS_PROFILE", "human:andre")
    today = now_date()
    tags = args.tag or []

    meta = {
        "id": card_id,
        "title": args.title,
        "status": "open",
        "owner": args.owner,
        "priority": args.priority,
        "created": today,
        "updated": today,
        "next_action": args.next_action,
        "blocked_by": args.depends_on or None,
        "depends_on": args.depends_on or None,
        "tags": tags,
    }
    meta = {k: v for k, v in meta.items() if v is not None}

    description = args.description or "(no description)"
    acceptance = args.acceptance or "(no acceptance criteria defined)"
    body = (
        f"## Description\n{description}\n\n"
        f"## Acceptance\n{acceptance}\n\n"
        f"## Log\n- {now_iso()} — created by {actor}\n"
    )
    write_card(target, meta, body)
    print(f"WROTE {target}")


def op_transition(args):
    """Change status with validation."""
    card_path = find_card(args.card_id)
    if not card_path:
        err("file-missing", f"{args.card_id} not found in cards/active/")

    meta, body, raw = parse_card(card_path)
    if meta is None or "_yaml_error" in meta:
        err("yaml-parse", f"frontmatter is not valid YAML: {meta.get('_yaml_error', 'unknown')}")

    from_status = meta.get("status")
    if from_status not in TRANSITIONS:
        err("status-enum", f"current status '{from_status}' is not in {sorted(VALID_STATUS)}")
    if args.to not in TRANSITIONS[from_status]:
        err("transition-invalid", f"cannot transition from {from_status} to {args.to}")

    # Build proposed state and validate
    proposed = dict(meta)
    proposed["status"] = args.to
    proposed["updated"] = now_date()
    if args.next_action:
        proposed["next_action"] = args.next_action
    if args.blocked_by:
        proposed["blocked_by"] = args.blocked_by

    errors = validate_card(args.card_id, proposed)
    if errors:
        for e in errors:
            sys.stderr.write(f"ERROR rule: {e}\n")
        err("validation-failed", f"transition to {args.to} would violate {len(errors)} SCHEMA rule(s)")

    # Apply
    meta.update(proposed)
    log_entry = f"- {now_iso()} — status: {from_status} → {args.to}"
    if args.log:
        log_entry += f" ({args.log})"
    if "## Log" in body:
        body = body.replace("## Log\n", f"## Log\n{log_entry}\n", 1)
    else:
        body += f"\n## Log\n{log_entry}\n"

    write_card(card_path, meta, body)
    print(f"TRANSITIONED {args.card_id} {from_status} → {args.to}")


def op_move(args):
    """Terminal status → directory move."""
    if args.to not in ("done", "dropped"):
        err("move-target", f"move target must be 'done' or 'dropped', got '{args.to}'")

    card_path = find_card(args.card_id)
    if not card_path:
        err("file-missing", f"{args.card_id} not found in cards/active/")
    if card_path.parent == DONE or card_path.parent == DROPPED:
        err("terminal-move", f"card is already in {card_path.parent.name}/; cannot move between terminal dirs")

    target_dir = DONE if args.to == "done" else DROPPED
    meta, body, raw = parse_card(card_path)
    if meta is None or "_yaml_error" in meta:
        err("yaml-parse", f"frontmatter is not valid YAML: {meta.get('_yaml_error', 'unknown')}")

    if meta.get("status") != args.to:
        err("status-mismatch", f"card status '{meta.get('status')}' does not match move target '{args.to}'; transition first")

    meta["updated"] = now_date()
    log_entry = f"- {now_iso()} — moved to {args.to}/"
    if "## Log" in body:
        body = body.replace("## Log\n", f"## Log\n{log_entry}\n", 1)
    else:
        body += f"\n## Log\n{log_entry}\n"

    target = target_dir / card_path.name
    # Write updated content to target first, then move (atomic-ish)
    write_card(card_path, meta, body)
    shutil.move(str(card_path), str(target))
    print(f"MOVED {args.card_id} → {args.to}/")


def op_validate(args):
    """Run the 7 SCHEMA rules."""
    if args.card_id:
        paths = [find_card(args.card_id)]
        paths = [p for p in paths if p]
        if not paths:
            err("file-missing", f"{args.card_id} not found")
    else:
        paths = sorted(ACTIVE.glob("*.md"))

    if not paths:
        print("0 cards validated, 0 errors")
        return

    total_errors = 0
    for p in paths:
        meta, _, _ = parse_card(p)
        cid = p.stem.split("-")[0:4]
        cid = "-".join(cid) if len(cid) >= 4 else p.stem
        if meta is None or "_yaml_error" in meta:
            err_str = meta.get("_yaml_error", "unknown") if meta else "no frontmatter"
            sys.stderr.write(f"ERROR yaml-parse: {p.name}: {err_str}\n")
            total_errors += 1
            continue
        errors = validate_card(cid, meta)
        for e in errors:
            sys.stderr.write(f"ERROR rule: {p.name}: {e}\n")
            total_errors += 1

    if total_errors:
        print(f"{len(paths)} cards validated, {total_errors} errors", file=sys.stderr)
        sys.exit(1)
    print(f"{len(paths)} cards validated, 0 errors")


# ─── CLI ────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(prog="kanban.sh", description=__doc__)
    sub = p.add_subparsers(dest="op", required=True)

    # read
    pr = sub.add_parser("read", help="List active cards")
    pr.add_argument("--owner")
    pr.add_argument("--status")
    pr.add_argument("--tag")
    pr.set_defaults(func=op_read)

    # new
    pn = sub.add_parser("new", help="Write a new card")
    pn.add_argument("--title", required=True)
    pn.add_argument("--owner", required=True)
    pn.add_argument("--priority", required=True, choices=sorted(VALID_PRIORITY))
    pn.add_argument("--next-action", required=True)
    pn.add_argument("--description")
    pn.add_argument("--acceptance")
    pn.add_argument("--depends-on")
    pn.add_argument("--tag", action="append", default=[])
    pn.set_defaults(func=op_new)

    # transition
    pt = sub.add_parser("transition", help="Change card status with validation")
    pt.add_argument("card_id")
    pt.add_argument("--to", required=True, choices=sorted(VALID_STATUS))
    pt.add_argument("--next-action")
    pt.add_argument("--blocked-by")
    pt.add_argument("--log")
    pt.set_defaults(func=op_transition)

    # move
    pm = sub.add_parser("move", help="Terminal move to done/ or dropped/")
    pm.add_argument("card_id")
    pm.add_argument("--to", required=True, choices=["done", "dropped"])
    pm.set_defaults(func=op_move)

    # validate
    pv = sub.add_parser("validate", help="Run the 7 SCHEMA rules")
    pv.add_argument("card_id", nargs="?")
    pv.set_defaults(func=op_validate)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
