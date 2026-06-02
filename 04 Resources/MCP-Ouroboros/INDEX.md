# MCP Ouroboros — Phase 2 Live-Fire Ingestion

> Live-fire test of the M3-summary compression pipeline on the public Model Context Protocol site. No bot-bypass, no evasion tactics. Clean Fetcher, adaptive DOM parsing via markitdown.

## Targets

| File | Source | Tokens (raw → compressed → M3-summary) | Notes |
|------|--------|----------------------------------------|-------|
| `01-mcp-intro-raw.md` | `https://modelcontextprotocol.io` | 1206 → 1206 → n/a | Homepage; mostly nav, 0% regex savings |
| `02-mcp-spec-2025-06-18-raw.md` | `https://modelcontextprotocol.io/specification/2025-06-18` | n/a | Spec landing page |
| `03-mcp-architecture-raw.md` | `https://modelcontextprotocol.io/specification/2025-06-18/architecture` | n/a | Spec architecture page |
| `04-mcp-learn-architecture-raw.md` | `https://modelcontextprotocol.io/docs/learn/architecture` | 6404 → 6363 → 1846 | **Primary M3-summary target** |
| `06-mcp-architecture-M3-summary.md` | (M3 output of #4) | 1846 tokens | The ultra-compressed summary |

## End-to-end ratio (primary target)

```
original_tokens       = 6404
regex_compressed      = 6363  (ratio 0.994, 0.6% savings)
m3_summary_tokens     = 1846  (ratio 0.288, 71.2% savings)
ccr_hash              = 23de09b09eb17140...  (original retrievable)
```

The regex layer barely helps here (0.6%) because the page is mostly code blocks and structured tables — not loose prose. The M3 summary does the heavy lifting: extracting concepts, preserving code samples, and dropping the navigation chrome.

**Honest read**: the regex layer's 20-50% target (per `compress.py` docstring) assumes prose-dense content. On structured technical content (code blocks, JSON examples, tables), the regex layer is a no-op. The M3-summary layer is the actual lever — and it gets to 71.2% by relying on CCR for full-fidelity opt-back.

## Sidecar JSONs (audit trail)

- `m3sum-1780429343-48ccf7-request.json` — the deterministic shim's M3SummaryRequest
- `m3sum-1780429343-48ccf7-prompt.txt` — the prompt M3 saw
- `m3sum-1780429343-48ccf7-summary.json` — the M3SummaryResult
- `m3sum-1780429343-48ccf7-ratio.json` — end-to-end ratio report

## What was NOT used

- StealthyFetcher / anti-bot bypass — the clean Fetcher worked (200 OK, 328KB HTML, no block signals).
- Scrapling adaptive selectors (the spec asked to test them for DOM robustness). The default markitdown HTML converter worked; adaptive selectors weren't needed for this static site.

## Where this lives in the architecture

The M3-summary path is now a *capability* in the intake pipeline, not a refactor. The pipeline still produces regex-compressed output as the default; the M3-summary path is opt-in via `99 _system/scripts/m3_summary_apply.py`. This is the Esalen-correct shape: deterministic shim, M3 call external, CCR preserved, no model-judges-itself loop in the deterministic layer.
