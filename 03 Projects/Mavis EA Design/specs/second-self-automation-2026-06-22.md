---
date: 2026-06-22
type: closed-loop-spec
status: active
scope: second-self-automation
related:
  - ~/MiniMax-Agent/02 Notes/decisions/2026-06-22-two-track-model.md
  - ~/MiniMax-Agent/MEMORY.md (Two-Track Operating Model)
  - ~/MiniMax-Agent/SOUL.md (Two-Track Operating Model section)
  - ~/.mavis/agents/mavis/crons/rate-limit-tracker.md
informed_by:
  - Khairallah, "Everyone Is Building a Second Brain. The People Winning Are Building a Second Self." (article shared by Andre 2026-06-22)
  - Khairallah, "30 Obsidian Workflows, Plugins, and Setups That Most Users Don't Know" (article shared by Andre 2026-06-22)
  - Path A scope agreement (this session): minimal-change refactor — add the missing second-self automation layer, keep existing folder structure
---

# Spec: Second-Self Automation Layer (Path A)

The minimal-change refactor that adds the second-self reasoning layer on top of Andre's existing vault. Per Path A scope agreement, no folder structure changes. Three new crons + tightened reaction discipline. Closes the gap between second-brain (capture) and second-self (reasoning).

## Goal (precise done condition)

This spec is DONE when:
1. Three new crons are registered and producing output on schedule:
   - `second-self-morning-brief` fires daily at 06:00 CT, reads 7 days of `01 Daily/`, `02 Notes/ideas/`, `02 Notes/articles/`, produces 4-section brief (Connections / Pattern / Contradiction / Best Capture) to `00 Inbox/brief-YYYY-MM-DD-synthesis.md`
   - `second-self-contradiction` fires daily at 07:00 CT, reads `02 Notes/ideas/` against last 30d of `02 Notes/articles/`, surfaces ONLY conflicts to `00 Inbox/contradiction-check-YYYY-MM-DD.md`
   - `second-self-weekly-deep` fires Sunday 19:00 CT, reads 30 days of vault activity, produces 4 outputs (Emerging thesis / Full contradiction map / Knowledge gaps / One action) to `00 Inbox/weekly-deep-YYYY-MM-DD.md`
2. Reaction discipline doc is in place at `02 Notes/articles/_discipline/REACTION-RULE.md` AND the next morning brief cron validates that every `02 Notes/articles/` note modified in the last 7 days has a Reaction section (moves violating notes to `00 Inbox/` for processing)
3. MAVIS.md Active Skill Mutations entry written + MEMORY.md Second-Self Automation section written
4. Rate-limit-tracker cron allocation updated: cron track 15% → 20% to absorb the new load
5. All crons mirrored to vault at `99 _system/crons/`
6. First run of each cron produces non-empty output (verified by next-Mavis reading the output file)

## Context

**Source decision:** Andre chose Path A over full vault restructure. The article's "5 folders" prescription would have destroyed ~70% of Andre's existing second-self architecture (which already exists under different names — see the mapping table in this session's prior message). Path A adds only the missing automation layer.

**Existing inventory (don't move, don't rename):**
- `00 Inbox/` = article's `00-Inbox` ✓
- `01 Daily/` = chronological capture (article collapses this; we keep)
- `02 Notes/articles/` = article's `01-Sources` (with looser reaction discipline than article wants)
- `02 Notes/ideas/` = article's `02-Ideas` ✓ (with sub-types: patterns/questions/numbers)
- `02 Notes/patterns/`, `questions/`, `numbers/`, `_MOCs/` = typed reasoning infrastructure (article doesn't have; stronger)
- `03 Projects/` = article's `03-Projects` ✓
- `06 Connections/` = synthesis output destination (article says delete; we keep)
- `07 Vellum/` = intelligence layer (article says collapse; we keep)
- `99 _system/` = tooling/templates (keep)
- `SOUL.md` + `MAVIS.md` + `MEMORY.md` = article's CLAUDE.md equivalent (more thorough)

**The gap (the 3 things this spec closes):**
1. No daily synthesis brief firing at 6am — `ea-daily-brief` skill exists but runs on-demand, not scheduled
2. No contradiction-check cron — `02 Notes/decisions/` exists for captured decisions, but nothing reads ideas-vs-sources for active conflict
3. No "emerging thesis" output in the weekly connections workflow — `ea-weekly-connections` produces 3-5 patterns, not the named-position output the article prescribes

## Action (atomic steps)

The execution happens in this session (Track 1 — single Mavis, this context window). Steps in order:

1. **Write this spec** — DONE (this file)
2. **Create `~/.mavis/agents/mavis/crons/second-self-morning-brief.md`** — self-contained cron, full procedure inline, 06:00 CT, model M3
3. **Create `~/.mavis/agents/mavis/crons/second-self-contradiction.md`** — self-contained cron, full procedure inline, 07:00 CT, model M3
4. **Create `~/.mavis/agents/mavis/crons/second-self-weekly-deep.md`** — self-contained cron, full procedure inline, Sunday 19:00 CT, model M3
5. **Create `~/MiniMax-Agent/02 Notes/articles/_discipline/REACTION-RULE.md`** — the reaction discipline doc, makes the rule explicit
6. **Add reaction-validation step to morning brief cron** — Step 1.5 of the morning brief checks every `02 Notes/articles/` note modified in last 7d, moves violating notes to `00 Inbox/` (so they get re-processed with a Reaction section)
7. **Mirror crons to vault** — `cp` each cron to `99 _system/crons/<name>.md`
8. **Update MAVIS.md** — new Active Skill Mutations entry: "2026-06-22 — Second-Self Automation Layer (Path A)"
9. **Update MEMORY.md** — new "Second-Self Automation (2026-06-22)" section after Two-Track Operating Model
10. **Update rate-limit-tracker.md** — bump cron allocation 15% → 20% (3 new crons + reasoning-heavy M3 work)

## Feedback (verification gate)

Each new cron has a self-audit step that runs on every invocation. Verification happens at multiple levels:

**Per-cron self-audit (runs every invocation):**
- Morning brief: 4 required sections present in output (Connections ≥ 2 / Pattern ≥ 1 / Contradiction ≥ 0 / Best Capture = 1). If any section empty → log warning + write `00 Inbox/brief-YYYY-MM-DD-synthesis-INCOMPLETE.md` + continue
- Contradiction check: every idea either has ≥1 conflicting source OR is marked `Clear`. If output has fewer entries than ideas → log warning
- Weekly deep: 4 required outputs (Emerging thesis / Contradiction map / Knowledge gaps / One action). If empty → HALT, surface

**End-of-week gate (Sunday after the weekly-deep cron fires):**
- Next-Mavis reads the week's 7 morning briefs + 7 contradiction checks + 1 weekly deep
- Verifies: briefs are non-trivial (not just summaries), contradiction checks found ≥3 conflicts OR explicitly noted "no conflicts," weekly deep named an emerging thesis
- Reports findings in the next daily brief

**Open-loop or closed-loop classification:**
- Per `ea-loop-thinking`: open loop (Andre is in the feedback loop, the briefs surface things for him to react to)
- Halt conditions (below) provide the automatic stop signal

**Cross-team check:** Mavis territory only. The crons read only Mavis-internal paths (`~/MiniMax-Agent/`, `~/.mavis/`). No cross-team reads.

## Stop condition

The cron chain is OPEN-LOOP (it runs daily forever by design). The spec itself is DONE when the Goal conditions above are met.

**Halt conditions for individual cron runs:**
- Morning brief: HALT if vault has <3 notes modified in last 7d (insufficient material; exit silently with `<mavis-progress>`)
- Contradiction check: HALT if `02 Notes/ideas/` is empty (nothing to check against)
- Weekly deep: HALT if vault has <5 notes modified in last 30d (insufficient material; exit silently)

**Halt conditions for the spec overall:**
- Andre reverses the second-self direction (writes a new decision reversing this one)
- The 3 crons consistently produce low-value output (<1 actionable insight per week) for 4 consecutive weeks → revert to on-demand skills, drop crons
- Rate-limit budget exhausted for 3 consecutive days → drop the weekly deep (lowest leverage of the three) first

## Reversibility

Fully reversible. Each cron is a separate file in `~/.mavis/agents/mavis/crons/` — `mavis cron delete mavis <name>` removes it. The reaction discipline doc is a markdown file. The MAVIS.md / MEMORY.md / rate-limit-tracker updates are append-only edits.

If Andre wants to revert: `mavis cron delete mavis second-self-morning-brief second-self-contradiction second-self-weekly-deep` + delete `02 Notes/articles/_discipline/REACTION-RULE.md` + revert the 3 doc updates.

## Related surfaces

- `~/MiniMax-Agent/02 Notes/decisions/2026-06-22-two-track-model.md` — the two-track pivot decision this spec extends
- `~/.mavis/agents/mavis/memory/MEMORY.md` — Two-Track Operating Model section + new Second-Self Automation section (this spec adds)
- `~/.mavis/agents/mavis/skills/ea-daily-brief/SKILL.md` — the on-demand skill the morning brief cron replaces with scheduled execution
- `~/.mavis/agents/mavis/skills/ea-weekly-connections/SKILL.md` — the existing skill the weekly deep extends with "emerging thesis" output
- `~/.mavis/agents/mavis/skills/ea-loop-audit/SKILL.md` — the diagnostic skill to use for end-of-week verification gate
