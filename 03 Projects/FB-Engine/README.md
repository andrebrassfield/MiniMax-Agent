# FB-Engine (Project Layer)

Facebook content engine. Phase 3 (cron + Telegram approval) shipped —
pipeline fully armed.

## State

| Phase | Status | Owner |
| --- | --- | --- |
| **Phase 1: read path** | shipped (v1.0.0, 2026-06-18) | Mavis |
| `fb-session-guardian` | shipped | Mavis |
| `fb-group-reader` | shipped | Mavis |
| **Phase 2: draft + post** | shipped (v1.1.0, 2026-06-18) | Mavis |
| `ammunition.mdl` ledger | shipped (18 entries, 3 pillars) | Mavis |
| `fb-draft-scribe` | shipped (v1.0.0) | Mavis |
| `ea-fb-draft-approval` | shipped (v1.0.0) | Mavis |
| `fb-poster` | shipped (v1.0.0) | Mavis |
| **Phase 3: cron + Telegram approval** | shipped (v1.2.0, 2026-06-18) | Mavis |
| 5 crons wired | shipped | Mavis |
| Telegram delivery | live (msg_id 78 verified) | Mavis |

## Architecture (same shape as X-Content-Engine)

```
fb-session-guardian (PASS required)
        ↓
fb-group-reader (extract posts to JSON)
        ↓
fb-draft-scribe (generate typology-1 + typology-2 drafts)
        ↓
drafts/                        ← Scribe writes here
        ↓
ea-draft-approval (Mavis → Telegram)
        ↓
Andre replies: approve / deny / edit
        ↓
approved/                      ← Mavis moves approved drafts here
        ↓
fb-poster (publish via real Chrome, Hard Rule #10: human-in-the-loop)
```

## Hard rules

1. **Real Chrome via CDP bridge** — no headless browsers, no
   bot-detection bypass.
2. **Human-in-the-loop on every deploy** — Scribe drafts, operator
   approves, Mavis moves, poster publishes. No autonomous deployment.
3. **No coordinated inauthentic engagement** — no auto-reply loops, no
   multi-Group scrape-and-deploy, no structured deployment to
   "high-engagement posts" without human approval.
4. **Group membership required** — scripts only work on Groups the
   user is already a member of.

## Folder structure

```
03 Projects/FB-Engine/
├── README.md                       ← this file
├── drafts/                         ← Scribe writes drafts here
├── approved/                       ← operator-approved drafts (Poster reads here)
├── archive/
│   └── denied/                     ← denied drafts
├── lists/                          ← target Groups
├── briefs/                         ← research briefs
└── ammunition.mdl                  ← 3-pillar research ledger (18 entries)
```

## Skills (canonical)

- `~/.mavis/agents/mavis/skills/fb-engine/README.md`
- `~/.mavis/agents/mavis/skills/fb-engine/fb-session-guardian/`
- `~/.mavis/agents/mavis/skills/fb-engine/fb-group-reader/`

## Skills (vault mirror)

- `~/MiniMax-Agent/99 _system/skills/fb-engine/`

## Two typologies (defined in the original directive; awaiting Scribe impl)

### Typology 1: The Group Value Bomb (original post)

- **Formula:** [Empathetic Hook about a common pain point] + [Inject
  Metric from `ammunition.mdl`] + [Step-by-step breakdown] + [Question
  to drive comments].
- **Trigger:** Weekly high-effort posts in key groups.
- **Source:** Scribe reading from `ammunition.mdl` + Group context.
- **Approval gate:** Telegram approval before posting (Hard Rule #10).

### Typology 2: The Authority Comment (reply)

- **Formula:** [Acknowledge their premise] + [Inject constraint from
  `ammunition.mdl`] + ["In our experience, the actual bottleneck is
  X..."].
- **Trigger:** High-engagement posts < 4 hours old in target groups.
- **Source:** Scribe reading from `ammunition.mdl` + the original post
  text.
- **Approval gate:** Telegram approval before posting. **No autonomous
  deployment** — the operator sees the original post + the proposed
  reply, replies `approve` / `deny` / `edit`, and the approved reply
  moves to `approved/`.

## Changelog

- 1.0.0 (2026-06-18) — initial project layer. Read path shipped. Draft + post pipeline scaffolded.
- 1.1.0 (2026-06-18) — Phase 2 shipped. `ammunition.mdl` (18 entries, 3 pillars). `fb-draft-scribe` v1.0.0 (template-based, T1+T2). `ea-fb-draft-approval` v1.0.0 (Telegram bridge). `fb-poster` v1.0.0 (CDP poster, HALT gate). Bug fixed: ledger parser marker collision + topic tag filtering.
- 1.2.0 (2026-06-18) — Phase 3 wired. 5 crons scheduled, Telegram delivery live (msg_id 78 verified). Bot token + Andre chat ID configured. Twice-daily cycle: 08:30/09:00/14:00/14:30/20:00 CT.
