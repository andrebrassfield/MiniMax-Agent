---
type: project
created: 2026-06-02
updated: 2026-06-02
status: design
tags: [project, mavis, architecture, mcp, design, intake, capture, multimodal, ingestion, markitdown, scrapling]
---

# 04 Direct-Intake MCP (Ingestion Engine)

> Design spec for the *Ingestion Engine* — the passive multimodal capture layer that turns anything that lands in your drop folder into a vault note. Revised 2026-06-02 during Operation Omniscience to integrate [[Markdown as Universal LLM Interchange\|MarkItDown]] (PDF/Office/Image/Audio → markdown) and [[Adaptive Selectors for Web Scraping\|Scrapling]] (URL → markdown, with anti-bot bypass). Same five-tool API surface as the v1 design; the ingestion pipeline is what changed.

## Purpose

Passive capture of multimodal context that doesn't naturally surface in a chat with Mavis — screenshots, voice memos, bookmarked links, photos of whiteboards, PDF reports, Office decks, Excel models. Today the intake path is "you tell me, I write to vault"; that misses the passive intelligence that lives in your camera roll, clipboard, saved-for-later queue, and downloads folder.

The Direct-Intake MCP watches a drop folder, processes whatever lands through the **ingestion engine** (MarkItDown for binary docs, Scrapling for URLs, M3 native for vision/audio), and writes a processed note to `00 Inbox/` with pre-suggested tags and pre-suggested wikilinks.

The principle: **show, don't describe.** When you can drop a PDF into a folder and get a vault note out the other end, the friction of "let me describe this to Mavis" disappears.

## Why custom

The generic `filesystem` MCP can watch a folder and the generic `obsidian` MCP can write a note. What M3 + the ingestion engine specifically unlocks:

- **Native vision** — no OCR pipeline, no preprocessing. Drop a screenshot, M3 sees the content directly (Apple Notes outline, Slack thread, Figma mock, error dialog). For the *text* content of an image, [[Markdown as Universal LLM Interchange\|MarkItDown]]'s `markitdown-ocr` plugin handles it via LLM-vision — same client, same model, no new dependency.
- **Native audio** — no Whisper, no ffmpeg dance. Drop a voice memo, M3 transcribes and reasons. MarkItDown's audio converter handles the *transcript* path; M3 audio handles the *understanding* path.
- **Native document parsing** — MarkItDown converts PDF, PPTX, DOCX, XLSX, EPUB, ZIP, CSV, JSON, XML, HTML, YouTube URLs to markdown in one deterministic call. The model gets markdown, which it already speaks natively. (See [[Markdown as Universal LLM Interchange]] for the principle.)
- **Native web scraping** — Scrapling fetches any URL, with adaptive element selection (selectors survive website redesigns) and native Cloudflare Turnstile bypass via `StealthyFetcher`. The HTML becomes markdown via MarkItDown's HTML converter. (See [[Adaptive Selectors for Web Scraping]] for the principle.)
- **Whole-vault in-context** — at intake time, the linker can pull the top-20 most-similar existing notes (per [[03 The Custom MCP Arsenal#MCP #1: `vault-brain`]]) and pre-suggest wikilinks with confidence scores.
- **M3-as-classifier** — the same model that processes the media also classifies it (idea vs article vs number vs pattern), saving a separate classification step.

The 40% gap: generic MCPs get bytes from A to B; this MCP gets **understanding** from A to B, and does it in the model's native units (markdown, vision, audio) instead of forcing the model to parse binary formats.

## The Ingestion Engine

The ingestion engine is a 4-stage pipeline that runs *before* the M3 reasoning call. Each stage is a deterministic primitive; the model gets called once at the end for the classification + linking step.

```
file lands in drop folder
  → Stage 1: Sniff (extension + magic bytes)
    → Stage 2: Convert to markdown (MarkItDown) OR fetch+convert (Scrapling + MarkItDown)
      → Stage 3: Optional Headroom compression (if markdown > 5K tokens)
        → Stage 4: M3 reasoning (classify, link, write note)
```

### Stage 1: Sniff

A 10-line Python function maps `path` → `(type, converter)`:

| Type | Extension(s) | Converter |
|---|---|---|
| `image` | `.jpg`, `.jpeg`, `.png`, `.heic`, `.webp`, `.tiff` | `markitdown-ocr` plugin (LLM-vision) |
| `audio` | `.wav`, `.mp3`, `.m4a`, `.ogg`, `.flac` | MarkItDown `audio-transcription` + M3 audio |
| `video` | `.mp4`, `.mov`, `.webm` | M3 video (keyframe extraction + transcript) |
| `pdf` | `.pdf` | MarkItDown `pdf` (or Azure Doc Intel for scanned) |
| `pptx` | `.pptx` | MarkItDown `pptx` (+ LLM-vision for embedded images) |
| `docx` | `.docx` | MarkItDown `docx` |
| `xlsx` | `.xlsx`, `.xls`, `.csv` | MarkItDown `xlsx` / direct CSV passthrough |
| `text` | `.txt`, `.md`, `.rtf` | Direct passthrough |
| `data` | `.json`, `.xml`, `.yaml` | Direct passthrough with structure preserved |
| `url` | `.url`, `.webloc`, or `.txt` containing only a URL | Scrapling fetch → MarkItDown HTML |
| `youtube` | URLs matching `youtube.com` / `youtu.be` | MarkItDown `youtube-transcription` |
| `epub` | `.epub` | MarkItDown `epub` |
| `zip` | `.zip` | MarkItDown iterates contents |
| `outlook` | `.msg`, `.eml` | MarkItDown `outlook` (optional extras) |

The sniff is the source of truth for routing. The downstream converter doesn't re-detect.

### Stage 2: Convert

**For documents** (PDF, Office, images, audio, EPUB, ZIP, etc.):

```python
from markitdown import MarkItDown

md = MarkItDown(
    enable_plugins=True,                  # enable markitdown-ocr
    llm_client=openai_client,             # for image descriptions + OCR
    llm_model="MiniMax/M3",
)
result = md.convert_local(path)          # narrow API: local file only
markdown = result.text_content
```

The narrow `convert_local()` is the *only* entry point. We never use `convert()` (which can fetch URLs) and we never use `convert_stream()` with untrusted streams. This is the security discipline from MarkItDown's README applied.

**For URLs** (`.url`, `.webloc`, `.txt` containing a URL):

```python
from scrapling.fetchers import StealthyFetcher, Fetcher

def fetch_url(url: str) -> str:
    # Stage 1: Try the cheap fetcher
    try:
        page = Fetcher.get(url, stealthy_headers=True)
        if page.status == 200 and not is_blocked(page):
            return page.html
    except BlockedError:
        pass

    # Stage 2: Escalate to stealthy fetcher (anti-bot bypass)
    page = StealthyFetcher.fetch(
        url,
        headless=True,
        network_idle=True,
        solve_cloudflare=True,
    )
    return page.html
```

The escalation chain (Fetcher → StealthyFetcher → DynamicFetcher → cu MCP) is the routing decision from [[Adaptive Selectors for Web Scraping]]. We start cheap, escalate only on block detection.

After fetch, the HTML goes through MarkItDown's HTML converter:

```python
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert_stream(io.BytesIO(html.encode()))
markdown = result.text_content
```

**For interactive sites** (login-walled, JS-rendered SPAs with auth), the ingestion engine falls back to `cu` MCP for a GUI scrape. This is the [[02 Native Execution Layers]] path. Rare (~5% of drops) but exists.

### Stage 3: Optional Headroom compression

If the resulting markdown is > 5K tokens, it gets routed through the [[Context Compression as First-Class Layer\|Headroom]] compression layer before the M3 reasoning call:

```python
from headroom import compress

if len(tokenize(markdown)) > 5000:
    compressed = compress(markdown, model="MiniMax/M3")
    markdown = compressed.text
    # CCR stores the original with content hash; M3 can call headroom_retrieve
```

This is the budget discipline from [[06 Token Economics & Headroom]]. The model gets dense content; the original is retrievable on demand via CCR.

### Stage 4: M3 reasoning (classify, link, file)

The M3 call takes the markdown + the file metadata + the vault-brain in-context top-20, and produces:

```typescript
{
  classification: "idea" | "article" | "pattern" | "number" | "question" | "meeting" | "link",
  confidence: number,                  // 0-1
  summary: string,                     // 1-3 sentence summary
  suggested_tags: string[],
  suggested_links: Array<{...}>,       // top-5 with confidence
  proposed_destination: string,
  rationale: string
}
```

The same model that processes the media also classifies it — this is the "M3-as-classifier" advantage. One call, one cost, two outputs (understanding + classification).

## Tool surface (unchanged from v1)

The MCP exposes the same five tools. The pipeline behind them is what changed.

```typescript
// Drop a media file for processing (called by the filesystem watcher on save)
intake.drop({
  path: string,                  // absolute path to dropped file
  type: "image" | "audio" | "video" | "url" | "pdf" | "office" | "text" | "data" | "youtube" | "epub" | "zip" | "outlook",
  hint?: string,                 // optional user-provided context
}) => {
  intake_id: string,
  status: "queued" | "processing" | "ready" | "needs-review",
  result_path?: string,
}

// Process a queued drop (called by the worker)
intake.process({
  intake_id: string
}) => {
  classification: "idea" | "article" | "pattern" | "number" | "question" | "meeting" | "link",
  confidence: number,
  summary: string,
  suggested_tags: string[],
  suggested_links: Array<{ target_path: string, relationship: string, confidence: number }>,
  proposed_destination: "00 Inbox" | "02 Notes/ideas" | "02 Notes/articles" | "02 Notes/patterns" | "02 Notes/numbers" | "02 Notes/questions",
  rationale: string
}

// Approve or reject a processed drop
intake.review({
  intake_id: string,
  decision: "approve" | "edit" | "reject",
  edits?: { classification?: string, summary?: string, tags?: string[], destination?: string }
}) => { filed_path: string, links_added: string[] }

// List pending drops
intake.list_pending({
  status?: "queued" | "processing" | "needs-review" | "all",
  limit?: number
}) => Array<{...}>

// Show what links were suggested and why
intake.explain_links({
  intake_id: string
}) => Array<{ target_path: string, target_title: string, relationship: string, confidence: number, existing_context: string }>
```

## The drop folder

```
~/Mavis-Inbox/                  # watched folder (Mavis has no fleet, so no Telegram drop)
├── images/                     # screenshots, photos, whiteboard captures
├── audio/                      # voice memos
├── video/                      # screen recordings, Looms
├── documents/                  # PDFs, Office files, ebooks
├── data/                       # CSV, JSON, XML, YAML
├── links/                      # .url files, .webloc, or just text files containing URLs
└── text/                       # raw text snippets copied from anywhere
```

Watcher: a small daemon (the `intake` server) using `fsevents` (macOS native). On file-write-close, it triggers `intake.drop` and queues for processing. File names get a timestamp prefix to avoid collisions.

## Auto vs human review (unchanged)

The line that matters: **what gets filed silently vs what waits for human eyes**.

**Auto-file (confidence ≥ 0.85, unambiguous type)**:
- Articles (clear external content, single topic)
- Numbers (specific data points)
- Patterns (explicit "this is a pattern" framing)

**Needs review (default)**:
- Ideas (subjective — does this earn a permanent note?)
- Questions (open — should it become a permanent question or stay ephemeral?)
- Meetings (high-stakes content; misclassification is expensive)
- Low confidence (any of the above below 0.85)

**Always review**:
- Anything containing PII, credentials, financial data (auto-redact before writing, mark for review)
- Anything that mentions a person not yet in the vault
- Voice memos (because tone matters and audio → text loses signal)

## The auto-redaction rule (MarkItDown's security discipline)

MarkItDown's README is explicit about I/O privilege: it runs with the process's privileges, can fetch any URL, can read any local file. The discipline: **never let untrusted input reach a permissive API.**

For the intake engine:

1. **URL drop validation** — before calling Scrapling, validate the URL:
   - Block `localhost`, `127.0.0.0/8`, `169.254.0.0/16` (AWS metadata), `::1`
   - Block `file://`, `gopher://`, `ftp://`
   - Allow only `http://`, `https://`
   - Resolve DNS and re-check (DNS rebinding defense)
2. **File path validation** — before calling `convert_local()`, verify the path is under `~/Mavis-Inbox/`. Reject paths that escape (e.g., `../../etc/passwd`).
3. **File size cap** — 100MB hard limit. Larger files go to `00 Inbox/over-size/` for manual review.
4. **MIME re-check** — verify the file's actual content type matches the extension. Disagreement → quarantine.

These checks live in the `intake.drop` MCP tool, before any I/O happens.

## The intake-log note format (unchanged from v1)

Every drop creates two artifacts: the processed note (in destination or inbox) and an intake-log entry (in `99 _system/intake-log/yyyy-mm-drop-NNN.md`).

```markdown
---
type: intake-log
intake_id: 2026-06-02-drop-001
dropped_at: 2026-06-02T09:15:00
source_path: ~/Mavis-Inbox/documents/Q2-board-update.pdf
type: pdf
ingestion_engine: markitdown[pdf]+headroom
classification: article
confidence: 0.91
filed_to: 02 Notes/articles/
status: ready
---

## Source
PDF, 24 pages, "Q2 2026 Board Update" from Acme Corp.

## Markdown rendering
<full markdown text from MarkItDown.convert_local()>

## M3 summary
The deck covers Q2 revenue ($4.2M, +18% QoQ), the new enterprise tier launch (12 customers in pipeline), and a fundraising update (Series B target $30M, lead term sheet from Sequoia). Three open risks called out: cloud cost overrun, key hire attrition, and a regulatory question on EU data residency.

## Suggested tags
[[board-update]] [[q2-2026]] [[revenue]] [[series-b]]

## Suggested links
- [[M3 Eval Lab]] (confidence 0.91) — the project this thread is about
- [[Long-Horizon Patterns]] (confidence 0.74) — relevant pattern
- [[M3 Bypass Hypothesis]] (confidence 0.62) — possibly relevant, lower confidence

## Disposition
Status: ready (confidence 0.91, article classification unambiguous)
Compression: 4,200 → 1,800 tokens via Headroom CodeCompressor
```

This is the artifact. The human (or the daily-brief workflow) can read it in 15 seconds, approve / edit / reject. Approval writes the final note to its destination with the right wikilinks applied.

## Avoiding the inbox-fill problem (unchanged)

The graveyard of every "passive capture" system is an inbox that fills faster than it empties. The defenses (carried over from v1):

1. **Hard confidence floor.** Below 0.85, the file goes to `00 Inbox/`, not the permanent folder. The inbox has a daily-brief.
2. **Dedup by content fingerprint.** SHA-256 of the file + a semantic fingerprint of the M3 summary. If the same file (or a near-duplicate summary) drops twice, the second is rejected with a link to the first.
3. **Batch processing.** The worker processes in batches of 5 (or 10), not one-at-a-time. This lets the linker cross-reference within a batch (two screenshots from the same moment get considered together).
4. **Rate cap.** Max 20 drops processed per hour. If more land, the queue stalls and the user gets a notification.
5. **Tag garbage collection.** Suggested tags are checked against the existing tag set (`/^#\w+/$`). New tags require review.
6. **The "where are my notes" dashboard.** `99 _system/dashboards/Intake Review.md` — a Dataview of all `intake-log/` entries with status.

New defenses added in v2:

7. **Adaptive selector reuse.** When a Scrapling fetch succeeds on a domain, the adaptive selector signature is cached. Next fetch on the same domain uses the cached signature first, falls back to fresh adaptive learning on miss. (See [[Adaptive Selectors for Web Scraping]].)
8. **Compression budget.** A drop that produces > 50K tokens of markdown is compressed via Headroom before the M3 call. This protects the budget. The compression ratio is logged in the intake-log entry.

## Cost (revised)

The cost structure changed with the ingestion engine:

- **Image processing** — MarkItDown's `markitdown-ocr` plugin: ~$0.005 per image (LLM-vision call). M3 vision at intake time: bundled, no extra cost.
- **Audio transcription** — MarkItDown's `audio-transcription`: ~$0.001/minute. M3 audio: bundled.
- **PDF/Office conversion** — MarkItDown: free, host-side, ~50ms-2s depending on size.
- **URL fetch** — Scrapling: free, host-side. StealthyFetcher on a Cloudflare-protected site: ~3s browser time. No API cost.
- **Headroom compression** — local, free. CCR storage: ~1KB per drop, trivial.
- **M3 classification + linking** — one M3 call per drop, ~$0.005-0.02 depending on compressed input size.
- **Storage** — original files + processed notes. ~500KB per image, ~1MB per audio minute, ~50-200KB per processed note (markdown). 100 drops/week ≈ 300MB/week. Trivial.

Per drop (typical mix): ~$0.01-0.02 (mostly M3). Per week (20 drops): $0.20-0.40. The Headroom compression reduces the M3 portion by 50-80% on dense content. The value is in the time saved on "let me describe this to Mavis" + the files Mavis can now read natively that it couldn't before.

## What this is NOT

- **Not a replacement for active capture.** When you have a specific question or task, you tell Mavis. The intake is for the *passive* context you would otherwise forget.
- **Not magic.** M3's classification is only as good as the file content. A blurry photo of a whiteboard is a blurry photo of a whiteboard. A scanned PDF with handwritten notes is still a scanned PDF.
- **Not autonomous filing.** The auto-file threshold (0.85) is conservative. Most drops go to review. That's the point.
- **Not a fleet bridge.** Mavis is isolated. There's no Telegram drop, no Slack drop — just a local folder. Andre's design choice, not a limitation.
- **Not a scraper for adversarial sites.** Scrapling handles the long tail of "normal" sites with anti-bot. For LinkedIn, Facebook, Twitter with active legal teams, the right tool is a paid proxy service or a third-party API. Don't pretend Scrapling is the answer there.
- **Not a HostileDoc reader.** MarkItDown is permission-preserving. A malicious PDF that exploits a PDF parser is still a malicious PDF. The auto-redaction + size cap + MIME re-check are defenses, not guarantees. Quarantine the suspicious, don't try to read them.

## The skill layer (per [[Skill Library Architecture]])

The Direct-Intake MCP is the composition of three skills, each in its own folder under `99 _system/skills/`:

| Skill | Purpose | Source |
|---|---|---|
| `intake` | The MCP server, watcher, queue, auto-file logic | new design |
| `intake-markitdown` | The PDF/Office/Image/Audio → markdown converter | [[Markdown as Universal LLM Interchange]] |
| `intake-scrapling` | The URL → HTML → markdown fetcher with anti-bot escalation | [[Adaptive Selectors for Web Scraping]] |
| `intake-headroom` | The compression layer for high-volume drops | [[Context Compression as First-Class Layer]] |

The MCP is the *composition*. Each skill is independently testable. The validation script (`validate_skills.py` style) runs on each skill before the composition is allowed to load.

## Connections

- [[00 Overview]] — the project hub
- [[03 The Custom MCP Arsenal]] — the broader 5-MCP design space; this extends the arsenal
- [[MCP #1: `vault-brain`]] — the link-suggestion primitive this MCP uses for `intake.suggest_links`
- [[MCP #5: `self-model-card`]] — companion: intake is *external* self-awareness (what came in), self-model-card is *internal* self-awareness (what I am)
- [[M3 Edge]] — the capability shift (native multimodal) this design exploits
- [[02 Native Execution Layers]] — the GUI fallback for sites that block all programmatic scraping
- [[Mavis EA Workflow]] — current workflow that would consume this
- [[06 Token Economics & Headroom]] — the compression layer this design depends on for budget
- [[Markdown as Universal LLM Interchange]] — the MarkItDown integration
- [[Adaptive Selectors for Web Scraping]] — the Scrapling integration
- [[Context Compression as First-Class Layer]] — the Headroom integration
- [[Skill Library Architecture]] — the skill structure this MCP composes from
- [[state-of-mavis]] — the MOC that should record when this is built + operational
- [[learnings]] — `[capability]` entries on native multimodal, ingestion, anti-bot scraping

---

*Design doc v2 — 2026-06-02. v1 was 2026-06-02. The v2 update integrates MarkItDown + Scrapling + Headroom into the ingestion engine. Build is straightforward once the design is right — pending greenlight.*
