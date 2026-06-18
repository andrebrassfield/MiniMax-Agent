# Niche-Specific Halts — x-niche-scraper

Inherits all halt conditions from `x-bookmark-parser` (login prompt,
unfamiliar UI, rate limit, sensitive content, no bridge). See
`../../x-bookmark-parser/tests/safety-halts.md` for those.

This file documents the one additional halt that search-specific scraping
needs.

## H7. X bot-detection ("This request looks automated")

**Detection:** The snapshot contains text like "This request looks like it
might be automated" or similar bot-warning page. The URL is still
`x.com/search` but the page body is the warning, not results.

**Expected response:** Halt and surface the bot-detection message to the
operator. The operator's options are:
- Wait 10+ minutes and try again with a different query phrasing
- Log in more explicitly (X weighs cookies differently for repeated searches)
- Use a different account's session (not the operator's, that's outside scope)

Do NOT retry in a tight loop. X's bot detection is per-IP and per-cookie;
aggressive retries make the block worse.

## Eval cases

| Halt | Input | Expected behavior |
|---|---|---|
| H7 | snapshot contains "This request looks automated" | Halt, no retry, recommend wait |
