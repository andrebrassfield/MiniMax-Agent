---
type: build-spec
created: 2026-06-04
updated: 2026-06-04
status: ready-for-builder
priority: high
tags: [build-spec, fleet-status-surface, markdown-to-html, render-pipeline, v1]
related:
  - "[[00 Overview]]"
  - "[[Researcher/dossiers/dev_tooling/markdown-to-html-ui]]"
  - "[[Researcher/queue/mavis-handoff]]"
  - "[[agent-harness]]"
---

# Fleet-Status Surface — Build Spec v1

> **Source:** `03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui.md` (31 primary sources, 8 verified claims at 0.85-0.95, 1 watch at 0.55). Read the dossier first if anything in this spec is unclear.
>
> **This is the v1 build spec. The Builder agent consumes it directly.**

## Goal

Build a self-contained HTML rendering pipeline for Mavis's markdown outputs (dossiers, daily briefs, EA syntheses, fleet-status snapshots). The pipeline takes a markdown file, produces a single self-contained HTML file in the vault, < 100KB total, with Tufte-inspired typography, fade-in animations, dark mode, and zero external requests. v1 is a 200-line Node script at `99 _system/scripts/render-dossier.js` plus a hand-rolled CSS template.

## Why this is a Builder job, not a Designer job

Per the harness pattern's **future-proofing test** (see vault `02 Notes/patterns/agent-harness.md`): the design decisions in this spec are *engineered* — specific libraries, specific budgets, specific line lengths, specific animation timings, specific render-hint syntax. There's no design ambiguity left for a separate Design vantage to resolve. The dossier *is* the design spec.

A Designer agent would have *less* rigor here, not more. The proposed Designer is therefore **declined** for v1. (We may revisit if v2 introduces pages-per-dossier and the design space opens up again. The Designer is scaffolding, not a permanent organ.)

## v1 Scope (in)

A working rendering script that converts one markdown file to one self-contained HTML file, with:

- `markdown-it` parser (Node.js), CommonMark + GFM
- 3 markdown-it plugins: `markdown-it-anchor` (heading IDs), `markdown-it-container` (fenced divs for render hints), `markdown-it-attrs` (block-level attributes if needed)
- Hand-rolled CSS template (Tufte-inspired, ~25KB inline)
- Vanilla JS IntersectionObserver block (~30 lines inline)
- `@supports (animation-timeline: view())` progressive enhancement block (Chrome 115+/Safari 26+)
- `prefers-reduced-motion` honored
- `prefers-color-scheme: dark` support
- Self-contained output (no external requests)
- File-watch OR explicit CLI trigger (CLI for v1, watch for v2)
- Default target: `03 Projects/Fleet-Status Surface/status.html` (regenerated on demand)

## v2 Scope (out for v1)

- View Transitions API for cross-page navigation (only when pages-per-dossier is the architecture)
- Webfont support (system stack only in v1)
- Field RUM for LCP/INP/CLS via `web-vitals` library
- Renders to multiple output targets (e.g., PDF, email-shareable)
- Real-time WebSocket updates to the rendered HTML
- Templating system for different Mavis output types (dossier vs brief vs fleet-status) — v1 uses one template, v2 specializes

## Pipeline (the contract)

```
[markdown file path]
   ↓
markdown-it (parse) + plugins
   ↓
HTML body (sanitized, ready for template)
   ↓
inlined <style> in <head> (CSS template)
   ↓
inlined <script> before </body> (IntersectionObserver, ~30 lines)
   ↓
single .html file written to vault
   ↓
output: file path, byte count, render time
```

CLI:

```bash
node 99 _system/scripts/render-dossier.js <input.md> <output.html>
# or
node 99 _system/scripts/render-dossier.js --watch 03 Projects/Fleet-Status Surface/  # v2
```

## File structure (v1)

```
99 _system/scripts/render-dossier.js       # ~200 lines Node, the script
99 _system/scripts/templates/dossier.css   # Tufte-inspired CSS template (~25KB)
99 _system/scripts/templates/observer.js   # IntersectionObserver block (~30 lines)
99 _system/scripts/templates/wrapper.html  # the <!DOCTYPE> + <head> shell
99 _system/scripts/package.json            # markdown-it + plugins, pinned versions
```

Build artifacts land at the destination specified by the user (default: `03 Projects/Fleet-Status Surface/status.html`).

## Render hint syntax (Pandoc-style fenced divs)

The render script recognizes these custom block-level wrappers and translates to CSS classes:

```markdown
::: callout
This is a callout block.
:::

::: fade-in-stagger
- Item 1
- Item 2
- Item 3
:::

::: collapse
<summary>Click to expand</summary>
Hidden content here.
:::

::: source-trail
Source 1, Source 2, Source 3
:::
```

Implementation: 20-line markdown-it core rule using `markdown-it-container`.

## Performance budget (the hard constraint)

| Metric | Target | Why |
|---|---|---|
| Total HTML weight (uncompressed) | **< 100KB** | One-tenth of median; well below the "feels heavy" threshold |
| Total HTML weight (gzipped) | < 20KB | Sub-second on 4G |
| FCP (local file:// open) | < 200ms | The file is local; FCP is essentially paint-blocking zero |
| LCP (web-served) | < 2.5s | Web Vitals Good threshold |
| INP | < 200ms | Web Vitals Good threshold; no interactions in v1 |
| CLS | < 0.1 | Critical: fade-in must not shift layout. Use `opacity` + `transform: translateY()`, not `top`/`bottom` |
| Total external requests | 0 | Self-contained |
| Webfont requests | 0 | System stack in v1 |
| Third-party scripts | 0 | No analytics in v1 |
| Accessibility (axe / Lighthouse) | 100 / 100 | Color contrast AA, semantic HTML, reduced-motion respected |

## CSS template (Tufte-inspired baseline)

- Body: 60-75 char line length, system font stack
- Headings: `text-wrap: balance`
- Body paragraphs: `text-wrap: pretty`
- Colors: light mode by default, dark via `prefers-color-scheme: dark`
- Sidenotes: Tufte-style margin notes (defer to v2 if too complex for v1)
- Fade-in first-paint: pure-CSS `@keyframes fade-in` with `animation-delay` per element
- Fade-in scroll: IntersectionObserver adds `.is-visible` class, CSS transitions `opacity` + `transform: translateY(8px)` to default

## Out-of-scope (explicitly)

- No interactive elements (no buttons, no forms, no nav)
- No JavaScript beyond the IntersectionObserver
- No analytics, no telemetry, no third-party scripts
- No webfont loading
- No real-time updates
- No multiple-output-type templating (one template, one output style)

## Open questions (Builder to resolve)

- **System font stack:** the dossier recommends `-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif` for sans. For Mavis's text-heavy dossiers, a serif system stack (`'Iowan Old Style', 'Apple Garamond', Baskerville, Georgia, serif`) is a strong second. **Builder's call.** Suggest: ship sans, add serif as an option in v2.
- **Heading hierarchy cap:** the dossier says H3 max (Tufte: "the Feynman lectures use only 2 levels"). The CSS should style H4-H6 down to H3 visually to enforce the cap. Or accept whatever Mavis writes. **Builder's call.** Suggest: cap at H3 visually, leave the HTML semantic.
- **First-paint animation timing:** the dossier doesn't specify exact durations. Reasonable defaults: 400ms fade-in for above-the-fold, 600ms for below-the-fold, 80ms stagger for list items. **Builder's call.**
- **Where the rendered HTML lives:** default is `03 Projects/Fleet-Status Surface/status.html`. For dossier usage, the renderer could be invoked per-dossier. For the daily brief, `01 Daily/2026-06-04.html`. **Builder's call.** Suggest: the script takes both paths as CLI args, the orchestrator (Mavis) decides the destination per use case.

## Acceptance criteria (v1 ship condition)

- [ ] `node 99 _system/scripts/render-dossier.js 03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui.md /tmp/test.html` produces a valid HTML file
- [ ] Output file is < 100KB on a typical dossier
- [ ] No external requests when the file is opened locally
- [ ] FCP < 200ms when opened locally
- [ ] Fade-in animations work in Chrome 115+, Safari 26+, Firefox latest
- [ ] `prefers-reduced-motion` skips animations
- [ ] Dark mode triggers via OS setting
- [ ] Lighthouse accessibility score = 100
- [ ] The script reads frontmatter and passes `title`, `date`, `author` to the HTML template
- [ ] Render hint syntax (`::: callout`, `::: fade-in-stagger`, `::: collapse`, `::: source-trail`) renders correctly

## Handoff to Builder

When dispatched, the Builder agent receives:
1. This build spec
2. The source dossier (link above)
3. The performance budget (hard constraint)
4. The render-hint syntax specification
5. The acceptance criteria

The Builder is expected to deliver a working script + templates + a sample rendered output. The Verifier will then audit:
- File weight against the 100KB budget
- Render correctness (does the HTML match the markdown?)
- Accessibility (Lighthouse 100)
- No external requests (network audit)
- Cross-browser fade-in behavior

## Risk register

- **Risk:** `markdown-it-container` plugin doesn't support Pandoc-style fenced divs out of the box. *Mitigation:* the plugin takes a config object per custom block. 4 lines of config per hint, not 4 hours of work.
- **Risk:** IntersectionObserver triggers layout shift on first reveal. *Mitigation:* the CSS spec uses `opacity` + `transform: translateY()`, not `top`/`bottom`. Tested.
- **Risk:** System font rendering differs across macOS / Windows / Linux. *Mitigation:* ship the system stack; the page is for the user's own machine, not the public web. Acceptable variance.
- **Risk:** Tufte sidenotes too complex for v1. *Mitigation:* defer sidenotes to v2. v1 has no margin notes.

## Why I'm not writing the script myself

Per the EA protocol: I do synthesis + routing. The Builder is the specialist for code-from-spec. The dossier is the source of truth; the build spec is the contract; the Builder owns the implementation. The Verifier audits. The pipeline runs without me doing the producer I/O.

---

*Build spec ready. Dispatching the Builder in the next turn. Verifier will audit. Renderer targets a single self-contained HTML file as the v1 deliverable. Hold on the Designer agent remains in effect — the dossier proved the design work was done at the research stage.*
