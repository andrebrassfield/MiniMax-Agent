# Daily Brief Callout — ea-commitment-tracker

The format for the "open commitments" callout in the
`ea-daily-brief`. The brief surfaces the 3 most
time-sensitive commitments + the overdue count.

## Callout format (the load-bearing shape)

```markdown
## Open commitments (3 of N)

🔴 **OVERDUE: <count>** commitments past due. Surface first.

### 1. <commitment text>
- **Due:** <due_by> (<time-until-due>)
- **Surface:** <surface path>
- **Dependencies:** <dependencies, if any>
- **Session:** <session_pointer>

### 2. <commitment text>
- **Due:** <due_by> (<time-until-due>)
- **Surface:** <surface path>

### 3. <commitment text>
- **Due:** <due_by> (<time-until-due>)
- **Surface:** <surface path>

(Remaining <N-3> commitments: see `/commitments` workflow)
```

## Ranking rules (the 3 most time-sensitive)

1. **Overdue first.** If any commitment has `due_by < now`
   and `status = open`, the callout becomes a red flag.
2. **Then by due-date proximity.** Soonest `due_by` first.
3. **Then by status.** `in-progress` before `open` (the
   work is in flight, more likely to deliver on time).
4. **Then by `ts`** (older commitments first, FIFO).

The 3 are the callout. The full list is the
`/commitments` workflow (separate command, not in the
brief).

## When the callout becomes a red flag

The callout is a red flag if:
- **Any commitment is overdue** (due_by < now, status = open)
- **Any commitment is approaching overdue** (due_by within
  the next 4 hours and status = open)

When red flag:
- The callout moves to the TOP of the brief, before all
  other sections
- The overdue count is shown in red
- Each overdue commitment gets the full detail block (not
  just summary)

## When to surface

The brief gets the callout:
- **At the start of the brief** (per `ea-daily-brief`
  constraint #4) — open commitments are NEVER buried
- **At any time during a Mavis-touch** (if the EA is
  running mid-session and a commitment is overdue, surface
  inline)
- **Before any new work starts** (if the EA is about to
  pick up a new task, check the open commitments first)

The brief does NOT enumerate all open commitments. That's
`/commitments` workflow territory. The brief surfaces only
the 3 most time-sensitive + the overdue count.

## What the callout does NOT include

- **All open commitments** — that's `/commitments`
- **Delivered commitments** — those go in the
  `[delivered]` log, not the brief
- **Reversed/dropped commitments** — those are in the
  audit trail, not the brief
- **Andre's commitments to other people** — separate
  ledger, not Mavis's
- **One-shot operational promises** — never reach the
  ledger in the first place

## Eval cases

```bash
# Test 1: overdue triggers red flag
overdue_count=$(jq -r 'select(.status == "open" and .due_by < now)' commitments.jsonl | wc -l)
[ "$overdue_count" -gt 0 ] && echo "RED FLAG"

# Test 2: ranking by due-date proximity
# (sort by due_by, take top 3)
sort -t'"' -k4 commitments.jsonl | head -3

# Test 3: 3 most time-sensitive + count
top_3=$(jq -r 'select(.status == "open") | .due_by' commitments.jsonl | sort | head -3)
total_open=$(jq -r 'select(.status == "open")' commitments.jsonl | wc -l)
echo "Open: $total_open. Top 3: $top_3"
```
