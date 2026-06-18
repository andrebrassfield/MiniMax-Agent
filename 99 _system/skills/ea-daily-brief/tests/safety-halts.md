# Safety Halts — ea-daily-brief

The skill must HALT (not improvise) when any of these fire. The
"halt" means: stop, surface the condition, do not fabricate a brief.

## H1. Empty corpus (<24h of new inbox activity)

**Detection:** The 24h `find` of `00 Inbox/` returns no files.

**Expected response:** Halt. Do not write a brief. The
`vault-daily-logger` cron handles the empty case; the brief does
not. Surface "no usable corpus today" to Andre.

## H2. Brief already written

**Detection:** `00 Inbox/brief-YYYY-MM-DD.md` already exists.

**Expected response:** Halt. Do not overwrite. To update, append a
`## Update — HH:MM CT` section (preserves the audit trail). Surface
the existing brief path to Andre.

## H3. Today's daily note has a `daily_brief:` link

**Detection:** Today's `01 Daily/YYYY-MM-DD.md` already references
the brief (a `daily_brief:` line or similar).

**Expected response:** Halt. The brief has been written; this is the
ledger check. Do not duplicate.

## H4. Single-domain corpus (all 24h items are one project)

**Detection:** All 24h inbox items are from the same project
directory (e.g., all `03 Projects/X-Content-Engine/`).

**Expected response:** The brief is cross-project by design. A
single-project corpus means a 1-connection brief at most. Write it
with the "inbox was thin" note. Do not pad with weak connections.

## H5. Corpus suggests task, not question

**Detection:** The 3 connections + 1 pattern naturally lead to a
"do you want me to do X?" question, not a decision.

**Expected response:** Halt before writing. Rewrite the question
using a good form (see `references/question-forms.md`). The brief
fails if the question is a task-asking question.

## H6. Today's daily note is missing AND <100 bytes

**Detection:** Today's `01 Daily/YYYY-MM-DD.md` doesn't exist or has
<100 bytes of body.

**Expected response:** Proceed without the daily note context. The
`vault-daily-logger` cron will fill it later in the day; the brief
should not wait. This is not a halt — it's a proceed-with-caveat.

## Eval cases

| Halt | Input (mock state) | Expected behavior |
|---|---|---|
| H1 | 24h inbox find returns 0 files | Halt, no brief |
| H2 | `00 Inbox/brief-YYYY-MM-DD.md` exists | Halt, surface existing path |
| H3 | daily note has `daily_brief:` link | Halt, brief already exists |
| H4 | all 24h items are one project | Write 1-connection brief, note "thin" |
| H5 | closing line is "do you want me to X?" | Halt, rewrite question |
| H6 | daily note missing, <100 bytes | Proceed without context |
