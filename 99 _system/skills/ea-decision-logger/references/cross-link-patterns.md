# Cross-link Patterns — ea-decision-logger

How to link the decision file to related surfaces. The
decision file is not useful in isolation; the links
provide the context future-Mavis needs to reason about
the decision.

## The 3 link types

### 1. Informed the decision (upstream)

The brief, research, or analysis that produced the
evidence.

**Examples:**
- `03 Projects/Mavis EA Design/reports/loop-engineering-framework.md`
  (justified the GEPA pivot)
- `00 Inbox/2026-06-10 - sk race article.md` (informed
  the M2.7 vs M3 routing decision)
- `04 Resources/articles/2026-06-08 - Tony Simons SOUL.md`
  (informed the EA contract)

**YAML pattern:**
```yaml
related:
  - 03 Projects/Mavis EA Design/reports/loop-engineering-framework.md
```

### 2. Depend on the decision (downstream)

The skill, cron, memory, or workflow that this decision
enables or constrains.

**Examples:**
- `99 _system/skills/ea-skill-evolution/SKILL.md` depends
  on the GEPA decision
- `99 _system/skills/ea-data-quality-audit/SKILL.md`
  depends on the data-quality-audit-cadence decision
- `~/.mavis/agents/mavis/memory/MEMORY.md` depends on the
  memory-schema decision

**YAML pattern:**
```yaml
related:
  - 99 _system/skills/ea-skill-evolution/SKILL.md
  - ~/.mavis/agents/mavis/memory/MEMORY.md
```

### 3. Preceded the decision (history)

Any prior decision that this one reverses, supersedes,
or builds on.

**Examples:**
- `2026-05-15-old-architecture.md` (reversed by
  `2026-06-16-gepa-pivot.md`)
- `2026-04-01-routing-default.md` (superseded by
  `2026-06-10-routing-v2.md`)

**YAML pattern:**
```yaml
related:
  - 02 Notes/decisions/2026-05-15-old-architecture.md
  # Or for reversal:
  reverses: 02 Notes/decisions/2026-05-15-old-architecture.md
```

## Wikilink vs path

Two conventions for cross-links:

**Path (YAML):** explicit, machine-readable
```yaml
related:
  - 99 _system/skills/ea-skill-evolution/SKILL.md
```

**Wikilink (body text):** Obsidian-style, human-readable
```markdown
The decision affects [[ea-skill-evolution]] and
[[MEMORY|the memory schema]].
```

Use paths in YAML (machine-readable for cross-reference
queries). Use wikilinks in body text (human-readable for
Andre's reading).

## Cross-link completeness

A decision file with all 3 link types is "fully
linked." A file with only 1 or 2 is "partially linked."

**Discipline:** aim for fully linked. If a link type
doesn't apply (e.g., no prior decision this reverses),
explicitly note "no prior decision" rather than
silently omitting.

## Eval cases

```bash
# Check that the decision file has at least 1 informed-by link
yaml=$(awk '/^---$/,/^---$/' "$decision_file")
informed=$(echo "$yaml" | grep -A20 "related:" | grep -cE "informed|reports/|articles/")
[ "$informed" -lt 1 ] && echo "WARN: no 'informed by' link"

# Check that the decision file references a related surface
related_count=$(echo "$yaml" | grep -cE "  - ")
[ "$related_count" -lt 1 ] && echo "WARN: no related surfaces"
```
