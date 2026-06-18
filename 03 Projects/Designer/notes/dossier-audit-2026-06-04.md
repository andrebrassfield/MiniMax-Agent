---
type: audit
created: 2026-06-04
status: complete
scope: 03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui.md
auditor: Designer
related:
  - "[[../dossiers/fleet-status-design-system]]"
  - "[[../notes/motion-vocabulary]]"
  - "[[../notes/a11y-checklist]]"
  - "[[../../../03 Projects/Fleet-Status Surface/01 Build Spec]]"
tags: [audit, dossier, design, fleet-status-surface]
---

# Dossier Audit — `markdown-to-html-ui.md` (2026-06-04)

> **Auditor:** Designer (newly onboarded, 2026-06-04 01:35 CT)
> **Source dossier:** `03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui.md` (8 sections, 31 primary sources, 0.85-0.95 trust floor)
> **Context:** The Build Spec v1 explicitly *declined* a Designer (see `01 Build Spec.md` lines 25-29), but Mavis (EA) reversed that decision at 01:32 CT to capture a **reusable design system** for *every* future Mavis HTML surface — not just v1. This audit validates the dossier's engineering choices and surfaces the design language the dossier did not specify.

## Audit framing

The dossier is the **spine** (engineering: libs, budgets, animation techniques, render-hint syntax). I am authoring the **muscle** (typography pairing, color tokens, spacing scale, motion vocabulary, accessibility checklist, the CSS template the Builder can iterate on). My job is to:

1. Verify each dossier design choice is sound for production.
2. Surface gaps the Builder will trip over without explicit guidance.
3. Extend with the design language the dossier did not specify.
4. Hold the line on hard constraints (no webfont, no JS framework, a11y non-negotiable).

## Section-by-section audit

### Section 1 — Markdown → HTML rendering surface — **SOUND**

**The verdict is correct:** `markdown-it` server-side, build-time, with `markdown-it-anchor` + `markdown-it-container` + `markdown-it-attrs` plugins. **Trust 0.95.**

**Gaps I close:**

- **G1.1 — Sanitization posture is underspecified.** The dossier says "sanitization is less critical but still a recommended discipline" but does not name a concrete default. The Build Spec v1 also does not mandate a sanitizer. **My recommendation:** because Mavis is the *only* author and the markdown lives in the trusted vault, the renderer should *skip* HTML sanitization (it would strip pandoc-style fenced-divs anyway) but should add a defense-in-depth `markdown-it-attrs` allowlist so the renderer cannot be tricked into writing arbitrary `class`/`id` values via `{#id .class}` syntax from untrusted inputs. For v1, Mavis-authored-only is the assumption; document the assumption in `00 wrapper.html` as a `<meta name="author-trust" content="vault-resident-v1">` comment so the v2 author can flip it.

- **G1.2 — Code-block syntax highlighting is absent.** Tufte CSS uses a serif body but a monospace for code. The dossier doesn't say whether to add a syntax highlighter. **My recommendation:** no syntax highlighter in v1 (each adds 20-50KB; the dossier is `<100KB` total). A 4-line CSS token for `pre`, `code`, `<code class="language-*">` with `font-variant-ligatures: none` and a 1.05 line-height is enough. Ship highlighted code in v2 if Andre's reading density demands it.

- **G1.3 — `markdown-it-anchor` slugify strategy is not specified.** Default slugify lowercases and replaces spaces with hyphens. For Mavis's headliny dossier titles ("Build Spec v1", "2026-06-04 — Designer ONBOARDED"), that becomes `build-spec-v1` and `2026-06-04-designer-onboarded`. **My recommendation:** use the default `github-slugger` (already in `markdown-it-anchor`'s deps). Add `permalink: false` (we don't want `¶` glyphs in Tufte).

### Section 2 — CSS fade-in animation (zero-JS preferred, IO acceptable) — **SOUND**

**The verdict is correct:** hybrid pure-CSS `@keyframes` for first paint + IntersectionObserver for scroll-into-view, with `@supports (animation-timeline: view())` progressive enhancement. **Trust 0.9.**

**Gaps I close:**

- **G2.1 — Exact animation timings not specified.** The Build Spec v1 says "Builder's call: 400ms / 600ms / 80ms stagger." **My design decision** (codified in `notes/motion-vocabulary.md` and the CSS template):
  - Above-the-fold entrance: **400ms** `cubic-bezier(0.16, 1, 0.3, 1)` (ease-out-expo; "decelerate hard, settle soft"). 8px translateY → 0, opacity 0 → 1.
  - Below-the-fold reveal: **600ms** same curve, triggered by IO `is-visible` class. **80ms stagger** between siblings, capped at 8 (then 40ms beyond that — perceptual clutter control).
  - **Rationale:** the 400/600 split matches Material Motion's "incoming / incoming-content" durations and the `cubic-bezier(0.16, 1, 0.3, 1)` is the "Apple spring-out" curve that feels alive without being bouncy. Stagger cap at 8 is a hard rule — beyond 8 items, the eye stops tracking individual items and the stagger becomes noise.

- **G2.2 — "Reveal budget" for a typical dossier not specified.** If the dossier is 3,000 words, scrolling reveals ~30-50 `fade-in-stagger` children. **My design decision:** stagger cap of 8 + IO `rootMargin: '0px 0px -10% 0px'` (start loading before the user actually sees the element, by 10% of the viewport) + threshold `0.1` (10% of element visible triggers reveal). This means by the time the user reads the bottom of the dossier, the entire page is visible — but it never feels like a "reveal show."

- **G2.3 — `prefers-reduced-motion` handling is correct in the dossier but the CSS to honor it is missing.** My CSS template wraps every animation in `@media (prefers-reduced-motion: no-preference) { ... }` and provides a non-animated `is-visible` state by default. The IO script also checks the media query and skips adding `is-visible` if reduced motion is requested. **Both layers must be present** — defense in depth.

- **G2.4 — `@starting-style` is listed but not adopted.** The dossier says "defer to v2." **My audit agrees** — Chrome 117+ only, Firefox and Safari support is inconsistent as of 2026-06. The hybrid approach (IO + `@keyframes`) is the right v1 path.

- **G2.5 — `view-transition-name` for intra-page nav is not in scope.** v1 is one long page. Confirmed.

### Section 3 — Tufte-inspired long-form layout — **SOUND**

**The verdict is correct:** 60-75 char body, system stack, no webfont, `text-wrap: pretty` on body, `text-wrap: balance` on headings, dark mode via `prefers-color-scheme`. **Trust 0.95.**

**Gaps I close:**

- **G3.1 — System stack specific tokens not in the dossier.** The dossier names the sans stack and a serif fallback, but doesn't specify the monospace stack, the heading stack, the cap-height, the x-height, the leading ratio. **My design system spec** (`dossiers/fleet-status-design-system.md`) defines:
  - **Sans UI stack:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, 'Helvetica Neue', Arial, sans-serif` (covers macOS, Windows, Linux, Android; 'Helvetica Neue' + 'Arial' are belt-and-suspenders for older systems).
  - **Serif body stack (for text-heavy dossiers):** `'Iowan Old Style', 'Apple Garamond', 'Baskerville', 'Times New Roman', 'Droid Serif', Times, 'Source Serif Pro', serif` — 8 fonts covers 99% of macOS/Windows/Linux.
  - **Monospace stack:** `ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace` (ui-monospace is the modern Firefox 92+ / Chrome 91+ / Safari 14+ system-mono token).
  - **Type scale:** 1.250 (Major Third) — `0.875rem` (sm), `1rem` (base), `1.25rem` (h4), `1.563rem` (h3), `1.953rem` (h2), `2.441rem` (h1). 6 sizes, semantic only — no `text-2xl` Tailwind-style proliferation.
  - **Leading ratio:** 1.5 body (Tufte-canonical), 1.25 headings, 1.6 code blocks.
  - **Measure (line length):** 64ch max-width, content centered in viewport with `margin-inline: auto`, viewport-padded at `clamp(1rem, 4vw, 2rem)`.

- **G3.2 — "Dark mode by default-light" is ambiguous.** The dossier says "dark mode by default-light" which I read as "the default is light mode, with dark mode available via OS preference." **My design decision:** light mode is default. `prefers-color-scheme: dark` triggers the dark palette. **We do NOT ship a manual toggle in v1** — that would require JavaScript to persist the choice (localStorage), and the dossier says "no JS beyond the IntersectionObserver." OS preference is the right v1 answer. v2 (with View Transitions) is the right time to add a manual toggle.

- **G3.3 — Tufte sidenotes are out of v1 scope per the Build Spec.** Confirmed. The CSS template includes a stub `.sidenote` rule so a v2 author can implement them without rewriting the cascade.

- **G3.4 — `text-wrap: balance` for headings is a good call but has caveats.** Browser support: Chrome 114+, Firefox 121+, Safari 17.5+. Below those, the fallback is `text-wrap: wrap` (which is the default, so the rule is a progressive enhancement). **My CSS template** wraps it in `@supports (text-wrap: balance) { ... }` to make the intent explicit.

- **G3.5 — Heading hierarchy cap is correct but enforcement is unspecified.** The Build Spec says "cap at H4-H6 visually to H3." **My CSS template** maps H4-H6 to H3-size-type but keeps the H4-H6 semantic levels (so `text-wrap: balance` + the original `id` for jump-links work). This is the right shape — visual hierarchy enforced, semantic hierarchy preserved.

### Section 4 — Existing similar tools audit — **SOUND**

The audit of `content-deck-generator`, `html-presentation-generator`, `landing-page-builder`, `pptx-generator`, `visual-summary`, Obsidian Publish, and Quartz 5 is thorough. **The build-vs-borrow decision is correct** for v1: borrow from `content-deck-generator` (auto-refresh shape), ignore the binary-deliverable skills.

**Gaps I close:**

- **G4.1 — The "anti-animation" stance from `html-presentation-generator` is misclassified as "wrong for our use case."** The Build Spec reads it as a feature for export. **My audit agrees** — the PPTX-export pattern is "stable, predictable, no surprises." That's a *different* UX from the Mavis reading surface. Worth a one-paragraph rationale in `dossiers/fleet-status-design-system.md` to lock the design philosophy.

- **G4.2 — `content-deck-generator`'s 60s `<meta http-equiv="refresh">` is the right inspiration for fleet-status but wrong for dossiers.** A dossier doesn't auto-refresh — it's a static artifact. **My design decision:** the CSS template is parameterizable via a single `--auto-refresh-seconds` CSS custom property. `0` (default) = no refresh. Non-zero = the build script emits a `<meta http-equiv="refresh" content="N">` tag in `<head>`. Fleet-status sets it to 21600 (6h); dossiers set it to 0. No CSS change needed.

### Section 5 — Self-contained vs server-rendered tradeoffs — **SOUND**

The verdict is correct: single self-contained HTML, CSS inlined, no external requests, **<100KB total uncompressed**.

**Gaps I close:**

- **G5.1 — The 100KB budget needs a per-line accounting.** A typical dossier (3,000-8,000 words) will hit:
  - HTML body: 35-50KB (markdown text density ≈ 5 bytes/word → 15-40KB rendered + 5-10KB structure overhead)
  - Inline CSS: **must stay under 30KB** (Tufte-CSS baseline is 4KB; my design system spec adds typography tokens + motion library + render-hint styles → ~15-18KB realistic, headroom 12KB)
  - IntersectionObserver inline JS: 1KB
  - Total realistic: **46-81KB**, well under budget. The **30KB inline CSS hard ceiling** is the design constraint that matters.

- **G5.2 — The dossier doesn't say what happens if the budget is exceeded.** **My design decision:** the build script (`render-dossier.js`) should print a warning to stderr if the output exceeds 80KB (80% of budget) and a hard fail at 100KB. This makes the budget a build-time gate, not a launch-day surprise.

- **G5.3 — "AI crawlers see the initial raw HTML" is a real value.** Worth a callout in the design system spec — the self-contained shape isn't just for offline use, it's for AI-crawler indexing, and that's a Mavis-as-EA posture (the work is legible to *anyone* who can read the file, not just to a browser with JS).

### Section 6 — AI-agent → human content surfaces (the emerging pattern) — **SOUND but philosophical**

The pattern analysis (Claude Artifacts, ChatGPT Canvas, Perplexity Pages) is correct, and the "Mavis-archive variant" framing is the right one. **The dossier's source set is thin (3 primary launches + 1 inference)** — this section's trust should be 0.7, not 0.85. **Not blocking for v1.**

**Gaps I close:**

- **G6.1 — The "AI output landing page" pattern needs a *visual signature*, not just a name.** What's the visual difference between a Mavis dossier and a Claude Artifact? **My design system spec** answers this with a "Mavis-archive visual signature": Tufte-CSS typography (the off-white `#fffff8` and off-black `#111111`), generous margins, the fade-in animation, the absence of any chrome. The signature *is* the design language. Worth a one-paragraph philosophy section in the design system spec.

- **G6.2 — "Companionship aesthetics ≠ productivity aesthetics"** is the strategic insight the dossier hints at but doesn't say. The strategic context in `00 Inbox/2026-06-04 — the-missing-use-case-of-ai-you.md` is the reason for the design choice. **My design system spec** opens with this: "Mavis's surface is a *companion* surface, not a *product* surface. The reading experience should feel like opening a friend's notebook, not opening a SaaS dashboard."

### Section 7 — Performance budget — **SOUND but the budget table needs the design contract**

The Web Vitals + HTTP Archive numbers are correct. The budget table is the right shape.

**Gaps I close:**

- **G7.1 — The dossier lists targets but doesn't say *what to do if any is missed*.** **My design decision:** the build script measures FCP/CLS at build time (using a headless puppeteer-style assertion) and refuses to write the output if any metric is out of bounds. The dossier doesn't have a toolchain for this; the Builder can wire it up. **Defer to v2** if the build-time assertion is too much for v1's 200-line budget.

- **G7.2 — "Zero third-party scripts" is a strong stance and the right one.** Document it in the design system spec as a *non-negotiable* for v1, with a "revisit in v2" footnote for the case where Mavis wants to add a RUM endpoint to measure LCP/INP/CLS in the field.

- **G7.3 — The dossier's "Accessibility (axe / Lighthouse) 100 / 100" is the right target.** The a11y checklist (Phase 6) is the build-time check that *enforces* this target, not just measures it. The a11y checklist is the quality bar; Lighthouse is the audit.

### Section 8 — Author markdown structure — **SOUND, with one ambiguity**

The frontmatter / heading hierarchy / semantic breaks / code fences / image alt / render-hints are well-specified.

**Gaps I close:**

- **G8.1 — "Cap at H3" is a soft rule.** Some dossiers will need H4 for procedural steps ("Step 1, Step 2, Step 3, Step 4"). **My design system spec** is more lenient: H3 is the *preferred* cap, H4 is allowed but visually de-emphasized to a smaller weight of the H3 type. The CSS enforces visual hierarchy, not semantic hierarchy.

- **G8.2 — `::: callout` syntax is the right shape but the visual is unspecified.** Tufte has no callouts. **My design decision** (in the CSS template): callout uses a left border (4px solid `--color-accent`), padding 1rem 1.5rem, background `color-mix(in srgb, var(--color-accent) 5%, var(--color-bg))`. No icons in v1. The 4px solid left border is the visual signature — it's distinctive, accessible (it survives color-blindness and high-contrast mode), and low-weight.

- **G8.3 — `::: collapse` syntax needs HTML clarity.** The dossier shows `<summary>Click to expand</summary>` as a child of the `:::` block. **My design system spec** documents this: the render script transforms `::: collapse` to `<details class="collapse">` and the *first line* of the block content becomes the `<summary>`. This avoids the "where do I put the summary" confusion.

- **G8.4 — `::: source-trail` is a Mavis-specific render hint not generic to markdown.** Document it as a Mavis-research pattern, not a portable construct. The CSS template includes a stub `.source-trail` rule with a horizontal divider above, a smaller font, and a citation list styling.

## Cross-cutting audit findings

### Sound dossier choices (do not change)
1. `markdown-it` server-side, build-time rendering. **Verified.**
2. Hybrid pure-CSS + IntersectionObserver for fade-in. **Verified.**
3. `@supports (animation-timeline: view())` progressive enhancement. **Verified.**
4. Tufte-inspired typography, system stack only, no webfont. **Verified.**
5. Self-contained single HTML, no external requests. **Verified.**
6. Pandoc-style fenced divs for render hints. **Verified.**
7. <100KB total budget with the 28x-lighter-than-median-web-page framing. **Verified.**

### Dossier gaps the Builder needs explicit guidance on (my design system + motion library + a11y checklist + CSS template close these)
1. **G1.1, G2.1, G2.2, G2.3, G3.1, G3.2, G3.4, G3.5, G4.2, G5.1, G5.2, G6.1, G6.2, G7.1, G7.2, G7.3, G8.1, G8.2, G8.3, G8.4** — all addressed in the design system spec + motion library + CSS template.

### Open questions the Build Spec asked the Builder to resolve — my recommendations
- **System font stack:** ship the sans stack as the default. Add the serif body stack as a `data-reading-mode="serif"` attribute on `<article>` that swaps it in. Builder can implement the data-attr-driven swap in 5 lines of CSS.
- **Heading hierarchy cap:** enforce visual cap, preserve semantic hierarchy. CSS maps H4-H6 to H3 type-size; HTML keeps the original `<h4>` etc.
- **First-paint animation timing:** 400ms entrance, 600ms scroll-reveal, 80ms stagger capped at 8, then 40ms. The 8-item cap is in the motion library and the CSS template.
- **Where the rendered HTML lives:** the build script takes both paths as CLI args. Mavis (orchestrator) decides the destination per use case. This matches the Build Spec's suggestion.

### Contradictions worth Mavis's attention
- **The Build Spec v1's "no Designer needed" stance (line 25-29) is technically correct for v1 but strategically narrow.** The dossier is the design spec *for v1*. A reusable design system is needed *for v2 and beyond* (every future Mavis HTML surface). The reversal to onboard the Designer is the right call — not because v1 needs it, but because the design system is a compounding asset that pays for itself across 5+ future surfaces (dossiers, briefs, weekly syntheses, fleet-status, dashboards). The dossier is the spine; the design system is the muscle; both are needed.
- **"Dark mode by default-light" is one of those phrases that could be misread.** I'm reading it as "default = light, dark = opt-in via OS preference." If Mavis read it as "default = dark, light = opt-in," that's a one-line fix in the CSS template. **Confirm this with Mavis before the Builder ships.**
- **The dossier says "first-paint animation timing" is "Builder's call" but my design system spec is locking it to 400/600/80ms.** This is a design decision, not an engineering ambiguity, and the Builder should take it as a given. The motion vocabulary note is the source of truth; the CSS template implements it; the Builder shouldn't second-guess it.

## Audit verdict

**Overall:** the dossier is **engineered sound, design-incomplete, philosophically undercooked.** Engineering: 0.95. Design language: 0.4 (no typography pairing, no color tokens, no spacing scale, no motion timings, no a11y contract). Philosophy: 0.6 (the "AI output landing page" pattern is named but the visual signature isn't).

**My deliverables close the design and philosophy gaps.** The Builder can ship v1 against the design system spec + CSS template + motion library + a11y checklist without ambiguity. v2 (generalize to all Mavis outputs) will need a one-page addendum to the design system spec when the page-per-dossier decision is made.

**Audit complete.** Filing this in `03 Projects/Designer/notes/dossier-audit-2026-06-04.md` for the design system, motion library, a11y checklist, and CSS template to reference.
