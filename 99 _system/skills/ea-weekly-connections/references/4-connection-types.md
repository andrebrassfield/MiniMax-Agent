# 4 Connection Types — ea-weekly-connections

The 4 connection types that constitute a strong
cross-domain pattern. The 3 anti-patterns that constitute
"not a connection" (and the discipline that rejects
them).

## The 4 connection types

### 1. Same procedural gap, different surfaces

Two unrelated surfaces share the same underlying
procedural gap.

**Example:** "The X-Content-Engine persona leak and the
Hermes config drift both stem from the same gap: the
worker is reading a stale cached file, not the live
config." Two surfaces, one root cause.

**Why it's a connection:** the gap is structural, not
incidental. Fixing it once fixes both surfaces.

### 2. Cascading effect

One upstream change has multiple downstream effects.

**Example:** "The ea-5-mistakes-audit Addition 11
triggered the ea-research-brief regulatory frame, which
then flagged the EU AI Act in three downstream briefs."
One upstream change, multiple downstream effects.

**Why it's a connection:** the downstream effects
cluster in time + topic. The connection reveals the
system's response to a single change.

### 3. Convergent timing

Multiple surfaces touch the same theme in the same week,
indicating the theme is being stress-tested.

**Example:** "Three different surfaces (memory entry,
kanban card, daily note) all touched the Mavis↔Hermes
separation in the same week — that's a signal the rule
is being stress-tested, not just referenced."

**Why it's a connection:** convergent timing is
informative. If three surfaces independently surface
the same theme, the theme is alive.

### 4. Contradictory surfaces

Two surfaces disagree about the state of the world.

**Example:** "The 30-day footprint report said 'no
orphan spawns this week' but the kanban-health-check
tick on Wednesday found 2. The contradiction is the
connection — one of them is wrong, and the audit ladder
resolves it."

**Why it's a connection:** the contradiction forces
a re-verification. The "which is right" question
surfaces evidence that wouldn't otherwise be visible.

## The 3 anti-patterns (NOT connections)

### 1. Multiple items on the same surface

**Example:** 3 kanban cards about the same project, all
moved in the same direction.

**Why it's not a connection:** it's a project
summary, not a cross-domain pattern.

**Discipline:** if the items are all on the same
surface, they go in the project summary, not the
weekly connections.

### 2. Forced connections

**Example:** "The new skill file and the morning coffee
are both 'things that happened this week.'"

**Why it's not a connection:** if you have to stretch
to make the link, the link is not load-bearing.

**Discipline:** when in doubt, don't force the
connection. Put the item in "open threads" for next
week.

### 3. Obvious-from-any-single-surface

**Example:** "The Scribe wrote 5 drafts and Andre
approved 3." This is a single-surface story
(X-Content-Engine).

**Why it's not a connection:** the insight is
visible from looking at any one surface. A
connection should reveal something not visible in
isolation.

**Discipline:** if a single-surface read reveals the
insight, it's not a connection.

## Decision tree

```
For each item in the surface pull:
│
├─ Does it relate to an item on another surface?
│  │
│  ├─ No → not a connection
│  │
│  └─ Yes ─► Is the relation one of the 4 types?
│           │
│           ├─ Yes ─► Add to the 3-5 connections
│           │
│           └─ No ─► Is the relation a forced
│                      connection? (if you have to
│                      stretch, it's forced)
│               │
│               ├─ Yes → reject (open threads for next week)
│               └─ No → not a connection
```

## The 3-5 range discipline

- **2 connections:** insufficient. The cross-domain
  signal is weak.
- **3-5 connections:** the spec. Strong signal,
  readable in 5 minutes.
- **7+ connections:** signal-diluted. Pick the
  strongest 3-5; put the rest in "open threads."

## Cross-reference

- `4-step-procedure.md` — Step 2 in detail
- `brief-template.md` — the connection brief structure
- `tests/discipline.md` — 3-5 range, cross-domain,
  EA-voice checks
