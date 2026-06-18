# Output Format — scribe-humanizer

## File location

`03 Projects/X-Content-Engine/drafts/humanized-[original-filename].md`

## File structure

```markdown
---
type: humanized-draft
source: drafts/[original-filename].md
generator: scribe-humanizer
humanizer_version: 1.0
stages_applied: [fluff-purge, voice-injection, conflict-check]
humanized_at: YYYY-MM-DD HH:MM CT
---

# Humanized — [original filename]

> **Reading guide:** Stage 1 (Fluff Purge) is mechanical. Stage 2
> (Voice-Injection) is judgment-call. Stage 3 (Conflict Check) is the
> load-bearing one — it ensures every post has a contrarian edge. Review
> each stage independently. Accept/reject each match individually. The
> Scribe's original text is preserved at the bottom of each draft for
> diff/revert.

---

## Draft 1 — [original draft title / pillar / format]

### Original (verbatim, Scribe output)

> "[verbatim original post text]"

### Stage 1: Fluff Purge

[Matches and suggested fixes, if any. If clean, write "No matches —
12 Banned AI Phrases clear."]

### Stage 2: Voice-Injection

[Matches and rewrites, if any. If clean, write "No matches —
academic/polite register absent. Staccato rhythm holds."]

### Stage 3: Conflict Check

[Either PASS with the specific criterion that fired, or FAIL with the
proposed hot-take + insertion point.]

### Humanized Version (proposed)

> "[full rewritten post, with Stage 1 + Stage 2 + Stage 3 changes
> applied, if Andre accepts all]"

### Original vs. Humanized Diff

[Side-by-side or before/after blocks. Highlight the load-bearing
changes.]

### Accept/Reject (Andre's call)

- [ ] Accept Stage 1 (Fluff Purge)
- [ ] Accept Stage 2 (Voice-Injection)
- [ ] Accept Stage 3 (Conflict Check, if applicable)
- [ ] Accept the Humanized Version as the final draft
- [ ] Reject all and revert to Scribe's original

---

## Summary

- Drafts processed: N
- Stage 1 matches: N (across all drafts)
- Stage 2 matches: N
- Stage 3 PASSES: N | FAILURES: N
- Drafts that need a hot-take added: [list of K values]
- Humanized versions proposed: N
- Originals preserved at: drafts/[original-filename].md (untouched)
```

## Ledger append

After writing, append one line to
`03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — humanized from [original-filename] (N drafts,
  Stage 1: N matches, Stage 2: N matches, Stage 3: N passes / M failures)
```

## Verification

- Output file exists at the expected path with non-zero size
- All 3 stage sections present per draft (or "no matches" / "PASS" line)
- Humanized version is ≤280 chars (per draft)
- Original post text preserved verbatim in each draft's section
- Source file was not modified (compare stat --format=%Y before/after)
- No emoji, no hashtags, no "follow for more" in any humanized version
