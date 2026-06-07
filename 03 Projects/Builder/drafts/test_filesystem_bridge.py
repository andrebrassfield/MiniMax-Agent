"""
test_filesystem_bridge.py — formal test suite for filesystem_bridge.

Runs as a unittest suite via:
    python3 03 Projects/Builder/drafts/test_filesystem_bridge.py

Or via pytest:
    python3 -m pytest 03 Projects/Builder/drafts/test_filesystem_bridge.py -v

Covers the 7 audit checks from the Sprint 4 dispatch prompt:
  1. load_full_topic path-traversal protection
  2. atomic_write fsync ordering
  3. atomic_write cleans up temp file on failure
  4. Tier3Loader.evict_if_stale enforces 30-min hard floor
  5. No external dependencies
  6. filesystem_bridge self-test passes
  7. (this file) runs as a test suite

Standard library only. No external dependencies.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import filesystem_bridge as fb  # noqa: E402


class TestLoadFullTopic(unittest.TestCase):
    """Audit check 1: load_full_topic path-traversal protection."""

    def setUp(self):
        self.vault = tempfile.mkdtemp(prefix="fb_test_vault_")
        Path(self.vault, "02 Notes").mkdir(parents=True, exist_ok=True)
        Path(self.vault, "02 Notes", "a.md").write_text("# A\n", encoding="utf-8")
        Path(self.vault, "01 Daily").mkdir(parents=True, exist_ok=True)
        Path(self.vault, "01 Daily", "today.md").write_text("today", encoding="utf-8")
        self.sibling = tempfile.mkdtemp(prefix="fb_test_sibling_")
        Path(self.sibling, "secret").write_text("secret content", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.vault, ignore_errors=True)
        shutil.rmtree(self.sibling, ignore_errors=True)

    def test_loads_existing_topic(self):
        self.assertEqual(fb.load_full_topic(self.vault, "02 Notes/a.md"), "# A\n")

    def test_loads_nested_topic(self):
        self.assertEqual(fb.load_full_topic(self.vault, "01 Daily/today.md"), "today")

    def test_file_not_found_raises(self):
        with self.assertRaises(FileNotFoundError):
            fb.load_full_topic(self.vault, "02 Notes/does_not_exist.md")

    def test_relative_traversal_rejected(self):
        with self.assertRaises(ValueError):
            fb.load_full_topic(self.vault, "../../../etc/passwd")

    def test_absolute_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            fb.load_full_topic(self.vault, "/etc/passwd")

    def test_sibling_directory_traversal_rejected(self):
        with self.assertRaises(ValueError):
            fb.load_full_topic(
                self.vault, "../" + os.path.basename(self.sibling) + "/secret"
            )

    def test_relative_vault_root_rejected(self):
        with self.assertRaises(ValueError):
            fb.load_full_topic("relative/path", "02 Notes/a.md")

    def test_nonexistent_vault_root_rejected(self):
        with self.assertRaises(ValueError):
            fb.load_full_topic("/this/path/does/not/exist", "02 Notes/a.md")


class TestAtomicWrite(unittest.TestCase):
    """Audit checks 2 + 3: atomic write pattern + failure cleanup."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="fb_test_atomic_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_writes_file(self):
        target = os.path.join(self.tmp, "out.md")
        fb.atomic_write(target, "hello world")
        self.assertEqual(Path(target).read_text(encoding="utf-8"), "hello world")

    def test_creates_parent_dirs(self):
        target = os.path.join(self.tmp, "deep", "nested", "dirs", "out.md")
        fb.atomic_write(target, "nested content")
        self.assertEqual(Path(target).read_text(encoding="utf-8"), "nested content")

    def test_overwrites_existing_file(self):
        target = os.path.join(self.tmp, "overwrite.md")
        fb.atomic_write(target, "first version")
        fb.atomic_write(target, "second version")
        self.assertEqual(Path(target).read_text(encoding="utf-8"), "second version")

    def test_no_temp_files_left_behind(self):
        target = os.path.join(self.tmp, "no_leak.md")
        fb.atomic_write(target, "content")
        leaked = [f for f in os.listdir(self.tmp) if f.startswith("no_leak.md.tmp.")]
        self.assertEqual(leaked, [], f"temp files leaked: {leaked!r}")

    def test_no_temp_files_after_overwrite(self):
        target = os.path.join(self.tmp, "no_leak_overwrite.md")
        fb.atomic_write(target, "v1")
        fb.atomic_write(target, "v2")
        leaked = [f for f in os.listdir(self.tmp) if ".tmp." in f]
        self.assertEqual(leaked, [], f"temp files leaked: {leaked!r}")

    def test_empty_content(self):
        target = os.path.join(self.tmp, "empty.md")
        fb.atomic_write(target, "")
        self.assertEqual(Path(target).read_text(encoding="utf-8"), "")

    def test_unicode_content(self):
        target = os.path.join(self.tmp, "unicode.md")
        content = "# Hello World\nMavis, Phase Next, 100k+ tokens."
        fb.atomic_write(target, content)
        self.assertEqual(Path(target).read_text(encoding="utf-8"), content)

    def test_relative_target_rejected(self):
        with self.assertRaises(ValueError):
            fb.atomic_write("relative/out.md", "x")

    def test_fsync_is_invoked_internally(self):
        target = os.path.join(self.tmp, "fsync_check.md")
        original_fsync = os.fsync
        called_with = []

        def recording_fsync(fd):
            called_with.append(fd)
            return original_fsync(fd)

        os.fsync = recording_fsync
        try:
            fb.atomic_write(target, "content")
        finally:
            os.fsync = original_fsync
        self.assertTrue(len(called_with) >= 1, "os.fsync was not called; called_with=" + repr(called_with))

    def test_cleans_up_on_failure(self):
        target_dir = os.path.join(self.tmp, "fail_target")
        os.makedirs(target_dir)
        os.chmod(target_dir, 0o500)
        try:
            target = os.path.join(target_dir, "out.md")
            with self.assertRaises(Exception):
                fb.atomic_write(target, "x")
            leaked = []
            for d in (target_dir, self.tmp):
                if os.path.isdir(d):
                    leaked.extend(f for f in os.listdir(d) if ".tmp." in f)
            self.assertEqual(leaked, [], f"temp files leaked: {leaked!r}")
        finally:
            os.chmod(target_dir, 0o700)


class TestTier3Loader(unittest.TestCase):
    """Audit check 4: Tier3Loader 30-min hard floor enforcement."""

    def setUp(self):
        self.vault = tempfile.mkdtemp(prefix="fb_test_tier3_")
        for i in range(5):
            path = "topics/" + str(i) + ".md"
            Path(self.vault, path).parent.mkdir(parents=True, exist_ok=True)
            Path(self.vault, path).write_text("topic " + str(i) + "\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.vault, ignore_errors=True)

    def test_cache_miss_then_hit(self):
        loader = fb.Tier3Loader()
        loader.load(self.vault, "topics/0.md", importance=0.5)
        self.assertEqual(loader.stats().misses, 1)
        loader.load(self.vault, "topics/0.md", importance=0.5)
        self.assertEqual(loader.stats().hits, 1)

    def test_importance_out_of_range_rejected(self):
        loader = fb.Tier3Loader()
        with self.assertRaises(ValueError):
            loader.load(self.vault, "topics/0.md", importance=1.5)
        with self.assertRaises(ValueError):
            loader.load(self.vault, "topics/0.md", importance=-0.1)

    def test_lru_overflow_evicts_oldest(self):
        loader = fb.Tier3Loader(max_entries=3, eviction_threshold=0.0)
        for i in range(4):
            loader.load(self.vault, "topics/" + str(i) + ".md", importance=0.9)
        self.assertEqual(len(loader), 3)
        cache_key_0 = os.path.realpath(self.vault) + "::topics/0.md"
        cache_key_3 = os.path.realpath(self.vault) + "::topics/3.md"
        self.assertNotIn(cache_key_0, loader._cache)
        self.assertIn(cache_key_3, loader._cache)

    def test_lru_promotes_on_access(self):
        loader = fb.Tier3Loader(max_entries=3, eviction_threshold=0.0)
        loader.load(self.vault, "topics/0.md", importance=0.9)
        loader.load(self.vault, "topics/1.md", importance=0.9)
        loader.load(self.vault, "topics/2.md", importance=0.9)
        # Promote topics/0.md to MRU
        loader.load(self.vault, "topics/0.md", importance=0.9)
        # 4th insert evicts topics/1.md (now LRU), not topics/0.md
        loader.load(self.vault, "topics/3.md", importance=0.9)
        cache_key_0 = os.path.realpath(self.vault) + "::topics/0.md"
        cache_key_1 = os.path.realpath(self.vault) + "::topics/1.md"
        self.assertIn(cache_key_0, loader._cache)
        self.assertNotIn(cache_key_1, loader._cache)

    def test_hard_floor_blocks_eviction_within_30_min(self):
        loader = fb.Tier3Loader(eviction_threshold=0.5)
        loader.cache_topic("fresh:low", "x", importance=0.0)
        evicted = loader.evict_if_stale(now=time.monotonic())
        self.assertNotIn("fresh:low", evicted)

    def test_hard_floor_holds_just_under_floor(self):
        loader = fb.Tier3Loader(eviction_threshold=0.5)
        loader.cache_topic("almost_old", "x", importance=0.0)
        entry = loader._cache["almost_old"]
        entry.cached_at_monotonic = time.monotonic() - (29 * 60)
        evicted = loader.evict_if_stale(now=time.monotonic())
        self.assertNotIn("almost_old", evicted, "evicted=" + repr(evicted))

    def test_hard_floor_allows_eviction_after_30_min(self):
        loader = fb.Tier3Loader(eviction_threshold=0.5)
        loader.cache_topic("old:low", "x", importance=0.0)
        entry = loader._cache["old:low"]
        entry.cached_at_monotonic = time.monotonic() - (35 * 60)
        evicted = loader.evict_if_stale(now=time.monotonic())
        self.assertIn("old:low", evicted)

    def test_high_importance_never_evicted_by_time(self):
        loader = fb.Tier3Loader(eviction_threshold=0.5)
        loader.cache_topic("important", "x", importance=1.0)
        entry = loader._cache["important"]
        entry.cached_at_monotonic = time.monotonic() - (24 * 3600)
        evicted = loader.evict_if_stale(now=time.monotonic())
        self.assertNotIn("important", evicted)

    def test_stats_snapshot_independent(self):
        loader = fb.Tier3Loader()
        loader.load(self.vault, "topics/0.md", importance=0.5)
        snap = loader.stats()
        snap.hits = 9999
        snap.misses = 9999
        self.assertEqual(loader.stats().misses, 1)
        self.assertEqual(loader.stats().hits, 0)

    def test_clear_empties_cache_keeps_stats(self):
        loader = fb.Tier3Loader()
        loader.load(self.vault, "topics/0.md", importance=0.5)
        misses_before = loader.stats().misses
        loader.clear()
        self.assertEqual(len(loader), 0)
        self.assertEqual(loader.stats().misses, misses_before)

    def test_invalid_max_entries_rejected(self):
        with self.assertRaises(ValueError):
            fb.Tier3Loader(max_entries=0)
        with self.assertRaises(ValueError):
            fb.Tier3Loader(max_entries=-1)

    def test_invalid_eviction_threshold_rejected(self):
        with self.assertRaises(ValueError):
            fb.Tier3Loader(eviction_threshold=-0.1)
        with self.assertRaises(ValueError):
            fb.Tier3Loader(eviction_threshold=1.5)


class TestNoExternalDeps(unittest.TestCase):
    """Audit check 5: no third-party imports in the module."""

    def test_stdlib_only(self):
        import ast
        with open(fb.__file__, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        allowed = {
            "__future__", "os", "secrets", "time", "collections",
            "dataclasses", "typing", "shutil", "tempfile", "sys",
            "unittest", "pathlib",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertIn(alias.name, allowed, "non-stdlib import in filesystem_bridge: " + alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module is None or node.module == "__future__":
                    continue
                self.assertIn(node.module, allowed, "non-stdlib import in filesystem_bridge: from " + node.module)


class TestModuleSelfTest(unittest.TestCase):
    """Audit check 6: the module's own self-test must run cleanly."""

    def test_selftest_passes(self):
        rc = fb._selftest()
        self.assertEqual(rc, 0, "filesystem_bridge self-test failed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
