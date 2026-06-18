---
name: x-niche-scraper
description: Search X for a parameterized query (e.g., "Shopify inventory", "HVAC business", "AI automation"), extract the top 10 high-engagement posts, and dump them to 00 Inbox/ using the same data schema as x-bookmark-parser. Uses mavis browser tool against the user's real Chrome session. Triggers when the user says "search x for X", "find posts about X", "niche scrape X", or specifies a topic to scout. Halt on login prompt, unfamiliar UI, or unexpected behavior. Zero interaction. Read-only.
---

# X Niche Scraper

## What this skill does

Opens `https://x.com/search?q=<query>` in the user's real Chrome session, scrolls through the top results, extracts the high-engagement posts (default: top 10 by relevance, the skill can also sort by Top / Latest / People), and writes a dated markdown file to `00 Inbox/` using the same per-post data schema as `x-bookmark-parser`. The output becomes the new raw-material feed for the Content Researcher.

This is the supply-side skill — the user's bookmarks are personal saves (subjective), but this is the wider market: what other accounts are publishing in the same niche, with what engagement, in what format.

## When to run

**Trigger phrases:**
- "search x for X" / "search twitter for X"
- "find posts about X" / "find tweets on X"
- "niche scrape X" / "scrape X for [topic]"
- "what's X saying about [topic]" / "what are people posting about [topic]"

**Do NOT run for:**
- The user's own bookmarks (use `x-bookmark-parser` instead)
- A single X URL (use `x-link-reader` instead)
- A specific account's profile/timeline (that's `x-engagement-hunter` territory — different skill)
- Non-X platforms

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Query | (none — must be specified) | **yes** |
| Search tab | `Top` (relevance-sorted) | no — `Latest`, `People`, `Media`, `Lists` also valid |
| Capture depth | top 10 posts | no — override to 5, 20, or "all visible in first snapshot" |
| Engagement floor | 1,000 views | no — set higher to filter for high-performing (e.g., 50K views) |
| Destination dir | `00 Inbox/` | no |
| File naming | `x-niche-<query-slug>-YYYY-MM-DD-HHMM.md` | no |

**Query formatting:** spaces in the query become `+` or `%20` in the URL. Special characters (colons, quotes) need URL encoding. Phrase queries (exact match) wrap in double quotes: `"missed call revenue"`.

**Engagement floor:** the default 1,000 views is a noise filter — X search results include a lot of low-engagement posts. Set higher (e.g., 50K views) when the user wants only proven winners. Posts below the floor are skipped without being parsed.

## Outputs

A single markdown file at `00 Inbox/x-niche-<query-slug>-YYYY-MM-DD-HHMM.md` with the same per-post schema as `x-bookmark-parser`. The header includes the query string, the search tab used, the engagement floor, and the timestamp.

The file also returns a one-paragraph summary to the operator with: file path, post count, and a one-line note about the dominant format / theme observed.

## Procedure

### Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected`, **HALT** and tell the operator to load the Chrome extension per `mavis browser install` output. Do not proceed with auto-spawned Chromium fallbacks for x.com — the security memory locks the OAuth-hijack surface.

### Step 2: Open or navigate to the search URL

```bash
mavis browser tool open_tab '{"url":"https://x.com/search?q=<URL-encoded query>&f=<tab>"}'
```

Notes:
- `f=top` is the default (relevance). `f=live` for Latest, `f=user` for People, `f=media` for Media, `f=lists` for Lists.
- Quote-wrapped phrases in the query: `"missed+call+revenue"` for an exact-match search.
- Note the returned `tabId` for subsequent calls.

### Step 3: Authentication check + load wait

Wait 3-5 seconds for the page to render. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":2}'
```

**Halt conditions (operator-alert only, never type credentials):**
- Snapshot shows "Sign in to X" / "Log in" / "Sign up" — operator needs to log in manually
- Snapshot shows a rate-limit warning ("You have exceeded the rate limit")
- URL is not `x.com/search` after navigation
- The query appears to be filtered / blanked by X (some queries trigger "This request looks like it might be automated")

**Proceed conditions:**
- Search results visible, with author handles + post timestamps
- The query string appears in the page (top of results or breadcrumb)

### Step 4: Extract top posts

Parse the snapshot's `text` field. Each search result is a post with:
- Author name + handle
- Timestamp
- Post text (full)
- Engagement metrics
- Link to original post (anchor href with `/status/<id>`)
- Whether the post is a Top hit, a quote, a reply, or a thread preview

Filter by the engagement floor (default 1,000 views). Posts below the floor are skipped.

**Do NOT scroll via `press_key`** — keyboard events route to the focused tab, not the `tabId` parameter. Same Focus Rule as `x-bookmark-parser`. If more posts are needed than fit in the first snapshot, the operator scrolls manually and re-runs the skill.

### Step 5: Format and write the file

Use the same per-post schema as `x-bookmark-parser`:

```markdown
# X Niche Scrape — <query> — YYYY-MM-DD HH:MM CT

**Query:** "<query>"
**Search tab:** Top (or Latest / People / Media)
**Engagement floor:** 1,000 views
**Posts captured:** N
**Source:** https://x.com/search?q=<query>&f=<tab>

---

## Post 1 — @author · [handle] · [timestamp]

[...same per-post fields as bookmark-parser...]

---

## Notes for the Content Researcher

[Any auto-detected patterns: dominant format, hook patterns observed, voice profiles of the top accounts, common thread types. If the operator specified a search-tab, note the differences in results between Top and Latest.]
```

### Step 6: Update the niches ledger

Append a one-line entry to `00 Inbox/_x-niche-ledger.mdl` (markdown list) so the Researcher can quickly see which niche captures are available:

```markdown
- YYYY-MM-DD HH:MM CT — <query-slug> (N posts, top tab, floor 1K)
```

### Step 7: Return summary

Send a one-paragraph summary to the operator:
- File path
- Post count
- Dominant format / theme observed (one line)
- Suggestions for follow-up scrapes (e.g., "narrow to Top accounts with 50K+ views" or "try Latest tab for fresher results")

## The Focus Rule (inherited from x-bookmark-parser)

The mavis browser tool has a documented limitation: `scroll`, `press_key`, and the click helper route to whichever tab the user's Chrome currently has focused, NOT the `tabId` passed to the tool. This skill uses `snapshot` (focus-agnostic) for content reading. If the operator wants more posts, they scroll manually and re-run.

## The Data Schema (inherited from x-bookmark-parser)

For every post, extract these fields. If a field is not visible in the snapshot, mark it as `unclear` rather than skipping.

| Field | Type | Source in snapshot |
|-------|------|-------------------|
| `index` | int | ordinal position (1-based) |
| `author_name` | string | text immediately before `@handle` |
| `handle` | string | `@<username>` |
| `timestamp` | string | relative time (e.g., "21h", "Jun 15") |
| `post_url` | string | first `/status/<id>` link under the post |
| `type` | enum | `Text` / `Article` / `Quote` / `Reply` / `Repost` |
| `title` | string? | if Article: the bolded first line |
| `pull_quote` | string? | the first 1-2 sentences if there's a strong hook |
| `full_text` | string | everything between author block and engagement metrics |
| `engagement.replies` | int | first number in the engagement row |
| `engagement.reposts` | int | second number |
| `engagement.likes` | int | third number |
| `engagement.views` | int | the "K"-suffixed number |
| `quoted_post` | object? | nested schema for any quoted post |
| `media_attached` | bool | true if `photo/N` links are present |

Do NOT extract: profile pics, follower counts, right-column "Who to follow" / trending widgets, the bottom-of-page ToS / Privacy links.

## The Safety Halts (inherited from x-bookmark-parser)

1. **No interaction.** Strictly read-only. Do not like, repost, follow, or reply.
2. **No credential entry.** If the page shows a login prompt, halt and alert the operator.
3. **Sensitive content skip.** If a search result contains DM screenshots, personal profile data, financial information, or any content the operator hasn't explicitly opted to capture, skip that post in the output.
4. **Unfamiliar UI.** If the snapshot shows a layout you don't recognize, halt and surface to the operator.
5. **Rate limiting.** If `mavis browser` returns a rate-limit error, halt and surface. X is aggressive about scraping; if the operator runs this skill repeatedly, expect to hit a rate limit within 10-20 minutes.
6. **Query filtering.** If X returns a "This request looks like it might be automated" page, halt. The operator needs to either slow down or log in more explicitly.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Bridge offline | `mavis browser status` shows `not connected` | Halt; tell operator to load Chrome extension |
| Login prompt | snapshot shows Sign in / Log in | Halt; tell operator to log in manually |
| Rate limit | snapshot shows rate limit warning OR `mavis browser` returns 429 | Halt; surface the rate-limit to operator; recommend waiting 10+ minutes |
| Query returns zero results | snapshot has no author blocks | Empty file with note "no results for this query"; suggest query refinement |
| Posts below engagement floor | views < floor | Skip silently; log in the "Notes for the Researcher" section that N posts were filtered |
| Mixed-language result set | multiple languages detected | Stay language-neutral in the file; flag in "Notes for the Researcher" |
| Active tab is wrong | `get_active_tab` returns a non-search URL | Note the issue; the search tab can still be snapshotted via `tabId` |

## Verification

After writing the file:
1. `ls -la` confirms the file exists with non-zero size
2. `wc -l` shows the expected number of `---` separators + 1 (header) + 1 (notes) = post count + 2
3. `grep -c "^## Post" <file>` matches the post count
4. The niches ledger is appended (not overwritten)
5. No posts below the engagement floor are present

## Cross-reference

- `x-bookmark-parser` — for the user's own bookmarks (subjective curation). Different output destination, same data schema.
- `x-engagement-hunter` — for replying to a specific account's posts (uses the Scribe to draft a value-add reply, different output destination).
- `x-link-reader` — for a single X URL.
- `mavis browser` CLI — the underlying tool surface; this skill is a procedure on top.
- The Content Researcher (`03 Projects/X-Content-Engine/agents/researcher.md`) — consumes this skill's output as a primary input source.
