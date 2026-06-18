# Eval Cases — ea-5-mistakes-audit

11 self-check eval cases (1 per dimension). Each case is a
disk-verifiable probe the chief runs to answer "is this mistake
present in the work surface under audit."

## E1. Architecture obsession

```bash
# Find new skills / MCP servers / role definitions added in the last 30 days
find ~/.mavis/agents/mavis/skills/ -name "SKILL.md" -mtime -30
find ~/MiniMax-Agent/.harness/ -mtime -30 -name "*.md" 2>/dev/null
git -C ~/MiniMax-Agent log --since="30 days ago" --diff-filter=A --name-only
```

**Present if:** new files exist in skills/ or .harness/ in the
last 30 days AND the new addition is not load-bearing in any
current workflow.

## E2. Data as commodity

```bash
# Check memory hygiene
wc -l ~/.mavis/agents/mavis/memory/MEMORY.md
# Find topic files without YAML description
for f in ~/.mavis/agents/mavis/memory/*.md; do
  grep -L "^description:" "$f" 2>/dev/null
done
# Find repeated entries (same fact in 3+ places)
grep -c "^### " ~/.mavis/agents/mavis/memory/MEMORY.md
```

**Present if:** MEMORY.md > 15KB, OR topic files without YAML
description, OR repeated entries (3+ identical headings).

## E3. Skipping scaling math

```bash
# Skills that have never been triggered (no execution log)
for skill in ~/.mavis/agents/mavis/skills/*/SKILL.md; do
  name=$(basename $(dirname "$skill"))
  log=~/.mavis/agents/mavis/memory/skills/$name.log
  [ ! -f "$log" ] && echo "NEVER TRIGGERED: $name"
done
# Skills triggered < 3 times in the last 30 days
find ~/.mavis/agents/mavis/memory/skills/ -name "*.log" -mtime -30 -size -100c
```

**Present if:** skills with no execution log exist, OR the
trigger count is < 3 for skills that exist for > 30 days.

## E4. Stopping at SFT (no feedback loop)

```bash
# Find skills without --feedback or ## Iteration section
for skill in ~/.mavis/agents/mavis/skills/*/SKILL.md; do
  name=$(basename $(dirname "$skill"))
  if ! grep -qE "(## Iteration|## Feedback|--feedback|verifier_request)" "$skill"; then
    echo "NO FEEDBACK: $name"
  fi
  if ! grep -qE "## When NOT to run" "$skill"; then
    echo "NO REFUSAL CRITERIA: $name"
  fi
done
```

**Present if:** skills without feedback section OR without
refusal criteria exist.

## E5. Trusting surface metrics

```bash
# User-facing metrics (from 01 Daily/ feedback)
grep -r "unblock\|decision\|answered\|feedback" ~/MiniMax-Agent/01\ Daily/ | wc -l
# Vanity metrics (skill count, agent count, kanban throughput)
ls ~/.mavis/agents/mavis/skills/ | wc -l
mavis session list --state closed 2>/dev/null | wc -l
```

**Present if:** user-facing metrics are flat OR down while
vanity metrics are up. Or "Looks good to me" without evidence
appears in 01 Daily/.

## E6. Skipping RLVR (no auto-verifiable success)

```bash
# Skills with auto-verifiable Verification sections
for skill in ~/.mavis/agents/mavis/skills/*/SKILL.md; do
  name=$(basename $(dirname "$skill"))
  if grep -qE "## Verification" "$skill"; then
    if ! grep -qE "(exit code|test|TypeCheck|kanban move|file committed|cron fired)" "$skill"; then
      echo "HUMAN-ONLY VERIFICATION: $name"
    fi
  fi
done
# Cron health
mavis cron list mavis 2>/dev/null | grep -c "agent-disease-detector"
mavis cron list mavis 2>/dev/null | grep -c "kanban-health-check"
```

**Present if:** skills with verification sections depend on
human review only, OR the auto-eval cron isn't running.

## E7. Saturated benchmarks

```bash
# Last update to success criteria on recurring loops
for loop in ~/MiniMax-Agent/03\ Projects/*/loops/*-spec.md; do
  name=$(basename "$loop")
  last_modified=$(stat -f "%m" "$loop")
  days_ago=$(( ($(date +%s) - last_modified) / 86400 ))
  [ "$days_ago" -gt 180 ] && echo "STALE LOOP ($days_ago days): $name"
done
# Recent run verdicts (last 30 days)
find ~/MiniMax-Agent/03\ Projects/ -name "*.runlog" -mtime -30 -exec grep -l "FAIL" {} \;
```

**Present if:** success criteria last updated > 6 months ago
OR no FAIL in the last 30 days (the bar may be too low).

## E8. Ignoring inference cost

```bash
# Loops without ## Cost ceiling
for loop in ~/MiniMax-Agent/03\ Projects/*/loops/*-spec.md; do
  name=$(basename "$loop")
  if ! grep -qE "## Cost ceiling|## Cost Ceiling|Cost ceiling:" "$loop"; then
    echo "NO COST CEILING: $name"
  fi
done
# Recent run costs
mavis session list --state closed 2>/dev/null | head -5
```

**Present if:** loops without cost ceiling, OR a loop that
exceeded 2x expected cost in the last 30 days.

## E9. No eval pipeline in production

```bash
# Cron health
mavis cron list mavis 2>/dev/null
# Open disease alerts
ls ~/MiniMax-Agent/03\ Projects/Mavis\ EA\ Design/alerts/ 2>/dev/null
# Unmonitored work surfaces
for surface in ~/MiniMax-Agent/03\ Projects/*/; do
  if ! find "$surface" -name "*.healthcheck*" -o -name "*disease*" 2>/dev/null | head -1 | grep -q .; then
    echo "UNMONITORED: $surface"
  fi
done
```

**Present if:** no cron-based disease detection, OR open
disease alerts not actioned, OR work surfaces with no health
check.

## E10. No observability

```bash
# Find recurring loops
for loop in ~/MiniMax-Agent/03\ Projects/*/loops/*-spec.md; do
  name=$(basename "$loop")
  # Find the most recent runlog
  runlog=$(find ~/MiniMax-Agent/03\ Projects/ -name "${name%.md}.runlog" 2>/dev/null | head -1)
  if [ -n "$runlog" ]; then
    # Does the runlog have 3+ lines of evidence?
    lines=$(wc -l < "$runlog")
    [ "$lines" -lt 3 ] && echo "THIN EVIDENCE ($lines lines): $name"
  else
    echo "NO RUNLOG: $name"
  fi
done
```

**Present if:** loops without runlog OR runlogs with < 3 lines
of evidence (can't tell whether the loop ran correctly).

## E11. Ignoring regulatory realities

```bash
# Work surface description mentions regulated terms
surface=~/MiniMax-Agent/03\ Projects/<surface>/  # operator-supplied
if grep -qiE "(medical|clinical|patient|diagnosis|prescription|attorney|legal advice|client privilege|contract review|lending|credit|mortgage|employment|hiring|biometric|face recognition|ID verification)" "$surface/README.md" 2>/dev/null; then
  echo "REGULATED DOMAIN HIT"
  # Check for DPIA, BAA, Annex III classification
  [ ! -f "$surface/DPIA.md" ] && echo "NO DPIA"
  [ ! -f "$surface/BAA.md" ] && echo "NO BAA"
  [ ! -f "$surface/eu-ai-act-classification.md" ] && echo "NO EU AI Act classification"
fi
```

**Present if:** work surface description mentions regulated
terms AND any of: no DPIA, no BAA, no EU AI Act classification,
no human-in-the-loop clause, no audit log retention policy,
output language that asserts medical/legal certainty.

**Action:** HALT — pause for Andre's call. A regulated-domain
work surface that ships without a regulator named is a
liability, not a feature gap.
