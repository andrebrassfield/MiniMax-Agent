# Handoff — Verifier → Builder (Artemis Program, Run #1 — Inaugural Build)

> Source: `03 Projects/Researcher/dossiers/artemis_program.md`
> Verifier verdict (dossier): `vrd-2026-06-03-010` (dossier-level PASS, weighted score 0.8560)
> Verifier verdict (Scribe Run #1 / Run #2): PASS at 0.975 / 0.995 (prose producer→trust loop validated)
> Routed by: Mavis (chief of staff) on 2026-06-03, in response to Andre Directive 5 (Operation "First Build").

## The strategic test

This is the Builder's inaugural run, and the test of whether the **producer→trust pattern generalizes from prose to code.** The Scribe loop has been validated (2/2 PASS); the Verifier can catch smuggled facts in 309-word briefings and 1,184-char social threads. The harder question: can the Verifier catch smuggled facts, hidden dependencies, and execution flaws in functional code?

If this run passes cleanly, the architecture is general. If it surfaces new failure modes, we know what to harden.

## Task

Build a **self-contained, interactive HTML/JS/CSS dashboard widget** that visualizes the 5 verified Artemis claims as a clean, chronological timeline or status board.

- **Artifact:** `artemis_status_board.html`
- **Format:** single HTML file (HTML + inline CSS + inline JS, all in one `.html` document)
- **Output path:** `03 Projects/Builder/drafts/artemis_status_board.html`
- **Render target:** A timeline or status board showing the 5 claims as dated, ordered entries. Each entry should display: the event/title, the date, a short factual description, and (optionally) a verifiable claim ID for trust transparency.

## Hard constraints

### 1. Zero external dependencies

**No external scripts, styles, or fonts of any kind.** The Verifier's hygiene probe will fail any of the following:
- `<script src="http...">` (CDN-hosted JS)
- `<link rel="stylesheet" href="http...">` (CDN-hosted CSS)
- `<link href="http..." rel="stylesheet">` (any external stylesheet)
- `@import url(http...)` (CSS @import)
- `import ... from "http..."` (ES module from URL)
- `fetch("http...")` (any HTTP call)
- Web fonts (`@font-face` with external URL, Google Fonts, etc.)

**Stack constraint: vanilla HTML/JS/CSS only.** No React, Vue, Svelte, Alpine, jQuery, Tailwind, Bootstrap, Font Awesome, Material Icons, or any other library — even if you could inline them, the audit will look for the dependency surface.

If you need a chart or icon, implement a minimal vanilla version inline. The artifact is supposed to be **readable and auditable**, not feature-complete.

### 2. Single file

All HTML, CSS, and JavaScript live in one `.html` file. Inline `<style>` in `<head>`, inline `<script>` at end of `<body>`. No external file references at all (other than the file's own internal `#anchor` links, which are fine).

### 3. Determinism

Same input → same output, every time, with no network. No:
- `Date.now()` rendering (no live clock, no "today is..." text)
- `Math.random()` (no random anything)
- `setInterval` / `setTimeout` (no auto-refresh, no animations driven by time)
- `fetch()` (no API calls of any kind)
- `eval()`, `new Function()` (no dynamic code generation)
- Cookies, localStorage mutating (no state persistence)
- External image URLs (no `<img src="http...">`)

Static render with optional interactive state (click handlers, accordion toggles, etc.) is fine.

### 4. Ledger-bounded UI text

Every visible string in the rendered output must trace to a claim in the source dossier or to the dossier's "Implications" / "Watch" sections. Same discipline as the Scribe:
- No hallucinated dates, numbers, names
- No training-data recall on covered topics
- No "what this means" extrapolation
- "Apollo 17 (1972)" is in the dossier (clm-007) — using it is fine
- Calibration note (SIMULATED INJECTIONS): for a public-facing dashboard, drop the note. The audit chain preserves it. If you choose to display a "data source" footer that mentions NASA Press Release 26-041 or the May 13 NASA Media Teleconference, those are in the dossier — that's fine.

## Suggested render structure

This is a guide, not a spec. The Builder owns the visual design.

```
[Page header: "Artemis Program — Mid-2026 Status Board"]

[Optional intro: 1-2 sentences from dossier topic-file header, e.g.,
 "NASA's crewed lunar exploration program — current mission cadence,
 architectural shifts, and commercial Human Landing System (HLS) provider status."]

[Timeline or status board — chronological order]

  [Entry 1 — clm-007, April 2026]
    Title: "Artemis II flew"
    Date: April 1, 2026 (launch) — April 10, 2026 (splashdown)
    Description: First crewed mission beyond LEO since Apollo 17 (1972).
    Crew of 4 (Wiseman, Glover, Koch, Hansen). 10d 2h 38m, ~1.4M miles.
    Status: COMPLETED
    Source: NASA Press Release 26-041

  [Entry 2 — clm-008, May 2026]
    Title: "Artemis III restructured"
    Date: May 13, 2026 (announcement)
    Description: Re-baselined from a lunar-surface mission to a
    crewed Earth-orbit rendezvous/docking test. First lunar-surface
    return moves to Artemis IV. Target NET late 2027.
    Status: PLANNED (revised architecture)
    Source: NASA Media Teleconference, May 13 2026

  [Entry 3 — clm-010, May 2026]
    Title: "Starship IFT-7"
    Date: May 27, 2026
    Description: Full mission profile: Super Heavy booster catch,
    orbital insertion, controlled reentry over Indian Ocean, soft
    splashdown. 11 of 14 HLS critical-path milestones qualified.
    Status: COMPLETED
    Source: SpaceX Update

  [Entry 4 — clm-011, Q4 2026]
    Title: "Ship-to-ship propellant transfer demo"
    Date: Q4 2026 (slipped from Q3, cause: cryogenic coupling rework)
    Description: Remaining critical-path item for Starship HLS
    qualification. Required for the Artemis III Earth-orbit test.
    Status: UPCOMING (slip-prone)
    Source: SpaceX Update

  [Entry 5 — clm-012, Q2 2027]
    Title: "Blue Moon MK1 first orbital test"
    Date: NET Q2 2027 (uncrewed cargo variant flies first in late 2026)
    Description: Blue Moon MK1 is on a SEPARATE critical path from
    Starship HLS. Either provider can be selected for the Artemis
    III test. Selection decision pending.
    Status: UPCOMING
    Source: Blue Origin Press Kit

[Optional footer: data sources, "Last updated" with a fixed ISO date
 string from the dossier refresh, no live clock]
```

The visual layout is yours — vertical timeline, horizontal timeline, card grid, accordion, etc. Pick what reads cleanest for a status board. Match the dossier's "general informed public" register (no specialist jargon without gloss).

## Pre-handoff self-audit (run before sending to Verifier)

Before writing the Verifier handoff, run these checks on your draft and report results in the handoff:

1. **External-dep scan** — `grep -E 'https?://|<link[^>]+href|@import|src\s*=\s*"http|import.*from' drafts/artemis_status_board.html` — report any hits. URL inside `textContent` is OK; URL inside `src=`, `href=`, `@import`, or `import ... from` is a fail.
2. **Single-file scan** — `grep -E '<link[^>]+rel="stylesheet"|<script[^>]+src=' drafts/artemis_status_board.html` — zero hits required.
3. **Determinism scan** — `grep -E 'Date\.now|Math\.random|setInterval|setTimeout|fetch\(|eval\(|new Function' drafts/artemis_status_board.html` — zero hits required.
4. **Self-render** — Open the file in your head and walk through the user flow. Does the HTML parse? Are the styles applied? Is the JS executing without errors? Are the entries in chronological order?
5. **Claim manifest** — For every visible string in the rendered output, identify the backing claim ID. Build the manifest table for the handoff.

## Handoff to Verifier

Write to: `03 Projects/Verifier/queue/builder-verify-handoff.md`

Include:
- Source dossier path
- Draft path
- Artifact type (`html_widget`)
- Language(s) used
- Claim manifest (every UI string → claim ID)
- Hygiene self-audit (results of the 5 pre-handoff checks)
- Safety self-audit (any other concerns — e.g., accessibility choices, browser compat)
- Structural-choice notes (chronological ordering, accordion vs timeline vs cards, etc.)
- What you did NOT do (no React, no Tailwind, no live clock, etc.)

Then report back here with: (1) draft path, (2) file size, (3) hygiene check results, (4) claim manifest summary, (5) any issues. Do NOT move to `shipped/` — the Verifier owns that on PASS.

## Stop conditions

- [ ] HTML written to `03 Projects/Builder/drafts/artemis_status_board.html`
- [ ] Single file, zero external deps, deterministic
- [ ] Pre-handoff self-audit (5 checks) all clean
- [ ] Handoff to Verifier with claim manifest, hygiene audit, safety audit, structural notes
- [ ] Did NOT move to `shipped/`

You are done. The Verifier will route PASS → `shipped/` or FAIL → redlines back to you.
