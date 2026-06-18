---
type: builder-handoff
project: fleet-status-surface
created: 2026-06-04
updated: 2026-06-04
author: designer
status: ready-for-builder
related:
  - "[[00 Overview]]"
  - "[[01 Build Spec]]"
  - "[[02 Design System]]"
  - "[[03 Motion Vocabulary]]"
  - "[[04 A11y Checklist]]"
  - "[[05 CSS Template Draft]]"
  - "[[Researcher/dossiers/dev_tooling/markdown-to-html-ui]]"
  - "[[Researcher/dossiers/harness-engineering]]"
tags: [builder-handoff, fleet-status-surface, mavis-design, m3, render-pipeline]
---

# Builder Handoff — Fleet-Status Surface (Designer's v1)

> **To:** Builder (next dispatched session, sibling agent)
> **From:** Designer (this session)
> **Re:** Design contract for `99 _system/scripts/render-dossier.js` and friends
>
> **TL;DR.** The CSS, motion, a11y, and design system are locked. Drop `05 CSS Template Draft.md` into `templates/dossier.css` verbatim. Add `class="fade-in"` to block-level elements via your render script. Honor `prefers-reduced-motion`. Do not invent new tokens. Open questions at the bottom.
>
> **This is a contract, not a recommendation.** Every value, class, and token in the linked files is buildable as-shipped. If something doesn't fit your script structure, escalate via the queue — don't freelance.

## 1. What you ship

Per the Build Spec §"v1 Scope (in)":

```
99 _system/scripts/
├── render-dossier.js           # ~200-line Node script
├── package.json                # markdown-it + 3 plugins, pinned versions
└── templates/
    ├── dossier.css             # ← THIS HANDOFF'S PRIMARY DELIVERABLE
    ├── observer.js             # IntersectionObserver, ~30 lines
    └── wrapper.html            # <!DOCTYPE> + <head> shell
```

Build artifact (default destination):
```
03 Projects/Fleet-Status Surface/status.html   # or wherever Mavis specifies
```

## 2. The CSS — the implementation

`05 CSS Template Draft.md` is the **drop-in stylesheet** for `templates/dossier.css`. The Builder does *not* add to it. The Builder reads it, inlines it in `<style>` in `<head>`, and ships.

The CSS is **~10KB** uncompressed. The full page budget is < 100KB. The CSS leaves room for the HTML body, the inline observer JS, and the frontmatter.

### 2.1 What the CSS contains (sections, in order)

| Section | Lines | What it does |
|---|---|---|
| Tokens (`:root`) | ~80 | Color, type, spacing, motion, shape. Single source of truth. |
| Dark mode (`prefers-color-scheme: dark`) | ~20 | Token overrides. |
| High contrast (`prefers-contrast: more`) | ~20 | Token overrides. |
| Reset + base | ~20 | Box-sizing, body defaults, image defaults. |
| Skip link | ~10 | a11y 2.4.1 Bypass Blocks. |
| Page header | ~25 | `.page-header`, `.page-title`, `.page-meta`. |
| Main container | ~10 | `article > *:not(.page-header)` measure + padding. |
| Headings | ~25 | H1-H6, visual cap at H3, anchor links. |
| Paragraphs + lists | ~10 | Standard. |
| Blockquote | ~10 | Left-border accent. |
| Code | ~25 | Inline + block. |
| Tables | ~15 | Tufte rules-only style. |
| Links | ~15 | Underlined, hover transitions, focus-visible. |
| Focus + selection | ~10 | `:focus-visible` ring, `::selection`. |
| Render hints | ~50 | `.callout`, `.fade-in-stagger`, `.collapse`, `.source-trail`. |
| Fade-in (the entry) | ~50 | Above-the-fold keyframes, scroll-in transitions, presence, `view()` enhancement. |
| Reduced motion | ~10 | Mandatory fallback (a11y 2.3.1 + WCAG 2.2.2). |
| Footnotes | ~10 | `.footnotes` container. |
| Print | ~15 | White background, no animation, page breaks. |

### 2.2 What the CSS does NOT contain (and why)

- **No webfonts.** The system stack handles it. The 100KB budget cannot carry webfont requests.
- **No drop shadows.** Tufte print discipline. Elevation is background tint.
- **No JS hooks.** The CSS is class-based; the JS reads class names. No `data-*` attributes.
- **No nested selectors > 3 levels deep.** The CSS is intentionally shallow.
- **No dark-mode auto-toggle button.** Dark mode follows the OS preference. The page does not get a "theme switcher." (v2 if Andre wants one.)

## 3. What the render script adds — the contract

The render script's job, in terms of HTML output:

### 3.1 The page-header (from frontmatter)

```html
<header class="page-header">
  <h1 class="page-title fade-in-presence">${title}</h1>
  <div class="page-meta">
    <time datetime="${isoDate}">${humanDate}</time>
    ${authorTag}
  </div>
</header>
```

- The page title is the only `class="fade-in-presence"` element on the page.
- Author: from frontmatter `author:`, default `"Mavis"`.
- Date: from frontmatter `date:`, formatted as ISO + human-readable.

### 3.2 The body (markdown-it output, with three changes)

Your script's three additions to the standard markdown-it HTML:

#### (a) Add `class="fade-in"` to every block-level element

```js
// pseudocode
const blockSelector = 'p, h1, h2, h3, h4, h5, h6, ul, ol, blockquote, pre, table, .callout, .source-trail, .spacious';
html.querySelectorAll(blockSelector).forEach(el => {
  el.classList.add('fade-in');
});
```

Skip elements that are already inside a `.fade-in-stagger` block (those get their stagger treatment from the container, not from `.fade-in`).

#### (b) Translate render hints (markdown-it-container config)

Per the Build Spec §"Render hint syntax." Five hints, each a 4-line config in markdown-it-container:

| Markdown | Output | CSS class |
|---|---|---|
| `::: callout ... :::` | `<aside class="callout fade-in" role="note">...</aside>` | `.callout` |
| `::: fade-in-stagger ... :::` | `<div class="fade-in-stagger">...children... </div>` (children NOT given `class="fade-in"`) | `.fade-in-stagger` |
| `::: collapse ... :::` | `<details class="collapse">...</details>` | `.collapse` |
| `::: source-trail ... :::` | `<section class="source-trail">...</section>` | `.source-trail` |
| `::: spacious ... :::` | `<div class="spacious">...</div>` | `.spacious` (adds 96px margin-bottom) |

The `role="note"` on `.callout` is a11y 1.3.1 (Info and Relationships). The Builder adds it.

#### (c) Add the page-level `<a class="skip-link" href="#main">` and `<main id="main">`

Per a11y 2.4.1. The skip-link is the first element inside `<body>`; `<main id="main">` wraps the article.

### 3.3 The observer (the JS, in `templates/observer.js`)

Per Build Spec: ~30 lines of inline JS, before `</body>`. The Designer's motion vocabulary (`03 Motion Vocabulary.md` §4.2) specifies the exact IO config:

```js
// observer.js (inlined before </body>)
(function () {
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.fade-in, .fade-in-presence, .fade-in-stagger')
      .forEach(el => el.classList.add('is-visible'));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) {
        e.target.classList.add('is-visible');
        io.unobserve(e.target);
      }
    }
  }, { threshold: 0.1, rootMargin: '0px 0px -10% 0px' });
  document.querySelectorAll('.fade-in, .fade-in-presence, .fade-in-stagger')
    .forEach(el => io.observe(el));
})();
```

Notes:
- `unobserve` after first reveal = one-shot. Scrolling back up does not re-trigger.
- `threshold: 0.1` + `rootMargin: '0px 0px -10% 0px'` = element is considered visible when 10% of it is past a 10%-inset viewport bottom. Feels natural; not jumpy.
- Fallback for browsers without `IntersectionObserver` (pre-2019): all `.fade-in` and `.fade-in-stagger` elements get `.is-visible` immediately. Content shows. The fade doesn't happen, but the page works.

### 3.4 The wrapper (`templates/wrapper.html`)

The Builder assembles the final HTML by string concatenation (or template literal) in `render-dossier.js`. The wrapper is:

```html
<!DOCTYPE html>
<html lang="${lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title} — Fleet Status</title>
  <meta name="description" content="${description}">
  <meta name="generator" content="fleet-status-renderer v1">
  <style>
    /* dossier.css inlined here */
  </style>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <main id="main">
    <article>
      ${pageHeader}
      ${body}
    </article>
  </main>
  <script>
    /* observer.js inlined here */
  </script>
</body>
</html>
```

- `<html lang="${lang}">` reads from frontmatter `lang:`, defaults to `en`. a11y 3.1.1.
- `<title>` reads from frontmatter `title:`, falls back to first H1. a11y 2.4.2.
- `<meta name="description">` reads from frontmatter `description:`. SEO + screen reader context.
- No analytics. No third-party scripts. Self-contained.

## 4. Token names — the contract

The Builder's render script does not need to know CSS token names. The CSS is the spec. But for documentation, the render script's HTML output uses these class names (which the CSS already styles):

| CSS class | Where it comes from | Where it goes |
|---|---|---|
| `.page-header`, `.page-title`, `.page-meta` | Builder (from frontmatter) | Around the page title block |
| `.fade-in` | Builder (added to block elements) | Every block-level element |
| `.fade-in-presence` | Builder (added to one element only) | The `<h1 class="page-title">` |
| `.fade-in-stagger` | markdown-it-container (from `:::fade-in-stagger`) | Around staggered children |
| `.callout` | markdown-it-container (from `:::callout`) | The callout block |
| `.collapse` | markdown-it-container (from `:::collapse`) | The `<details>` |
| `.source-trail` | markdown-it-container (from `:::source-trail`) | The source-trail block |
| `.spacious` | markdown-it-container (from `:::spacious`) | Around breath-pause blocks |
| `.skip-link` | Builder (from wrapper) | The first focusable element |
| `.header-anchor` | markdown-it-anchor | Heading anchor links |

The Builder does not pass inline `style="..."`. The CSS is the spec; the HTML is structural.

## 5. The reduced-motion contract

The CSS includes the mandatory fallback. The Builder does **not** write JS to detect reduced motion. The CSS does it. The Builder's only job is to make sure the *content* is fully present in the initial HTML (no JS-dependent content), and that the observer's fallback (no-IO browsers) reveals everything.

**The Verifier will check this.** Open DevTools → Rendering → "Emulate CSS media feature prefers-reduced-motion: reduce" → reload → confirm: all content is immediately visible, no fade, no transition.

## 6. The performance budget (reminder)

| Metric | Target | Source of truth |
|---|---|---|
| Total HTML weight | < 100KB | Build Spec §"Performance budget" |
| CSS weight | < 25KB (we're at ~10KB) | Build Spec §"v1 Scope" |
| FCP (local) | < 200ms | Build Spec |
| LCP (web) | < 2.5s | Web Vitals |
| INP | < 200ms | Web Vitals (v1 has no interactions) |
| CLS | < 0.1 | Web Vitals |
| External requests | 0 | Build Spec |
| Webfont requests | 0 | Build Spec |
| Third-party scripts | 0 | Build Spec |
| Lighthouse a11y | 100/100 | Build Spec §"Acceptance criteria" |
| axe violations | 0 (serious/critical) | A11y Checklist §7 |

## 7. What the Builder does NOT do

- **Does not edit `02 Design System.md`, `03 Motion Vocabulary.md`, or `04 A11y Checklist.md`.** These are the design contracts. If the script needs something not covered, the Builder escalates to the Designer via the queue.
- **Does not invent new CSS classes.** The 11 classes in §4 are the complete set. New needs escalate.
- **Does not introduce JS frameworks.** The observer is vanilla. The script is Node, not React.
- **Does not add webfonts.** The 100KB budget cannot carry them.
- **Does not add analytics.** v1 has no telemetry. (v2 with `web-vitals` RUM if Andre wants it.)
- **Does not add dark mode toggle.** Dark follows OS preference; the page does not get a switcher.
- **Does not animate `top`/`bottom`/`width`/`height`/`margin`/`padding`.** CLS breaks if the script introduces layout-animating properties.
- **Does not exceed 800ms on any motion.** `--t-presence` is the cap.
- **Does not commit, push, or external-send.** Per the 6 hard constraints.

## 8. Open questions (for Mavis, not for the Builder to resolve)

These are choices the Designer made under the future-proofing test bias. The Builder implements them as-specified. Mavis and the Verifier may challenge them. See `02 Design System.md` §6 for the full list.

1. **Sage accent vs. Tufte navy.** Default: sage (`#5c6b4f`). Mavis's call: whisper or speak?
2. **Serif body vs. sans body.** Default: serif. Mavis's call.
3. **The 96px `--space-9` breath.** Default: token is in the palette; author decides per dossier.
4. **`.page-header` reusability for the fleet-status snapshot.** Default: v1 ships one template. v2 specializes.

## 9. Acceptance criteria (Designer's contribution)

The Builder's script + the CSS template together must satisfy:

- [ ] Output HTML is < 100KB uncompressed for a typical 3,000-word dossier
- [ ] No external requests when the file is opened locally
- [ ] FCP < 200ms locally
- [ ] `class="fade-in"` on every block-level element outside `.fade-in-stagger`
- [ ] `class="fade-in-presence"` on **exactly one** element (the page title)
- [ ] `class="page-header"`, `.page-title`, `.page-meta` present and populated from frontmatter
- [ ] `<a class="skip-link" href="#main">` is the first focusable element
- [ ] `<main id="main">` wraps the article
- [ ] `<html lang="...">` is set (a11y 3.1.1)
- [ ] `<title>` is set (a11y 2.4.2)
- [ ] Render hints (`:::callout`, `:::fade-in-stagger`, `:::collapse`, `:::source-trail`, `:::spacious`) translate to the right CSS classes
- [ ] The observer JS is inlined before `</body>`, ~30 lines, with the `unobserve` discipline
- [ ] `prefers-reduced-motion: reduce` → all content immediately visible, no animation
- [ ] `prefers-color-scheme: dark` → tokens swap, contrast still passes
- [ ] `prefers-contrast: more` → tokens swap to high-contrast palette
- [ ] Print preview → white background, no animation, readable

## 10. References (all primary sources or vault docs)

- **Build Spec** — `01 Build Spec.md`. The Builder's primary contract. The Designer's spec is *additional* to this, not a replacement.
- **Design system** — `02 Design System.md`. Token sources, palette math, type scale.
- **Motion vocabulary** — `03 Motion Vocabulary.md`. Timing + easing + entry patterns + reduced motion.
- **A11y checklist** — `04 A11y Checklist.md`. The 26 a11y items the Builder's output must satisfy.
- **CSS template** — `05 CSS Template Draft.md`. The drop-in stylesheet.
- **Researcher dossier** — `03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui.md`. 31 primary sources for the engineering decisions.
- **Researcher dossier (harness)** — `03 Projects/Researcher/dossiers/harness-engineering.md`. The harness pattern the design serves.
- **Harness pattern** — `02 Notes/patterns/agent-harness.md`. The future-proofing test the Designer applied to keep this spec thin.
- **Mavis-as-companion synthesis** — `02 Notes/ideas/mavis-as-companion.md`. The companion-mode framing that re-biases the design language toward warmth + presence.
- **MDN IntersectionObserver** — https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
- **MDN scroll-driven animations** — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll-driven_animations
- **WCAG 2.2** — https://www.w3.org/TR/WCAG22/

---

*Builder handoff, v1. The design contract is locked. Drop the CSS in. Add the class names. Honor reduced motion. Ship the dossier. The Builder owns the script; the Designer owns the surface; the Verifier owns the audit; Mavis owns the dispatch.*
