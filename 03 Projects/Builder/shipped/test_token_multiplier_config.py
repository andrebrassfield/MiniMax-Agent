"""
test_token_multiplier_config — Sprint 2 pre-handoff self-audit tests.

Run with: python -m pytest test_token_multiplier_config.py -v
Or:       python test_token_multiplier_config.py

Covers 8 pre-handoff checks + 1 math sanity test.
"""

import json
import tempfile
import unittest
from pathlib import Path

from token_multiplier_config import (
    load_config,
    compute_actual_cost,
    MissingConfigError,
    MalformedConfigError,
    IncompleteConfigError,
)


class ValidConfig:
    """A complete, well-formed YAML config snippet."""

    Yaml = """\
multipliers:
  input_rate: 1.0
  output_rate: 1.0
  system_prompt_per_char: 0.0
base_rates:
  input_per_m: 0.30
  output_per_m: 1.20
source_status:
  multipliers_primary_documented: false
  base_rates_primary_documented: true
  last_verified: "2026-06-05"
  notes: "test"
"""

    @classmethod
    def write(cls, tmp_dir: Path) -> Path:
        p = tmp_dir / "token-plan.yaml"
        p.write_text(cls.Yaml, encoding="utf-8")
        return p


# ---------------------------------------------------------------------------
# Pre-handoff Check 1: Hardcoded-multiplier scan
# ---------------------------------------------------------------------------

class TestHardcodedMultiplierScan(unittest.TestCase):
    """Grep the Python source for forbidden literal strings."""

    def test_no_1_3_in_source(self):
        src = Path(__file__).parent / "token_multiplier_config.py"
        content = src.read_text(encoding="utf-8")
        lines_with_1_3 = [l for l in content.splitlines() if "1.3" in l and not l.strip().startswith("#")]
        self.assertEqual(lines_with_1_3, [], f"Found '1.3' in source: {lines_with_1_3}")

    def test_no_1_8_in_source(self):
        src = Path(__file__).parent / "token_multiplier_config.py"
        content = src.read_text(encoding="utf-8")
        lines_with_1_8 = [l for l in content.splitlines() if "1.8" in l and not l.strip().startswith("#")]
        self.assertEqual(lines_with_1_8, [], f"Found '1.8' in source: {lines_with_1_8}")

    def test_no_0_2_token_char_in_source(self):
        src = Path(__file__).parent / "token_multiplier_config.py"
        content = src.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines()
                 if "0.2" in l and "token" in l.lower() and not l.strip().startswith("#")]
        self.assertEqual(lines, [], f"Found '0.2 token' in source: {lines}")


# ---------------------------------------------------------------------------
# Pre-handoff Check 2: Fail-closed on missing config
# ---------------------------------------------------------------------------

class TestMissingConfigError(unittest.TestCase):
    def test_missing_file_raises_missing_config_error(self):
        fake_path = Path("/tmp/nonexistent_token_plan_abc123.yaml")
        with self.assertRaises(MissingConfigError) as ctx:
            load_config(fake_path)
        self.assertIn("Config not found", str(ctx.exception))


# ---------------------------------------------------------------------------
# Pre-handoff Check 3: Fail-closed on malformed YAML
# ---------------------------------------------------------------------------

class TestMalformedConfigError(unittest.TestCase):
    def test_invalid_yaml_raises_malformed_config_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.yaml"
            p.write_text("  this is not: [yaml\n    broken: indentation", encoding="utf-8")
            with self.assertRaises(MalformedConfigError) as ctx:
                load_config(p)
            self.assertIn("Invalid YAML", str(ctx.exception))

    def test_root_not_mapping_raises_malformed_config_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.yaml"
            p.write_text("- item1\n- item2", encoding="utf-8")  # list, not dict
            with self.assertRaises(MalformedConfigError) as ctx:
                load_config(p)
            self.assertIn("YAML mapping", str(ctx.exception))


# ---------------------------------------------------------------------------
# Pre-handoff Check 4: Fail-closed on incomplete config
# ---------------------------------------------------------------------------

class TestIncompleteConfigError(unittest.TestCase):
    def test_missing_required_key_raises_incomplete_config_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "incomplete.yaml"
            p.write_text("multipliers:\n  input_rate: 1.0\n", encoding="utf-8")  # missing output_rate, system_prompt_per_char, base_rates
            with self.assertRaises(IncompleteConfigError) as ctx:
                load_config(p)
            missing = str(ctx.exception)
            self.assertIn("Missing required keys", missing)
            # Check at least one of the known-missing keys is named
            self.assertTrue(
                "output_rate" in missing or
                "system_prompt_per_char" in missing or
                "input_per_m" in missing or
                "output_per_m" in missing,
                f"Exception should name a missing key, got: {missing}"
            )


# ---------------------------------------------------------------------------
# Pre-handoff Check 5: Runtime re-read — config update takes effect without restart
# ---------------------------------------------------------------------------

class TestRuntimeReRead(unittest.TestCase):
    def test_config_update_affects_next_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "token-plan.yaml"

            # Write initial config with multiplier 1.0
            config_path.write_text(ValidConfig.Yaml, encoding="utf-8")
            cfg1 = load_config(config_path)
            self.assertEqual(cfg1.input_rate, 1.0)

            # Compute a cost event
            log_path = Path(tmp) / "log.jsonl"
            event1 = compute_actual_cost(1_000_000, 0, "sess-1", cfg1, log_path)
            self.assertAlmostEqual(event1.actual_input_cost, 0.30)  # 1M tokens * 1.0 * 0.30 / 1M

            # Overwrite config with multiplier 2.0
            new_yaml = ValidConfig.Yaml.replace("input_rate: 1.0", "input_rate: 2.0")
            config_path.write_text(new_yaml, encoding="utf-8")
            cfg2 = load_config(config_path)
            self.assertEqual(cfg2.input_rate, 2.0)

            # Compute a second cost event with the re-loaded config
            event2 = compute_actual_cost(1_000_000, 0, "sess-2", cfg2, log_path)
            # 1M tokens * 2.0 * 0.30 / 1M = 0.60
            self.assertAlmostEqual(event2.actual_input_cost, 0.60)
            # event1 should still be 0.30 (logged before the update)
            self.assertAlmostEqual(event1.actual_input_cost, 0.30)


# ---------------------------------------------------------------------------
# Pre-handoff Check 6: Default-values test
# ---------------------------------------------------------------------------

class TestDefaultValues(unittest.TestCase):
    def test_defaults_are_1_0_1_0_0_0_in_template(self):
        config_path = Path(__file__).parent / "config" / "token-plan.yaml"
        cfg = load_config(config_path)
        self.assertEqual(cfg.input_rate, 1.0)
        self.assertEqual(cfg.output_rate, 1.0)
        self.assertEqual(cfg.system_prompt_per_char, 0.0)


# ---------------------------------------------------------------------------
# Pre-handoff Check 7: Audit log — one JSONL line per call, all 9 fields
# ---------------------------------------------------------------------------

class TestAuditLog(unittest.TestCase):
    def test_every_call_appends_one_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = ValidConfig.write(Path(tmp))
            log_path = Path(tmp) / "audit.jsonl"

            cfg = load_config(config_path)

            # First call
            compute_actual_cost(100_000, 50_000, "sess-a", cfg, log_path)
            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)

            # Second call
            compute_actual_cost(200_000, 75_000, "sess-b", cfg, log_path)
            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2)

    def test_all_nine_fields_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            config_path = ValidConfig.write(Path(tmp))
            log_path = Path(tmp) / "audit.jsonl"

            cfg = load_config(config_path)
            compute_actual_cost(500_000, 300_000, "sess-c", cfg, log_path)

            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])

            expected_fields = [
                "timestamp", "session_id",
                "sdk_input_tokens", "sdk_output_tokens",
                "multipliers_applied",
                "actual_input_cost", "actual_output_cost", "actual_total_cost",
                "config_version",
            ]
            for field in expected_fields:
                self.assertIn(field, record, f"Missing field: {field}")


# ---------------------------------------------------------------------------
# Pre-handoff Check 8 + Math sanity
# ---------------------------------------------------------------------------

class TestMathAccuracy(unittest.TestCase):
    def test_1m_input_at_0_30_per_m(self):
        """1M input tokens at $0.30/M = $0.30 (multiplier 1.0)."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = load_config(ValidConfig.write(Path(tmp)))
            event = compute_actual_cost(1_000_000, 0, "sess-math", cfg, log_path=None)
            self.assertAlmostEqual(event.actual_input_cost, 0.30, places=6)

    def test_1m_output_at_1_20_per_m(self):
        """1M output tokens at $1.20/M = $1.20 (multiplier 1.0)."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = load_config(ValidConfig.write(Path(tmp)))
            event = compute_actual_cost(0, 1_000_000, "sess-math", cfg, log_path=None)
            self.assertAlmostEqual(event.actual_output_cost, 1.20, places=6)

    def test_combined_cost(self):
        """Combined: 1M input ($0.30) + 1M output ($1.20) = $1.50."""
        with tempfile.TemporaryDirectory() as tmp:
            cfg = load_config(ValidConfig.write(Path(tmp)))
            event = compute_actual_cost(1_000_000, 1_000_000, "sess-math", cfg, log_path=None)
            self.assertAlmostEqual(event.actual_total_cost, 1.50, places=6)

    def test_multiplier_applied(self):
        """With multiplier 2.0: 1M input * 2.0 * $0.30/M = $0.60."""
        with tempfile.TemporaryDirectory() as tmp:
            yaml = ValidConfig.Yaml.replace("input_rate: 1.0", "input_rate: 2.0")
            p = Path(tmp) / "t.yaml"
            p.write_text(yaml, encoding="utf-8")
            cfg = load_config(p)
            event = compute_actual_cost(1_000_000, 0, "sess-math", cfg, log_path=None)
            self.assertAlmostEqual(event.actual_input_cost, 0.60, places=6)
            self.assertEqual(event.multipliers_applied["input_rate"], 2.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)