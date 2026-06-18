# Procedure — ea-commitment-tracker

The 5-step procedure with bash commands. The SKILL.md only
carries the procedure overview. The actual commands live
here (the deterministic layer).

---

## Step 1: DETECT — pull commitment markers

Scan the current session for marker phrases. The detection
rule is conservative: only flag statements that are
**first-person + future-tense + have a deliverable or a due
date** (explicit or implied). Pure acknowledgments ("I
see," "got it," "noted") are not commitments.

Marker regex + 3-condition rule + edge cases in
`marker-detection.md`.

If the regex fires on a statement, load this skill and
extract the 6 fields. Do not ask Andre to confirm — the
verbatim quote is the evidence.

## Step 2: EXTRACT — fill the 6 fields

Apply the schema discipline. The hard parts:

- **`commitment`** — quote verbatim if the wording is
  precise ("I'll have the regulatory anchors codified by
  EOD"). If the chat is loose ("yeah I'll get to that"),
  sharpen to one specific sentence per EA contract behavior
  #2. Never lose the due-by in the sharpening.
- **`due_by`** — if the chat said "by EOD," compute today's
  23:59:59 CT. If the chat said "Friday," compute the next
  Friday 23:59:59 CT. If no due-by is given, default to
  `next-session` (the literal string).
- **`surface`** — if the deliverable is a file, the surface
  is the file path. If it's a brief or a decision, the
  surface is the project or the doc. If the deliverable is
  unclear, surface = `TBD` and flag in `dependencies`.
- **`dependencies`** — if Andre needs to do something first
  ("I'll do X once you send me Y"), `dependencies:
  ["andre-to-send-Y"]`. If another commitment blocks this
  one, cross-reference the other commitment's timestamp.

## Step 3: WRITE — append to JSONL + mirror to markdown

```bash
LEDGER=~/.mavis/agents/mavis/commitments.jsonl
MARKDOWN="02 Notes/commitments/$(date +%Y-%m).md"

# Step 3a: append to JSONL (atomic for append)
echo '{"ts":"<ISO>","commitment":"<verbatim>","beneficiary":"andre","due_by":"<ISO or next-session>","surface":"<path>","dependencies":[],"status":"open","session_pointer":"<sid>","delivered_at":null,"reversed_at":null,"reversal_reason":null}' >> "$LEDGER"
LEDGER_EXIT=$?

# Step 3b: mirror to markdown (atomic via tmp + mv)
mkdir -p "$(dirname "$MARKDOWN")"
TMP=$(mktemp)
echo "- [open] <commitment-text> · due <due_by> · <surface-link>" >> "$TMP"
cat "$MARKDOWN" 2>/dev/null >> "$TMP"
mv -f "$TMP" "$MARKDOWN"
MARKDOWN_EXIT=$?

# Step 3c: if either failed, surface (do not retry silently)
if [ $LEDGER_EXIT -ne 0 ] || [ $MARKDOWN_EXIT -ne 0 ]; then
  echo "MIRROR SYNC FAILED: ledger=$LEDGER_EXIT markdown=$MARKDOWN_EXIT" >&2
fi
```

**Append-only.** Never edit a prior line. Status changes
are new lines that reference the original `ts`.

Full mirror discipline in `mirror-discipline.md`.

## Step 4: SURFACE — include in the next daily brief

The daily brief gets a callout: **"Open commitments: N"**
with the top 3 (by due-date proximity, soonest first). If
any commitment is overdue (due_by < now and status = open),
the callout becomes a **red flag** — Andre should see this
before any other brief content.

The brief does NOT enumerate all open commitments (that's
`/commitments` workflow territory). It surfaces the 3 most
time-sensitive and the overdue count.

Full callout format in `daily-brief-callout.md`.

## Step 5: UPDATE — append on delivery or reversal

When the deliverable lands:

```bash
LEDGER=~/.mavis/agents/mavis/commitments.jsonl
echo '{"ts":"<delivery-ISO>","commitment":"DELIVERED: <original-commitment-text>","original_ts":"<original-ts>","status":"delivered","delivered_at":"<ISO>","surface":"<path-where-it-landed>","session_pointer":"<sid>"}' >> "$LEDGER"
```

When the commitment is reversed (Andre says "drop that" or
"never mind"):

```bash
echo '{"ts":"<reversal-ISO>","commitment":"REVERSED: <original-commitment-text>","original_ts":"<original-ts>","status":"reversed","reversed_at":"<ISO>","reversal_reason":"<why>","session_pointer":"<sid>"}' >> "$LEDGER"
```

**Never edit the original line.** The audit trail is the
value. Reversals are new lines that reference the original.
