---
name: ea-research-brief
description: |
  Codifies the EA's research dispatch procedure for multi-source grounded
  briefs. Five stages: (1) scope the question + deliverable shape +
  disk anchors; (2) run the multi-regime safety frame (EU AI Act
  high-risk, FDA AI/ML + PCCP for medical, HIPAA for PHI, state-bar UPL
  for legal — HALT and escalate on any hit before proceeding); (3)
  apply the synthesis-doc audit pattern (citations are ground truth,
  fetch 1-2 to anchor, prose is synthesis and may be wrong); (4)
  filter stale scaling laws and editorial noise (Chinchilla, "AI
  replaces X" op-eds, vendor launch copy, saturated benchmarks like
  MMLU); (5) cross-reference against active runtime configurations
  (memory, skills, crons, recent dispatches). Triggers on "research
  this", "what do I know about X", "write a brief on Y", "investigate
  Z", "synthesize the X articles", and the EA `/deep-research`
  workflow. Do NOT load for single-source lookups, for topics the
  answer is already in MEMORY.md, or for research in other agents'
  trees (Mavis↔Hermes / Mavis↔OpenClaw / Mavis↔Socratic separation
  rules apply — file an incident card, do not dispatch).
---

# ea-research-brief

The EA's dispatch discipline for research. Encodes what Mavis does
*before* and *after* a worker reports back, so the brief is safe
(regulatory), grounded (primary sources, not synthesis), current
(filters noise), and runtime-aware (cross-references live state).

This is not a research-quality improvement. The Researcher agent and
`gepa-evaluator` handle the underlying eval. What this skill encodes
is the EA's procedure for safely dispatching research.

## Intent

- Take a research question from Andre
- Lock the scope (Stage 1)
- Pre-flight the regulatory regime (Stage 2)
- Dispatch a worker with primary-source anchoring requirements (Stage 3)
- Filter noise from the worker's report (Stage 4)
- Cross-reference the brief against live runtime state (Stage 5)
- Produce a brief that is safe + grounded + current + runtime-aware

The model decides *which* primary sources to anchor on, *which* noise
patterns to filter, and *which* runtime contradictions to surface. The
deterministic layer (4 regulatory regimes, dispatch prompt template,
output schema, noise patterns) lives in `references/`. Safety halts
and synthesis discipline live in `tests/`.

## When to run

**Triggers:**
- "research this" / "investigate X" / "what do I know about Y"
- "write a brief on Z" / "synthesize the X articles" / "summarize the literature on Y"
- "deep-dive on D" / "give me the full picture on F"
- The EA `/deep-research [topic]` workflow
- The source material has citation markers + a citation list
- The topic touches any of the 4 regulatory regimes
- The output will be cited in a downstream artifact (decision log, content brief, Scribe draft, Mavis report)

**Do NOT load for:**
- Single-step lookups ("what's the X API endpoint", "who wrote Y")
- Questions whose answer is already in `~/.mavis/agents/mavis/memory/MEMORY.md`
- Research being done for another agent's team (Mavis↔Hermes / Mavis↔OpenClaw / Mavis↔Socratic separation rules apply — file an incident card or escalate, do not dispatch)
- Topics where the answer is on a single canonical page (use `mavis-browser` skill + `WebFetch` directly)

## The 5 stages (high-level)

1. **Scope** — question in one sentence, deliverable shape, disk anchors
2. **Regime check** — 4 named regulatory regimes; HALT on any hit
3. **Primary-source dispatch** — worker prompt with anchoring requirements
4. **Noise filter** — separate signal from editorial / stale / saturated
5. **Runtime cross-reference** — verify against live memory/skills/crons

The 5-stage procedure is the intent. The full per-stage procedure
(specs, templates) lives in `references/`.

## Output contract

Every brief produced via this skill has the same 6-section structure
(full template in `references/brief-output-schema.md`):

1. Scope (Stage 1)
2. Primary sources (Stage 3)
3. Findings (the substance, with verbatim quotes for non-trivial claims)
4. Runtime cross-reference (Stage 5)
5. What I don't know (explicit gaps)
6. Verification (5-item checklist)

The brief ends with "What I don't know" — acknowledged unknowns beat
confidently-wrong claims.

## Resolver

Auto-invoke when:
- Andre asks a multi-source research question
- The source material has citation markers + a citation list
- The topic touches a regulated domain (medical, legal, credit, employment, biometric, critical infrastructure)

Do NOT auto-invoke for:
- Single-step lookups (use `WebFetch` or `mavis-browser` directly)
- Questions already in MEMORY.md
- Research for another agent's team (cross-team discipline applies)

## Hard halt conditions (these override the workflow)

- **Regime hit + no human-in-the-loop → HALT, surface to Andre, do not dispatch.** Brief is the precursor to a regulated product.
- **Login / paywall / unfamiliar UI on a primary source → HALT, flag to Andre, find open-access version.**
- **Primary sources contradict on a load-bearing claim → HALT, do not synthesize a "compromise," surface the contradiction.**
- **Worker reports a saturated-benchmark number as evidence → flag in noise audit, ask for current-benchmark or runtime-evidence alternative.**
- **Brief would require reading >50KB of source → consider splitting, or use `deep-research-agent` skill (designed for 50+ source scale).**

The regime hit is the load-bearing constraint. If a brief is the
precursor to a regulated product, the EA's value is escalation, not
silent dispatch.

## Cross-reference

- `references/regulatory-regimes.md` — the 4 named regimes (EU AI Act, FDA, HIPAA, UPL)
- `references/dispatch-prompt-template.md` — the worker dispatch template
- `references/brief-output-schema.md` — the 6-section output template
- `references/noise-patterns.md` — the editorial/stale/saturated filter
- `tests/safety-halts.md` — regime hit, login, contradictions
- `tests/synthesis-discipline.md` — citation anchor, quote-don't-summarize, what-I-don't-know
- `ea-contract.md` (Mavis memory) — the dispatch taxonomy + 5 EA behaviors
- `ea-5-mistakes-audit` — Addition 11 (4 regulatory regimes)
- `ea-data-quality-audit` — disk-evidence discipline
- `ea-loop-thinking` — the 5-stage loop as the meta-frame
- `deep-research-agent` — upstream skill for 50+ source scale
- Mavis MEMORY.md "Synthesis-doc audit pattern" — citation-vs-prose discipline
