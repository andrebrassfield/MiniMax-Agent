# Verifier Discipline — ea-closed-loop-builder

The verifier-must-not-be-the-executor check. Boris Cherny's
load-bearing rule: "the maker is too nice grading its own
homework."

## V1. Verifier is not the same model

```bash
# Extract verifier and executor
verifier=$(awk '/^## 4\. FEEDBACK/,/^## 5\./' spec.md | grep -A1 "Verifier" | tail -1)
executor=$(grep "^\\*\\*Owner:\\*\\*" spec.md | sed 's/.*: //')

# Model tokens to check
model_tokens="M[0-9.]+|GPT-[0-9.]+|Claude|Gemini|Grok"

# If executor is a model name, verifier must be a different model
if echo "$executor" | grep -qE "$model_tokens"; then
  executor_model=$(echo "$executor" | grep -oE "$model_tokens" | head -1)
  verifier_model=$(echo "$verifier" | grep -oE "$model_tokens" | head -1)
  if [ "$executor_model" = "$verifier_model" ]; then
    echo "FAIL: verifier and executor are the same model"
  fi
fi
```

**Failure mode this catches:** the spec names the executor
(e.g., "M2.7") and the verifier (e.g., "M2.7 in a different
prompt") as the same model. That's self-verification, not
verification.

## V2. Verifier is not the same agent (when both are agents)

```bash
verifier_agent=$(echo "$verifier" | grep -oE "[a-z-]+(-[a-z]+)?-agent|@?[a-z-]+ agent" | head -1)
executor_agent=$(echo "$executor" | grep -oE "[a-z-]+(-[a-z]+)?-agent|@?[a-z-]+ agent" | head -1)
[ "$verifier_agent" = "$executor_agent" ] && echo "FAIL: verifier and executor are the same agent"
```

**Failure mode this catches:** the spec names the same agent
as executor and verifier (e.g., "Mavis both writes and
reviews"). Even if the system prompt is different, the agent
identity is the same. Pick a different agent.

## V3. Verification has a defined FAIL path

```bash
on_fail=$(awk '/^## 4\. FEEDBACK/,/^## 5\./' spec.md | grep -A1 "On FAIL" | tail -1)
case "$on_fail" in
  *retry*|*escalate*|*halt*|*stop*|*alert*|*notify*)
    echo "PASS: on-FAIL path defined"
    ;;
  *)
    echo "FAIL: on-FAIL path not defined (placebo gate)"
    ;;
esac
```

**Failure mode this catches:** gates that can't fail (no
retry/escalate/halt path). A gate that can't fail is a
placebo.

## V4. Verifier pattern is rank-ordered (auto > cross-model > cross-agent > sampled human > pre-commit)

```bash
# Extract the verifier pattern
verifier_line=$(awk '/^## 4\. FEEDBACK/,/^## 5\./' spec.md | grep "Verifier" | head -1)
case "$verifier_line" in
  *test*|*TypeCheck*|*linter*|*exit code*|*schema*|*validator*)
    echo "PASS: auto-verifiable (pattern 1)" ;;
  *M3*|*M2.7*|*GPT*|*Claude*|*Gemini*|cross.model)
    echo "PASS: cross-model (pattern 2)" ;;
  *-agent*|*-verifier*|*-reviewer*|*-checker*|cross.agent)
    echo "PASS: cross-agent (pattern 3)" ;;
  *sample*|*1 in*|*human*|sampled)
    echo "PASS: sampled human (pattern 4)" ;;
  *pre.commit*|*hook*|*gate*)
    echo "PASS: pre-commit hook (pattern 5)" ;;
  *)
    echo "WARN: verifier pattern not classified" ;;
esac
```

**Failure mode this catches:** the verifier is named but
doesn't fit any of the 5 known patterns (which means it's
probably "looks good to me" or another self-verification
variant).

## V5. Verifier runs at a defined frequency

```bash
frequency=$(awk '/^## 4\. FEEDBACK/,/^## 5\./' spec.md | grep -A1 "Frequency" | tail -1)
case "$frequency" in
  *every*|*each*|*per run*|*1 in*|*sample*|*on demand*)
    echo "PASS: frequency defined" ;;
  *)
    echo "FAIL: frequency not defined" ;;
esac
```

**Failure mode this catches:** the verifier exists but
"when" it runs is vague ("sometimes", "as needed", "when
relevant"). Frequency is a contract.

## V6. Self-verification patterns are flagged

```bash
# Common self-verification patterns
self_verify="same model|self.verify|its own homework|self.grade|self.assess"

if echo "$verifier" | grep -qiE "$self_verify"; then
  echo "FAIL: self-verification pattern detected"
fi
```

**Failure mode this catches:** the spec explicitly says
"the model grades its own work" or "self-verification is
fine" — both are anti-patterns.
