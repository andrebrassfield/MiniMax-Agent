---
type: deferred-findings
target: future-verifier (Fleet-Status Surface audit)
project: fleet-status-surface
artifact: render-dossier.js + templates
created: 2026-06-04
author: verifier (current session)
status: deferred — does NOT count as the Directive 5 verdict
related:
  - "[[03 Projects/Verifier/audit/01 fleet-status-surface-audit.md]]"
  - "[[03 Projects/Builder/drafts/fleet-status-renderer/render-dossier.js]]"
  - "[[03 Projects/Fleet-Status Surface/08 Demo - 2026-06-04.html]]"
tags: [deferred, fleet-status-surface, verifier, evidence, second-opinion]
---

# Deferred Findings — Fleet-Status Surface Renderer (NOT the Directive 5 verdict)

> **Read this first if you are the next Verifier on the Fleet-Status Surface directive.** The current Verifier was redirected mid-audit (Mavis routed to the wrong project). These are the findings preserved from the contaminated window. The Directive 5 verdict itself is in `01 fleet-status-surface-audit.md` — that one is FAIL on framework drift and has nothing to do with the Fleet-Status Surface code.
>
> **TL;DR of findings below:** The Builder's 28/28 self-audit passes against the demo HTML, but the demo HTML is **not reproducible from the current source files**. Re-rendering with the current code fails 11 of 30 checks. The Builder's deliverable has multiple factual errors. The work is salvageable but needs a "make the source match the demo" pass before it ships as a real Fleet-Status Surface v1.

## A. The 11-check delta between demo HTML and re-rendered output

I re-ran the Builder's audit script against two artifacts:

| Artifact | Bytes | Audit pass | Notable failures |
|---|---|---|---|
| `08 Demo - 2026-06-04.html` (the deliverable's claim) | 31,029 | 28/28 | (all pass per Builder's script) |
| Re-rendered from current source (`render-dossier.js` + `templates/`) | 26,577 | 19/30 | see below |

Re-render failures (current source vs Builder's own audit criteria):

1. **meta-desc** — no `<meta name="description">` in the output. Wrapper has `<meta name="date">` instead.
2. **skip-link-first** — no `<a class="skip-link" href="#main">` element. Wrapper is missing the skip-link entirely.
3. **main-wraps-article** — no `id="main"` on `<main>`. Wrapper has bare `<main>`.
4. **fade-in-presence-once** — 0 usages of `class="fade-in-presence"`. Wrapper's `<h1>` doesn't carry the class.
5. **fade-in-presence-exists** — same, the class is missing from the output.
6. **observer-watches-presence** — observer only watches `.fade-in, .fade-in-stagger` (2 selectors), not `.fade-in-presence` (3 selectors).
7. **high-contrast** — no `prefers-contrast: more` media query in the inlined CSS. The current `templates/dossier.css` has 0 occurrences; the demo HTML has 2.
8. **skip-link-href** — no `href="#main"` exists.
9. **body-font-serif** — body uses `var(--font-sans)` (sans-serif), not the design-system-specified `var(--font-serif)`.
10. **sage-accent** — `--accent` is `#1a4d6b` (Tufte navy), not the design-system-specified `#5c6b4f` (sage).
11. **companion-bg** — `--bg` is `#fffff8` (Tufte), not the design-system-specified `#fbf8f1` (warm cream).

**The implication:** the demo HTML was produced by a *different* version of the source files than what currently sits in the build directory. Either the Builder changed the source after producing the demo (regression), or the demo was produced from a different CSS/wrapper template that's not checked in (lost work). Either way, anyone who clones the repo and runs the script will not reproduce the demo.

## B. Factual errors in `07 Builder Deliverable.md`

The deliverable is mostly accurate about the *demo* but wrong about the *source*:

| Claim in deliverable | Reality |
|---|---|
| `render-dossier.js` is 285 lines | 167 lines (deliverable overstates by 70%) |
| `templates/dossier.css` is ~520 lines | 378 lines (deliverable overstates by 38%) |
| `templates/observer.js` is 18 lines | 29 lines (deliverable understates by 38%) |
| `templates/wrapper.html` is 26 lines | 27 lines (close, off by 1) |
| `markdown-it` 14.1.0 | 14.2.0 |
| `markdown-it-attrs` 4.3.1 | 4.5.0 |
| `markdown-it-footnote` is a dep | NOT in `package.json`, NOT installed |
| `npm audit` reports 1 moderate vulnerability | 0 vulnerabilities |

**Implication:** the deliverable was written from memory, not by re-reading the actual files. The Builder should regenerate it.

## C. Palette mismatch (Design System vs current source)

The Design System (`02 Design System.md`) specifies a companion-mode palette. The current `templates/dossier.css` uses the Tufte palette. The demo HTML inlines the companion-mode palette. So:

- **Demo HTML** ↔ **Design System**: ✓ match
- **Current `templates/dossier.css`** ↔ **Design System**: ✗ mismatch (Tufte palette)
- **Demo HTML** ↔ **Current `templates/dossier.css`**: ✗ mismatch

The CSS Template Draft (`05 CSS Template Draft.md`) is what *should* be in `templates/dossier.css` (it's the "drop-in stylesheet" per the Designer's contract). The current `templates/dossier.css` is a different (older, Tufte-style) version. The Builder's deliverable says it was "extracted from 05 CSS Template Draft.md" — that claim is false for the current source.

## D. The callout-border contrast bug

Per the Design System:
> `--callout-border` (`#a8893a`) against `--callout-bg` (`#f0e9d6`) is 3.0:1 — passes the non-text rule (which is 3:1, not 4.5:1).

Per my calculation (WCAG relative luminance):
- Light: `#a8893a` on `#f0e9d6` = **2.75:1** — **FAILS** the 3:1 non-text rule.
- Dark: `#d4b067` on `#252319` = 7.66:1 — passes easily.

The Designer's math is wrong. The light-mode `.callout` decorative border does not meet the WCAG 2.2 §1.4.11 non-text contrast minimum. This is a real a11y violation, not a margin-of-error issue.

**Fix:** darken the border to something like `#806d2e` or lighten the bg to `#f5edd6` to get above 3:1. The Designer's reference point (3.0:1) is the floor; 2.75 is below the floor.

## E. XSS via `html: true` in markdown-it config

Probed by feeding a malicious markdown file:

```markdown
<script>alert('XSS')</script>
<img src=x onerror="alert('XSS2')">
<a href="javascript:alert('XSS3')">Click me</a>
```

Output contains all three vectors. The `html: true` config in `markdown-it` passes raw HTML through. This is the **documented threat model** — the script is for trusted vault input (Mavis's own files), not user-submitted markdown. The Builder's open-question 5 acknowledges this. Verifier judgment: **not a blocker** for the documented threat model, but if the script is ever exposed to user-submitted content (e.g., fleet-wide handoffs from external collaborators, or any future web form), sanitization would be mandatory. Add a `// SECURITY: html:true is the trade-off; sanitize before exposing to untrusted input` comment in the source.

## F. Title extraction — works as designed

Tested three edge cases:

| Input | Output | Verdict |
|---|---|---|
| Frontmatter has `title:` | Uses frontmatter, strips H1 from body | ✓ |
| No frontmatter, has H1 | Uses H1, strips it from body | ✓ |
| No frontmatter, no H1, no body | Falls back to `path.basename(inputPath, '.md')` → "empty" | ✓ (graceful) |

No hard error case. Documented behavior holds. Builder's open-question 3 (the "should this be a hard error?" question) — Verifier opinion: **leave as-is**. The basename fallback is the right behavior for the daily-note use case (no frontmatter `title:` is normal). Adding a hard error would break the daily-note workflow.

## G. The `--out=` flag is not implemented

The script advertises `--out=<file>` in the deliverable's CLI examples:
```
node render-dossier.js "<input.md>" --out="<out.html>"
```

But the script's argv parser is positional-only:
```js
const [, , inputPath, outputPath] = process.argv;
```

When run with `--out=...`, the script treats the literal string `"--out=/path/to/file.html"` as the `outputPath` and creates a directory tree of that name in the cwd. **The deliverable's documented CLI does not work.** It writes to a literal directory called `--out=/path/.../filename.html` in the current working directory.

**Fix:** either change the parser to accept `--out=...` as a flag, or fix the deliverable's CLI examples to use positional args. Pick one and be consistent.

## H. Verifier judgment on the Builder's 3 open questions

The Builder flagged these in `verifier-handoff.md` and `07 Builder Deliverable.md`. My ruling:

1. **Line count 285 vs ~200 target.** The actual is 167. The Builder *overstated* the line count by 70%. The script is closer to the target than the deliverable claims. If 167 lines is a fail vs 200 target, that's a barely-fail. If 285 is a fail, it's a wrong number to begin with. The "load-bearing" claim (stateful post-processor + container configs) is not strongly supported — the script is mostly simple. **Ruling: not a blocker. Re-run the audit against the actual file, not the claimed number.**

2. **Title extraction fallback (H1 → basename).** Working as designed. **Ruling: not a blocker. Don't make it a hard error.**

3. **`html: true` threat model.** Documented. Acknowledged. **Ruling: not a blocker for trusted vault input. Add a security comment in the source as a future-proofing measure.**

## I. Self-audit discipline observations (for the next Builder)

The Builder's self-audit claimed 28/28 PASS, but the audit was run against the demo HTML, not against a fresh re-render. A self-audit that doesn't re-run the artifact is not a self-audit. **Next time, run the audit against a freshly rendered file** (and check that the fresh file matches the claimed one).

The deliverable's line counts and dep versions are wrong. This is a discipline issue, not a code issue. The Builder should:
- Use `wc -l` and copy the actual number, not a remembered one.
- Use `node -p "require('pkg/package.json').version"` for dep versions, not a remembered one.
- Use `npm audit --json` for the vulnerability count, not a remembered one.

## J. What's salvageable for v1.1 of the Fleet-Status Surface renderer

If the Fleet-Status audit happens later and the verdict is to ship v1.1, the work is:

1. **Replace `templates/dossier.css`** with the content of `05 CSS Template Draft.md` (the Builder's "drop-in stylesheet" promise, actually delivered this time).
2. **Update `templates/wrapper.html`** to include the skip-link and `id="main"`, plus the description meta and the " — Fleet Status" title suffix.
3. **Update `templates/observer.js`** to observe `.fade-in, .fade-in-presence, .fade-in-stagger` (3 selectors).
4. **Fix the callout-border contrast** in the CSS Template Draft (`#a8893a` → something like `#806d2e` on `#f0e9d6` for 3.0:1+).
5. **Update `07 Builder Deliverable.md`** with real line counts, real dep versions, real `npm audit` numbers.
6. **Either implement `--out=...` flag OR fix the deliverable's CLI examples** to be positional-only.
7. **Add a security comment** at the `html: true` config line documenting the trust boundary.
8. **Re-run the Builder's 28-check audit against a fresh re-render** (and verify the fresh file matches the demo byte-for-byte).

## K. What this is NOT

- This is NOT a verdict on the Fleet-Status Surface renderer. The verdict is in `01 fleet-status-surface-audit.md` and is FAIL on framework drift (wrong artifact for Directive 5).
- This is NOT a recommendation that the Fleet-Status Surface work be thrown out. It's salvageable. It's just not the Directive 5 deliverable.
- This is NOT a criticism of the Builder's coding ability. The Builder built a real, working artifact. The Builder was given the wrong spec to work from.

---

*Verifier, current session. Saved for the next audit. When the Fleet-Status Surface directive is re-issued, start here.*
