---
name: fb-poster
description: |
  Publish one approved FB-Engine draft to Facebook via the user's real
  Chrome (CDP bridge). Reads `03 Projects/FB-Engine/approved/` for
  drafts with `status: approved`, navigates to the target (Group URL
  for Typology 1, post URL for Typology 2), finds the contentEditable
  composer / comment input via semantic locators, pastes the approved
  text using `page.fill()` (NOT `page.type()` — same React-controlled
  input duplication issue as `x-publish`), HALTs for human verification
  by default, then clicks Post and captures the post URL. Safety gate:
  HALT immediately if the draft is NOT in `approved/`. Trigger on:
  "post the approved FB draft", "publish the next FB-CE draft", "ship
  the FB comment". Do NOT use for: drafts in `drafts/` (un-approved),
  reading posts (that's `fb-group-reader`), drafting (that's the
  Scribe), the Telegram bridge (that's `ea-fb-draft-approval`), or
  non-FB platforms.
---

# fb-poster

The Mavis-side "post the approved draft" step for the FB-Engine.
Closes the Scribe → EA → Facebook half of the FB-Engine loop. Pairs
with `fb-draft-scribe` (writer) and `ea-fb-draft-approval` (router).

## When to invoke

**Auto-invoke (cron — recommended):**
- Every 5 minutes during business hours (09:00-21:00 CT)
- This is tight because Typology 2 replies have a 4-hour engagement
  window; the Poster must fire fast after the bridge routes approval

**Triggers (manual):**
- "post the approved FB draft"
- "publish the next FB-CE draft"
- "ship the FB comment"
- "fb-poster on approved/"

**Do NOT use for:**
- Drafts in `drafts/` (status: open) — the Poster only reads `approved/`
- Reading posts (that's `fb-group-reader`)
- Drafting (that's `fb-draft-scribe`)
- The Telegram bridge (that's `ea-fb-draft-approval`)
- Non-FB platforms (X has `x-publish`, LinkedIn has its own)

## Inputs

| Input | Default | Required |
|---|---|---|
| `--approved-dir` | `03 Projects/FB-Engine/approved/` | yes |
| `--published-dir` | `03 Projects/FB-Engine/archive/published/` | yes (auto-created) |
| `--publish-ledger` | `03 Projects/FB-Engine/queue/drafts-published.mdl` | yes (auto-created) |
| `--cdp-url` | `ws://localhost:58632` | yes (or `--cdp-port` to auto-detect) |
| `--draft` | next in queue | optional |
| `--all` | off (one at a time) | optional |
| `--no-halt` | off (HALT enabled) | optional |

## The mechanism (the discipline)

For each approved draft:

### Step 1: SAFETY GATE

The Poster HALTs immediately if the draft's frontmatter `status` is
not `approved`. The Poster only reads from `approved/` — never
`drafts/`. This is the load-bearing safety check. Without it, the
Scribe's `drafts/` could leak into Facebook.

### Step 2: Parse the draft

Parse the YAML frontmatter to extract:
- `target_url` (or `group_url` / `post_url` / `original_url` fallback)
- `typology` (T1 or T2)
- `draft_id` (for the publish ledger)
- Body text from `## Generated draft` (or `## Edited draft` for
  Telegram-edited drafts)

### Step 3: Connect to the user's real Chrome via CDP

Auto-detect the CDP port by scanning `ps -axww` for
`--remote-debugging-port=N` (prefers the Playwright MCP's managed
Chrome). Connect via `p.chromium.connect_over_cdp(cdp_url)`.

### Step 4: Navigate to the target

```python
await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
```

For Typology 1: the target is the Group URL (the Group feed).
For Typology 2: the target is the post URL (the specific post).

### Step 5: Find the composer / comment input

The composer / comment input is a `[contenteditable="true"]` div. FB's
DOM is heavily obfuscated with random React/Tailwind classes, so we
use semantic locators (a11y tree + contenteditable) instead of CSS
selectors.

```python
composers = page.locator('[contenteditable="true"]')
# T1 (original post): the first composer (top of feed)
# T2 (reply): the last composer (the post's comment input)
composer = composers.first if typology == "T1" else composers.last
```

### Step 6: Fill the text (the load-bearing fix)

`page.locator(...).type()` duplicates text in FB's React-controlled
inputs — same bug as the X-CE `x-publish` skill on x.com. The fix is
`page.locator(...).fill(text)`, which sets the value directly without
firing keyboard events:

```python
await composer.fill(text, timeout=10000)
```

### Step 7: Verify the staged text (programmatic)

```python
staged_text = await composer.inner_text()
# Compare to expected text (tolerate trailing newline)
if staged_text.strip() != text.strip():
    HALT
```

### Step 8: HALT for human verification (default)

The script prints a summary and waits for the operator to press Enter
on stdin. The operator verifies the staged text in the live Chrome,
then presses Enter to confirm the click. Ctrl+C aborts.

This is the same HALT as `x-publish` — the operator's last chance to
catch a typo, a wrong post, or a wrong target. The draft was
operator-approved via Telegram, so this HALT adds a "the text looks
right in the live UI" check.

Use `--no-halt` to skip the HALT for fully-automated cron runs.

### Step 9: Click Post and capture the URL

```python
post_button = page.get_by_role("button", name=re.compile("Post|Share|Send|Comment|Reply"))
# Filter to visible + enabled, click the first match
await post_button.click(timeout=5000)
```

After clicking, wait 3 seconds for FB to complete the post, then
capture `page.url`. If the URL changed to a post-specific URL, that's
the post URL. If it stayed on the same page, fall back to the original
URL + the post_id (for some T1 cases).

### Step 10: Archive the published draft

Move the draft to `archive/published/`, update the frontmatter:
- `status: approved` → `status: published`
- Add `published_at: <ISO timestamp>`
- Add a `post_url: <captured URL>` field

Append a one-line entry to `queue/drafts-published.mdl`:
```
- 2026-06-18 13:30 CT — <draft_filename> → <post_url> | T<1|2> | fb.com
```

## Hard constraints

1. **SAFETY GATE:** The Poster HALTs immediately if the draft is not
   in `approved/`. This is non-negotiable.
2. **HALT by default:** Between fill and click, the script pauses for
   operator verification. `--no-halt` is the override.
3. **No bot-detection bypass:** Drives the user's real Chrome via CDP.
   No user-agent rotation, no request timing randomization, no
   fingerprint spoofing.
4. **One draft at a time by default:** `--all` is opt-in. Each
   operator-cron cycle processes up to `--max-posts` drafts.
5. **No scraping:** The Poster only navigates to operator-provided
   target URLs from the draft's frontmatter. It does not discover
   URLs, follow links, or search.
6. **No engagement surface interaction:** The Poster only types in
   the composer / comment input and clicks the Post button. It does
   not like, share, react, or follow.
7. **Read the operator's `target_url`:** The Poster does not infer
   the target from the post's URL or the Group's URL. It uses the
   frontmatter field.

## HALT conditions

- Draft not in `approved/` (status != approved) → HALT, return code 2
- CDP connection fails → HALT with error, return code 1
- Navigation to target fails → HALT with error, return code 1
- Composer / comment input not found on page → HALT with error
- Fill fails → HALT with error
- Staged text doesn't match expected → HALT with error
- No Post / Share / Comment button found → HALT with error
- Operator aborts at HALT (Ctrl+C) → return code 1, draft stays in
  `approved/`
- Operator aborts AFTER Post clicked but URL capture fails → log
  error, draft stays in `approved/` (the post may have succeeded; the
  operator should verify in the live Chrome before re-running)

## CLI

```bash
# Default: process the next approved draft, HALT before clicking Post
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-poster/scripts/poster.py

# Process a specific draft
python3 .../poster.py --draft "2026-06-18-1330-t2-post-1234567890.md"

# Process all approved drafts (cron mode)
python3 .../poster.py --all

# Fully-automated: skip the HALT
python3 .../poster.py --no-halt

# Custom paths
python3 .../poster.py --approved-dir /path/to/approved/ \
                       --published-dir /path/to/published/
```

## Cron schedule (recommended)

```cron
# Every 5 min during business hours (9am-9pm CT)
*/5 9-20 * * 1-6  python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-poster/scripts/poster.py --all --no-halt \
    >> ~/.mavis/logs/fb-poster.log 2>&1
```

The `--all --no-halt` combo is the cron-mode default: process every
approved draft, click Post on each. The cron mode is safe because
each draft was operator-approved via Telegram before reaching
`approved/`. The 5-minute cadence is tight enough for the 4-hour
Typology 2 engagement window.

For operator-triggered mode (manual runs), use the default
(one-at-a-time, with HALT).

## Integration with other skills

The full FB-Engine chain:

```
fb-group-reader (read path)
        ↓ JSON
fb-draft-scribe (drafts → drafts/)
        ↓ markdown
ea-fb-draft-approval (drafts/ → approved/)
        ↓ operator-approved markdown
fb-poster (THIS skill, approved/ → Facebook)
        ↓ published URL
archive/published/  ← audit trail
queue/drafts-published.mdl  ← chronological ledger
```

## Cross-references

- `fb-session-guardian` — pre-flight (Poster depends on a valid session)
- `fb-draft-scribe` — writes drafts
- `ea-fb-draft-approval` — routes operator decisions to `approved/`
- `x-publish` — the X-CE parallel (same shape: stage → HALT → click
  → capture URL; different platform)
- `queue/drafts-published.mdl` — the publish ledger (per-platform,
  append-only)

## Source

- `~/.mavis/agents/mavis/skills/fb-engine/fb-poster/scripts/poster.py`
- Mirror: `~/MiniMax-Agent/99 _system/skills/fb-engine/fb-poster/scripts/poster.py`

## Changelog

- 1.0.0 (2026-06-18) — initial skill. Mirrors `x-publish` shape
  (stage → HALT → click → capture URL). CDP-bridged Playwright. Auto-
  detects CDP port. Semantic locators for `[contenteditable="true"]`
  (a11y-based, not CSS — robust against FB's random React classes).
  `page.locator(...).fill(text)` (not `.type()` — same React-controlled
  input duplication fix as x-publish). HALT by default with
  `--no-halt` override. Safety gate: HALT if draft not in `approved/`.
  Archive on success: moves to `archive/published/`, appends to
  `queue/drafts-published.mdl`. CLI flags: --approved-dir, --published-
  dir, --publish-ledger, --cdp-url, --cdp-port, --draft, --all,
  --max-posts, --no-halt.
