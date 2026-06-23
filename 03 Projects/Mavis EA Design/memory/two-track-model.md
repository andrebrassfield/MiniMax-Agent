# Two-Track Operating Model — Detailed Reference

Companion to `MAVIS.md` "Active Theses" thesis 1 and MEMORY.md pointer. Loaded when Mavis needs the operational details of the two-track model.

**Source decision:** `02 Notes/decisions/2026-06-22-two-track-model.md`

## The 5 Hard Rules

1. **One Track 2 per spec.** Track 3 requires explicit Andre approval. Two tracks is the cap.
2. **Spec must be on disk before Track 2 spawns.** Disk = source of truth. Chat is not.
3. **Track 2 reads, Track 1 writes (for shared state).** Track 2 only writes to its assigned output path.
4. **Subagent channel stays verifier-only.** Producer work → skill it, do it in Track 1, or spawn Track 2 (not a producer subagent).
5. **Rate-limit budget allocated, not consumed freely.** 50/30/5/15 (Track 1 / Track 2 / Verifier / Cron) → bumped to 50/25/5/20 after Cron track added the second-self crons. Tracked by `rate-limit-tracker` cron. Enforced at spawn by `two-track-handoff` skill.

## What This Replaces

The "team of internal agents" model (builder, coder, designer, general) was retired 2026-06-22. Their work goes in Track 2 sessions with the appropriate skills loaded — same capability, no subagent quota burned, no parallel-attention cost. See `03 Projects/Mavis EA Design/agent-audit-2026-06-22.md` for the per-agent disposition.

## What Stays Unchanged

- The X-Content-Engine cron chain (x-researcher, x-scribe) runs on its own session tree against a separate rate-limit pool. Not affected by this model.
- The verifier-only subagent channel. Same hard rule, same scope.
- The ABSOLUTE SEPARATION from Hermes / OpenClaw / gbrain. No relationship with any other agent's filesystem territory.
- Memory hygiene, decision logging, commitment tracking. All unchanged.

## Active Project (the Karpathy Pattern)

When Andre is focused on one project, Mavis scopes context to that project only. The `active_project` field in `MAVIS.md` YAML frontmatter signals the focus.

- Set: Andre says "let's work on X" → Mavis sets `active_project: X`
- Clear: Andre says "back to inbox" → Mavis clears to null
- Read: cold-start procedure at `~/.mavis/agents/mavis/skills/context-loader/SKILL.md`

Cross-project moments (second-self crons, explicit "load everything") bypass the scope automatically.

## Skill: `two-track-handoff`

The canonical procedure for spec → Track 2 spawn → poll → verify. Loaded when a spec is approved and implementation needs to run autonomously.

- 8 pre-conditions: spec on disk, plan, Andre approval, output path, ≥30% budget, single-track scope, halt conditions, stop condition
- 5-step procedure: verify → compose packet → spawn session → register → confirm
- Halt conditions, output schema, failure modes all in the skill file

## Reversibility

Fully reversible in <5 min:
1. Remove `active_project` field from MAVIS.md
2. Delete `~/.mavis/agents/mavis/skills/two-track-handoff/` + mirror
3. Restore MEMORY.md session-start checklist to ad-hoc discovery
4. Remove the SOUL.md usage note
5. Remove this MEMORY.md entry

No data at risk.
