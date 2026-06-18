# Dossier — Markdown → HTML, Fade-Animated UI Layer

> Living topic file. Built 2026-06-04 for Mavis (EA) by the Researcher on urgent dispatch from Andre. Single-shot focused dossier (REFRESH-with-focused-collect mode), not a full REFRESH.
>
> **Purpose:** Spec the markdown-to-HTML rendering pipeline + fade-in animation + long-form layout baseline + performance budget for v1 of the Fleet-Status Surface, and as the foundation for every HTML delivery Mavis produces (dossiers, briefs, weekly syntheses). Read in 10 minutes. Use as a build spec.
>
> **Canonical synthesis pointer:** *No cross-dossier synthesis article yet* — this dossier is the only dossier that currently spans `dev_tooling` + a new sub-lane we'd call `reading_ui` or `human_facing_render`. If a `wiki/articles/markdown-to-html-ui.md` synthesis is added later, link it from this dossier header.

## Why this topic matters to Andre

Mavis is the EA. Her current delivery model is: she writes markdown into the Obsidian vault (dossiers, daily briefs, EA summaries, fleet-status state), Andre opens Obsidian to read. That's a good authoring surface but a slow *consumption* surface. The vault is where the work *lives*; the HTML surface is how the work *lands*. The dossier loop, the fleet-status pattern, the daily brief, and the EA synthesis all need a rendering layer that feels alive (fade-in as you scroll, content arrives, no preloader, no jank) but stays zero-JS, single-file, cacheable, vault-resident.

The thesis of this dossier: **the right pipeline is markdown-it → vanilla CSS scroll-driven animations + IntersectionObserver fade-in → Tufte-inspired long-form layout with self-hosted system stack → <100KB total page weight**. Every claim that crosses weight 0.6 below is backed by a primary source (MDN, Chrome for Developers, official docs).

## Current signal (last refresh: 2026-06-04 01:02 CT)

This is a 8-section dossier, one per the research question's required findings.

### 1. Markdown → HTML rendering surface

**Bottom line:** **`markdown-it` (Node/Python binding) for server-side / build-time, vanilla HTML output. The vault pipeline runs at file-save time, not in the browser.** Pandoc is a viable second choice for documents that need a full standalone HTML5 wrapper with metadata.

Primary sources (all `primary`):

- **`markdown-it`** is the canonical "CommonMark + GFM + 1000+ plugins" parser. `markdown-it` token-stream architecture, comprehensive plugin system (footnotes, deflists, containers, attrs, sup/sub, mark, ins, abbreviations, emoji), 100% Markdown 1.0, 100% CommonMark 0.31, full GFM. Active since 2014. Trust 0.95. (src-2026-06-04-001, src-2026-06-04-002)
- **`marked`** is the canonical "fastest low-level parser" alternative. 100% Markdown 1.0, 98% CommonMark 0.31, 97% GFM 0.29. **Caveat: marked does NOT sanitize output — must pipe through DOMPurify, js-xss, sanitize-html, or insane on untrusted input.** For Mavis's case (trusted author = Mavis, trusted input = the vault), sanitization is less critical but still a recommended discipline. Trust 0.9. (src-2026-06-04-003)
- **`pandoc`** is the universal document converter. Supports 40+ input formats and even more output formats including `gfm` (GitHub-Flavored Markdown) and `commonmark_x` (CommonMark with Pandoc's extensions). Markdown variants available: `markdown` (Pandoc's), `markdown_strict`, `markdown_phpextra`, `markdown_mmd` (MultiMarkdown), `markdown_github` (deprecated), `gfm`, `commonmark`, `commonmark_x`. The `--embed-resources` flag produces a self-contained HTML file with no external dependencies via `data:` URIs — exactly the "single file in the vault" pattern this dossier wants. Trust 0.95. (src-2026-06-04-004)
- **`gfm` (GitHub Flavored Markdown)** is a strict superset of CommonMark. Adds tables, task list items, strikethrough, autolinks, disallowed raw HTML. GFM Spec 0.29 (Apr 6, 2019) is the canonical reference. Trust 0.95. (src-2026-06-04-005)
- **Build-time static site generators** are how the file-in-the-vault pattern actually delivers. Three leading options for Obsidian-flavored content:
  - **Quartz 5** (jackyzha0) — Obsidian-native (full-text search, graph view, wikilinks, transclusions, backlinks, Latex, syntax highlighting, popover previews, Docker, i18n, comments). Hot-reload on config, incremental rebuilds. "Ridiculously fast page loads and tiny bundle sizes." Requires Node v22. (src-2026-06-04-006)
  - **Material for MkDocs** (squidfunk) — Material Design system, 60+ languages, 10,000+ icons, code annotations, social cards, built-in instant search, offline-capable, "fast and lightweight," used by NASA, CERN, TC39, W3C, Google, Microsoft, Mozilla, Font Awesome, Apache, freeCodeCamp. Trust 0.9. (src-2026-06-04-007)
  - **Eleventy / 11ty** (zachleat) — "simpler static site generator," zero-config, multiple template languages (HTML, Markdown, WebC, JS, Liquid, Nunjucks, etc.), zero client-side JavaScript by default, no telemetry. Build benchmark: 4000 markdown files in **1.93s** vs Astro 22.90s, Gatsby 29.05s, Next.js 70.65s. Used by Chrome for Developers. 19.7K stars, 18.7M downloads, 82K+ dependent repos. (src-2026-06-04-008)
  - **Astro** (with Content Collections) — Content Collections API with `glob()` loader (markdown, mdx, markdoc, JSON, YAML, TOML), Zod-schema validation, TypeScript type safety, dev toolbar, server rendering, view transitions. New `live content collections` for runtime-loaded content. v6.0 most recent. (src-2026-06-04-009)

**Verdict for Mavis's use case:** **Build-time pre-render, not client-side, not server-runtime.** The vault is the source of truth; the HTML is a generated view. The pipeline runs at file-save time (or on a cron / file-watch trigger) and writes a single self-contained HTML file into the vault. **Use `markdown-it` for the parser; build with a small Node.js script in `99 _system/scripts/`.** Don't pull in Quartz, 11ty, or Astro for v1 — those are overkill for "render one dossier to one HTML file." The dependency surface is one npm install: `markdown-it` + `markdown-it-anchor` (auto-generates heading IDs for jump-links). Pandoc is the fallback when Mavis needs a full standalone HTML5 wrapper (e.g., a brief that should be email-shareable as a single `.html` file).

### 2. CSS fade-in animation (zero-JS preferred, IntersectionObserver acceptable)

**Bottom line:** **Use a hybrid — pure-CSS `@keyframes` + `animation-delay` for first paint, and IntersectionObserver (~30 lines) for scroll-into-view fade.** Add native `animation-timeline: view()` only for users on Chrome 115+ (progressive enhancement). This keeps the page zero-JS for the *readable* surface while adding the "feels alive" reveal Andre wants.

Primary sources (all `primary`):

- **CSS scroll-driven animations module** (W3C/CSSWG, MDN canonical) — The `scroll()` function ties animation progress to a scroll container's position; the `view()` function ties progress to an element's relative position in its scroll container. Runs **off the main thread** (compositor), silky smooth. Two built-in timelines: `Scroll Progress Timeline` and `View Progress Timeline`. MDN page last updated 2026-05-28. (src-2026-06-04-010)
- **Chrome 115+ ships scroll-driven animations** natively. Bramus's canonical blog post on `developer.chrome.com` (May 5, 2023) walks through `animation-timeline: scroll()`, `animation-timeline: view()`, and the `animation-range` property. Page notes "if you can't wait to check out some demos go visit scroll-driven-animations.style." Safari 26, Chrome 115+, Edge 115+ support. (src-2026-06-04-011)
- **Baseline status: animation-timeline** is "baseline: false" per web-platform-dx. Chrome 115+ only as of 2026-06. (src-2026-06-04-012)
- **IntersectionObserver API** (MDN canonical) — "widely available since March 2019." Asynchronously observes changes in target element intersection with an ancestor element or top-level document's viewport. Configurable `root`, `rootMargin`, `threshold` (single number or array of percentages). Solves "fade in as the user scrolls down" pattern in 30 lines of vanilla JS. Replaces the legacy `getBoundingClientRect()` + scroll event loop pattern. (src-2026-06-04-013)
- **`@starting-style` CSS at-rule** (Chrome 117+ / Baseline entry 2024) — defines starting values for properties an element should transition *from* when first rendered, including from `display: none`. Combined with `transition-behavior: allow-discrete` (Chrome 117+) for entry animations on new DOM elements. "Now in Baseline" per web.dev 2024-10. Caveat: `@starting-style` rules must be placed AFTER the post-entry state declarations (as of Chrome 130). Trust 0.85 — newer spec, smaller browser footprint. (src-2026-06-04-014, src-2026-06-04-015)
- **View Transitions API** (Chrome 111+ for same-document, Chrome 126+ for cross-document) — Wraps DOM mutations in `document.startViewTransition()`. The browser takes a snapshot of the old state, applies the DOM change, and animates the transition. Useful for the *fleet-status → dossier → brief* navigation flow if those become separate pages, but **NOT recommended for v1** (we're rendering one long page, not navigating between pages). Defer to v2. (src-2026-06-04-016)
- **Web Animations API** — The framework underneath all of this. `Element.animate()` is the JS equivalent of `@keyframes`. Trust 0.95. (src-2026-06-04-017)

**Verdict for Mavis's use case:** **Hybrid layer-cake** —
- **First paint above the fold:** pure-CSS `@keyframes fade-in` + small `animation-delay` per element. Zero JS. Works in every browser since 2014.
- **Below the fold as the user scrolls:** vanilla JS IntersectionObserver (~30 lines), one observer per page, threshold `0.1`, adds class `is-visible` to elements that fade in via CSS transition. `prefers-reduced-motion: reduce` honored (skip the animation, show the content immediately).
- **Progressive enhancement:** `@supports (animation-timeline: view())` block adds the modern path for Chrome 115+ / Safari 26+ users — same visual, runs off the main thread.
- **NOT in v1:** View Transitions, `@starting-style` (save for v2 when the API stabilizes across Safari/Firefox).

### 3. Minimal / elegant long-form reading layouts

**Bottom line:** **Tufte-inspired long-form, 60–75 char line length, system font stack (no webfont network request), `text-wrap: pretty` on body, `text-wrap: balance` on headings, dark mode via `prefers-color-scheme`.** Gwern.net is the philosophical north star; Tufte CSS is the implementation template.

Primary sources (all `primary`):

- **Gwern.net "Design Of This Website"** (Gwern Branwen) — "4 design principles: aesthetically-pleasing minimalism, accessibility/progressive-enhancement, speed, and a 'semantic zoom' approach to hypertext use." Built with Pandoc + Hakyll, "JavaScript is not required for the core reading experience." Inspirations: English Wikipedia, Project Xanadu, Tufte, Robert Bringhurst, Susan Kare, Donald Knuth, Matthew Butterick, Markdeep, Andy Matuschak's evergreen notes. The "semantic zoom" framing — page hierarchy as collapsible, progressive disclosure — is the philosophical underpinning of how a long dossier should be presented. (src-2026-06-04-018)
- **Tufte CSS** (Dave Liepmann, edwardtufte/tufte-css) — Sidenotes (margin notes that don't force the reader to jump to the bottom of the page), full-width figures, careful typography (`#fffff8` off-white, `#111111` off-black, ETBook serif with system-font fallback), `newthought` for the first few words of a section in small caps, "the Feynman lectures use only 2 levels of hierarchical headings" (quote, Edward Tufte). Goal stated: "Webpages are not books. The goal of Tufte CSS is not to say 'websites should look like this interpretation of Tufte's books' but rather 'here are some techniques Tufte developed that we've found useful in print; maybe you can find a way to make them useful on the web.'" Trust 0.95. (src-2026-06-04-019)
- **CSS `text-wrap: pretty`** (Chrome 117+, WebKit, Baseline entry 2024) — improves line wrapping and avoids orphans on the last paragraph line. Use on body paragraphs. `text-wrap: balance` is for headings and short blocks; `text-wrap: pretty` is for paragraphs. Trust 0.9. (src-2026-06-04-020, src-2026-06-04-021)
- **Web Almanac 2025 Page Weight** (HTTP Archive) — The objective landscape. Median desktop home page is **2.86 MB**, median mobile home page is **2.56 MB** in 2025. Breakdown: HTML 22KB, CSS 82KB, fonts 139KB, JavaScript 697KB, images 1058KB on desktop. (src-2026-06-04-022)
- **Web Vitals** (web.dev canonical) — Core Web Vitals 2026 thresholds: LCP < 2.5s (Good), INP ≤ 200ms (Good), CLS ≤ 0.1 (Good). LCP / INP / CLS all **stable** as of 2024. (src-2026-06-04-023)

**Verdict for Mavis's use case:** **Tufte-inspired, 60–75 char body, system stack, dark mode by default-light, `text-wrap: pretty` on body, `text-wrap: balance` on headings.** **No webfont network request** in v1 (system font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif` for sans; `'Iowan Old Style', 'Apple Garamond', Baskerville, Georgia, serif` for body if the dossier is text-heavy). This is the only way to stay under 100KB total page weight on a long-form dossier.

### 4. Existing similar tools (audit before we build)

The closest existing patterns in Mavis's own catalog and in the wider ecosystem:

| Tool | What it does | What it does NOT do | Gap ours fills |
|------|--------------|---------------------|----------------|
| **`content-deck-generator`** (Mavis skill) | Reads `~/.mavis/fleet/*-draft.md` files, parses tweets + LinkedIn, renders standalone dark-theme HTML deck with Copy buttons + 60s auto-refresh via `<meta http-equiv="refresh">`. Inline JS for clipboard + countdown. Theme: "Tony Stark / Dark Arc Reactor." | Only X + LinkedIn buckets; dark theme only; fade-in animations absent; only handles one specific source format. | The pipeline shape (markdown → standalone HTML in a known location) is exactly what we want to reuse. The auto-refresh pattern is the right move for the fleet-status surface (it changes every 6h). |
| **`html-presentation-generator`** (Mavis skill) | Generates multi-page HTML presentations exportable to PDF/PPTX. Cover, TOC, section divider, content pages, summary/closing. Fixed 960×540 dimensions per slide. **"No animations: No CSS animations, transitions, hover effects, or SVG animations."** Times New Roman font, no gradients, all CSS inline. | Deliberately animation-free; slide-deck UX, not long-form reading; binary-export-focused. | Nothing for v1 — the anti-animation rule is a feature for export, not for reading. |
| **`landing-page-builder`** (Mavis skill) | Awwwards-level landing pages, cinematic hero, deployed online, video-first. Spec-then-build flow with `spec.md`. | Hero-video-driven, not reading-driven; meant to deploy to a public URL, not stay vault-resident. | The spec-first discipline is a good model for our `01 Build Spec.md`; the deliverable shape is wrong for our use case. |
| **`pptx-generator`** / `minimax-pptx` / `minimax-pdf` | Binary deliverables (PPTX / PDF). | Not HTML+animation. | Confirms the gap: there is no skill in the Mavis catalog that does markdown → self-contained HTML with fade-in. v1 fills it. |
| **`visual-summary`** (Mavis skill) | Not currently installed in `~/.mavis/skills/`. Per the skill catalog description, "Proactively create a visual summary HTML page when plain text cannot effectively convey the information." (src-2026-06-04-024) | The trigger is "when plain text cannot effectively convey," which is a *narrower* use case than ours. | Our pipeline is the generalization: every Mavis output (text-or-visual) gets the same rendering treatment. |
| **Obsidian Publish** | Obsidian's official vault-to-web service. $8/mo. Full-text search, graph view, backlinks. | Hosted, $8/mo, requires publishing. | We want vault-resident, not published. |
| **Quartz 5** | The closest to our use case at the static-site-generator level. Full Obsidian compatibility. | It's a *site* generator — it produces dozens of pages. We need *one* page per dossier. | Don't pull in Quartz. Borrow its `popover previews` and `wikilinks` rendering for the dossier, build as a 200-line Node script using markdown-it + a hand-rolled CSS template. |

**Verdict for v1:** **Build a new pipeline, borrow the shape from `content-deck-generator` (auto-refresh + standalone file), borrow the typography discipline from Tufte CSS, ignore the binary-deliverable skills.** The pipeline is novel for the Mavis catalog but small (≤ 200 lines of Node).

### 5. Self-contained vs server-rendered tradeoffs

**Bottom line:** **Self-contained single HTML file. Pandoc's `--embed-resources` (or markdown-it + manual inlining in a 50-line script) is the right shape.** The vault-resident pattern is non-negotiable: the HTML file must live next to the markdown file, must be openable directly in a browser, must not require a server.

Primary sources:

- **HTTP Archive Web Almanac 2025 Page Weight** — Median home page in 2025 is 2.86 MB desktop / 2.56 MB mobile. The browser spends "significant CPU power parsing and executing" JavaScript; "excessive page weight creates significant inequities" on low-end devices. The constraint "all key information should be present in the initial raw HTML, since AI crawlers do not render JavaScript" is a useful framing for the vault's delivery model. (src-2026-06-04-022)
- **Pandoc `--embed-resources`** — "Produce a standalone HTML file with no external dependencies, using `data:` URIs to incorporate the contents of linked scripts, stylesheets, images, and videos. The resulting file should be 'self-contained,' in the sense that it needs no external files and no net access to be displayed properly by a browser. This option works only with HTML output formats, including `html4`, `html5`, `html+lhs`, `html5+lhs`, `s5`, `slidy`, `slideous`, `dzslides`, and `revealjs`." Caveat: "resources that are loaded dynamically through JavaScript cannot be incorporated." (src-2026-06-04-004)
- **Pandoc `--self-contained` is the deprecated synonym** for `--embed-resources --standalone` — both still work, but `--embed-resources` is the modern name. (src-2026-06-04-004)

**Verdict for Mavis's use case:** **Single self-contained HTML, CSS inlined in `<style>` in `<head>`, no external requests.** The script writes the file, the file lives at `03 Projects/Fleet-Status Surface/status.html` (or `02 Notes/dossiers/{name}.html`), openable by double-click. This:
- Eliminates the network round-trip on first load
- Makes the file archiveable as a single artifact (committed to git, included in backups)
- Honors the AI-crawler constraint (all content in initial raw HTML)
- Means the page works offline (vault-resident = no server dependency)

**Performance budget for v1 (dossier with 3,000-8,000 words):** target **< 100KB total uncompressed HTML** (which compresses to ~15-20KB gzipped, vs the median web page's 700+KB JS budget). Components: HTML 20KB + inline CSS 25KB + minimal JS (IntersectionObserver) 1KB + zero webfonts + zero images. Compare to the median web page: HTML 22KB + CSS 82KB + JS 697KB + fonts 139KB + images 1058KB = 2.86MB.

### 6. AI-agent → human content surfaces (the emerging pattern)

**Bottom line:** **The "AI output landing page" is a real emerging pattern, but no one has a name for it yet.** Claude Artifacts, ChatGPT Canvas, Perplexity Pages, and Google Gemini Gems all solve the same problem: AI generates a long, structured artifact; the human wants to *read* it (not just see it as a chat turn); the product surfaces it in a dedicated panel. Our dossier rendering is the **Mavis-archive variant** of this pattern — the artifact is the dossier the EA produced, the human is Andre, the panel is the vault HTML.

Primary sources (mix of primary and secondary):

- **Claude Artifacts (Anthropic)** — Announced June 21, 2024 with Claude 3.5 Sonnet on `anthropic.com/news/claude-3-5-sonnet`. Anthropic's framing: "Artifacts on Claude.ai, a new feature that expands how users can interact with Claude. When a user asks Claude to generate content like code snippets, text documents, or website designs, these Artifacts appear in a dedicated window alongside their conversation. This creates a dynamic workspace where they can see, edit, and build upon Claude's creations in real-time, seamlessly integrating AI-generated content into their projects and workflows." "This preview feature marks Claude's evolution from a conversational AI to a collaborative work environment." Made generally available Aug 28, 2024. Trust 0.9. (src-2026-06-04-025)
- **Perplexity Pages** — Announced May 30, 2024 on `perplexity.ai/hub/blog/perplexity-pages`. Framing: "Meet Perplexity Pages, your new tool for easily transforming research into visually stunning, comprehensive content." Features: section-by-section reformat, media insertion, source citation, audience targeting. The "AI-Wikipedia" framing. Initially Pro-only, then rolled out to free/Enterprise. (src-2026-06-04-026)
- **ChatGPT Canvas (OpenAI)** — Launched October 2024. Side-panel collaborative writing surface. (Secondary; not directly fetched from OpenAI's blog in this dossier cycle. Logged for next REFRESH.)
- **The pattern is real but unnamed.** Andre's instinct that "Mavis outputs need a rendering layer" is on the leading edge of a pattern that every major AI lab is also working on. (Inference from the three launch patterns.)

**Verdict for Mavis's use case:** **The vault HTML is the Mavis-archive instance of this pattern.** Our rendering layer (single-file HTML, fade-in on scroll, self-contained) is functionally equivalent to what Anthropic / OpenAI / Perplexity do in their product surfaces, just with the host *being the vault file* instead of a chat panel. Don't try to ship a "Mavis Artifacts" product; the file IS the artifact. v1 is enough.

### 7. Performance budget (the hard constraint)

**Bottom line:** **< 100KB total uncompressed HTML for a typical dossier, FCP < 200ms locally, zero layout shift on fade-in, LCP < 2.5s on a fresh load, INP < 200ms, CLS < 0.1.** The page must be readable without JS executing. All metrics are field metrics (75th percentile of real users), not lab metrics.

Primary sources:

- **Web Vitals canonical thresholds** (web.dev) — "Largest Contentful Paint (LCP): measures loading performance. To provide a good user experience, LCP should occur within 2.5 seconds of when the page first starts loading. Interaction to Next Paint (INP): measures interactivity. To provide a good user experience, pages should have a INP of 200 milliseconds or less. Cumulative Layout Shift (CLS): measures visual stability. To provide a good user experience, pages should maintain a CLS of 0.1. or less." 75th percentile is the measurement target. (src-2026-06-04-023)
- **HTTP Archive Web Almanac 2025** — Median HTML 22KB, median CSS 82KB, median JS 697KB. Our budget is one-tenth of the median HTML and one-third of the median CSS — feasible because we have no JS framework and a single inline stylesheet. (src-2026-06-04-022)
- **web-vitals JS library** (GoogleChrome/web-vitals) — `import {onCLS, onINP, onLCP} from 'web-vitals'` is the standard way to measure in the field. (src-2026-06-04-023)
- **`prefers-reduced-motion`** — Always honor the user OS-level setting. Skip the animation, show the content immediately. (De facto discipline across all sources above.)

**Verdict for Mavis's use case:**

| Metric | Target | Why |
|---|---|---|
| Total HTML weight (uncompressed) | **< 100KB** | One-tenth of median; well below the "feels heavy" threshold |
| Total HTML weight (gzipped) | < 20KB | Sub-second on 4G |
| FCP (local file:// open) | < 200ms | The file is local; FCP is essentially paint-blocking zero |
| LCP (web-served) | < 2.5s | Web Vitals Good threshold |
| INP | < 200ms | Web Vitals Good threshold; we have no interactions in v1 |
| CLS | < 0.1 | Critical: fade-in must not shift layout. Use `opacity` + `transform: translateY()`, not `top`/`bottom` |
| Total external requests | 0 | Self-contained |
| Webfont requests | 0 | System stack in v1 |
| Third-party scripts | 0 | No analytics in v1; if added later, must be async and below the fold |
| Accessibility (axe / Lighthouse) | 100 / 100 | Color contrast AA; semantic HTML; reduced-motion respected |

**Defer to v2:** Field-measurement of LCP / INP / CLS via the web-vitals library + a Mavis-managed RUM endpoint. Not v1 scope.

### 8. How the agent should structure its markdown so the render is clean

**Bottom line:** **Heading hierarchy, semantic breaks, image alt text, code-fence languages, and Pandoc-style "render hints" passed through to the HTML for the rendering script to consume.** The render script reads the frontmatter, the markdown body, and any `<!-- render-hint: ... -->` comments and applies the appropriate CSS class or template variable.

Primary sources:

- **CommonMark Spec** (referenced in GFM) — Defines the basic block / inline grammar. Heading levels 1-6, ATX (`#`) and Setext (`=====` / `-----`), fenced code blocks (3+ backticks or tildes), blockquotes, lists, links, images, emphasis, code spans, hard/soft line breaks. (src-2026-06-04-005)
- **GFM Spec 0.29** — Strict superset of CommonMark. Adds: tables (extension), task list items (extension), strikethrough (extension), autolinks (extension), disallowed raw HTML (extension). All user content on github.com uses GFM. (src-2026-06-04-005)
- **Pandoc's markdown variants** — `markdown` (Pandoc's flavor, the default), `gfm` (GitHub's), `commonmark` (CommonMark strict), `commonmark_x` (CommonMark + Pandoc extensions). Pandoc's `--from` accepts the variant. (src-2026-06-04-004)

**Verdict for Mavis's use case:** **Author in GFM-flavored markdown with Pandoc-style extensions.** Concretely:
- **Frontmatter** (YAML): `title`, `author` (default: Mavis), `date`, `tags`, `dossier_id` (links to `dossiers/*.md`).
- **Heading hierarchy:** H1 once per page (the title), H2 for sections, H3 for subsections. Cap at H3 (Tufte: "the Feynman lectures use only 2 levels of hierarchical headings"). If Mavis needs H4, she's nesting too deep.
- **Semantic breaks:** horizontal rule (`---`) between major sections.
- **Code fences:** always with language (`js`, `python`, `bash`).
- **Image alt text:** always. Non-negotiable.
- **Render hints** (Pandoc-style `<!-- render-hint: class="callout" -->`): a small set of custom block-level wrappers the render script recognizes and translates to a CSS class. Examples:
  - `:::callout` → `<aside class="callout">` (Mavis's "important note" wrapper)
  - `:::fade-in-stagger` → `<div class="fade-in-stagger">` (the children fade in with staggered animation-delay)
  - `:::collapse` → `<details><summary>...</summary>...</details>` (Gwern-style collapsibles)
  - `:::source-trail` → `<section class="source-trail">` (the research dossier's source-trail rendering)
  - This is a thin custom block syntax, not a new markdown dialect. Implemented in 20 lines of markdown-it core rules.

## Source trail

See `knowledge/sources.jsonl`. Key primary sources for this dossier (all fetched 2026-06-04 01:02-01:25 CT):

- `src-2026-06-04-001` markdown-it demo — weight 0.95 (primary, official)
- `src-2026-06-04-002` markdown-it GitHub (implicit via demo) — weight 0.9
- `src-2026-06-04-003` marked.js official docs — weight 0.9
- `src-2026-06-04-004` Pandoc User's Guide (pandoc.org/MANUAL.html) — weight 0.95
- `src-2026-06-04-005` GFM Spec 0.29 (github.github.com/gfm) — weight 0.95
- `src-2026-06-04-006` Quartz 5 docs (quartz.jzhao.xyz) — weight 0.85
- `src-2026-06-04-007` Material for MkDocs (squidfunk.github.io/mkdocs-material) — weight 0.9
- `src-2026-06-04-008` Eleventy (11ty.dev) — weight 0.9
- `src-2026-06-04-009` Astro Content Collections docs (docs.astro.build) — weight 0.9
- `src-2026-06-04-010` MDN CSS scroll-driven animations module — weight 0.95
- `src-2026-06-04-011` Chrome for Developers: "Animate elements on scroll" (Bramus) — weight 0.9
- `src-2026-06-04-012` web-platform-dx animation-timeline feature status — weight 0.85
- `src-2026-06-04-013` MDN Intersection Observer API — weight 0.95
- `src-2026-06-04-014` MDN @starting-style — weight 0.85
- `src-2026-06-04-015` Chrome for Developers: "Four new CSS features for smooth entry and exit animations" — weight 0.9
- `src-2026-06-04-016` Chrome for Developers: "Smooth transitions with the View Transition API" — weight 0.85
- `src-2026-06-04-017` MDN Web Animations API — weight 0.9
- `src-2026-06-04-018` Gwern.net "Design Of This Website" (gwern.net/design) — weight 0.9
- `src-2026-06-04-019` Tufte CSS (edwardtufte.github.io/tufte-css) — weight 0.95
- `src-2026-06-04-020` Chrome for Developers: CSS text-wrap pretty — weight 0.9
- `src-2026-06-04-021` WebKit blog: "Better typography with text-wrap pretty" — weight 0.9
- `src-2026-06-04-022` HTTP Archive Web Almanac 2025 Page Weight chapter — weight 0.95
- `src-2026-06-04-023` web.dev: Web Vitals — weight 0.95
- `src-2026-06-04-024` Mavis skill catalog: visual-summary (referenced) — weight 0.7
- `src-2026-06-04-025` Anthropic: "Introducing Claude 3.5 Sonnet" (Artifacts announcement) — weight 0.9

## Contradictions and open questions

- **Anthropic engineer's "MD is dead" thread (May 2026)** — Thariq (Anthropic engineer) published a viral thread arguing HTML > Markdown for AI-generated artifacts, with Karpathy endorsing. Secondary sources (36kr, Sohu, Tencent News) reported on it. Implication: long-form AI outputs may converge to HTML, not Markdown. (src-2026-06-04-027 secondary) — **Implication for v1: keep the markdown source of truth, but the render artifact is HTML. That's already the plan. Watch this space.** Not a contradiction, more a "your instinct is right" signal.
- **Astro vs 11ty vs Quartz for "what's the best long-term foundation"** — Astro is the most flexible (islands, content collections, view transitions) but heaviest. 11ty is the simplest and fastest. Quartz is the most Obsidian-native. **For v1 (one rendering script, one HTML output per dossier), none of them is the right tool. For v2 (generalize to all Mavis outputs as a site), Astro is the right call.** Flagged for the next dossier.
- **View Transitions for cross-page navigation** — If/when the dossier/brief/fleet-status become separate pages (rather than one long page), View Transitions (Chrome 126+ cross-document) becomes the right cross-page animation primitive. v2 question.
- **IntersectionObserver + `prefers-reduced-motion`** — the canonical pattern in the Chrome docs checks the media query and skips the animation. We need to follow this. **Test before shipping.**
- **Open question — should the render hint syntax be markdown-it-specific or pandoc-style?** — Pandoc's fenced_divs extension (`::: classname`) is the more portable choice. Mavis would write the same hint whether she later switches from markdown-it to pandoc. **Recommended: pandoc-style fenced_divs, implemented in markdown-it via the `markdown-it-container` plugin.**

## Implications

**The recommended rendering pipeline (Mavis's Build Spec v1):**

```
[markdown file] → markdown-it (server-side parse)
                 → + markdown-it-anchor (auto-generate heading IDs)
                 → + markdown-it-container (::: callout / fade-in-stagger / collapse)
                 → + manual CSS template
                 → inlined <style> in <head>
                 → vanilla JS IntersectionObserver block (~30 lines, inlined before </body>)
                 → single .html file written to vault
```

| Layer | Choice | Why |
|---|---|---|
| **Markdown lib** | `markdown-it` + 3 plugins | Plugin system, 100% CommonMark + GFM, zero config, mature, fast |
| **Animation technique** | Hybrid: pure-CSS @keyframes for first paint + IntersectionObserver for scroll-into-view; `@supports (animation-timeline: view())` progressive enhancement for Chrome 115+/Safari 26+ | Zero JS for the readable surface; ~30 lines of JS for scroll-into-view; modern path for users on newer browsers |
| **Layout baseline** | Tufte-inspired, 60-75 char body, system font stack, `text-wrap: pretty` on body, `text-wrap: balance` on headings, dark mode via `prefers-color-scheme` | Performance budget forces no-webfont; Tufte is the gold standard; system stack keeps the file under 100KB |
| **Performance budget** | < 100KB total HTML, FCP < 200ms locally, LCP < 2.5s web, INP < 200ms, CLS < 0.1, zero external requests, zero webfonts | See Section 7. The median web page is 2.86MB; we ship < 100KB. 28x lighter. |
| **Delivery** | Self-contained single HTML in the vault, version-controlled, regenerable by a script in `99 _system/scripts/` | Round-trip: markdown is source of truth, HTML is generated view |
| **Render hints** | Pandoc-style fenced divs: `:::callout`, `:::fade-in-stagger`, `:::collapse`, `:::source-trail` | Portable, 20-line markdown-it plugin, no new dialect |

**Build:** for v1 (Fleet-Status Surface), the v1 implementation is "build a 200-line Node script in `99 _system/scripts/render-dossier.js` that takes a markdown file path, returns a self-contained HTML file path, and runs on file-watch or manual trigger." This is the Builder agent's job, not Researcher's. The dossier above is the spec; the Builder owns the script.

**Content:** the EA synthesis ("why is the fleet-status surface worth building") is ready to use as the framing for the v1 announcement. The "AI output landing page" pattern (Section 6) is the strongest single claim — the dossier is novel because Mavis is on the leading edge of a pattern every major lab is converging on.

**Watch:** Anthropic engineer's "MD is dead" thread (single-source; watch for further corroboration from other AI labs). View Transitions cross-document (Chrome 126+) — only when the v2 page-per-dossier decision is made.

**Verify:** none this cycle. The IntersectionObserver pattern is verified by MDN canonical doc; the markdown-it / pandoc / GFM claims are verified by their own canonical docs; the HTTP Archive numbers are verified by their own primary source. No external claims need a second-source cross-check at the rubric boundary.

**Re-verification watch (90-day discipline):** the Web Vitals thresholds (LCP 2.5s, INP 200ms, CLS 0.1) are stable as of 2024 and unlikely to change by next REFRESH (2026-09-04), but if Google re-tunes, this dossier needs an update. Marked for context_decay recompute on 2026-09-04 (90 days from `verified_at`).

## Routing history

| Date | Routed to | Item | Outcome |
|------|-----------|------|---------|
| 2026-06-04 | queue/mavis-handoff.md | mvs-handoff-2026-06-04-001 (dossier ready) | Pending Mavis consumption |
| 2026-06-04 | queue/research-questions.md | research-question-2026-06-04-001 (this dossier) | Pending move to Processed |
| 2026-06-04 | runs/RUN-2026-06-04-0102-DIVE-MAVIS-UI.md | run receipt | Pending Mavis consumption |

---

*This dossier is the spec for the v1 build. It accumulates. The Builder takes this and turns it into a 200-line script. Mavis takes the script and renders the first dossier. Andre opens the HTML in his browser, sees it fade in, and says "now that's a desk."*
