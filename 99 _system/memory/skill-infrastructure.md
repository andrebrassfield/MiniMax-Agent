---
description: SkillOpt pipeline (Microsoft self-evolving skills), skill install decision protocol, no-wrappers fleet lock. Load when running a SkillOpt pilot, installing a new skill, or auditing the skill layer.
---

# Skill Infrastructure

## SkillOpt pipeline — installed, wired, pilot ran (2026-06-02)
First self-evolving skills pilot completed 2026-06-02 night. Microsoft SkillOpt (arxiv 2605.23904, github.com/microsoft/SkillOpt) installed and wired through MiniMax. Pilot ran on kanban-health-check as the test case. Result: pipeline works end-to-end, but the test case was the wrong shape for SearchQA-style SkillOpt. Documented in `~/.mavis/agents/mavis/sandbox/night-report-2026-06-02.md`.

**Where things live:**
- Repo: `~/.mavis/agents/mavis/sandbox/skillopt/` (cloned microsoft/SkillOpt, --depth 1)
- venv: `~/.mavis/agents/mavis/sandbox/.skillopt-venv/`
- Working config: `~/.mavis/agents/mavis/sandbox/skillopt-runs/kanban-health-v1/config.yaml`
- Reusable answer-key generator: `~/.mavis/agents/mavis/sandbox/build_kanban_items.py`
- Reference artifacts: `skillopt-runs/kanban-health-v1/reference/{best_skill_v0002.md, history.json, summary.json}`

**The non-obvious model wiring (3 failed runs to learn this):**
SkillOpt's `minimax_chat` backend is **target-only by design** — see `skillopt/model/__init__.py:54-57` which hard-codes `set_optimizer_backend("openai_chat")` when minimax_chat is selected. The optimizer always goes through `openai_chat`, which defaults to Azure OpenAI. To use MiniMax for both roles, set BOTH:
- `model.target_backend: minimax_chat` + `MINIMAX_API_KEY` env var (target path uses minimax_backend.py with urllib)
- `model.optimizer_backend: openai_chat` + `AZURE_OPENAI_*` env vars with `AZURE_OPENAI_AUTH_MODE=openai_compatible` and `AZURE_OPENAI_ENDPOINT=https://api.minimax.io/v1` (optimizer path uses openai SDK in openai_compatible mode)

Both roles hit the same MiniMax endpoint with the same `GOOSE_MINIMAX_API_KEY`. Reuses existing env var, no new credentials.

**The structural finding (load-bearing for future pilots):**
SearchQA-style SkillOpt tests the model by extracting the answer from `<answer>...</answer>` tags. If the QUESTION already encodes the rules, the SKILL body is redundant and may actively hurt performance. The kanban-health-check pilot:
- Empty skill (13 bytes): 15/15 = 100% on held-out test
- Seed skill (3.6KB): 14/15 = 93.33% on held-out test
- Optimized skill (4.5KB): 13/15 = 86.67% on held-out test (regression on one case)
- SkillOpt accepted the edit because val went 33%→67%, but the val set was only 3 items — single-item flip dominates

**Pre-flight filter for any future SkillOpt target:**
"Does the SKILL BODY contain the rules, or does the QUESTION contain the rules?"
- If the question is the rules → operational/classification skill → SkillOpt is the wrong tool
- If the body is the rules → format-conversion / output-template / extraction-rubric skill → SkillOpt is the right tool

**Cost benchmark (MiniMax-M2.7, no reasoning):**
- 12 train items + 3 val + 15 test, 1 epoch, batch 4 = ~117K tokens, ~$0.10-$0.20, ~3 min wall
- Eval-only on 15 items = ~15K tokens, ~$0.01-$0.02, ~30s wall
- The paper's worst case (46M tokens) is for long multimodal tasks; simple text tasks are well under 1M

**Don't change without re-deriving:**
- The MiniMax wiring pattern (minimax_chat target + openai_chat+openai_compatible optimizer, both pointing at api.minimax.io/v1 with the same GOOSE_MINIMAX_API_KEY)
- The original `~/.minimax/skills/kanban-health-check/SKILL.md` (the seed is better than the optimized version)
- The 12/3/15 split direction (lean toward larger val, 20% not 10%, for any future pilot)

**Next-pilot candidate:** a new "format-conversion" skill where the body IS the format spec, and items.json tests whether the model follows it. Clean gate, EM-friendly, no operational-script noise.

## Skills belong with the operator, not the chief (full protocol)
When Andre asks me to install a skill/CLI/tool, default to placing it in the **agent that will actually use it**, not in my Mavis drawer. Mavis is chief of staff — I delegate, synthesize, and route. I don't run research collectors, don't execute fleet builders, don't drive browser automation. Putting a skill in `~/.mavis/skills/` because the install was the easiest path is the wrong move.

**Concrete instance (2026-06-02):** Andre shared the "very Agentic Engineering Hack I Know (June 2026)" article and asked me to install `/last30days` (mvanhorn, v3.3.1, multi-source recency aggregator). I installed it under `~/.mavis/skills/last30days/` with a wrapper. Andre corrected: "assign it to the research agent. skills should be paired with the agents that need them." I trashed the Mavis wrapper, wrote a research question to `03 Projects/Researcher/queue/research-questions.md` (Mavis's only write lane into the Researcher), and pinged the Researcher via `mavis communication send`. Right outcome.

**Why this matters:** the fleet's value is each agent doing its lane. When I install a research collector in my drawer and "synthesize from it" myself, I am doing the Researcher's job — that's the "hallucination laundry" failure mode the Researcher's SOUL.md warns about (raw findings presented as Mavis-grade synthesis). The stage discipline the Researcher enforces (raw → findings → claims → verified → dossiers) exists because the stages need different operators. Mavis is downstream of the dossier, not upstream of the finding.

**Override:** if Andre explicitly says "install this for Mavis," install it for Mavis. The principle is default-correct, not absolute.

## No wrappers fleet lock (2026-06-02)
Fleet-wide lock set by Andre 2026-06-02 22:33 CT: **no shitty wrappers, everything flows through Obsidian through markdown and HTML.**

- No skill/CLI wrappers around other agents work. If a tool in `~/.mavis/skills/` is named after another agent job, it is a violation.
- The thing itself is the deliverable. Skills that produce .md or .html are fine — the artifact IS the output. Skills that need engine code to *read* are the wrong shape.
- The Obsidian vault IS the database, the state, and the rendering layer. Do not duplicate state into JSON configs or sqlite blobs the vault already holds.
- Mavis chief tools stay (plan-mode, mavis-team, skill-creator, brain-ops, kanban-ops, hermes-fleet-sync) — those are chief-domain, not fleet-wrappers. The rule is about wrapping *other* agents, not about having chief tools.
- HTML for rendering, markdown for content, Obsidian for everything. No proprietary formats.

Generalizes the "skills belong with the agent that uses them" rule from per-agent fix to fleet-wide lock.
