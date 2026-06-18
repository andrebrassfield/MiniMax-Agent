# State Schema — ea-draft-approval

The state file schema. The state file is at
`~/.mavis/agents/mavis/crons/ea-draft-approval.state.json`
(agent home canonical, mirrored to
`~/MiniMax-Agent/99 _system/crons/ea-draft-approval.state.json`
per `ea-skill-evolution` Hard Constraint #6).

## Top-level schema

```json
{
  "last_scan_at": "<ISO or null>",
  "proposals": [
    {
      "draft_id": "<file>:<draft-N>:<sha256-of-post-text>",
      "source_file": "drafts/humanized-machine-batch-2026-06-16-v2.md",
      "draft_number": 1,
      "post_text": "<verbatim>",
      "proposed_at": "<ISO>",
      "response_status": "open",
      "response_text": null,
      "responded_at": null,
      "acted_at": null,
      "action": null
    }
  ]
}
```

## Field definitions

| Field | Type | Description |
|---|---|---|
| `last_scan_at` | ISO 8601 \| null | Timestamp of the last scan. Null on first run |
| `proposals` | array | All proposals (open + closed) |
| `draft_id` | string | `<source_file>:<draft_number>:<sha256-of-post-text>`. Stable identifier for matching Andre's reply |
| `source_file` | string | Path to the Scribe's batch file (relative to vault root) |
| `draft_number` | integer | The `N` from `## Draft N` header |
| `post_text` | string | The verbatim post text from the Scribe |
| `proposed_at` | ISO 8601 | When Mavis proposed this draft to Andre |
| `response_status` | enum | "open" / "approved" / "denied" / "edited" |
| `response_text` | string \| null | Verbatim reply from Andre |
| `responded_at` | ISO 8601 \| null | When Andre replied |
| `acted_at` | ISO 8601 \| null | When Mavis moved/archived/edited the file |
| `action` | enum \| null | "moved" / "archived" / "edited" |

## State lifecycle

```
  [proposed] ──────► [open] ──────► [approved] ──► [moved]
                            │                        │
                            │                        └► [acted]
                            │
                            ├──────► [denied] ───► [archived] ──► [acted]
                            │
                            └──────► [edited] ───► [edited+approved] ──► [acted]
```

The state is append-only. New proposals append;
status changes are updates, not edits.

## Stable draft_id (the load-bearing discipline)

The `draft_id` is `<file>:<draft-N>:<sha256-of-post-text>`.

**Why the sha256?** If the Scribe rewrites the file
between the proposal and the reply, the post_text's
sha256 changes. Mavis treats this as a new draft
(re-propose, don't act on the stale reply).

**Why the file path + draft number?** The combination
uniquely identifies the proposal. If the Scribe writes
the same post text in two different files, they get
different draft_ids.

## Mirror discipline

The state file is at
`~/.mavis/agents/mavis/crons/ea-draft-approval.state.json`
(agent home, canonical).

The mirror is at
`~/MiniMax-Agent/99 _system/crons/ea-draft-approval.state.json`
(vault).

The mirror write is the precondition for `status: shipped`.
If the mirror write fails, the state is in a
`mirror-pending` state until the next sync.

Mirror pattern (atomic):

```bash
# Write to tmp + atomic move
TMP="/tmp/ea-draft-approval-state-$$.json"
cat > "$TMP" <<EOF
[state content]
EOF
mv -f "$TMP" "$HOME/.mavis/agents/mavis/crons/ea-draft-approval.state.json"

# Mirror to vault
cp -f "$HOME/.mavis/agents/mavis/crons/ea-draft-approval.state.json" \
      "$HOME/MiniMax-Agent/99 _system/crons/ea-draft-approval.state.json"

# Verify byte-identity
cmp -s "$HOME/.mavis/agents/mavis/crons/ea-draft-approval.state.json" \
        "$HOME/MiniMax-Agent/99 _system/crons/ea-draft-approval.state.json" \
  || echo "FAIL: mirror mismatch"
```

## What the state file is NOT

- **Not a memory write.** The state is in the cron state
  file, not in Mavis's memory.
- **Not a chat log.** Only proposals + responses are
  recorded. The full chat history is elsewhere.
- **Not a backup of the Scribe's drafts.** The Scribe's
  drafts are in `drafts/`. The state file tracks
  proposals + responses, not the source content (the
  source content may be moved or deleted).
- **Not a global decision log.** That's
  `02 Notes/decisions/`. This state is for draft
  proposals specifically.
