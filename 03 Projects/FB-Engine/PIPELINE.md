# FB-Engine Pipeline Runbook

## Overview

The FB-Engine pipeline has three phases. Phase 1 (read path) and Phase 2
(draft + post) are shipped. Phase 3 (cron + Telegram approval) is pending.

```
fb-session-guardian (auth pre-flight)
        ↓
fb-group-reader (extract posts to JSON)
        ↓
fb-draft-scribe (generate T1 Value Bombs + T2 Authority Comments)
        ↓
 drafts/                        ← Scribe writes here
        ↓
ea-fb-draft-approval            ← Mavis scans drafts, proposes via Telegram
        ↓
Andre replies: approve / deny / edit
        ↓
approved/                       ← Mavis moves approved drafts here
        ↓
fb-poster (publish via real Chrome — HALT gate on approved/ only)
```

---

## Phase 1: Read Path (shipped)

### 1. Launch Chrome with CDP bridge

```bash
# Already running? Check first:
ps -axww | grep remote-debugging-port

# If not, launch:
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=58632
```

### 2. Auth pre-flight

```bash
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-session-guardian/scripts/guard.py
# Expected: PASS (port NNNNN) — exit 0
```

If FAIL: log in to Facebook in your real Chrome, re-run.

### 3. Extract posts from a group

```bash
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-group-reader/scripts/read.py \
  --group "https://www.facebook.com/groups/<your-group-slug>" \
  --output /tmp/fb-posts.json
# Expected: captured=N posts=N errors=0 → /tmp/fb-posts.json
```

---

## Phase 2: Draft + Post (shipped)

### 4. Generate drafts (T2 Authority Comments from group posts)

```bash
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-draft-scribe/scripts/scribe.py \
  --from-reader /tmp/fb-posts.json \
  --output-dir "03 Projects/FB-Engine/drafts/"
# Writes: drafts/fb-YYYY-MM-DD-*.md
```

### 4b. Generate a T1 Value Bomb (original post, operator hook required)

```bash
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-draft-scribe/scripts/scribe.py \
  --typology 1 \
  --hook "Most HVAC owners I talk to are losing \$400/day to missed calls" \
  --pillar 1 \
  --output-dir "03 Projects/FB-Engine/drafts/"
```

### 5. Review drafts manually

```bash
ls "03 Projects/FB-Engine/drafts/"
cat "03 Projects/FB-Engine/drafts/fb-YYYY-MM-DD-*.md"
```

Edit drafts as needed before approving.

### 6. Approve via Telegram

```bash
# Phase 3 cron handles this automatically. Manual trigger:
python3 ~/.mavis/agents/mavis/skills/fb-engine/ea-fb-draft-approval/scripts/bridge.py \
  --propose
# Posts drafts to Telegram one by one
```

Andre replies: `approve` / `deny` / `edit <new text>`

### 7. Capture Andre's reply (Phase 3)

```bash
# Phase 3 cron polls Telegram for replies. Manual trigger:
python3 ~/.mavis/agents/mavis/skills/fb-engine/ea-fb-draft-approval/scripts/bridge.py \
  --capture
# Reads last N Telegram messages, matches to draft_ids, updates state
# Moves approved → approved/
# Moves denied → archive/denied/
```

### 8. Publish approved drafts (HALT gate)

```bash
# Default: HALT before clicking Post (safety gate on approved/ only)
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-poster/scripts/poster.py \
  --draft "03 Projects/FB-Engine/approved/fb-YYYY-MM-DD-*.md"

# Fully automated (operator approved via Telegram, wants cron mode):
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-poster/scripts/poster.py \
  --draft "03 Projects/FB-Engine/approved/fb-YYYY-MM-DD-*.md" \
  --no-halt
```

**Safety gate:** Poster refuses to post from `drafts/` — only `approved/`.
This means even if the cron fires on the wrong directory, nothing publishes
without explicit human approval.

---

## Cron Schedule (Phase 3 — pending)

| Cron | Time | Job |
| --- | --- | --- |
| `fb-draft-proposer` | daily 09:00 CT | `bridge.py --propose` — scan drafts/, post to Telegram |
| `fb-reply-catcher` | daily 19:00 CT | `bridge.py --capture` — read replies, move to approved/ |
| `fb-draft-scribe` | daily 08:30 CT | `scribe.py --from-reader /tmp/fb-posts.json` |

---

## Directory Reference

```
03 Projects/FB-Engine/
├── drafts/             ← Scribe writes here. NOT consumed by poster.
├── approved/          ← Operator-approved. ONLY source for poster.
├── archive/
│   └── denied/        ← Denied drafts. Never published.
├── lists/             ← Target Facebook Groups (one URL per line)
├── briefs/            ← Research briefs from fb-researcher (Phase 3)
└── ammunition.mdl     ← 3-pillar research ledger (18 entries, 3 pillars)
```

---

## Troubleshooting

### Guard returns FAIL

Log in to Facebook in your Chrome, re-run `guard.py`.

### Group reader captures 0 posts

1. Confirm you're a member of the Group.
2. Open the Group URL in your Chrome manually — confirm posts are visible.
3. Check `ps -axww | grep remote-debugging-port` — port must match.
4. Try a smaller Group (fewer posts = faster initial load).

### Scribe generates no drafts

The `--from-reader` path requires posts with non-empty `text` fields.
If the group reader captured 0 posts, the scribe has nothing to draft.

### Poster HALT fires unexpectedly

The `--halt` gate checks `status` in the draft frontmatter.
Only drafts in `approved/` with `status: approved` proceed.
If the draft is in `drafts/` (not `approved/`), Poster halts with:
`HALT: draft is not in approved/ — human approval required.`

### Telegram bridge not sending

1. Check `FB_TELEGRAM_BOT_TOKEN` + `FB_TELEGRAM_CHAT_ID` are set:
   `cat ~/.mavis/secrets/telegram.env`
2. Confirm the bot has been started (/start) in the chat.
3. Run with `--verbose` to see API call details.

---

## Hard Rules (never bypass)

1. **Real Chrome only** — no headless, no UA spoofing, no timing randomization.
2. **Human-in-the-loop** — Poster HALT gate is on by default. `--no-halt`
   is available for cron mode but requires Telegram approval first.
3. **No auto-reply loops** — T2 Authority Comments are one-at-a-time,
   one post at a time, human-approved.
4. **Group membership required** — scripts only read Groups you're in.
5. **Only `approved/` is publishable** — `drafts/` is never touched by poster.

---

## Version History

| Version | Date | Notes |
| --- | --- | --- |
| 1.0.0 | 2026-06-18 | Phase 1: guardian + group-reader shipped |
| 1.1.0 | 2026-06-18 | Phase 2: scribe + approval bridge + poster shipped |
