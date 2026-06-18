---
type: project
created: 2026-06-17
status: design
tags: [project, cpg, sepo, vault, self-evolving, mavis, minimax-m3]
related: [[Mavis EA Design]], [[Mavis-Apex-Architecture]], [[M3 Eval Lab]], [[Obsidian-Glass]]
related_skills: [ea-skill-evolution, ea-loop-audit, ea-closed-loop-builder, ea-5-mistakes-audit, vault-30day-auditor]
related_docs: [obsidian-local-rest-api-wiring]
domains: [self-improvement, prompt-optimization, vault-architecture, multi-agent]
source: Gemini research (2026-06-17) + Mavis audit + on-disk verification
---

# Cognitive Parameter Graph — Integration Blueprint for Mavis

> **TL;DR.** The Gemini doc describes a self-evolving vault: prompts as nodes, SePO loop, Leader-Worker-Verifier, GoldenSet + fitness scoring, fswatch daemon, Token Plan awareness. About **40% already exists** in pieces (skill evolution, MCP vault wiring, cron monitoring, harness principles). About **30% is genuinely new and worth building** (formal SePO loop, fitness scoring, GoldenSet rubrics, prompt-as-node schema). About **30% needs auditing** — some Gemini claims are unverifiable or conflict with Mavis's actual scope and existing structure.
>
> Recommended rollout: **Phase 1 = codification (1-2 days, ship now)**, **Phase 2 = SePO prototype for skills layer only (1-2 weeks)**, **Phase 3 = autonomous background loop (deferred — depends on Phase 2 fitness).**

---

## 0. Reality-check of the Gemini doc

Audit by claim. ✓ verified, ⚠ unverified, ✗ incorrect or misframed.

| # | Claim | Status | Evidence |
|---|---|---|---|
| 1 | "MiniMax M3 is a ~428B-param MoE activating ~22-23B/token" | ⚠ unverified | mavis `config.yaml` shows M3 is configured with `reasoning: true` but no architecture detail. Doc's param counts may be Gemini-estimated. Not load-bearing for design. |
| 2 | "MSA: 9.7x prefill, 15.6x decoding at 1M tokens vs M2.7" | ⚠ unverified | Specific numbers; can't verify without primary source. Architectural shape (sparse attention, KV block selection) is plausible. Not load-bearing. |
| 3 | "Mavis is a native multi-agent framework with Team Engine" | ✗ partially wrong | `mavis` is the runtime CLI; I'm **Mavis** (EA) — single agent, not multi-agent. `mavis-team` exists as opt-in skill for actual multi-agent plans. The doc conflates me with the runtime framework. |
| 4 | "Plus $20 / Max $50 / Ultra $120 token plans" | ⚠ unverified | Memory has `sk-cp-` prefix + `MINIMAX_API_KEY` env convention confirmed. Pricing tiers not in my memory. Treat as approximate. |
| 5 | "mmx-cli on npm" | ✓ verified | `npm view mmx-cli` → `mmx-cli@1.0.16`, bin `mmx`. Real package. |
| 6 | "Local REST API plugin on 27123/27124 with bearer auth + MCP endpoint" | ✓ verified | Just wired this tonight. Confirmed listening, 16 tools exposed, round-trip green. |
| 7 | "obsidian-shellcommands plugin" | ✗ not installed | Plugin isn't in `community-plugins.json`. Not strictly required — REST API + launchd can do everything this plugin does. Skip it. |
| 8 | "fswatch for filesystem events" | ✓ real, with caveat | brew-installable. launchd domain matters: `gui/501` vs `user/501` distinction per `tooling-gotchas.md`. Doc's plist uses `gui/$(id -u)` which is right for the user domain. |
| 9 | "Leader-Worker-Verifier adversarial loop" | ⚠ partially real | `mavis-team` skill exists for this, but only when explicitly invoked via `/mavis-team` slash command. Default Mavis runtime is single-agent. |
| 10 | "TPG = prompts as markdown nodes with frontmatter + evolution log" | ✓ verified, partial overlap | This is exactly what `99 _system/skills/ea-*/SKILL.md` already does. Skill layer is narrower than prompt layer (skills = procedural, prompts = any). |
| 11 | "SePO loop with fitness scoring + GoldenSet" | ✗ does NOT exist | No formal fitness score anywhere in the vault. `ea-5-mistakes-audit` is qualitative. `ea-loop-audit` checks loop shape, not output quality. **This is the genuinely new piece.** |
| 12 | "Mathematical formulation: F(P) = mean of G(f(x;P), y) over GoldenSet" | ✓ verified as math | Standard GEPA formulation. Memory has `ea-skill-evolution` skill that runs GEPA-anchored mutation. The math is right; the codification isn't. |
| 13 | "Vault structure: /Knowledge/, /System/Prompts/, /System/Evaluators/, /Output/" | ✗ conflicts with existing | Existing vault uses `00 Inbox/`, `01 Daily/`, `02 Notes/`, `03 Projects/`, `99 _system/`. Per MAVIS.md, this structure is load-bearing. **Do NOT rename.** Extend instead. |
| 14 | "Self-evolving prompts stored as notes" | ⚠ partially exists | `MAVIS.md` already has "Active Skill Mutations" changelog. That's SePO for the skill layer, manual-driven. The doc's version would automate it. |
| 15 | "Bidirectional sync via Local REST API / Port 27124" | ✓ verified | MCP wiring shipped tonight. `vault_read`, `vault_write`, `vault_patch` tools all live. |

**Bottom line:** the doc is a competent LLM-generated synthesis with the right conceptual shape and some factual specifics that need verification. Treat as **research input, not blueprint**. Map to existing systems; don't rebuild.

---

## 1. Mapping CPG concepts to existing Mavis infrastructure

This is where the doc earns its keep — translating concepts into reality. The point: most CPG components already exist; the integration is mostly **wiring**, not new builds.

| CPG concept (Gemini doc) | Already exists as | What's missing | CPG-specific? |
|---|---|---|---|
| TPG — prompts as nodes | `99 _system/skills/ea-*/SKILL.md`, MAVIS.md "Active Skill Mutations", `02 Notes/patterns/` | A schema that treats ALL prompts uniformly with fitness score + generation counter | Partially |
| SePO loop | `ea-skill-evolution` (GEPA-anchored mutation), `ea-loop-audit` (verification) | Formal fitness scoring function; GoldenSet as code; rolling re-eval cron | **YES** |
| GoldenSet | `ea-5-mistakes-audit` (10 qualitative dimensions) | Quantitative rubric with scoring; stored as test inputs with expected outputs | **YES** |
| Leader-Worker-Verifier | `mavis-team` skill (opt-in via `/mavis-team`) | Default-runtime mode; pre-baked team plans for recurring loops | Adjacent — `mavis-team` is real, just opt-in |
| fswatch + launchd daemon | Existing launchd services: `vault-watchdog`, `vault-daily-logger-daily`, `skill-build-monitor`, `skillopt-pilot-7am-report`, `pattern-library-weekly`, `content-research-daily`, `ea-draft-approval-daily` | Direct FSEvents → Mavis dispatch (currently cron-pulled, not event-pushed) | No — cron-based is fine for most use cases |
| fswatch for `/Knowledge/Inbox/` | `00 Inbox/` already exists; daily processing via `process-inbox` workflow (archived 2026-06-17, replaced by `ea-decision-logger` + `ea-research-brief`) | Real-time event-driven dispatch (vs daily pull) | Adjacent |
| MCP vault access | Just shipped: `obsidian-local-rest-api-wiring` skill | Nothing — done | — |
| Token Plan awareness | `03 Projects/Mavis-Apex-Architecture/06 Token Economics & Headroom.md` | Dynamic quota checking at runtime | Codified, just not automated |
| M3 reasoning modes (enabled/adaptive/disabled) | `config.yaml` shows `thinking_config: mode: forced_on` | Per-task mode selection (currently forced) | Adjacent |
| Bidirectional vault ↔ agent loop | New: MCP server `obsidian` with full CRUD tools | Verification gates on writes (commit to vault only after Verifier pass) | Partial |

**Two-thirds of CPG components have an analog or a stronger version in the existing system.** The integration is about connecting these pieces, not building them from scratch.

---

## 2. Architecture decisions (load-bearing)

These are decisions that shape everything downstream. I'm stating my recommendation; flagged for Andre to ratify or override.

### D1 — Extend existing vault structure, do not rename

**Recommendation:** **Don't rename.** Keep `00 Inbox/`, `01 Daily/`, `02 Notes/`, `99 _system/`. The Gemini doc's `/Knowledge/Inbox/`, `/System/Prompts/`, `/Output/Profiles/` would force a one-time migration of every existing note and break every existing wikilink.

Instead, **add to existing folders**:
- `99 _system/prompts/` (new) — agent system prompts, schemas, routing rules as TPG nodes
- `99 _system/evaluators/` (new) — fitness rubrics (quantitative + qualitative)
- `99 _system/golden-set/` (new) — test inputs with expected outputs
- `99 _system/sepo/` (new) — SePO loop artifacts: generation history, textual gradients, fitness traces

Existing `99 _system/skills/` stays as the procedural layer (skills). Prompts + evaluators + golden-set + sepo trace are the new substrate SePO mutates.

### D2 — SePO scope: skill layer first, prompt layer second, never all-at-once

**Recommendation:** **Skill layer only for Phase 2.** The risk of mutating all prompts simultaneously is catastrophic regression. Skill layer is bounded, well-tested, has clear failure modes (skill didn't fire, skill output was wrong). Prompt layer comes later if skill-layer SePO shows stable fitness gains.

### D3 — Fitness function: hybrid quantitative + qualitative, with Veto power

**Recommendation:** Quantitative scorer (regex + structural checks) gets 60% weight; qualitative rubric (M3 reasoning, called via `mavis team plan`) gets 40% weight. **Veto power on safety properties** — if the qualitative check flags "destructive without confirmation," fitness is forced to 0 regardless of quantitative score.

The Gemini doc's `G(f(x;P), y) ∈ [0, 1]` is correct as a math abstraction; the real `G` is a composite:
```
G = 0.6 * structural_score(f, y)
  + 0.4 * reasoning_audit(f, y)
  * safety_veto
```

### D4 — GoldenSet curation: human-in-the-loop, version-controlled

**Recommendation:** **Andre curates the GoldenSet**, Mavis proposes. The GoldenSet is the source of truth for "good output" — letting Mavis curate it independently is a textbook alignment failure mode. Curation pattern: 5-10 inputs × expected outputs per surface area, reviewed monthly.

### D5 — SePO runs on a schedule, not on every event

**Recommendation:** **Weekly SePO runs**, scheduled via the existing cron infrastructure (`pattern-library-weekly` is a near-perfect template). Event-driven SePO on every vault write is too aggressive — fitness oscillates because individual inputs are noisy.

### D6 — No direct Obsidian-shellcommands plugin

**Recommendation:** **Skip the plugin.** Not installed; would need install + trust + restart. REST API + launchd covers everything we'd use it for. If a specific use case arises, evaluate then.

---

## 3. Phased rollout

### Phase 1 — Codification (ship today / tomorrow, ~2-4 hours)

Goal: make the SePO substrate exist as files, even if no loop runs against it yet.

**Step 1.1 — Create the four new folders.**
```
99 _system/prompts/      (TPG nodes — agent system prompts)
99 _system/evaluators/   (fitness rubrics)
99 _system/golden-set/   (test inputs + expected outputs)
99 _system/sepo/         (SePO trace: generations, gradients, fitness history)
```

**Step 1.2 — Seed one prompt as a TPG node (proof of shape).**
Pick `ea-decision-logger` as the prototype. Convert `SKILL.md` frontmatter into TPG schema:
```yaml
---
node_type: agent_parameter
parameter_id: ea-decision-logger
generation: 1
fitness_score: null        # populated by Phase 2
last_optimized: null
last_evaluated: null
mutation_count: 0
schema_version: 1
---
```
Keep the existing `SKILL.md` content unchanged. The TPG frontmatter is an *additional* layer, not a replacement.

**Step 1.3 — Write one fitness rubric as a sanity check.**
`99 _system/evaluators/skill_fitness_v1.md`:
- Structural checks: frontmatter present, name field present, description ≥100 chars
- Reasoning checks: trigger phrases explicit, "do NOT load" conditions explicit
- Safety checks: no destructive ops without confirmation mention
- Score 0-1 per dimension; aggregate = mean.

**Step 1.4 — Write one GoldenSet entry per skill.**
Start with the top 5 skills by invocation frequency (`ea-daily-brief`, `ea-decision-logger`, `ea-commitment-tracker`, `ea-skill-evolution`, `ea-loop-audit`). For each: 3 input cases + expected output sketch.

**Step 1.5 — Add a `sepo-trace.md` log file at `99 _system/sepo/trace.md`.**
Empty for now. Phase 2 writes here.

**Done criteria:** folders exist, one skill has TPG frontmatter, one evaluator exists, one GoldenSet entry exists, trace file exists.

### Phase 2 — SePO loop prototype for skill layer (1-2 weeks)

Goal: a working SePO loop that mutates one skill, evaluates against GoldenSet, accepts or rolls back the mutation, logs the trace.

**Step 2.1 — Implement the SePO loop as a Mavis skill.**
Skill: `sepo-runner` at `~/.mavis/agents/mavis/skills/sepo-runner/`. Inputs: parameter_id, GoldenSet path, evaluator path. Outputs: trace entry (generation, fitness, candidate diff, accept/reject).

The loop runs **synchronously in this Mavis session**, not as a background cron yet. Verifier = me (the same Mavis session), with structured critique per the Gemini doc's textual-gradient pattern. Worker = also me, running M3 in adaptive reasoning mode per the doc.

```
Loop:
  1. Read current prompt P_t from TPG node
  2. Read GoldenSet (x_i, y_i)
  3. For each (x_i, y_i): Worker generates f(x_i; P_t)
  4. Verifier scores each (f, y_i) → fitness components
  5. Aggregate fitness F(P_t) = mean
  6. If F(P_t) ≥ threshold: stop (no improvement needed)
  7. Otherwise: Verifier compiles textual gradient ∇_text
  8. M3 generates candidate P_{t+1} = M3(Optimize(P_t, ∇_text))
  9. Re-evaluate P_{t+1}: F(P_{t+1})
  10. If F(P_{t+1}) > F(P_t): commit P_{t+1} to TPG node, log to trace
  11. Else: discard, log rejection, try mutation_count += 1
  12. If mutation_count > max_attempts: halt, alert Andre
```

**Step 2.2 — Run SePO on `ea-decision-logger` as the prototype.**
GoldenSet: 3 cases (chat capture with decision markers, capture without decision, ambiguous case). Evaluator: `skill_fitness_v1.md`. Watch the trace; tune thresholds.

**Step 2.3 — Manual review gate.**
After each candidate mutation, Mavis **halts and shows Andre** the diff before committing. Auto-accept only after 5+ successful runs demonstrate the loop is stable.

**Step 2.4 — Cost guardrail.**
Each SePO run = ~5-15 M3 calls. At Token Plan rates, ~50-150K tokens per skill per run. Weekly run × 5 skills = ~250-750K tokens/week. Well within Plus tier.

**Done criteria:** `sepo-runner` skill ships, runs end-to-end on one skill, halts for human review on every candidate, trace file shows real entries.

### Phase 3 — Autonomous background evolution (deferred, ~1-2 months after Phase 2 is stable)

This is where the Gemini doc's vision gets real. **Only proceed if Phase 2 shows stable fitness gains AND Andre is comfortable with autonomous mutation.**

**Step 3.1 — Schedule SePO via cron.**
Add `sepo-weekly-skill-evolution.md` to the cron list, modeled on `pattern-library-weekly.md`. Runs every Sunday 02:00 CT. One skill per run (round-robin across the 5 top-frequency skills).

**Step 3.2 — Veto + audit trail.**
Every autonomous commit gets logged with: timestamp, fitness delta, candidate diff, Andre notification via existing daily-brief mechanism. Andre can revert any commit by deleting the trace entry + restoring the prior TPG frontmatter.

**Step 3.3 — Expand scope carefully.**
Only after 4+ weeks of clean runs: expand from skill layer to prompt layer (system prompts in `99 _system/prompts/`). Same loop, different parameter type. Higher Veto strictness on prompt layer (destructive mutations blocked entirely).

**Done criteria:** weekly cron, audit trail, Andre reverting zero commits per month. Only THEN is the "self-evolving organism" claim actually true.

---

## 4. Risks / contradictions to flag

**R1 — Gemini's "Mavis multi-agent" framing conflates me with the runtime.** I am **Mavis, the EA** (single agent). `mavis-team` is the multi-agent orchestrator. The doc positions Mavis as both, which is wrong. In the design above, the SePO loop's "Worker = me, Verifier = me, Leader = me" is honest about single-agent reality; for genuine multi-agent work (parallel verification, ensemble scoring), invoke `mavis-team` explicitly. Don't conflate.

**R2 — Verifier-as-separate-agent violates peer separation rule.** Per `cross-team-discipline.md`, Mavis has **absolute separation** from Hermes, OpenClaw, gbrain, etc. The doc's "Verifier Agent" can be Mavis-internal (different session role, same agent), but **not** a peer agent in another team's filesystem tree. Phase 2 stays in Mavis-internal. Phase 3 stays in Mavis-internal. Don't drift.

**R3 — Token Plan pricing unverified.** Doc claims Plus/Max/Ultra tiers at specific prices. I can't verify these without checking the live billing page. Treat as approximate. Real concern: if the SePO loop is more expensive than estimated, the cost guardrail (Step 2.4) catches it via `quota` check before each run.

**R4 — GoldenSet drift.** If GoldenSet is curated once and never updated, SePO optimizes for stale "good output" definitions. Mitigated by D4 (human-in-the-loop curation, monthly review). Without this, SePO is a local optimum lock-in.

**R5 — Fitness function gaming.** If fitness function is purely structural, SePO will optimize for structure (passes structural checks) at the expense of substance (useful output). Mitigated by D3 (40% reasoning audit, safety Veto). Re-evaluate the qualitative split quarterly.

**R6 — "Self-improving organism" claim is overclaim if SePO halts on every candidate.** Until Phase 3 ships with autonomous commits, the system is "human-supervised evolution with Mavis as the proposer," not "self-improving." This is the right framing — full autonomy is riskier than the doc acknowledges.

---

## 5. Open questions (need Andre's call)

**Q1 — Is the proposed scope right?** Phase 1 (codification) is cheap and reversible. Phase 2 (skill-layer SePO) is the load-bearing bet. Phase 3 (autonomous) is the doc's vision but should be deferred. **Confirm: do Phase 1 + Phase 2 in the proposed shape?**

**Q2 — GoldenSet curation cadence.** Doc implies passive. I'm proposing monthly review. **Confirm monthly, or different cadence?**

**Q3 — Auto-accept threshold for Phase 3.** After how many clean weekly runs (3? 5? 10?) do we move to fully autonomous commits? **Pick a number.**

**Q4 — SePO on prompt layer (system prompts in `99 _system/prompts/`)?** Doc treats prompts and skills uniformly. I propose skills first, prompts much later (higher Veto strictness). **Confirm separation or unification?**

**Q5 — Cost ceiling.** What's the monthly token budget for SePO? I'm proposing ~750K tokens/week (3M/month) for 5 skills. **Confirm or adjust.**

---

## 6. What to read next

- `obsidian-local-rest-api-wiring` skill (just shipped) — the MCP layer SePO depends on
- `ea-skill-evolution` skill — the existing GEPA-anchored foundation
- `ea-loop-audit` skill — the verification patterns Phase 2 borrows from
- `agent-harness-principles.md` (memory) — the 12-component framework the doc partly reinvents
- `loop-engineering-framework.md` (memory) — the 5-stage loop doc aligns with
- `03 Projects/Mavis-Apex-Architecture/06 Token Economics & Headroom.md` — Token Plan reality

---

## 7. The honest one-paragraph version

The Gemini doc is a competent LLM-generated synthesis with real conceptual value but factual specifics that need verification, structural recommendations that conflict with the existing vault, and a "self-improving organism" framing that overclaims until Phase 3 ships with stable autonomous commits. The right move is **ship Phase 1 today** (codification is cheap and reversible), **build Phase 2 over 1-2 weeks** (skill-layer SePO with human review gate), **defer Phase 3 until Phase 2 demonstrates stable fitness gains** (1-2 months out at earliest). Most of the underlying substrate already exists in pieces; the integration is wiring, not new construction.

---

*Drafted 2026-06-17. Source: Gemini research doc + Mavis audit of on-disk reality + Mavis's existing framework docs. Next action: get Andre's call on Q1-Q5 above, then ship Phase 1 step 1.1.*
