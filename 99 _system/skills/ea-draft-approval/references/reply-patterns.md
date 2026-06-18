# Reply Patterns — ea-draft-approval

How Mavis classifies Andre's reply to a draft proposal.
The reply classification is the load-bearing step that
turns the human input into an action.

## The 3 reply classes

| Class | Reply patterns | Action |
|---|---|---|
| **Approve** | `approve`, `approved`, `ship it`, `yes`, `go`, `+1`, `y`, `yep`, `yup` | mark draft_id as approved → move to `approved/` |
| **Deny** | `deny`, `denied`, `kill it`, `no`, `-1`, `skip`, `n`, `nope`, `nah` | mark draft_id as denied → move to `archive/denied/` |
| **Edit** | `edit <text>` or a reply that starts with the post text but differs | mark draft_id as edited → apply the edit → move to `approved/` |

Anything else: ask Andre to clarify with one short
message: "approve / deny / edit?"

## The classification procedure

```python
import re

def classify_reply(reply_text: str) -> str:
    """Classify Andre's reply into approve/deny/edit/clarify."""
    normalized = reply_text.strip().lower()

    # Approve patterns
    approve_patterns = [
        r"^approve", r"^approved", r"^ship it", r"^yes",
        r"^go", r"^\+1", r"^y$", r"^yep$", r"^yup$"
    ]
    for pattern in approve_patterns:
        if re.match(pattern, normalized):
            return "approve"

    # Deny patterns
    deny_patterns = [
        r"^deny", r"^denied", r"^kill it", r"^no",
        r"^-1", r"^skip", r"^n$", r"^nope$", r"^nah$"
    ]
    for pattern in deny_patterns:
        if re.match(pattern, normalized):
            return "deny"

    # Edit pattern: starts with "edit " or the post text differs
    if normalized.startswith("edit "):
        return "edit"
    # Heuristic: if the reply is longer than 50 chars and
    # doesn't match approve/deny, it's likely an edit
    if len(reply_text.strip()) > 50:
        return "edit"

    return "clarify"
```

## The draft_id matching

Mavis matches the reply to a draft_id by:

1. **Explicit reference:** Andre replies with "Draft 1: <text>"
   → match to the proposal where `draft_number == 1`
2. **Implicit reference:** Andre replies with a single
   word ("approve") → match to the most recent open
   proposal
3. **Stale draft_id:** if the reply's sha256 doesn't
   match the proposal's sha256 → re-propose the new draft

## Stale reply handling (H5)

If the Scribe rewrote the file between the proposal and
the reply, the post_text's sha256 changes. The reply
matches the draft_id, but the post_text is different.

**Discipline:** re-propose the new draft. Do NOT act on
the stale reply.

```python
import hashlib

def is_stale_reply(proposal_post_text: str, current_post_text: str) -> bool:
    proposal_hash = hashlib.sha256(proposal_post_text.encode()).hexdigest()
    current_hash = hashlib.sha256(current_post_text.encode()).hexdigest()
    return proposal_hash != current_hash
```

## Ambiguous reply handling (H4)

If the reply doesn't match any of the 3 classes, ask for
clarification:

> "approve / deny / edit?"

One short message. Don't elaborate. The clarification is
the operator's job.

## What reply patterns are NOT

- **Not "I love it" or "great work."** Praise is not an
  action. If Andre says "great work," Mavis asks for
  clarification.
- **Not "let's discuss" or "what do you think."** These
  are conversations, not decisions. Mavis can engage in
  the conversation, but the proposal stays open until
  Andre gives a clear approve/deny/edit.
- **Not emoji-only.** A thumbs-up emoji is ambiguous
  (approve? or just acknowledgment?). Ask for
  clarification.
- **Not "tomorrow" or "later."** Deferrals don't close
  the proposal. The proposal stays open.

## Cross-reference

- `references/procedure.md` — the 5-step procedure
- `references/state-schema.md` — state file schema
- `references/scribe-batch-format.md` — the Scribe's batch
  format (multi-draft files)
- `tests/state-discipline.md` — append-only, stable-
  draft_id, no-silent-failure checks
