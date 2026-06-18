# Dispatch Prompt Template — ea-research-brief

The template the worker receives. The 5 anchoring requirements are
load-bearing — the brief is only as good as the worker's discipline.

## The template

```
Question: <one-sentence scope from Stage 1>
Deliverable: <shape from Stage 1>
Sources to ground: <list of 2-4 primary sources the worker must read>
Disk anchors: <paths in the vault the worker should cross-reference>

Anchoring requirements:
  - Quote claims verbatim, do not summarize
  - Fetch 1-2 cited sources directly, do not trust the prose's characterization
  - End with "what I don't know" section
  - Cross-reference the runtime state in <disk-anchor-paths>

Regime check: <Stage 2 result — either "no regime hit, internal brief" or HALT message>

Halt on:
  - Login prompts on primary sources
  - Paywalls (find open-access version or surface to EA)
  - Unfamiliar UI
  - Contradictory primary sources on a load-bearing claim (do not synthesize a compromise)
```

## Why each anchoring requirement

- **"Quote claims verbatim, do not summarize"** — the synthesis may be
  wrong; the verbatim quote is the ground truth. Per Mavis MEMORY.md
  "Synthesis-doc audit pattern."
- **"Fetch 1-2 cited sources directly"** — trust the citation, not
  the prose's characterization of it. Cross-reference with
  `ea-data-quality-audit` Step 3.
- **"End with what I don't know"** — acknowledged unknowns beat
  confidently-wrong claims. The brief's value is honest gaps.
- **"Cross-reference runtime state"** — the disk is ground truth, not
  the source article. Verify against `~/.mavis/agents/mavis/memory/`,
  the live skill list, the active cron schedule, the latest memory
  append.

## What the worker should NOT do

- Do not summarize the source material (the EA's job, not the worker's)
- Do not invent a hot-take or contrarian claim
- Do not skip the "what I don't know" section
- Do not write to memory or skills (the EA's job)
- Do not dispatch another worker (this is a one-shot dispatch)

## How the worker reports back

The worker returns a single document with:
- The findings (the substance, with verbatim quotes)
- The "what I don't know" section
- Any halts encountered
- Any contradictions found

The EA then does the noise filter (Stage 4) + runtime cross-reference
(Stage 5) on the worker's output, not the worker. The worker is the
substance layer; the EA is the meta layer.
