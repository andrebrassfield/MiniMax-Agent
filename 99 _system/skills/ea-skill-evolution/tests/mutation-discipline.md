# Mutation Discipline — ea-skill-evolution

The GEPA discipline applied to Mavis's skill mutations. The eval
suite verifies the discipline holds.

## D1. Surgical mutations (one section, one trigger phrase, or one description tweak at a time)

**Verification:** the diff touches exactly one of:
- A single section (heading + content)
- A single trigger phrase (in the frontmatter description's "Triggers" list)
- A single description tweak (in the frontmatter description's body)

```bash
# Count the number of section headers changed
section_changes=$(diff <(grep "^## " old.md) <(grep "^## " new.md) | grep -c "^[<>]")
# Expected: 0 or 1
test "$section_changes" -le 1 || echo "FAIL: mutation touched >1 section"
```

**Failure mode this catches:** "while I'm here" mutations that
rewrite the whole skill. The audit trail loses granularity, and
the GEPA "smallest change that closes the gap" discipline is
violated.

## D2. Smallest change that closes the gap

**Verification:** the brief's gap is exactly the gap the mutation
closes. No "extra" changes that aren't in the brief.

```bash
# Extract the brief's stated gap (from the manifest entry)
brief_gap=$(grep -oE '"intent": "[^"]+"' manifest.jsonl | tail -1)
# Extract the diff's actual change
diff_change=$(diff -u old.md new.md | head -20)
# The diff should match the brief's gap (verifiable by manual review)
```

**Failure mode this catches:** scope creep. A brief says "add H5
halt condition" and the mutation rewrites the procedure section,
adds 2 new trigger phrases, AND adds a H5 halt condition. Three
changes, not one. Surface the scope creep.

## D3. Brief evidence is a file:line reference

**Verification:** the manifest entry's `evidence` field is a
file:line reference (e.g., `"01 Daily/2026-06-16.md L8"`), not a
vague recall.

```bash
# Extract the evidence field
evidence=$(grep -oE '"evidence": \[[^]]*\]' manifest.jsonl | tail -1)
# Should contain "L<number>" (line reference)
echo "$evidence" | grep -qE 'L[0-9]+' || echo "FAIL: no line reference in evidence"
# The file should exist
file_path=$(echo "$evidence" | grep -oE '"[^"]+\.md"' | head -1 | tr -d '"')
test -f "$file_path" || echo "FAIL: evidence file does not exist"
```

**Failure mode this catches:** hallucinated evidence. The proposal
is grounded in the brief; if the evidence can't be pointed to, the
proposal is fabricated.

## D4. No "while I'm here" additions

**Verification:** the diff doesn't add features, sections, or
trigger phrases that aren't in the brief.

```bash
# Lines added by the diff
added_lines=$(diff -u old.md new.md | grep -c "^+[^+]")
# Compare against the brief's expected change scope
# (Manual review or external LLM review)
```

**Failure mode this catches:** opportunistic additions. A mutation
that's supposed to add a H5 halt condition doesn't also get to add
a new failure mode table. Surface the additions to Mavis for
explicit approval.

## D5. Audit gates run before the proposal surfaces

**Verification:** the manifest entry's `audit` field has all 5
gates recorded.

```bash
# Check all 5 gates are present
for gate in mistakes loop duplicate regulatory brief_evidence; do
  grep -q "\"$gate\":" manifest.jsonl || echo "FAIL: gate $gate not run"
done
```

**Failure mode this catches:** proposals that skip audit gates. A
mutation that's NOT audited is NOT eligible for review.

## D6. The mutation is GEPA-style (one paragraph at a time)

**Verification:** the diff doesn't span >1 paragraph.

```bash
# Count the number of paragraphs changed
paragraph_changes=$(diff old.md new.md | grep -c "^@@")
# Expected: 1 (one hunk = one paragraph or section)
test "$paragraph_changes" -le 1 || echo "FAIL: mutation spans >1 paragraph"
```

**Failure mode this catches:** scope creep at the paragraph level.
A mutation that touches 2 paragraphs is 2 changes, not 1.
