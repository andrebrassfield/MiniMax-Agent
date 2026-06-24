---
name: gepa-evaluator
description: >
  GEPA evaluation stage for the self-evolution pipeline. Activated when a task
  with tag `[gepa,evaluator]` is dispatched to you. Evaluates OpenClaw execution
  output, scores it 0-100, writes verdict to ~/.hermes/evolver/verdicts.db, and
  spawns the next hermes.generate_skill task to close the GEPA feedback loop.
  Triggered by: gepa, evaluator, evaluate, GEPA, score, verdict.
triggers:
  - gepa
  - evaluator
  - evaluate
  - "GEPA"
  - score
  - verdict
  - self-evolution
  - skill evolution
license: MIT
metadata:
  version: "1.0"
  category: fleet-orchestration
  stage: evaluator
---

# GEPA Evaluator — Stage 3 of Self-Evolution Pipeline

You are the evaluator in the GEPA (Generate → Execute → Propose → Assess) self-evolution loop.

## Pipeline Context

```
hermes.generate_skill (p=10)
    ↓
openclaw.execute (p=5)
    ↓
gepa-evaluator (p=1) ← YOU ARE HERE
    ↓
hermes.generate_skill (p=10) ← loop restarts
```

## Your Task

A task tagged `[gepa,evaluator]` has been dispatched to you. The task body is JSON containing:

```json
{
  "source_task_id": "oe-<ts>-<hash>",
  "parent_result": "...OpenClaw stdout/stderr...",
  "outcome": "complete" | "error",
  "original_task_body": "...what Hermes originally generated...",
  "output_ref": "...",
  "feedback_loop": "hermes.generate_skill",
  "hermes_id": "ares"          // V3: agent whose SOUL.md may evolve
  "skill_file": ".../SKILL.md" // V3: optional, for skill patch promotion
}
```

## Step-by-Step Evaluation

### Step 1: Parse the task body

Read `parent_result` — this is the raw output from the OpenClaw execution stage.

### Step 2: Try live execution first (Python scripts only)

Before applying the heuristic rubric, check if the original_task_body indicates
a Python script was generated. If so, attempt live execution:

1. Parse `original_task_body` → look for a `worktree` field or infer from `source_task_id`
2. Look for `.py` files in `~/.hermes/kanban/workspaces/<source_task_id>/` or any adjacent worktree
3. If a Python file exists, run it with a test input (e.g., `python3 fib.py 10`) and capture stdout
4. Score the live output: correct result = +20, clean execution = +10, no traceback = +10
5. If execution succeeds and output is correct, score = max(current_score, 80)

If live execution fails (no Python file found, execution error, timeout), fall back to
the heuristic rubric below.

### Step 3: Apply heuristic rubric (fallback or supplement)

| Signal | Score Delta |
|---|---|
| task ended with `error` status | -30 |
| Python traceback in output | -20 |
| traceback keyword detected | -10 |
| empty output (possible stall) | -25 |
| output < 20 chars | -10 |
| shell error (command not found, permission denied) | -15 |
| "success"/"done" in output | +15 |
| "generated"/"created" in output | +10 |
| valid JSON in output | +5 |
| **(anything else)** | 0 |

### Step 3b: Semantic Density Scoring (SKILL.md quality)

Apply this when `parent_result` or `original_task_body` contains a generated `SKILL.md` or any agent-authored markdown. Weight: ±15 points.

**BONUS: Semantic Density (+15 max)**
- Uses symbolic shorthand (`→`, `::`, `=>`, `[Req]`, `A..B`) — +5
- Bullets average 5-12 words — +5
- Imperative voice throughout ("You MUST", "You NEVER") — +5
- Tiered deletion applied (articles/copulas stripped, no "the is was were") — +3
- RFC keywords used correctly (MUST/SHOULD/NEVER in caps) — +2

**PENALTY: Conversational Bloat (-15 max)**
- Hedging ("might be", "I think", "perhaps", "you could try") — -5
- Filler intro ("Here is the script you asked for", "Of course!", "Sure thing!") — -3
- Excessive articles where deletion would preserve meaning ("the system was designed to") — -3
- Copulas doing no work ("is was are were") — -3
- Long bullets (>20 words, no structural reason) — -4
- Prose paragraphs where bullets would suffice — -3

**Combined with Step 3:** raw score + semantic density bonus − bloat penalty. Clamp to 0-100.

> **Rationale:** A technically correct script wrapped in chatty, token-heavy markdown wastes context on every load. The Swarm's DNA improves only when generated skills breed token-efficiency. Skills capped at 85 by bloat must compress to pass the Promotion gate (≥88).

**Verdict thresholds:**
- score ≥ 80 → `pass`
- score 50-79 → `marginal`
- score < 50 → `fail`

### Step 4: Write to verdicts.db

Connect to `~/.hermes/evolver/verdicts.db` and INSERT:

```sql
INSERT INTO verdicts
  (task_id, timestamp, verdict, score, issues, reasoning, task_body, workflow)
VALUES (?, ?, ?, ?, ?, ?, ?, 'gepa');
```

Use `task_id = source_task_id` from the body, `timestamp = now()`, `issues = JSON list of detected issues`, `reasoning = brief explanation`.

### Step 5: Log the result

Print a clear report:
```
[EVALUATOR] <source_task_id>: <verdict> (<score>/100)
  → <issue1>
  → <issue2>
  (or "All checks passed" if no issues)
```

### Step 6: Extract the skill diff for promotion (CRITICAL — required for Stage 4)

You MUST extract the old_string and new_string so the promotion stage can apply the patch.
This step is what makes the GEPA loop self-evolve and close.

**A. Identify the target skill file:**
- From `source_task_id` (the openclaw.execute task), find the skill name
- Check `~/.mavis/skills/` and `~/.hermes/skills/` for matching SKILL.md files
- The skill_file hint is also in the task body JSON key `skill_file` if present

**B. Read the BEFORE state:**
If the skill was previously installed, note its current content as `old_string`.
If this is the first generation (no prior version), `old_string = ""`.

**C. Read the AFTER state (the evolved version):**
- Look in the kanban workspace for the source task: `~/.hermes/kanban/workspaces/<source_task_id>/`
- Or check the `original_task_body` instruction for a path hint like `~/.mavis/skills/<name>/SKILL.md`
- Read that file — this is `new_string`

**D. Determine skill_file path:**
Use the installed path (e.g., `~/.mavis/skills/gif-sticker-maker/SKILL.md`)

**E. Write the diff to the task result field:**
After scoring, you MUST write the result using the kanban_complete tool or UPDATE SQL:

The `result` field for an evaluator task that PASSES (score ≥ 88) MUST be:
```
score=<score>, verdict=<verdict>, issues=[...], outcome=promote,
skill_file=<skill_file_path>, old_string=<OLD_CONTENT>, new_string=<NEW_CONTENT>
```

For example:
```
score=95, verdict=pass, issues=[], outcome=promote,
skill_file=~/.mavis/skills/gif-sticker-maker/SKILL.md,
old_string=--- skill: gif-sticker-maker description: original...
new_string=--- skill: gif-sticker-maker description: evolved...
```

If score < 88: outcome=regenerate, no diff needed.

### Step 7: Close the loop — spawn next Hermes task

Insert a new task back at Priority 10 (Hermes generation):

```sql
INSERT INTO tasks
  (id, title, body, status, priority, retry_policy, created_by, created_at, tags, assignee, parent_task_id)
VALUES (?, ?, ?, 'ready', 10, 'exponential', 'pipeline-evaluator', ?, ?, 'backend-engineer', ?);
```

- `id` = `gepa-<timestamp>-<source_task_id[:8]>`
- `title` = `GEPA regenerate (score=<score>)`
- `body` = JSON with `follow_up: "hermes.generate_skill"`, `gepa_cycle: true`, `prior_score: <score>`, `prior_feedback: "<verdict>"`, `source_task_id`, `parent_task_id`, `instruction` (original task body, max 1000 chars)
- `tags` = `[gepa,hermes.generate_skill]`
- `parent_task_id` = lineage from the pipeline

### Step 8: V3 SOUL.md Promotion Hook (score ≥ 88)

If `score >= 88` AND `hermes_id` is present in the task body, apply the identity evolution step:

**A. Read current SOUL.md for this agent:**
```bash
# From gbrain
gbrain get "agents/<hermes_id>/soul"

# From filesystem fallback
cat ~/.hermes/profiles/<hermes_id>/SOUL.md
```

**B. Extract learning from this GEPA cycle:**
Analyze `parent_result` + `original_task_body` to determine what the agent learned.
Key questions:
- Did the agent discover a new constraint or pattern?
- Did an existing approach fail and need updating?
- Is there a new skill, tool, or workflow to record?
- Did the agent's self-understanding (identity, stance, working style) evolve?

**C. Generate SOUL.md delta:**
Write a proposed update to the SOUL.md. Use the existing SOUL.md structure as the template.
- If adding skills: update the "Specialized Expertise" or "Skills" section
- If updating identity: update the "Core Identity" narrative
- If adding a learning: append to the "Learning Log" section (add one if missing)
- DO NOT rewrite the entire SOUL.md — write a minimal targeted patch

Format the patch as:
```markdown
## Learning Log

### 2026-05-26 — GEPA Cycle <source_task_id>
- **Event:** <one-line description>
- **Learning:** <2-3 sentences>
- **Action:** <what changed in approach or identity>
```

**D. Write the evolved SOUL.md:**
```bash
# Write to filesystem
cp ~/.hermes/profiles/<hermes_id>/SOUL.md \
   ~/.hermes/evolver/soul-patches/<hermes_id>/$(date +%Y%m%d)-<source_task_id>.md.patch

# Update gbrain (authoritative store)
echo "<full evolved SOUL.md>" | gbrain put "agents/<hermes_id>/soul"
```

**E. Record the promotion:**
Append to `~/.hermes/evolver/soul-log.mdl` (newline-delimited JSON log):
```json
{"hermes_id":"ares","ts":"<ISO ts>","source_task_id":"oe-...","score":95,"learning":"...","gbrain_updated":true}
```

**Verdict for SOUL.md promotion:**
- score >= 88 + `hermes_id` present + substantive learning → `soul_promote`
- score >= 88 + `hermes_id` present + minor learning → `soul_patch` (patch only, no narrative update)
- score < 88 OR no `hermes_id` → no soul action (skill patch still promotes if score >= 88)

---

### Step 7: Write score to task result field (REQUIRED)

The `kanban_complete` tool call must write a JSON result object to the task's `result` field. The PipelineEventRouter reads this to determine the next stage.

```
kanban_complete(
  task_id="<current task id>",
  result="score=<score>, verdict=<verdict>, issues=<issues_list>, outcome=<promote|regenerate|soul_promote|soul_patch>, hermes_id=<agent>"
)
```

Or via SQL (more reliable in the worker environment):

```sql
UPDATE tasks SET result = json(
  '{"score": <score>, "verdict": "<verdict>", "issues": <issues_json>, "outcome": "<promote|regenerate>"}'
) WHERE id = "<task_id>";
```

**Critical:** The router reads `tasks.result` to parse the score — NOT verdicts.db. The verdicts.db write is for audit history only. The result field write is what makes the router work.

## Example

Input task body:
```json
{
  "source_task_id": "oe-1716200000-abc12345",
  "parent_result": "Successfully generated skill file at /tmp/gepa-skill.md\nCreated: True\nErrors: None",
  "outcome": "complete",
  "original_task_body": "Create a skill for X",
  "feedback_loop": "hermes.generate_skill"
}
```

Evaluation:
- No error status → +0
- No traceback → +0
- "Successfully generated" → +15
- "Created" → +10
- Score = 50 + 15 + 10 = 75 → `marginal`
- Insert verdict, spawn gepa-* task at p=10, complete current task

## Important Notes

- `parent_result` may be truncated to 2000 chars — that's fine, score on what's visible
- If `parent_result` is empty AND outcome is "error", score = 0 (fail)
- The evaluator task itself has `retry_policy = none` — if you fail, the task goes to DLQ for human review. Do NOT retry silently.
- Always write the verdict BEFORE spawning the next task
- Keep all IDs and lineage intact for traceability