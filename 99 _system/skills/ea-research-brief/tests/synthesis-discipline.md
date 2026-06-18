# Synthesis Discipline — ea-research-brief

The 5-step discipline for grounding a brief. Per Mavis MEMORY.md
"Synthesis-doc audit pattern": citations are ground truth, prose is
synthesis, the synthesis may be wrong.

## D1. Citation markers detected

**Verification:** the source material has citation markers
(`[1]`, `[2]`, `(Smith et al., 2023)`, `<cite>`, footnote numbers,
hyperlinks to specific papers). If present, the doc is a synthesis
of external sources and the audit pattern applies.

**Failure mode this catches:** the EA treated a primary source as a
synthesis (skipped the grounding discipline).

## D2. 1-2 citations fetched and anchored

**Verification:** the worker directly fetched at least 1-2 of the
cited sources, read the abstract or full paper, and verified the
synthesis matches.

```bash
# Citation count in the brief
citation_count=$(grep -c "^\- \[" brief.md)
# Expected: ≥2 (at least 1-2 primary sources fetched and cited)

# For each cited [N], the brief has at least one anchor: "[N]" or "(Smith et al., 2023)"
for n in $(seq 1 $citation_count); do
  count=$(grep -c "\[$n\]" brief.md)
  if [ "$count" -lt 2 ]; then
    echo "WARN: citation [$n] appears $count times — may be unused"
  fi
done
```

**Failure mode this catches:** the worker cited sources it never
read (paraphrased from the source's abstract, not the source).

## D3. Mapping to Mavis's runtime

**Verification:** each primary source is mapped to Mavis's actual
runtime context. A paper about 100B+ parameter models is not
applicable to Mavis's 7B/12B quantized local models. The brief's
"Findings" section should note where the source applies and where
it doesn't.

**Failure mode this catches:** the brief makes claims that don't
transfer to Mavis's actual deployment.

## D4. "What I don't know" section populated

**Verification:** the brief has a non-empty "What I don't know"
section. Empty or missing → HALT.

**Failure mode this catches:** the brief is over-confident. Honest
gaps are part of the deliverable.

## D5. Verbatim quotes for non-trivial claims

**Verification:** non-trivial claims in the Findings section are
backed by verbatim quotes from the primary source (not paraphrases).

```bash
# Findings section
findings=$(sed -n '/^## 3. Findings/,/^## 4/p' brief.md)
# Quote density: at least 1 quoted phrase per paragraph
quote_count=$(echo "$findings" | grep -c '"')
paragraph_count=$(echo "$findings" | grep -c '^$')
# Expected: quote_count > paragraph_count (multiple quotes per section)
```

**Failure mode this catches:** the worker paraphrased load-bearing
claims instead of quoting the source.

## D6. Runtime cross-reference done

**Verification:** the brief's "Runtime cross-reference" section is
non-empty and lists at least one of: memory state, skill state,
cron state, recent work. If all 4 are "no relevant state," the
runtime was not actually checked.

**Failure mode this catches:** the EA skipped Stage 5 (the disk
wins over recap discipline).

## D7. No fabrication on unknowns

**Verification:** the brief does not contain "X is widely known" or
"everyone agrees that" without a specific citation. Generic
consensus claims are a red flag for fabrication.

**Failure mode this catches:** the worker invented a consensus to
fill a knowledge gap.
