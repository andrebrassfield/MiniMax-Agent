---
name: ea-decision-logger
description: Codifies the capture of architectural decisions that happen in chat but should live on disk. The procedure: (1) detect decision points in the current conversation or in a Mavis session (the marker phrases are "let's do X", "we're going with Y", "the decision is Z", "ship it", "approved", and any time Andre reverses a prior position); (2) extract the 5 fields — decision, rationale, alternatives considered, expected impact, "what would change my mind" — and the date, the conversation pointer, and any related surfaces; (3) write to `02 Notes/decisions/YYYY-MM-DD-<slug>.md` with a stable filename (slug is 2-4 words, lowercase, hyphenated); (4) cross-link to the related vault surfaces (the skill that triggered it, the brief that informed it, the cron that depends on it); (5) surface on the next daily brief so Andre can verify the capture. The discipline: decisions-in-chat vanish within 2 weeks. Decisions-on-disk survive the EA's context window, future-Mavis's re-litigation, and the next vault rebuild. Use this skill when an architectural decision is made in the current session, when Mavis is about to take a destructive or hard-to-reverse action, when Andre explicitly says "log this decision" or "record that", and as a self-trigger on the EA workflow `/log-decision`. Do NOT load for trivial operational decisions (cron schedule, file path), for decisions that are already documented in a MAVIS.md / SOUL.md / topic file, or for decisions that belong to another agent's tree.
---

# EA Decision Logger — Capture Architectural Decisions

## What this skill does

You are codifying the capture of **architectural decisions** — the kind of choice that affects how the system works for the next 6+ months, costs >2 hours to reverse, or shapes how future-Mavis reasons about the vault. The 2026-06-16 loop-engineering / GEPA pivot was a load-bearing decision; right now it lives only in the session log. A future-Mavis would re-litigate it from zero. This skill exists to prevent that.

**The discipline:** chat is ephemeral. Disk is durable. Every load-bearing decision needs both: a one-line confirmation in chat, and a structured file in `02 Notes/decisions/`. The chat is the trigger; the file is the artifact.

## When to run

**Trigger phrases (Mavis-side, in the current session):**
- Andre says "let's do X" / "we're going with Y" / "the decision is Z"
- Andre says "ship it" / "approved" / "do it" / "go" (in the context of a prior alternative-options discussion)
- Andre reverses a prior position ("actually, scratch that, let's go with...")
- Mavis is about to take a destructive / hard-to-reverse action (cron schedule change, skill deletion, memory purge, deployment)
- Andre explicitly says "log this decision" / "record that" / "make sure we remember"

**Auto-trigger conditions (load the skill when):**
- The current conversation contains an architectural choice with ≥2 alternatives that were explicitly considered
- The choice affects the EA workflow contract (`ea-contract.md`), a load-bearing skill, a cron, or the memory schema
- Reversing the choice would cost >2 hours or break existing automation

**Do NOT load for:**
- Trivial operational decisions (cron minute adjustments, file rename, single-file edit)
- Decisions already documented in `MAVIS.md` / `SOUL.md` / `ea-contract.md` / a topic file (cross-link instead of duplicate)
- Decisions that belong to another agent's tree (Hermes architecture, OpenClaw work, Socratic — file an incident card for the peer team, do not log as Mavis's decision)
- Tactical pivots that are <2 hours of work to reverse (note in the daily note, not a decisions/ file)

## The 5-step procedure

### Step 1: Detect the decision point

The decision is in the chat. Mavis's job is to **catch it before the conversation moves on**. Detection markers:

- **Direct markers:** "let's go with X", "we're doing Y", "ship it", "approved", "decision is Z", "log this"
- **Indirect markers:** a back-and-forth where ≥2 alternatives were named and one was chosen ("I think option A is better than B... actually let's try A" → that's a decision)
- **Reversal markers:** "actually scratch that", "I changed my mind", "no wait, let's do it the other way" (log the reversal as a new decision, do not edit the prior decision file — the audit trail is the value)

**Detection failure mode:** Mavis recognizes the decision but doesn't pause to log it. The conversation moves on, the session ends, the decision is lost. **The skill is to be loaded mid-session, not post-hoc.** If you can see the decision happening, load the skill, capture the 5 fields, write the file, then continue the conversation.

### Step 2: Extract the 5 fields

Every decision gets these 5 fields. None are optional. The format forces rigor — if you can't fill in a field, the decision isn't fully baked yet (escalate to Andre).

| Field | What it captures | Format |
|---|---|---|
| **Decision** | The choice that was made, in one sentence | Past tense, definitive. "We are using X for Y." Not "we should consider X." |
| **Rationale** | Why this choice over the alternatives | 2-4 sentences. The synthesis + the why, in EA voice. Cite the brief / research / evidence that informed the decision. |
| **Alternatives considered** | The other options that were on the table | Bulleted list, 2-5 options. Each option: name + 1-line why it was rejected. |
| **Expected impact** | What this decision enables / prevents / changes | 2-4 sentences. Concrete effects: which skills / crons / memory / workflows change, what the new failure modes are, what gets easier. |
| **What would change my mind** | The conditions under which this decision should be revisited | 2-3 sentences. Specific triggers: a measurement, a benchmark, a regulatory change, a scale threshold, a new tool. NOT "if I learn more" — that's not a trigger. |

**Optional fields** (capture when available):
- **Date** (auto: today's date)
- **Conversation pointer** (the session ID or chat reference where the decision was made)
- **Decider** (Andre, Mavis with Andre's approval, Mavis autonomously — be honest about the autonomy level)
- **Reversibility** (fully reversible / partially reversible / hard to reverse)

### Step 3: Write the file

**Path:** `02 Notes/decisions/YYYY-MM-DD-<slug>.md`

**Filename slug rules:**
- 2-4 words, lowercase, hyphenated
- Captures the decision's essence, not the date ("gepa-pivot", "weekly-connections-skill", "loop-engineering-frame", "5-mistakes-audit-addition-11")
- Date in YYYY-MM-DD prefix
- Example: `2026-06-16-gepa-pivot.md`

**File template:**

```markdown
---
date: YYYY-MM-DD
type: architectural-decision
status: active | superseded | reversed
decider: Andre | Mavis-with-approval | Mavis-autonomous
reversibility: full | partial | hard
conversation: <session-id or chat pointer>
related:
  - <path to the brief / research that informed it>
  - <path to the skill / cron / memory that depends on it>
  - <path to any prior decision this reverses or supersedes>
---

# Decision: <one-sentence decision>

> Captured <YYYY-MM-DD HH:MM CT> by Mavis (EA) from <conversation pointer>.

## Decision

<one sentence, past tense, definitive>

## Rationale

<2-4 sentences, EA voice>

## Alternatives considered

- **<option name>** — <1-line why rejected>
- **<option name>** — <1-line why rejected>
- **<option name>** — <1-line why rejected>

## Expected impact

<2-4 sentences>

## What would change my mind

<2-3 sentences, specific triggers>

## Reversal log

<if this decision is later reversed, append the reversal here with date + new decision link. The prior file is not edited — the audit trail is the value.>
```

### Step 4: Cross-link to related surfaces

The decision file is not useful in isolation. Mavis must cross-link to the surfaces that:

- **Informed the decision** — the brief, research, or analysis that produced the evidence (e.g., the `03 Projects/Mavis EA Design/reports/loop-engineering-framework.md` that justified the GEPA pivot)
- **Depend on the decision** — the skill, cron, memory, or workflow that this decision enables or constrains (e.g., `99 _system/skills/ea-skill-evolution/SKILL.md` depends on the GEPA decision)
- **Preceded the decision** — any prior decision that this one reverses, supersedes, or builds on

Use the `related:` YAML field for paths. The Obsidian wikilink convention `[[path]]` also works for the body text.

### Step 5: Surface in the daily brief

The next daily brief (or the `ea-weekly-connections` if the decision is large) gets a one-line entry: "<YYYY-MM-DD> — Decision logged: <one-sentence decision> (<slug>)". Andre can click through to the file.

**Discipline:** the daily brief is the audit hook. If the brief doesn't surface the decision, Mavis will never know if the capture is right or wrong. Andre's review is the verification step.

## Output schema

The file at `02 Notes/decisions/YYYY-MM-DD-<slug>.md` follows the template in Step 3. Total: YAML frontmatter + decision + rationale + alternatives + impact + what-would-change-my-mind + reversal log.

## Halt conditions

- **Can't fill in all 5 fields → HALT, escalate to Andre.** The decision isn't fully baked. Don't write a partial decision file — that's worse than no file (creates a false record of rigor).
- **Reversal with no prior decision → HALT, this is a new decision, not a reversal.** Write the new decision with the `reverses:` related field pointing at the prior file.
- **Decision belongs to another agent's tree → HALT, file an incident card or escalate.** Do not log peer-team decisions as Mavis's.
- **Decision is trivial operational → do not log, note in daily note instead.** The decisions/ folder is for architectural choices, not cron minute adjustments.
- **Duplicate decision in the same week → consolidate.** Multiple small decisions on the same theme get one file with a "decisions" section, not 4 separate files. Example: 4 ea-* skills built in one session → one decision file "Tier 1 ea-* bundle built 2026-06-16", not 4.

## Anchoring sources

- **`ea-loop-thinking`** — the 5-stage loop; this skill lives at the Iterate stage (decisions close loops, that's their function)
- **`ea-5-mistakes-audit`** — Mistake 4 (stopping at SFT, no feedback loops) is precisely what the decision logger prevents: without the log, the system has no learning memory
- **`ea-skill-evolution`** — consumes the decision log as input; when Mavis proposes a skill mutation, "what decisions does this contradict" is the first check
- **MEMORY.md "Cross-layer fix verification"** — the discipline of capturing decisions at the same layer as the action, not letting them drift into adjacent files
- **The 2026-06-16 GEPA / loop-engineering pivot** — the motivating example for this skill. That decision is currently only in this conversation; the next step is to write the decisions/ file and link it.

## What this skill is NOT

- **Not a chat-log dump.** The decision file is structured, not a transcript. The chat is the trigger; the file is the artifact.
- **Not a project journal.** Project journals are in `03 Projects/<project>/`; decisions are cross-project and architectural. Decisions affect how future-Mavis reasons about the vault, not how a specific project progresses.
- **Not a one-line note in the daily.** Daily notes are operational ("shipped skill X", "fixed bug Y"). Decisions are architectural ("chose framework X over Y because Z"). The threshold is reversibility + scope.
- **Not a substitute for the daily brief.** The daily brief surfaces the decision; the decisions/ file is the source of truth. The two are different artifacts.
- **Not a peer-team decision log.** Decisions in Hermes's tree, OpenClaw's tree, etc. are NOT logged in Mavis's `02 Notes/decisions/`. File an incident card for the peer team; let them own the decision log.
- **Not retroactive.** This skill is for *current* and *forward* decisions. Backfilling old decisions is a different task (and requires more rigor — don't backfill without Andre's explicit request).
