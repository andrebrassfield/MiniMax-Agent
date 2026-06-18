# Marker Detection Accuracy — ea-commitment-tracker

The eval suite verifies the marker regex catches commitments
with high recall + precision. False negatives (missed
commitments) and false positives (over-capture) both fail
the suite.

## Recall: catch all strong markers

```bash
# True positives: each strong marker should match
declare -A true_positives=(
  ["I'll have the regulatory anchors by EOD"]="CAPTURE"
  ["I will draft the brief tomorrow"]="CAPTURE"
  ["Let me look into that"]="CAPTURE"
  ["I owe you the audit"]="CAPTURE"
  ["I'll handle that by Friday"]="CAPTURE"
  ["I'll have it ready in an hour"]="CAPTURE"
  ["I'll come back to that"]="CAPTURE"
  ["I should have that by tomorrow"]="CAPTURE"
  ["I need to check on the kanban"]="CAPTURE"
  ["I'll follow up next session"]="CAPTURE"
)

correct=0
total=${#true_positives[@]}
for input in "${!true_positives[@]}"; do
  expected="${true_positives[$input]}"
  if [ "$expected" = "CAPTURE" ]; then
    if echo "$input" | grep -qiE "\b(I('ll| will)|let me|i owe|i should|i need to|by (eod|monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|next (week|month|quarter))|in the morning|in an hour|next session|come back to|follow up|check on)\b"; then
      correct=$((correct + 1))
    fi
  fi
done
recall=$(echo "scale=2; $correct / $total" | bc)
echo "Recall: $recall ($correct/$total)"
[ "$(echo "$recall > 0.85" | bc)" -eq 1 ] || echo "FAIL: recall too low"
```

**Target:** recall > 0.85 (catch at least 85% of strong
markers).

## Precision: reject pure acknowledgments

```bash
# True negatives: pure acknowledgments should NOT match
declare -A true_negatives=(
  ["Got it"]="NOT-CAPTURE"
  ["Noted"]="NOT-CAPTURE"
  ["I see"]="NOT-CAPTURE"
  ["Acknowledged"]="NOT-CAPTURE"
  ["Thanks"]="NOT-CAPTURE"
  ["Yes"]="NOT-CAPTURE"
  ["OK"]="NOT-CAPTURE"
  ["Right"]="NOT-CAPTURE"
)

correct=0
total=${#true_negatives[@]}
for input in "${!true_negatives[@]}"; do
  expected="${true_negatives[$input]}"
  if [ "$expected" = "NOT-CAPTURE" ]; then
    if ! echo "$input" | grep -qiE "\b(I('ll| will)|let me|i owe|i should|i need to|by (eod|monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|next (week|month|quarter))|in the morning|in an hour|next session|come back to|follow up|check on)\b"; then
      correct=$((correct + 1))
    fi
  fi
done
precision=$(echo "scale=2; $correct / $total" | bc)
echo "Precision: $precision ($correct/$total)"
[ "$(echo "$precision > 0.95" | bc)" -eq 1 ] || echo "FAIL: precision too low"
```

**Target:** precision > 0.95 (reject at least 95% of pure
acknowledgments).

## 3-condition rule (first-person + future-tense + deliverable/due date)

```bash
# Each capture candidate must pass the 3-condition rule
capture_candidate="I'll have the regulatory anchors by EOD"

# Condition 1: first-person
echo "$capture_candidate" | grep -qiE "^(i|let me)\\b" || echo "FAIL: not first-person"

# Condition 2: future-tense
echo "$capture_candidate" | grep -qiE "('ll| will|going to|should have|need to)" || echo "FAIL: not future-tense"

# Condition 3: deliverable or due date
echo "$capture_candidate" | grep -qiE "(by |in |next |tomorrow|have |do |deliver |send )" || echo "FAIL: no deliverable/due date"
```

**Failure mode this catches:** a candidate that passes the
regex but fails one of the 3 conditions. The 3-condition
rule is the conservative filter; the regex alone is too
loose.

## Third-party commitment exclusion

```bash
# Third-party commitments should NOT match as Mavis commitments
third_party="Andre said he'd send the report"
# Should fail: subject is "Andre", not "I"
if echo "$third_party" | grep -qiE "^(i|let me)\\b"; then
  echo "FAIL: third-party commitment captured as Mavis"
fi

# Mavis talking about a third party should be re-routed
# (not the canonical case, but covered)
mavis_speaks_about_3p="I'll ask him to send the report"
# This IS a Mavis commitment (she'll do the action of asking),
# so it should capture
echo "$mavis_speaks_3p" | grep -qiE "^(i|let me)\\b" && echo "CAPTURE"
```

**Failure mode this catches:** Mavis's commitments are
captured; third-party commitments (Andre's, others') are
NOT captured as Mavis commitments.

## One-shot operational promise exclusion

```bash
# One-shot operational promises that complete in the same turn
# should NOT be captured
one_shot="I'll run that command now"
# This completes in the same turn — no ledger entry needed.
# The eval is to verify the marker fires (it should, because
# the regex matches) but the human review step excludes it
echo "$one_shot" | grep -qiE "^(i|let me)\\b" && echo "MATCHED-AT-MARKER-LEVEL"
# The chief's review excludes it: "completes in the same turn"

# A non-one-shot commitment should be captured
real_commitment="I'll have it ready by Friday"
echo "$real_commitment" | grep -qiE "^(i|let me)\\b|by friday" && echo "CAPTURE"
```

**Failure mode this catches:** the regex matches a one-shot
operational promise. The chief's review (not the regex)
excludes it.
