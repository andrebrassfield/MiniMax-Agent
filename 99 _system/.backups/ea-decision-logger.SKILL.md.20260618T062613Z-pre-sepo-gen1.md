---
name: ea-decision-logger
description: |
  Codifies the capture of architectural decisions that happen in chat but
  should live on disk. The procedure: (1) detect decision points in the
  current conversation or in a Mavis session (the marker phrases are "let's
  do X", "we're going with Y", "the decision is Z", "ship it", "approved",
  and any time Andre reverses a prior position); (2) extract the 5 fields —
  decision, rationale, alternatives considered, expected impact, "what would
  change my mind" — and the date, the conversation pointer, and any related
  surfaces; (3) write to `02 Notes/decisions/YYYY-MM-DD-<slug>.md` with a
  stable filename (slug is 2-4 words, lowercase, hyphenated); (4) cross-link
  to the related vault surfaces (the skill that triggered it, the brief that
  informed it, the cron that depends on it); (5) surface on the next daily
  brief so Andre can verify the capture. The discipline: decisions-in-chat
  vanish within 2 weeks. Decisions-on-disk survive the EA's context window,
  future-Mavis's re-litigation, and the next vault rebuild. Use this skill
  when an architectural decision is made in the current session, when Mavis
  is about to take a destructive or hard-to-reverse action, when Andre
  explicitly says "log this decision" or "record that", and as a self-trigger
  on the EA workflow `/log-decision`. Do NOT load for trivial operational
  decisions (cron schedule, file path), for decisions that are already docu-
  mented in a MAVIS.md / SOUL.md / topic file, or for decisions that belong
  to another agent's tree.

# === TPG (Cognitive Parameter Graph) layer - added 2026-06-17 ===
# Phase 1 codification: schema-only, no SePO loop running yet.
# Phase 2 will populate fitness_score, last_evaluated, etc. via sepo-runner.
node_type: agent_parameter
parameter_id: ea-decision-logger
generation: 1
fitness_score: null
last_optimized: null
last_evaluated: 2026-06-18T04:43:49.879229Z
mutation_count: 0
schema_version: 1
---

# ea-decision-logger

The capture of architectural decisions — the kind of
choice that affects how the system works for the next 6+
months, costs >2 hours to reverse, or shapes how future-
Mavis reasons about the vault. Chat is ephemeral; disk is
durable. Every load-bearing decision needs both.

## When to run

**Trigger phrases (Mavis-side, in the current session):**
- Andre says "let's do X" / "we're going with Y" / "the
  decision is Z"
- Andre says "ship it" / "approved" / "do it" / "go" (in
  the context of a prior alternative-options discussion)
- Andre reverses a prior position ("actually, scratch
  that, let's go with...")
- Mavis is about to take a destructive / hard-to-reverse
  action (cron schedule change, skill deletion, memory
  purge, deployment)
- Andre explicitly says "log this decision" / "record
  that" / "make sure we remember"

**Auto-trigger conditions (load the skill when):**
- The current conversation contains an architectural
  choice with ≥2 alternatives that were explicitly
  considered
- The choice affects the EA workflow contract
  (`ea-contract.md`), a load-bearing skill, a cron, or
  the memory schema
- Reversing the choice would cost >2 hours or break
  existing automation

**Do NOT load for:**
- Trivial operational decisions (cron minute adjustments,
  file rename, single-file edit)
- Decisions already documented in `MAVIS.md` / `SOUL.md` /
  `ea-contract.md` / a topic file (cross-link instead of
  duplicate)
- Decisions that belong to another agent's tree (Hermes
  architecture, OpenClaw work, Socratic — file an
  incident card for the peer team, do not log as Mavis's
  decision)
- Tactical pivots that are <2 hours of work to reverse
  (note in the daily note, not a decisions/ file)

## The 5-field schema (the load-bearing structure)

Every decision gets these 5 fields. **None are
optional** — the format forces rigor. If you can't fill in
a field, the decision isn't fully baked yet (escalate to
Andre). Full field definitions + capture rules in
`references/5-field-schema.md`.

| Field | What it captures | Format |
|---|---|---|
| **Decision** | The choice that was made | One sentence, past tense, definitive |
| **Rationale** | Why this choice over the alternatives | 2-4 sentences, EA voice, citing the brief/research that informed it |
| **Alternatives considered** | The other options that were on the table | Bulleted list, 2-5 options, each with 1-line why-rejected |
| **Expected impact** | What this decision enables / prevents / changes | 2-4 sentences, concrete effects on skills / crons / memory / workflows |
| **What would change my mind** | Conditions under which this decision should be revisited | 2-3 sentences, specific triggers (measurement, benchmark, scale threshold) — NOT "if I learn more" |

**Optional fields** (capture when available):
- **Date** (auto: today's date)
- **Conversation pointer** (session ID or chat reference)
- **Decider** (Andre, Mavis-with-approval, Mavis-
  autonomous — be honest about the autonomy level)
- **Reversibility** (fully reversible / partially
  reversible / hard to reverse)

## The 5-step procedure (overview)

The full procedure with bash commands in
`references/procedure.md`. The high-level flow:

1. **DETECT** — catch the decision point mid-session
   (direct markers: "let's go with X"; indirect markers:
   back-and-forth with ≥2 alternatives; reversal markers:
   "actually scratch that")
2. **EXTRACT** — fill the 5 fields. Sharpen loose wording.
   Compute the decision's "what would change my mind" —
   vague "if I learn more" is not a trigger
3. **WRITE** — append to `02 Notes/decisions/YYYY-MM-DD-<slug>.md`
   with a stable filename (2-4 words, lowercase,
   hyphenated, captures the decision's essence, not the
   date)
4. **CROSS-LINK** — link to related surfaces (the brief
   that informed it, the skill that depends on it, the
   prior decision this reverses or supersedes)
5. **SURFACE** — include in the next daily brief so
   Andre can verify the capture

## Hard constraints

1. **All 5 fields are required.** If you can't fill in a
   field, the decision isn't fully baked — HALT and
   escalate to Andre. A partial decision file is worse
   than no file (creates a false record of rigor).
2. **Append-only.** New decisions append; reversals are
   new files (do not edit the prior file). The audit
   trail is the value.
3. **Stable filename.** `<YYYY-MM-DD>-<slug>.md`. The slug
   is 2-4 words, lowercase, hyphenated. Captures the
   decision's essence, not the date. Example: `gepa-
   pivot`, not `2026-06-16-decision-1`.
4. **Cross-link to related surfaces.** The decision
   file is not useful in isolation. Link to: the brief
   that informed it, the skill that depends on it, any
   prior decision this reverses or supersedes.
5. **Surface in the daily brief.** The brief is the
   audit hook. If the brief doesn't surface the decision,
   Mavis will never know if the capture is right or
   wrong. Andre's review is the verification step.
6. **Mavis territory only.** Do not log decisions for
   other agents' trees. File an incident card for the
   peer team; let them own the decision log.
7. **Reverse as a new file, not an edit.** Reversals
   create a new decision file with a `reverses:` related
   field. The prior file is not edited.
8. **Consolidate small decisions in the same week.**
   Multiple small decisions on the same theme get one
   file with a "decisions" section, not 4 separate
   files.


## Destructive Operations Pre-Flight

**Trigger:** When the captured decision involves an irreversible action — `delete`, `rm -rf`, `force push`, `reset --hard`, `drop database/table`, `truncate`, `override remote`, or any operation where a failure mode cannot be undone by re-running. This applies whether the action is filesystem-level, git-level, database-level, cloud-level, or system-level.

Before writing the decision file, Mavis MUST execute a 3-step pre-flight checklist and document each step in the decision record's **Expected impact** field. **No destructive decision is logged without all 3 steps documented.**

### Pre-Flight Checklist (mandatory, in order)

**Step 1 — Timestamped tar snapshot of affected directories.** Run `tar` with an ISO-timestamped backup path so the snapshot is identifiable and reversible. The exact backup path MUST be recorded in the decision file's Expected impact field.

```sh
# Example
tar czvf /Users/<user>/.backups/pre-<decision-slug>-<ISO-timestamp>.tar.gz \
  <affected-path-1> <affected-path-2> ...
```

If the affected scope is git-tracked, additionally capture a `git rev-parse HEAD` for the affected repo as a complementary restore anchor.

**Step 2 — Explicit command string dry-run review.** State the exact command(s) that will be executed when the decision is acted on — verbatim, not paraphrased. The dry-run is the act of presenting the command to Andre for explicit review, NOT executing it with a `--dry-run` flag. Andre's review is the gate.

```
# Example: rm -rf /Users/.../production/test-data
# Example: git push --force-with-lease origin feature-branch
# Example: DROP TABLE prod.users;
```

For multi-command destructive chains, list each command separately and explicitly. If any command depends on prior commands' success, document the dependency.

**Step 3 — Documented rollback path.** State the exact steps to reverse the action if it goes wrong. Reference the backup from Step 1 by path. Include verification commands to confirm the rollback succeeded.

```sh
# Example rollback:
rm -rf /Users/.../production/test-data \
  && tar xzvf /Users/.../.backups/pre-<decision-slug>-<ISO-timestamp>.tar.gz -C /
```

If rollback is non-trivial (e.g., requires manual reconciliation, has downtime, or has data loss window), document that explicitly so Andre can decide whether to proceed.

### After Pre-Flight: standard 5-step procedure

Only after all 3 steps are documented AND Andre approves the destructive action does Mavis proceed to log the decision per the standard 5-step procedure above. The pre-flight evidence becomes part of the decision record's Expected impact field, not a separate artifact.

If Andre declines the destructive action, halt and surface alternatives (KEEP, delay, smaller-scope version of the action) — do NOT proceed to log a decision that won't be acted on.

### Cross-references

- **Hard constraints** (above): "Reconfirm before any irreversible action" — this section IS the operationalization of that rule.
- **When the skill HALTs** (below): halt conditions include "Andre declines destructive action during pre-flight."
- **ea-commitment-tracker**: once approved, the destructive action becomes a commitment with the documented rollback path as the contingency.
- **ea-loop-audit Verify stage**: the 3-step checklist IS the verification gate. ea-loop-audit's "Verify" dimension passes when Steps 1-3 are documented.


## When the skill HALTs

Halt and escalate to Andre when:
- Can't fill in all 5 fields (H1) — decision isn't fully
  baked
- Reversal with no prior decision (H2) — this is a new
  decision, not a reversal
- Decision belongs to another agent's tree (H3) — file
  an incident card, don't log as Mavis's
- Decision is trivial operational (H4) — note in daily
  note, not in `decisions/`
- The decision file write fails (H5) — surface

The skill is a diagnostic, not an authorization. The
operator decides the action.

## Anchoring sources

- **`ea-loop-thinking`** — the 5-stage loop; this skill
  lives at the Iterate stage (decisions close loops)
- **`ea-5-mistakes-audit`** — Mistake 4 (stopping at SFT,
  no feedback loops) is precisely what the decision
  logger prevents
- **`ea-skill-evolution`** — consumes the decision log
  as input; when Mavis proposes a skill mutation, "what
  decisions does this contradict" is the first check
- **MEMORY.md "Cross-layer fix verification"** — the
  discipline of capturing decisions at the same layer
  as the action
- **The 2026-06-16 GEPA / loop-engineering pivot** — the
  motivating example for this skill

## Cross-reference

- `references/5-field-schema.md` — full 5-field
  definitions + capture rules + optional fields
- `references/procedure.md` — the 5-step procedure with
  bash commands
- `references/file-template.md` — the decision file
  template (YAML frontmatter + 5 sections + reversal log)
- `references/cross-link-patterns.md` — how to link to
  related surfaces
- `tests/5-field-presence.md` — 5-field sanity check
- `tests/audit-discipline.md` — no-partial, append-
  only, Mavis-territory checks
- `ea-loop-thinking` — the framework
- `ea-5-mistakes-audit` — Mistake 4 cross-check
- `ea-skill-evolution` — consumes the log
