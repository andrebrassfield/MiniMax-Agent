#!/usr/bin/env python3
"""ea-fb-draft-approval: Telegram bridge for FB-Engine draft approval.

The mechanism: read `03 Projects/FB-Engine/drafts/` for files with
`status: open`, send each draft to Telegram via the Bot API, capture
Andre's reply (approve / deny / edit <text>), update the state file,
and move the draft to `approved/`, `archive/denied/`, or apply the
edit + move to `approved/`.

The bridge does NOT publish. It routes operator decisions to the right
folder. The Poster (`fb-poster`) consumes `approved/`.

State file: `~/.mavis/agents/mavis/crons/ea-fb-draft-approval.state.json`
(Mavis canonical). Mirrored to `~/MiniMax-Agent/99 _system/crons/`.

Cron-friendly: one cycle = propose new drafts + capture recent replies.
Idempotent: re-running doesn't double-send.

Environment:
  FB_TELEGRAM_BOT_TOKEN  — Telegram bot token (required)
  FB_TELEGRAM_CHAT_ID    — Andre's chat ID with the bot (required)
  FB_TELEGRAM_OFFSET     — optional, override the getUpdates offset

Usage:
    # One cycle: propose + capture (default cron mode)
    python3 bridge.py

    # Propose only (no reply polling)
    python3 bridge.py --propose-only

    # Capture only (no new proposals)
    python3 bridge.py --capture-only

    # Local-test: print the would-be Telegram message without sending
    python3 bridge.py --dry-run

    # Custom paths
    python3 bridge.py --drafts-dir /path/to/drafts/ --approved-dir /path/to/approved/
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------- Paths ----------

DEFAULT_STATE_DIR = Path.home() / ".mavis" / "agents" / "mavis" / "crons"
DEFAULT_VAULT = Path.home() / "MiniMax-Agent"
DEFAULT_DRAFTS = DEFAULT_VAULT / "03 Projects" / "FB-Engine" / "drafts"
DEFAULT_APPROVED = DEFAULT_VAULT / "03 Projects" / "FB-Engine" / "approved"
DEFAULT_DENIED = DEFAULT_VAULT / "03 Projects" / "FB-Engine" / "archive" / "denied"

# ---------- Telegram API ----------

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

MARKER = "[FB-Engine]"


def _telegram_call(token: str, method: str, **params) -> dict:
    """Call the Telegram Bot API. Returns the response dict, or raises.
    Uses urllib (stdlib) — no external dependencies required."""
    import urllib.parse
    import urllib.request
    import urllib.error
    url = TELEGRAM_API.format(token=token, method=method)
    try:
        req = urllib.request.Request(
            url,
            data=urllib.parse.urlencode(params).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
    except urllib.error.URLError as e:
        raise RuntimeError(f"Telegram API call failed: {e}") from e
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data.get('description', data)}")
    return data


def send_proposal(token: str, chat_id: str, draft_path: Path, body: str,
                  typology: str, source: str, ammo_summary: str) -> int:
    """Send a draft proposal to Telegram. Returns the Telegram message_id."""
    text = (
        f"{MARKER} Draft: {draft_path.stem}\n"
        f"Typology: T{typology[-1]}\n"
        f"Source: {source}\n"
        f"Ammunition: {ammo_summary}\n"
        f"\n"
        f"{body}\n"
        f"\n"
        f"Reply: approve / deny / edit <text>"
    )
    if len(text) > 4000:
        text = text[:3950] + "\n\n[... truncated; see draft file for full text ...]\n\nReply: approve / deny / edit"
    data = _telegram_call(token, "sendMessage", chat_id=chat_id, text=text)
    return int(data["result"]["message_id"])


# ---------- State file ----------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_state(state_file: Path) -> dict:
    if not state_file.exists():
        return {"last_scan_at": None, "last_update_id": 0, "proposals": []}
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"WARNING: state file corrupt ({e}); initializing fresh", file=sys.stderr)
        return {"last_scan_at": None, "last_update_id": 0, "proposals": []}


def save_state(state_file: Path, mirror_file: Path, state: dict) -> None:
    """Atomic write to canonical + mirror."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    mirror_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_file.with_suffix(f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(state_file)
    mirror_file.write_text(state_file.read_text(encoding="utf-8"), encoding="utf-8")


# ---------- Draft parsing ----------

def parse_draft_frontmatter(path: Path) -> dict | None:
    """Parse the YAML frontmatter of a draft file. Returns dict or None."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fm = text[3:end].strip()
    result: dict = {}
    for line in fm.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip()
        v = v.strip()
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        if v.startswith("|") or v.startswith(">"):
            # Block scalar — for our purposes, just store the marker
            result[k] = v
            continue
        result[k] = v
    return result


def extract_draft_body(path: Path) -> str:
    """Extract the text under '## Generated draft'."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"## Generated draft\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def extract_ammo_summary(ammo_block: str) -> str:
    """Compact summary of ammunition used."""
    if not ammo_block or ammo_block == "|":
        return "(none)"
    lines = [l.strip() for l in ammo_block.splitlines() if l.strip() and l.strip().startswith("-")]
    if not lines:
        return "(none)"
    claims = []
    for line in lines[:2]:
        # Format: - pillar=X | typology=Y | claim | source=Z
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3:
            claims.append(parts[2][:80])
    return " | ".join(claims) if claims else "(none)"


# ---------- Propose cycle ----------

def propose_new_drafts(
    drafts_dir: Path,
    state: dict,
    token: str | None,
    chat_id: str | None,
    dry_run: bool,
) -> list[Path]:
    """Find open drafts not yet proposed, send to Telegram, update state."""
    if not drafts_dir.exists():
        return []
    proposed_ids = {p["draft_id"] for p in state.get("proposals", [])}
    sent: list[Path] = []
    for draft_path in sorted(drafts_dir.glob("*.md")):
        if not draft_path.is_file():
            continue
        fm = parse_draft_frontmatter(draft_path)
        if not fm:
            continue
        if fm.get("status") != "open":
            continue
        draft_id = fm.get("draft_id") or draft_path.stem
        if draft_id in proposed_ids:
            continue
        body = extract_draft_body(draft_path)
        if not body:
            print(f"WARNING: no body in {draft_path}, skipping", file=sys.stderr)
            continue
        typology = fm.get("typology", "T2")
        source = (
            fm.get("original_author")
            or (f"reply to post {fm.get('original_post_id', 'unknown')}" if typology == "T2" else "operator hook")
        )
        ammo_summary = extract_ammo_summary(fm.get("ammunition_used", ""))
        if dry_run or not token or not chat_id:
            print(
                f"[DRY-RUN] Would send: {MARKER} {draft_id} (T{typology[-1]}) → Telegram",
                file=sys.stderr,
            )
            msg_id = 0
        else:
            try:
                msg_id = send_proposal(token, chat_id, draft_path, body, typology, source, ammo_summary)
            except Exception as e:
                print(f"ERROR: failed to send {draft_id}: {e}", file=sys.stderr)
                continue
        state["proposals"].append({
            "draft_id": draft_id,
            "source_file": str(draft_path.relative_to(drafts_dir.parent.parent)),
            "draft_path": str(draft_path),
            "typology": typology,
            "telegram_message_id": msg_id,
            "proposed_at": _now_iso(),
            "response_status": "open",
            "response_text": None,
            "responded_at": None,
            "acted_at": None,
            "action": None,
        })
        sent.append(draft_path)
        print(f"[bridge] proposed {draft_id} → Telegram (msg_id={msg_id})", file=sys.stderr)
    return sent


# ---------- Capture cycle ----------

REPLY_PATTERNS = {
    "approve": re.compile(r"^\s*(approve|approved|ship it|yes|go|\+1)\s*$", re.IGNORECASE),
    "deny": re.compile(r"^\s*(deny|denied|kill it|no|-1|skip)\s*$", re.IGNORECASE),
    "edit": re.compile(r"^\s*edit[:\s]+(.+)$", re.IGNORECASE | re.DOTALL),
}


def classify_reply(text: str) -> tuple[str, str | None]:
    """Classify a reply. Returns (action, edit_text_or_None)."""
    m = REPLY_PATTERNS["approve"].match(text)
    if m:
        return ("approve", None)
    m = REPLY_PATTERNS["deny"].match(text)
    if m:
        return ("deny", None)
    m = REPLY_PATTERNS["edit"].match(text)
    if m:
        return ("edit", m.group(1).strip())
    return ("unknown", None)


def find_open_proposal_for_reply(state: dict, reply_text: str) -> dict | None:
    """Find the open proposal this reply targets. If the reply contains
    a draft_id (e.g., 'fb-2-post-123-a1b2c3d4e5'), match that. Otherwise
    return the most recent open proposal.
    """
    open_proposals = [p for p in state.get("proposals", []) if p.get("response_status") == "open"]
    if not open_proposals:
        return None
    # Try to find a draft_id in the reply
    m = re.search(r"fb-\d-[a-z0-9-]+", reply_text)
    if m:
        target_id = m.group(0)
        for p in open_proposals:
            if p["draft_id"] == target_id or p["draft_id"].startswith(target_id):
                return p
    # Default: most recent
    return sorted(open_proposals, key=lambda p: p.get("proposed_at", ""), reverse=True)[0]


def act_on_decision(
    proposal: dict,
    action: str,
    edit_text: str | None,
    approved_dir: Path,
    denied_dir: Path,
) -> str:
    """Move the draft file based on the decision. Returns the action label."""
    src = Path(proposal["draft_path"])
    if not src.exists():
        return f"missing_source:{src}"
    if action == "approve":
        dest = approved_dir / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Update frontmatter status
        text = src.read_text(encoding="utf-8")
        text = re.sub(r"^status:\s*open\s*$", "status: approved", text, flags=re.MULTILINE)
        text = re.sub(
            r"^(approved_at:.*)$",
            f"approved_at: {_now_iso()}",
            text,
            flags=re.MULTILINE,
        )
        if "approved_at:" not in text:
            text = text.replace("status: approved\n", f"status: approved\napproved_at: {_now_iso()}\n", 1)
        dest.write_text(text, encoding="utf-8")
        src.unlink()
        return "moved_to_approved"
    if action == "deny":
        dest = denied_dir / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        text = re.sub(r"^status:\s*open\s*$", "status: denied", text, flags=re.MULTILINE)
        text = re.sub(
            r"^(denied_at:.*)$",
            f"denied_at: {_now_iso()}",
            text,
            flags=re.MULTILINE,
        )
        if "denied_at:" not in text:
            text = text.replace("status: denied\n", f"status: denied\ndenied_at: {_now_iso()}\n", 1)
        dest.write_text(text, encoding="utf-8")
        src.unlink()
        return "moved_to_denied"
    if action == "edit" and edit_text:
        dest = approved_dir / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        # Replace the body of "## Generated draft" with edit_text
        text = re.sub(
            r"(## Generated draft\s*\n).*?(?=\n## |\Z)",
            lambda m: m.group(1) + edit_text + "\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
        # Update frontmatter
        text = re.sub(r"^status:\s*open\s*$", "status: approved", text, flags=re.MULTILINE)
        text = re.sub(
            r"^(approved_at:.*)$",
            f"approved_at: {_now_iso()}",
            text,
            flags=re.MULTILINE,
        )
        if "approved_at:" not in text:
            text = text.replace("status: approved\n", f"status: approved\napproved_at: {_now_iso()}\n", 1)
        # Add an edit marker
        text = re.sub(
            r"^(ammunition_used:.*?\n(?:  - .*?\n)*)",
            r"\1edited_by: Andre (via Telegram)\n",
            text,
            count=1,
            flags=re.MULTILINE,
        )
        dest.write_text(text, encoding="utf-8")
        src.unlink()
        return "edited_and_moved_to_approved"
    return f"unknown_action:{action}"


def capture_replies(
    state: dict,
    token: str | None,
    approved_dir: Path,
    denied_dir: Path,
    dry_run: bool,
) -> int:
    """Poll Telegram for replies, match to open proposals, take action.

    Returns the number of proposals acted on.
    """
    if not token:
        return 0
    offset = int(state.get("last_update_id", 0)) + 1
    try:
        data = _telegram_call(token, "getUpdates", offset=offset, timeout=0, allowed_updates=["message"])
    except Exception as e:
        print(f"ERROR: getUpdates failed: {e}", file=sys.stderr)
        return 0
    acted = 0
    for update in data.get("result", []):
        update_id = int(update["update_id"])
        state["last_update_id"] = max(state.get("last_update_id", 0), update_id)
        msg = update.get("message") or update.get("edited_message")
        if not msg:
            continue
        text = (msg.get("text") or "").strip()
        if not text:
            continue
        # Filter: only process replies that contain the marker, or are direct
        # replies to one of our proposals
        if MARKER.lower() not in text.lower() and not re.search(r"fb-\d-", text):
            continue
        # Skip our own outgoing messages (which contain MARKER)
        if MARKER in text:
            continue
        action, edit_text = classify_reply(text)
        if action == "unknown":
            continue
        proposal = find_open_proposal_for_reply(state, text)
        if not proposal:
            continue
        if dry_run:
            result_label = f"DRY-RUN {action} on {proposal['draft_id']}"
        else:
            result_label = act_on_decision(proposal, action, edit_text, approved_dir, denied_dir)
        proposal["response_status"] = "approved" if action == "approve" else (
            "denied" if action == "deny" else "edited"
        )
        proposal["response_text"] = text
        proposal["responded_at"] = _now_iso()
        proposal["acted_at"] = _now_iso()
        proposal["action"] = result_label
        print(f"[bridge] {action} → {proposal['draft_id']} ({result_label})", file=sys.stderr)
        acted += 1
    return acted


# ---------- Entry point ----------

def main() -> int:
    parser = argparse.ArgumentParser(description="FB-Engine Telegram bridge (draft approval)")
    parser.add_argument("--drafts-dir", type=Path, default=DEFAULT_DRAFTS)
    parser.add_argument("--approved-dir", type=Path, default=DEFAULT_APPROVED)
    parser.add_argument("--denied-dir", type=Path, default=DEFAULT_DENIED)
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE_DIR / "ea-fb-draft-approval.state.json")
    parser.add_argument("--mirror-file", type=Path,
                        default=DEFAULT_VAULT / "99 _system" / "crons" / "ea-fb-draft-approval.state.json")
    parser.add_argument("--propose-only", action="store_true")
    parser.add_argument("--capture-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print actions without sending Telegram / moving files")
    args = parser.parse_args()

    token = os.environ.get("FB_TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("FB_TELEGRAM_CHAT_ID")
    if not args.dry_run and (not token or not chat_id):
        print(
            "ERROR: FB_TELEGRAM_BOT_TOKEN and FB_TELEGRAM_CHAT_ID must be set "
            "(or use --dry-run)",
            file=sys.stderr,
        )
        return 1

    state = load_state(args.state_file)

    proposed = []
    if not args.capture_only:
        proposed = propose_new_drafts(args.drafts_dir, state, token, chat_id, args.dry_run)

    acted = 0
    if not args.propose_only:
        acted = capture_replies(state, token, args.approved_dir, args.denied_dir, args.dry_run)

    state["last_scan_at"] = _now_iso()
    if not args.dry_run:
        save_state(args.state_file, args.mirror_file, state)

    print(
        f"[ea-fb-draft-approval] proposed={len(proposed)} acted={acted} → {args.state_file}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
