---
description: "The 4-step ea-correction-capture procedure — scan recent activity, classify corrections via LLM, surface to Andre for review, route approved ones to skill evolution. First 7 days = manual calibration. Moved from inline per the aggressive skill-scaling-law template 2026-06-22."
---

# ea-correction-capture — The 4-step Procedure

## 1. Scan recent activity

Find files modified in the scan window (default 24h):
- `~/MiniMax-Agent/02 Notes/` (vault notes, patterns, articles, decisions)
- `~/MiniMax-Agent/01 Daily/` (daily logs)
- `~/.mavis/agents/mavis/memory/MEMORY.md` (recent appends)

Cap at 20 files per run (LLM context budget). For each file, read first 2KB only.

## 2. Classify corrections via LLM

Call the classifier:
```bash
python3 ~/.mavis/agents/mavis/skills/ea-correction-capture/scripts/classify.py --since 24h
```

The classifier prompts the LLM to identify corrections — moments where Andre said "stop doing X", "do Y instead", expressed a preference, or vetoed an approach. Output schema:

```json
{
  "corrections": [
    {
      "timestamp": "...",
      "trigger": "the actual phrase or paraphrase",
      "type": "decision-mode | preference | new-info | correction",
      "context": "what Mavis did that triggered the correction",
      "confidence": 0.0-1.0,
      "suggested_skill_update": "what skill/memory change this implies"
    }
  ]
}
```

If no corrections: return empty list (do NOT fabricate).

## 3. Surface to Andre (daily Telegram summary)

Write the daily log at `~/.mavis/state/corrections-YYYY-MM-DD.md`:

```markdown
---
date: YYYY-MM-DD
calibration-day: N
mode: manual | auto
---

# Corrections Detected — YYYY-MM-DD

**Scan window:** last 24h
**Files scanned:** N
**Corrections found:** N

## Corrections

### [1] <trigger phrase or paraphrase>
- **Type:** decision-mode / preference / new-info / correction
- **Context:** <what Mavis did>
- **Confidence:** 0.NN
- **Suggested update:** <what skill/memory change implies>

[repeat per correction]

## Calibration status

- Day N of manual eval (day 1-7)
- Confirmed true positives: N
- Confirmed false positives: N
- True-positive rate: N%

[if day 7+] Suggested auto-mode threshold: 0.NN

## Andre's review

For each correction above, reply:
- `confirm` → mark as true positive (used for calibration)
- `deny` → mark as false positive (used for calibration)
- `route` → approve AND route to skill evolution queue
```

Send a Telegram summary to Andre with: corrections count, day N status, link to the daily log file.

Mirror the daily log to `~/MiniMax-Agent/99 _system/state/corrections-YYYY-MM-DD.md`.

## 4. Route approved corrections (auto mode only)

In auto mode (day 8+), for corrections with confidence >= threshold:
- Append to `~/.mavis/state/correction-routing-queue.mdl`
- The chief reviews the queue weekly and applies approved updates via `ea-skill-evolution` or direct memory edits
- Each routing entry: `YYYY-MM-DD HH:MM | confidence: 0.NN | type: <type> | target: <skill-name> | trigger: "<phrase>" | suggested: <update>`

In manual mode (day 1-7): NO auto-routing. Surface only.

## Calibration procedure

Day 1-7: **Manual eval mode.**
- Chief surfaces corrections
- Andre reviews each, replies `confirm` / `deny` / `route`
- State file tracks: `confirmed_positive`, `confirmed_negative`, `day_count`
- NO auto-routing regardless of confidence

Day 8: **Calibration threshold computed.**
- Calculate true-positive rate at threshold 0.7
- If >=60% → recommend switching to auto mode with threshold 0.7
- If <60% → suggest threshold adjustment (raise to 0.8 or 0.9)
- Andre makes the call

Day 15+: **Auto mode (if approved).**
- Route corrections with confidence >= calibrated threshold automatically
- Surface lower-confidence ones for manual review
- Track routing accuracy, recalibrate monthly

State file: `~/.mavis/state/correction-calibration.json`
```json
{
  "started_at": "YYYY-MM-DD",
  "current_day": N,
  "mode": "manual | auto",
  "threshold": 0.7,
  "confirmed_positive": N,
  "confirmed_negative": N,
  "total_scanned": N,
  "true_positive_rate": N.NN
}
```

## What this skill does NOT do

- Does not learn from positive feedback (only corrections). "This is fine" is captured but doesn't trigger routing.
- Does not correct peer-agent work (cross-team discipline applies).
- Does not modify skills/memory directly. Routes to a queue; chief reviews + applies.
- Does not fabricate corrections to seem productive. Empty list is a valid result.
