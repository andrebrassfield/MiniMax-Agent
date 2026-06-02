# direct-intake MCP

> The Universal Ingestion Engine for Mavis. Esalen posture: thin deterministic layer — fetch, convert, compress. The model (M3) does the understanding.

Per [[04 Direct-Intake MCP]] design doc (v2). Sits at the **Ingestion Layer** of the [[Mavis-Apex-Map.canvas|Mavis-Apex-Map]] — between the host OS and the execution layer. Catches content from the drop folder or URL drops, converts to clean markdown, and hands it to M3 for classification + linking.

## What this is

A 4-stage ingestion pipeline:

```
file or URL
  → Sniff  (type detection + security validation)
    → Convert  (markitdown for files, scrapling for URLs)
      → Compress  (Headroom-style deterministic, CCR-reversible)
        → M3 call (classification + linking + filing)  [out of scope here]
```

The Python code is stages 1-3. Stage 4 is the model's job.

## File layout

```
99 _system/mcps/direct-intake/
├── direct_intake.py          # the main MCP server + CLI
├── intake/
│   ├── __init__.py
│   ├── sniff.py              # type detection + security boundaries
│   ├── convert.py            # markitdown adapter
│   ├── scrape.py             # scrapling adapter (4-fetcher escalation)
│   ├── compress.py           # Headroom-style compression + CCR
│   └── store.py              # intake-log persistence
├── tests/
│   ├── test_sniff.py         # security tests (FIRST priority)
│   ├── test_compress.py      # compression + CCR tests
│   └── test_pipeline.py      # end-to-end with real URLs
├── requirements.txt
├── README.md                 # this file
└── .venv-direct-intake/      # local venv (NOT tracked)
```

## Five MCP tools

Per the [[04 Direct-Intake MCP#Tool surface]] design:

| Tool | Purpose |
|---|---|
| `intake.drop` | Register a file/URL for ingestion (sniff + queue) |
| `intake.process` | Run the full pipeline (fetch + convert + compress) |
| `intake.review` | Approve / edit / reject a processed drop |
| `intake.list` | List pending drops, optionally filtered by status |
| `intake.explain` | Show suggested links + tags for a drop |

## Setup

```bash
cd 99 _system/mcps/direct-intake
uv venv --python 3.12 .venv-direct-intake
source .venv-direct-intake/bin/activate
uv pip install -r requirements.txt
```

## Usage

### CLI (one-shot)

```bash
# Ingest a URL — fetch via Scrapling, convert via markitdown, compress
python3 direct_intake.py --url "https://en.wikipedia.org/wiki/Markdown"

# Ingest a local PDF/DOCX/XLSX
python3 direct_intake.py --file /path/to/document.pdf

# Aggressive compression (also strip stopwords from prose)
python3 direct_intake.py --url "..." --aggressive

# Write the markdown to a file
python3 direct_intake.py --url "..." --out /tmp/rendered.md
```

### MCP server (stdio)

```bash
python3 direct_intake.py --serve
```

Wire into your MCP client config:

```json
{
  "mcpServers": {
    "direct-intake": {
      "command": "python3",
      "args": ["/path/to/99 _system/mcps/direct-intake/direct_intake.py", "--serve"]
    }
  }
}
```

### Tests

```bash
source .venv-direct-intake/bin/activate
pytest tests/                              # all tests
pytest tests/test_sniff.py -v              # security tests only (fast)
pytest tests/ -m integration -v            # requires network
```

## Security (the part that matters most)

The Sniff is the I/O boundary. It enforces:

1. **URL scheme allowlist** — only `http` and `https`. No `file://`, no `gopher://`, no `ftp://`.
2. **Host blocklist** — no `localhost`, no `127.0.0.1`, no `169.254.169.254` (cloud metadata service), no private IP literals.
3. **Path-traversal defense** — file paths must resolve under the drop root.
4. **File-size cap** — 100MB hard limit. Larger files go to `00 Inbox/over-size/` for manual review.
5. **Narrow markitdown API** — only `convert_local()` and `convert_stream()`. Never the permissive `convert()` (which can fetch URLs).

Every test in `test_sniff.py` exercises one of these. The test order is intentional — security tests run first.

## Compression (the budget multiplier)

Three algorithms:

| Algorithm | What | When |
|---|---|---|
| `markdown_clean` | Strip redundant markdown, HTML leftovers, bold on single chars | Always |
| `whitespace_squash` | Normalize line endings, collapse horizontal whitespace | Always |
| `stopword_strip` | Remove English stopwords from prose (not code/JSON) | Aggressive mode only |

The full pipeline (`compress()`) returns a `CompressedBlock` with the compressed text + a CCR hash for retrieval. The original is kept in the process-local `CCRStore`; the LLM can call `headroom_retrieve(hash)` to get it back.

For the canonical CCR + Headroom design rationale, see [[06 Token Economics & Headroom]].

## What this is NOT

- **Not an LLM caller.** The Python never makes an LLM call. M3 is the only LLM in the loop, called by the Mavis runtime after this server hands back the markdown.
- **Not a classifier.** Classification is the model's job. The server just prepares the content.
- **Not a vector database.** Embeddings happen in M3 at query time.
- **Not a caged state machine.** The pipeline is 4 thin functions. Each can be tested independently. The model decides what to do with the output.
- **Not a fully autonomous filer.** Most drops end up in `00 Inbox/` for human review. The auto-file threshold is the model's, not the server's.

## Connections

- [[04 Direct-Intake MCP]] — the design spec this implements
- [[Markdown as Universal LLM Interchange]] — the markitdown rationale
- [[Adaptive Selectors for Web Scraping]] — the scrapling rationale
- [[Context Compression as First-Class Layer]] — the compression rationale
- [[06 Token Economics & Headroom]] — the CCR design
- [[03 The Custom MCP Arsenal]] — where this fits in the 5-MCP design
- [[Mavis-Apex-Map.canvas|Mavis-Apex-Map]] — the Ingestion Layer
