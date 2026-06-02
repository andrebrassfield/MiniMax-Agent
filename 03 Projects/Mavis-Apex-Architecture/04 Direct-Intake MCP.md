---
type: project
created: 2026-06-02
status: design
tags: [project, mavis, architecture, mcp, design, intake, capture, multimodal]
---

# 04 Direct-Intake MCP

> Design spec. No build greenlight yet — written while the M3-native multimodal context from Operation Apex is fresh. Same shape as the five MCPs in [[03 The Custom MCP Arsenal]].

## Purpose

Passive capture of multimodal context that doesn't naturally surface in a chat with Mavis — screenshots, voice memos, bookmarked links, photos of whiteboards. Today the intake path is "you tell me, I write to vault"; that misses the passive intelligence that lives in your camera roll, clipboard, and saved-for-later queue. The Direct-Intake MCP watches a drop folder, processes whatever lands (M3-native vision on images, M3-native audio on voice memos, fetch+extract on links), and writes a processed note to `00 Inbox/` with pre-suggested tags and pre-suggested wikilinks.

The principle: **show, don't describe.** When you can drop a screenshot into a folder and get a vault note out the other end, the friction of "let me describe this to Mavis" disappears.

## Why custom

The generic `filesystem` MCP can watch a folder and the generic `obsidian` MCP can write a note. What M3 specifically unlocks:

- **Native vision** — no OCR pipeline, no preprocessing. Drop a screenshot, M3 sees the content directly (Apple Notes outline, Slack thread, Figma mock, error dialog).
- **Native audio** — no Whisper, no ffmpeg dance. Drop a voice memo, M3 transcribes and reasons.
- **Whole-vault in-context** — at intake time, the linker can pull the top-20 most-similar existing notes (per [[03 The Custom MCP Arsenal#MCP #1: `vault-brain`]]) and pre-suggest wikilinks with confidence scores.
- **M3-as-classifier** — the same model that processes the media also classifies it (idea vs article vs number vs pattern), saving a separate classification step.

The 40% gap: generic MCPs get bytes from A to B; this MCP gets **understanding** from A to B.

## Tool surface

```typescript
// Drop a media file for processing (called by the filesystem watcher on save)
intake.drop({
  path: string,                  // absolute path to dropped file
  type: "image" | "audio" | "video" | "url" | "text",
  hint?: string,                 // optional user-provided context
}) => {
  intake_id: string,             // unique ID for this drop
  status: "queued" | "processing" | "ready" | "needs-review",
  result_path?: string,          // path to the processed note if status=ready
}

// Process a queued drop (called by the worker)
intake.process({
  intake_id: string
}) => {
  classification: "idea" | "article" | "pattern" | "number" | "question" | "meeting" | "link",
  confidence: number,            // 0-1
  summary: string,               // 1-3 sentence summary
  suggested_tags: string[],
  suggested_links: Array<{
    target_path: string,
    relationship: string,
    confidence: number           // 0-1
  }>,
  proposed_destination: "00 Inbox" | "02 Notes/ideas" | "02 Notes/articles" | "02 Notes/patterns" | "02 Notes/numbers" | "02 Notes/questions",
  rationale: string              // why this classification + destination
}

// Approve or reject a processed drop
intake.review({
  intake_id: string,
  decision: "approve" | "edit" | "reject",
  edits?: {                      // optional overrides
    classification?: string,
    summary?: string,
    tags?: string[],
    destination?: string
  }
}) => {
  filed_path: string,            // where the note was filed
  links_added: string[]
}

// List pending drops
intake.list_pending({
  status?: "queued" | "processing" | "needs-review" | "all",
  limit?: number
}) => Array<{
  intake_id: string,
  path: string,
  type: string,
  dropped_at: string,
  status: string,
  summary?: string
}>

// Show what links were suggested and why
intake.explain_links({
  intake_id: string
}) => Array<{
  target_path: string,
  target_title: string,
  relationship: string,
  confidence: number,
  existing_context: string       // 1-2 sentences of the matched note for the user to confirm relevance
}>
```

## Why custom (the 40% gap, restated)

A filesystem-watcher → OCR-pipeline → classifier → vault-writer chain can be built from generic MCPs. The reason this earns a custom slot:

1. **No OCR.** M3 reads the image directly. A chat-thread screenshot → M3 sees "yeah, that's Andre arguing with Sam about the contract clause, the Open question is the indemnity cap." A generic pipeline gets text out, not the *understanding*.
2. **Multimodal fusion.** A voice memo that's actually a screenshot of text spoken aloud gets processed correctly (audio → transcript, then image-aware). A "voice memo while looking at a doc" gets both streams.
3. **M3 already has the vault in context.** When M3 is also the linker, the link suggestions are consistent with how the model already reasons about the vault, not a separate semantic-search result that doesn't share context.
4. **M3 already knows the linking rules.** A separate classifier would re-derive "this is an idea, not an article" from scratch. M3 already knows the CHIEF structure.

## The implementation hint

### The drop folder

```
~/Mavis-Inbox/                  # watched folder (Mavis has no fleet, so no Telegram drop)
├── images/                     # screenshots, photos, whiteboard captures
├── audio/                      # voice memos
├── video/                      # screen recordings, Looms
├── links/                      # .url files, .webloc, or just text files containing URLs
└── text/                       # raw text snippets copied from anywhere
```

Watcher: a small daemon (the `intake` server) using `fsevents` (macOS native). On file-write-close, it triggers `intake.drop` and queues for processing. File names get a timestamp prefix to avoid collisions.

### The processing pipeline

```
file lands in drop folder
  → watcher calls intake.drop({path, type})
    → worker picks up the queue
      → for image: M3 vision (no preprocessing)
      → for audio: M3 audio (transcribe + analyze)
      → for video: M3 video (extract keyframes + transcribe)
      → for link: fetch + defuddle + M3 summarize
      → classification: M3 picks one of the 7 types (idea, article, pattern, etc.)
      → link suggestions: M3 generates top-5 candidate links using vault-brain in-context
      → write a temporary note to 00 Inbox/ with frontmatter: classification, confidence, suggested_tags, suggested_links
      → if confidence ≥ 0.85 AND classification is unambiguous: status=ready, file in proposed destination
      → else: status=needs-review, file in 00 Inbox/ with [[REVIEW]] tag
    → notification to user (optional: daily-brief, or a separate morning review)
```

### Auto vs human review — the schema decision

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

The threshold is tunable, and the audit trail (every drop's classification + confidence) is itself a permanent note in `99 _system/intake-log/` for later review.

### Avoiding the inbox-fill problem

The graveyard of every "passive capture" system is an inbox that fills faster than it empties. The defenses:

1. **Hard confidence floor.** Below 0.85, the file goes to `00 Inbox/`, not the permanent folder. The inbox has a daily-brief.
2. **Dedup by content fingerprint.** SHA-256 of the file + a semantic fingerprint of the M3 summary. If the same file (or a near-duplicate summary) drops twice, the second is rejected with a link to the first.
3. **Batch processing.** The worker processes in batches of 5 (or 10), not one-at-a-time. This lets the linker cross-reference within a batch (two screenshots from the same moment get considered together).
4. **Rate cap.** Max 20 drops processed per hour. If more land, the queue stalls and the user gets a notification.
5. **Tag garbage collection.** Suggested tags are checked against the existing tag set (`/^#\w+/$`). New tags require review.
6. **The "where are my notes" dashboard.** `99 _system/dashboards/Intake Review.md` — a Dataview of all `intake-log/` entries with status. The "I dropped something 3 days ago and forgot about it" failure mode is the one to prevent.

### The intake-log note format

Every drop creates two artifacts: the processed note (in destination or inbox) and an intake-log entry (in `99 _system/intake-log/yyyy-mm-drop-NNN.md`).

```markdown
---
type: intake-log
intake_id: 2026-06-02-drop-001
dropped_at: 2026-06-02T09:15:00
source_path: ~/Mavis-Inbox/images/IMG_4421.png
type: image
classification: idea
confidence: 0.78
filed_to: 00 Inbox/
status: needs-review
---

## Source
Screenshot of a Slack thread in #m3-eval with Sam arguing about the eval-rubric.

## M3 summary
Sam thinks the eval rubric under-weights long-horizon behavior; Andre pushed back saying precision on the rubric matters more than recall. Open question: do we add a "plateau persistence" axis?

## Suggested tags
[[eval-rubric]] [[long-horizon]] [[disagreement]]

## Suggested links
- [[M3 Eval Lab]] (confidence 0.91) — the project this thread is about
- [[Long-Horizon Patterns]] (confidence 0.74) — relevant pattern
- [[M3 Bypass Hypothesis]] (confidence 0.62) — possibly relevant, lower confidence

## Disposition
Status: needs-review (confidence 0.78, ambiguous between idea and question)
```

This is the artifact. The human (or the daily-brief workflow) can read it in 15 seconds, approve / edit / reject. Approval writes the final note to its destination with the right wikilinks applied.

## Cost

- **Image processing**: M3 vision is bundled in the model call, no separate cost.
- **Audio transcription**: M3 audio, same call.
- **Link fetch + defuddle**: ~$0.001 per link (host-side cost).
- **Classification + linking**: one M3 call per drop, ~$0.005 with thinking on, ~$0.001 with thinking off.
- **Storage**: original files + processed notes. ~500KB per image, ~1MB per audio minute, ~50KB per processed note. 100 drops/week ≈ 200MB/week. Trivial.

Per drop: ~$0.01. Per week (assuming 20 drops): $0.20. The value is in the time saved on "let me describe this to Mavis."

## What this is NOT

- **Not a replacement for active capture.** When you have a specific question or task, you tell Mavis. The intake is for the *passive* context you would otherwise forget.
- **Not magic.** M3's classification is only as good as the file content. A blurry photo of a whiteboard is a blurry photo of a whiteboard.
- **Not autonomous filing.** The auto-file threshold (0.85) is conservative. Most drops go to review. That's the point.
- **Not a fleet bridge.** Mavis is isolated. There's no Telegram drop, no Slack drop — just a local folder. Andre's design choice, not a limitation. (A future fleet-integrated Mavis instance could add a Telegram drop; this design supports it via the `intake.drop` API.)

## Connections

- [[00 Overview]] — the project hub
- [[03 The Custom MCP Arsenal]] — the broader 5-MCP design space; this extends the arsenal
- [[MCP #1: `vault-brain`]] — the link-suggestion primitive this MCP uses for `intake.suggest_links`
- [[MCP #5: `self-model-card`]] — companion: intake is *external* self-awareness (what came in), self-model-card is *internal* self-awareness (what I am)
- [[M3 Edge]] — the capability shift (native multimodal) this design exploits
- [[Native Execution Layers]] — the "no OCR, no ffmpeg" principle
- [[Mavis EA Workflow]] — current workflow that would consume this
- [[state-of-mavis]] — the MOC that should record when this is built + operational
- [[learnings]] — `[capability]` entries on native multimodal

---

*Design doc 2026-06-02. Written while the M3-native multimodal context from Operation Apex is fresh. Build is straightforward once the design is right — pending greenlight.*
