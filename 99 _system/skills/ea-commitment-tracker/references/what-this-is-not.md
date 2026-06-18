# What This Skill Is NOT — ea-commitment-tracker

The negative-space definition. Clarifies what the
commitment ledger ISN'T, so the chief doesn't conflate it
with adjacent artifacts.

## Not a decision log

**Decisions and commitments are different artifacts.** A
decision is a choice ("we're using X for Y"). A commitment
is a promise to act ("I'll have X done by Friday"). Use
`ea-decision-logger` for decisions, this skill for
commitments. The append-only discipline is the same; the
schema is different.

| Artifact | Question it answers | Tool |
|---|---|---|
| Decision | "What did we choose?" | `ea-decision-logger` |
| Commitment | "What did I promise to do?" | this skill |

## Not a project tracker

**Project-level work lives in `03 Projects/<project>/`.**
The commitment ledger is cross-project, for cross-session
promises. A project plan lives with the project; a
commitment is EA-level.

| Surface | Use for |
|---|---|
| `03 Projects/<project>/` | Project plans, todos, deliverables |
| `~/.mavis/agents/mavis/commitments.jsonl` | Cross-session chat promises |
| `02 Notes/commitments/YYYY-MM.md` | Human-readable commitment mirror |

## Not autonomous

**The skill captures Mavis-said commitments.** Mavis is the
beneficiary's agent (Andre's), not the promiser's agent.
Andre's commitments to other people go in a separate file
(`02 Notes/commitments/andre-to-others.md`). The skill does
NOT capture:
- Andre's commitments to third parties
- Third-party commitments mentioned in passing
- Commitments in other agents' trees

## Not exhaustive

**One-shot operational promises are excluded.** "I'll run
that command now" or "let me check that" — if it completes
in the same turn, no ledger entry. The ledger is for
cross-session promises with a deliverable and (usually) a
due date.

| Promise | Captured? |
|---|---|
| "I'll have X by Friday" (cross-session) | yes |
| "I'll run that command now" (same turn) | no |
| "Let me check that" (same turn) | no |
| "I'll come back to that tomorrow" (next session) | yes |
| "I'll think about it" (no deliverable) | no |

## Not the kanban

**The kanban (`mavis team plan` / `mavis kanban`) is for
dispatched tasks with workers.** The ledger is for chat
promises that don't have a worker yet. A commitment might
later be dispatched to a worker (and end up on the kanban),
but the ledger entry is the chat-promise artifact, not the
task-tracking artifact.

| Tool | Use for |
|---|---|
| Kanban | Dispatched tasks with workers (`mavis team plan`) |
| Commitment ledger | Chat promises, not yet dispatched |
| Project plan (`03 Projects/<project>/`) | Project-level work, owned by the project |

## The 3 negative-space rules

1. **Decisions ≠ commitments.** Use `ea-decision-logger`
   for decisions.
2. **Project work ≠ chat promises.** Use
   `03 Projects/<project>/` for project-level work.
3. **Andre's commitments to others ≠ Mavis's commitments
   to Andre.** Use `02 Notes/commitments/andre-to-others.md`
   for Andre's commitments.

If the chief is unsure which artifact a promise belongs
to, ask: "Is this a choice (decision) or a promise to act
(commitment)? Is it cross-session (ledger) or
single-session (no ledger)? Is it Mavis's promise (this
ledger) or Andre's promise (separate file)?"
