---
name: two-track-handoff
description: |
  Codifies the **two-track handoff** procedure — the canonical way to spawn
  a Track 2 (implementation) Mavis session from a Track 1 (spec) Mavis
  session. Triggered when a spec + implementation plan is approved by Andre
  and implementation work needs to run autonomously in parallel with the
  next spec. The handoff is the bridge between the spec track (interactive,
  high Andre attention) and the implementation track (autonomous, low
  Andre attention). Per the 2026-06-22 two-track-model decision, Track 2
  is a *second Mavis session* (same agent, different session_id) — not a
  different agent.

  Triggers: "hand off to implementation", "spawn the implementation track",
  "two-track handoff", "track 2", "implementation session", "spec approved,
  start building", or when a Mavis session detects a spec → implementation
  transition with explicit user approval.

  Do NOT load for: spawning producer subagents (forbidden — skill it instead),
  spawning verifier subagents (different procedure), spawning X-Content-Engine
  cron sessions (x-researcher/x-scribe handle their own scheduling), spawning
  without an approved spec on disk, or one-line chat replies.
---

# two-track-handoff

The canonical bridge from spec track to implementation track. Produces a handoff packet on disk and spawns one Track 2 Mavis session. No more, no less.

## Intent

When Andre approves a spec + implementation plan, this skill does three things:
1. **Compose the handoff packet** — spec + plan + project pointer + halt conditions + expected output path, written to `~/.mavis/state/handoffs/<handoff-id>.md`
2. **Spawn the Track 2 session** — `mavis session new mavis --from <this-session>` with the handoff packet as the system-prompt seed
3. **Register the handoff** — append to `~/.mavis/state/handoffs/registry.jsonl` (append-only)

The Track 2 session is autonomous. It runs the implementation plan, writes output to the assigned path, and reports back. Track 1 (this session) continues with the next spec.

## When to run

**Triggers:**
- Spec + implementation plan has been approved by Andre in this session
- The work fits the criteria: bounded scope, halt conditions nameable, single implementation session is sufficient
- Implementation work can run in parallel with the next spec work

**Hard pre-conditions (ALL must be true):**
- ✅ Spec is on disk at `03 Projects/<X>/specs/<feature>-YYYY-MM-DD.md`
- ✅ Implementation plan is on disk (either inline in the spec file or separate at `03 Projects/<X>/plans/<feature>-YYYY-MM-DD.md`)
- ✅ Andre has explicitly approved the spec ("go", "ship it", "approved", "implement this", or equivalent)
- ✅ The work fits within one Track 2 session (single-track discipline — Track 3 requires explicit escalation)
- ✅ Output path is identified and writable
- ✅ Rate-limit budget has ≥30% remaining (Track 2 burns ~30% of the budget per the `rate-limit-tracker` allocation)

**Do NOT run for:**
- Producer subagent spawn (forbidden — skill it instead, execute in main session)
- Verifier subagent spawn (use the `verifier` agent directly)
- X-Content-Engine cron session (x-researcher/x-scribe handle their own scheduling via crons)
- Any spawn where the spec is NOT on disk
- One-off ad-hoc work that doesn't need a Track 2 session (just do it in Track 1)
- Cross-team work (Hermes, OpenClaw, gbrain — Mavis↔Hermes ABSOLUTE SEPARATION rule applies)

## The 5-step procedure

### Step 1 — Verify pre-conditions

Before composing the handoff packet, verify all 6 pre-conditions above. If any fails:
- Spec not on disk → HALT, surface "spec must be written to `03 Projects/<X>/specs/` before handoff"
- Implementation plan missing → HALT, surface "implementation plan required"
- Andre approval missing → HALT, surface "Andre must approve the spec before handoff"
- Output path ambiguous → HALT, surface "specify the output path"
- Rate-limit budget low → HALT, surface "rate-limit budget < 30%, defer handoff"
- Multi-track scope detected → HALT, surface "this work needs >1 Track 2 session — requires explicit Andre approval for Track 3"

### Step 2 — Compose the handoff packet

Write to `~/.mavis/state/handoffs/<handoff-id>.md`. The `handoff-id` is `<ISO-timestamp>-<short-slug>` (e.g., `2026-06-22T20-42-CT-fb-poster-v2`).

Required sections:
1. **Spec pointer** — absolute path to the spec file
2. **Implementation plan** — either inlined or absolute path to the plan file
3. **Project context** — which `03 Projects/<X>/` directory, brief description
4. **Expected output path** — where Track 2 writes the deliverable (absolute path)
5. **Halt conditions** — specific conditions that trigger Track 2 to HALT and report back instead of continuing
6. **Verification gate** — what Track 1 (this session) will check when Track 2 reports completion
7. **Stop condition** — what tells Track 2 the loop is done (token budget, time budget, condition met, specific output produced)
8. **Rate-limit budget** — Track 2's allocated ceiling (default: 30% of remaining)

Use this template:

```markdown
---
handoff_id: <ISO-timestamp>-<short-slug>
track: 2
source_session: <this-session-id>
created_at: <ISO-timestamp>
status: open | claimed | completed | failed | halted
---

# Track 2 Handoff — <feature name>

> Spec: <absolute path to spec>
> Plan: <absolute path to plan, or "inline below">
> Output: <absolute path to expected deliverable>

## Project context

<2-3 sentences: what this is, why it matters, where it lives in the vault>

## Implementation plan

<inline if not in a separate file>

## Halt conditions

HALT and report back to <source_session> if:
- Spec ambiguity detected (can't proceed without clarification)
- Output path conflict (existing file would be overwritten without approval)
- Verifier-side audit failure (the deliverable fails its own self-audit)
- Rate-limit budget exhausted mid-task
- External dependency blocked (network, MCP, credential)
- Scope expansion detected (the work is bigger than the plan covers)

## Verification gate

When Track 2 reports completion, Track 1 verifies:
- <specific check 1>
- <specific check 2>
- <specific check 3>

## Stop condition

Track 2 stops when:
- <output file exists at expected path AND passes self-audit>, OR
- <halt condition triggered>, OR
- <rate-limit budget reaches 0>
```

### Step 3 — Spawn the Track 2 session

```bash
mavis session new mavis --from <this-session-id> \
  --prompt "You are Track 2 implementation for handoff <handoff-id>. Read the handoff packet at ~/.mavis/state/handoffs/<handoff-id>.md first. Execute the implementation plan autonomously. Report back to <source_session> on completion or halt." \
  --model minimax/MiniMax-M2.7  # default; use M3 only if Track 1 specifies
```

**Model routing default:** M2.7 for Track 2 (cost discipline). Use M3 only when:
- The implementation work is design-critical (UI/UX, novel algorithm)
- Andre specifies M3 explicitly
- The verification gate requires reasoning depth M2.7 can't reach

### Step 4 — Register the handoff

Append to `~/.mavis/state/handoffs/registry.jsonl` (one JSON object per line, append-only):

```json
{"handoff_id":"<id>","track":2,"source_session":"<this-session-id>","track2_session":"<new-session-id>","created_at":"<ISO>","status":"open","spec_path":"<path>","output_path":"<path>"}
```

### Step 5 — Confirm handoff + next step

Surface to Andre:
- "Track 2 handoff registered: `<handoff-id>`. Track 2 session: `<track2-session-id>`. The implementation runs autonomously. I'll continue with the next spec — surface the verification gate when Track 2 reports back."

Do NOT page Andre with progress updates mid-implementation. Track 2 reports back on completion or halt only.

## Hard constraints

1. **One Track 2 per handoff.** No spawning Track 3 from within Track 2. Two tracks is the cap.
2. **Spec must be on disk before handoff.** Chat is not the source of truth. If the spec isn't written, the handoff blocks.
3. **Track 2 reads, Track 1 writes (for shared state).** Track 2 can read any vault file but only writes to its assigned output path. Vault structural changes go through Track 1.
4. **Append-only registry.** The handoff registry is append-only. Status updates are NEW lines, not edits. The audit trail is the value.
5. **No producer subagent spawn.** Track 2 is for implementation only. Verifier subagents are the only legitimate subagent spawn — Track 2 can request one via Track 1 if needed.
6. **Mavis territory only.** No handoff to other agents' filesystem territory (Hermes, OpenClaw, gbrain). ABSOLUTE SEPARATION rule applies.
7. **Halt conditions are mandatory.** Every handoff packet must have at least 3 halt conditions. If you can't name 3, the spec isn't ready.
8. **Rate-limit budget is enforced.** If `rate-limit-tracker` reports <30% remaining, handoff is blocked.

## Cross-reference

- `references/handoff-packet-template.md` — the full handoff packet template with field definitions
- `references/registry-schema.md` — the `registry.jsonl` schema and query patterns
- `tests/halt-discipline.md` — verifying halt conditions are concrete and triggerable
- `tests/no-track3-escape.md` — ensuring Track 2 doesn't spawn Track 3
- `tests/spec-on-disk.md` — verifying the spec is on disk before handoff
- `~/.mavis/agents/mavis/crons/rate-limit-tracker.md` — the budget gate
- `~/.mavis/agents/mavis/memory/MEMORY.md` — Two-Track Operating Model entry (2026-06-22)
- `02 Notes/decisions/2026-06-22-two-track-model.md` — the source decision

## Failure modes + recovery

| Failure | Detection | Recovery |
|---|---|---|
| Track 2 session never starts (daemon error) | `mavis session list` doesn't show new session within 30s | Re-spawn with same handoff packet; if still failing, surface to Andre |
| Track 2 halts without reporting back | Registry shows `status: open` for >expected duration | Read Track 2 session log via `mavis session view <id>`; decide whether to re-spawn or surface |
| Track 2 produces wrong output | Verification gate fails | Move output to `~/.mavis/state/handoffs/failed/<handoff-id>/` with failure note; surface to Andre |
| Rate-limit budget exhausted mid-Track-2 | `rate-limit-tracker` reports 0 remaining | Track 2 must save state to its output path and HALT; Track 1 resumes next cycle |
| Spec ambiguity surfaces mid-implementation | Track 2 hits halt condition #1 | Track 2 writes ambiguity note to output path; Track 1 surfaces to Andre |
