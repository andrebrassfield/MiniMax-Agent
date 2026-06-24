---
type: spec
status: proposed
date: 2026-06-22
source: 02 Notes/articles/2026-06-22 - 5-Stage-LLM-Pipeline.md
framework: 02 Notes/patterns/mavis-as-llm.md
estimated-spend: ~80K tokens (Phase 1 audit + Phase 2 prototype)
priority: P2 (high — these gaps are active failure modes, but no P1 incident yet)
---

# Spec: Mavis-as-LLM Upgrades (5-stage audit → concrete fixes)

> Inspired by the 5-stage LLM pipeline article (see source). The Mavis-as-LLM pattern gives us the audit framework; this spec proposes concrete upgrades for the gaps that audit surfaced. Each upgrade maps to a specific stage + a specific mistake the LLM literature has already mapped solutions for.

## Background

The 5-stage audit (see `02 Notes/patterns/mavis-as-llm.md`) identifies **3 active gaps** in Mavis's current design:

| Gap | LLM analog | Mavis status |
|---|---|---|
| No scaling law for skills | Mistake #3 — skipping scaling math | Open. Skills are 4-10KB; no codified ratio between skill instruction and vault context |
| No RLHF-analog feedback loop | Mistake #4 — stopping at SFT | Open. `ea-skill-evolution` exists but trigger is unclear |
| No formal benchmark suite | Mistake #5 — trusting perplexity after alignment | Open. Disease-detector cron exists but no representative-task eval |

These are not blockers — Mavis works. They're leverage points. Each fix has a high expected return because the LLM literature has already proven the analog works.

## Upgrade proposals

### Upgrade 1: Mavis Skill Scaling Law (Stage 3) — **IN PROGRESS 2026-06-22**

**Hypothesis:** A skill's instruction length should be ~1:10 to ~1:50 relative to the vault content it points to. Lean skills + rich vault = the Chinchilla scaling-law analog. AND, per the skill-bundles architectural insight, the audit must also consider **bundle cohesion** — which skills cluster, whether clusters have clean entry points, whether cluster token footprints are sustainable.

**Audit current state:**
- Survey all 50+ skills in `~/.mavis/agents/mavis/skills/`
- For each skill, measure: instruction length (bytes) + vault topic files it references (count + total bytes)
- Compute ratio distribution
- Identify outliers (>5KB skill with <1 vault reference, or vice versa)
- **NEW: cluster skills by natural affinity** (which skills reference the same vault topics, which skills cite each other, which skills are typically used together in the EA workflows)

**Deliverable:**
- New pattern note: `02 Notes/patterns/mavis-skill-scaling-law.md` with the codified ratio
- A `wc -l` audit script that produces a skill-vs-vault ratio report
- Proposed **skill bundle map** — which clusters are ready to bundle, which need work first
- Refactor 3-5 overstuffed skills to lean pointers + vault topic files (separate approval gate)

**Effort:** ~20K tokens (higher than original 15K estimate due to bundle-cohesion analysis). 2-3 hours.
**Risk:** Low. Refactoring skills can be done incrementally; each refactor is independently testable.

### Upgrade 2: RLHF-Analog Feedback Loop (Stage 4)

**Decision (locked 2026-06-22):** **LLM-based classifier** for trigger detection. Per Andre's call.

**Hypothesis:** Andre's mid-session corrections ("stop asking, decide", "no, do X not Y", "Want me to..." that get answered) are the RLHF signal. Capturing them systematically = the Mavis RLHF pipeline. An LLM classifier captures intent + implicit corrections (not just literal trigger phrases), which a regex matcher misses.

**Audit current state:**
- Survey last 7 days of vault for explicit corrections (e.g., the 2026-06-07 "stop giving me problems solve them" pattern)
- Count how many corrections produced skill/memory updates vs how many were lost
- Identify the gap: corrections that should have triggered skill evolution but didn't

**Deliverable:**
- New skill: `ea-correction-capture` — runs as a daily cron, scans recent sessions for correction patterns, proposes skill/memory updates
- **Trigger detection: LLM-based classifier.** Reads session transcripts (or memory entries), classifies each "Mavis did X, Andre said Y" pair as: `correction` / `preference` / `new-info` / `none`. Outputs a structured list with confidence scores.
- Calibration discipline (per Garry Tan): first run is **manual evaluation**, not auto-deployment. Run the classifier on 7 days of past sessions, surface candidates to Andre for review, calibrate threshold from confirmed-positive rate. Only THEN codify as the cron.
- Output: daily Telegram summary of proposed updates; one-tap approve/deny
- Integration with existing `ea-skill-evolution` skill

**Effort:** ~35K tokens (higher than original 30K estimate due to LLM classifier + calibration step). 4-5 hours.
**Risk:** Medium. LLM classifier has higher recall but lower precision → calibration step is the spam-control. The "first run = manual evaluation" rule prevents auto-spamming before the threshold is tuned.

### Upgrade 3: Mavis Benchmark Suite (Stage 5)

**Hypothesis:** A weekly eval against 10-20 representative tasks produces a Mavis-improvement signal that pure cron-based disease detection misses. The article calls this the human-benchmark equivalent post-alignment.

**Audit current state:**
- Identify the 10-20 task categories that cover Mavis's surface (research brief, daily brief, cold-start, draft-approval, fleet-router, state-audit, vault-health, etc.)
- For each, define a "representative query" + "expected behavior" baseline
- Set up a weekly cron that runs the queries (in dry-run mode where possible) and scores output against baseline

**Deliverable:**
- New skill: `ea-mavis-eval` — runs weekly, picks N representative queries, scores outputs, writes to `03 Projects/Mavis EA Design/reports/mavis-eval-YYYY-MM-DD.md`
- Initial benchmark set: 15 queries covering the main EA workflows
- Scoring rubric: 4 dimensions (correctness / efficiency / tone / task-completion), 1-5 each, total 4-20
- Trend tracking: weekly deltas, surface drift signals

**Effort:** ~35K tokens. 4-5 hours.
**Risk:** Medium-high. The "expected behavior" baseline is subjective; needs Andre's review. Risk of self-fulfilling eval (Mavis optimizes to score well, not to be useful). Mitigation: keep Andre-in-the-loop on baseline updates.

### Upgrade 4 (optional): "Mavis-as-LLM" Self-Audit Skill (cross-cutting)

**Hypothesis:** Codify the 5-stage audit as an executable skill, so Mavis can audit itself or any new capability proposal against the framework.

**Deliverable:**
- New skill: `ea-mavis-llm-audit` — takes a proposed change (skill, memory edit, vault entry, cron), runs the 5-stage audit, returns a verdict (durable / has gap / needs redesign) with specific recommendations
- Pair with existing `ea-state-audit` (the operational diagnostic) and `agent-harness-principles` (the framework trigger)

**Effort:** ~20K tokens. 2-3 hours.
**Risk:** Low. Pure diagnostic skill; no side effects.

## Priority ordering

If we can only do one: **Upgrade 1 (Scaling Law)**. Highest leverage, lowest risk, directly improves the skill library that's already at 50+ skills and growing.

If we can do two: **Upgrade 1 + Upgrade 2 (Feedback Loop)**. Together they close the "stopping at SFT" + "skipping scaling math" gaps simultaneously.

If we can do all three: **+ Upgrade 3 (Benchmark Suite)**. Closes the post-alignment eval gap. Requires Andre's involvement on baseline review — explicit permission gate.

Upgrade 4 (Self-Audit Skill) is a follow-on — useful once the framework has been validated against real upgrades.

## Success criteria

After 30 days:
- Upgrade 1: Skill library has documented ratio; overstuffed skills refactored; no skill >5KB without explicit justification
- Upgrade 2: Daily correction-capture cron running; ≥3 corrections captured and routed to skill/memory updates in the first month
- Upgrade 3: Weekly eval cron running; ≥3 weekly reports produced; drift detection flagged at least one issue for investigation

## Open questions for Andre

1. ~~**Upgrade 2 trigger precision:** the correction-detection matcher needs to be high-precision. Do you want me to start with a strict matcher (only explicit phrases like "stop asking, decide") and broaden later, OR use an LLM-based classifier from the start (higher recall, lower precision)?~~ **RESOLVED 2026-06-22: LLM-based classifier.** Calibration step deferred — see Upgrade 2 spec for rationale (post-refactor baseline needed; running classifier on pre-refactor data would be stale).

2. ~~**Upgrade 3 baseline:** who sets the "expected behavior" for the 15 representative queries?~~ **RESOLVED 2026-06-22 (implicit from "upgrade one first"):** Upgrade 3 deferred until Upgrade 1 + 2 land. Baseline ownership TBD when we revisit.

3. ~~**Skill library size:** 50+ skills is approaching the "skills library too big to navigate" zone. Is the goal to GROW the library or CONSOLIDATE?~~ **RESOLVED 2026-06-22: GROW.** And the future shape is **skill bundles for specialist agent workflows** — individual skills are units of work; bundles are the deployment unit (grouped skills for a specialist agent's vantage). **Architectural insight: load-bearing for Upgrade 1's audit criteria.**

4. ~~**Refactor target ceiling:** pragmatic (3-5KB) vs aggressive (1-2KB).~~ **RESOLVED 2026-06-22: AGGRESSIVE.** Chinchilla ideal. 1-2KB skill instruction + vault topic file for depth. Codified in `02 Notes/patterns/mavis-skill-scaling-law.md`.

5. ~~**Refactor first batch:** which skills first?~~ **RESOLVED 2026-06-22: ALL 10 ZERO-REF SKILLS + x-reply-guy.** Full first pass.

6. ~~**Bundle manifests:** write now or after refactor?~~ **RESOLVED 2026-06-22: AFTER refactor.** Skill shapes need to be stable before bundling.

7. **Metric for "Mavis is improving":** what does success look like to you in 30/60/90 days? Better brief quality? Faster response time? Less repetition? This shapes the benchmark suite. **Proposed default if not specified:** "Mavis requires fewer corrections per session over time" (measurable via the Upgrade 2 classifier once running).

## Architectural insight: skill bundles (locked 2026-06-22)

Andre's directive: **"skill library is to grow and then we will have skill bundles for specialist agent workflows."**

This adds a layer above individual skills:

- **Skill** = a single markdown procedure. Unit of work. Examples: `ea-cold-start`, `ea-draft-approval`, `ea-correction-capture`.
- **Skill bundle** = a named, curated set of skills deployed together for a specialist agent's vantage. Examples (proposed, not yet built):
  - `bundle: cold-start-ops` — `ea-cold-start` + `context-loader` + `two-link-rule` + vault-health-trigger
  - `bundle: daily-content-ops` — `ea-daily-brief` + `ea-research-brief` + `ea-weekly-connections` + vault-nightly-summarize
  - `bundle: quality-ops` — `ea-state-audit` + `ea-skill-evolution` + `ea-correction-capture` + disease-detector-trigger
  - `bundle: content-publish-ops` — `ea-draft-approval` + platform-specific posters + analytics trackers
- **Specialist agent** = a Mavis session configured to load a bundle on cold-start. NOT a separate agent in `~/.mavis/agents/` — it's the same chief-of-staff, scoped to a bundle.

**Implication for Upgrade 1:** the audit must consider not just individual skill size but also **bundle cohesion** — which skills naturally cluster, whether each cluster has a clean entry point, and whether the cluster's combined token footprint is sustainable in cold-start context.

## Cross-references

- **[[02 Notes/patterns/mavis-as-llm]]** — the pattern that produced this spec
- **[[02 Notes/articles/2026-06-22 - 5-Stage-LLM-Pipeline]]** — the source article
- **[[01-PERMANENT/2026-06-22 - active-theses]]** — Thesis 3 (Skills beat agents) and Thesis 4 (long-term knowledge in vault) are validated by this spec's analysis
- **[[03 Projects/Mavis EA Design/minimax-token-dialin-ledger-2026-06-22]]** — the dial-in cycle as a worked example of Upgrade 1's principles already applied to MEMORY.md/SOUL.md
- **[[~/.mavis/agents/mavis/skills/ea-state-audit/SKILL.md]]** — the existing audit skill that Upgrade 4 would build on

## Status

**Proposed.** Waiting for Andre's call on which upgrade(s) to prioritize. No work started. Each upgrade is independently executable; no dependencies between them.
