# fb-engine

Facebook content engine. Mirrors the X-Content-Engine architecture:
CDP-to-real-Chrome + human approval. The Scribe drafts, the operator
approves via Telegram, Mavis moves approved drafts to `approved/`. **No
autonomous deployment, no bot-detection bypass, no coordinated
inauthentic engagement.**

## Status: Phase 3 (cron + Telegram) shipped. Pipeline fully armed.

| Skill | Status | Role |
| --- | --- | --- |
| `fb-session-guardian` | **shipped (v1.0.0)** | Auth pre-flight |
| `fb-group-reader` | **shipped (v1.0.0)** | Read-only GraphQL feed extractor |
| `fb-draft-scribe` | **shipped (v1.0.0)** | Template-based typology-1 + typology-2 drafts |
| `ea-fb-draft-approval` | **shipped (v1.0.0)** | Telegram approval bridge (two-phase propose + capture) |
| `fb-poster` | **shipped (v1.0.0)** | CDP poster, HALT gate on `approved/` only |
| `ammunition.mdl` ledger | **shipped (v1.0.0, 18 entries)** | 3-pillar research ledger for typology 2 |
| Phase 3 crons | **shipped (v1.2.0)** | Twice-daily read/draft + Telegram approve/capture cycle |

## Hard architecture rules (read these first)

1. **Real Chrome via CDP bridge.** Every skill in this folder connects to
   the user's existing Chrome session via the Playwright MCP's CDP
   bridge. No headless browsers, no bot-detection bypass. The user's
   real browser is the substrate.
2. **Human-in-the-loop on every deploy.** Scribe drafts → operator
   approves via Telegram → Mavis moves drafts to `approved/` → the
   poster (if enabled) publishes from `approved/`. No autonomous
   deployment to live conversations. Same Hard Rule #10 as the Scribe.
3. **No coordinated inauthentic engagement.** No auto-reply loops, no
   multi-Group scrape-and-deploy, no structured deployment to
   "high-engagement posts" without human approval. The CFAA / TOS line
   is real: bot-detection bypass is "exceeding authorized access" per
   `hiQ v. LinkedIn` and `Facebook v. Power Ventures`.
4. **Group membership is a hard requirement.** The scripts only work on
   Groups the user is already a member of. They do not bypass join
   restrictions, and they do not scrape posts the user cannot already
   see in their own browser.

## Folder structure

```
~/.mavis/agents/mavis/skills/fb-engine/          ← canonical (loaded by mavis)
├── README.md                                     ← this file
├── fb-session-guardian/
│   ├── SKILL.md
│   └── scripts/guard.py
├── fb-group-reader/
│   ├── SKILL.md
│   └── scripts/read.py
├── fb-draft-scribe/
│   ├── SKILL.md
│   └── scripts/scribe.py
├── ea-fb-draft-approval/
│   ├── SKILL.md
│   └── scripts/bridge.py
└── fb-poster/
    ├── SKILL.md
    └── scripts/poster.py

~/MiniMax-Agent/99 _system/skills/fb-engine/      ← vault mirror
~/MiniMax-Agent/03 Projects/FB-Engine/            ← project layer
    ├── drafts/
    ├── approved/
    ├── archive/denied/
    ├── lists/
    ├── briefs/
    └── ammunition.mdl
```

## Quick start (Phase 1 — read path)

### 1. Launch Chrome with the CDP bridge enabled

**This is required for crons to work.** The scripts auto-detect the
CDP port, but your real Chrome must be running with the flag set.

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=58632
```

You'll see a macOS Keychain prompt — authenticate, then Chrome restarts
with CDP enabled. The Playwright MCP browser (port 57931) does NOT have
your Facebook session; only your real Chrome does. Use port 58632.

Check it's running: `ps -axww | grep remote-debugging-port` — you should
see your Chrome on 58632.

### 2. Log in to Facebook in that Chrome

Manually. The scripts do not authenticate; they read the cookies you
already have in your browser.

### 3. Run the session guardian

```bash
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-session-guardian/scripts/guard.py
```

Expect: `PASS (port NNNNN)` on stderr, JSON with `session_state:
"PASS"` on stdout. Exit code 0.

If FAIL: log in to Facebook in your real Chrome, re-run the guardian.

### 4. Run the group reader

```bash
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-group-reader/scripts/read.py \
  --group "https://www.facebook.com/groups/<your-group-slug>" \
  --output /tmp/fb-posts.json
```

Expect: `captured=N posts=N errors=0 → /tmp/fb-posts.json` on stderr,
JSON with `results[]` on stdout.

### 5. Inspect the output

```bash
cat /tmp/fb-posts.json | jq '.results[0:3]'
```

Each post has: `post_id`, `author`, `text`, `timestamp`, `fetched_at`,
`source_query`.

## Local-test debugging (the question you actually asked)

> Provide instructions on how I can test the FB interceptor locally
> against a public Facebook Group to verify we are successfully
> catching the `/api/graphql/` payload.

The end-to-end local-test procedure:

1. **Confirm Chrome is on the CDP port.** Run `ps -axww | grep
   remote-debugging-port`. You should see a `Google Chrome ... --
   remote-debugging-port=NNNNN` line. Note the port (default 58632).
2. **Confirm you're logged in to Facebook.** Open `facebook.com` in
   that Chrome. You should see your News Feed, not a login wall.
3. **Run `fb-session-guardian`.** It should output `PASS`. If it
   outputs `FAIL` with `LOGIN_REQUIRED`, log in to Facebook and
   re-run.
4. **Pick a Group URL.** Start with a Group you're a member of that
   has visible posts in the feed. Public Groups (e.g., `fb.com/groups/
   ycombinator`) work for a smoke test if you're a member.
5. **Run `fb-group-reader`.** The script navigates to the Group,
   registers the response listener before navigation, captures every
   `/api/graphql/` response, parses them, and writes JSON.
6. **Verify the captured responses.** Open the output file:
   ```bash
   jq '{captured: .graphql_responses_captured, post_count: (.results | length), first_post: .results[0]}' /tmp/fb-posts.json
   ```
   You should see `graphql_responses_captured >= 1` and `post_count >=
   1`. If `captured: 0`, the script didn't catch any GraphQL calls —
   the listener was registered too late, or the page didn't fire any
   GraphQL (e.g., the user isn't a member).
7. **Cross-check in DevTools.** Open Chrome DevTools (F12) → Network
   tab → filter by `graphql` → scroll the Group manually. You should
   see the same query names the script captured (`source_query` field
   in the JSON). This is the manual verification that the script is
   catching the same payloads you'd see if you did it by hand.
8. **End-to-end smoke test passes when:**
   - `fb-session-guardian` returns `PASS`
   - `fb-group-reader` captures > 0 GraphQL responses
   - The extracted posts match what you see in the Group feed by eye
   - The DevTools cross-check shows the same query names

## Why no bot-detection bypass

Facebook's TOS explicitly prohibits automated access bypassing
technical measures. The post-`hiQ v. LinkedIn` and `Facebook v.
Power Ventures` line of cases treats bot-detection bypass as
"exceeding authorized access" under CFAA. Realistic downside: civil
treble damages + permanent ban.

CDP-to-real-Chrome is fine because you're driving your own browser,
not circumventing anything. The instant we add interception logic
designed to evade bot checks (rotating user agents, request timing
randomization, fingerprint spoofing, etc.), we cross the line.

## Why no autonomous deployment

The X-Content-Engine works because of the human-approval gate. The
Scribe drafts, you approve via Telegram, Mavis moves the draft to
`approved/`, the post-N cron publishes. Hard Rule #10: Scribe never
publishes.

The same shape applies to FB:
- `fb-draft-scribe` (next) writes to `03 Projects/FB-Engine/drafts/`
- Mavis surfaces drafts via Telegram using the `ea-draft-approval`
  pattern
- Operator replies `approve` / `deny` / `edit <text>`
- Approved drafts move to `approved/`
- `fb-poster` (next, gated on `approved/`) publishes via real Chrome

No auto-reply loops. No "Typology 2 deployed to high-engagement posts
< 4h old." The leverage is the same as X: Scribe + human approval.

## Source-of-truth mirrors

- Canonical: `~/.mavis/agents/mavis/skills/fb-engine/`
- Vault mirror: `~/MiniMax-Agent/99 _system/skills/fb-engine/`
- Project layer: `~/MiniMax-Agent/03 Projects/FB-Engine/`

## Changelog

- 1.0.0 (2026-06-18) — initial folder. `fb-session-guardian` + `fb-group-reader` shipped. Project layer scaffolded.
- 1.1.0 (2026-06-18) — Phase 2 shipped. `ammunition.mdl` (18 entries, 3 pillars). `fb-draft-scribe` v1.0.0 (template-based, T1+T2). `ea-fb-draft-approval` v1.0.0 (Telegram bridge, state file, two-phase). `fb-poster` v1.0.0 (CDP poster, HALT gate, safety gate on `approved/` only). Bug fixed: ammunition ledger parser marker collision + topic tag filtering.
- 1.2.0 (2026-06-18) — Phase 3 wired. 5 crons scheduled (twice-daily read/draft + Telegram approve/capture at 08:30/09:00/14:00/14:30/20:00 CT). Telegram delivery enabled. Bot token + chat ID configured. Test message sent successfully (msg_id 78).
