# Dimension Checks — ea-loop-audit

The 7-dimension self-check probes. Each probe is a
disk-verifiable question the chief asks to answer PASS / WARN
/ FAIL. The eval suite verifies the auditor can produce
evidence per dimension.

## D1. Discovery

```bash
# Did the worker read the directive?
grep -c "directive\|task\|asked\|request" session.log  # > 0
# Did the worker load context?
[ -f ~/.mavis/agents/mavis/memory/MEMORY.md ] && echo "memory loaded"
# Did the worker name the scope?
grep -c "scope\|objective\|goal" session.log  # > 0
```

**PASS:** all 3 conditions met. **WARN:** directive + scope
read, no context. **FAIL:** directive not in log, no context
load.

## D2. Plan

```bash
# Are there named, ordered todos?
[ -f todowrite.json ] || [ -n "$(ls .todos 2>/dev/null)" ]
# Is there a verification-gate step?
grep -c "verify\|check\|test\|eval\|halt" todowrite.md  # > 0
```

**PASS:** todos exist + verification gate exists. **WARN:**
todos exist, no gate. **FAIL:** no todos.

## D3. Building blocks

```bash
# Skills in play
grep -c "skill\|x-researcher\|x-scribe\|x-empowerment" session.log
# Subagents spawned
grep -c "spawn\|mavis communication" session.log
# Memory consulted
grep -c "MEMORY.md\|memory append\|memory read" session.log
```

**PASS:** each block named (in play or correctly absent).
**WARN:** some blocks ambiguous. **FAIL:** block that should
be in play is missing.

## D4. Verification

```bash
# Verifier named?
grep -c "verifier\|verify\|check\|test" session.log
# Verifier is different model/agent?
verifier=$(grep "verifier" session.log | head -1)
executor=$(grep "executor\|executed" session.log | head -1)
[ "$verifier" != "$executor" ] || echo "WARN: same model"
# Evidence on disk?
[ -f $verdict_file ] && [ $(wc -l < $verdict_file) -ge 3 ] || echo "WARN: no disk evidence"
```

**PASS:** verifier different + disk evidence exists.
**WARN:** verifier same model (self-verify) or no disk.
**FAIL:** no verifier or "looks good" without evidence.

## D5. Stop condition

```bash
# Stop condition named upfront?
grep -c "stop when\|stop condition\|done when\|complete when" todowrite.md
# Stop condition met with evidence?
[ -f $stop_evidence_file ] || echo "WARN: no evidence"
```

**PASS:** condition named + met with evidence. **WARN:**
condition named but ambiguous. **FAIL:** worker stopped
before condition met.

## D6. Cost ceiling

```bash
# Ceiling named upfront?
grep -c "ceiling\|budget\|cost cap\|token budget" todowrite.md
# Actual cost within ceiling?
ceiling=$(grep "ceiling" todowrite.md | head -1)
actual=$(grep "actual\|elapsed" session.log | head -1)
# Parse and compare (heuristic)
```

**PASS:** ceiling named + respected with evidence. **WARN:**
ceiling exceeded slightly. **FAIL:** no ceiling or
significantly exceeded.

## D7. Loop type

```bash
# Was the work cost-bounded (clear inputs/outputs)?
grep -c "input:\|output:\|deliverable:" todowrite.md
# If yes, was it run as closed loop?
grep -c "closed loop\|closed-loop" session.log
# If no, was open loop signed off?
grep -c "sign.off\|approved by\|cost approved" session.log
```

**PASS:** closed for bounded work, open only with sign-off.
**WARN:** open without sign-off. **FAIL:** wrong loop type
for the work.
