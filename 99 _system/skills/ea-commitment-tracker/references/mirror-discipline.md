# Mirror Discipline — ea-commitment-tracker

The atomic mirror write that keeps the JSONL ledger and the
human-readable markdown in sync. Same discipline as
`ea-skill-evolution` mirror discipline — the JSONL is the
canonical, the markdown is the mirror.

## The two surfaces

**JSONL ledger (canonical):**
`~/.mavis/agents/mavis/commitments.jsonl`

One JSON object per line. Append-only. The machine-readable
audit trail.

**Markdown mirror (human-readable):**
`02 Notes/commitments/YYYY-MM.md`

One file per month. Each commitment gets one line with a
`[STATUS]` tag, due date, and a link to the surface. This is
what Andre sees on the daily brief.

## The mirror rules

1. **JSONL is canonical.** The markdown is derived. If
   they disagree, the JSONL wins.
2. **Append in both.** When a commitment is added, the line
   goes to the JSONL AND a corresponding line goes to the
   current month's markdown.
3. **Status changes update both.** When a commitment is
   delivered or reversed, the JSONL gets a new line AND the
   markdown's `[STATUS]` tag updates.
4. **Monthly rotation.** The current month's markdown is
   always active. Past months' files stay as-is (they're
   the historical record).
5. **No edit on prior lines.** Same as the JSONL. The
   markdown lines are also append-only for the
   `commitment` text. The `[STATUS]` tag can update (it's a
   status, not the commitment text).

## Atomic write procedure

The write must be atomic. If the JSONL append succeeds but
the markdown update fails, the mirror is out of sync. Use a
tmp + `mv` pattern:

```bash
LEDGER=~/.mavis/agents/mavis/commitments.jsonl
MARKDOWN="02 Notes/commitments/$(date +%Y-%m).md"

# Step 1: append to JSONL (already atomic for append)
echo '{"ts":"<ISO>","commitment":"<verbatim>","beneficiary":"andre","due_by":"<ISO or next-session>","surface":"<path>","dependencies":[],"status":"open","session_pointer":"<sid>","delivered_at":null,"reversed_at":null,"reversal_reason":null}' >> "$LEDGER"
LEDGER_EXIT=$?

# Step 2: append to markdown (atomic via tmp + mv)
mkdir -p "$(dirname "$MARKDOWN")"
TMP=$(mktemp)
echo "- [open] <commitment-text> · due <due_by> · <surface-link>" >> "$TMP"
cat "$MARKDOWN" 2>/dev/null >> "$TMP"
mv -f "$TMP" "$MARKDOWN"
MARKDOWN_EXIT=$?

# Step 3: if either failed, surface (do not retry silently)
if [ $LEDGER_EXIT -ne 0 ] || [ $MARKDOWN_EXIT -ne 0 ]; then
  echo "MIRROR SYNC FAILED: ledger=$LEDGER_EXIT markdown=$MARKDOWN_EXIT" >&2
  # Halt: surface the failure
fi
```

## Markdown format (the per-line shape)

```markdown
- [open] Have the regulatory anchors codified in ea-research-brief by EOD · due 2026-06-16 23:59 CT · [ea-research-brief](~/.mavis/agents/mavis/skills/ea-research-brief/SKILL.md)
- [in-progress] Draft the weekly synthesis · due 2026-06-21 09:00 CT · [weekly-synthesis](02 Notes/weekly-synthesis-2026-06-21.md)
- [delivered] Surface open commitments in the daily brief · due 2026-06-17 08:00 CT · delivered at 2026-06-17 07:42 CT
- [reversed] Build a custom agent for the hospital · due 2026-06-20 · reversed at 2026-06-18 14:00 CT (Andre said drop it — too speculative)
- [dropped] Send the audit log to compliance · due 2026-06-19 · dropped at 2026-06-19 09:00 CT (compliance system changed scope)
```

The format is:
- Status tag in brackets: `[open]` / `[in-progress]` /
  `[delivered]` / `[reversed]` / `[dropped]`
- Commitment text (verbatim or sharpened)
- Due date + time
- Surface link (or path)
- If delivered/reversed/dropped: terminal timestamp + reason

## Status update rule

The `[STATUS]` tag updates in place (it's a status, not
content). The `commitment` text does NOT update (it's the
audit trail).

**Example status update:**
```markdown
# Before
- [open] Have the regulatory anchors by EOD

# After (status update in place)
- [delivered] Have the regulatory anchors by EOD · delivered at 2026-06-16 22:14 CT
```

The line is rewritten with the new status + delivery
timestamp. The original commitment text is preserved.

## Cross-month commitments

If a commitment is created in May and delivered in June, the
delivery event updates the **June** markdown (the current
month), not the May markdown. The May markdown keeps the
original line. The audit trail crosses month boundaries but
the markdown update stays in the current month.

The JSONL has both events: the original (May) and the
delivery (June). The `original_ts` field links them.
