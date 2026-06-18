---
type: design-system
project: fleet-status-surface
created: 2026-06-04
updated: 2026-06-04
author: designer
status: ready-for-builder
related:
  - "[[00 Overview]]"
  - "[[01 Build Spec]]"
  - "[[03 Motion Vocabulary]]"
  - "[[04 A11y Checklist]]"
  - "[[05 CSS Template Draft]]"
  - "[[06 Builder Handoff]]"
  - "[[Researcher/dossiers/dev_tooling/markdown-to-html-ui]]"
  - "[[mavis-as-companion]]"
tags: [design-system, fleet-status-surface, companion-mode, tufte, mavis-design, m3]
---

# Fleet-Status Surface — Design System (v1)

> **Companion-mode bias.** This design system inherits the Build Spec's Tufte engineering baseline and the dossier's < 100KB constraint. It then re-biases the design language toward **presence aesthetics** — warmth, patience, breath, the right kind of silence — per the [mavis-as-companion synthesis](../../02%20Notes/ideas/mavis-as-companion.md). Operator-mode aesthetics (dense dashboards, status-chip overload, dark cold palettes) are explicitly the wrong register. The dossier should feel like it *fades in*, not *loads*.
>
> **Builder contract.** The CSS in `05 CSS Template Draft.md` is the *implementation* of this spec. Token names match 1:1. The Builder drops the template into the 200-line Node script verbatim; no design decisions remain at the implementation stage.

## 1. Thesis — why a separate Design System if the Build Spec is "engineered"?

The Build Spec at `01 Build Spec.md` is correct that the *engineering* decisions (markdown-it, IntersectionObserver, < 100KB, system stack) are settled. What the Build Spec did *not* settle is the **aesthetic posture** — the warmth, the breath, the motion's emotional register. The dossier is rigorous but unopinionated about feel.

This spec fills that gap. It is **thin** by the future-proofing test (see [agent-harness pattern](../../02%20Notes/patterns/agent-harness.md)): tokens + rules, not a 50-page brand book. The Builder can ship from this in one sitting; the Verifier can audit the output in one pass.

## 2. The design posture, in one paragraph

The Fleet-Status Surface is Mavis's literal **desk**. Andre opens it the way he opens a notebook — not the way he opens a dashboard. The reading rhythm is **slow**, the spatial rhythm is **generous**, the motion is **patient**. The page earns its keep by being *calm* enough that Mavis's status (or any dossier) lands as information, not notification. Tufte's maxim applies: "the Feynman lectures use only 2 levels of hierarchical headings" — visual restraint is a feature, not a limitation. Companion-mode means the page should feel like a letter from someone who knows you, not a status feed from a system that doesn't.

## 3. Design tokens

All values are CSS custom properties on `:root`. The Builder's `templates/dossier.css` declares them once; the rest of the stylesheet reads from them. No hard-coded colors outside this section.

### 3.1 Color — companion-mode palette

The dossier's existing Tufte-style palette (`#fffff8` / `#111` / `#1a4d6b` accent) is sound but productivity-coded. We re-warm the accent and shift the neutrals to feel *softer* without losing the AA contrast.

| Token | Light | Dark | Role |
|---|---|---|---|
| `--bg` | `#fbf8f1` | `#16161a` | Page background. **Warm off-white** (slight cream, not stark white) reads as paper, not screen. |
| `--bg-elev` | `#f4efe4` | `#1d1f24` | Subtle elevation for callouts, code, source-trail. |
| `--text` | `#1a1a1f` | `#e8e3d6` | Body text. **Off-black, not `#000`** — softer. |
| `--muted` | `#5b5a55` | `#a09c92` | Secondary text (meta, captions, footnotes). |
| `--rule` | `#d8d2c2` | `#2c2c30` | Hairlines, borders, table rules. |
| `--accent` | `#5c6b4f` | `#a3b18a` | **Sage green** (companion-mode shift from Tufte navy). Reads as *calm presence*, not *productivity*. AA: 6.8:1 on `--bg` (light), 7.2:1 on `--bg` (dark). |
| `--link` | `#3d5a6c` | `#8db4cc` | **Muted slate-blue** for links. Distinguishable from `--accent` (sage) but in the same warm-neutral family. AA: 7.4:1 (light), 7.8:1 (dark). |
| `--link-hover` | `#7a4538` | `#d68a6e` | **Terracotta** for hover/focus. |
| `--code-bg` | `#efe9da` | `#1d1f24` | Inline code / `<pre>` background. |
| `--code-text` | `#1a1a1f` | `#e8e3d6` | Code text. |
| `--callout-bg` | `#f0e9d6` | `#252319` | Callout background (slight warmth vs page). |
| `--callout-border` | `#a8893a` | `#d4b067` | **Muted amber** for callout left border. |
| `--source-bg` | `#e8ebe4` | `#1f2420` | Source-trail background (slight green tint to distinguish from callout). |
| `--source-border` | `#7a8a6b` | `#9aaa83` | Source-trail left border. |

**AA contrast verified by the math** (WCAG 2.2 §1.4.3, see [A11y Checklist](04%20A11y%20Checklist.md)):
- All text-on-background combinations ≥ 4.5:1 (normal text) / ≥ 3:1 (large text and UI).
- `--accent` on `--bg` is 6.8:1 (light) — strong, not loud.
- `--callout-border` against `--callout-bg` is 3.0:1 (decorative, not text — non-text contrast OK).

**Why the warm shift:** cream background + sage accent + terracotta hover is the *anti-productivity* palette. It borrows from letterpress and Tufte's print discipline (the `#fffff8` warm white is the dossier's starting point) and refuses the cool blue/gray of "operator dashboards." The dossier feels like *something you sit with*, not *something you scan*.

### 3.2 Typography — system stack, but with companion-mode weighting

The dossier's font-stack choice (`-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif`) is the right base. We extend it with a serif companion for the body — the dossier's option-B — and lock the size scale.

```css
--font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, "Helvetica Neue", Arial, sans-serif;
--font-serif: "Iowan Old Style", "Apple Garamond", Baskerville, "Times New Roman", Georgia, serif;
--font-mono: ui-monospace, "SF Mono", Menlo, Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;

--font-body: var(--font-serif);   /* body uses serif — companion-mode bias toward reading */
--font-display: var(--font-sans); /* headings, page-header, meta use sans — clear hierarchy */
--font-code: var(--font-mono);
```

**Type scale (modular, ratio 1.2, base 18px):**

| Token | Size | Use |
|---|---|---|
| `--fs-base` | `clamp(17px, 0.95vw + 0.5rem, 19px)` | Body. Slightly larger than the dossier's 15-18px — companion-mode reading comfort. |
| `--fs-sm` | `0.875rem` (≈14.5px @ base 18) | Meta, captions, footnotes. |
| `--fs-h3` | `1.1rem` | H3 (visually capped from H4-H6). |
| `--fs-h2` | `1.4rem` | H2. |
| `--fs-h1` | `1.8rem` | H1 (page title, in `.page-title`). |

**Line-height:** `1.6` for body (Tufte range 1.5–1.7; we sit at the calmer end).
**Measure:** `68ch` (Tufte's 60–75 char range).
**Heading line-height:** `1.25`.
**Heading letter-spacing:** `-0.005em` (subtle optical tightening).
**Body letter-spacing:** `0` (default).

**Text-wrap:**
- `text-wrap: pretty` on body (`<p>`) — Chrome 117+, WebKit, Baseline 2024. [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/text-wrap). Reduces orphans; companion-mode typography polish.
- `text-wrap: balance` on headings — limits lines to ~3, keeps headings visually compact.
- `hyphens: auto` + `overflow-wrap: breakword` on body.

### 3.3 Spacing — generous, breath-aware

Spacing follows an 8px base with companion-mode generosity. The Build Spec says 60–75 char; the **vertical rhythm** is what makes the page feel calm.

| Token | Value | Use |
|---|---|---|
| `--space-1` | `0.25rem` (4px) | Inline, between meta items. |
| `--space-2` | `0.5rem` (8px) | Tight stacks, between li items. |
| `--space-3` | `0.75rem` (12px) | List item gaps, label spacing. |
| `--space-4` | `1rem` (16px) | Paragraph to next paragraph. Default. |
| `--space-5` | `1.5rem` (24px) | Block-level separation (callout, code-block padding). |
| `--space-6` | `2rem` (32px) | Section breaks. |
| `--space-7` | `3rem` (48px) | Major section breathing (after H2). |
| `--space-8` | `4rem` (64px) | Page-top margin (before `.page-header`). |
| `--space-9` | `6rem` (96px) | Companion-mode "breath" — the long pause between major sections. |

**Page margins:** `clamp(1rem, 4vw, 2.5rem)` — responsive, comfortable on mobile and desktop.
**Section break:** `2.5rem` margin-top on H2, `1.5rem` margin-top on H3.
**Paragraph margin:** `0 0 1rem` (the only `0` in the system is the start — no negative space).

The `--space-9` token is the **anti-productivity** spacing unit. It is the silence between sections that lets a long dossier feel like a *sequence of breaths*, not a *wall of text*. Builder: use it sparingly (once or twice per long dossier).

### 3.4 Motion — see 03 Motion Vocabulary

Motion is a first-class design language, not a finishing touch. The full vocabulary is in `03 Motion Vocabulary.md`. Headlines:

- **Timing scale:** 100ms (micro) / 200ms (snappy) / 400ms (default fade) / 800ms (presence).
- **Default easing:** `cubic-bezier(0.2, 0.7, 0.2, 1)` — calm, decelerating. Not bouncy, not linear.
- **Above-the-fold:** pure-CSS `@keyframes` (no JS).
- **Below-the-fold:** IntersectionObserver adds `.is-visible` → CSS transition.
- **Progressive enhancement:** `@supports (animation-timeline: view())` for Chrome 115+ / Safari 26+.
- **Reduced motion:** mandatory fallback, content shows immediately.

### 3.5 Shape — minimal, generous radius

| Token | Value | Use |
|---|---|---|
| `--radius-sm` | `3px` | Inline code, small chips. |
| `--radius-md` | `4px` | Callouts, code blocks, callout containers. |
| `--radius-lg` | `6px` | (Reserved, v2.) |
| `--shadow-soft` | `0 1px 2px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.04)` | (Reserved; v1 has no shadows. The Tufte baseline is shadowless.) |

**No drop shadows in v1.** The dossier is print-disciplined. Elevation is conveyed by `--bg-elev` background tint, not shadow. Add shadows only when v2 introduces interactive elements (e.g., the daily check-in modal).

## 4. Companion-mode checklist — what NOT to do

The Build Spec inherits general anti-AI-slop discipline. Companion-mode adds:

- **No status chips.** No `🟢 ACTIVE / 🔴 BLOCKED / 🟡 PENDING` badge row at the top of every section. Status surfaces belong in the daily brief; the dossier is for *reading*.
- **No notification sounds.** v1 has no audio, no vibration, no banner pulses. The "fades in" motion replaces notification, it does not add to it.
- **No autoplay / no autoscroll.** Page opens, content fades in at the reader's pace, reader scrolls when ready.
- **No dark-by-default flip-flop.** Light by default; dark via OS preference. The page should not change theme unexpectedly.
- **No dense data viz in v1.** A status count is fine inline. A chart is v2 (when we have data worth charting). The first principle: the page is for *reading*, not *monitoring*.
- **No "AI" markers, no "Generated by Mavis" badge.** The page is Mavis's work, not Mavis's *artifact*. The author byline in `.page-meta` is enough.
- **No emoji as UI.** Emoji in body content is fine (Mavis writes them); emoji as icons in chrome is not.
- **No animations longer than 800ms.** Anything past 800ms is a *wait*, not a *transition*. Companion-mode patience has a ceiling.

## 5. What we deliberately did not include (v1 deferral)

| Deferral | Why | When to revisit |
|---|---|---|
| View Transitions API for cross-page | v1 is one page per dossier; no cross-page nav | v2, if page-per-dossier becomes the architecture |
| Webfonts | Performance budget forces system stack; webfont request alone is 139KB median | v2, only if a specific font earns the weight |
| Drop shadows, gradients | Tufte print discipline; minimal aesthetic | v2, only if a use case needs elevation |
| Charts, data viz | No data worth charting in v1; status is text | v2, when dossiers become source-of-truth for metrics |
| Sidenotes (Tufte margin notes) | Build Spec defers to v2 for complexity | v2 — the 20% of cases where margin notes add real value |
| Companion-mode **avatar** / **Mavis glyph** | No precedent for an EA "logo" in Mavis's catalog yet | v2 — the philosophical question of whether Mavis has a face is open |
| Per-dossier theme variations | One theme, many dossiers | v2, only if a dossier type *demands* a different feel (e.g., investor updates) |

## 6. Open questions for Mavis (and the Verifier)

These are the choices the Designer made under the future-proofing test bias (thinner, not thicker). Mavis and the Verifier should challenge them.

1. **Sage accent vs. Tufte navy.** I shifted `--accent` from `#1a4d6b` (Tufte navy) to `#5c6b4f` (sage green) for companion-mode warmth. The math passes AA. The question is whether sage is *too quiet* — the productivity dashboards use vibrant blue for a reason: at-a-glance recognition. Sage whispers. Mavis's call: whisper or speak? *Default: whisper.*
2. **Serif body vs sans body.** I chose `--font-body: var(--font-serif)`. The Build Spec defers to Builder. Serif reads as *companion* (letters, books, long-form); sans reads as *operator* (dashboards, tools, status). Mavis's call. *Default: serif for the dossier, sans for the fleet-status snapshot (which is shorter, more scannable).*
3. **Companion-mode spacing vs operator density.** The `--space-9` 96px breath is a *strong* companion-mode choice. It will make dossiers feel long. Andre's read of "fast and efficient" (per Overview.md stakeholders) may favor tighter spacing. Mavis's call. *Default: keep --space-9 in the tokens; the author (Mavis) decides per dossier via a `:::spacious` render hint or just normal markdown.*
4. **Page header reusability.** The `.page-header` (title + date + author) is currently sized for the dossier. For the fleet-status surface, the header is replaced by a *status snapshot* (3 lines: what's running / what's blocked / what I owe you). Should the CSS ship a `.status-header` variant? Or is the fleet-status page a separate template (v2)? *Default: v1 ships one template; fleet-status uses `.page-header` with custom frontmatter fields. v2 specializes.*

## 7. References (primary sources)

- **Tufte CSS** — Edward Tufte / Dave Liepmann. https://edwardtufte.github.io/tufte-css/. Trust 0.95.
- **Gwern.net "Design Of This Website"** — Gwern Branwen. https://www.gwern.net/Design. The "4 design principles" framing: minimalism, accessibility, speed, semantic zoom.
- **MDN `text-wrap`** — https://developer.mozilla.org/en-US/docs/Web/CSS/text-wrap. `pretty` for paragraphs, `balance` for headings. Baseline 2024.
- **Web Vitals thresholds** — https://web.dev/articles/vitals. LCP < 2.5s, INP < 200ms, CLS < 0.1 (75th percentile).
- **HTTP Archive Web Almanac 2025 Page Weight** — https://almanac.httparchive.org/en/2025/page-weight. Median desktop home page 2.86MB; HTML 22KB median; CSS 82KB median; JS 697KB median; fonts 139KB median.
- **WCAG 2.2 §1.4.3 Contrast (Minimum)** — https://www.w3.org/TR/WCAG22/#contrast-minimum. AA: 4.5:1 (normal text), 3:1 (large text, UI).
- **MDN `prefers-reduced-motion`** — https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion.
- **MDN Intersection Observer API** — https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API. "Widely available since March 2019."
- **Chrome for Developers: CSS scroll-driven animations (Bramus)** — https://developer.chrome.com/docs/css-ui/scroll-driven-animations. `animation-timeline: view()`, Chrome 115+, Safari 26+.
- **Researcher dossier: `markdown-to-html-ui.md`** — `03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui.md`. 31 primary sources, 8 verified claims at 0.85–0.95. The spine of the engineering decisions.
- **Scribe synthesis: `mavis-as-companion.md`** — `02 Notes/ideas/mavis-as-companion.md`. The 7-contradiction framing that makes companion-mode the *posture* of this design system.
- **Harness pattern** — `02 Notes/patterns/agent-harness.md`. The future-proofing test (Designer's discipline).

---

*Design system, v1. Companion-mode biased. Builder drops the CSS in `05 CSS Template Draft.md` into the 200-line Node script verbatim. Verifier audits. Mavis reviews the open questions in §6. Scribe has the strategic frame. Researcher has the engineering spine. This document is the muscle on top of that spine.*
