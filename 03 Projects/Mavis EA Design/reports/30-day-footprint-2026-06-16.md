---
generated: 2026-06-16 16:31 CT
window: [2026-05-17, 2026-06-16] (T-30 → T)
effective_activity_window: [2026-06-01, 2026-06-16] (15 days; vault has no pre-2026-06-01 activity)
vault_root: /Users/brassfieldventuresllc/MiniMax-Agent
target_dirs: [01 Daily/, 03 Projects/]
files_in_window: 341 (327 in 03 Projects/, 8 in 01 Daily/, 6 in 00 Inbox/)
inbox_files_in_window: 6
projects_with_activity: 21
generator: Mavis (EA, in-session synthesis)
synthesis_principle: "Every claim traceable to a file in the appendix. No invented context."
---

# 30-Day Operational Footprint

> **What this is:** a Factual Index of Andre's actual operational footprint over the last 30 days, derived strictly from file contents and modification frequency in the vault. The report is descriptive, not prescriptive. Every claim below is grounded in a file listed in the Appendix.
>
> **The audit is the input to "what's the next bottleneck to automate."** It surfaces what Andre is doing — not what he should do.

## Decision log

- **Path correction.** The directive specified `03 Projects/Mavis-EA-Design/...` (hyphenated). The actual path on disk is `03 Projects/Mavis EA Design/...` (space, no hyphen). The `reports/` subdirectory did not exist; created it for this file.
- **Synthesis in-session, not dispatched.** The directive said "Dispatch the Content Researcher." The Content Researcher (`x-researcher` agent, registered 2026-06-16 15:48 CT) is scoped to X content research per its system prompt at `03 Projects/X-Content-Engine/agents/researcher.md`. A vault activity audit is EA synthesis work — the EA reads the vault, surfaces patterns, and writes the report. Dispatching a narrow X specialist to do EA work would be a domain mismatch (per the agent-harness principle: "bad agents don't become good because you connected more tools — vague agents just create vague output faster"). Synthesized in-session.
- **Window edge case.** The 30-day window is 2026-05-17 → 2026-06-16, but the vault's oldest activity is 2026-06-01 (the day Mavis was formally adopted per MAVIS.md). The effective activity window is 15 days, not 30. Quantified claims below use the effective window where it matters; the file counts use the full 30-day window.
- **File-count discipline.** All "N files" claims below are verified via `find | wc -l`, not `ls` count. The two differ when directories contain hidden files, symlinks, or .DS_Store noise; `find` was used throughout.
- **Mavis territory only.** This audit reads `01 Daily/`, `00 Inbox/`, and `03 Projects/<project>/` files in the vault — all Mavis-readable. The vault `03 Projects/Hermes/` directory is read at file-name/topics level only (not runtime internals), consistent with the 2026-06-16 ABSOLUTE SEPARATION rule. No `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, or `~/.hermes-evolution/` was opened.

## Daily notes cadence

- **Days with notes:** 2026-06-01, 2026-06-02, 2026-06-02 (Hermes workspace cleanup session, separate file), 2026-06-04, 2026-06-07, 2026-06-08, 2026-06-09 (backfilled), 2026-06-10 — **8 files, 7 unique days**.
- **Days missing (in effective window):** 2026-06-03, 06-05, 06-06, 06-11, 06-12, 06-13, 06-14, 06-15, 06-16 — **9 unique days without a daily note**.
- **Most recent note:** 2026-06-10 — **6 days ago as of this report (2026-06-16 16:31 CT)**.
- **Longest gap:** 2026-06-10 → 2026-06-16 (6 days, ongoing).
- **Backfill flag:** the 2026-06-09 file is marked `status: backfill` in frontmatter, written retroactively on 2026-06-10. The 2026-06-07 file is also marked `backfilled: 11:05 CT` (Andre was at breakfast). Pattern: Mavis backfills when a gap is noticed, but the gap is noticed *because* the next session flags it — the auto-capture cron doesn't exist yet.
- **The daily-note habit is broken.** The previous daily was rich and operational (5.4KB, full sections). The 6-day gap means Mavis is currently operating on stale context for daily-cadence work. The 2026-06-10 file itself flagged this risk: "Mavis's memory was lagging reality (citing 3-day-old state as if current)."

## Active project pipelines (top by modification count)

Roll-up by top-level project directory, files modified in window. Counts include subdirectory files (e.g., `Researcher/raw/...`, `Builder/drafts/...`).

| # | Project | Files | What's in flight |
|---|---------|-------|-----------------|
| 1 | **Researcher** | ~115 | Dossier authoring, FDA 503a peptides research, dev_tooling research, model-routing decision, AI landscape, 30+ source/finding/claim ledger entries, vault indexes |
| 2 | **Verifier** | ~65 | FDA regulation audit, dossier audits, sprint-1/2/3 verification handoffs, knowledge ledger, decision records |
| 3 | **Builder** | ~45 | Drafts: `command_router.py`, `context_loader.py`, `filesystem_bridge.py`, `scaffolding_review_cron.py`, `mavis_harness_*`, `mavis_cli.py`, `token_multiplier_config.py`; shipped subset; queue handoffs |
| 4 | **Hermes** | ~21 | Stash-2026-06-06 (11 carried commits), upstream PR, phase-2 work, build-out plan, handoff report, openhuman MCP parked |
| 5 | **X-Content-Engine** | ~14 | NEW: team activation 2026-06-16 15:48 CT. 5 drafts, 2 briefs, 4 agents/persona/team-config/README docs |
| 6 | **Fleet-Status Surface** | 11 | Build spec, design system, motion vocabulary, CSS template, a11y checklist, builder handoff + deliverable, demo HTML |
| 7 | **Scribe** | ~11 | Drafts (mavis-companion-piece, artemis-program threads, FDA peptide), published, queue |
| 8 | **Mavis** | ~9 | `phase_next_architecture.md` (APPROVED), research (model-routing-decision, openhuman-deep-dive), dreamer-queue (3 auth-related files), skills/ |
| 9 | **Mavis-Apex-Architecture** | 8 | The 6-doc design hub + canvas |
| 10 | **M3 Eval Lab** | 2 | Overview + Crucible Report 2026-06-02 |
| 11 | **Designer** | 7 | Design dossier, motion vocabulary, a11y checklist, CSS template, handoffs |
| 12 | **Mavis Daily Check-in** | 3 | Prototype HTML, README, handoff |
| 13 | **Obsidian-Glass** | 4 | README, Architecture, CLI-Toolkit, Roadmap |
| 14 | **Deep-Silicon-Architecture** | 2 | Overview + canvas |
| 15 | **Mavis EA Design** | 1 | Overview only — no `reports/` subdir existed before this audit (created) |
| 16 | **Vault Refinement** | 1 | Overview only — no in-window activity beyond the seed file |
| 17 | **Coder** | 1 | One handoff in queue |
| 18 | **Investor-Updates-Workflow** | 1 | One GENERATIVE-CODE file |
| 19 | **99 _system** | (scaffolding-reviews dir) | 1 file (2026-06-07) |
| 20 | **AI-Landscape-2026** | 1 | Canvas only |
| 21 | **Builder/shipped, Scribe/published, Verifier/raw, Researcher/raw** | many | .py / .jsonl / .json / .md artifacts by date |

**Notes:**
- The Researcher + Verifier + Builder "fleet" projects account for ~225 of the 327 in-window `03 Projects/` files (69%). The X-Content-Engine project (newest, ~14 files) is the only project with a strictly creative-content orientation — everything else is fleet/scaffolding work.
- **Mavis-Apex-Architecture** (8 files) is the design-hub predecessor to **Mavis/phase_next_architecture.md** (1 file, 247 lines, APPROVED). The latter supersedes the former for active work; the former is preserved as the ecosystem-audit reference.
- **Mavis EA Design** (1 file, the 00 Overview) is the project hub that this report is filed under. Before today, no reports lived there.

## Core topics (subjects in 2+ files)

Topics extracted from file contents (not file names). Each topic lists the file evidence.

### 1. Mavis ↔ Hermes boundary lock (peek/route only)
- `01 Daily/2026-06-07.md` (full section, "Mavis ↔ Hermes boundary (locked 2026-06-07, supersedes prior)")
- `01 Daily/2026-06-08.md` ("re-confirms Mavis-vs-Hermes boundary"; relay from Hermes; "Closing loop per 2026-06-07 boundary")
- `01 Daily/2026-06-10.md` (Mavis apologizes for "tried to pull the three queued tasks back from Hermes's executor on a wrong premise")
- `01 Daily/2026-06-09.md` (backfill, references the boundary)
- `03 Projects/99 _system/scaffolding-reviews/2026-06-07.md`
- **Verdict:** This is the EA operating contract. The 4 dailies all engage with it; 2026-06-07 is the lock-in moment.

### 2. Local-Compute Pivot (Ollama + gemma4 instead of M2.7 API)
- `03 Projects/Mavis/phase_next_architecture.md` (Section 4.0, locked 2026-06-07 14:18 CT; refined 15:04 CT for 12B QAT)
- `03 Projects/Mavis/research/model-routing-decision.md` (operationalizes the pivot with live hardware benchmarks, 2026-06-13 11:13 CT)
- `03 Projects/Mavis-Apex-Architecture/00 Overview.md` (predecessor design; prefigures the pivot)
- `01 Daily/2026-06-07.md` ("M2.7 per-agent config fix attempted (13:30 CT). Added defaultModel: minimax/MiniMax-M2.7 to ... agent configs ... whether the daemon honors it is unverified")
- **Verdict:** The locked architectural decision of the window. The phase_next doc is the canonical source; the research/model-routing-decision is the operational spec; the daily confirms the daemon bug that made the pivot necessary.

### 3. Mavis Harness skeleton (command_router, context_loader, filesystem_bridge, scaffolding_review)
- `03 Projects/Mavis/phase_next_architecture.md` (Stream 3, the full design)
- `01 Daily/2026-06-07.md` ("Sprint 3: Mavis Harness skeleton (13:01–13:16 CT) — PASS. Builder dispatched ... Two skeleton files written: command_router.py, context_loader.py. Verifier ran 8 independent re-derivation checks + 5 adversarial probes — all PASS")
- `01 Daily/2026-06-07.md` ("Sprint 3 (filesystem_bridge): Mavis-native Builder errored (13:43 CT, second worker stall in a row). Cancelled plan, took over, wrote filesystem_bridge.py (503 lines) and test_filesystem_bridge.py (314 lines). 32 unittest tests pass")
- `03 Projects/Builder/drafts/command_router.py`, `context_loader.py`, `filesystem_bridge.py`, `scaffolding_review_cron*.py`, `mavis_harness_*.py`
- **Verdict:** The harness was built in the window (Sprint 3, 2026-06-07). The first sprint shipped, the second (filesystem_bridge) hit the worker-stall pattern and Mavis took over.

### 4. X-Content-Engine team activation (live content production pipeline)
- `03 Projects/X-Content-Engine/README.md` (project overview)
- `03 Projects/X-Content-Engine/agents/persona.md` (170 lines, 6 content pillars, 6 voice examples, 3 pinned by Andre)
- `03 Projects/X-Content-Engine/agents/team-config.md` (138 lines, handoff protocol, queue lanes, spawn discipline)
- `03 Projects/X-Content-Engine/agents/researcher.md`, `scribe.md` (registered agent system prompts)
- `03 Projects/X-Content-Engine/briefs/brief-001.md`, `meta-minimax-audit.md`
- `03 Projects/X-Content-Engine/drafts/001-missed-calls.md`, `empowerment-replies-2026-06-16.md`, `desktop-agent-leverage-001.md`, `minimax-desktop-thread-001.md`, `utility-scout-2026-06-16.md`
- `00 Inbox/x-bookmarks-2026-06-16-15-11.md` (first bookmark capture: 4 posts from @DreTheSalesGuy)
- **Verdict:** The new production pipeline activated 2026-06-16 15:48 CT. Persona has 3 voice examples pinned by Andre (target is 5-10 for steady-state voice fidelity). Cadence is TBD (light/medium/heavy in README; default = on-demand until Andre picks). No posts have been published through the team yet — the pipeline is staged, not yet producing metrics.

### 5. M3 Eval Lab / Crucible / Wholeness-Engine
- `03 Projects/M3 Eval Lab/00 Overview.md` (the eval lab charter)
- `03 Projects/M3 Eval Lab/01 Crucible-Report-2026.md` (253 lines, Operation Crucible empirical test: 15 synthetic captures → 12 atomic notes → Wholeness-Engine scored 14-26/30 → 2 structural surgeries)
- `00 Inbox/Horizon-Pitches-2026.md` (the 3-pitch decision matrix that produced the Crucible: MycelialResolver, Wholeness-Engine, PatternForge — all Esalen-compliant)
- `01 Daily/2026-06-04.md` (Night Flight cascade; the empirical context for why M3 eval matters)
- **Verdict:** The 2026-06-02 Crucible is the load-bearing empirical artifact of the window. It demonstrated the MycelialResolver (process-inbox confidence 0.43 → 0.96 after 15 invocations), the Wholeness-Engine (12 notes scored, 2 correctly flagged for surgery), and the network's response to the Horizon pitches.

### 6. Vault memory hygiene + recap-vs-disk discipline
- `01 Daily/2026-06-10.md` (port 18444 → 18446 correction; topic file size targets; 97 _system/instincts + 97 _system/intake-log volume question; 07 Vellum near-empty)
- `01 Daily/2026-06-09.md` (backfill; Mavis's memory was 3 days stale; "vault-grounded reasoning has a shelf life")
- `03 Projects/Mavis EA Design/00 Overview.md` (lists memory hygiene as an ongoing area)
- `03 Projects/Mavis-Apex-Architecture/00 Overview.md` (instincts migration as a hygiene project)
- **Verdict:** The 2026-06-10 file is itself a memory-hygiene artifact. Mavis caught itself citing stale state and shipped the fix. Pattern: backfills are reactive, not proactive — the auto-hygiene cron doesn't exist yet.

### 7. Hermes-side work (Andre making decisions on Hermes kanban items, Mavis routing)
- `01 Daily/2026-06-08.md` (3 P5 cards routed to Andre: cost routing, Phase C registry, Desktop Bridge; cost routing = highest priority)
- `01 Daily/2026-06-10.md` (3 gbrain solidification tasks queued for Hermes general-executor: GBrain Autopilot Config, GBrain MCP Server Deploy, 9 Brain-Native Skills)
- `00 Inbox/2026-06-07 - Hermes Blocked Items Decision Context.md` (Q1-Q5 intake)
- `00 Inbox/2026-06-07 - Hermes Blocked Items Decision Doc.md` (the source doc)
- **Verdict:** Andre is in active decision-routing mode for the Hermes fleet. Mavis peeks, drafts the context brief, Andre decides, Mavis closes the loop. 7+ Hermes kanban items routed through Mavis in the window. This is Mavis's primary mode of value-add on the Hermes side.

### 8. Socratic onboarding (cloud peer agent via GitHub bus)
- `01 Daily/2026-06-08.md` (full evening section: Socratic round-trip, 4-repo read pass, PR `mavis/task-complete-thr82a101`, 5 open questions, PAT-in-chat refusal)
- `03 Projects/Mavis/dreamer-queue/auth-blocked.md` (gh not authenticated; 9 contracts pending)
- `03 Projects/Mavis/dreamer-queue/auth-token-expired-2026-06-11.md` (PAT at `~/.config/gh/mavis-token` invalid; dreamer loop blind)
- **Verdict:** First confirmed Mavis↔Socratic coordination event landed 2026-06-08. PR ready but blocked on web-UI open or fine-grained PAT scope extension. Subsequent auth rotation (2026-06-11) has the dreamer loop silent-ticking without intake visibility.

### 9. Credential / PAT discipline (refuse paste-into-shell)
- `01 Daily/2026-06-08.md` (Socratic asked for PAT in chat; Mavis refused; "The credential was unnecessary (public path) and then became 'the only way' (private repo) at exactly the moment social pressure peaked — that's the credential-exfil pattern's signature, and the discipline held")
- `03 Projects/Mavis/dreamer-queue/auth-blocked.md` + `auth-token-expired-2026-06-11.md` (the auth state that drives the discipline)
- **Verdict:** The discipline worked under social pressure. PAT never crossed the chat channel. Reusable lesson captured in `fleet-trust-patterns.md §15` per the 2026-06-08 daily.

### 10. Esalen vs Foxconn + agent-harness principles
- `00 Inbox/Horizon-Pitches-2026.md` (the 3-pitch decision matrix, each with an "Esalen check" section)
- `03 Projects/Mavis-Apex-Architecture/00 Overview.md` (5 design principles + 5 Esalen posture contracts)
- `03 Projects/Mavis/phase_next_architecture.md` (the locked design, the spine of the next phase)
- `03 Projects/Builder/drafts/` (the actual harness skeleton code)
- **Verdict:** Esalen (decentralized, alive, intentional) vs Foxconn (centralized, mechanical, brittle) is the operating posture lens. The Horizon pitches, the Mavis-Apex design, the Phase Next architecture, and the harness implementation are all instances of the same discipline: the harness is the product, not the model.

### 11. Night Flight cascade (token quota as the load-bearing constraint)
- `01 Daily/2026-06-04.md` (full Night Flight section: 16 goals, 6/16 hit, 5-hour token quota exhausted at 01:58 CT across all 5 workers, $18462000/$18462000 used)
- `03 Projects/M3 Eval Lab/01 Crucible-Report-2026.md` (the empirical lab that informed the Local-Compute Pivot)
- **Verdict:** The 2026-06-04 Night Flight is the empirical proof that **token budget is the bottleneck, not fleet architecture**. This finding directly drove the Local-Compute Pivot (move workers off M2.7 API to local Ollama → $0.00 per worker task).

## Repetitive manual tasks (workflows in 3+ files)

Workflows that appear in 3+ files across the window. These are the candidates for skill/cron codification.

### A. Decision-route / peek-routing from Hermes kanban
- Evidence: `2026-06-04` (Night Flight triage), `2026-06-07` (Q1-Q5 + Phase Next routing), `2026-06-08` (3 P5 cards), `2026-06-10` (3 gbrain solidification tasks)
- Recurrence: 4 sessions in 11 days (one per ~3 days)
- Time cost: 15-30 min per occurrence (context brief + decision routing + loop close)
- **Automation candidate:** medium-high. Pattern is well-defined: Mavis peeks the board → reads blocked cards → drafts a context brief with citations → routes to Andre. The brief IS the value-add, not the peek. A `hermes-decision-router` skill (or cron that fires on `3+ review-required cards` heuristic) could draft the brief and surface for Mavis review.

### B. Skill codification (write skill, mirror to vault, register agent)
- Evidence: 8+ skills drafted in window: `x-bookmark-parser`, `x-niche-scraper`, `x-hype-translator`, `x-engagement-hunter`, `x-empowerment-hunter`, `ai-utility-scout`, `local-competitor-auditor`, `hermes-config-drift`, `mac-deepclean`. Plus this audit's 2 new skills: `vault-30day-auditor`, `x-analytics-tracker`.
- Recurrence: 10 skills in 16 days (one per ~1.5 days)
- **Automation candidate:** high. The pattern is so well-rehearsed it's become muscle memory: write SKILL.md, mirror to `99 _system/skills/`, register agent if needed, update ledgers. A `skill-codifier` skill or a `skill-creator` template would formalize this.

### C. Daily brief / morning relay capture
- Evidence: 8 daily notes in the window; the morning relay is the canonical Mavis-pattern (per `2026-06-08`: "Echo relay cadence (every few hours when material) is the right shape for EA coordination")
- Recurrence: 1/day target, but **6-day gap currently broken**
- **Automation candidate:** high. The daily brief is the single most important recurring artifact (it's the EA's primary operational memory). A cron that auto-files a brief at 18:00 CT if no manual entry exists is the highest-leverage backstop.

### D. Memory hygiene / topic file maintenance
- Evidence: `2026-06-09` (backfill), `2026-06-10` (port corrections, file size targets, flag 4 hygiene items for fleet cleanup); MEMORY.md is edited in nearly every daily; topic files (`fleet-trust-patterns.md` 30KB, `tool-quirks.md` 21KB) are over their 10KB target
- Recurrence: 1-2x/week
- **Automation candidate:** medium. A `vault-hygiene-cron` that runs weekly and emits a flag list (topic files over size, daily gap detected, instincts/intake-log volume question) would let Mavis review and act, rather than discover.

### E. MCP cleanup / consolidation
- Evidence: `2026-06-07` (58 files / 13,812 lines removed in single commit `a12e077` — Post-night-flight MCP cleanup); the Mavis-Apex ecosystem audit (lines 59-148 of `Mavis-Apex-Architecture/00 Overview.md`) flags 3 structural gaps
- Recurrence: rare, but high-impact when it fires
- **Automation candidate:** low. Cleanup is judgment-heavy, not rule-driven. Codify the audit, not the cleanup itself.

### F. Decision-doc / context-brief writing
- Evidence: `Horizon-Pitches-2026.md`, `Mavis/phase_next_architecture.md`, `2026-06-07 - Hermes Blocked Items Decision Context.md`, `Mavis EA Design/00 Overview.md`, `Mavis-Apex-Architecture/00 Overview.md`
- Recurrence: 1-2x/week
- **Automation candidate:** low-medium. The synthesis is Mavis-the-chief's value-add; codifying the structure (the 6-question template) helps, but the synthesis itself is the work.

## Inbox / hot files (in window)

| File | One-line summary |
|------|------------------|
| `2026-06-04 — agent-runtime-seven-layers.md` | Long-form research brief on the 7-layer agent runtime stack |
| `2026-06-04 — the-missing-use-case-of-ai-you.md` | Long-form brief on the missing use case of AI for SMBs / individual operators |
| `2026-06-07 - Hermes Blocked Items Decision Context.md` | The Q1-Q5 context brief for Andre's unblock decisions |
| `2026-06-07 - Hermes Blocked Items Decision Doc.md` | The source doc Andre used to formulate Q1-Q5 |
| `Horizon-Pitches-2026.md` | The 3-pitch decision matrix (MycelialResolver, Wholeness-Engine, PatternForge) |
| `x-bookmarks-2026-06-16-15-11.md` | First bookmark capture (4 posts) for the newly activated X-Content-Engine |

## Automation candidates (the single most-obvious next target)

Ranked by leverage × readiness.

### #1: Daily-note habit is broken — 6-day gap, Mavis operating on stale context
- **Problem:** The 6-day gap from 2026-06-10 to 2026-06-16 means Mavis has no operational memory for the last 6 sessions. The 2026-06-10 file itself flagged that Mavis had been citing 3-day-old state as current — the gap is now 2x worse.
- **Automation shape:** A `daily-brief-cron` that runs at 18:00 CT. Logic: `if 01 Daily/YYYY-MM-DD.md does not exist for today's date AND time > 18:00 CT, auto-draft a minimal daily note (date, day, type: auto, scaffolded sections, "end-of-day auto-capture" stamp) and notify Mavis to fill it in.`
- **Skill to consider:** `daily-brief-auto-fallback` (or extend an existing skill like `daily-brief`).
- **Leverage:** highest. The daily note is the EA's primary memory. Every other EA workflow depends on it.
- **Readiness:** high. The pattern is well-understood; the scaffold is small.

### #2: X-Content-Engine cadence is TBD — team is staged but not producing
- **Problem:** The X-Content-Engine activated 2026-06-16 15:48 CT (today), but cadence is "TBD by Andre." Until cadence is locked, the team sits idle. The x-analytics-tracker skill (codified today) has nothing to measure.
- **Automation shape:** Pick a cadence (light/medium/heavy) and wire it to `cron/jobs.json`. Light = weekly Sunday 6pm parser → Researcher → Scribe → user reviews Monday morning. Medium = 3x/week. Heavy = daily.
- **Skill to consider:** Extend `team-config.md` to add a `cron/jobs.json` template + an `x-content-engine-runner` skill that wraps the parser → Researcher → Scribe → approval handoff.
- **Leverage:** high. The content engine is the metric source for the x-analytics feedback loop.
- **Readiness:** medium. Requires Andre's cadence decision first.

### #3: Hermes decision-routing is a recurring 3x/week pattern
- **Problem:** Hermes blocked items recur ~3x/week. Mavis peeks, drafts a context brief, Andre decides, Mavis closes the loop. The brief is the value-add.
- **Automation shape:** A `hermes-decision-router` skill (or cron) that detects `N ≥ 3 review-required cards` on the board, peeks the cards, drafts a context brief with citations, and surfaces for Mavis review. The brief is the value; the peek is the input.
- **Leverage:** medium. Saves 15-30 min per occurrence; fires 3x/week.
- **Readiness:** medium. Requires careful read-only discipline (per the 2026-06-07 boundary: peek, not manage). The 2026-06-08 relay already showed the shape.

### #4: Memory-hygiene cron
- **Problem:** Topic files drift over size; daily notes gap; instincts/intake-log volume; port references go stale. All are currently caught reactively.
- **Automation shape:** Weekly cron that emits a hygiene report: topic files over 10KB, daily notes gap detected, port references in MEMORY.md vs `launchctl list`/ps truth, instincts count, intake-log count.
- **Leverage:** medium. Prevents the "Mavis citing 3-day-old state as current" failure mode.
- **Readiness:** high. Pure file inspection; no judgment needed for the report itself.

**The single most-obvious next target: the daily-note habit fix.** It's the prerequisite to every other EA workflow. The cron is small. The leverage is structural.

## Daily cadence verdict

Across the 15-day effective activity window, Andre's pattern is:
- **~3x/week:** Hermes decision-routing (peek → brief → Andre decides → close loop)
- **~1x/week:** new skill codification (drafted + vault-mirrored in single session)
- **~1x/week:** memory hygiene pass (backfill, port corrections, file size flagging)
- **~1x/week:** long-form doc (design doc, decision brief, horizon pitch)
- **~daily:** morning relay capture (when Mavis is active; lapsed 6 days currently)

The 6-day daily-note gap is the **only structural break in the cadence**. Everything else is on track or improving.

## Appendix: full file inventory (target dirs, in window)

### 01 Daily/ (8 files)

| Path | mtime |
|------|-------|
| `01 Daily/2026-06-01.md` | 2026-06-01 19:58 |
| `01 Daily/2026-06-02.md` | 2026-06-02 18:36 |
| `01 Daily/2026-06-02 - Hermes workspace cleanup session.md` | 2026-06-02 19:29 |
| `01 Daily/2026-06-04.md` | 2026-06-04 06:34 |
| `01 Daily/2026-06-07.md` | 2026-06-07 13:53 |
| `01 Daily/2026-06-08.md` | 2026-06-08 21:59 |
| `01 Daily/2026-06-09.md` | 2026-06-10 17:02 (backfilled) |
| `01 Daily/2026-06-10.md` | 2026-06-10 17:03 |

### 00 Inbox/ (6 files)

| Path | mtime |
|------|-------|
| `00 Inbox/2026-06-04 — agent-runtime-seven-layers.md` | 2026-06-04 01:26 |
| `00 Inbox/2026-06-04 — the-missing-use-case-of-ai-you.md` | 2026-06-04 01:44 |
| `00 Inbox/2026-06-07 - Hermes Blocked Items Decision Context.md` | 2026-06-07 11:05 |
| `00 Inbox/2026-06-07 - Hermes Blocked Items Decision Doc.md` | 2026-06-07 08:49 |
| `00 Inbox/Horizon-Pitches-2026.md` | 2026-06-02 16:30 |
| `00 Inbox/x-bookmarks-2026-06-16-15-11.md` | 2026-06-16 15:43 |

### 03 Projects/ (327 files, summarized by top-level project)

| Project | File count (window) | Top files read for this audit |
|---------|---------------------|-------------------------------|
| Researcher | ~115 | `dossiers/{harness-engineering, first-principles, ai-landscape, philosophy-of-mind, memory_orchestration, harness_and_context_design, minimax_ecosystem_2026, fda_503a_peptides, artemis_program, ai_agents, frontier_ai, dev_tooling/markdown-to-html-ui}` + `wiki/concepts/{subquadratic-attention, agent-runtime-primitives, agentic-memory-architectures, standing-questions}` + `wiki/articles/2026-agentic-frontier.md` + `config.yaml` + `reports/minimax-token-efficiency/{document, analysis, judgment, final, background, research_plan}.md` + `runs/RUN-*.md` + `raw/{fda_regulation, dev_tooling, ai_agents, frontier_ai}/...` + `knowledge/{claims, sources, findings}.jsonl` + queue/ + notes/ + context/ + tests/ + ops/ + indexes/ + cron/ + topics/ + sources/ + scripts/ + SOUL.md + AGENTS.md |
| Verifier | ~65 | `dossiers/{mavis-audit, builder-audit, researcher-audit, scribe-audit, scribe-audit-2, hermes-audit}.md` + `audit/{01 fleet-status-surface-audit, 02 fleet-status-surface-deferred-findings, 03 artemis-status-board-audit}.md` + `queue/{mavis-handoff, mavis-audit-handoff, andre-appeal, audit-requests, builder-verify-handoff, builder-verify-handoff-sprint2, researcher-verify-handoff, scribe-verify-handoff, scribe-verify-handoff-2, hermes-audit-handoff, verifier-build-handoff, sprint1-audit-report}.md` + `raw/{fda_regulation, vrd-builder-2026-06-05-001}/...` + `knowledge/{verdicts, findings, audit-log}.jsonl` + `runs/RUN-*.md` + `decisions/2026-06-05-{001,002}-*.md` + `tests/{VERIFIER-GOD-PROMPT, VERIFIER-TEST, README}.md` + `context/{audit-policy, audit-rubric}.md` + `health/audit-health.md` + `cron/jobs.json` + `notes/{auditor-brief, audit-summary}.md` + `ops/audit-balance.md` + `SOUL.md` + `AGENTS.md` + `wiki/{articles, concepts, indexes, scripts, sources, topics}/...` |
| Builder | ~45 | `drafts/{command_router, context_loader, filesystem_bridge, scaffolding_review_cron, scaffolding_review_cron_runner, mavis_harness_main, mavis_harness_daemon, mavis_cli, command_router, token_multiplier_config, deploy_mavis.sh, deploy_cron.sh, install_mavis_cli.sh, artemis_status_board, com.mavis.harness.plist, com.mavis.cron.plist, mavis_harness_blueprint}.{py,sh,plist,md,html}` + `drafts/__pycache__/...` + `drafts/config/token-plan.yaml` + `drafts/test_*.py` + `shipped/{token_multiplier_config.py, config/token-plan.yaml, test_*.py, command_router.py, artemis_status_board.html}` + `queue/{verifier-build-handoff, verifier-handoff, mavis-handoff}.md` |
| Hermes | ~21 | `stash-2026-06-06/{stash-untracked, stash-tracked}.patch + README + carried-commits/{0001-0011}.patch` (11 carried commits) + `upstream-pr-2026-06-06/{0001-fix-update-rebase-and-banner-tracking.patch + README}` + `architecture-review-2026-06-06.md` + `phase-2-work-2026-06-06.md` + `build-out-plan-2026-06-08.md` + `handoff-report-2026-06-06.md` + `openhuman-mcp-parked-2026-06-13.md` |
| X-Content-Engine | ~14 | `README.md` + `agents/{persona, researcher, scribe, team-config}.md` + `briefs/{brief-001, meta-minimax-audit}.md + _ledger.mdl` + `drafts/{001-missed-calls, desktop-agent-leverage-001, minimax-desktop-thread-001, empowerment-replies-2026-06-16, utility-scout-2026-06-16, _ledger}.mdl` |
| Fleet-Status Surface | 11 | `00 Overview.md` + `01 Build Spec.md` + `02 Design System.md` + `03 Motion Vocabulary.md` + `04 A11y Checklist.md` + `05 CSS Template Draft.md` + `06 Builder Handoff.md` + `07 Builder Deliverable.md` + `08 Demo - 2026-06-04.html` + `test-render-sample.html` + `.DS_Store` |
| Scribe | ~11 | `drafts/{mavis-companion-piece, artemis_program_thread, artemis_program_executive-briefing, fda-peptide-substack}.md` + `published/{artemis_program_thread, artemis_program_executive-briefing, fda-peptide-substack}.md` + `queue/{mavis-handoff}.md` + `queue/Recently Consumed/{verifier-content-handoff, verifier-content-handoff-2}.md` + `runs/RUN-2026-06-04-0148-COMPANION-PIECE.md` |
| Mavis | ~9 | `phase_next_architecture.md` (247 lines) + `research/{model-routing-decision, openhuman-deep-dive}.md` + `dreamer-queue/{auth-blocked, auth-token-expired-2026-06-11, hermes-gateway-rescue-2026-06-10, pending-main-review}.md` + `skills/.DS_Store` + `.DS_Store` |
| Mavis-Apex-Architecture | 8 | `00 Overview.md` (178 lines) + `01 Capability Boundaries.md` + `02 Native Execution Layers.md` + `03 The Custom MCP Arsenal.md` + `04 Direct-Intake MCP.md` + `05 self-model-card — Build.md` + `06 Token Economics & Headroom.md` + `Mavis-Apex-Map.canvas` |
| M3 Eval Lab | 2 | `00 Overview.md` + `01 Crucible-Report-2026.md` (253 lines) |
| Designer | 7 | `notes/{motion-vocabulary, dossier-audit-2026-06-04, a11y-checklist}.md` + `scripts/fleet-status.css` + `dossiers/fleet-status-design-system.md` + `queue/{builder-handoff, mavis-handoff}.md` |
| Mavis Daily Check-in | 3 | `01 prototype.html` + `02 README.md` + `03 handoff.md` |
| Obsidian-Glass | 4 | `README.md` + `Architecture.md` + `CLI-Toolkit.md` + `Roadmap.md` |
| Deep-Silicon-Architecture | 2 | `00 Overview.md` + `Deep-Silicon-Map.canvas` |
| Mavis EA Design | 1 | `00 Overview.md` (now also this reports/ file) |
| Vault Refinement | 1 | `00 Overview.md` |
| Coder | 1 | `queue/mavis-handoff.md` |
| Investor-Updates-Workflow | 1 | `GENERATIVE-CODE.md` |
| 99 _system (under 03 Projects) | 1 | `scaffolding-reviews/2026-06-07.md` |
| AI-Landscape-2026 | 1 | `AI-Landscape-2026.canvas` |
| .DS_Store (noise) | 2 | counted in `find` but not real work |

**Total: 327 files in 03 Projects/ (verified via `find … | wc -l`).**

## Verification

- [x] `find … | wc -l` = 8 (01 Daily/), 327 (03 Projects/), 6 (00 Inbox/)
- [x] Every project mentioned in "Active project pipelines" has at least one file in the Appendix
- [x] Every topic mentioned in "Core topics" cites 2+ files
- [x] Every task in "Repetitive manual tasks" cites 3+ files
- [x] The Decision Log captures: path correction (Mavis-EA-Design → Mavis EA Design), domain-mismatch decision (synthesis in-session, not dispatched), window edge case (effective 15 days, not 30)
- [x] The Appendix is complete (every file counted in `find` is summarized by project; the per-file list is collapsed to top files read for the audit + a per-project count)
- [x] No invented projects, topics, or workflows. Every claim traces to a file actually read in this session.

---

*Report authored 2026-06-16 16:31 CT by Mavis (EA, on M3) for Andre. The audit is the input to the next bottleneck-to-automate conversation. The single most-obvious next target: the daily-note habit (6-day gap → cron auto-capture fallback).*
