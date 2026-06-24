---
description: "Quick decision tree per dimension for ea-loop-audit — short questions the chief asks out loud, in order. Fast-path version. Moved from skill-local references 2026-06-22."
source: ~/.mavis/agents/mavis/skills/ea-loop-audit/references/dimension-decision-tree.md
---

# Dimension Decision Tree — ea-loop-audit

Quick decision tree per dimension. The 7 dimensions'
PASS/WARN/FAIL criteria live in `audit-dimensions.md`. This
file is the fast-path version: short questions the chief
asks out loud, in order.

---

## D1. Discovery happened

```
Q: Did the worker read the directive before starting?
   │
   ├─ No (executed on assumed intent) ──────────► FAIL
   │
   ├─ Yes ─► Did the worker load relevant context
   │         (vault, memory, gBrain, files)?
   │         │
   │         ├─ No ─────────────────────────────► WARN
   │         │
   │         └─ Yes ─► Did the worker name the
   │                    scope before executing?
   │                    │
   │                    ├─ No ──────────────────► WARN
   │                    └─ Yes ──────────────────► PASS
```

**One-line evidence pattern:** "Directive: <path or quote>.
Context loaded: <files>. Scope: <one-sentence summary>."

---

## D2. Plan was explicit

```
Q: Is there a todowrite (or equivalent) before execution?
   │
   ├─ No (mental plan only) ───────────────────► WARN
   │
   ├─ Yes ─► Are the steps named, ordered, with
   │         a verification-gate step?
   │         │
   │         ├─ Steps exist but no gate ────────► WARN
   │         │
   │         ├─ Steps + gate exist ─► Are
   │         │   dependencies named?
   │         │   │
   │         │   ├─ No ──────────────────────► WARN
   │         │   └─ Yes ──────────────────────► PASS
   │         │
   │         └─ No ordered steps ────────────────► FAIL
```

**One-line evidence pattern:** "Todos: <N> steps, <with/without>
verification gate, <with/without> dependencies."

---

## D3. Execution used the right building blocks

```
For each of: Automations / Worktrees / Skills / Plugins /
             Subagents / Memory:
  │
  ├─ Was the block in play? ─► Is the artifact named?
  │   │
  │   ├─ Yes + named ────────► PASS (in play)
  │   ├─ Yes + not named ────► WARN (ambiguous)
  │   └─ No (correctly absent) ► PASS (correctly absent)
  │
  └─ Was a block that should have been in play missing? ─► FAIL
```

**One-line evidence pattern:** "Blocks in play: skills=X,
subagent=Y, memory=Z. Absent (justified): plugins=N/A."

---

## D4. Verification was independent

```
Q: Did a different model / agent / human verify the work?
   │
   ├─ No verification ──────────────────────────► FAIL
   │
   ├─ Yes ─► Was the verifier the same model as
   │         the executor (with a different prompt)?
   │         │
   │         ├─ Yes (self-grade in a hat) ──────► WARN
   │         │
   │         └─ No (different model/agent/human) ─►
   │            Was the evidence on disk?
   │            │
   │            ├─ No (recap) ─────────────────► WARN
   │            └─ Yes (disk hit) ──────────────► PASS
```

**One-line evidence pattern:** "Verifier: <different model /
agent / human>. Evidence: <disk path or log line>."

---

## D5. Stop condition was hit, not just claimed

```
Q: Was a stop condition named before execution?
   │
   ├─ No (worker stopped because they ran out of
   │   patience) ──────────────────────────────► FAIL
   │
   ├─ Yes ─► Was the stop condition met with evidence?
   │         │
   │         ├─ No (worker stopped before the
   │         │   condition was met) ────────────► FAIL
   │         │
   │         ├─ Yes + evidence (disk hit) ──────► PASS
   │         └─ Yes but ambiguous (no evidence) ► WARN
```

**One-line evidence pattern:** "Stop condition: <name>. Met
because: <evidence — disk hit, log line, or 'met'>."

---

## D6. Cost was within ceiling

```
Q: Was a cost ceiling named upfront?
   │
   ├─ No ─► Was the work bounded (single-shot, <$1,
   │         <5 min)? ─► Yes (bounded) ─► PASS
   │         │
   │         └─ No (unbounded work) ─────────► FAIL
   │
   ├─ Yes ─► Did the work stay within the ceiling?
   │         │
   │         ├─ Yes ─────────────────────────► PASS
   │         ├─ Slightly exceeded (< 2x) ─────► WARN
   │         └─ Significantly exceeded (> 2x) ► FAIL
```

**One-line evidence pattern:** "Ceiling: <X>. Actual: <Y>.
Within: <yes/no>."

---

## D7. Right loop type (closed/open)

```
Q: Was the work cost-bounded (clear inputs, clear outputs,
   clear "done")?
   │
   ├─ Yes ─► Was it run as a closed loop? ─► Yes ─► PASS
   │         │
   │         └─ No (run as open loop) ─────► WARN
   │             (cost-bounded work should
   │              be closed)
   │
   └─ No (work was exploratory) ─► Was the open
                                    loop signed off?
                                    │
                                    ├─ No ────────────► FAIL
                                    └─ Yes ───────────► PASS
```

**One-line evidence pattern:** "Closed (bounded: <X>) | Open
(justified: <reason>). Sign-off: <yes/no>."
