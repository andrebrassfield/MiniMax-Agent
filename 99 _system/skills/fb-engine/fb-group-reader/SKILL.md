---
name: fb-group-reader
description: |
  Read recent posts from a Facebook Group via the user's real Chrome
  session. Connects to CDP, navigates to a Group URL, intercepts
  `/api/graphql/` responses via `page.on("response")`, extracts Post ID
  / Author / Text / Timestamp to JSON. READ-ONLY — identical to opening
  DevTools and copying the response. Use to build the ammunition for
  fb-draft-scribe typologies. Do NOT use to bypass bot detection, scrape
  Groups the user is not a member of, or auto-engage.
---

# fb-group-reader

Read-only GraphQL feed extractor for a Facebook Group. Mirrors the
`x-graphql-interceptor` pattern, scoped to Facebook.

## When to invoke

**Pre-flight required:** `fb-session-guardian` must return PASS first.

**Auto-invoke when:**
- The operator wants to see recent posts in a specific Group
- `fb-draft-scribe` needs raw material for the Authority Comment typology
- The operator asks "what's happening in [group name]"
- A scheduled research cron fires (the next iteration)

**Triggers (manual):**
- "read the latest from [group URL]"
- "intercept GroupFeed for [group]"
- "extract posts from [group]"
- "what's in [group] this week"

**Do NOT use for:**
- Groups the user is not a member of (the GraphQL feed is gated by
  membership — non-members get a "Join this group to see posts" wall)
- Bypassing bot detection (this script does not evade — it uses the
  user's real browser)
- Auto-engaging (READ-ONLY — no replies, no posts, no likes)
- Single-post deep reads (use the `fb-link-reader` analog, TBD)

## The mechanism (the discipline)

Facebook's Group feed fires GraphQL requests when the user navigates to
a Group and scrolls. The endpoint pattern is:

```
/api/graphql/?q=<QueryName>  OR  /api/graphql/<hash>/<QueryName>
```

Common query names you'll see:
- `GroupFeedQuery` — the main group feed
- `GroupsCometFeedRootQuery` — the new Comet UI's root feed query
- `GroupDiscussionFeedQuery` — discussion thread feed
- `CometGroupDiscussionRootSuccessQuery` — newer Comet variant

Response bodies are deeply nested JSON. The shape changes frequently
(Facebook A/B tests response structures regularly). The parser uses a
heuristic walker that identifies post records by the presence of:
- A numeric `post_id` (10-20 digit number) OR an `id` matching the
  pattern, AND
- A `message` or `text` field somewhere in the node

The walker dedupes by post_id across multiple captured responses
(Facebook fires the same feed query several times as the user scrolls).

## The procedure (the discipline)

### Step 1: Pre-flight (load-bearing)

`fb-session-guardian` MUST return PASS first. If the session is dead,
the GraphQL calls return 401 or redirect to a login wall.

### Step 2: Run the script

```bash
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-group-reader/scripts/read.py \
  --group "https://www.facebook.com/groups/<slug>" \
  --output /tmp/fb-posts.json
```

The script:
1. Auto-detects the CDP port (or accepts `--cdp-port`)
2. Connects to the user's real Chrome via CDP
3. Registers `page.on("response")` BEFORE navigation
4. Navigates to the Group URL
5. Waits for the initial feed to render + GraphQL to fire
6. Scrolls N times (default 2) to capture more posts
7. Walks each captured `/api/graphql/` response, extracts post records
8. Deduplicates by post_id, sorts by timestamp desc, keeps top N
9. Writes JSON to `--output`

### Step 3: Consume the JSON

```python
import json
with open("/tmp/fb-posts.json") as f:
    data = json.load(f)
results = data["results"]  # list of post dicts
# Filter / sort / dispatch to fb-draft-scribe (next)
```

Each `results[i]` has:
- `post_id` (str, numeric)
- `author` (str, may be "unknown" if not extractable)
- `text` (str, the post body)
- `timestamp` (int, Unix seconds; may be null)
- `fetched_at` (int, Unix seconds)
- `source_query` (str, the GraphQL query name; may be null)

### Step 4: Local-test the interceptor

To verify the interceptor is catching `/api/graphql/` payloads:

1. Launch Chrome with the CDP bridge enabled:
   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
     --remote-debugging-port=58632
   ```
2. In that Chrome, log in to Facebook.
3. Run the guardian:
   ```bash
   python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-session-guardian/scripts/guard.py
   ```
   Expect: `PASS (port 58632)` on stderr, JSON with `session_state: "PASS"` on stdout.
4. Pick a Group URL you are a member of (a public Group for first test).
5. Run the reader:
   ```bash
   python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-group-reader/scripts/read.py \
     --group "https://www.facebook.com/groups/<your-group-slug>" \
     --output /tmp/fb-test.json
   ```
6. Inspect `/tmp/fb-test.json`:
   - `graphql_responses_captured` should be > 0 (typically 5-15)
   - `results` should be a list of post dicts
   - Each post has `post_id`, `author`, `text`, `timestamp`
7. Cross-check by opening the Group in a browser tab and confirming the
   same posts are listed. The top 5 by timestamp should match the
   visible "Recent" posts.
8. **Optional validation:** open Chrome DevTools Network tab, filter by
   `graphql`, scroll the Group, and confirm the same query names appear
   in the script's `source_query` field.

### Common issues (local-test debugging)

- **`graphql_responses_captured: 0`** — the listener was registered too
  late, the Group URL didn't fire GraphQL, or the user's session is
  gated. Check that you're a member of the Group and that
  `fb-session-guardian` returns PASS.
- **Empty `results` but `responses > 0`** — the parser is missing the
  post node. Open the captured response in DevTools, look for a
  `message` field near a `post_id` / `id` field, and adjust the
  heuristic. (FB's response shape changes; the heuristic has 6+
  fallback paths but it can miss a new shape.)
- **All `author: "unknown"`** — the actor field is in an unexpected
  place. The script checks `actor`, `owner`, `author`, `poster`,
  `from`. If FB moves it, add the new field name to `ACTOR_FIELDS`.
- **All `timestamp: null`** — the timestamp is in an unexpected place.
  The script checks `timestamp`, `creation_time`, `published_time`,
  `time`. Add the new field to `TS_FIELDS` if needed.

## CLI flags

```bash
--group <url>            # required
--output <path>          # required
--cdp-port <N>           # default: auto-detect
--max-posts <N>          # default: 25
--scroll-passes <N>      # default: 2
--scroll-wait <seconds>  # default: 4.0
--page-timeout-ms <ms>   # default: 45000
```

## HALT conditions

- CDP connection fails → error in `errors[]`, no results written
- Navigation fails → error in `errors[]`, no results written
- 0 GraphQL responses captured → likely not a member, or the page
  didn't fire (e.g., checkpoint wall). Check the guardian's output
  and verify membership.
- All scroll passes fail → error in `errors[]`, partial results
  (whatever was captured before the scroll failures)

## Hard constraints

- READ-ONLY: zero clicks on reply / post / like / share
- NO bot-detection bypass: drives the real browser via CDP
- NO scrape-and-deposit loops: invoked by the operator, not chained
  to an auto-reply loop
- Group membership: the user must already be a member of the Group
- NO data exfiltration: the script writes only to the operator's
  local `--output` path; nothing is sent off-device

## Integration with other skills

The cron chain is:
1. `fb-session-guardian` — auth pre-flight (PASS required)
2. `fb-group-reader` — extract posts to JSON (this skill)
3. `fb-draft-scribe` — generate typology-1 + typology-2 drafts (next)
4. `ea-draft-approval` — Mavis surfaces drafts to Andre via Telegram
5. `fb-poster` — publish approved drafts (next, gated on `approved/`)

## Cross-references

- `x-graphql-interceptor` — the X.com analog (same interception
  mechanism, different parser)
- `fb-session-guardian` — the auth pre-flight
- `fb-draft-scribe` — the next skill (consumes this JSON)
- `ea-draft-approval` — the Telegram approval bridge
- `ammunition.mdl` — the structured research ledger (typology 2 reads
  from this)

## Source

- `~/.mavis/agents/mavis/skills/fb-engine/fb-group-reader/scripts/read.py`
- Mirror: `~/MiniMax-Agent/99 _system/skills/fb-engine/fb-group-reader/scripts/read.py`

## Changelog

- 1.0.0 (2026-06-18) — initial skill. Mirrors x-graphql-interceptor
  structure. CDP port auto-detection. `page.on("response")` registered
  before navigation. Heuristic post-record walker with 6 text-field
  fallbacks, 5 actor-field fallbacks, 4 timestamp-field fallbacks.
  Multi-pass scroll capture. JSON output with results[] + errors[].
  Scroll wait configurable per Group size.
