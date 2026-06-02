# SkillOpt — Mavis Skill Training Pipeline

> Reusable pipeline for training Mavis's procedural skills as text-space artefacts. Inspired by [Microsoft's SkillOpt](https://github.com/microsoft/SkillOpt).

## What this is

A pipeline that takes a hand-written Mavis skill (a workflow, a template, a MOC) and evolves it into a measurably-better version. Output: `best_skill.md`, a small (380-2,000 token) text file that beats the hand-written baseline on a held-out eval set.

The pipeline is reusable. Every Mavis skill (current and future) can be dropped in and trained.

## What this is NOT

- Not a fine-tuning setup. The model is frozen. The skill text is the trainable artefact.
- Not a one-time thing. Each skill gets a config + a split + a starting file. Re-running with new data is expected.
- Not magic. The answer key is the whole game. If the eval items are bad, the trained skill is bad.

## Directory layout

```
99 _system/skillopt/
├── README.md                          # this file
├── PIPELINE.md                        # how to add a new skill to the pipeline
├── configs/
│   └── mavis/
│       └── default.yaml               # SkillOpt config (target=optimizer=M3, cheap-first-run)
├── skills/                            # starting skills (hand-written, SkillOpt will optimize)
│   ├── process_inbox.md
│   ├── daily_brief.md
│   ├── weekly_connections.md
│   └── deep_research.md
├── splits/                            # train/val/test splits per skill
│   └── <skill>/
│       ├── train/items.json
│       ├── val/items.json
│       └── test/items.json
├── rubrics/                           # LLM-as-judge scoring rubrics (one per skill)
│   ├── process_inbox.md
│   ├── daily_brief.md
│   ├── weekly_connections.md
│   └── deep_research.md
├── outputs/                           # SkillOpt writes here (gitignored)
│   └── <skill>/                       # best_skill.md, history.json, per-step snapshots
└── soul_compliance/                   # SOUL compliance eval set (Phase A: outline only)
    └── SCAFFOLDING.md
```

## Current state (Phase A, 2026-06-02)

**Pipeline**:
- ✅ `configs/mavis/default.yaml` — SkillOpt config, target=optimizer=M3, cheap-first-run hyperparameters
- ✅ `README.md`, `PIPELINE.md`

**Skills (starting files, hand-written)**:
- ✅ `process_inbox.md` (54 lines)
- ✅ `daily_brief.md` (43 lines)
- ✅ `weekly_connections.md` (57 lines)
- ✅ `deep_research.md` (45 lines)

**Eval sets (16 items each, split 6 train / 2 val / 8 test, 64 items total)**:
- ✅ `process_inbox/{train,val,test}/items.json`
- ✅ `daily_brief/{train,val,test}/items.json`
- ✅ `weekly_connections/{train,val,test}/items.json`
- ✅ `deep_research/{train,val,test}/items.json`

**Pending**:
- ⏳ Rubrics (LLM-as-judge scoring criteria) — Phase A.5
- ⏳ `pip install skillopt` (or clone the repo) — Phase B
- ⏳ First training run — Phase B
- ⏳ SOUL compliance eval set (40 items) — co-design with Andre

## Items.json schema (per-task)

```json
{
  "id": "<skill>-<split>-<NNN>",
  "question": "the task in natural language",
  "context": "the relevant inputs (raw capture, vault state, topic, etc.)",
  "reference_output": { ... },          // known-good example of the expected output
  "scoring_dimensions": [ ... ]         // what the LLM-as-judge should evaluate
}
```

For procedural tasks (multi-section output, judgment-required), this schema is preferred over the SearchQA exact-match shape. The judge uses `reference_output` as the example and `scoring_dimensions` as the rubric; it returns a 0-1 score per item.

## How to run a training pass (Phase B, pending)

```bash
# 1. Install SkillOpt
cd 99 _system/skillopt && pip install -e .

# 2. (One-time) Wire up the local M3 client to the Mavis runtime
#    Per Friction 3 ruling: M3 itself is the optimizer (lower temperature)
#    See PIPELINE.md for the wiring spec

# 3. Train a single skill (cheap first run)
python scripts/train.py \
  --config configs/mavis/default.yaml \
  --split_dir splits/process_inbox \
  --target_model minimax/MiniMax-M3 \
  --optimizer_model minimax/MiniMax-M3 \
  --num_epochs 2 \
  --batch_size 16 \
  --out_root outputs/process_inbox_run_01

# 4. Read outputs/process_inbox_run_01/best_skill.md
# 5. If the gain is real, replace skills/process_inbox.md with best_skill.md
# 6. If the gain is suspect (or the skill reads worse), reject and re-run
```

## Related

- [[PIPELINE]] — the convention for adding a new skill to the training pipeline
- [[The Custom MCP Arsenal]] — Mavis's broader tool design space
- [[Mavis-Apex-Architecture]] — the project this pipeline supports
- [[state-of-mavis]] — session-continuity MOC; Friction Log is where pipeline questions surface
- [Microsoft SkillOpt paper](https://arxiv.org/pdf/2605.23904) — the method this implements
- [SkillOpt repo](https://github.com/microsoft/SkillOpt) — upstream
- [SkillOpt docs](https://microsoft.github.io/SkillOpt/) — official docs

---

*Pipeline seeded 2026-06-02. Phase A complete (config + 4 skills + 64 eval items). Phase B (install + first run) pending greenlight.*
