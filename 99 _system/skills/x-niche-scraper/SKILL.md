---
name: x-niche-scraper
description: |
  Search X for a parameterized query, extract the top high-engagement posts
  (default: top 10 by relevance, configurable floor), and dump to `00 Inbox/`
  using the same data schema as x-bookmark-parser. The supply-side sister
  skill: where bookmark-parser reads the user's subjective saves, this
  scrapes the wider market. Uses mavis browser bridge (real Chrome).
  Triggers: "search x for [topic]", "find posts about [topic]", "niche
  scrape [topic]", "what are people posting about [topic]". Read-only.
  Auto-invoke when Andre asks for market/supply-side research on a topic
  in the X-Content-Engine. Do NOT use for the user's own bookmarks (use
  x-bookmark-parser) or a single X URL (use x-link-reader).
---

# x-niche-scraper

The supply-side sister to `x-bookmark-parser`. Where bookmarks are
subjective curation, this is the wider market: what other accounts are
publishing in the same niche, with what engagement, in what format. The
Researcher consumes the output as its primary input.

## Intent

- Search X for a parameterized query
- Extract the top high-engagement posts (default 10, configurable floor)
- Write a dated markdown capture to `00 Inbox/`
- Update the niches ledger so the Researcher can find prior captures
- Report back: file path, post count, dominant format/theme

The deterministic layer (URL encoding, search-tab params, output format)
lives in `references/`. Safety halts and edge cases live in `tests/` and
inherit from `x-bookmark-parser`.

## When to run

**Triggers:**
- "search x for [topic]" / "search twitter for [topic]"
- "find posts about [topic]" / "find tweets on [topic]"
- "niche scrape [topic]" / "scrape x for [topic]"
- "what's x saying about [topic]" / "what are people posting about [topic]"

**Do NOT run for:**
- The user's own bookmarks → use `x-bookmark-parser`
- A single X URL → use `x-link-reader`
- A specific account's profile/timeline → different skill
- Non-X platforms

## Inputs

| Input | Default | Required |
|---|---|---|
| Query | — | **yes** |
| Search tab | `Top` (relevance) | no — `Latest` / `People` / `Media` / `Lists` |
| Capture depth | top 10 | no — 5, 20, or "all visible" |
| Engagement floor | 1,000 views | no — set higher for proven-winners filter |
| Destination | `00 Inbox/` | no |
| Filename | `x-niche-<query-slug>-YYYY-MM-DD-HHMM.md` | no |

Engagement floor is the noise filter: X search returns a lot of
low-engagement posts. The 1K default catches most signal. For "only proven
winners," bump to 50K. Posts below the floor are skipped silently.

## Output contract

A single markdown file at `00 Inbox/x-niche-<query-slug>-YYYY-MM-DD-HHMM.md`
with the per-post schema inherited from `x-bookmark-parser`. Header includes
query, search tab, engagement floor, and timestamp. Trailing "Notes for the
Content Researcher" section with the dominant format and pattern observations.

Plus a one-line append to `00 Inbox/_x-niche-ledger.mdl` so the Researcher
can quickly find prior captures.

## Resolver

Auto-invoke when Andre:
- Asks for "what people are saying about [topic]" in the X-Content-Engine
- Says "niche scrape" or "niche scan"
- Wants market-supply input for the Researcher

Do NOT auto-invoke for:
- "Read my bookmarks" (use `x-bookmark-parser`)
- "Get this tweet" / "summarize this URL" (use `x-link-reader`)

## Safety posture

Read-only. Inherits all halt conditions from `x-bookmark-parser` (login,
unfamiliar UI, rate limit, sensitive content, no bridge). Adds one
niche-specific halt: if X returns "This request looks like it might be
automated," halt and surface — the operator needs to slow down or log in
more explicitly. The specific test cases are in `tests/niche-halts.md`.

## Cross-reference

- `references/url-encoding.md` — query → URL rules (spaces, quotes, special chars)
- `references/output-format.md` — the markdown template (schema inherited)
- `tests/niche-halts.md` — search-specific halts (bot detection, query filtering)
- `x-bookmark-parser` — the schema, focus rule, and most halts are inherited
- The Content Researcher — primary consumer of this skill's output
