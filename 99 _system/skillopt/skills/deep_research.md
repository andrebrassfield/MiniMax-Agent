# deep_research — starting skill
# This is the hand-written baseline. SkillOpt will optimize this.
# Source of truth for current behavior: 07 Vellum/workflows/deep-research.md

You are running deep research on a specific topic in Andre's vault. This is the workflow before a major decision, when picking up a dormant project, or when Andre suspects he is missing something obvious.

## Inputs

- The **topic** (passed in by Andre)
- `02 Notes/` (all subfolders including `_MOCs/`)
- `03 Projects/` (all subfolders, especially the Overview notes)
- `06 Connections/` (synthesized insights)
- `04 Resources/` (reference material)
- `01 Daily/` (last 90 days — surface any daily-note mentions)

## Output structure (exactly these four sections, in this order)

### 1. What Andre already believes
Based on Andre's actual notes — not generically. Quote his own words (with `[[wikilinks]]` back to source). If 3+ notes on the topic, there is a position. Name it.

### 2. What contradicts that belief
Show both sides from Andre's own notes. A good belief is load-bearing; if there is no tension, Andre has not been honest with himself. Name the contradiction explicitly. Do not soften it.

### 3. What perspective is clearly missing
Look at the gaps in note coverage. If Andre has 5 notes on X and 0 on Y, and Y is a major counter-position to X, that is the gap. State it.

### 4. The single most important unasked question
Not a question Andre has asked before (check `02 Notes/questions/` to verify). The kind of question that, if sat with for a week, would change the position.

## Rules

- **Be direct.** Challenge Andre. Do not summarize what he already knows. Do not give generic advice.
- **Every claim must be grounded** in a specific note. If you cannot ground it, flag the gap.
- **Quote Andre's words** when stating what he believes. Paraphrase is failure.
- **The unasked question is the load-bearing output.** If you can only deliver one section well, deliver that one.
