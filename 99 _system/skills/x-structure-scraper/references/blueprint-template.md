# Blueprint Template — x-structure-scraper

The markdown file structure. The Scribe's blueprint-reading procedure
relies on these sections being in this order.

## File path

- Multi-account run: `03 Projects/X-Content-Engine/briefs/blueprints-YYYY-MM-DD.md`
- Single-account run: `03 Projects/X-Content-Engine/briefs/blueprint-[handle]-YYYY-MM-DD.md`

## Template

```markdown
# Structural Blueprint — @[handle] — YYYY-MM-DD CT

**Threads analyzed:** N
**Engagement floor:** 50K views
**Source URLs:** (one per thread, with view count)
**Analyzed by:** x-structure-scraper (Mavis)

---

## The Single Most-Copyable Move

[1-2 sentences on the one structural move that, if stolen, would
most improve a Scribe draft in this account's style. AT THE TOP —
this is the load-bearing answer.]

---

## Thread 1 — "[headline or first-tweet quote]" — N views

**Source:** https://x.com/[handle]/status/[id]

### Hook Structure
- **Bait:** "[verbatim first 1-2 sentences]"
- **Switch:** "[verbatim or paraphrased 1-2 sentences]"
- **Gap:** [1-2 sentences on what the bait promises vs. what the switch delivers]

### Argument Architecture
- **Thesis:** [1 sentence]
- **Antithesis:** [1 sentence]
- **Synthesis:** [1 sentence]
- **Transition phrasing:** "[verbatim 'but' / 'however' / 'the real reason' phrasing]"

### Pacing
- **Tweets:** N
- **Avg chars/tweet:** NNN
- **Avg sentences/tweet:** N.N
- **Rhythm example:** "[verbatim tweet showing the staccato beat or the long exhale]"

### Human Markers
- **"I don't know" admissions:** N (1 verbatim)
- **Personal anecdotes:** N (1-line summary each)
- **Past-wrongness references:** N (1-line summary each)

---

## Thread 2 — ...

---

## Cross-Thread Synthesis

### What unifies them
[1-2 paragraphs on the signature structural move]

### What varies
[1 paragraph on the range]

---

## Notes for the Scribe

- [Move 1 to try: e.g., "open with a specific $ figure, switch to a math-problem reframe in tweet 2"]
- [Move 2 to try: e.g., "use 1-clause sentences for emphasis at 20% frequency"]
- [Move 3 to try: e.g., "include at least 1 'I don't know' admission in every thread >5 tweets"]
- [Move to AVOID: e.g., "do not use 'the real reason is' — this account used it 4x across 5 threads, which means it's a tic, not a move"]

---

## Cross-Account Patterns (only if multi-account run)

[If the skill was run on 2+ handles, add a section comparing them.
Otherwise omit.]
```

## File growth pattern

The blueprint is one file per run. To build a multi-account
comparison, run the skill on each handle and reference the
per-account files in the cross-account section.

## Briefs ledger

After writing, append one line to
`03 Projects/X-Content-Engine/briefs/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — blueprint from @[handle] (N threads, floor 50K, output: blueprints-YYYY-MM-DD.md)
```
