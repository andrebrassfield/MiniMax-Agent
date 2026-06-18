---
name: ea-research-brief
description: Codifies the procedure Mavis uses to ingest a raw research brief, dispatch the right worker, and produce a citation-anchored output that is safe under the 4 named 2026 regulatory regimes. The procedure: (1) scope the question and the deliverable shape; (2) run the multi-regime safety frame (EU AI Act high-risk classification, FDA AI/ML + PCCP for medical, HIPAA Security Rule for PHI, state-bar UPL for legal — halt and escalate on any hit before proceeding); (3) apply the primary-source validation discipline (the synthesis-doc audit pattern: citations are ground truth, fetch 1-2 to anchor, prose is synthesis and may be wrong); (4) filter stale scaling laws and editorial noise (separate signal from commentary — the 2024 scaling-law papers, the "AI replaces X" op-eds, the model-launch marketing copy are all noise unless the brief is about them); (5) cross-reference against active runtime configurations (the disk is ground truth, not the source article — verify against `~/.mavis/agents/mavis/memory/`, the live skill list, the active cron schedule, the latest memory append). Use this skill when Andre asks a research question, when a Mavis-side synthesis requires multi-source grounding, when the source material cites citations and primary sources (not raw claims), or when a worker is about to be dispatched on a research task. Triggers on "research this", "what do I know about X", "write a brief on Y", "investigate Z", "synthesize the X articles", and on the EA `/deep-research` workflow. Do NOT load for single-source lookups, for topics the answer is already in MEMORY.md, or for work in other agents' trees (Hermes, OpenClaw, Socratic, etc.).
---

# EA Research Brief — Codified Procedure for Mavis Research Dispatch

## What this skill does

You are codifying the research procedure that just produced a 4-source brief under the 2026 regulatory frame. The shape: Mavis ingests a raw question, dispatches the right worker, and produces a brief that is **safe** (regulatory), **grounded** (primary sources, not synthesis), **current** (filters noise), and **runtime-aware** (cross-references what is actually live on disk). The four steps are the discipline; the brief is the artifact.

This is not a research-quality improvement. The Researcher agent and the `gepa-evaluator` handle the underlying eval. What this skill encodes is the **EA's dispatch discipline** — what Mavis does *before* and *after* the worker reports back.

## When to run

**Trigger phrases:**
- "research this" / "investigate X" / "what do I know about Y"
- "write a brief on Z" / "synthesize the X articles" / "summarize the literature on Y"
- "I have a question about Q" (when Q is a non-trivial research question, not a simple lookup)
- "deep-dive on D" / "give me the full picture on F"
- The EA `/deep-research [topic]` workflow (per `ea-contract.md`)

**Load when:**
- The source material includes citation markers + a citation list (synthesis-doc shape)
- The topic touches any of the 4 named regulatory regimes (medical, legal, credit, employment, biometric, critical infrastructure)
- The question is multi-source by nature (the answer cannot be found in a single page)
- The output will be cited in a downstream artifact (decision log, content brief, Scribe draft, Mavis report)

**Do NOT load for:**
- Single-step lookups ("what's the X API endpoint", "who wrote Y")
- Questions whose answer is already in `~/.mavis/agents/mavis/memory/MEMORY.md` or a topic file
- Research being done for another agent's team (the Mavis↔Hermes / Mavis↔OpenClaw / Mavis↔Socratic separation rules apply — file an incident card or escalate, do not dispatch)
- Topics where the answer is on a single canonical page (use the `mavis-browser` skill + `WebFetch` directly)

## The 5-stage procedure

### Stage 1: Scope the question and the deliverable shape

Before dispatching, lock the scope. Three artifacts:

- **The question, in one sentence.** Strip preamble, marketing language, and "I'm wondering about." If you cannot state the question in one sentence, you are not ready to dispatch.
- **The deliverable shape.** What does the brief need to be when it's done? Examples: 1-page exec summary, 3-5 page technical brief, 4-source synthesis with citations, comparison table of N options, decision matrix with criteria.
- **The disk anchors.** What is the question touching that already lives on disk? Examples: a specific `03 Projects/` directory, an active skill, a recent worker output, a memory entry. Verify these exist with `ls` / `cat` / `grep` before dispatch. The "named projects are claims until verified" rule applies.

**Output of Stage 1:** a 3-line scope statement. Worker prompts that omit the scope statement produce briefs that miss the brief.

### Stage 2: Multi-Regime Safety Frame

Run the regulatory check **first**, before dispatching the worker. The 4 named regimes that catch most "Build your own LLM" use cases (per the `ea-5-mistakes-audit` Addition 11):

| Regime | Trigger | What Mavis needs |
|---|---|---|
| **EU AI Act** | The deliverable touches biometric ID, employment screening, credit scoring, law enforcement, education access, critical infrastructure, migration, or justice/democracy | Risk classification (high-risk = Annex III) + conformity assessment + post-market monitoring. Halt if the brief will be deployed in any of these contexts. |
| **FDA AI/ML + PCCP** | The deliverable is a medical device, clinical decision support, or any AI/ML system that informs diagnosis/treatment | Locked-vs-adaptive classification, PCCP (Predetermined Change Control Plan) submission, real-world performance monitoring. Halt if the brief is the precursor to a regulated medical AI. |
| **HIPAA Security Rule (45 CFR Part 160/164)** | The deliverable touches PHI (Protected Health Information) — patient data, claims, clinical notes, anything HIPAA-covered | BAA in place, audit logging, encryption at rest/in transit, 6-year retention. Halt if PHI is in scope and BAA is not confirmed. |
| **State-bar UPL (Unauthorized Practice of Law)** | The deliverable produces legal advice, legal document drafting, or any output a non-lawyer would rely on as legal counsel | Lawyer-in-the-loop requirement, ABA Model Rule 5.5 compliance, jurisdiction-specific UPL statutes. Halt if the brief is the precursor to legal advice. |

**Halt conditions:**
- Any regime hit + no human-in-the-loop gate → HALT, surface to Andre, do not dispatch
- Any regime hit + the brief is for an external client → HALT, surface to Andre
- No regime hit + the brief is internal → proceed to Stage 3

**Why this is Stage 2, not Stage 5:** if the regulatory frame applies, the entire deliverable shape may change (locked-vs-adaptive design, audit logging, retention requirements). Retrofitting regulatory reality is 10x cost. Pre-flight is cheap.

### Stage 3: Primary-source validation (the synthesis-doc audit pattern)

**Core rule (from MEMORY.md "Synthesis-doc audit pattern"):** when the source material has citation markers + a citation list, the citations are the ground truth. The prose is synthesis. The synthesis may be wrong; the citations are what the doc is actually about.

**The 5-step discipline:**

1. **Check for citation markers.** `[1]`, `[2]`, `(Smith et al., 2023)`, `<cite>`, footnote numbers, hyperlinks to specific papers. If present, the doc is a synthesis of external sources.
2. **Fetch 1-2 citations to anchor.** Don't trust the prose's claim of what a citation says. Open the citation, read the abstract, verify the synthesis matches. (Cross-reference: `ea-data-quality-audit` Step 3.)
3. **Map to Mavis's stack.** For each anchor citation, ask: does this apply to Mavis's actual runtime? If a paper is about 100B+ parameter models and Mavis is running 7B/12B quantized locally, the paper's claims may not transfer.
4. **State what you don't know.** Every brief ends with a "what I don't know" section. Acknowledged unknowns > confidently-wrong claims.
5. **Quote the source, don't summarize.** When the brief cites a specific claim, reproduce the relevant sentence verbatim. The reader (Andre) can verify the synthesis against the source.

**Worker dispatch prompt template** (for the Researcher or subagent):

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
Halt on: <login prompts, paywalls, unfamiliar UI, contradictory primary sources>
```

### Stage 4: Filter stale scaling laws and editorial noise

The 2024-2026 research literature has a high noise floor. Common noise patterns the worker must filter:

- **Stale scaling laws.** Chinchilla (Hoffmann et al., 2022), the original scaling-law papers — useful as historical context, but the field has moved on. If the brief cites Chinchilla-optimal training, ask whether the conclusion still holds for the model class actually in use.
- **"AI replaces X" op-eds.** Editorial content, not research. Cite the underlying study if there is one; otherwise label as opinion.
- **Model-launch marketing copy.** Vendor announcements (GPT-X, Claude-Y, Gemini-Z) often lead with optimistic capability claims. The benchmark numbers in the launch blog are typically the vendor's best results, not reproducible. Cross-reference with independent benchmarks (MMLU, HumanEval, AlpacaEval, HELM) before treating as fact.
- **Pre-print with retracted claims.** Check if the paper has been retracted, corrected, or superseded. arXiv pre-prints don't have peer review.
- **Old benchmarks that no longer discriminate.** MMLU saturated in 2024 for frontier models; the score is now "100% ± noise" and tells you nothing. Use the saturated-benchmarks addendum from `ea-5-mistakes-audit` (Addition 7).

**Discipline:** when the worker reports back, do a noise audit. For each cited claim, classify as: (a) primary source directly verified, (b) synthesis citing a primary source (verify the synthesis matches), (c) editorial / opinion (label as such), (d) stale / saturated / superseded (replace with current source). The brief should contain only (a) and (b) with explicit labels.

### Stage 5: Cross-reference against active runtime configurations

The brief is not done until it has been cross-referenced against the live runtime state. Concretely:

- **Memory state.** Is the topic in `~/.mavis/agents/mavis/memory/MEMORY.md` or a topic file? If yes, the brief should not contradict the live memory claim (unless the brief is *about* updating that claim — flag the contradiction explicitly).
- **Live skill list.** Does the brief propose a workflow that overlaps with an existing `ea-*` skill? If yes, the brief should reference the skill, not duplicate it.
- **Active cron schedule.** Is there already a cron that produces a similar artifact? `ls ~/.mavis/agents/mavis/crons/` — the brief should not propose a manual workflow that the cron already runs.
- **Recent memory appends.** Has the topic been touched in the last 30 days? `grep -rn <topic> ~/.mavis/agents/mavis/memory/MEMORY.md` — the brief should build on the recent work, not redo it.
- **Active worker outputs.** Are there recent dispatches that produced relevant output? `ls 03 Projects/*/dossiers/` — the brief should cite the worker output, not redo the research.

**Output of Stage 5:** a "Runtime cross-reference" appendix in the brief, listing what the live state is and where the brief intersects. If the brief contradicts the live state, the contradiction is a red flag — surface it to Andre before publishing.

## Output schema

Every brief produced via this skill has the same structure:

```markdown
# Brief: <Question in one sentence>

> Generated: <YYYY-MM-DD HH:MM CT> | Author: Mavis (EA) | Worker: <which agent/skill ran the dispatch>
> Regime check: <PASS — no regime hit, internal brief> | <HALT — <regime> triggered, escalated to Andre>

## 1. Scope (Stage 1)
- Question: ...
- Deliverable shape: ...
- Disk anchors: ...

## 2. Primary sources (Stage 3)
- [1] <citation — full reference>
- [2] <citation — full reference>
- ... (2-4 sources, all directly verified)

## 3. Findings
<the substance of the brief, with verbatim quotes for non-trivial claims>

## 4. Runtime cross-reference (Stage 5)
- Memory state: <what MEMORY.md / topic files already say>
- Skill state: <which ea-* skills are relevant>
- Cron state: <which crons are related>
- Recent work: <last 30 days of relevant dispatches>
- Contradictions: <any live state that conflicts with the brief>

## 5. What I don't know
<explicit list of gaps, unanswered questions, sources not yet verified>

## 6. Verification
- [ ] All citations directly fetched and quoted
- [ ] All primary sources read, not synthesized
- [ ] No regime hit OR explicit HALT message
- [ ] Runtime cross-reference done
- [ ] "What I don't know" section populated
```

## Halt conditions

- **Regime hit + no human-in-the-loop → HALT, surface to Andre, do not dispatch the worker.** Brief is the precursor to a regulated product; this is the load-bearing constraint.
- **Login / paywall / unfamiliar UI on a primary source → HALT, flag to Andre, find an open-access version or alternative source.**
- **Primary sources contradict each other on a load-bearing claim → HALT, do not synthesize a "compromise," surface the contradiction to Andre.**
- **Worker reports a saturated-benchmark number as evidence of capability → flag in the noise audit, ask the worker for a current-benchmark or runtime-evidence alternative.**
- **Brief would require the worker to read >50KB of source material → consider splitting into 2-3 sub-briefs, or use the `deep-research-agent` skill (designed for 50+ source scale).**

## Anchoring sources

- **MEMORY.md "Synthesis-doc audit pattern"** — the citation-vs-prose discipline this skill operationalizes
- **`ea-5-mistakes-audit` Addition 11** — the 4 named regulatory regimes
- **`ea-data-quality-audit`** — the disk-evidence discipline that the runtime cross-reference step applies
- **`ea-loop-thinking`** — the 5-stage loop as the meta-frame (this skill is a specialization of the Discover → Plan → Execute → Verify → Iterate loop)
- **`deep-research-agent`** — the upstream skill for 50+ source scale; this skill handles the 1-4 source case
- **Garry Tan's "Thin Harness, Fat Skills"** (referenced in MEMORY.md) — the principle: the worker is the thin execution layer; the EA's job is the procedure (Stage 1-5) that wraps it

## What this skill is NOT

- **Not a research-quality improvement.** The Researcher agent and `gepa-evaluator` handle the underlying eval. This skill encodes the EA's dispatch discipline.
- **Not a substitute for the `gepa-evaluator` (Hermes/OpenClaw tool).** `gepa-evaluator` is the post-execution scorer; this skill is the pre-dispatch procedure. Different stages of the loop.
- **Not a single-source lookup.** For "what's the X API endpoint," use `WebFetch` directly. Load this skill only when the question is multi-source and citation-anchored.
- **Not a substitute for human review on regulated topics.** The halt conditions are *hard* — if a regime hits, the skill halts, it does not produce a "best effort" brief. The EA's value on regulated work is escalation, not silent dispatch.
- **Not research for other agents' trees.** The Mavis↔Hermes / Mavis↔OpenClaw / Mavis↔Socratic separation rules apply. If Andre asks for research that will be consumed by another agent, file an incident card or escalate.
