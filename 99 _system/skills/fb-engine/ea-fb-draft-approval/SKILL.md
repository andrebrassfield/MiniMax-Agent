---
name: ea-fb-draft-approval
description: |
  Telegram bridge for FB-Engine draft approval. Cron-driven Python
  script that scans `03 Projects/FB-Engine/drafts/` for files with
  `status: open`, posts each draft to Telegram via the Bot API, captures
  Andre's reply (approve / deny / edit <text>), updates the state file,
  and moves approved drafts to `approved/` (or `archive/denied/` for
  denied, or applies the edit and moves to `approved/`). The bridge
  does NOT publish — it routes operator decisions. The Poster
  (`fb-poster`) consumes `approved/`. Mirrors the X-CE
  `ea-draft-approval` pattern, scoped to FB-Engine. Do NOT use for:
  publishing to Facebook (that's the Poster), drafting (that's the
  Scribe), reading posts (that's `fb-group-reader`), or non-FB
  pipelines.
---

# ea-fb-draft-approval

The Mavis-side Telegram bridge for FB-Engine draft approval. Sits
between the Scribe (writer) and the Poster (publisher). The Scribe
writes to `drafts/`, this bridge routes operator decisions, the
Poster consumes `approved/`.

## When to invoke

**Auto-invoke (cron):**
- Every 15 minutes during business hours (default: 09:00-21:00 CT)
- This is a tight loop because Typology 2 replies have a 4-hour
  engagement window — drafts need to surface to Andre quickly

**Triggers (manual):**
- "propose the FB drafts"
- "check FB approvals"
- "ea-fb-draft-approval cycle"
- "run the FB bridge"

**Do NOT use for:**
- Publishing to Facebook (the Poster does that, from `approved/`)
- Drafting (the Scribe does that, into `drafts/`)
- Reading posts (the read path is `fb-group-reader`)
- Other agents' pipelines (Hermes / OpenClaw have their own bridges)

## The mechanism (the discipline)

Each cron cycle runs two phases:

### Phase 1: PROPOSE — push open drafts to Telegram

1. Scan `03 Projects/FB-Engine/drafts/` for `.md` files with
   `status: open` in the YAML frontmatter
2. For each, parse the frontmatter to extract `draft_id`, `typology`,
   `original_author`, `ammunition_used`
3. Extract the body under `## Generated draft`
4. Send a Telegram message:
   ```
   [FB-Engine] Draft: <draft_id>
   Typology: T<1|2>
   Source: <author or "operator hook">
   Ammunition: <ammo summary>

   <post body verbatim>

   Reply: approve / deny / edit <text>
   ```
5. Record the proposal in the state file with the Telegram `message_id`
6. The state file prevents double-sending (stable `draft_id`)

### Phase 2: CAPTURE — match Andre's reply to a draft

1. Call Telegram `getUpdates` with `offset = last_update_id + 1`
2. For each update, classify the text:
   - `approve / approved / ship it / yes / go / +1` → approve
   - `deny / denied / kill it / no / -1 / skip` → deny
   - `edit <text>` → apply edit, move to `approved/`
   - Anything else → ignore (or ask for clarification)
3. Match the reply to an open proposal:
   - If the reply contains a `draft_id` substring, match that
   - Otherwise, match the most recent open proposal
4. Take action:
   - `approve` → move to `approved/`, update frontmatter `status: approved`
   - `deny` → move to `archive/denied/`, update `status: denied`
   - `edit <text>` → apply the edit, move to `approved/`
5. Update the state file: `response_status`, `response_text`,
   `responded_at`, `acted_at`, `action`
6. Save state to canonical + mirror (atomic write)

## The state file

Path: `~/.mavis/agents/mavis/crons/ea-fb-draft-approval.state.json`
Mirror: `~/MiniMax-Agent/99 _system/crons/ea-fb-draft-approval.state.json`

Schema:
```json
{
  "last_scan_at": "2026-06-18T13:30:00+00:00",
  "last_update_id": 1234567,
  "proposals": [
    {
      "draft_id": "fb-2-post-1234567890-a1b2c3d4e5",
      "source_file": "03 Projects/FB-Engine/drafts/2026-06-18-1330-t2-post-1234567890.md",
      "draft_path": "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/FB-Engine/drafts/2026-06-18-1330-t2-post-1234567890.md",
      "typology": "T2",
      "telegram_message_id": 9876,
      "proposed_at": "2026-06-18T13:30:00+00:00",
      "response_status": "approved",
      "response_text": "approve",
      "responded_at": "2026-06-18T13:35:00+00:00",
      "acted_at": "2026-06-18T13:35:01+00:00",
      "action": "moved_to_approved"
    }
  ]
}
```

The state is append-only on `proposals[]`; existing proposal entries
are updated in place when status changes. The audit trail is the value.

## Environment

```bash
export FB_TELEGRAM_BOT_TOKEN="<token from @BotFather>"
export FB_TELEGRAM_CHAT_ID="<Andre's chat ID with the bot>"
```

The bot token and chat_id are stored in `~/.mavis/secrets/telegram.env`
(mode 600) per the Obsidian-MCP wiring pattern in
`~/.mavis/agents/mavis/memory/tooling-gotchas.md`. Set them once; the
script reads from env on each run.

## CLI

```bash
# One cycle: propose new drafts + capture recent replies (default cron mode)
python3 ~/.mavis/agents/mavis/skills/fb-engine/ea-fb-draft-approval/scripts/bridge.py

# Propose only
python3 .../bridge.py --propose-only

# Capture only
python3 .../bridge.py --capture-only

# Local-test: print actions without sending / moving
python3 .../bridge.py --dry-run
```

## Hard constraints

- **The bridge NEVER publishes.** It only routes drafts between
  `drafts/`, `approved/`, and `archive/denied/`. The Poster publishes
  from `approved/`.
- **Marker filter.** All Telegram messages have a `[FB-Engine]`
  prefix. The bridge only processes incoming replies that don't have
  the prefix (outgoing) and that contain `fb-N-` (a draft_id) OR that
  were sent as a direct reply to one of our proposals. This prevents
  the bridge from acting on unrelated Telegram messages.
- **One Telegram message per draft.** The proposal is a single message
  with the full body. If the body exceeds Telegram's 4096-char limit,
  it's truncated with a "see draft file" marker.
- **Stable draft_id.** The `draft_id` is
  `<typology>-<source_key>-<sha256[:10]>`. The bridge matches
  Andre's reply to this ID. If the Scribe rewrites the draft between
  the proposal and the reply, the sha256 changes; the bridge treats
  it as a new draft (re-propose, don't act on the stale reply).
- **Append-only state.** New proposals append; status changes are
  updates, not edits. The audit trail is the value.
- **No silent failure.** If `sendMessage` fails (auth, network), HALT
  with stderr. Don't assume the proposal was sent.
- **Mirror discipline.** State file is at
  `~/.mavis/agents/mavis/crons/ea-fb-draft-approval.state.json`
  (agent home canonical). Mirrored to
  `~/MiniMax-Agent/99 _system/crons/`. If the mirror write fails,
  the script HALT with a clear error.

## HALT conditions

- `FB_TELEGRAM_BOT_TOKEN` or `FB_TELEGRAM_CHAT_ID` not set → HALT
- `sendMessage` returns non-OK → HALT (don't assume sent)
- `getUpdates` returns non-OK → HALT (don't assume no replies)
- Source draft file missing during `act_on_decision` → log + skip
  (don't fail the whole cycle)
- Reply is `unknown` (not approve/deny/edit) → log + skip (don't
  silently reject)
- State file write fails → HALT (atomic write + fsync ensures this
  is rare; if it does fail, surface to stderr)

## Cron schedule (recommended)

```cron
# Every 15 min during business hours (9am-9pm CT)
*/15 9-20 * * 1-6  cd ~ && FB_TELEGRAM_BOT_TOKEN=... FB_TELEGRAM_CHAT_ID=... \
    python3 ~/.mavis/agents/mavis/skills/fb-engine/ea-fb-draft-approval/scripts/bridge.py \
    >> ~/.mavis/logs/ea-fb-draft-approval.log 2>&1
```

The 15-minute cadence is tight enough for the 4-hour Typology 2
engagement window (any draft surfaces within 15 min of being written,
Andre approves within minutes, the Poster fires within minutes after
that — total surface-to-post: <30 min, well inside the 4-hour window).

## Integration with other skills

```
fb-group-reader (read path)
        ↓ JSON
fb-draft-scribe (drafts → drafts/)
        ↓ markdown
ea-fb-draft-approval (THIS skill, drafts/ ↔ approved/)
        ↓ operator-approved markdown
fb-poster (approved/ → Facebook)
        ↓ published URL
archive/published/  ← audit trail
```

## Cross-references

- `fb-draft-scribe` — writes drafts this skill consumes
- `fb-poster` — consumes the `approved/` directory this skill writes to
- `ea-draft-approval` (X-CE) — the parallel skill for the X-Content-Engine
  (different state file, different paths — do NOT cross-consume)
- `x-publish` — the X-CE publisher (same `approved/`-driven pattern,
  different platform)
- `03 Projects/FB-Engine/ammunition.mdl` — the ammunition ledger
  (referenced in the proposal message)

## Source

- `~/.mavis/agents/mavis/skills/fb-engine/ea-fb-draft-approval/scripts/bridge.py`
- Mirror: `~/MiniMax-Agent/99 _system/skills/fb-engine/ea-fb-draft-approval/scripts/bridge.py`

## Changelog

- 1.0.0 (2026-06-18) — initial skill. Two-phase cycle (propose + capture).
  Direct Telegram Bot API via `requests`. State file at
  `~/.mavis/agents/mavis/crons/ea-fb-draft-approval.state.json` with
  mirror. Stable `draft_id` matching. Marker filter (`[FB-Engine]`) to
  prevent cross-bridge interference. Reply classifier (approve / deny /
  edit). Atomic state writes (temp + fsync + replace). CLI flags:
  --propose-only, --capture-only, --dry-run. HALT on auth/network
  failures; skip-on-missing-source-draft.
