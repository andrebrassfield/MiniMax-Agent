---
type: design-system
created: 2026-06-04
status: v1-draft
owner: Designer
audience: Builder, Mavis, Scribe, Researcher (all HTML-surface authors)
extends: "[[../dossiers/markdown-to-html-ui]]" (Researcher dossier, the spine)
enforces: "[[../notes/motion-vocabulary]]", "[[../notes/a11y-checklist]]"
implements: "[[../../../03 Projects/Fleet-Status Surface/01 Build Spec]]" (Build Spec v1)
tags: [design-system, typography, color, motion, fleet-status-surface, v1, reusable]
---

# Fleet-Status Design System v1 — Mavis's Human-Facing Surfaces

> **This is the canonical design language for every Mavis HTML surface.** v1 ships against the Fleet-Status Surface build spec; v2 generalizes to dossiers, briefs, weekly syntheses, and dashboards. The Researcher dossier (`markdown-to-html-ui.md`) is the **engineering spine**; this document is the **design muscle** — typography, color, spacing, motion, render-hint syntax. Together they are the contract the Builder implements.

## Design philosophy

Mavis's surface is a **companion surface, not a product surface.** The reading experience should feel like opening a friend's notebook, not opening a SaaS dashboard. Three commitments:

1. **Tufte typography, always.** Off-white paper, off-black ink, generous margins, sidenotes, no chrome. The text is the design.
2. **Fade-in is the only animation.** Content arrives as you scroll. No bouncing, no parallax, no skeleton loaders. The page is alive because it reveals, not because it moves.
3. **The system stack is the only stack.** No webfonts, no framework, no analytics. The file is a single HTML page in the vault, readable offline, openable by double-click.

This is **the opposite of the SaaS dashboard aesthetic.** The pattern is Gwern (philosophical north star), Tufte (implementation), Mavis-archive (the variant where the file IS the artifact, not a chat panel). v1 fills a gap every major AI lab is converging on (Claude Artifacts, ChatGPT Canvas, Perplexity Pages) but with the host being the vault file.

## Hard constraints (from Build Spec v1, do not violate)

- **No webfonts in v1.** System font stack only.
- **No JS framework dependencies.** Pure CSS + vanilla JS. The only JS is the IntersectionObserver block (~30 lines).
- **No external requests.** Self-contained single HTML. CSS inlined in `<head>`, JS inlined before `</body>`.
- **<100KB total HTML weight uncompressed.** Realistic target: 50-80KB for a 3,000-8,000 word dossier.
- **Lighthouse accessibility = 100/100.** See `notes/a11y-checklist.md` for the contract.
- **`prefers-reduced-motion: reduce` honored.** Skip animation, show content immediately.
- **`prefers-color-scheme: dark` supported.** Light is default; dark is opt-in via OS preference.

## Design tokens

All tokens are **CSS custom properties** (variables), declared on `:root`. The Build Spec's `99 _system/scripts/render-dossier.js` should emit them as the first block in the inline `<style>`.

### Typography tokens

```css
:root {
  /* === FONT STACKS === */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui,
               'Helvetica Neue', Arial, sans-serif;
  --font-serif: 'Iowan Old Style', 'Apple Garamond', Baskerville,
                'Times New Roman', 'Droid Serif', Times,
                'Source Serif Pro', serif;
  --font-mono: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas,
               'Liberation Mono', monospace;

  /* === TYPE SCALE (Major Third, 1.250 ratio) === */
  --fs-xs:  0.75rem;   /* 12px — captions, source-trail */
  --fs-sm:  0.875rem;  /* 14px — callouts, sidenotes, table */
  --fs-base: 1rem;     /* 16px — body */
  --fs-md:  1.25rem;   /* 20px — H4 */
  --fs-lg:  1.563rem;  /* 25px — H3 */
  --fs-xl:  1.953rem;  /* 31px — H2 */
  --fs-2xl: 2.441rem;  /* 39px — H1 */

  /* === LINE HEIGHT (leading) === */
  --lh-tight: 1.25;    /* headings */
  --lh-normal: 1.5;    /* body — Tufte canonical */
  --lh-loose: 1.6;     /* code blocks, callouts */

  /* === MEASURE (line length) === */
  --measure: 64ch;     /* body max-width */
  --measure-wide: 80ch;/* for tables, code blocks */

  /* === WEIGHTS === */
  --fw-normal: 400;
  --fw-medium: 500;
  --fw-semibold: 600;
  --fw-bold: 700;

  /* === LETTER-SPACING === */
  --ls-tight: -0.02em;  /* large headings */
  --ls-normal: 0;
  --ls-wide: 0.04em;    /* small caps, all-caps labels */
}
```

**Reading mode swap:** dossiers are text-heavy, so the body should default to serif. Fleet-status and other dashboard surfaces default to sans. The Build Spec's render script can set `data-reading-mode="serif"` on `<article>` to swap; the CSS responds with `article[data-reading-mode="serif"] { --font-body: var(--font-serif); }`.

### Color tokens

```css
:root {
  /* === LIGHT MODE (default) === */
  --color-bg:        #fffff8;  /* Tufte off-white paper */
  --color-bg-alt:    #f8f8f0;  /* sidenote, callout background */
  --color-text:      #111111;  /* Tufte off-black ink */
  --color-text-muted:#555555;  /* source-trail, captions */
  --color-text-faint:#888888;  /* de-emphasized */
  --color-rule:      #d0d0c8;  /* horizontal rules, table borders */
  --color-accent:    #8b0000;  /* Tufte dark red — callouts, links */
  --color-accent-bg: color-mix(in srgb, var(--color-accent) 5%, var(--color-bg));
  --color-link:      #8b0000;
  --color-link-visited: #6b0000;
  --color-focus:     #0066cc;  /* keyboard focus ring — AA contrast on bg */
  --color-code-bg:   #f4f4ec;  /* code block background */
  --color-selection: #ffe066;  /* text selection */

  /* === DARK MODE (opt-in via OS preference) === */
  @media (prefers-color-scheme: dark) {
    :root {
      --color-bg:        #1a1a1a;  /* warm dark, not pure black */
      --color-bg-alt:    #222222;
      --color-text:      #e8e6e0;  /* warm off-white */
      --color-text-muted:#a8a8a0;
      --color-text-faint:#707070;
      --color-rule:      #3a3a3a;
      --color-accent:    #ff6b6b;  /* brighter for dark bg, AA contrast */
      --color-accent-bg: color-mix(in srgb, var(--color-accent) 8%, var(--color-bg));
      --color-link:      #ff6b6b;
      --color-link-visited: #ff9999;
      --color-focus:     #66b3ff;  /* AA contrast on dark bg */
      --color-code-bg:   #242422;
      --color-selection: #4a4a2a;
    }
  }
}
```

**Color discipline:**

- Tufte off-white `#fffff8` and off-black `#111111` are the canonical light-mode anchors. Don't change them.
- The accent color is Tufte's dark red. **AA contrast on `#fffff8`:** `#8b0000` measures 11.4:1 (well above 4.5:1 body / 3:1 large text / 3:1 UI). **AA contrast on `#1a1a1a`:** `#ff6b6b` measures 5.1:1 (above 4.5:1 body).
- Use `color-mix(in srgb, ...)` for tinted backgrounds — it composes correctly with the dark-mode override.
- **No pure black, no pure white.** The off-white and warm-dark reduce eye strain and feel like a book, not a screen.
- **No brand colors in v1.** The accent IS the brand. v2 can add a per-surface accent if Mavis needs visual differentiation.

### Spacing tokens (4px / 8px grid)

```css
:root {
  /* === BASE UNIT === */
  --space-1:  0.25rem;  /* 4px  — xs, micro-gaps */
  --space-2:  0.5rem;   /* 8px  — sm, between related items */
  --space-3:  0.75rem;  /* 12px — md, list-item padding */
  --space-4:  1rem;     /* 16px — lg, paragraph spacing */
  --space-6:  1.5rem;   /* 24px — xl, section spacing */
  --space-8:  2rem;     /* 32px — 2xl, heading-to-content */
  --space-12: 3rem;     /* 48px — 3xl, major section break */
  --space-16: 4rem;     /* 64px — 4xl, page-top padding */

  /* === SEMANTIC SPACING === */
  --gap-inline:   var(--space-4);  /* margin between paragraphs */
  --gap-section:  var(--space-12); /* margin between sections */
  --gap-page:     var(--space-16); /* padding above H1 */

  /* === CONTAINER === */
  --container-padding: clamp(1rem, 4vw, 2rem); /* responsive */
}
```

**Spacing discipline:**

- The grid is **strictly 4px / 8px**. No odd values. If a design needs 13px, use 12px or 16px.
- The `clamp(1rem, 4vw, 2rem)` container-padding is the only responsive spacing token. Below 320px viewport, content gets `1rem` margin; above 1920px, it gets `2rem`. No breakpoint-specific layouts in v1.
- **Vertical rhythm is paragraph-1.5, section-3, page-4.** The 1.5 / 3 / 4 ratio comes from Tufte's "let the type lead" principle — the bigger the break, the bigger the whitespace.

### Motion tokens

```css
:root {
  /* === DURATION === */
  --dur-instant: 100ms;   /* hover, focus ring */
  --dur-fast:    150ms;   /* hover transitions */
  --dur-base:    400ms;   /* above-the-fold entrance */
  --dur-slow:    600ms;   /* below-the-fold reveal */

  /* === EASING === */
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);     /* "Apple spring-out" */
  --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);    /* decelerate hard */
  --ease-in-out:    cubic-bezier(0.4, 0, 0.2, 1);      /* standard */

  /* === STAGGER === */
  --stagger-step: 80ms;  /* between siblings */
  --stagger-cap:  8;     /* max items with full stagger */
  --stagger-decay: 40ms; /* per-item after the cap */
}
```

**Motion discipline:** see `notes/motion-vocabulary.md` for the full vocabulary. The tokens above are the *parameters*. The vocabulary is the *grammar*.

### Render-hint tokens (CSS class names)

The build script translates Pandoc-style fenced divs to elements with these classes. The CSS below is the visual treatment.

```css
/* === RENDER HINT: callout === */
.callout {
  border-left: 4px solid var(--color-accent);
  background: var(--color-accent-bg);
  padding: var(--space-4) var(--space-6);
  margin: var(--gap-section) 0;
  font-size: var(--fs-sm);
}

/* === RENDER HINT: fade-in-stagger === */
.fade-in-stagger > * {
  opacity: 0;
  transform: translateY(8px);
  transition: opacity var(--dur-slow) var(--ease-out-expo),
              transform var(--dur-slow) var(--ease-out-expo);
}
.fade-in-stagger.is-visible > * {
  opacity: 1;
  transform: translateY(0);
}
.fade-in-stagger.is-visible > *:nth-child(1) { transition-delay: 0ms; }
.fade-in-stagger.is-visible > *:nth-child(2) { transition-delay: 80ms; }
.fade-in-stagger.is-visible > *:nth-child(3) { transition-delay: 160ms; }
.fade-in-stagger.is-visible > *:nth-child(4) { transition-delay: 240ms; }
.fade-in-stagger.is-visible > *:nth-child(5) { transition-delay: 320ms; }
.fade-in-stagger.is-visible > *:nth-child(6) { transition-delay: 400ms; }
.fade-in-stagger.is-visible > *:nth-child(7) { transition-delay: 480ms; }
.fade-in-stagger.is-visible > *:nth-child(8) { transition-delay: 560ms; }
/* Beyond 8: 40ms per item (decay) */
.fade-in-stagger.is-visible > *:nth-child(n+9) {
  transition-delay: calc(560ms + (var(--stagger-decay) * (var(--child-index) - 8)));
}

/* === RENDER HINT: collapse === */
.collapse {
  margin: var(--gap-section) 0;
  border: 1px solid var(--color-rule);
  border-radius: 2px;
  padding: var(--space-3) var(--space-4);
}
.collapse > summary {
  cursor: pointer;
  font-weight: var(--fw-medium);
  user-select: none;
}
.collapse > summary:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}
.collapse[open] > summary { margin-bottom: var(--space-3); }

/* === RENDER HINT: source-trail === */
.source-trail {
  margin-top: var(--gap-section);
  padding-top: var(--space-4);
  border-top: 1px solid var(--color-rule);
  font-size: var(--fs-xs);
  color: var(--color-text-muted);
}
.source-trail ol, .source-trail ul { padding-left: 1.5rem; }
.source-trail li { margin-bottom: var(--space-1); }
```

## Element styles

### Headings

```css
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-sans);
  font-weight: var(--fw-semibold);
  line-height: var(--lh-tight);
  letter-spacing: var(--ls-tight);
  margin-top: var(--gap-section);
  margin-bottom: var(--gap-inline);
  color: var(--color-text);
}
h1 { font-size: var(--fs-2xl); margin-top: 0; }
h2 { font-size: var(--fs-xl); }
h3 { font-size: var(--fs-lg); }
h4 { font-size: var(--fs-md); }
h5 { font-size: var(--fs-base); font-weight: var(--fw-bold); }
h6 { font-size: var(--fs-sm);  font-weight: var(--fw-bold); text-transform: uppercase; letter-spacing: var(--ls-wide); }

/* Visual cap: H4-H6 are still semantic but visually de-emphasized to H3 size. */
h4, h5, h6 { font-size: var(--fs-lg); }  /* force visual to H3 size */

/* Progressive enhancement: balance wrapping on large headings. */
@supports (text-wrap: balance) {
  h1, h2, h3 { text-wrap: balance; }
}
```

### Body

```css
body {
  font-family: var(--font-sans);
  font-size: var(--fs-base);
  line-height: var(--lh-normal);
  color: var(--color-text);
  background: var(--color-bg);
  margin: 0;
  padding: var(--container-padding);
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

article[data-reading-mode="serif"] {
  --font-body: var(--font-serif);
  font-family: var(--font-body);
}
```

### Links

```css
a {
  color: var(--color-link);
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 0.2em;
  transition: color var(--dur-fast) var(--ease-in-out);
}
a:hover { color: var(--color-accent); }
a:visited { color: var(--color-link-visited); }
a:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
  border-radius: 2px;
}
```

### Code

```css
code, pre, kbd, samp {
  font-family: var(--font-mono);
  font-size: 0.92em;
  font-variant-ligatures: none;
}
code {
  background: var(--color-code-bg);
  padding: 0.1em 0.3em;
  border-radius: 2px;
}
pre {
  background: var(--color-code-bg);
  padding: var(--space-4);
  border-radius: 2px;
  overflow-x: auto;
  line-height: var(--lh-loose);
  max-width: var(--measure-wide);
}
pre code {
  background: transparent;
  padding: 0;
}
```

### Tables, lists, blockquotes

```css
table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--fs-sm);
  margin: var(--gap-section) 0;
}
th, td {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--color-rule);
}
th { font-weight: var(--fw-semibold); }

ul, ol { padding-left: 1.5rem; margin: var(--gap-inline) 0; }
li { margin-bottom: var(--space-1); }

blockquote {
  border-left: 4px solid var(--color-rule);
  padding-left: var(--space-4);
  margin: var(--gap-section) 0;
  color: var(--color-text-muted);
  font-style: italic;
}
```

## Fade-in animation system

Two layers, both required:

### Layer 1: Above-the-fold pure-CSS animation

```css
@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.fade-in {
  opacity: 0;
  animation: fade-in var(--dur-base) var(--ease-out-expo) forwards;
}

/* Staggered first paint: 5 visible elements max above the fold. */
.fade-in-stagger > .fade-in:nth-child(1) { animation-delay: 0ms; }
.fade-in-stagger > .fade-in:nth-child(2) { animation-delay: 80ms; }
.fade-in-stagger > .fade-in:nth-child(3) { animation-delay: 160ms; }
.fade-in-stagger > .fade-in:nth-child(4) { animation-delay: 240ms; }
.fade-in-stagger > .fade-in:nth-child(5) { animation-delay: 320ms; }
```

### Layer 2: Below-the-fold IntersectionObserver

The JS (inlined before `</body>`, ~30 lines):

```javascript
(function() {
  if (!('IntersectionObserver' in window)) {
    // Fallback: just show everything.
    document.querySelectorAll('.fade-in-stagger').forEach(function(el) {
      el.classList.add('is-visible');
    });
    return;
  }

  // Respect reduced-motion preference.
  var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (prefersReduced) {
    document.querySelectorAll('.fade-in-stagger').forEach(function(el) {
      el.classList.add('is-visible');
    });
    return;
  }

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });

  document.querySelectorAll('.fade-in-stagger').forEach(function(el) {
    observer.observe(el);
  });
})();
```

### Progressive enhancement: scroll-driven animations

```css
@supports (animation-timeline: view()) {
  .fade-in-stagger > * {
    animation: fade-in linear forwards;
    animation-timeline: view();
    animation-range: entry 0% cover 30%;
  }
}
```

This is a no-op in browsers that don't support `animation-timeline: view()` and a *parallel* implementation in browsers that do. Both paths produce the same visual result; the IO + CSS path is the fallback.

## Accessibility contract (full checklist in `notes/a11y-checklist.md`)

The non-negotiables:

- **`<html lang="en">`** (or appropriate) — language set.
- **H1 once per page**, H2-H3 for sections, H4-H6 visually de-emphasized but semantically preserved.
- **Skip-link as the first focusable element** in `<body>`: `<a href="#main" class="skip-link">Skip to content</a>`. CSS: `.skip-link { position: absolute; top: -100px; } .skip-link:focus { top: 0; }`.
- **Focus indicators visible** — `outline: 2px solid var(--color-focus); outline-offset: 2px;` on every focusable element.
- **Color contrast AA** — body text 4.5:1 minimum, large text 3:1, UI components 3:1. All tokens above pass.
- **`prefers-reduced-motion: reduce` honored** — animations skipped, content shown immediately. Both CSS and JS layers enforce this.
- **Image alt text** — every `<img>` has an `alt` attribute (decorative: `alt=""`).
- **Semantic HTML** — `<article>`, `<section>`, `<nav>`, `<header>`, `<footer>`, `<aside>` used appropriately. `<div>` only when no semantic element fits.
- **No ARIA when semantic HTML suffices.** Only use `aria-label`, `aria-describedby`, `aria-current` etc. when the native element lacks the right semantics.

## Performance contract

- **CSS budget: < 30KB uncompressed inline** (the hard ceiling). Realistic: 15-18KB with these tokens.
- **JS budget: < 2KB uncompressed inline** (the IO block + any progressive enhancement). Realistic: 1KB.
- **Total HTML budget: < 100KB uncompressed** (the Build Spec's hard constraint).
- **No external requests.** Self-contained.
- **No webfonts in v1.**
- **No third-party scripts.**

The build script (`99 _system/scripts/render-dossier.js`) should print a warning to stderr at 80% of any budget and a hard fail at 100%.

## Render-hint syntax (Pandoc-style fenced divs)

The build script recognizes four block-level wrappers. Source:

```markdown
::: callout
This is a callout. Mavis's "important note" wrapper.
:::

::: fade-in-stagger
- Item 1
- Item 2
- Item 3
:::

::: collapse
<summary>Click to expand</summary>
Hidden content here. The build script promotes the first line to the `<summary>`.
:::

::: source-trail
- [Source 1](https://...)
- [Source 2](https://...)
:::
```

Output (HTML):

```html
<aside class="callout">This is a callout. Mavis's "important note" wrapper.</aside>

<div class="fade-in-stagger">
  <ul>
    <li>Item 1</li>
    <li>Item 2</li>
    <li>Item 3</li>
  </ul>
</div>

<details class="collapse">
  <summary>Click to expand</summary>
  Hidden content here. The build script promotes the first line to the <summary>.
</details>

<section class="source-trail">
  <ul>
    <li><a href="https://...">Source 1</a></li>
    <li><a href="https://...">Source 2</a></li>
  </ul>
</section>
```

Implementation: 20-line markdown-it core rule using `markdown-it-container`. Each hint is a single config block. The full config is in the CSS template at `scripts/fleet-status.css` and the JS example is in the dossier.

## Reading mode swap (v1 nicety)

The `<article>` element can carry `data-reading-mode="serif"` to switch the body font to the serif stack. The Build Spec's render script sets this for text-heavy dossiers; the default (sans) is for dashboards and fleet-status.

```css
article[data-reading-mode="serif"] {
  --font-body: var(--font-serif);
}
article[data-reading-mode="serif"] p,
article[data-reading-mode="serif"] li,
article[data-reading-mode="serif"] blockquote {
  font-family: var(--font-body);
}
```

## v2 addenda (out of scope for v1)

- Tufte sidenotes (margin notes). Stub class `.sidenote` reserved in CSS.
- View Transitions for cross-page navigation (only when pages-per-dossier is the architecture).
- Webfont support (optional loading via `<link rel="preload" as="font" crossorigin>`).
- Field RUM via `web-vitals` library (LCP / INP / CLS measurement).
- Manual dark-mode toggle (requires JS for state persistence; defer to v2).
- Icon system (none in v1; flag for v2).
- Per-surface accent color (the single accent is enough in v1).

## Reference

- **Source dossier (engineering spine):** `[[../dossiers/markdown-to-html-ui]]`
- **Build Spec v1 (the contract):** `[[../../../03 Projects/Fleet-Status Surface/01 Build Spec]]`
- **Motion vocabulary (the grammar):** `[[../notes/motion-vocabulary]]`
- **A11y checklist (the quality bar):** `[[../notes/a11y-checklist]]`
- **CSS template (the implementation):** `[[../scripts/fleet-status.css]]`
- **Dossier audit (the gap analysis):** `[[../notes/dossier-audit-2026-06-04]]`
- **Tufte CSS:** `edwardtufte.github.io/tufte-css`
- **Gwern.net design philosophy:** `gwern.net/design`

---

*This design system is the canonical design language for every Mavis HTML surface. v1 ships against the Fleet-Status Surface build spec. v2 generalizes to all Mavis outputs. The Builder takes the design system + the CSS template + the motion library + the a11y checklist and ships the renderer.*
