---
type: moc
purpose: session-continuity layer — read FIRST on every cold start, updated at every session end
update-cadence: per session (start = read, end = regenerate)
created: 2026-06-02
updated: 2026-06-02 (end of session 5 — Chimera + Daedalus + Prometheus shipped, Omni-Loop active, 86 tests passing)
owner: Mavis (self-maintained via 99 _system/scripts/update_state_of_mavis.py)
related: [[MAVIS]] (weekly context), [[SOUL]] (permanent identity), [[agent]] (procedures), [[ESALEN-NOT-FOXCONN]] (operating posture), [[GUI Automation Gated on Operator Toggles]] (operator-gated capabilities), [[Pytest Skill Pack Module Namespacing]] (new Instinct from this session)
---
# state-of-mavis — where we are right now

> The session-continuity layer. MAVIS.md tells the next session *what's fresh this week*. This file tells the next session *what's open right now*.
> Read on cold start. Rewrite before signing off.

---

## Operating envelope (this session)

- **Model**: `minimax/MiniMax-M3` (thinking mode default: on)
- **Role**: EA + Omni-Operator. Persistent heartbeat active (4h interval).
- **Vault root**: `/Users/brassfieldventuresllc/MiniMax-Agent/`
- **Active session**: `mvs_07595ff541f1404da332890f60634809`
- **Date**: 2026-06-02 (Tuesday)
- **Mavis's stance today**: build mode — closed 3 Operations in one session (Chimera, Daedalus, Prometheus). Pushed 2 commits. Heartbeat loaded.
- **Posture**: Esalen, not Foxconn. Audit Q1+Q2 pass across all 4 new code surfaces (Resolver, Daemon, vision-anchor, Instinct).

---

## Just-shipped (since last update)

8 commits since the last state-of-mavis update at `4d99bd8`.

### Operation Ouroboros (sessions 4 prep)

- **Friction 9 (vault-brain stop-words)** — held for v0.2.0; the test query worked, no real failure yet.
- **Friction 12 (locked paths must be audited, not assumed)** — codified as Instinct 2026-06-02-006. The harvester's `note` field now surfaces missing-file gaps.
- **Intake + Instincts harvesters** — `generate_instincts.py` runs as dry-run by default; `--apply` is gated. Locked in `99 _system/instincts/`.

### Session 5 (this regen) — Chimera, Daedalus, Prometheus

**Operation Chimera** — Resolver MCP + 3 Skill Packs refactored to Esalen anatomy
- `99 _system/mcps/resolver/` — 626-line deterministic router. No LLM call inside. M3 does the classification; Python does the I/O + validation.
- 3 Skill Packs refactored: daily-brief, deep-research, weekly-connections (each: skill.md + `<slug>_action.py` + `test_<slug>_action.py`)
- 74 tests passing (17 resolver + 12 daily-brief + 13 deep-research + 12 weekly-connections + 20 process-inbox from prior merge)
- Commit `f6fe9ba` — 18 files, +2754/-114

**Operation Daedalus** — Dispatcher + Hands
- `99 _system/scripts/mavis_daemon.py` (582 lines) — tiered autonomy. GREEN auto-executes, YELLOW writes Inbox alert and skips, RED refuses. can_i() gate on every action. Dry-run by default; `--apply` opt-in.
- `99 _system/mcps/macos-vision-anchor/` (the 4th MCP) — vision-anchored UI element locator. M3 does the visual reasoning; Python does the I/O + parsing. 12 unit tests.
- Static-screenshot test verified: "Click Here" button found at exact x=100, "Submit" button found at exact x=500/y=500, negative case (purple gear) correctly returns found=false.
- Pytest Instinct i-2026-06-02-009 captured the module-name shadowing gotcha (process-inbox uses legacy `action.py`; the 3 refactored packs use `<slug>_action.py` to avoid collision).
- 86 tests passing total (74 prior + 12 vision-anchor).
- Commit `e62df85` — 7 files, +1301

**Operation Prometheus** — Heartbeat activation
- `git push origin main` — both commits pushed. `f1fd1ac..e62df85`.
- `~/Library/LaunchAgents/com.mavis.daemon.plist` — 4h interval, RunAtLoad=false, no startup churn.
- Manual kickstart verified: `runs=1, last exit code=0`. Audit log has a new entry with the kickstart timestamp.
- Omni-Operator is live. The Daemon is the heartbeat. The vault is the body. M3 (when invoked) is the brain.

### Process discipline wins

- **The "184 tests" hallucination was caught and corrected to 74** — the ground-truth audit pattern held. Trust the test runner, not the spec narrative.
- **The Resolver is NOT autonomous** — its own README says "router, not a dispatcher." Daedalus built the dispatcher.
- **process-inbox is a STUB in the Daemon** — needs M3's JSON output, which the Daemon cannot produce without violating "model judges itself." v0.2.0 will wire an offline classifier or session handoff. This was the right call; an alternative would have been a Foxconn loop.

---

## Open loops (live right now — pick up here next session)

### High priority

- **Daily-brief 2-week habit gate** — state-of-mavis.md L84 deferred daily-brief cron automation until 14 on-demand invocations are recorded. The Daemon treats daily-brief as YELLOW-tier until then. The clock starts the first time you call daily-brief; today is invocation 0. Use it on-demand for 2 weeks, then the gate opens.
- **process-inbox stub → real classifier** — the Daemon's `execute_skill("process-inbox")` returns a stub list (per-inbox-file, with "needs M3 JSON" notes). v0.2.0 options: (a) offline rule-based classifier (folder = filename keyword), (b) hand off to the next M3 session via 00 Inbox/ queue, (c) defer to user (write Inbox alert, wait for explicit invocation). Pick one.
- **macos-vision-anchor live-screencapture authorization** — the static-screenshot test passed, but no live screencapture has been authorized. The first live use (e.g., "click the Save button in Numbers") needs an explicit per-action go, like all cu/desktop_ actions per SOUL.

### Medium priority

- **Mavis Daemon first real run** — heartbeat is on a 4h interval, but the kickstart was idle (Tuesday 3:42 PM, no inbox). The first real run will be when state changes (inbox non-empty, Sunday evening, 6-7 AM, etc.). Watch `99 _system/logs/daemon-runs.jsonl` for the first non-idle entry.
- **SOUL compliance eval set** — 40 items to author per the 5-category outline. Co-design answers still pending.
- **Phase B SkillOpt** — install + first training pass + audit best_skill.md. Pending greenlight.
- **Heartbeat kill switch** — `launchctl unload ~/Library/LaunchAgents/com.mavis.daemon.plist` halts the Daemon. The plist file stays; `launchctl bootstrap` re-loads. Document this in `agent.md` for cold-start reference.

### Low priority

- **M3 Eval Lab first run** — 0 runs to date. The eval pattern is set up; no data.
- **Local REST API auth** — broken since 2026-06-01. Held.
- **06 Connections/** — weekly-connections will fire on Sunday evenings via the Daemon. First real run = first data point.

### Carry-forward

- Direct-Intake MCP build (design exists, no build greenlight)
- `update_state_of_mavis.py` script → v0.1.0 → run for 2-3 more sessions before skillifying (this is regen #3; pattern holding)
- Long-context-curator, tool-self-healer MCP builds (designs exist, no greenlight)

---

## Deferred (decided-not-now, with reason)

| Item | Why deferred | Revisit when |
|------|--------------|--------------|
| Daily-brief cron automation | Per state-of-mavis L84 + Daemon YELLOW tier; 14 invocations needed | After 14 on-demand invocations |
| `cu` MCP probe (renderer toggle) | Per `[[GUI Automation Gated on Operator Toggles]]`: blocked on operator-side toggle flip | When Andre flips the renderer toggle |
| macos-vision-anchor live screencapture | YELLOW-tier per SOUL; static-screenshot test verified the design, but live use needs per-action go | On first live use case |
| 1M context full-vault load test | Vault at ~80 notes now | When vault hits 500+ notes |
| M3 technical report deep-dive | Not published yet | When it lands |
| Smart Connections vs M3 native A/B | Need a stable vault to A/B on | After a few weeks of real captures |
| Building long-context-curator / tool-self-healer | Apex designs exist, no build greenlight | Per individual greenlight |
| Self-evolving SOUL via SkillOpt | SOUL compliance eval set must exist first | After the 40-item eval set is authored and run once |
| Semantic-layer upgrade for vault-brain (embeddings) | M3 synthesis handles the noise well enough for v0.1.0; held for v0.2.0 | When anchor-ends + BM25 isn't enough |
| Daemon run-at-load | Currently RunAtLoad=false to avoid startup churn. Could enable if the first run is the most valuable. | When you want the Daemon to also fire on boot |

---

## Decisions landed (this session, or recently)

1. **Friction 13 (ground-truth audit over spec narrative)** — When a directive claims X (e.g., "184 tests"), the assistant runs X independently before executing. Spec blocks are design reviews; the test runner + filesystem are ground truth. A spec that doesn't survive the audit gets the corrected version.
2. **Friction 14 (kebab-case MCP filenames need importlib shim)** — `macos-vision-anchor.py` is a valid CLI filename but breaks `import` in pytest. Tests use `importlib.util.spec_from_file_location` to load by path. Future kebab-case MCPs need the same shim; rename to underscores only if a real need arises.
3. **The Resolver is a router, not a dispatcher** — Operation Chimera closed the routing layer; Operation Daedalus built the dispatcher on top. The two are distinct, both needed. The Resolver's README already said this; Daedalus makes it operational.
4. **The Daemon does NOT call M3 (Esalen Q1+Q2)** — process-inbox is a STUB. Alternative would have been a Foxconn loop ("the Daemon calls M3 to produce the routing JSON, then calls M3 again to verify"). Rejected. v0.2.0 will wire an offline classifier or a session handoff.
5. **Tiered autonomy policy locked** — GREEN auto-executes, YELLOW writes Inbox alert and skips, RED refuses. The policy is in `99 _system/scripts/mavis_daemon.py` `TIER_POLICY`. No YELLOW skill ever auto-executes — the human sees the alert and decides. This is the "abort-window" you asked for, implemented as a human-in-the-loop handoff (better than a 60s timer for an unattended cron).
6. **Launchd plist is outside the vault** — `~/Library/LaunchAgents/com.mavis.daemon.plist` is NOT in the vault repo. The Daemon script IS in the vault. The plist references the script by absolute path. This is intentional: the plist is a state mutation (YELLOW-tier per SOUL), not source code. The vault stays pure markdown + Python; the schedule lives in macOS where it belongs.
7. **Operations naming pattern locked** — Ouroboros → Leviathan → Omniscience → Chimera → Daedalus → Prometheus. The pattern is Greek-mythology themed, sequential, and each operation has a one-line thesis (Ouroboros = self-feeding cleanup; Leviathan = monolithic compression; Omniscience = 5-repo monsoon; Chimera = hybrid routing layer; Daedalus = the maze-exit; Prometheus = fire stolen for autonomy). Documented here so future sessions don't reinvent the pattern.
8. **Two `feat(*)` commits, two distinct operations** — `feat(chimera)` and `feat(daedalus)` were committed separately so the Esalen audit gate could pass for each (different since-commits, different file scopes, different rationale).

---

## Active constraints (session-specific, expire at session end)

- **Heartbeat is now ACTIVE** — this is no longer a session-specific constraint; it persists. `~/Library/LaunchAgents/com.mavis.daemon.plist` will run `mavis_daemon.py --once --apply` every 4h. To halt: `launchctl unload ~/Library/LaunchAgents/com.mavis.daemon.plist`.
- **Daily-brief is YELLOW-tier** — held by 2-week habit gate. The Daemon writes `00 Inbox/daemon-blocked-daily-brief-*.md` alerts instead of auto-executing.
- **process-inbox execution is a STUB** — the Daemon lists inbox files and reports what it would do, but doesn't move them. Reversible via the next M3 session.
- Standing vault-level constraints (per SOUL § Autonomy Boundary Table) remain in force.

---

## Next session primer (read in this order on cold start)

1. **This file** — `state-of-mavis.md` (you are here)
2. `[[MAVIS]]` — weekly context, what's fresh this week
3. `[[SOUL]]` — permanent identity + green/yellow/red table
4. `[[agent]]` — procedures + M3 cheat sheet
5. `[[ESALEN-NOT-FOXCONN]]` — operating posture (3 audit questions, build order)
6. `[[GUI Automation Gated on Operator Toggles]]` — operator-gated capabilities; load-bearing for live screencapture and cu
7. `[[INDEX]]` — vault navigation
8. `99 _system/logs/daemon-runs.jsonl` — the Daemon's heartbeat. Read the last 5 entries to see what it's been doing.
9. `99 _system/instincts/2026-06-02-009-pytest-namespace-skill-pack-action-modules-per.md` — new Instinct from this session
10. `01 Daily/2026-06-03.md` — if it exists, read it; if not, create it
11. **Then**: check `00 Inbox/` count (currently 0), `06 Connections/` freshness, `03 Projects/` open loops

> Do NOT re-read 02 Notes/ from scratch. They're indexed in MOCs. Pull a MOC when you need a topic, not before. Use vault-brain for retrieval.

---

## Patterns observed (this session, worth keeping)

- **Ground-truth audit catches inflated specs** — the "184 tests" claim in the Operation Daedalus directive was 74. The first action of any spec-block execution should be a quick ground-truth pass: run the claim, count the items, check the file paths. If the spec survives, execute; if not, correct the spec first.
- **The Resolver + Daemon split is the right discipline** — Resolver = routing (no execution), Daemon = dispatch (no LLM call), Skill Pack action.py = I/O. Three layers, each with one job. The Esalen split made operational.
- **Vision-anchored UI automation is feasible at 1px variance** — M3's native vision found the "Submit" button with x/y/w/h matching drawn coords to within 1px. The pattern (screenshot → M3 prompt → bounding box → click) is the right replacement for brittle coordinate caching.
- **process-inbox as a stub is honest, not lazy** — refusing to call M3 from the Daemon is the Esalen-correct call. The stub is a v0.1.0 limitation, not a v0.2.0+ bug. Document the limitation clearly; the v0.2.0 design conversation is now well-framed.
- **Operations with one-line theses compound** — the Greek-mythology naming (Ouroboros, Leviathan, Omniscience, Chimera, Daedalus, Prometheus) gives each build a thesis the next session can recall without re-reading the spec. The thesis IS the spec. Compress aggressively.
- **The 60s abort window is the wrong shape for cron** — headless cron can't honor a "cancel within 60s" prompt. The right shape is a human-in-the-loop handoff: YELLOW skills write an Inbox alert, the next M3 session sees it and decides. The Daemon never auto-executes a YELLOW skill.
- **Plists are state, not code** — `~/Library/LaunchAgents/com.mavis.daemon.plist` is a macOS state mutation, not a code artifact. It does NOT belong in the vault repo. The vault stays pure; the schedule lives in macOS. This separation matters when the vault is cloned to another machine — the schedule is per-machine.
- **The audit gate IS the canary** — the Friction 11 (non-determinism at temp 0.2) → Friction 11 fix (temp 0.0 hardcoded) is the same discipline: when the eval is the gate, the eval must be bit-deterministic. Same pattern: the canary rule is the bit-deterministic version of the soft-tier rule.

---

## Friction Log (where I got stuck, what would unblock me)

### Resolved (2026-06-02)

- ~~Friction 1: Where do MCP build artifacts live?~~ → **`99 _system/mcps/<name>/`** (locked)
- ~~Friction 2: Language/runtime for MCPs?~~ → **Python + pytest** (locked)
- ~~Friction 3: LLM fallback model?~~ → **M3 itself at lower temperature** (locked; no Haiku)
- ~~Friction 4: Audit log path?~~ → **`99 _system/logs/audit_log.jsonl`** (LOCKED PATH, NOT YET MATERIALIZED. Per Friction 12 discipline: harvesters must surface the missing path. `generate_instincts.py harvest_audit_log()` does this via the `note` field. Instinct 2026-06-02-006 codifies the operational rule.)
- ~~Friction 5: Test runner?~~ → **pytest** (locked; implied by F2)
- ~~Friction 6: Override path?~~ → **binary for v1** (locked; conditional deferred to v2)
- ~~Friction 7: state-of-mavis script's "since commit" windowing~~ → **`--since <commit>` flag added** (locked; default unchanged)
- ~~Friction 8: state-of-mavis script's can_i() rule duplication~~ → **accept tech debt in v1, unify into `rules.json` in v2** (locked)
- ~~Friction 12: Spec blocks can claim file paths that don't exist; harvester must surface the gap~~ → Instinct 2026-06-02-006; harvesters' `note` field carries the gap forward (resolved 2026-06-02)

### Still open (2026-06-02)

**Friction 9: vault-brain's keyword scorer is brittle on common words** (held for v0.2.0)

**Friction 10: state-of-mavis regen via Write tool vs --apply path** — This regen used the Write tool (it's a major release with a complex diff). The --apply path was tested in this session via the heartbeat kickstart; future routine regens can use --apply. Document the choice per-regen.

**Friction 11: SOUL compliance eval was non-determinism at temperature 0.2** (resolved by temp=0.0 hardcode in evaluator.py v0.3.1)

### New (2026-06-02, end of session 5)

**Friction 13: Spec blocks can inflate numbers; ground-truth audit is the discipline**
- The Operation Daedalus directive claimed "184 passing tests" but the actual test count was 74. The first action of spec-block execution (per the "Spec blocks = design review" pattern) should be a quick ground-truth pass: run the test, count the items, check the file paths.
- **Unblock**: at the start of any spec-block execution, do a 30-second audit of the most-claim-heavy items (test counts, file paths, line counts, version numbers). Report the ground truth in the design-review response. If the spec survives, execute; if not, correct it.
- **Cost of not deciding**: an inflated spec gets executed as-written, and the inflated claim gets baked into the commit message, the README, the post-mortem. Future sessions trust the inflated number; future bugs are framed against the wrong baseline.

**Friction 14: Kebab-case MCP filenames break pytest's regular import**
- `macos-vision-anchor.py` is a valid CLI filename (kebab-case matches the directory name) but Python's import system uses `import x` which translates the module name to an identifier — hyphens are not valid identifier characters. The result is `ModuleNotFoundError: No module named 'macos_vision_anchor'` even when the file is right there.
- **Unblock**: kebab-case MCP filenames are FINE for CLI usage (`python3 macos-vision-anchor.py --serve`). For pytest, use `importlib.util.spec_from_file_location("mva", path / "macos-vision-anchor.py")` to load by file path. The Instinct on the matter is implicit in `test_vision_anchor.py` lines 17-25. Codify as Instinct 2026-06-02-010 when the next kebab-case MCP ships.
- **Cost of not deciding**: the next person to write a kebab-case MCP test will hit the same `ModuleNotFoundError` and waste 5 minutes rediscovering the importlib shim.

---

*First written 2026-06-02 09:40 CT. End-of-session regeneration #3 at 15:45 CT, Mavis session `mvs_07595ff541f1404da332890f60634809`. Operations closed this session: Chimera (Resolver), Daedalus (Daemon + vision-anchor), Prometheus (heartbeat activation). Audit-gate approved (2 GREEN actions: feat(chimera) at f6fe9ba, feat(daedalus) at e62df85). 86 tests passing. Omni-Operator active.*
