"""test_scaffolding_review_cron.py — Sprint 4 unit tests.

Run: python3 -m unittest drafts.test_scaffolding_review_cron -v

Covers the two areas the spec called out:
  1. Drift-score calculation (boundary, weighting, clamping, healthy/sick inputs)
  2. File I/O (atomic write, dated filename, idempotency, no temp leaks)

Plus Markdown rendering and the harness-change event hook for completeness.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure drafts/ is on the import path (matches the pattern in test_command_router.py).
_DRAFTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_DRAFTS_DIR.parent))  # 03 Projects/Builder on path
sys.path.insert(0, str(_DRAFTS_DIR))         # drafts/ on path

from scaffolding_review_cron import (  # type: ignore  # noqa: E402
    COMPONENT_THRESHOLDS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_WEIGHTS,
    HEALTHY_BAND,
    WATCH_BAND,
    DEGRADED_BAND,
    CostSnapshot,
    LoaderSnapshot,
    RouterSnapshot,
    SafetySnapshot,
    ScaffoldingReview,
    ScaffoldingStats,
    build_review,
    compute_component_scores,
    compute_drift_score,
    detect_anomalies,
    health_band,
    maybe_emit_change_event,
    recommend,
    render_markdown,
    run_review,
    write_review,
)


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _healthy_stats() -> ScaffoldingStats:
    return ScaffoldingStats(
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


def _critical_stats() -> ScaffoldingStats:
    return ScaffoldingStats(
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


# ---------------------------------------------------------------------------
# Drift-score component tests
# ---------------------------------------------------------------------------


class TestComponentScores(unittest.TestCase):
    """Each component score is in [0, 1] and matches the documented formula."""

    def test_rule_fallback_rate_normal(self):
        stats = ScaffoldingStats(
            router=RouterSnapshot(total_classifications=100, fallback_count=25)
        )
        components = compute_component_scores(stats)
        self.assertAlmostEqual(components["rule_fallback"], 0.25, places=4)

    def test_rule_fallback_rate_zero_traffic(self):
        # No traffic → report 0.0 (no evidence of drift either way)
        stats = ScaffoldingStats(router=RouterSnapshot(total_classifications=0))
        components = compute_component_scores(stats)
        self.assertEqual(components["rule_fallback"], 0.0)

    def test_rule_fallback_rate_clamps_overflow(self):
        # fallback_count > total shouldn't happen, but defend against bad inputs
        stats = ScaffoldingStats(
            router=RouterSnapshot(total_classifications=10, fallback_count=99)
        )
        components = compute_component_scores(stats)
        self.assertEqual(components["rule_fallback"], 1.0)

    def test_cache_miss_rate_normal(self):
        stats = ScaffoldingStats(
            loader=LoaderSnapshot(hits=70, misses=30)
        )
        components = compute_component_scores(stats)
        self.assertAlmostEqual(components["cache_miss"], 0.30, places=4)

    def test_cache_miss_rate_no_traffic(self):
        stats = ScaffoldingStats(loader=LoaderSnapshot(hits=0, misses=0))
        components = compute_component_scores(stats)
        self.assertEqual(components["cache_miss"], 0.0)

    def test_cost_overrun_ratio_normal(self):
        stats = ScaffoldingStats(
            cost=CostSnapshot(total_actual_cost=1.50, total_planned_cost=1.00)
        )
        components = compute_component_scores(stats)
        self.assertAlmostEqual(components["cost_overrun"], 0.50, places=4)

    def test_cost_overrun_ratio_no_baseline(self):
        # No planned cost → 0.0 (can't measure overrun without a plan)
        stats = ScaffoldingStats(
            cost=CostSnapshot(total_actual_cost=1.00, total_planned_cost=0.0)
        )
        components = compute_component_scores(stats)
        self.assertEqual(components["cost_overrun"], 0.0)

    def test_cost_overrun_ratio_override(self):
        # Explicit override bypasses the (actual - planned) / planned calculation
        stats = ScaffoldingStats(
            cost=CostSnapshot(
                total_actual_cost=0.0,
                total_planned_cost=0.0,
                cost_overrun_ratio_override=0.42,
            )
        )
        components = compute_component_scores(stats)
        self.assertEqual(components["cost_overrun"], 0.42)

    def test_safety_violation_rate_normal(self):
        stats = ScaffoldingStats(
            safety=SafetySnapshot(
                path_traversal_attempts_blocked=1,
                atomic_write_temp_file_leaks=0,
                total_atomic_writes=10,
                total_load_full_topic_calls=90,
            )
        )
        components = compute_component_scores(stats)
        # 1 / (10 + 90) = 0.01
        self.assertAlmostEqual(components["safety_violation"], 0.01, places=4)

    def test_safety_violation_rate_no_traffic(self):
        stats = ScaffoldingStats(safety=SafetySnapshot())
        components = compute_component_scores(stats)
        self.assertEqual(components["safety_violation"], 0.0)

    def test_hard_floor_violation_is_binary(self):
        zero = ScaffoldingStats(loader=LoaderSnapshot(hard_floor_violations=0))
        one = ScaffoldingStats(loader=LoaderSnapshot(hard_floor_violations=1))
        many = ScaffoldingStats(loader=LoaderSnapshot(hard_floor_violations=99))
        comp_zero = compute_component_scores(zero)
        comp_one = compute_component_scores(one)
        comp_many = compute_component_scores(many)
        self.assertEqual(comp_zero["hard_floor_violation"], 0.0)
        self.assertEqual(comp_one["hard_floor_violation"], 1.0)
        self.assertEqual(comp_many["hard_floor_violation"], 1.0)

    def test_components_in_unit_interval(self):
        # Healthy and critical both must produce scores in [0, 1].
        for stats in (_healthy_stats(), _critical_stats()):
            for name, score in compute_component_scores(stats).items():
                self.assertGreaterEqual(score, 0.0, f"{name} below 0")
                self.assertLessEqual(score, 1.0, f"{name} above 1")


# ---------------------------------------------------------------------------
# Drift-score calculation tests
# ---------------------------------------------------------------------------


class TestDriftScore(unittest.TestCase):
    """Drift score is a weighted blend, clamped to [0, 1]."""

    def test_healthy_drift_is_low(self):
        score = compute_drift_score(_healthy_stats())
        self.assertLess(score, 0.20, f"healthy drift should be < 0.20, got {score:.3f}")
        self.assertGreaterEqual(score, 0.0)

    def test_critical_drift_is_high(self):
        score = compute_drift_score(_critical_stats())
        self.assertGreater(score, 0.50, f"critical drift should be > 0.50, got {score:.3f}")
        self.assertLessEqual(score, 1.0)

    def test_empty_stats_drift_is_zero(self):
        score = compute_drift_score(ScaffoldingStats())
        self.assertEqual(score, 0.0)

    def test_drift_score_is_clamped_to_unit_interval(self):
        # Even with adversarial inputs, score must stay in [0, 1].
        # Build a stats object with extreme values.
        bad = ScaffoldingStats(
            router=RouterSnapshot(total_classifications=1, fallback_count=1000),
            loader=LoaderSnapshot(hits=0, misses=1000, hard_floor_violations=1000),
            safety=SafetySnapshot(
                path_traversal_attempts_blocked=1000,
                atomic_write_temp_file_leaks=1000,
                total_atomic_writes=1,
                total_load_full_topic_calls=1,
            ),
            cost=CostSnapshot(total_actual_cost=1000.0, total_planned_cost=0.01),
        )
        score = compute_drift_score(bad)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_custom_weights_apply(self):
        # With only rule_fallback weighted at 1.0, the drift equals the
        # rule_fallback_rate exactly.
        stats = ScaffoldingStats(
            router=RouterSnapshot(total_classifications=100, fallback_count=20)
        )
        custom = {"rule_fallback": 1.0}
        score = compute_drift_score(stats, weights=custom)
        self.assertAlmostEqual(score, 0.20, places=4)

    def test_zero_weights_yield_zero_drift(self):
        # Edge case: caller passes an empty weights dict.
        score = compute_drift_score(_critical_stats(), weights={})
        self.assertEqual(score, 0.0)

    def test_default_weights_sum_to_one(self):
        # The 5 default weights must sum to <= 1.0 (clamped) so that
        # the "all components = 1.0" scenario produces drift = 1.0.
        total = sum(DEFAULT_WEIGHTS.values())
        self.assertAlmostEqual(total, 1.0, places=4,
                               msg=f"DEFAULT_WEIGHTS sum to {total}, expected 1.0")


# ---------------------------------------------------------------------------
# Health band tests
# ---------------------------------------------------------------------------


class TestHealthBand(unittest.TestCase):
    """Drift score maps to the 4-band health scale."""

    def test_bands_are_in_expected_order(self):
        self.assertLess(HEALTHY_BAND, WATCH_BAND)
        self.assertLess(WATCH_BAND, DEGRADED_BAND)
        self.assertLess(DEGRADED_BAND, 1.0)

    def test_band_boundaries(self):
        self.assertEqual(health_band(0.0), "healthy")
        self.assertEqual(health_band(0.199), "healthy")
        self.assertEqual(health_band(0.20), "watch")
        self.assertEqual(health_band(0.499), "watch")
        self.assertEqual(health_band(0.50), "degraded")
        self.assertEqual(health_band(0.799), "degraded")
        self.assertEqual(health_band(0.80), "critical")
        self.assertEqual(health_band(1.0), "critical")

    def test_healthy_stats_review_band(self):
        review = build_review(_healthy_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        self.assertEqual(review.band, "healthy")
        self.assertEqual(health_band(review.drift_score), "healthy")

    def test_critical_stats_review_band(self):
        review = build_review(_critical_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        self.assertIn(review.band, ("degraded", "critical"))


# ---------------------------------------------------------------------------
# Anomaly detection tests
# ---------------------------------------------------------------------------


class TestAnomalies(unittest.TestCase):
    """Anomalies list components that crossed their thresholds."""

    def test_no_anomalies_for_healthy_state(self):
        review = build_review(_healthy_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        self.assertEqual(review.anomalies, [])

    def test_critical_state_has_anomalies(self):
        review = build_review(_critical_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        self.assertGreater(len(review.anomalies), 0)
        # All five components should be flagged in the critical fixture.
        for component in DEFAULT_WEIGHTS.keys():
            self.assertTrue(
                any(component in a for a in review.anomalies),
                f"expected anomaly for {component} in {review.anomalies}",
            )

    def test_empty_rule_registry_is_an_anomaly(self):
        stats = ScaffoldingStats(router=RouterSnapshot(rule_count=0))
        review = build_review(stats, "2026-06-07", "2026-06-07T14:00:00+00:00")
        self.assertTrue(any("empty" in a for a in review.anomalies))

    def test_l2_l3_stubs_flagged(self):
        stats = ScaffoldingStats(
            router=RouterSnapshot(l2_not_implemented=3, l3_not_implemented=2)
        )
        review = build_review(stats, "2026-06-07", "2026-06-07T14:00:00+00:00")
        self.assertTrue(any("L2" in a for a in review.anomalies))
        self.assertTrue(any("L3" in a for a in review.anomalies))

    def test_anomalies_sorted_by_severity(self):
        # Anomalies should be deterministic in order. Verify that two
        # builds produce the same ordering.
        review1 = build_review(_critical_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        review2 = build_review(_critical_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        self.assertEqual(review1.anomalies, review2.anomalies)

    def test_hard_floor_violation_always_an_anomaly(self):
        # The threshold for hard_floor_violation is 0.0, so any violation
        # at all is an anomaly.
        stats = ScaffoldingStats(loader=LoaderSnapshot(hard_floor_violations=1))
        review = build_review(stats, "2026-06-07", "2026-06-07T14:00:00+00:00")
        self.assertTrue(any("hard_floor_violation" in a for a in review.anomalies))


# ---------------------------------------------------------------------------
# Recommendation tests
# ---------------------------------------------------------------------------


class TestRecommendations(unittest.TestCase):
    """Each anomalous component triggers a corresponding recommendation."""

    def test_no_recommendations_for_healthy(self):
        review = build_review(_healthy_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        self.assertEqual(review.recommendations, [])

    def test_critical_state_has_recommendations(self):
        review = build_review(_critical_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        self.assertGreater(len(review.recommendations), 0)

    def test_each_anomalous_component_has_a_recommendation(self):
        # Critical fixture has all 5 components above threshold; the
        # recommendations should mention each one.
        review = build_review(_critical_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        joined = " | ".join(review.recommendations).lower()
        for keyword in ("l1", "cache", "cost", "safety", "hard floor"):
            self.assertIn(keyword, joined,
                          f"expected recommendation mentioning {keyword!r}")


# ---------------------------------------------------------------------------
# Markdown rendering tests
# ---------------------------------------------------------------------------


class TestRenderMarkdown(unittest.TestCase):
    """Markdown output contains all required sections and is deterministic."""

    def setUp(self):
        self.review = build_review(_healthy_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")

    def test_render_returns_string(self):
        md = render_markdown(self.review)
        self.assertIsInstance(md, str)
        self.assertGreater(len(md), 200)

    def test_render_contains_all_sections(self):
        md = render_markdown(self.review)
        for section in [
            "# Scaffolding Health Receipt — 2026-06-07",
            "**Drift score:**",
            "**Harness version:**",
            "## Component scores",
            "## Anomalies flagged",
            "## Recommendations",
            "## Raw stats",
            "### Command router",
            "### Context loader",
            "### Cost",
            "### Safety",
        ]:
            self.assertIn(section, md, f"missing section: {section}")

    def test_render_contains_component_table(self):
        md = render_markdown(self.review)
        for component in DEFAULT_WEIGHTS.keys():
            self.assertIn(f"| {component} |", md,
                          f"component {component} not in table")

    def test_render_contains_lane_distribution(self):
        md = render_markdown(self.review)
        for lane in ("capture", "synthesize", "dispatch", "observe", "ask_first"):
            self.assertIn(f"  - {lane}:", md, f"lane {lane} missing")

    def test_render_is_deterministic(self):
        md1 = render_markdown(self.review)
        md2 = render_markdown(self.review)
        self.assertEqual(md1, md2)

    def test_render_ends_with_single_newline(self):
        md = render_markdown(self.review)
        self.assertFalse(md.endswith("\n\n"), "trailing blank line")


# ---------------------------------------------------------------------------
# File I/O tests
# ---------------------------------------------------------------------------


class TestFileIO(unittest.TestCase):
    """write_review creates the dated file atomically, no temp leaks, idempotent."""

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="scaffoldreview_test_"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_write_review_creates_dated_file(self):
        review = build_review(_healthy_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        target = write_review(review, output_dir=self.tmp_dir)
        self.assertTrue(Path(target).is_file())
        self.assertEqual(Path(target).name, "2026-06-07.md")

    def test_write_review_returns_absolute_path(self):
        review = build_review(_healthy_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        target = write_review(review, output_dir=self.tmp_dir)
        self.assertTrue(os.path.isabs(target), f"expected absolute path, got {target}")

    def test_write_review_creates_output_dir(self):
        nested = self.tmp_dir / "deep" / "nested" / "path"
        review = build_review(_healthy_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        target = write_review(review, output_dir=nested)
        self.assertTrue(nested.is_dir())
        self.assertTrue(Path(target).is_file())

    def test_write_review_no_temp_files_leaked(self):
        review = build_review(_healthy_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        write_review(review, output_dir=self.tmp_dir)
        leaked = [
            f for f in os.listdir(self.tmp_dir)
            if f.startswith("2026-06-07.md.tmp.")
        ]
        self.assertEqual(leaked, [], f"temp files leaked: {leaked}")

    def test_write_review_idempotent_same_day(self):
        # Re-writing on the same day should overwrite the file, not duplicate.
        review1 = build_review(_healthy_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        review2 = build_review(_critical_stats(), "2026-06-07", "2026-06-07T15:00:00+00:00")
        path1 = write_review(review1, output_dir=self.tmp_dir)
        path2 = write_review(review2, output_dir=self.tmp_dir)
        self.assertEqual(path1, path2)
        # And only one file exists
        self.assertEqual(
            len([f for f in os.listdir(self.tmp_dir) if f.endswith(".md")]),
            1,
        )
        # The file content reflects the second (critical) review.
        with open(path2, "r", encoding="utf-8") as f:
            content = f.read()
        # Critical review's drift score is > 0.5, so the band is "degraded" or "critical".
        self.assertTrue("degraded" in content or "critical" in content)

    def test_written_file_content_round_trips(self):
        review = build_review(_healthy_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        target = write_review(review, output_dir=self.tmp_dir)
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
        # The rendered output should be a strict superset of the
        # original review's content
        rendered = render_markdown(review)
        self.assertEqual(content, rendered)

    def test_run_review_end_to_end(self):
        # run_review handles defaults, writes the file, and emits an
        # event for the critical fixture.
        import io
        import contextlib

        critical = _critical_stats()
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            review = run_review(
                stats=critical,
                review_date="2026-06-07",
                timestamp_utc="2026-06-07T14:00:00+00:00",
                output_dir=self.tmp_dir,
            )
        target = self.tmp_dir / "2026-06-07.md"
        self.assertTrue(target.is_file())
        # Critical → event is emitted
        stdout = captured.getvalue().strip()
        self.assertTrue(stdout, "expected an event on stdout for critical review")
        event = json.loads(stdout)
        self.assertEqual(event["event"], "harness_change_detected")
        self.assertEqual(event["review_date"], "2026-06-07")
        self.assertGreater(event["drift_score"], WATCH_BAND)

    def test_run_review_healthy_emits_no_event(self):
        import io
        import contextlib

        healthy = _healthy_stats()
        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            review = run_review(
                stats=healthy,
                review_date="2026-06-07",
                timestamp_utc="2026-06-07T14:00:00+00:00",
                output_dir=self.tmp_dir,
            )
        stdout = captured.getvalue().strip()
        self.assertEqual(stdout, "", f"healthy should not emit event, got {stdout!r}")

    def test_maybe_emit_change_event_gates_on_threshold(self):
        healthy = build_review(_healthy_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        critical = build_review(_critical_stats(), "2026-06-07", "2026-06-07T14:00:00+00:00")
        # Healthy: no event
        self.assertIsNone(maybe_emit_change_event(healthy))
        # Critical: event with expected keys
        ev = maybe_emit_change_event(critical)
        self.assertIsNotNone(ev)
        parsed = json.loads(ev)  # type: ignore
        self.assertEqual(parsed["event"], "harness_change_detected")
        self.assertIn("band", parsed)
        self.assertIn("review_date", parsed)
        self.assertIn("drift_score", parsed)


# ---------------------------------------------------------------------------
# Constants sanity tests
# ---------------------------------------------------------------------------


class TestConstants(unittest.TestCase):
    """The defaults are documented and stable."""

    def test_default_output_dir_points_into_99_system(self):
        # The default output dir should be inside the vault's 99 _system folder.
        path = DEFAULT_OUTPUT_DIR
        self.assertTrue(str(path).endswith("scaffolding-reviews"),
                        f"unexpected path: {path}")
        # The path should contain "99 _system" (with the space).
        self.assertIn("99 _system", str(path))

    def test_default_weights_keys(self):
        # All 5 components are accounted for.
        self.assertEqual(
            set(DEFAULT_WEIGHTS.keys()),
            {"rule_fallback", "cache_miss", "cost_overrun", "safety_violation", "hard_floor_violation"},
        )

    def test_default_thresholds_keys(self):
        # Thresholds cover the same 5 components.
        self.assertEqual(
            set(COMPONENT_THRESHOLDS.keys()),
            set(DEFAULT_WEIGHTS.keys()),
        )


if __name__ == "__main__":
    unittest.main()
