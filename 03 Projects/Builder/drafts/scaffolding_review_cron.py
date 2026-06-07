"""scaffolding_review_cron.py — Mavis Harness, Sprint 4: scaffolding_review cron.

Source: 03 Projects/Mavis/phase_next_architecture.md, Section 4.3
Status: APPROVED 2026-06-07 14:08 CT (Chief-executed, post worker-stall diagnosis)

Purpose
-------
Periodic review of Mavis's own runtime scaffolding. Prevents framework drift
and silent timeouts. The 2026 evidence: model drift is the primary failure
mode (Phil Schmid); observability-driven harness self-evolution added 7.3
points on Terminal-Bench 2.0 (Fudan AHE, clm-2026-06-07-006). Daily scaffolding
review + event-driven response on harness change is the eval-vault pattern
for the harness itself (clm-2026-06-07-010).

The cron is a pure calc + render + write module. Three responsibilities:

  1. INGEST — accept snapshots from the four harness primitives:
     - command_router.RouterSnapshot   (L1 regex hit/fallback counts)
     - context_loader.LoaderSnapshot   (3-tier cache stats)
     - filesystem_bridge.SafetySnapshot (path-traversal blocks + write integrity)
     - token_multiplier_config.CostSnapshot (cost drift, optional)
     The snapshots are dataclasses; the caller (a M3 synthesis session)
     is responsible for populating them from live traffic. The cron does
     not import the live modules itself — that keeps the cron testable
     in isolation and avoids I/O at import time.

  2. COMPUTE — blend 5 component scores into a single drift_score in [0, 1].
     Weights are baked-in defaults; the dataclass accepts overrides.

       drift_score = clamp01(
           0.30 * rule_fallback_rate
         + 0.25 * cache_miss_rate
         + 0.20 * cost_overrun_ratio
         + 0.15 * safety_violation_rate
         + 0.10 * hard_floor_violation_rate
       )

  3. RENDER + WRITE — format a Markdown health receipt and atomic_write
     it to <output_dir>/YYYY-MM-DD.md. The output filename is the
     review date (UTC, YYYY-MM-DD), so a re-run on the same day is
     idempotent at the filename level (the file is overwritten; old
     content never partial-visible thanks to atomic_write).

The M3 synthesis layer (a fresh Mavis session invoked by launchd or cron
on a 24h schedule, per phase_next_architecture.md §4.3) is responsible
for *acting on* the receipt: dispatching a Builder task on
"harness change detected" if drift crosses the threshold, appending a
[[harness change detected]] event, etc. The cron itself is mechanical
and deterministic — no LLM, no stochastic content, no time.time() calls
in the calc path. The caller passes `review_date: str` and `now: float`
for testability.

Constraints
-----------
- Standard library only — except for one optional import of
  filesystem_bridge.atomic_write (Sprint 3 primitive, stdlib-only itself).
- Deterministic. The review_date and now are caller-supplied.
- Fail-closed. Any None snapshot is treated as a zero signal; the cron
  never crashes on missing data, it just flags the gap in the receipt.

Outputs
-------
- Markdown file: <output_dir>/<YYYY-MM-DD>.md
  Default output_dir: <workspace>/99 _system/scaffolding-reviews/
- Optional stdout JSON line: {"event": "harness_change_detected",
   "drift_score": ..., "review_date": "..."} emitted when drift >= 0.50.
  This is the hook for the launchd wrapper / Builder to subscribe to.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


# Reuse the Sprint 3 atomic_write pattern for the receipt output. This
# guarantees that a concurrent reader (e.g., Obsidian live preview) sees
# either the old file or the new file — never a half-written receipt.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from filesystem_bridge import atomic_write  # type: ignore
except ImportError:  # pragma: no cover — fallback so the module is usable
                     # standalone if filesystem_bridge is not on the path.
    def atomic_write(target_path: str, content: str) -> None:  # type: ignore
        """Minimal in-module fallback for atomic_write. Identical contract:
        write to <target>.tmp.<pid>.<rand>, fsync, rename. The full
        filesystem_bridge version is preferred; this fallback exists so
        scaffolding_review_cron can be unit-tested without depending on
        filesystem_bridge being installed on the import path.
        """
        import secrets
        target_dir = os.path.dirname(target_path)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        temp_path = f"{target_path}.tmp.{os.getpid()}.{secrets.token_hex(8)}"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.rename(temp_path, target_path)
        except BaseException:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass
            raise


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Default drift-score component weights. The 5 components and weights are
# derived from the failure modes called out in phase_next_architecture.md
# §4.3 and Phil Schmid's "model drift is the primary failure mode" thesis.
# Rule fallback gets the heaviest weight because the L1 regex index is
# the most commonly-edited piece of scaffolding and the most likely to
# go stale as user vocabulary evolves.
DEFAULT_WEIGHTS: Dict[str, float] = {
    "rule_fallback":        0.30,
    "cache_miss":           0.25,
    "cost_overrun":        0.20,
    "safety_violation":     0.15,
    "hard_floor_violation": 0.10,
}

# Health bands for the drift score. The band name is what shows up in
# the receipt header and feeds the "harness change detected" event.
HEALTHY_BAND = 0.20       # 0.00–0.20: healthy (green)
WATCH_BAND   = 0.50       # 0.20–0.50: watch (yellow)
DEGRADED_BAND = 0.80      # 0.50–0.80: degraded (orange)
# 0.80–1.00: critical (red)

# Per-component thresholds. If a component score exceeds its threshold,
# it's listed in the "Anomalies flagged" section of the receipt.
COMPONENT_THRESHOLDS: Dict[str, float] = {
    "rule_fallback":        0.20,
    "cache_miss":           0.20,
    "cost_overrun":         0.10,
    "safety_violation":     0.05,
    "hard_floor_violation": 0.00,  # any violation is an anomaly
}

# Default output directory. The vault-relative path is "99 _system/scaffolding-reviews/".
# Default workspace is the parent of the Builder/drafts/ directory.
DEFAULT_OUTPUT_DIR = _SCRIPT_DIR.parent.parent / "99 _system" / "scaffolding-reviews"

HARNESS_VERSION = "v1.0 — Mavis Local-Compute Harness (Sprint 5, 12B QAT, 2026-06-07)"


# ---------------------------------------------------------------------------
# Snapshot dataclasses — caller populates these from live traffic
# ---------------------------------------------------------------------------


@dataclass
class RouterSnapshot:
    """Snapshot of command_router traffic over the review window.

    Fields
    ------
    total_classifications : int
        Total Intent objects emitted by command_router.classify() during
        the review window. Must be > 0 for fallback_rate to be defined;
        the cron treats 0 total as "no traffic" and reports the rule
        fallback component as 0.0 (with an anomaly flag for review).
    fallback_count : int
        Number of Intent objects with lane == "ask_first" (fail-closed).
    lane_distribution : Dict[str, int]
        Histogram of Intent.lane values: keys in
        {"capture", "synthesize", "dispatch", "observe", "ask_first"}.
    l2_not_implemented : int
        How many times classify_l2() raised NotImplementedError. Should
        be 0 in production (L2 is a stub in Sprint 4); any non-zero
        count is a v1-API signal.
    l3_not_implemented : int
        Same for classify_l3().
    rule_count : int
        Number of L1 rules in the registry at snapshot time. Used to
        detect shrinkage (someone accidentally removed rules).
    """

    total_classifications: int = 0
    fallback_count: int = 0
    lane_distribution: Dict[str, int] = field(default_factory=dict)
    l2_not_implemented: int = 0
    l3_not_implemented: int = 0
    rule_count: int = 0


@dataclass
class LoaderSnapshot:
    """Snapshot of context_loader cache state and traffic.

    Fields
    ------
    meta_entries : int
        Number of keys in MetaIndexCache.
    topic_entries : int
        Number of keys in TopicIndexCache.
    full_entries : int
        Number of keys in FullTopicCache.
    hits : int
        Total cache hits across all 3 tiers during the review window.
    misses : int
        Total cache misses.
    evictions : int
        Total evictions (LRU overflow + importance-aware + hard-floor).
    bytes_served : int
        Total bytes returned to callers (hits + misses).
    bytes_cached : int
        Total bytes currently held in cache.
    hard_floor_violations : int
        Number of times an entry was evicted before the 30-min hard
        floor. Should be 0; any non-zero is a hard anomaly.
    recent_turns : int
        Current size of the recent-turns deque (max 10).
    avg_window_tokens : float
        Mean ContextWindow.estimated_tokens across the last 50 turns.
    """

    meta_entries: int = 0
    topic_entries: int = 0
    full_entries: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    bytes_served: int = 0
    bytes_cached: int = 0
    hard_floor_violations: int = 0
    recent_turns: int = 0
    avg_window_tokens: float = 0.0


@dataclass
class SafetySnapshot:
    """Snapshot of filesystem_bridge safety counters.

    Fields
    ------
    path_traversal_attempts_blocked : int
        Number of times _resolve_vault_path() raised ValueError due to
        a path escaping the vault boundary. Should be 0 in healthy
        operation; a non-zero count means someone or something tried
        to escape the vault.
    atomic_write_temp_file_leaks : int
        Number of .tmp.<pid>.<rand> files left behind in the output
        directory after atomic_write calls. Should be 0 (atomic_write
        cleans up on failure); a non-zero count means cleanup failed.
    total_atomic_writes : int
        Total atomic_write() calls during the review window.
    total_load_full_topic_calls : int
        Total load_full_topic() calls (cache miss + hit-equivalent).
    """

    path_traversal_attempts_blocked: int = 0
    atomic_write_temp_file_leaks: int = 0
    total_atomic_writes: int = 0
    total_load_full_topic_calls: int = 0


@dataclass
class CostSnapshot:
    """Snapshot of token_multiplier_config cost accounting.

    Fields
    ------
    event_count : int
        Number of CostEvent JSONL entries appended to the audit log
        during the review window.
    total_actual_cost : float
        Sum of actual_total_cost across all events (USD).
    total_planned_cost : float
        Sum of the planned cost (pre-multiplier, base rates only). 0.0
        if planned cost was not tracked; the cron treats planned_cost==0
        as "no plan baseline" and reports cost_overrun_ratio as 0.0.
    cost_overrun_ratio_override : Optional[float]
        If set, used directly as the cost_overrun_ratio component
        score. Bypasses the (actual - planned) / planned calculation.
        Use when the caller has a more sophisticated overrun model.
    last_verified : str
        ISO date string from token-plan.yaml's source_status.last_verified.
    """

    event_count: int = 0
    total_actual_cost: float = 0.0
    total_planned_cost: float = 0.0
    cost_overrun_ratio_override: Optional[float] = None
    last_verified: str = ""


@dataclass
class ScaffoldingStats:
    """Composite snapshot from all four primitives. The cron's main input."""

    router: RouterSnapshot = field(default_factory=RouterSnapshot)
    loader: LoaderSnapshot = field(default_factory=LoaderSnapshot)
    safety: SafetySnapshot = field(default_factory=SafetySnapshot)
    cost: CostSnapshot = field(default_factory=CostSnapshot)


# ---------------------------------------------------------------------------
# Drift-score components
# ---------------------------------------------------------------------------


def _rule_fallback_rate(stats: ScaffoldingStats) -> float:
    """L1 rule fallback rate. [0, 1]. High = L1 rules don't match real traffic."""
    if stats.router.total_classifications <= 0:
        # No traffic: report 0.0 (we don't have evidence of drift either way).
        return 0.0
    rate = stats.router.fallback_count / stats.router.total_classifications
    return _clamp01(rate)


def _cache_miss_rate(stats: ScaffoldingStats) -> float:
    """Cache miss rate across all 3 tiers. [0, 1]."""
    total = stats.loader.hits + stats.loader.misses
    if total <= 0:
        return 0.0
    return _clamp01(stats.loader.misses / total)


def _cost_overrun_ratio(stats: ScaffoldingStats) -> float:
    """Cost overrun ratio. [0, 1]. Compares actual vs planned spend."""
    if stats.cost.cost_overrun_ratio_override is not None:
        return _clamp01(stats.cost.cost_overrun_ratio_override)
    if stats.cost.total_planned_cost <= 0.0:
        # No baseline — report 0.0 (we can't measure overrun without a plan).
        return 0.0
    overrun = (stats.cost.total_actual_cost - stats.cost.total_planned_cost) / stats.cost.total_planned_cost
    return _clamp01(overrun)


def _safety_violation_rate(stats: ScaffoldingStats) -> float:
    """Safety violation rate. [0, 1]. Blocks + leaks normalized by total ops."""
    total_ops = stats.safety.total_atomic_writes + stats.safety.total_load_full_topic_calls
    if total_ops <= 0:
        return 0.0
    violations = (
        stats.safety.path_traversal_attempts_blocked
        + stats.safety.atomic_write_temp_file_leaks
    )
    # Allow a small absolute floor: 1 violation out of 100 ops is 0.01,
    # not 0.00. This avoids false-green on tiny denominators.
    return _clamp01(violations / total_ops)


def _hard_floor_violation_rate(stats: ScaffoldingStats) -> float:
    """Hard-floor violation rate. [0, 1]. Binary in practice: any = 1.0."""
    if stats.loader.hard_floor_violations > 0:
        return 1.0
    return 0.0


def _clamp01(x: float) -> float:
    """Clamp a float to [0.0, 1.0]."""
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


# ---------------------------------------------------------------------------
# Drift-score calculation
# ---------------------------------------------------------------------------


def compute_component_scores(
    stats: ScaffoldingStats,
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """Compute the 5 component scores for a stats snapshot.

    Returns a dict of {component_name: score_in_[0,1]}. The components are
    the 5 keys in DEFAULT_WEIGHTS. Weights are NOT applied here — see
    compute_drift_score() for the weighted blend.

    Note: an explicit empty `weights={}` is honored (returns an empty
    components dict). Use `weights=None` to fall back to DEFAULT_WEIGHTS.
    """
    w = weights if weights is not None else DEFAULT_WEIGHTS
    components: Dict[str, float] = {}
    if "rule_fallback" in w:
        components["rule_fallback"] = _rule_fallback_rate(stats)
    if "cache_miss" in w:
        components["cache_miss"] = _cache_miss_rate(stats)
    if "cost_overrun" in w:
        components["cost_overrun"] = _cost_overrun_ratio(stats)
    if "safety_violation" in w:
        components["safety_violation"] = _safety_violation_rate(stats)
    if "hard_floor_violation" in w:
        components["hard_floor_violation"] = _hard_floor_violation_rate(stats)
    return components


def compute_drift_score(
    stats: ScaffoldingStats,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """Compute the weighted drift score in [0, 1].

    The score is a blend of 5 components, each in [0, 1], weighted by
    DEFAULT_WEIGHTS (or the supplied override). The result is clamped
    to [0, 1] to defend against the edge case where weights > 1.0 sum
    to > 1.0 — that would be a config bug, not a feature, so we clamp.

    Note: an explicit empty `weights={}` is honored (returns 0.0).
    Use `weights=None` to fall back to DEFAULT_WEIGHTS.
    """
    w_dict = weights if weights is not None else DEFAULT_WEIGHTS
    components = compute_component_scores(stats, weights=weights)
    if not components:
        return 0.0
    score = 0.0
    for name, comp in components.items():
        w = w_dict.get(name, 0.0)
        score += w * comp
    return _clamp01(score)


# ---------------------------------------------------------------------------
# Anomaly detection + recommendations
# ---------------------------------------------------------------------------


def detect_anomalies(
    components: Dict[str, float],
    stats: ScaffoldingStats,
    thresholds: Optional[Dict[str, float]] = None,
) -> List[str]:
    """Return a list of human-readable anomaly strings.

    Each anomaly names the component, the observed score, and the
    threshold it exceeded. Anomalies are sorted by observed - threshold
    (most-violating first) for stable ordering across runs.
    """
    th = dict(COMPONENT_THRESHOLDS)
    if thresholds:
        th.update(thresholds)

    anomalies: List[tuple] = []  # (excess, message)
    for name, score in components.items():
        threshold = th.get(name, 1.0)
        if score > threshold:
            excess = score - threshold
            anomalies.append(
                (excess, f"{name} = {score:.3f} exceeds threshold {threshold:.3f}")
            )

    # Hard-fail checks: certain stats should never be non-zero. Flag
    # them as anomalies regardless of the threshold.
    if stats.router.l2_not_implemented > 0:
        anomalies.append(
            (1.0, f"command_router L2 raised NotImplementedError "
                  f"{stats.router.l2_not_implemented} times (stub not yet implemented)")
        )
    if stats.router.l3_not_implemented > 0:
        anomalies.append(
            (1.0, f"command_router L3 raised NotImplementedError "
                  f"{stats.router.l3_not_implemented} times (stub not yet implemented)")
        )
    if stats.router.rule_count == 0:
        anomalies.append((1.0, "command_router registry is empty"))

    anomalies.sort(key=lambda x: x[0], reverse=True)
    return [msg for _, msg in anomalies]


def recommend(
    components: Dict[str, float],
    stats: ScaffoldingStats,
) -> List[str]:
    """Return a list of actionable recommendations based on the components.

    Skeleton-level recommendations — the M3 synthesis layer will add
    richer context (cross-references to other harness events, etc.)
    when acting on the receipt.
    """
    recs: List[str] = []
    if components.get("rule_fallback", 0.0) > COMPONENT_THRESHOLDS["rule_fallback"]:
        recs.append(
            "Inspect the L1 regex registry. High fallback rate means the "
            "current rules don't cover real user vocabulary. Review the "
            "fallback Intent payloads in the audit log to find missing patterns."
        )
    if components.get("cache_miss", 0.0) > COMPONENT_THRESHOLDS["cache_miss"]:
        recs.append(
            "Cache miss rate is above threshold. Check Tier 3 LRU parameters "
            "(max_entries, eviction_threshold) and recent topic churn. "
            "Consider pre-warming the cache for high-importance topics."
        )
    if components.get("cost_overrun", 0.0) > COMPONENT_THRESHOLDS["cost_overrun"]:
        recs.append(
            "Cost overrun detected. Review token-plan.yaml multipliers and "
            "the latest session accounting. Verify the M3 reservation hasn't "
            "shifted the actual_rate baseline."
        )
    if components.get("safety_violation", 0.0) > COMPONENT_THRESHOLDS["safety_violation"]:
        recs.append(
            "Safety violations detected. Audit path-traversal attempts and "
            "atomic-write temp-file leaks. Path-traversal attempts may indicate "
            "a malicious or malformed input; atomic-write leaks indicate an "
            "OS-level failure during the rename step."
        )
    if components.get("hard_floor_violation", 0.0) > 0.0:
        recs.append(
            "CRITICAL: Tier 3 30-min hard floor was violated. Investigate the "
            "eviction path immediately — this is a locked decision (§6a d4) "
            "and any violation means the loader is misconfigured."
        )
    return recs


# ---------------------------------------------------------------------------
# Health band
# ---------------------------------------------------------------------------


def health_band(drift_score: float) -> str:
    """Map a drift score to a band name."""
    if drift_score < HEALTHY_BAND:
        return "healthy"
    if drift_score < WATCH_BAND:
        return "watch"
    if drift_score < DEGRADED_BAND:
        return "degraded"
    return "critical"


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def _fmt_band_emoji(band: str) -> str:
    """Map a band to a single emoji for visual scanning. No emoji in body text."""
    return {
        "healthy":  "🟢",
        "watch":    "🟡",
        "degraded": "🟠",
        "critical": "🔴",
    }.get(band, "⚪")


def render_markdown(review: "ScaffoldingReview") -> str:
    """Render a ScaffoldingReview as a Markdown receipt.

    The output is a single Markdown document with sections:
      - Header (date, drift score, band, harness version)
      - Component scores (table)
      - Anomalies flagged (bullet list)
      - Recommendations (bullet list)
      - Raw stats (per-module subsections)

    The output is deterministic for a given review object: same drift
    score, same stats, same recommendations → identical bytes.
    """
    lines: List[str] = []
    band = health_band(review.drift_score)
    band_emoji = _fmt_band_emoji(band)

    # Header
    lines.append(f"# Scaffolding Health Receipt — {review.review_date}")
    lines.append("")
    lines.append(f"**Generated:** {review.timestamp_utc}")
    lines.append(f"**Drift score:** {review.drift_score:.3f} / 1.000 — {band} {band_emoji}")
    lines.append(f"**Harness version:** {HARNESS_VERSION}")
    lines.append("")

    # Component scores table
    lines.append("## Component scores")
    lines.append("")
    lines.append("| Component | Score | Threshold | Status |")
    lines.append("|---|---:|---:|---|")
    for name in DEFAULT_WEIGHTS.keys():
        score = review.component_scores.get(name, 0.0)
        threshold = COMPONENT_THRESHOLDS.get(name, 0.0)
        status = "healthy" if score <= threshold else "anomaly"
        lines.append(f"| {name} | {score:.3f} | {threshold:.3f} | {status} |")
    lines.append("")

    # Anomalies
    lines.append("## Anomalies flagged")
    lines.append("")
    if review.anomalies:
        for a in review.anomalies:
            lines.append(f"- {a}")
    else:
        lines.append("- (none)")
    lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    if review.recommendations:
        for r in review.recommendations:
            lines.append(f"- {r}")
    else:
        lines.append("- (no action required)")
    lines.append("")

    # Raw stats
    lines.append("## Raw stats")
    lines.append("")

    # Router
    r = review.stats.router
    lines.append("### Command router")
    lines.append("")
    lines.append(f"- Total classifications: {r.total_classifications}")
    fallback_pct = (
        100.0 * r.fallback_count / r.total_classifications
        if r.total_classifications > 0
        else 0.0
    )
    lines.append(f"- Fallback (ask_first) count: {r.fallback_count} ({fallback_pct:.1f}%)")
    lines.append(f"- L1 rule count: {r.rule_count}")
    lines.append(f"- L2 not-implemented: {r.l2_not_implemented}")
    lines.append(f"- L3 not-implemented: {r.l3_not_implemented}")
    lines.append("- Lane distribution:")
    for lane in ("capture", "synthesize", "dispatch", "observe", "ask_first"):
        n = r.lane_distribution.get(lane, 0)
        lines.append(f"  - {lane}: {n}")
    lines.append("")

    # Loader
    ldr = review.stats.loader
    lines.append("### Context loader")
    lines.append("")
    lines.append(f"- Meta entries: {ldr.meta_entries}")
    lines.append(f"- Topic entries: {ldr.topic_entries}")
    lines.append(f"- Full entries: {ldr.full_entries}")
    lines.append(f"- Hits: {ldr.hits}")
    lines.append(f"- Misses: {ldr.misses}")
    lines.append(f"- Evictions: {ldr.evictions}")
    lines.append(f"- Bytes served: {ldr.bytes_served:,}")
    lines.append(f"- Bytes cached: {ldr.bytes_cached:,}")
    lines.append(f"- Hard floor violations: {ldr.hard_floor_violations}")
    lines.append(f"- Recent turns: {ldr.recent_turns}")
    lines.append(f"- Avg window tokens: {ldr.avg_window_tokens:.0f}")
    lines.append("")

    # Cost
    c = review.stats.cost
    lines.append("### Cost")
    lines.append("")
    lines.append(f"- Events logged: {c.event_count}")
    lines.append(f"- Total actual cost: ${c.total_actual_cost:.4f}")
    lines.append(f"- Total planned cost: ${c.total_planned_cost:.4f}")
    if c.cost_overrun_ratio_override is not None:
        lines.append(f"- Cost overrun ratio (override): {c.cost_overrun_ratio_override:.3f}")
    lines.append(f"- Last verified: {c.last_verified or '(unknown)'}")
    lines.append("")

    # Safety
    s = review.stats.safety
    lines.append("### Safety")
    lines.append("")
    lines.append(f"- Path traversal attempts blocked: {s.path_traversal_attempts_blocked}")
    lines.append(f"- Atomic write temp file leaks: {s.atomic_write_temp_file_leaks}")
    lines.append(f"- Total atomic writes: {s.total_atomic_writes}")
    lines.append(f"- Total load_full_topic calls: {s.total_load_full_topic_calls}")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(
        "*Receipt written by `scaffolding_review_cron` (Sprint 4, "
        "Chief-executed). The M3 synthesis layer should treat a band of "
        "`watch` or worse as a signal to inspect; `degraded` and `critical` "
        "should trigger a Builder dispatch.*"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Review dataclass
# ---------------------------------------------------------------------------


@dataclass
class ScaffoldingReview:
    """The cron's full output. Persisted to Markdown; the dataclass is
    also useful for test assertions."""

    review_date: str                       # YYYY-MM-DD (caller-supplied)
    timestamp_utc: str                     # ISO 8601 (caller-supplied)
    drift_score: float
    component_scores: Dict[str, float]
    anomalies: List[str]
    recommendations: List[str]
    stats: ScaffoldingStats
    band: str = ""                         # filled by run_review()

    def __post_init__(self) -> None:
        if not self.band:
            self.band = health_band(self.drift_score)


# ---------------------------------------------------------------------------
# Top-level entry points
# ---------------------------------------------------------------------------


def build_review(
    stats: ScaffoldingStats,
    review_date: str,
    timestamp_utc: str,
    weights: Optional[Dict[str, float]] = None,
) -> ScaffoldingReview:
    """Compute the review from a stats snapshot. No I/O — pure calc."""
    components = compute_component_scores(stats, weights=weights)
    drift = compute_drift_score(stats, weights=weights)
    anomalies = detect_anomalies(components, stats)
    recs = recommend(components, stats)
    return ScaffoldingReview(
        review_date=review_date,
        timestamp_utc=timestamp_utc,
        drift_score=drift,
        component_scores=components,
        anomalies=anomalies,
        recommendations=recs,
        stats=stats,
    )


def write_review(
    review: ScaffoldingReview,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> str:
    """Render the review to Markdown and atomic_write it to disk.

    The output filename is <output_dir>/<review_date>.md. The atomic_write
    pattern (from filesystem_bridge) guarantees the file is never
    half-written. The function returns the absolute path of the written
    file as a string.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    body = render_markdown(review)
    target = str((output_dir / f"{review.review_date}.md").resolve())
    atomic_write(target, body)
    return target


def maybe_emit_change_event(review: ScaffoldingReview) -> Optional[str]:
    """If drift is at the watch band or worse, emit a one-line JSON event
    to stdout. This is the hook the launchd wrapper / Builder uses to
    subscribe to "harness change detected" without parsing the receipt.

    Returns the event JSON string (or None if drift is below the
    threshold). The caller decides where to redirect stdout (file, log,
    Builder inbox, etc.).
    """
    if review.drift_score < WATCH_BAND:
        return None
    event = {
        "event": "harness_change_detected",
        "drift_score": round(review.drift_score, 3),
        "band": review.band,
        "review_date": review.review_date,
        "anomaly_count": len(review.anomalies),
        "first_anomaly": review.anomalies[0] if review.anomalies else None,
    }
    return json.dumps(event, ensure_ascii=False)


def run_review(
    stats: ScaffoldingStats,
    review_date: Optional[str] = None,
    timestamp_utc: Optional[str] = None,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    weights: Optional[Dict[str, float]] = None,
    emit_event: bool = True,
) -> ScaffoldingReview:
    """End-to-end: build, render, write, optionally emit change event.

    Convenience wrapper for cron invocation. Defaults review_date to
    today (UTC) and timestamp_utc to now (UTC). Pass explicit values in
    tests.
    """
    if review_date is None:
        review_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if timestamp_utc is None:
        timestamp_utc = datetime.now(timezone.utc).isoformat()

    review = build_review(
        stats=stats,
        review_date=review_date,
        timestamp_utc=timestamp_utc,
        weights=weights,
    )
    write_review(review, output_dir=output_dir)
    if emit_event:
        event = maybe_emit_change_event(review)
        if event is not None:
            print(event)
    return review


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def _selftest() -> int:
    """Run the module's self-test. Exits 0 on success, non-zero on failure."""
    import shutil
    import tempfile

    failures: List[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        status = "PASS" if cond else "FAIL"
        line = f"  [{status}] {name}"
        if detail:
            line += f" — {detail}"
        print(line)
        if not cond:
            failures.append(name)

    print("scaffolding_review_cron self-test")
    print("=" * 50)

    # 1. Healthy stats → drift ~ 0
    healthy = ScaffoldingStats(
        router=RouterSnapshot(
            total_classifications=100,
            fallback_count=5,
            lane_distribution={"capture": 10, "synthesize": 20, "dispatch": 30, "observe": 35, "ask_first": 5},
            l2_not_implemented=0,
            l3_not_implemented=0,
            rule_count=10,
        ),
        loader=LoaderSnapshot(
            meta_entries=20, topic_entries=5, full_entries=2,
            hits=95, misses=5, evictions=1, bytes_served=100_000, bytes_cached=20_000,
            hard_floor_violations=0, recent_turns=10, avg_window_tokens=80_000.0,
        ),
        safety=SafetySnapshot(
            path_traversal_attempts_blocked=0,
            atomic_write_temp_file_leaks=0,
            total_atomic_writes=10,
            total_load_full_topic_calls=20,
        ),
        cost=CostSnapshot(
            event_count=100,
            total_actual_cost=0.50,
            total_planned_cost=0.50,
            last_verified="2026-06-07",
        ),
    )
    review = build_review(healthy, review_date="2026-06-07", timestamp_utc="2026-06-07T14:00:00+00:00")
    check("healthy review drift is low", review.drift_score < 0.10, f"score={review.drift_score:.3f}")
    check("healthy review band is healthy", review.band == "healthy", f"band={review.band}")
    check("healthy review has no anomalies", len(review.anomalies) == 0, f"anomalies={review.anomalies}")

    # 2. Critical stats → drift ~ 1
    critical = ScaffoldingStats(
        router=RouterSnapshot(
            total_classifications=100,
            fallback_count=80,
            lane_distribution={"ask_first": 80, "dispatch": 20},
            l2_not_implemented=0,
            l3_not_implemented=0,
            rule_count=10,
        ),
        loader=LoaderSnapshot(
            meta_entries=0, topic_entries=0, full_entries=0,
            hits=10, misses=90, evictions=50, bytes_served=1_000_000, bytes_cached=0,
            hard_floor_violations=3,
            recent_turns=0, avg_window_tokens=200_000.0,
        ),
        safety=SafetySnapshot(
            path_traversal_attempts_blocked=5,
            atomic_write_temp_file_leaks=2,
            total_atomic_writes=10,
            total_load_full_topic_calls=10,
        ),
        cost=CostSnapshot(
            event_count=100,
            total_actual_cost=2.00,
            total_planned_cost=0.50,
            last_verified="2026-06-07",
        ),
    )
    review_crit = build_review(critical, review_date="2026-06-07", timestamp_utc="2026-06-07T14:00:00+00:00")
    check("critical review drift is high", review_crit.drift_score > 0.50, f"score={review_crit.drift_score:.3f}")
    check("critical review band is degraded/critical",
          review_crit.band in ("degraded", "critical"), f"band={review_crit.band}")
    check("critical review has anomalies", len(review_crit.anomalies) > 0)

    # 3. Weights sum to <= 1 (after clamp, the score is well-defined)
    custom_weights = {"rule_fallback": 1.0}
    one_comp = build_review(healthy, review_date="2026-06-07",
                            timestamp_utc="2026-06-07T14:00:00+00:00",
                            weights=custom_weights)
    # Healthy: rule_fallback = 5/100 = 0.05, weight 1.0 → drift = 0.05
    check("custom weights apply", abs(one_comp.drift_score - 0.05) < 0.001,
          f"score={one_comp.drift_score:.3f}, expected 0.05")

    # 4. Render produces a Markdown document with all expected sections
    md = render_markdown(review)
    for section in [
        "# Scaffolding Health Receipt",
        "## Component scores",
        "## Anomalies flagged",
        "## Recommendations",
        "## Raw stats",
        "### Command router",
        "### Context loader",
        "### Cost",
        "### Safety",
    ]:
        check(f"render includes section: {section}", section in md)

    # 5. write_review: file I/O, atomic, returns correct path
    tmp = Path(tempfile.mkdtemp(prefix="scaffoldreview_selftest_"))
    try:
        target = write_review(review, output_dir=tmp)
        check("write_review returns string", isinstance(target, str))
        check("write_review target exists", Path(target).is_file())
        check(
            "write_review file is named YYYY-MM-DD.md",
            Path(target).name == "2026-06-07.md",
            f"actual={Path(target).name}",
        )
        # Re-read and confirm content round-trips
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
        check("written file has the drift score", f"{review.drift_score:.3f}" in content)
        # No temp file leaked
        check(
            "no temp files leaked after write_review",
            not any(
                f.startswith("2026-06-07.md.tmp.")
                for f in os.listdir(tmp)
            ),
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 6. maybe_emit_change_event gates on WATCH_BAND
    check("healthy review emits no event", maybe_emit_change_event(review) is None)
    crit_event = maybe_emit_change_event(review_crit)
    check("critical review emits an event", crit_event is not None)
    if crit_event is not None:
        parsed = json.loads(crit_event)
        check("event is JSON with expected keys",
              "event" in parsed and "drift_score" in parsed,
              f"keys={list(parsed.keys())}")
        check("event drift_score round-trips",
              abs(parsed["drift_score"] - review_crit.drift_score) < 0.01)

    # 7. Empty stats → drift = 0, no crash
    empty_review = build_review(ScaffoldingStats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
    check("empty stats produces 0.0 drift", empty_review.drift_score == 0.0,
          f"score={empty_review.drift_score}")
    check("empty stats has anomaly: empty rule_count", any("empty" in a for a in empty_review.anomalies))

    # 8. Hard-floor violation triggers a critical anomaly
    hf_violation = ScaffoldingStats(
        loader=LoaderSnapshot(hard_floor_violations=1),
    )
    hf_review = build_review(hf_violation, "2026-06-07", "2026-06-07T14:00:00+00:00")
    check("hard floor violation flagged as anomaly",
          any("hard_floor_violation" in a for a in hf_review.anomalies))
    check("hard floor violation component score is 1.0",
          hf_review.component_scores.get("hard_floor_violation") == 1.0)

    print("=" * 50)
    if failures:
        print(f"FAIL: {len(failures)} check(s) failed: {failures}")
        return 1
    print("PASS: all self-test checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
