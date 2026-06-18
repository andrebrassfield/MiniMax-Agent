# Procedure — x-value-bomb-dropper

The 7-step procedure with bash commands. The SKILL.md only
carries the procedure overview. The actual commands live
here (the deterministic layer).

---

## Step 1: Verify bridge is live

```bash
mavis browser status
```

If `Native host: not connected` → HALT (H1). Do not fall
back to auto-spawned Chromium for x.com.

## Step 2: Open the search URL

```bash
mavis browser tool open_tab '{"url":"https://x.com/search?q=<URL-encoded query>&f=live"}'
```

Default `f=live` (Latest) — operational Q posts are
time-sensitive. Use `f=top` for established conversations.

Note the returned `tabId`.

## Step 3: Auth + load wait + result check

Wait 3-5s, then `snapshot` (interactive=false, depth=3).
Halt conditions (H2/H3/H4):
- "Sign in to X" / "Log in" / "Sign up"
- Rate-limit warning
- URL not on `x.com/search`
- Zero results

**Filter heuristic:** mentally check that results contain
actual operational Q posts — tweets ending in "?" or
starting with "how do I" / "anyone using" / "best way to" /
"recommend a tool for." Skip rhetorical "what do you think
about AI" posts and AI influencer threads.

## Step 4: Extract + rank source posts

Parse the snapshot. For each post extract: author handle,
full post text, timestamp, engagement, source URL, the
specific operational Q being asked (1-sentence paraphrase).

**Pick the strongest target** — one post only. Ranking:
1. Question specific enough for 3-step answer? (skip "what's
   the best AI tool")
2. Author a real SMB owner / operator / knowledge worker?
   (skip AI influencers, founders pitching, anonymous)
3. Engagement floor met (5+ likes, or 0 for new post)
4. Recency (prefer last 24h)

If no post meets all four → HALT and report "no operational
question matching the query — try a different angle."

Do NOT scroll via `press_key` (Focus Rule — same as sibling
skills).

## Step 5: Dispatch Scribe

One spawn per target (not batched). The task spec is the
verbatim block in `references/scribe-task-spec.md` with
placeholders filled in. Spawn protocol per `team-config.md`:

```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{"agent":"x-scribe","model":"MiniMax-M2.7","prompt":"<task spec>"}'
```

The chief should spawn the Scribe **once per source post**
(not in batch). Single-target by design — the value-bomb
format loses its punch in batch.

## Step 6: Update value-bombs ledger

Append one line to
`03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — value-bomb to @<handle> (source: <source-url>, Scribe draft, pending)
```

## Step 7: Return summary

Send a one-paragraph summary to the operator:
- File path
- Number of value-bombs drafted (1 by default; single-target
  by design)
- The strongest reply candidate (one line)
- Any concerns (e.g., "the Scribe flagged 2 of the 5
  candidate posts as too vague to answer with a 3-step —
  those were skipped; one strong target was identified and
  drafted")
