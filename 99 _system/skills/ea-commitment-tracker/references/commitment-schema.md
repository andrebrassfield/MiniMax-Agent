# Commitment Schema — ea-commitment-tracker

The 6-field + 5 metadata field schema. Every commitment line
is a JSON object. None of the 6 load-bearing fields are
optional — the format forces rigor.

## The 6 load-bearing fields

| Field | What it captures | Format | Required |
|---|---|---|---|
| **`commitment`** | The verbatim or sharpened quote | First-person, future-tense, ≤2 sentences | **yes** |
| **`beneficiary`** | Who the commitment is to | `andre` (default) or named | **yes** |
| **`due_by`** | When the deliverable is due | ISO 8601 with timezone, or `next-session` | **yes** |
| **`surface`** | Where the deliverable lands | File path, project path, or "TBD" | **yes** |
| **`dependencies`** | What blocks this | Array of strings (other commitments, Andre-input, external) | **yes** |
| **`status`** | Lifecycle state | `open` → `in-progress` → `delivered` / `dropped` / `reversed` | **yes** |

## The 5 metadata fields

| Field | What it captures | Format | Required |
|---|---|---|---|
| **`ts`** | When the commitment was made | ISO 8601 with timezone | **yes** |
| **`session_pointer`** | Where it was said | Session ID or chat reference | **yes** |
| **`delivered_at`** | When the deliverable landed | ISO 8601, or `null` until delivered | yes (null until delivered) |
| **`reversed_at`** | When the commitment was reversed | ISO 8601, or `null` | yes (null until reversed) |
| **`reversal_reason`** | Why it was reversed (if applicable) | Short string | yes (empty string until reversed) |

## Full JSON template

```json
{
  "ts": "2026-06-16T23:24:37-05:00",
  "commitment": "Have the regulatory anchors codified in ea-research-brief by EOD",
  "beneficiary": "andre",
  "due_by": "2026-06-16T23:59:59-05:00",
  "surface": "~/.mavis/agents/mavis/skills/ea-research-brief/SKILL.md",
  "dependencies": [],
  "status": "open",
  "session_pointer": "mvs_697b3c19c91b4910bfa4bc09914b60d7",
  "delivered_at": null,
  "reversed_at": null,
  "reversal_reason": null
}
```

## Status lifecycle

```
   open ────► in-progress ────► delivered
     │              │                  (terminal)
     │              │
     │              ├────► dropped    (terminal — surface
     │              │                   didn't pan out)
     │              │
     │              └────► reversed   (terminal — Andre said
     │                                drop it, requires reason)
     │
     └────────────────────► dropped (terminal — chat promise
                                          never picked up)
```

The status field is the only field that gets updated
post-creation, and even then via append (new line references
the original `ts`), never via edit.

## The append discipline (the load-bearing rule)

**Never edit a prior line.** Status changes are new lines
that reference the original `ts`. The original line stays
forever. Reversals and deliveries are new lines, not edits.

Why: the audit trail is the value, not the cleanliness of
the file. If you edit, you lose the history of when the
commitment was made, when it changed, and why. If you
append, you have the full picture.

## Field parsing rules

### commitment

- Quote verbatim if the wording is precise
- If the chat is loose ("yeah I'll get to that"), sharpen to
  one specific sentence per EA contract behavior #2
- Never lose the due-by in the sharpening

### beneficiary

- Default: `andre` (string, lowercase)
- If commitment is to a third party (rare for Mavis), name
  them: e.g., `"third-party: <name>"`

### due_by

- If chat said "by EOD" → today's 23:59:59 in CT
- If chat said "Friday" → next Friday 23:59:59 CT
- If chat said "tomorrow morning" → tomorrow 09:00 CT
- If no due-by given → `next-session` (literal string, not
  ISO 8601)

### surface

- File deliverable → file path
- Project deliverable → project path
- Decision/brief deliverable → doc path
- Unclear → `"TBD"` and flag in dependencies

### dependencies

- Array of strings, may be empty
- If Andre needs to do something first: `["andre-to-send-Y"]`
- If another commitment blocks: `["commitment:<original-ts>"]`
- If external: `["external:<description>"]`

### status

- Initial: `"open"`
- On pickup: `"in-progress"`
- On delivery: `"delivered"` (via append)
- On drop: `"dropped"` (via append, requires reason)
- On reversal: `"reversed"` (via append, requires reason)
