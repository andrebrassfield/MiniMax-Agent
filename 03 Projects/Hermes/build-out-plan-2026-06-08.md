---
title: Hermes Agent macOS App — Build-Out Plan (2026-06-08)
date: 2026-06-08
type: build-plan
author: Mavis (EA)
source: YouTube https://youtube.com/watch?v=EJm8Ka-gVOc (Greg Isenberg × Alex Finn — Hermes Masterclass)
related:
  - 03 Projects/Hermes/architecture-review-2026-06-06.md
  - 03 Projects/Hermes/handoff-report-2026-06-06.md
  - 03 Projects/Hermes/phase-2-work-2026-06-06.md
status: plan-delivered, ready for team execution
---

# Hermes Agent macOS App — Build-Out Plan

## What the user asked

> "The hermes dashboard is open now use your computer use tool to open it and go analyze the Hermes Agent MacOS APP. Use the video to build it out properly."

Three parts:
1. **Analyze** the Hermes Agent MacOS app (Computer Use exploration, done)
2. **Map** the video's 10 masterclass hacks against the current state
3. **Build out properly** — execute the missing hacks

## The current app (live, observed)

**Hermes Desktop** by Nous Research, v0.15.1, Electron, installed at `/Applications/Hermes.app`.
Bundle ID: `com.nousresearch.hermes`. User-data root: `~/Library/Application Support/Hermes/`.

**Sidebar (observed):**
- **Core:** Model, Chat, Appearance, Worktrees, Safety, Memory & Context, Voice, Advanced
- **Providers:** Gateway, Tools & Keys, MCP, Architecture *(rare label = experimental)*, Account

**Worktrees observed in app:** multiple `main` worktrees + `Sync Hermes Config`. Indicates Hermes already supports parallel worktree isolation natively.

**Memory & Context section (observed):**
- Persistent Memory (on) — Fibonacci provider
- User Profile (on)
- Memory Budget 20000 / Profile Budget 4000
- Context Engine: **LCM** (Lossless Context Management, our `hermes-lcm` plugin)
- Auto-Compression (on), threshold 0.85, target 0.2, protected 50 messages

**What the app does NOT have** (vs the video):
- Mission Control dashboard (kanban + cron + skills at-a-glance)
- Event Triggers / Webhooks UI
- Cron Job scheduler with English-to-cron UI
- /goal structured-prompt runner
- Sub-agent swarm launcher
- Telegram Topics multi-platform gateway
- Bundles (named skill groups)
- Profiles-as-personas with separate soul.md + memory + tools
- Reverse Prompting "Brain Dump → cron" UI
- Artifacts (auto-categorized second-brain)

## The video's 10 masterclass hacks (mapped to our 6/6/2026 scorecard)

| # | Hack | Native Hermes mechanism | Current state | Build action |
|---|------|--------------------------|---------------|--------------|
| 1 | Mission Control | `hermes dashboard` (9119) + `openclaw-dashboard` plugin | Plugin not enabled | Enable plugin, surface kanban+cron+skills+bundles in one webview |
| 2 | Event Triggers | `hermes webhook` (port 8644) | Not enabled | Run `hermes gateway setup` → webhook → 3+ subscriptions (kanban-add, cron-finish, skill-installed) |
| 3 | Cron Jobs | `hermes cron` (English-to-cron) | 4 active, all DreBrain | Add 5: morning brief, X scan, content audit, weekly synthesis, competitor watch |
| 4 | /goal Structure | prompt discipline | No `goal-runner` skill | Author `goal-runner` skill wrapping the 5-step template |
| 5 | Sub-Agents | `hermes kanban swarm` v1 | CLI exists, informal | Make swarm the default for multi-stream research; document playbook |
| 6 | Telegram Topics | gateway multi-platform | Only `default` has running gateway | Enable per-profile gateways + Topics; route profiles to their own topics |
| 7 | Kanban | `hermes kanban` | Strong on `default` | Surface `mavis-kanban-monitor` and `v4` boards in Mission Control |
| 8 | Skills as SOPs | `hermes bundles` | Only 2 bundles for 112+ skills | Group into 15-20 named bundles (research, content, code, ops, finance, etc.) |
| 9 | Webhooks | `hermes webhook` | Not enabled | Same as #2 (gateway setup) |
| 10 | Separate Agents by Job | `hermes profile` | 14 profiles, only `default` has model+gateway | Activate the orchestrator layer: per-profile model, gateway, soul, memory, toolset |

## Native Hermes 0.16.0 features not activated (additional)

| Feature | State | Worldclass target |
|---------|-------|-------------------|
| `hermes acp` (Agent Client Protocol server) | not used | expose Hermes as a service |
| `hermes computer-use` (cua-driver) | installed, disabled | enable after accessibility grant |
| `hermes insights` (usage analytics) | not running | monthly review to prune |
| `hermes security` (OSV.dev supply chain) | not scheduled | weekly Sunday 4am |
| `hermes backup` / `hermes import` | not scheduled | weekly Sunday 5am |

## Scope — what to build (the "properly" part)

The user said "build it out properly." The honest scope is:
- **In scope (definitive):** all 10 masterclass hacks + 5 native features above. These are config / skill / bundle / cron / gateway / webhook / profile work on `~/.hermes/` — we own the deployment, not the upstream app binary.
- **In scope (touch):** Mission Control plugin wiring. The `openclaw-dashboard` plugin is "not enabled" per the 6/6 review. Enabling it + surfacing our existing kanban/cron/skills/bundles is the highest-leverage hack.
- **Out of scope:** modifying the Hermes Desktop app binary (Nous Research owns it). We can request upstream features, but the build is on the Hermes runtime/config side.
- **Out of scope:** Gibson V4 (per Andre's hard correction 6/6/2026 — Hermes-native only, plugins over custom layers).

## Recommended team plan

10 hacks = 10 parallel-ish workstreams, but they have dependencies. The right shape is **4 phases**:

### Phase 1 — Foundation (Day 1, parallel)
- **A1:** `hermes gateway setup` (covers #2, #9, #6) — webhook + telegram topics + per-profile gateway
- **A2:** Mission Control plugin enable (#1, #7) — `openclaw-dashboard` enabled, Mission Control webview populated
- **A3:** Activate orchestrator layer (#10) — per-profile model/gateway/soul/memory/toolset for all 14 profiles
- **A4:** Bundles authoring (#8) — 15-20 named bundles grouping the 112 skills

### Phase 2 — Workflow (Day 2, parallel after A1/A2)
- **B1:** Add the 5 new cron jobs (#3) — morning brief, X scan, content audit, weekly synthesis, competitor watch
- **B2:** Author `goal-runner` skill (#4) — wraps the 5-step /goal template, installable
- **B3:** Document sub-agent swarm playbook (#5) — make kanban swarm the default for multi-stream research

### Phase 3 — Hygiene (Day 3, parallel)
- **C1:** Schedule `hermes security` (weekly Sun 4am) + `hermes backup` (weekly Sun 5am)
- **C2:** Schedule `hermes insights` (monthly, first Sunday)
- **C3:** `hermes acp` server — expose Hermes as a service for downstream consumers
- **C4:** `hermes computer-use` enable (requires accessibility grant — flag to Andre)

### Phase 4 — Verify (Day 3-4, sequential)
- **V1:** Verifier runs through the 10-hack scorecard and confirms each is live
- **V2:** Update `03 Projects/Hermes/architecture-review-2026-06-06.md` to v2 with new state
- **V3:** Write a "Hermes Worldclass Setup" handoff doc to `02 Notes/`

## Risks / known gotchas

- **M3 worker stall** (per memory 2026-06-07): workers dispatched on M3 may stall. Take over after 2 failed attempts. Plan accordingly.
- **Computer Use permission already granted** (visible in OpenCode UI: "Computer Use mode is on — the agent can control mouse, keyboard, and screen"). No friction.
- **Hermes Desktop app is not the work surface** — work happens in the Hermes runtime (`~/.hermes/`, `hermes` CLI, plugins, profiles, skills, bundles, crons, gateway). The app is just the visible front end.
- **Andre's gate:** spec blocks = design review, wait for "go". This is now a finished spec. Pause for go-signal before dispatching the team.

## Open question for Andre

- **Scope of "build it out properly":** does "properly" mean the full 4-phase plan (10 hacks + 5 native features, ~3-4 days of team work), or a slimmer cut (Phase 1 only — gateway + mission control + orchestrator + bundles, ~1 day)?
- **Computer Use scope:** do you want me to also drive the Hermes Desktop app UI (Settings → Providers → toggle) as part of the work, or is the build purely on the Hermes runtime / config side and the Mac app just gets the result?

## Memory writeback (after go-signal + execution)

Update `ea-contract.md` and `vault-mechanics.md` with the build outcome, the M3 worker-stall pattern confirming again, and the new "what counts as built out properly" rule for future "use the video to build it out" requests.
