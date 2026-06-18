# Noise Patterns — ea-research-brief

The 2024-2026 research literature has a high noise floor. The worker
must filter these patterns before treating any claim as evidence.

## Categories of noise

### 1. Stale scaling laws

Chinchilla (Hoffmann et al., 2022), the original scaling-law papers
— useful as historical context, but the field has moved on. If the
brief cites Chinchilla-optimal training, ask whether the conclusion
still holds for the model class actually in use.

**Filter:** cite as historical context only. Use a 2024+ source for
the current best-practice.

### 2. "AI replaces X" op-eds

Editorial content, not research. Cite the underlying study if there
is one; otherwise label as opinion in the brief.

**Filter:** the absence of a citation is the signal. If a claim
"AI replaces X" has no underlying study, it's an op-ed.

### 3. Model-launch marketing copy

Vendor announcements (GPT-X, Claude-Y, Gemini-Z) often lead with
optimistic capability claims. The benchmark numbers in the launch
blog are typically the vendor's best results, not reproducible.

**Filter:** cross-reference with independent benchmarks (MMLU,
HumanEval, AlpacaEval, HELM) before treating as fact. If only the
vendor's benchmark is cited, label as "vendor-reported, not
independently verified."

### 4. Pre-prints with retracted claims

Check if the paper has been retracted, corrected, or superseded.
arXiv pre-prints don't have peer review.

**Filter:** check arXiv retraction list, OpenReview, and the
paper's citation count (low citations on a 1+ year-old pre-print =
likely superseded or wrong).

### 5. Saturated benchmarks

MMLU saturated in 2024 for frontier models; the score is now
"100% ± noise" and tells you nothing. Same for HumanEval on
GPT-4-class models.

**Filter:** use the saturated-benchmarks addendum from
`ea-5-mistakes-audit` (Addition 7). When a worker cites a
saturated-benchmark number, ask for a current-benchmark or
runtime-evidence alternative.

## The noise audit

When the worker reports back, do a noise audit. For each cited claim,
classify as:
- **(a)** primary source directly verified
- **(b)** synthesis citing a primary source (verify the synthesis matches)
- **(c)** editorial / opinion (label as such)
- **(d)** stale / saturated / superseded (replace with current source)

The brief should contain only (a) and (b) with explicit labels.
(c) and (d) are demoted or replaced.

## What stays

- Primary research papers from peer-reviewed venues (with the year
  and venue in the citation)
- Vendor benchmarks that are independently replicated
- Working code / open-source implementations (the proof is in the
  running system, not the paper)
- Mavis's own runtime state (memory, skills, crons — the disk is
  always the ground truth)
