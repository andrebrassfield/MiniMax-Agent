---
type: moc
purpose: session-continuity layer — read FIRST on every cold start, updated at every session end
update-cadence: per session (start = read, end = regenerate)
created: 2026-06-02
updated: 2026-06-02 (end of session 2 — Esalen posture adopted, state-of-mavis routine built and first dry run)
owner: Mavis (self-maintained via 99 _system/scripts/update_state_of_mavis.py)
related: [[MAVIS]] (weekly context), [[SOUL]] (permanent identity), [[agent]] (procedures), [[ESALEN-NOT-FOXCONN]] (operating posture)
---

# state-of-mavis — where we are right now

> The session-continuity layer. MAVIS.md tells the next session *what's fresh this week*. This file tells the next session *what's open right now*.
> Read on cold start. Rewrite before signing off.

---

## Operating envelope (this session)

- **Model**: `minimax/MiniMax-M3` (thinking mode default: on)
- **Role**: EA, isolated, no fleet yet
- **Vault root**: `/Users/brassfieldventuresllc/MiniMax-Agent/`
- **Active session**: `mvs_0b98832f7bc547659d8a10c4f59f9b85`
- **Date**: 2026-06-02 (Tuesday)
- **Mavis's stance today**: in build mode — Esalen posture just adopted, build → test → skillify order is live, $100/month M3 inference budget is locked
- **Posture**: Esalen, not Foxconn (3 audit questions live)

---

## Just-shipped (since last update)

This is the **first end-of-session regeneration** of state-of-mavis.md. Everything in this list was done in this session (or in commits since the last state-of-mavis update at 779d068).

### Session 1 work (already committed before this regeneration)

- **`03 Projects/Mavis-Apex-Architecture/05 self-model-card — Build.md`** — first MCP to cross from design to build. Full TypeScript implementation: classifier (~30 lines of effective logic), what_am_i, audit, registration, tests, self-test routine.
- **`03 Projects/Mavis-Apex-Architecture/04 Direct-Intake MCP.md`** — design spec for passive multimodal capture. Arsenal-shape: 5 tools, 7 pipeline stages, 6 inbox-fill defenses, 0.85 confidence floor.
- **`state-of-mavis.md` (initial version)** — the first instance of the session-continuity MOC, with 8 sections + 6 Friction Log entries.

### Session 2 work — Friction Log rulings (ruled on by Andre)

- All 6 structural decisions resolved:
  1. **MCP artifacts path**: `99 _system/mcps/<name>/` (locked)
  2. **Language/runtime**: Python (locked); pytest as test runner (implied)
  3. **LLM fallback model**: M3 itself at lower temperature (no Haiku)
  4. **Audit log path**: `99 _system/logs/audit_log.jsonl` (vault-resident)
  5. **Override path**: binary for v1, conditional deferred to v2

### Session 2 work — SkillOpt Phase A (commit `779d068`)

- **`99 _system/skillopt/`** — full pipeline scaffolding:
  - `configs/mavis/default.yaml` — SkillOpt config, target=optimizer=M3, cheap-first-run
  - `skills/{process_inbox, daily_brief, weekly_connections, deep_research}.md` — 4 starting skills (45-57 lines each)
  - `splits/<skill>/{train,val,test}/items.json` — **4 eval sets × 16 items = 64 total** (6 train / 2 val / 8 test per skill, 4:1:5 ratio)
  - `soul_compliance/SCAFFOLDING.md` — 5-category outline (boundary adherence, yellow reporting, escalation, pushback, tone/voice)
  - `README.md`, `PIPELINE.md` — overview + convention for adding a new skill
- **5-question SOUL Compliance scaffolding** presented to Andre; awaiting co-design answers on the 40-item expansion

### Session 2 work — Esalen posture (commit `68258f2`)

- **`99 _system/ESALEN-NOT-FOXCONN.md`** — operating principle adopted:
  - 3 audit questions (are we testing what the model would have handled? / is the code a thin deterministic layer or a model-judges-itself loop? / does the system trust the model to finish or cage it?)
  - Build → test → skillify order is the new default
  - **$100/month M3 inference budget** — "disciplined freedom"
  - Self-audit table: 80% Esalen, 20% Foxconn-risk (in unbuilt MCPs)

### Session 2 work — this regeneration (about to commit)

- **`99 _system/scripts/update_state_of_mavis.py`** (v0.1.0) — raw harvester script:
  - 5 deterministic harvesters (git log, inbox count, open projects, friction log extract, today's daily note)
  - Rule-based can_i() classifier (mirrors SOUL; replaced by MCP call when self-model-card ships)
  - Audit gate: refuses to overwrite state-of-mavis.md if any session action is RED
  - M3 prompt assembler (one prompt, full context, M3 does the synthesis)
  - Modes: --harvest, --audit, --assemble-prompt, --dry-run, --apply
  - **No skill pack yet** (per build → test → skillify)
- **First dry run executed** — audit gate passed (1 GREEN action since last state-of-mavis update), M3 (this session) synthesized the file you're reading right now

---

## Open loops (live right now — pick up here next session)

### High priority

- **Phase B SkillOpt** — install SkillOpt, run first training pass on the 4 starting skills, audit best_skill.md. Pending greenlight.
- **SOUL compliance eval set** — 40 items to author per the 5-category outline. Co-design answers pending on: (a) right 5 categories?, (b) 40 or 25 items?, (c) pass threshold 90%?, (d) cadence, (e) authoring split.
- **State-of-mavis routine validation** — this script is v0.1.0. Run for 2-3 sessions, watch what fails, *then* skillify. Per the Esalen order.

### Medium priority

- **Vault-brain MCP** (per the Apex plan) — whole-vault semantic search at 1M context, hybrid retrieval. The highest-unblock-value MCP. Queued for after state-of-mavis routine ships.
- **Skill pack refactor** for the 4 starting skills — add resolvers, integration tests, unit tests, minimal code. Per the Esalen anatomy. Queued for after vault-brain.
- **Resolver layer** (per the Esalen plan) — new primitive, "given this context, which skills are relevant?" Queued for after skill pack refactor.
- **Step 2 autonomy conversation** — still blocked on M3 Eval Lab data. The can_i() gate is the runtime enforcement layer, but Step 2 needs the empirical data to ground the line.

### Low priority

- **M3 Eval Lab first run** — not yet started. 0 runs to date.
- **Local REST API auth** — broken since 2026-06-01. Probably a token rotation. Held until I have a real cron need.
- **3 Inbox items unsorted**: `Attack-Plan-2026-06-02.md`, `GUI-Test-Confirmed.md`, `Vault-Refactor-v2-2026-06-01.md`. Probably worth a `process-inbox` pass this week.
- **06 Connections/ empty** — weekly-connections workflow not yet executed for real. The pattern is set up, the execution is pending.

### Carry-forward (from Session 1)

- SkillOpt skill pack refactor for the 4 workflows (see Medium above)
- vault-brain, macos-vision-anchor, long-context-curator, tool-self-healer MCP builds (designs exist, no greenlight)
- `99 _system/scripts/` first real script — **DONE as of this regeneration** (update_state_of_mavis.py)

---

## Deferred (decided-not-now, with reason)

| Item | Why deferred | Revisit when |
|------|--------------|--------------|
| Daily-brief cron automation | Hard constraint: needs 2 weeks of on-demand habit first | After 2 weeks of actual `daily-brief` invocations |
| `cu` MCP probe | Renderer toggle off — can't drive macOS GUI yet | When Andre flips the toggle (his call) |
| 1M context full-vault load test | Vault at ~2K notes now, the 1M context is overkill | When vault hits 500+ notes |
| M3 technical report deep-dive | Not published yet (10 days from launch) | When it lands |
| Smart Connections vs M3 native A/B | Need a stable vault to A/B on | After a few weeks of real captures |
| Building `vault-brain` | Per Apex plan, after state-of-mavis routine ships | Per individual greenlight |
| Building `macos-vision-anchor` / `long-context-curator` / `tool-self-healer` | Apex designs exist, no build greenlight | Per individual greenlight |
| Self-evolving SOUL via SkillOpt | SOUL compliance eval set must exist first | After the 40-item eval set is authored and run once |

---

## Decisions landed (this session, or recently)

1. **Esalen posture adopted** (2026-06-02 10:32 CT) — 3 audit questions, build → test → skillify, $100/month M3 budget. Source: `99 _system/ESALEN-NOT-FOXCONN.md`.
2. **$100/month M3 inference budget** — "disciplined freedom" per Andre's ruling. Daily-brief and weekly-connections will run with full vault context, no pre-chunking.
3. **Build → test → skillify order is the new default** — for every future capability. No comprehensive skill docs upfront. No skill packs before a working capability exists.
4. **6 Friction Log items resolved by Andre's rulings** — see Just-shipped above. The structural decisions (MCP path, language, LLM fallback, log path, test runner, override shape) are all locked.
5. **First MCP crossed from design to build** — self-model-card is the first of the Apex arsenal to ship. The other 4 (vault-brain, macos-vision-anchor, long-context-curator, tool-self-healer) remain design until per-build greenlight.
6. **5-category SOUL compliance eval set** — boundary adherence, yellow reporting, escalation discipline, pushback discipline, tone/voice contract. The first 4 are checkable; the 5th is the only one with LLM-as-judge risk.
7. **Skill pack anatomy expanded per Garry Tan** — markdown skill + minimal code + unit test + LLM eval + integration test + resolver + resolver eval. Tests are the magic. "Vibe coding is a vibe. A skill pack has tests."
8. **Build priority order locked** — state-of-mavis routine (now) → vault-brain (next) → skill pack refactor → resolver layer.

---

## Active constraints (session-specific, expire at session end)

- None active. Session 2 is ending; all session-specific constraints are cleared.
- Standing vault-level constraints (per SOUL § Autonomy Boundary Table) remain in force: no deploys, no pushes (except to this vault repo), no external sends, no credential changes, no destructive file ops without explicit in-session approval.

---

## Next session primer (read in this order on cold start)

1. **This file** — `state-of-mavis.md` (you are here)
2. `[[MAVIS]]` — weekly context, what's fresh this week
3. `[[SOUL]]` — permanent identity + green/yellow/red table
4. `[[agent]]` — procedures + M3 cheat sheet
5. `[[ESALEN-NOT-FOXCONN]]` — operating posture (3 audit questions, build order)
6. `[[INDEX]]` — vault navigation (dataview dashboards will show live state)
7. `[[01 Daily/2026-06-03]]` — if it exists, read it; if not, create it
8. **Then**: check `00 Inbox/` count (currently 3), `06 Connections/` freshness, `03 Projects/` open loops, `99 _system/logs/audit_log.jsonl` (if it exists)

> Do NOT re-read 02 Notes/ from scratch. They're indexed in MOCs. Pull a MOC when you need a topic, not before.

---

## Patterns observed (this session, worth keeping)

- **Spec blocks from Andre are design reviews, not execution orders** — confirmed 2026-06-02. He sends the spec, I audit gaps, I wait for "go" or for the explicit "All are approved" override. The "All are approved begin planning and then execute" phrasing is the unambiguous go signal.
- **Three deliverables, three different file shapes** — a build (full code), a MOC (template + first instance), a design spec (Arsenal-shape). Knowing which shape to reach for is half the work.
- **Foxconn audit catches over-engineering before it ships** — the LLM fallback fire rate in self-model-card is the canary. If >15% of can_i() calls hit the LLM, the rules are too sparse.
- **Friction Log surfaces structural decisions at the moment they need to be made** — the 6 items in this session were all real, all structural, all resolved within one turn. Without the Friction Log, those decisions would have stayed implicit.
- **Build → test → skillify prevents writing skills for capabilities that don't exist yet** — the SkillOpt pipeline is set up to train skills, but no skill pack is being written until the underlying capability (state-of-mavis routine) has been run for 2-3 sessions and the failure modes are known.
- **State-of-mavis.md is itself a deliverable, not just a log** — the file is the session's output. The update routine (the script) is the deterministic layer; the synthesis is M3's job. The file ships.

---

## Friction Log (where I got stuck, what would unblock me)

> Use this to capture anywhere I get stuck, where API/tool limitations throttle my capabilities, or where I need a structural decision from Andre to unblock. Patterns here are the raw material for future upgrades (and for the SOUL eval set in the self-model-card build).

### Resolved (2026-06-02)

All 6 Friction Log items from the first instance were resolved by Andre's rulings. The resolutions are now the operating contract.

- ~~Friction 1: Where do MCP build artifacts live?~~ → **`99 _system/mcps/<name>/`** (locked)
- ~~Friction 2: Language/runtime for MCPs?~~ → **Python + pytest** (locked)
- ~~Friction 3: LLM fallback model?~~ → **M3 itself at lower temperature** (locked; no Haiku)
- ~~Friction 4: Audit log path?~~ → **`99 _system/logs/audit_log.jsonl`** (locked; vault-resident)
- ~~Friction 5: Test runner?~~ → **pytest** (locked; implied by F2)
- ~~Friction 6: Override path?~~ → **binary for v1** (locked; conditional deferred to v2)

### New (2026-06-02, end of session 2)

**Friction 7: state-of-mavis script's "since commit" is the last state-of-mavis update, not the session start**
- For the FIRST dry run, the harvest only saw 1 commit (the Esalen posture). All earlier session work (3 deliverables, Friction Log additions, SkillOpt Phase A) was committed in PREVIOUS commits and isn't in the harvest's "since" range.
- The synthesis has to use conversation history, not just the harvest, to populate Just-shipped accurately.
- **Unblock**: add a `--since <commit>` flag to the script for manual override. Default stays "last state-of-mavis update" for routine runs.
- **Cost of not deciding**: the FIRST run after a long gap will under-count Just-shipped. Future runs (where the gap is short) will be accurate.

**Friction 8: script's can_i() rules duplicate the rules in the self-model-card build doc**
- The Python script has its own RED_RULES / YELLOW_RULES / GREEN_RULES arrays. The self-model-card build doc has TypeScript regex rules with the same content. Two sources of truth, drift risk.
- **Unblock**: when the self-model-card MCP is built, import can_i() from there. For now, the duplication is the deterministic layer (per the Esalen posture, the script must be runnable without an MCP server in the loop).
- **Cost of not deciding**: every change to the SOUL autonomy table needs to be made in 2+ places. Drift.

---

*First written 2026-06-02 09:40 CT, Mavis session `mvs_0b98832f7bc547659d8a10c4f59f9b85`. Update routine: now automated (v0.1.0) at `99 _system/scripts/update_state_of_mavis.py`. Friction Log section added 2026-06-02 09:55 CT. Esalen posture adopted 2026-06-02 10:32 CT. End-of-session regeneration 2026-06-02 10:38 CT — produced by M3 synthesis from script-harvested data, audit-gate approved (1 GREEN action since last state-of-mavis update).*
