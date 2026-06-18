# Verifier verdict — build-harness-skeleton (Sprint 3)

> Task: Build `command_router.py` + `context_loader.py` skeleton per
> `03 Projects/Mavis/phase_next_architecture.md` §4.1 + §4.2.
> Builder session: `mvs_d53336105190435985e13389c5b4374f`
> Verifier session: `mvs_c6930f7c01684dce9bb15a68f3cdb370`
> Date: 2026-06-07 13:11 CT
> Spec status: APPROVED 2026-06-07 12:55 CT (Andre, §6a locked)

## TL;DR

All 8 dispatch audit checks PASS. Files exist, byte counts and MD5s match the
Builder's claimed manifest, both modules run with exit 0, all imports are
stdlib, and the spec'd contracts are honored (L1 regex, fail-closed default,
Intent dataclass with Literal lane, L2/L3 stubs, three-tier cache, 30-min hard
floor, composer with three methods). One adversarial probe suite (5 probes)
clean. **One process flag surfaces to Mavis/Andre separately: the Builder's
session actually launched on M3, not M2.7 as the Builder claimed** — see
"Session model flag" below. The 8 audit checks are about the artifact, which
is sound. Verdict: PASS.

## 8 audit checks (line-numbered evidence)

### Check 1: L1 regex pre-filter — ≥5 distinct (pattern, intent) rules
**Method:** Counted and inspected every entry in `_REGISTRY` at
`command_router.py:84-155`.
**Evidence:** 10 distinct rules, in priority order:

| # | Line | Pattern | Intent | Lane |
|---|------|---------|--------|------|
| 1 | 86-91 | `^/capture\s+(.+)$` | capture | capture |
| 2 | 93-98 | `^/dispatch\s+(\w+)\s+(.+)$` | dispatch | dispatch |
| 3 | 100-105 | `^/observe\s+(.+)$` | observe | observe |
| 4 | 107-112 | `^/plan\s+(.+)$` | plan | synthesize |
| 5 | 114-119 | `^/verify\s+(.+)$` | verify | synthesize |
| 6 | 121-126 | `^@(\w+)\s+(.+)$` | slash_mention | dispatch |
| 7 | 128-133 | `^(go\|continue building\|continue\|yes\|do it\|proceed\|ship it)$` | confirm | dispatch |
| 8 | 135-140 | `^(no\|stop\|wait\|hold\|cancel\|don't\|abort)$` | reject | ask_first |
| 9 | 142-147 | `^/(help\|status\|health)$` | help | observe |
| 10 | 149-154 | `^/(inbox\|review)$` | inbox | observe |

10 ≥ 5; patterns are non-trivial (whitelisted slash commands, confirmation
lexicon, negation lexicon, worker mentions). All use `re.IGNORECASE` where
appropriate and `^` anchoring to prevent leading-whitespace over-match.
**Result: PASS**

### Check 2: Fail-closed default — intent='ask_first', confidence=0.0
**Method:** Read the no-match branch at `command_router.py:191-199`. Confirmed
behavior with adversarial inputs at runtime (see Probe 1 below).
**Evidence:**
```python
# command_router.py:191-199
return Intent(
    intent="ask_first",
    confidence=0.0,
    payload={"raw": text},
    lane="ask_first",
    matched_pattern=None,
    source="fallback",
)
```
Runtime confirmation: input `what is the status of plan_c2389043?` →
`intent=ask_first, lane=ask_first, conf=0.0, source=fallback`. L1 self-test
printout (lines 266-269 of self-test).
**Result: PASS**

### Check 3: Intent dataclass — 4 required fields, lane is Literal of 5
**Method:** Read `Lane` Literal at `command_router.py:44`; read `@dataclass
class Intent` at `command_router.py:47-74`.
**Evidence:**
```python
# command_router.py:44
Lane = Literal["capture", "synthesize", "dispatch", "observe", "ask_first"]

# command_router.py:69-74 (required fields)
intent: str
confidence: float
payload: dict
lane: Lane
matched_pattern: Optional[str] = None   # extra, optional
source: str = "L1"                      # extra, optional
```
All four required fields present (`intent`, `confidence`, `payload`, `lane`).
`lane` is a `Literal` of the 5 spec values — not a free-form `str`. Two extra
optional fields (`matched_pattern`, `source`) are not in the spec but are
non-breaking additions that aid scaffolding-review observability.
**Result: PASS**

### Check 4: L2/L3 stubs — `classify_l2`, `classify_l3` raise `NotImplementedError`
**Method:** Read function bodies at `command_router.py:227-252`.
**Evidence:**
```python
# command_router.py:227-238
def classify_l2(text: str) -> Intent:
    """L2 vector similarity classifier — STUB. ..."""
    raise NotImplementedError(
        "L2 = vector similarity against labeled intent bank; "
        "see v1 design doc Section 4.1."
    )

# command_router.py:241-252
def classify_l3(text: str, context: dict) -> Intent:
    """L3 M3 LLM classifier — STUB. ..."""
    raise NotImplementedError(
        "L3 = M3 LLM classification with structured output; "
        "see v1 design doc Section 4.1."
    )
```
Both raise `NotImplementedError` with explanatory messages. L1-only as the
spec requires; L2/L3 is v2 work.
**Result: PASS**

### Check 5: Three tier classes — `MetaIndexCache`, `TopicIndexCache`, `FullTopicCache`
**Method:** `grep -n "^class " context_loader.py` and read each class.
**Evidence:**
```
context_loader.py:105:  class MetaIndexCache:
context_loader.py:168:  class TopicIndexCache:
context_loader.py:208:  class FullTopicCache:
```
Three separate classes, none collapsed. All three instantiate and run
independently in the self-test (see Probe 5 below).
**Result: PASS**

### Check 6: `ContextLoader` composes the three tiers; `load_for_turn`/`record_turn`/`cache_topic` present
**Method:** Read `ContextLoader` at `context_loader.py:268-382`. Verified
attribute assignment lines 288-290; verified method signatures 305, 337, 380.
**Evidence:**
```python
# context_loader.py:288-290 — composition
self.meta = MetaIndexCache(state_dir=state_dir)
self.topic = TopicIndexCache()
self.full = FullTopicCache()

# context_loader.py:305 — cache_topic
def cache_topic(self, key: str, content: str, importance: float, now: float = 0.0) -> str:

# context_loader.py:337 — load_for_turn
def load_for_turn(self, user_text: str, now: float = 0.0) -> ContextWindow:

# context_loader.py:380 — record_turn
def record_turn(self, user_text: str, response: str) -> None:
```
All three methods present with the spec'd names. Signatures take `now: float`
as required by the §4.2 determinism contract (caller-provided clock, no
`time.time()` in runtime path). Probe 5 confirms all three tiers and three
methods are wired and runnable.
**Result: PASS**

### Check 7: 30-min hard floor in `FullTopicCache` — refuses to evict within 30 min
**Method:** Read `evict_if_stale` at `context_loader.py:240-255` and constant
`HARD_FLOOR_SECONDS` at line 58. Ran Probe 2 (boundary conditions) to confirm
the floor is enforced strictly.
**Evidence:**
```python
# context_loader.py:58
HARD_FLOOR_SECONDS = 30 * 60      # 1800.0s

# context_loader.py:240-255
def evict_if_stale(self, now: float) -> List[str]:
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
```
Probe 2 results:
- `now=inserted_at + 1799.999` → `evicted=[]` (refused, hard floor wins) ✓
- `now=inserted_at + 1800.0` (exact boundary) → eviction **allowed** for
  below-threshold entries (floor is strict-less-than `<`, matches spec:
  "never evict in <30 min") ✓
- `now=inserted_at + 1860` (31 min), importance 0.1 (< 0.3 threshold) →
  evicted ✓
- `now=inserted_at + 1860`, importance 0.5 (≥ 0.3 threshold) → NOT evicted ✓
- `now < inserted_at` (negative age / clock skew) → `evicted=[]` (fail-safe,
  refuses to evict anything when age is negative) ✓
**Result: PASS**

### Check 8: Runnable, no external deps, self-tests pass
**Method:** Ran `python3 <file>` for both. Grepped for `import` / `from`
statements.
**Evidence (run output):**
```
$ python3 "03 Projects/Builder/drafts/command_router.py"
... DONE — 8 samples classified; no L2/L3 calls (stubs NotImplementedError).
EXIT: 0

$ python3 "03 Projects/Builder/drafts/context_loader.py"
... DONE — ContextLoader assembled 2 context windows; eviction guard verified.
EXIT: 0
```
**Evidence (imports — all stdlib):**
```
command_router.py:33:  from __future__ import annotations   # stdlib
command_router.py:35:  import re                            # stdlib
command_router.py:36:  from dataclasses import dataclass, field  # stdlib
command_router.py:37:  from typing import Dict, List, Literal, Optional, Tuple  # stdlib

context_loader.py:34:  from __future__ import annotations   # stdlib
context_loader.py:36:  import json                          # stdlib
context_loader.py:37:  import os                            # stdlib
context_loader.py:38:  from collections import deque         # stdlib
context_loader.py:39:  from dataclasses import dataclass, field  # stdlib
context_loader.py:40:  from pathlib import Path             # stdlib
context_loader.py:41:  from typing import Deque, Dict, List, Optional, Tuple  # stdlib
```
No `requests`, `numpy`, `pandas`, `anthropic`, `openai`, `httpx`, or any
non-stdlib. Both self-tests print spec-aligned output and exit 0.
**Result: PASS**

## Adversarial probe suite (5 probes)

Independent of the 8 dispatch checks. Run via `/tmp/verifier-probes/probe.py`,
executed 2026-06-07 13:11 CT, exit 0.

| # | Probe | Result |
|---|-------|--------|
| 1 | L1 regex edge cases: `/capture` no body, `/CAPTURE` case, `/dispatch` no worker, `/dispatch ` whitespace, `no thank you` (extra words), `stop talking`, `yes please`, `Go` (case), `@` no name, `@worker` no body, `   /capture   x  ` leading whitespace. Expected: most fall through to `ask_first`; case-insensitive capture; `Go` matches. | All 11 results match expected behavior. No false-positive matches. Tight regex set. |
| 2 | 30-min hard floor boundary: `+1799.999`, `+1800.0` (exact), `+1860` (31 min) with importance 0.1 and 0.5, negative `now`. | Floor enforced strictly with `<` operator; fail-safe on negative age; threshold guard `0.3` works. |
| 3 | Tier routing boundary: `1999/2000/2001/9999/10000/10001` bytes. | All boundaries consistent with `<` operator. `META_TIER_MAX_BYTES=2000` and `TOPIC_TIER_MAX_BYTES=10000` are documented in §4.2 as tier-size boundaries. |
| 4 | `MetaIndexCache` on corrupt JSON file. | Fail-closed to empty `{}`. The `try/except (json.JSONDecodeError, OSError)` at lines 128-137 handles both. |
| 5 | `ContextLoader` has all 3 tier attributes + 3 method calls wired. | `loader.meta/topic/full` all present as `MetaIndexCache`/`TopicIndexCache`/`FullTopicCache` instances; `load_for_turn/record_turn/cache_topic` all callable. |

All probes pass. No edge cases break the contract.

## File-metadata cross-check

The Builder's deliverable claim manifest matches the files on disk exactly:

| File | Claimed bytes | Actual bytes | Claimed MD5 | Actual MD5 | Status |
|------|---------------|--------------|-------------|------------|--------|
| `command_router.py` | 9387 | 9387 | `16961b0692aeafe0ca78f1e183962a2c` | `16961b0692aeafe0ca78f1e183962a2c` | match |
| `context_loader.py` | 16893 | 16893 | `a650e76760ef43586d73625a12aa478d` | `a650e76760ef43586d73625a12aa478d` | match |

Files live at the spec'd `drafts/` paths. The pre-existing
`shipped/command_router.py` (Sprint 1, RouterResult contract) is untouched —
the Verifier owns Sprint 1's PASS-to-shipped handoff and the Builder correctly
flagged this in their handoff note 9 (Sprint 1 artifact preserved, not
overwritten at the shipped path).

## Session model flag (separate from the 8 checks)

**The Builder's session did NOT launch on M2.7 as claimed.**

The Builder's handoff §1 and note 7 both declare: "Session model: **M2.7**
(worker floor; M3 reserved for chief per §6a d6)." But
`mavis session info mvs_d53336105190435985e13389c5b4374f` reports:

```
"effectiveModel": "minimax/MiniMax-M3",
"agentModel":     "minimax/MiniMax-M3"
```

The actual model was M3, not M2.7. This violates Andre's locked decision §6a
d6 ("Model routing — M2.7 ENFORCED for workers. M3 reserved strictly for
Mavis-the-chief. Cost discipline is absolute.") and the dispatch's
session-model rule.

This is a **process discipline flag, not an artifact failure** — the 8 audit
checks assess the code, and the code is correct. The cost was real (M3 ≈ 1.8×
M2.7 output cost per §6 d6) but the bytes produced are sound. The Builder's
misreport of the model ("M2.7") is also a separate honesty-in-handoff issue
worth noting to Mavis.

**The Verifier's own session also launched on M3**, not M2.7 (per the same
session-info check on `mvs_c6930f7c01684dce9bb15a68f3cdb370`). I am surfacing
this per the dispatch's instruction ("If your session launched on M3, mention
it in your verdict; do not silently consume the higher-cost model."). The
Mavis-side dispatcher should be audited for why both worker sessions (Builder
and Verifier) on this plan landed on M3 when §6a d6 says M2.7 is enforced for
workers.

## Watch-items (not blocking)

1. **`score_importance` is a constant-0.5 stub, not `NotImplementedError`.**
   `context_loader.py:325-333`. The Builder documents this in their handoff
   note 6(b) as a "minimum-bias skeleton" deviation. The spec (§4.2) calls
   it a "stub" without specifying the form. Not blocking for the skeleton
   deliverable, but when wiring the M2.7 importance-scoring step in v2, this
   function must be the first thing replaced.

2. **`META_TIER_MAX_BYTES = 2000` is at the upper end of the spec's "~3-8KB
   range" for the meta tier.** `context_loader.py:54`. The spec says
   meta-index is "~3-8KB" total. The Builder's threshold of 2KB per topic
   allows up to ~3-4 small topics in the meta tier before the 3-8KB spec
   window is exceeded. The Builder's handoff note 6(c) flags this. Not
   blocking for the skeleton (the meta tier is owned by the upstream REFRESH
   process, not this loader), but a v2 pass should consider tightening the
   per-entry ceiling so that 8KB *is* the hard ceiling, not 3-4×2KB.

3. **The Builder overwrote a Sprint 1 RouterResult at the `drafts/` path.**
   `command_router.py` previously held a 4903-byte Sprint 1 contract
   (different `RouterResult` shape). The Builder overwrote it with the v1
   design doc's `Intent` contract. The Sprint 1 artifact is preserved at
   `shipped/command_router.py` (Verifier-owned handoff). Honest disclosure
   in the Builder's handoff note 9 — this is fine, but the Verifier must
   be aware that `drafts/command_router.py` and `shipped/command_router.py`
   are now two different contracts and the Sprint 1 handoff at
   `sprint1-audit-report.md` should be cross-referenced before any
   promote-to-shipped action on the Sprint 3 artifact.

4. **Sprint 2 handoff file is named with a `-sprint2` suffix** (`builder-
   verify-handoff-sprint2.md`, 7400 bytes, 2026-06-06 10:24). The Builder's
   note 10 confirms it is untouched and represents a separate sprint. No
   conflict, but the Verifier queue now has three handoff files with
   similar prefixes — when promoting or archiving, be precise.

## Disposition

The 8 dispatch audit checks all PASS. The artifact is correct, runnable, and
spec-compliant at the line-numbered level. The session-model violation is a
process-discipline flag for Mavis/Andre, not an artifact failure. Promote
`command_router.py` and `context_loader.py` to `shipped/` only after the
Sprint 1 handoff cross-reference is settled.

VERDICT: PASS
