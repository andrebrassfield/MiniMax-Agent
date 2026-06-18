# 5-Sub-Step Checks — ea-data-quality-audit

The 5 sub-step disk-verifiable probes. Each sub-step has
a probe the chief runs to answer "did the audit actually
do this sub-step?"

## S1. Inventory probe

```bash
# Did the audit enumerate the 6 surfaces?
for surface in \
  "memory/MEMORY.md" \
  "memory/*.md" \
  "skills/*/SKILL.md" \
  "99 _system/skills/*/SKILL.md" \
  "01 Daily" \
  "02 Notes"; do
  if [ -z "$(ls ~/.mavis/agents/mavis/$surface ~/MiniMax-Agent/$surface 2>/dev/null)" ]; then
    echo "WARN: surface not inventoried: $surface"
  fi
done
```

**Failure mode this catches:** the audit skipped a
surface. The inventory is incomplete.

## S2. Filter probe

```bash
# Did the audit produce a filter list (deletion/rewrite with file:line refs)?
filter_section=$(awk '/## 2\. Filter list/,/## 3\./' "$report")
echo "$filter_section" | grep -cE "^\\- " || echo "0"
# Should be > 0 for a real audit, but > 0 doesn't mean useful
# The deeper check: each line should have a file:line ref
echo "$filter_section" | grep -E "^\\- " | grep -vE ":[0-9]+|:line" \
  && echo "WARN: filter entry without file:line reference"
```

**Failure mode this catches:** the filter list is
vague ("remove some old entries") instead of specific
("remove `MEMORY.md:42` — contradicted by 01 Daily/2026-06-10").

## S3. Dedup probe

```bash
# Did the audit find at least one dedup candidate?
dedup_section=$(awk '/## 3\. Dedup map/,/## 4\./' "$report")
canonical_count=$(echo "$dedup_section" | grep -cE "canonical|→|primary")

[ "$canonical_count" -lt 1 ] && echo "WARN: no dedup candidates identified"
```

**Failure mode this catches:** the audit didn't find any
duplicates. Either the corpus is deduped (rare) or the
audit didn't look.

## S4. Quality-score probe

```bash
# Are all 4 score tiers represented (or explicitly noted as N/A)?
score_section=$(awk '/## 4\. Quality scores/,/## 5\./' "$report")
for tier in HIGH MEDIUM LOW DEAD; do
  echo "$score_section" | grep -qE "^\| .*\\| $tier" \
    || echo "WARN: no $tier scores in report"
done
```

**Failure mode this catches:** the audit scored everything
HIGH (false positive) or skipped the scoring.

## S5. Balance probe

```bash
# Did the audit report on the 4 balance dimensions?
balance_section=$(awk '/## 5\. Balance report/,/## 6\./' "$report")
for dim in "Memory vs skills" "Domain coverage" "Temporal balance" "Rule vs example"; do
  echo "$balance_section" | grep -qF "$dim" \
    || echo "WARN: balance dimension missing: $dim"
done
```

**Failure mode this catches:** the audit only checked one
balance dimension. The corpus may be skewed in other
dimensions.

## Cross-reference

- `references/5-sub-steps.md` — full per-sub-step detail
- `references/procedure.md` — the 8-step procedure
- `references/report-template.md` — the audit report
  template
- `tests/audit-discipline.md` — disk-wins, no-fixing,
  Mavis-territory checks
