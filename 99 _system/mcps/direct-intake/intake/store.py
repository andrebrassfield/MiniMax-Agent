"""
store.py — intake-log persistence.

Every drop creates a record. Stored as JSON (one file per drop) under
`99 _system/intake-log/yyyy-mm-drop-NNN.json`. The processed markdown
output also goes to `00 Inbox/` (or a permanent folder) for the model
to read directly.

This is the "audit trail" — every drop's classification, confidence,
and disposition is preserved.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)

DEFAULT_LOG_DIR = Path(
    os.environ.get(
        "INTAKE_LOG_DIR",
        "/Users/brassfieldventuresllc/MiniMax-Agent/99 _system/intake-log",
    )
)


@dataclass
class IntakeRecord:
    """A single drop's full audit trail."""

    intake_id: str
    dropped_at: str                  # ISO 8601
    source: str                      # original input (path or URL)
    type: str                        # canonical type from sniff
    converter: str                   # which converter was used
    size_bytes: int | None           # file size (None for URLs)
    status: str                      # queued | processing | ready | needs-review | rejected
    classification: str | None = None
    confidence: float | None = None
    summary: str | None = None
    suggested_tags: list[str] = field(default_factory=list)
    suggested_links: list[dict] = field(default_factory=list)
    proposed_destination: str | None = None
    rationale: str | None = None
    markdown_excerpt: str | None = None  # first 500 chars of the rendered markdown
    markdown_full_path: str | None = None  # path to the full markdown in 00 Inbox/
    error: str | None = None
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=1, ensure_ascii=False)


def make_intake_id(source: str) -> str:
    """Generate a unique intake_id from the current timestamp + a short uuid."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    short = uuid.uuid4().hex[:6]
    # Sanitize source for the id (in case we want to include it later)
    safe_source = re.sub(r"[^a-z0-9]+", "-", source.lower())[:20]
    return f"{ts}-{safe_source}-{short}"


def write_log(
    record: IntakeRecord,
    log_dir: Path = DEFAULT_LOG_DIR,
) -> Path:
    """Persist an intake record to disk as JSON.

    Returns the path to the written file.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    # Filename: <dropped_date>-<intake_id>.json
    date_part = record.dropped_at[:10] if record.dropped_at else "undated"
    fname = f"{date_part}-{record.intake_id}.json"
    path = log_dir / fname
    path.write_text(record.to_json(), encoding="utf-8")
    return path


def read_log(path: Path) -> IntakeRecord:
    """Load an intake record from disk."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return IntakeRecord(**data)


def list_pending(
    status: str | None = None,
    log_dir: Path = DEFAULT_LOG_DIR,
    limit: int = 50,
) -> list[IntakeRecord]:
    """List intake records, optionally filtered by status. Newest first."""
    if not log_dir.exists():
        return []

    records: list[IntakeRecord] = []
    for path in sorted(log_dir.glob("*.json"), reverse=True):
        try:
            rec = read_log(path)
            if status is None or status == "all" or rec.status == status:
                records.append(rec)
            if len(records) >= limit:
                break
        except Exception as e:
            log.warning("could not read intake log %s: %s", path, e)
    return records
