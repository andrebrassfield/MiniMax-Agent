---
type: pattern
created: 2026-06-04
status: v1
audience: Designer, Builder, Mavis, Scribe (any HTML-surface author)
scope: cross-project — every Mavis HTML surface
extends: "[[../dossiers/fleet-status-design-system]]"
enforces: "[[./a11y-checklist]]" (prefers-reduced-motion contract)
implements: "[[../../../03 Projects/Fleet-Status Surface/01 Build Spec]]" (Build Spec v1)
tags: [motion, animation, fade-in, intersection-observer, a11y, cross-project, v1]
---

# Motion Vocabulary v1 — Mavis HTML Surfaces

> **The grammar of how Mavis's HTML surfaces feel.** Three rules, eight patterns, one accessibility contract. Used by every Mavis HTML surface (Fleet-Status Surface v1, dossiers, briefs, weekly syntheses, dashboards). The Build Spec v1 says "no JS framework dependencies" and "the only JS is the IntersectionObserver block" — this vocabulary is what that JS + CSS implements.

## Three rules

1. **Motion is reveal, not performance.** Fade-in tells the user "this content is for you, now." It does not entertain, bounce, or grab attention. If the motion is the *point*, the design is wrong.
2. **Fade only. No bounce, no parallax, no scroll-jacking, no skeleton loaders.** The page is alive because content arrives as you scroll, not because things move on their own.
3. **`prefers-reduced-motion: reduce` is non-negotiable.** Both the CSS and the JS check the media query. If reduced motion is requested, the content is shown immediately with no animation. This is enforced at two layers (defense in depth) so a CSS bug cannot break a11y.

## Token reference (full set in design system spec)

```css
--dur-instant:  100ms;   /* hover, focus ring */
--dur-fast:     150ms;   /* hover transitions */
--dur-base:     400ms;   /* above-the-fold entrance */
--dur-slow:     600ms;   /* below-the-fold reveal */

--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);     /* "Apple spring-out" */
--ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);    /* decelerate hard */
--ease-in-out:    cubic-bezier(0.4, 0, 0.2, 1);      /* standard */

--stagger-step: 80ms;
--stagger-cap:  8;
--stagger-decay: 40ms;
```

**Why these numbers:**

- `400ms` entrance is the sweet spot — fast enough to feel "instant," slow enough to be perceptible. <200ms reads as a flicker; >600ms reads as slow.
- `600ms` scroll-reveal gives the eye time to track each item as it fades in. The longer duration compensates for the user's scroll velocity.
- `80ms` stagger is the maximum perceptual interval between siblings before the eye stops grouping them. Beyond 80ms, the stagger becomes a sequence, not a group.
- `cubic-bezier(0.16, 1, 0.3, 1)` is the "Apple spring-out" curve — starts fast, decelerates hard, settles soft. Used in iOS / macOS spring animations. Feels alive without being bouncy.

## Eight patterns

### 1. Entrance — above-the-fold (pure CSS)

When the page first loads, content above the fold fades in. **Zero JavaScript.** Works in every browser since 2014.

```css
@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.fade-in {
  opacity: 0;
  animation: fade-in var(--dur-base) var(--ease-out-expo) forwards;
}
```

Apply to the H1, the lede paragraph, and the first 2-3 sections. That's the above-the-fold surface. Don't apply to more — the stagger logic handles the rest.

**Critical:** `transform: translateY(8px)` is used instead of `top: 8px` or `margin-top: 8px` to avoid triggering layout shift (CLS). The animation is GPU-composited; layout doesn't move.

### 2. Entrance — staggered siblings (pure CSS, ≤5 items above the fold)

```css
.fade-in-stagger > .fade-in:nth-child(1) { animation-delay: 0ms; }
.fade-in-stagger > .fade-in:nth-child(2) { animation-delay: 80ms; }
.fade-in-stagger > .fade-in:nth-child(3) { animation-delay: 160ms; }
.fade-in-stagger > .fade-in:nth-child(4) { animation-delay: 240ms; }
.fade-in-stagger > .fade-in:nth-child(5) { animation-delay: 320ms; }
```

Cap at 5 above the fold. More than 5 means the user is waiting too long; the first 5 should be the page's lede.

### 3. Reveal — below-the-fold (IntersectionObserver)

The IO pattern. ~30 lines of JS, inlined before `</body>`. This is the *only* JS in the v1 design system.

```javascript
(function() {
  if (!('IntersectionObserver' in window)) {
    // Fallback for very old browsers: just show everything.
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

The matching CSS:

```css
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
```

**Two key choices:**

- `rootMargin: '0px 0px -10% 0px'` — the reveal triggers when the element is 10% *above* the bottom of the viewport. This means by the time the user is reading the previous section, the next section has already faded in. The reveal is *invisible* — the user just sees content that's already there.
- `threshold: 0.1` — 10% of the element must be visible. Avoids triggering on a 1-pixel sliver.

### 4. Stagger — list items (capped at 8)

```css
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
  transition-delay: calc(560ms + (var(--stagger-decay) * (var(--child-index, 0) - 8)));
}
```

**The 8-item cap is a perceptual rule, not a technical one.** Beyond 8 items with a stagger, the eye stops tracking the individual items and the stagger becomes a generic "everything appearing at once with a slight delay." 8 is the max where the stagger still *reads* as a sequence.

For a 50-item dossier, the visual effect is: items 1-8 fade in distinctly, then items 9-50 fade in as a 40ms-per-item trickle. The reader's eye is on the content, not the animation.

### 5. Hover — color, opacity, transform (150ms)

```css
a, button, .interactive {
  transition: color var(--dur-fast) var(--ease-in-out),
              opacity var(--dur-fast) var(--ease-in-out),
              transform var(--dur-fast) var(--ease-in-out);
}
```

**Use only on actual interactive elements** — links, buttons, accordion triggers. Do not put hover transitions on body text, headings, or other non-interactive elements. Hover-on-text is a tell of a non-native-feeling interface.

### 6. Focus — keyboard accessibility (instant)

```css
:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
  border-radius: 2px;
}
```

Focus indicators are **instant** (no transition). They are the user's *proof* that the keyboard is being heard by the page. Animating them is hostile to keyboard users.

**Always use `:focus-visible`, never `:focus`.** `:focus-visible` is the modern standard — it suppresses the focus ring for mouse clicks (which don't need it) and shows it for keyboard tabbing (which does). Supported in Chrome 86+, Firefox 85+, Safari 15.4+.

### 7. Exit — rare in v1 (defer to v2)

In v1, content does not exit. The only "exit" patterns are:

- **User-triggered dismiss** (e.g., a "close" button on a notification): 150ms `opacity` 1 → 0, then `display: none`. Use sparingly.
- **Page navigation** (when v2 introduces multi-page): use the View Transitions API (Chrome 126+ cross-document). Defer to v2.

**Do not use exit animations on scroll.** "Fade out as you scroll up" is a feel-bad pattern — the user feels like content is being taken away.

### 8. Scroll-tied — progressive enhancement only

```css
@supports (animation-timeline: view()) {
  .fade-in-stagger > * {
    animation: fade-in linear forwards;
    animation-timeline: view();
    animation-range: entry 0% cover 30%;
  }
}
```

**This is a no-op in browsers that don't support `animation-timeline: view()`.** The IO + CSS path is the fallback for Chrome <115, Safari <26, and Firefox (which has shipped it as of 2026-06, but the rule is still wrapped in `@supports` for safety).

The visual result is identical between the two paths. The advantage of the scroll-driven path: it runs **off the main thread** (compositor), so even on a 3-year-old phone, the animation is silky smooth.

## Accessibility contract

This is the *non-negotiable* layer. The full a11y checklist is in `notes/a11y-checklist.md`; the motion-specific parts are:

### `prefers-reduced-motion: reduce` — both CSS and JS must honor

**CSS layer** (the default state is "motion is off"; motion is opted-in via the media query):

```css
.fade-in, .fade-in-stagger > * {
  /* default: no motion */
  opacity: 1;
  transform: none;
}

@media (prefers-reduced-motion: no-preference) {
  @keyframes fade-in {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .fade-in {
    opacity: 0;
    animation: fade-in var(--dur-base) var(--ease-out-expo) forwards;
  }
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
}
```

**JS layer** (the IO block also checks the media query and skips the animation):

```javascript
var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (prefersReduced) {
  document.querySelectorAll('.fade-in-stagger').forEach(function(el) {
    el.classList.add('is-visible');
  });
  return;
}
```

**Why two layers:** if a future CSS refactor accidentally breaks the `@media` wrap, the JS still respects the OS preference. Defense in depth.

### No motion that triggers vestibular disorders

The patterns above all use `transform: translateY()` and `opacity`. Both are safe for vestibular disorders (no rotation, no scaling, no parallax). The Apple spring-out curve is decelerating, not oscillating, so it doesn't trigger motion sickness.

**Forbidden in v1:**

- Rotation animations
- Scaling animations
- Parallax scrolling
- Background-attachment: fixed (parallax-adjacent)
- Auto-playing video with motion
- `setInterval` / `setTimeout` (no time-driven motion)

## Performance contract

- **No layout shift.** All animations use `transform` and `opacity`. Never `top`, `bottom`, `left`, `right`, `width`, `height`, `margin`, `padding`.
- **GPU-composited.** The `transform: translateY()` and `opacity` properties are GPU-composited. The animation runs on the compositor thread, not the main thread. The page is responsive during the animation.
- **Single IO observer per page.** The IO block creates one observer, observes all `.fade-in-stagger` elements. ~30 lines of JS, ~1KB uncompressed.
- **No infinite animations.** Every animation is `forwards` — it ends and stays at the final state. No looping, no bouncing, no perpetual motion.
- **No JS for the readable surface.** The IO block is the only JS. If JS is disabled (or fails to load), the content is visible by default (because the CSS opacity is 1 unless wrapped in `@media (prefers-reduced-motion: no-preference)`).

## Anti-patterns to avoid

- **Skeleton loaders.** They're a confession that the page is slow. The dossier rendering is <100KB; it doesn't need a skeleton.
- **Loading spinners.** The page is local; it loads instantly. No spinner.
- **Bounce / overshoot easing.** Anything that overshoots and settles (`cubic-bezier` with a y > 1) feels playful, not professional. Mavis's surface is a desk, not a toy.
- **Multiple animations on the same element.** One element, one motion. Stacking animations (e.g., a fade-in *and* a slide-up *and* a scale) is a sign the designer doesn't know what they want.
- **Animations that delay the LCP.** The Largest Contentful Paint (typically the H1 or the first paragraph) should not be animation-delayed. The H1 is `.fade-in` with no delay; only the children get the stagger.
- **Animations on text selection or hover.** Selecting text or hovering over a paragraph is the user's action, not a state to design for. Don't transition on `::selection` or `p:hover`.

## Reference

- **Design system spec (the tokens + render hints):** `[[../dossiers/fleet-status-design-system]]`
- **A11y checklist (the contract):** `[[./a11y-checklist]]`
- **CSS template (the implementation):** `[[../scripts/fleet-status.css]]`
- **Researcher dossier (the engineering spine):** `[[../../Researcher/dossiers/dev_tooling/markdown-to-html-ui]]` (Section 2: fade-in animation)
- **Build Spec v1:** `[[../../../03 Projects/Fleet-Status Surface/01 Build Spec]]`
- **MDN IntersectionObserver:** https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
- **MDN CSS scroll-driven animations:** https://developer.mozilla.org/en-US/docs/Web/CSS/animation-timeline
- **Chrome for Developers: Animate elements on scroll (Bramus):** https://developer.chrome.com/docs/css-ui/scroll-driven-animations
- **prefers-reduced-motion (MDN):** https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion

---

*This motion vocabulary is the grammar of how Mavis's HTML surfaces feel. Three rules, eight patterns, one a11y contract. The Builder takes this + the design system spec + the a11y checklist + the CSS template and ships the renderer.*
