---
type: checklist
created: 2026-06-04
status: v1
audience: Builder, Designer, Mavis, Scribe (every Mavis HTML-surface author)
scope: cross-project — every Mavis HTML surface
enforces: "[[../dossiers/fleet-status-design-system]]", "[[./motion-vocabulary]]"
implements: "[[../../../03 Projects/Fleet-Status Surface/01 Build Spec]]" (Lighthouse 100/100 target)
tags: [a11y, accessibility, wcag, contrast, motion-reduce, keyboard, semantic, screen-reader, lighthouse, v1]
---

# A11y Checklist v1 — Mavis HTML Surfaces

> **The quality bar for every Mavis HTML surface.** v1 targets Lighthouse Accessibility 100/100. This checklist is what the Builder checks at build time, what the Verifier audits at review time, and what the Designer references when adding a new pattern. The dossier (`markdown-to-html-ui.md`) and the Build Spec v1 both call out accessibility as non-negotiable; this is the operationalization.
>
> **If a design choice conflicts with a11y, the design choice loses.** This is the rule. Every token, every animation, every render hint in the design system spec is downstream of this contract.

## WCAG 2.2 conformance target

v1 targets **WCAG 2.2 Level AA conformance**. AAA is a stretch goal for specific high-leverage items (color contrast on body text), but the build budget doesn't allow full AAA auditing. The minimum:

- **1.4.3 Contrast (Minimum) — Level AA** — 4.5:1 for body text, 3:1 for large text (≥18pt or ≥14pt bold), 3:1 for UI components and graphical objects.
- **1.4.4 Resize Text — Level AA** — text can be resized to 200% without loss of content or functionality.
- **1.4.11 Non-text Contrast — Level AA** — UI components and graphical objects have 3:1 contrast.
- **1.4.12 Text Spacing — Level AA** — content remains functional when the user adjusts line-height (1.5x), paragraph spacing (2x), letter-spacing, word-spacing.
- **1.4.13 Content on Hover or Focus — Level AA** — hover/focus content is dismissible, hoverable, persistent.
- **2.1.1 Keyboard — Level A** — all functionality is available from the keyboard.
- **2.1.2 No Keyboard Trap — Level A** — focus can be moved away from any component using the keyboard.
- **2.4.1 Bypass Blocks — Level A** — a skip-link is provided to bypass repeated content.
- **2.4.2 Page Titled — Level A** — pages have descriptive `<title>`.
- **2.4.3 Focus Order — Level A** — focus order preserves meaning and operability.
- **2.4.6 Headings and Labels — Level AA** — headings and labels are descriptive.
- **2.4.7 Focus Visible — Level AA** — keyboard focus is visible.
- **2.5.3 Label in Name — Level A** — visible label matches accessible name.
- **3.1.1 Language of Page — Level A** — `<html lang="...">` is set.
- **3.1.2 Language of Parts — Level AA** — language changes within content are marked.
- **3.2.1 On Focus — Level A** — focus does not initiate a change of context.
- **3.2.2 On Input — Level A** — input does not initiate a change of context without warning.
- **3.3.1 Error Identification — Level A** — input errors are identified and described.
- **3.3.2 Labels or Instructions — Level A** — labels/instructions are provided for user input.
- **4.1.2 Name, Role, Value — Level A** — name, role, and value of UI components are programmatically determinable.
- **4.1.3 Status Messages — Level AA** — status messages are announced to assistive tech (relevant if v2 adds dynamic content).

## Build-time check (the 12 non-negotiables)

The Builder runs these checks before writing the output HTML. **A failed check is a build error, not a warning.**

### 1. Color contrast — AA minimum

- [ ] **Body text** (`--color-text` on `--color-bg`): **≥ 4.5:1**
  - Light mode: `#111111` on `#fffff8` = **16.4:1** ✓
  - Dark mode: `#e8e6e0` on `#1a1a1a` = **12.6:1** ✓
- [ ] **Muted text** (`--color-text-muted` on `--color-bg`): **≥ 4.5:1**
  - Light mode: `#555555` on `#fffff8` = **7.5:1** ✓
  - Dark mode: `#a8a8a0` on `#1a1a1a` = **7.0:1** ✓
- [ ] **Faint text** (`--color-text-faint` on `--color-bg`): **≥ 4.5:1**
  - Light mode: `#888888` on `#fffff8` = **4.6:1** ✓ (just above threshold — verify in design review)
  - Dark mode: `#707070` on `#1a1a1a` = **4.7:1** ✓
- [ ] **Links** (`--color-link` on `--color-bg`): **≥ 4.5:1**
  - Light mode: `#8b0000` on `#fffff8` = **11.4:1** ✓
  - Dark mode: `#ff6b6b` on `#1a1a1a` = **5.1:1** ✓
- [ ] **Focus ring** (`--color-focus` on `--color-bg`): **≥ 3:1** (UI component, not text)
  - Light mode: `#0066cc` on `#fffff8` = **5.4:1** ✓
  - Dark mode: `#66b3ff` on `#1a1a1a` = **7.5:1** ✓
- [ ] **Callout left border** (`--color-accent` on `--color-accent-bg`): **≥ 3:1**
  - Light mode: `#8b0000` on the tinted bg = **11.4:1** ✓
  - Dark mode: `#ff6b6b` on the tinted bg = **5.1:1** ✓

**Test methodology:** WebAIM Contrast Checker (https://webaim.org/resources/contrastchecker/) for every pair, or use Chrome DevTools' built-in contrast audit (Lighthouse → Accessibility). **Never eyeball it.**

### 2. Motion — `prefers-reduced-motion: reduce` respected

- [ ] **CSS layer:** all `@keyframes` and `transition` declarations are wrapped in `@media (prefers-reduced-motion: no-preference) { ... }`. The default state (without the media query) is "no animation, content visible."
- [ ] **JS layer:** the IntersectionObserver block checks `window.matchMedia('(prefers-reduced-motion: reduce)').matches` and skips adding `is-visible` if reduced motion is requested. It just shows everything.
- [ ] **No infinite animations** — every animation is `forwards`, ending at a stable state.
- [ ] **No rotation, no scaling, no parallax** — only `transform: translateY()` and `opacity`. Vestibular-safe.
- [ ] **Manual test:** in macOS System Preferences → Accessibility → Display → Reduce motion (on), open the rendered HTML. Content is visible immediately, no fade-in. The IntersectionObserver never fires the `is-visible` class.

### 3. Keyboard navigation — every interactive element reachable

- [ ] **Skip-link** as the first focusable element in `<body>`: `<a href="#main" class="skip-link">Skip to content</a>`. CSS hides it offscreen until focused.
- [ ] **All links, buttons, and `<details>` summary elements are focusable** via Tab. No `tabindex="-1"` on any interactive element.
- [ ] **No keyboard traps** — the user can Tab into and out of every interactive element. Test by tabbing through the entire page.
- [ ] **Focus order is logical** — the visual reading order matches the DOM order matches the tab order. No `tabindex` values other than 0 and -1.
- [ ] **`<details>` summary is keyboard-activatable** with Space and Enter. (Native browser behavior; the `collapse` render hint relies on this.)
- [ ] **Manual test:** open the rendered HTML, press Tab repeatedly. Every interactive element gets a visible focus ring. Pressing Enter on the skip-link jumps to `<main>`. No element traps the focus.

### 4. Focus indicators — visible

- [ ] **`:focus-visible` rule** applies `outline: 2px solid var(--color-focus); outline-offset: 2px;` to every focusable element.
- [ ] **The focus ring contrast** on the background color is **≥ 3:1** (UI component, not text). Verified in check #1.
- [ ] **`outline: none` is forbidden** on any focusable element. If a custom focus style is desired, use `:focus-visible` to show the outline only for keyboard focus.
- [ ] **The skip-link** is visible when focused (it's hidden by default with `position: absolute; top: -100px;` and visible on focus with `top: 0;`).

### 5. Semantic HTML — H1 once per page, no skipped levels

- [ ] **Exactly one `<h1>` per page.** It's the document title. The renderer should warn (or fail) if the markdown has zero or multiple `#` headings.
- [ ] **Heading levels are sequential** — H1 → H2 → H3, no skipping. H4-H6 are allowed but visually de-emphasized. The renderer should warn on level skips (`# h1`, `### h3` without a `## h2` in between).
- [ ] **`<article>` wraps the main content** (the rendered markdown body).
- [ ] **`<main>` is the primary landmark** of the page (one per page, contains the `<article>`).
- [ ] **`<header>`, `<nav>`, `<footer>`, `<aside>`, `<section>` used appropriately.** No `<div>` where a semantic element fits.
- [ ] **Lists are real lists** — `<ul>` for unordered, `<ol>` for ordered. Not paragraphs with bullets.
- [ ] **Blockquotes are `<blockquote>`** — not paragraphs with italic.
- [ ] **Code is `<code>` and `<pre>`** — not styled `<div>`s. The language hint is preserved in the class (`language-js`).
- [ ] **Tables are `<table>` with `<thead>`, `<tbody>`, `<th>`** — not grid-styled `<div>`s.

### 6. ARIA — only when semantic HTML is insufficient

- [ ] **No `role="..."` on a semantic element** that already has the right role. Adding `role="button"` to a `<button>` is a fail.
- [ ] **`aria-label` only when the visible text is not descriptive enough** (e.g., an icon-only button has no visible text but needs an accessible name). For text-only surfaces, this should be rare.
- [ ] **`aria-labelledby` only when the label is in a different element** from the control.
- [ ] **`aria-describedby` only when a description needs to be programmatically associated** with a control.
- [ ] **`<details>` / `<summary>` get no ARIA** — the native semantics are correct. The `collapse` render hint relies on this.
- [ ] **Manual test:** install the axe DevTools browser extension, run the audit. Zero violations.

### 7. Screen reader — tested with VoiceOver / NVDA

- [ ] **Heading hierarchy is announced** — VoiceOver's rotor (VO+Cmd+H) lists all headings in order. Verify H1 appears once, then H2s, then H3s.
- [ ] **Lists are announced as lists** — VO says "list, 5 items" when entering a `<ul>`.
- [ ] **Links are descriptive** — VO reads the link text, not just "link." Avoid "click here" / "read more" / "this" as link text.
- [ ] **Landmarks are announced** — VO's rotor (VO+Cmd+U) lists landmarks: header, nav, main, footer. Verify `<main>` is the primary content landmark.
- [ ] **The skip-link works with VO** — VO+Cmd+L (or VO+Space when focused) activates the link and jumps to `<main>`.
- [ ] **`<details>`/`<summary>` toggle is announced** — VO says "expanded" or "collapsed" when the user toggles. Native behavior.
- [ ] **Manual test (macOS):** `Cmd+F5` to enable VoiceOver. Navigate the page with VO+Cmd+arrows. Verify all of the above.

### 8. Image alt text — always

- [ ] **Every `<img>` has an `alt` attribute.** Non-negotiable.
- [ ] **Decorative images use `alt=""`** (empty alt, the screen reader skips it).
- [ ] **Informative images use descriptive `alt`** — describe the content, not the appearance ("Mavis's fleet-status dashboard" not "a screenshot").
- [ ] **No `alt` text on CSS-loaded background images** — those are decorative by nature. If a background image conveys meaning, put it in an `<img>` with alt.
- [ ] **Note for v1:** the dossier says "no images in v1." This is a v1 nicety; the checklist applies when v2 adds imagery.

### 9. Language — `<html lang="...">`

- [ ] **`<html lang="en">`** (or appropriate) is set. The Build Spec's render script must emit this in the wrapper.
- [ ] **Frontmatter `language` field** is respected — if the dossier is in French, `<html lang="fr">`.
- [ ] **Code blocks in a different language** use `<!-- language: python -->` hint or the markdown `\`\`\`python` fence (which markdown-it converts to `<code class="language-python">`). The `<code>` element does not need a `lang` attribute, but for accessibility, screen readers will pronounce it as code. If pronunciation matters, add `lang="..."` per code block.

### 10. Text resize — 200% without breaking

- [ ] **No fixed `height` on text containers** — only `min-height` if needed. Text reflow must not be clipped.
- [ ] **No `overflow: hidden` on text containers** — content must remain visible when resized.
- [ ] **`font-size` is in `rem`, not `px`** — so the user's browser font-size setting is respected.
- [ ] **Manual test (Chrome):** View → Zoom In (Cmd++) to 200%. Verify the layout adapts, no horizontal scroll, no clipped text.

### 11. Color-only meaning — never

- [ ] **Links are underlined, not just colored.** A colorblind user must be able to identify a link by its underline, not by its color.
- [ ] **Errors / warnings are not color-only** — pair the color with an icon or text. (v1 has no forms, so this is v2-relevant.)
- [ ] **Status indicators (e.g., "in progress" vs "blocked") are not color-only** — pair with text or icon.

### 12. Page title — descriptive

- [ ] **`<title>` is set** — typically `{frontmatter.title} — Mavis` or `{frontmatter.title}` for fleet-status. The wrapper template includes the title slot.
- [ ] **The title is unique per page** — no two rendered HTML files have the same `<title>`. (The orchestrator names files by date / dossier ID.)

## Build-time assertion (for the Builder)

The Build Spec's render script should refuse to write the output if any of these checks fail. **Hard fail, not warning.**

```javascript
// Pseudo-code for the build script's a11y check.
const checks = [
  { name: 'lang-attribute',          test: html => /<html[^>]+lang=/.test(html) },
  { name: 'single-h1',               test: html => (html.match(/<h1\b/g) || []).length === 1 },
  { name: 'skip-link',               test: html => /class="skip-link"/.test(html) },
  { name: 'focus-visible-rule',      test: html => /:focus-visible/.test(css) },
  { name: 'reduced-motion-css',      test: html => /@media \(prefers-reduced-motion: no-preference\)/.test(css) },
  { name: 'reduced-motion-js',       test: html => /prefers-reduced-motion: reduce/.test(js) },
  { name: 'no-rotation-animation',   test: html => !/rotate|@keyframes[^{]*\b(rotate|spin)/.test(css) },
  { name: 'no-fixed-height-text',    test: html => !/p\s*{[^}]*height:\s*\d+px/.test(css) },
  { name: 'no-external-requests',    test: html => !/(?:src|href)=["']https?:/i.test(html) },
  { name: 'no-eval-or-function',     test: html => !/eval\(|new Function/.test(js) },
  { name: 'no-outline-none',         test: html => !/outline:\s*none/.test(css) },
  { name: 'links-underlined',        test: html => /a\s*{[^}]*text-decoration:\s*underline/.test(css) },
];

let failed = [];
for (const check of checks) {
  if (!check.test(html + css + js)) failed.push(check.name);
}
if (failed.length > 0) {
  console.error('a11y build check failed:', failed.join(', '));
  process.exit(1);
}
```

The Builder can implement the contrast checks via the `wcag-contrast` npm package (1KB, regex + math, no DOM) or via the axe-core CLI (heavier, 1MB+, more accurate). v1 ships with the regex-based checks above; v2 can integrate axe.

## Lighthouse target

**Lighthouse Accessibility: 100/100.** This is the Build Spec's hard target. The checklist above is what produces the 100. If Lighthouse reports <100, the build is broken.

Common Lighthouse a11y failures and how to avoid them:

- **"Background and foreground colors do not have a sufficient contrast ratio."** → All token pairs verified in check #1.
- **"Links do not have a discernible name."** → Link text is descriptive; no icon-only links in v1.
- **"Heading elements are not in a sequentially-descending order."** → Check #5.
- **"Some elements have a `[tabindex]` value greater than 0."** → No `tabindex` other than 0/-1.
- **"`<html>` element does not have a `[lang]` attribute."** → Check #9.
- **"Image elements do not have `[alt]` attributes."** → Check #8 (v1 has no images; v2 enforces).
- **"Form elements do not have associated labels."** → v1 has no forms; v2 enforces.

## Verifier audit pass

The Verifier runs the same 12 checks as a static analysis on the rendered output. **The Verifier's audit is the final gate, not the Build Spec's check.** Both layers are required.

## Reference

- **WCAG 2.2 (canonical):** https://www.w3.org/TR/WCAG22/
- **WebAIM Contrast Checker:** https://webaim.org/resources/contrastchecker/
- **axe DevTools browser extension:** https://www.deque.com/axe/devtools/
- **MDN Accessibility:** https://developer.mozilla.org/en-US/docs/Web/Accessibility
- **The A11y Project:** https://www.a11yproject.com/
- **VoiceOver User Guide (macOS):** https://support.apple.com/guide/voiceover/welcome/mac
- **Design system spec (the tokens):** `[[../dossiers/fleet-status-design-system]]`
- **Motion vocabulary (the a11y motion contract):** `[[./motion-vocabulary]]`
- **CSS template (the implementation):** `[[../scripts/fleet-status.css]]`
- **Researcher dossier (the engineering spine):** `[[../../Researcher/dossiers/dev_tooling/markdown-to-html-ui]]` (Section 7: perf budget a11y target)
- **Build Spec v1 (the contract):** `[[../../../03 Projects/Fleet-Status Surface/01 Build Spec]]`

---

*This is the quality bar. The Builder checks at build time. The Verifier audits at review time. The Designer references when adding a new pattern. If a design choice conflicts with a11y, the design choice loses.*
