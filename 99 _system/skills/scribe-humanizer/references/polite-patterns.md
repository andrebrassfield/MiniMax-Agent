# Polite-Pattern Tables — Stage 2 (Voice-Injection)

The Scribe is trained on the persona's voice examples but drifts toward
academic register. Stage 2 catches sentences that are too long, too hedged,
or too polite, and proposes staccato rewrites.

## The pattern table

| Polite/academic pattern | Example | Persona-style rewrite |
|---|---|---|
| "It is important to note that" | "It is important to note that 27% of leads are missed." | "27% of leads are missed." |
| "One might consider" | "One might consider the impact of…" | "The impact is…" |
| "It could be argued" | "It could be argued that AI…" | "AI…" |
| "In essence" | "In essence, the problem is…" | "The problem is…" |
| "Furthermore" / "Moreover" / "Additionally" | "Furthermore, the system…" | "And the system…" (or just delete) |
| "It is worth mentioning" | "It is worth mentioning that…" | DELETE |
| "In light of this" | "In light of this, we can see…" | DELETE |
| "Notably" | "Notably, the metric doubled." | DELETE |
| "It should be noted" | "It should be noted that…" | DELETE |
| Long compound sentences (3+ clauses) | "When the integration fails, which happens 12% of the time, the inventory drift can compound, leading to overselling." | "Integration fails 12% of the time. Inventory drifts. Overselling." |

## Rewrite discipline

- Use periods instead of commas for impact
- Drop the hedging/politeness entirely
- Mirror the persona's voice examples' rhythm (1-2 clauses per sentence)
- Keep the load-bearing specifics (numbers, names, dates)

## Match output format

```markdown
### Match N — "[academic pattern]" in Draft K

**Original:** "[verbatim full sentence]"
**Rewrite:** "[staccato rewrite in persona voice]"
**Diff:** [1-line summary — e.g., "Removed hedging. Split 1 long sentence into 3 staccato beats. Kept the $3,800 figure."]
```

## Discipline

Stage 2 is judgment-call. The rewrite is a PROPOSAL, not an auto-replace.
The original is preserved. Andre has the final say.

**Preserve load-bearing details.** If a rewrite loses a specific number,
name, or date, flag it as a "load-bearing detail" and let Andre decide
between the rewrite and the original. The persona values specifics over
fluency.

The reference for what "staccato" means in the persona's voice is the
persona file itself (`agents/persona.md`), not this table. When in doubt,
match the persona's 6 voice examples' rhythm.
