# Output Shape Discipline — ea-daily-brief

The brief is bounded: exactly 3 connections + 1 pattern + 1 question.
The eval suite verifies the shape holds.

## D1. Exactly 3 connection sections

**Verification:**
```bash
grep -c "^## [0-9]\." brief-YYYY-MM-DD.md
# Expected: 3 (numbered 1, 2, 3)
```

**Failure mode this catches:** the brief has 2 or 4+ connections
(under- or over-spec'd).

## D2. Connection sections have all 4 required fields

**Verification:** each connection section contains:
- **Surfaces:** line
- **Pattern:** line
- **Evidence:** line

```bash
for n in 1 2 3; do
  section=$(sed -n "/^## $n\\./,/^## /p" brief-YYYY-MM-DD.md)
  for field in "Surfaces" "Pattern" "Evidence"; do
    echo "$section" | grep -q "\\*\\*$field:\\*\\*" || echo "FAIL: connection $n missing $field"
  done
done
```

**Failure mode this catches:** a connection is missing surfaces or
evidence (just a claim with no anchoring).

## D3. Cross-domain pattern is one sentence (or omitted)

**Verification:**
- If present, the "## Cross-domain pattern" section is exactly 1
  sentence (no period before the next section)
- Or the section is entirely absent

```bash
section=$(sed -n '/^## Cross-domain pattern/,/^## /p' brief-YYYY-MM-DD.md)
# Count sentences (periods followed by space or end-of-line)
sentence_count=$(echo "$section" | grep -oE '[.!?]( |$)' | wc -l)
# Expected: 0 (omitted) or 1 (one sentence)
```

**Failure mode this catches:** the pattern is a paragraph (per EA
contract behavior #2: sharpen to one specific sentence).

## D4. Exactly 1 question (the closing section)

**Verification:**
- The "## Question" section is exactly 1 sentence
- It ends with a question mark

```bash
section=$(sed -n '/^## Question/,$p' brief-YYYY-MM-DD.md)
sentence_count=$(echo "$section" | grep -oE '[.!?]( |$)' | wc -l)
# Expected: 1
# And the sentence should end with "?"
echo "$section" | grep -q '?$' || echo "FAIL: Question does not end with '?'"
```

**Failure mode this catches:** the brief has 0 or 2+ questions, or
the question is a task-asking question that doesn't end with "?".

## D5. No "to-do" or task-list content

**Verification:** the brief does not contain a list of items that
look like todos (`- [ ]`, `TODO:`, `Action: <verb>`, etc.)

```bash
grep -E '^\s*-\s*\[[ x]\]' brief-YYYY-MM-DD.md | head -5
# Expected: empty
grep -E '^(TODO|Action|Next steps?):' brief-YYYY-MM-DD.md | head -5
# Expected: empty
```

**Failure mode this catches:** the brief has degraded into a task
list. The brief is the question; the work after the question is
Andre's call.

## D6. All 3 connections reference ≥2 different surfaces

**Verification:** each connection's **Surfaces** line has ≥2 file
paths.

```bash
for n in 1 2 3; do
  surfaces=$(sed -n "/^## $n\\./,/^## /p" brief-YYYY-MM-DD.md | grep -A1 "Surfaces" | tail -1)
  # Count file-like references (paths or filenames)
  count=$(echo "$surfaces" | grep -oE '`[^`]+`' | wc -l)
  test "$count" -ge 2 || echo "WARN: connection $n has <2 surfaces"
done
```

**Failure mode this catches:** a connection is single-domain (which
should be a project status, not a brief connection). Per hard
constraint #8: cross-domain by default.
