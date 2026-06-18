# Roadmap Completeness — client-pov-tracker

The 7-section sanity check. Each section has a defined
purpose and a defined minimum content. The eval suite
verifies each section is filled out and the roadmap is
executable.

## R1. All 7 sections are present

```bash
roadmap="03 Projects/Clients/[ClientName]/pov-roadmap.md"

for section in \
  "## 1. The Friction" \
  "## 2. The Agentic Standard" \
  "## 3. Target ROI" \
  "## 4. The Blueprint" \
  "## 5. The 5 Measurement Numbers" \
  "## 6. The Outcome-Pricing Commitment" \
  "## 7. Caveats and open questions"; do
  grep -qF "$section" "$roadmap" || echo "FAIL: section missing: $section"
done
```

**Failure mode this catches:** a section is missing entirely.
The roadmap is structurally incomplete.

## R2. Section 1 (Friction) is categorized by tier

```bash
for tier in "Tier 1" "Tier 2" "Tier 3"; do
  grep -qF "### $tier" "$roadmap" || echo "WARN: tier missing: $tier"
done
```

**Failure mode this catches:** Section 1 doesn't categorize
friction by the 3-tier taxonomy. The Friction Filter is
not applied.

## R3. Section 2 (Agentic Standard) names 4 criteria

```bash
for criterion in "Idempotency" "Real-time sync" "FSM-native" "Outcome-priced"; do
  grep -qF "$criterion" "$roadmap" || echo "FAIL: Agentic Standard criterion missing: $criterion"
done
```

**Failure mode this catches:** the 4 Agentic Standard
criteria are not all present. The whitepaper §2 application
is incomplete.

## R4. Section 3 (Target ROI) has ≥3 line items

```bash
# Count rows in the ROI table
roi_section=$(awk '/^## 3\. Target ROI/,/^## 4\./' "$roadmap")
row_count=$(echo "$roi_section" | grep -c "^|")
[ "$row_count" -lt 5 ] && echo "FAIL: ROI table has $row_count rows (need ≥3 data + header + separator)"
```

**Failure mode this catches:** the Target ROI table is too
small. The dollar math isn't specific enough.

## R5. Section 5 (5 Numbers) has all 5 numbers

```bash
for number in \
  "Time per task" \
  "Output quality" \
  "Revenue per AI-supported activity" \
  "Error rate" \
  "Tool cost vs value delivered"; do
  grep -qF "$number" "$roadmap" || echo "FAIL: 5-numbers list missing: $number"
done
```

**Failure mode this catches:** the 5 measurement numbers
aren't all present. The baseline is incomplete.

## R6. Section 6 (Outcome-Pricing) is committed

```bash
# Must contain the outcome-pricing language
grep -qiE "outcome.pricing|bills on outcomes|negative.*ROI.*agency eats" "$roadmap" \
  || echo "FAIL: outcome-pricing commitment not stated"
```

**Failure mode this catches:** the agency hasn't committed
to outcome-pricing. The whitepaper §2.4 contract is not
applied.

## R7. Section 7 (Caveats) is non-empty for stale audits

```bash
# If any audit was >90 days old, Section 7 must be non-empty
caveats=$(awk '/^## 7\. Caveats/,/^## Appendix|EOF/' "$roadmap" | grep -v "^##" | wc -l | tr -d ' ')
[ "$caveats" -lt 1 ] && echo "WARN: Caveats section is empty (may be OK if no stale audits)"
```

**Failure mode this catches:** the Caveats section is
empty when there should be staleness warnings.

## R8. Appendix lists the source briefs

```bash
# Appendix should reference the local-audit briefs
appendix=$(awk '/^## Appendix/,EOF' "$roadmap")
echo "$appendix" | grep -qE "local-audit|whitepaper" \
  || echo "FAIL: Appendix missing source references"
```

**Failure mode this catches:** the Appendix doesn't cite
the source data. The roadmap's claims are not traceable.

## R9. No fabrication in ROI math

```bash
# ROI numbers should reference the whitepaper or client data
# No random dollar amounts without a Source citation
roi_section=$(awk '/^## 3\. Target ROI/,/^## 4\./' "$roadmap")
echo "$roi_section" | grep -oE "\\\$[0-9,]+" | sort -u | while read amount; do
  # Each dollar amount should have a Source column citation
  echo "$roi_section" | grep -F "$amount" | grep -qE "whitepaper|client" \
    || echo "WARN: $amount may lack Source citation"
done
```

**Failure mode this catches:** the ROI table has dollar
amounts without a source citation. The no-fabrication
constraint is violated.
