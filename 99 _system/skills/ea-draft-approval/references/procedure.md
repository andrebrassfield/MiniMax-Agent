# Procedure — ea-draft-approval

The 5-step procedure with bash commands. The SKILL.md
only carries the procedure overview. The actual commands
live here.

---

## Step 1: SCAN — find drafts modified since the last run

```bash
VAULT="/Users/brassfieldventuresllc/MiniMax-Agent"
DRAFTS_DIR="$VAULT/03 Projects/X-Content-Engine/drafts"
STATE_FILE="$HOME/.mavis/agents/mavis/crons/ea-draft-approval.state.json"

# Initialize state on first run
if [ ! -f "$STATE_FILE" ]; then
  mkdir -p "$(dirname "$STATE_FILE")"
  cat > "$STATE_FILE" <<'EOF'
{
  "last_scan_at": null,
  "proposals": []
}
EOF
fi

# Find draft files modified in the last 24h (or since last_scan_at)
LAST_SCAN=$(state_get last_scan_at)
DRAFTS=$(find "$DRAFTS_DIR" -maxdepth 1 -type f -name '*.md' -newermt "$LAST_SCAN" 2>/dev/null)
```

For each file, parse the individual posts. The Scribe's
batch format is in `references/scribe-batch-format.md`.

## Step 2: PROPOSE — post each draft to Telegram

For each draft, post a Telegram message with this
structure:

```
Draft N: <title>
Pillar: <which of the 6>
Source: <the idea from content_brain backlog>

<Post text — verbatim, no edits>

Reply: approve / deny / edit
```

Keep the post text verbatim. Do NOT add commentary, do
NOT shorten, do NOT format. Andre needs to see exactly
what the Scribe wrote.

The proposal must be a single Telegram message per
draft. If the draft is too long for one message (>4096
chars), split into "Draft N (1/2)" and "Draft N (2/2)" but
keep the approve instruction only in the last message.

After posting, record the proposal in the state file.
The state schema is in `references/state-schema.md`:

```json
{
  "draft_id": "<file>:<draft-N>:<sha256-of-post-text>",
  "source_file": "drafts/humanized-machine-batch-2026-06-16-v2.md",
  "draft_number": 1,
  "post_text": "<verbatim>",
  "proposed_at": "<ISO>",
  "response_status": "open",
  "response_text": null,
  "acted_at": null
}
```

The `draft_id` is the stable identifier Andre's reply
will be matched against. The sha256 ensures duplicate
proposals don't get sent for the same post.

## Step 3: CAPTURE — match Andre's reply to a draft_id

When Andre replies (on Telegram or in a Mavis session),
classify the reply per `references/reply-patterns.md`:

| Reply pattern | Action |
|---|---|
| `approve`, `approved`, `ship it`, `yes`, `go`, `+1` | mark draft_id as approved |
| `deny`, `denied`, `kill it`, `no`, `-1`, `skip` | mark draft_id as denied |
| `edit <text>` or a reply that starts with the post text but differs | mark draft_id as edited, capture new text |
| Anything else | ask Andre to clarify (one short message: "approve / deny / edit?") |

Update the state file with the response:

```json
{
  "response_status": "approved" | "denied" | "edited",
  "response_text": "<verbatim reply>",
  "responded_at": "<ISO>"
}
```

## Step 4: ACT — move / archive / edit

For each closed proposal (response_status != "open"):

**Approved:** preserve the batch file structure; copy the
approved post into the Scribe's `approved/` directory,
preserving the `## Draft N` header. If the original file
had only this draft (single-draft file), move the whole
file to `approved/`. If it had multiple drafts, extract
just the approved one into a new `approved/` file.

```bash
# For a multi-draft batch file with Draft N approved:
# Extract just Draft N into a new approved file
python3 -c "
import re
with open('drafts/$SOURCE_FILE') as f: content = f.read()
match = re.search(r'## Draft $N.*?(?=^## Draft |\Z)', content, re.MULTILINE | re.DOTALL)
if match:
    with open('approved/$DRAFT_TITLE.md', 'w') as out: out.write(match.group(0))
"
```

**Denied:** move the source file to `archive/denied/`
(preserve the whole batch; do not split)

```bash
mkdir -p archive/denied
mv drafts/$SOURCE_FILE archive/denied/
```

**Edited:** replace the post text in the source file
with the edited version, then move the source file to
`approved/` (or extract if multi-draft)

```bash
python3 -c "
import re
with open('drafts/$SOURCE_FILE') as f: content = f.read()
# Replace the post text under '## Draft N' with the edited version
new = re.sub(
    r'(## Draft $N.*?)(?=\n\n## |\Z)',
    r'\1\n\n$EDITED_TEXT\n',
    content, count=1, flags=re.DOTALL
)
with open('approved/$DRAFT_TITLE.md', 'w') as out: out.write(new)
"
```

After the action, update the state:

```json
{ "acted_at": "<ISO>", "action": "moved" | "archived" | "edited" }
```

## Step 5: UPDATE — the post-N chain picks up `approved/`

After the action, the file is in `approved/`. The post-N
cron chain (post-1-v2-2026-06-16 style, with the silent-
failure + chain-validation + duplication-detection
patches) will pick it up on the next scheduled run, or
on the next post-N trigger.

**The loop is now closed end-to-end:**

```
Scribe drafts → Mavis proposes → Andre approves →
Mavis moves to approved/ → post-N publishes →
Analytics learns → Scribe's next batch uses the analytics
```
