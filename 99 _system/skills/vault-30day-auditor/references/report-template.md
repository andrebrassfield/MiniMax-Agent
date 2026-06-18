# Report Template — vault-30day-auditor

The 9-section report template. The audit produces this
report at `03 Projects/Mavis EA Design/reports/30-day-footprint-YYYY-MM-DD.md`.

## Full template

```markdown
---
generated: YYYY-MM-DD HH:MM CT
window: [T-30, T]
vault_root: /Users/brassfieldventuresllc/MiniMax-Agent
files_in_window: <integer>
target_dirs: ["01 Daily/", "03 Projects/"]
generator: Mavis (chief-of-staff, in-session synthesis)
---

# 30-Day Operational Footprint

## 1. Header

- **Generated:** YYYY-MM-DD HH:MM CT
- **Window:** [T-30, T] (30 days)
- **Vault root:** /Users/brassfieldventuresllc/MiniMax-Agent
- **Files in window:** <integer> (01 Daily: <N>, 03 Projects: <N>)
- **00 Inbox (out of scope but cross-referenced):** <integer>
- **Generator:** Mavis (chief-of-staff, in-session synthesis)

## 2. Decision log

- <non-obvious choices made during the audit>
- (none) if no decisions were non-obvious

## 3. Daily notes cadence

- **Days with notes:** <list>
- **Days missing:** <list>
- **Longest gap:** <N days, between X and Y>
- **Most recent note:** <date> (N days ago)

## 4. Active project pipelines (top 5 by modification count)

1. **<project name>** — <N> files modified
   - <top files>
2. **<project name>** — <N> files modified
   - <top files>
3. ...

## 5. Core topics (subjects in 2+ files)

1. **<topic>** — files: <list>
2. **<topic>** — files: <list>
3. ...

## 6. Repetitive manual tasks (workflows in 3+ files)

1. **<task>** — evidence: <file references>
2. ...

## 7. Inbox / hot files

- <file>: <one-line summary>
- <file>: <one-line summary>

## 8. Automation candidates

- **<task>** — highest-leverage automation target based on
  repetition count + manual effort. Skill to consider:
  <name>.

## 9. Appendix: full file inventory

| Path | mtime | size |
|------|-------|------|
| <path> | <mtime> | <size> |
| ... | ... | ... |
```

## Field shapes (the deterministic layer)

**Header fields:**
- `generated`: ISO 8601 with timezone (`YYYY-MM-DD HH:MM CT`)
- `window`: ISO 8601 range `[T-30, T]`
- `vault_root`: absolute path
- `files_in_window`: integer
- `target_dirs`: array of strings
- `generator`: literal string (audit provenance)

**Decision log entries:** one bullet per non-obvious choice.
Common entries: path corrections, window partial, domain
mismatch decisions, read budget hits.

**Daily notes cadence:** dates as `YYYY-MM-DD` strings. Gap
in days, between dates.

**Active project pipelines:** ranked list (1-N), each with
the project name, file count, and top 3-5 files.

**Core topics:** ranked list (1-N), each topic with the
files it appears in. A topic must appear in 2+ files.

**Repetitive manual tasks:** ranked list (1-N), each task
with the file references that evidence it. A task must
appear in 3+ files.

**Inbox / hot files:** list of `00 Inbox/` files modified
in the window, each with a one-line summary.

**Automation candidates:** the single most-obvious next
target. Identifies the workflow + a skill to consider
crafting.

**Appendix:** every file in the inventory, with path +
mtime + size. Completeness is the discipline.

## What goes in vs out

**In the report:**
- All claims with file evidence
- Counts and rankings derived from `find | wc -l`
- Topics extracted from file content (not filenames)
- Tasks surfaced from 3+ file references
- The single most-obvious automation candidate

**Out of the report:**
- Inferred activity (no file evidence)
- Recap from prior sessions
- Topics that exist in 1 file only
- Tasks that exist in 2 files only
- Multiple automation candidates (pick the one)
- Andre's commitments to other people (separate ledger)
- Other agents' tree activity (Mavis territory rule)

## The "descriptive, not prescriptive" rule

The report surfaces what Andre is doing, not what he
should do. The "automation candidate" section flags the
single most obvious next target but does not draft the
skill. The EA does the synthesis; Andre decides the
action.
