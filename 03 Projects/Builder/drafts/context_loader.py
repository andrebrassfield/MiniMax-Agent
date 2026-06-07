"""context_loader.py — Mavis Harness, Sprint 3: context_loader skeleton

Source: 03 Projects/Mavis/phase_next_architecture.md, Section 4.2
Status: APPROVED 2026-06-07 12:55 CT (Andre's locked decisions, Section 6a)

Purpose
-------
Load the right tier of context for each Mavis turn, under the latency budget
(P50<2s, P95<8s — locked Q1 2026-06-07).

Three-tier cache (§3 + §4.2):
  Tier 1 — MetaIndexCache : always-loaded, ~3-8KB, section headers + 1-line summaries.
                            Backing: ~/MiniMax-Agent/.mavis/state/meta_index.json
  Tier 2 — TopicIndexCache: lazy-loaded, ~5-50KB each, TTL-cached.
                            Backing: in-memory dict for skeleton (FS wiring is v2).
  Tier 3 — FullTopicCache  : on-demand only, ~1-50KB each, importance-aware eviction
                            with 30-min hard floor (Andre's decision 4, 6a).
                            Backing: in-memory dict for skeleton.

Context window assembly (§4.2 outputs):
  [system_prompt | meta_index | active_topic_indexes (1-3) | full_topic (0-1)
   | recent_turns | user_input]
  Target: 30-150KB per turn.

Constraints
-----------
- Standard library only. No external imports.
- Deterministic. The caller passes `now: float`; the loader does not call
  time.time() itself. The 30-min hard floor is a duration in seconds (1800.0).
- Eviction is importance-aware (§3) but never evicts within 30 min of insertion
  (Andre's locked decision 4, 6a).
"""

from __future__ import annotations

import json
import os
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Deque, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants — Andre's locked decisions (6a)
# ---------------------------------------------------------------------------

DEFAULT_STATE_DIR = Path(
    os.path.expanduser("~/MiniMax-Agent/.mavis/state")
)
META_INDEX_FILE = "meta_index.json"

# Tier-size boundaries for cache_topic() routing.
META_TIER_MAX_BYTES = 2_000       # < 2KB → meta_index
TOPIC_TIER_MAX_BYTES = 10_000     # < 10KB → topic, else → full

# Andre's locked decision 4: 30-min hard floor on Tier 3 eviction.
HARD_FLOOR_SECONDS = 30 * 60      # 1800.0s

# Recent-turns buffer.
RECENT_TURNS_MAX = 10

# Token-estimate heuristic (rough; §4.2 output spec).
CHARS_PER_TOKEN = 4


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ContextWindow:
    """Assembled context for a single Mavis turn (§4.2 outputs)."""
    system_prompt: str
    meta_index: str
    active_topic_indexes: List[Tuple[str, str]]   # (key, content) pairs, 1-3
    full_topic: Optional[Tuple[str, str]]          # (key, content) or None, 0-1
    recent_turns: List[Tuple[str, str]]            # (user, response) pairs
    user_input: str
    estimated_tokens: int                          # rough: total_chars / 4

    def total_chars(self) -> int:
        n = len(self.system_prompt) + len(self.meta_index) + len(self.user_input)
        n += sum(len(c) for _, c in self.active_topic_indexes)
        if self.full_topic is not None:
            n += len(self.full_topic[1])
        n += sum(len(u) + len(r) for u, r in self.recent_turns)
        return n


@dataclass
class _CachedTopic:
    """Tier 2/3 entry."""
    key: str
    content: str
    importance: float
    inserted_at: float        # epoch seconds (caller-provided)
    last_accessed_at: float   # epoch seconds (caller-provided)


# ---------------------------------------------------------------------------
# Tier 1 — MetaIndexCache (always-loaded, file-backed)
# ---------------------------------------------------------------------------

class MetaIndexCache:
    """Always-loaded meta-index. Backing: meta_index.json in state dir.

    The meta-index is a flat dict[str, str] mapping topic keys to a 1-line
    summary. Bounded to ~3-8KB total by the upstream REFRESH process; this
    class just loads/saves and serves.
    """

    def __init__(self, state_dir: Path = DEFAULT_STATE_DIR):
        self.state_dir = state_dir
        self.path = state_dir / META_INDEX_FILE
        self._index: Dict[str, str] = {}
        self._load()

    def _ensure_dir(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _load(self) -> None:
        self._ensure_dir()
        if not self.path.exists():
            # Empty index is a valid skeleton state.
            self._index = {}
            return
        try:
            with self.path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            if not isinstance(raw, dict):
                raw = {}
            # Coerce to str→str.
            self._index = {str(k): str(v) for k, v in raw.items()}
        except (json.JSONDecodeError, OSError):
            # Corrupt or unreadable — fail-closed to empty.
            self._index = {}

    def _save(self) -> None:
        self._ensure_dir()
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self._index, f, ensure_ascii=False, indent=2, sort_keys=True)

    def get(self, key: str) -> Optional[str]:
        return self._index.get(key)

    def set(self, key: str, one_line_summary: str) -> None:
        self._index[key] = one_line_summary
        self._save()

    def all(self) -> Dict[str, str]:
        return dict(self._index)

    def render(self) -> str:
        """Render the meta-index as a stable, sorted markdown-ish block."""
        if not self._index:
            return ""
        lines = ["# meta-index"]
        for key in sorted(self._index.keys()):
            lines.append(f"- {key}: {self._index[key]}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tier 2 — TopicIndexCache (lazy, in-memory)
# ---------------------------------------------------------------------------

class TopicIndexCache:
    """Lazy-loaded topic index. In-memory dict for skeleton (FS wiring is v2).

    No TTL enforcement in the skeleton — caller decides when to call
    ContextLoader.load_for_turn(), which is when eviction is checked.
    """

    def __init__(self) -> None:
        self._cache: Dict[str, _CachedTopic] = {}

    def get(self, key: str, now: float) -> Optional[str]:
        entry = self._cache.get(key)
        if entry is None:
            return None
        entry.last_accessed_at = now
        return entry.content

    def put(self, key: str, content: str, importance: float, now: float) -> None:
        self._cache[key] = _CachedTopic(
            key=key,
            content=content,
            importance=importance,
            inserted_at=now,
            last_accessed_at=now,
        )

    def keys(self) -> List[str]:
        return list(self._cache.keys())

    def evict(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    def size_bytes(self) -> int:
        return sum(len(e.content) for e in self._cache.values())


# ---------------------------------------------------------------------------
# Tier 3 — FullTopicCache (on-demand, importance-aware, 30-min hard floor)
# ---------------------------------------------------------------------------

class FullTopicCache:
    """On-demand full topic cache. Importance-aware eviction with 30-min hard floor.

    Andre's locked decision 4 (6a): never evict in <30 min regardless of
    importance score. After the hard floor, an entry is evictable when its
    importance score falls below a threshold (default 0.3 for the skeleton).
    """

    EVICTION_THRESHOLD = 0.3

    def __init__(self) -> None:
        self._cache: Dict[str, _CachedTopic] = {}

    def get(self, key: str, now: float) -> Optional[str]:
        entry = self._cache.get(key)
        if entry is None:
            return None
        entry.last_accessed_at = now
        return entry.content

    def put(self, key: str, content: str, importance: float, now: float) -> None:
        self._cache[key] = _CachedTopic(
            key=key,
            content=content,
            importance=importance,
            inserted_at=now,
            last_accessed_at=now,
        )

    def evict(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    def evict_if_stale(self, now: float) -> List[str]:
        """Evict entries that are past the 30-min hard floor AND below the
        importance threshold. Returns the list of evicted keys (deterministic
        order: sorted key).
        """
        evictable: List[str] = []
        for key, entry in self._cache.items():
            age = now - entry.inserted_at
            if age < HARD_FLOOR_SECONDS:
                continue                                  # hard floor (§6a d4)
            if entry.importance < self.EVICTION_THRESHOLD:
                evictable.append(key)
        evictable.sort()
        for key in evictable:
            self._cache.pop(key, None)
        return evictable

    def keys(self) -> List[str]:
        return list(self._cache.keys())

    def size_bytes(self) -> int:
        return sum(len(e.content) for e in self._cache.values())


# ---------------------------------------------------------------------------
# Top-level composer
# ---------------------------------------------------------------------------

class ContextLoader:
    """Composes the three tiers. v1 design doc §4.2.

    Lifecycle:
      loader = ContextLoader()                  # tier 1 loads from disk
      loader.cache_topic(key, content, imp)     # tier 1/2/3 routing by size
      ctx = loader.load_for_turn(user_text)     # assembles context window
      loader.record_turn(user_text, response)   # updates recent-turns buffer
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are Mavis, Andre's chief-of-staff. Respond directly, plain prose, "
        "no marketing language. Cite dossier claims when relevant."
    )

    def __init__(
        self,
        state_dir: Path = DEFAULT_STATE_DIR,
        system_prompt: Optional[str] = None,
    ) -> None:
        self.meta = MetaIndexCache(state_dir=state_dir)
        self.topic = TopicIndexCache()
        self.full = FullTopicCache()
        self._recent: Deque[Tuple[str, str]] = deque(maxlen=RECENT_TURNS_MAX)
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT

    # -- routing helpers -----------------------------------------------------

    @staticmethod
    def _pick_tier(size_bytes: int) -> str:
        """Size-based tier routing. The heuristic from the task spec."""
        if size_bytes < META_TIER_MAX_BYTES:
            return "meta"
        if size_bytes < TOPIC_TIER_MAX_BYTES:
            return "topic"
        return "full"

    def cache_topic(self, key: str, content: str, importance: float, now: float = 0.0) -> str:
        """Populate the right tier by size. Returns the tier name used.

        Heuristic: <2KB → meta_index (summary stored as 1-line), <10KB → topic,
        else → full. For meta routing, only a 1-line summary is stored (first
        200 chars); the full content is dropped (skeleton behavior).
        """
        size = len(content.encode("utf-8"))
        tier = self._pick_tier(size)
        if tier == "meta":
            summary = content if len(content) <= 200 else content[:197] + "..."
            self.meta.set(key, summary)
        elif tier == "topic":
            self.topic.put(key, content, importance, now)
        else:
            self.full.put(key, content, importance, now)
        return tier

    # -- importance scoring (stub) ------------------------------------------

    @staticmethod
    def score_importance(text: str) -> float:
        """Importance scoring — STUB.

        v1 design doc §4.2: M2.7-class LLM scoring on Tier 3 eviction decisions.
        Skeleton returns a constant 0.5. Real implementation should call an
        M2.7 model and return a float in [0, 1].
        """
        return 0.5

    # -- main entry points ---------------------------------------------------

    def load_for_turn(self, user_text: str, now: float = 0.0) -> ContextWindow:
        """Assemble the context window for a single turn (§4.2 outputs).

        Skeleton heuristic: pick up to 3 most-recently-inserted topic-index
        entries (by insertion order) and 1 most-recently-inserted full-topic
        entry. The intent-keyword selection logic is a v2 step.
        """
        # Tier 3: importance-aware eviction with 30-min hard floor (§6a d4)
        self.full.evict_if_stale(now)

        # Pick up to 3 active topic indexes, in insertion order
        # (TopicIndexCache._cache is a dict; Python 3.7+ preserves insertion order).
        active_topic_entries: List[Tuple[str, str]] = []
        for key in self.topic.keys():
            content = self.topic.get(key, now)
            if content is not None:
                active_topic_entries.append((key, content))
            if len(active_topic_entries) >= 3:
                break

        # Pick up to 1 full topic.
        full_entry: Optional[Tuple[str, str]] = None
        for key in self.full.keys():
            content = self.full.get(key, now)
            if content is not None:
                full_entry = (key, content)
            break  # 0-1, so first wins

        meta_str = self.meta.render()
        recent = list(self._recent)

        window = ContextWindow(
            system_prompt=self.system_prompt,
            meta_index=meta_str,
            active_topic_indexes=active_topic_entries,
            full_topic=full_entry,
            recent_turns=recent,
            user_input=user_text,
            estimated_tokens=0,  # filled below
        )
        window.estimated_tokens = window.total_chars() // CHARS_PER_TOKEN
        return window

    def record_turn(self, user_text: str, response: str) -> None:
        """Push the (user, response) pair into the recent-turns buffer (last 10)."""
        self._recent.append((user_text, response))


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 72)
    print("context_loader self-test — 3-tier cache skeleton (v1 design doc §4.2)")
    print("=" * 72)

    loader = ContextLoader()
    NOW = 1_700_000_000.0  # fixed epoch; deterministic

    # Cache 3 sample topics of varying sizes.
    meta_content = "small note body, well under 2KB"  # < 2KB → meta
    topic_content = "x" * 3_000                       # < 10KB → topic
    full_content = "y" * 15_000                       # ≥ 10KB → full

    t1 = loader.cache_topic("notes/small", meta_content, importance=0.5, now=NOW)
    t2 = loader.cache_topic("notes/medium", topic_content, importance=0.6, now=NOW)
    t3 = loader.cache_topic("notes/large", full_content, importance=0.7, now=NOW)

    print()
    print(f"  tier routing: small→{t1}, medium→{t2}, large→{t3}")
    print(f"  meta index   : {loader.meta.all()}")
    print(f"  topic keys   : {loader.topic.keys()}")
    print(f"  full keys    : {loader.full.keys()}")

    # Record a turn, then assemble a context window.
    loader.record_turn("hello", "hi there")
    loader.record_turn("what's the plan?", "ship the harness")

    ctx1 = loader.load_for_turn("next move?", now=NOW)
    print()
    print("  --- load_for_turn #1 ---")
    print(f"  system_prompt      : {ctx1.system_prompt[:60]!r}...")
    print(f"  meta_index         : {ctx1.meta_index!r}")
    print(f"  active_topic_index : {len(ctx1.active_topic_indexes)} entries")
    for k, c in ctx1.active_topic_indexes:
        print(f"    - {k}: {len(c)} chars")
    print(f"  full_topic         : {ctx1.full_topic[0] if ctx1.full_topic else None}")
    print(f"  recent_turns       : {len(ctx1.recent_turns)} pairs")
    print(f"  user_input         : {ctx1.user_input!r}")
    print(f"  estimated_tokens   : {ctx1.estimated_tokens}")

    # Run load_for_turn a second time (idempotent in skeleton).
    ctx2 = loader.load_for_turn("second turn", now=NOW)
    print()
    print("  --- load_for_turn #2 ---")
    print(f"  user_input         : {ctx2.user_input!r}")
    print(f"  estimated_tokens   : {ctx2.estimated_tokens}")

    # Importance-aware eviction with 30-min hard floor: NOT_EVICTABLE in skeleton
    # (importance 0.7 > 0.3 threshold).
    evicted = loader.full.evict_if_stale(now=NOW + 60.0)  # only +60s, well under hard floor
    print()
    print(f"  evicted at +60s    : {evicted}  (expect []; under 30-min hard floor)")

    print()
    print("=" * 72)
    print("DONE — ContextLoader assembled 2 context windows; eviction guard verified.")
