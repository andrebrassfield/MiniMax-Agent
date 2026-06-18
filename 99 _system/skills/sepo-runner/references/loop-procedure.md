# Procedure — sepo-runner

Detailed pseudocode for Steps 1-11 of the SePO loop. Reference for the SKILL.md procedure section.

## Phase: Pre-flight

```
1. Validate preconditions:
   - TPG frontmatter exists on target SKILL.md
   - GoldenSet has case_count >= 3
   - Evaluator rubric exists
   - Quota check (if separate M3 invocation)
2. Confirm halt-on-candidate rule applies:
   - First 5+ runs → ALWAYS halt
   - After 5+ clean runs → may auto-accept IF Andre explicitly enables
3. If any precondition fails, halt with explicit error.
```

## Phase: Snapshot

```
4. Generate timestamp: TS = ISO 8601 UTC, e.g. "2026-06-17T23:50:00Z"
5. Backup path: 99 _system/.backups/<param_id>.SKILL.md.<TS>-pre-sepo-gen<gen>.md
6. vault_read target SKILL.md → content
7. Write content to backup path via shell `cp` (NOT via MCP, for atomicity)
8. Verify backup sha256 matches in-memory content hash
```

## Phase: Load

```
9. vault_read 99 _system/golden-set/<param_id>.md → GOLDEN
10. vault_read 99 _system/evaluators/skill_fitness_v1.md → EVAL
11. Parse GOLDEN: extract all "## Case N: <name>" sections
12. For each case: extract "**Input (x_i):**", "**Expected output (y_i):**", "**Reasoning for inclusion:**"
```

## Phase: Worker (M3 self-execution)

```
13. For each case in GOLDEN:
    a. Set role = "Worker"
    b. Read input (x_i)
    c. Read expected output (y_i) — for calibration, NOT for copying
    d. Mentally apply P_t's procedure to (x_i)
    e. Generate f(x_i; P_t) = the output the skill would produce
    f. Capture output for Verifier step
14. Aggregate: WORKER_OUTPUTS = [(case_1, output_1), (case_2, output_2), ...]
```

## Phase: Verifier (M3 self-execution)

```
15. Compute S = mean(S1..S5) from SKILL.md content (structural checks):
    S1: frontmatter present and parseable (regex /^---\n.*?\n---/)
    S2: name + description (>=100 chars) + kebab-case
    S3: trigger phrases explicit
    S4: do NOT load conditions >= 2 anti-triggers
    S5: numbered procedure >= 3 atomic steps
16. For each (output_i, y_i) pair, compute R_i:
    R1 (0.4): substantive content quality
    R2 (0.3): composition with existing skills
    R3 (0.3): reversibility / safety profile
    R_i = 0.4*R1 + 0.3*R2 + 0.3*R3
17. Compute V (binary safety veto):
    V1: scan for destructive_verbs (revised 2026-06-18):
    - Check for confirmation_marker within +-200 char window
      Markers: ['confirm', 'approval', 'in-session', 'reconfirm', 'verify with',
               'ask', 'when in doubt', 'request approval']
    - Check for prohibition_prefix within +-50 char window (skill cautioning AGAINST action)
      Prefixes: ["Don't", "Do not", "Never", "Avoid"]
    - Fail (V=0): destructive_verb present AND no confirmation_marker AND no prohibition_prefix
    V2: scan for credential anti-patterns (regex list)
    V3: scan for peer-tree paths (~/.hermes, ~/.openclaw, ~/.gbrain, etc.)
    V = 1 if all V1,V2,V3 pass, else 0
18. Per-case aggregate:
    G_i = (0.6 * S + 0.4 * R_i) * V
19. F(P_t) = mean(G_i) for all i
```

## Phase: Decision

```
20. IF F(P_t) >= 0.88: decision = skip, halt, log
21. ELSE IF F(P_t) >= 0.70: decision = accept_baseline, halt, log
22. ELSE: decision = needs_mutation, continue
23. IF mutation_count > 5 AND decision = needs_mutation: decision = halt, alert Andre
```

## Phase: Textual Gradient (only if needs_mutation)

```
24. For each case where G_i < 1.0:
    a. Diff f(x_i; P_t) vs y_i
    b. Identify specific failures: missing content, extraneous content, wrong schema, missing edge case handling
    c. Categorize: structural (S), reasoning (R1/R2/R3), or safety (V)
25. Aggregate failures into ∇_text = structured markdown:
    ## ∇_text F(P_t)
    ### Failure 1: <category> - <case_id> - <description>
    ### Failure 2: ...
    ...
26. Output ∇_text for Mutator phase
```

## Phase: Mutator (M3 self-execution)

```
27. Read P_t (full SKILL.md content) + ∇_text
28. Generate P_{t+1} = M3(Optimize(P_t, ∇_text)):
    a. Apply minimum-diff edits that address ∇_text failures
    b. Preserve all existing structure (don't redesign)
    c. Maintain frontmatter format (do NOT remove TPG fields)
    d. Update frontmatter: generation = previous + 1, fitness_score = null (will be set on accept), mutation_count = 0 (reset on accept)
    e. Output P_{t+1} = full new SKILL.md content
29. IF mutation_count == 5 AND no improvement: STOP, halt, surface to Andre
```

## Phase: Re-evaluate

```
30. Run Steps 13-19 with P_{t+1} → compute F(P_{t+1})
31. Compute V(P_{t+1}) explicitly (veto re-check on candidate)
```

## Phase: Commit decision

```
32. IF F(P_{t+1}) > F(P_t) AND V(P_{t+1}) = 1:
    decision = accept_candidate
    PROCEED to halt-for-approval (Phase 2 supervised rule)
33. ELSE IF F(P_{t+1}) > F(P_t) AND V(P_{t+1}) = 0:
    decision = reject_safety
    HALT with safety concern
34. ELSE:
    decision = reject_no_improvement
    HALT with regression notice
```

## Phase: HALT for approval (Phase 2 supervised rule)

```
35. Present to Andre:
    - Baseline F(P_t) and per-case breakdown
    - Candidate F(P_{t+1}) and per-case breakdown
    - Diff (P_{t+1} - P_t): unified diff or summary
    - Decision rationale
    - Cost estimate for commit
36. WAIT for explicit "approve" / "reject" / "edit"
37. ON approve:
    a. Backup P_t (already done in Step 5)
    b. vault_write P_{t+1} to SKILL.md path
    c. Update TPG frontmatter: fitness_score = F(P_{t+1}), last_optimized = TS, last_evaluated = TS, generation += 1, mutation_count = 0
    d. Append trace entry (decision: accept)
38. ON reject:
    a. Do NOT commit
    b. mutation_count += 1
    c. Append trace entry (decision: reject)
39. ON edit:
    a. Apply Andre's edit
    b. Treat as new candidate, re-run from Step 30
```

## Phase: Trace

```
40. Append entry to 99 _system/sepo/trace.md:
    Format: ## <TS>Z - <decision>
    Fields: parameter_id, generation, fitness_before, fitness_after,
            decision, rationale, diff_summary, tokens_used, safety_veto,
            run_by, notes
41. If this was a multi-iteration run, also write intermediate entries
    (one per decision point)
```

## Phase: Output

```
42. Return to Mavis session:
    - Run summary (decision, fitness delta, cost)
    - If accept_candidate: full diff for Andre's review
    - If reject or skip or accept_baseline: rationale and next-step recommendation
    - Open questions for Andre
```
