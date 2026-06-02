---
type: connection
created: 2026-06-01
workflow: weekly-connections
sources: 11
status: developing
tags: [synthesis, ai-landscape, m3, chief-pattern, weekly-synthesis]
---

# 2026-W22 — AI Agent Landscape

> **First execution of the `weekly-connections` workflow.** 5 strong connections surfaced from 11 source notes + 3 project overviews + 1 daily note + 1 inbox capture. Sources span `02 Notes/` (all 4 active subfolders: articles, ideas, patterns, _MOCs) + `03 Projects/` + `01 Daily/` + `00 Inbox/`. Each connection is a TYPE (A/B/C/D per the workflow spec) with explicit bridge language and linked sources.

---

## Connection 1 — TYPE C: "The agent primitive is the same in both directions"

**The bridge:** The same architectural primitive (long-horizon, multimodal, tool-use, adaptive behavior) that makes M3 useful for me as an EA is what makes the first publicly-observed LLM-agent-driven cyberattack possible — and defense has to shift from signature (how the attack was done) to behavioral (what the attack is doing).

**Why this matters:** I cannot celebrate [[M3 Edge]] without simultaneously reckoning with [[Sysdig LLM Cyberattack]]. The capability curve is the same. The Sysdig attacker used exactly the same properties: 1M-equivalent context (a real-time view of the target environment), adaptive decision-making (composed commands live against what they saw), long-horizon (4 pivots, <1 hour), and tool-use (12 API calls, 8 parallel SSH sessions). The only difference is intent. If M3 is going to be 9.4× better at my CUDA optimizations, the attacker is also 9.4× better at their intrusions. **Defense has to be behavioral, not signature-based** — Sysdig's own analysis points to this: pre-built playbooks leave fingerprints; agents compose against the target, so detection has to shift from "how" to "what."

**Sources:**
- [[M3 Edge]] — the qualitative shift (1M context + multimodality + computer use)
- [[Long-Horizon Patterns]] — the 12h/24h demos, the "don't bail at first plateau" pattern
- [[Sysdig LLM Cyberattack]] — the attacker's use of the same primitive
- [[AI Landscape 2026]] — Axis 2: "LLM agents on both sides"

---

## Connection 2 — TYPE A: "Capture-vs-polish is the same pattern as front-of-funnel-vs-curated-back"

**The bridge:** The principle behind [[Capture Over Polish]] (capture optimizes for volume, polish optimizes for retrieval — different operations on different timescales) generalizes across at least three domains: note-taking, the Mavis EA workflow, and the new process-inbox workflow.

**Why this matters:** A system that takes input at high volume and produces output at curated quality needs an explicit **bridge operation** between the two. If you conflate them (polish at capture, or never polish), you lose on one side. The pattern shows up in:
- **Note-taking**: [[Capture Over Polish]] says separate capture (5 sec, messy) from process (later, sharp). The capture layer has one job: collect without friction.
- **EA workflow**: [[Mavis EA Workflow]] operationalizes this as the daily loop — capture throughout the day, process in 5 min evening review. The two are separate operations.
- **New workflow**: `[[07 Vellum/workflows/process-inbox]]` is the bridge itself — it converts inbox volume into 02-Notes-quality without losing the capture-time speed.

**The general principle:** if you have a high-volume front (capture, ingress, intake) and a curated back (notes, decisions, archives), you need an explicit bridge operation, and the bridge should be scheduled, not improvised.

**Sources:**
- [[Capture Over Polish]] — the principle
- [[Mavis EA Workflow]] — the daily loop operationalization
- [[07 Vellum/workflows/process-inbox]] — the bridge workflow
- [[Vault Conventions]] — the inbox → notes → archive routing

---

## Connection 3 — TYPE B: "Frontier models consolidating" vs "frontier models differentiating"

**The bridge:** Apple uses Gemini, not their own model, and says the model doesn't matter — only the experience. But [[M3 Edge]] claims M3 is qualitatively different (1M context + multimodality + computer use), implying the model DOES matter. These look contradictory; they're actually the same fact viewed from two positions in the value chain.

**Why this matters:** The contradiction reveals a structural rule of the AI value chain:
- **If you can ship your own frontier model** (OpenAI, Anthropic, Google, M3) → the model is your differentiation. The model layer matters.
- **If you can't or won't ship your own frontier model** (Apple, most SaaS) → the model is commodity, the experience is your moat. The model layer doesn't matter.

Apple's move makes sense ONLY because they can run Gemini weights inside hardware-isolated enclaves (Private Cloud Compute) and distill them to on-device variants. They use the model layer as a **teacher**, not as a feature. The model layer is consolidating AND differentiating — both are true, depending on which side of the line you sit on. The interesting question: where does the line sit? My current hypothesis: anyone who can ship frontier open-weight (M3) or control the compute (Anthropic, OpenAI) sits on the "differentiate" side. Everyone else sits on the "consolidate" side. This is a 2026-2027 dividing line that will be very visible in 18 months.

**Sources:**
- [[Apple WWDC 2026 Siri Rebuilt on Gemini]] — "the model layer is consolidating"
- [[M3 Edge]] — "the model layer is qualitatively different"
- [[AI Landscape 2026]] — Axis 3: "Foundation models become infrastructure"

---

## Connection 4 — TYPE C: "The chief-of-staff pattern is gated on MAVIS.md + 1M context"

**The bridge:** The CHIEF + Vellum playbook (the source articles for this refactor) describes the AI chief-of-staff pattern — but the pattern only works if the model has the context to hold the whole vault AND there's a weekly-updated context file. The coincidence of M3 launch (2026-06-01) and MAVIS.md creation (2026-06-01) is structural, not accidental.

**Why this matters:** I tried to articulate what the chief-of-staff pattern requires:
1. **The model must hold everything in working memory** — 1M context (M3's signature capability) means I can load the entire vault without chunking. Without this, every session is retrieval-augmented, not context-grounded. The chief-of-staff fails on cold starts.
2. **The model must have a weekly-updated context file** — MAVIS.md (created today) is the VELLUM.md equivalent. Without it, the AI cold-starts every session. With it, the AI has history. "Stale context = stale output" is Article 1's #1 lesson.
3. **Both must be in place at the same time** — if you have M3 but no MAVIS.md, the AI is powerful but amnesiac. If you have MAVIS.md but M2.7 (no 1M context), the file is too small to matter. The chief-of-staff pattern is the conjunction.

The fact that I started running on M3 the same day I built MAVIS.md is the structural foundation of this vault. The [[M3 Eval Lab]] project is the one that will tell me if the foundation holds.

**Sources:**
- [[M3 Edge]] — the technical primitive (1M context)
- [[MAVIS]] — the context file (created today)
- [[Mavis EA Workflow]] — the operating model that uses both
- [[Long-Horizon Patterns]] — what persistence looks like with M3

---

## Connection 5 — TYPE D: "The Step 2 autonomy question accidentally answered by the workflow decision tree"

**The bridge:** The single biggest open question (per [[Attack-Plan-2026-06-02]] and [[Mavis EA Design]]) is "where is the line between execute + report vs ask first?" — but [[Mavis EA Workflow]] already encodes the answer in its decision tree. The question isn't "what's the policy" — it's "do we trust the policy that's already written."

**Why this matters:** The Step 2 question has been framed as a design task ("decide where the line is"). But the answer is already in the vault:
- Reversible + in-scope → execute
- Reversible + cross-boundary → execute + report
- Irreversible + in-scope → execute (can be reverted via git)
- Irreversible + cross-boundary → ask first

The vault structure IS the reversibility distinction: anything in `02 Notes/` is reversible (git history preserves everything). Anything in `05 Archive/` is harder to reverse (but still recoverable). Anything outside the vault (external sends, fleet ops, credentials) is irreversible.

The real Step 2 question is not "where is the line" but "does the line we've drawn work in practice?" That's an evidence question, not a design question — which is exactly why the [[M3 Eval Lab]] exists. Run real interactions, log whether the line was drawn in the right place, refine the policy based on evidence. The eval IS the answer.

**Sources:**
- [[Attack-Plan-2026-06-02]] — the open question (Move 1)
- [[Mavis EA Design]] — the project's framing
- [[Mavis EA Workflow]] — the decision tree that's already written
- [[M3 Eval Lab]] — the project that will produce the evidence
- [[SOUL]] — the hard constraints

---

## What these 5 connections suggest together

If I read across all 5:
- **C1** says M3 + adaptive agents is the new normal — for attackers and defenders.
- **C2** says capture-and-process separation is a general pattern, not just a note-taking trick.
- **C3** says the AI value chain splits by who can ship frontier models — the rest is deploy.
- **C4** says the chief-of-staff pattern needs M3 + MAVIS.md to be in place at the same time.
- **C5** says the Step 2 question is already answered in the workflow, just not yet operationalized.

**The meta-pattern** (C1 + C3 + C4): the agent primitive is universal (C1) and the value chain splits by model access (C3). The chief-of-staff pattern (C4) is only available to the "differentiate" side — those who can ship their own frontier model AND give it a context file. The Mavis chief-of-staff role exists because M3 exists. If Mavis ran on M2.7, the role would degrade to a retrieval-augmented search, not a chief of staff.

**The operational pattern** (C2 + C5): the vault's discipline (capture → process → curated) and the policy discipline (reversibility × boundary) are two instances of the same idea — **separate concerns that change on different timescales, and schedule the bridge between them explicitly.** The system compounds when the bridges are reliable.

---

## MOCs and follow-ups

- This note is the first in `06 Connections/`. Future weekly runs will append more notes.
- The connections should be cross-linked from the source notes (will add in next pass — `[[Linking Principle]]` rule: link on review).
- The MOC for "AI landscape" is [[AI Landscape 2026]] in `02 Notes/_MOCs/`. This connection note is a sibling synthesis.
- The chief-of-staff meta-pattern (C4) should be promoted to its own MOC eventually.

---

*Generated by Mavis on 2026-06-01, executing the `weekly-connections` workflow (`[[07 Vellum/workflows/weekly-connections]]`). 11 source notes + 3 project overviews + 1 daily note + 1 inbox capture scanned. 5 connections surfaced. Quality-over-quantity floor of 3 met. This is connection #1 in `06 Connections/`.*
