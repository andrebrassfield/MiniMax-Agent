"""
scrape.py — scrapling adapter.

The 4-fetcher escalation chain:
  1. Fetcher       — fast, TLS fingerprint, ~100ms
  2. StealthyFetcher — anti-bot bypass, Cloudflare Turnstile, ~2-5s
  3. DynamicFetcher — full Chromium, JS-rendered, ~3-10s
  4. (fallback)    — return the raw HTML; the caller can decide to escalate to cu MCP

For 95% of drops the Fetcher is enough. We escalate only on block detection.

The output is HTML. The caller (the ingestion engine) pipes the HTML through
markitdown's HTML converter to get clean markdown.
"""

from __future__ import annotations

import logging
import re
from typing import Optional
from urllib.parse import urlparse

log = logging.getLogger(__name__)


class ScrapeError(RuntimeError):
    """scrapling could not fetch the URL."""


# Block-detection patterns: Cloudflare interstitial, generic 403/503, etc.
BLOCK_PATTERNS = [
    re.compile(r"checking your browser before accessing", re.IGNORECASE),
    re.compile(r"cloudflare", re.IGNORECASE),
    re.compile(r"please complete the security check", re.IGNORECASE),
    re.compile(r"access denied", re.IGNORECASE),
    re.compile(r"please enable cookies", re.IGNORECASE),
    re.compile(r"<title>\s*Just a Moment\.\.\.\s*</title>", re.IGNORECASE),
]


def is_blocked(html: str, status: int) -> bool:
    """Detect if the response was blocked (Cloudflare interstitial, etc.)."""
    if status in (403, 503, 429):
        return True
    for pat in BLOCK_PATTERNS:
        if pat.search(html[:5000]):  # only check the first 5K
            return True
    return False


def fetch(
    url: str,
    *,
    escalate: bool = True,
    timeout: int = 30,
    use_stealthy: bool = False,
) -> str:
    """Fetch a URL, return raw HTML.

    Args:
        url: The URL to fetch.
        escalate: If True and the cheap fetcher is blocked, try the
            StealthyFetcher. Default True.
        timeout: Request timeout in seconds.
        use_stealthy: If True, skip the cheap fetcher and go straight to
            StealthyFetcher. Set this when you already know the site has
            anti-bot measures (e.g., the URL host is on a known-protected list).

    Returns:
        Raw HTML string.

    Raises:
        ScrapeError: If all attempts fail.
    """
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ScrapeError(f"invalid URL: {url!r}")

    # First attempt: cheap Fetcher
    if not use_stealthy:
        try:
            html = _fetch_cheap(url, timeout=timeout)
            # Block detection
            if not is_blocked(html, 200):
                return html
            log.info("Fetcher blocked on %s, escalating to StealthyFetcher", url)
        except Exception as e:
            log.warning("Fetcher failed on %s: %s", url, e)
            if not escalate:
                raise ScrapeError(f"fetcher failed and escalation disabled: {e}") from e

    # Escalation: StealthyFetcher (anti-bot bypass)
    if escalate or use_stealthy:
        try:
            return _fetch_stealthy(url, timeout=timeout)
        except Exception as e:
            log.exception("StealthyFetcher failed on %s", url)
            raise ScrapeError(f"all scrapling fetchers failed on {url}: {e}") from e

    raise ScrapeError(f"no fetcher succeeded on {url}")


def _fetch_cheap(url: str, timeout: int) -> str:
    """The Fetcher — fast, TLS-fingerprint, no browser."""
    try:
        from scrapling.fetchers import Fetcher
    except ImportError as e:
        raise ScrapeError(f"scrapling not installed: pip install scrapling ({e})")

    page = Fetcher.get(
        url,
        stealthy_headers=True,
        timeout=timeout,
        follow_redirects=True,
    )
    # Scrapling's Response has the HTML in `html_content` (not `html`).
    if hasattr(page, "html_content"):
        return page.html_content
    if hasattr(page, "text"):
        return page.text
    return str(page)


def _fetch_stealthy(url: str, timeout: int) -> str:
    """The StealthyFetcher — anti-bot bypass, real browser. Slower."""
    try:
        from scrapling.fetchers import StealthyFetcher
    except ImportError as e:
        raise ScrapeError(f"scrapling StealthyFetcher not available: {e}")

    # StealthyFetcher needs browsers installed via `scrapling install`.
    # If the user hasn't run that, this will fail with a clear error.
    try:
        page = StealthyFetcher.fetch(
            url,
            headless=True,
            network_idle=True,
            solve_cloudflare=True,
            timeout=timeout * 1000,  # scrapling takes ms
        )
    except Exception as e:
        if "browser" in str(e).lower() or "playwright" in str(e).lower():
            raise ScrapeError(
                f"StealthyFetcher needs browser binaries. "
                f"Run `scrapling install` to download them. ({e})"
            ) from e
        raise
    if hasattr(page, "html_content"):
        return page.html_content
    if hasattr(page, "text"):
        return page.text
    return str(page)
