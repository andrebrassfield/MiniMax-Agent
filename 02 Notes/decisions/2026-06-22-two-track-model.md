---
date: 2026-06-22
type: architectural-decision
status: active
decider: Andre
reversibility: partial
conversation: mvs_ade0b2e2c2b141f396fa3bb6ba6ba5c3
related:
  - ~/MiniMax-Agent/SOUL.md
  - ~/MiniMax-Agent/MAVIS.md
  - ~/.mavis/agents/mavis/skills/two-track-handoff/SKILL.md
  - ~/.mavis/agents/mavis/crons/rate-limit-tracker.md
  - ~/MiniMax-Agent/03 Projects/Mavis EA Design/agent-audit-2026-06-22.md
  - ~/.mavis/agents/mavis/memory/MEMORY.md (agent-harness-principles)
informed_by:
  - Tiago Forte, "You don't need ten agents. You need two tracks." (article shared by Andre in chat 2026-06-22)
  - 3-day rate-limit incident — too many concurrent Mavis subagents exhausted shared token quota
---

# Decision: Two-track model + fat skills replace internal agent team

> Captured 2026-06-22 20:42 CT by Mavis (EA) from session mvs_ade0b2e2c2b141f396fa3bb6ba6ba5c3.

## Decision

Mavis abandons the "team of internal agents" operating model in favor of a **two-track model with fat skills**: one Mavis running the spec track interactively with Andre, and a second Mavis session (different session_id, same agent) running the implementation track autonomously. The internal agents (builder, coder, designer, general, and any orphan agent) are candidates for retirement — their work goes in Track 2 sessions with the appropriate skills loaded.

## Rationale

Tiago Forte's article "You don't need ten agents. You need two tracks" gave the clean theoretical frame for what we hit empirically: a 3-day rate-limit incident caused by too many concurrent Mavis subagents burning through shared quota. The bottleneck is not implementation throughput — it's spec creation (1 Andre × 1 agent in tight loop, unparallelizable) and verification (human review of code + UX, also unparallelizable). Adding more agents multiplies the wrong variable. The rate-limit budget gets consumed faster while Andre's spec throughput stays the same.

The two-track model maps the spec bottleneck to Track 1 (high Andre attention) and the implementation work to Track 2 (autonomous, low Andre attention). Both run in parallel because they need different amounts of Andre's time. This is the dual-track development model (Marty Cagan, product management) adapted to agentic development.

Fat skills replace the internal agent team because an "agent" is really just (procedure + context + state) and the procedure+state layers belong in skill files, not in separate agent system prompts. Per `agent-harness-principles`: "Push intelligence UP into skills. Push execution DOWN into deterministic tooling. Keep the harness thin." Skills I execute directly in the main session consume zero subagent quota; spawning a Track 2 session consumes one.

## Alternatives considered

- **10-agent parallel model (the article's strawman).** Rejected — adding agents to a non-bottleneck just burns the rate-limit budget. Verified by 3-day incident.
- **5-agent reduction (Hermes-style fleet consolidation, 2026-06-07 pattern).** Rejected — still wrong variable. Reduces count but doesn't change the bottleneck analysis. Skill-first beats agent-first regardless of agent count.
- **Single Mavis, no Track 2, all work interactive.** Rejected — loses the parallelism between spec and implementation, which is the actual leverage point in the model.
- **Track 2 = a different agent (e.g., a new "implementer" agent).** Rejected — same memory + skills + voice, just split across two system prompts. Adds load-bearing complexity (state divergence, model routing, session tree plumbing) for zero quality gain. Same Mavis, different session_id, same skill library.
- **Keep all current agents (no retirement).** Rejected — the team-of-agents is a 2026-06-04-era model that hasn't produced real work in ~3 weeks. The active workloads (X-Content-Engine cron chain + verifier-only subagent channel) don't need it.

## Expected impact

**New shape:** Mavis = single chief running two tracks. Track 1 (interactive session, current session_id) handles spec work with Andre. Track 2 (separate session_id, spawned on demand with an approved spec) handles implementation autonomously. Skills become the workforce; subagent channel stays verifier-only. X-Content-Engine cron chain (x-researcher, x-scribe) keeps running on its own session tree against a separate rate-limit pool — not affected by this decision.

**Skills affected:**
- New: `two-track-handoff` (the canonical procedure for spec → Track 2 spawn → poll → verify)
- New: rate-limit-budget allocation logic surfaces via the `rate-limit-tracker` cron
- Unchanged: all existing `ea-*` skills, X-Content-Engine skills, FB-Engine skills

**Crons affected:**
- New: `rate-limit-tracker` (writes daily/weekly allocation to `~/.mavis/state/rate-limit-YYYY-MM.md`)
- Unchanged: existing cron chain

**Memory affected:**
- MEMORY.md updates: add "Two-track operating model" entry under Core Identity, retire stale references to "Mavis is the leader of a multi-agent team"
- Topics affected: `ea-contract.md` (scope section), `agent-harness-principles.md` (already aligned), `orchestration-failure-modes.md` (add 3-day incident as new failure mode)

**New failure modes:**
- Track 2 session loses context mid-implementation → mitigate via handoff packet (spec + plan + project pointer + halt conditions on disk)
- Two tracks conflict on shared vault state → mitigate by serializing vault writes through Track 1 (Track 2 reads, only writes to its assigned output path)
- Rate-limit budget overshoot → mitigate via the `rate-limit-tracker` cron surfacing daily allocation

**What gets easier:**
- Andre's attention stays on the spec track where it matters
- Implementation gets full Mavis capability without burning interactive-session budget
- Skill codification becomes the default outcome of recurring workflows (Garry Tan discipline, now structurally enforced)
- "Should I dispatch this?" becomes "should this be a skill?" — fewer decision moments

## What would change my mind

- If a measurement shows spec throughput ≥ 3 specs/week sustained AND verification becomes the new bottleneck (not spec or impl) → consider Track 3 (a dedicated verifier session, narrow scope)
- If MiniMax Code adds per-track rate-limit isolation (so Track 2 doesn't compete with Track 1's budget) → consider lifting the "one implementation session per spec" cap and going multi-Track-2 with explicit budget fences
- If the agent-harness pattern shifts back toward "one specialist agent per domain" (e.g., a coding model with isolated context that genuinely outperforms fat-skill-loaded Mavis) → re-evaluate the specialist-agent carve-out
- If Andre's attention budget grows (e.g., a second operator) → the spec bottleneck partially lifts; Track 1 can parallelize across operators and the model shifts

## Reversal log

None yet. Active decision.
