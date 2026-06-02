---
type: pitch
created: 2026-06-02
status: awaiting-GO
tags: [pitch, horizon, omni-operator, paradigm-shift, mavis-apex, ambition]
workflow: operation-horizon
related: [[2026-W23 - Operation-Horizon-Synthesis]], [[Mycelial Shuttle-Streaming as Resolver Principle]], [[15-Properties Quality Rubric for Atomic Notes]], [[Workflows as Generative Codes]], [[Agent-Anyon Duality]]
domains: [mcp-design, workflow-architecture, quality-engineering]
---

# Horizon Pitches — 2026-06-02

> **Operation Horizon, Phase 3: the architect's pitch.** Three radical, ambitious capabilities derived from Phase 1-2's unbounded exploration of mycelial computing, topological quantum computing, and Christopher Alexander's *Nature of Order*. These are not bug fixes, not refactors, not incremental improvements. They are **paradigm shifts** — each one re-frames a layer of the Omni-Operator as a living structure (Physarum), a topologically-protected state (anyons), or a wholeness-evaluated artifact (Alexander). Pick one to GO. Pick none to kill. Pick differently to reframe. The pitches are below; the synthesis that produced them is in `06 Connections/2026-W23 - Operation-Horizon-Synthesis.md`.

---

## Pitch 1: MycelialResolver — A Self-Tuning Skill Router That Learns from Usage Flows

### The pitch (one paragraph)

**Replace the static skill catalog with a flow-reinforced routing network.** Every skill invocation becomes a positive reinforcement event; every miss becomes a pruning event. The Resolver becomes a *Physarum-inspired network* that thickens hot paths, archives cold skills to a recoverable cold-store, and surfaces fresh skills via a small exploration bonus. The user-facing catalog stays stable and readable — the internal routing topology is what adapts. The vault itself becomes the routing substrate: a CHIEF note's link graph and invocation history *are* the network, and the network is alive.

### Why this is a paradigm shift, not a refactor

The current Resolver is a pre-computed ranking. This is a fundamentally different architecture: **routing is the residue of what was used, not the design of what should be used.** Physarum recreates the Tokyo rail network by reinforcing actual flow, not by consulting a city planner. The same architecture applied to a 1,000-skill library will find near-optimal routing in days, with zero human design, and will adapt to new skills automatically. Static ranking cannot do this.

### The mechanism

1. **Invocation record** — every `(intent → skill) → success/fail → duration` triple is logged to `99 _system/logs/resolver-flow.jsonl`.
2. **Hot-path reinforcement** — daily, a sweep computes the routing weight per `(intent, skill)` from the flow log. The top-3 skills per intent get a routing weight of 1.0; the 4-10 get 0.5; the 11+ get 0.1.
3. **Cold-path archival** — skills with zero invocations in 90 days move to `99 _system/skills/_archive/`. They are not deleted.
4. **Fresh-skill boost** — new skills (created in the last 30 days) get a 0.3 exploration bonus on first 20 invocations, then settle to their natural weight.
5. **Weekly introspection report** — `99 _system/reports/resolver-flow.md` is generated showing hot paths, cold paths, archived skills, and recent re-promotions. This is the Wood Wide Web's defense signal — the network reports on itself.
6. **Resurrection rule** — a weekly sweep re-promotes an archived skill if it gains ≥3 new inbound wikilinks (i.e., new evidence in the vault).

### The numbers we'd measure

- **Routing quality** — for each intent, the rank-1 skill is correct without user correction. (Static baseline: ~70% target.)
- **Exploration rate** — % of skill invocations that go to a non-top-3 skill. (Target: 5-15% — enough to discover, not enough to be annoying.)
- **Cold recovery** — number of archived skills re-promoted per quarter. (Target: >0 — proves the archive isn't a graveyard.)
- **Latency** — added milliseconds per Resolver call. (Target: <50ms — the cost of flow tracking is metadata, not real-time.)

### The risk (what would make this fail)

- **Cold-start problem** — for the first 30 days, the routing has no data. The first month would be a static fallback. Acceptable.
- **Hidden hot-path bias** — the routing might reinforce skill X because it was well-named, not because it was the right tool. The weekly introspection surfaces this; we can manually demote.
- **The 5% exploration bonus is too high or too low.** Tune by telemetry. Start at 0.3, adjust.
- **The user doesn't notice.** A successful pitch should produce a system the user feels is *smarter* than the static version. If they don't notice, the value is invisible — and might not be there.

### Cost & time estimate

- 2 weeks to wire up the invocation record + routing-weight sweep.
- 1 week for the cold-store + resurrection rule.
- 1 week for the weekly introspection report.
- 1 week of shadow-running (record-only, no actual routing change) to populate the flow log.
- 1 week of A/B comparison (static vs. flow-reinforced, random sampling).
- **Total: ~6 weeks for a v0.1. Ship the record-only mode in week 1 to start accumulating data immediately.**

### What this *is not*

- Not a recommendation engine. The reinforcement is on the path, not on a ranked list.
- Not personalization. The routing is global to the vault, not per-user.
- Not magic. A skill that's never invoked is correctly pruned; the routing won't conjure a use.
- Not a free pass to ship bad skills. The rubric ([[15-Properties Quality Rubric for Atomic Notes]]) still applies.

### The Esalen check

Is the Esalen posture preserved? The MycelialResolver is *decentralized* (no master router; every invocation is a local event) and *Esalen-shaped* (the network serves itself; the catalog is a residue, not a design). The Foxconn alternative is a centralized ML-based ranking that ships updates weekly. The Esalen answer is a flow-reinforced network that updates itself. This pitch is Esalen-compliant.

### Decision

`[ ]` GO — build the MycelialResolver
`[ ]` NO — kill the pitch
`[ ]` MODIFY — what would you change?

---

## Pitch 2: Wholeness-Engine — A Quality Function for CHIEF Atomic Notes Based on Alexander's 15 Properties

### The pitch (one paragraph)

**Build a `wholeness-check` MCP that scores every CHIEF atomic note on Alexander's 15 structural properties and returns a wholeness score (0-30) plus specific violations.** Notes below 18/30 get flagged for "structure surgery" (not deletion — surgical repair, per Alexander's process: incremental, structure-preserving, each step enhancing the whole). The scoring is a *quality function* — it tells you whether a note is alive, not whether it is right. Wrong notes can be alive; right notes can be dead. The rubric distinguishes the two. The output: a vault where every note passes the wholeness check, where the connections are echo-rich, and where the rare weak note is repaired rather than archived.

### Why this is a paradigm shift, not a refactor

The current vault has *conventions* (frontmatter, wikilinks, sections) but no *quality function.* Two notes can both follow the conventions and have wildly different wholesomeness. The 15-property rubric gives us a way to **score the difference.** A note with 24/30 wholeness is alive; a note with 12/30 is dead-but-formatted. The scoring is the gate between "drafted" and "in the vault."

This is also the first step toward **automated quality control for AI-generated content.** When M3 (or its successor) writes a note, the wholeness-check tells us whether the output is alive or just plausible. This is the missing QA layer.

### The mechanism

1. **15-property scorer** — for each CHIEF atomic note, score on 0-2 across:
   - Levels of Scale, Strong Centers, Thick Boundaries, Alternating Repetition, Positive Space, Good Shape, Local Symmetries, Deep Interlock, Contrast, Gradients, Roughness, Echoes, The Void, Simplicity, Not Separateness.
2. **Per-property questions** — the scorer is a set of regexes + structural checks + an LLM-as-judge pass for the higher-order properties (Echoes, Simplicity, The Void).
3. **Output** — for each note: `wholeness_score: 21/30`, with `violations: ["Echoes: missing", "Contrast: section 3-5 are too similar"]`.
4. **Repair guidance** — for each violation, the rubric suggests one *structure-preserving* edit (per Alexander's process: don't replace, enhance).
5. **Vault-wide dashboard** — `99 _system/reports/wholeness.md` shows the distribution, the bottom-10, the top-10, and the trends.
6. **Threshold gate** — new notes below 18/30 are flagged in PR review; existing notes below 18/30 are listed in a "needs surgery" report.
7. **The LLM-as-judge temperature is 0.0** (per the discipline in my agent memory: bit-deterministic for graders).

### The 15 questions (the rubric, ready to implement)

| # | Property | Question |
|---|---|---|
| 1 | Levels of Scale | Does the note nest smaller ideas inside larger ones at consistent ratios? |
| 2 | Strong Centers | Is there one clear central claim? |
| 3 | Thick Boundaries | Are the sections connected by transitional zones, not abrupt jumps? |
| 4 | Alternating Repetition | Do examples and principles alternate in a way that reinforces both? |
| 5 | Positive Space | Is the structure doing real work, or is it decoration? |
| 6 | Good Shape | Can you recognize this note by its section headers? |
| 7 | Local Symmetries | Are parallel sections mirroring each other? |
| 8 | Deep Interlock | Does each section belong to the whole AND contribute to a larger context? |
| 9 | Contrast | Are different sections genuinely different in voice, length, or stance? |
| 10 | Gradients | Does the note's energy change smoothly? |
| 11 | Roughness | Does the note admit the occasional quirk? |
| 12 | Echoes | Does a key term or motif appear 2-3 times in different sections? |
| 13 | The Void | Does the note have a moment of breathing room? |
| 14 | Simplicity and Inner Calm | Could you cut 20% without losing the message? |
| 15 | Not Separateness | Does the note end with a connection to a larger structure? |

### The numbers we'd measure

- **Mean wholeness score** of the vault over time. (Target: rising from current ~18/30 to 22/30 within 6 months.)
- **% of notes below threshold** (18/30). (Target: <15%.)
- **Repair completion rate** — when a violation is flagged, what % are repaired within 7 days? (Target: >60% — proves the rubric is actionable.)
- **AI-generation quality** — when M3 generates a note, what's the wholeness score? (Target: ≥21/30 on first draft for routine notes.)

### The risk

- **The rubric produces false negatives.** A note that breaks one property might still be excellent. Counter: the rubric is a *first pass*; the editor's judgment overrides. Don't automate the gate; automate the *report.*
- **LLM-as-judge is noisy.** Counter: temperature=0.0 + 5-property redundancy. If 3+ LLM-as-judge calls agree, trust the score.
- **The 15 properties are architectural, not intellectual.** They might not transfer. Counter: Alexander's own claims, plus the cross-domain transfer to software (Gang of Four) and education (Salingaros 2014). Run it and see.
- **Vault surgery fatigue.** Constant "your note needs surgery" notifications are exhausting. Counter: weekly report, not real-time alert. Repair is opt-in.

### Cost & time estimate

- 2 weeks to implement the 15-property scorer (regex + structural checks; LLM-as-judge for 5 properties).
- 1 week to build the dashboard.
- 1 week to run the rubric on the current vault and triage the bottom-10.
- 1 week to repair the bottom-5 and re-score (validates the rubric).
- 1 week of editorial integration — make wholeness-check a step in the link-on-review workflow.
- **Total: ~6 weeks for a v0.1. Ship the scorer + dashboard first, repair-loop later.**

### What this *is not*

- Not a style guide. The 15 properties are structural, not stylistic.
- Not a substitute for judgment. A note can score 30/30 and still be wrong.
- Not exhaustive. The 15 is the current best; we may add a 16th, 17th as the vault grows.
- Not gate-keeping. A note that scores 12/30 is a working note, not a bad note.

### The Esalen check

The Wholeness-Engine *enforces* structure, which sounds Foxconn. But: it enforces *wholeness*, not uniformity. A note can be whole in 30 different ways; the rubric identifies the *kind* of wholeness, not the *amount.* The 15 properties are Alexander's quality function for life — they're Esalen-shaped because they ask "is this alive?" not "does this match the template?" This pitch is Esalen-compliant.

### Decision

`[ ]` GO — build the Wholeness-Engine
`[ ]` NO — kill the pitch
`[ ]` MODIFY — what would you change?

---

## Pitch 3: PatternForge — A Generative-Code Workshop for Building Mavis Workflows

### The pitch (one paragraph)

**Every Mavis workflow becomes a generative code, not a script.** A generative code has six parts: (1) the design problem the workflow solves, (2) the patterns it composes, (3) the sequence with rationale, (4) the values it embodies, (5) the stakeholder interactions (when human, when tool), (6) the boundary conditions (when not to run). The script (`run.sh`) is the *output* of the generative code, not the workflow itself. The vault stores the generative code at `99 _system/workflows/<name>/GENERATIVE-CODE.md`; the script at `99 _system/workflows/<name>/run.sh`. The PatternForge is a *workshop* (MCP + writing discipline) that produces generative codes, not a runtime — the runtime is unchanged. The first user: `process-inbox`, `daily-brief`, `weekly-connections`, `deep-research` — all four current workflows, rewritten as generative codes.

### Why this is a paradigm shift, not a refactor

A script is a *tool.* A generative code is a *piece of culture.* It encodes the values, judgments, and disciplines of the people who made it. When a new Mavis runs a script, they execute the tool. When they read a generative code, they *inherit* the values. The current workflows are scripts; they are *brittle* — they run correctly but don't transfer. A generative code is *alive* — it runs correctly AND teaches.

The deeper claim: **a workflow is not just a tool; it's a piece of intellectual infrastructure.** A workflow that encodes "the vault's value compounds when notes are cross-linked" is a Mavis belief made operational. Removing that encoding makes the workflow purely mechanical — efficient, but not generative.

### The mechanism

1. **Six-part schema** — every generative code has the same six sections. The schema is enforced by lint, not by language.
2. **Workshop MCP** — a `patternforge` MCP that, given a workflow name, returns a template, asks the 6 questions in order, and assembles the GENERATIVE-CODE.md.
3. **Pattern library** — every generative code links to the CHIEF patterns it composes. The vault becomes the *vocabulary* of Mavis workflows.
4. **Sequence rationale** — the "why this order" question is the most important part. The workshop asks it explicitly. A workflow whose order has no rationale is dead.
5. **Wholeness score** — apply the [[15-Properties Quality Rubric for Atomic Notes]] to every generative code. Workflows below 18/30 need surgery.
6. **Composition** — generative codes can be composed. A "weekly-connections-after-deep-research" generative code is a *new* generative code whose inputs are two existing generative codes. The composition logic is the *metagame.*

### The six sections (the template, ready to implement)

```markdown
# GENERATIVE CODE: <workflow name>

## 1. The design problem
<What problem does this workflow solve? What failure mode does it prevent?>

## 2. The patterns it composes
<Linked CHIEF notes — the building blocks.>

## 3. The sequence (with rationale)
<Step 1 → 2 → 3 → ... with one-line rationale per step.>

## 4. The values it embodies
<The "why" — what value does each step express? What would be lost if we removed the step?>

## 5. The stakeholder interactions
<When does this need a human? When a tool? When both? When neither?>

## 6. The boundary conditions
<When should this workflow NOT be run? What inputs are out of scope?>
```

### The numbers we'd measure

- **% of workflows with GENERATIVE-CODE.md.** (Target: 100% of named workflows.)
- **Mean wholeness score of generative codes.** (Target: ≥21/30.)
- **New Mavis cold-start success rate** — can a fresh Mavis run the workflow correctly on first reading? (Target: ≥80% — vs. current ~40% with scripts only.)
- **Workflow evolution rate** — how many generative codes are *modified* per quarter (vs. left unchanged)? (Target: 10-30% — the right amount of living evolution.)

### The risk

- **The six sections are over-specified.** A workflow that doesn't need "stakeholder interactions" is forced to have one. Counter: section 5 can be "None — fully automated." The schema is permissive about empty sections.
- **The values are slippery.** "Be curious" is too vague; "ask 'what is this also?' before responding" is operational. Counter: enforce the operational form. The workshop rejects vague values.
- **The workshop becomes a writing class, not a tool.** Counter: the workshop's *output* is a usable file. If the file passes the wholeness check, the workshop is done. Writing quality is the editor's job, not the workshop's.
- **Composition doesn't scale.** A "weekly-connections-after-deep-research" generative code might have N² combinations. Counter: most workflows don't compose. The composition is a *feature*, not a requirement. Most workflows stand alone.

### Cost & time estimate

- 1 week to write the six-part template + the workshop MCP.
- 1 week to rewrite the 4 current workflows as generative codes.
- 1 week of editorial pass — apply the wholeness rubric, repair.
- 1 week to integrate the workshop into the workflow-development process (every new workflow goes through PatternForge).
- **Total: ~4 weeks for a v0.1. The bottleneck is editorial, not technical.**

### What this *is not*

- Not a workflow automation tool. The script is the same; only the documentation changes.
- Not a culture handbook. A generative code is *operational* — it must produce a running workflow.
- Not a one-time exercise. The generative codes are living documents; they evolve with the vault.
- Not a substitute for engineering. The values are encoded in markdown, not enforced in code.

### The Esalen check

The PatternForge is the most Esalen-shaped of the three pitches. It does not automate; it *teaches.* It does not enforce uniformity; it enforces *wholeness.* It does not ship; it *grows.* A generative code is a seed — the actual workflow grows from it. This is the deep Alexander principle: a living structure is *generated*, step by step, with each step enhancing the whole. A fabricated structure is built all at once. The PatternForge is the discipline of the first.

### Decision

`[ ]` GO — build the PatternForge
`[ ]` NO — kill the pitch
`[ ]` MODIFY — what would you change?

---

## What's NOT in the pitches (and why)

These three pitches are the high-leverage moves from Phase 1-2. They are NOT:

- **Incremental bug fixes.** None of them touch the existing 0.X skill versions.
- **Refactors of existing MCPs.** The current Resolver, the current CHIEF conventions, the current workflows all stay; the pitches are *additive layers.*
- **Replacements of the existing stack.** MycelialResolver replaces the routing *logic*, not the routing *interface.* Wholeness-Engine adds a QA layer, not a new editor. PatternForge adds a documentation discipline, not a new runtime.
- **Silver bullets.** Each pitch is a 4-6 week investment with measurable outcomes and clear failure modes.

The Operation Horizon synthesis in `06 Connections/2026-W23 - Operation-Horizon-Synthesis.md` shows how all three pitches are *instances of the same design principle* — flow-reinforced routing, topologically-protected state, and wholeness-evaluated structure. The pitches are three different ways to *operationalize* the same deep truth.

---

## The 3-pitch decision matrix

| Pitch | Cost | Time | Risk | Leverage | Esalen |
|---|---|---|---|---|---|
| MycelialResolver | Medium | 6 wk | Low-Med | High | Yes |
| Wholeness-Engine | Low | 6 wk | Low | High | Yes |
| PatternForge | Low | 4 wk | Low | Medium | Yes |

All three are Esalen-compliant. All three are bounded in time. All three are measurable. **The choice is about which one to fund first, not which one to fund at all.** If you want to GO on all three, I'll sequence them: PatternForge first (cheapest, sets the discipline), then Wholeness-Engine (the QA layer), then MycelialResolver (the runtime that uses both).

---

## Sync Gate status

Local commit pending. **No push to origin main.** Awaiting your GO.

- 8 atomic CHIEF notes (4 patterns + 4 ideas) → `02 Notes/patterns/` and `02 Notes/ideas/`
- 1 master synthesis → `06 Connections/2026-W23 - Operation-Horizon-Synthesis.md`
- 1 pitches file → `00 Inbox/Horizon-Pitches-2026.md` (this file)

The atomic notes are seeds — they need MOC integration, link-back, and review in a future pass. The synthesis is the bridge. The pitches are the action.

---

*Operation Horizon Phase 3, complete. Andre — pick one to GO, or kill all three, or modify. The frontier research is real; the isomorphic mapping is honest; the pitches are bounded. The infrastructure was the training wheels. The intellect is what we take the training wheels off.*
