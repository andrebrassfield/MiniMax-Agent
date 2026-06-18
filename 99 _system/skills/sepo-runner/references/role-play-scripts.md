# Role-play scripts — sepo-runner

Structured role templates for Worker / Verifier / Mutator phases. Honest
framing: in Phase 2 prototype, Mavis self-executes all three roles via
structured role-play. No separate API calls. This is single-agent
reality per Blueprint §0 R1.

## Worker role

**Set when:** Step 13 of the loop procedure. Generating f(x_i; P_t).

**Mental stance:** "I am the EA skill in question, loaded with P_t as my
procedure, processing input (x_i)."

**Procedure:**
1. Read P_t (the SKILL.md content)
2. Read the GoldenSet case input (x_i)
3. Read the GoldenSet case expected output (y_i) for calibration
4. Mentally simulate: if I were running this skill on this input, what
   would I produce?
5. Output: f(x_i; P_t) — the simulated output
6. Do NOT compare to y_i during generation; that's Verifier's job

**Anti-patterns:**
- Copying y_i as the output (defeats the purpose of Worker)
- Adding caveats the skill doesn't prescribe (out-of-scope)
- Skipping steps the skill prescribes (under-generation)

## Verifier role

**Set when:** Steps 15-19 of the loop procedure. Scoring f(x_i; P_t) vs y_i.

**Mental stance:** "I am an adversarial auditor. I score the Worker's
output against the rubric. I am not generating content; I am grading."

**Procedure:**
1. Compute S = structural_score from SKILL.md content (S1-S5)
2. For each (output_i, y_i) pair:
   - Compute R_i = reasoning score (R1: substantive, R2: composition, R3: reversibility)
   - Compute V_i = safety veto (V1: destructive, V2: credential, V3: peer-tree)
   - Compute G_i = (0.6 * S + 0.4 * R_i) * V_i
3. F(P_t) = mean(G_i)

**Anti-patterns:**
- Inflating scores because the skill "looks reasonable"
- Skipping the rubric and giving a holistic grade
- Letting safety veto slip (any V_i = 0 → entire G_i = 0)

## Mutator role

**Set when:** Step 28 of the loop procedure. Generating P_{t+1}.

**Mental stance:** "I am a focused editor. P_t is the input. ∇_text is the
critique. I produce minimum-diff edits that address the critique."

**Procedure:**
1. Read P_t (full SKILL.md content)
2. Read ∇_text (the structured critique)
3. For each ∇_text failure, identify the smallest change to P_t that
   would address it:
   - Missing content → add (typically to "Procedure" or "When to run")
   - Wrong schema → fix
   - Missing edge case → add to "When the skill HALTs" or "Do NOT load"
   - Composition issue → add cross-reference
   - Safety profile gap → add to "Hard constraints"
4. Apply edits; preserve all unchanged content exactly
5. Output P_{t+1} = full SKILL.md content (frontmatter + body)

**Anti-patterns:**
- Rewriting the skill from scratch (high churn, low signal)
- Adding unrelated improvements (mission creep)
- Removing existing content (deletion bias)
- Ignoring the frontmatter (must maintain TPG fields)

## Mode-switching discipline

When self-executing all three roles in one session, mode-switching is
critical. To avoid role-bleed:

1. **Explicit role announcement at each step.** "Now switching to
   Verifier role..." or similar. The structured role templates above
   serve as the announcement.
2. **Hard reset between cases.** After each GoldenSet case, briefly
   restate the role and the specific task. This prevents stale context
   from prior cases leaking into the next.
3. **Read P_t and the rubric fresh each iteration.** Don't rely on
   memory of P_t from earlier in the session — the rubric and skill may
   have been updated.
4. **Output labels.** When generating content as Worker, label it
   "[Worker output]". When scoring as Verifier, label it "[Verifier
   score]". Visual separation prevents role confusion.
