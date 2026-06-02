---
type: pattern
created: 2026-06-02
tags: [pattern, scraping, scrapling, ingestion, adaptive-selectors, anti-bot, mavis-apex]
source: https://github.com/D4Vinci/Scrapling
---

# Adaptive Selectors for Web Scraping

> The Scrapling insight that generalizes: **selectors that survive website redesigns are learned, not written.** A CSS selector brittle to layout changes is a static assertion. A selector that uses content similarity + sibling structure to relocate itself after a redesign is an adaptive assertion. The first kind breaks; the second kind heals.

## The principle

Most scraping breaks the same way: a site's redesign changes a class name, an ID, a layout. The brittle selector `div.product-card .price::text` stops matching. The agent either fails silently (returns empty) or noisily (throws an error). Either way, the data flow breaks.

Scrapling's adaptive selector flips this: when you call `.css('.product', auto_save=True)`, the library *learns the element's signature* — its position in the DOM tree, its siblings, its text content, its style attributes. On a subsequent call, if the selector fails, passing `adaptive=True` makes the library search for the element by similarity to the saved signature. If the new element is "close enough" (configurable threshold), it gets returned.

This is the same mental model as:
- **Self-healing tools** ([[03 The Custom MCP Arsenal#MCP #4: `tool-self-healer`]]) — same idea, different layer
- **Mixture of agents** ([[Mixture of Agents]]) — N selectors, take the consensus
- **Reflexion loops** ([[Reflexion Loop]]) — when a step fails, remember why, retry differently

The Scrapling pattern is the *web-scraping* instantiation of the same principle: **don't hardcode brittle assumptions; encode them as constraints the system can re-derive.**

## The four fetchers (the type system of web access)

| Fetcher | Target | Speed | Anti-bot | When to use |
|---|---|---|---|---|
| `Fetcher` | Static HTML, JSON APIs | ~100ms | TLS fingerprint only | Default. Try this first. |
| `StealthyFetcher` | Cloudflare Turnstile, anti-bot interstitial | ~2-5s | Native bypass | When Fetcher gets blocked |
| `DynamicFetcher` | JS-rendered SPAs, infinite scroll | ~3-10s | Real Chromium | When content requires JS to appear |
| `AsyncFetcher` | Async equivalent of Fetcher | ~100ms × N | TLS fingerprint | For parallel batch fetches |

The principle: **escalate up the chain only when the cheaper option fails.** Don't reach for StealthyFetcher by default — it's 20-50× slower than Fetcher. Start with Fetcher, fall back to StealthyFetcher only on block detection.

Scrapling's block detection is built in: it watches for 403/503 responses, Cloudflare interstitial HTML patterns, and redirect loops. When detected, the Spider framework automatically retries with a different fetcher.

## The agent engineering principle

**Anti-bot bypass is a *routing* decision, not a *reliability* decision.** Treating Cloudflare bypass as "just retry until it works" wastes time. Treating it as a routing decision — "Fetcher failed → escalate to StealthyFetcher" — is correct because each tier has different cost characteristics.

The same shape applies to:
- Model selection: cheap model first, frontier model on hard cases
- Tool selection: fast tool first, slow tool on failure
- Memory access: in-memory cache first, disk second, network third

Escalation chains are a first-class pattern.

## The Spider framework (full crawls)

For multi-page scraping, Scrapling offers a Scrapy-like Spider:

```python
class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]
    concurrent_requests = 10
    
    async def parse(self, response: Response):
        for item in response.css('.product'):
            yield {"title": item.css('h2::text').get()}
```

Key features that matter for EA use:

1. **Pause and resume** — checkpoints to disk. Ctrl+C is a graceful pause. Restart resumes. For a 10K-page crawl that takes 8 hours, this is the difference between losing 7 hours of work and losing 0.
2. **Multi-session per spider** — `manager.add("fast", FetcherSession(impersonate="chrome"))` and `manager.add("stealth", AsyncStealthySession())`. Route specific URLs to specific sessions. The Spider framework handles the dispatch.
3. **Streaming mode** — `async for item in spider.stream()`. The first item arrives in seconds, not after the full crawl completes. For an EA getting paged during a long crawl, this matters.
4. **Development mode** — cache responses to disk on first run, replay on subsequent runs. Iterate on `parse()` logic without re-hitting the target. (Same idea as VCR cassettes in HTTP testing.)
5. **Robots.txt compliance** — optional `robots_txt_obey=True`. For an EA scraping at scale, respecting robots.txt is the right default.

## The MCP server (the integration surface)

Scrapling ships an MCP server (`pip install "scrapling[ai]"`). The README:

> Built-in MCP server for AI-assisted Web Scraping and data extraction. The MCP server features powerful, custom capabilities that leverage Scrapling to extract targeted content before passing it to the AI (Claude/Cursor/etc), thereby speeding up operations and reducing costs by minimizing token usage.

This is the killer feature for Mavis-Apex. The MCP server extracts *targeted* content (CSS/XPath selector applied at the scraping site) before passing it to the LLM. Instead of "here's a 200KB HTML page, figure out where the product titles are," the LLM gets "here are the 47 product titles, plus the price, plus the URL." The token cost drops by 100×.

The `auto_save=True` + `adaptive=True` combo is the M3-equivalent insight: the *tool* does the structural work, the *model* does the reasoning work. Same as the rest of the Mavis-Apex design philosophy.

## The CLI (no code path)

For one-off fetches, the CLI is sufficient:

```bash
scrapling extract get 'https://example.com' content.md
scrapling extract get 'https://example.com' content.txt --css-selector '#fromSkipToProducts'
scrapling extract stealthy-fetch 'https://nopecha.com/demo/cloudflare' captchas.html --solve-cloudflare
```

The `--css-selector` flag is the key: pre-filter the HTML down to the relevant subtree before any token counting. The result is markdown or text, ready to be ingested by [[Markdown as Universal LLM Interchange]].

## How Mavis-Apex uses it

The integration lives in [[04 Direct-Intake MCP]] and [[03 The Custom MCP Arsenal]]. The pipeline for URL drops:

```
URL lands in intake (via .url, .webloc, .txt containing URL)
  → Scrapling MCP: scrapling.fetch with adaptive=True
    → if fetcher=Fetcher: try 1-3 times
      → if blocked: escalate to scrapling.stealthy_fetch with solve_cloudflare=True
        → if still blocked: route to cu (Computer Use) MCP for GUI scrape
          → if HTML response: MarkItDown.convert() → markdown
            → if already-markdown response: ship to intake.summarize
              → M3 classifies, links, files
```

The escalation chain is:
1. **Fetcher** — fast, cheap, no anti-bot
2. **StealthyFetcher** — slower, bypasses Cloudflare Turnstile natively
3. **DynamicFetcher** — slowest, full Chromium for JS-rendered content
4. **cu MCP** — fallback only when all programmatic scraping fails (most expensive, but unblocks anything with a GUI)

For the EA operating envelope, 95% of URL drops are Fetcher-tier. The escalation is rare but exists.

## What this is NOT

- **Not a scraper for adversarial targets.** Scrapling's README is explicit: "for educational and research purposes only." For sites with active anti-scraping legal teams (LinkedIn, Facebook, Twitter), the right tool is a third-party API or a paid proxy service. Scrapling handles the long tail of "normal" sites with anti-bot measures.
- **Not a replacement for browser automation.** For sites that genuinely require user interaction (login flows, multi-step wizards), Scrapling is the wrong tool. That's [[02 Native Execution Layers]] territory.
- **Not a server.** Scrapling is a library + CLI + MCP server (single-shot). It doesn't run as a long-lived service. For Mavis-Apex, the MCP server is the right shape — invoked when needed, not always-on.

## Connections

- [[04 Direct-Intake MCP]] — the URL drop integration
- [[Markdown as Universal LLM Interchange]] — what Scrapling hands off to
- [[03 The Custom MCP Arsenal]] — the MCP server slot
- [[02 Native Execution Layers]] — the GUI fallback for sites that block all programmatic access
- [[01 Capability Boundaries]] — the cost boundary (Fetcher < StealthyFetcher < DynamicFetcher < cu)
- [[learnings]] — `[capability]` entry on adaptive selectors
- https://github.com/D4Vinci/Scrapling — the source

## Anticipated future direction

- **Vault of adaptive signatures** — every successful adaptive extraction stores its signature in `99 _system/adaptive-signatures/`. Next time a similar site is scraped, the signature matches faster.
- **Cost-aware fetcher selection** — the intake worker tracks which fetcher succeeded for which domain, and routes new requests to the cheapest successful tier.
- **Scrapling + MarkItDown MCP composition** — `scrapling.fetch(url) → markitdown.convert_stream(html) → vault note`. The two MCPs compose cleanly; the integration is plumbing, not architecture.

---

*Seeded 2026-06-02 from Operation Omniscience Phase 1. The integration is in [[04 Direct-Intake MCP]].*
