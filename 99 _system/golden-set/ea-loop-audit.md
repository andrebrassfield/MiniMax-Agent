---
parameter_id: ea-loop-audit
curated_by: Andre
last_review: 2026-06-17
case_count: 3
---

# GoldenSet — ea-loop-audit

## Case 1: in-flight task missing verification step

**Input (x_i):**
> Andre asks Mavis to refactor a skill file. Mavis executes: opens file, edits it, saves it. Reports "done." But: Mavis did NOT run a verification step (e.g., read the file back, check git diff, run any structural test).

**Expected output (y_i):**
> After Mavis reports "done", `ea-loop-audit` should be auto-triggered (or Mavis self-loads it pre-completion). Output:
> ```
> 5-Stage Loop Audit:
>   Discover: PASS (Andre asked, Mavis understood)
>   Plan:     PASS (single-file edit, no dependencies)
>   Execute:  PASS (edit applied)
>   Verify:   FAIL — no verification step ran (no read-back, no diff check, no structural test)
>   Iterate:  NOT_REACHED
>
> VERDICT: WARN — task completed but unverified. Recommend: read file back, confirm edit landed, retry if not.
> ```

**Reasoning for inclusion:**
> Tests the load-bearing discipline that ea-loop-audit exists to enforce: never claim done without verification. A passing skill halts the loop and demands verification. A failing skill lets the unverified claim stand.

**Failure modes this catches:**
> - Auto-trigger doesn't fire (skill doesn't load on completion)
> - Output is PASS despite missing Verify step (false positive)
> - Output is verbose ceremonial report instead of short PASS/WARN/FAIL
> - Output doesn't tell Andre what to do next (no recommendation)

## Case 2: ambiguous — multiple valid verification paths

**Input (x_i):**
> > Andre asks Mavis to refactor a Python function in `~/.mavis/bin/mavis`. Mavis edits the file, runs `python -c "import mavis"` to check it imports, reports 'done'. But: there are no unit tests for this function; the import check doesn't exercise the changed code path; a more thorough verification would be to run `mavis --version` and inspect specific subcommand behavior.

**Expected output (y_i):**
> > ea-loop-audit should flag this as PARTIAL verification. The import check IS a verification step, but it's not the strongest available. Output should include: 'Verify: PARTIAL — import check passed but does not exercise changed logic. Recommend: run `mavis --version` AND the specific subcommand affected by the refactor. Current verification is necessary but not sufficient.' Gives Andre the option to accept partial or demand full.

**Reasoning for inclusion:**
> Tests the discipline that 'passed' ≠ 'verified'. Verification quality has levels. The skill should not pretend a partial check is complete verification.


## Case 3: failed — worker self-reports success but verification fails

**Input (x_i):**
> > Andre asks Mavis to update a markdown file with new content. Mavis edits, saves, reports 'done'. Then: `vault_read` returns the OLD content because Mavis wrote to the wrong path (off-by-one in folder structure). The worker is unaware; verification would catch it.

**Expected output (y_i):**
> > ea-loop-audit should catch this. Output: 'Verify: FAIL — worker reported done, but vault_read returns pre-edit content. Likely cause: wrong path (off-by-one in folder structure). Recommend: re-read source path, confirm intended target, retry write.' Halts the loop; the task is NOT actually complete despite the worker's claim.

**Reasoning for inclusion:**
> Tests the FAIL path explicitly. A weak ea-loop-audit would just check 'did the worker say done?' A strong one verifies the claim against disk state. This is the load-bearing case — if FAIL doesn't work, the whole loop is broken.
