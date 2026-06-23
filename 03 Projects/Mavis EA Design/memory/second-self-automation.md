# Second-Self Automation Layer — Detailed Reference

Companion to `MAVIS.md` "Active Theses" thesis 2 and MEMORY.md pointer. Loaded when Mavis needs operational details on the second-self crons.

**Source decision:** `02 Notes/decisions/2026-06-22-two-track-model.md`
**Source spec:** `03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md`

## What "Second Self" Means Here

Per the article ("Everyone Is Building a Second Brain..."):

> "A second brain remembers for you. A second self thinks with you."

The shift: from passive storage (capture + retrieve) to active reasoning (surface connections, contradictions, emerging theses). The automation layer below delivers this shift.

## The 4 Crons (canonical at `~/.mavis/agents/mavis/crons/`)

1. **`second-self-morning-brief`** — 06:00 CT daily. Reads 7d of vault activity. 4 sections (Connections / Pattern / Contradiction / Best Capture) + Calendar section. Output: `00 Inbox/brief-YYYY-MM-DD-synthesis.md`.
2. **`inbox-filer`** — 06:30 CT daily. Routes new inbox files to correct folders. Reaction discipline enforced (articles without `## Reaction` → `_pending_reaction/` subfolder).
3. **`second-self-contradiction`** — 07:00 CT daily. Reads `02 Notes/ideas/` vs last 30d of `02 Notes/articles/`. Surfaces ONLY conflicts. Default: "Clear."
4. **`second-self-nightly-connections`** — 23:00 CT daily. Reads notes from last 48h, searches vault for non-obvious connections. Writes connection notes to `08-COMPOUND/`. (Added 2026-06-22.)
5. **`second-self-weekly-deep`** — Sunday 19:00 CT. Reads 30d of vault. 4 outputs (Emerging thesis / Full contradiction map / Knowledge gaps / One action). "This session should be uncomfortable."

Plus: `vault-health` (1st Sun 23:00 CT — monthly audit), `rate-limit-tracker` (22:00 CT daily — budget ledger).

## Reaction Discipline (the load-bearing rule)

Every note in `02 Notes/articles/` must have a `## Reaction` section. The morning brief cron Step 1.5 enforces: notes modified in last 7d without a Reaction get moved to `02 Notes/articles/_pending_reaction/` for re-processing.

Doc: `02 Notes/articles/_discipline/REACTION-RULE.md`

## Halt Conditions Per Cron

- Morning brief: <3 notes in window → silent skip
- Inbox filer: ambiguous classification → leave in inbox, flag in output
- Contradiction check: `02 Notes/ideas/` empty → silent skip
- Nightly connections: <2 recent notes → silent skip
- Weekly deep: <5 notes in last 30d → silent skip
- All: vault unreadable → HALT, surface

## Rate-Limit Impact

The cron track budget was bumped 15% → 20% when the second-self crons were added. These are reasoning-heavy M3 work; the increase is real but justified.

## Reversibility Per Cron

`<5 min: mavis cron delete mavis <name> + mavis-trash state file + revert MAVIS.md/MEMORY.md`

## Cross-References

- Spec: `03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md`
- Article: "Everyone Is Building a Second Brain..." (2026-06-22)
- Reaction discipline: `02 Notes/articles/_discipline/REACTION-RULE.md`
- Calendar integration: `~/.mavis/agents/mavis/memory/calendar-mcp.md`
