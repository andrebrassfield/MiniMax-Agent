---
description: "URL encoding rules for x-niche-scraper search queries — spaces, special characters, phrase quoting, search-tab parameters. Load when the skill is invoked or when debugging search URL construction. Moved from skill-local references 2026-06-22 as part of Upgrade 1 skill-scaling-law refactor."
source: ~/.mavis/agents/mavis/skills/x-niche-scraper/references/url-encoding.md
---

# URL Encoding — x-niche-scraper

The search URL format is `https://x.com/search?q=<encoded>&f=<tab>`. Query
encoding rules:

## Basic rules

- Spaces in the query become `+` or `%20` (both work; `+` is shorter)
- Special characters need percent-encoding:
  - `:` → `%3A`
  - `"` → `%22`
  - `&` → `%26`
  - `#` → `%23`
  - `?` → `%3F`

## Phrase queries (exact match)

Wrap the phrase in double quotes inside the query: `"missed call revenue"`.
URL-encoded: `%22missed+call+revenue%22`.

## Tab parameters

| Tab | URL param | Behavior |
|---|---|---|
| Top | `f=top` | relevance-sorted, default |
| Latest | `f=live` | newest first |
| People | `f=user` | user handles matching the query |
| Media | `f=media` | posts with images/video |
| Lists | `f=lists` | public lists matching the query |

## Examples

| Query | Encoded URL |
|---|---|
| `Shopify inventory` | `https://x.com/search?q=Shopify+inventory&f=top` |
| `"missed call revenue"` | `https://x.com/search?q=%22missed+call+revenue%22&f=top` |
| `HVAC: AI agents` | `https://x.com/search?q=HVAC%3A+AI+agents&f=top` |
| `AI automation` (Latest) | `https://x.com/search?q=AI+automation&f=live` |

## Failure indicator

If the URL navigates but the snapshot shows "This request looks like it
might be automated" or a similar warning, X's bot detection has flagged
the query. Halt per `tests/niche-halts.md#H7`.
