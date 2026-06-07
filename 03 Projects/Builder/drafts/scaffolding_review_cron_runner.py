#!/usr/bin/env python3
"""scaffolding_review_cron_runner.py — Mavis Harness, daily eval-vault runner.

Source: 03 Projects/Mavis/phase_next_architecture.md §4.3
Status: DEPLOY 2026-06-07 15:42 CT (replaces the selftest-only path)

Why this exists
---------------
The cron module's __main__ block runs _selftest(), which exercises the full
review pipeline against mock stats. That is a smoke test, not the eval-vault
review. This runner is the thin live-data adapter:

    GET /stats on the harness daemon
        -> parse JSON
        -> build ScaffoldingStats (the four snapshot dataclasses)
        -> run_review(stats)        (cron module's real entry point)
        -> write_review() to vault
        -> exit 0 / non-zero

The harness daemon (com.mavis.harness, http://127.0.0.1:11435) is the
authoritative live data source. If the daemon is down, this runner exits
non-zero — the launchd log will show the connection error, and the
yesterday's-review file will be the most recent receipt.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# Live next to scaffolding_review_cron.py in ~/.mavis/bin/
sys.path.insert(0, str(Path(__file__).parent))
import scaffolding_review_cron as cron  # noqa: E402

DAEMON_URL = "http://127.0.0.1:11435/stats"
FETCH_TIMEOUT = 10  # seconds; harness /stats is local and tiny


def fetch_stats(url: str = DAEMON_URL) -> Dict[str, Any]:
    """GET /stats from the harness daemon. Raises on connection / parse failure."""
    with urllib.request.urlopen(url, timeout=FETCH_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_stats(payload: Dict[str, Any]) -> cron.ScaffoldingStats:
    """Map the daemon's /stats JSON into ScaffoldingStats. Dataclass field
    names are 1:1 with the daemon's payload keys — see mavis_harness_daemon.py
    _stats_payload() and scaffolding_review_cron.py snapshot dataclasses."""
    return cron.ScaffoldingStats(
        router=cron.RouterSnapshot(**payload["router"]),
        loader=cron.LoaderSnapshot(**payload["loader"]),
        safety=cron.SafetySnapshot(**payload["safety"]),
        cost=cron.CostSnapshot(**payload["cost"]),
    )


def main() -> int:
    try:
        payload = fetch_stats()
    except (urllib.error.URLError, ConnectionError, OSError) as exc:
        print(f"runner: harness daemon unreachable at {DAEMON_URL}: {exc!r}",
              file=sys.stderr)
        return 64  # EX_USAGE-style; signals "infrastructure not ready"
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"runner: malformed /stats payload: {exc!r}", file=sys.stderr)
        return 65  # data shape regression; the daemon or cron changed

    stats = build_stats(payload)
    review = cron.run_review(stats)  # writes vault receipt, emits event on stdout
    print(
        f"runner: review_date={review.review_date} "
        f"drift_score={review.drift_score:.3f} "
        f"band={review.band} "
        f"anomalies={len(review.anomalies)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
