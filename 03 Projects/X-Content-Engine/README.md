---
type: project-overview
status: staging
created: 2026-06-16
owner: Andre (Dre)
handle: @DreTheSalesGuy
purpose: Scale @DreTheSalesGuy's X account via a Chief-of-Staff + 2 specialist agent team.
---

# X-Content-Engine

## What this is

A two-agent content production team, orchestrated by Mavis (EA), to scale @DreTheSalesGuy's X account. The team:

1. **Reads X bookmarks** (via `x-bookmark-parser` skill — already shipped)
2. **Analyzes high-performing formats** (Researcher agent)
3. **Drafts new posts in the user's voice** (Scribe agent)
4. **Queues drafts for user approval** (no auto-publish)

The chief (Mavis) routes bookmarks → researcher → brief → scribe → draft → human approval → publish (manual, by user).

## Data flow

```
x.com/i/bookmarks
   ↓ (Mavis runs x-bookmark-parser skill)
00 Inbox/x-bookmarks-YYYY-MM-DD-HHMM.md
   ↓ (Mavis spawns Researcher, consumes the file)
03 Projects/X-Content-Engine/briefs/YYYY-MM-DD-HHMM-brief.md
   ↓ (Mavis spawns Scribe with brief + persona file)
03 Projects/X-Content-Engine/drafts/YYYY-MM-DD-HHMM-draft-NNN.md
   ↓ (Mavis files the draft for user review)
00 Inbox/ → user reviews → user publishes manually on x.com
```

## Agents

| Agent | Role | File |
|-------|------|------|
| **researcher** | Viral Format Analyst — reads bookmarks, deconstructs hooks, generates Content Briefs | `agents/researcher.md` |
| **scribe** | X-Platform Ghostwriter — translates briefs into drafts in @DreTheSalesGuy voice | `agents/scribe.md` |
| **(chief: Mavis)** | Orchestrator — runs the parser, dispatches agents, queues drafts for review | (already in `~/.mavis/agents/mavis/`) |

Team config + handoff protocol: `agents/team-config.md`.

## Status

**Active. Live spawn mode since 2026-06-16 15:48 CT.** Both agents (`x-researcher`, `x-scribe`) are registered; the team is dispatched via `mavis communication send --command spawn` per `agents/team-config.md`. The feedback loop (Stage 4 in `team-config.md` + `agents/feedback-loop.md`) is wired as of 2026-06-17 11:05 CT — publishes flow into `queue/drafts-published.mdl`, a one-shot cron fires the analytics skill 3-5 days later, and the `performance_log` rank-weights the next Researcher + Scribe runs.

The README's earlier "Staging. Not activated" status was stale; the team has been live since 2026-06-16 15:48 CT and the activation checklist in `agents/team-config.md` reflects the actual state.

## TODO (open, not blocking)

- [ ] Confirm cadence (light / medium / heavy) — deferred. Default is on-demand.
- [ ] Add 4-7 more voice examples to `agents/persona.md` as the brand evolves. Current: 6 examples (target steady-state: 5-10).
- [ ] Decide the cross-platform publishing surface (LinkedIn, Threads). For now, `x.com` is the only post-URL source.

## What this is NOT

- Not an auto-publisher. Drafts go to a queue, not to x.com. The user publishes manually after approval.
- Not a content farm. The Researcher only analyzes what the user has actually bookmarked — it does not invent formats from nothing. The Scribe only drafts from approved briefs, not from generic AI patterns.
- Not a persona-mimicry engine with persona data the team invented. The Scribe halts until `persona.md` is filled with the user's actual voice examples.
- Not a real-time analytics engine. The feedback loop runs on a 3-5 day lag (X's per-post analytics aggregation window). It is weekly-cadence learning, not per-minute.
- Not a content recommender. The feedback loop ranks ideas by hook family performance; it does not tell Andre what to write. The Researcher + Scribe still produce the actual drafts, with Andre as the editor in chief.
