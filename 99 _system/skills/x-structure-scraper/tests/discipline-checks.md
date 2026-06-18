# Discipline Checks — x-structure-scraper

The "Skeleton, Not Substance" discipline. The skill must pass all 4
checks before returning. This is the eval suite.

## D1. No paraphrased content lines

**Verification:** `grep` the file for sentences that summarize what a
thread *argues* (not how it's *built*).

**Failure indicators:**
- Lines starting with "The thread argues that..."
- Lines containing "the main point is" / "the thesis is" / "the claim is"
- Any line that paraphrases the SUBSTANCE of the thread

**Failure mode this catches:** the analyst drifted into content
summary. The blueprint is structure, not substance.

## D2. At least 2 verbatim hook examples

**Verification:** the file contains ≥2 Hook Structure sections with
**Bait:** values wrapped in quotation marks (the verbatim quote).

```bash
grep -c '^- \*\*Bait:\*\* "' "blueprint-[handle]-YYYY-MM-DD.md"
# Expected: ≥ 2
```

**Failure mode this catches:** the analyst paraphrased the bait
instead of capturing it verbatim. Verbatim beats paraphrase for
rhythm analysis.

## D3. Single Most-Copyable Move is present and at the top

**Verification:** the file contains `## The Single Most-Copyable Move`
as the second-level heading, and it's positioned BEFORE the
per-thread analysis (not buried at the bottom).

```bash
# Section is present
grep -c "^## The Single Most-Copyable Move" "blueprint-[handle]-YYYY-MM-DD.md"
# Expected: 1

# Position: it should come before the first "^## Thread"
most_copyable_line=$(grep -n "^## The Single Most-Copyable Move" "blueprint-[handle]-YYYY-MM-DD.md" | head -1 | cut -d: -f1)
first_thread_line=$(grep -n "^## Thread " "blueprint-[handle]-YYYY-MM-DD.md" | head -1 | cut -d: -f1)
test "$most_copyable_line" -lt "$first_thread_line" || echo "FAIL: Most-Copyable Move is after first Thread"
```

**Failure mode this catches:** the most-actionable section is
buried in the middle/end, making Andre scroll to find the answer.

## D4. Filename matches single vs. multi-account

**Verification:** the file naming matches the run shape.
- Single-account run → `blueprint-[handle]-YYYY-MM-DD.md`
- Multi-account run → `blueprints-YYYY-MM-DD.md`

**Failure mode this catches:** the wrong file name makes the
Scribe's blueprint-reading procedure fail (it looks for the
canonical naming pattern).

## D5. Hard rules honored

**Verification:**
- File contains no @-mentions that would trigger engagement (no
  retweets, no replies, no follows)
- All "human markers" reported as counts (numbers), not as "yes"/"no"
- The 4 hard rules (read-only, no credential entry, no fabrication,
  structure-only, verbatim over paraphrase) are honored

**Failure mode this catches:** the skill accidentally interacted with
x.com (forbidden), fabricated a marker, or paraphrased the substance.
