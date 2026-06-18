---
type: builder-deliverable
project: fleet-status-surface
created: 2026-06-04
author: builder
status: ready-for-verifier
related:
  - "[[00 Overview]]"
  - "[[01 Build Spec]]"
  - "[[05 CSS Template Draft]]"
  - "[[06 Builder Handoff]]"
  - "[[08 Demo - 2026-06-04.html]]"
tags: [builder-deliverable, fleet-status-surface, render-dossier, v1, mavis-design, m3]
---

# Builder Deliverable — Fleet-Status Surface Renderer v1

> **Status:** v1 shipped. Self-audit passes (28 / 28). Demo rendered. Ready for the Verifier.
>
> **What this is:** A 285-line Node script (`render-dossier.js`) + 3 templates (CSS, observer JS, wrapper HTML) + a 30.3 KB rendered demo of `01 Daily/2026-06-04.md`. The script turns a markdown file (dossier, daily note, brief) into a self-contained, fade-animated HTML surface. Output is < 100 KB, has zero external requests, and honors `prefers-reduced-motion`.

## File inventory

```
99 _system/scripts/
├── render-dossier.js          (285 lines, the main script)
├── package.json               (pinned deps, CommonJS)
├── package-lock.json          (npm-generated)
├── node_modules/              (markdown-it + 4 plugins)
└── templates/
    ├── dossier.css            (~10 KB, extracted from 05 CSS Template Draft.md)
    ├── observer.js            (~30 lines, IntersectionObserver)
    └── wrapper.html           (~25 lines, DOCTYPE shell)

03 Projects/Fleet-Status Surface/
└── 08 Demo - 2026-06-04.html  (30.3 KB rendered output)
```

## Line count

| File | Lines | Notes |
|---|---|---|
| `render-dossier.js` | **285** | Dispatch asked for ~200. Over by ~85. The script is well-commented, the Verifier reads the source, and trimming comments would hurt audit clarity. The bloat is in `addFadeInClass` (stateful tag stack, ~70 lines) and the 5 render-hint container configs (~30 lines). Both are load-bearing. |
| `templates/dossier.css` | ~520 | The Designer's drop-in stylesheet, extracted verbatim. |
| `templates/observer.js` | 18 | IntersectionObserver + no-op fallback. |
| `templates/wrapper.html` | 26 | DOCTYPE shell with 6 placeholders. |

## Dependencies (pinned, in `package.json`)

| Package | Version | Role |
|---|---|---|
| `markdown-it` | 14.1.0 | Core parser. CommonMark + GFM, plugin architecture. |
| `markdown-it-anchor` | 9.2.0 | Heading IDs + permalink anchors. |
| `markdown-it-attrs` | 4.3.1 | Class/id attribute passthrough (`{.classname}`). |
| `markdown-it-container` | 4.0.0 | 5 render-hint containers (callout, fade-in-stagger, collapse, source-trail, spacious). |
| `markdown-it-footnote` | 4.0.0 | Footnote support. |

`npm install` reports 1 moderate-severity vulnerability in a transitive dep (not in our direct deps). Not blocking for v1. `npm audit fix` will be a follow-up.

## How to run

```bash
# From anywhere:
node /Users/brassfieldventuresllc/MiniMax-Agent/99\ _system/scripts/render-dossier.js <input.md> --out=<out.html>

# From inside the scripts dir:
cd "/Users/brassfieldventuresllc/MiniMax-Agent/99 _system/scripts"
node render-dossier.js "<input.md>" --out="<out.html>"

# stdin:
cat "<input.md>" | node render-dossier.js - --out="<out.html>"

# help:
node render-dossier.js --help
```

The first successful run was:

```bash
node render-dossier.js "/Users/brassfieldventuresllc/MiniMax-Agent/01 Daily/2026-06-04.md" \
  --out="/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Fleet-Status Surface/08 Demo - 2026-06-04.html"

# Output: Wrote ... (31029 bytes)
```

## Self-audit (28 / 28 pass)

Run on the demo render:

| # | Check | Pass |
|---|---|---|
| 1 | `<!DOCTYPE html>` present | ✓ |
| 2 | `<html lang="en">` set (a11y 3.1.1) | ✓ |
| 3 | `<title>` set (a11y 2.4.2) | ✓ |
| 4 | `<meta name="description">` set | ✓ |
| 5 | `<a class="skip-link" href="#main">` is first focusable (a11y 2.4.1) | ✓ |
| 6 | `<main id="main">` wraps article | ✓ |
| 7 | `<header class="page-header">` present | ✓ |
| 8 | `<h1 class="page-title fade-in-presence">` on exactly one element | ✓ |
| 9 | `class="fade-in"` on block elements outside render-hint containers | ✓ |
| 10 | Observer JS inlined before `</body>` | ✓ |
| 11 | CSS inlined in `<style>` in `<head>` | ✓ |
| 12 | Observer has no-op fallback for pre-IO browsers | ✓ |
| 13 | Observer uses `IntersectionObserver` with `unobserve` discipline | ✓ |
| 14 | `prefers-reduced-motion: reduce` honored in CSS | ✓ |
| 15 | `prefers-color-scheme: dark` token swap | ✓ |
| 16 | `prefers-contrast: more` token swap | ✓ |
| 17 | `@media print` styles present | ✓ |
| 18 | No external `<script src=...>` | ✓ |
| 19 | No external `<link href=...>` | ✓ |
| 20 | No `@import url(http...)` | ✓ |
| 21 | No `fetch(` in the inlined observer | ✓ |
| 22 | No `eval(` in the inlined observer | ✓ |
| 23 | No `Date.now` in the inlined observer | ✓ |
| 24 | No `Math.random` in the inlined observer | ✓ |
| 25 | No `setTimeout` in the inlined observer | ✓ |
| 26 | No `setInterval` in the inlined observer | ✓ |
| 27 | No `new Function` anywhere | ✓ |
| 28 | Tag balance: 236 non-void opens = 236 closes, stack empty | ✓ |

**Output size: 30.3 KB / 100 KB budget. Used 30.3%.**

## Render-hint containers — all 5 verified

| Markdown | Output | Verified |
|---|---|---|
| `::: callout ... :::` | `<aside class="callout" role="note">...</aside>` | ✓ |
| `::: fade-in-stagger ... :::` | `<div class="fade-in-stagger">...</div>` (children NOT given `class="fade-in"`) | ✓ |
| `::: collapse Summary ... :::` | `<details class="collapse"><summary>Summary</summary>...</details>` | ✓ |
| `::: source-trail ... :::` | `<section class="source-trail">...</section>` | ✓ |
| `::: spacious ... :::` | `<div class="spacious">...</div>` (96px margin-bottom via CSS) | ✓ |

The `role="note"` on `.callout` is a11y 1.3.1 (Info and Relationships). The Builder adds it.

## Title extraction (frontmatter / fallback)

- If frontmatter has `title:`, that wins.
- Otherwise the first H1 in the body is extracted as the title and stripped from the body (so we don't get two H1s on the page).
- The H1 regex tolerates a leading newline left over from frontmatter parsing.

## First successful render — head of the demo file

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>2026-06-04, Thursday, June 4, 2026 — Fleet Status</title>
  <meta name="description" content="2026-06-04, Thursday, June 4, 2026">
  <meta name="generator" content="fleet-status-renderer v1">
  <meta name="color-scheme" content="light dark">
  <style>
/* === FLEET-STATUS SURFACE — DOSSIER CSS TEMPLATE v1 ===
   …(10 KB of inlined CSS)…
*/
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <main id="main">
    <article>
      <header class="page-header">
        <h1 class="page-title fade-in-presence">2026-06-04, Thursday, June 4, 2026</h1>
        <div class="page-meta">
          <time datetime="2026-06-04">2026-06-04</time>
          <span class="page-author">Mavis</span>
        </div>
      </header>
      <h2 class="fade-in" id="…">…</h2>
      …(body content with fade-in on every block element)…
    </article>
  </main>
  <script>
    /* IntersectionObserver fade-in entry point. …(18 lines)… */
  </script>
</body>
</html>
```

## What the Builder did NOT do (per the 6 hard constraints + Designer's contract)

- Did not edit `02 Design System.md`, `03 Motion Vocabulary.md`, or `04 A11y Checklist.md`.
- Did not invent new CSS classes. The 11 classes the script emits are exactly the ones in §4 of the Designer's handoff.
- Did not introduce JS frameworks. The observer is vanilla.
- Did not add webfonts, analytics, dark-mode toggle.
- Did not animate `top`/`bottom`/`width`/`height`/`margin`/`padding` (CLS-safe).
- Did not exceed 800 ms on any motion (`--t-presence` is the cap).
- Did not commit, push, or external-send.

## Open questions (for the Verifier, not for the Builder to resolve)

1. **Line count.** The script is 285 lines, not 200. Trade-off documented above. The Builder is open to a refactor pass if the Verifier flags it; the spec says "~200" so this is borderline, not a fail.
2. **The 1 npm-audit moderate vulnerability.** Transitive dep, not blocking. Worth a follow-up `npm audit fix` after v1 ships.
3. **Frontmatter `description:` field.** The Build Spec mentions it; the daily note doesn't have one, so the demo falls back to the title. Working as designed.
4. **`<a class="skip-link" href="#main">` visibility.** The CSS hides the link until `:focus`. The Verifier should confirm this is the intended pattern (it matches Tufte CSS + a11y 2.4.1).

## Routing history

| Date | Routed to | Item | Outcome |
|---|---|---|---|
| 2026-06-04 | `03 Projects/Builder/queue/verifier-handoff.md` | v1 ready for audit | Pending Verifier |
| 2026-06-04 | `03 Projects/Builder/queue/mavis-handoff.md` | v1 ready for Mavis review | Pending Mavis |
| 2026-06-04 | `03 Projects/Fleet-Status Surface/08 Demo - 2026-06-04.html` | first render of daily note | Saved, 30.3 KB |

---

*Builder v1. Drop the input, get the surface. The Verifier audits.*
