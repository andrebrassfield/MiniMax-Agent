# Pipeline Convention — How to Add a New Skill

> The repeatable pattern for adding a new Mavis skill to the SkillOpt training pipeline. If you're training a new skill, this is the workflow.

## When to use this

Any time you have a Mavis skill (workflow, template, MOC, sub-routine) that:
- Is hand-written today
- Is used repeatedly (the training data signal is real)
- Has a checkable "right answer" (otherwise the eval set is impossible)

If the skill has no checkable answer (e.g., "be helpful" or "be honest"), do NOT add it to SkillOpt — the LLM-as-judge scorer will be noisy and the trained skill will drift. Use a different discipline for those (Reflexion Log, weekly review, etc.).

## The 5-step process

### Step 1: Identify the skill + its input/output shape

What does the skill take in? What does it produce? Write a one-paragraph description. This is the "task definition" the eval items will test.

**Example** (process-inbox):
- **Input**: a raw capture in `00 Inbox/`
- **Output**: a sharpened permanent note in the right `02 Notes/` subfolder, with tags and at least one wikilink
- **Success criteria**: destination correct, sharpened is one specific sentence, tag matches existing taxonomy, primary link is a real note

### Step 2: Write 12-20 eval items in items.json format

For each item, provide:
- `id`: unique (`<skill>-<split>-<NNN>`, where split is train/val/test)
- `question`: the task in natural language
- `context`: the relevant inputs (raw capture, vault state, topic, etc.)
- `reference_output`: a known-good example of the expected output
- `scoring_dimensions`: what the LLM-as-judge should evaluate (3-6 dimensions)

**Split ratio** (per the SkillOpt paper's defaults): 40% train, 10% val, 50% test. For 16 items: 6 train / 2 val / 8 test. For 20 items: 8 train / 2 val / 10 test.

**Quality bar for items**:
- Realistic: based on actual captures, actual notes, actual topics — not toy examples
- Specific: the question names the actual file, the actual topic, the actual context
- Grounded: the reference_output uses real note paths, real tags from the existing taxonomy
- Diverse: cover the typical cases (60%), edge cases (20%), ambiguous cases (20%)

**The most common failure mode**: items that test the wrong thing. E.g., for process-inbox, testing "does the model understand the task" instead of "does the model pick the right destination + write a sharp sentence + suggest a real link." Stay close to the actual success criteria.

### Step 3: Write the LLM-as-judge rubric

For procedural tasks, the SearchQA exact-match scorer is too brittle. Use LLM-as-judge with a tight rubric.

Per skill, write `rubrics/<skill>.md`:
- The 3-6 scoring dimensions (typically mirror `scoring_dimensions` in items.json)
- For each dimension: 0.0 (fail), 0.5 (partial), 1.0 (full) criteria
- Worked example of a good output, a partial output, a bad output

The rubric is what makes the eval trustworthy. A loose rubric accepts bad edits; a tight rubric rejects good edits. Err on the side of tight.

### Step 4: Write the starting skill

Put the hand-written version at `skills/<skill>.md`. This is what SkillOpt will start from and optimize.

Format: clear, structured, no cruft. The bounded edit budget (default 4 edits per step) means SkillOpt can only make small changes; if the starting file is bloated, the optimizer can't fix it.

**Don't put in the starting file**:
- TODO comments ("we should also do X")
- Meta-commentary ("this skill is being trained, so...")
- Code blocks that don't run

**Do put in the starting file**:
- Clear purpose statement
- Step-by-step procedure
- Output format (if any)
- Rules (the "do not" list)
- A worked example of a good output

### Step 5: Wire the local M3 client (Phase B only)

Per Friction 3 ruling (M3 is the optimizer, lower temperature): the Mavis runtime needs a thin client that:
1. Takes a prompt + generation params
2. Returns the M3 completion
3. Supports temperature override (0.2 for optimizer, 0.7 for target)
4. Logs every call to `99 _system/logs/skillopt-runs.jsonl` (for cost tracking + audit)

This is the wiring spec; implementation in Phase B.

## After the first run

Read `outputs/<skill>/best_skill.md`. Three outcomes:

1. **Real gain on the test set, skill reads as well or better than the starting file** → ship. Replace `skills/<skill>.md` with `best_skill.md`. Commit. Note the gain in the run log.

2. **Real gain, but the skill reads worse** → reject. The validation gate said yes, but the audit (you reading the file) says no. Reject and document why. Re-run with a different starting file or a tighter rubric.

3. **No gain or regression** → diagnose. Either the eval items are bad (no signal), the rubric is too loose, or the starting file is already optimal. Don't ship a regression.

## The "answer key is the whole game" reminder

The SkillOpt paper is explicit: the answer key is the input that determines everything. If the eval items are wrong or inconsistent, SkillOpt faithfully optimizes toward the wrong target.

Spending extra time on the eval set is the highest-leverage activity in the pipeline. If you're stuck on "why isn't the trained skill better?" the answer is almost always "the eval set wasn't tight enough."

## Related

- [[README]] — the pipeline overview
- [[state-of-mavis]] — Friction Log is where pipeline questions surface

---

*Convention drafted 2026-06-02. Used by 4 skills so far (process-inbox, daily-brief, weekly-connections, deep-research).*
