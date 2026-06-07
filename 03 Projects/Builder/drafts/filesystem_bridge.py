"""
filesystem_bridge.py — Tier 3 lazy loader with macOS atomic writes.

Module purpose: Let Mavis read full topics (Tier 3) from the Obsidian
Vault directly via filesystem, bypassing API serialization token
overhead, and write atomically so partial writes are never visible.

Architecture: 03 Projects/Mavis/phase_next_architecture.md §2.1.1
(read path) + §2.1.2 (write path). Tier 3 cache policy §4.2 with the
30-min hard floor from §6a locked decision 4.

macOS prerequisite: Full Disk Access (FDA) must be granted to the
Mavis runtime at the OS level (System Settings > Privacy & Security >
Full Disk Access). Without FDA, filesystem reads of the Vault directory
will fail with EACCES at the OS layer — not in this Python code. The
bridge is FDA-aware (it documents the prerequisite) but does not
attempt to bypass or probe the OS-level access check.

Standard library only. No external dependencies.
"""

from __future__ import annotations

import os
import secrets
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Optional


# --- Security boundary: path-traversal protection -----------------


def _resolve_vault_path(vault_root: str, note_path: str) -> str:
    """Resolve a (vault_root, note_path) pair to a canonical absolute
    path that is guaranteed to live inside the vault.

    The vault boundary is enforced via realpath comparison, not
    string-prefix matching. String-prefix is bypassable by sibling
    directories whose names are prefixes of the vault name (e.g.,
    "/Users/me/vault2" passes a "/Users/me/vault" prefix check but
    is not inside the vault). realpath + trailing-sep comparison is
    the standard pattern.

    Returns the resolved absolute path. Raises ValueError if the
    resolved path escapes the vault.
    """
    if not os.path.isabs(vault_root):
        raise ValueError(f"vault_root must be absolute, got: {vault_root!r}")
    if not os.path.isdir(vault_root):
        raise ValueError(f"vault_root does not exist or is not a directory: {vault_root!r}")

    # Realpath resolves symlinks AND normalizes ../ components.
    real_vault = os.path.realpath(vault_root)
    # If note_path is absolute, the join drops vault_root — that's
    # fine, realpath will catch the escape. If relative, it joins
    # under the vault.
    candidate = os.path.realpath(os.path.join(real_vault, note_path))

    # Trailing-sep comparison: the resolved path must be the vault
    # itself or a descendant. Without the sep, "/foo/vault2" would
    # be accepted as inside "/foo/vault".
    vault_with_sep = real_vault + os.sep
    if candidate != real_vault and not candidate.startswith(vault_with_sep):
        raise ValueError(
            f"path traversal detected: {note_path!r} resolves to "
            f"{candidate!r}, which is outside vault {real_vault!r}"
        )
    return candidate


# --- Tier 3 read path: lazy load with path-traversal safety ---------


def load_full_topic(vault_root: str, note_path: str) -> str:
    """Lazy load a single full topic (Tier 3) from the Obsidian Vault.

    Reads the file at <vault_root>/<note_path> directly via filesystem,
    bypassing the API serialization layer. Returns the file contents
    as a UTF-8 string. Raises FileNotFoundError if the topic doesn't
    exist (caller can distinguish "not yet captured" from "load
    failure"). Raises ValueError if the path escapes the vault.
    """
    resolved = _resolve_vault_path(vault_root, note_path)
    if not os.path.isfile(resolved):
        raise FileNotFoundError(f"full topic not found: {resolved}")
    with open(resolved, "r", encoding="utf-8") as f:
        return f.read()


# --- Tier 3 write path: macOS atomic write pattern ------------------


def atomic_write(target_path: str, content: str) -> None:
    """Write content to target_path atomically.

    Pattern (POSIX/macOS-safe):
      1. Generate a temp file at <target_path>.tmp.<pid>.<rand>
      2. Open the temp file, write content, fsync() the file
         descriptor (forces bytes to disk before the rename)
      3. os.rename() temp -> target (atomic on POSIX and APFS)
      4. On any failure: remove the temp file so it doesn't leak

    The parent directory of target_path is created with
    makedirs(exist_ok=True) so callers don't need to pre-create.

    This pattern guarantees that a concurrent reader will see either
    the old file (no rename yet) or the new file (rename complete) —
    never a half-written file with mixed content.
    """
    if not os.path.isabs(target_path):
        raise ValueError(f"target_path must be absolute, got: {target_path!r}")

    target_dir = os.path.dirname(target_path)
    if target_dir:
        os.makedirs(target_dir, exist_ok=True)

    # Random hex + pid makes collisions across processes astronomically
    # unlikely while keeping the temp file human-debuggable.
    temp_path = f"{target_path}.tmp.{os.getpid()}.{secrets.token_hex(8)}"
    try:
        # Write content, flush, fsync, close — all before the rename.
        # No fd juggling: use a normal open() context manager, then
        # call os.fsync on the underlying fileno() before exit. The
        # flush() before fsync() is redundant in practice (fsync
        # implies flush) but harmless and makes the intent explicit.
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.rename(temp_path, target_path)
    except BaseException:
        # Best-effort cleanup of the temp file. If the rename
        # already happened, this no-ops; if it didn't, the partial
        # file is removed so it doesn't accumulate.
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass  # temp was never created or already renamed
        raise  # re-raise the original exception so the caller sees it


# --- Tier 3 cache: LRU + importance with 30-min hard floor ---------

# Hard floor per §6a locked decision 4. Never evict before this
# many seconds, regardless of importance score.
TIER3_HARD_FLOOR_SECONDS = 30 * 60  # 30 minutes
DEFAULT_EVICTION_THRESHOLD = 0.3
DEFAULT_MAX_ENTRIES = 64


@dataclass
class _CacheEntry:
    """One cached full-topic entry. Tracks the cache key, content,
    importance score, size, and when it was cached. The
    `cached_at_monotonic` uses time.monotonic() so it is robust to
    wall-clock adjustments (NTP, DST, etc.).
    """
    key: str
    content: str
    importance: float
    cached_at_monotonic: float = field(default_factory=time.monotonic)
    hits: int = 0

    @property
    def size_bytes(self) -> int:
        return len(self.content.encode("utf-8"))


@dataclass
class Tier3LoaderStats:
    """Snapshot of Tier3Loader counters. Returned by Tier3Loader.stats()."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    bytes_served: int = 0
    bytes_cached: int = 0


class Tier3Loader:
    """Tier 3 lazy loader with an LRU+importance cache.

    Cache eviction policy:
      - LRU ordering (OrderedDict) for fast eviction on overflow
      - Importance-weighted: a topic with importance >= threshold
        is treated as "keep" and is never evicted by importance
      - 30-min hard floor (TIER3_HARD_FLOOR_SECONDS): even a
        low-importance topic is never evicted before 30 min of age;
        this is the locked decision 4 from §6a

    The cache holds at most `max_entries` (default 64) — beyond that,
    the LRU end is evicted. The hard floor applies to time-based
    eviction via `evict_if_stale`, not to size-based LRU eviction
    on overflow. (If you need hard floor on overflow too, raise
    `max_entries` or rely on importance to keep topics alive.)
    """

    def __init__(
        self,
        max_entries: int = DEFAULT_MAX_ENTRIES,
        eviction_threshold: float = DEFAULT_EVICTION_THRESHOLD,
    ) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        if not 0.0 <= eviction_threshold <= 1.0:
            raise ValueError("eviction_threshold must be in [0.0, 1.0]")
        self._max_entries = max_entries
        self._eviction_threshold = eviction_threshold
        # OrderedDict for O(1) move-to-end on cache hit (LRU semantics)
        self._cache: "OrderedDict[str, _CacheEntry]" = OrderedDict()
        self._stats = Tier3LoaderStats()

    @property
    def max_entries(self) -> int:
        return self._max_entries

    @property
    def eviction_threshold(self) -> float:
        return self._eviction_threshold

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        return key in self._cache

    def load(self, vault_root: str, note_path: str, importance: float = 0.5) -> str:
        """Load a full topic, using the cache.

        On cache hit: updates LRU order, increments hit counter, returns
        cached content.
        On cache miss: calls load_full_topic, caches with the
        provided importance score, evicts LRU end if over capacity,
        returns the content.

        importance is in [0.0, 1.0]. The caller decides importance
        (e.g., from a content-relevance signal or user-intent weight).
        """
        if not 0.0 <= importance <= 1.0:
            raise ValueError(f"importance must be in [0.0, 1.0], got {importance!r}")

        cache_key = f"{os.path.realpath(vault_root)}::{note_path}"

        # Cache hit path
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            # move_to_end marks this key as most-recently-used
            self._cache.move_to_end(cache_key)
            entry.hits += 1
            self._stats.hits += 1
            self._stats.bytes_served += entry.size_bytes
            return entry.content

        # Cache miss path
        content = load_full_topic(vault_root, note_path)
        entry = _CacheEntry(key=cache_key, content=content, importance=importance)
        self._cache[cache_key] = entry
        self._stats.misses += 1
        self._stats.bytes_served += entry.size_bytes
        self._stats.bytes_cached += entry.size_bytes

        # LRU overflow eviction (size-based, not time-based)
        while len(self._cache) > self._max_entries:
            evicted_key, evicted_entry = self._cache.popitem(last=False)
            self._stats.evictions += 1
            self._stats.bytes_cached -= evicted_entry.size_bytes

        return content

    def cache_topic(self, key: str, content: str, importance: float) -> None:
        """Pre-populate the cache without going through load_full_topic.

        Useful for warming the cache on startup or after a bulk import.
        `key` should be in the same form as load()'s internal key
        (typically "<realpath>/<note_path>") but the caller can use
        any string — it's just a cache key.
        """
        if not 0.0 <= importance <= 1.0:
            raise ValueError(f"importance must be in [0.0, 1.0], got {importance!r}")
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key].importance = importance
            self._cache[key].content = content
            return
        self._cache[key] = _CacheEntry(key=key, content=content, importance=importance)
        self._stats.bytes_cached += self._cache[key].size_bytes
        while len(self._cache) > self._max_entries:
            _, evicted = self._cache.popitem(last=False)
            self._stats.evictions += 1
            self._stats.bytes_cached -= evicted.size_bytes

    def evict_if_stale(self, now: float) -> list[str]:
        """Evict entries where the 30-min hard floor is satisfied AND
        importance is below the eviction threshold.

        Returns the list of evicted cache keys (in eviction order).

        The 30-min hard floor is absolute: an entry with
        `now - cached_at < TIER3_HARD_FLOOR_SECONDS` is NEVER evicted
        regardless of importance. After the floor is satisfied, an
        entry is evicted if and only if its importance is below
        `self.eviction_threshold`.

        The caller passes `now` (typically `time.monotonic()`) so the
        test suite and the production code share the same time
        source. time.monotonic is used internally for caching
        timestamps so wall-clock changes don't break eviction.
        """
        evicted_keys: list[str] = []
        # Iterate over a snapshot — we mutate the dict during the loop.
        for key in list(self._cache.keys()):
            entry = self._cache[key]
            age = now - entry.cached_at_monotonic
            if age < TIER3_HARD_FLOOR_SECONDS:
                # Hard floor — skip regardless of importance.
                continue
            if entry.importance < self._eviction_threshold:
                del self._cache[key]
                self._stats.evictions += 1
                self._stats.bytes_cached -= entry.size_bytes
                evicted_keys.append(key)
        return evicted_keys

    def clear(self) -> None:
        """Drop all cached entries. Stats are not reset."""
        self._cache.clear()

    def stats(self) -> Tier3LoaderStats:
        """Return a snapshot of the current stats counters.

        Returned dataclass is independent of the loader's internal
        state — modifying it does not affect the loader.
        """
        return Tier3LoaderStats(
            hits=self._stats.hits,
            misses=self._stats.misses,
            evictions=self._stats.evictions,
            bytes_served=self._stats.bytes_served,
            bytes_cached=self._stats.bytes_cached,
        )


# --- Self-test -----------------------------------------------------


def _selftest() -> int:
    """Run the module's self-test. Exits 0 on success, non-zero on
    failure. Used both as a `python3 filesystem_bridge.py` smoke
    check and as a regression target.
    """
    import shutil
    import tempfile

    failures: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        status = "PASS" if cond else "FAIL"
        line = f"  [{status}] {name}"
        if detail:
            line += f" — {detail}"
        print(line)
        if not cond:
            failures.append(name)

    print("filesystem_bridge self-test")
    print("=" * 40)

    # 1. Create a temp dir as fake vault
    fake_vault = tempfile.mkdtemp(prefix="fsbridge_selftest_")
    try:
        check("temp fake vault created", os.path.isdir(fake_vault), fake_vault)

        # 2. Write 2 test files via atomic_write
        topic_a = os.path.join(fake_vault, "02 Notes", "a.md")
        topic_b = os.path.join(fake_vault, "02 Notes", "b.md")
        atomic_write(topic_a, "# Topic A\n\nBody of A.")
        atomic_write(topic_b, "# Topic B\n\nBody of B.")
        check("atomic_write created topic A", os.path.isfile(topic_a))
        check("atomic_write created topic B", os.path.isfile(topic_b))
        check(
            "no temp files leaked after atomic_write",
            not any(
                f.startswith(os.path.basename(topic_a) + ".tmp.")
                for f in os.listdir(os.path.dirname(topic_a))
            ),
        )

        # 3. Read them back via load_full_topic and Tier3Loader
        contents_a = load_full_topic(fake_vault, "02 Notes/a.md")
        check("load_full_topic reads topic A", contents_a == "# Topic A\n\nBody of A.")

        loader = Tier3Loader(max_entries=8, eviction_threshold=0.4)
        result = loader.load(fake_vault, "02 Notes/b.md", importance=0.5)
        check("Tier3Loader.load reads topic B", result == "# Topic B\n\nBody of B.")
        check("first call is a miss", loader.stats().misses == 1)
        check("no hits yet", loader.stats().hits == 0)

        # Repeat the call — should be a hit now
        result2 = loader.load(fake_vault, "02 Notes/b.md", importance=0.5)
        check("repeat call is a hit", result2 == result)
        check("hits == 1 after repeat", loader.stats().hits == 1)

        # 4. Overwrite topic A; verify no temp file leak
        atomic_write(topic_a, "# Topic A v2\n\nOverwritten body.")
        check("atomic_write overwrites cleanly", os.path.isfile(topic_a))
        check(
            "no temp files leaked after overwrite",
            not any(
                f.startswith(os.path.basename(topic_a) + ".tmp.")
                for f in os.listdir(os.path.dirname(topic_a))
            ),
        )
        check("overwrite content is correct", load_full_topic(fake_vault, "02 Notes/a.md") == "# Topic A v2\n\nOverwritten body.")

        # 5. evict_if_stale: low-importance entry beyond 30-min age should evict
        # Cache a low-importance entry, age it past the floor, evict.
        now = time.monotonic()
        # Bypass load() to get precise cached_at control.
        loader.cache_topic("warm:low", "low importance content", importance=0.0)
        entry = loader._cache["warm:low"]
        entry.cached_at_monotonic = now - 4000  # ~67 min ago
        evicted = loader.evict_if_stale(now=now)
        check("low-importance entry beyond floor IS evicted", "warm:low" in evicted, f"evicted={evicted!r}")

        # 6. evict_if_stale: hard floor holds even for importance=0.0
        loader.cache_topic("warm:fresh", "fresh entry", importance=0.0)
        # Don't age it — it's fresh
        evicted = loader.evict_if_stale(now=time.monotonic())
        check(
            "fresh low-importance entry is NOT evicted (hard floor)",
            "warm:fresh" not in evicted,
            f"evicted={evicted!r}",
        )

        # 6b. And after manually aging it within the floor, still not evicted
        fresh_entry = loader._cache["warm:fresh"]
        fresh_entry.cached_at_monotonic = time.monotonic() - 60  # 1 min ago
        evicted = loader.evict_if_stale(now=time.monotonic())
        check(
            "1-min-old low-importance entry is NOT evicted (still within floor)",
            "warm:fresh" not in evicted,
            f"evicted={evicted!r}",
        )

        # 7. stats() returns a snapshot with sensible numbers
        stats = loader.stats()
        check("stats has the expected counter types", hasattr(stats, "hits") and hasattr(stats, "misses"))
        check("stats.hits >= 1", stats.hits >= 1, f"hits={stats.hits}")
        check("stats.misses >= 1", stats.misses >= 1, f"misses={stats.misses}")
        check("stats.evictions >= 1", stats.evictions >= 1, f"evictions={stats.evictions}")
        check("stats.bytes_served > 0", stats.bytes_served > 0, f"bytes_served={stats.bytes_served}")
        print(f"  stats: {stats}")

        # 8. Path-traversal: must raise ValueError
        traversal_attempts = [
            "../../../etc/passwd",
            "/etc/passwd",
            "02 Notes/../../etc/passwd",
            "../sibling_vault/secret",
        ]
        for attempt in traversal_attempts:
            try:
                load_full_topic(fake_vault, attempt)
                check(f"path traversal rejected: {attempt!r}", False, "did not raise")
            except ValueError as e:
                check(f"path traversal rejected: {attempt!r}", True, "raised ValueError")
            except FileNotFoundError:
                # If the realpath still lands inside the vault (e.g.,
                # the realpath of the attempt is a missing file
                # inside the vault), the code would attempt to read
                # it. That's also OK as long as we don't return
                # content from outside the vault. Treat as PASS if
                # the resulting path is inside the vault.
                resolved = _resolve_vault_path(fake_vault, attempt)
                check(
                    f"path traversal rejected: {attempt!r}",
                    resolved.startswith(os.path.realpath(fake_vault)),
                    f"resolved to {resolved!r} (inside vault, FileNotFoundError acceptable)",
                )

        # 9. Concurrent-atomic test: while atomic_write is happening
        # (synchronous in this design), confirm a reader would see
        # the full file or no file, never a half-file. We simulate
        # by checking the write is atomic on the file system.
        target = os.path.join(fake_vault, "atomic_test.md")
        atomic_write(target, "x" * 1000)
        size = os.path.getsize(target)
        check("atomic write produced full content", size == 1000, f"size={size}")

    finally:
        shutil.rmtree(fake_vault, ignore_errors=True)

    print("=" * 40)
    if failures:
        print(f"FAIL: {len(failures)} check(s) failed: {failures}")
        return 1
    print("PASS: all self-test checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
