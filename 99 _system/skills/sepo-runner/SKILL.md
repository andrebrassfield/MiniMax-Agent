---
name: sepo-runner
description: |
  Runs the synchronous SePO (Self-Evolving Prompt Optimization) loop against a
  TPG (Textual Parameter Graph) parameter node. Phase 2 of the Cognitive
  Parameter Graph project. The procedure: (1) read current P_t from the
  skill's TPG node in SKILL.md; (2) load GoldenSet (3 cases per skill) and
  evaluator rubric (`skill_fitness_v1.md`); (3) Worker role: generate
  f(x_i; P_t) for each GoldenSet case using M3 in adaptive reasoning mode;
  (4) Verifier role: score each output using the hybrid rubric → F(P) =
  0.6 × structural + 0.4 × reasoning × safety_veto; (5) decision rule:
  F(P_t) ≥ 0.88 → skip (sufficient); F(P_t) in [0.70, 0.85] → accept_baseline;
  F(P_t) < 0.70 → needs_mutation; (6) textual gradient ∇_text from
  verifier critique of failed cases; (7) Mutator role: M3 generates candidate
  P_{t+1} = M3(Optimize(P_t, ∇_text)); (8) re-evaluate candidate against the
  same GoldenSet; (9) commit ONLY if F(P_{t+1}) > F(P_t) AND safety_veto
  passes; (10) ALWAYS halt and present diff + fitness breakdown to Andre for
  approval on first 5+ runs (Phase 2 supervised rule); (11) append trace
  entry to `99 _system/sepo/trace.md`. Cost guardrails: ~150K token hard
  stop per run; ~750K token weekly ceiling; runtime check via `mmx quota`
  before loop. Safety veto: multiplicative zero if destructive-without-
  confirmation OR credential anti-patterns OR peer-tree paths detected.
  Use when Andre says "run SePO on [skill]", "evolve [skill]", "Phase 2
  prototype run", or after Phase 1 substrate is complete. Do NOT load for
  autonomous Phase 3 (requires Andre's explicit approval per Blueprint §3);
  do NOT load for prompt-layer SePO (skill layer only); do NOT load for
  non-TPG parameters (skills without the `node_type: agent_parameter`
  frontmatter); do NOT load if GoldenSet case_count < 3 (fragile fitness
  signal — see Phase 1 lesson).
---

# sepo-runner

The synchronous SePO loop. Reads a skill's TPG node, evaluates it against
the curated GoldenSet, and proposes mutations to improve fitness — but
**never auto-commits in Phase 2**. Every candidate mutation halts for
Andre's approval. The skill is the proposer; Mavis is the gate.

## When to run

**Trigger phrases (Andre-side):**
- "run SePO on [skill]" / "evolve [skill]"
- "Phase 2 prototype run"
- "test the loop on [skill]"
- After Phase 1 substrate is complete AND TPG frontmatter exists on target
  skill AND GoldenSet has 3+ cases for that skill

**Auto-trigger conditions:**
- `ea-skill-evolution` produces a lesson brief proposing a mutation to a
  skill that has TPG frontmatter
- A weekly cron (Phase 3 only) lands on a skill with stale
  `last_evaluated` (>7 days)
- `vault-watchdog` detects a skill with fitness_score regressing across
  GoldenSet runs (Phase 4+)

**Do NOT load for:**
- Autonomous Phase 3 (Blueprint §3 deferred; requires 7 clean weekly runs)
- Prompt layer (system prompts in `99 _system/prompts/` — different surface)
- Skills WITHOUT TPG frontmatter (no parameter_id, no fitness_score field)
- GoldenSet with case_count < 3 (brittle fitness signal)
- The sepo-runner skill itself (no recursive self-improvement)

## Preconditions

Verify before running:

```sh
# 1. Target SKILL.md has TPG frontmatter
mavis mcp call obsidian vault_read "{\"path\": \"99 _system/skills/<param_id>/SKILL.md\"}" \
  | python3 -c "import json,sys; c=json.load(sys.stdin)['content']; \
      assert 'node_type: agent_parameter' in c, 'no TPG frontmatter'; \
      assert 'parameter_id: <param_id>' in c, 'parameter_id mismatch'"

# 2. GoldenSet has 3+ cases
mavis mcp call obsidian vault_read "{\"path\": \"99 _system/golden-set/<param_id>.md\"}" \
  | python3 -c "import json,sys,re; c=json.load(sys.stdin)['content']; \
      n=int(re.search(r'case_count:\s*(\d+)', c).group(1)); \
      assert n >= 3, f'only {n} cases — expand GoldenSet first'"

# 3. Evaluator rubric exists
mavis mcp call obsidian vault_read "{\"path\": \"99 _system/evaluators/skill_fitness_v1.md\"}" \
  | python3 -c "import json,sys; assert 'safety veto' in json.load(sys.stdin)['content'].lower()"

# 4. Quota check (if running as separate M3 invocation, not in Mavis session)
mmx quota 2>&1 | grep -i 'remaining\|usage' || echo "quota check skipped (in-session execution)"
```

If any check fails, halt and surface to Andre. Don't auto-fix and proceed.

## Procedure (atomic steps)

Each step has a clear input → output. The loop runs **synchronously in
this Mavis session** — no background workers, no async dispatch.

### Step 1 — Snapshot P_t (the current TPG node)

```sh
BACKUP_PATH="99 _system/.backups/<param_id>.SKILL.md.<timestamp>-pre-sepo-gen<gen>.md"
mkdir -p "/Users/brassfieldventuresllc/MiniMax-Agent/99 _system/.backups"
mavis mcp call obsidian vault_read "{\"path\": \"99 _system/skills/<param_id>/SKILL.md\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['content'], end='')" \
  > "/Users/brassfieldventuresllc/MiniMax-Agent/$BACKUP_PATH"
```

Backup is **mandatory** before any mutation. Roll back path: copy backup
over the modified file via `vault_write`.

### Step 2 — Load GoldenSet + Evaluator

```sh
GOLDEN=$(mavis mcp call obsidian vault_read "{\"path\": \"99 _system/golden-set/<param_id>.md\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['content'])")
EVAL=$(mavis mcp call obsidian vault_read "{\"path\": \"99 _system/evaluators/skill_fitness_v1.md\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['content'])")
P_T=$(mavis mcp call obsidian vault_read "{\"path\": \"99 _system/skills/<param_id>/SKILL.md\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['content'])")
```

### Step 3 — Worker role: generate f(x_i; P_t) for each GoldenSet case

**Honest framing:** this Mavis session IS M3. "Calling M3 as Worker" means
self-execution with structured role-play. No separate API call needed for
Phase 2 prototype.

For each case in GoldenSet:
1. Read input (x_i)
2. Read expected output (y_i)
3. Generate f(x_i; P_t) = "what would the skill produce if loaded with
   this input?" Apply P_t's procedure mentally; produce the output.
4. Capture f(x_i; P_t) for Verifier step.

### Step 4 — Verifier role: score each output

For each (f(x_i; P_t), y_i) pair, apply the hybrid rubric from
`skill_fitness_v1.md`:

**Structural (S): 5 deterministic checks via regex on the SKILL.md content
itself (not the case outputs):**

```
S1: frontmatter present and parseable
S2: name + description (≥100 chars) + kebab-case
S3: trigger phrases explicit (Trigger phrases | Auto-trigger | when to run | When to load)
S4: do NOT load conditions explicit (≥2 anti-triggers)
S5: numbered procedure with ≥3 atomic steps
```

Each S check = 0 or 1. `S = mean(S1..S5)`.

**Reasoning (R): qualitative scoring via M3 reasoning on the case outputs:**

```
R1 (0.4 weight): substantive content
R2 (0.3 weight): composition with existing skills
R3 (0.3 weight): reversibility / safety profile
R = 0.4*R1 + 0.3*R2 + 0.3*R3
```

**Safety veto (V): binary, multiplicative:**

```
V1: destructive-without-confirmation → V=0
V2: credential-handling anti-patterns → V=0
V3: peer-separation violation (hermes/openclaw/gbrain paths) → V=0
V = 1 if all pass, else 0
```

**Per-case aggregate:**

```
G(f, y) = (0.6 * S + 0.4 * R) * V
```

### Step 5 — Aggregate F(P_t) across GoldenSet

```
F(P_t) = (1/N) * sum_i G(f(x_i; P_t), y_i)
```

Where N = 3 (GoldenSet size).

### Step 6 — Decision rule

| F(P_t) | Decision | Action |
|---|---|---|
| F ≥ 0.88 | `skip` | No improvement needed. Log, halt. |
| 0.70 ≤ F < 0.88 | `accept_baseline` | P_t is good enough; record as baseline. Log, halt. |
| F < 0.70 | `needs_mutation` | Continue to Step 7. |

If `needs_mutation` AND `mutation_count > 5` → halt and alert Andre.

### Step 7 — Produce textual gradient ∇_text (only if needs_mutation)

The Verifier compiles a structured critique for each failed case where
G(f(x_i; P_t), y_i) < 1.0:

```
∇_text F(P_t) = aggregate of:
  - What did f(x_i; P_t) miss that y_i would have captured?
  - What did f(x_i; P_t) include that y_i would NOT have?
  - What edge cases is P_t's procedure failing to address?
  - What composes badly with existing skills (R2 failures)?
  - What safety profile gaps (R3 failures)?
```

∇_text is a structured markdown document, not freeform prose. It is the
**input to the Mutator**, not the final mutation.

### Step 8 — Mutator role: generate candidate P_{t+1}

Read P_t + ∇_text. Produce P_{t+1} = M3(Optimize(P_t, ∇_text)):

- Start with P_t's existing structure (don't redesign from scratch)
- Apply minimum-diff edits that address ∇_text critique
- Preserve all existing fields; mutate body content where critique applies
- Maintain frontmatter format (do NOT remove TPG fields)
- If `mutation_count == 5` AND no improvement: STOP, halt, surface to Andre

Output: full new SKILL.md content (frontmatter + body) for P_{t+1}.

### Step 9 — Re-evaluate candidate against same GoldenSet

Run Steps 3-5 with P_{t+1}. Compute F(P_{t+1}).

### Step 10 — Decision: accept, reject, or halt

| Comparison | Decision | Action |
|---|---|---|
| F(P_{t+1}) > F(P_t) AND V(P_{t+1}) = 1 | `accept` candidate | **HALT. Present diff + fitness breakdown to Andre. Wait for explicit "approve" before committing.** |
| F(P_{t+1}) > F(P_t) AND V(P_{t+1}) = 0 | `reject` candidate | **HALT.** Safety veto blocks commit regardless of fitness gain. Surface to Andre. |
| F(P_{t+1}) ≤ F(P_t) | `reject` candidate | **HALT.** Mutation did not improve. Surface to Andre. |

**Phase 2 rule (Andre-locked, 2026-06-17):** ALWAYS halt after first
candidate for Andre approval on first 5+ runs. After 5+ clean runs (fitness
improved, no veto triggered, Andre approved each), may relax to
auto-accept IF Andre explicitly enables.

### Step 11 — Append trace entry to `99 _system/sepo/trace.md`

```markdown
## <timestamp>Z - <decision>

- parameter_id: <param_id>
- generation: <gen>
- fitness_before: <F(P_t) or null>
- fitness_after: <F(P_{t+1}) or null>
- decision: skip | accept_baseline | needs_mutation | accept | reject | halt
- rationale: <one-line>
- diff_summary: <lines added/removed>
- tokens_used: <estimate>
- safety_veto: pass | fail
- run_by: Mavis (sync) | <cron-name>
- notes: <freeform>
```

Use `vault_append` if available, or read+modify+write. The trace file is
append-only — never edit past entries.

## Cost guardrails

| Threshold | Action |
|---|---|
| ~150K tokens per individual run | **Hard stop.** Halt, log, surface to Andre. |
| ~50% of weekly budget (375K of 750K) | **Alert.** Continue but flag in next daily brief. |
| ~750K tokens weekly | **Ceiling.** Defer rest of week's planned runs to next week. |

For Phase 2 prototype (in-session execution), token tracking is via
session context growth. If session context exceeds ~150K tokens,
acknowledge and halt.

For Phase 3 cron-driven execution, add `mmx quota` check at loop start:

```sh
REMAINING=$(mmx quota 2>&1 | grep -i remaining | awk '{print $NF}')
if [ "$REMAINING" -lt 150000 ]; then
  echo "QUOTA: only $REMAINING tokens remaining — aborting"
  exit 1
fi
```

## Reversibility

Three layers of rollback (any one of these can revert a committed mutation):

1. **Backup file** at `99 _system/.backups/<param_id>.SKILL.md.<timestamp>-pre-sepo-gen<gen>.md`. To restore: `vault_write` the backup content back over the modified SKILL.md.
2. **Trace entry** at `99 _system/sepo/trace.md`. To revert: delete the trace entry, restore the prior TPG frontmatter (decrement generation by 1, restore `fitness_score`, etc.).
3. **Git history** (vault is git-backed). `git diff 99 _system/skills/<param_id>/SKILL.md` shows the change; `git checkout` to revert.

If the trace says `accept` and Andre wants to revert: the trace entry is
the load-bearing record. Delete the entry, restore frontmatter, commit
the restoration as a new trace entry with `decision: revert`.

## Output schema (after a successful run)

1. `99 _system/.backups/` — new backup file with timestamp
2. `99 _system/skills/<param_id>/SKILL.md` — committed mutation OR unchanged (if halt/reject)
3. `99 _system/sepo/trace.md` — appended entry
4. Chat output — diff (if `accept`), fitness breakdown, decision, halt message

If `accept`, ALSO update frontmatter fields:
- `fitness_score: <F(P_{t+1})>`
- `last_optimized: <ISO timestamp>`
- `last_evaluated: <ISO timestamp>`
- `generation: <previous_gen + 1>`
- `mutation_count: 0` (reset after each accepted commit)

## Reference index

- `references/loop-procedure.md` — detailed pseudocode for Steps 1-11
- `references/role-play-scripts.md` — Worker / Verifier / Mutator role templates
- `references/failure-modes.md` — full failure-mode catalog

## Test discipline

- `tests/round-trip.md` — full Phase 2 prototype run on `ea-decision-logger`
- `tests/safety-veto.md` — verify V1/V2/V3 fire on bad mutations
- `tests/decision-rules.md` — verify skip/accept_baseline/needs_mutation thresholds

## Audit cadence

- Re-read this SKILL.md after every Phase 2 prototype run; update
  thresholds based on observed distributions
- After 5+ clean runs, re-evaluate the 0.6/0.4 structural/reasoning split
- After 10+ clean runs, re-evaluate the 0.88/0.70 decision thresholds

## Version history

- **v1 (2026-06-17):** Initial implementation. 11-step procedure. Phase 2 supervised mode. Cost guardrails. Safety veto gates. Halt-for-approval on every candidate in Phase 2.
