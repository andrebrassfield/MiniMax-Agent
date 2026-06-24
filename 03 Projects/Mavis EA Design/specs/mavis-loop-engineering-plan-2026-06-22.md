---
type: spec
status: proposed
date: 2026-06-22
source: 02 Notes/articles/2026-06-22 - Loop-Engineering-in-2026.md
framework: 02 Notes/patterns/mavis-as-llm.md + 02 Notes/patterns/loop-engineering-framework.md
estimated-spend: 60-90K tokens across 2-3 fresh sessions
priority: P1 (the 3 carry-over items are the highest-leverage Mavis work right now)
---

# Plan: Mavis as Loop Engineer — Synthesis + 3 Carry-Over Items

> Synthesizes the Loop Engineering article with everything we built today. The article validates Mavis's architecture (all 6 loop components present). The plan addresses the 3 carry-over items you named (bundle manifests, Upgrade 2, Upgrade 3) plus 2 refinements the article surfaced.

## Framing: what the article means for Mavis

The article's headline — "design loops, don't prompt agents" — is **not new for Mavis**. We already operate as a loop engineering system:

- **Skills (block #3):** 46 skills at `~/.mavis/agents/mavis/skills/` + 55 vault topic files
- **Automations (block #1):** 40+ crons at `~/.mavis/agents/mavis/crons/`
- **Memory (block #6):** MEMORY.md + topic files + vault + kanban
- **Subagents (block #5):** verifier + gepa-evaluator + fleet-trust-patterns
- **Plugins/Connectors (block #4):** 8 MCP servers
- **Worktrees (block #2):** `mavis team plan` parallel streams (analog, not literal git worktrees)

**What's NEW from the article:**
1. **The cost problem is named.** Loops burn 50K-200K per run; fleets 500K-2M. Daily cron loops cost millions per week. We just hit this today (~$22 → $35-40+ after one session's work). The dial-in discipline is justified.
2. **The mindset shift is explicit.** Prompt Engineer → Loop Engineer. Linguistic skill → Software engineering skill. Mavis IS the loop engineer; Andre is the operator who encodes judgment into loop design.
3. **The 5-part loop template is sharper than ours.** Goal → Context → Action → Feedback → Stop. Same content as our 5-stage pipeline but cleaner naming. Worth adopting.
4. **Closed loop as default is the right 2026 posture.** Open loops burn "insane amounts." We already default to closed loops in `ea-loop-thinking`'s hard constraints. Validation.
5. **Real loop examples map to Mavis directly.** Research loop = `ea-research-brief`. Content loop = `x-reply-guy`. Coding loop = `ea-5-mistakes-audit`. The architecture is consistent across domains.

## What the article exposed as gaps

Three places where Mavis is NOT yet a complete loop engineer:

1. **No bundle manifests.** Skills exist individually; the bundles (curated skill sets for specialist workflows) are implicit, not explicit. A new Mavis session loads skills by trigger-matching, not by bundle-design.
2. **No RLHF-analog feedback loop.** We capture corrections ad-hoc (`ea-correction-capture` was the proposed skill; not built). Without it, Mavis doesn't learn from Andre's "stop asking, decide" patterns.
3. **No formal benchmark suite.** `agent-disease-detector` cron is the only eval. No representative-task benchmarks, no drift detection over time.

These are the 3 carry-over items you named. Below.

## The 3 carry-over items (the plan proper)

### Item 1: Bundle manifests (6 bundles)

**Per the earlier decision (2026-06-22):** "After refactor — bundles need stable skill set first." The 10 refactored + 5 archived = stable set. **Now is the time.**

**The 6 bundles proposed:**

| Bundle | Skills it composes | When to load |
|---|---|---|
| `bundle: cold-start-ops` | `mavis-cold-start`, `context-loader`, `two-link-rule`, vault-health-trigger | Mavis session cold start (every root session) |
| `bundle: ea-workflows` | `ea-daily-brief`, `ea-research-brief`, `ea-weekly-connections`, `ea-decision-logger`, `ea-commitment-tracker`, `ea-draft-approval`, `ea-state-audit`, `ea-skill-evolution`, `ea-5-mistakes-audit`, `ea-loop-audit`, `ea-loop-thinking`, `ea-closed-loop-builder`, `ea-data-quality-audit` | Any EA workflow invocation |
| `bundle: x-content-publish-ops` | `x-publish`, `x-reply-guy`, `x-semantic-locator`, `x-ui-bouncer`, `x-session-guardian`, `x-health-telemetry`, `x-lead-qualifier`, `x-niche-scraper`, `x-bookmark-parser`, `x-engagement-hunter`, `x-value-bomb-dropper`, `x-empowerment-hunter`, `x-hype-translator`, `x-analytics-tracker`, `x-structure-scraper` | X-Content-Engine cron chain + manual X actions |
| `bundle: quality-ops` | `ea-state-audit`, `ea-5-mistakes-audit`, `ea-loop-audit`, `ea-data-quality-audit`, `ea-skill-evolution`, `agent-disease-detector`, `kanban-health-check` (now archived — needs replacement), `vault-health` | Pre-ship audits, drift detection, weekly eval |
| `bundle: mac-setup-ops` | `agent-harness-mac-setup`, `mac-deepclean` | First-time fleet host setup, post-OS-upgrade cleanup |
| `bundle: archive` | (5 archived skills: mavis-kanban-bridge, kanban-health-check, telegram-kanban-bridge, kanban-html-board, gepa-evaluator) | NOT loaded by default; only for historical reference |

**Format (per the pattern note):** thin manifest file at `~/.mavis/agents/mavis/bundles/<name>.yaml` listing skill paths. Not a wrapper — just a list. Specialist agent = Mavis session that loads a specific bundle on cold-start.

**Effort:** ~10K tokens. Single session. Mostly file writes + a yaml schema decision.
**Risk:** Low. Bundles don't change skill behavior; they just organize discovery.

### Item 2: Upgrade 2 — RLHF-analog Feedback Loop

**Status: implemented 2026-06-22.** Architecture pivoted during implementation.

**Decisions locked (2026-06-22):**
- Trigger precision: **LLM-based classifier** (higher recall, lower precision)
- Calibration: **7-day manual eval** (Garry Tan discipline)
- Architecture: **two-phase (cron + chief)** — see below

**Architecture pivot (2026-06-22 23:30 CT):** the daemon does NOT expose an external LLM endpoint, and the `mavis llm call` CLI subcommand does not exist. Discovered during implementation when the standalone classify.py script could not reach an LLM. Pivoted to two-phase design:
- **Phase A (cron, no LLM):** `correction-classifier-nightly` cron at 21:00 CT scans files, writes daily summary, appends context buffer to `~/.mavis/state/correction-buffer/`. Pure filesystem ops.
- **Phase B (chief session, LLM available):** When chief loads, checks for pending buffer. Runs LLM classifier. Surfaces corrections to Andre via Telegram. Routes approved corrections (in auto mode).

**Files written (2026-06-22):**
- `~/.mavis/agents/mavis/skills/ea-correction-capture/SKILL.md` (lean pointer, ~1.5KB)
- `~/MiniMax-Agent/02 Notes/patterns/ea-correction-capture-procedure.md` (4-step procedure, ~6KB)
- `~/.mavis/agents/mavis/crons/correction-classifier-nightly.md` (Phase A prompt, ~5KB)
- `~/.mavis/agents/mavis/skills/ea-correction-capture/scripts/classify.py` (Python stub for future standalone use, awaits daemon LLM endpoint)
- Bundle updates: `ea-workflows.yaml` and `quality-ops.yaml` now include `ea-correction-capture`

**Daemon registration status:** Cron on disk. Registration pending daemon refresh (same 40904 stale-cache issue that affected `rate-limit-tracker` earlier today). Auto-registers on next macOS app restart. Manual command for that refresh:
```bash
mavis cron create mavis correction-classifier-nightly \
  --schedule "0 21 * * *" \
  --timezone "America/Chicago" \
  --session-mode new \
  --keep-sessions 7 \
  --report-root \
  --prompt "$(cat ~/.mavis/agents/mavis/crons/correction-classifier-nightly.md)"
```

**First scan:** 2026-06-23 21:00 CT (tomorrow evening). Manual eval mode begins at calibration day 1.

**Open work item:** the chief-of-staff session needs a Phase B trigger wired — when it loads, check for `~/.mavis/state/correction-buffer/<today>-context.md`, run LLM classifier, surface to Andre. This is in-chief work, not standalone. Recommend wiring it in tomorrow's session when chief is loaded fresh.

**Effort:** ~30K tokens (matches the plan estimate).
**Risk:** Medium-low. Phase A is pure filesystem, low risk. Phase B is in-chief, uses existing LLM path. Calibration discipline (7-day manual eval) is the spam-control.

### Item 3: Upgrade 3 — Mavis Benchmark Suite

**Decision still open:** baseline ownership (Andre sets them upfront, or me proposing + you approving?).

**What's new from the article:** the benchmark is the "Feedback" component (#4) of every loop. Without it, the loop can't tell if it's improving. The article says: "Stop condition: when the loop knows it's finished." Benchmarks tell the loop when it's at the desired state.

**Deliverable:**
- `ea-mavis-eval` skill
- Weekly cron `mavis-eval-weekly` (Sunday 19:00 CT — distinct from existing weekly-deep cron)
- Initial benchmark set: 15 representative queries covering the main EA workflows (cold-start, daily-brief, draft-approval, research-brief, state-audit, fleet-router, vault-health, etc.)
- Scoring rubric: 4 dimensions (correctness / efficiency / tone / task-completion), 1-5 each, total 4-20
- Trend tracking: weekly deltas, drift signals, surface issues to Andre

**Effort:** ~35K tokens. 4-5 hours. **Requires Andre's involvement on baseline review.**
**Risk:** Medium-high. Baseline definition is subjective; risk of self-fulfilling eval (Mavis optimizes to score well, not to be useful). Mitigation: keep Andre-in-the-loop on baseline updates.

## Sequence and dependencies

| Order | Item | Why this order | Effort |
|---|---|---|---|
| 1 | **Bundles (Item 1)** | Stable foundation. No dependency on other items. Closes a gap that's been open since the spec decision. Low risk. | ~10K |
| 2 | **Upgrade 2 (Item 2)** | Independent of bundles. The article's "Subagents = maker ≠ checker" framing sharpens the design. Manual-first calibration mitigates risk. | ~30K |
| 3 | **Upgrade 3 (Item 3)** | Independent of 1 + 2. Needs Andre's involvement on baselines; budget-aware decision (Track 1 is over budget today). | ~35K |

**Total: ~75K tokens across 2-3 fresh sessions.**

**Why this order:** Bundles are the smallest, lowest-risk item AND they unblock a stable foundation for future specialist agents. Upgrade 2 is the next-highest leverage (closes the RLHF gap). Upgrade 3 is the highest-effort item and needs Andre's time — best scheduled when budget recovers.

## 2 refinements the article surfaced (deferred)

These are NOT in the 3 carry-over items, but the article named them as worth doing. **Defer to a future session unless you want to pull forward:**

1. **Cost ceiling per loop.** Every cron should have an explicit cost ceiling in its prompt (tokens + time + side effects). This is the article's "Stop condition: when the loop knows it's finished" applied to economics. Effort: ~10K tokens to audit all 40+ crons.

2. **VISION.md / ARCHITECTURE.md / RULES.md at the agent level.** We have SOUL.md (identity) and MAVIS.md (weekly context). The article suggests VISION.md (what done means) and ARCHITECTURE.md (system structure) as canonical loop-context files. Worth considering if bundles need richer context. Effort: ~5K to draft if you want it.

## Resource reality

Today's Track 1 budget is well past allocation (likely $35-40+). Tomorrow's Track 2 budget gets eaten. **Recommendation:** Items 1 + 2 in a Track 2 spawned session tomorrow; Item 3 in a fresh root session once budget normalizes (likely Tuesday based on the weekly cycle).

## Success criteria (30 days)

- **Item 1:** 6 bundle manifests written + loaded by their respective specialist workflows at least once each. Skill discovery happens via bundles, not ad-hoc trigger matching.
- **Item 2:** `ea-correction-capture` skill + nightly cron running. ≥3 corrections captured and routed to skill/memory updates in the first month. Calibration tuned from confirmed-positive rate.
- **Item 3:** Weekly eval cron running. ≥3 weekly reports produced. Drift detection flagged at least one issue for investigation.
- **Aggregate:** Mavis operates as a measured Loop Engineer system — every loop has goal + context + action + feedback + stop, every cron has a cost ceiling, every skill has a verification gate.

## Cross-references

- **[[02 Notes/articles/2026-06-22 - Loop-Engineering-in-2026]]** — the source article
- **[[02 Notes/patterns/mavis-as-llm]]** — the build-side lens
- **[[02 Notes/patterns/ea-loop-vocabulary]]** — the 5-stage + 6-block vocabulary
- **[[02 Notes/patterns/mavis-skill-scaling-law]]** — the Skills component discipline
- **[[03 Projects/Mavis EA Design/specs/mavis-as-llm-upgrades-2026-06-22]]** — the parent spec (this plan is the operational follow-on)
- **[[03 Projects/Mavis EA Design/specs/minimax-token-dialin-2026-06-22]]** — the dial-in spec (justification for the cost discipline)
- **[[03 Projects/Mavis EA Design/minimax-token-dialin-ledger-2026-06-22]]** — the dial-in ledger (the worked example)

## Open questions for Andre

1. ~~**Bundles: am I missing one?**~~ **RESOLVED 2026-06-22:** 6 bundles as proposed. Add more if workflows emerge.
2. ~~**Upgrade 2 calibration: how many days?**~~ **RESOLVED 2026-06-22:** 7 days (Garry Tan discipline). Manual eval only during this window.
3. ~~**Upgrade 3 baseline ownership:**~~ **RESOLVED 2026-06-22:** me proposing + Andre approving (matches existing Mavis working pattern — faster iteration).
4. ~~**Sequence: do you want to start tomorrow with bundles + Upgrade 2 in a fresh session, or pick a different order?**~~ **RESOLVED 2026-06-22:** 1 → 2 → 3 in order.
5. ~~**Refinements (cost ceiling, VISION/ARCHITECTURE docs):**~~ **DEFERRED** — article-named but not on critical path. Revisit after the 3 items ship.
