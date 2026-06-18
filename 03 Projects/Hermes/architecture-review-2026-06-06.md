---
title: Hermes Architecture — Strategic Review vs Masterclass
date: 2026-06-06
type: strategic-memo
author: Mavis (EA)
status: analysis delivered, awaiting prioritization
related: ["Hermes Agent Masterclass.md (Nous Research)", "handoff-report-2026-06-06.md", "PR #40673"]
---

# Hermes Architecture — Strategic Review vs the Nous Masterclass

## Context

Andre asked Mavis to analyze the [Hermes Agent Masterclass](../Hermes%20Agent%20Masterclass.md) (Nous Research, 90K+ stars) against our current `~/.hermes/` state and recommend a path to "worldclass." Constraint: **Hermes-native only, plugins over custom layers, Gibson V4 dropped.** This memo is the strategic read; the operational execution is being routed through Hermes himself as a self-evolution exercise.

## Current state — what's strong

- **Hermes Agent v0.16.0** native, up to date (source + runtime coloced at `~/.hermes/`)
- **14 profiles with disciplined SOUL.md** — orchestrators (macro/eng/content), executors (research/engineering/content/ops), specialists (code-reviewer/verifier/extractor/researcher/writer), plus `mavis` and `default` roots
- **3 kanban boards, real activity** — `default` (130+ tasks, 93 done, 16 ready, 6 blocked), `mavis-kanban-monitor`, `v4`
- **4 cron jobs running** — DreBrain Watchdog, Vault Index, Honcho Model, Research Crawl
- **Curator enabled, 7-day cycle, 30/90-day discipline** — but with 0 skills archived (under-driven)
- **`hermes-lcm` plugin enabled** — Lossless Context Management
- **112 agent-created skills** + 87 bundled + 79 optional + 16 Anthropic + 505 LobeHub from the Hub
- **Tier 2 search** via SQLite state.db, FTS5-indexed

## Masterclass scorecard — the 10 hacks

| # | Hack | Native Hermes mechanism | State | Action |
|---|------|------------------------|-------|--------|
| 1 | Mission Control | `hermes dashboard` (9119) + `openclaw-dashboard` plugin | Plugin "not enabled" | Enable plugin, surface kanban+cron+skills |
| 2 | Event Triggers | `hermes webhook` (port 8644) | **Not enabled** | `hermes gateway setup` for webhook, then 3+ subscriptions |
| 3 | Cron Jobs | `hermes cron` (English-to-cron) | 4 active, all DreBrain; missing coverage | Add morning brief, X scan, content audit, weekly synthesis, competitor watch |
| 4 | /goal Structure | prompt discipline | No `goal-runner` skill | Create `goal-runner` skill wrapping the template |
| 5 | Sub-Agents | `hermes kanban swarm` v1 | CLI exists, informal use | Make swarm the default for multi-stream research |
| 6 | Telegram Topics | gateway multi-platform | Only `default` has running gateway | Enable per-profile gateways + Topics |
| 7 | Kanban | `hermes kanban` | Strong on `default` | Underused `mavis-kanban-monitor` and `v4` |
| 8 | Skills as SOPs | `hermes bundles` | **Only 2 bundles** for 112+ skills | Group into 15-20 named bundles |
| 9 | Webhooks | `hermes webhook` | **Not enabled** | Same as #2 |
| 10 | Separate Agents by Job | `hermes profile` (full lifecycle) | 14 profiles, only `default` has model + gateway | Activate the orchestrator layer |

## Hermes 0.16.0 native features not activated

| Feature | State | Worldclass target |
|---------|-------|-------------------|
| `hermes acp` (Agent Client Protocol server) | not used | expose Hermes as a service |
| `hermes computer-use` (cua-driver) | installed, disabled | enable after accessibility grant |
| `hermes insights` (usage analytics) | not running | monthly review to prune |
| `hermes security` (OSV.dev supply chain) | not scheduled | weekly Sunday 4am |
| `hermes backup` / `hermes import` | not scheduled | weekly Sunday 5am |
| `hermes bundles` | 2 of 200+ skills | 15-20 named bundles |
| 8 external memory providers (honcho, openviking, mem0, hindsight, holographic, retaindb, byterover) | built-in only | pick one, run `hermes memory setup` |
| `hermes doctor` | not in cron | weekly Sunday 3am |
| 6+ bundled plugins (disk-cleanup, google_meet, teams_pipeline, hermes-labyrinth, etc.) | 5 of 6 disabled | enable by ROI |

## Production issues spotted today

1. **Honcho Model cron failing** — `HTTP 429: 5-hour usage limit reached`. No retry/backoff. Silent failure for 1h 37m.
2. **`mavis` profile missing from `hermes profile list`** — only default + 7 stopped executors show. Registry may be stale.
3. **13/14 profiles have no model assigned** (column shows `—`). Profiles cannot be activated without a model.
4. **`openclaw-dashboard` plugin status is "not enabled"** despite being the mission control for the fleet.
5. **Webhook platform completely off** — `hermes webhook list` returns the setup prompt.

## Worldclass target — sequenced

### Tier 1: Activation (this week)
1. Wire all 14 profiles to a model + running gateway (mimo-v2.5-pro for executors, sonnet for orchestrators, opus for verifier)
2. Enable the webhook platform and wire 3 subscriptions (Notion card move, GitHub PR open, competitor RSS)
3. Fix the failing Honcho Model cron — add backoff/retry or fallback model
4. Register `mavis` in `hermes profile list` if missing — `hermes profile describe mavis` to verify

### Tier 2: The 10 Hacks in production (this month)
5. Enable `openclaw-dashboard` plugin — wire Mission Control
6. Add 5 missing cron jobs: morning brief (6am), X niche scan (3h), competitor check (9pm), content audit (Mon 9am), weekly synthesis (Fri 6pm)
7. Create `goal-runner` skill wrapping `/goal [OUTCOME] using [SOURCES] with constraints: [CONSTRAINTS] deliverable: [DELIVERABLE]`
8. Make `hermes kanban swarm` the default for multi-stream research
9. Create Telegram group with Topics (YouTube, React, Coding, Research, General, Ops), each topic → different profile
10. Group 112+ skills into 15-20 named bundles

### Tier 3: Native extras (this quarter)
11. External memory provider — `hermes memory setup` (honcho or hindsight recommended)
12. GEPA on `hermes-fleet-orchestration` (highest activity: 216 activity, 67 use) — per-skill effect size, bounded edits, validation gate
13. Plugin activation by ROI: `disk-cleanup` (cron logs), `hermes-labyrinth` (dashboard), `hermes security` (audit). Leave `google_meet` and `teams_pipeline` disabled.
14. Weekly rituals automated: `hermes doctor` Sun 3am, `hermes security` Sun 4am, `hermes backup` Sun 5am, GEPA weekly
15. `hermes insights` monthly review — prune the bottom 20% of skills/profiles/crons

## Don't change

- **14-profile architecture** — orchestrator/executor/specialist split is good
- **Curator settings** — 7d interval, 30d stale, 90d archive
- **DreBrain skill** — load-bearing for vault indexing
- **Tier 1 + Tier 2 memory** — built-in MEMORY.md/USER.md + SQLite FTS5
- **Skill volume (112)** — asset, not problem. Organization is the issue
- **Hermes-native over Gibson V4** — plugins, profiles, bundles, kanban, webhooks, cron, GEPA, curator, memory, insights already cover everything V4 was rebuilding

## The self-evolution moment

PR #40673 is itself a self-evolution artifact — Andre found a real Hermes bug (`hermes update` silent no-op on feature branches), wrote the handoff, and the fix is in flight. **Hermes reviewing his own PR and catching a stash-restore ordering bug in the fix is the loop closing.** This is what `skill_manage` + curator + GEPA exist to compound.

The right next move is to **let Hermes ship the v2 of the PR with his own suggested fix**, then run a GEPA pass on whichever skill generated the original code. The agent catching the agent's bug, then getting better at writing the next one, is the system learning itself.

## Self-evolution loop result — 2026-06-06, single session

In one relay session, Hermes completed three full bug cycles and produced a meta-skill. The loop (bug → handoff → PR → review → merge → regression test → skill → meta-skill) is now proven end-to-end.

### PRs landed (all open, mergeable, all tests green)

| PR | Fix shape | Tests | Skill created |
|----|-----------|-------|---------------|
| #40673 (v2) | Reorder — gate stash restore on current_branch in {branch, "HEAD"} | 49 (12 new + 30 autostash + 7 banner) | `software-development/git-stash-branch-update-ordering` |
| #40706 | Bypass — parse slash commands before `busy_text_mode` early return using `ACTIVE_SESSION_BYPASS_COMMANDS` | 43 (9 new + 17 busy_session_ack + 17 subagent_protection) | `software-development/session-aware-command-ordering` |
| #40714 | Clamp — `_last_flushed_db_idx = min(_last_flushed_db_idx, len(messages))` after scaffolding drop | 32 (regression suite mirrors v1/v2 structure) | `software-development/scaffold-drop-persist-ordering` |

**Total: 124 tests, all green.** The three fixes share a deeper shape — lifecycle code runs before operational logic that needs to be ordered against it. Three different fix shapes (reorder, bypass, clamp) because the coupling surfaces differently each time, but the same error class.

### The meta-skill

`software-development/mixed-concern-ordering` is live. Built from three concrete instances, captures:
- Recognition triggers (when to load it)
- Three fix shapes (reorder, bypass, clamp) and when each applies
- Anti-patterns (lifecycle running before operational logic)
- Pointers to the three specific skills as loaded primitives

**The next agent that writes code crossing two state dimensions has the pattern before writing the code.** That is the self-evolution loop in its strongest form — the system teaching the next iteration of itself.

### What the loop result tells us about the architecture

The fact that three bugs in one session all fit the same family is *evidence the family is real*. It also suggests the codebase has more instances we haven't found yet — the meta-skill should be loaded during any future code review that touches mixed-concern paths, not just during the next bug triage.

**GEPA discipline:** Do not run GEPA on `mixed-concern-ordering` yet. The meta-skill is brand-new with zero usage data. Schedule GEPA after 2-3 real PRs load the skill and the per-skill effect size has a baseline. Same discipline applies to the three concrete skills.

### Three PRs is a healthy pipeline

The bottleneck is now merge velocity, not generation velocity. Three mergeable PRs in flight means the next session can either (a) continue the bug loop with the meta-skill loaded, or (b) pivot to Tier 1 strategic work (model assignment across 14 profiles, gateway activation, webhook enable, Honcho cron retry). Both threads are independent and compoundable.

## Next decisions for Andre

- [ ] Merge timing for #40673, #40706, #40714 (all open, all mergeable)
- [ ] Confirm Tier 1 priority (activation) before Tier 2/Tier 3 strategic work
- [ ] Pick the external memory provider (honcho vs hindsight vs mem0)
- [ ] Approve model routing table (executors / orchestrators / verifier)
- [ ] After meta-skill has 2-3 real PRs of usage data, schedule first GEPA pass on `mixed-concern-ordering`

## Routing

This memo lives at `03 Projects/Hermes/architecture-review-2026-06-06.md`. Mavis will not execute any changes — Hermes is the operator for this scope. Andre relays between Mavis and Hermes until the activation tier is complete.

**Memo status:** strategic analysis delivered 2026-06-06 12:55 CT, self-evolution loop result section appended 2026-06-06 13:45 CT. Next update when PR #40673 merges (loop-result confirmation) or when Tier 1 strategic work begins.

---

## Updated framing — 2026-06-06 15:22 CT (post-activation)

The original "Worldclass target" section above over-indexed on Telegram and treated surface options as load-bearing primitives. After the activation batch landed and the fleet started running, Andre re-anchored the actual architecture:

**The actual worldclass target:**
- **Hermes builds specialist agents.** Profiles are designed as needed when the work demands a new domain of expertise. Not pre-defined for every possible future job.
- **Agent profiles are the team.** Each profile has its own context, memory, skills, toolsets, boundaries. The dispatcher routes work to the right profile based on the task.
- **Hermes-native kanban is the work surface.** Tasks go on the board, profiles claim them, work happens, results land back. `hermes kanban swarm` (parallel workers → verifier → synthesizer) is the multi-agent pattern.
- **Workflows get automated.** Recurring patterns become cron jobs, become skills, become SOPs. Curator keeps the library clean. GEPA tunes the skills.
- **Specialist agents designed as needed.** When a gap appears in the fleet, Hermes designs a new profile to fill it.

**What this drops from the original target:**
- ❌ Per-profile Telegram routing / Topics supergroup
- ❌ 7-bots-per-profile architecture
- ❌ Treating Mission Control as a separate product (the kanban + cron + dashboard already is mission control natively)
- ❌ The 10 masterclass hacks as the spine (they're surface options, not architecture)

**What stays (still valuable, separate from the spine):**
- ✅ The 3 PRs in flight — bug → handoff → PR → review → merge → regression test → skill → meta-skill loop is a working pattern
- ✅ The 4 skills (1 meta + 3 concrete) — real artifacts regardless of surface
- ✅ The architecture review itself as a reference doc
- ✅ The model/plugin/voice/surface-area hard corrections in agent memory

**Tier 1 in motion (2026-06-06 15:22 CT):**
- 8 active tasks on the kanban across 5 specialist profiles
- 3 specialists running: code-reviewer (PR #40673 audit), verifier (PR #40706 tests), researcher (AI frameworks comparison)
- 5 new tasks dispatched: PR #40714 review, profile fleet audit, first 2-3 workflows to automate, mixed-concern-ordering meta-skill audit, self-evolution loop SOP doc
- Profile rename complete (specialist.* → specialist-*, dots broke the dispatcher regex)
- 15 poison tasks blocked, 3 clean tasks running

**Next move:** the dispatcher claims and routes on its 60-second tick. Results come back per task. The system proves itself by doing things, not by being configured.

**Memo status (updated):** strategic analysis 12:55 CT, self-evolution loop result 13:45 CT, framing update 15:22 CT. Next update when kanban results come back or when new strategic questions arise.
