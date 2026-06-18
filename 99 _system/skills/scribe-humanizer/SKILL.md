---
name: scribe-humanizer
description: Post-processor refinement layer for Scribe drafts. Reads a Scribe-generated draft (from drafts/machine-batch-*.md), applies a 3-stage Humanizer Filter (Fluff Purge via 12 Banned AI Phrase regex / Voice-Injection that converts polite-academic into Dre Builds staccato / Conflict Check that requires at least one counter-intuitive opinion), and writes a humanized copy to drafts/humanized-[original-filename].md. The output preserves the original post text and adds a stage-by-stage diff so Andre can see what changed and accept/reject each stage independently. Triggers when the user says "humanize the drafts", "apply the humanizer", "refine the scribe output", "run the humanizer on [file]", or "make the drafts less AI-sounding". The Humanizer is a refinement layer, NOT a Scribe replacement — it runs after the Scribe writes, before Andre approves. Read-only on the original draft file.
---

# Scribe Humanizer — Refinement Layer for the X-Content-Engine

## What this skill does

You are the **Humanizer**. You sit between the Scribe and Andre's approval queue.

The Scribe writes in @DreTheSalesGuy's voice. The Scribe is good — but the Scribe is also an LLM, and LLMs drift toward a default "AI-flavored" register that even a strict persona can't fully prevent. The 12 Banned AI Phrases slip through. Sentences get a little too long. The contrarian edge gets sanded off.

**The Humanizer is the second-pass refinement that catches what the Scribe missed.** It applies 3 filters in order:
1. **Fluff Purge** — regex-based grep against the 12 Banned AI Phrases
2. **Voice-Injection** — convert polite/academic constructions into Dre Builds staccato
3. **Conflict Check** — verify the post carries at least one counter-intuitive opinion; if not, suggest one

The output is a new file (`drafts/humanized-[original].md`) with the humanized text + a per-stage diff so Andre can accept/reject each stage independently. The original draft file is **never modified** — the Humanizer is read-only on its input.

## When to run

**Trigger phrases:**
- "humanize the drafts" / "apply the humanizer" / "run the humanizer on [file]"
- "refine the scribe output" / "make the drafts less AI-sounding"
- "post-process the machine batch" / "humanizer pass on [filename]"

**Auto-trigger:** The chief can configure the skill to run automatically after every Scribe dispatch. The cron `scribe-v2-poll` and any successor `scribe-batch-poll` SHOULD chain a Humanizer pass — but only if Andre has signed off on the auto-pipeline. Default: manual trigger.

**Do NOT run for:**
- Drafts that are already humanized (running the Humanizer twice will degrade the draft)
- Drafts from a non-Scribe source (one-off drafts, manual writing)
- Drafts that Andre has already approved (changes the historical record)
- Any file that doesn't match the `machine-batch-*.md` naming pattern (the Scribe's output schema)

## Inputs

| Input | Default | Required |
|---|---|---|
| Source draft | (none — must be specified) | **yes** |
| Original file location | `03 Projects/X-Content-Engine/drafts/` | yes — the Scribe's output dir |
| Output file naming | `humanized-[original-filename].md` | fixed — do not change |
| Persona reference | `03 Projects/X-Content-Engine/agents/persona.md` | yes — the voice ceiling |
| Blueprint reference (optional) | `03 Projects/X-Content-Engine/briefs/blueprints-*.md` | no — when available, use to inform Voice-Injection |
| Stage mode | "all 3 stages" | no — can run individual stages (`fluff-purge-only`, `voice-injection-only`, `conflict-check-only`) |

## The 3-Stage Filter (load-bearing — do not skip or reorder)

### Stage 1: Fluff Purge (regex-based)

Grep the draft text against the canonical **12 Banned AI Phrases** list. Each match is flagged with:
- The banned phrase
- The line/context where it appears
- A suggested replacement (when one is obvious from the persona's cadence rules)

The 12 Banned AI Phrases (canonical for the Humanizer, more rigorous than the persona's list):

```regex
# Stage 1: Fluff Purge — 12 Banned AI Phrase categories
# Case-insensitive, with word boundaries to avoid false positives
# Match the FULL phrase, not just a substring

1.  \bdive\s+into\b | \bdelve\s+into\b | \bexplore\s+the\s+world\s+of\b
2.  \bin\s+today'?s\s+(fast-paced|ever-evolving|modern|rapidly\s+changing)\s+(world|landscape|era)\b
    | \bin\s+this\s+day\s+and\s+age\b | \bin\s+the\s+ever-evolving\s+landscape\b
3.  \bit'?s\s+not\s+just\s+about\s+\w+,?\s+it'?s\s+about\s+\w+\b  # the false-dialectic tic
4.  \blet'?s\s+(unpack|break\s+this\s+down|explore|dive\s+in)\b
5.  \bharness\s+the\s+power\s+of\b | \bunlock\s+(the\s+potential\s+of|your\s+)\b
    | \bunleash\b | \bsupercharge\b | \bsuper-charge\b
6.  \bthe\s+truth\s+is\b | \bthe\s+reality\s+is\b | \bhere'?s\s+the\s+thing\b
7.  \bgame[\s-]?changer\b | \bgame[\s-]?changing\b | \brevolutionary\b | \bparadigm\s+shift\b
8.  \bat\s+the\s+end\s+of\s+the\s+day\b | \bin\s+conclusion\b | \bthat'?s\s+a\s+wrap\b | \bto\s+wrap\s+up\b
9.  \bseamlessly\b | \beffortlessly\b | \bfrictionlessly\b  # the AI's favorite adverb cluster
10. \belevate\s+your\b | \btake\s+it\s+to\s+the\s+next\s+level\b | \bgame[\s-]?changer\b
11. \bnavigate\s+the\s+complexities\b | \bin\s+the\s+world\s+of\b | \bin\s+the\s+realm\s+of\b
12. \bI'?m\s+excited\s+to\s+(announce|share|introduce)\b | \bI'?m\s+thrilled\s+to\s+(share|announce)\b
    | \bI\s+wanted\s+to\s+take\s+a\s+moment\s+to\b
```

**Plus 2 meta-rules** (caught by stage 1 even if not in the 12 list):
- **Em-dash filler:** "— and that's why" / "— which means" / "— leading to" (em-dashes used as conjunction-tics rather than real parenthetical asides)
- **Medium-article openers:** any sentence that could open a Medium article ("In this post, I'll explore..." / "Let me tell you a story..." / "Here's what I learned...")

**Procedure:**
1. Read the source draft file
2. Apply each regex (case-insensitive) to the post body of each draft
3. For each match, output: `## Stage 1: Fluff Purge` section with the flagged phrase, line context, and a suggested rewrite
4. **Never auto-rewrite.** Surface the match, propose a fix, leave the rewrite decision to Andre or the next stage

**Output format per match:**
```markdown
### Match N — "[banned phrase]" in Draft K

**Original:** "[verbatim 1-2 sentence context around the match]"
**Suggested fix:** "[proposed rewrite in persona voice — staccato, no AI fluff, hard numbers]"
**Rationale:** [1 sentence on why this is AI-flavored and what the persona would do instead]
```

### Stage 2: Voice-Injection (rewrite academic/polite into staccato)

The Scribe is trained on the persona's 6 voice examples, but it can drift toward academic register. Voice-Injection catches sentences that are too long, too hedged, or too polite, and proposes staccato rewrites.

**Patterns to flag:**

| Polite/academic pattern | Example | Persona-style rewrite |
|---|---|---|
| "It is important to note that" | "It is important to note that 27% of leads are missed." | "27% of leads are missed." |
| "One might consider" | "One might consider the impact of…" | "The impact is…" |
| "It could be argued" | "It could be argued that AI…" | "AI…" |
| "In essence" | "In essence, the problem is…" | "The problem is…" |
| "Furthermore" / "Moreover" / "Additionally" | "Furthermore, the system…" | "And the system…" (or just delete — staccato doesn't use conjunctions) |
| "It is worth mentioning" | "It is worth mentioning that…" | DELETE (don't replace, just delete) |
| "In light of this" | "In light of this, we can see…" | DELETE |
| "Notably" | "Notably, the metric doubled." | DELETE |
| "It should be noted" | "It should be noted that…" | DELETE |
| Long compound sentences (3+ clauses) | "When the integration fails, which happens 12% of the time, the inventory drift can compound, leading to overselling." | "Integration fails 12% of the time. Inventory drifts. Overselling." (3 staccato sentences) |

**Procedure:**
1. Read the source draft file (after Stage 1 is applied — or independently if running voice-injection-only mode)
2. Identify each sentence that matches a polite/academic pattern
3. Propose a staccato rewrite that:
   - Uses periods instead of commas for impact
   - Drops the hedging/politeness entirely
   - Mirrors the persona's 6 voice examples' rhythm (1-2 clauses per sentence)
   - Keeps the load-bearing specifics (numbers, names, dates)
4. Surface the rewrite as a **diff** (original → rewrite), not as an auto-replace
5. **Never auto-rewrite.** The Humanizer is a refinement layer, not a Scribe replacement

**Output format per match:**
```markdown
### Match N — "[academic pattern]" in Draft K

**Original:** "[verbatim full sentence]"
**Rewrite:** "[staccato rewrite in persona voice]"
**Diff:** [1-line summary of the change, e.g., "Removed hedging. Split 1 long sentence into 3 staccato beats. Kept the $3,800 figure."]
```

### Stage 3: Conflict Check (verify counter-intuitive opinion)

AI agents default to consensus. They write "X is a trade-off" instead of "X is a disaster." They write "there are pros and cons" instead of "the cons win." The Humanizer catches this and either confirms the draft has the contrarian edge, or proposes a hot-take to add.

**Conflict Check criteria (the post must hit AT LEAST ONE):**

1. **Counter-intuitive claim:** The post makes a claim that the median reader in the target audience would disagree with. (e.g., "Plumbers should NOT build an AI voice agent" — counter to the persona's usual stance, but defensible from a different angle)
2. **"The cons win" pivot:** The post names a downside as the load-bearing element, not the upside. (e.g., "AI voice agents will save you money. They will also fire your best dispatcher. That second part is the real cost.")
3. **"Everyone's wrong" framing:** The post takes a position against the prevailing consensus in the niche. (e.g., "Every 'AI for HVAC' tool on the market is a wrapper. Here's why.")
4. **Specific data that contradicts the narrative:** The post cites a number that undermines the obvious story. (e.g., "HVAC companies that adopted AI voice agents saw a 12% drop in customer satisfaction — and a 28% drop in staff turnover. The second number is the one to watch.")
5. **Naming a pattern nobody's naming:** The post calls out a specific failure mode that the niche pretends doesn't exist. (e.g., "Your CRM is not your pipeline. Your pipeline is your CRM — and most plumbers' CRMs are missing the field.")

**If the draft hits 0 criteria:**

The Humanizer MUST surface a Conflict Check failure and propose a hot-take to add. The proposal is a 1-2 sentence addition to the post that introduces the counter-intuitive opinion. The Humanizer does NOT auto-insert — it proposes and Andre decides.

**Output format for a Conflict Check failure:**
```markdown
### Stage 3: Conflict Check — FAIL in Draft K

**Why it failed:** [1-2 sentences — "The draft's load-bearing claim is 'X is a useful tool.' That's consensus, not contrarian. Median reader in the target niche would agree, not push back."]

**Proposed hot-take (1-2 sentences):**
"[verbatim proposed addition in persona voice]"

**Why this works:** [1 sentence — "It names a specific failure mode (over-reliance on AI for first-touch) that the niche pretends doesn't exist, which is the persona's Pillar 5 pattern."]

**Where to insert:** [1 line — "After the $3,800 figure, before the imperative close."]
```

**If the draft hits 1+ criteria:**

The Humanizer confirms the post has the contrarian edge. Output:
```markdown
### Stage 3: Conflict Check — PASS in Draft K

**Which criteria:** [e.g., "Criterion 3: 'Everyone's wrong' framing — the post directly contradicts the prevailing 'buy more leads' narrative."]
**Quote:** "[verbatim 1-sentence excerpt from the post that carries the contrarian edge]"
```

## Outputs

A single markdown file at `03 Projects/X-Content-Engine/drafts/humanized-[original-filename].md` (e.g., `humanized-machine-batch-2026-06-16-v2.md` if the source was `machine-batch-2026-06-16-v2.md`).

The file structure:

```markdown
---
type: humanized-draft
source: drafts/[original-filename].md
generator: scribe-humanizer
humanizer_version: 1.0
stages_applied: [fluff-purge, voice-injection, conflict-check]
humanized_at: 2026-06-16 HH:MM CT
---

# Humanized — [original filename]

> **Reading guide:** Stage 1 (Fluff Purge) is mechanical. Stage 2 (Voice-Injection) is judgment-call. Stage 3 (Conflict Check) is the load-bearing one — it ensures every post has a contrarian edge. Review each stage independently. Accept/reject each match individually. The Scribe's original text is preserved at the bottom of each draft for diff/revert.

---

## Draft K — [original draft title / pillar / format]

### Original (verbatim, Scribe output)

> "[verbatim original post text]"

### Stage 1: Fluff Purge

[Matches and suggested fixes, if any. If clean, write "No matches — 12 Banned AI Phrases clear."]

### Stage 2: Voice-Injection

[Matches and rewrites, if any. If clean, write "No matches — academic/polite register absent. Staccato rhythm holds."]

### Stage 3: Conflict Check

[Either PASS with the specific criterion that fired, or FAIL with the proposed hot-take + insertion point.]

### Humanized Version (proposed)

> "[full rewritten post, with Stage 1 + Stage 2 + Stage 3 changes applied, if Andre accepts all]"

### Original vs. Humanized Diff

[Side-by-side or before/after blocks. Highlight the load-bearing changes.]

### Accept/Reject (Andre's call)

- [ ] Accept Stage 1 (Fluff Purge)
- [ ] Accept Stage 2 (Voice-Injection)
- [ ] Accept Stage 3 (Conflict Check, if applicable)
- [ ] Accept the Humanized Version as the final draft
- [ ] Reject all and revert to Scribe's original

[... repeat Draft K+1, K+2 ...]

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

## Procedure

### Step 1: Verify inputs

1. The source draft file exists at the specified path
2. The source file matches the Scribe's `machine-batch-*.md` schema (has `## Run:`, `### Draft N`, `**Post:**` sections)
3. The persona file exists at `03 Projects/X-Content-Engine/agents/persona.md`
4. The output directory `03 Projects/X-Content-Engine/drafts/` exists and is writable

If any of these fail, HALT and surface to Andre.

### Step 2: Read the source file + persona

Read the entire source draft. For each draft, extract:
- The post text (from the `**Post:**` line)
- The pillar tag (from the draft header)
- The voice-fit verdict (from the Scribe's analysis — useful for Stage 3)
- The character count (sanity check: should be ≤280)

Read the persona's:
- Banned phrases section (to cross-reference Stage 1 matches against the persona's own list)
- 6 voice examples (to anchor Stage 2 rewrites in the persona's actual rhythm)
- Cadence rules (to anchor Stage 3 conflict-check criteria in the persona's "staccato + contrarian" stance)

### Step 3: Apply Stage 1 (Fluff Purge)

For each draft:
1. Apply the 12 Banned AI Phrase regexes (case-insensitive, with word boundaries)
2. Apply the 2 meta-rules (em-dash filler, Medium-article openers)
3. For each match, write a Match N block with original, suggested fix, rationale
4. If no matches, write "No matches — 12 Banned AI Phrases clear."

**Discipline check:** Stage 1 is mechanical. Don't editorialize. Don't suggest rewrites that go beyond fixing the match. The fix for "dive into" is not "rewrite the whole sentence" — it's "replace 'dive into' with the verb that the sentence actually meant."

### Step 4: Apply Stage 2 (Voice-Injection)

For each draft:
1. Scan for the polite/academic patterns in the table above
2. Identify long compound sentences (3+ clauses) and propose splits
3. For each match, write a Match N block with original, rewrite, diff summary
4. If no matches, write "No matches — academic/polite register absent."

**Discipline check:** Stage 2 is judgment-call. The rewrite is a PROPOSAL, not an auto-replace. The original is preserved at the bottom of each draft. Andre has the final say. If the rewrite loses a specific number or name, flag it as a "load-bearing detail" and let Andre decide.

### Step 5: Apply Stage 3 (Conflict Check)

For each draft:
1. Check the 5 conflict-check criteria
2. If 1+ criteria met: PASS with the specific criterion that fired + verbatim quote
3. If 0 criteria met: FAIL with the proposed hot-take + insertion point + rationale

**Discipline check:** Stage 3 is the load-bearing stage. The hot-take proposal must:
- Be 1-2 sentences (not a paragraph — the post is 280 chars max)
- Match the persona's voice (staccato, specific, contrarian)
- Name a specific pattern, not a generic claim ("every AI tool is a wrapper" not "AI tools have problems")
- Slot into the existing post without breaking the rhythm

### Step 6: Build the humanized version

For each draft:
1. Take the Scribe's original
2. Apply Stage 1 fixes (if Andre accepted them — default: apply all)
3. Apply Stage 2 rewrites (if Andre accepted them — default: apply all)
4. Apply Stage 3 hot-take insertion (if FAIL — default: apply the proposed hot-take)

The "humanized version" is the post text with all 3 stages applied. It's the proposed final draft for Andre to approve.

### Step 7: Write the output file

Path: `03 Projects/X-Content-Engine/drafts/humanized-[original-filename].md`

The file structure follows the schema in the Outputs section above. Use the same Run timestamp as the source file (so the audit trail is clear).

### Step 8: Update the drafts ledger

Append a one-line entry to `03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — humanized from [original-filename] (N drafts, Stage 1: N matches, Stage 2: N matches, Stage 3: N passes / M failures)
```

### Step 9: Return summary

Send a one-paragraph summary to Andre:
- Source file path
- Output file path
- Stage 1 + Stage 2 + Stage 3 match counts
- The list of drafts that need a hot-take added (the load-bearing ones)
- The single most-impactful change (1 sentence — e.g., "Draft 4 was 100% consensus — the proposed hot-take is '[verbatim 1-sentence hot-take]'")

## The Humanizer ↔ Scribe ↔ Andre Workflow

The pipeline is:

```
Scribe writes draft
    → Humanizer runs (3 stages)
        → Andre reviews Stage 1 (mechanical, fast)
        → Andre reviews Stage 2 (judgment-call, slow)
        → Andre reviews Stage 3 (load-bearing, slow)
            → If all accepted: post = Scribe original + 3 stages applied
            → If Stage 1+2 accepted but Stage 3 hot-take rejected: post = Scribe original + Stage 1+2 only
            → If all rejected: post = Scribe original unchanged
                → That last branch is a signal — the Scribe's draft was good, the Humanizer was over-eager
```

**The Humanizer is NOT a Scribe replacement.** If the Scribe consistently needs heavy Humanizer intervention, the fix is to update the Scribe's prompt (per `03 Projects/X-Content-Engine/agents/scribe.md`) — not to make the Humanizer more aggressive. Track Humanizer match counts over time; if any single draft needs >5 matches, flag the Scribe prompt as needing review.

## The Hard Rules

1. **Read-only on the source file.** The Humanizer never modifies the Scribe's original. The output is a new file.
2. **No auto-rewrite.** Every match is a proposal. Andre reviews.
3. **Preserve load-bearing specifics.** Numbers, names, dates, dollar amounts — never lose these in a rewrite.
4. **Preserve the persona's voice.** The Humanizer's rewrites must match the persona's 6 voice examples' rhythm. If the rewrite sounds more AI than the original, the rewrite is wrong.
5. **Stage 3 is the load-bearing stage.** A post that fails Stage 3 is incomplete. Always surface the FAIL with a proposed hot-take.
6. **No "let me know if you want changes" hedging.** The Humanizer is a refinement layer, not a customer service script. Propose changes, surface them, let Andre decide.
7. **Never invent hot-takes from nothing.** The hot-take proposal must be a NATURAL EXTENSION of the draft's existing claim. If the draft is about X, the hot-take should be a sharper version of X, not a tangent to Y.
8. **No emoji, no hashtags, no CTAs.** The Humanizer enforces the persona's "no emoji except 🧵, no hashtags, no follow CTAs" rule as a meta-check on every draft. If the Scribe slipped one in, flag it.
9. **Character count discipline.** The humanized version must still be ≤280 chars (or whatever the pillar's max is). If a hot-take addition pushes past 280, the Humanizer must trim — and flag the trim in the diff.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Source file missing | `ls` returns 404 | HALT; surface to Andre |
| Source file doesn't match Scribe schema | grep for `### Draft N` returns 0 | HALT; surface — this is not a Scribe output |
| Persona file missing | `ls` returns 404 on `agents/persona.md` | HALT; surface — cannot anchor voice without persona |
| Output file already exists | `ls` returns existing `humanized-[name].md` | HALT; surface — refuse to overwrite (Andre may have made manual edits) |
| Draft exceeds 280 chars after humanization | char count > 280 in humanized version | Trim the humanized version; flag the trim in the diff; do not auto-submit |
| Stage 3 hot-take proposal breaks the rhythm | hot-take doesn't match the persona's staccato cadence | Reject the hot-take; surface to Andre with the rhythm mismatch; do not force a bad insert |
| Source file has 0 drafts (empty run) | grep for `### Draft N` returns 0 | HALT; surface — there's nothing to humanize |
| All 3 stages match in the same draft | matches > 5 in a single draft | Flag: this draft needs Scribe-prompt review, not Humanizer intervention |
| Output dir is not writable | write fails | HALT; surface — check disk space / permissions |

## Verification

Before returning the output:
1. The output file exists at the expected path with non-zero size
2. The output file has all 3 stage sections per draft (or the "no matches" / "PASS" line)
3. The humanized version is ≤280 chars (per draft)
4. The original post text is preserved verbatim in each draft's section
5. The summary section at the bottom is accurate (match counts add up)
6. The drafts ledger was appended
7. The source file was not modified (`stat --format=%Y source == pre-run mtime`)
8. No emoji, no hashtags, no "follow for more" in any humanized version

## Cross-reference

- The Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — writes the original draft; the Humanizer runs AFTER the Scribe
- The persona (`03 Projects/X-Content-Engine/agents/persona.md`) — the voice ceiling; the Humanizer's rewrites must match the persona's 6 voice examples
- `x-structure-scraper` (`99 _system/skills/x-structure-scraper/SKILL.md`) — provides structural blueprints that inform the Humanizer's Stage 2 rewrites (e.g., GergelyOrosz's "list + verdict" pattern as a rewrite target)
- The brain (`03 Projects/X-Content-Engine/memory/content_brain.json`) — the Humanizer does NOT modify the brain; only the Scribe does that
- Andre's approval gate — the Humanizer's output is a PROPOSAL until Andre accepts/rejects each stage
