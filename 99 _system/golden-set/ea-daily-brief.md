---
parameter_id: ea-daily-brief
curated_by: Andre
last_review: 2026-06-17
case_count: 3
---

# GoldenSet — ea-daily-brief

## Case 1: standard morning, sufficient inbox activity

**Input (x_i):**
> First Mavis interaction of the day. `00 Inbox/` has 4 new captures (2 from yesterday's session, 2 from overnight X bookmarks). `02 Notes/` has 1 new article (Claude Code skill evolution pattern). No new daily note exists yet for today. Andre asks: "what's the brief?"

**Expected output (y_i):**
> Writes `00 Inbox/brief-YYYY-MM-DD.md` with EXACTLY:
> - 3 connections (per `ea-contract.md` connection types A-D)
> - 1 pattern surfaced across 2+ notes
> - 1 question (per Behavior #3 — never a task list)
> - Each connection cites the specific notes it links
> - Ends with the question, not a TODO
> - Skips fabrication if <24h of inbox activity (no padding)

**Reasoning for inclusion:**
> This is the canonical case. Tests all 4 connection types are reachable, the question-end discipline holds, and the brief is genuinely grounded (not generic). A skill that produces a 3-connection brief with a question is a passing skill. A skill that produces a TODO list, or fewer than 3 connections, or connections without source citations, is failing.

**Failure modes this catches:**
> - Producing 5 connections instead of 3 (over-generation, common failure)
> - Producing a TODO list instead of a question (treats EA as PM, common failure)
> - Generic connections that don't cite specific notes (hallucinated grounding)
> - Skipping the question entirely (Behavior #3 violation)

## Case 2: minimal inbox activity (halt-not-fabricate)

**Input (x_i):**
> > First Mavis interaction of the day. `00 Inbox/` is empty. No new notes in last 24h. No activity. Andre asks: "what's the brief?"

**Expected output (y_i):**
> > Mavis **halts** the brief. Returns: 'Insufficient activity in last 24h to ground a brief. Either capture something or check back later.' Does NOT produce a 3-connection brief from unrelated older notes.

**Reasoning for inclusion:**
> Tests the halt-not-fabricate discipline from `ea-daily-brief`. The most common failure mode is filling the brief with stale connections to satisfy the 3-connection rule. Better to halt than hallucinate.


## Case 3: high-stakes project launch day

**Input (x_i):**
> > It's the morning of a major client launch. `00 Inbox/` has 6 captures (3 client emails, 2 internal coordination notes, 1 vendor update). `02 Notes/articles/` has a new article about the client's industry. `01 Daily/` has yesterday's notes about prep.

**Expected output (y_i):**
> > Brief with 3 connections: (A) same principle across client emails + new article; (B) contradiction between vendor timeline and internal coordination; (C) synthesis of yesterday's prep + today's signals into one operational insight. Pattern: a recurring risk Andre hasn't consciously seen. Question: 'Want me to draft a launch-day incident-response skeleton, or are we keeping the runbook as-is?' Brief is grounded in actual notes; no fabricated urgency.

**Reasoning for inclusion:**
> Tests quality under pressure. Failure mode is producing generic 'launch day best practices' content that ignores Andre's specific vault state. Brief must be EARNED by the captures present, not templated.
