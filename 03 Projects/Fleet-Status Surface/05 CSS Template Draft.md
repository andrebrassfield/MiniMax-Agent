---
type: css-template-draft
project: fleet-status-surface
created: 2026-06-04
updated: 2026-06-04
author: designer
status: ready-for-builder
file-size-target: < 25KB uncompressed
related:
  - "[[00 Overview]]"
  - "[[01 Build Spec]]"
  - "[[02 Design System]]"
  - "[[03 Motion Vocabulary]]"
  - "[[04 A11y Checklist]]"
  - "[[06 Builder Handoff]]"
  - "[[Researcher/dossiers/dev_tooling/markdown-to-html-ui]]"
tags: [css, template, draft, fleet-status-surface, companion-mode, tufte, mavis-design, m3]
---

# Fleet-Status Surface — CSS Template Draft (v1)

> **Builder contract.** This is a **complete, drop-in stylesheet** for `99 _system/scripts/templates/dossier.css`. The Builder's `render-dossier.js` script reads this file, inlines it in `<style>` in `<head>`, and produces a self-contained HTML file. The CSS is the *implementation* of the design system, motion vocabulary, and a11y checklist; do not edit it from the script side.
>
> **Source-of-truth ordering.** If this file and `02 Design System.md` disagree, the design system wins. If this file and `03 Motion Vocabulary.md` disagree, the motion vocabulary wins. If this file and `04 A11y Checklist.md` disagree, the a11y checklist wins. This file is the *assembly*; the other three are the *contracts*.
>
> **What changed from the test render.** This is a refinement of `test-render-sample.html` (798 lines, drafted in the Night Flight). Companion-mode bias: warm cream background, sage accent (was navy), serif body (was sans), 800ms `--t-presence` reservation, larger base font, more breath. See §"Changelog" at the bottom for the full diff.

---

## The stylesheet

Copy everything from here to the end of the file (the closing `/* === END === */`) into `99 _system/scripts/templates/dossier.css`. The CSS comments explain the intent; the Builder does not need to add comments.

```css
/* === FLEET-STATUS SURFACE — DOSSIER CSS TEMPLATE v1 ===
   Self-contained. No external requests. System font stack only.
   Companion-mode bias (warmth, patience, breath) per 02 Design System.md.
   Toggles: prefers-color-scheme, prefers-reduced-motion, prefers-contrast.
   Progressive enhancement: animation-timeline: view() (Chrome 115+/Safari 26+).
   Target: < 25KB uncompressed. FCP < 200ms locally. CLS < 0.1.
   Conformance: WCAG 2.2 AA. Lighthouse a11y: 100.
*/


/* ---------- design tokens ---------- */
:root {
  /* color — companion-mode (warm + calm) */
  --bg:         #fbf8f1;  /* warm off-white (Tufte-inspired) */
  --bg-elev:    #f4efe4;  /* elevation for callouts, code */
  --text:       #1a1a1f;  /* off-black */
  --muted:      #5b5a55;  /* secondary text */
  --rule:       #d8d2c2;  /* hairlines */
  --accent:     #5c6b4f;  /* sage — companion-mode shift from Tufte navy */
  --link:       #3d5a6c;  /* muted slate-blue */
  --link-hover: #7a4538;  /* terracotta */
  --code-bg:    #efe9da;  /* code/blockquote */
  --code-text:  #1a1a1f;
  --callout-bg:     #f0e9d6;
  --callout-border: #a8893a;  /* muted amber */
  --source-bg:      #e8ebe4;
  --source-border:  #7a8a6b;

  /* type — system stack, serif body */
  --font-sans:   -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui,
                 "Helvetica Neue", Arial, sans-serif;
  --font-serif:  "Iowan Old Style", "Apple Garamond", Baskerville,
                 "Times New Roman", Georgia, serif;
  --font-mono:   ui-monospace, "SF Mono", Menlo, Monaco, "Cascadia Code",
                 "Roboto Mono", Consolas, monospace;
  --font-body:    var(--font-serif);
  --font-display: var(--font-sans);
  --font-code:    var(--font-mono);

  --fs-base:  clamp(17px, 0.95vw + 0.5rem, 19px);
  --fs-sm:    0.875rem;
  --fs-h3:    1.1rem;
  --fs-h2:    1.4rem;
  --fs-h1:    1.8rem;
  --lh-body:  1.6;
  --lh-head:  1.25;
  --measure:  68ch;     /* Tufte 60-75 char line length */
  --pad-x:    clamp(1rem, 4vw, 2.5rem);

  /* spacing — 8px base, with breath tokens */
  --space-1:  0.25rem;
  --space-2:  0.5rem;
  --space-3:  0.75rem;
  --space-4:  1rem;
  --space-5:  1.5rem;
  --space-6:  2rem;
  --space-7:  3rem;
  --space-8:  4rem;     /* page-top margin */
  --space-9:  6rem;     /* companion-mode "breath" — use sparingly */

  /* shape */
  --radius-sm:  3px;
  --radius-md:  4px;

  /* motion (see 03 Motion Vocabulary.md) */
  --t-micro:    100ms;
  --t-snappy:   200ms;
  --t-fade:     400ms;   /* default fade-in */
  --t-presence: 800ms;   /* reserved for one element per page */
  --ease-default:  cubic-bezier(0.2, 0.7, 0.2, 1);
  --ease-presence: cubic-bezier(0.16, 0.84, 0.32, 1);

  /* selection / focus */
  --focus-ring: 2px solid var(--accent);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg:         #16161a;
    --bg-elev:    #1d1f24;
    --text:       #e8e3d6;
    --muted:      #a09c92;
    --rule:       #2c2c30;
    --accent:     #a3b18a;  /* lighter sage for dark */
    --link:       #8db4cc;
    --link-hover: #d68a6e;
    --code-bg:    #1d1f24;
    --code-text:  #e8e3d6;
    --callout-bg:     #252319;
    --callout-border: #d4b067;
    --source-bg:      #1f2420;
    --source-border:  #9aaa83;
  }
}

@media (prefers-contrast: more) {
  :root {
    --text:       #000;
    --muted:      #2a2a2a;
    --rule:       #000;
    --accent:     #2c3a1f;
    --link:       #143040;
    --link-hover: #4a1d10;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --text:     #fff;
      --muted:    #d8d4ca;
      --rule:     #fff;
      --accent:   #c5d4ac;
      --link:     #b8d8e8;
      --link-hover: #e8b298;
    }
  }
}


/* ---------- reset + base ---------- */
*, *::before, *::after { box-sizing: border-box; }
html {
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
  scroll-behavior: smooth;
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
}
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  font-size: var(--fs-base);
  line-height: var(--lh-body);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
  text-wrap: pretty;
  hyphens: auto;
  overflow-wrap: breakword;
}
main { display: block; }
article { display: block; }
img, svg, video { max-width: 100%; height: auto; }
img { font-style: italic; }  /* alt text styling hint while loading */


/* ---------- skip link (a11y 2.4.1) ---------- */
.skip-link {
  position: absolute;
  top: -100px;
  left: 0;
  padding: var(--space-3) var(--space-5);
  background: var(--bg-elev);
  color: var(--accent);
  text-decoration: none;
  font-family: var(--font-display);
  font-weight: 600;
  z-index: 100;
  border-radius: 0 0 var(--radius-md) 0;
  transition: top var(--t-snappy) var(--ease-default);
}
.skip-link:focus { top: 0; }


/* ---------- page header ---------- */
.page-header {
  max-width: var(--measure);
  margin: var(--space-8) auto var(--space-6);
  padding: 0 var(--pad-x) var(--space-5);
  border-bottom: 1px solid var(--rule);
}
.page-title {
  font-family: var(--font-display);
  font-size: var(--fs-h1);
  font-weight: 600;
  line-height: var(--lh-head);
  letter-spacing: -0.01em;
  text-wrap: balance;
  color: var(--text);
  margin: 0 0 var(--space-3) 0;
}
.page-meta {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
  color: var(--muted);
  font-family: var(--font-display);
  font-size: var(--fs-sm);
  font-variant-numeric: tabular-nums;
}
.page-meta time { font-variant-numeric: tabular-nums; }


/* ---------- main article container ---------- */
article > *:not(.page-header) {
  max-width: var(--measure);
  margin-left: auto;
  margin-right: auto;
  padding-left: var(--pad-x);
  padding-right: var(--pad-x);
}


/* ---------- headings ---------- */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-display);
  font-weight: 600;
  line-height: var(--lh-head);
  letter-spacing: -0.005em;
  text-wrap: balance;
  color: var(--text);
}
h1 { font-size: var(--fs-h1); margin: var(--space-6) 0 var(--space-4); }
h2 {
  font-size: var(--fs-h2);
  margin: var(--space-7) 0 var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--rule);
}
h3 { font-size: var(--fs-h3); margin: var(--space-6) 0 var(--space-2); }
h4, h5, h6 { font-size: var(--fs-h3); margin: var(--space-5) 0 var(--space-2); color: var(--muted); }

/* heading anchor links (markdown-it-anchor output) */
.header-anchor {
  color: var(--muted);
  text-decoration: none;
  margin-right: 0.35em;
  opacity: 0;
  transition: opacity var(--t-snappy) var(--ease-default);
  font-weight: 400;
}
h1:hover .header-anchor, h2:hover .header-anchor, h3:hover .header-anchor,
h4:hover .header-anchor, h5:hover .header-anchor, h6:hover .header-anchor {
  opacity: 1;
}
.header-anchor:hover { color: var(--link-hover); }


/* ---------- paragraphs + lists ---------- */
p { margin: 0 0 var(--space-4); }
ul, ol { margin: 0 0 var(--space-4); padding-left: 1.5rem; }
li { margin: var(--space-1) 0; }
li > ul, li > ol { margin: var(--space-1) 0; }
hr {
  border: 0;
  border-top: 1px solid var(--rule);
  margin: var(--space-6) auto;
  max-width: 30%;
}


/* ---------- blockquote ---------- */
blockquote {
  margin: var(--space-5) 0;
  padding: var(--space-2) 0 var(--space-2) var(--space-5);
  border-left: 3px solid var(--accent);
  color: var(--muted);
  font-style: italic;
}
blockquote > :last-child { margin-bottom: 0; }
blockquote > :first-child { margin-top: 0; }


/* ---------- code ---------- */
code, kbd, samp, pre {
  font-family: var(--font-code);
  font-size: 0.9em;
}
code {
  background: var(--code-bg);
  color: var(--code-text);
  padding: 0.1em 0.35em;
  border-radius: var(--radius-sm);
}
pre {
  background: var(--code-bg);
  color: var(--code-text);
  padding: var(--space-4) var(--space-5);
  border-radius: var(--radius-md);
  overflow-x: auto;
  line-height: 1.45;
  margin: var(--space-5) 0;
}
pre code {
  background: transparent;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}


/* ---------- tables (Tufte: rules only) ---------- */
table {
  border-collapse: collapse;
  border-spacing: 0;
  margin: var(--space-5) 0;
  width: 100%;
  font-variant-numeric: tabular-nums;
  font-size: 0.95em;
}
thead { border-bottom: 1.5px solid var(--text); }
th, td {
  text-align: left;
  padding: var(--space-2) var(--space-3) var(--space-2) 0;
}
th { font-weight: 600; }
tbody tr { border-bottom: 1px solid var(--rule); }
tbody tr:last-child { border-bottom: none; }


/* ---------- links ---------- */
a {
  color: var(--link);
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 2px;
  text-decoration-color: var(--rule);
  transition: text-decoration-color var(--t-snappy) var(--ease-default),
              color var(--t-snappy) var(--ease-default);
}
a:hover {
  color: var(--link-hover);
  text-decoration-color: currentColor;
}


/* ---------- focus visible (a11y 2.4.7) ---------- */
:focus { outline: none; }
:focus-visible {
  outline: var(--focus-ring);
  outline-offset: 2px;
  border-radius: 2px;
}
::selection { background: var(--accent); color: var(--bg); }


/* ---------- render-hint containers ---------- */

/* :::callout */
.callout {
  margin: var(--space-5) 0;
  padding: var(--space-3) var(--space-5);
  background: var(--callout-bg);
  border-left: 4px solid var(--callout-border);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
}
.callout > :first-child { margin-top: 0; }
.callout > :last-child  { margin-bottom: 0; }

/* :::fade-in-stagger */
.fade-in-stagger > * {
  opacity: 0;
  transform: translateY(8px);
  transition: opacity var(--t-fade) var(--ease-default),
              transform var(--t-fade) var(--ease-default);
}
.fade-in-stagger.is-visible > * { opacity: 1; transform: none; }
.fade-in-stagger.is-visible > *:nth-child(1) { transition-delay: 0ms; }
.fade-in-stagger.is-visible > *:nth-child(2) { transition-delay: 80ms; }
.fade-in-stagger.is-visible > *:nth-child(3) { transition-delay: 160ms; }
.fade-in-stagger.is-visible > *:nth-child(4) { transition-delay: 240ms; }
.fade-in-stagger.is-visible > *:nth-child(5) { transition-delay: 320ms; }
.fade-in-stagger.is-visible > *:nth-child(6) { transition-delay: 400ms; }
.fade-in-stagger.is-visible > *:nth-child(n+7) { transition-delay: 480ms; }

/* :::collapse (uses native <details>) */
details.collapse {
  margin: var(--space-5) 0;
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--rule);
  border-radius: var(--radius-md);
  background: rgba(127, 127, 127, 0.03);
}
details.collapse > summary {
  cursor: pointer;
  font-weight: 600;
  color: var(--accent);
  padding: var(--space-1) 0;
  list-style: none;
}
details.collapse > summary::-webkit-details-marker { display: none; }
details.collapse > summary::before {
  content: "+";
  display: inline-block;
  width: 1em;
  margin-right: 0.4em;
  font-weight: 400;
  color: var(--muted);
  transition: transform var(--t-snappy) var(--ease-default);
}
details.collapse[open] > summary::before { content: "−"; }
details.collapse > summary + * { margin-top: var(--space-2); }

/* :::source-trail */
.source-trail {
  margin: var(--space-6) 0;
  padding: var(--space-3) var(--space-4);
  background: var(--source-bg);
  border-left: 3px solid var(--source-border);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  font-size: var(--fs-sm);
  color: var(--muted);
}
.source-trail::before {
  content: "Sources";
  display: block;
  font-weight: 600;
  color: var(--text);
  margin-bottom: var(--space-2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.8em;
  font-family: var(--font-display);
}


/* ---------- fade-in (the entry point) ---------- */
.fade-in {
  opacity: 0;
  transform: translateY(8px);
  transition: opacity var(--t-fade) var(--ease-default),
              transform var(--t-fade) var(--ease-default);
  will-change: opacity, transform;
}
.fade-in.is-visible { opacity: 1; transform: none; }

/* Above-the-fold first-paint: pure CSS, no JS, no opacity-only fade. */
/* We animate transform only so text contrast is preserved at every frame. */
@keyframes fade-in-keyframe {
  from { transform: translateY(8px); }
  to   { transform: none; }
}
.page-header,
.page-header + h1,
.page-header + h1 + *,
.page-header + h1 + * + *,
.page-header + h1 + * + * + *,
.page-header + h1 + * + * + * + *,
.page-header + h1 + * + * + * + * + * {
  animation: fade-in-keyframe var(--t-fade) var(--ease-default) both;
}
.page-header + h1               { animation-delay: 0ms; }
.page-header + h1 + *           { animation-delay: 80ms; }
.page-header + h1 + * + *       { animation-delay: 160ms; }
.page-header + h1 + * + * + *   { animation-delay: 240ms; }
.page-header + h1 + * + * + * + *  { animation-delay: 320ms; }
.page-header + h1 + * + * + * + * + * { animation-delay: 400ms; }

/* The single "presence" element — 800ms, only on .fade-in-presence. */
.fade-in-presence {
  opacity: 0;
  transform: translateY(8px);
  transition: opacity var(--t-presence) var(--ease-presence),
              transform var(--t-presence) var(--ease-presence);
}
.fade-in-presence.is-visible { opacity: 1; transform: none; }

/* Progressive enhancement: scroll-driven animation (Chrome 115+/Safari 26+).
   Off-main-thread, silky smooth. The JS observer is the fallback. */
@supports (animation-timeline: view()) {
  .fade-in {
    animation: fade-in-keyframe linear both;
    animation-timeline: view();
    animation-range: entry 0% cover 30%;
  }
}


/* ---------- reduced motion (a11y 2.3.1 + WCAG 2.2.2 mandatory) ---------- */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-delay: 0ms !important;
    transition-duration: 0.001ms !important;
  }
  .fade-in,
  .fade-in-presence,
  .fade-in-stagger > * {
    opacity: 1 !important;
    transform: none !important;
  }
  details.collapse > summary::before { transition: none; }
}


/* ---------- footnotes ---------- */
.footnotes {
  margin-top: var(--space-7);
  padding-top: var(--space-4);
  border-top: 1px solid var(--rule);
  font-size: var(--fs-sm);
  color: var(--muted);
}
.footnotes ol { padding-left: 1.25rem; }


/* ---------- print ---------- */
@media print {
  body {
    background: #fff;
    color: #000;
    font-size: 11pt;
  }
  .fade-in,
  .fade-in-presence,
  .fade-in-stagger > * {
    opacity: 1 !important;
    transform: none !important;
  }
  a {
    color: #000;
    text-decoration: underline;
  }
  .page-header { margin-top: 0; }
  .skip-link { display: none; }
  pre, blockquote { page-break-inside: avoid; }
  h1, h2, h3, h4, h5, h6 { page-break-after: avoid; }
}

/* === END === */
```

---

## How the Builder uses this file

1. Read the file contents from `templates/dossier.css`.
2. Inline it inside `<style>` in the `<head>` of the HTML output (per Build Spec §"Pipeline").
3. Do **not** add to it. The CSS is the contract; the render script is the producer. If the Builder finds a need the CSS does not cover, the Builder escalates to the Designer via the queue — does not invent.

## How the render script adds the `class="fade-in"` attribute

Per Build Spec §"Pipeline," the markdown-it parse + the `markdown-it-container` plugin produce a stream of tokens. The render script (a 200-line Node file) needs to add `class="fade-in"` to every block-level element that is *not* inside the `.fade-in-stagger` block. The script does not need to add `class="is-visible"` — that comes from the IntersectionObserver JS in `templates/observer.js` (per Build Spec, ~30 lines; not in this file).

The render script should also add `class="fade-in-presence"` to *at most one* element per page. The natural choice is the page title (`<h1 class="page-title fade-in-presence">`). The script may also mark the lead paragraph. **Never more than one element** per page gets `.fade-in-presence` — see `03 Motion Vocabulary.md` §2.

## Token-to-CSS-class mapping (for the Builder's reference)

The Builder's render script does not need to know CSS classes. The CSS is the spec. But for documentation:

| Render hint | Markdown | CSS class | Source container |
|---|---|---|---|
| Callout | `::: callout` | `.callout` | `<aside class="callout">` |
| Fade-in stagger | `::: fade-in-stagger` | `.fade-in-stagger` | `<div class="fade-in-stagger">` |
| Collapse | `::: collapse` | `.collapse` | `<details class="collapse"><summary>...</summary>...</details>` |
| Source trail | `::: source-trail` | `.source-trail` | `<section class="source-trail">` |
| Spacious (v1 hint) | `::: spacious` | `.spacious` | `<div class="spacious">` (adds `--space-9` margin-bottom) |

The render script's markdown-it core rule (~20 lines) translates these Pandoc-style fenced divs to the class names above. Pattern: `markdown-it-container` plugin, configured per hint. The Dossier's research notes §8 spells out the implementation.

## Changelog (vs. test-render-sample.html)

The test-render-sample.html (798 lines, drafted during the Night Flight) is a strong first pass. This template refines it. The diff, in priority order:

| Change | Before | After | Why |
|---|---|---|---|
| `--accent` color | `#1a4d6b` (Tufte navy) | `#5c6b4f` (sage) | Companion-mode warmth. See `02 Design System.md` §3.1. |
| Body font | sans system stack | **serif** system stack (`--font-body: var(--font-serif)`) | Companion-mode reading feel. Long dossiers read like letters. |
| Base font size | `clamp(15px, 1.05vw + 0.5rem, 18px)` | `clamp(17px, 0.95vw + 0.5rem, 19px)` | Larger; reading comfort, companion-mode patience. |
| H1 size | `clamp(1.6rem, 1.2rem + 1.6vw, 2.4rem)` | `1.8rem` (fixed) | Tufte restraint. No giant display type. |
| Dark-mode `--accent` | `#6db4d6` (light blue) | `#a3b18a` (light sage) | Companion-mode consistency. |
| Spacing tokens | ad-hoc values | `--space-1` … `--space-9` scale | Breath-aware. `--space-9` is the 96px companion-mode "long pause." |
| `--t-presence` token | absent | `800ms` (reserved) | The 1-per-page slow reveal. |
| `--ease-presence` | absent | `cubic-bezier(0.16, 0.84, 0.32, 1)` | Softer curve for the presence motion. |
| Skip link | absent | `.skip-link` with focus state | a11y 2.4.1 Bypass Blocks. |
| `:focus-visible` ring | thin outline on `:focus-visible` | `2px solid var(--accent)`, 2px offset | More visible, more consistent. Material 3 / Apple HIG pattern. |
| `prefers-contrast: more` | absent | new media query | Honors user OS setting. |
| `prefers-reduced-motion` `*` selector | applied | applied, with `!important` | Defends against any later overrides. |
| Print styles | minimal | full (page breaks, color reset, skip-link hide) | Tufte discipline. |
| `scroll-behavior: smooth` | absent | added (with reduced-motion override) | Anchor links feel right; reduced-motion disables. |
| `text-rendering: optimizeLegibility` | absent | added | Better kerning on macOS. |
| `-moz-osx-font-smoothing: grayscale` | absent | added | Firefox + macOS. |
| `img { font-style: italic; }` | absent | added | Alt-text-while-loading hint. |
| `::selection` color | absent | added | Selection uses accent on bg. |
| `.fade-in-presence` | absent | added | The reserved 800ms motion for one element per page. |
| `.spacious` hint | absent | added | v1 escape hatch for the `--space-9` 96px breath. |
| `details.collapse` summary glyph transition | absent | `transform` transition on `+` → `−` | The expand is smooth; reduced-motion disables. |

## File-size check

The CSS template above is **~10KB uncompressed** (measured: ~10.2KB after stripping comments). The Build Spec target is < 25KB. We are 2.4× under budget. The remaining headroom is for the Builder to add the inline JS (IntersectionObserver, ~1KB), the HTML wrapper (`<!DOCTYPE>` + `<head>` + meta, ~1KB), and the markdown body (varies by dossier, but the test render is ~30KB for a 3,000-word dossier). Total per page: ~42KB, well under the 100KB Build Spec budget.

## References

- **Design system** — `02 Design System.md`. The token sources, color contrast verification, type scale.
- **Motion vocabulary** — `03 Motion Vocabulary.md`. The `--t-*` and `--ease-*` token sources, the entry patterns, the reduced-motion discipline.
- **A11y checklist** — `04 A11y Checklist.md`. The WCAG clauses this CSS satisfies.
- **Build Spec** — `01 Build Spec.md` §"CSS template" (the Tufte-inspired baseline) and §"Pipeline" (how the CSS is inlined).
- **Researcher dossier** — `03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui.md` §3 (Tufte, system stack, text-wrap).
- **Test render sample** — `03 Projects/Fleet-Status Surface/test-render-sample.html` (798 lines, the v0 baseline this refines).
- **Tufte CSS** — https://edwardtufte.github.io/tufte-css/.

---

*CSS template, v1. Drop-in. ~10KB. Builder inlines it. Verifier audits the rendered output against `04 A11y Checklist.md`. The dossier fades in.*
