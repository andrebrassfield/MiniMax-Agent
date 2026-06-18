# Procedure — x-lead-qualifier

The 7-step procedure with bash commands. The SKILL.md
only carries the 7-step list. The actual commands live
here.

---

## Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected` → HALT (H1). Tell the
operator to load the Chrome extension per
`mavis browser install` output. Do not proceed with
auto-spawned Chromium fallbacks for x.com.

## Step 2: Open the X notifications tab

```bash
mavis browser tool open_tab '{"url":"https://x.com/notifications"}'
```

Note the returned `tabId`.

## Step 3: Wait for the page to render, then extract engagement

Wait 5-7 seconds for the page to render. Take a
snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":3}'
```

Extract from the snapshot:
- Mentions: post handle + post text
- Replies: same
- DM notifications (X shows a count + a few recent
  senders)

Apply the spam filter from `filter-rules.md`:
- Min follower count (default 50) — skip bot accounts
- Min account age (default 30 days) — skip burner
  accounts
- Verified status — optional, default to include all
- Sentiment — skip pure praise ("Great post!") with
  no question or pain point
- Spam signals — skip accounts with "crypto
  giveaway" / "follow back" / etc. in profile

For each filtered candidate, classify the intent
signal per the 5 types in `filter-rules.md`:
- `ai_automation_question`
- `pain_point_statement`
- `integration_inquiry`
- `job_defense_question`
- `operational_distress`

Each candidate gets a confidence score (0.0-1.0).
Below 0.6 → skip (too ambiguous for a qualification
DM).

## Step 4: For each candidate, dispatch the Scribe

For each intent-qualified candidate (confidence ≥
0.6), call the Scribe with the task spec template.
Each dispatch is a separate
`mavis communication send` call.

```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{"agent":"x-scribe","model":"MiniMax-M2.7","prompt":"<task spec>"}'
```

The task spec is the verbatim block in
`references/scribe-task-spec.md` with placeholders
filled in. One dispatch per candidate.

**Halt conditions for the dispatch:**
- Scribe system prompt returns "persona file missing"
  → halt, surface to operator (H6)
- Scribe returns a DM that fails the verification
  checklist → halt, surface the draft for review
- Dispatch error (timeout, spawn failure) → halt,
  surface

## Step 5: Write the draft to the queue

The Scribe writes to
`03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl`.
The skill's job is to verify the file was written and
the entry has the required sections.

## Step 6: Update the leads ledger

Append a one-line entry to
`03 Projects/X-Content-Engine/queue/qualification-dms.mdl`
(the rolling ledger; the daily file is the per-day
snapshot):

```markdown
- 2026-06-16 14:23 CT — @<handle> · intent: <type> · confidence: <0.0-1.0> · drafted by Scribe · status: pending_review
```

## Step 7: Return summary to operator

Send a one-paragraph summary:
- Number of candidates scanned
- Number of intent-qualified (confidence ≥ 0.6)
- Number of drafts written to the queue
- Queue file path
- Halt conditions, if any
- Suggested next action (operator reviews the queue,
  sends the drafts that fit)
