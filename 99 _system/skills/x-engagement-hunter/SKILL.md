---
name: x-engagement-hunter
description: |
  Open a target X account or post URL, extract the most recent post, dispatch
  the Content Scribe to draft a value-add reply in @DreTheSalesGuy voice, save
  to `03 Projects/X-Content-Engine/drafts/replies-YYYY-MM-DD.md` for manual
  review. **Hard constraint: NEVER click the reply button. Read-only extraction.**
  Operator copy/pastes and publishes manually. Triggers: "reply to @handle",
  "engage with @handle's latest post", "engagement hunt on @handle", "draft
  a reply to X". Single-target by design. Do NOT use for the user's own posts,
  mass-reply workflows, or non-X platforms.
---

# x-engagement-hunter

The single-target reply engine for Pillar 6 audience growth. Read a
target X post → dispatch Scribe for a value-add reply in Dre voice →
operator publishes manually. Read-only against x.com; writes only
to the vault.

## When to run

**Triggers:**
- "reply to @handle" / "draft a reply to @handle's latest post"
- "engage with @handle" / "engagement hunt on @handle"
- "what should I reply to @handle with"
- "build a reply to this X post: <url>"

**Do NOT run for:**
- The user's own posts
- Existing drafts (use them)
- Mass-reply workflows (run once per target)
- Non-X platforms
- The user's own posts / bookmarks (use x-bookmark-parser)
- Top-N market searches (use x-niche-scraper)

## Inputs

| Input | Default | Required |
|---|---|---|
| Target handle or URL | — | **yes** |
| Capture source | most recent post on profile | no — specific post URL |
| Reply angle hint | (none — Scribe picks from persona) | no — operator can hint "agree + tactical extension" |
| Destination | `03 Projects/X-Content-Engine/drafts/` | no |
| File naming | `replies-YYYY-MM-DD.md` (rolling per day) | no |

**URL normalization (in `references/url-normalization.md`):**
- `@NickHuber` → `https://x.com/NickHuber`
- `https://twitter.com/<handle>` → `https://x.com/<handle>`
- `https://x.com/<handle>/status/<id>` → leave as-is

## Procedure

### 1. Verify bridge is live
```bash
mavis browser status
```
If `Native host: not connected` → HALT (H1). Do not fall back to
auto-spawned Chromium for x.com.

### 2. Open target URL
```bash
mavis browser tool open_tab '{"url":"<normalized-url>"}'
```
Note the returned `tabId`.

### 3. Auth check + load wait
Wait 3-5s, then `snapshot` (interactive=false, depth=2). Halt
conditions (H2/H3/H4):
- "Sign in to X" / "Log in" / "Sign up" present
- Rate-limit warning
- URL not on `x.com/<handle>[/status/...]` after navigation

Proceed when profile or post page renders.

### 4. Extract source post
- Profile page → topmost post (most recent)
- Post page → post in main content area

Extract: author handle, full post text, timestamp, source URL.
Engagement metrics optional (operator reference only). Do NOT
scroll via `press_key` (Focus Rule — same as x-bookmark-parser).

If topmost is "Pinned" instead of "Latest" → note in output.
Operator decides whether to draft against pinned or scroll.

### 5. Dispatch Scribe
Send per `team-config.md` dispatch protocol:
```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{"agent":"x-scribe","model":"MiniMax-M2.7","prompt":"<task spec>"}'
```

The task spec is the verbatim block in
`references/scribe-task-spec.md` with placeholders filled in.
**One Scribe spawn per target** (not batched) — keeps each
task spec tight.

### 6. Update replies ledger
Append one line to `03 Projects/X-Content-Engine/drafts/_ledger.mdl`:
```markdown
- YYYY-MM-DD HH:MM CT — reply to @<handle> (source: <source-url>, Scribe draft, pending)
```

### 7. Return summary to operator
File path, target handled, one-line note on strongest reply
candidate (if multiple), halt if dispatch failed.

## The hard constraint (READ THIS)

**DO NOT click the reply button on x.com. EVER.** Read-only against
the X UI. Drafts go to a file. Operator copy/pastes the draft
manually after approval.

If a tool call would click a reply button, type into a reply
textarea, or submit a reply → HALT and surface. The skill is
"draft a reply" — it is NOT "post a reply."

X's UI has reply buttons, quote-reply buttons, and the post
detail page has a reply textarea. ALL of these are forbidden.

## Output format

The Scribe appends a reply section to the file. Schema (the
load-bearing shape) in `references/output-format.md`. Per-reply
section contains:
- Header with target handle + source post URL + quoted excerpt
- Reply draft (raw, copy-pasteable)
- Character count
- "Why this reply" rationale linking to persona pillar
- "Notes for Andre" specifics to verify
- Unchecked approval box

The Scribe's system prompt enforces the schema; chief does NOT
repeat it in the task spec.

## Hard rules

1. **Never argue.** If the target's premise is correct, agree. If debatable, don't pick the fight. Add a technical/agentic insight that extends or operationalizes their point.
2. **Add value, don't restate.** Bring a number, a tactical implication, a vendor/tool name, a Pillar 2 (Trades) or Pillar 4 (Build Logs) connection.
3. **Match Andre's voice per persona.md.** Staccato periods, lead with a punch, follow with unit economics. No AI fluff. No "great point" / "I love this" / "well said" openers.
4. **Hard char limit: 280.** Replies 80-260 chars typical.
5. **No emoji, no hashtags, no "follow for more" CTAs.**
6. **Frame for the target's audience, not just the target.** Third-party reader benefits too.
7. **No "I will" / "we will" / "let's" openers.** Peer voice, not coach voice.
8. **Banned phrases re-grep** (per Scribe's persona spec) — Scribe's own discipline.
9. **Mavis territory only.** This skill dispatches the Scribe — both are Mavis-side. No cross-team handoff.

## Cross-reference

- `references/scribe-task-spec.md` — the load-bearing contract to the Scribe
- `references/url-normalization.md` — handle/URL canonicalization rules
- `references/output-format.md` — the reply section markdown schema
- `tests/safety-halts.md` — 8 halt conditions + eval cases
- `tests/scribe-discipline.md` — 6 quality checks (never-argue, value-add, char, banned, peer voice, source targeted)
- `x-bookmark-parser` — for the user's own bookmarks
- `x-niche-scraper` — for top-N market searches
- `x-link-reader` — for reading a single X URL without writing to vault
- `x-empowerment-hunter` — for the parallel Pillar 5 reply (anxiety-targeted)
- `x-hype-translator` — for outbound AI-tool posts (Pillar 5/6 broadcast)
- The Content Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`)
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`) — voice source
- `team-config.md` — dispatch protocol
