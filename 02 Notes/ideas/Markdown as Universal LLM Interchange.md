---
type: idea
created: 2026-06-02
tags: [idea, ingestion, markitdown, llm, markdown, ocr, multimodal, mavis-apex]
source: https://github.com/microsoft/markitdown
---

# Markdown as Universal LLM Interchange

> The single most important mental model from Operation Omniscience's monsoon: every structured document that lands in your vault should become markdown *before* the model sees it. The model already speaks markdown — it doesn't need a PDF parser, an XLSX parser, or a Word parser in its head.

## The principle

**Markdown is the lowest-common-denominator format that LLMs natively understand.** Not JSON (loses semantic structure), not plain text (loses structure entirely), not HTML (token-heavy, brittle, model has to parse). Markdown is:

- **Close to plain text** — minimal markup overhead
- **Structurally faithful** — headings, lists, tables, links all survive
- **Token-efficient** — far cheaper than JSON or HTML for the same content
- **Universally trained-on** — every frontier model has seen massive amounts of markdown and "speaks" it fluently

Microsoft's MarkItDown takes this seriously: it's a *narrow* utility (one job: file → markdown) that does that job well across 10+ input formats. The README states the goal explicitly:

> Markdown is extremely close to plain text, with minimal markup or formatting, but still provides a way to represent important document structure. Mainstream LLMs, such as OpenAI's GPT-4o, natively "speak" Markdown, and often incorporate Markdown into their responses unprompted. This suggests that they have been trained on vast amounts of Markdown-formatted text, and understand it well.

## The agent engineering principle

**Don't bring the document's structure into the model — bring the document's *content* into the model in the model's native language.**

Concretely: instead of feeding the model a PDF binary and asking it to "parse this," feed it the markdown rendering and let the model focus on *understanding*. The parser step is a deterministic, host-side operation. The understanding step is what the model is for.

This is the same shape as the rest of the Mavis-Apex design philosophy:
- **Native > wrapper** ([[M3 Edge]]) — if M3 can see it natively, don't preprocess
- **The model is the working memory** ([[00 Overview]]) — keep the prompt in model-native units
- **Tool surface area = audit surface area** — one well-defined conversion tool, not 10 parsers

## What MarkItDown actually supports

Out of the box (`pip install 'markitdown[all]'`):

| Format | Strategy | Notes |
|---|---|---|
| PDF | Layout extraction (built-in) or Azure Document Intelligence / Azure Content Understanding | Optional cloud tier for scanned/handwritten |
| PowerPoint (`.pptx`) | Slide-by-slide with text + structure + (optional) LLM-vision image descriptions | `llm_client` + `llm_model` for image content |
| Word (`.docx`) | OpenXML extraction | Native Python |
| Excel (`.xlsx`, `.xls`) | Sheet-by-sheet, table-preserving | |
| Images (`.jpg`, `.png`, ...) | EXIF metadata + LLM-vision OCR via plugin | `markitdown-ocr` plugin |
| Audio (`.wav`, `.mp3`) | EXIF metadata + speech transcription | Optional `audio-transcription` extras |
| HTML | Readability-style extraction | Or use [[Scrapling — Adaptive Selectors for Web Scraping]] upstream |
| CSV / JSON / XML | Direct passthrough with structure preserved | |
| ZIP | Iterate contents, convert each | |
| YouTube URLs | Fetch transcript | Optional `youtube-transcription` |
| EPub | EPub → markdown | |
| Outlook messages | Via `markitdown[outlook]` | |

The plugin system is the key extension seam. `markitdown-ocr` is the canonical example: a separate package that hooks into the convert pipeline and uses an LLM client to OCR embedded images. **No new ML libraries or binary dependencies required** — it uses the same `llm_client` pattern MarkItDown already has.

## Security: the part people skip

The README's "Security Considerations" section is the part most agents ignore and most attacks exploit:

> MarkItDown performs I/O with the privileges of the current process. Like `open()` or `requests.get()`, it will access resources that the process itself can access. Sanitize your inputs in untrusted environments, and call the narrowest `convert_*` function needed for your use case (e.g., `convert_stream()`, or `convert_local()`).

The principle: `convert()` is intentionally permissive (handles local files, remote URIs, byte streams). If your code only needs to read local files, call `convert_local()`. If you need more control over URI fetching, fetch the URL yourself and pass the response to `convert_response()`. **For maximum control, open a stream and call `convert_stream()`.**

For [[04 Direct-Intake MCP]] this matters: when a URL drop lands in the inbox, we must pre-validate the URL (block private IPs, metadata-service IPs, link-local addresses) before handing it to anything that performs I/O. MarkItDown's `convert()` would happily fetch `http://169.254.169.254/` if asked.

## How Mavis-Apex uses it

The integration lives in the [[04 Direct-Intake MCP]] design. The ingestion pipeline becomes:

```
file lands in drop folder
  → file-type sniff (extension + magic bytes)
    → if PDF/Office/Image/Audio:  MarkItDown.convert_local() → markdown
      → if URL (.url, .webloc, .txt with URL): Scrapling.StealthyFetcher.fetch() → HTML → MarkItDown HTML converter
        → markdown output + EXIF/audio transcript → M3 vision (for screenshots) or M3 audio (for voice)
          → classification: M3 picks one of the CHIEF types
            → link suggestions: M3 generates top-5 candidate links using vault-brain
              → write to 00 Inbox/ or destination folder
```

The narrow `convert_local()` and `convert_stream()` are the only entry points we expose in the MCP. URL drops never go through `convert()` because URL handling is Scrapling's job, not MarkItDown's.

## What this is NOT

- **Not a replacement for the LLM reading the image.** A PDF with a chart on page 4 is converted to markdown, but the chart is *not* converted. For visual content, the markdown text is the index, and M3 vision still sees the original. MarkItDown is the *text* path; M3 is the *visual* path.
- **Not OCR for visual content.** `markitdown-ocr` exists, but for a screenshot of a Slack thread, M3 vision is still better than OCR → LLM. The principle holds: native > wrapper, vision > OCR.
- **Not a vectorization tool.** MarkItDown is the *input* side. Vault-brain embedding (FTS5 + vector) is the *index* side. They don't replace each other.

## Cost economics

- **MarkItDown convert**: free, host-side. ~50ms-2s depending on file size. PDF: ~1s/MB. PPTX: ~0.5s/MB.
- **Plugin LLM-vision OCR**: ~$0.005 per image (matches M3 vision cost).
- **No API call to convert**: deterministic, can run on local CPU.

This is a free preprocessing step that *reduces* the M3 call's token cost. A 50-page PDF → markdown is typically 5-10K tokens, vs the raw PDF binary or the 50 pages of OCR'd text at 30K+ tokens.

## Connections

- [[04 Direct-Intake MCP]] — the primary integration surface
- [[Scrapling — Adaptive Selectors for Web Scraping]] — handles the URL drop path before MarkItDown
- [[M3 Edge]] — the native multimodal context that makes this work
- [[00 Overview]] — the "native > wrapper" principle
- [[01 Capability Boundaries]] — the ingestion cost curve this design lives on
- [[learnings]] — `[capability]` entry on Markdown as LLM interchange
- https://github.com/microsoft/markitdown — the source

## Anticipated future direction

The plugin ecosystem will grow. Watch for:
- **markitdown-screenshot** — screenshot → structured UI extraction (using M3 vision)
- **markitdown-tweet** — tweet URL → canonical markdown with thread, quote-tweets, and replies
- **markitdown-podcast** — RSS feed → transcript + chapters

Each is a thin Python package with a single `convert()` function that produces markdown. The pattern scales.

---

*Seeded 2026-06-02 from Operation Omniscience Phase 1 (5-repo knowledge monsoon). The ingestion layer in [[04 Direct-Intake MCP]] integrates this design.*
