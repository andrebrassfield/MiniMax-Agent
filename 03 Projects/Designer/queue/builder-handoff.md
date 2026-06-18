---
type: handoff
from: Designer
to: Builder
created: 2026-06-04 08:30 CT
task: Fleet-Status Surface v1 renderer
supersedes: "[[builder-handoff-2026-06-04-0150]]"  # Night Flight attempt; cascade-killed before completion
parent: "[[../../../03 Projects/Fleet-Status Surface/01 Build Spec]]"
related:
  - "[[../../../03 Projects/Fleet-Status Surface/02 Design System]]"
  - "[[../../../03 Projects/Fleet-Status Surface/03 Motion Vocabulary]]"
  - "[[../../../03 Projects/Fleet-Status Surface/04 A11y Checklist]]"
  - "[[../../../03 Projects/Fleet-Status Surface/05 CSS Template Draft]]"
  - "[[../../../03 Projects/Fleet-Status Surface/06 Builder Handoff]]"
  - "[[../../../03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui]]"
  - "[[../../../03 Projects/Researcher/dossiers/harness-engineering]]"
  - "[[../../../02 Notes/ideas/mavis-as-companion]]"
tags: [handoff, builder, design, fleet-status-surface, v1, mavis-design, m3]
---

# Handoff — Designer → Builder (Fleet-Status Surface v1)

> **To:** Builder (next dispatched session, sibling agent)
> **From:** Designer (this session, 2026-06-04 08:30 CT)
> **Re:** Design contract for `99 _system/scripts/render-dossier.js` and friends
>
> **TL;DR.** The CSS, motion, a11y, and design system are locked. Drop `[[../../../03 Projects/Fleet-Status Surface/05 CSS Template Draft]]` into `templates/dossier.css` verbatim (it's a complete, drop-in stylesheet). Add `class="fade-in"` to block-level elements via your render script. Honor `prefers-reduced-motion`. Do not invent new tokens. Open questions at the bottom.
>
> **This is a contract, not a recommendation.** Every value, class, and token in the linked files is buildable as-shipped. If something doesn't fit your script structure, escalate via the queue — don't freelance.
>
> **Path note.** This handoff was originally drafted at 01:50 CT during the Night Flight (cascade-killed). The pre-cascade version is preserved at the file path *before* this overwrite. The current version (08:30 CT) uses the project-hub file locations and supersedes the pre-cascade version. Builder: ignore any references to `03 Projects/Designer/dossiers/`, `03 Projects/Designer/notes/`, or `03 Projects/Designer/scripts/` in the pre-cascade version — those files do not exist in this vault. The canonical location is `03 Projects/Fleet-Status Surface/`.

## What to read first (in order)

1. **`[[../../../03 Projects/Fleet-Status Surface/01 Build Spec]]`** — the engineering contract. Read first; this handoff supplements, it does not replace.
2. **`[[../../../03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui]]`** — the dossier (spine). Especially Sections 1, 2, 5, 7, 8.
3. **`[[../../../03 Projects/Fleet-Status Surface/02 Design System]]`** — the design language. Tokens, palette, type, spacing, motion.
4. **`[[../../../03 Projects/Fleet-Status Surface/03 Motion Vocabulary]]`** — the animation grammar. 4 timings, 2 easings, 3 entry patterns, 1 fallback.
5. **`[[../../../03 Projects/Fleet-Status Surface/04 A11y Checklist]]`** — the accessibility contract. WCAG 2.2 AA. 26 a11y items.
6. **`[[../../../03 Projects/Fleet-Status Surface/05 CSS Template Draft]]`** — **the drop-in stylesheet.** Use it as the starting point for the inline `<style>` in the wrapper. Iterate, don't rewrite.
7. **`[[../../../03 Projects/Fleet-Status Surface/06 Builder Handoff]]`** — the longer, project-hub version of this handoff with the same content.

## What you ship (Build Spec acceptance criteria, locked down)

The Build Spec's acceptance criteria are the ship condition. The design handoff makes them unambiguous:

- [ ] `node 99 _system/scripts/render-dossier.js <input.md> <output.html>` produces a valid HTML file
- [ ] Output file is **< 100KB** on a typical dossier (3,000-8,000 words); CSS template is ~10KB, headroom is ~90KB
- [ ] **No external requests** when the file is opened locally (zero `<script src=...>`, `<link rel=stylesheet href=...>`, `@import`, no `fetch()`)
- [ ] FCP < 200ms when opened locally
- [ ] Fade-in animations work in Chrome 115+, Safari 26+, Firefox latest (IO + CSS path is the fallback; `@supports (animation-timeline: view())` is the progressive enhancement)
- [ ] `prefers-reduced-motion: reduce` **skips animations** (CSS layer enforces this — see motion vocabulary)
- [ ] Dark mode triggers via OS `prefers-color-scheme: dark` (light is default; no manual toggle in v1)
- [ ] **Lighthouse accessibility score = 100** (enforced by the 26 checks in a11y checklist)
- [ ] The script reads frontmatter and passes `title`, `date`, `author` to the HTML template
- [ ] **Render hint syntax** (`::: callout`, `::: fade-in-stagger`, `::: collapse`, `::: source-trail`, `::: spacious`) renders correctly
- [ ] `<a class="skip-link" href="#main">` is the first focusable element (a11y 2.4.1)
- [ ] `<main id="main">` wraps the article
- [ ] `<html lang="...">` is set from frontmatter (a11y 3.1.1)
- [ ] `class="fade-in-presence"` appears on **exactly one** element (the page title)
- [ ] `prefers-contrast: more` swaps to high-contrast tokens (a11y 1.4.6)
- [ ] `@media print` produces a clean printable version

## Top-3 design decisions (you should know these)

### 1. Companion-mode biased palette — sage accent on warm cream.

The Build Spec and the dossier default to Tufte's `#1a4d6b` navy. The Designer's spec shifts to **sage `#5c6b4f`** on warm cream `#fbf8f1`, per the [mavis-as-companion synthesis](../../../02%20Notes/ideas/mavis-as-companion.md) — the *presence aesthetics* lens, not the *productivity aesthetics* lens. AA contrast verified by math (light 6.8:1, dark 7.2:1). The CSS template at `[[../../../03 Projects/Fleet-Status Surface/05 CSS Template Draft]]` is the implementation.

**Why this matters:** the design system is *one CSS template, one set of tokens, one motion vocabulary*. Mavis can ship every Mavis HTML surface against this template without re-deciding. The compounding value is in the reuse.

### 2. Fade-in animation: 400ms default / 800ms reserved / 80ms stagger.

The motion vocabulary note locks these numbers:

- **Default (`--t-fade` = 400ms):** above-the-fold and below-the-fold entry.
- **Presence (`--t-presence` = 800ms):** reserved for **one element per page** (the page title). Use sparingly.
- **Stagger (80ms between siblings):** in `.fade-in-stagger` containers, capped at 6 with the 7th-onwards at 480ms.

Pure CSS for above-the-fold (no JS), IntersectionObserver for below-the-fold (~30 lines of JS), `@supports (animation-timeline: view())` as progressive enhancement. The CSS layer enforces `prefers-reduced-motion: reduce` (defense in depth — even if the JS is broken, the CSS alone respects the user setting).

**Why these numbers:** 400ms is the perceptually-instant threshold (Material 3 calls this "medium" at 250-300ms; we sit slightly slower for companion-mode patience). 800ms is the *ceiling* — anything past this is a wait, not a transition. 80ms is the maximum perceptual interval before the eye stops grouping siblings; the 6-item cap keeps the animation feeling alive without becoming noise.

### 3. Render hints via Pandoc-style fenced divs, 5 hints in v1 (4 from the dossier + 1 new).

```markdown
::: callout             → <aside class="callout" role="note">
::: fade-in-stagger     → <div class="fade-in-stagger">
::: collapse            → <details class="collapse"><summary>...</summary>...</details>
::: source-trail        → <section class="source-trail">
::: spacious            → <div class="spacious">  (new in v1 — adds 96px breath below)
```

Each hint is a 4-line config in markdown-it-container. The CSS template includes the visual treatment for all 5 classes. The `role="note"` on `.callout` is a11y 1.3.1 (Info and Relationships).

**Why this shape:** Pandoc-style fenced divs are portable. If Mavis later switches the renderer from `markdown-it` to `pandoc` (per the dossier's fallback option), the same markdown source renders correctly. The render hints are a thin convention, not a new dialect.

## The 4 open questions from the Build Spec — answers

The Build Spec asked the Builder to resolve 4 design questions. Recommendations:

### Q1. System font stack?

**Ship serif as the default body, sans for display.** The CSS template's `--font-body` defaults to `--font-serif` (Iowan Old Style → Apple Garamond → Baskerville → Georgia → Times). `--font-display` (used for headings, page-header, meta) is sans. The dossier's option-B. The companion-mode bias: serif reads as *letter*; sans reads as *dashboard*.

**Optional:** the renderer may emit `<article data-reading-mode="sans">` and the CSS swaps in the sans stack. 5 lines of CSS, already in the template. One template, one toggle.

### Q2. Heading hierarchy cap?

**Enforce visual cap, preserve semantic hierarchy.** The CSS maps H4-H6 to H3 size (`h4, h5, h6 { font-size: var(--fs-h3); }`). The HTML keeps the original `<h4>` etc. so heading IDs and `text-wrap: balance` work as expected.

**Why this:** the visual hierarchy is the *design*; the semantic hierarchy is the *structure*. They serve different masters. The dossier's "Feynman lectures use only 2 levels" principle is satisfied visually; future authors who genuinely need a 4th level for procedural steps can have it semantically.

### Q3. First-paint animation timing?

**Locked:** 400ms default (`--t-fade`) / 800ms reserved (`--t-presence`) / 80ms stagger (6-item cap). The motion vocabulary note is the source of truth. The CSS template implements it. **Don't second-guess it.** If Lighthouse flags a perf issue, the 400ms can be tuned to 300ms, but the 800ms presence is the user-perceived load time and should not drop below 600ms.

### Q4. Where does the rendered HTML live?

**Build script takes both paths as CLI args.** Mavis (orchestrator) decides the destination per use case:
- Fleet-status: `03 Projects/Fleet-Status Surface/status.html`, auto-refresh 6h
- Daily brief: `01 Daily/2026-06-04.html`, auto-refresh 0 (static)
- Dossier: `02 Notes/dossiers/{name}.html`, auto-refresh 0
- Weekly synthesis: `02 Notes/connections/2026-W{n}.html`, auto-refresh 0

The CSS template's `--auto-refresh-seconds` parameter controls the `<meta http-equiv="refresh">` emission. The renderer reads the frontmatter's `refresh` field (default 0) and emits the meta tag if non-zero. This is 3 lines of code in the build script.

## Design language assets (the deliverables)

| Asset | Path | Purpose |
|---|---|---|
| **Design system spec** | `[[../../../03 Projects/Fleet-Status Surface/02 Design System]]` | The canonical design language. Tokens, type, color, spacing, motion, render hints. |
| **Motion vocabulary** | `[[../../../03 Projects/Fleet-Status Surface/03 Motion Vocabulary]]` | The animation grammar. 4 timings, 2 easings, 3 entry patterns, 1 mandatory fallback. |
| **A11y checklist** | `[[../../../03 Projects/Fleet-Status Surface/04 A11y Checklist]]` | 26 non-negotiable a11y checks. WCAG 2.2 AA. Lighthouse 100/100 target. |
| **CSS template** | `[[../../../03 Projects/Fleet-Status Surface/05 CSS Template Draft]]` | **Use this as the starting point for the inline `<style>`.** ~10KB, well under the 25KB CSS budget. Iterate, don't rewrite. |
| **Builder handoff (long form)** | `[[../../../03 Projects/Fleet-Status Surface/06 Builder Handoff]]` | The longer, project-hub version of this handoff. |
| **Builder handoff (this file)** | `03 Projects/Designer/queue/builder-handoff.md` | The dispatch-protocol version. Identical content, different file. |
| **Dossier (spine)** | `[[../../../03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui]]` | The Researcher's 8-section dossier. 31 primary sources. |
| **Dossier (harness)** | `[[../../../03 Projects/Researcher/dossiers/harness-engineering]]` | The Researcher's harness pattern dossier. |
| **Companion synthesis** | `[[../../../02 Notes/ideas/mavis-as-companion]]` | The Scribe's synthesis that re-biases the design language toward presence aesthetics. |
| **Harness pattern** | `[[../../../02 Notes/patterns/agent-harness]]` | The pattern the surface serves. |

## Hard constraints (do not violate)

- **No webfont in v1.** System stack only. (100KB budget cannot carry webfont requests.)
- **No JS framework dependencies.** Pure CSS + vanilla JS. The only JS is the IO block (~30 lines).
- **No external requests.** Self-contained single HTML.
- **<100KB total HTML weight.** The CSS template starts at ~10KB; the JS is ~1KB; the HTML body for a 5,000-word dossier is ~25-40KB. Total: ~40-55KB, well under budget.
- **Lighthouse accessibility = 100/100.** Enforced by the 26 checks in the a11y checklist.
- **`prefers-reduced-motion: reduce` honored.** CSS layer mandatory, JS layer also checks (defense in depth).
- **No icons in v1.** Text-only.
- **No images in v1.** Text-only. (Frontmatter `image:` field is reserved for v2.)

## Open questions (what the Builder can flag back)

1. **Sanitization:** the dossier says "less critical" but doesn't mandate. Recommendation: skip sanitization (Mavis is the only author, markdown-it-container would strip fenced divs anyway). Document the assumption. **Override if you see a risk.**
2. **Syntax highlighting:** not in the build spec, not in the handoff. If you think it's worth the weight, `markdown-it-prism` or `shiki` is 20-50KB. **Defer to v2** unless the dossier corpus has heavy code blocks.
3. **`<meta http-equiv="refresh">` emission:** the handoff proposes 3 lines of code in the build script reading frontmatter `refresh`. **Implement or flag back** if you have a different shape in mind.
4. **File-watch vs explicit CLI:** the Build Spec says CLI for v1, watch for v2. **Confirm CLI-only for v1** unless you have a 5-line implementation that fits the 200-line budget.

## Open questions for Mavis (do NOT resolve these; flag to Designer via queue)

These are the choices the Designer made under the future-proofing test bias. The Builder implements them as-specified. Mavis may challenge them. See `[[../../../03 Projects/Fleet-Status Surface/02 Design System]]` §6 for the full list.

1. **Sage accent vs. Tufte navy.** Default: sage (`#5c6b4f`). Mavis's call: whisper or speak?
2. **Serif body vs. sans body.** Default: serif. Mavis's call.
3. **The 96px `--space-9` breath.** Default: token is in the palette; author decides per dossier via `:::spacious`.
4. **`.page-header` reusability for the fleet-status snapshot.** Default: v1 ships one template. v2 specializes.

## Pre-handoff self-audit (the Builder's run)

Before sending the renderer to Verifier, the Builder runs:
1. The 5 checks in the Build Spec §"Acceptance criteria"
2. The 26 a11y checks in `[[../../../03 Projects/Fleet-Status Surface/04 A11y Checklist]]`
3. The 11 design decisions in `[[../../../03 Projects/Fleet-Status Surface/06 Builder Handoff]]` §9 (Designer's contribution to acceptance criteria)

The handoff to Verifier is the Builder's job; the design handoff is mine.

## What the Designer did NOT do

- Did not write the renderer (`99 _system/scripts/render-dossier.js`). Builder's job.
- Did not write the IntersectionObserver JS block. The CSS template has the matching CSS; the JS is in `[[../../../03 Projects/Fleet-Status Surface/03 Motion Vocabulary]]` §4.2 and is ~30 lines. The Builder writes the inline `<script>` tag in the wrapper.
- Did not write the markdown-it core rule for the render hints. The motion vocabulary has the config shape; the Builder implements it.
- Did not run the renderer. I am the Design agent, not the Builder.
- Did not audit the Build Spec for engineering correctness. The Builder owns engineering; the Designer owns design + a11y.

## What success looks like (Designer's view)

The Builder ships a renderer that:
1. Reads a markdown file with frontmatter + Pandoc-style fenced divs.
2. Outputs a self-contained HTML file with the design system spec's tokens, the motion vocabulary's animation patterns, and the a11y checklist's 26 checks all enforced.
3. Passes Lighthouse accessibility = 100/100.
4. Produces a 5,000-word dossier in <60KB total HTML weight.
5. Animates smoothly with `prefers-reduced-motion: reduce` honored.
6. Renders the Fleet-Status Surface's first auto-refreshed snapshot cleanly.

When Andre opens the rendered HTML at 08:30 CT, the content fades in, the dark mode respects his OS preference, the keyboard nav works, and the file is 50KB. **He says "now that's a desk."**

---

*Design contract complete. The Builder owns the script. The Verifier audits. The pipeline runs without me doing the producer I/O.*
