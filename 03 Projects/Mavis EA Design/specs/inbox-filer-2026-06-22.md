---
date: 2026-06-22
type: closed-loop-spec
status: awaiting-approval-then-immediate
scope: inbox-filer
related:
  - ~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md
  - ~/.mavis/agents/mavis/crons/second-self-morning-brief.md
  - ~/MiniMax-Agent/02 Notes/articles/_discipline/REACTION-RULE.md
---

# Spec: Inbox Filer Cron

Closes the gap between capture (morning brief surfaces new files in `00 Inbox/`) and organization (files move to their proper locations). Daily cron at 06:30 CT — fires right after the morning brief, processes that day's inbox additions.

## Goal (done condition)

1. New cron `inbox-filer` at `~/.mavis/agents/mavis/crons/inbox-filer.md` — 06:30 CT daily
2. Reads new files in `00 Inbox/` (modified since last run, via state file)
3. For each file: classifies (idea / article / project note / task / link / quote), routes to correct folder, adds wikilinks, writes minimal frontmatter
4. Reaction discipline enforced — articles without `## Reaction` go to `02 Notes/articles/_pending_reaction/` not back to `02 Notes/articles/`
5. State file at `~/.mavis/state/inbox-filer.state.json` tracks last_run_at + processed files
6. Vault mirror of cron at `99 _system/crons/inbox-filer.md`
7. MAVIS.md + MEMORY.md updates
8. Manual test passes: drop 3 sample files in `00 Inbox/`, run cron, verify correct routing

## Context

The morning brief (06:00 CT) surfaces what's in the inbox but doesn't move anything. This creates a graveyard effect: files accumulate in `00 Inbox/` without clear ownership. The article's Step 10 mentions a daily task that "files anything new sitting in Inputs folders into the right place and link it." That's what this spec delivers.

## Action (atomic steps)

1. Write this spec (this file)
2. Build the cron prompt (self-contained procedure)
3. Create state file at `~/.mavis/state/inbox-filer.state.json` (init with empty)
4. Mirror cron to vault
5. Update MAVIS.md Active Skill Mutations
6. Update MEMORY.md (pointer)
7. Manual test with 3 sample files

## Feedback

- Per-file audit log in the state file
- Daily output written to `~/.mavis/state/inbox-filer-YYYY-MM-DD.md`
- Sunday weekly-deep cron consumes this output as input
- End-of-week gate: <50% of files routed correctly → halt the cron, surface

## Stop condition

Open-loop (runs daily). Halt conditions:
- Inbox file unreadable (permissions, encoding) → skip file, log, continue
- Classification ambiguous (can't decide folder) → leave in inbox, flag in output
- Daily count > 50 → process first 50, surface "X files remaining"
- Same file fails to classify 3 days in a row → move to `05 Archive/`

## Reversibility

`<5 min: mavis cron delete mavis inbox-filer + mavis-trash state file + revert MAVIS.md/MEMORY.md`
