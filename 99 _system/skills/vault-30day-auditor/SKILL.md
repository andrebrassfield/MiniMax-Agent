---
name: vault-30day-auditor
description: Run a 30-day operational footprint audit on Andre's vault — scan `01 Daily/` and `03 Projects/` for files modified in the last 30 days, extract core topics, repetitive manual tasks, and active project pipelines strictly from file contents and modification frequency, then synthesize a Factual Index report to `03 Projects/Mavis EA Design/reports/30-day-footprint-YYYY-MM-DD.md`. Triggers: "vault 30-day audit", "what am I working on", "footprint report", "30-day audit", "map my activity", "what did I do this month". Hard constraint: do not invent context, do not include projects/topics that are not evidenced by on-disk files. Synthesis is done in-session by Mavis (EA work) — do NOT dispatch the X-Content-Engine `x-researcher` for this; that agent is scoped to X content research, not vault activity audits.
---

# Vault 30-Day Auditor

## What this skill does

Generates a **Factual Index** of Andre's actual operational footprint over the last 30 days. The audit is read-only against the vault filesystem. It produces a single report that maps:

1. **Core topics** — what subjects are showing up repeatedly in daily notes, project files, and inbox captures
2. **Repetitive manual tasks** — workflows Andre is performing by hand that could become a skill or cron
3. **Active project pipelines** — projects with file activity in the 30-day window, ranked by modification frequency

The report is the input for "what's the next bottleneck to automate" — every claim in the report must be traceable to specific on-disk files.

## When to run

**Trigger phrases:**
- "vault 30-day audit" / "run a 30-day audit"
- "what am I working on" / "footprint report"
- "what did I do this month" / "monthly activity"
- "map my activity" / "operational footprint"

**Do NOT run for:**
- A specific single project (just `ls` the project dir, no audit needed)
- Less than 7 days of vault history (the window is too narrow to surface patterns)
- Vault files Andre hasn't touched (the audit measures *modification* frequency, not existence)
- Non-vault data (calendar, email, browser history are out of scope for this skill)

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Vault root | `/Users/brassfieldventuresllc/MiniMax-Agent` | no |
| Target dirs | `01 Daily/` and `03 Projects/` (recursive) | no |
| Window | last 30 days (T-30 → T, where T = today) | no |
| Report path | `03 Projects/Mavis EA Design/reports/30-day-footprint-YYYY-MM-DD.md` | no |
| Top-N projects to read in full | 5 (by modification count) | no |

## Outputs

A single markdown report at `03 Projects/Mavis EA Design/reports/30-day-footprint-YYYY-MM-DD.md`. Structure:

1. **Header** — date, vault root, window, file counts, generation timestamp
2. **Decision log** — any non-obvious choices made during the audit (e.g., path corrections, domain mismatch notes, dual-location decisions)
3. **Daily notes cadence** — which days have notes, which don't, mtime gaps
4. **Active project pipelines** — projects with file activity, ranked by modification count, with the top files listed
5. **Core topics** — recurring subjects extracted from the top files, with the file evidence listed
6. **Repetitive manual tasks** — workflows that show up in 3+ files (daily notes + project files), with the workflow description and evidence
7. **Inbox / hot files** — files in `00 Inbox/` modified in the window (research briefs, decision docs, capture files)
8. **Automation candidates** — derived from the repetitive tasks: which one, if automated, would unblock the most work
9. **Appendix** — full file inventory (path + mtime) for traceability

The report is **descriptive, not prescriptive** — it surfaces what Andre is doing, not what he should do. The "automation candidate" section flags the single most obvious next target but does not draft the skill.

## The Hard Constraints (READ THIS)

1. **No invented context.** Every claim must be traceable to a specific file in the report's appendix. If a project is mentioned in the report, it must appear in the file inventory. If a topic is mentioned, it must come from reading at least one file that contains it.
2. **Disk is ground truth.** Do not pull topics from memory or prior context. Re-read the files in this session.
3. **Mavis synthesizes, not x-researcher.** The audit is EA synthesis work. Dispatching the X-Content-Engine `x-researcher` for this would be a domain mismatch — that agent is scoped to X content research. Do the synthesis in-session. (Per the agent-harness principle: "bad agents don't become good because you connected more tools — vague agents just create vague output faster.")
4. **Mavis territory only.** The audit does not cross into `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/`, or any other agent's tree. Hermes is a separate agent with absolute separation (Andre-locked 2026-06-16).
5. **Quantified claims need verification.** "X projects active" requires `find | wc -l` against the actual files, not an `ls` count. "Daily notes on N days" requires `ls -la` against `01 Daily/`, not a recap.
6. **Window edge cases.** If the vault has no files in the 30-day window (e.g., a fresh vault), halt and surface. If the window is partial (e.g., the vault's oldest file is 12 days old), note the actual coverage in the header.

## Procedure

### Step 1: Verify ground truth

Confirm the vault root and target dirs exist:

```bash
ls "/Users/brassfieldventuresllc/MiniMax-Agent/01 Daily/"
ls "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/"
```

If either is missing, halt and surface. The audit cannot proceed without these target dirs.

### Step 2: Establish the 30-day window

Get today's date and compute T-30:

```bash
date "+%Y-%m-%d"  # T
date -v-30d "+%Y-%m-%d"  # T-30 (macOS)
```

The window is `[T-30, T]` inclusive. Record both in the report header.

### Step 3: Inventory files modified in the window

Run `find` with `-mtime -30` against the target dirs:

```bash
find "/Users/brassfieldventuresllc/MiniMax-Agent/01 Daily" -type f -mtime -30
find "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects" -type f -mtime -30
```

Capture the full output. The line count and the file list are the basis for every claim in the report.

Also pull `00 Inbox/` (out of target scope but operationally important):

```bash
find "/Users/brassfieldventuresllc/MiniMax-Agent/00 Inbox" -type f -mtime -30
```

### Step 4: Project ranking

Count modifications per project dir:

```bash
find "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects" -type f -mtime -30 \
  | sed 's|/[^/]*$||' \
  | sort | uniq -c | sort -rn
```

This gives a ranked list of active projects. The top 5 (by count) are the "active pipelines" — read their top files in Step 5.

### Step 5: Read the top files

For each of the top-N projects and for the daily notes:

- Read the most-recently-modified file in full (to extract topics)
- Read 1-2 more if the topics are ambiguous

Use `Read` tool with offset/limit for large files; do not skip large files just because they're long — chunked reads are fine.

Topics are extracted from file **content**, not file name. A file called "research-brief.md" with content about "M3 eval lab" gets categorized under M3 eval lab, not research.

### Step 6: Daily notes cadence

From the `01 Daily/` inventory, list:

- Which dates have a note
- Which dates are missing
- The longest gap between notes
- The most recent note's mtime (vs today)

This surfaces the daily-notes habit's health. A 6-day gap at the end of the window is a finding.

### Step 7: Synthesize

In-session synthesis. Three sections:

1. **Core topics** — subjects that appear in 2+ files across the window. Examples: "X content engine", "Mavis role design", "fleet architecture", "agent disease model", "skill codification". List each topic with the files it appears in.
2. **Repetitive manual tasks** — workflows that show up in 3+ files (often phrased as "I need to..." or "the workflow is..." in daily notes and project READMEs). Examples from prior runs: "ledger append", "skill codification", "weekly review".
3. **Active pipelines** — projects with file activity, ranked by modification count. The top 5 are the most active.

The synthesis must be **defensible**: every claim has a file reference in the appendix.

### Step 8: Write the report

Create `03 Projects/Mavis EA Design/reports/30-day-footprint-YYYY-MM-DD.md` (create the `reports/` dir if missing):

```bash
mkdir -p "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Mavis EA Design/reports"
```

Use the `Write` tool. Follow the Output structure above. The report is one file, one session's worth of synthesis — do not append to a prior report.

### Step 9: Return summary to operator

Send a short summary:

- Report path
- Total files in window
- Top 3 active projects
- Top 3 core topics
- The single most-obvious automation candidate
- Any halt conditions or window edge cases

## The Data Schema (the report)

```markdown
---
generated: YYYY-MM-DD HH:MM CT
window: [T-30, T]
vault_root: /Users/brassfieldventuresllc/MiniMax-Agent
files_in_window: <integer>
target_dirs: ["01 Daily/", "03 Projects/"]
generator: Mavis (EA, in-session synthesis)
---

# 30-Day Operational Footprint

## Decision log
- <non-obvious choices made during the audit>

## Daily notes cadence
- Days with notes: <list>
- Days missing: <list>
- Longest gap: <N days, between X and Y>
- Most recent note: <date> (N days ago)

## Active project pipelines (top 5 by modification count)
1. **<project name>** — <N> files modified
   - <top files>
2. ...

## Core topics (subjects in 2+ files)
1. **<topic>** — files: <list>
2. ...

## Repetitive manual tasks (workflows in 3+ files)
1. **<task>** — evidence: <file references>
2. ...

## Inbox / hot files
- <file>: <one-line summary>

## Automation candidates
- **<task>** — highest-leverage automation target based on repetition count + manual effort. Skill to consider: <name>.

## Appendix: full file inventory
| Path | mtime | size |
|------|-------|------|
| ... | ... | ... |
```

## The Safety Halts

1. **Vault root not found.** Halt. The skill depends on the canonical vault path.
2. **Target dirs missing.** Halt. The audit cannot proceed without `01 Daily/` and `03 Projects/`.
3. **Zero files in window.** Halt. The audit assumes there's something to audit; if the vault is empty or stale, surface the staleness.
4. **Domain mismatch detected.** If during the audit it becomes clear that the synthesis requires reading another agent's tree (Hermes, OpenClaw, etc.), halt and surface. The audit is Mavis-internal.
5. **Path correction required.** If the operator specified a path that doesn't exist (e.g., `Mavis-EA-Design` vs the actual `Mavis EA Design`), note the correction in the Decision Log and proceed with the actual path. Do not silently invent files.
6. **Mass file read budget.** Read at most ~20 files in full during the synthesis. If the top-N projects have more, sample — do not read the entire vault.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| `find` returns no files | empty output | Halt; surface "no activity in 30-day window" |
| Daily notes dir is empty | `ls` returns nothing | Note "no daily notes"; proceed with project-only audit |
| Top project file is binary or unreadable | `Read` fails | Skip; note in Decision Log |
| `00 Inbox/` mtime is stale (no recent captures) | no files in window | Note "inbox quiet this period"; do not invent activity |
| Vault path moves | `ls` fails on the canonical root | Halt; ask operator for the new path |
| Report dir missing | `mkdir` not run | `mkdir -p` before `Write`; idempotent |

## Verification

After writing the report:

1. `ls -la` confirms the report file exists
2. The report's `files_in_window` matches the `find | wc -l` output from Step 3
3. Every project mentioned in "Active project pipelines" has at least one file in the appendix
4. Every topic mentioned in "Core topics" has at least 2 file references
5. The Decision Log captures the path correction (if any) and the domain-mismatch decision (synthesis in-session, not dispatched)
6. The Appendix is complete (every file in the inventory is listed)

## Cross-reference

- `00 Inbox/` — the raw capture surface; the audit cross-references it
- `01 Daily/` — primary input for daily cadence + topic extraction
- `03 Projects/` — primary input for active pipeline ranking
- `99 _system/dashboards/` — for the report's destination pattern (`reports/` is a project-local convention; dashboards are system-wide)
- Chief-of-staff role contract — the synthesis work this skill performs is core Mavis territory
- Garry Tan's "audit and integration tests, repeat" principle — the audit is an integration test for the vault
