---
name: scribe-humanizer
description: |
  Post-processor refinement layer for Scribe drafts. Reads a Scribe-generated
  draft (machine-batch-*.md), applies a 3-stage filter (Fluff Purge via
  banned-phrase regex / Voice-Injection that converts polite-academic into
  Dre Builds staccato / Conflict Check that requires at least one
  counter-intuitive opinion), and writes a humanized copy to
  `drafts/humanized-[original-filename].md`. The output preserves the
  original post text and adds a stage-by-stage diff so Andre can
  accept/reject each stage independently. Triggers: "humanize the drafts",
  "apply the humanizer", "refine the scribe output", "run the humanizer
  on [file]", "make the drafts less AI-sounding". Read-only on the source
  draft file. Auto-invoke when a Scribe batch is ready and Andre asks to
  refine it before approval. Do NOT use on non-Scribe drafts, on
  already-humanized files, or on drafts Andre has already approved.
---

# scribe-humanizer

The second-pass refinement layer for the X-Content-Engine. The Scribe writes
in @DreTheSalesGuy's voice, but the Scribe is an LLM and drifts toward
default "AI-flavored" register. The Humanizer catches what the Scribe
missed.

## Intent

- Read a Scribe batch file (`drafts/machine-batch-*.md`)
- Apply 3 filter stages in order:
  1. **Fluff Purge** — regex grep against the 12 Banned AI Phrases
  2. **Voice-Injection** — convert polite/academic into staccato
  3. **Conflict Check** — verify the post carries a counter-intuitive opinion
- Write a humanized copy with per-stage diff to `drafts/humanized-*.md`
- Append to the drafts ledger
- Report back: source path, output path, stage match counts, list of
  drafts that need a hot-take

The model decides *whether* a match is real (vs. a false positive) and
*what* the rewrite should be (the persona's voice is the ceiling). The
deterministic layer — the regex, the pattern tables, the output format —
lives in `references/`. Stage correctness is verified by the test cases
in `tests/`.

## The 3 stages (high-level)

| Stage | What it does | When to fail |
|---|---|---|
| 1. Fluff Purge | Regex grep against 12 banned phrases + 2 meta-rules | N/A — mechanical, no failure mode |
| 2. Voice-Injection | Detect polite/academic register, propose staccato rewrites | N/A — judgment-call, always proposes |
| 3. Conflict Check | Verify ≥1 of 5 contrarian criteria | If 0 criteria met, propose a hot-take to add |

**Never auto-rewrite.** Every match is a proposal. Andre accepts/rejects
each stage independently. The original is preserved verbatim in each
draft's section.

## When to run

**Triggers:**
- "humanize the drafts" / "apply the humanizer" / "run the humanizer on [file]"
- "refine the scribe output" / "make the drafts less AI-sounding"
- "post-process the machine batch"

**Auto-trigger (optional):** The chief can chain a Humanizer pass after
every Scribe dispatch. Default: manual trigger. Auto-pipeline requires
explicit Andre sign-off.

**Do NOT run for:**
- Drafts that are already humanized (running the Humanizer twice degrades)
- Non-Scribe drafts (one-offs, manual writing)
- Drafts Andre has already approved (changes the historical record)
- Files that don't match `machine-batch-*.md` schema

## Inputs

| Input | Default | Required |
|---|---|---|
| Source draft path | — | **yes** |
| Output filename | `humanized-[original-filename].md` | fixed |
| Persona reference | `03 Projects/X-Content-Engine/agents/persona.md` | yes |
| Blueprint reference | `03 Projects/X-Content-Engine/briefs/blueprints-*.md` | optional |
| Stage mode | "all 3 stages" | no — `fluff-purge-only`, `voice-injection-only`, `conflict-check-only` |

## Output contract

A single markdown file at `03 Projects/X-Content-Engine/drafts/humanized-*.md`
with one section per original draft, each containing: original text,
per-stage findings, proposed humanized version, diff, and Andre's
accept/reject checkboxes. The full file schema is in
`references/output-format.md`.

Plus a one-line append to `03 Projects/X-Content-Engine/drafts/_ledger.mdl`.

## Resolver

Auto-invoke when:
- A Scribe batch is ready (file matches `machine-batch-*.md`) and Andre
  asks to refine / humanize / process it
- Andre says "make the drafts less AI-sounding" and there's a recent
  Scribe batch in `drafts/`

Do NOT auto-invoke on:
- One-off drafts, manual writing, or non-Scribe files
- Files that already have a `humanized-*.md` companion

## Hard rules (load-bearing)

1. **Read-only on the source file.** The Humanizer never modifies the
   Scribe's original. The output is a new file.
2. **No auto-rewrite.** Every match is a proposal. Andre reviews.
3. **Preserve load-bearing specifics.** Numbers, names, dates, dollar
   amounts — never lose these in a rewrite.
4. **Preserve the persona's voice.** Rewrites must match the persona's
   voice examples' rhythm. If the rewrite sounds more AI than the
   original, the rewrite is wrong.
5. **Stage 3 is the load-bearing stage.** A post that fails Stage 3 is
   incomplete. Always surface the FAIL with a proposed hot-take.
6. **No "let me know if you want changes" hedging.** Propose, surface,
   let Andre decide.
7. **Never invent hot-takes from nothing.** The hot-take must be a natural
   extension of the draft's existing claim, not a tangent.
8. **No emoji, no hashtags, no CTAs.** Meta-check on every draft.
9. **Character count discipline.** The humanized version must stay
   ≤280 chars. If a hot-take addition pushes past, trim and flag the trim.

The discipline: if the Scribe consistently needs heavy Humanizer
intervention, the fix is the Scribe's prompt, not a more aggressive
Humanizer. Track match counts; flag drafts with >5 matches.

## Cross-reference

- `references/banned-phrases.md` — the 12 banned phrases + 2 meta-rules (Stage 1)
- `references/polite-patterns.md` — the polite/academic patterns (Stage 2)
- `references/conflict-criteria.md` — the 5 contrarian criteria (Stage 3)
- `references/output-format.md` — the humanized file template
- `tests/stage-1-fluff-purge.md` — Stage 1 eval cases
- `tests/stage-2-voice-injection.md` — Stage 2 eval cases
- `tests/stage-3-conflict-check.md` — Stage 3 eval cases
- `tests/read-only-discipline.md` — source file not modified
- The Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — the upstream
- The persona (`03 Projects/X-Content-Engine/agents/persona.md`) — the voice ceiling
- `x-structure-scraper` — provides structural blueprints for Stage 2 rewrites
