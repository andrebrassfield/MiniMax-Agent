---
name: x-bookmark-parser
description: |
  Read the user's X/Twitter bookmarks via the real Chrome session (mavis browser
  bridge) and dump structured post metadata to a dated file in `00 Inbox/`.
  Triggers: "read my X bookmarks", "parse my bookmarks", "summarize my x saves",
  "what's in my x bookmarks", "x bookmarks". Read-only — zero interaction. Auto-
  invoke when Andre references X bookmarks and wants them captured for downstream
  research/synthesis. Do NOT use for a single X URL (use `x-link-reader`), a
  profile timeline, or non-X platforms.
---

# x-bookmark-parser

The supply-side data extraction skill for the X-Content-Engine. The user's
bookmarks are subjective curation; the Researcher and Scribe consume the
extracted metadata to find format patterns, hook structures, and voice
references.

## Intent

- Open the user's bookmarks page in the real Chrome session (mavis browser
  bridge, NOT auto-spawned Chromium — the security boundary).
- Extract the visible bookmarks' metadata into the standard per-post schema.
- Write a dated markdown capture to `00 Inbox/`.
- Report back with the file path, post count, and a one-paragraph theme
  synthesis.

The model decides *how* to read the snapshot, parse the post boundaries, and
synthesize the themes. The deterministic layer (data schema, output format,
tool commands) lives in `references/`. Safety halts live as test cases in
`tests/`.

## When to run

**Triggers:**
- "read my X bookmarks" / "parse my bookmarks" / "what's in my x bookmarks"
- "summarize my x saves" / "summarize my bookmarks"
- "x bookmarks" (as a request, not a reference)

**Do NOT run for:**
- A single X URL → use `x-link-reader`
- A profile timeline or thread → different x-* skill
- A non-X platform

## Inputs

| Input | Default | Required |
|---|---|---|
| Capture target | `https://x.com/i/bookmarks` | no |
| Destination | `00 Inbox/` | no |
| Filename | `x-bookmarks-YYYY-MM-DD-HHMM.md` | no |
| Timezone | `America/Chicago` | no |

The skill reads the "All Bookmarks" view at snapshot time. If the operator
wants more than fits in the first snapshot, they scroll in Chrome and re-run.

## Output contract

A single markdown file at `00 Inbox/x-bookmarks-YYYY-MM-DD-HHMM.md` with the
header block, one section per post, and a trailing "Themes" paragraph. Per-post
schema, output format, and the focus-rule constraint are in `references/`.

Report back: file path, post count, themes paragraph, partial-capture flag if
the visible window was incomplete.

## Resolver

Auto-invoke this skill when Andre:
- References X bookmarks and wants them captured
- Says "what have I saved on X about [topic]?"
- Asks for a "bookmarks digest" or "bookmarks summary"

Do NOT auto-invoke for:
- A specific tweet URL (use `x-link-reader`)
- Search/discovery (use `x-niche-scraper`)
- A profile timeline (use `x-engagement-hunter`)

## Safety posture

Read-only. No like, repost, follow, reply, or any interactive action. If the
page shows a login prompt, unfamiliar UI, or rate-limit warning, the skill
*halts and surfaces* — never types credentials or retries aggressively. The
specific halt conditions and their test cases are in `tests/safety-halts.md`.

## Cross-reference

- `references/data-schema.md` — the per-post extraction schema
- `references/output-format.md` — the markdown file template
- `references/focus-rule.md` — the mavis browser tool's tabId-vs-focus limitation
- `tests/safety-halts.md` — login, unfamiliar UI, rate-limit, sensitive content
- `tests/edge-cases.md` — empty bookmarks, partial capture, quote-tweet nesting
- `x-link-reader` skill — for a single X URL
- `x-niche-scraper` skill — for the market-supply side (other accounts' posts)
- CHIEF pattern: `00 Inbox/` is the staging lane; capture goes to `02 Notes/articles/`
  for keepers, or trash.
