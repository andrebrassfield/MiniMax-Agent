# Filter Rules — x-lead-qualifier

The 5 intent signal types + the spam filter + the
classification procedure. The skill only drafts DMs
for engagement that matches one of the 5 types AND
has a confidence score ≥ 0.6.

---

## The 5 intent signal types

### 1. `ai_automation_question`

**Patterns:**
- "How does that integration work?"
- "What stack are you using?"
- "What AI tools are you using?"
- "How do you build X with AI?"
- "Can AI do Y?"

**Why it qualifies:** Specific question about AI
tools, integrations, or stacks. The lead is at the
"researching solutions" stage.

### 2. `pain_point_statement`

**Patterns:**
- "I need help with this"
- "We're losing $X to Y"
- "I tried Z and it didn't work"
- "This is taking forever"
- "We can't keep doing this manually"

**Why it qualifies:** Expressed pain. The lead has a
concrete problem.

### 3. `integration_inquiry`

**Patterns:**
- "How does X integrate with Y?"
- "Does your tool work with Z?"
- "Can I connect A and B?"

**Why it qualifies:** Specific integration question.
The lead is evaluating technical fit.

### 4. `job_defense_question`

**Patterns:**
- "How do I learn this?"
- "Where do I start?"
- "I'm worried about AI taking my job"
- "What skills should I learn?"

**Why it qualifies:** Skill/learning gap. The lead is
trying to upskill.

### 5. `operational_distress`

**Patterns:**
- "My VAs are burning out"
- "We're scaling and breaking"
- "Things are falling through the cracks"
- "I need to hire but can't afford to"

**Why it qualifies:** Operational scaling pain. The
lead is at the "we need to fix this now" stage.

---

## The spam filter

| Filter | Threshold | Reason |
|---|---|---|
| Min follower count | 50 | Bots / new accounts typically have <50 followers |
| Min account age | 30 days | Burner accounts typically <30 days old |
| Spam signal keywords | reject | "crypto giveaway", "follow back", "DM for collab" |
| Verified status | optional | Default to include all |

Apply the filter BEFORE intent classification. Spam
accounts don't qualify, regardless of intent.

## The classification procedure

```python
def classify_intent(text: str) -> tuple[str, float]:
    """Classify engagement text into one of the 5 intent types.
    Returns (intent_type, confidence)."""
    text_lower = text.lower()

    # Pattern matches per intent type
    patterns = {
        "ai_automation_question": [
            r"how does.*integrat", r"what stack", r"what.*tools",
            r"how do you build.*ai", r"can ai do"
        ],
        "pain_point_statement": [
            r"i need help", r"losing.*\\$", r"i tried.*didn't work",
            r"taking forever", r"can't keep.*manual"
        ],
        "integration_inquiry": [
            r"how does.*integrate with", r"work with", r"connect.*and"
        ],
        "job_defense_question": [
            r"how do i learn", r"where do i start", r"worried about",
            r"what skills"
        ],
        "operational_distress": [
            r"burning out", r"scaling.*breaking", r"falling through",
            r"need to hire"
        ]
    }

    # Score each intent type
    scores = {}
    for intent, pattern_list in patterns.items():
        score = 0
        for pattern in pattern_list:
            if re.search(pattern, text_lower):
                score += 1
        scores[intent] = score

    # Return the highest-scoring intent (if any)
    if not scores or max(scores.values()) == 0:
        return ("", 0.0)

    best_intent = max(scores, key=scores.get)
    # Confidence: ratio of matched patterns to total patterns
    # for the best intent
    confidence = scores[best_intent] / len(patterns[best_intent])
    return (best_intent, confidence)
```

## Confidence threshold

Below 0.6 confidence → skip (too ambiguous for a
qualification DM). The lead's intent is unclear; the
Scribe would have to guess at the technical tip.

Above 0.6 → dispatch the Scribe. The lead's intent is
clear enough to write a useful DM.

## The "no intent" case

If the engagement text is:
- Pure praise ("Great post!") with no question
- Spam signal keywords
- Off-topic (not related to AI/automation/trading)
- Single emoji ("👍") with no text

→ Skip silently. Do not draft a DM.

## What this filter is NOT

- **Not a perfect classifier.** Some engagement falls
  between types (e.g., a pain point that's also a job
  defense question). The chief reviews the Scribe's
  draft; the filter is a starting point, not the final
  word.
- **Not context-aware.** The filter doesn't know the
  lead's history with @DreTheSalesGuy. A first-time
  mention and a 5th-time reply are treated the same.
- **Not exhaustive.** New intent types may emerge as
  the operator's X engagement evolves. Update the
  pattern list as needed.
