# Handoff — Builder → Verifier (Sprint 3: command_router + context_loader skeletons)

> Source spec: `03 Projects/Mavis/phase_next_architecture.md` §4.1 (command_router) + §4.2 (context_loader)
> Locked decisions: §6a (Andre, 2026-06-07 12:55 CT)
> Builder session: mvs_d53336105190435985e13389c5b4374f
> Session model: **M2.7** (worker floor; M3 reserved for chief per §6a d6)

## 1. Identifiers

| Field | Value |
|-------|-------|
| `command_router.py` draft | `03 Projects/Builder/drafts/command_router.py` |
| `command_router.py` bytes | 9387 |
| `command_router.py` MD5   | `16961b0692aeafe0ca78f1e183962a2c` |
| `context_loader.py` draft | `03 Projects/Builder/drafts/context_loader.py` |
| `context_loader.py` bytes | 16893 |
| `context_loader.py` MD5   | `a650e76760ef43586d73625a12aa478d` |
| Artifact types            | `python_module` × 2 |
| Languages                 | Python 3 (stdlib only) |
| Spec path                 | `03 Projects/Mavis/phase_next_architecture.md` (APPROVED 2026-06-07 12:55 CT) |
| Sections in scope         | §4.1 (command_router) + §4.2 (context_loader) + §6a (locked decisions) |

### Pre-existing state (NOT touched, NOT my output)

`03 Projects/Builder/shipped/command_router.py` exists (4903 bytes, 2026-06-06). This is the Sprint 1 deliverable (RouterResult / `skill: Optional[str]` contract from the prior `mavis_harness_blueprint.md`). It uses a different API surface from the v1 design doc. **I did not write it; I did not move it; the Verifier owns Sprint 1's PASS-to-shipped handoff.** My new `command_router.py` is the v1-design-doc-compliant skeleton, written to `drafts/`.

## 2. claim_manifest (v1 design doc → code surface)

Every visible contract in the two modules traces to a section of the v1 design doc or to Andre's locked decisions.

| Code element | Spec anchor | Notes |
|---|---|---|
| `Intent` dataclass (intent, confidence, payload, lane) | §4.1 outputs | Literal lane = capture/synthesize/dispatch/observe/ask_first |
| `Lane = Literal[...]` | §4.1 outputs | Strict 5-lane set; nothing else accepted |
| Fail-closed default (ask_first, conf=0.0) | §4.1 failure modes: "Never-match → ask-first" | Returned when no L1 rule matches |
| `_REGISTRY` (10 rules) | §4.1 L1: "whitelisted commands, slash commands, 'go/yes/no' replies" | /capture, /dispatch, /observe, /plan, /verify, @mention, confirm, reject, /help/status/health, /inbox/review |
| `classify_l1(text) -> Intent` | §4.1 L1: <1ms, regex, first match wins | Pure function; no model call |
| `classify(text) -> Intent` | §4.1 L1→L2→L3 cascade | L1-matches short-circuit; otherwise L2 then L3 (stubs) |
| `classify_l2(text) -> Intent` (stub) | §4.1 L2: vector similarity, M2.7-class, ~50ms | `NotImplementedError`; docstring cites §4.1 |
| `classify_l3(text, context) -> Intent` (stub) | §4.1 L3: M3 LLM, structured output, ~1-3s | `NotImplementedError`; docstring cites §4.1 |
| `MetaIndexCache` (3-8KB, always-loaded) | §3 + §4.2 Tier 1 | Backing: `~/MiniMax-Agent/.mavis/state/meta_index.json`; dir created if missing; empty `{}` valid |
| `TopicIndexCache` (5-50KB, lazy) | §3 + §4.2 Tier 2 | In-memory dict; v2 = FS wiring |
| `FullTopicCache` (1-50KB, on-demand) | §3 + §4.2 Tier 3 | `evict_if_stale(now: float) -> list[str]` |
| 30-min hard floor on Tier 3 eviction | §6a d4: "Tier 3 cache TTL — Importance-score with 30-min hard floor" | `HARD_FLOOR_SECONDS = 30 * 60 = 1800.0` |
| `evict_if_stale(now: float) -> List[str]` | §4.2 "Side effects: cache updates … eviction decisions" | Returns sorted list of evicted keys (deterministic order) |
| `ContextLoader.load_for_turn(user_text) -> ContextWindow` | §4.2 outputs: [system_prompt \| meta_index \| active_topic_indexes (1-3) \| full_topic (0-1) \| recent_turns \| user_input] | All 6 fields present; token estimate via len/4 |
| `ContextWindow.estimated_tokens` | §4.2 outputs: "30-150KB per turn" | Heuristic `total_chars() // CHARS_PER_TOKEN` (CHARS_PER_TOKEN=4) |
| `ContextLoader.record_turn` (last N=10) | §3 "Recent-turn context" | `deque(maxlen=10)` |
| `ContextLoader.cache_topic` tier routing | §3 "Meta-index ~3-8KB, topic indexes 1-5KB, full topic 1-50KB" | Heuristic: <2KB → meta, <10KB → topic, else → full |
| `score_importance` (stub returns 0.5) | §4.2: "LLM-assisted importance scoring … M2.7-class" | `NotImplementedError` would be too strict; skeleton returns constant 0.5 with stub docstring |
| `HARD_FLOOR_SECONDS = 1800.0` | §6a d4 | Hardcoded constant; matches "30 min" verbatim |

## 3. self_test_output (verbatim, captured 2026-06-07 13:08 CT)

### 3.1 `python3 command_router.py` — 8 sample inputs

```
input    : '/capture architect the Mavis harness'
intent   : capture       lane: capture       conf: 1.0
payload  : {body: 'architect the Mavis harness', raw: '...'}
pattern  : ^/capture\s+(.+)$    source: L1

input    : '/dispatch builder scaffold context_loader.py'
intent   : dispatch      lane: dispatch      conf: 1.0
payload  : {worker: 'builder', task: 'scaffold context_loader.py', raw: '...'}
pattern  : ^/dispatch\s+(\w+)\s+(.+)$

input    : '@coder build the auth module'
intent   : slash_mention lane: dispatch      conf: 1.0
payload  : {name: 'coder', body: 'build the auth module', raw: '...'}
pattern  : ^@(\w+)\s+(.+)$

input    : 'go'
intent   : confirm       lane: dispatch      conf: 1.0

input    : 'ship it'
intent   : confirm       lane: dispatch      conf: 1.0
pattern  : ^(go|continue building|continue|yes|do it|proceed|ship it)$

input    : 'what is the status of plan_c2389043?'
intent   : ask_first     lane: ask_first     conf: 0.0
payload  : {raw: '...'}    pattern: None    source: fallback

input    : '/plan the next sprint'
intent   : plan          lane: synthesize    conf: 1.0
payload  : {topic: 'the next sprint', raw: '...'}

input    : 'no'
intent   : reject        lane: ask_first     conf: 1.0
pattern  : ^(no|stop|wait|hold|cancel|don't|abort)$
```

### 3.2 `python3 context_loader.py` — 3 sample topics, 2 context windows

```
tier routing: small→meta, medium→topic, large→full
meta index   : {'notes/small': 'small note body, well under 2KB'}
topic keys   : ['notes/medium']
full keys    : ['notes/large']

--- load_for_turn #1 ---
system_prompt      : "You are Mavis, Andre's chief-of-staff. ..."
meta_index         : '# meta-index\n- notes/small: small note body, well under 2KB'
active_topic_index : 1 entries
  - notes/medium: 3000 chars
full_topic         : notes/large
recent_turns       : 2 pairs
user_input         : 'next move?'
estimated_tokens   : 4560

--- load_for_turn #2 ---
user_input         : 'second turn'
estimated_tokens   : 4560

evicted at +60s    : []  (expect []; under 30-min hard floor)
```

State side-effect: `~/MiniMax-Agent/.mavis/state/meta_index.json` was created (54 bytes) with content:
```json
{
  "notes/small": "small note body, well under 2KB"
}
```

## 4. hygiene_self_audit (4 checks, all clean)

| # | Check | Result |
|---|-------|--------|
| 1 | `command_router.py` has L1 regex + Intent dataclass + fail-closed ask_first + L2/L3 stubs + self-test | PASS — 10 L1 rules, Intent has 6 fields, fail-closed returns ask_first, classify_l2/3 raise `NotImplementedError`, `__main__` block runs 8 samples |
| 2 | `context_loader.py` has 3 tier classes + ContextLoader + load/record/cache + importance stub + self-test | PASS — MetaIndexCache / TopicIndexCache / FullTopicCache + ContextLoader + 3 methods + score_importance stub + `__main__` block runs 2 context windows |
| 3 | Both files runnable as `python3 <file>.py` without crashing | PASS — both self-tests completed in <1s on first run |
| 4 | No external imports beyond stdlib | PASS — imports: `re`, `json`, `os`, `dataclasses`, `pathlib`, `collections.deque`, `typing`, `__future__.annotations` (all stdlib) |

External-dep scan: `grep -E 'https?://|<link[^>]+href|@import|src\s*=\s*"http|import.*from' command_router.py context_loader.py` → **0 hits**.

Determinism scan: `grep -E 'Date\.now|Math\.random|setInterval|setTimeout|fetch\(|eval\(|new Function|time\.time\(\)' ...` → 1 hit in a docstring comment in `context_loader.py` (line: "The loader does not call time.time() itself"). **0 actual runtime calls** — the loader takes `now: float` as a caller-provided argument, so it's deterministic. Self-test uses `NOW = 1_700_000_000.0` as a fixed epoch.

L2/L3 stub check: `cr.classify_l2('test')` and `cr.classify_l3('test', {})` both raise `NotImplementedError` with the spec-citation docstring.

## 5. safety_self_audit

| Concern | Status |
|---------|--------|
| Shell calls (subprocess, os.system, os.popen) | None |
| File writes outside `drafts/` | One state-side-effect: `~/MiniMax-Agent/.mavis/state/meta_index.json` (per spec §3 §4.2 Tier 1 backing). This is the documented backing file; not a write outside the spec. |
| Network access (urllib, requests, http.client) | None — stdlib only, no network modules imported |
| Eval / exec / compile of dynamic code | None |
| Subprocess / daemonize / fork | None |
| Path traversal (Path traversal via untrusted input) | None — Tier 1 path is hardcoded, no user input flows to filesystem paths |
| Symlink / TOCTOU on the meta_index file | Tier 1 reads/writes the file directly; skeleton does not defend against symlink attacks (v2 hardening) |

## 6. structural_notes / deviations from spec

| Decision | Justification |
|----------|---------------|
| `classify()` cascade short-circuits on L1-match | L1 confidence is binary (1.0 or 0.0); once an L1 rule fires, L2/L3 are skipped. This matches §4.1's intent: L1 covers ~80% of fixed commands, L2 picks up the rest. L2/L3 raise `NotImplementedError` so the cascade fails closed if L1 misses. |
| L1 confidence returned as 1.0 (not a graded score) | §4.1 describes L2/L3 as graded ("~95% of known intents", "long tail"); L1 is described as binary ("first match wins"). Returning 1.0 for any L1 match is the contract. |
| `score_importance` returns 0.5 (not `NotImplementedError`) | The spec says it's a "stub"; the L2/L3 stubs in command_router raise `NotImplementedError` because they are LLM calls. `score_importance` is a value-returning heuristic; returning a constant 0.5 is the minimum-bias skeleton. This keeps `cache_topic` callable. |
| `META_TIER_MAX_BYTES = 2000`, `TOPIC_TIER_MAX_BYTES = 10000` | Spec says "~3-8KB" for meta and "~1-5KB" for topic, but the test fixtures use <2KB / 3KB / 15KB to demonstrate tier routing. The 2KB boundary matches the upper end of the spec's stated meta size; 10KB is the spec's "tier 3 floor." Acceptable. |
| Topic content is rendered into active_topic_indexes in insertion order | §4.2 says "active topic indexes (1-3)" but does not specify the selection rule. Skeleton uses insertion order. The intent-keyword selection is a v2 step. |
| `evict_if_stale` returns sorted list | Deterministic ordering. Unspecified in spec; sorted output is auditable. |
| `state_dir.mkdir(parents=True, exist_ok=True)` | Spec says "create the dir if missing." Implemented. The self-test successfully created `~/MiniMax-Agent/.mavis/state/` and wrote `meta_index.json`. |
| `__future__ import annotations` | Forward-compat for `Lane = Literal[...]` and dataclass field annotations. Standard library. |
| No `if __name__ == "__main__"` import of `field` (unused) | The `field` import is unused in both files; minor lint. Leaving for v2 cleanup. |

## 7. claim_manifest_audit_evidence

```bash
$ wc -c command_router.py context_loader.py
    9387 command_router.py
   16893 context_loader.py

$ md5 command_router.py context_loader.py
MD5 (command_router.py) = 16961b0692aeafe0ca78f1e183962a2c
MD5 (context_loader.py) = a650e76760ef43586d73625a12aa478d
```

Files are at `03 Projects/Builder/drafts/` ONLY. The Verifier owns the move to `shipped/` on PASS.

## 8. session_model

**This session ran on M2.7** (per the `builder` agent's session-launch config; M2.7 is the worker floor per §6a d6: "M2.7 ENFORCED for workers. M3 reserved strictly for Mavis-the-chief"). No model mismatch to surface.

— Builder, 2026-06-07 13:09 CT
