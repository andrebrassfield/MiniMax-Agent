---
name: x-bookmark-parser
description: Read the user's X/Twitter bookmarks page and dump structured post metadata to a dated file in 00 Inbox/. Uses mavis browser tool against the user's real Chrome session (not auto-spawned Chromium — preserves X login state, no OAuth hijack surface). Triggers when the user says "read my X bookmarks", "parse my bookmarks", "what's in my x bookmarks", "summarize my x saves", or "x bookmarks". Halt on login prompt, unfamiliar UI, or any unexpected behavior. Zero interaction (no like/repost/follow).
---

# X Bookmark Parser

## What this skill does

Opens `https://x.com/i/bookmarks` in the user's real Chrome session, extracts the post metadata for the currently visible bookmarks, and writes a dated markdown file to `00 Inbox/` with a structured per-post schema. Reports back with the file path, post count, and a one-paragraph theme summary.

## When to run

**Trigger phrases:**
- "read my X bookmarks" / "parse my bookmarks" / "what's in my x bookmarks"
- "summarize my x saves" / "summarize my bookmarks"
- "x bookmarks" (when used as a request, not a reference)

**Do NOT run for:**
- A single X URL (use the `x-link-reader` skill instead — it's a different surface)
- A profile timeline, a single post, a thread (different x-* skills)
- A non-X platform (this skill is x.com-specific)

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Target URL | `https://x.com/i/bookmarks` | no |
| Capture depth | "all visible in first snapshot" | no |
| Destination dir | `00 Inbox/` | no |
| File naming | `x-bookmarks-YYYY-MM-DD-HHMM.md` | no |

The skill does not currently support pagination, folder navigation, or a specific handle/folder. It reads whatever is in the user's "All Bookmarks" view at the time of the snapshot. Pagination is the operator's job (manual scroll in the X tab) — re-run the skill after scrolling to get more.

## Outputs

A single markdown file at `00 Inbox/x-bookmarks-YYYY-MM-DD-HHMM.md` with:

- A header block (timestamp, X handle, capture target, capture source)
- One section per bookmarked post with the Data Schema fields filled in
- A trailing "Themes" section with a one-paragraph synthesis

The skill also returns to the operator with: file path, post count, and the themes paragraph.

## Procedure

### Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected`, **HALT** and tell the operator to load the Chrome extension per `mavis browser install` output (drag `/Users/brassfieldventuresllc/.mavis/browser-extension` into `chrome://extensions`, verify the loaded extension ID matches the one in the install output, remove any old "Mavis Browser Bridge" entry first). Do not proceed with auto-spawned Chromium fallbacks for x.com — the security memory locks the OAuth-hijack surface.

### Step 2: Open or navigate to the bookmarks URL

```bash
mavis browser tool open_tab '{"url":"https://x.com/i/bookmarks"}'
```

Note the returned `tabId`. The tool is documented to auto-claim the tab for the calling session. If the tab exists already, use `mavis browser tool navigate` with the existing `tabId` instead.

### Step 3: Authentication check

Wait 3-5 seconds for the page to load. Then run:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":2}'
```

**Halt conditions (operator-alert only, never type credentials):**
- The snapshot text contains "Sign in to X" / "Log in" / "Sign up" — operator needs to log in manually
- The snapshot shows an error page (e.g., "Something went wrong", "Rate limit exceeded")
- The URL is not `x.com/i/bookmarks` after navigation

**Proceed conditions:**
- The snapshot text contains "All Bookmarks" and a user handle (e.g., `@DreTheSalesGuy`)
- Post metadata visible (handles, timestamps, view counts)

### Step 4: Extract post data

Use the `text` field from the snapshot JSON. Parse the bookmarks feed into the Data Schema below. The text field concatenates all visible text in DOM order, so post boundaries are:

- Each post starts with the author's name + handle + timestamp
- Ends at the next author/timestamp line OR at the right-column "Who to follow" widget

Do NOT scroll via `press_key` — keyboard events go to the focused tab, not the tab ID passed to the tool. See **The Focus Rule** below.

If the operator wants more posts than fit in the first snapshot, they scroll manually in Chrome, then re-run the skill. The skill reads whatever is visible at snapshot time.

### Step 5: Write the capture file

Compose the markdown file at `00 Inbox/x-bookmarks-YYYY-MM-DD-HHMM.md`. Use UTC offset `America/Chicago` for the timestamp. Filename uses local time.

```markdown
# X Bookmarks Capture — 2026-06-16 15:11 CT

**Handle:** @DreTheSalesGuy
**Source:** https://x.com/i/bookmarks
**Captured:** 2026-06-16 15:11:23 CT
**Posts captured:** 4

---

## Post 1 — @bibryam · 21h

- **URL:** https://x.com/bibryam/status/2066652088029852098
- **Type:** Article
- **Title:** Top 10 Agent Skills by GitHub Stars
- **Pull-quote:** "The agent skills market has a clear signal: small, sharp workflows are winning."
- **Full text:** I refreshed the top 10 most-starred agent skills on GitHub: 228,740 stars. Agentic skills framework and dev methodology....
- **Engagement:** 2 replies · 11 reposts · 153 likes · 15K views

---

## Post 2 — @RetroChainer · Jun 15

- **URL:** https://x.com/RetroChainer/status/2066580357277782191
- **Type:** Text
- **Pull-quote:** "Netflix owns the IP on every show in their catalog. A 22-year-old licensed his to 50 creators last month at $97 each."
- **Full text:** ... (full thread)
- **Engagement:** 12 replies · 14 reposts · 293 likes · 607K views
- **Quoted:** @0x_fokki/status/... — "I Built a Lost 90s Sitcom With AI for $47"

---

(... etc)

---

## Themes

AI agents and the agentic-skills market dominate the feed. AI as a content-production and monetization engine is the second thread (sitcom, IP licensing, $47 in / $12K out per month). LLM education and the "how it actually works" stack rounds it out. Hermes (Nous Research public product) release notes are tracked but treated as a third-party ecosystem update, not internal agent territory.
```

### Step 6: Verify the file wrote

```bash
ls -la "00 Inbox/x-bookmarks-YYYY-MM-DD-HHMM.md"
wc -l "00 Inbox/x-bookmarks-YYYY-MM-DD-HHMM.md"
```

Confirm the file exists, has the expected post count, and isn't empty.

### Step 7: Report back

Tell the operator:
- File path
- Post count
- A one-paragraph theme synthesis (the "Themes" section from the file)
- Whether the capture was partial (operator should scroll + re-run for more)

## The Data Schema

For every post, extract these fields. If a field is not visible in the snapshot, mark it as `unclear` rather than skipping.

| Field | Type | Source in snapshot |
|-------|------|-------------------|
| `index` | int | ordinal position in feed (1-based) |
| `author_name` | string | text immediately before `@handle` |
| `handle` | string | `@<username>` |
| `timestamp` | string | relative time string (e.g., "21h", "Jun 15") — keep raw, do not normalize |
| `post_url` | string | first `/status/<id>` link under the post |
| `type` | enum | `Text` / `Article` / `Quote` / `Reply` / `Repost` (infer from "·" + content type indicators) |
| `title` | string? | if Article: the bolded first line |
| `pull_quote` | string? | the first 1-2 sentences if there's a strong hook; do not invent |
| `full_text` | string | everything between author block and engagement metrics |
| `engagement.replies` | int | first number in the engagement row |
| `engagement.reposts` | int | second number |
| `engagement.likes` | int | third number |
| `engagement.views` | int | the "K"-suffixed number (e.g., "15K", "607K") |
| `quoted_post` | object? | if present: a nested schema for the quoted post (handle, full_text, link) |
| `media_attached` | bool | true if `photo/N` links are present in the post block |

Do NOT extract: profile pics, follower counts, the right-column "Who to follow" / trending widgets, the bottom-of-page Terms of Service / Privacy Policy links. Those are platform chrome, not bookmark content.

## The Focus Rule

The mavis browser tool has a documented limitation: **`scroll`, `press_key`, and the click helper route to whichever tab the user's Chrome currently has focused, NOT the `tabId` passed to the tool.** This was hit on the 2026-06-16 15:11 CT run: `press_key PageDown` against the bookmarks tab did nothing because the user's active tab was `chrome://extensions/`. The tab was at the right URL but invisible to keyboard input.

**What works regardless of focus:**
- `navigate` (with `tabId`) — routes correctly
- `snapshot` (with `tabId`) — reads the page regardless of focus
- `query` (with `tabId`, when given a `selector`) — element-level reads

**What requires focus:**
- `scroll` (amount-based) — no-op when tab is in background
- `press_key` (PageDown, End, etc.) — routes to focused tab, not `tabId`
- `click` on a real link — needs focus for the click to be visible to the user

**The skill's posture:** rely on `snapshot` (which is focus-agnostic) for the data extraction. Do not use `press_key` or `scroll` for content reading. If the visible content is incomplete, the operator scrolls manually in Chrome and re-runs the skill.

If a future MCP version of the tool adds focus management, this rule can be relaxed. Until then, document the limitation in any run report that returned fewer posts than the operator expected.

## The Safety Halts

1. **No interaction.** The skill is strictly read-only. Do not like, repost, follow, or reply to any post. If a tool call requires a click on a post action (e.g., expanding a thread), prefer `snapshot` with deeper depth first; if that doesn't reveal the content, halt and ask the operator.

2. **No credential entry.** If the page shows a login prompt, capture the URL + page state in the report and halt. Do not type credentials, do not attempt to fill login forms. The operator handles auth.

3. **Sensitive content.** If a post contains DM screenshots, personal profile data, financial information, or any content the operator hasn't explicitly opted to capture, stop reading immediately and skip that post in the output. Do not include its text or engagement in the file. Note the skip in the report.

4. **Unfamiliar UI.** If the snapshot shows a layout you don't recognize (e.g., "Subscribe to Premium" overlays, X Premium paywall, the bookmarks page is suddenly gated), halt and surface the UI to the operator. Do not improvise.

5. **Rate limiting.** If `mavis browser` returns a rate-limit error, halt and surface. Do not retry aggressively.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Bridge offline | `mavis browser status` shows `not connected` | Halt; tell operator to load Chrome extension |
| Login prompt | snapshot shows Sign in / Log in | Halt; tell operator to log in manually |
| Active tab is wrong | `get_active_tab` returns a non-bookmarks URL | Note the issue; the bookmarks tab can still be snapshotted via `tabId` |
| No posts visible | snapshot text shows "Bookmark posts to save them for later" but no author blocks | Empty bookmarks; write an empty-file placeholder and report |
| Post text truncated | engagement metrics or next-post header in the middle of the content | Include the partial text with `[truncated]` marker; do not invent the rest |
| Quote-tweet nesting | a post quotes another post | Render the quoted post as a nested object in the schema; do not flatten |

## Verification

After writing the file:
1. `ls -la` confirms the file exists with non-zero size
2. `wc -l` shows the expected number of `---` separators + 1 (header) + 1 (themes) = post count + 2
3. `grep -c "^## Post" <file>` matches the post count reported
4. The themes paragraph is present and non-empty

## Cross-reference

- `x-link-reader` skill — for a single X URL, NOT the bookmarks list
- `mavis browser` CLI — the underlying tool surface; this skill is a procedure on top
- `99 _system/memory/tool-quirks.md` — for tool-specific gotchas if a future run hits an unexpected tool error
- CHIEF pattern: `00 Inbox/` is the staging lane; the operator processes captures into `02 Notes/articles/` (for keepers) or trashes
