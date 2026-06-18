---
name: session-lesson-extractor
description: |
  Tool that scans Mavis's recent state surfaces (last 7-30 days of `01 Daily/`, kanban tickets, recent memory edits, recent skill creations, recent worker dispatches) and extracts candidate memory entries — the patterns, corrections, and rules that emerged but haven't yet been codified into `MEMORY.md` or a topic file. This is the MEMORY building block from the loop-engineering framework in action: the loop never forgets between runs, but only if something on disk is updating the corpus. The extractor is the write-back. Triggers on session end (cron), on "what did I learn this week", on "extract the lessons", and on the EA weekly reflection. Outputs a markdown brief to `03 Projects/Mavis EA Design/reports/lesson-extract-YYYY-MM-DD.md` with: (1) candidate entries ranked by recurrence, (2) disk evidence for each, (3) suggested memory slot (MEMORY.md or topic file), (4) a "discard with reason" list for candidates that look like patterns but aren't durable lessons. Mavis reviews and commits. The script is the suggestion engine; the EA is the gate. Do NOT load for one-off sessions with no notable corrections, or when the corpus is already up to date.
---

# Session Lesson Extractor — The MEMORY Building Block in Action

## What this skill does

You scan Mavis's recent state surfaces for **patterns that emerged but haven't been codified**. The output is a brief of candidate memory entries. The chief (Mavis) reviews and decides what to commit.

This is the **MEMORY building block** from the loop-engineering framework (see `ea-loop-thinking`). Loops that don't write back to memory are loops that re-derive everything from zero on the next run. The lesson extractor is the write-back.

**The frame:** the @sairahul1 article says "data quality > architecture" — and the Mavis analog is that the corpus (memory + skills + vault) IS the data. The corpus only stays valuable if it gets updated with new lessons. This tool is the update mechanism.

## When to run

**Trigger phrases:**
- "what did I learn this week" / "extract the lessons"
- "the corpus is getting stale" / "I keep correcting the same thing"
- Weekly cadence (recommended: Sunday evening, before the weekly-connections workflow)
- After a major project transition
- After a series of corrections (3+ "stop doing X" directives in a week)

**Do NOT run for:**
- One-off sessions with no notable corrections
- When the corpus is already up to date (run `ea-data-quality-audit` first to check)
- Less than 7 days of vault history

## What the extractor looks for

The script scans 5 surfaces and looks for 4 pattern types:

### Surfaces scanned

| Surface | What to look for |
|---|---|
| `01 Daily/` (last 7-30 days) | Andre's directives, corrections, "stop doing X", "from now on", "I keep", praise patterns ("good, that worked"), course-corrections |
| Kanban (last 7 days activity) | Recurring ticket types, blockers, closed-then-reopened patterns, Mavis-side failures |
| `~/.mavis/agents/mavis/memory/MEMORY.md` and topic files (last 7 days edits) | What's already in memory (to avoid duplicates) |
| `~/.mavis/agents/mavis/skills/` (last 7 days creations) | New skills (don't extract lessons that are already in a skill) |
| Recent `mavis communication send` dispatches and worker reports (last 7 days) | Worker failure modes, "stalled 2x" patterns, common verifier findings |

### Pattern types (rank-ordered by durability)

#### Type A: Recurring correction (HIGH durability)

Andre has said "stop doing X" or "from now on do Y" 3+ times in the window. This is a durable rule that should be in memory.

**Example:** Andre says "stop giving me problems solve them" 3 times in 2 weeks → candidate: "When in execution flow, default to decide-and-report, not enumerate-and-ask."

#### Type B: Course-correction with generalizable rule (HIGH)

A single instance of a course-correction that contains a generalizable rule. Worth a memory entry if the rule applies beyond the one instance.

**Example:** Andre sends a bare URL, I almost patch without reading → candidate: "Bare URL from Andre = 'go read the spec' — pause, read, then propose."

#### Type C: Recurring worker failure (MEDIUM)

A worker has stalled or failed in a specific way 2+ times. This is a fleet-trust-pattern, not a Mavis memory entry — file it as a candidate for the relevant worker's spec, or for `fleet-trust-patterns.md` topic.

#### Type D: New "X is the state" claim (LOW)

A claim about the current state of the world (e.g., "DeepSeek V4 is the cheapest frontier model"). Low durability because the state moves. These usually belong in the vault, not in memory.

## The output format

The brief is a single markdown file at `03 Projects/Mavis EA Design/reports/lesson-extract-YYYY-MM-DD.md`. Structure:

```markdown
# Lesson Extract: [date range]

**Window:** [start date] → [end date]
**Auditor:** Mavis (EA) — auto-extracted, manual review
**Sources scanned:** [which surfaces were hit]

## HIGH-durability candidates (commit to memory)
1. **[candidate claim]** (Type A, evidence: 3 occurrences)
   - Evidence: 01 Daily/2026-06-07.md L12, 01 Daily/2026-06-09.md L4, 01 Daily/2026-06-12.md L8
   - Suggested slot: MEMORY.md "Post-decision execution mode" section
   - Suggested wording: "[draft one-sentence rule]"
   - **Action:** commit / defer / discard (reason: ___)

2. ...

## MEDIUM-durability candidates (commit to topic file or skill)
1. ...

## LOW-durability candidates (move to vault, not memory)
1. ...

## Discard with reason
- [candidate that looks like a pattern but isn't durable] — reason: ___
- ...

## Stats
- Total candidates: N
- HIGH: N | MEDIUM: N | LOW: N
- Surfaces scanned: N
- Memory slot conflicts: N (candidates that overlap with existing memory)
```

## The procedure (what Mavis does with the brief)

1. **Read the brief.** The extractor surfaces candidates; Mavis judges.
2. **For each HIGH candidate:** decide commit / defer / discard. The decision rule:
   - **Commit** if the rule applies beyond the specific instance AND the corpus doesn't already say this AND Andre hasn't already updated memory
   - **Defer** if the rule is real but the evidence is thin (1-2 occurrences) — wait for one more
   - **Discard** if the rule is a one-off, or already in memory, or contradicted by Andre's other behavior
3. **For each MEDIUM candidate:** route to the right file (a topic file, a skill, the kanban)
4. **For each LOW candidate:** file in the vault, not memory
5. **For each "discard with reason":** read the reason — sometimes the extractor is wrong, sometimes the discard is right
6. **Commit the HIGH candidates to memory.** Use `mavis memory append` for new entries, or Edit/Write for updates/merges. Per memory hygiene: target MEMORY.md ≤10KB, hard ceiling 15KB; topic files MUST have YAML description.
7. **Surface the brief to Andre.** A weekly summary of "what Mavis learned this week" is the right artifact for the EA role.

## The script (the suggestion engine)

The extractor is a Python script at `~/.mavis/agents/mavis/skills/session-lesson-extractor/extract.py`. It:

1. Reads the 5 surfaces via `find` + `grep` + `sqlite3` (for kanban)
2. Tokenizes the content for pattern matching
3. Ranks candidates by recurrence (number of distinct occurrences in the window)
4. Cross-references against current memory to flag duplicates
5. Outputs the brief in the format above

**The script is the suggestion engine; Mavis is the gate.** The script does not write to memory. It produces a brief. Mavis reviews, decides, and commits (or doesn't).

## Hard constraints

1. **The script never writes to memory.** It produces a brief. Memory writes are Mavis's decision, with Andre's approval for non-trivial entries.
2. **Disk is ground truth.** Every candidate must have file:line evidence. No "I think Andre said X" — show the file.
3. **Cross-reference with current memory.** Before surfacing a candidate, check `MEMORY.md` and topic files. Don't surface candidates that are already canon.
4. **Mavis territory only.** Scan `~/.mavis/agents/mavis/`, `~/MiniMax-Agent/`, `~/.mavis/kanban.db`. Do not cross into other agents' trees.
5. **The script is a tool, not a cron.** Running the script on a cron is fine; running the memory writes on a cron is not. Memory writes need Mavis's review.

## Anchoring sources

- MEMORY building block in the loop-engineering framework (`ea-loop-thinking`)
- "Data quality > architecture" — the Mavis analog: corpus > agent definition
- Mavis `MEMORY.md` memory hygiene rules (≤10KB target, 15KB ceiling, topic files must have YAML description)
- "If I have to ask you twice, you failed" — Garry Tan (Andre's user memory) — the discipline that justifies the extractor's existence
