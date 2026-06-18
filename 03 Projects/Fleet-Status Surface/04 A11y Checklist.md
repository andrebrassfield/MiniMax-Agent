---
type: a11y-checklist
project: fleet-status-surface
created: 2026-06-04
updated: 2026-06-04
author: designer
status: ready-for-builder
conformance: WCAG-2.2-AA
related:
  - "[[00 Overview]]"
  - "[[01 Build Spec]]"
  - "[[02 Design System]]"
  - "[[03 Motion Vocabulary]]"
  - "[[05 CSS Template Draft]]"
  - "[[06 Builder Handoff]]"
  - "[[Researcher/dossiers/dev_tooling/markdown-to-html-ui]]"
tags: [a11y, wcag-2.2, contrast, reduced-motion, keyboard, screen-reader, mavis-design, m3]
---

# Fleet-Status Surface — A11y Checklist (v1)

> **Standard:** WCAG 2.2 Level AA minimum (per the Build Spec §"Performance budget"). Where the standard permits a range, we choose the companion-mode-friendly option (more breath, more patience, more presence).
>
> **Builder contract.** This is a *checklist*, not a recommendation. Every item must be true of the rendered output. The Verifier audits against this list with axe-core and Lighthouse, plus the manual checks below. Lighthouse target: **100/100** accessibility. axe: **0 violations**.

## 1. Perceivable

The page must present information in ways users can perceive — through sight, sound, touch (none of v1), or assistive tech.

### 1.1 Text alternatives (§1.1)

- [ ] **1.1.1 Non-text Content (Level A):** All `<img>` elements have an `alt` attribute. Decorative images use `alt=""`. SVG icons that convey information have `<title>` or `aria-label`. **Builder:** the render script must pass the `title` from `![alt](src)` markdown to `<img alt="...">`. If a content author writes `![](image.png)` (no alt), the script warns and outputs `alt=""` (decorative default) — never a missing attribute.

### 1.2 Time-based media (§1.2)

- [ ] **1.2.x** N/A. v1 has no audio, no video, no auto-playing media.

### 1.3 Adaptable (§1.3)

- [ ] **1.3.1 Info and Relationships (Level A):** Semantic HTML throughout. Headings are `<h1>`-`<h6>`, lists are `<ul>` / `<ol>`, paragraphs are `<p>`, blockquotes are `<blockquote>`, code is `<code>` / `<pre>`. The render script must NOT use `<div>` for what is semantically a heading or list. **Builder:** markdown-it outputs semantic HTML by default; verify the post-render HTML passes axe-core's "heading-order" and "list" rules.
- [ ] **1.3.2 Meaningful Sequence (Level A):** Reading order is the DOM order. CSS does not reorder content visually (`order` is forbidden on the page-header / heading chain). **Builder:** do not use `flex` or `grid` `order` to reshuffle the article; reading order is reading order.
- [ ] **1.3.3 Sensory Characteristics (Level A):** No instruction relies on color, shape, or position alone. Callouts have a label ("Callout" via `role="note"` or visual marker + text). **Builder:** the `.callout` block's left border is reinforced by a `<aside role="note">` semantic.
- [ ] **1.3.4 Orientation (Level AA, 2.1+):** Page works in portrait and landscape. Single-column, responsive. **Builder:** the `clamp(1rem, 4vw, 2.5rem)` padding handles this; no `@media (orientation: landscape)` overrides that change layout.
- [ ] **1.3.5 Identify Input Purpose (Level AA, 2.1+):** N/A. v1 has no form inputs.

### 1.4 Distinguishable (§1.4)

This is where the dossier's design decisions get audited. The Build Spec's "Lighthouse 100" promise lives or dies here.

- [ ] **1.4.1 Use of Color (Level A):** Color is not the *only* means of conveying information. Links are underlined (in addition to color) — see `02 Design System.md` §3.1. The `.callout`'s left border is the same color as the heading (`--callout-border`), and the callout *also* has a different background (`--callout-bg`). **Builder:** never rely on color alone. Underlines on links, borders on callouts, distinct backgrounds on `.callout` vs `.source-trail`.
- [ ] **1.4.3 Contrast Minimum (Level AA):** All text-on-background combinations ≥ 4.5:1 (normal text) or ≥ 3:1 (large text, 18pt+ or 14pt+ bold). **Pre-verified in the palette** (`02 Design System.md` §3.1):
  - `--text` on `--bg`: light 14.5:1 / dark 13.8:1 ✓
  - `--muted` on `--bg`: light 5.2:1 / dark 5.5:1 ✓
  - `--accent` on `--bg`: light 6.8:1 / dark 7.2:1 ✓
  - `--link` on `--bg`: light 7.4:1 / dark 7.8:1 ✓
  - `--link-hover` on `--bg`: light 6.1:1 / dark 6.3:1 ✓
  - **Builder:** run the rendered HTML through the [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) on every token pair listed in `02 Design System.md` §3.1. Do not invent new colors outside the token list.
- [ ] **1.4.4 Resize Text (Level AA, 2.1+ rename):** Up to 200% zoom, no loss of content or function. **Builder:** the page uses `clamp(15px, 0.95vw + 0.5rem, 19px)` for base size. Verify in DevTools that 200% zoom does not break the page (no horizontal scrollbar on a 1280px-wide viewport, no clipped text).
- [ ] **1.4.5 Images of Text (Level AA):** No images of text in v1. The system font stack renders actual text. **Builder:** if Mavis ever wants a "designed quote" graphic, the renderer refuses (v1).
- [ ] **1.4.10 Reflow (Level AA, 2.1+):** At 320px CSS width (320 × 256 viewport equivalent), no horizontal scrolling, no content hidden. **Builder:** verify in DevTools with a 320px-wide viewport, all sections remain readable. The `clamp()` and `1fr` grid patterns handle this; do not introduce fixed pixel widths.
- [ ] **1.4.11 Non-text Contrast (Level AA, 2.1+):** UI components and graphical objects ≥ 3:1. The `--callout-border` (`#a8893a`) against `--callout-bg` (`#f0e9d6`) is 3.0:1 — passes the non-text rule (which is 3:1, not 4.5:1). The `--source-border` (`#7a8a6b`) against `--source-bg` (`#e8ebe4`) is 3.2:1. ✓
- [ ] **1.4.12 Text Spacing (Level AA, 2.1+):** No loss of content when the user overrides `line-height: 1.5`, `letter-spacing: 0.12em`, `word-spacing: 0.16em`, or `paragraph-spacing: 2em`. **Builder:** the body uses `line-height: 1.6` and `letter-spacing: 0` — overriding these does not break layout. The system font stack is robust to letter-spacing.
- [ ] **1.4.13 Content on Hover or Focus (Level AA, 2.1+):** N/A. v1 has no hover-revealed content (no tooltips, no hover-only navigation).

## 2. Operable

The page must be operable through keyboard, mouse, touch, voice, and assistive tech. v1 is keyboard + screen reader + mouse (touch inherits from mobile-friendly responsive).

### 2.1 Keyboard (§2.1)

- [ ] **2.1.1 Keyboard (Level A):** All functionality is available through keyboard. v1 has no interactive elements *except* the `<details>` from the `:::collapse` render hint. **Builder:** the `<details>` element is keyboard-operable by default (Enter / Space to toggle). Do not use `tabindex="0"` on headings; they are not interactive. Do not add a `<div role="button">` for the page; there is no button.
- [ ] **2.1.2 No Keyboard Trap (Level A):** No keyboard trap. **Builder:** there is no JS modal, no focus-trap library, no `onkeydown` handler. Page is naturally tabbable top to bottom. The skip-link (see §2.4.1) is the only programmatic focus change.
- [ ] **2.1.3 Keyboard (No exception, AAA, 2.1+):** The page must be operable without timing. v1 has no time limits.

### 2.2 Enough Time (§2.2)

- [ ] **2.2.x** N/A. v1 has no timed content, no auto-playing media, no sessions, no logins.

### 2.3 Seizures and Physical Reactions (§2.3)

- [ ] **2.3.1 Three Flashes or Below Threshold (Level A):** No content flashes more than 3 times per second. The fade animations are *single* transitions, not flashes. **Builder:** the 800ms `--t-presence` and 400ms `--t-fade` are far above the 100ms flash threshold. The reduced-motion fallback (§2.3 in the [Motion Vocabulary](03%20Motion%20Vocabulary.md)) eliminates the only potential concern.

### 2.4 Navigable (§2.4)

- [ ] **2.4.1 Bypass Blocks (Level A):** A "Skip to content" link is the first focusable element on the page. **Builder:** the render script adds `<a class="skip-link" href="#main">Skip to content</a>` as the first element inside `<body>`. CSS hides it visually until focused.
  ```css
  .skip-link {
    position: absolute;
    top: -100px;
    left: 0;
    padding: 0.5rem 1rem;
    background: var(--bg-elev);
    color: var(--accent);
    text-decoration: none;
    z-index: 100;
  }
  .skip-link:focus { top: 0; }
  ```
- [ ] **2.4.2 Page Titled (Level A):** The `<title>` element describes the page. The render script reads the frontmatter `title:` and outputs `<title>{title} — Fleet Status</title>`. **Builder:** never output a generic `<title>Document</title>`. If frontmatter is missing `title`, fall back to the first H1.
- [ ] **2.4.3 Focus Order (Level A):** Focus order matches reading order. **Builder:** the DOM order is the reading order. Do not add `tabindex` to non-interactive elements. Do not `tabindex="0"` headings.
- [ ] **2.4.4 Link Purpose (In Context) (Level A):** Link text describes the destination. **Builder:** the markdown renderer should NOT auto-generate "click here" or "read more" links. Wikilinks like `[[Foo]]` become `<a href="Foo.html">Foo</a>` — the link text is the page name. External links preserve their text. **Exception:** if a link is inside a paragraph, its text is the inline phrase. No "click here" anti-pattern.
- [ ] **2.4.5 Multiple Ways (Level AA):** N/A. v1 has no navigation across multiple pages. v2 if a TOC is added.
- [ ] **2.4.6 Headings and Labels (Level AA):** Headings describe the section that follows. Labels describe the input that follows. **Builder:** no heading skips (H1 → H3 is bad). The Build Spec's "visual cap at H3" applies to CSS, not HTML; the rendered HTML may use H1, H2, H3 (and H4+ for nested content if Mavis writes it). **Enforce:** no H4+ visually demotes to H3 but the *DOM* keeps the level — for accessibility, an H4 in the DOM is read as "subsection" by screen readers, even if it's styled like an H3.
- [ ] **2.4.7 Focus Visible (Level AA):** Focus is visible on all focusable elements. **Builder:**
  ```css
  :focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
    border-radius: 2px;
  }
  ```
  The accent (`#5c6b4f` / `#a3b18a`) is 6.8:1 / 7.2:1 against `--bg` — the focus ring is *very* visible. The 2px outline + 2px offset is a Material 3 / Apple HIG pattern.
- [ ] **2.4.11 Focus Not Obscured (Minimum, Level AA, 2.2+):** The focused element is not hidden by other content. v1 has no sticky headers or popups. **Builder:** if v2 adds a sticky table-of-contents, the focused heading must not be obscured. v1 is fine.
- [ ] **2.4.13 Fixed Reference Points (AAA, 2.2+, advisory):** N/A. v1 has no repeated content (nav menus, etc.).

### 2.5 Input Modalities (§2.5)

- [ ] **2.5.x** N/A. v1 has no form inputs, no gestures, no motion-actuated controls.

## 3. Understandable

The page and the rendering must be understandable to the user and to assistive tech.

### 3.1 Readable (§3.1)

- [ ] **3.1.1 Language of Page (Level A):** `<html lang="en">` (or `lang` matches the frontmatter `lang:` field). **Builder:** the render script sets `lang` from frontmatter, defaulting to `en`.
- [ ] **3.1.2 Language of Parts (Level AA):** Quoted text in another language gets `<span lang="...">`. **Builder:** markdown-it does not auto-detect this. If Mavis writes blockquotes in another language, she should add a `<!-- lang: fr -->` render hint, and the render script applies `lang`. **Default:** N/A in v1 — defer to v2 if needed.
- [ ] **3.1.3 Unusual Words (AAA):** N/A. (This is a Level AAA, advisory only. Not in scope for v1 AA compliance.)
- [ ] **3.1.4 Abbreviations (AAA):** N/A. (Same as 3.1.3.)
- [ ] **3.1.5 Reading Level (AAA):** N/A. (Same as 3.1.3.)
- [ ] **3.1.6 Pronunciation (AAA):** N/A. (Same as 3.1.3.)

### 3.2 Predictable (§3.2)

- [ ] **3.2.1 On Focus (Level A):** Focusing an element does not trigger a context change. **Builder:** there is no `onfocus` handler. ✓
- [ ] **3.2.2 On Input (Level A):** Changing an input does not trigger a context change. v1 has no inputs. ✓
- [ ] **3.2.3 Consistent Navigation (Level AA):** N/A. v1 has no navigation across multiple pages.
- [ ] **3.2.4 Consistent Identification (Level AA):** Components with the same function are identified the same way. **Builder:** the render hint containers (`.callout`, `.collapse`, `.source-trail`) use consistent class names. The `:::source-trail` block always renders the same way.
- [ ] **3.2.5 Change on Request (AAA, 2.2+):** N/A. v1 has no auto-updating content. (The 60s auto-refresh on `content-deck-generator` is a different skill; v1's Fleet-Status Surface does NOT auto-refresh — the dossier is regenerated on save.)

### 3.3 Input Assistance (§3.3)

- [ ] **3.3.x** N/A. v1 has no inputs.

## 4. Robust

The page must work with assistive tech, including future ones.

### 4.1 Compatible (§4.1)

- [ ] **4.1.1 Parsing (Level A):** In WCAG 2.2, this is now advisory (the spec acknowledges that valid HTML is the goal, but does not fail for minor parse errors since modern UAs handle them). **Builder:** the markdown-it output is well-formed HTML. The render script does not introduce unbalanced tags.
- [ ] **4.1.2 Name, Role, Value (Level A):** All UI components have a programmatic name, role, and value. **Builder:** semantic HTML provides this by default. The `:::collapse` render hint uses `<details><summary>...</summary>...</details>` which has the correct ARIA semantics out of the box (the `summary` is the accessible name, the `details` exposes `aria-expanded`).
- [ ] **4.1.3 Status Messages (Level AA, 2.1+):** Status updates (e.g., "dossier regenerated") are announced to screen readers via `aria-live="polite"`. **Builder:** the render script does NOT add status messages (the regeneration is silent). If v2 adds a "last updated" indicator, it gets `aria-live="polite"`. v1: N/A.

## 5. Companion-mode a11y (the extras)

The WCAG checklist above is the floor. Companion-mode adds three more commitments, sourced from the mavis-as-companion synthesis.

### 5.1 The page is not loud

- [ ] **No autoplay anything.** The page does not autoplay audio, autoscroll, or auto-update in v1. The user is the agent of their own reading rhythm.
- [ ] **No flash or attention-grab.** No "important!", no badge pulses, no banner carousels. The page's only motion is the fade vocabulary in `03 Motion Vocabulary.md`.
- [ ] **No notification sounds.** N/A — v1 has no audio.

### 5.2 The page forgives

- [ ] **Long pages are not punished.** Reading a 5,000-word dossier is not a 5,000-word wall. The motion vocabulary and spacing tokens reward *long* reading, not *short* scanning.
- [ ] **Reduced motion is content, not a stripped version.** When reduced motion is on, the content is *complete and present*, not a "minimal mode." The user who sets this preference is not penalized; the page simply arrives without fanfare.
- [ ] **Dark mode is honest.** When the OS preference is dark, the page is dark — but the *structure* (line lengths, breaks, hierarchy) is identical. Dark mode is not a different page.

### 5.3 The page is patient

- [ ] **No artificial pacing.** The page does not force the user to wait, pause, or sit through transitions. The 800ms `--t-presence` is the maximum, and it's a *user-perceived* transition, not a *blocking* one — the content is present, just settling.
- [ ] **Stagger is gentle.** 80ms between elements is just-perceptible. The page does not *announce* each element.

## 6. The manual checks (not automatable)

The Verifier cannot run a tool for these. They require opening the page in a real browser and exercising it like a user.

- [ ] **Keyboard-only test.** Open the page, press Tab from address bar. Verify: skip-link appears → focus it → press Enter → focus moves to main content. Tab through the document. Verify every link and `<details>` is reachable. Verify focus order matches reading order.
- [ ] **Screen reader test.** VoiceOver (macOS): ⌘F5 to start, navigate by heading (Ctrl+Opt+Cmd+H). Verify all headings are present in DOM order. Verify the page title is announced. Verify the `<details>` summary is announced as "collapsed" / "expanded." NVDA (Windows) and Orca (Linux) equivalents.
- [ ] **Reduced motion test.** DevTools → Rendering → "Emulate CSS media feature prefers-reduced-motion: reduce" → reload. Verify: all content is immediately visible, no fade, no transition. Tab to a `<details>` → press Enter → verify the expand is instant.
- [ ] **200% zoom test.** DevTools → Rendering → "Apply device pixel ratio" → set zoom 200% (or Cmd-+ 4 times in browser). Verify: no horizontal scrollbar on a 1280px viewport, no clipped text, no overlapping content.
- [ ] **320px width test.** DevTools → Device toolbar → "Responsive" → 320 × 568. Verify: all content readable, no horizontal scrollbar, line lengths adapt.
- [ ] **Dark mode test.** OS-level dark mode → reload. Verify: tokens swap, contrast still passes, focus ring still visible.
- [ ] **Tab key after each `<details>`** — verify focus does not get trapped inside the `<details>`.
- [ ] **Print test.** Cmd-P → print preview. Verify: backgrounds do not print (the `@media print` rule sets white background / black text), links are still visible, no animation artifacts.

## 7. The tooling checks (automatable)

The Verifier runs these in CI / pre-ship:

- [ ] **axe-core** (via `@axe-core/cli` or `pa11y-ci`): **0 violations of severity "serious" or "critical."** `npx @axe-core/cli https://localhost:port/...` or local-file equivalent.
- [ ] **Lighthouse accessibility audit:** **score 100/100.** `npx lighthouse <url> --only-categories=accessibility --quiet --chrome-flags="--headless"`.
- [ ] **HTML validation:** The W3C Nu HTML Checker returns no errors. `https://validator.w3.org/nu/` or `vnu --jar`.
- [ ] **Color contrast audit:** A custom script walks every `<text>` element (or the token table) and asserts contrast ≥ 4.5:1 (or 3:1 for large text). The token table in `02 Design System.md` §3.1 is the source of truth; the rendered HTML must use only those tokens.
- [ ] **Bundle weight:** The HTML file is < 100KB uncompressed (Build Spec §"Performance budget"). `wc -c status.html`.

## 8. References (primary sources)

- **WCAG 2.2** — https://www.w3.org/TR/WCAG22/. The W3C Recommendation (Oct 5, 2023). All §-references in this document are to WCAG 2.2.
- **WCAG 2.2 Quick Reference** — https://www.w3.org/WAI/WCAG22/quickref/. The W3C's filter-by-role tool. Level A and AA are required; AAA is advisory.
- **WebAIM Contrast Checker** — https://webaim.org/resources/contrastchecker/. The reference tool for §1.4.3.
- **axe-core rules** — https://dequeuniversity.com/rules/axe/. The Deque axe-core rule list. Used in CI.
- **Lighthouse accessibility audit** — https://developer.chrome.com/docs/lighthouse/accessibility/. The Chrome DevRel scoring rubric.
- **W3C Nu HTML Checker** — https://validator.w3.org/nu/. The W3C's own validator.
- **MDN Accessible HTML** — https://developer.mozilla.org/en-US/docs/Web/Accessibility. The MDN canonical reference.
- **MDN `<details>` element** — https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details. The keyboard + ARIA semantics for the `:::collapse` render hint.
- **MDN `:focus-visible`** — https://developer.mozilla.org/en-US/docs/Web/CSS/:focus-visible. The selector for the focus ring.
- **MDN `prefers-reduced-motion`** — https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion. The reduced-motion media query.
- **Chrome for Developers: Accessible focus indicators** — https://developer.chrome.com/blog/accessible-focus-indicators. Best practices for focus rings.
- **Chrome for Developers: prefers-reduced-motion** — https://developer.chrome.com/blog/prefers-reduced-motion. The case for honoring the user setting.
- **APG (ARIA Authoring Practices Guide)** — https://www.w3.org/WAI/ARIA/apg/. The W3C's ARIA pattern catalog. (v2 reference, not v1.)
- **Researcher dossier** — `03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui.md` §7 (the performance budget includes the 100/100 Lighthouse commitment).
- **Build Spec** — `01 Build Spec.md` §"Performance budget" and §"Acceptance criteria."

---

*A11y checklist, v1. WCAG 2.2 AA. Lighthouse 100. axe 0 violations. Builder ships it. Verifier audits it. The dossier is for every reader, including the ones who can't see it, can't move to it, or can't sit through the fade.*
