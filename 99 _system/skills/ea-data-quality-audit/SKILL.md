---
name: ea-data-quality-audit
description: Operational skill that audits Mavis's own "training data" (memory entries, skill files, vault files, kanban state) using the LLM data-cleaning framework: (1) extract clean content from raw state, (2) filter noise / harmful / off-topic, (3) deduplicate by entry / topic / line, (4) quality-score entries (is this still load-bearing, or stale?), (5) balance the mix (memory vs topic files vs skills vs kanban). The "data quality > architecture" insight from the LLM-training article applies directly to Mavis: the agent's memory + skill corpus IS the data, and the ceiling on output quality is the ceiling on the corpus. Triggers when Andre says "audit my data", "clean the memory", "is the vault fresh", "what's in the skill library", or as a recurring monthly check. Pairs with `ea-5-mistakes-audit` (Mistake 2: treating data as commodity) and `vault-30day-auditor` (the modification-frequency surface). Do NOT load for ad-hoc memory entries, for other agents' trees (Mavis territory only), or for less than 7 days of vault history (the window is too narrow to surface patterns).
---

# EA Data Quality Audit — Memory + Skills + Vault + Kanban as Training Data

## What this skill does

You audit Mavis's own data corpus — the inputs that drive every Mavis output — using the LLM data-cleaning framework from the @sairahul1 article, adapted to the Mavis surfaces. The 5 sub-steps (extract / filter / dedupe / quality-score / balance) are the analog of the 6-step cleaning pipeline the article describes for raw web text.

**The frame:** the article says "data quality beats data quantity, every time. The most guarded secret in the field is not the architecture. It's how the data was cleaned." The Mavis analog is: the skill library, memory corpus, vault, and kanban are the data. Architecture (Mavis's role definition, the dispatch taxonomy, the loop vocabulary) is one paragraph. The corpus is where Mavis wins or loses.

## When to run

**Trigger phrases:**
- "audit my data" / "clean the memory" / "is the vault fresh"
- "what's in the skill library" / "are the skills still load-bearing"
- "I think the corpus has gone stale"
- Monthly cadence (recommended: first Sunday of the month, after `vault-30day-auditor`)

**Pairing triggers:**
- After `ea-5-mistakes-audit` flags Mistake 2 (treating data as commodity)
- After `vault-30day-auditor` surfaces a stale or saturated work surface
- After a major project transition (clean the old project's residue)

**Do NOT run for:**
- Ad-hoc memory entries (single entry, not corpus)
- Other agents' trees (Mavis territory only — `~/.mavis/agents/mavis/` and `~/MiniMax-Agent/`)
- Less than 7 days of vault history
- Active in-flight work (the audit is read-only against the corpus, but the corpus should be quiet)

## The 5 sub-steps (load-bearing, in order)

### Sub-step 1: Extract clean content from raw state

**Purpose:** inventory the corpus, in canonical form.

**What to inventory:**

| Surface | Path | What to extract |
|---|---|---|
| Memory (canonical) | `~/.mavis/agents/mavis/memory/MEMORY.md` | Full file, line count, topic file references |
| Memory (topic files) | `~/.mavis/agents/mavis/memory/*.md` | Each file's first H1, description, size |
| Skills (agent home, canonical) | `~/.mavis/agents/mavis/skills/*/SKILL.md` | Skill name, description, line count |
| Skills (vault mirror) | `~/MiniMax-Agent/99 _system/skills/*/SKILL.md` | Cross-check vs agent home (must be in sync per X-Content-Engine rule) |
| Vault | `~/MiniMax-Agent/01 Daily/`, `02 Notes/`, `03 Projects/` | Modified in last 30 days |
| Kanban | `~/.mavis/kanban.db` (sqlite) | Open tickets, closed tickets, last 30 days activity |

**Output:** a single inventory table with file path, size, last modified, and a one-line "what's in it" tag.

### Sub-step 2: Filter noise / harmful / off-topic

**Purpose:** remove what's actively polluting the corpus.

**Filter criteria:**
- **Harmful:** any memory entry that instructs a behavior Andre has explicitly corrected (check `01 Daily/` for course-corrections; if a memory entry says one thing and Andre's later notes say another, the memory is noise)
- **Off-topic:** topic files in MEMORY.md/ that haven't been read or written in 60+ days (use `find -atime +60` and `find -mtime +60`)
- **Personal data:** PII, credentials, API keys in memory or skill files (rare but possible — check the corpus)
- **Stale claims:** any "X is the state as of <date>" claim where <date> is > 30 days old and the state has likely moved (e.g., "X is launching next week" from 3 weeks ago)
- **Duplicates with drift:** same fact in 3+ places with slightly different wording (the corpus is whispering the same thing in different voices — pick the canonical version and delete the rest)

**Output:** a deletion/rewrite list with file:line references and the reason for the filter.

### Sub-step 3: Deduplicate

**Purpose:** remove redundant copies so the canonical version is the only version.

**Dedup levels:**
- **By file:** same content in two files (e.g., a memory entry in `MEMORY.md` and a topic file). Pick one, link from the other.
- **By topic:** 3+ entries making the same point. Synthesize into one canonical entry.
- **By line:** repeated phrases in the same file (e.g., a "we always do X" line in 5 skills — pick one as the home, link from the rest).

**Tools:**
- `find ~/.mavis/agents/mavis/memory -type f -name "*.md" | xargs grep -l "<key phrase>"` to find candidates
- `diff <file1> <file2>` to identify drift between copies
- Read with intent: are these two entries really the same claim, or two facets of the same claim that both belong?

**Output:** a dedup map — for each duplicated claim, name the canonical file and the links to update.

### Sub-step 4: Quality-score

**Purpose:** for each remaining entry, score its quality on a 4-point scale.

**Score rubric:**

| Score | Meaning | Action |
|---|---|---|
| **HIGH** | Still load-bearing, still accurate, still referenced in the last 30 days | Keep as-is |
| **MEDIUM** | Accurate but hasn't been referenced; possibly overhead | Keep with a "last reviewed" date; consider promoting to topic file or demoting to archive |
| **LOW** | Stale, inaccurate, or contradicted by newer entries | Rewrite or remove |
| **DEAD** | Pure noise, was never load-bearing, or has been superseded | Remove |

**Quality signals:**
- Was it referenced in the last 30 days? (`grep -r "<key phrase>" 01\ Daily/ 03\ Projects/`)
- Is the claim verifiable against disk? (memory's "disk wins over recap" rule)
- Is the date still relevant? ("the new X" from 6 months ago is probably not new)
- Is the claim contradicted by a newer entry? (the later entry wins, delete the older)

**Output:** a per-entry score table with action.

### Sub-step 5: Balance the mix

**Purpose:** ensure the corpus is well-distributed across Mavis's actual work surfaces, not skewed to one domain.

**Mix dimensions to check:**
- **Memory vs skills vs vault vs kanban:** is one surface carrying all the load? (If memory is 30KB and skills are 5 total, the corpus is skewed.)
- **Domain coverage:** is the corpus balanced across Andre's active projects, or is one project dominating?
- **Temporal balance:** are recent entries roughly proportional to recent activity, or is the corpus old-heavy?
- **Rule vs example vs context:** is the corpus mostly rules (memory entries), mostly examples (skill files), or mostly context (vault)?

**The article's analog:** "balance the data mix across code, books, science, and web" — the Mavis analog is to ensure the corpus spans Andre's actual work domains, not one project's obsession.

**Output:** a balance report — for each dimension, the current distribution and the target.

## The output (the audit report)

The report is a single markdown file at `03 Projects/Mavis EA Design/reports/data-quality-audit-YYYY-MM-DD.md`. Structure:

```markdown
# Data Quality Audit: Mavis Corpus

**Audit time:** [timestamp]
**Auditor:** Mavis (EA)
**Scope:** [memory + skills + vault + kanban — which surfaces in scope]
**Window:** [the period the corpus covers]

## Inventory
[table from sub-step 1]

## Filter list
[entries to remove/rewrite, with reasons from sub-step 2]

## Dedup map
[canonical file + links to update, from sub-step 3]

## Quality scores
[per-entry score table, from sub-step 4]

## Balance report
[mix dimensions, current vs target, from sub-step 5]

## Recommended actions (in priority order)
1. [highest-leverage fix]
2. [next fix]
3. ...
```

## The procedure

1. **Pick the scope.** All surfaces by default, or a specific surface if Andre says so.
2. **Run sub-step 1 (inventory).** Use `find`, `wc -l`, `ls -la`. Disk hits only.
3. **Run sub-step 2 (filter).** Read the entries, don't recap. Apply the filter criteria.
4. **Run sub-step 3 (dedupe).** Use `grep` + `diff` to find duplicates. Read with intent before merging.
5. **Run sub-step 4 (quality-score).** Score every entry. Be honest — if it's LOW, say so.
6. **Run sub-step 5 (balance).** Compare the distribution to Andre's actual work mix (use `vault-30day-auditor` for the work mix).
7. **Aggregate to the report.** Prioritize the recommended actions. Top 3 should be doable in one session.
8. **Decide action.** If the audit is run on a cron, write the report and notify. If run on demand, present the report and ask Andre for the go-ahead on the actions.

## Hard constraints

1. **Disk is ground truth.** Every inventory, filter, dedup, and score must reference a real file path. No "I think there's an entry that says X" — show the file:line.
2. **Read-only during audit.** The audit doesn't delete or rewrite anything. It produces a recommended-actions list. Fixes are a separate step, owned by the chief.
3. **Mavis territory only.** Inventory is `~/.mavis/agents/mavis/` and `~/MiniMax-Agent/`. Do not cross into `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/`, or any other agent's tree. (Per ABSOLUTE SEPARATION rule.)
4. **The article is a trigger, not a source.** The 5-sub-step framework is from the LLM data-cleaning pipeline; the Mavis mapping is mine. Cite the article for the framework, but the specific filter criteria, score rubric, and balance dimensions are Mavis-specific.
5. **No fixing during audit.** If the audit finds a critical entry that is actively harmful, surface it inline and stop — don't fix in this skill.

## Anchoring sources

- The 5-sub-step framework: @sairahul1 "How To Build Your Own LLM" Stage 1 (popularization, use as trigger)
- Mavis `MEMORY.md` cross-cutting disciplines: "Disk wins over recap", "quantified claims need verification"
- `vault-30day-auditor` skill — for the work-mix baseline
- `ea-5-mistakes-audit` skill — for the Mistake 2 cross-check
- X-Content-Engine rule: skill agent home + vault mirror must be in sync
