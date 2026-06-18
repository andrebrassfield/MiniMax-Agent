# Query Generation — x-hype-translator

The chief (Mavis) auto-generates 2-3 X search queries from the tool
name. Operator can override with a specific query if they have one
in mind.

## Default query patterns (in priority order)

| # | Pattern | When to use |
|---|---|---|
| 1 | `<tool> just released` | Fresh drops, same-day posts |
| 2 | `<tool> launch` | Day-of-launch announcements |
| 3 | `<tool> dropped` or `<tool> shipped` | Casual / community-speak announcements |
| 4 | `<tool> benchmark` | Technical posts (model releases, eval results) |

## URL pattern

```bash
mavis browser tool open_tab '{"url":"https://x.com/search?q=<encoded>&f=live"}'
```

- `f=live` is the default tab (Latest — fresh posts first)
- `f=top` for established tools (relevance-sorted)
- `f=media` for screenshot-heavy announcements

URL encoding rules: spaces → `+` or `%20`; phrases → wrapped in `%22`.
Full rules in `x-niche-scraper/references/url-encoding.md`.

## Query retry logic

If the first query returns 0 results, try the next pattern in
sequence. After 2 patterns fail, halt and report "tool too fresh,
try again in 24h" — the X chatter may not have rolled up yet.

## Operator override

If the operator provides a specific query (e.g., "search for
'claude code hooks' instead of 'claude code'"), use that query
verbatim. Skip the auto-generation. The override is a single query,
not a list — pass it directly.
