---
type: tpg-folder
purpose: TPG parameter nodes (agent system prompts as mutatable markdown)
created: 2026-06-17
parent: Cognitive Parameter Graph
schema_version: 1
---

# 99 _system/prompts/

TPG (Textual Parameter Graph) parameter nodes — agent system prompts, schemas, and routing rules treated as **mutatable markdown**.

Each parameter file:

```yaml
---
node_type: agent_parameter
parameter_id: <stable-id>
generation: 1                  # bumped by SePO after each accepted mutation
fitness_score: null            # populated by evaluators/skill_fitness_v1.md
last_optimized: null           # ISO timestamp
last_evaluated: null          # ISO timestamp
mutation_count: 0              # counter for SePO loop safety
schema_version: 1
---
```

## Relationship to skills

Skills at `99 _system/skills/ea-*/SKILL.md` are the **procedural layer** — when to run, how to invoke. Prompts at `99 _system/prompts/` are the **instruction layer** — what to say when running. Both can be TPG nodes; SePO mutates both, with different safety profiles.

## SePO mutation flow

1. Worker reads prompt P_t from this folder
2. Worker generates outputs on GoldenSet (`../golden-set/`)
3. Verifier scores via `../evaluators/skill_fitness_v1.md`
4. If fitness < threshold → textual gradient → M3 mutation → P_{t+1}
5. If fitness improves → commit + log to `../sepo/trace.md`

See `03 Projects/Cognitive-Parameter-Graph/Blueprint.md` for the full design.
