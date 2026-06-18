---
name: ea-draft-approval
description: Codifies the **half-loop bridge** between the Scribe's draft queue and the post-N publish chain. The Scribe (per `agents/scribe.md` Hard Rule #10) writes drafts to `03 Projects/X-Content-Engine/drafts/` but never publishes. The post-N cron chain reads from `approved/` and publishes. The gap: drafts must move from `drafts/` to `approved/` only after Andre approves. This skill codifies Mavis's role as the bridge — propose drafts to Andre via Telegram, capture his approval, move approved drafts to `approved/`, archive denied drafts, and apply edits when given. The procedure: (1) on a daily trigger (default 18:00 CT, after the Scribe's daily work, before the 19:00 x-analytics-tracker), scan `drafts/` for files modified since the last scan; (2) for each new draft file, parse the individual posts (the Scribe's batch files contain 2-4 posts each, separated by `## Draft N` headers); (3) post each draft to Telegram as a separate proposal with: the post text verbatim, a 1-2 line rationale (which pillar, which audience), and the explicit "Reply: approve / deny / edit" instruction; (4) record the proposal in the state file at `~/.mavis/agents/mavis/crons/ea-draft-approval.state.json` with a stable draft_id, the post text, the proposal timestamp, and the response status (open / approved / denied / edited); (5) on Andre's reply, match the reply to a draft_id, update the state, and act: approved → move to `approved/` (preserve the batch file structure for the post-N chain); denied → move to `archive/denied/`; edited → apply the edit, then move to `approved/`. Use this skill when the Scribe writes new drafts, when the daily cron fires, and on Andre's Telegram reply about a draft. Do NOT load for the post-N publish chain (that's the post-N cron), for the Scribe's drafting work (Scribe is its own agent), for the Analytics feedback loop (that's a different cron), or for any draft that's already in `approved/` (the bridge is between `drafts/` and `approved/`, not after).
---

# EA Draft Approval — The Scribe → Andre → post-N Bridge

## What this skill does

You are codifying the bridge between the Scribe's `drafts/` queue and the post-N cron chain's `approved/` queue. The Scribe's Hard Rule #10 ("Never publish to x.com") means every draft needs human approval before publishing. Andre is the human. The bridge is Mavis: scan the Scribe's queue, propose each draft to Andre, capture the reply, and route the approved drafts to the post-N chain.

**The discipline:** the Scribe does the writing, Andre does the approving, Mavis does the routing. The post-N chain does the publishing. Four roles, three handoffs, zero ambiguity. The skill codifies the second and third handoffs (Mavis ↔ Andre, Mavis → post-N).

**The 5-part loop (per `ea-closed-loop-builder`):**
1. **Trigger** — Daily at 18:00 CT (after the Scribe's daily work, before the 19:00 x-analytics-tracker); OR on-demand when a new draft is detected in `drafts/`
2. **Signal + context** — Read the Scribe's batch file, parse the individual posts, check the persona for pillar alignment, check the content_brain for the source idea (the Scribe's backlog-pull)
3. **Action** — Post each draft to Telegram with: verbatim text, 1-2 line rationale, "Reply: approve / deny / edit"
4. **Eval gate** — Andre's reply (text-based, one of: approve / deny / edit + new text). Mavis matches the reply to a draft_id in the state file
5. **Stop condition** — Reply captured → action taken (move / archive / edit) → state updated → next draft proposed → cron ends

## When to run

**Trigger phrases (auto-load on detection):**
- The daily cron fires at 18:00 CT
- Andre replies to a draft proposal with: "approve", "deny", "edit", "ship it", "kill it", or any of: "approved", "yes", "no", "denied", or a draft text that starts with "Draft N:" (indicates an edit)
- Mavis detects a new file in `drafts/` during a normal session

**Do NOT load for:**
- The post-N cron chain (publishes from `approved/`, doesn't propose)
- The Scribe's drafting work (Scribe is its own agent, separate from Mavis)
- The Analytics feedback loop (reads `performance_log` after posts land)
- Drafts already in `approved/` (the bridge ends at `approved/`, not after)
- The X.com compose flow (handled by the post-N cron's `mavis browser tool` procedure)
- Cross-agent territory (this is Mavis's surface; do not propose drafts on behalf of Hermes or OpenClaw)

## Inputs

| Input | Default | Required |
|---|---|---|
| Cron schedule | `0 18 * * *` (daily 18:00 CT) | yes (configured at create time) |
| Scribe queue | `03 Projects/X-Content-Engine/drafts/` | yes |
| Approve queue | `03 Projects/X-Content-Engine/approved/` | yes |
| Deny archive | `03 Projects/X-Content-Engine/archive/denied/` | yes (create if missing) |
| Persona | `03 Projects/X-Content-Engine/agents/persona.md` | yes (read for pillar check) |
| State file | `~/.mavis/agents/mavis/crons/ea-draft-approval.state.json` | yes (auto-managed) |

## The procedure (5 steps, per the closed-loop builder)

### 1. SCAN — find drafts modified since the last run

```bash
# Initialize state on first run
if [ ! -f "$STATE_FILE" ]; then
  cat > "$STATE_FILE" <<'EOF'
{
  "last_scan_at": null,
  "proposals": []
}
EOF
fi

# Find draft files modified in the last 24h (or since last_scan_at)
LAST_SCAN=$(state_get last_scan_at)
DRAFTS_DIR="$VAULT/03 Projects/X-Content-Engine/drafts"
find "$DRAFTS_DIR" -maxdepth 1 -type f -name '*.md' -newermt "$LAST_SCAN" 2>/dev/null
```

For each file, parse the individual posts. The Scribe's batch format is:

```markdown
## Draft 1: <title>
<post text>
<load-bearing specifics callout>

## Draft 2: <title>
<post text>
...

## Draft 3: <title>
<post text>
```

Use `awk` or `python3` to split on `^## Draft ` headers. Each draft is a separate proposal.

### 2. PROPOSE — post each draft to Telegram

For each draft, post a Telegram message with this structure:

```
Draft N: <title>
Pillar: <which of the 6>
Source: <the idea from content_brain backlog>

<Post text — verbatim, no edits>

Reply: approve / deny / edit
```

Keep the post text verbatim. Do NOT add commentary, do NOT shorten, do NOT format. Andre needs to see exactly what the Scribe wrote.

The proposal must be a single Telegram message per draft. If the draft is too long for one message (>4096 chars), split into "Draft N (1/2)" and "Draft N (2/2)" but keep the approve instruction only in the last message.

After posting, record the proposal in the state file:
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

The `draft_id` is the stable identifier Andre's reply will be matched against. The sha256 ensures duplicate proposals don't get sent for the same post.

### 3. CAPTURE — match Andre's reply to a draft_id

When Andre replies (on Telegram or in a Mavis session), classify the reply:

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

### 4. ACT — move / archive / edit

For each closed proposal (response_status != "open"):

- **approved**: preserve the batch file structure; copy the approved post into the Scribe's `approved/` directory, preserving the `## Draft N` header. If the original file had only this draft (single-draft file), move the whole file to `approved/`. If it had multiple drafts, extract just the approved one into a new `approved/` file.

  Concretely:
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

- **denied**: move the source file to `archive/denied/` (preserve the whole batch; do not split)
  ```bash
  mkdir -p archive/denied
  mv drafts/$SOURCE_FILE archive/denied/
  ```

- **edited**: replace the post text in the source file with the edited version, then move the source file to `approved/` (or extract if multi-draft)

  Concretely:
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

### 5. UPDATE — the post-N chain picks up `approved/`

After the action, the file is in `approved/`. The post-N cron chain (post-1-v2-2026-06-16 style, with the silent-failure + chain-validation + duplication-detection patches) will pick it up on the next scheduled run, or on the next post-N trigger.

**The loop is now closed end-to-end:**
Scribe drafts → Mavis proposes → Andre approves → Mavis moves to `approved/` → post-N publishes → Analytics learns → Scribe's next batch uses the analytics.

## Hard constraints

1. **Verbatim post text.** The Telegram proposal shows the post text EXACTLY as the Scribe wrote it. No reformatting, no shortening, no commentary. Andre needs to see what the Scribe wrote, not Mavis's interpretation.
2. **One Telegram message per draft.** If the draft is too long, split into N/N with the approval instruction only in the last message. Do NOT collapse multiple drafts into one message.
3. **Stable draft_id.** The draft_id is `<file>:<draft-N>:<sha256-of-post-text>`. Mavis matches Andre's reply to this ID. If the Scribe rewrites the file between the proposal and the reply, the sha256 changes; treat as a new draft (re-propose, don't act on the stale reply).
4. **The Scribe's Hard Rule #10 binds Mavis too.** Mavis does not auto-approve. Mavis does not auto-publish. Mavis proposes, Andre decides. The bridge is propose → decide → route.
5. **State is append-only.** New proposals append; status changes are updates, not edits. The audit trail is the value.
6. **Multi-draft batch files stay together until approved.** If a batch has 3 drafts and Andre approves 1, the source file remains in `drafts/` until all 3 are decided (approved → extracted to `approved/`, denied → file moves to `archive/denied/`). Splitting a batch mid-decision is not allowed.
7. **Mavis territory only.** Do not propose drafts on behalf of other agents' queues. This skill is for the X-Content-Engine drafts, not for any other agent's pipeline.
8. **Mirror discipline.** The state file is at `~/.mavis/agents/mavis/crons/ea-draft-approval.state.json` (agent home). Mirror to `~/MiniMax-Agent/99 _system/crons/ea-draft-approval.state.json` per `ea-skill-evolution` Hard Constraint #6.
9. **No silent-failure.** If the Telegram post fails (auth, network), HALT and surface. Do not assume the proposal was sent. Same discipline as the post-N chain's silent-failure patch.

## What this skill is NOT

- **Not the Scribe.** Drafting is the Scribe's job. Mavis doesn't write drafts; Mavis proposes them.
- **Not the post-N publish chain.** The post-N cron reads `approved/` and publishes. This skill writes to `approved/`. The two skills are different handoffs in the same loop.
- **Not the Analytics feedback loop.** Analytics reads `performance_log` after posts land and writes the feedback to the Scribe's backlog. This skill is upstream of post-N, not downstream.
- **Not autonomous.** The Scribe's Hard Rule #10 binds. Mavis does not auto-approve. Andre decides.
- **Not a memory write.** State is in the cron state file, not in Mavis's memory. The skill's behavior is fixed; only the data changes per run.

## Anchoring sources

- **EA contract — 4 workflows, 5 behaviors** — `ea-contract.md` — quote verbatim, sharpen to one sentence, end with question (Andre's reply is the "question" that closes the loop)
- **Closed-loop builder — 5-section spec** — `ea-closed-loop-builder` (Mavis skill) — Goal / Context / Action / Feedback / Stop condition
- **Three-hard-stops discipline** — `~/.mavis/agents/mavis/memory/loop-engineering-framework.md` — the cron fleet's discipline
- **Scribe's Hard Rule #10** — `03 Projects/X-Content-Engine/agents/scribe.md` — "Never publish to x.com"
- **Persona load-bearing** — `03 Projects/X-Content-Engine/agents/persona.md` — the 6 pillars + 6 voice examples (used for the rationale line)
- **Matt Van Horn (2026-06-08) on the eval gate** — "the part the hype skips and the practitioners obsess over" — Andre's reply IS the eval gate
- **Hermes-article #13 (Mnilax, 2026-06-07) — inbox-zero drafts** — the original pattern, translated to Mavis's surface
- **Revenue Engineering (ericosiu, 2026-06-15) — 6-question loop audit** — Q4 (eval gate = the human reply), Q5 (kill criteria = the reply), Q6 (compounding = Mavis learns which drafts Andre approves)
- **Mirror-sync.sh gate** — `ea-skill-evolution/scripts/mirror-sync.sh` — for the state file mirror
- **Garry Tan's "if I have to ask you twice, you failed"** — Andre's user memory — the discipline that justifies codifying the bridge as a skill
