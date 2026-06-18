---
type: motion-vocabulary
project: fleet-status-surface
created: 2026-06-04
updated: 2026-06-04
author: designer
status: ready-for-builder
related:
  - "[[00 Overview]]"
  - "[[01 Build Spec]]"
  - "[[02 Design System]]"
  - "[[04 A11y Checklist]]"
  - "[[05 CSS Template Draft]]"
  - "[[06 Builder Handoff]]"
  - "[[Researcher/dossiers/dev_tooling/markdown-to-html-ui]]"
tags: [motion, fade, intersection-observer, scroll-driven, reduced-motion, mavis-design, m3]
---

# Fleet-Status Surface — Motion Vocabulary (v1)

> **One sentence.** The dossier *fades in* — it does not *load*. Motion is a small, disciplined vocabulary: four timings, one easing, three entry patterns, one progressive enhancement, and a mandatory reduced-motion fallback. The vocabulary is intentionally thin.
>
> **Builder contract.** The CSS in `05 CSS Template Draft.md` and the JS in `templates/observer.js` (per the Build Spec) implement this vocabulary verbatim. Do not invent new timings or easings at the script stage.

## 1. The posture — "fades in", not "loads"

The mavis-as-companion synthesis calls for *presence aesthetics* — patience, breath, the right kind of silence. The page should feel like it is *arriving*, not *appearing*. Three implications:

1. **Duration is slow but bounded.** The slowest entry is 800ms; the fastest is 100ms. Nothing past 800ms is a transition; it's a wait. Anything faster than 100ms is a flash, not a motion.
2. **Easing is decelerating, not springy.** `cubic-bezier(0.2, 0.7, 0.2, 1)` — the curve lands softly, like a person sitting down. No bounce, no overshoot, no spring. Companion-mode does not snap.
3. **Reduced motion is mandatory, not optional.** WCAG 2.2.2 (Level A) requires it. The user OS setting wins. The fallback is *content shows immediately* — not a "subtle alternative" animation.

## 2. The timing scale

Four timings, in 2x ratio. Anything outside this scale is a smell.

| Token | Duration | Use |
|---|---|---|
| `--t-micro` | **100ms** | Hover, focus-visible outlines, color shifts on interactive elements (none in v1, reserved for v2). |
| `--t-snappy` | **200ms** | Color-only transitions: link hover, focus ring, accordion expand (the `+` → `−` glyph). |
| `--t-fade` | **400ms** | **Default fade-in duration** for above-the-fold content (the page header, H1, first paragraph). |
| `--t-presence` | **800ms** | Reserved for *one thing*: the `.fade-in-presence` class, used on the *single* most important element on the page (the page title, or the fleet-status snapshot). Never used on more than one element per page. |

**Why this scale.** The Build Spec's open question #3 said "reasonable defaults: 400ms above-the-fold, 600ms below-the-fold, 80ms stagger for list items." I tightened it to 400ms / 800ms with 80ms stagger steps (see §4). The 2x ratio is a Chrome DevRel convention — see the [Chrome for Developers "UI animation fundamentals" guide](https://developer.chrome.com/docs/devtools/animations) for the underlying pattern of small, disciplined scales.

**Where the values come from:**
- **Material Design 3 motion durations** (Google) — short (100-200ms), medium (200-300ms), long (300-500ms). We use 400ms as the default (slightly slower than Material's long) for companion-mode patience. Source: [m3.material.io/styles/motion/transitions/transition-patterns](https://m3.material.io/styles/motion/transitions/transition-patterns).
- **Apple HIG motion** — standard duration 0.35s, with a 0.2-0.5s range. We sit in the upper end. Source: [developer.apple.com/design/human-interface-guidelines/motion](https://developer.apple.com/design/human-interface-guidelines/motion).
- **The dossier's `600ms cubic-bezier(0.2, 0.7, 0.2, 1)`** — the test-render-sample.html uses 600ms for the `--transition-fade` token. We split that into 400ms (default) and 800ms (presence). Source: `03 Projects/Fleet-Status Surface/test-render-sample.html` line 25.

## 3. The easing scale

**One default easing.** Resist the urge to add more. The exception is the `--t-presence` motion, which uses a softer curve.

| Token | cubic-bezier | Use |
|---|---|---|
| `--ease-default` | `cubic-bezier(0.2, 0.7, 0.2, 1)` | **All v1 transitions and keyframes.** Decelerating, lands softly. No bounce, no overshoot. |
| `--ease-presence` | `cubic-bezier(0.16, 0.84, 0.32, 1)` | **Only on `.fade-in-presence`** (the 800ms reserved motion). Slightly softer start, gentler settle. The "I have arrived" curve. |

**Why this curve family.** `cubic-bezier(0.2, 0.7, 0.2, 1)` is the Chrome DevRel "ease-out" pattern — it accelerates fast, decelerates slow. It feels like *settling*. The dossier already used it. Companion-mode bias says *keep* this; do not switch to `ease-in` (which feels *retreating*) or `ease-in-out` (which feels *mechanical*).

**What to never use in v1:**
- `linear` — feels robotic, breaks the "presence" feel
- `ease` (the keyword) — too generic, lands mid-courve
- `cubic-bezier` with overshoot (>1 in y2) — bounce is operator-mode showmanship
- `steps()` — too jumpy for a fading dossier

Sources:
- [Material Design 3 motion easing](https://m3.material.io/styles/motion/easing-and-duration/tokens-1) — standard easing token set, decelerating curves dominate.
- [Chrome for Developers: animation easing](https://developer.chrome.com/docs/devtools/animations) — Bramus's "animation fundamentals" walkthrough.

## 4. The entry patterns

Three patterns, each for a different surface. Builder implements all three.

### 4.1 Pattern A — Above-the-fold first-paint (pure CSS, zero JS)

**When:** The page-header, H1, and the first 4–6 elements of the article. These are visible at FCP; we want them to fade in *immediately*, without waiting for any JS to execute.

**How:** Pure-CSS `@keyframes` with `animation-delay` per element. No IntersectionObserver (the observer is below-the-fold's job). Animations use `transform: translateY(8px) → none` only — **opacity stays at 1** during the animation, so color contrast passes the Lighthouse audit throughout the reveal (the audit checks computed styles, not animation states).

```css
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
.page-header + h1 + *          { animation-delay: 0ms; }
.page-header + h1 + * + *      { animation-delay: 80ms; }
.page-header + h1 + * + * + *  { animation-delay: 160ms; }
.page-header + h1 + * + * + * + * { animation-delay: 240ms; }
.page-header + h1 + * + * + * + * + * { animation-delay: 320ms; }
.page-header + h1 + * + * + * + * + * + * { animation-delay: 400ms; }
```

**Stagger:** 80ms between elements. Just-perceptible. (Smaller = chaotic. Larger = boring. 80ms is the Chrome DevRel-recommended default for "stagger" — [Bramus's "staggered animations" demo](https://css-tricks.com/css-grid-can-do-auto-flow-value/) aligns.)

**Builder's responsibility:** The CSS template ships with these selectors. The Builder's render script does **not** need to add `class="fade-in"` to every element. The CSS is the spec.

### 4.2 Pattern B — Below-the-fold scroll-in (IntersectionObserver + CSS transition)

**When:** Every other element on the page (paragraphs, lists, callouts, source-trail, etc.). These fade in as the user scrolls.

**How:** The render script (or the inline `<script>`) runs an IntersectionObserver with `threshold: 0.1` and `rootMargin: 0px 0px -10% 0px` (slight inset so the fade starts *just before* the element is fully visible — feels more natural). When an element enters the viewport, the observer adds the class `.is-visible`. The CSS transition handles the visual change.

```css
.fade-in {
  opacity: 0;
  transform: translateY(8px);
  transition: opacity var(--t-fade) var(--ease-default),
              transform var(--t-fade) var(--ease-default);
  will-change: opacity, transform;
}
.fade-in.is-visible {
  opacity: 1;
  transform: none;
}
```

```js
// observer.js (inlined before </body>; ~30 lines per Build Spec)
(function () {
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.fade-in').forEach(el => el.classList.add('is-visible'));
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
  document.querySelectorAll('.fade-in').forEach(el => io.observe(el));
})();
```

**Why `unobserve` after first reveal.** One-shot reveal. Scrolling back up should *not* re-trigger the animation. Companion-mode is *patient*, not *demanding attention*.

**Render script's responsibility:** The Builder's `render-dossier.js` adds `class="fade-in"` to every block-level element (paragraphs, headings, lists, blockquotes, callouts, code blocks, tables, source-trail, the `.fade-in-stagger` container). The CSS handles the rest.

### 4.3 Pattern C — Stagger inside a `:::fade-in-stagger` block

**When:** When Mavis writes `:::fade-in-stagger` in markdown, the children (typically list items) should fade in one after another when the *container* enters the viewport. This is the "task list reveals itself" feel.

**How:** The container gets the IntersectionObserver treatment. The CSS handles the per-child delay via `:nth-child(n)` selectors.

```css
.fade-in-stagger > * {
  opacity: 0;
  transform: translateY(8px);
  transition: opacity var(--t-fade) var(--ease-default),
              transform var(--t-fade) var(--ease-default);
}
.fade-in-stagger.is-visible > *                  { opacity: 1; transform: none; }
.fade-in-stagger.is-visible > *:nth-child(1)    { transition-delay: 0ms; }
.fade-in-stagger.is-visible > *:nth-child(2)    { transition-delay: 80ms; }
.fade-in-stagger.is-visible > *:nth-child(3)    { transition-delay: 160ms; }
.fade-in-stagger.is-visible > *:nth-child(4)    { transition-delay: 240ms; }
.fade-in-stagger.is-visible > *:nth-child(5)    { transition-delay: 320ms; }
.fade-in-stagger.is-visible > *:nth-child(6)    { transition-delay: 400ms; }
.fade-in-stagger.is-visible > *:nth-child(n+7)  { transition-delay: 480ms; }
```

**The observer's responsibility:** The JS adds `.is-visible` to the *container*, not to the children. The CSS does the cascade via `> *:nth-child` selectors.

**Why `> *` not `*`.** Direct children only. Nested lists stagger independently.

### 4.4 Progressive enhancement — `@supports (animation-timeline: view())`

**When:** Chrome 115+ / Edge 115+ / Safari 26+ user. The IntersectionObserver path is the fallback. The `view()` timeline path is the *premium* experience — animation runs **off the main thread** (compositor), silky smooth, no layout thrash.

```css
@supports (animation-timeline: view()) {
  .fade-in {
    animation: fade-in-keyframe linear both;
    animation-timeline: view();
    animation-range: entry 0% cover 30%;
  }
}
```

**How it works:** The element's animation progress is tied to its position in the scroll container. `entry 0% cover 30%` means the animation starts when the element's top edge enters the viewport and ends when 30% of the element has been scrolled through. The keyframe stays `transform: translateY(8px) → none` (preserving the AA contrast insight from Pattern A).

**The fallback is still the JS observer.** `@supports` either matches or doesn't — there's no third state. If `view()` is supported, the CSS animation runs and the JS observer's `is-visible` class is harmless (it triggers a transition that has no animation left to play, since the keyframe is doing the work).

**Source:** [Chrome for Developers: "Animate elements on scroll"](https://developer.chrome.com/docs/css-ui/scroll-driven-animations) (Bramus, May 5 2023). MDN canonical: [CSS scroll-driven animations module](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll-driven_animations).

**Why we kept the IntersectionObserver as the base path:** the dossier was correct that this gives a uniform behavior across browsers. The `view()` timeline is *progressive enhancement*, not the *primary* path. Companion-mode bias: the page should *work* on every browser, *shine* on modern ones.

## 5. The reduced-motion fallback (MANDATORY)

**WCAG 2.2.2 Level A: Pause, Stop, Hide.** If the user has `prefers-reduced-motion: reduce` set at the OS level, all animation must be skippable. The fallback is **content shows immediately**, no fade, no transition.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-delay: 0ms !important;
    transition-duration: 0.001ms !important;
  }
  .fade-in, .fade-in-stagger > * {
    opacity: 1 !important;
    transform: none !important;
  }
}
```

**Why `0.001ms` not `0s`.** A duration of 0 can cause a flash of the *starting* state on some browsers (the element renders at `opacity: 0` for one frame). `0.001ms` is effectively instant but avoids the flash.

**Why `!important`.** Reduced motion is a user *right*, not a style preference. It overrides everything, including third-party styles inlined by the render script.

**Source:** [WCAG 2.2.2 Pause, Stop, Hide](https://www.w3.org/TR/WCAG22/#pause-stop-hide). [MDN prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion). [Chrome for Developers: prefers-reduced-motion](https://developer.chrome.com/blog/prefers-reduced-motion).

**The Verifier must check this.** Open DevTools → Rendering → "Emulate CSS media feature prefers-reduced-motion: reduce" → reload → confirm content is immediately visible, no fade, no transition.

## 6. Interaction motion (v2 deferred)

There are no interactive elements in v1. The dossier has no buttons, no nav, no form. v1 is a *read* surface. When v2 introduces interactivity (e.g., the daily check-in modal, expand/collapse on the `:::collapse` render hint), the motion vocabulary extends:

| Interaction | Duration | Easing | Source pattern |
|---|---|---|---|
| Hover color shift | 100ms | `--ease-default` | Material 3 state layer |
| Focus ring fade-in | 100ms | `--ease-default` | a11y best practice |
| Accordion expand | 200ms | `--ease-default` | Tufte + Material 3 |
| Modal/dialog enter | 200ms | `--ease-default` | Material 3 dialog pattern |
| Page navigation (View Transitions) | 400ms | `--ease-presence` | Chrome View Transitions API |

Builder: do not implement any of these in v1. The CSS template reserves the `--t-micro` and `--t-snappy` tokens, but no rule uses them yet.

## 7. CLS discipline — why we animate transform, not top/bottom

**Web Vitals: CLS < 0.1.** Cumulative Layout Shift. If the fade-in animates a property that affects layout (`height`, `top`, `margin`, `padding`), the page *shifts* as the animation runs. A 0.1 CLS is the Good threshold; a fade-in that shifts the page by 50px is a Bad CLS.

The fix: animate only `opacity` and `transform`. `transform` is composited; the GPU handles it. The layout doesn't change.

**The Builder must never:**
- Animate `top`, `bottom`, `left`, `right`, `width`, `height`, `margin`, `padding`, `font-size` (these trigger layout)
- Use `display: none` → `display: block` transitions in v1 (use `opacity` + visibility for v1 disclosure)
- Apply `transition` to `box-shadow` on a frequently-animated element (composite, but expensive)

**The Builder can:**
- Animate `opacity`, `transform`, `color`, `background-color`, `border-color`, `text-decoration-color`, `outline`, `filter`
- Use `@starting-style` (Chrome 117+) in v2, when display transitions are needed (the dossier defers this to v2 — the spec is newer, smaller browser footprint).

**Source:** [web.dev CLS](https://web.dev/articles/cls), [Chrome for Developers: animation performance](https://developer.chrome.com/docs/devtools/animations).

## 8. CSS custom properties — the final token block

The Builder inlines this block at the top of the `<style>` element. The motion tokens are referenced by the rest of the stylesheet and by the inline `<script>` (which doesn't need them, but documents the design intent).

```css
:root {
  /* timing */
  --t-micro:    100ms;
  --t-snappy:   200ms;
  --t-fade:     400ms;
  --t-presence: 800ms;

  /* easing */
  --ease-default:  cubic-bezier(0.2, 0.7, 0.2, 1);
  --ease-presence: cubic-bezier(0.16, 0.84, 0.32, 1);
}
```

The full token set (colors, type, spacing) lives in `02 Design System.md` §3. The CSS template in `05 CSS Template Draft.md` brings them all together.

## 9. References (primary sources)

- **MDN Intersection Observer API** — https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API. "Widely available since March 2019."
- **MDN CSS scroll-driven animations** — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll-driven_animations. `scroll()`, `view()` timelines. Last updated 2026-05-28.
- **Chrome for Developers: "Animate elements on scroll"** (Bramus Van Damme) — https://developer.chrome.com/docs/css-ui/scroll-driven-animations. The canonical blog post on `view()`.
- **Chrome for Developers: "Four new CSS features for smooth entry and exit animations"** — https://developer.chrome.com/blog/four-new-css-features-for-smooth-entry-and-exit-animations. `@starting-style`, `transition-behavior: allow-discrete`. (v2 reference, not v1.)
- **MDN `prefers-reduced-motion`** — https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion.
- **WCAG 2.2.2 Pause, Stop, Hide (Level A)** — https://www.w3.org/TR/WCAG22/#pause-stop-hide. The accessibility standard for motion.
- **WCAG 2.3.3 Animation from Interactions (Level AAA)** — https://www.w3.org/TR/WCAG22/#animation-from-interactions. Not a v1 requirement, but informs the philosophy.
- **Material Design 3 motion** — https://m3.material.io/styles/motion. Easing tokens, duration buckets, transition patterns.
- **Apple Human Interface Guidelines: Motion** — https://developer.apple.com/design/human-interface-guidelines/motion. 0.35s standard duration, 0.2-0.5s range.
- **CSS-Tricks: A Walkthrough of CSS `animation` Easing Functions** — https://css-tricks.com/ease-out-in-out-cubic-bezier/. The cubic-bezier deep dive.
- **web.dev CLS (Cumulative Layout Shift)** — https://web.dev/articles/cls. The CLS discipline; why transform is safe, top/bottom is not.
- **Researcher dossier** — `03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui.md` §2 and §7. The dossier's fade + IO + reduced-motion + `view()` progressive enhancement pattern.
- **Scribe synthesis** — `02 Notes/ideas/mavis-as-companion.md`. The "presence aesthetics" framing that motivates the patient timings.
- **Harness pattern** — `02 Notes/patterns/agent-harness.md`. The future-proofing test applied to motion vocabulary: thinner, not thicker.

---

*Motion vocabulary, v1. Four timings. Two easings. Three entry patterns. One progressive enhancement. One mandatory fallback. Builder drops it in. Verifier checks reduced-motion and CLS. The dossier fades in.*
