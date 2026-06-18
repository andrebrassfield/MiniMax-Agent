# 5 Sub-Steps — ea-data-quality-audit

The LLM data-cleaning pipeline applied to Mavis surfaces.
The load-bearing structure. The SKILL.md only carries
the 5-sub-step list. The full per-sub-step detail lives
here.

---

## Sub-step 1: Extract clean content from raw state

**Purpose:** inventory the corpus, in canonical form.

**What to inventory:**

| Surface | Path | What to extract |
|---|---|---|
| Memory (canonical) | `~/.mavis/agents/mavis/memory/MEMORY.md` | Full file, line count, topic file references |
| Memory (topic files) | `~/.mavis/agents/mavis/memory/*.md` | Each file's first H1, description, size |
| Skills (agent home) | `~/.mavis/agents/mavis/skills/*/SKILL.md` | Skill name, description, line count |
| Skills (vault mirror) | `~/MiniMax-Agent/99 _system/skills/*/SKILL.md` | Cross-check vs agent home (must be in sync) |
| Vault | `~/MiniMax-Agent/01 Daily/`, `02 Notes/`, `03 Projects/` | Modified in last 30 days |
| Kanban | `~/.mavis/kanban.db` (sqlite) | Open tickets, closed tickets, last 30 days activity |

**Output:** a single inventory table with file path, size,
last modified, and a one-line "what's in it" tag.

---

## Sub-step 2: Filter noise / harmful / off-topic

**Purpose:** remove what's actively polluting the corpus.

**Filter criteria:**

- **Harmful:** any memory entry that instructs a behavior
  Andre has explicitly corrected (check `01 Daily/` for
  course-corrections; if a memory entry says one thing
  and Andre's later notes say another, the memory is
  noise)
- **Off-topic:** topic files in `MEMORY.md/` that haven't
  been read or written in 60+ days (use `find -atime +60`
  and `find -mtime +60`)
- **Personal data:** PII, credentials, API keys in memory
  or skill files (rare but possible — check the corpus)
- **Stale claims:** any "X is the state as of <date>" claim
  where <date> is > 30 days old and the state has likely
  moved (e.g., "X is launching next week" from 3 weeks
  ago)
- **Duplicates with drift:** same fact in 3+ places with
  slightly different wording (the corpus is whispering
  the same thing in different voices — pick the canonical
  version and delete the rest)

**Output:** a deletion/rewrite list with file:line
references and the reason for the filter.

---

## Sub-step 3: Deduplicate

**Purpose:** remove redundant copies so the canonical
version is the only version.

**Dedup levels:**

- **By file:** same content in two files (e.g., a memory
  entry in `MEMORY.md` and a topic file). Pick one, link
  from the other.
- **By topic:** 3+ entries making the same point.
  Synthesize into one canonical entry.
- **By line:** repeated phrases in the same file (e.g., a
  "we always do X" line in 5 skills — pick one as the
  home, link from the rest).

**Tools:**

```bash
# Find candidates
find ~/.mavis/agents/mavis/memory -type f -name "*.md" | xargs grep -l "<key phrase>"

# Identify drift between copies
diff <file1> <file2>

# Read with intent: are these two entries really the same
# claim, or two facets of the same claim that both belong?
```

**Output:** a dedup map — for each duplicated claim, name
the canonical file and the links to update.

---

## Sub-step 4: Quality-score

**Purpose:** for each remaining entry, score its quality
on a 4-point scale.

**Score rubric:**

| Score | Meaning | Action |
|---|---|---|
| **HIGH** | Still load-bearing, still accurate, still referenced in the last 30 days | Keep as-is |
| **MEDIUM** | Accurate but hasn't been referenced; possibly overhead | Keep with a "last reviewed" date; consider promoting to topic file or demoting to archive |
| **LOW** | Stale, inaccurate, or contradicted by newer entries | Rewrite or remove |
| **DEAD** | Pure noise, was never load-bearing, or has been superseded | Remove |

**Quality signals:**

- Was it referenced in the last 30 days?
  (`grep -r "<key phrase>" 01\ Daily/ 03\ Projects/`)
- Is the claim verifiable against disk? (memory's "disk
  wins over recap" rule)
- Is the date still relevant? ("the new X" from 6 months
  ago is probably not new)
- Is the claim contradicted by a newer entry? (the later
  entry wins, delete the older)

**Output:** a per-entry score table with action.

---

## Sub-step 5: Balance the mix

**Purpose:** ensure the corpus is well-distributed across
Mavis's actual work surfaces, not skewed to one domain.

**Mix dimensions to check:**

- **Memory vs skills vs vault vs kanban:** is one surface
  carrying all the load? (If memory is 30KB and skills are
  5 total, the corpus is skewed.)
- **Domain coverage:** is the corpus balanced across
  Andre's active projects, or is one project dominating?
- **Temporal balance:** are recent entries roughly
  proportional to recent activity, or is the corpus
  old-heavy?
- **Rule vs example vs context:** is the corpus mostly
  rules (memory entries), mostly examples (skill files),
  or mostly context (vault)?

**The article's analog:** "balance the data mix across
code, books, science, and web" — the Mavis analog is to
ensure the corpus spans Andre's actual work domains, not
one project's obsession.

**Output:** a balance report — for each dimension, the
current distribution and the target.

---

## What this framework is NOT

- **Not the LLM data-cleaning pipeline verbatim.** The
  Mavis mapping is local. The framework is a trigger;
  the criteria are Mavis-specific.
- **Not a one-shot fix.** Recommended actions may need a
  multi-session cleanup. The audit produces the list; the
  cleanup is a separate skill (`ea-skill-evolution` for
  skill mutations, manual edit for memory entries).
- **Not a re-architecture.** The audit is about the
  corpus, not the structure. Architecture changes go
  elsewhere (e.g., `ea-closed-loop-builder` for new
  loops, `ea-skill-evolution` for skill mutations).
