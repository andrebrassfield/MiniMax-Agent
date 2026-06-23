---
name: two-link-rule
description: |
  Soft enforcement of the Obsidian Masterclass's "two-link rule" — every permanent note should have at least two explicit wikilinks to existing notes. This skill recommends 2+ connections for a given note but does not force them (soft gate, not hard gate).

  Trigger: "add connections to this note", "check the two-link rule for [note]", "what should this link to?", "review connections for [note]".

  Do NOT load for: notes that are explicitly designed to be standalone (literature notes with reactions, daily captures), for files outside `~/MiniMax-Agent/02 Notes/ideas/` and `~/MiniMax-Agent/01-PERMANENT/`, or for one-line captures where linking would be busywork.
---

# two-link-rule

The Obsidian Masterclass's "two-link rule" as a soft Mavis skill. Every permanent note should have at least two explicit wikilinks to existing notes — the first connection is usually obvious, the second requires genuine thought.

## Why Soft, Not Hard

A hard gate (reject the note if < 2 connections) creates friction that kills the writing flow. The article explicitly says the second connection requires "genuine thought about how the idea fits the existing network" — that's work that happens at thinking-time, not at filing-time.

So this skill runs AFTER the note is written, as a recommendation engine. Not a gate.

## When to Run

**Triggers:**
- After Mavis processes a new note into `01-PERMANENT/` or `02 Notes/ideas/`
- Explicitly invoked: "check the two-link rule for [note]"
- During `inbox-filer` cron: when a new idea/pattern note lands, run this skill before completing the filing

**Do NOT run for:**
- Daily captures (raw notes in `01 Daily/`)
- Literature notes in `02 Notes/articles/` (those use reaction discipline, different shape)
- Project notes (`03 Projects/<X>/`) — those have project-scoped linking conventions
- One-line captures where linking would be busywork

## The 3-Step Procedure

### Step 1 — Read the note + extract core claim

Read the target note. Extract:
- Title (first `# ` heading or filename)
- Core claim (1-2 sentences)
- Tags (from frontmatter)
- Existing wikilinks (already-present connections)

### Step 2 — Find candidates (search + scan)

Search the vault for potential connections. Skip:
- Notes that already appear in the note's wikilinks
- Same-topic notes (the bar is "non-obvious")
- Notes that don't actually relate (grep matches on common words but no real connection)

Use a combination of:
```bash
# Grep for keywords from the core claim
KEYWORDS="<extracted keywords>"
grep -rilF "$KEYWORDS" ~/MiniMax-Agent/01-PERMANENT/ ~/MiniMax-Agent/02\ Notes/ 2>/dev/null | head -10

# Check related Maps of Content
ls ~/MiniMax-Agent/02\ Notes/_MOCs/ ~/MiniMax-Agent/03-MAPS/ 2>/dev/null
```

### Step 3 — Recommend 2+ connections

For each candidate that has a real connection (not just topical), propose:
- **Connection 1 (usually obvious):** the most direct link
- **Connection 2 (the load-bearing one):** the one that requires genuine thought — the one where reading both notes together reveals something neither says alone

If you can't find 2: surface that honestly. Don't pad with weak connections.

Output:

```markdown
# Two-Link Rule Review — <note title>

**Current connections:** <count>
**Verdict:** meets the rule / needs more / borderline

## Recommended connection 1
- **Target:** [[Note title]]
- **Why:** <one sentence — the obvious direct link>
- **Add wikilink:** <proposed text>

## Recommended connection 2
- **Target:** [[Note title]]
- **Why:** <2-3 sentences — the load-bearing insight from the connection>
- **Add wikilink:** <proposed text>

## If only 1 connection found
- **The note may be:** (a) genuinely standalone (rare), (b) ahead of its time (will link later when more notes exist), (c) needs more thinking before the second connection emerges.
- **Suggested action:** <one of: accept as standalone, defer, develop the note further>
```

## Hard Constraints

1. **Never force connections.** The rule's value comes from genuine thought. Padding with weak links is worse than no link.
2. **Non-obvious is the bar.** "Both notes mention X" is not a connection. "Reading A and B together reveals Y that neither says alone" is.
3. **Load on demand only.** This skill does not auto-run on every note save — it runs when invoked or during inbox-filer's filing step.
4. **Mavis territory only.** All paths are `~/MiniMax-Agent/`.
5. **Output is a recommendation.** The user (or Mavis in autonomous mode) decides whether to apply the suggested wikilinks.

## Halt Conditions

- Target note doesn't exist or unreadable → HALT, surface
- Note is outside the trigger folders (`01-PERMANENT/`, `02 Notes/ideas/`) → skip silently, log "out of scope"
- Note already has 5+ wikilinks → skip silently (rule comfortably exceeded)

## Cross-references

- Source article: Obsidian Masterclass (2026-06-22), Part 7 "The Linking System"
- Companion: `inbox-filer` cron (Step 3.5 could invoke this skill for new idea/pattern notes)
- Pattern: "retrieval-first principle" — connections make notes findable from multiple paths
