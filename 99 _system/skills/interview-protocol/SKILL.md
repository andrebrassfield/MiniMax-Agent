---
name: interview-protocol
description: |
  Codifies the structured Q&A procedure for extracting operational context from a human — the same procedure used to build SOUL.md and MAVIS.md for Andre. Use this skill when: onboarding a new operator, entering a new project domain, refreshing stale context, or extending an existing profile.

  Triggers: "interview me for the new operator", "set up a profile for [name]", "refresh my context", "extract context for [project]", "onboard [domain]".

  Do NOT load for: ongoing conversational Q&A (use ad-hoc), technical debugging (use specific skill), or one-line profile snapshots (overkill).
---

# interview-protocol

The canonical procedure for extracting operational context from a human. Produces structured output that maps directly to SOUL.md / MAVIS.md / MEMORY.md sections.

## Intent

Most operator profiles drift because:
1. They were captured organically in chat (no structured procedure)
2. They capture what the operator DOES, not how they THINK
3. They conflate biography with operational profile
4. They get stale because no re-extraction protocol exists

This skill fixes all four: structured Q&A → operational profile (not biography) → refreshable on demand.

## When to run

**Triggers:**
- "interview me for [name]" — full profile extraction
- "set up a profile for [domain]" — domain-specific extraction
- "refresh my context" — re-extract + diff against existing
- "what's missing in my profile" — gap analysis

**Do NOT run for:**
- One-line profile questions ("what's Andre's day job?")
- Ongoing conversational Q&A
- Technical debugging (use specific skills)
- Profile snapshots (one paragraph or less — use direct Q&A)

## The 14-Section Protocol

The procedure covers 14 sections that mirror SOUL.md's structure. Each section is a single question asked in sequence. Wait for each answer before asking the next.

**Critical discipline:** ONE question at a time. No batching. No "answer these 5 questions." The single-question rhythm produces deeper answers.

### Section 1 — Identity (one question)

> "Who are you as a thinker, not as a biography? How do you evaluate information?"

Probe for: how they distinguish signal from noise, what they trust, what they distrust, what they're optimizing for.

### Section 2 — Mission (one question)

> "What's the one thing you're trying to accomplish that, if you got it, would make everything else easier?"

Probe for: the load-bearing goal, not the wishlist.

### Section 3 — Active Projects (one question)

> "What are the 3 projects you most want to ship in the next 90 days, and which one is the highest leverage?"

Probe for: real projects, not aspirations. The "which is highest leverage" forces ranking.

### Section 4 — Hard Constraints (one question)

> "What's the constraint that, if you broke it, would break everything? What would you never do, even if it would help?"

Probe for: non-negotiables. These become the red-zone rules in SOUL.md.

### Section 5 — Communication Style (one question)

> "How do you want me to talk to you? What makes you stop reading? What makes you keep reading?"

Probe for: tone preferences, length tolerance, formatting preferences.

### Section 6 — Open Questions (one question)

> "What are the 3 questions you're sitting with right now that you haven't answered?"

Probe for: real questions, not rhetorical ones. These become the active question set.

### Section 7 — Stance / Pushback (one question)

> "When should I push back hard? When should I just do what you said?"

Probe for: the conditions under which pushback is welcome vs annoying.

### Section 8 — Accountability (one question)

> "How do you want to be held accountable? What does good output look like vs. performative output?"

Probe for: their definition of "actually useful" vs "looks useful."

### Section 9 — Domain Context (project-specific)

For domain interviews (not operator profiles):
> "What does the operator need to know about [domain] that they wouldn't learn from a textbook?"

Probe for: lived experience, scars, opinions that aren't in the docs.

### Section 10 — Autonomy Boundaries (one question)

> "What should I never do without explicit approval? What can I do and report?"

Probe for: the yellow/red/green zone of actions. Becomes the Autonomy Boundary Table.

### Section 11 — Failure Modes (one question)

> "What's the most common way I've failed you or someone like me? What does that failure look like?"

Probe for: past failures, near-misses, the failure modes to design against.

### Section 12 — Tools and Stack (one question)

> "What tools do you rely on daily that I should never break or override?"

Probe for: tooling that has high switching cost.

### Section 13 — Schedule and Cadence (one question)

> "When do you do deep work? When do you do admin? When are you unreachable?"

Probe for: the time-of-day context that affects when to surface what.

### Section 14 — End State (one question)

> "If this profile were working perfectly, what would I notice that's different from today?"

Probe for: the success criteria. If they can't articulate it, the profile is incomplete.

## Output Shape

Write to `~/MiniMax-Agent/03 Projects/[operator-or-domain]/interview-output-YYYY-MM-DD.md`:

```markdown
---
date: YYYY-MM-DD
type: interview-output
source: <operator name> or <domain name>
sections_covered: <N of 14>
duration: <minutes>
---

# Interview Output — <name> — YYYY-MM-DD

## 1. Identity
<answer verbatim + 1-2 line synthesis>

## 2. Mission
<answer + synthesis>

...

## 14. End State
<answer + synthesis>

## Synthesis (Mavis's read)

<2-3 paragraphs: what pattern emerges across the answers, what's load-bearing, what conflicts with existing SOUL.md/MAVIS.md if refreshing>

## Recommended updates

If refreshing existing profile:
- [ ] SOUL.md: <specific change>
- [ ] MAVIS.md: <specific change>
- [ ] MEMORY.md: <specific addition>

If new profile:
- [ ] Create new SOUL.md at `~/MiniMax-Agent/SOUL-<name>.md` (or extend if existing)
- [ ] Create new MAVIS.md or extend
- [ ] Add pointer in MEMORY.md
```

## Halt Conditions

- Operator gives "I don't know" on > 2 sections → flag, ask which to revisit later, end interview
- Answers contradict existing SOUL.md/MAVIS.md (when refreshing stale context) → HALT, surface contradiction, ask operator to resolve
- Interview runs > 2 hours → save partial output, end with summary of what's missing
- Operator asks to skip a section → mark as "skipped" not "unknown", continue

## State Tracking

State file at `~/.mavis/state/interview-protocol-YYYY-MM-DD.md`:
- Sections covered (1-14)
- Time per section
- Operator's energy/engagement notes
- Skipped sections (with reason)

## Cross-references

- Spec: `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/interview-protocol-2026-06-22.md`
- Source profile: `~/MiniMax-Agent/SOUL.md` (Andre's existing profile, can be re-extracted)
- Companion: `~/MiniMax-Agent/MAVIS.md` (operator's active state)
- Memory: `~/.mavis/agents/mavis/memory/MEMORY.md` (always-on context)

## Examples

### Example 1 — Onboarding a new operator

Use case: new team member joins, want to set up their profile for Mavis support.

Trigger: "interview [name] for the new operator"

Procedure:
1. Set up session with [name] (or transcript if pre-recorded)
2. Run all 14 sections in order
3. Output: `03 Projects/Operators/[name]/interview-output-YYYY-MM-DD.md`
4. Synthesize into `~/MiniMax-Agent/SOUL-[name].md` (or extend existing SOUL.md if multi-operator)
5. Add pointer in MEMORY.md

### Example 2 — Refreshing stale context

Use case: existing operator's profile is > 6 months old, may have drifted.

Trigger: "refresh my context"

Procedure:
1. Read existing SOUL.md / MAVIS.md / MEMORY.md
2. Run all 14 sections
3. Compare answers against existing profile
4. Output: synthesis + "Recommended updates" list
5. Operator reviews diffs, approves updates
6. Apply approved updates

### Example 3 — New domain expansion

Use case: entering a new project area (e.g., "let's work on real estate now").

Trigger: "extract context for [domain]"

Procedure:
1. Run sections 1-8 (operator-level)
2. Run section 9 (domain context — the heaviest for domain interviews)
3. Skip sections 10, 11, 13 (operator-level, already covered)
4. Add section 15 (optional): "What's the one thing about [domain] that experts know but newcomers don't?"
5. Output goes to `03 Projects/[domain]/interview-output-YYYY-MM-DD.md`

## Reversibility

`<5 min: rm skill + vault mirror + delete any interview outputs created`
