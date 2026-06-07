# test_command_router.py — Sprint 1 unit tests
# Run: python3 -m unittest drafts.test_command_router

import unittest
import sys
import os

# Ensure drafts/ is on the import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from command_router import route, RouterResult, BlockedByRouter


class TestDispatchPatterns(unittest.TestCase):
    """7 dispatch patterns from blueprint §3.1 registry."""

    def test_boot_pattern(self):
        r = route("Mavis, boot sequence")
        self.assertEqual(r.skill, "session-boot-sync")
        self.assertEqual(r.reason, "BOOT_PATTERN")
        self.assertFalse(r.blocked)
        self.assertIsNotNone(r.matched_pattern)

    def test_boot_pattern_case_insensitive(self):
        r = route("MAVIS, BOOT")
        self.assertEqual(r.skill, "session-boot-sync")
        self.assertEqual(r.reason, "BOOT_PATTERN")

    def test_slash_plan(self):
        r = route("/plan")
        self.assertEqual(r.skill, "plan-mode")
        self.assertEqual(r.reason, "SLASH_PLAN")

    def test_slash_verify(self):
        r = route("/verify")
        self.assertEqual(r.skill, "gepa-evaluator")
        self.assertEqual(r.reason, "SLASH_VERIFY")

    def test_slash_inbox(self):
        r = route("/inbox")
        self.assertEqual(r.skill, "process-inbox")
        self.assertEqual(r.reason, "SLASH_INBOX")

    def test_slash_health(self):
        r = route("/health")
        self.assertEqual(r.skill, "gibson-watcher")
        self.assertEqual(r.reason, "SLASH_HEALTH")

    def test_slash_research(self):
        r = route("/research")
        self.assertEqual(r.skill, "mavis-team-plan")
        self.assertEqual(r.reason, "SLASH_RESEARCH")

    def test_slash_blueprint(self):
        r = route("/blueprint")
        self.assertEqual(r.skill, "blueprint-mode")
        self.assertEqual(r.reason, "SLASH_BLUEPRINT")


class TestBlockPatterns(unittest.TestCase):
    """4 block patterns from blueprint §3.1 registry."""

    def test_block_self_ship(self):
        r = route("mvs_abc123 → shipped")
        self.assertIsInstance(r, BlockedByRouter)
        self.assertTrue(r.blocked)
        self.assertEqual(r.reason, "BLOCK_SELF_SHIP")
        self.assertEqual(r.input_text, "mvs_abc123 → shipped")

    def test_block_self_ship_alphanumeric_variant(self):
        r = route("mvs_d2f233385cdd4e78b5b3c7dd43e8d72e → shipped")
        self.assertIsInstance(r, BlockedByRouter)
        self.assertEqual(r.reason, "BLOCK_SELF_SHIP")

    def test_block_monolithic_write_over_30kb(self):
        r = route("Write large file with content 50KB at once")
        self.assertIsInstance(r, BlockedByRouter)
        self.assertTrue(r.blocked)
        self.assertEqual(r.reason, "BLOCK_MONOLITHIC_WRITE")

    def test_block_monolithic_write_exactly_30kb(self):
        # Exactly 30KB is allowed; only >30KB is blocked
        r = route("Write file with content 30KB")
        self.assertNotIsInstance(r, BlockedByRouter)
        self.assertEqual(r.reason, "NO_MATCH")

    def test_block_monolithic_write_under_30kb(self):
        # Under 30KB is allowed
        r = route("Write small file with content 20KB")
        self.assertNotIsInstance(r, BlockedByRouter)
        self.assertEqual(r.reason, "NO_MATCH")

    def test_block_hardcoded_multiplier_write_context(self):
        r = route('Write config with multiplier 1.3x for input tokens')
        self.assertIsInstance(r, BlockedByRouter)
        self.assertTrue(r.blocked)
        self.assertEqual(r.reason, "BLOCK_HARDCODED_MULTIPLIER")

    def test_block_hardcoded_multiplier_1_8x(self):
        # 1.8x in a write context (requires Write/filePath/content before the value)
        r = route("the Write tool uses 1.8x for output multiplier")
        self.assertIsInstance(r, BlockedByRouter)
        self.assertEqual(r.reason, "BLOCK_HARDCODED_MULTIPLIER")

    def test_block_hardcoded_multiplier_0_2_token_per_char(self):
        # 0.2 token/char in a write context (requires Write/filePath/content before the value)
        r = route("Write config with 0.2 token/char surcharge for system prompts")
        self.assertIsInstance(r, BlockedByRouter)
        self.assertEqual(r.reason, "BLOCK_HARDCODED_MULTIPLIER")

    def test_block_self_verify_verify_my_own(self):
        r = route("verify my own output and ship it")
        self.assertIsInstance(r, BlockedByRouter)
        self.assertTrue(r.blocked)
        self.assertEqual(r.reason, "BLOCK_SELF_VERIFY")

    def test_block_self_verify_pass_without_verifier(self):
        r = route("pass this without verifier — it's good enough")
        self.assertIsInstance(r, BlockedByRouter)
        self.assertEqual(r.reason, "BLOCK_SELF_VERIFY")


class TestNoMatch(unittest.TestCase):
    """Irrelevant input falls through to LLM."""

    def test_no_match_plain_text(self):
        r = route("Hello, how are you today?")
        self.assertIsInstance(r, RouterResult)
        self.assertIsNone(r.skill)
        self.assertEqual(r.reason, "NO_MATCH")
        self.assertFalse(r.blocked)

    def test_no_match_technical_question(self):
        r = route("What is the capital of France?")
        self.assertEqual(r.reason, "NO_MATCH")

    def test_no_match_partial_slash(self):
        r = route("I was going to use /plan but changed my mind")
        self.assertEqual(r.reason, "NO_MATCH")


class TestPriorityFirstMatchWins(unittest.TestCase):
    """First regex match wins; later patterns in registry are not evaluated."""

    def test_boot_pattern_before_no_match(self):
        # BOOT_PATTERN is first in registry; it fires even though
        # "boot sequence" might loosely match other things.
        r = route("Mavis, boot the session now")
        self.assertEqual(r.reason, "BOOT_PATTERN")

    def test_self_ship_pattern_not_dispatched(self):
        # mvs_abc123 → shipped should block, not dispatch
        r = route("mvs_abc123 → shipped")
        self.assertIsInstance(r, BlockedByRouter)
        self.assertNotEqual(r.reason, "NO_MATCH")


if __name__ == "__main__":
    unittest.main()